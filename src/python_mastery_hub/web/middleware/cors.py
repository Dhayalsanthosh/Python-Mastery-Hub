# Location: src/python_mastery_hub/web/middleware/cors.py

"""
CORS Middleware

Handles Cross-Origin Resource Sharing (CORS) configuration for the API,
allowing controlled access from different domains and origins.
"""

from typing import List, Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from python_mastery_hub.core.config import get_settings
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


def get_allowed_origins() -> List[str]:
    """Get list of allowed origins based on environment."""
    base_origins = [
        "http://localhost:3000",  # React development server
        "http://localhost:8000",  # FastAPI development server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    if settings.environment == "development":
        # Allow more permissive origins in development
        development_origins = [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "http://0.0.0.0:*",
            "https://localhost:*",
            "https://127.0.0.1:*",
        ]
        base_origins.extend(development_origins)
    
    elif settings.environment == "production":
        # Strict origins in production
        production_origins = [
            "https://pythonmasteryhub.com",
            "https://www.pythonmasteryhub.com",
            "https://api.pythonmasteryhub.com",
        ]
        base_origins = production_origins
    
    elif settings.environment == "staging":
        # Staging-specific origins
        staging_origins = [
            "https://staging.pythonmasteryhub.com",
            "https://staging-api.pythonmasteryhub.com",
        ]
        base_origins.extend(staging_origins)
    
    # Add custom origins from environment variables
    if hasattr(settings, 'allowed_origins') and settings.allowed_origins:
        custom_origins = settings.allowed_origins.split(",")
        base_origins.extend([origin.strip() for origin in custom_origins])
    
    logger.info(f"Configured CORS allowed origins: {base_origins}")
    return base_origins


def get_trusted_hosts() -> List[str]:
    """Get list of trusted hosts for security."""
    base_hosts = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
    ]
    
    if settings.environment == "production":
        production_hosts = [
            "pythonmasteryhub.com",
            "www.pythonmasteryhub.com",
            "api.pythonmasteryhub.com",
        ]
        base_hosts.extend(production_hosts)
    
    elif settings.environment == "staging":
        staging_hosts = [
            "staging.pythonmasteryhub.com",
            "staging-api.pythonmasteryhub.com",
        ]
        base_hosts.extend(staging_hosts)
    
    # Add custom trusted hosts from environment variables
    if hasattr(settings, 'trusted_hosts') and settings.trusted_hosts:
        custom_hosts = settings.trusted_hosts.split(",")
        base_hosts.extend([host.strip() for host in custom_hosts])
    
    return base_hosts


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the FastAPI application."""
    
    # Get configuration
    allowed_origins = get_allowed_origins()
    trusted_hosts = get_trusted_hosts()
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,  # Allow cookies and authorization headers
        allow_methods=[
            "GET",
            "POST", 
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
            "HEAD"
        ],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "X-Request-ID",
            "Cache-Control",
            "Pragma",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Response-Time",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
        max_age=86400,  # 24 hours for preflight cache
    )
    
    # Add trusted host middleware for additional security
    if settings.environment in ["production", "staging"]:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=trusted_hosts
        )
    
    logger.info("CORS middleware configured successfully")


def setup_security_headers(app: FastAPI) -> None:
    """Add security headers middleware."""
    
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        }
        
        # Content Security Policy
        if settings.environment == "production":
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https:",
                "connect-src 'self' https://api.pythonmasteryhub.com",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
            security_headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # HSTS for HTTPS
        if request.url.scheme == "https":
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Add all security headers to response
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    logger.info("Security headers middleware configured")


def setup_request_id_middleware(app: FastAPI) -> None:
    """Add request ID middleware for tracing."""
    import uuid
    
    @app.middleware("http")
    async def add_request_id(request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Add to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    logger.info("Request ID middleware configured")


def setup_response_time_middleware(app: FastAPI) -> None:
    """Add response time measurement middleware."""
    import time
    
    @app.middleware("http")
    async def add_response_time(request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Response-Time"] = f"{process_time:.4f}s"
        
        return response
    
    logger.info("Response time middleware configured")


def setup_all_middleware(app: FastAPI) -> None:
    """Setup all middleware components."""
    # Order matters - add in reverse order of execution
    setup_response_time_middleware(app)
    setup_request_id_middleware(app)
    setup_security_headers(app)
    setup_cors(app)
    
    logger.info("All middleware components configured successfully")


class CORSConfig:
    """CORS configuration class for centralized management."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
    
    @property
    def allowed_origins(self) -> List[str]:
        """Get allowed origins."""
        return get_allowed_origins()
    
    @property
    def trusted_hosts(self) -> List[str]:
        """Get trusted hosts."""
        return get_trusted_hosts()
    
    def is_origin_allowed(self, origin: str) -> bool:
        """Check if an origin is allowed."""
        allowed = self.allowed_origins
        
        # Exact match
        if origin in allowed:
            return True
        
        # Wildcard matching for development
        if self.settings.environment == "development":
            for allowed_origin in allowed:
                if "*" in allowed_origin:
                    base = allowed_origin.replace("*", "")
                    if origin.startswith(base):
                        return True
        
        return False
    
    def validate_request_origin(self, origin: str) -> bool:
        """Validate request origin and log if suspicious."""
        if not origin:
            return True  # Allow requests without origin header
        
        is_allowed = self.is_origin_allowed(origin)
        
        if not is_allowed:
            self.logger.warning(f"Blocked request from unauthorized origin: {origin}")
        
        return is_allowed


# Global CORS configuration instance
cors_config = CORSConfig()