# Test data constants for use across test files

# List of chart IDs to test with (representative sample)
TEST_CHART_IDS = [
    "hot-100",              # Hot 100
    "billboard-200",        # Billboard 200
    "artist-100",           # Artist 100
    "streaming-songs",      # Streaming Songs
    "digital-song-sales"    # Digital Song Sales
]

# Historical dates guaranteed to have data
HISTORICAL_TEST_DATES = [
    "2000-01-01",
    "2010-01-02",
    "2020-01-04"
]

# Error scenarios for testing error handling
ERROR_SCENARIOS = {
    "rate_limit": {
        "status_code": 429,
        "message": "Rate limit exceeded"
    },
    "server_error": {
        "status_code": 500,
        "message": "Internal server error"
    },
    "timeout": {
        "exception": "requests.exceptions.Timeout",
        "message": "Request timed out"
    },
    "connection_error": {
        "exception": "requests.exceptions.ConnectionError",
        "message": "Connection failed"
    }
}

# Cache key patterns
CACHE_KEY_PATTERNS = {
    "current_chart": "billboard:{chart_id}",
    "historical_chart": "billboard:{chart_id}:{week}",
    "apple_music_token": "apple_music:token",
    "apple_music_search": "apple_music:search:{title}:{artist}",
    "rate_limit_flag": "billboard:rate_limited"
}

# Test parameters for API requests
TEST_PARAMETERS = [
    # id, week, refresh, apple_music
    ("hot-100", None, "false", "true"),
    ("billboard-200", None, "false", "true"),
    ("hot-100", "2022-01-01", "false", "true"),
    ("hot-100", None, "true", "true"),
    ("hot-100", None, "false", "false")
]

# Sample songs for Apple Music tests
TEST_SONGS = [
    # title, artist, should_exist
    ("Bohemian Rhapsody", "Queen", True),
    ("Stairway to Heaven", "Led Zeppelin", True),
    ("Imagine", "John Lennon", True),
    ("This Is Not A Real Song Title", "Fake Artist Name", False)
]