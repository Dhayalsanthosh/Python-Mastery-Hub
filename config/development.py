# File: config/development.py
# Development environment configuration

import os
from datetime import timedelta

class DevelopmentConfig:
    """Development configuration settings"""
    
    # Environment
    ENV = 'development'
    DEBUG = True
    TESTING = False
    
    # Database
    DATABASE_URL = os.environ.get('DEV_DATABASE_URL') or 'postgresql://dev_user:dev_password@localhost:5432/app_dev'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Log SQL queries in development
    
    # Redis
    REDIS_URL = os.environ.get('DEV_REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Security
    SECRET_KEY = os.environ.get('DEV_SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('DEV_JWT_SECRET') or 'jwt-dev-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/development.log'
    
    # Email (using MailHog for development)
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'noreply@example.com'
    
    # File uploads
    UPLOAD_FOLDER = 'uploads/dev'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # API Rate limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100/hour"
    
    # External APIs
    EXTERNAL_API_TIMEOUT = 30
    
    # Development specific
    FLASK_RELOAD = True
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 5000
    
    # Monitoring
    SENTRY_DSN = None  # Disabled in development
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    @staticmethod
    def init_app(app):
        """Initialize application with development configuration"""
        # Development-specific initialization
        if not os.path.exists('logs'):
            os.makedirs('logs')
        if not os.path.exists('uploads/dev'):
            os.makedirs('uploads/dev')
        
        # Setup development logging
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )