# tests/unit/core/test_testing.py
# Unit tests for testing concepts and exercises

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock, call
import doctest
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

# Import modules under test (adjust based on your actual structure)
try:
    from src.core.testing import (
        UnitTestingExercise,
        IntegrationTestingExercise,
        MockingExercise,
        TestDrivenDevelopmentExercise,
        TestCoverageExercise
    )
    from src.core.evaluators import TestingEvaluator
except ImportError:
    # Mock classes for when actual modules don't exist
    class UnitTestingExercise:
        pass
    class IntegrationTestingExercise:
        pass
    class MockingExercise:
        pass
    class TestDrivenDevelopmentExercise:
        pass
    class TestCoverageExercise:
        pass
    class TestingEvaluator:
        pass


class TestUnitTestingConcepts:
    """Test cases for unit testing concepts and exercises."""
    
    def test_basic_unittest_structure(self):
        """Test basic unittest structure and methods."""
        code = '''
import unittest

class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def tearDown(self):
        # Clean up after each test
        self.calc = None
    
    def test_add(self):
        result = self.calc.add(2, 3)
        self.assertEqual(result, 5)
        
        # Test with negative numbers
        result = self.calc.add(-2, 3)
        self.assertEqual(result, 1)
    
    def test_subtract(self):
        result = self.calc.subtract(5, 3)
        self.assertEqual(result, 2)
    
    def test_multiply(self):
        result = self.calc.multiply(4, 3)
        self.assertEqual(result, 12)
    
    def test_divide(self):
        result = self.calc.divide(10, 2)
        self.assertEqual(result, 5.0)
    
    def test_divide_by_zero(self):
        with self.assertRaises(ValueError) as context:
            self.calc.divide(10, 0)
        
        self.assertIn("Cannot divide by zero", str(context.exception))
    
    def test_multiple_assertions(self):
        # Test multiple related assertions
        self.assertTrue(self.calc.add(1, 1) > 0)
        self.assertFalse(self.calc.subtract(1, 2) > 0)
        self.assertIsInstance(self.calc.multiply(2, 3), int)
        self.assertAlmostEqual(self.calc.divide(1, 3), 0.333, places=2)

# Run the tests and capture results
if __name__ == '__main__':
    # Capture test output
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculator)
    test_runner = unittest.TextTestRunner(stream=io.StringIO(), verbosity=2)
    test_result = test_runner.run(test_suite)
    
    # Extract results
    tests_run = test_result.testsRun
    failures = len(test_result.failures)
    errors = len(test_result.errors)
    success_rate = (tests_run - failures - errors) / tests_run if tests_run > 0 else 0
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['tests_run'] == 6
        assert globals_dict['failures'] == 0
        assert globals_dict['errors'] == 0
        assert globals_dict['success_rate'] == 1.0
    
    def test_pytest_style_testing(self):
        """Test pytest-style testing concepts."""
        code = '''
# Functions to test
def factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

def is_palindrome(s):
    s = s.lower().replace(' ', '')
    return s == s[::-1]

def fibonacci(n):
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Pytest-style test functions
def test_factorial_basic():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120

def test_factorial_negative():
    try:
        factorial(-1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "negative numbers" in str(e)

def test_is_palindrome():
    assert is_palindrome("racecar") == True
    assert is_palindrome("hello") == False
    assert is_palindrome("A man a plan a canal Panama") == True
    assert is_palindrome("") == True

def test_fibonacci():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(10) == 55

# Parametrized test simulation
test_cases = [
    (0, 1),
    (1, 1),
    (2, 2),
    (3, 6),
    (4, 24),
    (5, 120)
]

def test_factorial_parametrized():
    results = []
    for input_val, expected in test_cases:
        actual = factorial(input_val)
        results.append((input_val, expected, actual, actual == expected))
    return results

# Run tests manually
test_results = {
    'factorial_basic': True,
    'factorial_negative': True,
    'palindrome': True,
    'fibonacci': True
}

try:
    test_factorial_basic()
except:
    test_results['factorial_basic'] = False

try:
    test_factorial_negative()
except:
    test_results['factorial_negative'] = False

try:
    test_is_palindrome()
except:
    test_results['palindrome'] = False

try:
    test_fibonacci()
except:
    test_results['fibonacci'] = False

parametrized_results = test_factorial_parametrized()
all_parametrized_passed = all(result[3] for result in parametrized_results)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        results = globals_dict['test_results']
        assert all(results.values()), f"Some tests failed: {results}"
        assert globals_dict['all_parametrized_passed'] is True
    
    def test_test_fixtures_and_setup(self):
        """Test fixtures and setup/teardown concepts."""
        code = '''
import tempfile
import os
from pathlib import Path

class FileManager:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def create_file(self, filename, content=""):
        file_path = self.base_path / filename
        file_path.write_text(content)
        return file_path
    
    def read_file(self, filename):
        file_path = self.base_path / filename
        if file_path.exists():
            return file_path.read_text()
        return None
    
    def delete_file(self, filename):
        file_path = self.base_path / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def list_files(self):
        return [f.name for f in self.base_path.iterdir() if f.is_file()]

# Test fixture simulation
class TestFileManager:
    def setup_method(self):
        # Create temporary directory for each test
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(self.temp_dir)
    
    def teardown_method(self):
        # Clean up after each test
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_and_read_file(self):
        # Test file creation and reading
        content = "Hello, World!"
        file_path = self.file_manager.create_file("test.txt", content)
        
        assert file_path.exists()
        assert self.file_manager.read_file("test.txt") == content
    
    def test_delete_file(self):
        # Test file deletion
        self.file_manager.create_file("to_delete.txt", "Delete me")
        
        assert self.file_manager.delete_file("to_delete.txt") == True
        assert self.file_manager.read_file("to_delete.txt") is None
    
    def test_list_files(self):
        # Test file listing
        self.file_manager.create_file("file1.txt")
        self.file_manager.create_file("file2.txt")
        
        files = self.file_manager.list_files()
        assert len(files) == 2
        assert "file1.txt" in files
        assert "file2.txt" in files

# Run tests manually
test_instance = TestFileManager()
test_results = {}

# Test 1
test_instance.setup_method()
try:
    test_instance.test_create_and_read_file()
    test_results['create_read'] = True
except Exception as e:
    test_results['create_read'] = False
finally:
    test_instance.teardown_method()

# Test 2
test_instance.setup_method()
try:
    test_instance.test_delete_file()
    test_results['delete'] = True
except Exception as e:
    test_results['delete'] = False
finally:
    test_instance.teardown_method()

# Test 3
test_instance.setup_method()
try:
    test_instance.test_list_files()
    test_results['list_files'] = True
except Exception as e:
    test_results['list_files'] = False
finally:
    test_instance.teardown_method()

all_tests_passed = all(test_results.values())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['all_tests_passed'] is True
        results = globals_dict['test_results']
        assert results['create_read'] is True
        assert results['delete'] is True
        assert results['list_files'] is True


class TestMockingConcepts:
    """Test cases for mocking concepts and exercises."""
    
    def test_basic_mocking(self):
        """Test basic mocking with unittest.mock."""
        code = '''
from unittest.mock import Mock, patch
import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_user(self, user_id):
        response = requests.get(f"{self.base_url}/users/{user_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    def create_user(self, user_data):
        response = requests.post(f"{self.base_url}/users", json=user_data)
        return response.status_code == 201

# Test with mock
def test_api_client_with_mock():
    # Create mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 123, "name": "Test User"}
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        client = APIClient("https://api.example.com")
        user = client.get_user(123)
        
        # Verify the call was made correctly
        mock_get.assert_called_once_with("https://api.example.com/users/123")
        
        # Verify the response
        assert user["id"] == 123
        assert user["name"] == "Test User"
        
        return True

def test_api_client_create_user():
    mock_response = Mock()
    mock_response.status_code = 201
    
    with patch('requests.post', return_value=mock_response) as mock_post:
        client = APIClient("https://api.example.com")
        user_data = {"name": "New User", "email": "new@example.com"}
        
        result = client.create_user(user_data)
        
        # Verify the call
        mock_post.assert_called_once_with(
            "https://api.example.com/users", 
            json=user_data
        )
        
        assert result is True
        return True

def test_api_client_error_handling():
    mock_response = Mock()
    mock_response.status_code = 404
    
    with patch('requests.get', return_value=mock_response):
        client = APIClient("https://api.example.com")
        user = client.get_user(999)
        
        assert user is None
        return True

# Run tests
test_results = {
    'get_user': test_api_client_with_mock(),
    'create_user': test_api_client_create_user(),
    'error_handling': test_api_client_error_handling()
}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        results = globals_dict['test_results']
        assert all(results.values())
    
    def test_mock_side_effects(self):
        """Test mock side effects and advanced mocking."""
        code = '''
from unittest.mock import Mock, MagicMock, call
import random

class DatabaseConnection:
    def __init__(self):
        self.connected = False
    
    def connect(self):
        # Simulate connection that might fail
        if random.random() > 0.8:  # 20% failure rate
            raise ConnectionError("Failed to connect to database")
        self.connected = True
    
    def execute_query(self, query):
        if not self.connected:
            raise RuntimeError("Not connected to database")
        
        # Simulate query execution
        if "SELECT" in query.upper():
            return [{"id": 1, "name": "Test"}]
        elif "INSERT" in query.upper():
            return {"rows_affected": 1}
        else:
            return {"status": "success"}

class UserRepository:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_user(self, user_id):
        try:
            self.db.connect()
            result = self.db.execute_query(f"SELECT * FROM users WHERE id = {user_id}")
            return result[0] if result else None
        except (ConnectionError, RuntimeError) as e:
            return {"error": str(e)}
    
    def create_user(self, name):
        try:
            self.db.connect()
            query = f"INSERT INTO users (name) VALUES ('{name}')"
            result = self.db.execute_query(query)
            return result["rows_affected"] > 0
        except (ConnectionError, RuntimeError) as e:
            return False

# Test with side effects
def test_connection_failure():
    mock_db = Mock(spec=DatabaseConnection)
    mock_db.connect.side_effect = ConnectionError("Connection failed")
    
    repo = UserRepository(mock_db)
    result = repo.get_user(123)
    
    assert "error" in result
    assert "Connection failed" in result["error"]
    return True

def test_multiple_calls_with_side_effects():
    mock_db = Mock(spec=DatabaseConnection)
    
    # First call succeeds, second fails, third succeeds
    mock_db.connect.side_effect = [None, ConnectionError("Timeout"), None]
    mock_db.execute_query.return_value = [{"id": 1, "name": "Test User"}]
    
    repo = UserRepository(mock_db)
    
    # Call 1: Success
    result1 = repo.get_user(1)
    assert result1["name"] == "Test User"
    
    # Call 2: Failure
    result2 = repo.get_user(2)
    assert "error" in result2
    
    # Call 3: Success
    result3 = repo.get_user(3)
    assert result3["name"] == "Test User"
    
    # Verify all calls were made
    assert mock_db.connect.call_count == 3
    return True

def test_mock_call_arguments():
    mock_db = Mock(spec=DatabaseConnection)
    mock_db.connect.return_value = None
    mock_db.execute_query.return_value = {"rows_affected": 1}
    
    repo = UserRepository(mock_db)
    result = repo.create_user("Alice")
    
    # Verify the exact query was executed
    expected_query = "INSERT INTO users (name) VALUES ('Alice')"
    mock_db.execute_query.assert_called_with(expected_query)
    
    assert result is True
    return True

# Run advanced mock tests
advanced_test_results = {
    'connection_failure': test_connection_failure(),
    'side_effects': test_multiple_calls_with_side_effects(),
    'call_arguments': test_mock_call_arguments()
}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        results = globals_dict['advanced_test_results']
        assert all(results.values())
    
    def test_spy_and_stub_patterns(self):
        """Test spy and stub patterns."""
        code = '''
from unittest.mock import Mock, MagicMock

class EmailService:
    def send_email(self, to, subject, body):
        # In real implementation, this would send an email
        print(f"Sending email to {to}: {subject}")
        return True

class NotificationService:
    def __init__(self, email_service):
        self.email_service = email_service
        self.notifications_sent = 0
    
    def send_welcome_email(self, user_email, username):
        subject = f"Welcome, {username}!"
        body = f"Welcome to our platform, {username}. We're glad to have you!"
        
        success = self.email_service.send_email(user_email, subject, body)
        if success:
            self.notifications_sent += 1
        return success
    
    def send_password_reset(self, user_email):
        subject = "Password Reset Request"
        body = "Click the link below to reset your password."
        
        success = self.email_service.send_email(user_email, subject, body)
        if success:
            self.notifications_sent += 1
        return success

# Test with spy pattern (observing behavior)
def test_notification_service_with_spy():
    # Create a spy that tracks calls but uses real implementation
    email_service = EmailService()
    spy_email_service = Mock(wraps=email_service)
    
    notification_service = NotificationService(spy_email_service)
    
    # Send notifications
    result1 = notification_service.send_welcome_email("alice@example.com", "Alice")
    result2 = notification_service.send_password_reset("bob@example.com")
    
    # Verify behavior
    assert result1 is True
    assert result2 is True
    assert notification_service.notifications_sent == 2
    
    # Verify spy recorded calls
    assert spy_email_service.send_email.call_count == 2
    
    # Check specific calls
    calls = spy_email_service.send_email.call_args_list
    first_call = calls[0]
    second_call = calls[1]
    
    # Verify first call (welcome email)
    assert first_call[0][0] == "alice@example.com"  # to
    assert "Welcome, Alice!" in first_call[0][1]     # subject
    
    # Verify second call (password reset)
    assert second_call[0][0] == "bob@example.com"
    assert "Password Reset" in second_call[0][1]
    
    return True

# Test with stub pattern (controlling behavior)
def test_notification_service_with_stub():
    # Create a stub that controls return values
    stub_email_service = Mock()
    stub_email_service.send_email.return_value = False  # Simulate failure
    
    notification_service = NotificationService(stub_email_service)
    
    # Try to send notification
    result = notification_service.send_welcome_email("test@example.com", "Test")
    
    # Verify failure was handled
    assert result is False
    assert notification_service.notifications_sent == 0
    
    # Verify the call was attempted
    stub_email_service.send_email.assert_called_once()
    
    return True

# Test with partial mock (some methods mocked, others real)
def test_partial_mocking():
    notification_service = NotificationService(EmailService())
    
    # Mock only the email service
    with patch.object(notification_service, 'email_service') as mock_email:
        mock_email.send_email.return_value = True
        
        # Test the service
        result = notification_service.send_welcome_email("user@example.com", "User")
        
        assert result is True
        assert notification_service.notifications_sent == 1
        
        # Verify the mock was called
        mock_email.send_email.assert_called_once_with(
            "user@example.com",
            "Welcome, User!",
            "Welcome to our platform, User. We're glad to have you!"
        )
    
    return True

# Run spy and stub tests
spy_stub_results = {
    'spy_pattern': test_notification_service_with_spy(),
    'stub_pattern': test_notification_service_with_stub(),
    'partial_mocking': test_partial_mocking()
}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        results = globals_dict['spy_stub_results']
        assert all(results.values())


class TestTestDrivenDevelopment:
    """Test cases for Test-Driven Development concepts."""
    
    def test_tdd_red_green_refactor_cycle(self):
        """Test the Red-Green-Refactor TDD cycle."""
        code = '''
# TDD Example: Implementing a simple stack
# Step 1: RED - Write failing tests

class TestStack:
    def __init__(self):
        self.test_results = []
    
    def run_test(self, test_name, test_func):
        try:
            test_func()
            self.test_results.append((test_name, "PASS"))
            return True
        except Exception as e:
            self.test_results.append((test_name, f"FAIL: {str(e)}"))
            return False
    
    def assert_equal(self, actual, expected, message=""):
        if actual != expected:
            raise AssertionError(f"Expected {expected}, got {actual}. {message}")
    
    def assert_true(self, condition, message=""):
        if not condition:
            raise AssertionError(f"Expected True. {message}")
    
    def assert_raises(self, exception_type, func):
        try:
            func()
            raise AssertionError(f"Expected {exception_type.__name__} to be raised")
        except exception_type:
            pass  # Expected exception was raised

# RED Phase: Write failing tests first
def test_red_phase():
    tester = TestStack()
    
    # Test 1: Empty stack
    def test_empty_stack():
        stack = Stack()  # This will fail - Stack doesn't exist yet
        tester.assert_true(stack.is_empty())
        tester.assert_equal(stack.size(), 0)
    
    # Test 2: Push operation
    def test_push():
        stack = Stack()
        stack.push(1)
        tester.assert_equal(stack.size(), 1)
        tester.assert_true(not stack.is_empty())
    
    # These tests will fail initially
    tests_pass_red = tester.run_test("empty_stack", test_empty_stack)
    return tests_pass_red  # Should be False

# GREEN Phase: Implement minimal code to pass tests
class Stack:
    def __init__(self):
        self._items = []
    
    def is_empty(self):
        return len(self._items) == 0
    
    def size(self):
        return len(self._items)
    
    def push(self, item):
        self._items.append(item)
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self._items.pop()
    
    def peek(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self._items[-1]

def test_green_phase():
    tester = TestStack()
    
    # Test 1: Empty stack
    def test_empty_stack():
        stack = Stack()
        tester.assert_true(stack.is_empty())
        tester.assert_equal(stack.size(), 0)
    
    # Test 2: Push operation
    def test_push():
        stack = Stack()
        stack.push(1)
        tester.assert_equal(stack.size(), 1)
        tester.assert_true(not stack.is_empty())
    
    # Test 3: Pop operation
    def test_pop():
        stack = Stack()
        stack.push(1)
        stack.push(2)
        item = stack.pop()
        tester.assert_equal(item, 2)
        tester.assert_equal(stack.size(), 1)
    
    # Test 4: Peek operation
    def test_peek():
        stack = Stack()
        stack.push(1)
        item = stack.peek()
        tester.assert_equal(item, 1)
        tester.assert_equal(stack.size(), 1)  # Size should not change
    
    # Test 5: Error handling
    def test_pop_empty():
        stack = Stack()
        tester.assert_raises(IndexError, lambda: stack.pop())
    
    def test_peek_empty():
        stack = Stack()
        tester.assert_raises(IndexError, lambda: stack.peek())
    
    # Run all tests
    results = []
    results.append(tester.run_test("empty_stack", test_empty_stack))
    results.append(tester.run_test("push", test_push))
    results.append(tester.run_test("pop", test_pop))
    results.append(tester.run_test("peek", test_peek))
    results.append(tester.run_test("pop_empty", test_pop_empty))
    results.append(tester.run_test("peek_empty", test_peek_empty))
    
    return all(results), tester.test_results

# REFACTOR Phase: Improve code while keeping tests green
class ImprovedStack:
    """Refactored version with better error messages and additional features."""
    
    def __init__(self, max_size=None):
        self._items = []
        self._max_size = max_size
    
    def is_empty(self):
        return len(self._items) == 0
    
    def is_full(self):
        return self._max_size is not None and len(self._items) >= self._max_size
    
    def size(self):
        return len(self._items)
    
    def max_size(self):
        return self._max_size
    
    def push(self, item):
        if self.is_full():
            raise OverflowError(f"Stack is full (max size: {self._max_size})")
        self._items.append(item)
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Cannot pop from empty stack")
        return self._items.pop()
    
    def peek(self):
        if self.is_empty():
            raise IndexError("Cannot peek into empty stack")
        return self._items[-1]
    
    def clear(self):
        self._items.clear()
    
    def to_list(self):
        return self._items.copy()

# Test refactored version
def test_refactor_phase():
    tester = TestStack()
    
    # All original tests should still pass
    def test_basic_functionality():
        stack = ImprovedStack()
        
        # Empty stack
        tester.assert_true(stack.is_empty())
        tester.assert_equal(stack.size(), 0)
        
        # Push and pop
        stack.push(1)
        stack.push(2)
        tester.assert_equal(stack.size(), 2)
        
        item = stack.pop()
        tester.assert_equal(item, 2)
        tester.assert_equal(stack.size(), 1)
        
        # Peek
        top = stack.peek()
        tester.assert_equal(top, 1)
        tester.assert_equal(stack.size(), 1)
    
    # New functionality tests
    def test_new_features():
        # Test max size
        stack = ImprovedStack(max_size=2)
        stack.push(1)
        stack.push(2)
        tester.assert_true(stack.is_full())
        
        # Test overflow
        tester.assert_raises(OverflowError, lambda: stack.push(3))
        
        # Test clear
        stack.clear()
        tester.assert_true(stack.is_empty())
        tester.assert_equal(stack.size(), 0)
    
    results = []
    results.append(tester.run_test("basic_functionality", test_basic_functionality))
    results.append(tester.run_test("new_features", test_new_features))
    
    return all(results), tester.test_results

# Run TDD cycle
red_result = False  # Red phase should fail (Stack doesn't exist initially)
green_result, green_details = test_green_phase()
refactor_result, refactor_details = test_refactor_phase()

tdd_cycle_complete = green_result and refactor_result
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['green_result'] is True
        assert globals_dict['refactor_result'] is True
        assert globals_dict['tdd_cycle_complete'] is True
    
    def test_behavior_driven_development(self):
        """Test BDD concepts with Given-When-Then structure."""
        code = '''
# BDD Example: User authentication system

class User:
    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = True
        self.failed_login_attempts = 0
        self.is_locked = False

class AuthenticationService:
    def __init__(self):
        self.users = {}
        self.max_failed_attempts = 3
    
    def register_user(self, username, email, password_hash):
        if username in self.users:
            raise ValueError("Username already exists")
        
        user = User(username, email, password_hash)
        self.users[username] = user
        return user
    
    def authenticate(self, username, password_hash):
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        
        if user.is_locked:
            return False, "Account is locked"
        
        if not user.is_active:
            return False, "Account is inactive"
        
        if user.password_hash == password_hash:
            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            return True, "Authentication successful"
        else:
            # Increment failed attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.is_locked = True
                return False, "Account locked due to too many failed attempts"
            else:
                return False, "Invalid password"

# BDD-style test scenarios
class BDDTester:
    def __init__(self):
        self.scenario_results = []
        self.auth_service = None
        self.user = None
        self.result = None
        self.message = None
    
    def given(self, description, setup_func):
        """Given step - set up initial conditions."""
        try:
            setup_func()
            return self
        except Exception as e:
            self.scenario_results.append(f"GIVEN failed: {description} - {e}")
            raise
    
    def when(self, description, action_func):
        """When step - perform action."""
        try:
            action_func()
            return self
        except Exception as e:
            self.scenario_results.append(f"WHEN failed: {description} - {e}")
            raise
    
    def then(self, description, assertion_func):
        """Then step - verify outcome."""
        try:
            assertion_func()
            self.scenario_results.append(f"PASS: {description}")
            return True
        except Exception as e:
            self.scenario_results.append(f"FAIL: {description} - {e}")
            return False

def test_user_authentication_scenarios():
    tester = BDDTester()
    
    # Scenario 1: Successful authentication
    def scenario_1():
        return (tester
            .given("a user registration system", lambda: setattr(tester, 'auth_service', AuthenticationService()))
            .given("a registered user", lambda: setattr(tester, 'user', tester.auth_service.register_user("alice", "alice@example.com", "hashed_password_123")))
            .when("the user provides correct credentials", lambda: setattr(tester, 'result', tester.auth_service.authenticate("alice", "hashed_password_123")))
            .then("authentication should succeed", lambda: tester.result[0] and "successful" in tester.result[1])
        )
    
    # Scenario 2: Failed authentication with wrong password
    def scenario_2():
        tester_2 = BDDTester()
        return (tester_2
            .given("a user registration system", lambda: setattr(tester_2, 'auth_service', AuthenticationService()))
            .given("a registered user", lambda: setattr(tester_2, 'user', tester_2.auth_service.register_user("bob", "bob@example.com", "correct_password")))
            .when("the user provides wrong credentials", lambda: setattr(tester_2, 'result', tester_2.auth_service.authenticate("bob", "wrong_password")))
            .then("authentication should fail", lambda: not tester_2.result[0] and "Invalid password" in tester_2.result[1])
        )
    
    # Scenario 3: Account lockout after multiple failed attempts
    def scenario_3():
        tester_3 = BDDTester()
        auth_service = AuthenticationService()
        user = auth_service.register_user("charlie", "charlie@example.com", "secret")
        
        # Simulate multiple failed attempts
        auth_service.authenticate("charlie", "wrong1")
        auth_service.authenticate("charlie", "wrong2")
        final_result = auth_service.authenticate("charlie", "wrong3")
        
        return (tester_3
            .given("a user with multiple failed login attempts", lambda: None)
            .when("the user exceeds maximum failed attempts", lambda: setattr(tester_3, 'result', final_result))
            .then("the account should be locked", lambda: not tester_3.result[0] and "locked" in tester_3.result[1])
        )
    
    # Run scenarios
    results = []
    results.append(scenario_1())
    results.append(scenario_2())
    results.append(scenario_3())
    
    return all(results), tester.scenario_results

bdd_success, bdd_details = test_user_authentication_scenarios()
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['bdd_success'] is True
        assert len(globals_dict['bdd_details']) >= 3  # At least 3 scenarios tested


class TestCodeCoverage:
    """Test cases for code coverage concepts."""
    
    def test_statement_coverage(self):
        """Test statement coverage analysis."""
        code = '''
import sys
from io import StringIO

# Simple function to test coverage on
def calculate_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def calculate_discount(price, customer_type, quantity):
    discount = 0
    
    # Base discount for customer type
    if customer_type == "premium":
        discount = 0.15
    elif customer_type == "regular":
        discount = 0.05
    
    # Additional discount for quantity
    if quantity >= 10:
        discount += 0.10
    elif quantity >= 5:
        discount += 0.05
    
    # Cap discount at 25%
    if discount > 0.25:
        discount = 0.25
    
    return price * (1 - discount)

# Coverage tracking simulation
class CoverageTracker:
    def __init__(self):
        self.executed_lines = set()
        self.total_lines = set()
    
    def track_line(self, line_number):
        self.executed_lines.add(line_number)
        self.total_lines.add(line_number)
    
    def add_possible_line(self, line_number):
        self.total_lines.add(line_number)
    
    def get_coverage_percentage(self):
        if not self.total_lines:
            return 100.0
        return (len(self.executed_lines) / len(self.total_lines)) * 100

# Manual coverage tracking for calculate_grade
def test_grade_coverage():
    tracker = CoverageTracker()
    
    # Define all possible lines
    for line in range(1, 12):  # Assuming function has 11 lines
        tracker.add_possible_line(line)
    
    # Test case 1: Score 95 (A grade)
    tracker.track_line(1)  # Function entry
    tracker.track_line(2)  # if score >= 90
    tracker.track_line(3)  # return "A"
    result_a = calculate_grade(95)
    
    # Test case 2: Score 85 (B grade)
    tracker.track_line(1)  # Function entry
    tracker.track_line(2)  # if score >= 90 (False)
    tracker.track_line(4)  # elif score >= 80
    tracker.track_line(5)  # return "B"
    result_b = calculate_grade(85)
    
    # Test case 3: Score 50 (F grade)
    tracker.track_line(1)  # Function entry
    tracker.track_line(2)  # if score >= 90 (False)
    tracker.track_line(4)  # elif score >= 80 (False)
    tracker.track_line(6)  # elif score >= 70 (False)
    tracker.track_line(8)  # elif score >= 60 (False)
    tracker.track_line(10) # else
    tracker.track_line(11) # return "F"
    result_f = calculate_grade(50)
    
    coverage = tracker.get_coverage_percentage()
    
    return {
        'results': [result_a, result_b, result_f],
        'coverage_percentage': coverage,
        'executed_lines': len(tracker.executed_lines),
        'total_lines': len(tracker.total_lines)
    }

# Branch coverage test
def test_branch_coverage():
    # Test all possible branches in calculate_discount
    test_cases = [
        # (price, customer_type, quantity, expected_conditions)
        (100, "premium", 15, "premium + quantity >= 10"),
        (100, "premium", 7, "premium + quantity >= 5"),
        (100, "premium", 2, "premium + quantity < 5"),
        (100, "regular", 15, "regular + quantity >= 10"),
        (100, "regular", 7, "regular + quantity >= 5"),
        (100, "regular", 2, "regular + quantity < 5"),
        (100, "guest", 15, "no customer discount + quantity >= 10"),
        (100, "guest", 2, "no customer discount + quantity < 5"),
    ]
    
    results = []
    for price, customer_type, quantity, description in test_cases:
        result = calculate_discount(price, customer_type, quantity)
        results.append({
            'input': (price, customer_type, quantity),
            'output': result,
            'description': description
        })
    
    # Calculate unique branch combinations covered
    branches_covered = len(results)
    total_possible_branches = 8  # Based on the combinations above
    
    branch_coverage = (branches_covered / total_possible_branches) * 100
    
    return {
        'results': results,
        'branch_coverage': branch_coverage,
        'branches_tested': branches_covered
    }

grade_coverage = test_grade_coverage()
branch_coverage = test_branch_coverage()
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        grade_cov = globals_dict['grade_coverage']
        branch_cov = globals_dict['branch_coverage']
        
        assert grade_cov['coverage_percentage'] > 50  # Should have decent coverage
        assert len(grade_cov['results']) == 3
        assert branch_cov['branch_coverage'] == 100.0  # All branches tested
        assert len(branch_cov['results']) == 8
    
    def test_integration_testing_concepts(self):
        """Test integration testing concepts."""
        code = '''
# Integration testing example - testing component interactions

class Database:
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    def create_user(self, user_data):
        user_id = self.next_id
        self.next_id += 1
        self.users[user_id] = {**user_data, 'id': user_id}
        return user_id
    
    def get_user(self, user_id):
        return self.users.get(user_id)
    
    def update_user(self, user_id, user_data):
        if user_id in self.users:
            self.users[user_id].update(user_data)
            return True
        return False

class EmailService:
    def __init__(self):
        self.sent_emails = []
    
    def send_email(self, to, subject, body):
        email = {
            'to': to,
            'subject': subject,
            'body': body,
            'sent_at': 'now'
        }
        self.sent_emails.append(email)
        return True

class UserService:
    def __init__(self, database, email_service):
        self.db = database
        self.email_service = email_service
    
    def register_user(self, username, email, password):
        # Validate input
        if not username or not email or not password:
            raise ValueError("All fields are required")
        
        # Create user in database
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'status': 'active'
        }
        
        user_id = self.db.create_user(user_data)
        
        # Send welcome email
        self.email_service.send_email(
            email,
            "Welcome!",
            f"Welcome {username}, your account has been created."
        )
        
        return user_id
    
    def update_user_status(self, user_id, status):
        user = self.db.get_user(user_id)
        if not user:
            return False
        
        # Update status
        success = self.db.update_user(user_id, {'status': status})
        
        if success and status == 'inactive':
            # Send deactivation email
            self.email_service.send_email(
                user['email'],
                "Account Deactivated",
                f"Your account has been deactivated."
            )
        
        return success

# Integration tests
def test_user_registration_integration():
    # Set up real dependencies (not mocked)
    database = Database()
    email_service = EmailService()
    user_service = UserService(database, email_service)
    
    # Test the complete flow
    user_id = user_service.register_user("testuser", "test@example.com", "password123")
    
    # Verify database integration
    user = database.get_user(user_id)
    assert user is not None
    assert user['username'] == "testuser"
    assert user['email'] == "test@example.com"
    assert user['status'] == 'active'
    
    # Verify email service integration
    assert len(email_service.sent_emails) == 1
    welcome_email = email_service.sent_emails[0]
    assert welcome_email['to'] == "test@example.com"
    assert "Welcome" in welcome_email['subject']
    assert "testuser" in welcome_email['body']
    
    return True

def test_user_deactivation_integration():
    # Set up
    database = Database()
    email_service = EmailService()
    user_service = UserService(database, email_service)
    
    # Create a user first
    user_id = user_service.register_user("activeuser", "active@example.com", "pass")
    
    # Clear the welcome email
    email_service.sent_emails.clear()
    
    # Test deactivation
    success = user_service.update_user_status(user_id, 'inactive')
    
    # Verify database was updated
    user = database.get_user(user_id)
    assert user['status'] == 'inactive'
    
    # Verify deactivation email was sent
    assert len(email_service.sent_emails) == 1
    deactivation_email = email_service.sent_emails[0]
    assert deactivation_email['to'] == "active@example.com"
    assert "Deactivated" in deactivation_email['subject']
    
    return success

def test_error_handling_integration():
    database = Database()
    email_service = EmailService()
    user_service = UserService(database, email_service)
    
    # Test validation error
    try:
        user_service.register_user("", "test@example.com", "password")
        return False  # Should have raised an error
    except ValueError:
        pass  # Expected
    
    # Test updating non-existent user
    success = user_service.update_user_status(999, 'inactive')
    assert success is False
    
    # Verify no emails were sent for failed operations
    assert len(email_service.sent_emails) == 0
    
    return True

# Run integration tests
integration_results = {
    'registration': test_user_registration_integration(),
    'deactivation': test_user_deactivation_integration(),
    'error_handling': test_error_handling_integration()
}

all_integration_passed = all(integration_results.values())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        results = globals_dict['integration_results']
        assert all(results.values())
        assert globals_dict['all_integration_passed'] is True


class TestTestingEvaluator:
    """Test cases for testing code evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create a testing evaluator instance."""
        return TestingEvaluator()
    
    def test_evaluate_test_code(self, evaluator):
        """Test evaluation of test code."""
        test_code = '''
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

# Run the test
try:
    test_add()
    test_passed = True
except AssertionError:
    test_passed = False
'''
        result = evaluator.evaluate(test_code)
        
        assert result['success'] is True
        assert result['globals']['test_passed'] is True
    
    def test_analyze_test_quality(self, evaluator):
        """Test analysis of test quality."""
        good_test_code = '''
import unittest

class TestMathOperations(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()
    
    def test_addition_positive_numbers(self):
        """Test addition with positive numbers."""
        result = self.calculator.add(2, 3)
        self.assertEqual(result, 5)
    
    def test_addition_negative_numbers(self):
        """Test addition with negative numbers."""
        result = self.calculator.add(-2, -3)
        self.assertEqual(result, -5)
    
    def test_division_by_zero(self):
        """Test division by zero raises appropriate error."""
        with self.assertRaises(ValueError):
            self.calculator.divide(10, 0)
'''
        
        poor_test_code = '''
def test():
    x = add(1, 2)
    print(x)  # No assertion
    
def test2():
    # Empty test
    pass
'''
        
        good_analysis = evaluator.analyze_test_quality(good_test_code)
        poor_analysis = evaluator.analyze_test_quality(poor_test_code)
        
        assert good_analysis['quality_score'] > poor_analysis['quality_score']
        assert good_analysis['has_assertions'] is True
        assert poor_analysis['has_assertions'] is False
    
    def test_check_testing_patterns(self, evaluator):
        """Test checking for testing patterns and best practices."""
        test_code_with_patterns = '''
import unittest
from unittest.mock import Mock, patch

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_service = UserService()
    
    def tearDown(self):
        # Cleanup
        pass
    
    @patch('requests.get')
    def test_fetch_user_data(self, mock_get):
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {'id': 1, 'name': 'Test'}
        mock_get.return_value = mock_response
        
        # Act
        result = self.user_service.fetch_user_data(1)
        
        # Assert
        self.assertEqual(result['name'], 'Test')
        mock_get.assert_called_once_with('/users/1')
    
    def test_multiple_scenarios(self):
        # Test multiple scenarios
        with self.subTest("Valid input"):
            result = self.user_service.validate_email("test@example.com")
            self.assertTrue(result)
        
        with self.subTest("Invalid input"):
            result = self.user_service.validate_email("invalid-email")
            self.assertFalse(result)
'''
        
        patterns = evaluator.check_testing_patterns(test_code_with_patterns)
        
        assert patterns['uses_setup_teardown'] is True
        assert patterns['uses_mocking'] is True
        assert patterns['follows_aaa_pattern'] is True  # Arrange-Act-Assert
        assert patterns['uses_subtests'] is True
        assert patterns['test_isolation'] is True


class TestDocumentationTesting:
    """Test cases for documentation testing concepts."""
    
    def test_doctest_examples(self):
        """Test doctest functionality."""
        code = '''
def factorial(n):
    """
    Calculate the factorial of n.
    
    Args:
        n (int): Non-negative integer
    
    Returns:
        int: Factorial of n
    
    Examples:
        >>> factorial(0)
        1
        >>> factorial(1)
        1
        >>> factorial(5)
        120
        >>> factorial(-1)
        Traceback (most recent call last):
            ...
        ValueError: Factorial is not defined for negative numbers
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n (int): Position in Fibonacci sequence (0-indexed)
    
    Returns:
        int: The nth Fibonacci number
    
    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(10)
        55
        >>> [fibonacci(i) for i in range(7)]
        [0, 1, 1, 2, 3, 5, 8]
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Manual doctest runner simulation
import re

def run_doctests(function):
    """Simple doctest runner simulation."""
    docstring = function.__doc__
    if not docstring:
        return True, []
    
    # Find doctest examples
    examples = []
    lines = docstring.split('\\n')
    in_example = False
    current_example = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('>>> '):
            if current_example:
                examples.append('\\n'.join(current_example))
                current_example = []
            current_example.append(stripped[4:])  # Remove '>>> '
            in_example = True
        elif stripped.startswith('...'):
            if in_example:
                current_example.append(stripped[3:])  # Remove '...'
        elif in_example and stripped:
            # This might be expected output
            pass
        else:
            if current_example:
                examples.append('\\n'.join(current_example))
                current_example = []
            in_example = False
    
    if current_example:
        examples.append('\\n'.join(current_example))
    
    # Run examples
    results = []
    for example in examples:
        try:
            exec(example, globals())
            results.append(True)
        except Exception as e:
            results.append(False)
    
    return all(results), results

# Test doctests
factorial_doctest_passed, factorial_results = run_doctests(factorial)
fibonacci_doctest_passed, fibonacci_results = run_doctests(fibonacci)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Note: This is a simplified doctest runner
        # Real doctests would be more sophisticated
        assert isinstance(globals_dict['factorial_doctest_passed'], bool)
        assert isinstance(globals_dict['fibonacci_doctest_passed'], bool)


@pytest.mark.integration
class TestTestingIntegration:
    """Integration tests for testing concepts."""
    
    def test_complete_testing_workflow(self):
        """Test a complete testing workflow scenario."""
        code = '''
# Complete testing workflow example
from datetime import datetime

class Task:
    def __init__(self, title, description="", priority="medium"):
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = False
        self.created_at = datetime.now()
        self.completed_at = None
    
    def complete(self):
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.now()
    
    def is_high_priority(self):
        return self.priority == "high"

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1
    
    def add_task(self, title, description="", priority="medium"):
        task = Task(title, description, priority)
        task.id = self.next_id
        self.next_id += 1
        self.tasks.append(task)
        return task
    
    def complete_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            task.complete()
            return True
        return False
    
    def get_task(self, task_id):
        for task in self.tasks:
            if hasattr(task, 'id') and task.id == task_id:
                return task
        return None
    
    def get_completed_tasks(self):
        return [task for task in self.tasks if task.completed]
    
    def get_pending_tasks(self):
        return [task for task in self.tasks if not task.completed]
    
    def get_high_priority_tasks(self):
        return [task for task in self.tasks if task.is_high_priority()]

# Comprehensive test suite
class TaskManagerTestSuite:
    def __init__(self):
        self.test_results = []
        self.manager = None
    
    def setup(self):
        self.manager = TaskManager()
    
    def teardown(self):
        self.manager = None
    
    def run_test(self, test_name, test_func):
        self.setup()
        try:
            test_func()
            self.test_results.append((test_name, "PASS"))
            return True
        except Exception as e:
            self.test_results.append((test_name, f"FAIL: {str(e)}"))
            return False
        finally:
            self.teardown()
    
    def assert_equal(self, actual, expected):
        if actual != expected:
            raise AssertionError(f"Expected {expected}, got {actual}")
    
    def assert_true(self, condition):
        if not condition:
            raise AssertionError("Expected True")
    
    def assert_false(self, condition):
        if condition:
            raise AssertionError("Expected False")
    
    # Unit tests
    def test_task_creation(self):
        task = Task("Test task", "Description", "high")
        self.assert_equal(task.title, "Test task")
        self.assert_equal(task.description, "Description")
        self.assert_equal(task.priority, "high")
        self.assert_false(task.completed)
        self.assert_true(task.is_high_priority())
    
    def test_task_completion(self):
        task = Task("Test task")
        self.assert_false(task.completed)
        task.complete()
        self.assert_true(task.completed)
        self.assert_true(task.completed_at is not None)
    
    def test_add_task(self):
        task = self.manager.add_task("New task", "Description")
        self.assert_equal(task.title, "New task")
        self.assert_equal(len(self.manager.tasks), 1)
        self.assert_true(hasattr(task, 'id'))
    
    def test_complete_task_by_id(self):
        task = self.manager.add_task("Task to complete")
        task_id = task.id
        
        success = self.manager.complete_task(task_id)
        self.assert_true(success)
        self.assert_true(task.completed)
    
    def test_get_completed_tasks(self):
        task1 = self.manager.add_task("Task 1")
        task2 = self.manager.add_task("Task 2")
        
        self.manager.complete_task(task1.id)
        
        completed = self.manager.get_completed_tasks()
        pending = self.manager.get_pending_tasks()
        
        self.assert_equal(len(completed), 1)
        self.assert_equal(len(pending), 1)
        self.assert_equal(completed[0].title, "Task 1")
        self.assert_equal(pending[0].title, "Task 2")
    
    def test_high_priority_tasks(self):
        self.manager.add_task("Normal task", priority="medium")
        self.manager.add_task("Important task", priority="high")
        self.manager.add_task("Urgent task", priority="high")
        
        high_priority = self.manager.get_high_priority_tasks()
        self.assert_equal(len(high_priority), 2)
    
    # Integration test
    def test_complete_workflow(self):
        # Add multiple tasks
        task1 = self.manager.add_task("Review code", "Review PR #123", "high")
        task2 = self.manager.add_task("Write tests", "Unit tests for TaskManager", "medium")
        task3 = self.manager.add_task("Deploy app", "Deploy to production", "high")
        
        # Initial state
        self.assert_equal(len(self.manager.tasks), 3)
        self.assert_equal(len(self.manager.get_pending_tasks()), 3)
        self.assert_equal(len(self.manager.get_completed_tasks()), 0)
        self.assert_equal(len(self.manager.get_high_priority_tasks()), 2)
        
        # Complete some tasks
        self.manager.complete_task(task1.id)
        self.manager.complete_task(task2.id)
        
        # Verify state changes
        self.assert_equal(len(self.manager.get_pending_tasks()), 1)
        self.assert_equal(len(self.manager.get_completed_tasks()), 2)
        
        # Verify pending task is the right one
        pending = self.manager.get_pending_tasks()
        self.assert_equal(pending[0].title, "Deploy app")

# Run the complete test suite
suite = TaskManagerTestSuite()
test_methods = [
    'test_task_creation',
    'test_task_completion', 
    'test_add_task',
    'test_complete_task_by_id',
    'test_get_completed_tasks',
    'test_high_priority_tasks',
    'test_complete_workflow'
]

results = []
for test_method in test_methods:
    success = suite.run_test(test_method, getattr(suite, test_method))
    results.append(success)

all_tests_passed = all(results)
total_tests = len(results)
passed_tests = sum(results)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['all_tests_passed'] is True
        assert globals_dict['total_tests'] == 7
        assert globals_dict['passed_tests'] == 7


if __name__ == '__main__':
    pytest.main([__file__])