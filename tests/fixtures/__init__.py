# tests/fixtures/__init__.py
# Fixtures package initialization

"""
Test fixtures package for the Python learning platform.

This package contains reusable test fixtures organized by category:
- database.py: Database-related fixtures
- users.py: User model and authentication fixtures  
- exercises.py: Exercise and learning content fixtures

All fixtures can be imported directly from this package for convenience.
"""

from .database import *
from .users import *
from .exercises import *

__all__ = [
    # Database fixtures
    'db_session',
    'test_database',
    'clean_database',
    'sample_db_data',
    
    # User fixtures
    'test_user',
    'admin_user',
    'multiple_users',
    'authenticated_user_session',
    
    # Exercise fixtures
    'sample_exercise',
    'exercise_set',
    'completed_exercise',
    'exercise_with_hints',
    'multilevel_exercises',
]