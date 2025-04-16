from flask import Blueprint, jsonify, request
import requests
import os
import logging
from dotenv import load_dotenv
from cache_extension import cache
from datetime import datetime, timedelta
import jwt
import concurrent.futures
import re

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
# No URL prefix means routes will be registered at the root path
billboard_bp = Blueprint('billboard', __name__, url_prefix='')

# Constants for cache timeouts and rate limiting
ONE_HOUR = 3600
ONE_WEEK = 604800
RATE_LIMIT_TIMEOUT = 300  # 5 minutes - how long to wait when rate limited
APPLE_MUSIC_TOKEN_TIMEOUT = 11 * 3600  # 11 hours - token expires after 12 hours, refreshing slightly early

# ================= Apple Music Service =================

class AppleMusicService:
    @staticmethod
    def get_token():
        """
        Get a cached Apple Music token or generate a new one.
        
        The token is a JWT that lasts for 12 hours but we cache it for 11 hours
        to ensure we refresh it before expiration.
        
        Returns:
            str: The Apple Music JWT token or None if generation fails
        """
        cache_key = "apple_music:token"
        token = cache.get(cache_key)
        
        if token:
            return token
        
        try:
            # Generate a new token with a 12-hour expiration
            time_now = datetime.now()
            expiration_time = time_now + timedelta(hours=12)
            
            # Define JWT headers as required by Apple Music API
            headers = {
                "alg": "ES256",  # Required algorithm
                "kid": APPLE_MUSIC_KEY_ID  # Key identifier from Apple Developer account
            }
            
            # Define JWT payload as required by Apple Music API
            payload = {
                "iss": APPLE_MUSIC_TEAM_ID,  # Team ID from Apple Developer account
                "iat": int(time_now.timestamp()),  # Issued at time
                "exp": int(expiration_time.timestamp())  # Expiration time
            }
            
            # Generate the JWT token with ES256 algorithm
            token = jwt.encode(
                payload, 
                APPLE_MUSIC_AUTH_KEY,  # Private key from Apple Developer account
                algorithm='ES256',
                headers=headers
            )
            
            # Cache the token for slightly less than its full lifetime
            cache.set(cache_key, token, timeout=APPLE_MUSIC_TOKEN_TIMEOUT)
            return token
        except Exception as e:
            logger.error(f"Error generating Apple Music token: {e}")
            return None
        
    @staticmethod
    def standardize_artwork_url(url):
        """
        Standardize artwork URL to always use 1000x1000 dimensions.
        
        Args:
            url (str): The artwork URL to standardize
                
        Returns:
            str: Standardized artwork URL with 1000x1000 dimensions
        """
        if not url:
            return url
            
        # Replace {w}x{h} placeholders with 1000x1000
        return url.replace("{w}x{h}bb.jpg", "1000x1000bb.jpg")
    
    @staticmethod
    def search_song(title, artist):
        """
        Search Apple Music for a song by title and artist.
        
        Args:
            title (str): The song title to search for
            artist (str): The artist name to search for
            
        Returns:
            dict: Song details including ID, URL, preview URL, and artwork URL, or None if not found
        """
        # Create a cache key using both title and artist to ensure uniqueness
        cache_key = f"apple_music:search:{title}:{artist}"
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:  # Allow caching of None results too
            # Always standardize artwork URL for cached results
            if cached_result and "artwork_url" in cached_result:
                cached_result["artwork_url"] = AppleMusicService.standardize_artwork_url(cached_result["artwork_url"])
            return cached_result
        
        token = AppleMusicService.get_token()
        if not token:
            return None
            
        try:
            url = "https://api.music.apple.com/v1/catalog/us/search"
            headers = {"Authorization": f"Bearer {token}"}
            search_term = f"{title} {artist}"
            
            params = {
                'term': search_term,
                'types': 'songs',
                'limit': 1,
                'include': 'albums,artists,composers'  # Enhanced to include more relationships
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Extract song information and standardize artwork URL
            result = None
            if data.get("results", {}).get("songs", {}).get("data"):
                song = data["results"]["songs"]["data"][0]
                attributes = song["attributes"]
                artwork_url = attributes.get("artwork", {}).get("url", "")
                
                # Create basic result with required fields
                result = {
                    "id": song["id"],
                    "url": attributes["url"],
                    "preview_url": attributes.get("previews", [{}])[0].get("url") if attributes.get("previews") else None,
                    "artwork_url": AppleMusicService.standardize_artwork_url(artwork_url),
                }
                
                # Add important song details
                if attributes.get("durationInMillis"):
                    result["duration_in_millis"] = attributes["durationInMillis"]
                
                if attributes.get("isrc"):
                    result["isrc"] = attributes["isrc"]
                
                if attributes.get("releaseDate"):
                    result["release_date"] = attributes["releaseDate"]
                
                # Add GENRES (new)
                if attributes.get("genreNames"):
                    result["genres"] = attributes["genreNames"]
                
                # Add COMPOSERS (new)
                if attributes.get("composerName"):
                    result["composers"] = attributes["composerName"].split(", ")
                
                # Add LYRICISTS (new)
                if attributes.get("artistName") and attributes.get("composerName") != attributes.get("artistName"):
                    result["lyricists"] = attributes.get("artistName").split(", ")
                
                # Add album information if available
                if "relationships" in song and "albums" in song["relationships"] and song["relationships"]["albums"]["data"]:
                    album_data = song["relationships"]["albums"]["data"][0]
                    album = album_data["attributes"]
                    
                    # Enhanced album information
                    result["album"] = {
                        "id": album_data.get("id"),
                        "name": album.get("name"),
                        "artist": album.get("artistName"),
                        "url": album.get("url"),
                        "record_label": album.get("recordLabel"),
                        "release_date": album.get("releaseDate"),
                        "track_count": album.get("trackCount"),
                        "copyright": album.get("copyright"),
                        "editorial_notes": album.get("editorialNotes", {}).get("standard")
                    }
                    
                    # Add album genres (new)
                    if album.get("genreNames"):
                        result["album"]["genres"] = album["genreNames"]
                    
                    # Add album artwork if available
                    if album.get("artwork", {}).get("url"):
                        result["album"]["artwork_url"] = AppleMusicService.standardize_artwork_url(
                            album["artwork"]["url"]
                        )
                
                # Add artist information if available (new)
                if "relationships" in song and "artists" in song["relationships"] and song["relationships"]["artists"]["data"]:
                    artist_data = song["relationships"]["artists"]["data"][0]
                    artist_attributes = artist_data["attributes"]
                    
                    result["artist_info"] = {
                        "id": artist_data.get("id"),
                        "name": artist_attributes.get("name"),
                        "url": artist_attributes.get("url"),
                        "genres": artist_attributes.get("genreNames")
                    }
                    
                    # Add artist artwork if available
                    if artist_attributes.get("artwork", {}).get("url"):
                        result["artist_info"]["artwork_url"] = AppleMusicService.standardize_artwork_url(
                            artist_attributes["artwork"]["url"]
                        )
            
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
        """
        Add Apple Music data to chart entries and standardize artwork URLs.
        
        Args:
            data (dict): Billboard chart data to enrich
            
        Returns:
            dict: The chart data with standardized artwork URLs and Apple Music info
        """
        if not data:
            return data
            
        # Determine the song list structure
        songs = []
        if "chart" in data and "entries" in data["chart"]:
            songs = data["chart"]["entries"]
        elif "songs" in data:
            songs = data["songs"]
        else:
            return data
        
        # First, standardize artwork URLs for existing Apple Music data
        for song in songs:
            if "apple_music" in song and song["apple_music"] and "artwork_url" in song["apple_music"]:
                song["apple_music"]["artwork_url"] = AppleMusicService.standardize_artwork_url(song["apple_music"]["artwork_url"])
            
        # If songs already have Apple Music data, we're done
        if songs and all("apple_music" in song for song in songs):
            return data
            
        # Process songs that don't have Apple Music data
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
    """
    Main endpoint handler for retrieving Billboard chart data.
    
    Supports parameters:
    - id: The chart ID (default: hot-100)
    - week: Specific week in YYYY-MM-DD format (optional)
    - refresh: Force refresh from API (default: false)
    - apple_music: Include Apple Music data (default: true)
    
    Uses caching strategy based on:
    - Whether it's Tuesday (chart refresh day)
    - Whether week parameter is provided (historical data)
    - Whether a force refresh is requested
    - Whether we're currently rate limited
    
    Returns chart data with caching status and notes.
    """
    # Get query parameters
    chart_id = request.args.get('id', 'hot-100')
    week = request.args.get('week')
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    include_apple_music = request.args.get('apple_music', 'true').lower() == 'true'
    
    # Create cache key - format: billboard:chart_id:week (if week provided)
    cache_key = f"billboard:{chart_id}" + (f":{week}" if week else "")
    
    # Get cached data
    cached_data = cache.get(cache_key)
    
    # Determine if we need to fetch from API based on multiple conditions
    need_api_call = (
        refresh or  # Explicit refresh requested
        not cached_data or  # No cached data exists
        # It's Tuesday (when charts update) and we're not rate limited - check for updates
        (not week and datetime.now().weekday() == 1 and not cache.get("billboard:rate_limited"))
    )
    
    # Use cached data if we have it and don't need to refresh
    if not need_api_call and cached_data:
        # Add Apple Music data if requested and not already present
        if include_apple_music:
            cached_data = AppleMusicService.enrich_chart_data(cached_data)
            
        # Add note if we're rate limited to inform the client
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
        # Make the API request
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
        
        # Cache historical data permanently (specific week)
        if week:
            cache.set(cache_key, new_data, timeout=None)
            return jsonify({**new_data, "cached": False})
        
        # For current charts - check if data changed (only on Tuesdays)
        is_tuesday = datetime.now().weekday() == 1
        if is_tuesday and cached_data and not refresh:
            old_date = cached_data.get("chart", {}).get("date")
            new_date = new_data.get("chart", {}).get("date")
            
            # If dates match, the chart hasn't been updated yet despite being Tuesday
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
        # Handle HTTP errors (4xx, 5xx)
        logger.error(f"HTTP Error: {e}")
        
        # Handle rate limiting specifically
        if response.status_code == 429:
            # Set rate limit flag to prevent hammering the API
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
        
        # Fall back to cached data if available
        if cached_data:
            if include_apple_music:
                cached_data = AppleMusicService.enrich_chart_data(cached_data)
            return jsonify({**cached_data, "cached": True, "note": f"{error_type}: {error_message}, serving cached data"})
        return jsonify({"error": f"{error_type}: {error_message}", "cached": False}), 503
        
    except Exception as e:
        # Catch-all for any other errors
        error_message = str(e)
        logger.error(f"Unexpected error: {error_message}")
        
        # Fall back to cached data if available
        if cached_data:
            if include_apple_music:
                cached_data = AppleMusicService.enrich_chart_data(cached_data)
            return jsonify({**cached_data, "cached": True, "note": f"{error_message}, serving cached data"})
        return jsonify({"error": error_message, "cached": False}), 503