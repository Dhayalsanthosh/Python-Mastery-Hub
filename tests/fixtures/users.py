# tests/fixtures/users.py
# User-related test fixtures

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import hashlib
import uuid

# Import your user models and services (adjust based on your actual structure)
try:
    from src.models.user import User
    from src.services.auth import AuthService
    from src.services.user_service import UserService
    from src.core.user_manager import UserManager
except ImportError:
    # Mock classes for when actual models don't exist
    class User:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class AuthService:
        pass
    
    class UserService:
        pass
    
    class UserManager:
        pass


def hash_password(password: str) -> str:
    """Simple password hashing for testing."""
    return hashlib.sha256(password.encode()).hexdigest()


@pytest.fixture
def test_user():
    """Create a basic test user."""
    user_data = {
        'id': 'test_user_001',
        'email': 'testuser@example.com',
        'username': 'testuser',
        'password_hash': hash_password('testpass123'),
        'full_name': 'Test User',
        'skill_level': 'beginner',
        'preferred_language': 'en',
        'timezone': 'UTC',
        'is_active': True,
        'email_verified': True,
        'created_at': datetime.utcnow() - timedelta(days=30),
        'last_active': datetime.utcnow() - timedelta(hours=1),
        'profile': {
            'bio': 'I am learning Python!',
            'goals': ['Learn basics', 'Build projects'],
            'interests': ['web development', 'data science']
        },
        'settings': {
            'theme': 'light',
            'notifications_enabled': True,
            'email_notifications': True,
            'difficulty_preference': 'adaptive'
        }
    }
    
    return User(**user_data)


@pytest.fixture
def admin_user():
    """Create an admin test user."""
    user_data = {
        'id': 'admin_user_001',
        'email': 'admin@example.com',
        'username': 'admin',
        'password_hash': hash_password('adminpass123'),
        'full_name': 'Admin User',
        'skill_level': 'advanced',
        'preferred_language': 'en',
        'timezone': 'UTC',
        'is_active': True,
        'email_verified': True,
        'is_admin': True,
        'is_staff': True,
        'created_at': datetime.utcnow() - timedelta(days=100),
        'last_active': datetime.utcnow() - timedelta(minutes=15),
        'permissions': [
            'create_exercises',
            'edit_exercises',
            'delete_exercises',
            'manage_users',
            'view_analytics'
        ]
    }
    
    return User(**user_data)


@pytest.fixture
def inactive_user():
    """Create an inactive test user."""
    user_data = {
        'id': 'inactive_user_001',
        'email': 'inactive@example.com',
        'username': 'inactive',
        'password_hash': hash_password('inactivepass123'),
        'full_name': 'Inactive User',
        'skill_level': 'beginner',
        'is_active': False,
        'email_verified': False,
        'created_at': datetime.utcnow() - timedelta(days=90),
        'last_active': datetime.utcnow() - timedelta(days=60),
        'deactivated_at': datetime.utcnow() - timedelta(days=60),
        'deactivation_reason': 'User requested account deletion'
    }
    
    return User(**user_data)


@pytest.fixture
def multiple_users():
    """Create multiple test users with different characteristics."""
    users = []
    
    # Beginner user
    users.append(User(
        id='user_beginner_001',
        email='beginner@example.com',
        username='beginner',
        password_hash=hash_password('beginnerpass'),
        full_name='Beginner User',
        skill_level='beginner',
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow() - timedelta(days=5),
        progress_stats={
            'exercises_completed': 5,
            'total_points': 50,
            'current_streak': 3,
            'longest_streak': 3
        }
    ))
    
    # Intermediate user
    users.append(User(
        id='user_intermediate_001',
        email='intermediate@example.com',
        username='intermediate',
        password_hash=hash_password('intermediatepass'),
        full_name='Intermediate User',
        skill_level='intermediate',
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow() - timedelta(days=45),
        progress_stats={
            'exercises_completed': 25,
            'total_points': 350,
            'current_streak': 7,
            'longest_streak': 15
        }
    ))
    
    # Advanced user
    users.append(User(
        id='user_advanced_001',
        email='advanced@example.com',
        username='advanced',
        password_hash=hash_password('advancedpass'),
        full_name='Advanced User',
        skill_level='advanced',
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow() - timedelta(days=120),
        progress_stats={
            'exercises_completed': 75,
            'total_points': 1250,
            'current_streak': 12,
            'longest_streak': 30
        }
    ))
    
    # Premium user
    users.append(User(
        id='user_premium_001',
        email='premium@example.com',
        username='premium',
        password_hash=hash_password('premiumpass'),
        full_name='Premium User',
        skill_level='intermediate',
        is_active=True,
        email_verified=True,
        is_premium=True,
        premium_expires_at=datetime.utcnow() + timedelta(days=365),
        created_at=datetime.utcnow() - timedelta(days=60),
        subscription={
            'plan': 'premium',
            'status': 'active',
            'billing_cycle': 'yearly',
            'next_billing_date': datetime.utcnow() + timedelta(days=300)
        }
    ))
    
    return users


@pytest.fixture
def user_with_progress(test_user):
    """Create a user with learning progress."""
    progress_data = {
        'total_exercises_completed': 15,
        'total_points_earned': 180,
        'current_streak_days': 5,
        'longest_streak_days': 12,
        'time_spent_learning': 3600,  # 1 hour in seconds
        'topics_mastered': ['variables', 'data_types', 'basic_operations'],
        'topics_in_progress': ['functions', 'loops'],
        'skill_assessments': {
            'variables': 85,
            'data_types': 90,
            'basic_operations': 78,
            'functions': 65
        },
        'achievements': [
            {
                'id': 'first_exercise',
                'name': 'First Steps',
                'description': 'Completed your first exercise',
                'earned_at': datetime.utcnow() - timedelta(days=20)
            },
            {
                'id': 'streak_5',
                'name': '5-Day Streak',
                'description': 'Completed exercises for 5 consecutive days',
                'earned_at': datetime.utcnow() - timedelta(days=1)
            }
        ],
        'learning_path': {
            'current_topic': 'functions',
            'next_exercise': 'ex_functions_001',
            'recommended_exercises': ['ex_functions_001', 'ex_functions_002'],
            'completion_percentage': 45.5
        }
    }
    
    # Add progress data to user
    for key, value in progress_data.items():
        setattr(test_user, key, value)
    
    return test_user


@pytest.fixture
def authenticated_user_session():
    """Create an authenticated user session."""
    session_data = {
        'user_id': 'test_user_001',
        'session_token': str(uuid.uuid4()),
        'csrf_token': str(uuid.uuid4()),
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(hours=24),
        'ip_address': '192.168.1.100',
        'user_agent': 'Mozilla/5.0 (Test Browser)',
        'is_active': True,
        'last_activity': datetime.utcnow(),
        'permissions': ['read', 'write', 'execute_code']
    }
    
    return session_data


@pytest.fixture
def user_registration_data():
    """Sample user registration data."""
    return {
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'newuserpass123',
        'password_confirm': 'newuserpass123',
        'full_name': 'New User',
        'skill_level': 'beginner',
        'preferred_language': 'en',
        'timezone': 'America/New_York',
        'terms_accepted': True,
        'marketing_consent': False,
        'referral_code': None
    }


@pytest.fixture
def user_login_data():
    """Sample user login data."""
    return {
        'email': 'testuser@example.com',
        'password': 'testpass123',
        'remember_me': True,
        'captcha_token': 'valid_captcha_token'
    }


@pytest.fixture
def user_update_data():
    """Sample user update data."""
    return {
        'full_name': 'Updated Test User',
        'bio': 'I am actively learning Python and loving it!',
        'skill_level': 'intermediate',
        'goals': ['Master Python basics', 'Build web applications', 'Learn data science'],
        'interests': ['web development', 'machine learning', 'automation'],
        'timezone': 'America/Los_Angeles',
        'preferred_language': 'en',
        'profile_picture_url': 'https://example.com/avatar.jpg'
    }


@pytest.fixture
def mock_auth_service():
    """Create a mock authentication service."""
    service = Mock(spec=AuthService)
    
    # Mock authentication methods
    service.authenticate_user = AsyncMock(return_value={
        'success': True,
        'user_id': 'test_user_001',
        'token': 'mock_jwt_token',
        'expires_in': 3600
    })
    
    service.create_session = AsyncMock(return_value='mock_session_token')
    service.validate_session = AsyncMock(return_value=True)
    service.invalidate_session = AsyncMock(return_value=True)
    service.refresh_token = AsyncMock(return_value='new_mock_token')
    service.verify_password = Mock(return_value=True)
    service.hash_password = Mock(return_value='hashed_password')
    
    # Mock password reset
    service.generate_reset_token = AsyncMock(return_value='reset_token_123')
    service.validate_reset_token = AsyncMock(return_value=True)
    service.reset_password = AsyncMock(return_value=True)
    
    # Mock email verification
    service.generate_verification_token = AsyncMock(return_value='verify_token_123')
    service.verify_email = AsyncMock(return_value=True)
    
    return service


@pytest.fixture
def mock_user_service():
    """Create a mock user service."""
    service = Mock(spec=UserService)
    
    # Mock user CRUD operations
    service.create_user = AsyncMock()
    service.get_user_by_id = AsyncMock()
    service.get_user_by_email = AsyncMock()
    service.get_user_by_username = AsyncMock()
    service.update_user = AsyncMock()
    service.delete_user = AsyncMock()
    service.activate_user = AsyncMock()
    service.deactivate_user = AsyncMock()
    
    # Mock user progress operations
    service.update_progress = AsyncMock()
    service.get_user_stats = AsyncMock()
    service.calculate_skill_level = AsyncMock()
    service.get_learning_recommendations = AsyncMock()
    
    # Mock user preferences
    service.update_preferences = AsyncMock()
    service.get_preferences = AsyncMock()
    
    return service


@pytest.fixture
def mock_user_manager():
    """Create a mock user manager."""
    manager = Mock(spec=UserManager)
    
    # Mock high-level user operations
    manager.register_user = AsyncMock()
    manager.login_user = AsyncMock()
    manager.logout_user = AsyncMock()
    manager.update_profile = AsyncMock()
    manager.change_password = AsyncMock()
    manager.reset_password = AsyncMock()
    manager.verify_email = AsyncMock()
    
    # Mock user analytics
    manager.get_user_analytics = AsyncMock()
    manager.get_learning_insights = AsyncMock()
    manager.generate_progress_report = AsyncMock()
    
    return manager


@pytest.fixture
def user_test_cases():
    """Test cases for user validation."""
    return {
        'valid_emails': [
            'user@example.com',
            'test.user@domain.co.uk',
            'user+tag@example.org',
            'user123@example-domain.com'
        ],
        'invalid_emails': [
            'invalid.email',
            '@example.com',
            'user@',
            'user space@example.com',
            'user@.com'
        ],
        'valid_usernames': [
            'user123',
            'test_user',
            'testuser',
            'user-name',
            'User123'
        ],
        'invalid_usernames': [
            'us',  # too short
            'user name',  # contains space
            'user@name',  # contains @
            'a' * 51,  # too long
            '123user'  # starts with number
        ],
        'valid_passwords': [
            'password123',
            'StrongP@ssw0rd',
            'MySecurePassword!',
            'Test123Pass'
        ],
        'invalid_passwords': [
            'pass',  # too short
            'password',  # no numbers
            '12345678',  # no letters
            'PASSWORD123'  # no lowercase
        ]
    }


@pytest.fixture
def user_permissions():
    """Different user permission sets."""
    return {
        'guest': [],
        'user': [
            'view_exercises',
            'submit_solutions',
            'view_own_progress'
        ],
        'premium_user': [
            'view_exercises',
            'submit_solutions',
            'view_own_progress',
            'access_premium_content',
            'unlimited_hints',
            'priority_support'
        ],
        'moderator': [
            'view_exercises',
            'submit_solutions',
            'view_own_progress',
            'moderate_content',
            'view_user_reports',
            'manage_comments'
        ],
        'admin': [
            'view_exercises',
            'submit_solutions',
            'view_own_progress',
            'create_exercises',
            'edit_exercises',
            'delete_exercises',
            'manage_users',
            'view_analytics',
            'system_admin'
        ]
    }


# Helper functions for user testing
def create_user_with_role(role='user', **kwargs):
    """Helper to create users with specific roles."""
    permissions_map = {
        'guest': [],
        'user': ['view_exercises', 'submit_solutions'],
        'premium': ['view_exercises', 'submit_solutions', 'premium_content'],
        'admin': ['all_permissions']
    }
    
    base_data = {
        'id': f'{role}_user_{uuid.uuid4().hex[:8]}',
        'email': f'{role}@example.com',
        'username': role,
        'password_hash': hash_password(f'{role}pass123'),
        'full_name': f'{role.title()} User',
        'skill_level': 'beginner',
        'is_active': True,
        'email_verified': True,
        'permissions': permissions_map.get(role, []),
        'created_at': datetime.utcnow()
    }
    
    if role == 'admin':
        base_data.update({
            'is_admin': True,
            'is_staff': True
        })
    elif role == 'premium':
        base_data.update({
            'is_premium': True,
            'premium_expires_at': datetime.utcnow() + timedelta(days=365)
        })
    
    base_data.update(kwargs)
    return User(**base_data)


def assert_user_data_valid(user_data):
    """Helper to validate user data structure."""
    required_fields = ['email', 'username', 'password_hash', 'full_name']
    
    for field in required_fields:
        assert field in user_data, f"Missing required field: {field}"
    
    assert '@' in user_data['email'], "Email must contain @"
    assert len(user_data['username']) >= 3, "Username must be at least 3 characters"
    assert len(user_data['password_hash']) > 0, "Password hash cannot be empty"