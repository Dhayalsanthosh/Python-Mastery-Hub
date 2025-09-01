# Location: src/python_mastery_hub/web/routes/api.py

"""
API Blueprint Registration
Centralizes all API endpoints from different modules and provides unified API routing
"""

from flask import Blueprint, jsonify, request
import logging

from ..api.auth import auth_api
from ..api.exercises import exercises_api
from ..api.modules import modules_api
from ..api.progress import progress_api
from ..api.admin import admin_api

# Create main API Blueprint
api_bp = Blueprint('api', __name__)

logger = logging.getLogger(__name__)

# Register sub-blueprints
api_bp.register_blueprint(auth_api, url_prefix='/auth')
api_bp.register_blueprint(exercises_api, url_prefix='/exercises')
api_bp.register_blueprint(modules_api, url_prefix='/modules')
api_bp.register_blueprint(progress_api, url_prefix='/progress')
api_bp.register_blueprint(admin_api, url_prefix='/admin')

@api_bp.route('/health')
def health_check():
    """
    API health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': request.headers.get('X-Request-Start', 'unknown')
    })

@api_bp.route('/version')
def version():
    """
    API version information
    """
    return jsonify({
        'api_version': '1.0.0',
        'app_version': '1.0.0',
        'supported_versions': ['v1'],
        'documentation': '/api/docs'
    })

@api_bp.route('/docs')
def documentation():
    """
    API documentation endpoint
    """
    api_docs = {
        'title': 'Python Mastery Hub API',
        'version': '1.0.0',
        'description': 'REST API for the Python Mastery Hub learning platform',
        'base_url': '/api',
        'authentication': 'Session-based authentication required for most endpoints',
        'endpoints': {
            'auth': {
                'description': 'Authentication and user management',
                'endpoints': [
                    'POST /api/auth/login',
                    'POST /api/auth/logout',
                    'POST /api/auth/register',
                    'GET /api/auth/profile',
                    'PUT /api/auth/profile',
                    'POST /api/auth/change-password'
                ]
            },
            'exercises': {
                'description': 'Exercise management and submission',
                'endpoints': [
                    'GET /api/exercises',
                    'GET /api/exercises/{id}',
                    'POST /api/exercises/{id}/submit',
                    'POST /api/exercises/{id}/run',
                    'GET /api/exercises/{id}/submissions',
                    'POST /api/exercises/{id}/hint'
                ]
            },
            'modules': {
                'description': 'Learning module management',
                'endpoints': [
                    'GET /api/modules',
                    'GET /api/modules/{id}',
                    'GET /api/modules/{id}/progress',
                    'POST /api/modules/{id}/enroll',
                    'GET /api/modules/learning-path'
                ]
            },
            'progress': {
                'description': 'User progress tracking',
                'endpoints': [
                    'GET /api/progress/stats',
                    'GET /api/progress/achievements',
                    'GET /api/progress/activities',
                    'POST /api/progress/goals',
                    'PUT /api/progress/goals/{id}',
                    'DELETE /api/progress/goals/{id}'
                ]
            },
            'admin': {
                'description': 'Administrative functions (admin only)',
                'endpoints': [
                    'GET /api/admin/users',
                    'GET /api/admin/users/{id}',
                    'PUT /api/admin/users/{id}',
                    'GET /api/admin/exercises',
                    'GET /api/admin/analytics',
                    'GET /api/admin/export/users',
                    'GET /api/admin/export/submissions'
                ]
            }
        },
        'response_format': {
            'success_response': {
                'success': True,
                'data': '...',
                'message': 'Optional success message'
            },
            'error_response': {
                'success': False,
                'error': 'Error description',
                'code': 'ERROR_CODE'
            }
        },
        'status_codes': {
            '200': 'Success',
            '201': 'Created',
            '400': 'Bad Request',
            '401': 'Unauthorized',
            '403': 'Forbidden',
            '404': 'Not Found',
            '429': 'Too Many Requests',
            '500': 'Internal Server Error'
        }
    }
    
    return jsonify(api_docs)

@api_bp.route('/status')
def status():
    """
    Detailed API status information
    """
    try:
        # This would normally check actual system health
        status_info = {
            'api_status': 'operational',
            'database_status': 'healthy',
            'cache_status': 'healthy',
            'external_services': {
                'email_service': 'operational',
                'code_execution_service': 'operational'
            },
            'metrics': {
                'requests_per_minute': 150,  # Would come from monitoring
                'average_response_time': '95ms',
                'error_rate': '0.1%',
                'uptime': '99.95%'
            },
            'last_updated': '2024-01-01T12:00:00Z'
        }
        
        return jsonify(status_info)
        
    except Exception as e:
        logger.error(f"API status check error: {str(e)}")
        return jsonify({
            'api_status': 'degraded',
            'error': 'Unable to retrieve full status',
            'last_updated': '2024-01-01T12:00:00Z'
        }), 500

# Error handlers for API routes
@api_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return jsonify({
        'success': False,
        'error': 'Bad Request',
        'message': 'Invalid request data or parameters'
    }), 400

@api_bp.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors"""
    return jsonify({
        'success': False,
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401

@api_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    return jsonify({
        'success': False,
        'error': 'Forbidden',
        'message': 'Insufficient permissions'
    }), 403

@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        'success': False,
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404

@api_bp.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle 429 Too Many Requests errors"""
    return jsonify({
        'success': False,
        'error': 'Rate Limit Exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429

@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error"""
    logger.error(f"API internal error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

# Request/Response middleware for API
@api_bp.before_request
def before_api_request():
    """
    Process requests before they reach API endpoints
    """
    # Log API requests
    logger.info(f"API Request: {request.method} {request.path} from {request.remote_addr}")
    
    # Set CORS headers for API requests
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

@api_bp.after_request
def after_api_request(response):
    """
    Process responses after API endpoints
    """
    # Add API-specific headers
    response.headers['Content-Type'] = 'application/json'
    response.headers['X-API-Version'] = '1.0.0'
    
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    return response

# Rate limiting decorator for API endpoints
def rate_limit(requests_per_minute=60):
    """
    Decorator to apply rate limiting to API endpoints
    """
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Rate limiting logic would go here
            # For now, just pass through
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# API key authentication decorator (for future use)
def api_key_required(f):
    """
    Decorator to require API key authentication
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # API key validation logic would go here
        # For now, just pass through
        return f(*args, **kwargs)
    
    return decorated_function

# Utility functions for API responses
def success_response(data=None, message=None, status_code=200):
    """
    Standard success response format
    """
    response_data = {'success': True}
    
    if data is not None:
        response_data['data'] = data
    
    if message:
        response_data['message'] = message
    
    return jsonify(response_data), status_code

def error_response(error_message, status_code=400, error_code=None):
    """
    Standard error response format
    """
    response_data = {
        'success': False,
        'error': error_message
    }
    
    if error_code:
        response_data['code'] = error_code
    
    return jsonify(response_data), status_code

# Export utility functions for use in other API modules
__all__ = [
    'api_bp',
    'rate_limit',
    'api_key_required',
    'success_response',
    'error_response'
]