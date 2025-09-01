# File: config/testing.py
# Testing environment configuration

import os
from datetime import timedelta

class TestingConfig:
    """Testing configuration settings"""
    
    # Environment
    ENV = 'testing'
    DEBUG = True
    TESTING = True
    
    # Database (using in-memory SQLite for fast tests)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Redis (using fake Redis for testing)
    REDIS_URL = 'redis://localhost:6379/15'  # Use separate Redis DB for tests
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
    CELERY_ALWAYS_EAGER = True  # Execute tasks synchronously in tests
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    
    # Security
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'jwt-test-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000']
    
    # Logging
    LOG_LEVEL = 'ERROR'  # Reduce noise in test output
    
    # Email (disable email sending in tests)
    MAIL_SUPPRESS_SEND = True
    MAIL_DEFAULT_SENDER = 'test@example.com'
    
    # File uploads
    UPLOAD_FOLDER = '/tmp/test_uploads'
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB for tests
    
    # API Rate limiting (disabled for tests)
    RATELIMIT_ENABLED = False
    
    # External APIs
    EXTERNAL_API_TIMEOUT = 5
    
    # Testing specific
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier testing
    
    # Cache (use simple cache for tests)
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60
    
    # Performance monitoring (disabled in tests)
    SENTRY_DSN = None
    
    # Test database options
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Disable security features for easier testing
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    
    @staticmethod
    def init_app(app):
        """Initialize application with testing configuration"""
        # Testing-specific initialization
        import logging
        
        # Setup minimal logging for tests
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        # Create test upload directory
        if not os.path.exists('/tmp/test_uploads'):
            os.makedirs('/tmp/test_uploads')
        
        # Patch external services for testing
        app.config['TESTING_PATCHES'] = []