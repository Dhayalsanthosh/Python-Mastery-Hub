# Location: src/python_mastery_hub/web/routes/__init__.py

"""
Routes Module
Centralizes all route blueprints for the Python Mastery Hub web application
"""

from flask import Blueprint
from .auth import auth_bp
from .dashboard import dashboard_bp
from .exercises import exercises_bp
from .modules import modules_bp
from .admin import admin_bp
from .api import api_bp

def register_blueprints(app):
    """
    Register all blueprints with the Flask application
    
    Args:
        app: Flask application instance
    """
    # Main application routes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(exercises_bp, url_prefix='/exercises')
    app.register_blueprint(modules_bp, url_prefix='/modules')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # API routes
    app.register_blueprint(api_bp, url_prefix='/api')

# Route groups for easy access
__all__ = [
    'auth_bp',
    'dashboard_bp', 
    'exercises_bp',
    'modules_bp',
    'admin_bp',
    'api_bp',
    'register_blueprints'
]