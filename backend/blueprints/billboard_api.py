from flask import Blueprint, jsonify, request
import requests
import os
import logging
from dotenv import load_dotenv
from cache_extension import cache
from datetime import datetime, timedelta
import jwt
import concurrent.futures

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("RAPID_API_KEY")

# Apple Music credentials from .env file
APPLE_MUSIC_KEY_ID = os.getenv("APPLE_MUSIC_KEY_ID")
APPLE_MUSIC_TEAM_ID = os.getenv("APPLE_MUSIC_TEAM_ID")
APPLE_MUSIC_AUTH_KEY = os.getenv("APPLE_MUSIC_AUTH_KEY")

# Create blueprint with prefix
billboard_bp = Blueprint('billboard', __name__, url_prefix='')

# Constants
ONE_HOUR = 3600
ONE_WEEK = 604800
RATE_LIMIT_TIMEOUT = 300  # 5 minutes
APPLE_MUSIC_TOKEN_TIMEOUT = 11 * 3600  # 11 hours

# ================= Apple Music Service =================

class AppleMusicService:
    @staticmethod
    def get_token():
        """Get a cached token or generate a new one"""
        cache_key = "apple_music:token"
        token = cache.get(cache_key)
        
        if token:
            return token
        
        try:
            time_now = datetime.now()
            expiration_time = time_now + timedelta(hours=12)
            
            headers = {
                "alg": "ES256",
                "kid": APPLE_MUSIC_KEY_ID
            }
            
            payload = {
                "iss": APPLE_MUSIC_TEAM_ID,
                "iat": int(time_now.timestamp()),
                "exp": int(expiration_time.timestamp())
            }
            
            token = jwt.encode(
                payload, 
                APPLE_MUSIC_AUTH_KEY,
                algorithm='ES256',
                headers=headers
            )
            
            cache.set(cache_key, token, timeout=APPLE_MUSIC_TOKEN_TIMEOUT)
            return token
        except Exception as e:
            logger.error(f"Error generating Apple Music token: {e}")
            return None
    
    @staticmethod
    def search_song(title, artist):
        """Search Apple Music for a song"""
        cache_key = f"apple_music:search:{title}:{artist}"
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:  # Allow caching of None results too
            return cached_result
        
        token = AppleMusicService.get_token()
        if not token:
            return None
            
        try:
            search_term = f"{title} {artist}".replace(" ", "+")
            url = f"https://api.music.apple.com/v1/catalog/us/search?term={search_term}&types=songs&limit=1"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            result = None
            if data.get("results", {}).get("songs", {}).get("data"):
                song = data["results"]["songs"]["data"][0]
                result = {
                    "id": song["id"],
                    "url": song["attributes"]["url"],
                    "preview_url": song["attributes"].get("previews", [{}])[0].get("url") if song["attributes"].get("previews") else None,
                    "artwork_url": song["attributes"].get("artwork", {}).get("url", "").replace("{w}", "300").replace("{h}", "300")
                }
            
            # Cache results for 24 hours
            cache.set(cache_key, result, timeout=24*60*60)
            return result
            
        except Exception as e:
            logger.error(f"Error searching Apple Music: {e}")
            # Cache failures briefly to prevent immediate retries
            cache.set(cache_key, None, timeout=300)
            return None
    
    @staticmethod
    def enrich_chart_data(data):
        """Add Apple Music data to chart entries in parallel"""
        if not data:
            return data
            
        # Determine the song list structure
        songs = []
        if "chart" in data and "entries" in data["chart"]:
            songs = data["chart"]["entries"]
        elif "songs" in data:
            songs = data["songs"]
        else:
            # Unknown structure
            return data
            
        # Skip processing if songs already have Apple Music data
        if songs and "apple_music" in songs[0]:
            return data
            
        # Process songs in parallel (max 5 workers to avoid overwhelming)
        # Only process songs that don't already have Apple Music data
        songs_to_process = [s for s in songs if "apple_music" not in s]
        
        if not songs_to_process:
            return data
            
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # Map songs to their titles and artists
                song_data = [(s.get("title", s.get("name")), s.get("artist")) for s in songs_to_process]
                
                # Search for each song in parallel
                apple_music_results = list(executor.map(
                    lambda x: AppleMusicService.search_song(*x), 
                    song_data
                ))
                
                # Add results back to songs
                for song, result in zip(songs_to_process, apple_music_results):
                    song["apple_music"] = result
                    
        except Exception as e:
            logger.error(f"Error enriching chart data with Apple Music: {e}")
            
        return data

# ================= Billboard API Route =================

@billboard_bp.route('/billboard_api.php')
def get_chart():
    # Get query parameters
    chart_id = request.args.get('id', 'hot-100')
    week = request.args.get('week')
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    include_apple_music = request.args.get('apple_music', 'true').lower() == 'true'
    
    # Create cache key
    cache_key = f"billboard:{chart_id}" + (f":{week}" if week else "")
    
    # Get cached data
    cached_data = cache.get(cache_key)
    
    # Determine if we need to fetch from API
    need_api_call = (
        refresh or 
        not cached_data or 
        (not week and datetime.now().weekday() == 1 and not cache.get("billboard:rate_limited"))
    )
    
    # Use cached data if we have it and don't need to refresh
    if not need_api_call and cached_data:
        # Add Apple Music data if requested and not already present
        if include_apple_music:
            cached_data = AppleMusicService.enrich_chart_data(cached_data)
            
        note = "API rate limited, serving cached data" if cache.get("billboard:rate_limited") else None
        return jsonify({**cached_data, "cached": True, "note": note} if note else {**cached_data, "cached": True})
    
    # If we got here, we need to fetch from API
    url = "https://billboard-charts-api.p.rapidapi.com/chart.php"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "billboard-charts-api.p.rapidapi.com"
    }
    params = {'id': chart_id}
    if week:
        params['week'] = week
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        new_data = response.json()
        
        # Check if API returned an error
        if not isinstance(new_data, dict) or "error" in new_data:
            raise Exception(new_data.get("error", "Invalid API response") if isinstance(new_data, dict) else "Invalid response format")
        
        # Clear rate limit flag if request was successful
        cache.delete("billboard:rate_limited")
        
        # Add Apple Music data if requested
        if include_apple_music:
            new_data = AppleMusicService.enrich_chart_data(new_data)
        
        # Cache historical data permanently
        if week:
            cache.set(cache_key, new_data, timeout=None)
            return jsonify({**new_data, "cached": False})
        
        # For current charts - check if data changed (only on Tuesdays)
        is_tuesday = datetime.now().weekday() == 1
        if is_tuesday and cached_data and not refresh:
            old_date = cached_data.get("chart", {}).get("date")
            new_date = new_data.get("chart", {}).get("date")
            
            if old_date == new_date:
                # Data hasn't changed, check again in an hour
                # Make sure cached data has Apple Music info if requested
                if include_apple_music:
                    cached_data = AppleMusicService.enrich_chart_data(cached_data)
                cache.set(cache_key, cached_data, timeout=ONE_HOUR)
                return jsonify({**cached_data, "cached": True, "note": "No new chart data yet"})
        
        # New or changed data - cache for a week
        cache.set(cache_key, new_data, timeout=ONE_WEEK)
        return jsonify({**new_data, "cached": False})
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        
        # Handle rate limiting specifically
        if response.status_code == 429:
            cache.set("billboard:rate_limited", True, timeout=RATE_LIMIT_TIMEOUT)
            message = "API rate limit exceeded"
        else:
            message = f"API error: Status code {response.status_code}"
            
        # Fall back to cached data if available
        if cached_data:
            if include_apple_music:
                cached_data = AppleMusicService.enrich_chart_data(cached_data)
            return jsonify({**cached_data, "cached": True, "note": f"{message}, serving cached data"})
        return jsonify({"error": message, "cached": False, "status_code": response.status_code}), 503
        
    except (requests.exceptions.RequestException, ValueError) as e:
        # Handles connection, timeout, and JSON parsing errors
        error_type = "Timeout" if isinstance(e, requests.exceptions.Timeout) else "API error"
        error_message = str(e)
        logger.error(f"{error_type}: {error_message}")
        
        if cached_data:
            if include_apple_music:
                cached_data = AppleMusicService.enrich_chart_data(cached_data)
            return jsonify({**cached_data, "cached": True, "note": f"{error_type}: {error_message}, serving cached data"})
        return jsonify({"error": f"{error_type}: {error_message}", "cached": False}), 503
        
    except Exception as e:
        # Catch-all for any other errors
        error_message = str(e)
        logger.error(f"Unexpected error: {error_message}")
        
        if cached_data:
            if include_apple_music:
                cached_data = AppleMusicService.enrich_chart_data(cached_data)
            return jsonify({**cached_data, "cached": True, "note": f"{error_message}, serving cached data"})
        return jsonify({"error": error_message, "cached": False}), 503