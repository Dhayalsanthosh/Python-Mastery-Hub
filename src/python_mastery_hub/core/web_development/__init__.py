"""
Web Development Learning Module.

Comprehensive coverage of web development with Python including Flask, FastAPI,
REST APIs, WebSockets, authentication, database integration, and deployment.
"""

from .core import WebDevelopment
from .examples import (
    flask_examples,
    fastapi_examples,
    rest_api_examples,
    websocket_examples,
    auth_examples,
    database_examples
)
from .exercises import (
    rest_api_exercise,
    websocket_chat_exercise,
    jwt_auth_exercise,
    flask_blog_exercise,
    microservice_exercise
)

__all__ = [
    "WebDevelopment",
    "flask_examples",
    "fastapi_examples", 
    "rest_api_examples",
    "websocket_examples",
    "auth_examples",
    "database_examples",
    "rest_api_exercise",
    "websocket_chat_exercise",
    "jwt_auth_exercise",
    "flask_blog_exercise",
    "microservice_exercise"
]