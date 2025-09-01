# Location: src/python_mastery_hub/web/middleware/rate_limiting.py

"""
Rate Limiting Middleware

Implements rate limiting for API endpoints to prevent abuse and ensure
fair usage across users.
"""

from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, deque
from functools import wraps
import hashlib

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse

from python_mastery_hub.web.models.user import User
from python_mastery_hub.utils.logging_config import get_logger
from python_mastery_hub.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, limit: int, window: int, retry_after: int):
        self.limit = limit
        self.window = window
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded: {limit} requests per {window} seconds")


class TokenBucket:
    """Token bucket algorithm implementation for rate limiting."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = datetime.now()
        self.lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket."""
        async with self.lock:
            now = datetime.now()
            
            # Refill tokens based on time elapsed
            time_passed = (now - self.last_refill).total_seconds()
            self.tokens = min(
                self.capacity,
                self.tokens + (time_passed * self.refill_rate)
            )
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    @property
    def available_tokens(self) -> float:
        """Get current number of available tokens."""
        return self.tokens


class SlidingWindowLog:
    """Sliding window log algorithm for rate limiting."""
    
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def is_allowed(self) -> tuple[bool, int]:
        """Check if request is allowed and return remaining count."""
        async with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.window_seconds)
            
            # Remove old requests
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            
            # Check if we're under the limit
            if len(self.requests) < self.limit:
                self.requests.append(now)
                return True, self.limit - len(self.requests)
            
            return False, 0
    
    def time_until_reset(self) -> int:
        """Get seconds until the window resets."""
        if not self.requests:
            return 0
        
        oldest_request = self.requests[0]
        reset_time = oldest_request + timedelta(seconds=self.window_seconds)
        now = datetime.now()
        
        if reset_time > now:
            return int((reset_time - now).total_seconds())
        
        return 0


class RateLimiter:
    """Main rate limiter class."""
    
    def __init__(self):
        self.limiters: Dict[str, SlidingWindowLog] = {}
        self.cleanup_interval = 300  # Clean up every 5 minutes
        self.last_cleanup = datetime.now()
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate unique key for rate limiting."""
        return f"{identifier}:{endpoint}"
    
    def _cleanup_old_limiters(self):
        """Remove unused rate limiters to prevent memory leaks."""
        now = datetime.now()
        if (now - self.last_cleanup).total_seconds() < self.cleanup_interval:
            return
        
        keys_to_remove = []
        for key, limiter in self.limiters.items():
            if not limiter.requests or limiter.time_until_reset() == 0:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.limiters[key]
        
        self.last_cleanup = now
        logger.debug(f"Cleaned up {len(keys_to_remove)} unused rate limiters")
    
    async def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        limit: int,
        window: int
    ) -> tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limit."""
        key = self._get_key(identifier, endpoint)
        
        # Create limiter if it doesn't exist
        if key not in self.limiters:
            self.limiters[key] = SlidingWindowLog(limit, window)
        
        limiter = self.limiters[key]
        allowed, remaining = await limiter.is_allowed()
        
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + limiter.time_until_reset()),
            "X-RateLimit-Window": str(window)
        }
        
        # Periodic cleanup
        self._cleanup_old_limiters()
        
        return allowed, headers


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_identifier(request: Request, user: Optional[User] = None) -> str:
    """Get unique identifier for rate limiting."""
    if user and user.id:
        return f"user:{user.id}"
    
    # Use IP address as fallback
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Use first IP in case of multiple proxies
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    return f"ip:{client_ip}"


def get_endpoint_identifier(request: Request) -> str:
    """Get endpoint identifier for rate limiting."""
    method = request.method
    path = request.url.path
    
    # Hash long paths to keep keys manageable
    if len(path) > 100:
        path_hash = hashlib.md5(path.encode()).hexdigest()[:16]
        path = f"hashed:{path_hash}"
    
    return f"{method}:{path}"


# Rate limit configurations
RATE_LIMIT_CONFIGS = {
    # Authentication endpoints
    "POST:/auth/login": {"limit": 5, "window": 300},  # 5 attempts per 5 minutes
    "POST:/auth/register": {"limit": 3, "window": 3600},  # 3 attempts per hour
    "POST:/auth/forgot-password": {"limit": 3, "window": 3600},
    "POST:/auth/reset-password": {"limit": 5, "window": 3600},
    
    # API endpoints - general
    "default": {"limit": 100, "window": 60},  # 100 requests per minute
    
    # Code execution endpoints
    "POST:/exercises/execute": {"limit": 30, "window": 60},  # 30 executions per minute
    "POST:/exercises/*/submit": {"limit": 10, "window": 60},  # 10 submissions per minute
    
    # User-specific limits
    "authenticated": {"limit": 1000, "window": 3600},  # 1000 requests per hour for authenticated users
    "anonymous": {"limit": 100, "window": 3600},  # 100 requests per hour for anonymous users
    
    # Admin endpoints
    "admin": {"limit": 500, "window": 3600},  # 500 requests per hour for admin users
    
    # Search endpoints
    "GET:/search": {"limit": 50, "window": 60},  # 50 searches per minute
}


def get_rate_limit_config(endpoint: str, user: Optional[User] = None) -> Dict[str, int]:
    """Get rate limit configuration for endpoint and user."""
    # Check for specific endpoint configuration
    if endpoint in RATE_LIMIT_CONFIGS:
        return RATE_LIMIT_CONFIGS[endpoint]
    
    # Check for pattern matches
    for pattern, config in RATE_LIMIT_CONFIGS.items():
        if "*" in pattern:
            pattern_regex = pattern.replace("*", "[^/]+")
            import re
            if re.match(pattern_regex, endpoint):
                return config
    
    # User-based limits
    if user:
        if user.role.value == "admin":
            return RATE_LIMIT_CONFIGS["admin"]
        else:
            return RATE_LIMIT_CONFIGS["authenticated"]
    else:
        return RATE_LIMIT_CONFIGS["anonymous"]


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Rate limiting middleware."""
    try:
        # Skip rate limiting for certain paths
        skip_paths = ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Get user if authenticated
        user = getattr(request.state, "user", None)
        
        # Get identifiers
        client_id = get_client_identifier(request, user)
        endpoint_id = get_endpoint_identifier(request)
        
        # Get rate limit configuration
        config = get_rate_limit_config(endpoint_id, user)
        
        # Check rate limit
        allowed, headers = await rate_limiter.check_rate_limit(
            client_id,
            endpoint_id,
            config["limit"],
            config["window"]
        )
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_id} on {endpoint_id}")
            
            # Create rate limit exceeded response
            content = {
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {config['limit']} per {config['window']} seconds",
                "retry_after": headers["X-RateLimit-Reset"]
            }
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=content,
                headers=headers
            )
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header, value in headers.items():
            response.headers[header] = value
        
        return response
    
    except Exception as e:
        logger.error(f"Error in rate limiting middleware: {e}")
        # Continue without rate limiting if there's an error
        return await call_next(request)


def rate_limit(
    limit: int,
    window: int,
    per: str = "ip",
    key_func: Optional[Callable] = None
):
    """Decorator for applying rate limits to specific endpoints."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from arguments
            request = None
            user = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            for key, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                    break
                elif isinstance(value, User):
                    user = value
            
            if not request:
                # If no request found, proceed without rate limiting
                return await func(*args, **kwargs)
            
            # Determine identifier
            if key_func:
                identifier = key_func(request, user)
            elif per == "user" and user:
                identifier = f"user:{user.id}"
            else:
                identifier = get_client_identifier(request, user)
            
            endpoint = get_endpoint_identifier(request)
            
            # Check rate limit
            allowed, headers = await rate_limiter.check_rate_limit(
                identifier,
                endpoint,
                limit,
                window
            )
            
            if not allowed:
                retry_after = headers.get("X-RateLimit-Reset", "60")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {limit} requests per {window} seconds",
                    headers=headers
                )
            
            # Execute the original function
            result = await func(*args, **kwargs)
            
            # If result is a Response, add headers
            if hasattr(result, 'headers'):
                for header, value in headers.items():
                    result.headers[header] = value
            
            return result
        
        return wrapper
    return decorator


class RateLimitConfig:
    """Configuration class for rate limiting settings."""
    
    def __init__(self):
        self.configs = RATE_LIMIT_CONFIGS.copy()
    
    def add_limit(self, endpoint: str, limit: int, window: int):
        """Add or update rate limit for an endpoint."""
        self.configs[endpoint] = {"limit": limit, "window": window}
    
    def remove_limit(self, endpoint: str):
        """Remove rate limit for an endpoint."""
        if endpoint in self.configs:
            del self.configs[endpoint]
    
    def get_limit(self, endpoint: str, user: Optional[User] = None) -> Dict[str, int]:
        """Get rate limit configuration."""
        return get_rate_limit_config(endpoint, user)
    
    def update_config(self, new_config: Dict[str, Dict[str, int]]):
        """Update rate limit configuration."""
        self.configs.update(new_config)


# Global rate limit configuration
rate_limit_config = RateLimitConfig()