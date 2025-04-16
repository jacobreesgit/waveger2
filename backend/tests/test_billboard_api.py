import pytest
import requests
import json
from datetime import datetime
from freezegun import freeze_time
from app import create_app
from cache_extension import cache
from test_data import TEST_CHART_IDS, ERROR_SCENARIOS

@pytest.fixture
def client():
    """Create Flask test client"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            cache.clear()
            yield client
            # Clean up after test
            cache.clear()

def test_get_default_chart(client):
    """Test getting the default Hot 100 chart"""
    # Act
    response = client.get('/billboard_api.php')
    data = json.loads(response.data)
    
    # Assert
    assert response.status_code == 200
    assert data['chart']['name'] == 'Hot 100'
    assert not data['cached']
    assert len(data['chart']['entries']) > 0

@pytest.mark.parametrize("chart_id", ["billboard-200", "artist-100"])
def test_get_chart_by_id(client, chart_id):
    """Test getting different charts by ID"""
    # Act
    response = client.get(f'/billboard_api.php?id={chart_id}')
    
    # Assert
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'chart' in data
        assert 'entries' in data['chart']
    else:
        # Some chart IDs might not be valid, but response should be properly formed
        data = json.loads(response.data)
        assert 'error' in data

def test_historical_chart_caching(client):
    """Test getting and caching a chart for a specific week"""
    # Arrange
    test_date = "2022-01-01"
    url = f'/billboard_api.php?week={test_date}'
    
    # Act - First request
    response1 = client.get(url)
    data1 = json.loads(response1.data)
    
    # Assert - First request not cached
    assert response1.status_code == 200
    assert not data1['cached']
    
    # Act - Second request
    response2 = client.get(url)
    data2 = json.loads(response2.data)
    
    # Assert - Second request should be cached
    assert response2.status_code == 200
    assert data2['cached']

def test_refresh_parameter(client):
    """Test that refresh=true forces a new API call"""
    # Arrange - First get data normally
    client.get('/billboard_api.php')
    
    # Act - Then request with refresh=true
    response = client.get('/billboard_api.php?refresh=true')
    data = json.loads(response.data)
    
    # Assert
    assert response.status_code == 200
    assert not data['cached']

@freeze_time("2025-04-15")  # A Tuesday
def test_tuesday_refresh(client):
    """Test Tuesday chart update behavior"""
    # Arrange - First request to populate cache
    client.get('/billboard_api.php')
    
    # Act - Modify cache to simulate old data
    with client.application.app_context():
        cached_data = cache.get("billboard:hot-100")
        if cached_data and "chart" in cached_data:
            cached_data["chart"]["date"] = "2025-04-08"  # Previous Tuesday
            cache.set("billboard:hot-100", cached_data)
    
    # Act - Second request
    response = client.get('/billboard_api.php')
    data = json.loads(response.data)
    
    # Assert - Either new data or note about no updates
    assert response.status_code == 200
    if data.get('cached', False):
        assert "note" in data and "No new chart data yet" in data["note"]

@pytest.mark.parametrize("apple_music_param", ["true", "false"])
def test_apple_music_parameter(client, apple_music_param):
    """Test apple_music parameter behavior"""
    # Act
    response = client.get(f'/billboard_api.php?apple_music={apple_music_param}')
    
    # Assert
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'chart' in data

@pytest.mark.parametrize("error_type,status_code", [
    ("rate_limit", 429),
    ("server_error", 500)
])
def test_error_handling(client, monkeypatch, error_type, status_code):
    """Test handling of API errors with fallback to cache"""
    # Arrange - First successful request to populate cache
    response = client.get('/billboard_api.php')
    assert response.status_code == 200
    
    # Mock error response
    class MockResponse:
        def __init__(self):
            self.status_code = status_code
            self._content = json.dumps({"error": f"{error_type} error"}).encode('utf-8')
            
        def json(self):
            return json.loads(self._content)
            
        def raise_for_status(self):
            raise requests.exceptions.HTTPError(f"{status_code} Error", response=self)
    
    # Arrange - Setup monkeypatch
    def mock_error_response(*args, **kwargs):
        raise requests.exceptions.HTTPError(f"{status_code} Error", response=MockResponse())
    
    monkeypatch.setattr(requests, 'get', mock_error_response)
    
    # Act - Make request that should trigger error
    response = client.get('/billboard_api.php')
    data = json.loads(response.data)
    
    # Assert - Should return cached data with note
    assert response.status_code == 200
    assert data['cached']
    assert 'note' in data
    
    # Special assertion for rate limiting
    if error_type == "rate_limit":
        with client.application.app_context():
            assert cache.get("billboard:rate_limited") is True

@pytest.mark.parametrize("exception_type", ["timeout", "connection"])
def test_exception_handling(client, monkeypatch, exception_type):
    """Test handling of request exceptions"""
    # Arrange - First successful request to populate cache
    client.get('/billboard_api.php')
    
    # Arrange - Setup exception
    if exception_type == "timeout":
        mock_exception = requests.exceptions.Timeout("Connection timed out")
    else:
        mock_exception = requests.exceptions.ConnectionError("Connection failed")
    
    # Arrange - Setup monkeypatch
    monkeypatch.setattr(requests, 'get', lambda *args, **kwargs: (_ for _ in ()).throw(mock_exception))
    
    # Act
    response = client.get('/billboard_api.php')
    data = json.loads(response.data)
    
    # Assert - Should use cached data
    assert response.status_code == 200
    assert data['cached']
    assert 'note' in data