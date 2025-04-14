import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from freezegun import freeze_time

from app import create_app
from cache_extension import cache

@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['CACHE_TYPE'] = 'SimpleCache'  # Use simple cache for testing
    
    with app.app_context():
        cache.init_app(app)
        yield app
        cache.clear()  # Clear cache after each test

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

@pytest.fixture
def mock_chart_data():
    """Sample chart data for testing"""
    return {
        "chart": {
            "id": "hot-100",
            "name": "Hot 100",
            "date": "2023-04-01",
            "entries": [
                {
                    "rank": 1,
                    "title": "Test Song",
                    "artist": "Test Artist",
                    "weeks": 10,
                    "previous": 2
                }
            ]
        }
    }

@pytest.fixture
def mock_api_success(mock_chart_data):
    """Mock a successful API response"""
    with patch('blueprints.billboard_api.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_chart_data
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_api_error():
    """Mock an API error response"""
    with patch('blueprints.billboard_api.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API error")
        mock_get.return_value = mock_response
        yield mock_get

def test_get_chart_success(client, mock_api_success):
    """Test successful API call with default parameters"""
    response = client.get('/billboard_api.php')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['chart']['id'] == 'hot-100'
    assert data['cached'] is False
    
    # Verify API was called with correct parameters
    mock_api_success.assert_called_once()
    args, kwargs = mock_api_success.call_args
    assert kwargs['params']['id'] == 'hot-100'
    assert 'week' not in kwargs['params']

@pytest.mark.parametrize('chart_id', ['hot-100', 'billboard-200', 'artist-100'])
def test_get_chart_with_custom_id(client, mock_api_success, chart_id, mock_chart_data):
    """Test API call with different chart IDs"""
    # Update mock data with custom chart ID
    mock_chart_data['chart']['id'] = chart_id
    
    response = client.get(f'/billboard_api.php?id={chart_id}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['chart']['id'] == chart_id
    
    # Verify API was called with correct parameters
    args, kwargs = mock_api_success.call_args
    assert kwargs['params']['id'] == chart_id

def test_get_chart_with_week(client, mock_api_success):
    """Test API call with specific week"""
    response = client.get('/billboard_api.php?week=2023-01-01')
    
    assert response.status_code == 200
    
    # Verify API was called with correct parameters
    args, kwargs = mock_api_success.call_args
    assert kwargs['params']['week'] == '2023-01-01'

def test_cached_response(client, mock_api_success):
    """Test that cached data is returned on subsequent requests"""
    # First request should hit the API
    response1 = client.get('/billboard_api.php')
    assert response1.status_code == 200
    data1 = json.loads(response1.data)
    assert data1['cached'] is False
    
    # Reset the mock to track new calls
    mock_api_success.reset_mock()
    
    # Second request should use cache
    response2 = client.get('/billboard_api.php')
    assert response2.status_code == 200
    data2 = json.loads(response2.data)
    assert data2['cached'] is True
    
    # API should not be called again
    mock_api_success.assert_not_called()

def test_refresh_param(client, mock_api_success):
    """Test that refresh=true bypasses cache"""
    # First request caches the data
    client.get('/billboard_api.php')
    
    # Reset the mock to track new calls
    mock_api_success.reset_mock()
    
    # Second request with refresh=true should bypass cache
    response = client.get('/billboard_api.php?refresh=true')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['cached'] is False
    
    # API should be called again
    mock_api_success.assert_called_once()

def test_api_error_handling(client, mock_api_error):
    """Test error handling when API returns an error"""
    response = client.get('/billboard_api.php')
    
    assert response.status_code == 503
    data = json.loads(response.data)
    assert 'error' in data
    assert data['cached'] is False

def test_fallback_to_cache_on_error(client, mock_api_success, mock_chart_data):
    """Test fallback to cached data when API error occurs"""
    # First request caches the data
    client.get('/billboard_api.php')
    
    # Now simulate an API error
    with patch('blueprints.billboard_api.requests.get') as mock_error:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API error")
        mock_error.return_value = mock_response
        
        # Second request with refresh=true would normally hit API but should fall back to cache
        response = client.get('/billboard_api.php?refresh=true')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['cached'] is True
        assert 'note' in data
        assert 'API error' in data['note']

def test_rate_limit_handling(client, mock_chart_data):
    """Test handling of rate limit errors"""
    # First simulate a rate limit error
    with patch('blueprints.billboard_api.requests.get') as mock_rate_limit:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
        mock_rate_limit.return_value = mock_response
        
        # First request should set rate limit flag but fail
        response = client.get('/billboard_api.php')
        assert response.status_code == 503
    
    # Now succeed and cache some data
    with patch('blueprints.billboard_api.requests.get') as mock_success:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_chart_data
        mock_success.return_value = mock_response
        
        client.get('/billboard_api.php')
    
    # Now rate limit again and verify we use cache
    with patch('blueprints.billboard_api.requests.get') as mock_rate_limit_again:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
        mock_rate_limit_again.return_value = mock_response
        
        response = client.get('/billboard_api.php?refresh=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['cached'] is True
        assert 'note' in data
        assert 'rate limit' in data['note'].lower()

@freeze_time("2023-04-04")  # A Tuesday
def test_tuesday_refresh_logic(client, mock_chart_data):
    """Test Tuesday refresh logic with both new and unchanged data"""
    # First cache some data
    with patch('blueprints.billboard_api.requests.get') as mock_initial:
        mock_response = MagicMock()
        mock_response.status_code = 200
        old_data = mock_chart_data.copy()
        old_data['chart']['date'] = "2023-03-28"
        mock_response.json.return_value = old_data
        mock_initial.return_value = mock_response
        
        client.get('/billboard_api.php')
    
    # Test case 1: New data available on Tuesday
    with patch('blueprints.billboard_api.requests.get') as mock_new_data:
        mock_response = MagicMock()
        mock_response.status_code = 200
        new_data = mock_chart_data.copy()
        new_data['chart']['date'] = "2023-04-04"
        mock_response.json.return_value = new_data
        mock_new_data.return_value = mock_response
        
        response = client.get('/billboard_api.php')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['chart']['date'] == "2023-04-04"
        assert data['cached'] is False
    
    # Test case 2: No new data available on Tuesday
    with patch('blueprints.billboard_api.requests.get') as mock_same_data:
        mock_response = MagicMock()
        mock_response.status_code = 200
        same_data = mock_chart_data.copy()
        same_data['chart']['date'] = "2023-04-04"  # Same as above
        mock_response.json.return_value = same_data
        mock_same_data.return_value = mock_response
        
        response = client.get('/billboard_api.php')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['cached'] is True
        assert 'note' in data
        assert data['note'] == "No new chart data yet"

@freeze_time("2023-04-05")  # A Wednesday
def test_non_tuesday_caching(client, mock_api_success):
    """Test that non-Tuesdays use cached data"""
    # First request to cache data
    client.get('/billboard_api.php')
    
    # Reset the mock to track new calls
    mock_api_success.reset_mock()
    
    # Second request on Wednesday should use cache
    response = client.get('/billboard_api.php')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['cached'] is True
    
    # API should not be called again
    mock_api_success.assert_not_called()

def test_historical_data_caching(client, mock_api_success):
    """Test that historical data is cached"""
    # First request with week parameter
    client.get('/billboard_api.php?week=2022-01-01')
    
    # Reset the mock to track new calls
    mock_api_success.reset_mock()
    
    # Second request for same historical data should use cache
    response = client.get('/billboard_api.php?week=2022-01-01')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['cached'] is True
    
    # API should not be called again
    mock_api_success.assert_not_called()