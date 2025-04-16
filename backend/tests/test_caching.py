import pytest
import time
from app import create_app
from cache_extension import cache

@pytest.fixture
def app_context():
    """Create Flask app context for testing"""
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        cache.clear()
        yield
        cache.clear()

@pytest.mark.parametrize("test_data", [
    "string value",
    42,
    {"key": "value"},
    ["item1", "item2"],
    None
])
def test_cache_set_get(app_context, test_data):
    """Test basic cache operations with different data types"""
    # Arrange
    test_key = "test_key"
    
    # Act
    cache.set(test_key, test_data)
    result = cache.get(test_key)
    
    # Assert
    assert result == test_data
    
    # Clean up
    cache.delete(test_key)

@pytest.mark.parametrize("timeout,should_expire", [
    (1, True),     # Short timeout - should expire
    (None, False)  # No timeout - should not expire
])
def test_cache_timeout(app_context, timeout, should_expire):
    """Test cache timeout behavior"""
    # Arrange
    test_key = f"timeout_test_{timeout}"
    
    # Act
    cache.set(test_key, "test_value", timeout=timeout)
    
    # Assert - Value exists initially
    assert cache.get(test_key) == "test_value"
    
    # Wait longer than the timeout
    if timeout:
        time.sleep(timeout + 0.5)
    else:
        time.sleep(0.5)
    
    # Assert - Check if value expired as expected
    result = cache.get(test_key)
    if should_expire:
        assert result is None
    else:
        assert result == "test_value"

def test_cache_delete(app_context):
    """Test cache deletion operations"""
    # Arrange
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    # Act & Assert - Delete existing key
    cache.delete("key1")
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"
    
    # Act & Assert - Delete non-existent key (should not error)
    cache.delete("nonexistent_key")

def test_cache_clear(app_context):
    """Test clearing the entire cache"""
    # Arrange
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    # Act
    cache.clear()
    
    # Assert
    assert cache.get("key1") is None
    assert cache.get("key2") is None

@pytest.mark.parametrize("cache_key_pattern,data", [
    ("billboard:hot-100", {"chart": {"name": "Hot 100"}}),
    ("billboard:hot-100:2022-01-01", {"chart": {"name": "Hot 100", "date": "2022-01-01"}}),
    ("apple_music:token", "dummy_token"),
    ("apple_music:search:Song:Artist", {"id": "12345", "url": "https://example.com"}),
    ("billboard:rate_limited", True)
])
def test_application_cache_patterns(app_context, cache_key_pattern, data):
    """Test cache key patterns used in the application"""
    # Act
    cache.set(cache_key_pattern, data)
    result = cache.get(cache_key_pattern)
    
    # Assert
    assert result == data

def test_redis_connectivity(app_context):
    """Test Redis connection is working"""
    try:
        # Act
        cache.set("connectivity_test", "connected")
        
        # Assert
        assert cache.get("connectivity_test") == "connected"
    except Exception as e:
        pytest.fail(f"Redis connection failed: {e}")

def test_null_values(app_context):
    """Test caching and retrieving null/None values"""
    # Arrange
    null_key = "null_test"
    missing_key = "missing_key"
    cache.delete(missing_key)  # Ensure key doesn't exist
    
    # Act - Cache a None value
    cache.set(null_key, None)
    
    # Assert - Both keys return None, but for different reasons
    assert cache.get(null_key) is None  # Explicitly stored None
    assert cache.get(missing_key) is None  # Key doesn't exist
    
    # Differentiate using get_many
    many_result = cache.get_many([null_key, missing_key])
    assert null_key in many_result
    assert missing_key not in many_result