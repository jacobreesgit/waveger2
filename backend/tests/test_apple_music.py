import pytest
import os
import requests
from app import create_app
from cache_extension import cache
from blueprints.billboard_api import AppleMusicService

@pytest.fixture
def app_context():
    """Create Flask app context for testing"""
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        cache.clear()
        yield
        cache.clear()

@pytest.fixture
def skip_if_no_credentials():
    """Skip test if Apple Music credentials are missing"""
    if not all([
        os.getenv("APPLE_MUSIC_KEY_ID"),
        os.getenv("APPLE_MUSIC_TEAM_ID"),
        os.getenv("APPLE_MUSIC_AUTH_KEY")
    ]):
        pytest.skip("Apple Music credentials not available")

@pytest.mark.parametrize("clear_cache", [False, True])
def test_token_generation_and_caching(app_context, skip_if_no_credentials, clear_cache):
    """Test Apple Music token generation and caching"""
    # Arrange
    if clear_cache:
        cache.delete("apple_music:token")
    
    # Act - First token request
    token1 = AppleMusicService.get_token()
    
    # Assert - Token is valid
    assert token1 is not None
    assert cache.get("apple_music:token") == token1
    
    # Verify token is cached properly
    token2 = AppleMusicService.get_token()
    assert token2 == token1

def test_token_jwt_format(app_context, skip_if_no_credentials):
    """Test that the generated token has a valid JWT format"""
    # Act
    token = AppleMusicService.get_token()
    
    # Assert
    assert token is not None
    parts = token.split('.')
    assert len(parts) == 3  # Header, payload, signature

def test_missing_credentials(app_context, monkeypatch):
    """Test behavior when credentials are missing"""
    # Arrange - Save and remove credentials temporarily
    original_key_id = os.environ.get("APPLE_MUSIC_KEY_ID")
    original_team_id = os.environ.get("APPLE_MUSIC_TEAM_ID")
    
    try:
        monkeypatch.delenv("APPLE_MUSIC_KEY_ID", raising=False)
        monkeypatch.delenv("APPLE_MUSIC_TEAM_ID", raising=False)
        
        # Act
        token = AppleMusicService.get_token()
        
        # Assert
        assert token is None
    finally:
        # Restore environment
        if original_key_id:
            os.environ["APPLE_MUSIC_KEY_ID"] = original_key_id
        if original_team_id:
            os.environ["APPLE_MUSIC_TEAM_ID"] = original_team_id

@pytest.mark.parametrize("song,artist,should_exist", [
    ("Bohemian Rhapsody", "Queen", True),
    ("This Song Definitely Does Not Exist", "Nonexistent Artist", False)
])
def test_search_song(app_context, skip_if_no_credentials, song, artist, should_exist):
    """Test searching for songs on Apple Music"""
    # Act
    result = AppleMusicService.search_song(song, artist)
    
    # Assert
    if should_exist:
        assert result is not None
        assert "id" in result
        assert "url" in result
        assert "artwork_url" in result
    else:
        assert result is None
    
    # Verify caching
    cache_key = f"apple_music:search:{song}:{artist}"
    assert cache.get(cache_key) == result

def test_search_caching(app_context, skip_if_no_credentials, monkeypatch):
    """Test that search results are properly cached"""
    # Arrange
    song, artist = "Stairway to Heaven", "Led Zeppelin"
    
    # First search to populate cache
    result1 = AppleMusicService.search_song(song, artist)
    if result1 is None:
        pytest.skip("Song search returned no results - can't test caching")
    
    # Mock requests.get to ensure it's not called again
    original_get = requests.get
    monkeypatch.setattr(requests, 'get', 
                       lambda *args, **kwargs: pytest.fail("requests.get called when cache should be used"))
    
    try:
        # Act - Second search should use cache
        result2 = AppleMusicService.search_song(song, artist)
        
        # Assert
        assert result2 == result1
    finally:
        # Restore original function
        monkeypatch.setattr(requests, 'get', original_get)

@pytest.mark.parametrize("data_format", ["chart_format", "songs_format"])
def test_enrich_chart_data(app_context, skip_if_no_credentials, data_format):
    """Test enriching different chart data formats with Apple Music info"""
    # Arrange
    if data_format == "chart_format":
        sample_data = {
            "chart": {
                "entries": [
                    {"title": "Bohemian Rhapsody", "artist": "Queen"}
                ]
            }
        }
    else:
        sample_data = {
            "songs": [
                {"name": "Bohemian Rhapsody", "artist": "Queen"}
            ]
        }
    
    # Act
    enriched_data = AppleMusicService.enrich_chart_data(sample_data)
    
    # Assert
    assert enriched_data is not None
    
    # Check one song was enriched
    if data_format == "chart_format":
        entries = enriched_data["chart"]["entries"]
        has_apple_music = any("apple_music" in entry for entry in entries)
    else:
        songs = enriched_data["songs"]
        has_apple_music = any("apple_music" in song for song in songs)
    
    assert has_apple_music

def test_already_enriched_data(app_context, skip_if_no_credentials):
    """Test that already enriched data is not processed again"""
    # Arrange
    already_enriched = {
        "chart": {
            "entries": [
                {
                    "title": "Bohemian Rhapsody", 
                    "artist": "Queen",
                    "apple_music": {"id": "1234", "url": "http://example.com"}
                }
            ]
        }
    }
    
    # Act
    result = AppleMusicService.enrich_chart_data(already_enriched)
    
    # Assert - Data should be unchanged
    assert result == already_enriched

def test_api_error_handling(app_context, skip_if_no_credentials, monkeypatch):
    """Test error handling during Apple Music API calls"""
    # Arrange - Mock requests to raise an error
    def mock_error(*args, **kwargs):
        raise requests.exceptions.RequestException("API Error")
    
    monkeypatch.setattr(requests, 'get', mock_error)
    
    # Act
    result = AppleMusicService.search_song("Any Song", "Any Artist")
    
    # Assert - Should handle error gracefully
    assert result is None
    
    # Error result should be cached briefly
    cache_key = "apple_music:search:Any Song:Any Artist"
    assert cache.get(cache_key) is None