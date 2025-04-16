import pytest
import os
import json
import time
import concurrent.futures
from app import create_app
from cache_extension import cache
from test_data import TEST_CHART_IDS, HISTORICAL_TEST_DATES

@pytest.fixture
def requires_api_key():
    """Skip test if Billboard API key isn't available"""
    if not os.getenv("RAPID_API_KEY"):
        pytest.skip("Billboard API key not available")

@pytest.fixture
def client():
    """Create Flask test client"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            cache.clear()
            yield client
            cache.clear()

def test_chart_retrieval_with_caching(client, requires_api_key):
    """Test the complete chart retrieval pipeline with caching"""
    # Act - First request (cold cache)
    start_time = time.time()
    response1 = client.get('/billboard_api.php')
    first_request_time = time.time() - start_time
    
    # Assert - First request
    assert response1.status_code == 200
    data1 = json.loads(response1.data)
    assert not data1['cached']
    assert 'chart' in data1
    assert len(data1['chart']['entries']) > 0
    
    # Act - Second request (warm cache)
    start_time = time.time()
    response2 = client.get('/billboard_api.php')
    second_request_time = time.time() - start_time
    
    # Assert - Second request should be cached and faster
    assert response2.status_code == 200
    data2 = json.loads(response2.data)
    assert data2['cached']
    assert second_request_time < first_request_time

@pytest.mark.parametrize("date", HISTORICAL_TEST_DATES[:1])  # Use just one date for efficiency
def test_historical_chart(client, requires_api_key, date):
    """Test retrieving historical chart data"""
    # Act - Request historical chart
    response = client.get(f'/billboard_api.php?week={date}')
    
    # Assert
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'chart' in data
    assert 'date' in data['chart']
    assert data['chart']['date'] == date

def test_refresh_cached_chart(client, requires_api_key):
    """Test force refreshing a cached chart"""
    # Arrange - First populate the cache
    client.get('/billboard_api.php')
    
    # Act - Force refresh
    response = client.get('/billboard_api.php?refresh=true')
    
    # Assert
    assert response.status_code == 200
    data = json.loads(response.data)
    assert not data['cached']

@pytest.mark.parametrize("include_apple_music", ["true", "false"])
def test_apple_music_integration(client, requires_api_key, include_apple_music):
    """Test toggling Apple Music integration"""
    # Act
    response = client.get(f'/billboard_api.php?apple_music={include_apple_music}')
    
    # Assert
    assert response.status_code == 200
    # We can't guarantee Apple Music data will be present even when requested
    # due to API constraints, but the request should succeed

def test_concurrent_chart_requests(client, requires_api_key):
    """Test handling multiple concurrent chart requests"""
    # Arrange - Use a subset of charts for testing
    test_charts = TEST_CHART_IDS[:3]  # Use first 3 charts
    
    # Define request function
    def request_chart(chart_id):
        response = client.get(f'/billboard_api.php?id={chart_id}')
        if response.status_code == 200:
            return json.loads(response.data)
        return {"error": f"Failed with status {response.status_code}"}
    
    # Act - Make concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(request_chart, chart_id): chart_id 
                  for chart_id in test_charts}
        
        # Process results
        results = {}
        for future in concurrent.futures.as_completed(futures):
            chart_id = futures[future]
            results[chart_id] = future.result()
    
    # Assert - All requests should return valid data
    for chart_id, result in results.items():
        assert 'error' not in result
        if 'chart' in result:
            assert 'entries' in result['chart']

def test_performance_of_cached_responses(client, requires_api_key):
    """Test performance of cached responses"""
    # Arrange - Populate cache
    client.get('/billboard_api.php')
    
    # Act - Make multiple cached requests
    response_times = []
    for _ in range(5):  # 5 requests is sufficient for timing test
        start = time.time()
        response = client.get('/billboard_api.php')
        end = time.time()
        response_times.append(end - start)
        data = json.loads(response.data)
        assert data['cached']  # Verify we're testing cached responses
    
    # Assert - All cached responses should be fast (under 100ms is reasonable)
    # This threshold might need adjustment based on the testing environment
    assert all(t < 0.1 for t in response_times), "Cached responses too slow"
    
    # Average should be consistent
    avg_time = sum(response_times) / len(response_times)
    assert max(response_times) < avg_time * 2, "Response times too variable"