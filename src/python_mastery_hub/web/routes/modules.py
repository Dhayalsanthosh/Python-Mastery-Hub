# Location: src/python_mastery_hub/web/routes/modules.py

"""
Module Routes
Handles learning module listing, individual module pages, and module progress
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, abort
from datetime import datetime
import logging

from ..models.user import User
from ..services.progress_service import ProgressService
from ..services.auth_service import AuthService
from .auth import login_required

# Create Blueprint
modules_bp = Blueprint('modules', __name__)

# Initialize services
progress_service = ProgressService()
auth_service = AuthService()

logger = logging.getLogger(__name__)

# Static module data (in a real app, this would come from a database)
MODULES_DATA = {
    'python-basics': {
        'id': 'python-basics',
        'title': 'Python Basics',
        'description': 'Learn the fundamentals of Python programming language',
        'difficulty': 'beginner',
        'estimated_hours': 20,
        'prerequisites': [],
        'topics': [
            'Variables and Data Types',
            'Control Structures',
            'Functions',
            'Basic I/O',
            'Error Handling'
        ],
        'lessons': [
            {
                'id': 1,
                'title': 'Getting Started with Python',
                'description': 'Introduction to Python and setting up your environment',
                'type': 'lesson',
                'estimated_minutes': 45,
                'exercises': [1, 2, 3]
            },
            {
                'id': 2,
                'title': 'Variables and Data Types',
                'description': 'Learn about Python variables and basic data types',
                'type': 'lesson',
                'estimated_minutes': 60,
                'exercises': [4, 5, 6, 7]
            },
            {
                'id': 3,
                'title': 'Control Structures',
                'description': 'If statements, loops, and conditional logic',
                'type': 'lesson',
                'estimated_minutes': 90,
                'exercises': [8, 9, 10, 11, 12]
            },
            {
                'id': 4,
                'title': 'Functions and Scope',
                'description': 'Creating and using functions in Python',
                'type': 'lesson',
                'estimated_minutes': 75,
                'exercises': [13, 14, 15, 16]
            },
            {
                'id': 5,
                'title': 'Module Assessment',
                'description': 'Test your knowledge of Python basics',
                'type': 'assessment',
                'estimated_minutes': 120,
                'exercises': [17, 18, 19, 20]
            }
        ]
    },
    'data-structures': {
        'id': 'data-structures',
        'title': 'Data Structures',
        'description': 'Master Python data structures: lists, dictionaries, sets, and tuples',
        'difficulty': 'intermediate',
        'estimated_hours': 25,
        'prerequisites': ['python-basics'],
        'topics': [
            'Lists and List Comprehensions',
            'Dictionaries and Hash Tables',
            'Sets and Set Operations',
            'Tuples and Named Tuples',
            'Advanced Data Manipulation'
        ],
        'lessons': [
            {
                'id': 6,
                'title': 'Lists and Indexing',
                'description': 'Working with Python lists and indexing',
                'type': 'lesson',
                'estimated_minutes': 60,
                'exercises': [21, 22, 23, 24]
            },
            {
                'id': 7,
                'title': 'List Comprehensions',
                'description': 'Advanced list manipulation techniques',
                'type': 'lesson',
                'estimated_minutes': 45,
                'exercises': [25, 26, 27]
            },
            {
                'id': 8,
                'title': 'Dictionaries and Key-Value Pairs',
                'description': 'Working with dictionaries and hash tables',
                'type': 'lesson',
                'estimated_minutes': 70,
                'exercises': [28, 29, 30, 31, 32]
            },
            {
                'id': 9,
                'title': 'Sets and Set Operations',
                'description': 'Understanding sets and mathematical operations',
                'type': 'lesson',
                'estimated_minutes': 50,
                'exercises': [33, 34, 35]
            },
            {
                'id': 10,
                'title': 'Tuples and Immutable Data',
                'description': 'Working with tuples and immutable data structures',
                'type': 'lesson',
                'estimated_minutes': 40,
                'exercises': [36, 37, 38]
            },
            {
                'id': 11,
                'title': 'Data Structures Assessment',
                'description': 'Comprehensive test of data structure knowledge',
                'type': 'assessment',
                'estimated_minutes': 150,
                'exercises': [39, 40, 41, 42, 43]
            }
        ]
    },
    'algorithms': {
        'id': 'algorithms',
        'title': 'Algorithms',
        'description': 'Learn essential algorithms and problem-solving techniques',
        'difficulty': 'advanced',
        'estimated_hours': 40,
        'prerequisites': ['python-basics', 'data-structures'],
        'topics': [
            'Sorting Algorithms',
            'Search Algorithms',
            'Graph Algorithms',
            'Dynamic Programming',
            'Recursion and Backtracking'
        ],
        'lessons': [
            {
                'id': 12,
                'title': 'Sorting Algorithms',
                'description': 'Learn bubble sort, merge sort, quick sort, and more',
                'type': 'lesson',
                'estimated_minutes': 120,
                'exercises': [44, 45, 46, 47, 48]
            },
            {
                'id': 13,
                'title': 'Search Algorithms',
                'description': 'Binary search, linear search, and search optimization',
                'type': 'lesson',
                'estimated_minutes': 90,
                'exercises': [49, 50, 51, 52]
            },
            {
                'id': 14,
                'title': 'Graph Algorithms',
                'description': 'BFS, DFS, shortest path algorithms',
                'type': 'lesson',
                'estimated_minutes': 150,
                'exercises': [53, 54, 55, 56, 57]
            },
            {
                'id': 15,
                'title': 'Dynamic Programming',
                'description': 'Solve complex problems with dynamic programming',
                'type': 'lesson',
                'estimated_minutes': 180,
                'exercises': [58, 59, 60, 61, 62, 63]
            },
            {
                'id': 16,
                'title': 'Recursion and Backtracking',
                'description': 'Master recursive thinking and backtracking techniques',
                'type': 'lesson',
                'estimated_minutes': 120,
                'exercises': [64, 65, 66, 67]
            },
            {
                'id': 17,
                'title': 'Algorithms Mastery Assessment',
                'description': 'Comprehensive algorithms and problem-solving test',
                'type': 'assessment',
                'estimated_minutes': 240,
                'exercises': [68, 69, 70, 71, 72, 73, 74, 75]
            }
        ]
    },
    'web-development': {
        'id': 'web-development',
        'title': 'Web Development with Python',
        'description': 'Build web applications using Flask and Django',
        'difficulty': 'intermediate',
        'estimated_hours': 35,
        'prerequisites': ['python-basics', 'data-structures'],
        'topics': [
            'Flask Framework',
            'Django Framework',
            'Database Integration',
            'RESTful APIs',
            'Web Security'
        ],
        'lessons': [
            {
                'id': 18,
                'title': 'Introduction to Flask',
                'description': 'Get started with Flask web framework',
                'type': 'lesson',
                'estimated_minutes': 90,
                'exercises': [76, 77, 78, 79]
            },
            {
                'id': 19,
                'title': 'Flask Templates and Forms',
                'description': 'Working with Jinja2 templates and forms',
                'type': 'lesson',
                'estimated_minutes': 105,
                'exercises': [80, 81, 82, 83, 84]
            },
            {
                'id': 20,
                'title': 'Database Integration',
                'description': 'Connect your web app to databases',
                'type': 'lesson',
                'estimated_minutes': 120,
                'exercises': [85, 86, 87, 88]
            },
            {
                'id': 21,
                'title': 'RESTful API Development',
                'description': 'Build REST APIs with Flask',
                'type': 'lesson',
                'estimated_minutes': 135,
                'exercises': [89, 90, 91, 92, 93]
            },
            {
                'id': 22,
                'title': 'Web Development Final Project',
                'description': 'Build a complete web application',
                'type': 'project',
                'estimated_minutes': 300,
                'exercises': [94, 95, 96]
            }
        ]
    }
}

@modules_bp.route('/')
@modules_bp.route('/list')
@login_required
def list_modules():
    """
    Module listing page
    """
    try:
        user_id = session['user_id']
        
        # Get user data
        user = auth_service.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.logout'))
        
        # Get filter parameters
        difficulty = request.args.get('difficulty', '')
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'difficulty')
        
        # Filter modules based on criteria
        filtered_modules = []
        for module_id, module_data in MODULES_DATA.items():
            # Apply difficulty filter
            if difficulty and module_data['difficulty'] != difficulty:
                continue
            
            # Apply search filter
            if search:
                search_text = f"{module_data['title']} {module_data['description']} {' '.join(module_data['topics'])}".lower()
                if search.lower() not in search_text:
                    continue
            
            # Get user progress for this module
            module_progress = progress_service.get_module_progress(user_id, module_id)
            module_data['user_progress'] = module_progress
            
            # Check prerequisites
            module_data['prerequisites_met'] = progress_service.check_module_prerequisites(
                user_id, module_data.get('prerequisites', [])
            )
            
            filtered_modules.append(module_data)
        
        # Sort modules
        if sort_by == 'difficulty':
            difficulty_order = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            filtered_modules.sort(key=lambda x: difficulty_order.get(x['difficulty'], 2))
        elif sort_by == 'title':
            filtered_modules.sort(key=lambda x: x['title'])
        elif sort_by == 'progress':
            filtered_modules.sort(
                key=lambda x: x.get('user_progress', {}).get('completion_percentage', 0),
                reverse=True
            )
        
        # Get learning path recommendation
        recommended_next = progress_service.get_recommended_next_module(user_id, MODULES_DATA)
        
        # Get overall statistics
        module_stats = progress_service.get_module_stats(user_id, MODULES_DATA)
        
        context = {
            'modules': filtered_modules,
            'filters': {
                'difficulty': difficulty,
                'search': search,
                'sort': sort_by
            },
            'difficulties': ['beginner', 'intermediate', 'advanced'],
            'recommended_next': recommended_next,
            'module_stats': module_stats
        }
        
        return render_template('modules.html', **context)
        
    except Exception as e:
        logger.error(f"Module list error: {str(e)}")
        flash('Error loading modules.', 'error')
        return render_template('modules.html', modules=[], filters={})

@modules_bp.route('/<module_id>')
@login_required
def module_detail(module_id):
    """
    Individual module detail page
    """
    try:
        user_id = session['user_id']
        
        # Get module data
        if module_id not in MODULES_DATA:
            abort(404)
        
        module = MODULES_DATA[module_id].copy()
        
        # Get user data
        user = auth_service.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.logout'))
        
        # Get user progress for this module
        module_progress = progress_service.get_module_progress(user_id, module_id)
        
        # Check prerequisites
        prerequisites_met = progress_service.check_module_prerequisites(
            user_id, module.get('prerequisites', [])
        )
        
        if not prerequisites_met and module.get('prerequisites'):
            # Get prerequisite module details
            prerequisite_modules = []
            for prereq_id in module.get('prerequisites', []):
                if prereq_id in MODULES_DATA:
                    prereq = MODULES_DATA[prereq_id].copy()
                    prereq['progress'] = progress_service.get_module_progress(user_id, prereq_id)
                    prerequisite_modules.append(prereq)
            module['prerequisite_modules'] = prerequisite_modules
        
        # Get lesson progress for each lesson
        for lesson in module['lessons']:
            lesson_progress = progress_service.get_lesson_progress(user_id, lesson['id'])
            lesson['user_progress'] = lesson_progress
            
            # Get exercise progress for each exercise in the lesson
            lesson['exercise_progress'] = []
            for exercise_id in lesson.get('exercises', []):
                exercise_progress = progress_service.get_exercise_progress(user_id, exercise_id)
                lesson['exercise_progress'].append({
                    'id': exercise_id,
                    'progress': exercise_progress
                })
        
        # Calculate detailed progress statistics
        total_lessons = len(module['lessons'])
        completed_lessons = sum(1 for lesson in module['lessons'] 
                              if lesson.get('user_progress', {}).get('is_completed', False))
        
        total_exercises = sum(len(lesson.get('exercises', [])) for lesson in module['lessons'])
        completed_exercises = 0
        for lesson in module['lessons']:
            for exercise_progress in lesson.get('exercise_progress', []):
                if exercise_progress.get('progress', {}).get('is_completed', False):
                    completed_exercises += 1
        
        # Get time tracking data
        time_spent = progress_service.get_module_time_spent(user_id, module_id)
        
        # Get next recommended lesson
        next_lesson = None
        for lesson in module['lessons']:
            if not lesson.get('user_progress', {}).get('is_completed', False):
                next_lesson = lesson
                break
        
        # Get module achievements
        module_achievements = progress_service.get_module_achievements(user_id, module_id)
        
        context = {
            'module': module,
            'module_progress': module_progress,
            'prerequisites_met': prerequisites_met,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'total_exercises': total_exercises,
            'completed_exercises': completed_exercises,
            'time_spent': time_spent,
            'next_lesson': next_lesson,
            'module_achievements': module_achievements
        }
        
        return render_template('module.html', **context)
        
    except Exception as e:
        logger.error(f"Module detail error: {str(e)}")
        flash('Error loading module.', 'error')
        return redirect(url_for('modules.list_modules'))

@modules_bp.route('/<module_id>/lesson/<int:lesson_id>')
@login_required
def lesson_detail(module_id, lesson_id):
    """
    Individual lesson detail page
    """
    try:
        user_id = session['user_id']
        
        # Get module data
        if module_id not in MODULES_DATA:
            abort(404)
        
        module = MODULES_DATA[module_id]
        
        # Find the lesson
        lesson = None
        for l in module['lessons']:
            if l['id'] == lesson_id:
                lesson = l.copy()
                break
        
        if not lesson:
            abort(404)
        
        # Check module prerequisites
        prerequisites_met = progress_service.check_module_prerequisites(
            user_id, module.get('prerequisites', [])
        )
        
        if not prerequisites_met:
            flash('You must complete the prerequisite modules first.', 'warning')
            return redirect(url_for('modules.module_detail', module_id=module_id))
        
        # Get lesson progress
        lesson_progress = progress_service.get_lesson_progress(user_id, lesson_id)
        
        # Get exercise details for this lesson
        lesson_exercises = []
        if lesson.get('exercises'):
            from ..models.exercise import Exercise
            for exercise_id in lesson['exercises']:
                exercise = Exercise.get_by_id(exercise_id)
                if exercise:
                    exercise_progress = progress_service.get_exercise_progress(user_id, exercise_id)
                    exercise['user_progress'] = exercise_progress
                    lesson_exercises.append(exercise)
        
        # Get previous and next lessons
        lesson_index = next(i for i, l in enumerate(module['lessons']) if l['id'] == lesson_id)
        previous_lesson = module['lessons'][lesson_index - 1] if lesson_index > 0 else None
        next_lesson = module['lessons'][lesson_index + 1] if lesson_index < len(module['lessons']) - 1 else None
        
        # Mark lesson as started if not already
        if not lesson_progress:
            progress_service.start_lesson(user_id, lesson_id)
        
        context = {
            'module': module,
            'lesson': lesson,
            'lesson_progress': lesson_progress,
            'lesson_exercises': lesson_exercises,
            'previous_lesson': previous_lesson,
            'next_lesson': next_lesson
        }
        
        return render_template('lesson_detail.html', **context)
        
    except Exception as e:
        logger.error(f"Lesson detail error: {str(e)}")
        flash('Error loading lesson.', 'error')
        return redirect(url_for('modules.module_detail', module_id=module_id))

@modules_bp.route('/<module_id>/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(module_id, lesson_id):
    """
    Mark a lesson as completed
    """
    try:
        user_id = session['user_id']
        
        # Verify module and lesson exist
        if module_id not in MODULES_DATA:
            return jsonify({'success': False, 'error': 'Module not found'}), 404
        
        module = MODULES_DATA[module_id]
        lesson = None
        for l in module['lessons']:
            if l['id'] == lesson_id:
                lesson = l
                break
        
        if not lesson:
            return jsonify({'success': False, 'error': 'Lesson not found'}), 404
        
        # Check if all exercises in the lesson are completed
        all_exercises_completed = True
        if lesson.get('exercises'):
            for exercise_id in lesson['exercises']:
                exercise_progress = progress_service.get_exercise_progress(user_id, exercise_id)
                if not exercise_progress or not exercise_progress.get('is_completed', False):
                    all_exercises_completed = False
                    break
        
        if not all_exercises_completed:
            return jsonify({
                'success': False, 
                'error': 'Please complete all exercises before marking lesson as complete'
            }), 400
        
        # Complete the lesson
        success = progress_service.complete_lesson(user_id, lesson_id)
        
        if success:
            # Award points for lesson completion
            points_awarded = progress_service.award_lesson_completion_points(user_id, lesson_id)
            
            # Check for module completion
            module_completed = progress_service.check_module_completion(user_id, module_id)
            
            # Check for new achievements
            new_achievements = progress_service.check_achievements(user_id)
            
            logger.info(f"User {user_id} completed lesson {lesson_id} in module {module_id}")
            
            return jsonify({
                'success': True,
                'points_awarded': points_awarded,
                'module_completed': module_completed,
                'new_achievements': new_achievements
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to complete lesson'}), 500
        
    except Exception as e:
        logger.error(f"Complete lesson error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to complete lesson'}), 500

@modules_bp.route('/<module_id>/enroll', methods=['POST'])
@login_required
def enroll_module(module_id):
    """
    Enroll user in a module
    """
    try:
        user_id = session['user_id']
        
        # Verify module exists
        if module_id not in MODULES_DATA:
            return jsonify({'success': False, 'error': 'Module not found'}), 404
        
        module = MODULES_DATA[module_id]
        
        # Check prerequisites
        prerequisites_met = progress_service.check_module_prerequisites(
            user_id, module.get('prerequisites', [])
        )
        
        if not prerequisites_met:
            return jsonify({
                'success': False, 
                'error': 'Prerequisites not met'
            }), 400
        
        # Enroll user
        success = progress_service.enroll_user_in_module(user_id, module_id)
        
        if success:
            logger.info(f"User {user_id} enrolled in module {module_id}")
            return jsonify({'success': True, 'message': 'Successfully enrolled in module'})
        else:
            return jsonify({'success': False, 'error': 'Failed to enroll in module'}), 500
        
    except Exception as e:
        logger.error(f"Module enrollment error: {str(e)}")
        return jsonify({'success': False, 'error': 'Enrollment failed'}), 500

# API endpoints
@modules_bp.route('/api/search')
@login_required
def api_search_modules():
    """
    Search modules via API
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'success': True, 'modules': []})
        
        # Search through modules
        results = []
        for module_id, module_data in MODULES_DATA.items():
            search_text = f"{module_data['title']} {module_data['description']} {' '.join(module_data['topics'])}".lower()
            if query.lower() in search_text:
                results.append({
                    'id': module_id,
                    'title': module_data['title'],
                    'description': module_data['description'],
                    'difficulty': module_data['difficulty']
                })
        
        return jsonify({'success': True, 'modules': results})
        
    except Exception as e:
        logger.error(f"Module search error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@modules_bp.route('/api/<module_id>/progress')
@login_required
def api_get_module_progress(module_id):
    """
    Get module progress via API
    """
    try:
        user_id = session['user_id']
        
        if module_id not in MODULES_DATA:
            return jsonify({'success': False, 'error': 'Module not found'}), 404
        
        progress = progress_service.get_module_progress(user_id, module_id)
        
        return jsonify({'success': True, 'progress': progress})
        
    except Exception as e:
        logger.error(f"Module progress API error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@modules_bp.route('/api/learning-path')
@login_required
def api_get_learning_path():
    """
    Get personalized learning path
    """
    try:
        user_id = session['user_id']
        
        learning_path = progress_service.generate_learning_path(user_id, MODULES_DATA)
        
        return jsonify({'success': True, 'learning_path': learning_path})
        
    except Exception as e:
        logger.error(f"Learning path API error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Template context processors
@modules_bp.context_processor
def inject_module_data():
    """
    Inject common module data into templates
    """
    data = {}
    
    if 'user_id' in session:
        try:
            user_id = session['user_id']
            
            # Add overall module progress
            data['overall_module_progress'] = progress_service.get_overall_module_progress(user_id)
            
            # Add available modules count
            data['total_modules'] = len(MODULES_DATA)
            
        except Exception as e:
            logger.error(f"Module context processor error: {str(e)}")
    
    return data