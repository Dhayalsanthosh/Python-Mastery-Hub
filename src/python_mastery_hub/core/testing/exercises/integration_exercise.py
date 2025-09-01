"""
Integration Testing Exercise.

Comprehensive exercise for testing database operations, API integrations,
and real-world testing scenarios with proper setup and teardown.
"""

import unittest
import sqlite3
import tempfile
import os
import json
import time
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from unittest.mock import Mock, patch


class User:
    """User model for integration testing."""
    
    def __init__(self, user_id: Optional[int] = None, username: str = "", 
                 email: str = "", active: bool = True):
        self.id = user_id
        self.username = username
        self.email = email
        self.active = active
        self.created_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "active": self.active,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_row(cls, row) -> 'User':
        """Create user from database row."""
        user = cls(
            user_id=row["id"],
            username=row["username"],
            email=row["email"],
            active=bool(row["active"])
        )
        user.created_at = row.get("created_at")
        return user


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
        if not self.connection:
            raise RuntimeError("Database not connected")
        
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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER UNIQUE,
                first_name TEXT,
                last_name TEXT,
                bio TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_username ON users(username);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email ON users(email);
        """)
        
        self.connection.commit()
    
    def drop_tables(self):
        """Drop all tables."""
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS user_profiles")
        cursor.execute("DROP TABLE IF EXISTS users")
        self.connection.commit()
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
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
        
        return User.from_row(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        return User.from_row(row) if row else None
    
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
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return cursor.rowcount > 0
    
    def get_all_users(self, active_only: bool = False) -> List[User]:
        """Get all users."""
        cursor = self.db.connection.cursor()
        
        if active_only:
            cursor.execute("SELECT * FROM users WHERE active = 1 ORDER BY username")
        else:
            cursor.execute("SELECT * FROM users ORDER BY username")
        
        return [User.from_row(row) for row in cursor.fetchall()]
    
    def create_user_profile(self, user_id: int, first_name: str, 
                          last_name: str, bio: str = "") -> bool:
        """Create user profile."""
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_profiles (user_id, first_name, last_name, bio)
                VALUES (?, ?, ?, ?)
            """, (user_id, first_name, last_name, bio))
            return True
    
    def get_user_with_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user with profile information."""
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT u.*, p.first_name, p.last_name, p.bio
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            WHERE u.id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "user": User.from_row(row).to_dict(),
            "profile": {
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "bio": row["bio"]
            } if row["first_name"] else None
        }


class EmailService:
    """Mock email service for testing."""
    
    def __init__(self):
        self.sent_emails = []
    
    def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to user."""
        email = {
            "to": user.email,
            "subject": f"Welcome, {user.username}!",
            "body": f"Hello {user.username}, welcome to our platform!",
            "sent_at": time.time()
        }
        self.sent_emails.append(email)
        return True
    
    def send_notification(self, user: User, message: str) -> bool:
        """Send notification email."""
        email = {
            "to": user.email,
            "subject": "Notification",
            "body": message,
            "sent_at": time.time()
        }
        self.sent_emails.append(email)
        return True


class UserService:
    """Business logic layer for user operations."""
    
    def __init__(self, repository: UserRepository, email_service: EmailService):
        self.repository = repository
        self.email_service = email_service
    
    def register_user(self, username: str, email: str, 
                     first_name: str = "", last_name: str = "") -> User:
        """Register a new user with validation."""
        # Validation
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        
        # Check if username exists
        if self.repository.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        
        # Create user
        user = User(username=username, email=email)
        created_user = self.repository.create_user(user)
        
        # Create profile if names provided
        if first_name or last_name:
            self.repository.create_user_profile(
                created_user.id, first_name, last_name
            )
        
        # Send welcome email
        self.email_service.send_welcome_email(created_user)
        
        return created_user
    
    def deactivate_user(self, user_id: int, reason: str = "") -> User:
        """Deactivate a user."""
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        user.active = False
        updated_user = self.repository.update_user(user)
        
        # Send notification
        if reason:
            self.email_service.send_notification(
                updated_user, 
                f"Your account has been deactivated. Reason: {reason}"
            )
        
        return updated_user
    
    def get_user_details(self, user_id: int) -> Dict[str, Any]:
        """Get complete user details."""
        user_data = self.repository.get_user_with_profile(user_id)
        if not user_data:
            raise ValueError(f"User with ID {user_id} not found")
        
        return user_data


# Integration Test Base Class
class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level database for all tests."""
        # Create temporary database file
        cls.temp_db_fd, cls.temp_db_path = tempfile.mkstemp()
        os.close(cls.temp_db_fd)  # Close file descriptor
        
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
        self.db_manager.connection.execute("DELETE FROM user_profiles")
        self.db_manager.connection.execute("DELETE FROM users")
        self.db_manager.connection.commit()
        
        # Create fresh instances for each test
        self.repository = UserRepository(self.db_manager)
        self.email_service = EmailService()
        self.service = UserService(self.repository, self.email_service)


# Exercise: Complete these test classes
class TestUserRepositoryIntegration(IntegrationTestCase):
    """Integration tests for UserRepository."""
    
    def test_create_and_retrieve_user(self):
        """Exercise 1: Test creating and retrieving a user."""
        # TODO: Implement this test
        # 1. Create a user
        # 2. Verify user was created with ID
        # 3. Retrieve user by ID
        # 4. Verify all fields match
        pass
    
    def test_unique_constraints(self):
        """Exercise 2: Test unique constraints."""
        # TODO: Implement this test
        # 1. Create a user
        # 2. Try to create another user with same username (should fail)
        # 3. Try to create another user with same email (should fail)
        # 4. Verify original user still exists
        pass
    
    def test_user_profile_relationship(self):
        """Exercise 3: Test user-profile relationship."""
        # TODO: Implement this test
        # 1. Create a user
        # 2. Create a profile for the user
        # 3. Retrieve user with profile
        # 4. Verify profile data is correct
        pass
    
    def test_transaction_rollback(self):
        """Exercise 4: Test transaction rollback on error."""
        # TODO: Implement this test
        # 1. Create a user
        # 2. Start a transaction that will fail (e.g., duplicate username)
        # 3. Verify the transaction was rolled back
        # 4. Verify original user count unchanged
        pass


class TestUserServiceIntegration(IntegrationTestCase):
    """Integration tests for UserService business logic."""
    
    def test_complete_user_registration(self):
        """Exercise 5: Test complete user registration flow."""
        # TODO: Implement this test
        # 1. Register a user with profile information
        # 2. Verify user was created in database
        # 3. Verify profile was created
        # 4. Verify welcome email was sent
        pass
    
    def test_user_deactivation_with_notification(self):
        """Exercise 6: Test user deactivation with email notification."""
        # TODO: Implement this test
        # 1. Register and activate a user
        # 2. Deactivate the user with a reason
        # 3. Verify user is deactivated in database
        # 4. Verify notification email was sent
        pass
    
    def test_get_user_details_complete(self):
        """Exercise 7: Test getting complete user details."""
        # TODO: Implement this test
        # 1. Register a user with profile
        # 2. Get user details
        # 3. Verify both user and profile data are returned
        pass
    
    def test_user_registration_validation(self):
        """Exercise 8: Test user registration validation."""
        # TODO: Implement this test
        # 1. Test various invalid inputs (short username, invalid email, etc.)
        # 2. Verify appropriate exceptions are raised
        # 3. Verify no users were created
        # 4. Verify no emails were sent
        pass


class TestDatabasePerformance(IntegrationTestCase):
    """Performance tests for database operations."""
    
    def test_bulk_user_creation(self):
        """Exercise 9: Test bulk user creation performance."""
        # TODO: Implement this test
        # 1. Create many users (e.g., 100)
        # 2. Measure execution time
        # 3. Verify all users were created
        # 4. Assert reasonable performance
        pass
    
    def test_user_search_performance(self):
        """Exercise 10: Test user search performance."""
        # TODO: Implement this test
        # 1. Create many users
        # 2. Search for users by username and email
        # 3. Measure search times
        # 4. Verify search accuracy
        pass


class TestErrorHandling(IntegrationTestCase):
    """Test error handling in integration scenarios."""
    
    def test_database_connection_failure(self):
        """Exercise 11: Test handling of database connection failures."""
        # TODO: Implement this test
        # 1. Disconnect the database
        # 2. Try to perform operations
        # 3. Verify appropriate exceptions are raised
        pass
    
    def test_partial_failure_scenarios(self):
        """Exercise 12: Test partial failure scenarios."""
        # TODO: Implement this test
        # 1. Create a scenario where user creation succeeds but email fails
        # 2. Use mocking to simulate email service failure
        # 3. Verify user is still created
        # 4. Verify error is properly handled
        pass


# Real implementation examples for reference
class TestUserRepositoryIntegrationSolution(IntegrationTestCase):
    """Solution examples for the exercises."""
    
    def test_create_and_retrieve_user_solution(self):
        """Solution for Exercise 1."""
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
    
    def test_complete_user_registration_solution(self):
        """Solution for Exercise 5."""
        # Register user with profile
        user = self.service.register_user(
            "johndoe", "john@example.com", "John", "Doe"
        )
        
        # Verify user was created
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "johndoe")
        
        # Verify profile was created
        user_details = self.service.get_user_details(user.id)
        self.assertIsNotNone(user_details["profile"])
        self.assertEqual(user_details["profile"]["first_name"], "John")
        self.assertEqual(user_details["profile"]["last_name"], "Doe")
        
        # Verify welcome email was sent
        self.assertEqual(len(self.email_service.sent_emails), 1)
        welcome_email = self.email_service.sent_emails[0]
        self.assertEqual(welcome_email["to"], "john@example.com")
        self.assertIn("Welcome", welcome_email["subject"])


def run_integration_tests():
    """Run integration tests with proper reporting."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add exercise test classes (initially will have pass statements)
    suite.addTest(unittest.makeSuite(TestUserRepositoryIntegration))
    suite.addTest(unittest.makeSuite(TestUserServiceIntegration))
    suite.addTest(unittest.makeSuite(TestDatabasePerformance))
    suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    # Add solution examples
    suite.addTest(unittest.makeSuite(TestUserRepositoryIntegrationSolution))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("Integration Testing Exercise")
    print("=" * 50)
    print("Complete the TODO exercises in the test classes.")
    print("Run individual tests or the full suite.")
    print("=" * 50)
    
    # Run the tests
    run_integration_tests()