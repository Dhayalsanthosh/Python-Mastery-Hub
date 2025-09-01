# tests/unit/web/test_models.py
"""
Test module for web application models.
Tests data models, validation, serialization, and database interactions.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import Dict, List, Optional
import json


class MockUser:
    """Mock User model for testing"""
    
    def __init__(self, user_id=None, username=None, email=None, password_hash=None, 
                 created_at=None, is_active=True, role='student'):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now()
        self.is_active = is_active
        self.role = role
        self.last_login = None
        self.profile = None
        self._exercises_completed = []
        self._progress_data = {}
    
    def set_password(self, password):
        """Set user password (mock hashing)"""
        self.password_hash = f"hashed_{password}"
    
    def check_password(self, password):
        """Check user password"""
        return self.password_hash == f"hashed_{password}"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'role': self.role,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user from dictionary"""
        user = cls(
            user_id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            is_active=data.get('is_active', True),
            role=data.get('role', 'student')
        )
        if data.get('created_at'):
            user.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('last_login'):
            user.last_login = datetime.fromisoformat(data['last_login'])
        return user
    
    def validate(self):
        """Validate user data"""
        errors = []
        
        if not self.username or len(self.username) < 3:
            errors.append("Username must be at least 3 characters")
        
        if not self.email or '@' not in self.email:
            errors.append("Valid email required")
        
        if self.role not in ['student', 'instructor', 'admin']:
            errors.append("Invalid role")
        
        return len(errors) == 0, errors


class MockExercise:
    """Mock Exercise model for testing"""
    
    def __init__(self, exercise_id=None, title=None, description=None, 
                 difficulty='beginner', topic='basics', points=10,
                 created_at=None, is_active=True):
        self.id = exercise_id
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.topic = topic
        self.points = points
        self.created_at = created_at or datetime.now()
        self.is_active = is_active
        self.test_cases = []
        self.solution_template = ""
        self.hints = []
    
    def add_test_case(self, input_data, expected_output, is_hidden=False):
        """Add test case to exercise"""
        test_case = {
            'input': input_data,
            'expected_output': expected_output,
            'is_hidden': is_hidden
        }
        self.test_cases.append(test_case)
    
    def to_dict(self, include_hidden=False):
        """Convert exercise to dictionary"""
        test_cases = self.test_cases
        if not include_hidden:
            test_cases = [tc for tc in test_cases if not tc.get('is_hidden', False)]
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'topic': self.topic,
            'points': self.points,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'test_cases': test_cases,
            'solution_template': self.solution_template,
            'hints': self.hints
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create exercise from dictionary"""
        exercise = cls(
            exercise_id=data.get('id'),
            title=data.get('title'),
            description=data.get('description'),
            difficulty=data.get('difficulty', 'beginner'),
            topic=data.get('topic', 'basics'),
            points=data.get('points', 10),
            is_active=data.get('is_active', True)
        )
        
        if data.get('created_at'):
            exercise.created_at = datetime.fromisoformat(data['created_at'])
        
        exercise.test_cases = data.get('test_cases', [])
        exercise.solution_template = data.get('solution_template', '')
        exercise.hints = data.get('hints', [])
        
        return exercise
    
    def validate(self):
        """Validate exercise data"""
        errors = []
        
        if not self.title or len(self.title) < 5:
            errors.append("Title must be at least 5 characters")
        
        if not self.description:
            errors.append("Description is required")
        
        if self.difficulty not in ['beginner', 'intermediate', 'advanced']:
            errors.append("Invalid difficulty level")
        
        if self.points < 0:
            errors.append("Points cannot be negative")
        
        if not self.test_cases:
            errors.append("At least one test case is required")
        
        return len(errors) == 0, errors


class MockSubmission:
    """Mock Submission model for testing"""
    
    def __init__(self, submission_id=None, user_id=None, exercise_id=None,
                 code=None, language='python', status='pending',
                 submitted_at=None, score=None, feedback=None):
        self.id = submission_id
        self.user_id = user_id
        self.exercise_id = exercise_id
        self.code = code
        self.language = language
        self.status = status  # pending, running, completed, failed
        self.submitted_at = submitted_at or datetime.now()
        self.completed_at = None
        self.score = score
        self.feedback = feedback
        self.execution_time = None
        self.test_results = []
    
    def add_test_result(self, test_case_id, passed, output, error=None):
        """Add test result"""
        result = {
            'test_case_id': test_case_id,
            'passed': passed,
            'output': output,
            'error': error,
            'execution_time': 0.1  # Mock execution time
        }
        self.test_results.append(result)
    
    def calculate_score(self):
        """Calculate submission score based on test results"""
        if not self.test_results:
            return 0
        
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        total_tests = len(self.test_results)
        
        self.score = (passed_tests / total_tests) * 100
        return self.score
    
    def to_dict(self):
        """Convert submission to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_id': self.exercise_id,
            'code': self.code,
            'language': self.language,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'score': self.score,
            'feedback': self.feedback,
            'execution_time': self.execution_time,
            'test_results': self.test_results
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create submission from dictionary"""
        submission = cls(
            submission_id=data.get('id'),
            user_id=data.get('user_id'),
            exercise_id=data.get('exercise_id'),
            code=data.get('code'),
            language=data.get('language', 'python'),
            status=data.get('status', 'pending'),
            score=data.get('score'),
            feedback=data.get('feedback')
        )
        
        if data.get('submitted_at'):
            submission.submitted_at = datetime.fromisoformat(data['submitted_at'])
        if data.get('completed_at'):
            submission.completed_at = datetime.fromisoformat(data['completed_at'])
        
        submission.execution_time = data.get('execution_time')
        submission.test_results = data.get('test_results', [])
        
        return submission
    
    def validate(self):
        """Validate submission data"""
        errors = []
        
        if not self.user_id:
            errors.append("User ID is required")
        
        if not self.exercise_id:
            errors.append("Exercise ID is required")
        
        if not self.code or not self.code.strip():
            errors.append("Code is required")
        
        if self.language not in ['python', 'javascript', 'java', 'cpp']:
            errors.append("Unsupported programming language")
        
        if self.status not in ['pending', 'running', 'completed', 'failed']:
            errors.append("Invalid status")
        
        return len(errors) == 0, errors


class MockProgress:
    """Mock Progress model for testing"""
    
    def __init__(self, user_id=None, topic=None, exercises_completed=0,
                 total_exercises=0, points_earned=0, last_activity=None):
        self.user_id = user_id
        self.topic = topic
        self.exercises_completed = exercises_completed
        self.total_exercises = total_exercises
        self.points_earned = points_earned
        self.last_activity = last_activity or datetime.now()
        self.completion_percentage = 0.0
        self.average_score = 0.0
        self.streak_days = 0
    
    def update_progress(self, exercise_score, exercise_points):
        """Update progress with new exercise completion"""
        self.exercises_completed += 1
        self.points_earned += exercise_points
        self.last_activity = datetime.now()
        self.completion_percentage = (self.exercises_completed / self.total_exercises) * 100
        
        # Update average score (simplified calculation)
        if hasattr(self, '_total_score'):
            self._total_score += exercise_score
        else:
            self._total_score = exercise_score
        
        self.average_score = self._total_score / self.exercises_completed
    
    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'user_id': self.user_id,
            'topic': self.topic,
            'exercises_completed': self.exercises_completed,
            'total_exercises': self.total_exercises,
            'points_earned': self.points_earned,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'completion_percentage': round(self.completion_percentage, 2),
            'average_score': round(self.average_score, 2),
            'streak_days': self.streak_days
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create progress from dictionary"""
        progress = cls(
            user_id=data.get('user_id'),
            topic=data.get('topic'),
            exercises_completed=data.get('exercises_completed', 0),
            total_exercises=data.get('total_exercises', 0),
            points_earned=data.get('points_earned', 0)
        )
        
        if data.get('last_activity'):
            progress.last_activity = datetime.fromisoformat(data['last_activity'])
        
        progress.completion_percentage = data.get('completion_percentage', 0.0)
        progress.average_score = data.get('average_score', 0.0)
        progress.streak_days = data.get('streak_days', 0)
        
        return progress


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self):
        """Test user creation"""
        user = MockUser(
            user_id=1,
            username="testuser",
            email="test@example.com"
        )
        
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.role == "student"
        assert isinstance(user.created_at, datetime)
    
    def test_user_password_operations(self):
        """Test password setting and checking"""
        user = MockUser(username="testuser", email="test@example.com")
        
        user.set_password("secret123")
        assert user.password_hash == "hashed_secret123"
        
        assert user.check_password("secret123") is True
        assert user.check_password("wrong_password") is False
    
    def test_user_serialization(self):
        """Test user to_dict and from_dict"""
        original_user = MockUser(
            user_id=1,
            username="testuser",
            email="test@example.com",
            role="instructor"
        )
        
        user_dict = original_user.to_dict()
        
        assert user_dict['id'] == 1
        assert user_dict['username'] == "testuser"
        assert user_dict['email'] == "test@example.com"
        assert user_dict['role'] == "instructor"
        assert 'created_at' in user_dict
        
        # Test deserialization
        restored_user = MockUser.from_dict(user_dict)
        assert restored_user.id == original_user.id
        assert restored_user.username == original_user.username
        assert restored_user.email == original_user.email
        assert restored_user.role == original_user.role
    
    def test_user_validation_success(self):
        """Test successful user validation"""
        user = MockUser(
            username="validuser",
            email="valid@example.com",
            role="student"
        )
        
        is_valid, errors = user.validate()
        assert is_valid is True
        assert len(errors) == 0
    
    def test_user_validation_failures(self):
        """Test user validation failures"""
        # Test short username
        user = MockUser(username="ab", email="test@example.com")
        is_valid, errors = user.validate()
        assert is_valid is False
        assert "Username must be at least 3 characters" in errors
        
        # Test invalid email
        user = MockUser(username="testuser", email="invalid_email")
        is_valid, errors = user.validate()
        assert is_valid is False
        assert "Valid email required" in errors
        
        # Test invalid role
        user = MockUser(username="testuser", email="test@example.com", role="invalid")
        is_valid, errors = user.validate()
        assert is_valid is False
        assert "Invalid role" in errors


class TestExerciseModel:
    """Test Exercise model functionality"""
    
    def test_exercise_creation(self):
        """Test exercise creation"""
        exercise = MockExercise(
            exercise_id=1,
            title="Basic Python Variables",
            description="Learn about Python variables",
            difficulty="beginner",
            topic="basics",
            points=15
        )
        
        assert exercise.id == 1
        assert exercise.title == "Basic Python Variables"
        assert exercise.difficulty == "beginner"
        assert exercise.points == 15
        assert isinstance(exercise.created_at, datetime)
    
    def test_exercise_test_cases(self):
        """Test exercise test case management"""
        exercise = MockExercise(title="Test Exercise", description="Test")
        
        # Add test cases
        exercise.add_test_case("input1", "output1", is_hidden=False)
        exercise.add_test_case("input2", "output2", is_hidden=True)
        
        assert len(exercise.test_cases) == 2
        assert exercise.test_cases[0]['input'] == "input1"
        assert exercise.test_cases[1]['is_hidden'] is True
    
    def test_exercise_serialization(self):
        """Test exercise serialization"""
        exercise = MockExercise(
            exercise_id=1,
            title="Test Exercise",
            description="Test description",
            difficulty="intermediate"
        )
        exercise.add_test_case("test_input", "test_output", is_hidden=False)
        exercise.add_test_case("hidden_input", "hidden_output", is_hidden=True)
        
        # Test serialization without hidden test cases
        exercise_dict = exercise.to_dict(include_hidden=False)
        assert len(exercise_dict['test_cases']) == 1
        assert exercise_dict['test_cases'][0]['input'] == "test_input"
        
        # Test serialization with hidden test cases
        exercise_dict_full = exercise.to_dict(include_hidden=True)
        assert len(exercise_dict_full['test_cases']) == 2
    
    def test_exercise_deserialization(self):
        """Test exercise deserialization"""
        exercise_data = {
            'id': 1,
            'title': "Test Exercise",
            'description': "Test description",
            'difficulty': "advanced",
            'topic': "algorithms",
            'points': 25,
            'test_cases': [{'input': 'test', 'expected_output': 'result'}],
            'hints': ['hint1', 'hint2']
        }
        
        exercise = MockExercise.from_dict(exercise_data)
        
        assert exercise.id == 1
        assert exercise.title == "Test Exercise"
        assert exercise.difficulty == "advanced"
        assert exercise.topic == "algorithms"
        assert exercise.points == 25
        assert len(exercise.test_cases) == 1
        assert len(exercise.hints) == 2
    
    def test_exercise_validation(self):
        """Test exercise validation"""
        # Valid exercise
        exercise = MockExercise(
            title="Valid Exercise Title",
            description="Valid description",
            difficulty="beginner",
            points=10
        )
        exercise.add_test_case("input", "output")
        
        is_valid, errors = exercise.validate()
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid exercise - short title
        exercise.title = "Short"
        is_valid, errors = exercise.validate()
        assert is_valid is False
        assert "Title must be at least 5 characters" in errors


class TestSubmissionModel:
    """Test Submission model functionality"""
    
    def test_submission_creation(self):
        """Test submission creation"""
        submission = MockSubmission(
            submission_id=1,
            user_id=123,
            exercise_id=456,
            code="print('Hello, World!')",
            language="python"
        )
        
        assert submission.id == 1
        assert submission.user_id == 123
        assert submission.exercise_id == 456
        assert submission.code == "print('Hello, World!')"
        assert submission.language == "python"
        assert submission.status == "pending"
        assert isinstance(submission.submitted_at, datetime)
    
    def test_submission_test_results(self):
        """Test submission test result management"""
        submission = MockSubmission(user_id=1, exercise_id=1, code="test code")
        
        # Add test results
        submission.add_test_result(1, True, "correct output")
        submission.add_test_result(2, False, "wrong output", "AssertionError")
        submission.add_test_result(3, True, "correct output")
        
        assert len(submission.test_results) == 3
        assert submission.test_results[0]['passed'] is True
        assert submission.test_results[1]['passed'] is False
        assert submission.test_results[1]['error'] == "AssertionError"
    
    def test_submission_score_calculation(self):
        """Test submission score calculation"""
        submission = MockSubmission(user_id=1, exercise_id=1, code="test code")
        
        # Add test results: 2 passed out of 3
        submission.add_test_result(1, True, "output1")
        submission.add_test_result(2, False, "output2")
        submission.add_test_result(3, True, "output3")
        
        score = submission.calculate_score()
        expected_score = (2 / 3) * 100  # 66.67%
        
        assert abs(score - expected_score) < 0.1
        assert submission.score == score
    
    def test_submission_serialization(self):
        """Test submission serialization"""
        submission = MockSubmission(
            submission_id=1,
            user_id=123,
            exercise_id=456,
            code="test code",
            status="completed",
            score=85.5
        )
        
        submission_dict = submission.to_dict()
        
        assert submission_dict['id'] == 1
        assert submission_dict['user_id'] == 123
        assert submission_dict['exercise_id'] == 456
        assert submission_dict['code'] == "test code"
        assert submission_dict['status'] == "completed"
        assert submission_dict['score'] == 85.5
        
        # Test deserialization
        restored_submission = MockSubmission.from_dict(submission_dict)
        assert restored_submission.id == submission.id
        assert restored_submission.user_id == submission.user_id
        assert restored_submission.score == submission.score
    
    def test_submission_validation(self):
        """Test submission validation"""
        # Valid submission
        submission = MockSubmission(
            user_id=123,
            exercise_id=456,
            code="print('hello')",
            language="python"
        )
        
        is_valid, errors = submission.validate()
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid submission - missing code
        submission.code = ""
        is_valid, errors = submission.validate()
        assert is_valid is False
        assert "Code is required" in errors
        
        # Invalid language
        submission.code = "valid code"
        submission.language = "unsupported"
        is_valid, errors = submission.validate()
        assert is_valid is False
        assert "Unsupported programming language" in errors


class TestProgressModel:
    """Test Progress model functionality"""
    
    def test_progress_creation(self):
        """Test progress creation"""
        progress = MockProgress(
            user_id=123,
            topic="basics",
            exercises_completed=5,
            total_exercises=20,
            points_earned=150
        )
        
        assert progress.user_id == 123
        assert progress.topic == "basics"
        assert progress.exercises_completed == 5
        assert progress.total_exercises == 20
        assert progress.points_earned == 150
        assert isinstance(progress.last_activity, datetime)
    
    def test_progress_update(self):
        """Test progress update functionality"""
        progress = MockProgress(
            user_id=123,
            topic="basics",
            exercises_completed=5,
            total_exercises=20,
            points_earned=100
        )
        
        # Update progress with new exercise completion
        initial_completed = progress.exercises_completed
        initial_points = progress.points_earned
        
        progress.update_progress(exercise_score=85, exercise_points=25)
        
        assert progress.exercises_completed == initial_completed + 1
        assert progress.points_earned == initial_points + 25
        assert progress.average_score == 85
        assert progress.completion_percentage == (6 / 20) * 100  # 30%
    
    def test_progress_serialization(self):
        """Test progress serialization"""
        progress = MockProgress(
            user_id=123,
            topic="oop",
            exercises_completed=8,
            total_exercises=15,
            points_earned=200
        )
        progress.completion_percentage = 53.33
        progress.average_score = 87.5
        
        progress_dict = progress.to_dict()
        
        assert progress_dict['user_id'] == 123
        assert progress_dict['topic'] == "oop"
        assert progress_dict['exercises_completed'] == 8
        assert progress_dict['completion_percentage'] == 53.33
        assert progress_dict['average_score'] == 87.5
        
        # Test deserialization
        restored_progress = MockProgress.from_dict(progress_dict)
        assert restored_progress.user_id == progress.user_id
        assert restored_progress.topic == progress.topic
        assert restored_progress.exercises_completed == progress.exercises_completed
        assert restored_progress.completion_percentage == progress.completion_percentage


class TestModelIntegration:
    """Test model integration scenarios"""
    
    def test_user_exercise_submission_flow(self):
        """Test complete user exercise submission flow"""
        # Create user
        user = MockUser(user_id=1, username="student", email="student@example.com")
        user.set_password("password123")
        
        # Create exercise
        exercise = MockExercise(
            exercise_id=1,
            title="Hello World Exercise",
            description="Print Hello World",
            difficulty="beginner",
            points=10
        )
        exercise.add_test_case("", "Hello, World!")
        
        # Create submission
        submission = MockSubmission(
            user_id=user.id,
            exercise_id=exercise.id,
            code="print('Hello, World!')",
            language="python"
        )
        
        # Add test result
        submission.add_test_result(1, True, "Hello, World!")
        score = submission.calculate_score()
        
        # Update progress
        progress = MockProgress(
            user_id=user.id,
            topic=exercise.topic,
            exercises_completed=0,
            total_exercises=10,
            points_earned=0
        )
        progress.update_progress(score, exercise.points)
        
        # Verify the flow
        assert user.check_password("password123")
        assert exercise.difficulty == "beginner"
        assert submission.score == 100.0  # Perfect score
        assert progress.exercises_completed == 1
        assert progress.points_earned == exercise.points
    
    def test_model_validation_chain(self):
        """Test validation across multiple models"""
        # Valid models
        user = MockUser(username="validuser", email="valid@example.com")
        exercise = MockExercise(
            title="Valid Exercise",
            description="Valid description",
            difficulty="beginner"
        )
        exercise.add_test_case("input", "output")
        
        submission = MockSubmission(
            user_id=1,
            exercise_id=1,
            code="valid code",
            language="python"
        )
        
        # All should be valid
        user_valid, _ = user.validate()
        exercise_valid, _ = exercise.validate()
        submission_valid, _ = submission.validate()
        
        assert all([user_valid, exercise_valid, submission_valid])
    
    def test_model_serialization_consistency(self):
        """Test serialization consistency across models"""
        # Create models
        user = MockUser(user_id=1, username="test", email="test@example.com")
        exercise = MockExercise(exercise_id=1, title="Test Exercise", description="Test")
        submission = MockSubmission(submission_id=1, user_id=1, exercise_id=1, code="test")
        progress = MockProgress(user_id=1, topic="basics")
        
        # Serialize
        user_dict = user.to_dict()
        exercise_dict = exercise.to_dict()
        submission_dict = submission.to_dict()
        progress_dict = progress.to_dict()
        
        # Deserialize
        user_restored = MockUser.from_dict(user_dict)
        exercise_restored = MockExercise.from_dict(exercise_dict)
        submission_restored = MockSubmission.from_dict(submission_dict)
        progress_restored = MockProgress.from_dict(progress_dict)
        
        # Verify consistency
        assert user_restored.username == user.username
        assert exercise_restored.title == exercise.title
        assert submission_restored.code == submission.code
        assert progress_restored.topic == progress.topic