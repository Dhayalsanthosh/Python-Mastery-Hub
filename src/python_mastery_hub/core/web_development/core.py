"""
Web Development Learning Module Core.

Main WebDevelopment class with minimal orchestration logic.
"""

from typing import Dict, List, Any
from python_mastery_hub.core import LearningModule
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


class WebDevelopment(LearningModule):
    """Interactive learning module for Web Development with Python."""
    
    def __init__(self):
        super().__init__(
            name="Web Development",
            description="Master web development with Flask, FastAPI, REST APIs, and more",
            difficulty="intermediate"
        )
    
    def _setup_module(self) -> None:
        """Setup examples and exercises for web development."""
        self.examples = {
            "flask_basics": flask_examples.get_flask_basics(),
            "flask_advanced": flask_examples.get_flask_advanced(),
            "fastapi_fundamentals": fastapi_examples.get_fastapi_basics(),
            "fastapi_advanced": fastapi_examples.get_fastapi_advanced(),
            "rest_apis": rest_api_examples.get_rest_api_examples(),
            "websockets": websocket_examples.get_websocket_examples(),
            "authentication": auth_examples.get_auth_examples(),
            "database_integration": database_examples.get_database_examples(),
        }
        
        self.exercises = [
            {
                "topic": "rest_apis",
                "title": "Build a Complete REST API",
                "description": "Create a full-featured REST API with CRUD operations",
                "difficulty": "hard",
                "function": rest_api_exercise.get_exercise
            },
            {
                "topic": "websockets",
                "title": "Real-time Chat Application",
                "description": "Build a WebSocket-based chat system",
                "difficulty": "hard", 
                "function": websocket_chat_exercise.get_exercise
            },
            {
                "topic": "authentication",
                "title": "JWT Authentication System",
                "description": "Implement secure JWT-based authentication",
                "difficulty": "hard",
                "function": jwt_auth_exercise.get_exercise
            },
            {
                "topic": "flask_basics",
                "title": "Flask Blog Application",
                "description": "Build a complete blog with Flask",
                "difficulty": "medium",
                "function": flask_blog_exercise.get_exercise
            },
            {
                "topic": "fastapi_advanced",
                "title": "Microservice Architecture",
                "description": "Design and implement microservices with FastAPI",
                "difficulty": "expert",
                "function": microservice_exercise.get_exercise
            }
        ]
    
    def get_topics(self) -> List[str]:
        """Return list of topics covered in this module."""
        return [
            "flask_basics", 
            "flask_advanced",
            "fastapi_fundamentals", 
            "fastapi_advanced",
            "rest_apis", 
            "websockets", 
            "authentication", 
            "database_integration"
        ]
    
    def demonstrate(self, topic: str) -> Dict[str, Any]:
        """Demonstrate a specific topic with examples."""
        if topic not in self.examples:
            raise ValueError(f"Topic '{topic}' not found in web development module")
        
        return {
            "topic": topic,
            "examples": self.examples[topic],
            "explanation": self._get_topic_explanation(topic),
            "best_practices": self._get_best_practices(topic),
        }
    
    def _get_topic_explanation(self, topic: str) -> str:
        """Get detailed explanation for a topic."""
        explanations = {
            "flask_basics": "Flask provides a simple and flexible framework for building web applications with Python",
            "flask_advanced": "Advanced Flask features include blueprints, middleware, and application factories",
            "fastapi_fundamentals": "FastAPI provides automatic API documentation, request validation, and modern async support",
            "fastapi_advanced": "Advanced FastAPI includes dependency injection, background tasks, and middleware",
            "rest_apis": "REST APIs provide a standardized way to create web services with proper HTTP methods and status codes",
            "websockets": "WebSockets enable real-time bidirectional communication between client and server",
            "authentication": "JWT authentication provides secure, stateless user authentication for web APIs",
            "database_integration": "SQLAlchemy ORM provides powerful database integration with models and relationships"
        }
        return explanations.get(topic, "No explanation available")
    
    def _get_best_practices(self, topic: str) -> List[str]:
        """Get best practices for a topic."""
        practices = {
            "flask_basics": [
                "Use blueprints for modular application structure",
                "Implement proper error handling with custom error pages",
                "Use environment variables for configuration",
                "Implement CSRF protection for forms",
                "Use proper session management"
            ],
            "flask_advanced": [
                "Use application factories for better testing",
                "Implement proper logging and monitoring",
                "Use Flask-Migrate for database migrations",
                "Implement caching for better performance",
                "Use proper testing strategies"
            ],
            "fastapi_fundamentals": [
                "Use Pydantic models for request/response validation",
                "Implement proper dependency injection",
                "Use async/await for I/O operations",
                "Document your API with proper descriptions",
                "Handle exceptions with custom exception handlers"
            ],
            "fastapi_advanced": [
                "Use background tasks for async operations",
                "Implement proper middleware for cross-cutting concerns",
                "Use dependency injection for database connections",
                "Implement proper error handling strategies",
                "Use proper testing with TestClient"
            ],
            "rest_apis": [
                "Follow RESTful conventions for URL design",
                "Use appropriate HTTP status codes",
                "Implement proper pagination for list endpoints",
                "Version your APIs appropriately",
                "Provide comprehensive error messages"
            ],
            "websockets": [
                "Implement proper connection management",
                "Handle disconnections gracefully",
                "Use heartbeat/ping for connection health",
                "Implement proper message queuing",
                "Scale WebSocket connections with Redis or message brokers"
            ],
            "authentication": [
                "Use strong secret keys and rotate them regularly",
                "Implement proper token expiration",
                "Use refresh tokens for long-lived sessions",
                "Hash passwords with strong algorithms",
                "Implement rate limiting for auth endpoints"
            ],
            "database_integration": [
                "Use database migrations for schema changes",
                "Implement proper connection pooling",
                "Use database indexes for performance",
                "Handle database transactions properly",
                "Implement proper error handling for database operations"
            ]
        }
        return practices.get(topic, [])