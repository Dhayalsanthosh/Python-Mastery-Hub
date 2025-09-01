# Location: src/python_mastery_hub/web/routes/admin.py

"""
Admin Panel Routes
Handles administrative functions including user management, exercise management, and analytics
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, abort
from functools import wraps
from datetime import datetime, timedelta
import logging
import csv
import io

from ..models.user import User
from ..models.exercise import Exercise, ExerciseSubmission
from ..models.progress import UserProgress
from ..services.auth_service import AuthService
from ..services.progress_service import ProgressService
from .auth import login_required

# Create Blueprint
admin_bp = Blueprint('admin', __name__)

# Initialize services
auth_service = AuthService()
progress_service = ProgressService()

logger = logging.getLogger(__name__)

def admin_required(f):
    """
    Decorator to require admin privileges
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        user = auth_service.get_user_by_id(session['user_id'])
        if not user or not user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard.overview'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Admin dashboard overview
    """
    try:
        # Get overall platform statistics
        stats = {
            'total_users': User.get_total_count(),
            'active_users_today': User.get_active_users_count(days=1),
            'active_users_week': User.get_active_users_count(days=7),
            'active_users_month': User.get_active_users_count(days=30),
            'total_exercises': Exercise.get_total_count(),
            'total_submissions': ExerciseSubmission.get_total_count(),
            'submissions_today': ExerciseSubmission.get_submissions_count(days=1),
            'submissions_week': ExerciseSubmission.get_submissions_count(days=7)
        }
        
        # Get user growth data for charts
        user_growth = User.get_registration_growth(days=30)
        
        # Get submission activity data
        submission_activity = ExerciseSubmission.get_activity_data(days=30)
        
        # Get popular exercises
        popular_exercises = Exercise.get_popular_exercises(limit=10)
        
        # Get recent user registrations
        recent_users = User.get_recent_registrations(limit=10)
        
        # Get recent submissions
        recent_submissions = ExerciseSubmission.get_recent_submissions(limit=10)
        
        # Get system health metrics
        system_health = {
            'database_status': 'healthy',  # This would check actual DB status
            'average_response_time': '150ms',  # This would come from monitoring
            'error_rate': '0.02%',  # This would come from error tracking
            'uptime': '99.9%'  # This would come from uptime monitoring
        }
        
        context = {
            'stats': stats,
            'user_growth': user_growth,
            'submission_activity': submission_activity,
            'popular_exercises': popular_exercises,
            'recent_users': recent_users,
            'recent_submissions': recent_submissions,
            'system_health': system_health
        }
        
        return render_template('admin/dashboard.html', **context)
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        flash('Error loading admin dashboard.', 'error')
        return render_template('admin/dashboard.html', stats={})

@admin_bp.route('/users')
@admin_required
def manage_users():
    """
    User management page
    """
    try:
        # Get filter parameters
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '')  # active, inactive, banned
        role = request.args.get('role', '')  # admin, user
        sort_by = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build filter criteria
        filters = {
            'search': search,
            'status': status,
            'role': role,
            'sort_by': sort_by,
            'order': order
        }
        
        # Get users with pagination
        users_data = User.get_users_with_filters(
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        users = users_data['users']
        pagination = users_data['pagination']
        
        # Get user statistics for each user
        for user in users:
            user_stats = progress_service.get_user_stats(user['id'])
            user['stats'] = user_stats
        
        context = {
            'users': users,
            'pagination': pagination,
            'filters': filters,
            'statuses': ['active', 'inactive', 'banned'],
            'roles': ['user', 'admin']
        }
        
        return render_template('admin/users.html', **context)
        
    except Exception as e:
        logger.error(f"Admin users error: {str(e)}")
        flash('Error loading users.', 'error')
        return render_template('admin/users.html', users=[], pagination={})

@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """
    Detailed view of a specific user
    """
    try:
        # Get user data
        user = User.get_by_id(user_id)
        if not user:
            abort(404)
        
        # Get user progress and statistics
        user_stats = progress_service.get_detailed_user_stats(user_id)
        
        # Get user's recent activities
        activities = progress_service.get_recent_activities(user_id, limit=20)
        
        # Get user's submissions
        submissions = ExerciseSubmission.get_user_submissions(user_id, limit=20)
        
        # Get user's achievements
        achievements = progress_service.get_user_achievements(user_id)
        
        # Get user's session history
        sessions = auth_service.get_user_sessions(user_id, limit=10)
        
        context = {
            'user': user,
            'user_stats': user_stats,
            'activities': activities,
            'submissions': submissions,
            'achievements': achievements,
            'sessions': sessions
        }
        
        return render_template('admin/user_detail.html', **context)
        
    except Exception as e:
        logger.error(f"Admin user detail error: {str(e)}")
        flash('Error loading user details.', 'error')
        return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/update', methods=['POST'])
@admin_required
def update_user(user_id):
    """
    Update user information and status
    """
    try:
        # Get user
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get update data
        update_data = {
            'is_active': request.json.get('is_active', user.is_active),
            'is_admin': request.json.get('is_admin', user.is_admin),
            'username': request.json.get('username', user.username),
            'email': request.json.get('email', user.email)
        }
        
        # Validation
        if update_data['username'] != user.username:
            if auth_service.user_exists(username=update_data['username']):
                return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        if update_data['email'] != user.email:
            if auth_service.user_exists(email=update_data['email']):
                return jsonify({'success': False, 'error': 'Email already exists'}), 400
        
        # Update user
        success = auth_service.update_user(user_id, update_data)
        
        if success:
            logger.info(f"Admin updated user {user_id}: {update_data}")
            return jsonify({'success': True, 'message': 'User updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update user'}), 500
        
    except Exception as e:
        logger.error(f"Admin update user error: {str(e)}")
        return jsonify({'success': False, 'error': 'Update failed'}), 500

@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@admin_required
def ban_user(user_id):
    """
    Ban/unban a user
    """
    try:
        # Get user
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Prevent self-ban
        if user_id == session['user_id']:
            return jsonify({'success': False, 'error': 'Cannot ban yourself'}), 400
        
        ban_reason = request.json.get('reason', '').strip()
        action = request.json.get('action', 'ban')  # ban or unban
        
        if action == 'ban':
            success = auth_service.ban_user(user_id, ban_reason)
            message = 'User banned successfully'
            log_message = f"Admin banned user {user_id}: {ban_reason}"
        else:
            success = auth_service.unban_user(user_id)
            message = 'User unbanned successfully'
            log_message = f"Admin unbanned user {user_id}"
        
        if success:
            logger.info(log_message)
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': f'Failed to {action} user'}), 500
        
    except Exception as e:
        logger.error(f"Admin ban user error: {str(e)}")
        return jsonify({'success': False, 'error': 'Action failed'}), 500

@admin_bp.route('/exercises')
@admin_required
def manage_exercises():
    """
    Exercise management page
    """
    try:
        # Get filter parameters
        search = request.args.get('search', '').strip()
        difficulty = request.args.get('difficulty', '')
        topic = request.args.get('topic', '')
        status = request.args.get('status', '')  # active, inactive
        sort_by = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build filter criteria
        filters = {
            'search': search,
            'difficulty': difficulty,
            'topic': topic,
            'status': status,
            'sort_by': sort_by,
            'order': order
        }
        
        # Get exercises with pagination
        exercises_data = Exercise.get_exercises_with_filters(
            filters=filters,
            page=page,
            per_page=per_page,
            admin_view=True
        )
        
        exercises = exercises_data['exercises']
        pagination = exercises_data['pagination']
        
        # Get exercise statistics
        for exercise in exercises:
            exercise_stats = progress_service.get_exercise_admin_stats(exercise['id'])
            exercise['stats'] = exercise_stats
        
        # Get filter options
        topics = Exercise.get_available_topics()
        difficulties = ['easy', 'medium', 'hard']
        
        context = {
            'exercises': exercises,
            'pagination': pagination,
            'filters': filters,
            'topics': topics,
            'difficulties': difficulties
        }
        
        return render_template('admin/exercises.html', **context)
        
    except Exception as e:
        logger.error(f"Admin exercises error: {str(e)}")
        flash('Error loading exercises.', 'error')
        return render_template('admin/exercises.html', exercises=[], pagination={})

@admin_bp.route('/exercises/<int:exercise_id>')
@admin_required
def exercise_detail(exercise_id):
    """
    Detailed view of an exercise for editing
    """
    try:
        # Get exercise data
        exercise = Exercise.get_by_id(exercise_id)
        if not exercise:
            abort(404)
        
        # Get exercise statistics
        exercise_stats = progress_service.get_exercise_admin_stats(exercise_id)
        
        # Get recent submissions
        recent_submissions = ExerciseSubmission.get_exercise_submissions(exercise_id, limit=20)
        
        # Get submission analytics
        submission_analytics = progress_service.get_exercise_submission_analytics(exercise_id)
        
        context = {
            'exercise': exercise,
            'exercise_stats': exercise_stats,
            'recent_submissions': recent_submissions,
            'submission_analytics': submission_analytics
        }
        
        return render_template('admin/exercise_detail.html', **context)
        
    except Exception as e:
        logger.error(f"Admin exercise detail error: {str(e)}")
        flash('Error loading exercise details.', 'error')
        return redirect(url_for('admin.manage_exercises'))

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """
    Platform analytics and reporting
    """
    try:
        # Get time period filter
        period = request.args.get('period', 'month')  # week, month, quarter, year
        
        # Get user analytics
        user_analytics = {
            'registration_trends': User.get_registration_trends(period),
            'activity_patterns': User.get_activity_patterns(period),
            'retention_rates': User.get_retention_rates(period),
            'demographics': User.get_user_demographics()
        }
        
        # Get exercise analytics
        exercise_analytics = {
            'completion_rates': Exercise.get_completion_rates(period),
            'difficulty_distribution': Exercise.get_difficulty_distribution(),
            'popular_topics': Exercise.get_popular_topics(period),
            'average_attempts': Exercise.get_average_attempts(period)
        }
        
        # Get learning analytics
        learning_analytics = {
            'progress_patterns': progress_service.get_progress_patterns(period),
            'time_spent_analytics': progress_service.get_time_spent_analytics(period),
            'module_completion_rates': progress_service.get_module_completion_rates(period),
            'achievement_distribution': progress_service.get_achievement_distribution()
        }
        
        # Get system performance metrics
        performance_metrics = {
            'response_times': [],  # Would come from monitoring system
            'error_rates': [],     # Would come from error tracking
            'uptime_data': [],     # Would come from uptime monitoring
            'resource_usage': {}   # Would come from system monitoring
        }
        
        context = {
            'period': period,
            'user_analytics': user_analytics,
            'exercise_analytics': exercise_analytics,
            'learning_analytics': learning_analytics,
            'performance_metrics': performance_metrics
        }
        
        return render_template('admin/analytics.html', **context)
        
    except Exception as e:
        logger.error(f"Admin analytics error: {str(e)}")
        flash('Error loading analytics.', 'error')
        return render_template('admin/analytics.html')

@admin_bp.route('/export/users')
@admin_required
def export_users():
    """
    Export user data as CSV
    """
    try:
        # Get all users
        users = User.get_all_users()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Username', 'Email', 'Created At', 'Last Login',
            'Is Active', 'Is Admin', 'Total Exercises', 'Completed Exercises',
            'Total Points', 'Current Streak'
        ])
        
        # Write user data
        for user in users:
            stats = progress_service.get_user_stats(user.id)
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.created_at.isoformat() if user.created_at else '',
                user.last_login.isoformat() if user.last_login else '',
                user.is_active,
                user.is_admin,
                stats.get('total_exercises', 0),
                stats.get('completed_exercises', 0),
                stats.get('total_points', 0),
                stats.get('current_streak', 0)
            ])
        
        # Prepare response
        response = jsonify({
            'success': True,
            'csv_data': output.getvalue(),
            'filename': f'users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
        
        output.close()
        return response
        
    except Exception as e:
        logger.error(f"Export users error: {str(e)}")
        return jsonify({'success': False, 'error': 'Export failed'}), 500

@admin_bp.route('/export/submissions')
@admin_required
def export_submissions():
    """
    Export submission data as CSV
    """
    try:
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get submissions
        submissions = ExerciseSubmission.get_submissions_for_export(start_date, end_date)
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Submission ID', 'User ID', 'Username', 'Exercise ID', 'Exercise Title',
            'Score', 'Passed Tests', 'Total Tests', 'Is Completed', 'Submitted At',
            'Execution Time', 'Memory Usage'
        ])
        
        # Write submission data
        for submission in submissions:
            writer.writerow([
                submission.id,
                submission.user_id,
                submission.username,
                submission.exercise_id,
                submission.exercise_title,
                submission.score,
                submission.passed_tests,
                submission.total_tests,
                submission.is_completed,
                submission.submitted_at.isoformat() if submission.submitted_at else '',
                submission.execution_time,
                submission.memory_usage
            ])
        
        # Prepare response
        response = jsonify({
            'success': True,
            'csv_data': output.getvalue(),
            'filename': f'submissions_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
        
        output.close()
        return response
        
    except Exception as e:
        logger.error(f"Export submissions error: {str(e)}")
        return jsonify({'success': False, 'error': 'Export failed'}), 500

@admin_bp.route('/settings')
@admin_required
def settings():
    """
    Platform settings and configuration
    """
    try:
        # Get current settings (these would normally come from a database)
        current_settings = {
            'site_name': 'Python Mastery Hub',
            'site_description': 'Learn Python programming through interactive exercises',
            'max_file_size': 10,  # MB
            'session_timeout': 30,  # minutes
            'max_login_attempts': 5,
            'registration_enabled': True,
            'email_verification_required': True,
            'maintenance_mode': False,
            'analytics_enabled': True,
            'backup_enabled': True,
            'backup_frequency': 'daily'
        }
        
        return render_template('admin/settings.html', settings=current_settings)
        
    except Exception as e:
        logger.error(f"Admin settings error: {str(e)}")
        flash('Error loading settings.', 'error')
        return render_template('admin/settings.html', settings={})

@admin_bp.route('/settings/update', methods=['POST'])
@admin_required
def update_settings():
    """
    Update platform settings
    """
    try:
        settings_data = request.json
        
        # Validate settings
        required_fields = [
            'site_name', 'site_description', 'max_file_size',
            'session_timeout', 'max_login_attempts'
        ]
        
        for field in required_fields:
            if field not in settings_data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Update settings (this would normally save to database)
        # For now, we'll just log the update
        logger.info(f"Admin updated settings: {settings_data}")
        
        return jsonify({'success': True, 'message': 'Settings updated successfully'})
        
    except Exception as e:
        logger.error(f"Update settings error: {str(e)}")
        return jsonify({'success': False, 'error': 'Update failed'}), 500

# API endpoints for admin dashboard widgets
@admin_bp.route('/api/stats')
@admin_required
def api_get_admin_stats():
    """
    Get admin statistics for dashboard widgets
    """
    try:
        stats = {
            'users_today': User.get_active_users_count(days=1),
            'submissions_today': ExerciseSubmission.get_submissions_count(days=1),
            'new_registrations': User.get_registrations_count(days=1),
            'system_status': 'healthy'
        }
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        logger.error(f"Admin API stats error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/activity-chart')
@admin_required
def api_get_activity_chart():
    """
    Get activity chart data for admin dashboard
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        chart_data = {
            'user_activity': User.get_activity_chart_data(days),
            'submission_activity': ExerciseSubmission.get_activity_chart_data(days)
        }
        
        return jsonify({'success': True, 'data': chart_data})
        
    except Exception as e:
        logger.error(f"Admin activity chart error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Template context processors
@admin_bp.context_processor
def inject_admin_data():
    """
    Inject admin-specific data into templates
    """
    data = {}
    
    if 'user_id' in session:
        try:
            user = auth_service.get_user_by_id(session['user_id'])
            if user and user.is_admin:
                # Add quick admin stats for header/sidebar
                data['admin_quick_stats'] = {
                    'pending_reports': 0,  # Would come from reports system
                    'system_alerts': 0,    # Would come from monitoring
                    'active_users': User.get_active_users_count(days=1)
                }
        except Exception as e:
            logger.error(f"Admin context processor error: {str(e)}")
    
    return data