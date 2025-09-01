"""
API Package - REST API Endpoints

Contains all API route definitions for the Python Mastery Hub web application.
"""

from . import auth
from . import modules
from . import progress
from . import exercises
from . import admin

# Export API routers
__all__ = [
    "auth",
    "modules", 
    "progress",
    "exercises",
    "admin",
]