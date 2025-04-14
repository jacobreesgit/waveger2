from flask import Flask
from blueprints.billboard_api import billboard_bp
import os
from cache_extension import cache

def create_app():
    # Create app
    app = Flask(__name__)
    
    # Configure cache for Redis Labs
    cache_config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": os.environ.get("REDIS_URL"),
        "CACHE_DEFAULT_TIMEOUT": 3600  # 1 hour
    }
    app.config.update(cache_config)
    
    # Initialize extensions with app
    cache.init_app(app)
    
    # Register blueprint
    app.register_blueprint(billboard_bp)
    
    return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)