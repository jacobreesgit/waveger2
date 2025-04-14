from flask import Flask
from blueprints.billboard_api import billboard_bp

# Create app
app = Flask(__name__)

# Register blueprint
app.register_blueprint(billboard_bp)

if __name__ == '__main__':
    app.run(debug=True)