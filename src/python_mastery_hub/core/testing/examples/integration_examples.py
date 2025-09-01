"""
Integration testing examples for the Testing module.
Demonstrates testing components working together with real dependencies.
"""

from typing import Dict, Any


def get_integration_examples() -> Dict[str, Any]:
    """Get comprehensive integration testing examples."""
    return {
        "database_integration": {
            "code": '''
import unittest
import sqlite3
import tempfile
import os
from contextlib import contextmanager
from typing import Optional, List

class User:
    """User model for integration testing."""
    
    def __init__(self, user_id: Optional[int] = None, username: str = "", 
                 email: str = "", active: bool = True):
        self.id = user_id
        self.username = username
        self.email = email
        self.active = active

class DatabaseManager:
    """Database manager for user operations."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Connect to database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def disconnect(self):
        """Disconnect from database."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_tables(self):
        """Create database tables."""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_user(self, user: User) -> User:
        """Create a new user."""
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, active)
                VALUES (?, ?, ?)
            """, (user.username, user.email, user.active))
            
            user.id = cursor.lastrowid
            return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            return User(
                user_id=row["id"],
                username=row["username"],
                email=row["email"],
                active=bool(row["active"])
            )
        return None
    
    def update_user(self, user: User) -> User:
        """Update user information."""
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET username = ?, email = ?, active = ?
                WHERE id = ?
            """, (user.username, user.email, user.active, user.id))
            
            if cursor.rowcount == 0:
                raise ValueError(f"User with ID {user.id} not found")
            
            return user
    
    def get_all_users(self, active_only: bool = False) -> List[User]:
        """Get all users."""
        cursor = self.db.connection.cursor()
        
        if active_only:
            cursor.execute("SELECT * FROM users WHERE active = 1 ORDER BY username")
        else:
            cursor.execute("SELECT * FROM users ORDER BY username")
        
        users = []
        for row in cursor.fetchall():
            users.append(User(
                user_id=row["id"],
                username=row["username"],
                email=row["email"],
                active=bool(row["active"])
            ))
        
        return users

# Integration test base class
class DatabaseIntegrationTestCase(unittest.TestCase):
    """Base class for database integration tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level database for all tests."""
        cls.temp_db_fd, cls.temp_db_path = tempfile.mkstemp()
        os.close(cls.temp_db_fd)
        
        cls.db_manager = DatabaseManager(cls.temp_db_path)
        cls.db_manager.connect()
        cls.db_manager.create_tables()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level database."""
        cls.db_manager.disconnect()
        os.unlink(cls.temp_db_path)
    
    def setUp(self):
        """Set up for each test."""
        # Clear all data before each test
        self.db_manager.connection.execute("DELETE FROM users")
        self.db_manager.connection.commit()
        
        # Create fresh instances
        self.repository = UserRepository(self.db_manager)

class TestUserRepositoryIntegration(DatabaseIntegrationTestCase):
    """Integration tests for UserRepository."""
    
    def test_create_and_retrieve_user(self):
        """Test creating and retrieving a user."""
        # Create user
        user = User(username="testuser", email="test@example.com")
        created_user = self.repository.create_user(user)
        
        # Verify user was created with ID
        self.assertIsNotNone(created_user.id)
        self.assertEqual(created_user.username, "testuser")
        self.assertEqual(created_user.email, "test@example.com")
        self.assertTrue(created_user.active)
        
        # Retrieve user by ID
        retrieved_user = self.repository.get_user_by_id(created_user.id)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "testuser")
        self.assertEqual(retrieved_user.email, "test@example.com")
    
    def test_unique_username_constraint(self):
        """Test that username uniqueness is enforced."""
        # Create first user
        user1 = User(username="uniqueuser", email="user1@example.com")
        self.repository.create_user(user1)
        
        # Try to create second user with same username
        user2 = User(username="uniqueuser", email="user2@example.com")
        
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.create_user(user2)
    
    def test_update_user(self):
        """Test updating user information."""
        # Create user
        user = User(username="updateme", email="old@example.com")
        created_user = self.repository.create_user(user)
        
        # Update user
        created_user.email = "new@example.com"
        created_user.active = False
        updated_user = self.repository.update_user(created_user)
        
        # Verify update
        self.assertEqual(updated_user.email, "new@example.com")
        self.assertFalse(updated_user.active)
        
        # Verify in database
        retrieved_user = self.repository.get_user_by_id(created_user.id)
        self.assertEqual(retrieved_user.email, "new@example.com")
        self.assertFalse(retrieved_user.active)
    
    def test_get_all_users_with_filtering(self):
        """Test retrieving all users with filtering."""
        # Create multiple users
        users = [
            User(username="user1", email="user1@example.com"),
            User(username="user2", email="user2@example.com", active=False),
            User(username="user3", email="user3@example.com"),
        ]
        
        for user in users:
            self.repository.create_user(user)
        
        # Get all users
        all_users = self.repository.get_all_users()
        self.assertEqual(len(all_users), 3)
        
        # Get only active users
        active_users = self.repository.get_all_users(active_only=True)
        self.assertEqual(len(active_users), 2)
        
        # Verify they're sorted by username
        usernames = [user.username for user in all_users]
        self.assertEqual(usernames, sorted(usernames))

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Database integration testing with real SQLite database, transactions, and data persistence"
        },
        
        "api_integration": {
            "code": '''
import unittest
from unittest.mock import patch, Mock
import requests
import json

class APIIntegrationTest(unittest.TestCase):
    """Integration tests for external API interactions."""
    
    def setUp(self):
        """Set up test configuration."""
        self.api_base_url = "https://jsonplaceholder.typicode.com"
        self.timeout = 10
    
    def test_real_api_get_request(self):
        """Test real API GET request (requires internet)."""
        # This test makes an actual HTTP request
        response = requests.get(
            f"{self.api_base_url}/posts/1",
            timeout=self.timeout
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("title", data)
        self.assertIn("body", data)
        self.assertEqual(data["id"], 1)
    
    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling with mocked failures."""
        # Configure mock to simulate network error
        mock_get.side_effect = requests.ConnectionError("Network error")
        
        # Test error handling
        with self.assertRaises(requests.ConnectionError):
            requests.get(f"{self.api_base_url}/posts/1")
    
    @patch('requests.post')
    def test_api_post_request(self, mock_post):
        """Test API POST request with mocked response."""
        # Configure mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 101, "title": "New Post"}
        mock_post.return_value = mock_response
        
        # Make request
        post_data = {"title": "New Post", "body": "Content", "userId": 1}
        response = requests.post(
            f"{self.api_base_url}/posts",
            json=post_data
        )
        
        # Verify
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["id"], 101)
        mock_post.assert_called_once()

class FileSystemIntegrationTest(unittest.TestCase):
    """Integration tests for file system operations."""
    
    def setUp(self):
        """Set up temporary file for testing."""
        import tempfile
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file."""
        import os
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_file_write_and_read(self):
        """Test writing to and reading from file."""
        test_data = {"name": "Integration Test", "value": 42}
        
        # Write data
        with open(self.temp_file_path, 'w') as f:
            json.dump(test_data, f)
        
        # Read data back
        with open(self.temp_file_path, 'r') as f:
            loaded_data = json.load(f)
        
        # Verify
        self.assertEqual(loaded_data, test_data)
    
    def test_file_operations_with_context_manager(self):
        """Test file operations with proper resource management."""
        test_content = "Integration testing content\\nMultiple lines\\n"
        
        # Write with context manager
        with open(self.temp_file_path, 'w') as f:
            f.write(test_content)
        
        # Read with context manager
        with open(self.temp_file_path, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, test_content)

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Integration testing with external APIs and file system operations, mixing real and mocked dependencies"
        },
        
        "full_stack_integration": {
            "code": '''
import unittest
import tempfile
import os
import sqlite3
from typing import Dict, Any, List

class UserService:
    """Complete user service integrating repository and business logic."""
    
    def __init__(self, repository):
        self.repository = repository
        self.audit_log = []
    
    def register_user(self, username: str, email: str) -> Dict[str, Any]:
        """Register a new user with validation and audit logging."""
        # Validation
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        
        # Check if username exists
        existing_user = self.repository.get_user_by_username(username)
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")
        
        # Create user
        user = User(username=username, email=email)
        created_user = self.repository.create_user(user)
        
        # Audit log
        self.audit_log.append({
            "action": "user_registered",
            "user_id": created_user.id,
            "username": username,
            "timestamp": "2024-01-01T00:00:00Z"
        })
        
        return {
            "user_id": created_user.id,
            "username": created_user.username,
            "email": created_user.email,
            "active": created_user.active
        }
    
    def deactivate_user(self, user_id: int, reason: str = "") -> bool:
        """Deactivate a user with audit logging."""
        user = self.repository.get_user_by_id(user_id)
        if not user:
            return False
        
        user.active = False
        self.repository.update_user(user)
        
        # Audit log
        self.audit_log.append({
            "action": "user_deactivated",
            "user_id": user_id,
            "reason": reason,
            "timestamp": "2024-01-01T00:00:00Z"
        })
        
        return True
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        all_users = self.repository.get_all_users()
        active_users = self.repository.get_all_users(active_only=True)
        
        return {
            "total_users": len(all_users),
            "active_users": len(active_users),
            "inactive_users": len(all_users) - len(active_users),
            "activity_rate": len(active_users) / len(all_users) if all_users else 0
        }

class FullStackIntegrationTest(unittest.TestCase):
    """Full stack integration test covering multiple layers."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database for full integration testing."""
        cls.temp_db_fd, cls.temp_db_path = tempfile.mkstemp()
        os.close(cls.temp_db_fd)
        
        # Set up complete stack
        cls.db_manager = DatabaseManager(cls.temp_db_path)
        cls.db_manager.connect()
        cls.db_manager.create_tables()
        
        cls.repository = UserRepository(cls.db_manager)
        cls.user_service = UserService(cls.repository)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test resources."""
        cls.db_manager.disconnect()
        os.unlink(cls.temp_db_path)
    
    def setUp(self):
        """Clean state for each test."""
        # Clear database
        self.db_manager.connection.execute("DELETE FROM users")
        self.db_manager.connection.commit()
        
        # Clear audit log
        self.user_service.audit_log.clear()
    
    def test_complete_user_lifecycle(self):
        """Test complete user lifecycle from registration to deactivation."""
        # Register user
        user_data = self.user_service.register_user("testuser", "test@example.com")
        
        # Verify registration
        self.assertEqual(user_data["username"], "testuser")
        self.assertEqual(user_data["email"], "test@example.com")
        self.assertTrue(user_data["active"])
        self.assertIsNotNone(user_data["user_id"])
        
        # Verify audit log
        self.assertEqual(len(self.user_service.audit_log), 1)
        self.assertEqual(self.user_service.audit_log[0]["action"], "user_registered")
        
        # Verify user exists in database
        retrieved_user = self.repository.get_user_by_id(user_data["user_id"])
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "testuser")
        
        # Test user stats
        stats = self.user_service.get_user_stats()
        self.assertEqual(stats["total_users"], 1)
        self.assertEqual(stats["active_users"], 1)
        self.assertEqual(stats["inactive_users"], 0)
        self.assertEqual(stats["activity_rate"], 1.0)
        
        # Deactivate user
        success = self.user_service.deactivate_user(user_data["user_id"], "Test deactivation")
        self.assertTrue(success)
        
        # Verify deactivation in database
        updated_user = self.repository.get_user_by_id(user_data["user_id"])
        self.assertFalse(updated_user.active)
        
        # Verify audit log
        self.assertEqual(len(self.user_service.audit_log), 2)
        self.assertEqual(self.user_service.audit_log[1]["action"], "user_deactivated")
        
        # Test updated stats
        final_stats = self.user_service.get_user_stats()
        self.assertEqual(final_stats["total_users"], 1)
        self.assertEqual(final_stats["active_users"], 0)
        self.assertEqual(final_stats["inactive_users"], 1)
        self.assertEqual(final_stats["activity_rate"], 0.0)
    
    def test_business_logic_validation_integration(self):
        """Test that business logic validation integrates with database constraints."""
        # Test username validation
        with self.assertRaises(ValueError) as context:
            self.user_service.register_user("ab", "valid@example.com")
        self.assertIn("at least 3 characters", str(context.exception))
        
        # Test email validation
        with self.assertRaises(ValueError):
            self.user_service.register_user("validuser", "invalid-email")
        
        # Test duplicate username (business logic + database constraint)
        self.user_service.register_user("existinguser", "user1@example.com")
        
        with self.assertRaises(ValueError) as context:
            self.user_service.register_user("existinguser", "user2@example.com")
        self.assertIn("already exists", str(context.exception))
    
    def test_concurrent_user_operations(self):
        """Test multiple user operations in sequence."""
        # Register multiple users
        users_data = []
        for i in range(5):
            user_data = self.user_service.register_user(f"user{i}", f"user{i}@example.com")
            users_data.append(user_data)
        
        # Verify all users created
        stats = self.user_service.get_user_stats()
        self.assertEqual(stats["total_users"], 5)
        self.assertEqual(stats["active_users"], 5)
        
        # Deactivate some users
        self.user_service.deactivate_user(users_data[1]["user_id"])
        self.user_service.deactivate_user(users_data[3]["user_id"])
        
        # Verify final state
        final_stats = self.user_service.get_user_stats()
        self.assertEqual(final_stats["total_users"], 5)
        self.assertEqual(final_stats["active_users"], 3)
        self.assertEqual(final_stats["inactive_users"], 2)
        self.assertEqual(final_stats["activity_rate"], 0.6)
        
        # Verify audit log
        self.assertEqual(len(self.user_service.audit_log), 7)  # 5 registrations + 2 deactivations

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Full-stack integration testing covering database, repository, business logic, and audit logging layers"
        }
    }