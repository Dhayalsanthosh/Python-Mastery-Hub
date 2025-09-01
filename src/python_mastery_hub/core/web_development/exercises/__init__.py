"""
Web Development Exercises.

Comprehensive hands-on exercises for web development learning.
Each exercise is implemented in its own module with complete
starter code, implementation guides, and testing instructions.
"""

from .rest_api_exercise import get_exercise as rest_api_exercise
from .websocket_chat_exercise import get_exercise as websocket_chat_exercise  
from .jwt_auth_exercise import get_exercise as jwt_auth_exercise
from .flask_blog_exercise import get_exercise as flask_blog_exercise
from .microservice_exercise import get_exercise as microservice_exercise

__all__ = [
    "rest_api_exercise",
    "websocket_chat_exercise",
    "jwt_auth_exercise",
    "flask_blog_exercise",
    "microservice_exercise"
]