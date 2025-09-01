# Location: src/python_mastery_hub/web/middleware/__init__.py

"""
Web Middleware Package

Contains middleware components for authentication, CORS, rate limiting,
error handling, and other cross-cutting concerns.
"""

from .auth import get_current_user, require_admin, verify_token
from .cors import setup_cors
from .rate_limiting import RateLimiter, rate_limit
from .error_handling import setup_error_handlers

__all__ = [
    # Authentication middleware
    "get_current_user",
    "require_admin", 
    "verify_token",
    
    # CORS middleware
    "setup_cors",
    
    # Rate limiting middleware
    "RateLimiter",
    "rate_limit",
    
    # Error handling middleware
    "setup_error_handlers",
]