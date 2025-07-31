from flask import Flask
from flask_cors import CORS
from app.views.image_views import image_bp


def create_app():
    """Application factory pattern for Flask app creation"""
    app = Flask(__name__)
    
    # Enable CORS for cross-origin requests (Next.js and Android)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(image_bp, url_prefix='/api')
    
    return app 