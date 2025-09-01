# Location: src/python_mastery_hub/web/routes/exercises.py

"""
Exercise Routes
Handles exercise listing, detail view, submission, and results
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, abort
from datetime import datetime
import json
import logging

from ..models.exercise import Exercise, ExerciseSubmission
from ..services.code_executor import CodeExecutor
from ..services.progress_service import ProgressService
from ..services.auth_service import AuthService
from .auth import login_required

# Create Blueprint
exercises_bp = Blueprint('exercises', __name__)

# Initialize services
code_executor = CodeExecutor()
progress_service = ProgressService()
auth_service = AuthService()

logger = logging.getLogger(__name__)

@exercises_bp.route('/')
@exercises_bp.route('/list')
@login_required
def list_exercises():
    """
    Exercise listing page with filtering and search
    """
    try:
        user_id = session['user_id']
        
        # Get filter parameters
        difficulty = request.args.get('difficulty', '')
        topic = request.args.get('topic', '')
        status = request.args.get('status', '')
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'created_date')
        order = request.args.get('order', 'desc')
        page = request.args.get('page', 1, type=int)
        per_page = 12
        
        # Build filter criteria
        filters = {
            'difficulty': difficulty,
            'topic': topic,
            'status': status,
            'search': search,
            'sort_by': sort_by,
            'order': order,
            'user_id': user_id  # For progress tracking
        }
        
        # Get exercises with pagination
        exercises_data = Exercise.get_exercises_with_filters(
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        exercises = exercises_data['exercises']
        pagination = exercises_data['pagination']
        
        # Get user progress for each exercise
        for exercise in exercises:
            progress = progress_service.get_exercise_progress(user_id, exercise['id'])
            exercise['user_progress'] = progress
        
        # Get filter options
        topics = Exercise.get_available_topics()
        difficulties = ['easy', 'medium', 'hard']
        statuses = ['not_started', 'in_progress', 'completed']
        
        # Get user statistics
        exercise_stats = progress_service.get_exercise_stats(user_id)
        
        context = {
            'exercises': exercises,
            'pagination': pagination,
            'filters': filters,
            'topics': topics,
            'difficulties': difficulties,
            'statuses': statuses,
            'exercise_stats': exercise_stats
        }
        
        return render_template('exercises/list.html', **context)
        
    except Exception as e:
        logger.error(f"Exercise list error: {str(e)}")
        flash('Error loading exercises.', 'error')
        return render_template('exercises/list.html', exercises=[], pagination={})

@exercises_bp.route('/<int:exercise_id>')
@login_required
def detail(exercise_id):
    """
    Exercise detail page with code editor
    """
    try:
        user_id = session['user_id']
        
        # Get exercise data
        exercise = Exercise.get_by_id(exercise_id)
        if not exercise:
            abort(404)
        
        # Get user progress for this exercise
        user_progress = progress_service.get_exercise_progress(user_id, exercise_id)
        
        # Get user's previous submissions
        submissions = ExerciseSubmission.get_user_submissions(user_id, exercise_id, limit=5)
        
        # Get hints if user has unlocked them
        hints = []
        if user_progress and user_progress.get('hints_unlocked', 0) > 0:
            hints = exercise.get('hints', [])[:user_progress['hints_unlocked']]
        
        # Get starting code template
        starter_code = exercise.get('starter_code', '')
        
        # If user has a saved draft, use that instead
        if user_progress and user_progress.get('draft_code'):
            starter_code = user_progress['draft_code']
        
        # Get test cases (without solutions)
        test_cases = exercise.get('test_cases', [])
        public_test_cases = [tc for tc in test_cases if tc.get('public', True)]
        
        # Get related exercises
        related_exercises = Exercise.get_related_exercises(exercise_id, limit=3)
        
        # Get learning objectives
        learning_objectives = exercise.get('learning_objectives', [])
        
        # Get difficulty progression
        difficulty_info = Exercise.get_difficulty_info(exercise.get('difficulty', 'medium'))
        
        context = {
            'exercise': exercise,
            'user_progress': user_progress,
            'submissions': submissions,
            'hints': hints,
            'starter_code': starter_code,
            'test_cases': public_test_cases,
            'related_exercises': related_exercises,
            'learning_objectives': learning_objectives,
            'difficulty_info': difficulty_info
        }
        
        return render_template('exercises/detail.html', **context)
        
    except Exception as e:
        logger.error(f"Exercise detail error: {str(e)}")
        flash('Error loading exercise.', 'error')
        return redirect(url_for('exercises.list_exercises'))

@exercises_bp.route('/<int:exercise_id>/submit', methods=['POST'])
@login_required
def submit_exercise(exercise_id):
    """
    Submit exercise solution for evaluation
    """
    try:
        user_id = session['user_id']
        
        # Get exercise
        exercise = Exercise.get_by_id(exercise_id)
        if not exercise:
            return jsonify({'success': False, 'error': 'Exercise not found'}), 404
        
        # Get submitted code
        code = request.json.get('code', '').strip()
        if not code:
            return jsonify({'success': False, 'error': 'No code provided'}), 400
        
        # Validate code length
        if len(code) > 10000:  # 10KB limit
            return jsonify({'success': False, 'error': 'Code too long'}), 400
        
        # Run code against test cases
        execution_result = code_executor.execute_code(
            code=code,
            test_cases=exercise.get('test_cases', []),
            timeout=30,
            memory_limit=128  # MB
        )
        
        # Calculate score
        total_tests = len(execution_result.get('test_results', []))
        passed_tests = sum(1 for result in execution_result.get('test_results', []) 
                          if result.get('passed', False))
        
        score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Determine completion status
        is_completed = score >= 80  # 80% pass rate for completion
        
        # Save submission
        submission_data = {
            'user_id': user_id,
            'exercise_id': exercise_id,
            'code': code,
            'score': score,
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'execution_result': execution_result,
            'is_completed': is_completed,
            'submitted_at': datetime.utcnow()
        }
        
        submission = ExerciseSubmission.create(submission_data)
        
        if submission:
            # Update user progress
            progress_service.update_exercise_progress(
                user_id=user_id,
                exercise_id=exercise_id,
                submission_id=submission.id,
                score=score,
                is_completed=is_completed
            )
            
            # Award points and check achievements
            if is_completed:
                points_awarded = progress_service.award_exercise_completion_points(
                    user_id, exercise_id, exercise.get('difficulty', 'medium')
                )
                
                # Check for new achievements
                new_achievements = progress_service.check_achievements(user_id)
                
                logger.info(f"User {user_id} completed exercise {exercise_id} with score {score}")
                
                return jsonify({
                    'success': True,
                    'submission_id': submission.id,
                    'score': score,
                    'passed_tests': passed_tests,
                    'total_tests': total_tests,
                    'is_completed': is_completed,
                    'points_awarded': points_awarded,
                    'new_achievements': new_achievements,
                    'execution_result': execution_result
                })
            else:
                return jsonify({
                    'success': True,
                    'submission_id': submission.id,
                    'score': score,
                    'passed_tests': passed_tests,
                    'total_tests': total_tests,
                    'is_completed': is_completed,
                    'execution_result': execution_result
                })
        else:
            return jsonify({'success': False, 'error': 'Failed to save submission'}), 500
        
    except Exception as e:
        logger.error(f"Exercise submission error: {str(e)}")
        return jsonify({'success': False, 'error': 'Submission failed'}), 500

@exercises_bp.route('/<int:exercise_id>/run', methods=['POST'])
@login_required
def run_code(exercise_id):
    """
    Run code without submitting (for testing)
    """
    try:
        user_id = session['user_id']
        
        # Get exercise
        exercise = Exercise.get_by_id(exercise_id)
        if not exercise:
            return jsonify({'success': False, 'error': 'Exercise not found'}), 404
        
        # Get code to run
        code = request.json.get('code', '').strip()
        if not code:
            return jsonify({'success': False, 'error': 'No code provided'}), 400
        
        # Validate code length
        if len(code) > 10000:
            return jsonify({'success': False, 'error': 'Code too long'}), 400
        
        # Run only public test cases for preview
        test_cases = exercise.get('test_cases', [])
        public_test_cases = [tc for tc in test_cases if tc.get('public', True)]
        
        # Execute code
        execution_result = code_executor.execute_code(
            code=code,
            test_cases=public_test_cases,
            timeout=15,  # Shorter timeout for testing
            memory_limit=64  # Lower memory limit
        )
        
        # Save as draft
        progress_service.save_code_draft(user_id, exercise_id, code)
        
        return jsonify({
            'success': True,
            'execution_result': execution_result
        })
        
    except Exception as e:
        logger.error(f"Code execution error: {str(e)}")
        return jsonify({'success': False, 'error': 'Code execution failed'}), 500

@exercises_bp.route('/<int:exercise_id>/hint', methods=['POST'])
@login_required
def get_hint(exercise_id):
    """
    Unlock and get a hint for the exercise
    """
    try:
        user_id = session['user_id']
        
        # Get exercise
        exercise = Exercise.get_by_id(exercise_id)
        if not exercise:
            return jsonify({'success': False, 'error': 'Exercise not found'}), 404
        
        # Get user progress
        user_progress = progress_service.get_exercise_progress(user_id, exercise_id)
        hints_unlocked = user_progress.get('hints_unlocked', 0) if user_progress else 0
        
        # Check if more hints are available
        exercise_hints = exercise.get('hints', [])
        if hints_unlocked >= len(exercise_hints):
            return jsonify({'success': False, 'error': 'No more hints available'}), 400
        
        # Unlock next hint
        next_hint_index = hints_unlocked
        hint = exercise_hints[next_hint_index]
        
        # Update progress
        success = progress_service.unlock_hint(user_id, exercise_id, next_hint_index + 1)
        
        if success:
            # Deduct points for using hint
            points_deducted = progress_service.deduct_hint_points(user_id, exercise_id)
            
            return jsonify({
                'success': True,
                'hint': hint,
                'hints_unlocked': next_hint_index + 1,
                'points_deducted': points_deducted
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to unlock hint'}), 500
        
    except Exception as e:
        logger.error(f"Hint request error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get hint'}), 500

@exercises_bp.route('/<int:exercise_id>/save-draft', methods=['POST'])
@login_required
def save_draft(exercise_id):
    """
    Save code as draft
    """
    try:
        user_id = session['user_id']
        
        # Get code
        code = request.json.get('code', '').strip()
        
        # Save draft
        success = progress_service.save_code_draft(user_id, exercise_id, code)
        
        if success:
            return jsonify({'success': True, 'message': 'Draft saved'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save draft'}), 500
        
    except Exception as e:
        logger.error(f"Save draft error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to save draft'}), 500

@exercises_bp.route('/<int:exercise_id>/submissions')
@login_required
def view_submissions(exercise_id):
    """
    View user's submissions for an exercise
    """
    try:
        user_id = session['user_id']
        
        # Get exercise
        exercise = Exercise.get_by_id(exercise_id)
        if not exercise:
            abort(404)
        
        # Get user submissions
        submissions = ExerciseSubmission.get_user_submissions(user_id, exercise_id)
        
        # Get submission statistics
        submission_stats = progress_service.get_submission_stats(user_id, exercise_id)
        
        context = {
            'exercise': exercise,
            'submissions': submissions,
            'submission_stats': submission_stats
        }
        
        return render_template('exercises/submission.html', **context)
        
    except Exception as e:
        logger.error(f"View submissions error: {str(e)}")
        flash('Error loading submissions.', 'error')
        return redirect(url_for('exercises.detail', exercise_id=exercise_id))

@exercises_bp.route('/submission/<int:submission_id>')
@login_required
def view_submission_result(submission_id):
    """
    View detailed results of a specific submission
    """
    try:
        user_id = session['user_id']
        
        # Get submission
        submission = ExerciseSubmission.get_by_id(submission_id)
        if not submission or submission.user_id != user_id:
            abort(404)
        
        # Get exercise
        exercise = Exercise.get_by_id(submission.exercise_id)
        if not exercise:
            abort(404)
        
        # Parse execution result
        execution_result = submission.execution_result
        if isinstance(execution_result, str):
            execution_result = json.loads(execution_result)
        
        # Get performance metrics
        performance_metrics = progress_service.get_submission_performance_metrics(submission_id)
        
        # Get improvement suggestions
        suggestions = progress_service.get_improvement_suggestions(submission_id)
        
        context = {
            'submission': submission,
            'exercise': exercise,
            'execution_result': execution_result,
            'performance_metrics': performance_metrics,
            'suggestions': suggestions
        }
        
        return render_template('exercises/results.html', **context)
        
    except Exception as e:
        logger.error(f"View submission result error: {str(e)}")
        flash('Error loading submission result.', 'error')
        return redirect(url_for('exercises.list_exercises'))

@exercises_bp.route('/<int:exercise_id>/reset', methods=['POST'])
@login_required
def reset_exercise(exercise_id):
    """
    Reset exercise progress (admin/testing feature)
    """
    try:
        user_id = session['user_id']
        
        # Get exercise
        exercise = Exercise.get_by_id(exercise_id)
        if not exercise:
            return jsonify({'success': False, 'error': 'Exercise not found'}), 404
        
        # Reset progress
        success = progress_service.reset_exercise_progress(user_id, exercise_id)
        
        if success:
            logger.info(f"User {user_id} reset exercise {exercise_id}")
            return jsonify({'success': True, 'message': 'Exercise reset successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to reset exercise'}), 500
        
    except Exception as e:
        logger.error(f"Reset exercise error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to reset exercise'}), 500

# API endpoints for exercise data
@exercises_bp.route('/api/search')
@login_required
def api_search_exercises():
    """
    Search exercises via API
    """
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({'success': True, 'exercises': []})
        
        exercises = Exercise.search(query, limit=limit)
        
        return jsonify({'success': True, 'exercises': exercises})
        
    except Exception as e:
        logger.error(f"Exercise search error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@exercises_bp.route('/api/topics')
@login_required
def api_get_topics():
    """
    Get available exercise topics
    """
    try:
        topics = Exercise.get_available_topics()
        return jsonify({'success': True, 'topics': topics})
    except Exception as e:
        logger.error(f"Get topics error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@exercises_bp.route('/api/validate-code', methods=['POST'])
@login_required
def api_validate_code():
    """
    Validate code syntax without execution
    """
    try:
        code = request.json.get('code', '').strip()
        
        if not code:
            return jsonify({'success': True, 'valid': True})
        
        # Basic syntax validation
        validation_result = code_executor.validate_syntax(code)
        
        return jsonify({
            'success': True,
            'valid': validation_result['valid'],
            'errors': validation_result.get('errors', [])
        })
        
    except Exception as e:
        logger.error(f"Code validation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Template context processors
@exercises_bp.context_processor
def inject_exercise_data():
    """
    Inject common exercise data into templates
    """
    data = {}
    
    if 'user_id' in session:
        try:
            user_id = session['user_id']
            
            # Add exercise progress summary
            data['exercise_progress_summary'] = progress_service.get_exercise_progress_summary(user_id)
            
        except Exception as e:
            logger.error(f"Exercise context processor error: {str(e)}")
    
    return data