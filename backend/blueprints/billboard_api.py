from flask import Blueprint, jsonify, request
import requests
import os
from dotenv import load_dotenv
from cache_extension import cache
from datetime import datetime

# Load API key
load_dotenv()
api_key = os.getenv("RAPID_API_KEY")

# Create blueprint with prefix
billboard_bp = Blueprint('billboard', __name__, url_prefix='')

ONE_HOUR = 3600
ONE_WEEK = 604800

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
    
    # Historical data is simple - always serve from cache if available
    if week and cached_data and not refresh:
        return jsonify({**cached_data, "cached": True})
    
    # For current charts, check if we need fresh data
    if not week and cached_data and not refresh:
        # On Tuesdays, we might need to check for updates
        is_tuesday = datetime.now().weekday() == 1
        if not is_tuesday:
            return jsonify({**cached_data, "cached": True})
    
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
        response = requests.get(url, headers=headers, params=params)
        new_data = response.json()
        
        # Handle API errors
        if not isinstance(new_data, dict) or "error" in new_data:
            # Return cached data if available, otherwise return error
            if cached_data:
                return jsonify({**cached_data, "cached": True, 
                              "note": "API error, serving cached data"})
            return jsonify({"error": "API error", "cached": False}), 500
        
        # For historical data - cache permanently
        if week:
            cache.set(cache_key, new_data, timeout=None)
            return jsonify({**new_data, "cached": False})
        
        # For current charts - check if data changed (only on Tuesdays)
        is_tuesday = datetime.now().weekday() == 1
        
        if is_tuesday and cached_data:
            # Simple change detection - check the chart date
            if new_data.get("chart", {}).get("date") == cached_data.get("chart", {}).get("date"):
                # Data hasn't changed, check again in an hour
                cache.set(cache_key, cached_data, timeout=ONE_HOUR)
                return jsonify({**cached_data, "cached": True, 
                              "note": "No new chart data yet"})
        
        # New or changed data - cache for a week
        cache.set(cache_key, new_data, timeout=ONE_WEEK)
        return jsonify({**new_data, "cached": False})
        
    except Exception as e:
        # Return cached data if available, otherwise return error
        if cached_data:
            return jsonify({**cached_data, "cached": True, 
                          "note": f"API error: {str(e)}, serving cached data"})
        return jsonify({"error": str(e), "cached": False}), 500