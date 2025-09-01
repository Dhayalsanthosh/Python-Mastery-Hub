"""
Python Mastery Hub Web Application Package

FastAPI-based web application providing REST API and web interface
for the Python learning platform.
"""

from .app import app, create_app

__version__ = "1.0.0"
__description__ = "Python Mastery Hub Web Application"

# Export main application components
__all__ = [
    "app",
    "create_app",
]