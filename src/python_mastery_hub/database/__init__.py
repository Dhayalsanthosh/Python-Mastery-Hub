# File: src/python_mastery_hub/database/__init__.py

"""Database package for Python Mastery Hub.

This package provides database configuration, connection management,
session handling, and utilities for the application.
"""

from .base import Base, get_database_url, create_engine_instance
from .connection import DatabaseManager, get_database_manager
from .session import get_session, get_async_session, SessionManager
from .utils import (
    create_tables,
    drop_tables,
    reset_database,
    check_database_connection,
    get_table_info,
    backup_database,
    restore_database
)

__all__ = [
    # Base configuration
    'Base',
    'get_database_url',
    'create_engine_instance',
    
    # Connection management
    'DatabaseManager',
    'get_database_manager',
    
    # Session management
    'get_session',
    'get_async_session',
    'SessionManager',
    
    # Utilities
    'create_tables',
    'drop_tables',
    'reset_database',
    'check_database_connection',
    'get_table_info',
    'backup_database',
    'restore_database'
]