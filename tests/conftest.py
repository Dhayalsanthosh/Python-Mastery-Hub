# tests/conftest.py
# Pytest configuration file with shared fixtures and settings

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import your application modules (adjust imports based on your actual structure)
try:
    from src.database.models import Base
    from src.database.connection import get_database_session
    from src.web.app import create_app
    from src.core.user_manager import UserManager
    from src.core.exercise_engine import ExerciseEngine
    from src.core.progress_tracker import ProgressTracker
except ImportError:
    # Fallback for when modules don't exist yet
    Base = None
    get_database_session = None
    create_app = None
    UserManager = None
    ExerciseEngine = None
    ProgressTracker = None


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "requires_web: mark test as requiring web server"
    )


# Async test support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Database fixtures
@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine using SQLite in memory."""
    if Base is None:
        pytest.skip("Database models not available")
    
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def test_db_session(test_db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def mock_db_session():
    """Create a mock database session for unit tests."""
    session = Mock()
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    session.flush = Mock()
    session.refresh = Mock()
    return session


# File system fixtures
@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_file():
    """Create a temporary file for tests."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        temp_path = Path(tmp.name)
    
    yield temp_path
    
    if temp_path.exists():
        temp_path.unlink()


# Web application fixtures
@pytest.fixture
def test_app():
    """Create a test Flask/FastAPI application instance."""
    if create_app is None:
        pytest.skip("Web application not available")
    
    app = create_app(testing=True)
    app.config.update({
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False
    })
    
    return app


@pytest.fixture
def test_client(test_app):
    """Create a test client for the web application."""
    with test_app.test_client() as client:
        with test_app.app_context():
            yield client


@pytest.fixture
def authenticated_client(test_client, test_user):
    """Create an authenticated test client."""
    # Login the test user
    response = test_client.post('/auth/login', json={
        'email': test_user.email,
        'password': 'testpass123'
    })
    
    if response.status_code == 200:
        # Extract token or session info if needed
        pass
    
    return test_client


# Core service fixtures
@pytest.fixture
def mock_user_manager():
    """Create a mock UserManager for testing."""
    if UserManager is None:
        manager = Mock()
    else:
        manager = Mock(spec=UserManager)
    
    manager.create_user = AsyncMock()
    manager.authenticate_user = AsyncMock()
    manager.get_user_by_email = AsyncMock()
    manager.update_user_progress = AsyncMock()
    
    return manager


@pytest.fixture
def mock_exercise_engine():
    """Create a mock ExerciseEngine for testing."""
    if ExerciseEngine is None:
        engine = Mock()
    else:
        engine = Mock(spec=ExerciseEngine)
    
    engine.get_exercise = AsyncMock()
    engine.evaluate_solution = AsyncMock()
    engine.get_next_exercise = AsyncMock()
    engine.generate_hints = AsyncMock()
    
    return engine


@pytest.fixture
def mock_progress_tracker():
    """Create a mock ProgressTracker for testing."""
    if ProgressTracker is None:
        tracker = Mock()
    else:
        tracker = Mock(spec=ProgressTracker)
    
    tracker.track_completion = AsyncMock()
    tracker.get_user_progress = AsyncMock()
    tracker.calculate_mastery = AsyncMock()
    tracker.suggest_next_topics = AsyncMock()
    
    return tracker


# CLI fixtures
@pytest.fixture
def cli_runner():
    """Create a CLI test runner."""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def isolated_filesystem(cli_runner):
    """Create an isolated filesystem for CLI tests."""
    with cli_runner.isolated_filesystem():
        yield


# Mock external services
@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    client = Mock()
    client.chat = Mock()
    client.chat.completions = Mock()
    client.chat.completions.create = AsyncMock()
    
    return client


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client."""
    client = Mock()
    client.get = AsyncMock()
    client.set = AsyncMock()
    client.delete = AsyncMock()
    client.exists = AsyncMock()
    client.expire = AsyncMock()
    
    return client


# Test data fixtures
@pytest.fixture
def sample_exercise_data():
    """Sample exercise data for testing."""
    return {
        "id": "ex001",
        "title": "Basic Variable Assignment",
        "description": "Create a variable named 'name' and assign it the value 'Alice'",
        "difficulty": "beginner",
        "category": "basics",
        "template_code": "# Write your code here\n",
        "solution_code": "name = 'Alice'",
        "test_cases": [
            {
                "description": "Variable 'name' should exist",
                "test": "assert 'name' in globals()",
                "expected": True
            },
            {
                "description": "Variable 'name' should equal 'Alice'",
                "test": "assert name == 'Alice'",
                "expected": True
            }
        ],
        "hints": [
            "Use the assignment operator (=) to assign a value to a variable",
            "String values should be enclosed in quotes"
        ],
        "tags": ["variables", "strings", "assignment"]
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "user001",
        "email": "test@example.com",
        "username": "testuser",
        "password_hash": "hashed_password_123",
        "full_name": "Test User",
        "skill_level": "beginner",
        "preferred_language": "en",
        "created_at": "2024-01-01T00:00:00Z",
        "last_active": "2024-01-15T12:00:00Z",
        "is_active": True,
        "email_verified": True
    }


@pytest.fixture
def sample_progress_data():
    """Sample progress data for testing."""
    return {
        "user_id": "user001",
        "exercise_id": "ex001",
        "completed": True,
        "score": 85,
        "attempts": 3,
        "time_spent": 120,  # seconds
        "completed_at": "2024-01-15T14:30:00Z",
        "solution_code": "name = 'Alice'",
        "feedback": "Good job! Your solution is correct.",
        "hints_used": 1
    }


# Performance testing fixtures
@pytest.fixture
def performance_config():
    """Configuration for performance tests."""
    return {
        "max_response_time": 1.0,  # seconds
        "max_memory_usage": 100,   # MB
        "concurrent_users": 10,
        "test_duration": 30,       # seconds
        "ramp_up_time": 5          # seconds
    }


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    
    # Clean up any test files that might have been created
    test_files = [
        "test_output.txt",
        "test_data.json",
        "test_config.yaml"
    ]
    
    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            path.unlink()


# Parametrized fixtures for different test scenarios
@pytest.fixture(params=["beginner", "intermediate", "advanced"])
def skill_level(request):
    """Parametrized fixture for different skill levels."""
    return request.param


@pytest.fixture(params=["basics", "oop", "algorithms", "web_dev"])
def exercise_category(request):
    """Parametrized fixture for different exercise categories."""
    return request.param


# Custom assertion helpers
def assert_response_time(func, max_time=1.0):
    """Assert that a function executes within the specified time."""
    import time
    start_time = time.time()
    result = func()
    execution_time = time.time() - start_time
    
    assert execution_time <= max_time, f"Function took {execution_time:.2f}s, expected <= {max_time}s"
    return result


def assert_memory_usage(func, max_memory_mb=100):
    """Assert that a function doesn't exceed memory usage."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    result = func()
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = final_memory - initial_memory
    
    assert memory_used <= max_memory_mb, f"Function used {memory_used:.2f}MB, expected <= {max_memory_mb}MB"
    return result


# Make assertion helpers available to tests
pytest.assert_response_time = assert_response_time
pytest.assert_memory_usage = assert_memory_usage