from flask import Blueprint, jsonify, request
import requests
import os
from dotenv import load_dotenv
from cache_extension import cache

# Load API key
load_dotenv()
api_key = os.getenv("RAPID_API_KEY")

# Create blueprint with prefix
billboard_bp = Blueprint('billboard', __name__, url_prefix='')

@billboard_bp.route('/billboard_api.php')
def get_chart():
    # Get query parameters with defaults set
    chart_id = request.args.get('id', 'hot-100')
    week = request.args.get('week')
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Initialise with default value - assuming data will come from API
    from_cache = False
    
    # Try to get from cache for current charts
    data = None
    if not week and not refresh:
        cache_key = f"billboard:{chart_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            data = cached_data
            from_cache = True
    
    # If not in cache, make API request
    if data is None:
        # Build API request
        url = "https://billboard-charts-api.p.rapidapi.com/chart.php"
        params = {'id': chart_id}
        if week:
            params['week'] = week
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "billboard-charts-api.p.rapidapi.com"
        }
        
        # Make API request
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            # Cache current chart data
            if not week and not refresh:
                cache_key = f"billboard:{chart_id}"
                cache.set(cache_key, data, timeout=3600)
        except Exception as e:
            return jsonify({"error": str(e), "cached": False}), 500
    
    # Add the cache status flag to the original data
    data["cached"] = from_cache
    
    return jsonify(data)