from flask import Blueprint, jsonify, request
import requests
import os
import logging
from dotenv import load_dotenv
from cache_extension import cache
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key
load_dotenv()
api_key = os.getenv("RAPID_API_KEY")

# Create blueprint with prefix
billboard_bp = Blueprint('billboard', __name__, url_prefix='')

ONE_HOUR = 3600
ONE_WEEK = 604800
RATE_LIMIT_TIMEOUT = 300  # 5 minutes

@billboard_bp.route('/billboard_api.php')
def get_chart():
    # Get query parameters
    chart_id = request.args.get('id', 'hot-100')
    week = request.args.get('week')
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Create cache key
    cache_key = f"billboard:{chart_id}" + (f":{week}" if week else "")
    
    # Get cached data
    cached_data = cache.get(cache_key)
    
    # Don't hit the API if:
    # 1. We have historical data cached (and no refresh requested)
    # 2. It's not Tuesday and we have current data cached (and no refresh requested)
    # 3. We're currently rate limited and have cached data
    if not refresh and cached_data and (
        week or 
        (not week and datetime.now().weekday() != 1) or
        cache.get("billboard:rate_limited")
    ):
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
        response.raise_for_status()  # Raises exception for 4XX/5XX responses
        new_data = response.json()
        
        # Check if API returned an error in its response
        if not isinstance(new_data, dict) or "error" in new_data:
            raise Exception(new_data.get("error", "Invalid API response") if isinstance(new_data, dict) else "Invalid response format")
        
        # Clear rate limit flag if request was successful
        cache.delete("billboard:rate_limited")
        
        # For historical data - cache permanently
        if week:
            cache.set(cache_key, new_data, timeout=None)
            return jsonify({**new_data, "cached": False})
        
        # For current charts - check if data changed (only on Tuesdays)
        if datetime.now().weekday() == 1 and cached_data and not refresh:
            if new_data.get("chart", {}).get("date") == cached_data.get("chart", {}).get("date"):
                # Data hasn't changed, check again in an hour
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
            return jsonify({**cached_data, "cached": True, "note": f"{message}, serving cached data"})
        return jsonify({"error": message, "cached": False, "status_code": response.status_code}), 503
        
    except (requests.exceptions.RequestException, ValueError) as e:
        # Handles connection, timeout, and JSON parsing errors
        error_type = "Timeout" if isinstance(e, requests.exceptions.Timeout) else "API error"
        error_message = str(e)
        logger.error(f"{error_type}: {error_message}")
        
        if cached_data:
            return jsonify({**cached_data, "cached": True, "note": f"{error_type}: {error_message}, serving cached data"})
        return jsonify({"error": f"{error_type}: {error_message}", "cached": False}), 503
        
    except Exception as e:
        # Catch-all for any other errors
        error_message = str(e)
        logger.error(f"Unexpected error: {error_message}")
        
        if cached_data:
            return jsonify({**cached_data, "cached": True, "note": f"{error_message}, serving cached data"})
        return jsonify({"error": error_message, "cached": False}), 503