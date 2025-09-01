# Location: src/python_mastery_hub/web/routes/dashboard.py

"""
Dashboard Routes
Handles dashboard overview, progress tracking, and achievements
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from datetime import datetime, timedelta
import logging

from ..models.user import User
from ..models.progress import UserProgress
from ..services.progress_service import ProgressService
from ..services.auth_service import AuthService
from .auth import login_required

# Create Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Initialize services
progress_service = ProgressService()
auth_service = AuthService()

logger = logging.getLogger(__name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/overview')
@login_required
def overview():
    """
    Dashboard overview page
    """
    try:
        user_id = session['user_id']
        
        # Get user data
        user = auth_service.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.logout'))
        
        # Get dashboard statistics
        stats = progress_service.get_dashboard_stats(user_id)
        
        # Get recent activities
        activities = progress_service.get_recent_activities(user_id, limit=10)
        
        # Get current streak
        streak_data = progress_service.get_learning_streak(user_id)
        
        # Get recommended exercises
        recommended_exercises = progress_service.get_recommended_exercises(user_id, limit=5)
        
        # Get upcoming goals
        goals = progress_service.get_user_goals(user_id, active_only=True)
        
        # Get learning path progress
        learning_path = progress_service.get_learning_path_progress(user_id)
        
        # Get weekly progress chart data
        weekly_progress = progress_service.get_weekly_progress(user_id)
        
        context = {
            'user': user,
            'stats': stats,
            'activities': activities,
            'streak_data': streak_data,
            'recommended_exercises': recommended_exercises,
            'goals': goals,
            'learning_path': learning_path,
            'weekly_progress': weekly_progress
        }
        
        return render_template('dashboard/overview.html', **context)
        
    except Exception as e:
        logger.error(f"Dashboard overview error: {str(e)}")
        flash('Error loading dashboard.', 'error')
        return render_template('dashboard/overview.html', stats={}, activities=[])

@dashboard_bp.route('/progress')
@login_required
def progress():
    """
    Detailed progress tracking page
    """
    try:
        user_id = session['user_id']
        
        # Get time period filter
        period = request.args.get('period', 'month')  # week, month, year, all
        
        # Get user progress data
        user = auth_service.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.logout'))
        
        # Get progress statistics
        progress_stats = progress_service.get_detailed_progress_stats(user_id, period)
        
        # Get module progress
        module_progress = progress_service.get_module_progress(user_id)
        
        # Get skill progress
        skill_progress = progress_service.get_skill_progress(user_id)
        
        # Get time-based progress chart
        chart_data = progress_service.get_progress_chart_data(user_id, period)
        
        # Get completion rates
        completion_rates = progress_service.get_completion_rates(user_id, period)
        
        # Get difficulty breakdown
        difficulty_breakdown = progress_service.get_difficulty_breakdown(user_id)
        
        # Get study time analytics
        study_time_data = progress_service.get_study_time_analytics(user_id, period)
        
        context = {
            'user': user,
            'period': period,
            'progress_stats': progress_stats,
            'module_progress': module_progress,
            'skill_progress': skill_progress,
            'chart_data': chart_data,
            'completion_rates': completion_rates,
            'difficulty_breakdown': difficulty_breakdown,
            'study_time_data': study_time_data
        }
        
        return render_template('dashboard/progress.html', **context)
        
    except Exception as e:
        logger.error(f"Progress page error: {str(e)}")
        flash('Error loading progress data.', 'error')
        return render_template('dashboard/progress.html')

@dashboard_bp.route('/achievements')
@login_required
def achievements():
    """
    Achievements and badges page
    """
    try:
        user_id = session['user_id']
        
        # Get user data
        user = auth_service.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.logout'))
        
        # Get user achievements
        earned_achievements = progress_service.get_user_achievements(user_id)
        
        # Get available achievements
        available_achievements = progress_service.get_available_achievements()
        
        # Get achievement progress
        achievement_progress = progress_service.get_achievement_progress(user_id)
        
        # Get recent achievements
        recent_achievements = progress_service.get_recent_achievements(user_id, limit=5)
        
        # Get achievement statistics
        achievement_stats = progress_service.get_achievement_stats(user_id)
        
        # Group achievements by category
        achievements_by_category = {}
        for achievement in available_achievements:
            category = achievement.get('category', 'general')
            if category not in achievements_by_category:
                achievements_by_category[category] = []
            
            # Add progress data
            achievement['progress'] = achievement_progress.get(achievement['id'], {})
            achievement['earned'] = achievement['id'] in [a['id'] for a in earned_achievements]
            
            achievements_by_category[category].append(achievement)
        
        context = {
            'user': user,
            'earned_achievements': earned_achievements,
            'achievements_by_category': achievements_by_category,
            'recent_achievements': recent_achievements,
            'achievement_stats': achievement_stats
        }
        
        return render_template('dashboard/achievements.html', **context)
        
    except Exception as e:
        logger.error(f"Achievements page error: {str(e)}")
        flash('Error loading achievements.', 'error')
        return render_template('dashboard/achievements.html')

@dashboard_bp.route('/goals')
@login_required
def goals():
    """
    Learning goals management page
    """
    try:
        user_id = session['user_id']
        
        # Get user data
        user = auth_service.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.logout'))
        
        # Get user goals
        active_goals = progress_service.get_user_goals(user_id, active_only=True)
        completed_goals = progress_service.get_user_goals(user_id, completed_only=True)
        
        # Get goal suggestions
        goal_suggestions = progress_service.get_goal_suggestions(user_id)
        
        # Get goal statistics
        goal_stats = progress_service.get_goal_stats(user_id)
        
        context = {
            'user': user,
            'active_goals': active_goals,
            'completed_goals': completed_goals,
            'goal_suggestions': goal_suggestions,
            'goal_stats': goal_stats
        }
        
        return render_template('dashboard/goals.html', **context)
        
    except Exception as e:
        logger.error(f"Goals page error: {str(e)}")
        flash('Error loading goals.', 'error')
        return render_template('dashboard/goals.html')

@dashboard_bp.route('/goals/create', methods=['POST'])
@login_required
def create_goal():
    """
    Create a new learning goal
    """
    try:
        user_id = session['user_id']
        
        goal_data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'target_type': request.form.get('target_type', ''),
            'target_value': request.form.get('target_value', type=int),
            'deadline': request.form.get('deadline', ''),
            'priority': request.form.get('priority', 'medium')
        }
        
        # Validation
        if not goal_data['title']:
            flash('Goal title is required.', 'error')
            return redirect(url_for('dashboard.goals'))
        
        if not goal_data['target_type'] or not goal_data['target_value']:
            flash('Goal target is required.', 'error')
            return redirect(url_for('dashboard.goals'))
        
        # Parse deadline
        if goal_data['deadline']:
            try:
                goal_data['deadline'] = datetime.strptime(goal_data['deadline'], '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid deadline format.', 'error')
                return redirect(url_for('dashboard.goals'))
        
        # Create goal
        goal = progress_service.create_user_goal(user_id, goal_data)
        
        if goal:
            logger.info(f"User {user_id} created goal: {goal_data['title']}")
            flash('Goal created successfully!', 'success')
        else:
            flash('Failed to create goal.', 'error')
        
        return redirect(url_for('dashboard.goals'))
        
    except Exception as e:
        logger.error(f"Create goal error: {str(e)}")
        flash('Error creating goal.', 'error')
        return redirect(url_for('dashboard.goals'))

@dashboard_bp.route('/goals/<int:goal_id>/update', methods=['POST'])
@login_required
def update_goal(goal_id):
    """
    Update a learning goal
    """
    try:
        user_id = session['user_id']
        
        # Verify goal ownership
        goal = progress_service.get_user_goal(user_id, goal_id)
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('dashboard.goals'))
        
        update_data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'target_value': request.form.get('target_value', type=int),
            'deadline': request.form.get('deadline', ''),
            'priority': request.form.get('priority', 'medium'),
            'status': request.form.get('status', goal['status'])
        }
        
        # Parse deadline
        if update_data['deadline']:
            try:
                update_data['deadline'] = datetime.strptime(update_data['deadline'], '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid deadline format.', 'error')
                return redirect(url_for('dashboard.goals'))
        
        # Update goal
        success = progress_service.update_user_goal(user_id, goal_id, update_data)
        
        if success:
            logger.info(f"User {user_id} updated goal {goal_id}")
            flash('Goal updated successfully!', 'success')
        else:
            flash('Failed to update goal.', 'error')
        
        return redirect(url_for('dashboard.goals'))
        
    except Exception as e:
        logger.error(f"Update goal error: {str(e)}")
        flash('Error updating goal.', 'error')
        return redirect(url_for('dashboard.goals'))

@dashboard_bp.route('/goals/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete_goal(goal_id):
    """
    Delete a learning goal
    """
    try:
        user_id = session['user_id']
        
        # Verify goal ownership
        goal = progress_service.get_user_goal(user_id, goal_id)
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('dashboard.goals'))
        
        # Delete goal
        success = progress_service.delete_user_goal(user_id, goal_id)
        
        if success:
            logger.info(f"User {user_id} deleted goal {goal_id}")
            flash('Goal deleted successfully!', 'success')
        else:
            flash('Failed to delete goal.', 'error')
        
        return redirect(url_for('dashboard.goals'))
        
    except Exception as e:
        logger.error(f"Delete goal error: {str(e)}")
        flash('Error deleting goal.', 'error')
        return redirect(url_for('dashboard.goals'))

# API endpoints for AJAX requests
@dashboard_bp.route('/api/stats')
@login_required
def api_get_stats():
    """
    Get dashboard statistics as JSON
    """
    try:
        user_id = session['user_id']
        stats = progress_service.get_dashboard_stats(user_id)
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"API stats error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/activities')
@login_required
def api_get_activities():
    """
    Get recent activities as JSON
    """
    try:
        user_id = session['user_id']
        limit = request.args.get('limit', 10, type=int)
        activities = progress_service.get_recent_activities(user_id, limit=limit)
        return jsonify({'success': True, 'activities': activities})
    except Exception as e:
        logger.error(f"API activities error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/progress-chart')
@login_required
def api_get_progress_chart():
    """
    Get progress chart data as JSON
    """
    try:
        user_id = session['user_id']
        period = request.args.get('period', 'month')
        chart_data = progress_service.get_progress_chart_data(user_id, period)
        return jsonify({'success': True, 'data': chart_data})
    except Exception as e:
        logger.error(f"API progress chart error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/streak')
@login_required
def api_get_streak():
    """
    Get learning streak data as JSON
    """
    try:
        user_id = session['user_id']
        streak_data = progress_service.get_learning_streak(user_id)
        return jsonify({'success': True, 'streak': streak_data})
    except Exception as e:
        logger.error(f"API streak error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/update-goal-progress', methods=['POST'])
@login_required
def api_update_goal_progress():
    """
    Update goal progress via API
    """
    try:
        user_id = session['user_id']
        goal_id = request.json.get('goal_id')
        progress_value = request.json.get('progress_value')
        
        if not goal_id or progress_value is None:
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
        
        # Verify goal ownership
        goal = progress_service.get_user_goal(user_id, goal_id)
        if not goal:
            return jsonify({'success': False, 'error': 'Goal not found'}), 404
        
        # Update progress
        success = progress_service.update_goal_progress(user_id, goal_id, progress_value)
        
        if success:
            return jsonify({'success': True, 'message': 'Goal progress updated'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update progress'}), 500
        
    except Exception as e:
        logger.error(f"API update goal progress error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Template context processors
@dashboard_bp.context_processor
def inject_dashboard_data():
    """
    Inject common dashboard data into templates
    """
    data = {}
    
    if 'user_id' in session:
        try:
            user_id = session['user_id']
            
            # Add quick stats for sidebar/header
            data['quick_stats'] = progress_service.get_quick_stats(user_id)
            
            # Add notifications count
            data['notifications_count'] = progress_service.get_notifications_count(user_id)
            
        except Exception as e:
            logger.error(f"Dashboard context processor error: {str(e)}")
    
    return data