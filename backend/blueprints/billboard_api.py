from flask import Blueprint, jsonify, request
import requests
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("RAPID_API_KEY")

# Create blueprint with prefix
billboard_bp = Blueprint('billboard', __name__, url_prefix='')

@billboard_bp.route('/billboard_api.php')
def get_chart():
    # Get query parameters with default for id
    chart_id = request.args.get('id', 'hot-100')
    week = request.args.get('week')
    
    # Build API URL with parameters
    url = "https://billboard-charts-api.p.rapidapi.com/chart.php"
    params = {'id': chart_id}
    
    # Add optional week parameter if provided
    if week:
        params['week'] = week
    
    # Set up headers
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "billboard-charts-api.p.rapidapi.com"
    }
    
    # Make API request
    response = requests.get(url, headers=headers, params=params)
    
    # Return JSON response
    return jsonify(response.json())