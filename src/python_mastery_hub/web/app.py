# Location: src/python_mastery_hub/web/app.py

"""
Flask Application Factory for Python Mastery Hub
Creates and configures the Flask application with all components
"""

import os
import logging
from datetime import timedelta
from flask import Flask, render_template, session, redirect, url_for, flash, request

from .config.database import init_db
from .config.security import configure_security  
from .config.cache import init_cache
from .routes import register_blueprints
from .middleware.auth import init_auth_middleware
from .middleware.cors import init_cors
from .middleware.rate_limiting import init_rate_limiting
from .middleware.error_handling import init_error_handlers

def create_app(config_name='development'):
    """
    Application factory function
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configure application
    configure_app(app, config_name)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup middleware
    init_middleware(app)
    
    # Configure error handlers
    init_global_error_handlers(app)
    
    # Add template context processors
    register_template_processors(app)
    
    # Register main routes
    register_main_routes(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Configure logging
    configure_logging(app)
    
    return app

def configure_app(app, config_name):
    """Configure Flask application settings"""
    
    # Base configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_COOKIE_SECURE'] = config_name == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Database configuration
    if config_name == 'production':
        app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///production.db')
        app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    elif config_name == 'testing':
        app.config['DATABASE_URL'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
    else:  # development
        app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///development.db')
        app.config['DEBUG'] = True
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@pythonmasteryhub.com')
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Rate limiting configuration
    app.config['RATELIMIT_STORAGE_URL'] = os.environ.get('REDIS_URL', 'memory://')
    app.config['RATELIMIT_DEFAULT'] = '100 per hour'
    
    # Code execution security
    app.config['CODE_EXECUTION_TIMEOUT'] = 30  # seconds
    app.config['CODE_EXECUTION_MEMORY_LIMIT'] = 128  # MB
    
    # Feature flags
    app.config['ENABLE_REGISTRATION'] = os.environ.get('ENABLE_REGISTRATION', 'true').lower() == 'true'
    app.config['ENABLE_EMAIL_VERIFICATION'] = os.environ.get('ENABLE_EMAIL_VERIFICATION', 'false').lower() == 'true'
    app.config['ENABLE_MAINTENANCE_MODE'] = os.environ.get('ENABLE_MAINTENANCE_MODE', 'false').lower() == 'true'

def init_extensions(app):
    """Initialize Flask extensions"""
    
    # Initialize database
    init_db(app)
    
    # Initialize caching
    init_cache(app)
    
    # Configure security
    configure_security(app)

def init_middleware(app):
    """Initialize middleware components"""
    
    # CORS middleware
    init_cors(app)
    
    # Authentication middleware
    init_auth_middleware(app)
    
    # Rate limiting middleware
    init_rate_limiting(app)

def register_template_processors(app):
    """Register template context processors"""
    
    @app.context_processor
    def inject_global_vars():
        """Inject global variables into all templates"""
        return {
            'app_name': 'Python Mastery Hub',
            'app_version': '1.0.0',
            'current_year': 2024,
            'enable_registration': app.config.get('ENABLE_REGISTRATION', True),
            'maintenance_mode': app.config.get('ENABLE_MAINTENANCE_MODE', False)
        }
    
    @app.context_processor
    def inject_user_session():
        """Inject user session data into templates"""
        user_data = {}
        if 'user_id' in session:
            user_data = {
                'logged_in': True,
                'user_id': session['user_id'],
                'username': session.get('username', ''),
                'is_admin': session.get('is_admin', False)
            }
        else:
            user_data = {'logged_in': False}
        
        return {'user_session': user_data}

def configure_logging(app):
    """Configure application logging"""
    
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/python_mastery_hub.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Python Mastery Hub startup')

def init_global_error_handlers(app):
    """Initialize global error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        return render_template('errors/429.html'), 429

def register_main_routes(app):
    """Register main application routes"""
    
    @app.route('/')
    def index():
        """Main landing page"""
        if 'user_id' in session:
            return redirect(url_for('dashboard.overview'))
        return render_template('index.html')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': '2024-01-01T00:00:00Z'
        }
    
    @app.before_request
    def check_maintenance_mode():
        """Check if application is in maintenance mode"""
        if app.config.get('ENABLE_MAINTENANCE_MODE', False):
            # Allow admin access during maintenance
            if 'user_id' in session and session.get('is_admin', False):
                return None
            
            # Allow health check during maintenance
            if request.endpoint == 'health_check':
                return None
            
            return render_template('maintenance.html'), 503
    
    @app.before_request
    def load_user():
        """Load user data for each request"""
        if 'user_id' in session:
            try:
                from .services.auth_service import AuthService
                auth_service = AuthService()
                user = auth_service.get_user_by_id(session['user_id'])
                
                if not user or not user.is_active:
                    session.clear()
                    flash('Your session has expired. Please log in again.', 'warning')
                    return redirect(url_for('auth.login'))
                
                # Update last seen
                auth_service.update_last_seen(user.id)
                
            except Exception as e:
                app.logger.error(f"Error loading user: {str(e)}")
                session.clear()

def register_cli_commands(app):
    """Register CLI commands"""
    
    @app.cli.command()
    def init_db_command():
        """Initialize the database"""
        try:
            from .models import create_tables
            create_tables()
            print('Database initialized successfully.')
        except ImportError:
            print('Database models not found. Skipping database initialization.')
    
    @app.cli.command()
    def create_admin():
        """Create admin user"""
        from .services.auth_service import AuthService
        
        username = input('Admin username: ')
        email = input('Admin email: ')
        password = input('Admin password: ')
        
        auth_service = AuthService()
        user = auth_service.create_user(
            username=username,
            email=email,
            password=password,
            is_admin=True
        )
        
        if user:
            print(f'Admin user {username} created successfully.')
        else:
            print('Failed to create admin user.')
    
    @app.cli.command()
    def seed_data():
        """Seed database with sample data"""
        try:
            from .services.progress_service import ProgressService
            
            progress_service = ProgressService()
            # Add sample exercises, modules, etc.
            print('Sample data seeded successfully.')
        except ImportError:
            print('Progress service not found. Skipping data seeding.')

# Create default app instance
def create_default_app():
    """Create application with default configuration"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    return create_app(config_name)

# Export the app creation function
__all__ = ['create_app', 'create_default_app']