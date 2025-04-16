import pytest
from flask import Flask
from app import create_app
from cache_extension import cache

@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    return app

def test_app_creation(app):
    """Test that the Flask app is created correctly"""
    # Verify app is a Flask instance with the expected name
    assert isinstance(app, Flask)
    assert app.name == "app"
    
def test_cache_initialization(app):
    """Test that the cache is properly initialized with the app"""
    with app.app_context():
        # Verify cache operations work
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
        # Clean up
        cache.delete("test_key")
    
def test_blueprint_registration(app):
    """Test that the billboard blueprint is registered"""
    # Verify blueprint is registered
    registered_blueprints = [bp.name for bp in app.blueprints.values()]
    assert 'billboard' in registered_blueprints
    
    # Verify the route exists
    rules = [rule.endpoint for rule in app.url_map.iter_rules()]
    assert 'billboard.get_chart' in rules
    
@pytest.mark.parametrize("config_key,expected_value", [
    ('CACHE_TYPE', 'RedisCache'),
    ('CACHE_DEFAULT_TIMEOUT', 3600)
])
def test_cache_config(app, config_key, expected_value):
    """Test cache configuration is properly set up"""
    assert app.config[config_key] == expected_value
    assert 'CACHE_REDIS_URL' in app.config