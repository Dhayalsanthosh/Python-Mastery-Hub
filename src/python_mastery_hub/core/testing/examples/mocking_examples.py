"""
Mocking examples for the Testing module.
Comprehensive examples of unittest.mock and testing with mocks.
"""

from typing import Dict, Any


def get_mocking_examples() -> Dict[str, Any]:
    """Get comprehensive mocking examples."""
    return {
        "basic_mocking": {
            "code": '''
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import requests

# Classes to demonstrate mocking
class DatabaseConnection:
    """Mock database connection for testing."""
    
    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database
        self.connected = False
    
    def connect(self):
        """Simulate connecting to database."""
        self.connected = True
        return True
    
    def execute_query(self, query):
        """Execute a database query."""
        if not self.connected:
            raise RuntimeError("Not connected to database")
        return {"status": "success", "rows": []}
    
    def close(self):
        """Close database connection."""
        self.connected = False

class UserRepository:
    """User repository that uses database connection."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_user_by_id(self, user_id):
        """Get user by ID from database."""
        query = f"SELECT * FROM users WHERE id = {user_id}"
        result = self.db.execute_query(query)
        
        if result and result.get("rows"):
            return result["rows"][0]
        return None
    
    def create_user(self, username, email):
        """Create a new user."""
        query = f"INSERT INTO users (username, email) VALUES ('{username}', '{email}')"
        result = self.db.execute_query(query)
        
        if result["status"] == "success":
            return {"id": 123, "username": username, "email": email}
        return None

class TestBasicMocking(unittest.TestCase):
    """Basic mocking demonstrations."""
    
    def test_simple_mock(self):
        """Test basic mock usage."""
        # Create a mock object
        mock_db = Mock()
        
        # Configure mock behavior
        mock_db.connect.return_value = True
        mock_db.execute_query.return_value = {"status": "success", "rows": []}
        
        # Test using the mock
        repo = UserRepository(mock_db)
        result = repo.get_user_by_id(123)
        
        # Verify mock was called correctly
        mock_db.execute_query.assert_called_once_with("SELECT * FROM users WHERE id = 123")
        self.assertIsNone(result)  # No rows returned
    
    def test_mock_with_side_effects(self):
        """Test mock with side effects."""
        mock_db = Mock()
        
        # Mock can raise exceptions
        mock_db.execute_query.side_effect = RuntimeError("Database error")
        
        repo = UserRepository(mock_db)
        
        # Test that exception is properly raised
        with self.assertRaises(RuntimeError):
            repo.get_user_by_id(123)
    
    def test_mock_with_multiple_return_values(self):
        """Test mock with sequence of return values."""
        mock_db = Mock()
        
        # Mock returns different values on subsequent calls
        mock_db.execute_query.side_effect = [
            {"status": "success", "rows": [{"id": 1, "name": "Alice"}]},
            {"status": "success", "rows": [{"id": 2, "name": "Bob"}]},
            {"status": "error", "message": "Not found"}
        ]
        
        repo = UserRepository(mock_db)
        
        # First call
        result1 = repo.get_user_by_id(1)
        self.assertEqual(result1, {"id": 1, "name": "Alice"})
        
        # Second call
        result2 = repo.get_user_by_id(2)
        self.assertEqual(result2, {"id": 2, "name": "Bob"})
        
        # Third call returns error
        result3 = repo.get_user_by_id(3)
        self.assertIsNone(result3)

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Basic mocking with Mock objects, return values, and side effects"
        },
        
        "patch_decorator": {
            "code": '''
import unittest
from unittest.mock import Mock, patch
import requests

class APIClient:
    """API client for external service calls."""
    
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
    
    def get_user_profile(self, user_id):
        """Get user profile from external API."""
        url = f"{self.base_url}/users/{user_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile via API."""
        url = f"{self.base_url}/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.put(url, headers=headers, json=profile_data)
        response.raise_for_status()
        return response.json()

class TestPatchingDecorator(unittest.TestCase):
    """Demonstrate patching with decorators."""
    
    @patch('requests.get')
    def test_api_client_get_user(self, mock_get):
        """Test API client using patch decorator."""
        # Configure mock response
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123, "name": "Test User"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the API client
        client = APIClient("https://api.example.com", "test-key")
        result = client.get_user_profile(123)
        
        # Verify results
        self.assertEqual(result, {"id": 123, "name": "Test User"})
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://api.example.com/users/123",
            headers={"Authorization": "Bearer test-key"}
        )
    
    @patch('requests.put')
    def test_api_client_update_user(self, mock_put):
        """Test API client update with patch."""
        # Configure mock response
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123, "name": "Updated User"}
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        
        # Test the update
        client = APIClient("https://api.example.com", "test-key")
        profile_data = {"name": "Updated User", "email": "updated@example.com"}
        result = client.update_user_profile(123, profile_data)
        
        # Verify results
        self.assertEqual(result, {"id": 123, "name": "Updated User"})
        
        # Verify the request
        mock_put.assert_called_once_with(
            "https://api.example.com/users/123",
            headers={
                "Authorization": "Bearer test-key",
                "Content-Type": "application/json"
            },
            json=profile_data
        )

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Using patch decorators to mock external dependencies like HTTP requests"
        },
        
        "advanced_mocking": {
            "code": '''
import unittest
from unittest.mock import Mock, MagicMock, patch, call, mock_open
import json

class FileManager:
    """File manager for file operations."""
    
    def save_user_data(self, filename, user_data):
        """Save user data to file."""
        with open(filename, 'w') as f:
            json.dump(user_data, f)
        return True
    
    def load_user_data(self, filename):
        """Load user data from file."""
        with open(filename, 'r') as f:
            return json.load(f)

class TestAdvancedMocking(unittest.TestCase):
    """Advanced mocking techniques."""
    
    def test_mock_with_spec(self):
        """Test mock with spec to ensure correct interface."""
        # Mock with spec prevents calling non-existent methods
        mock_db = Mock(spec=DatabaseConnection)
        
        # This works - method exists on DatabaseConnection
        mock_db.connect.return_value = True
        self.assertTrue(mock_db.connect())
        
        # This would raise AttributeError if uncommented
        # mock_db.non_existent_method()
    
    def test_magic_mock_for_special_methods(self):
        """Test MagicMock for special methods like __len__, __iter__, etc."""
        mock_list = MagicMock()
        
        # Configure magic methods
        mock_list.__len__.return_value = 3
        mock_list.__iter__.return_value = iter([1, 2, 3])
        mock_list.__getitem__.side_effect = lambda i: [1, 2, 3][i]
        
        # Test magic method behavior
        self.assertEqual(len(mock_list), 3)
        self.assertEqual(list(mock_list), [1, 2, 3])
        self.assertEqual(mock_list[1], 2)
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"id": 1, "name": "File User"}')
    def test_load_user_data(self, mock_file):
        """Test loading user data from file."""
        file_manager = FileManager()
        result = file_manager.load_user_data("users.json")
        
        # Verify file was opened correctly
        mock_file.assert_called_once_with("users.json", 'r')
        
        # Verify data was loaded
        self.assertEqual(result, {"id": 1, "name": "File User"})
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_user_data(self, mock_json_dump, mock_file):
        """Test saving user data to file."""
        file_manager = FileManager()
        user_data = {"id": 2, "name": "Save User"}
        
        result = file_manager.save_user_data("users.json", user_data)
        
        # Verify file operations
        mock_file.assert_called_once_with("users.json", 'w')
        mock_json_dump.assert_called_once_with(user_data, mock_file.return_value.__enter__.return_value)
        
        self.assertTrue(result)
    
    def test_mock_call_tracking(self):
        """Test tracking mock calls."""
        mock_db = Mock()
        repo = UserRepository(mock_db)
        
        # Make several calls
        repo.get_user_by_id(1)
        repo.get_user_by_id(2)
        repo.create_user("alice", "alice@example.com")
        
        # Verify call count
        self.assertEqual(mock_db.execute_query.call_count, 3)
        
        # Verify specific calls
        expected_calls = [
            call("SELECT * FROM users WHERE id = 1"),
            call("SELECT * FROM users WHERE id = 2"),
            call("INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com')")
        ]
        mock_db.execute_query.assert_has_calls(expected_calls)
    
    def test_mock_reset(self):
        """Test resetting mock state."""
        mock_obj = Mock()
        
        # Make some calls
        mock_obj.method1()
        mock_obj.method2("arg")
        
        # Verify calls were made
        self.assertEqual(mock_obj.method1.call_count, 1)
        self.assertEqual(mock_obj.method2.call_count, 1)
        
        # Reset mock
        mock_obj.reset_mock()
        
        # Verify calls were cleared
        self.assertEqual(mock_obj.method1.call_count, 0)
        self.assertEqual(mock_obj.method2.call_count, 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Advanced mocking techniques including specs, magic methods, file operations, and call tracking"
        }
    }