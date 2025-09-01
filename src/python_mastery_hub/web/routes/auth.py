# Location: src/python_mastery_hub/web/routes/auth.py

"""
Authentication Routes
Handles user authentication, registration, and profile management
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import re
import logging

from ..models.user import User
from ..models.session import UserSession
from ..services.auth_service import AuthService
from ..services.email_service import EmailService

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize services
auth_service = AuthService()
email_service = EmailService()

logger = logging.getLogger(__name__)

def login_required(f):
    """
    Decorator to require login for protected routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def guest_only(f):
    """
    Decorator to redirect logged-in users away from auth pages
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('dashboard.overview'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
@guest_only
def login():
    """
    User login page
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me', False)
        
        # Validation
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/login.html')
        
        try:
            # Authenticate user
            user = auth_service.authenticate_user(email, password)
            
            if user:
                # Create session
                session_data = auth_service.create_session(
                    user.id, 
                    request.remote_addr,
                    request.headers.get('User-Agent', ''),
                    remember_me
                )
                
                # Set session variables
                session['user_id'] = user.id
                session['username'] = user.username
                session['session_token'] = session_data['token']
                
                # Set session expiry
                if remember_me:
                    session.permanent = True
                
                logger.info(f"User {user.username} logged in successfully")
                flash(f'Welcome back, {user.username}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard.overview'))
            else:
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
@guest_only
def register():
    """
    User registration page
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms_accepted = request.form.get('terms_accepted', False)
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Please enter a valid email address.')
        
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if not terms_accepted:
            errors.append('You must accept the terms and conditions.')
        
        # Check password strength
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter.')
        
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        try:
            # Check if user already exists
            if auth_service.user_exists(email=email):
                flash('An account with this email already exists.', 'error')
                return render_template('auth/register.html')
            
            if auth_service.user_exists(username=username):
                flash('This username is already taken.', 'error')
                return render_template('auth/register.html')
            
            # Create user
            user = auth_service.create_user(
                username=username,
                email=email,
                password=password
            )
            
            if user:
                logger.info(f"New user registered: {username} ({email})")
                
                # Send welcome email
                try:
                    email_service.send_welcome_email(user.email, user.username)
                except Exception as e:
                    logger.warning(f"Failed to send welcome email: {str(e)}")
                
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Registration failed. Please try again.', 'error')
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout
    """
    try:
        # Invalidate session in database
        if 'session_token' in session:
            auth_service.invalidate_session(session['session_token'])
        
        username = session.get('username', 'User')
        
        # Clear session
        session.clear()
        
        logger.info(f"User {username} logged out")
        flash('You have been logged out successfully.', 'info')
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        session.clear()
        flash('Logged out.', 'info')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """
    User profile page
    """
    try:
        user = auth_service.get_user_by_id(session['user_id'])
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.logout'))
        
        # Get user statistics
        stats = auth_service.get_user_stats(user.id)
        
        return render_template('auth/profile.html', user=user, stats=stats)
        
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        flash('Error loading profile.', 'error')
        return redirect(url_for('dashboard.overview'))

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit user profile
    """
    try:
        user = auth_service.get_user_by_id(session['user_id'])
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.logout'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            errors = []
            
            if not username or len(username) < 3:
                errors.append('Username must be at least 3 characters long.')
            
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                errors.append('Username can only contain letters, numbers, and underscores.')
            
            if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                errors.append('Please enter a valid email address.')
            
            # Check if username/email changed and if they're available
            if username != user.username:
                if auth_service.user_exists(username=username):
                    errors.append('This username is already taken.')
            
            if email != user.email:
                if auth_service.user_exists(email=email):
                    errors.append('An account with this email already exists.')
            
            # Password change validation
            if new_password:
                if not current_password:
                    errors.append('Current password is required to change password.')
                elif not check_password_hash(user.password_hash, current_password):
                    errors.append('Current password is incorrect.')
                elif len(new_password) < 8:
                    errors.append('New password must be at least 8 characters long.')
                elif new_password != confirm_password:
                    errors.append('New passwords do not match.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('auth/profile.html', user=user, editing=True)
            
            # Update user
            updates = {
                'username': username,
                'email': email
            }
            
            if new_password:
                updates['password'] = new_password
            
            success = auth_service.update_user(user.id, updates)
            
            if success:
                # Update session if username changed
                if username != user.username:
                    session['username'] = username
                
                logger.info(f"User {user.username} updated profile")
                flash('Profile updated successfully.', 'success')
                return redirect(url_for('auth.profile'))
            else:
                flash('Failed to update profile.', 'error')
        
        return render_template('auth/profile.html', user=user, editing=True)
        
    except Exception as e:
        logger.error(f"Edit profile error: {str(e)}")
        flash('Error updating profile.', 'error')
        return redirect(url_for('auth.profile'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@guest_only
def forgot_password():
    """
    Forgot password page
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('auth/forgot_password.html')
        
        try:
            # Generate reset token
            success = auth_service.request_password_reset(email)
            
            if success:
                flash('If an account with this email exists, you will receive password reset instructions.', 'info')
            else:
                # Don't reveal if email exists or not
                flash('If an account with this email exists, you will receive password reset instructions.', 'info')
            
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@guest_only
def reset_password(token):
    """
    Reset password with token
    """
    try:
        # Verify token
        user = auth_service.verify_password_reset_token(token)
        
        if not user:
            flash('Invalid or expired reset link.', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        if request.method == 'POST':
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            if not password or len(password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return render_template('auth/reset_password.html', token=token)
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('auth/reset_password.html', token=token)
            
            # Reset password
            success = auth_service.reset_password(token, password)
            
            if success:
                logger.info(f"Password reset successful for user {user.username}")
                flash('Password reset successfully. Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Failed to reset password. Please try again.', 'error')
        
        return render_template('auth/reset_password.html', token=token)
        
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('auth.forgot_password'))

@auth_bp.route('/check-username')
def check_username():
    """
    API endpoint to check username availability
    """
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3:
        return jsonify({'available': False, 'message': 'Username must be at least 3 characters'})
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'available': False, 'message': 'Username can only contain letters, numbers, and underscores'})
    
    try:
        exists = auth_service.user_exists(username=username)
        return jsonify({
            'available': not exists,
            'message': 'Username is available' if not exists else 'Username is already taken'
        })
    except Exception as e:
        logger.error(f"Username check error: {str(e)}")
        return jsonify({'available': False, 'message': 'Error checking username'})

@auth_bp.route('/check-email')
def check_email():
    """
    API endpoint to check email availability
    """
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'available': False, 'message': 'Invalid email format'})
    
    try:
        exists = auth_service.user_exists(email=email)
        return jsonify({
            'available': not exists,
            'message': 'Email is available' if not exists else 'Email is already registered'
        })
    except Exception as e:
        logger.error(f"Email check error: {str(e)}")
        return jsonify({'available': False, 'message': 'Error checking email'})

# Template context processors
@auth_bp.context_processor
def inject_user():
    """
    Inject current user into all templates
    """
    user = None
    if 'user_id' in session:
        try:
            user = auth_service.get_user_by_id(session['user_id'])
        except Exception as e:
            logger.error(f"Error getting user for template: {str(e)}")
    
    return {'current_user': user}

# Error handlers
@auth_bp.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500