"""
pytest examples for the Testing module.
Comprehensive examples of pytest framework features.
"""

from typing import Dict, Any


def get_pytest_examples() -> Dict[str, Any]:
    """Get comprehensive pytest examples."""
    return {
        "basic_pytest": {
            "code": '''
import pytest
import tempfile
import os
from typing import List

# Example classes for testing
class TodoList:
    """Simple todo list for demonstration."""
    
    def __init__(self):
        self.items: List[str] = []
        self.completed: List[bool] = []
    
    def add_item(self, item: str) -> None:
        """Add an item to the todo list."""
        if not item.strip():
            raise ValueError("Item cannot be empty")
        self.items.append(item.strip())
        self.completed.append(False)
    
    def complete_item(self, index: int) -> None:
        """Mark an item as completed."""
        if index < 0 or index >= len(self.items):
            raise IndexError("Invalid item index")
        self.completed[index] = True
    
    def remove_item(self, index: int) -> str:
        """Remove an item from the list."""
        if index < 0 or index >= len(self.items):
            raise IndexError("Invalid item index")
        item = self.items.pop(index)
        self.completed.pop(index)
        return item
    
    def get_pending_items(self) -> List[str]:
        """Get list of pending (not completed) items."""
        return [item for item, done in zip(self.items, self.completed) if not done]
    
    def get_completed_items(self) -> List[str]:
        """Get list of completed items."""
        return [item for item, done in zip(self.items, self.completed) if done]

# Basic pytest test functions
def test_add_item_to_empty_list():
    """Test adding an item to empty todo list."""
    todo = TodoList()
    todo.add_item("Buy groceries")
    
    assert len(todo.items) == 1
    assert todo.items[0] == "Buy groceries"
    assert todo.completed[0] is False

def test_add_multiple_items():
    """Test adding multiple items."""
    todo = TodoList()
    items = ["Task 1", "Task 2", "Task 3"]
    
    for item in items:
        todo.add_item(item)
    
    assert len(todo.items) == 3
    assert todo.items == items
    assert all(not completed for completed in todo.completed)

def test_add_empty_item_raises_error():
    """Test that adding empty item raises ValueError."""
    todo = TodoList()
    
    with pytest.raises(ValueError, match="Item cannot be empty"):
        todo.add_item("")
    
    with pytest.raises(ValueError):
        todo.add_item("   ")  # Only whitespace

def test_complete_item():
    """Test completing an item."""
    todo = TodoList()
    todo.add_item("Test task")
    todo.complete_item(0)
    
    assert todo.completed[0] is True

def test_complete_invalid_index():
    """Test completing item with invalid index."""
    todo = TodoList()
    todo.add_item("Test task")
    
    with pytest.raises(IndexError):
        todo.complete_item(1)  # Index out of range
    
    with pytest.raises(IndexError):
        todo.complete_item(-1)  # Negative index

def test_remove_item():
    """Test removing an item."""
    todo = TodoList()
    todo.add_item("Remove me")
    todo.add_item("Keep me")
    
    removed_item = todo.remove_item(0)
    
    assert removed_item == "Remove me"
    assert len(todo.items) == 1
    assert todo.items[0] == "Keep me"

def test_get_pending_items():
    """Test getting pending items."""
    todo = TodoList()
    todo.add_item("Pending task")
    todo.add_item("Complete task")
    todo.complete_item(1)
    
    pending = todo.get_pending_items()
    
    assert len(pending) == 1
    assert pending[0] == "Pending task"

def test_get_completed_items():
    """Test getting completed items."""
    todo = TodoList()
    todo.add_item("Task 1")
    todo.add_item("Task 2")
    todo.complete_item(0)
    
    completed = todo.get_completed_items()
    
    assert len(completed) == 1
    assert completed[0] == "Task 1"

# Parametrized tests
@pytest.mark.parametrize("item,expected", [
    ("Simple task", "Simple task"),
    ("  Whitespace task  ", "Whitespace task"),
    ("Task with numbers 123", "Task with numbers 123"),
    ("Special chars !@#$%", "Special chars !@#$%"),
])
def test_add_item_variations(item, expected):
    """Test adding various types of items."""
    todo = TodoList()
    todo.add_item(item)
    
    assert todo.items[0] == expected

@pytest.mark.parametrize("invalid_item", [
    "",
    "   ",
    "\\t\\n",
])
def test_add_invalid_items(invalid_item):
    """Test adding invalid items raises ValueError."""
    todo = TodoList()
    
    with pytest.raises(ValueError):
        todo.add_item(invalid_item)

if __name__ == "__main__":
    pytest.main(["-v"])
''',
            "explanation": "Basic pytest structure with simple test functions and parametrized tests"
        },
        
        "fixtures_and_advanced": {
            "code": '''
import pytest
import tempfile
import os
from typing import List

# Same TodoList class as before...
class TodoList:
    """Simple todo list for demonstration."""
    
    def __init__(self):
        self.items: List[str] = []
        self.completed: List[bool] = []
    
    def add_item(self, item: str) -> None:
        """Add an item to the todo list."""
        if not item.strip():
            raise ValueError("Item cannot be empty")
        self.items.append(item.strip())
        self.completed.append(False)
    
    def complete_item(self, index: int) -> None:
        """Mark an item as completed."""
        if index < 0 or index >= len(self.items):
            raise IndexError("Invalid item index")
        self.completed[index] = True
    
    def get_pending_items(self) -> List[str]:
        """Get list of pending (not completed) items."""
        return [item for item, done in zip(self.items, self.completed) if not done]

# Fixtures
@pytest.fixture
def empty_todo():
    """Fixture that provides an empty todo list."""
    return TodoList()

@pytest.fixture
def todo_with_items():
    """Fixture that provides a todo list with some items."""
    todo = TodoList()
    todo.add_item("Buy milk")
    todo.add_item("Walk the dog")
    todo.add_item("Write tests")
    return todo

@pytest.fixture
def todo_with_completed_items():
    """Fixture with some completed items."""
    todo = TodoList()
    todo.add_item("Completed task")
    todo.add_item("Pending task")
    todo.complete_item(0)
    return todo

# Tests using fixtures
def test_empty_todo_fixture(empty_todo):
    """Test using empty todo fixture."""
    assert len(empty_todo.items) == 0
    assert len(empty_todo.completed) == 0

def test_todo_with_items_fixture(todo_with_items):
    """Test using todo with items fixture."""
    assert len(todo_with_items.items) == 3
    assert "Buy milk" in todo_with_items.items
    assert all(not completed for completed in todo_with_items.completed)

def test_fixture_isolation(empty_todo):
    """Test that fixtures provide isolated instances."""
    empty_todo.add_item("Test isolation")
    assert len(empty_todo.items) == 1

def test_another_fixture_isolation(empty_todo):
    """Test that this test gets a fresh fixture instance."""
    assert len(empty_todo.items) == 0  # Should be empty again

# Fixture with parameters
@pytest.fixture(params=[1, 2, 3, 5])
def todo_with_n_items(request):
    """Parametrized fixture that creates todo with n items."""
    todo = TodoList()
    for i in range(request.param):
        todo.add_item(f"Item {i+1}")
    return todo, request.param

def test_multiple_items_fixture(todo_with_n_items):
    """Test using parametrized fixture."""
    todo, expected_count = todo_with_n_items
    assert len(todo.items) == expected_count

# Temporary file fixture
@pytest.fixture
def temp_file():
    """Fixture that provides a temporary file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_path = f.name
    
    yield temp_path  # This is where the test runs
    
    # Cleanup after test
    os.unlink(temp_path)

def test_temporary_file(temp_file):
    """Test using temporary file fixture."""
    with open(temp_file, 'r') as f:
        content = f.read()
    
    assert content == "test content"
    assert os.path.exists(temp_file)

# Markers for test organization
@pytest.mark.slow
def test_slow_operation():
    """Test marked as slow."""
    import time
    time.sleep(0.1)  # Simulate slow operation
    assert True

@pytest.mark.integration
def test_integration_feature():
    """Test marked as integration test."""
    assert True

@pytest.mark.unit
def test_unit_feature():
    """Test marked as unit test."""
    assert True

@pytest.mark.smoke
def test_critical_functionality():
    """Test marked as smoke test."""
    todo = TodoList()
    todo.add_item("Critical test")
    assert len(todo.items) == 1

# Skip and conditional tests
@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """Test for feature not yet implemented."""
    assert False  # This would fail if run

@pytest.mark.skipif(os.name == "nt", reason="Unix-specific test")
def test_unix_specific():
    """Test that only runs on Unix systems."""
    assert True

@pytest.mark.xfail(reason="Known bug, fix in progress")
def test_known_failing():
    """Test that is expected to fail."""
    assert False

# Custom assertions with detailed messages
def test_detailed_assertions(todo_with_items):
    """Test with detailed assertion messages."""
    todo = todo_with_items
    
    # Add more specific assertions
    assert len(todo.items) == 3, f"Expected 3 items, got {len(todo.items)}"
    assert "Buy milk" in todo.items, "Missing expected item 'Buy milk'"
    
    # Test completing an item
    todo.complete_item(0)
    completed_items = todo.get_completed_items()
    
    assert len(completed_items) == 1, f"Expected 1 completed item, got {len(completed_items)}"
    assert completed_items[0] == "Buy milk", f"Expected 'Buy milk' to be completed"

# Setup and teardown with fixtures
@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Automatic setup and teardown for all tests."""
    print("\\nSetup before test")
    yield
    print("Cleanup after test")

if __name__ == "__main__":
    # Run with specific markers
    pytest.main(["-v", "-m", "unit"])  # Run only unit tests
''',
            "explanation": "Advanced pytest features including fixtures, markers, and test organization"
        },
        
        "async_and_advanced": {
            "code": '''
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List

# Async service for testing
class AsyncEmailService:
    """Async email service for testing."""
    
    def __init__(self, smtp_host: str = "localhost"):
        self.smtp_host = smtp_host
        self.sent_emails = []
    
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email asynchronously."""
        await asyncio.sleep(0.01)  # Simulate network delay
        
        email = {
            "to": to,
            "subject": subject,
            "body": body,
            "timestamp": "2023-01-01T00:00:00Z"
        }
        
        self.sent_emails.append(email)
        return True
    
    async def send_bulk_emails(self, emails: List[Dict[str, str]]) -> int:
        """Send multiple emails."""
        sent_count = 0
        for email in emails:
            success = await self.send_email(
                email["to"], 
                email["subject"], 
                email["body"]
            )
            if success:
                sent_count += 1
        return sent_count

# Async tests
@pytest.mark.asyncio
async def test_send_email():
    """Test async email sending."""
    service = AsyncEmailService()
    
    result = await service.send_email(
        "test@example.com",
        "Test Subject",
        "Test Body"
    )
    
    assert result is True
    assert len(service.sent_emails) == 1
    
    sent_email = service.sent_emails[0]
    assert sent_email["to"] == "test@example.com"
    assert sent_email["subject"] == "Test Subject"
    assert sent_email["body"] == "Test Body"

@pytest.mark.asyncio
async def test_send_bulk_emails():
    """Test sending multiple emails."""
    service = AsyncEmailService()
    
    emails = [
        {"to": "user1@example.com", "subject": "Hello 1", "body": "Message 1"},
        {"to": "user2@example.com", "subject": "Hello 2", "body": "Message 2"},
        {"to": "user3@example.com", "subject": "Hello 3", "body": "Message 3"},
    ]
    
    sent_count = await service.send_bulk_emails(emails)
    
    assert sent_count == 3
    assert len(service.sent_emails) == 3

# Fixtures with different scopes
@pytest.fixture(scope="session")
def database_config():
    """Session-scoped fixture for database configuration."""
    return {
        "url": "sqlite:///:memory:",
        "echo": False,
        "pool_size": 5
    }

@pytest.fixture(scope="module")
def email_service():
    """Module-scoped fixture for email service."""
    service = AsyncEmailService()
    print("Creating email service for module")
    return service

@pytest.fixture(scope="function")
def sample_emails():
    """Function-scoped fixture providing sample email data."""
    return [
        {"to": "alice@example.com", "subject": "Test 1", "body": "Body 1"},
        {"to": "bob@example.com", "subject": "Test 2", "body": "Body 2"},
    ]

# Tests using scoped fixtures
def test_database_config(database_config):
    """Test using session-scoped fixture."""
    assert database_config["url"] == "sqlite:///:memory:"
    assert "pool_size" in database_config

@pytest.mark.asyncio
async def test_with_module_service(email_service, sample_emails):
    """Test using module-scoped email service."""
    # Clear any previous emails
    email_service.sent_emails.clear()
    
    sent_count = await email_service.send_bulk_emails(sample_emails)
    assert sent_count == 2

# Property-based testing style with pytest
@pytest.mark.parametrize("email_count", [1, 5, 10, 25])
@pytest.mark.asyncio
async def test_bulk_email_performance(email_count):
    """Test bulk email sending with different volumes."""
    service = AsyncEmailService()
    
    emails = [
        {
            "to": f"user{i}@example.com",
            "subject": f"Subject {i}",
            "body": f"Body {i}"
        }
        for i in range(email_count)
    ]
    
    sent_count = await service.send_bulk_emails(emails)
    
    assert sent_count == email_count
    assert len(service.sent_emails) == email_count

# Custom markers and configurations
pytestmark = pytest.mark.integration  # Mark all tests in this module

@pytest.mark.database
class TestAsyncDatabase:
    """Test class for async database operations."""
    
    @pytest.mark.asyncio
    async def test_async_query(self):
        """Test async database query."""
        # Simulate async database operation
        async def mock_query():
            await asyncio.sleep(0.01)
            return {"rows": [{"id": 1, "name": "Test"}]}
        
        result = await mock_query()
        assert "rows" in result
        assert len(result["rows"]) == 1
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_slow_async_operation(self):
        """Test slow async operation."""
        async def slow_operation():
            await asyncio.sleep(0.1)  # Simulate slow operation
            return "completed"
        
        result = await slow_operation()
        assert result == "completed"

# Advanced fixtures with cleanup
@pytest.fixture
async def async_resource():
    """Async fixture with setup and cleanup."""
    # Setup
    resource = {"connection": "established", "data": []}
    print("Setting up async resource")
    
    yield resource  # Provide resource to test
    
    # Cleanup
    print("Cleaning up async resource")
    resource.clear()

@pytest.mark.asyncio
async def test_with_async_fixture(async_resource):
    """Test using async fixture."""
    assert async_resource["connection"] == "established"
    async_resource["data"].append("test_data")
    assert len(async_resource["data"]) == 1

# Error handling in async tests
@pytest.mark.asyncio
async def test_async_error_handling():
    """Test error handling in async operations."""
    async def failing_operation():
        await asyncio.sleep(0.01)
        raise ValueError("Async operation failed")
    
    with pytest.raises(ValueError, match="Async operation failed"):
        await failing_operation()

# Timeout testing
@pytest.mark.asyncio
@pytest.mark.timeout(1)  # Requires pytest-timeout plugin
async def test_with_timeout():
    """Test that should complete within timeout."""
    await asyncio.sleep(0.1)  # Should complete quickly
    assert True

# Mocking async operations
@pytest.mark.asyncio
async def test_mocked_async_operation():
    """Test mocking async operations."""
    mock_service = AsyncMock()
    mock_service.send_email.return_value = True
    
    result = await mock_service.send_email("test@example.com", "Subject", "Body")
    
    assert result is True
    mock_service.send_email.assert_called_once_with("test@example.com", "Subject", "Body")

# Configuration and custom collection
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "database: marks tests that require database")

if __name__ == "__main__":
    # Run with different configurations
    pytest.main([
        "-v",
        "-m", "not slow",  # Skip slow tests
        "--tb=short",
        "--maxfail=3"
    ])
''',
            "explanation": "Advanced pytest features including async testing, fixtures with different scopes, and custom configurations"
        }
    }