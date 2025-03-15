from flask import Flask
from core.security.encryption import decrypt_log
from config.config import Config
import logging

def create_app():
    """Initialize the Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    
    # Register blueprints here if needed
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app