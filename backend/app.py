from flask import Flask
from blueprints.billboard_api import billboard_bp
import os
from flask_caching import Cache

# Create app
app = Flask(__name__)

# Configure cache for Redis Labs
cache_config = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": os.environ.get("REDIS_URL"),
    "CACHE_DEFAULT_TIMEOUT": 3600  # 1 hour
}
cache = Cache(app, config=cache_config)

# Register blueprint
app.register_blueprint(billboard_bp)

# Make cache available to blueprint
app.extensions['cache'] = cache

if __name__ == '__main__':
    app.run(debug=True)