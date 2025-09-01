# tests/fixtures/database.py
# Database-related test fixtures

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

# Import your database models (adjust based on your actual structure)
try:
    from src.database.models import Base, User, Exercise, UserProgress, Topic, Hint
    from src.database.connection import DatabaseManager
except ImportError:
    # Mock classes for when actual models don't exist
    class Base:
        metadata = type('MockMetadata', (), {
            'create_all': lambda **kwargs: None,
            'drop_all': lambda **kwargs: None,
        })()
    
    class User:
        pass
    
    class Exercise:
        pass
    
    class UserProgress:
        pass
    
    class Topic:
        pass
    
    class Hint:
        pass
    
    class DatabaseManager:
        pass


@pytest.fixture(scope="session")
def test_database():
    """Create a test database for the session."""
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(test_database):
    """Create a database session for testing."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_database
    )
    
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def clean_database(db_session):
    """Ensure database is clean before each test."""
    # Clear all tables before test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(text(f"DELETE FROM {table.name}"))
    db_session.commit()
    
    yield db_session
    
    # Clean up after test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(text(f"DELETE FROM {table.name}"))
    db_session.commit()


@pytest.fixture
async def async_db_session(test_database):
    """Create an async database session for testing."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    
    # Create async engine (you might need to adjust the URL format)
    async_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = AsyncSession(async_engine)
    
    try:
        yield async_session
    finally:
        await async_session.rollback()
        await async_session.close()
        await async_engine.dispose()


@pytest.fixture
def sample_db_data(clean_database):
    """Populate database with sample data for testing."""
    session = clean_database
    
    # Create sample topics
    topics = [
        Topic(
            id="topic_basics",
            name="Python Basics",
            description="Fundamental Python concepts",
            difficulty="beginner",
            order_index=1
        ),
        Topic(
            id="topic_oop",
            name="Object-Oriented Programming",
            description="Classes, objects, and inheritance",
            difficulty="intermediate",
            order_index=2
        ),
        Topic(
            id="topic_algorithms",
            name="Algorithms",
            description="Problem-solving and algorithms",
            difficulty="advanced",
            order_index=3
        )
    ]
    
    for topic in topics:
        session.add(topic)
    
    # Create sample users
    users = [
        User(
            id="user_001",
            email="alice@example.com",
            username="alice",
            password_hash="hashed_password_123",
            full_name="Alice Johnson",
            skill_level="beginner",
            is_active=True,
            email_verified=True,
            created_at=datetime.utcnow() - timedelta(days=30)
        ),
        User(
            id="user_002",
            email="bob@example.com",
            username="bob",
            password_hash="hashed_password_456",
            full_name="Bob Smith",
            skill_level="intermediate",
            is_active=True,
            email_verified=True,
            created_at=datetime.utcnow() - timedelta(days=15)
        ),
        User(
            id="admin_001",
            email="admin@example.com",
            username="admin",
            password_hash="hashed_admin_password",
            full_name="Admin User",
            skill_level="advanced",
            is_active=True,
            email_verified=True,
            is_admin=True,
            created_at=datetime.utcnow() - timedelta(days=100)
        )
    ]
    
    for user in users:
        session.add(user)
    
    # Create sample exercises
    exercises = [
        Exercise(
            id="ex_001",
            title="Variable Assignment",
            description="Learn to assign values to variables",
            topic_id="topic_basics",
            difficulty="beginner",
            order_index=1,
            template_code="# Assign the value 42 to variable x\n",
            solution_code="x = 42",
            test_cases='[{"test": "assert x == 42", "description": "x should equal 42"}]',
            points=10,
            estimated_time=5,
            is_active=True
        ),
        Exercise(
            id="ex_002",
            title="String Concatenation",
            description="Learn to concatenate strings",
            topic_id="topic_basics",
            difficulty="beginner",
            order_index=2,
            template_code="# Concatenate 'Hello' and 'World'\n",
            solution_code="result = 'Hello' + ' ' + 'World'",
            test_cases='[{"test": "assert result == \'Hello World\'", "description": "result should be \'Hello World\'"}]',
            points=10,
            estimated_time=5,
            is_active=True
        ),
        Exercise(
            id="ex_003",
            title="Simple Class",
            description="Create a basic class",
            topic_id="topic_oop",
            difficulty="intermediate",
            order_index=1,
            template_code="# Create a class named Person\n",
            solution_code="class Person:\n    def __init__(self, name):\n        self.name = name",
            test_cases='[{"test": "p = Person(\'Alice\'); assert p.name == \'Alice\'", "description": "Person class should work correctly"}]',
            points=20,
            estimated_time=10,
            is_active=True
        )
    ]
    
    for exercise in exercises:
        session.add(exercise)
    
    # Create sample hints
    hints = [
        Hint(
            id="hint_001",
            exercise_id="ex_001",
            content="Use the assignment operator (=) to assign a value to a variable",
            order_index=1,
            unlock_after_attempts=1
        ),
        Hint(
            id="hint_002",
            exercise_id="ex_001",
            content="The syntax is: variable_name = value",
            order_index=2,
            unlock_after_attempts=2
        ),
        Hint(
            id="hint_003",
            exercise_id="ex_002",
            content="Use the + operator to concatenate strings",
            order_index=1,
            unlock_after_attempts=1
        )
    ]
    
    for hint in hints:
        session.add(hint)
    
    # Create sample user progress
    progress_records = [
        UserProgress(
            id="prog_001",
            user_id="user_001",
            exercise_id="ex_001",
            status="completed",
            score=95,
            attempts=1,
            time_spent=180,  # 3 minutes
            completed_at=datetime.utcnow() - timedelta(days=5),
            solution_code="x = 42",
            feedback="Perfect! Great job on your first exercise."
        ),
        UserProgress(
            id="prog_002",
            user_id="user_001",
            exercise_id="ex_002",
            status="in_progress",
            score=0,
            attempts=2,
            time_spent=300,  # 5 minutes
            started_at=datetime.utcnow() - timedelta(hours=2),
            solution_code="result = 'Hello' + 'World'",  # Missing space
            feedback="Almost there! Check your spacing."
        ),
        UserProgress(
            id="prog_003",
            user_id="user_002",
            exercise_id="ex_001",
            status="completed",
            score=85,
            attempts=3,
            time_spent=420,  # 7 minutes
            completed_at=datetime.utcnow() - timedelta(days=2),
            solution_code="x = 42",
            feedback="Good work! You got it after a few tries."
        )
    ]
    
    for progress in progress_records:
        session.add(progress)
    
    session.commit()
    
    return {
        'topics': topics,
        'users': users,
        'exercises': exercises,
        'hints': hints,
        'progress': progress_records
    }


@pytest.fixture
def database_transaction(db_session):
    """Create a database transaction that can be rolled back."""
    transaction = db_session.begin()
    
    yield db_session
    
    transaction.rollback()


@pytest.fixture
def populated_database(sample_db_data):
    """Database populated with comprehensive test data."""
    return sample_db_data


@contextmanager
def database_snapshot(session):
    """Create a snapshot of database state that can be restored."""
    # Store initial state
    initial_state = {}
    
    for table in Base.metadata.sorted_tables:
        result = session.execute(text(f"SELECT * FROM {table.name}"))
        initial_state[table.name] = result.fetchall()
    
    try:
        yield session
    finally:
        # Restore initial state
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(text(f"DELETE FROM {table.name}"))
        
        for table_name, rows in initial_state.items():
            if rows:
                # Note: This is a simplified restoration
                # In practice, you might need more sophisticated logic
                pass
        
        session.commit()


@pytest.fixture
def mock_database_manager():
    """Create a mock database manager for unit tests."""
    from unittest.mock import Mock, AsyncMock
    
    manager = Mock(spec=DatabaseManager)
    manager.get_session = Mock()
    manager.create_user = AsyncMock()
    manager.get_user = AsyncMock()
    manager.update_user = AsyncMock()
    manager.delete_user = AsyncMock()
    manager.create_exercise = AsyncMock()
    manager.get_exercise = AsyncMock()
    manager.update_exercise = AsyncMock()
    manager.delete_exercise = AsyncMock()
    manager.save_progress = AsyncMock()
    manager.get_progress = AsyncMock()
    
    return manager


@pytest.fixture
def database_performance_test():
    """Fixture for database performance testing."""
    import time
    
    start_time = time.time()
    query_count = 0
    
    def track_query():
        nonlocal query_count
        query_count += 1
    
    yield {
        'track_query': track_query,
        'get_query_count': lambda: query_count,
        'get_elapsed_time': lambda: time.time() - start_time
    }


# Database utility functions for tests
def create_test_user(session, **kwargs):
    """Helper function to create a test user."""
    default_data = {
        'id': f'test_user_{datetime.utcnow().timestamp()}',
        'email': 'test@example.com',
        'username': 'testuser',
        'password_hash': 'hashed_password',
        'full_name': 'Test User',
        'skill_level': 'beginner',
        'is_active': True,
        'email_verified': True,
        'created_at': datetime.utcnow()
    }
    
    default_data.update(kwargs)
    user = User(**default_data)
    session.add(user)
    session.commit()
    
    return user


def create_test_exercise(session, **kwargs):
    """Helper function to create a test exercise."""
    default_data = {
        'id': f'test_ex_{datetime.utcnow().timestamp()}',
        'title': 'Test Exercise',
        'description': 'A test exercise',
        'topic_id': 'topic_basics',
        'difficulty': 'beginner',
        'order_index': 1,
        'template_code': '# Your code here',
        'solution_code': 'pass',
        'test_cases': '[]',
        'points': 10,
        'estimated_time': 5,
        'is_active': True
    }
    
    default_data.update(kwargs)
    exercise = Exercise(**default_data)
    session.add(exercise)
    session.commit()
    
    return exercise


def create_test_progress(session, user_id, exercise_id, **kwargs):
    """Helper function to create a test progress record."""
    default_data = {
        'id': f'test_prog_{datetime.utcnow().timestamp()}',
        'user_id': user_id,
        'exercise_id': exercise_id,
        'status': 'completed',
        'score': 100,
        'attempts': 1,
        'time_spent': 60,
        'completed_at': datetime.utcnow(),
        'solution_code': 'pass',
        'feedback': 'Great job!'
    }
    
    default_data.update(kwargs)
    progress = UserProgress(**default_data)
    session.add(progress)
    session.commit()
    
    return progress