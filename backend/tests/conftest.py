import pytest
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse

# Add the parent directory to the Python path so tests can import modules from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('billboard_tests')

@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """
    Load test environment variables and configure testing environment.
    This runs automatically once at the beginning of the test session.
    """
    # First try .env.test, then fall back to .env
    env_paths = [Path('.env.test'), Path('.env')]
    env_file = next((path for path in env_paths if path.exists()), None)
    
    if env_file:
        logger.info(f"Loading environment from {env_file}")
        load_dotenv(dotenv_path=env_file)
    else:
        logger.warning("No .env or .env.test file found")
    
    # Check and log missing required variables
    required_vars = [
        'RAPID_API_KEY',
        'APPLE_MUSIC_KEY_ID',
        'APPLE_MUSIC_TEAM_ID',
        'APPLE_MUSIC_AUTH_KEY',
        'REDIS_URL'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.warning(f"Missing environment variables: {', '.join(missing)}")

@pytest.fixture(scope="session", autouse=True)
def configure_cache():
    """
    Configure caching for tests - use SimpleCache for tests instead of Redis.
    This avoids issues with Redis connection and makes tests more reliable.
    """
    logger.info("Using SimpleCache for tests")
    os.environ['CACHE_TYPE'] = 'SimpleCache'
    
    # Log the original Redis URL for reference
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        logger.info(f"Original REDIS_URL: {redis_url}")
    else:
        logger.warning("REDIS_URL not set")

@pytest.fixture
def sample_chart_data():
    """Return sample chart data for testing"""
    return {
        "chart": {
            "id": "hot-100",
            "name": "Hot 100",
            "date": "2025-04-08",
            "entries": [
                {
                    "rank": 1,
                    "title": "Test Song 1",
                    "artist": "Test Artist 1",
                    "weeks": 4,
                    "last": 1,
                    "peak": 1
                },
                {
                    "rank": 2,
                    "title": "Test Song 2",
                    "artist": "Test Artist 2",
                    "weeks": 10,
                    "last": 2,
                    "peak": 1
                }
            ]
        }
    }