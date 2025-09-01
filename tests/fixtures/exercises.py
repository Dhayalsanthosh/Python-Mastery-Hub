# tests/fixtures/exercises.py
# Exercise-related test fixtures

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
from typing import List, Dict, Any

# Import your exercise models and services (adjust based on your actual structure)
try:
    from src.models.exercise import Exercise, TestCase, Hint, Topic
    from src.services.exercise_service import ExerciseService
    from src.core.exercise_engine import ExerciseEngine
    from src.core.code_evaluator import CodeEvaluator
except ImportError:
    # Mock classes for when actual models don't exist
    class Exercise:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class TestCase:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class Hint:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class Topic:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class ExerciseService:
        pass
    
    class ExerciseEngine:
        pass
    
    class CodeEvaluator:
        pass


@pytest.fixture
def sample_exercise():
    """Create a basic sample exercise."""
    exercise_data = {
        'id': 'ex_sample_001',
        'title': 'Variable Assignment',
        'description': 'Learn how to assign values to variables in Python.',
        'long_description': '''
        In this exercise, you'll learn the fundamentals of variable assignment in Python.
        Variables are used to store data that can be referenced and manipulated in your program.
        
        The basic syntax for variable assignment is:
        variable_name = value
        ''',
        'topic_id': 'topic_basics',
        'difficulty': 'beginner',
        'category': 'fundamentals',
        'subcategory': 'variables',
        'order_index': 1,
        'estimated_time': 5,  # minutes
        'points': 10,
        'template_code': '# Assign the value 42 to a variable named x\n# Your code here:\n',
        'solution_code': 'x = 42',
        'explanation': 'Variables in Python are created by assigning a value using the = operator.',
        'learning_objectives': [
            'Understand variable assignment syntax',
            'Practice creating variables',
            'Learn naming conventions'
        ],
        'test_cases': [
            {
                'id': 'test_001',
                'description': 'Variable x should exist',
                'test_code': "assert 'x' in globals()",
                'expected_output': None,
                'is_hidden': False,
                'points': 5
            },
            {
                'id': 'test_002', 
                'description': 'Variable x should equal 42',
                'test_code': 'assert x == 42',
                'expected_output': None,
                'is_hidden': False,
                'points': 5
            }
        ],
        'hints': [
            {
                'id': 'hint_001',
                'content': 'Use the assignment operator (=) to assign a value to a variable',
                'unlock_after_attempts': 1,
                'order_index': 1
            },
            {
                'id': 'hint_002',
                'content': 'The syntax is: variable_name = value',
                'unlock_after_attempts': 2,
                'order_index': 2
            },
            {
                'id': 'hint_003',
                'content': 'Try: x = 42',
                'unlock_after_attempts': 3,
                'order_index': 3,
                'is_solution_hint': True
            }
        ],
        'tags': ['variables', 'assignment', 'basics', 'integers'],
        'prerequisites': [],
        'follow_up_exercises': ['ex_string_assignment', 'ex_multiple_assignment'],
        'is_active': True,
        'created_at': datetime.utcnow() - timedelta(days=30),
        'updated_at': datetime.utcnow() - timedelta(days=5),
        'author_id': 'admin_001',
        'version': '1.0',
        'metadata': {
            'difficulty_score': 1.2,
            'completion_rate': 0.95,
            'average_attempts': 1.3,
            'average_time': 180  # seconds
        }
    }
    
    return Exercise(**exercise_data)


@pytest.fixture
def exercise_set():
    """Create a set of related exercises."""
    exercises = []
    
    # Beginner exercises
    exercises.append(Exercise(
        id='ex_basics_001',
        title='Hello World',
        description='Your first Python program',
        topic_id='topic_basics',
        difficulty='beginner',
        order_index=1,
        points=5,
        template_code='# Print "Hello, World!" to the console\n',
        solution_code='print("Hello, World!")',
        test_cases=[
            {
                'description': 'Should print Hello, World!',
                'test_code': 'import io; import sys; old_stdout = sys.stdout; sys.stdout = mystdout = io.StringIO(); exec(code); output = mystdout.getvalue(); sys.stdout = old_stdout; assert "Hello, World!" in output',
                'expected_output': 'Hello, World!',
                'points': 5
            }
        ],
        hints=[
            {
                'content': 'Use the print() function to display text',
                'unlock_after_attempts': 1
            }
        ],
        tags=['print', 'strings', 'hello_world'],
        is_active=True
    ))
    
    exercises.append(Exercise(
        id='ex_basics_002',
        title='Variable Assignment',
        description='Create and assign variables',
        topic_id='topic_basics',
        difficulty='beginner',
        order_index=2,
        points=10,
        template_code='# Create a variable called name and assign it your name\n',
        solution_code='name = "Alice"',
        test_cases=[
            {
                'description': 'Variable name should exist',
                'test_code': "assert 'name' in globals()",
                'points': 5
            },
            {
                'description': 'Variable name should be a string',
                'test_code': 'assert isinstance(name, str)',
                'points': 5
            }
        ],
        prerequisites=['ex_basics_001'],
        is_active=True
    ))
    
    # Intermediate exercise
    exercises.append(Exercise(
        id='ex_functions_001',
        title='Define a Function',
        description='Create your first function',
        topic_id='topic_functions',
        difficulty='intermediate',
        order_index=1,
        points=20,
        template_code='# Define a function called greet that takes a name parameter\n# and returns "Hello, {name}!"\n',
        solution_code='def greet(name):\n    return f"Hello, {name}!"',
        test_cases=[
            {
                'description': 'Function greet should exist',
                'test_code': "assert 'greet' in globals() and callable(greet)",
                'points': 5
            },
            {
                'description': 'Function should return correct greeting',
                'test_code': 'assert greet("Alice") == "Hello, Alice!"',
                'points': 10
            },
            {
                'description': 'Function should work with different names',
                'test_code': 'assert greet("Bob") == "Hello, Bob!"',
                'points': 5
            }
        ],
        hints=[
            {
                'content': 'Use the def keyword to define a function',
                'unlock_after_attempts': 1
            },
            {
                'content': 'Use f-strings for string formatting: f"Hello, {name}!"',
                'unlock_after_attempts': 2
            }
        ],
        prerequisites=['ex_basics_001', 'ex_basics_002'],
        is_active=True
    ))
    
    # Advanced exercise
    exercises.append(Exercise(
        id='ex_algorithms_001',
        title='Binary Search',
        description='Implement binary search algorithm',
        topic_id='topic_algorithms',
        difficulty='advanced',
        order_index=1,
        points=50,
        template_code='''# Implement binary search
def binary_search(arr, target):
    """
    Find the index of target in sorted array arr.
    Return -1 if not found.
    """
    # Your code here
    pass
''',
        solution_code='''def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1''',
        test_cases=[
            {
                'description': 'Should find element in middle',
                'test_code': 'assert binary_search([1, 2, 3, 4, 5], 3) == 2',
                'points': 10
            },
            {
                'description': 'Should find first element',
                'test_code': 'assert binary_search([1, 2, 3, 4, 5], 1) == 0',
                'points': 10
            },
            {
                'description': 'Should find last element',
                'test_code': 'assert binary_search([1, 2, 3, 4, 5], 5) == 4',
                'points': 10
            },
            {
                'description': 'Should return -1 for missing element',
                'test_code': 'assert binary_search([1, 2, 3, 4, 5], 6) == -1',
                'points': 10
            },
            {
                'description': 'Should work with empty array',
                'test_code': 'assert binary_search([], 1) == -1',
                'points': 10
            }
        ],
        hints=[
            {
                'content': 'Use two pointers: left and right',
                'unlock_after_attempts': 1
            },
            {
                'content': 'Calculate middle index as (left + right) // 2',
                'unlock_after_attempts': 2
            },
            {
                'content': 'Compare middle element with target to decide which half to search',
                'unlock_after_attempts': 3
            }
        ],
        prerequisites=['ex_functions_001'],
        is_active=True
    ))
    
    return exercises


@pytest.fixture
def completed_exercise(sample_exercise):
    """Create an exercise with completion data."""
    exercise = sample_exercise
    exercise.completion_data = {
        'total_attempts': 150,
        'successful_completions': 142,
        'completion_rate': 0.947,
        'average_attempts_to_complete': 1.8,
        'average_time_to_complete': 245,  # seconds
        'hint_usage_rate': 0.35,
        'common_mistakes': [
            {
                'mistake': 'Using == instead of =',
                'frequency': 0.25,
                'hint': 'Remember that = is for assignment, == is for comparison'
            },
            {
                'mistake': 'Forgetting variable name',
                'frequency': 0.15,
                'hint': 'Make sure to give your variable a name before the = sign'
            }
        ],
        'user_feedback': {
            'difficulty_rating': 2.1,  # out of 5
            'clarity_rating': 4.3,
            'usefulness_rating': 4.5,
            'comments': [
                'Great introduction to variables!',
                'Could use more examples',
                'Perfect difficulty for beginners'
            ]
        }
    }
    
    return exercise


@pytest.fixture
def exercise_with_hints():
    """Create an exercise with comprehensive hints."""
    return Exercise(
        id='ex_with_hints_001',
        title='List Comprehension',
        description='Create a list comprehension to filter even numbers',
        topic_id='topic_data_structures',
        difficulty='intermediate',
        points=25,
        template_code='# Create a list comprehension that filters even numbers from [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n# Store the result in a variable called even_numbers\n',
        solution_code='even_numbers = [x for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] if x % 2 == 0]',
        test_cases=[
            {
                'description': 'even_numbers should contain only even numbers',
                'test_code': 'assert even_numbers == [2, 4, 6, 8, 10]',
                'points': 25
            }
        ],
        hints=[
            {
                'id': 'hint_001',
                'content': 'List comprehensions have the format: [expression for item in iterable]',
                'unlock_after_attempts': 1,
                'hint_type': 'conceptual'
            },
            {
                'id': 'hint_002',
                'content': 'You can add a condition with: [expression for item in iterable if condition]',
                'unlock_after_attempts': 2,
                'hint_type': 'syntax'
            },
            {
                'id': 'hint_003',
                'content': 'Use the modulo operator (%) to check if a number is even: x % 2 == 0',
                'unlock_after_attempts': 3,
                'hint_type': 'logic'
            },
            {
                'id': 'hint_004',
                'content': 'Try: [x for x in [1,2,3,4,5,6,7,8,9,10] if x % 2 == 0]',
                'unlock_after_attempts': 4,
                'hint_type': 'example'
            }
        ],
        is_active=True
    )


@pytest.fixture
def multilevel_exercises():
    """Create exercises of different difficulty levels."""
    return {
        'beginner': [
            Exercise(
                id='beginner_001',
                title='Print Your Name',
                difficulty='beginner',
                points=5,
                template_code='# Print your name\n',
                solution_code='print("Your Name")',
                estimated_time=2
            ),
            Exercise(
                id='beginner_002',
                title='Simple Math',
                difficulty='beginner',
                points=10,
                template_code='# Calculate 5 + 3 and store in variable result\n',
                solution_code='result = 5 + 3',
                estimated_time=3
            )
        ],
        'intermediate': [
            Exercise(
                id='intermediate_001',
                title='Function with Parameters',
                difficulty='intermediate',
                points=20,
                template_code='# Create a function that adds two numbers\n',
                solution_code='def add_numbers(a, b):\n    return a + b',
                estimated_time=8
            ),
            Exercise(
                id='intermediate_002',
                title='Loop Through List',
                difficulty='intermediate',
                points=25,
                template_code='# Use a for loop to print each item in [1, 2, 3, 4, 5]\n',
                solution_code='for item in [1, 2, 3, 4, 5]:\n    print(item)',
                estimated_time=10
            )
        ],
        'advanced': [
            Exercise(
                id='advanced_001',
                title='Class Definition',
                difficulty='advanced',
                points=40,
                template_code='# Create a Person class with name and age attributes\n',
                solution_code='class Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age',
                estimated_time=15
            ),
            Exercise(
                id='advanced_002',
                title='Recursive Function',
                difficulty='advanced',
                points=50,
                template_code='# Implement factorial using recursion\n',
                solution_code='def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)',
                estimated_time=20
            )
        ]
    }


@pytest.fixture
def exercise_topics():
    """Create exercise topics/categories."""
    return [
        Topic(
            id='topic_basics',
            name='Python Basics',
            description='Fundamental Python concepts and syntax',
            difficulty='beginner',
            order_index=1,
            estimated_duration=120,  # minutes
            prerequisites=[],
            learning_objectives=[
                'Understand Python syntax',
                'Work with variables and data types',
                'Use basic operators',
                'Write simple programs'
            ],
            is_active=True
        ),
        Topic(
            id='topic_functions',
            name='Functions',
            description='Defining and using functions in Python',
            difficulty='intermediate',
            order_index=2,
            estimated_duration=180,
            prerequisites=['topic_basics'],
            learning_objectives=[
                'Define functions with parameters',
                'Understand return values',
                'Use local and global scope',
                'Apply function best practices'
            ],
            is_active=True
        ),
        Topic(
            id='topic_oop',
            name='Object-Oriented Programming',
            description='Classes, objects, and OOP principles',
            difficulty='intermediate',
            order_index=3,
            estimated_duration=240,
            prerequisites=['topic_functions'],
            learning_objectives=[
                'Create classes and objects',
                'Understand inheritance',
                'Implement encapsulation',
                'Apply polymorphism'
            ],
            is_active=True
        ),
        Topic(
            id='topic_algorithms',
            name='Algorithms and Data Structures',
            description='Common algorithms and data structures',
            difficulty='advanced',
            order_index=4,
            estimated_duration=300,
            prerequisites=['topic_oop'],
            learning_objectives=[
                'Implement sorting algorithms',
                'Understand time complexity',
                'Work with data structures',
                'Solve algorithmic problems'
            ],
            is_active=True
        )
    ]


@pytest.fixture
def mock_exercise_service():
    """Create a mock exercise service."""
    service = Mock(spec=ExerciseService)
    
    # Mock exercise CRUD operations
    service.create_exercise = AsyncMock()
    service.get_exercise_by_id = AsyncMock()
    service.get_exercises_by_topic = AsyncMock()
    service.update_exercise = AsyncMock()
    service.delete_exercise = AsyncMock()
    service.activate_exercise = AsyncMock()
    service.deactivate_exercise = AsyncMock()
    
    # Mock exercise retrieval
    service.get_next_exercise = AsyncMock()
    service.get_recommended_exercises = AsyncMock()
    service.search_exercises = AsyncMock()
    service.get_exercise_statistics = AsyncMock()
    
    # Mock exercise evaluation
    service.evaluate_solution = AsyncMock()
    service.run_tests = AsyncMock()
    service.provide_feedback = AsyncMock()
    service.generate_hints = AsyncMock()
    
    return service


@pytest.fixture
def mock_exercise_engine():
    """Create a mock exercise engine."""
    engine = Mock(spec=ExerciseEngine)
    
    # Mock core engine operations
    engine.load_exercise = AsyncMock()
    engine.execute_code = AsyncMock()
    engine.validate_solution = AsyncMock()
    engine.calculate_score = AsyncMock()
    engine.track_progress = AsyncMock()
    
    # Mock hint system
    engine.get_available_hints = AsyncMock()
    engine.unlock_hint = AsyncMock()
    engine.generate_dynamic_hint = AsyncMock()
    
    # Mock adaptive learning
    engine.adjust_difficulty = AsyncMock()
    engine.suggest_next_exercise = AsyncMock()
    engine.personalize_content = AsyncMock()
    
    return engine


@pytest.fixture
def mock_code_evaluator():
    """Create a mock code evaluator."""
    evaluator = Mock(spec=CodeEvaluator)
    
    # Mock code execution
    evaluator.execute_code = AsyncMock()
    evaluator.run_tests = AsyncMock()
    evaluator.check_syntax = AsyncMock()
    evaluator.analyze_code = AsyncMock()
    
    # Mock security
    evaluator.sanitize_code = Mock()
    evaluator.check_security = Mock()
    evaluator.validate_imports = Mock()
    
    # Mock performance
    evaluator.measure_execution_time = AsyncMock()
    evaluator.check_memory_usage = AsyncMock()
    evaluator.detect_infinite_loops = Mock()
    
    return evaluator


@pytest.fixture
def exercise_test_data():
    """Comprehensive test data for exercises."""
    return {
        'valid_python_code': [
            'x = 42',
            'print("Hello, World!")',
            'def greet(name):\n    return f"Hello, {name}!"',
            'numbers = [1, 2, 3, 4, 5]\neven = [n for n in numbers if n % 2 == 0]',
            'class Person:\n    def __init__(self, name):\n        self.name = name'
        ],
        'invalid_python_code': [
            'x = ',  # incomplete assignment
            'print("Hello World"',  # missing closing parenthesis
            'def function\n    return True',  # missing colon
            'for i in range(10)\n    print(i)',  # missing colon
            'class MyClass\n    pass'  # missing colon
        ],
        'malicious_code': [
            'import os; os.system("rm -rf /")',
            'open("/etc/passwd", "r").read()',
            '__import__("subprocess").call(["cat", "/etc/hosts"])',
            'exec("import os; os.listdir(\'/\')")',
            'eval("__import__(\'os\').system(\'ls\')")'
        ],
        'test_cases': {
            'simple': [
                {
                    'description': 'Variable should exist',
                    'test_code': "assert 'x' in globals()",
                    'expected': True
                }
            ],
            'complex': [
                {
                    'description': 'Function should return correct value',
                    'test_code': 'assert add(2, 3) == 5',
                    'expected': True
                },
                {
                    'description': 'Function should handle edge cases',
                    'test_code': 'assert add(0, 0) == 0',
                    'expected': True
                }
            ]
        },
        'hint_types': [
            'conceptual',  # Explains the concept
            'syntax',      # Shows correct syntax
            'logic',       # Explains the logic/algorithm
            'example',     # Provides example code
            'debugging'    # Helps find errors
        ]
    }


@pytest.fixture
def exercise_validation_rules():
    """Validation rules for exercises."""
    return {
        'title': {
            'min_length': 5,
            'max_length': 100,
            'required': True
        },
        'description': {
            'min_length': 20,
            'max_length': 500,
            'required': True
        },
        'template_code': {
            'max_length': 2000,
            'required': False
        },
        'solution_code': {
            'min_length': 1,
            'max_length': 5000,
            'required': True
        },
        'points': {
            'min_value': 1,
            'max_value': 100,
            'required': True
        },
        'estimated_time': {
            'min_value': 1,
            'max_value': 180,  # 3 hours max
            'required': True
        },
        'test_cases': {
            'min_count': 1,
            'max_count': 20,
            'required': True
        },
        'hints': {
            'max_count': 10,
            'required': False
        }
    }


@pytest.fixture
def exercise_submission_data():
    """Sample exercise submission data."""
    return {
        'valid_submission': {
            'exercise_id': 'ex_sample_001',
            'user_id': 'user_001',
            'code': 'x = 42',
            'submitted_at': datetime.utcnow().isoformat(),
            'attempt_number': 1,
            'time_spent': 120,  # seconds
            'hints_used': 0
        },
        'submission_with_hints': {
            'exercise_id': 'ex_sample_001',
            'user_id': 'user_002',
            'code': 'x = 42',
            'submitted_at': datetime.utcnow().isoformat(),
            'attempt_number': 3,
            'time_spent': 300,
            'hints_used': 2,
            'hints_viewed': ['hint_001', 'hint_002']
        },
        'incorrect_submission': {
            'exercise_id': 'ex_sample_001',
            'user_id': 'user_003',
            'code': 'x == 42',  # Wrong operator
            'submitted_at': datetime.utcnow().isoformat(),
            'attempt_number': 1,
            'time_spent': 60,
            'hints_used': 0
        }
    }


@pytest.fixture
def exercise_feedback_templates():
    """Templates for exercise feedback."""
    return {
        'success': [
            "Excellent work! Your solution is correct and efficient.",
            "Great job! You've mastered this concept.",
            "Perfect! Your code follows best practices.",
            "Well done! You solved this on your first try."
        ],
        'partial_success': [
            "Good effort! Your solution works but could be improved.",
            "You're on the right track. Consider optimizing your approach.",
            "Nice try! Your logic is correct, but check your syntax."
        ],
        'failure': [
            "Don't give up! Review the problem requirements carefully.",
            "You're learning! Check the hints for guidance.",
            "Keep trying! Programming takes practice.",
            "Good attempt! Review the examples and try again."
        ],
        'syntax_error': [
            "There's a syntax error in your code. Check your brackets and colons.",
            "Python syntax error detected. Review the error message for clues.",
            "Syntax issue found. Make sure your indentation is correct."
        ],
        'timeout': [
            "Your code took too long to execute. Check for infinite loops.",
            "Execution timeout. Consider a more efficient approach.",
            "Code execution exceeded time limit. Optimize your solution."
        ]
    }


# Helper functions for exercise testing
def create_test_exercise(difficulty='beginner', **kwargs):
    """Helper to create test exercises with different configurations."""
    base_data = {
        'id': f'test_ex_{datetime.utcnow().timestamp()}',
        'title': f'Test Exercise - {difficulty.title()}',
        'description': f'A test exercise for {difficulty} level',
        'topic_id': 'topic_basics',
        'difficulty': difficulty,
        'order_index': 1,
        'points': {'beginner': 10, 'intermediate': 20, 'advanced': 40}.get(difficulty, 10),
        'estimated_time': {'beginner': 5, 'intermediate': 10, 'advanced': 20}.get(difficulty, 5),
        'template_code': '# Your code here\n',
        'solution_code': 'pass',
        'test_cases': [
            {
                'description': 'Basic test',
                'test_code': 'assert True',
                'points': 10
            }
        ],
        'hints': [],
        'tags': [difficulty, 'test'],
        'is_active': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    base_data.update(kwargs)
    return Exercise(**base_data)


def validate_exercise_data(exercise_data):
    """Helper to validate exercise data structure."""
    required_fields = [
        'id', 'title', 'description', 'difficulty', 
        'solution_code', 'test_cases', 'points'
    ]
    
    for field in required_fields:
        assert field in exercise_data, f"Missing required field: {field}"
    
    assert exercise_data['difficulty'] in ['beginner', 'intermediate', 'advanced'], \
        "Invalid difficulty level"
    
    assert isinstance(exercise_data['test_cases'], list), \
        "Test cases must be a list"
    
    assert len(exercise_data['test_cases']) > 0, \
        "At least one test case is required"
    
    assert exercise_data['points'] > 0, \
        "Points must be positive"


def assert_exercise_equality(exercise1, exercise2, ignore_fields=None):
    """Helper to compare two exercises for equality."""
    ignore_fields = ignore_fields or ['created_at', 'updated_at', 'id']
    
    for field in ['title', 'description', 'difficulty', 'solution_code']:
        if field not in ignore_fields:
            assert getattr(exercise1, field) == getattr(exercise2, field), \
                f"Field {field} does not match"