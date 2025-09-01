# Location: src/python_mastery_hub/web/middleware/error_handling.py

"""
Error Handling Middleware

Centralized error handling for the FastAPI application, including
custom exception handlers, logging, and user-friendly error responses.
"""

import traceback
from typing import Dict, Any, Optional, Union
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError as PydanticValidationError

from python_mastery_hub.utils.logging_config import get_logger
from python_mastery_hub.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class BaseAPIException(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationException(BaseAPIException):
    """Authentication related errors."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(BaseAPIException):
    """Authorization related errors."""
    
    def __init__(self, message: str = "Access forbidden", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ResourceNotFoundException(BaseAPIException):
    """Resource not found errors."""
    
    def __init__(self, resource: str, identifier: str = "", details: Optional[Dict] = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details=details or {"resource": resource, "identifier": identifier}
        )


class ValidationException(BaseAPIException):
    """Data validation errors."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class BusinessLogicException(BaseAPIException):
    """Business logic errors."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details
        )


class RateLimitException(BaseAPIException):
    """Rate limiting errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )


class ServiceUnavailableException(BaseAPIException):
    """Service unavailable errors."""
    
    def __init__(self, message: str = "Service temporarily unavailable", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
            details=details
        )


class CodeExecutionException(BaseAPIException):
    """Code execution related errors."""
    
    def __init__(self, message: str = "Code execution failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="CODE_EXECUTION_ERROR",
            details=details
        )


def create_error_response(
    error: Union[Exception, BaseAPIException],
    request: Optional[Request] = None,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """Create standardized error response."""
    
    # Get request ID if available
    request_id = None
    if request and hasattr(request.state, "request_id"):
        request_id = request.state.request_id
    
    # Base error response structure
    error_response = {
        "error": True,
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
    }
    
    if isinstance(error, BaseAPIException):
        # Custom API exceptions
        error_response.update({
            "error_code": error.error_code,
            "message": error.message,
            "status_code": error.status_code,
            "details": error.details
        })
    elif isinstance(error, HTTPException):
        # FastAPI HTTP exceptions
        error_response.update({
            "error_code": "HTTP_ERROR",
            "message": error.detail,
            "status_code": error.status_code,
            "details": {}
        })
    elif isinstance(error, StarletteHTTPException):
        # Starlette HTTP exceptions
        error_response.update({
            "error_code": "HTTP_ERROR",
            "message": error.detail,
            "status_code": error.status_code,
            "details": {}
        })
    else:
        # Generic exceptions
        error_response.update({
            "error_code": "INTERNAL_ERROR",
            "message": "An internal error occurred",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "details": {}
        })
    
    # Add traceback in development mode
    if include_traceback and settings.environment == "development":
        error_response["traceback"] = traceback.format_exc()
    
    # Add user-friendly message for common errors
    if error_response["status_code"] == 404:
        error_response["user_message"] = "The requested resource was not found."
    elif error_response["status_code"] == 401:
        error_response["user_message"] = "Please log in to access this resource."
    elif error_response["status_code"] == 403:
        error_response["user_message"] = "You don't have permission to access this resource."
    elif error_response["status_code"] == 429:
        error_response["user_message"] = "Too many requests. Please try again later."
    elif error_response["status_code"] >= 500:
        error_response["user_message"] = "We're experiencing technical difficulties. Please try again later."
    
    return error_response


async def log_error(error: Exception, request: Optional[Request] = None):
    """Log error with contextual information."""
    
    # Gather context
    context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if request:
        context.update({
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "request_id": getattr(request.state, "request_id", None),
        })
        
        # Add user info if available
        if hasattr(request.state, "user"):
            user = request.state.user
            context["user_id"] = user.id
            context["username"] = user.username
    
    # Log based on error severity
    if isinstance(error, BaseAPIException):
        if error.status_code >= 500:
            logger.error(f"Server error: {error.message}", extra=context)
        elif error.status_code >= 400:
            logger.warning(f"Client error: {error.message}", extra=context)
        else:
            logger.info(f"API error: {error.message}", extra=context)
    else:
        logger.error(f"Unhandled exception: {str(error)}", extra=context, exc_info=True)


async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handler for custom API exceptions."""
    await log_error(exc, request)
    
    error_response = create_error_response(
        exc,
        request,
        include_traceback=settings.environment == "development"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for FastAPI HTTP exceptions."""
    await log_error(exc, request)
    
    error_response = create_error_response(exc, request)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler for Starlette HTTP exceptions."""
    await log_error(exc, request)
    
    error_response = create_error_response(exc, request)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for request validation errors."""
    await log_error(exc, request)
    
    # Format validation errors
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    error_response = create_error_response(
        ValidationException("Request validation failed", {"validation_errors": validation_errors}),
        request
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def pydantic_validation_exception_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    """Handler for Pydantic validation errors."""
    await log_error(exc, request)
    
    # Format validation errors
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = create_error_response(
        ValidationException("Data validation failed", {"validation_errors": validation_errors}),
        request
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unhandled exceptions."""
    await log_error(exc, request)
    
    error_response = create_error_response(
        exc,
        request,
        include_traceback=settings.environment == "development"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


def setup_error_handlers(app: FastAPI) -> None:
    """Setup all error handlers for the FastAPI application."""
    
    # Custom API exceptions
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(AuthenticationException, base_api_exception_handler)
    app.add_exception_handler(AuthorizationException, base_api_exception_handler)
    app.add_exception_handler(ResourceNotFoundException, base_api_exception_handler)
    app.add_exception_handler(ValidationException, base_api_exception_handler)
    app.add_exception_handler(BusinessLogicException, base_api_exception_handler)
    app.add_exception_handler(RateLimitException, base_api_exception_handler)
    app.add_exception_handler(ServiceUnavailableException, base_api_exception_handler)
    app.add_exception_handler(CodeExecutionException, base_api_exception_handler)
    
    # FastAPI exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, pydantic_validation_exception_handler)
    
    # Generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Error handlers configured successfully")


def setup_error_monitoring_middleware(app: FastAPI) -> None:
    """Setup middleware for error monitoring and alerting."""
    
    @app.middleware("http")
    async def error_monitoring_middleware(request: Request, call_next):
        try:
            response = await call_next(request)
            
            # Monitor for high error rates
            if response.status_code >= 500:
                # In production, you might want to send alerts here
                logger.warning(f"Server error detected: {response.status_code} for {request.url}")
            
            return response
        
        except Exception as e:
            # Log unhandled exceptions that bypass other handlers
            await log_error(e, request)
            
            # Re-raise to let error handlers deal with it
            raise
    
    logger.info("Error monitoring middleware configured")


class ErrorContext:
    """Context manager for handling errors with additional context."""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            # Add operation context to the exception
            if hasattr(exc_val, 'details'):
                exc_val.details.update({
                    "operation": self.operation,
                    **self.context
                })
            
            # Log the error with context
            logger.error(f"Error in {self.operation}: {exc_val}", extra=self.context)
        
        # Don't suppress the exception
        return False


# Utility function for raising common errors
def raise_not_found(resource: str, identifier: str = ""):
    """Raise a standardized not found error."""
    raise ResourceNotFoundException(resource, identifier)


def raise_validation_error(message: str, details: Optional[Dict] = None):
    """Raise a standardized validation error."""
    raise ValidationException(message, details)


def raise_business_error(message: str, details: Optional[Dict] = None):
    """Raise a standardized business logic error."""
    raise BusinessLogicException(message, details)


def raise_auth_error(message: str = "Authentication failed"):
    """Raise a standardized authentication error."""
    raise AuthenticationException(message)


def raise_permission_error(message: str = "Access forbidden"):
    """Raise a standardized authorization error."""
    raise AuthorizationException(message)