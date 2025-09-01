# tests/integration/test_database_integration.py
"""
Integration tests for database functionality.
Tests database operations, transactions, and data persistence.
"""

import pytest
import asyncio
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import Dict, List, Any, Optional


class MockDatabase:
    """Mock database for integration testing"""
    
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.connection = None
        self.transaction_active = False
        self.connection_pool = []
        self.max_connections = 10
    
    async def connect(self):
        """Connect to database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        await self.create_tables()
        return self.connection
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    async def create_tables(self):
        """Create database tables"""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                role TEXT DEFAULT 'student'
            )
        ''')
        
        # Exercises table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                difficulty TEXT NOT NULL,
                topic TEXT NOT NULL,
                points INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                language TEXT DEFAULT 'python',
                score REAL,
                status TEXT DEFAULT 'pending',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                feedback TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (exercise_id) REFERENCES exercises (id)
            )
        ''')
        
        # Progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                exercises_completed INTEGER DEFAULT 0,
                total_exercises INTEGER DEFAULT 0,
                points_earned INTEGER DEFAULT 0,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, topic),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.connection.commit()
    
    async def begin_transaction(self):
        """Begin database transaction"""
        if self.transaction_active:
            raise Exception("Transaction already active")
        
        self.connection.execute("BEGIN")
        self.transaction_active = True
    
    async def commit_transaction(self):
        """Commit database transaction"""
        if not self.transaction_active:
            raise Exception("No active transaction")
        
        self.connection.commit()
        self.transaction_active = False
    
    async def rollback_transaction(self):
        """Rollback database transaction"""
        if not self.transaction_active:
            raise Exception("No active transaction")
        
        self.connection.rollback()
        self.transaction_active = False
    
    async def create_user(self, username, email, password_hash, role='student'):
        """Create a new user"""
        cursor = self.connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, role))
            
            user_id = cursor.lastrowid
            self.connection.commit()
            
            # Initialize progress for all topics
            topics = ['basics', 'oop', 'advanced', 'data_structures', 'algorithms']
            for topic in topics:
                await self.init_user_progress(user_id, topic)
            
            return await self.get_user_by_id(user_id)
            
        except sqlite3.IntegrityError as e:
            raise ValueError(f"User creation failed: {str(e)}")
    
    async def get_user_by_id(self, user_id):
        """Get user by ID"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    async def get_user_by_username(self, username):
        """Get user by username"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    async def update_user(self, user_id, **kwargs):
        """Update user information"""
        if not kwargs:
            return await self.get_user_by_id(user_id)
        
        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['username', 'email', 'password_hash', 'role', 'is_active']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return await self.get_user_by_id(user_id)
        
        # Add updated_at
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
        
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        
        return await self.get_user_by_id(user_id)
    
    async def create_exercise(self, title, description, difficulty, topic, points=10):
        """Create a new exercise"""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO exercises (title, description, difficulty, topic, points)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, difficulty, topic, points))
        
        exercise_id = cursor.lastrowid
        self.connection.commit()
        
        # Update total exercises count for all users
        await self.update_topic_totals(topic)
        
        return await self.get_exercise_by_id(exercise_id)
    
    async def get_exercise_by_id(self, exercise_id):
        """Get exercise by ID"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM exercises WHERE id = ? AND is_active = 1', (exercise_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    async def get_exercises(self, topic=None, difficulty=None, limit=10, offset=0):
        """Get exercises with filtering and pagination"""
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM exercises WHERE is_active = 1"
        params = []
        
        if topic:
            query += " AND topic = ?"
            params.append(topic)
        
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        
        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        exercises = [dict(row) for row in rows]
        
        return {
            "exercises": exercises,
            "total": total,
            "page": (offset // limit) + 1,
            "per_page": limit
        }
    
    async def create_submission(self, user_id, exercise_id, code, language='python'):
        """Create a new submission"""
        cursor = self.connection.cursor()
        
        # Verify exercise exists
        exercise = await self.get_exercise_by_id(exercise_id)
        if not exercise:
            raise ValueError("Exercise not found")
        
        cursor.execute('''
            INSERT INTO submissions (user_id, exercise_id, code, language)
            VALUES (?, ?, ?, ?)
        ''', (user_id, exercise_id, code, language))
        
        submission_id = cursor.lastrowid
        self.connection.commit()
        
        return await self.get_submission_by_id(submission_id)
    
    async def update_submission(self, submission_id, score=None, status=None, feedback=None):
        """Update submission with results"""
        cursor = self.connection.cursor()
        
        updates = []
        params = []
        
        if score is not None:
            updates.append("score = ?")
            params.append(score)
        
        if status is not None:
            updates.append("status = ?")
            params.append(status)
            
            if status == 'completed':
                updates.append("completed_at = CURRENT_TIMESTAMP")
        
        if feedback is not None:
            updates.append("feedback = ?")
            params.append(feedback)
        
        if not updates:
            return await self.get_submission_by_id(submission_id)
        
        params.append(submission_id)
        query = f"UPDATE submissions SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        self.connection.commit()
        
        # Update user progress if submission completed
        if status == 'completed':
            submission = await self.get_submission_by_id(submission_id)
            await self.update_user_progress(submission['user_id'], submission['exercise_id'], score or 0)
        
        return await self.get_submission_by_id(submission_id)
    
    async def get_submission_by_id(self, submission_id):
        """Get submission by ID"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    async def get_user_submissions(self, user_id, exercise_id=None, limit=10, offset=0):
        """Get user submissions"""
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM submissions WHERE user_id = ?"
        params = [user_id]
        
        if exercise_id:
            query += " AND exercise_id = ?"
            params.append(exercise_id)
        
        query += " ORDER BY submitted_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    async def init_user_progress(self, user_id, topic):
        """Initialize user progress for a topic"""
        cursor = self.connection.cursor()
        
        # Count total exercises for topic
        cursor.execute('SELECT COUNT(*) FROM exercises WHERE topic = ? AND is_active = 1', (topic,))
        total_exercises = cursor.fetchone()[0]
        
        cursor.execute('''
            INSERT OR IGNORE INTO progress (user_id, topic, total_exercises)
            VALUES (?, ?, ?)
        ''', (user_id, topic, total_exercises))
        
        self.connection.commit()
    
    async def update_user_progress(self, user_id, exercise_id, score):
        """Update user progress after exercise completion"""
        # Get exercise info
        exercise = await self.get_exercise_by_id(exercise_id)
        if not exercise:
            return
        
        topic = exercise['topic']
        points = exercise['points'] if score >= 70 else 0  # Only award points for passing grade
        
        cursor = self.connection.cursor()
        
        # Check if this is the first successful submission for this exercise
        cursor.execute('''
            SELECT COUNT(*) FROM submissions 
            WHERE user_id = ? AND exercise_id = ? AND score >= 70 AND status = 'completed'
        ''', (user_id, exercise_id))
        
        successful_submissions = cursor.fetchone()[0]
        
        # Only update progress if this is the first successful submission
        if successful_submissions == 1 and score >= 70:
            cursor.execute('''
                UPDATE progress 
                SET exercises_completed = exercises_completed + 1,
                    points_earned = points_earned + ?,
                    last_activity = CURRENT_TIMESTAMP
                WHERE user_id = ? AND topic = ?
            ''', (points, user_id, topic))
            
            self.connection.commit()
    
    async def get_user_progress(self, user_id):
        """Get user progress across all topics"""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            SELECT topic, exercises_completed, total_exercises, points_earned, last_activity
            FROM progress 
            WHERE user_id = ?
        ''', (user_id,))
        
        rows = cursor.fetchall()
        progress = {"user_id": user_id, "topics": {}, "total_points": 0}
        
        total_completed = 0
        total_exercises = 0
        
        for row in rows:
            topic_data = dict(row)
            topic = topic_data['topic']
            
            progress["topics"][topic] = {
                "completed": topic_data['exercises_completed'],
                "total": topic_data['total_exercises'],
                "points": topic_data['points_earned'],
                "progress": (topic_data['exercises_completed'] / topic_data['total_exercises'] * 100) if topic_data['total_exercises'] > 0 else 0
            }
            
            total_completed += topic_data['exercises_completed']
            total_exercises += topic_data['total_exercises']
            progress["total_points"] += topic_data['points_earned']
        
        progress["overall_progress"] = (total_completed / total_exercises * 100) if total_exercises > 0 else 0
        progress["level"] = min(progress["total_points"] // 100 + 1, 10)
        
        return progress
    
    async def update_topic_totals(self, topic):
        """Update total exercises count for a topic"""
        cursor = self.connection.cursor()
        
        # Count active exercises for topic
        cursor.execute('SELECT COUNT(*) FROM exercises WHERE topic = ? AND is_active = 1', (topic,))
        total_exercises = cursor.fetchone()[0]
        
        # Update all users' progress for this topic
        cursor.execute('''
            UPDATE progress 
            SET total_exercises = ?
            WHERE topic = ?
        ''', (total_exercises, topic))
        
        self.connection.commit()
    
    async def create_session(self, session_id, user_id, expires_at):
        """Create user session"""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (id, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (session_id, user_id, expires_at))
        
        self.connection.commit()
    
    async def get_session(self, session_id):
        """Get session by ID"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM sessions 
            WHERE id = ? AND is_active = 1 AND expires_at > CURRENT_TIMESTAMP
        ''', (session_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE sessions 
            SET is_active = 0 
            WHERE expires_at <= CURRENT_TIMESTAMP
        ''')
        
        deleted_count = cursor.rowcount
        self.connection.commit()
        return deleted_count


class TestDatabaseConnection:
    """Test database connection and basic operations"""
    
    @pytest.fixture
    async def db(self):
        database = MockDatabase()
        await database.connect()
        yield database
        await database.disconnect()
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection and disconnection"""
        db = MockDatabase()
        
        # Initially not connected
        assert db.connection is None
        
        # Connect
        connection = await db.connect()
        assert connection is not None
        assert db.connection is not None
        
        # Disconnect
        await db.disconnect()
        assert db.connection is None
    
    @pytest.mark.asyncio
    async def test_table_creation(self, db):
        """Test that all required tables are created"""
        cursor = db.connection.cursor()
        
        # Check that tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'exercises', 'submissions', 'progress', 'sessions']
        for table in expected_tables:
            assert table in tables
    
    @pytest.mark.asyncio
    async def test_database_schema_integrity(self, db):
        """Test database schema integrity"""
        cursor = db.connection.cursor()
        
        # Test users table schema
        cursor.execute("PRAGMA table_info(users)")
        user_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'id' in user_columns
        assert 'username' in user_columns
        assert 'email' in user_columns
        assert 'password_hash' in user_columns
        
        # Test foreign key constraints
        cursor.execute("PRAGMA foreign_key_list(submissions)")
        foreign_keys = cursor.fetchall()
        
        # Should have foreign keys to users and exercises
        assert len(foreign_keys) >= 2


class TestUserOperations:
    """Test user-related database operations"""
    
    @pytest.fixture
    async def db(self):
        database = MockDatabase()
        await database.connect()
        yield database
        await database.disconnect()
    
    @pytest.mark.asyncio
    async def test_create_user(self, db):
        """Test user creation"""
        user = await db.create_user(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            role="student"
        )
        
        assert user is not None
        assert user['username'] == "testuser"
        assert user['email'] == "test@example.com"
        assert user['role'] == "student"
        assert user['is_active'] == 1
        assert 'id' in user
        assert 'created_at' in user
    
    @pytest.mark.asyncio
    async def test_create_duplicate_user(self, db):
        """Test handling of duplicate user creation"""
        # Create first user
        await db.create_user("duplicate", "dup1@example.com", "hash1")
        
        # Try to create user with same username
        with pytest.raises(ValueError, match="User creation failed"):
            await db.create_user("duplicate", "dup2@example.com", "hash2")
        
        # Try to create user with same email
        with pytest.raises(ValueError, match="User creation failed"):
            await db.create_user("different", "dup1@example.com", "hash3")
    
    @pytest.mark.asyncio
    async def test_get_user_operations(self, db):
        """Test user retrieval operations"""
        # Create test user
        created_user = await db.create_user("getuser", "get@example.com", "hash")
        user_id = created_user['id']
        
        # Get by ID
        user_by_id = await db.get_user_by_id(user_id)
        assert user_by_id['username'] == "getuser"
        
        # Get by username
        user_by_username = await db.get_user_by_username("getuser")
        assert user_by_username['id'] == user_id
        
        # Get non-existent user
        non_existent = await db.get_user_by_id(99999)
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_update_user(self, db):
        """Test user update operations"""
        # Create user
        user = await db.create_user("updateuser", "update@example.com", "hash")
        user_id = user['id']
        
        # Update user
        updated_user = await db.update_user(
            user_id,
            email="new@example.com",
            role="instructor"
        )
        
        assert updated_user['email'] == "new@example.com"
        assert updated_user['role'] == "instructor"
        assert updated_user['username'] == "updateuser"  # Unchanged
        
        # Verify update persisted
        retrieved_user = await db.get_user_by_id(user_id)
        assert retrieved_user['email'] == "new@example.com"
        assert retrieved_user['role'] == "instructor"
    
    @pytest.mark.asyncio
    async def test_user_progress_initialization(self, db):
        """Test that user progress is initialized on creation"""
        user = await db.create_user("progressuser", "prog@example.com", "hash")
        
        # Check that progress was initialized
        progress = await db.get_user_progress(user['id'])
        
        assert progress['user_id'] == user['id']
        assert 'topics' in progress
        assert len(progress['topics']) > 0
        
        # Each topic should have initial values
        for topic, data in progress['topics'].items():
            assert data['completed'] == 0
            assert data['total'] >= 0
            assert data['points'] == 0


class TestExerciseOperations:
    """Test exercise-related database operations"""
    
    @pytest.fixture
    async def db(self):
        database = MockDatabase()
        await database.connect()
        yield database
        await database.disconnect()
    
    @pytest.mark.asyncio
    async def test_create_exercise(self, db):
        """Test exercise creation"""
        exercise = await db.create_exercise(
            title="Test Exercise",
            description="A test exercise",
            difficulty="beginner",
            topic="basics",
            points=15
        )
        
        assert exercise is not None
        assert exercise['title'] == "Test Exercise"
        assert exercise['difficulty'] == "beginner"
        assert exercise['topic'] == "basics"
        assert exercise['points'] == 15
        assert exercise['is_active'] == 1
    
    @pytest.mark.asyncio
    async def test_get_exercises_with_filtering(self, db):
        """Test exercise retrieval with filtering"""
        # Create test exercises
        await db.create_exercise("Basics 1", "Desc 1", "beginner", "basics")
        await db.create_exercise("Basics 2", "Desc 2", "intermediate", "basics")
        await db.create_exercise("OOP 1", "Desc 3", "beginner", "oop")
        
        # Get all exercises
        all_exercises = await db.get_exercises()
        assert all_exercises['total'] == 3
        
        # Filter by topic
        basics_exercises = await db.get_exercises(topic="basics")
        assert basics_exercises['total'] == 2
        
        # Filter by difficulty
        beginner_exercises = await db.get_exercises(difficulty="beginner")
        assert beginner_exercises['total'] == 2
        
        # Filter by both
        basics_beginner = await db.get_exercises(topic="basics", difficulty="beginner")
        assert basics_beginner['total'] == 1
    
    @pytest.mark.asyncio
    async def test_exercise_pagination(self, db):
        """Test exercise pagination"""
        # Create multiple exercises
        for i in range(5):
            await db.create_exercise(f"Exercise {i}", f"Desc {i}", "beginner", "basics")
        
        # Test pagination
        page1 = await db.get_exercises(limit=2, offset=0)
        assert len(page1['exercises']) == 2
        assert page1['page'] == 1
        
        page2 = await db.get_exercises(limit=2, offset=2)
        assert len(page2['exercises']) == 2
        assert page2['page'] == 2
        
        page3 = await db.get_exercises(limit=2, offset=4)
        assert len(page3['exercises']) == 1
        assert page3['page'] == 3
    
    @pytest.mark.asyncio
    async def test_exercise_affects_user_progress_totals(self, db):
        """Test that creating exercises updates user progress totals"""
        # Create user first
        user = await db.create_user("exuser", "ex@example.com", "hash")
        
        # Initial progress
        initial_progress = await db.get_user_progress(user['id'])
        initial_total = initial_progress['topics']['basics']['total']
        
        # Create exercise
        await db.create_exercise("New Exercise", "Description", "beginner", "basics")
        
        # Check updated progress
        updated_progress = await db.get_user_progress(user['id'])
        updated_total = updated_progress['topics']['basics']['total']
        
        assert updated_total == initial_total + 1


class TestSubmissionOperations:
    """Test submission-related database operations"""
    
    @pytest.fixture
    async def setup_data(self):
        db = MockDatabase()
        await db.connect()
        
        # Create test user and exercise
        user = await db.create_user("subuser", "sub@example.com", "hash")
        exercise = await db.create_exercise("Sub Exercise", "Description", "beginner", "basics", 20)
        
        yield db, user, exercise
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_create_submission(self, setup_data):
        """Test submission creation"""
        db, user, exercise = setup_data
        
        submission = await db.create_submission(
            user_id=user['id'],
            exercise_id=exercise['id'],
            code="def solution(): return 'Hello'",
            language="python"
        )
        
        assert submission is not None
        assert submission['user_id'] == user['id']
        assert submission['exercise_id'] == exercise['id']
        assert submission['code'] == "def solution(): return 'Hello'"
        assert submission['language'] == "python"
        assert submission['status'] == 'pending'
    
    @pytest.mark.asyncio
    async def test_submission_to_nonexistent_exercise(self, setup_data):
        """Test submission to non-existent exercise"""
        db, user, exercise = setup_data
        
        with pytest.raises(ValueError, match="Exercise not found"):
            await db.create_submission(
                user_id=user['id'],
                exercise_id=99999,
                code="def solution(): pass"
            )
    
    @pytest.mark.asyncio
    async def test_update_submission_with_results(self, setup_data):
        """Test updating submission with results"""
        db, user, exercise = setup_data
        
        # Create submission
        submission = await db.create_submission(
            user_id=user['id'],
            exercise_id=exercise['id'],
            code="def solution(): return 42"
        )
        
        # Update with results
        updated_submission = await db.update_submission(
            submission['id'],
            score=85.5,
            status='completed',
            feedback='Good solution!'
        )
        
        assert updated_submission['score'] == 85.5
        assert updated_submission['status'] == 'completed'
        assert updated_submission['feedback'] == 'Good solution!'
        assert updated_submission['completed_at'] is not None
    
    @pytest.mark.asyncio
    async def test_submission_updates_progress(self, setup_data):
        """Test that completed submissions update user progress"""
        db, user, exercise = setup_data
        
        # Initial progress
        initial_progress = await db.get_user_progress(user['id'])
        initial_completed = initial_progress['topics']['basics']['completed']
        initial_points = initial_progress['total_points']
        
        # Submit and complete exercise
        submission = await db.create_submission(
            user_id=user['id'],
            exercise_id=exercise['id'],
            code="def solution(): return 'correct'"
        )
        
        await db.update_submission(
            submission['id'],
            score=85,  # Passing score
            status='completed'
        )
        
        # Check updated progress
        updated_progress = await db.get_user_progress(user['id'])
        
        assert updated_progress['topics']['basics']['completed'] == initial_completed + 1
        assert updated_progress['total_points'] == initial_points + exercise['points']
    
    @pytest.mark.asyncio
    async def test_failing_submission_no_progress_update(self, setup_data):
        """Test that failing submissions don't update progress"""
        db, user, exercise = setup_data
        
        # Initial progress
        initial_progress = await db.get_user_progress(user['id'])
        initial_completed = initial_progress['topics']['basics']['completed']
        initial_points = initial_progress['total_points']
        
        # Submit failing solution
        submission = await db.create_submission(
            user_id=user['id'],
            exercise_id=exercise['id'],
            code="def solution(): return 'wrong'"
        )
        
        await db.update_submission(
            submission['id'],
            score=45,  # Failing score
            status='completed'
        )
        
        # Progress should not change
        updated_progress = await db.get_user_progress(user['id'])
        
        assert updated_progress['topics']['basics']['completed'] == initial_completed
        assert updated_progress['total_points'] == initial_points
    
    @pytest.mark.asyncio
    async def test_get_user_submissions(self, setup_data):
        """Test retrieving user submissions"""
        db, user, exercise = setup_data
        
        # Create multiple submissions
        submission1 = await db.create_submission(user['id'], exercise['id'], "code1")
        submission2 = await db.create_submission(user['id'], exercise['id'], "code2")
        
        # Get all user submissions
        submissions = await db.get_user_submissions(user['id'])
        
        assert len(submissions) == 2
        assert submissions[0]['id'] in [submission1['id'], submission2['id']]
        
        # Get submissions for specific exercise
        exercise_submissions = await db.get_user_submissions(user['id'], exercise['id'])
        assert len(exercise_submissions) == 2


class TestTransactionOperations:
    """Test database transaction handling"""
    
    @pytest.fixture
    async def db(self):
        database = MockDatabase()
        await database.connect()
        yield database
        await database.disconnect()
    
    @pytest.mark.asyncio
    async def test_successful_transaction(self, db):
        """Test successful transaction commit"""
        await db.begin_transaction()
        
        try:
            # Perform operations within transaction
            user = await db.create_user("transuser", "trans@example.com", "hash")
            exercise = await db.create_exercise("Trans Exercise", "Desc", "beginner", "basics")
            
            # Commit transaction
            await db.commit_transaction()
            
            # Verify data persisted
            retrieved_user = await db.get_user_by_id(user['id'])
            retrieved_exercise = await db.get_exercise_by_id(exercise['id'])
            
            assert retrieved_user is not None
            assert retrieved_exercise is not None
            
        except Exception:
            await db.rollback_transaction()
            raise
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, db):
        """Test transaction rollback"""
        # Count initial users
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        initial_count = cursor.fetchone()[0]
        
        await db.begin_transaction()
        
        try:
            # Create user within transaction
            await db.create_user("rollbackuser", "rollback@example.com", "hash")
            
            # Simulate error and rollback
            raise Exception("Simulated error")
            
        except Exception:
            await db.rollback_transaction()
        
        # Verify user was not persisted
        cursor.execute("SELECT COUNT(*) FROM users")
        final_count = cursor.fetchone()[0]
        
        assert final_count == initial_count
    
    @pytest.mark.asyncio
    async def test_nested_transaction_error(self, db):
        """Test error handling for nested transactions"""
        await db.begin_transaction()
        
        # Try to begin another transaction
        with pytest.raises(Exception, match="Transaction already active"):
            await db.begin_transaction()
        
        await db.rollback_transaction()
    
    @pytest.mark.asyncio
    async def test_commit_without_transaction(self, db):
        """Test error when committing without active transaction"""
        with pytest.raises(Exception, match="No active transaction"):
            await db.commit_transaction()


class TestSessionManagement:
    """Test session management operations"""
    
    @pytest.fixture
    async def db_with_user(self):
        db = MockDatabase()
        await db.connect()
        
        user = await db.create_user("sessionuser", "session@example.com", "hash")
        
        yield db, user
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_create_and_retrieve_session(self, db_with_user):
        """Test session creation and retrieval"""
        db, user = db_with_user
        
        session_id = "session_123"
        expires_at = datetime.now() + timedelta(hours=24)
        
        # Create session
        await db.create_session(session_id, user['id'], expires_at)
        
        # Retrieve session
        session = await db.get_session(session_id)
        
        assert session is not None
        assert session['id'] == session_id
        assert session['user_id'] == user['id']
        assert session['is_active'] == 1
    
    @pytest.mark.asyncio
    async def test_expired_session_not_retrieved(self, db_with_user):
        """Test that expired sessions are not retrieved"""
        db, user = db_with_user
        
        session_id = "expired_session"
        expires_at = datetime.now() - timedelta(hours=1)  # Already expired
        
        # Create expired session
        await db.create_session(session_id, user['id'], expires_at)
        
        # Try to retrieve expired session
        session = await db.get_session(session_id)
        
        assert session is None
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, db_with_user):
        """Test cleanup of expired sessions"""
        db, user = db_with_user
        
        # Create mix of active and expired sessions
        active_expires = datetime.now() + timedelta(hours=24)
        expired_expires = datetime.now() - timedelta(hours=1)
        
        await db.create_session("active_session", user['id'], active_expires)
        await db.create_session("expired_session_1", user['id'], expired_expires)
        await db.create_session("expired_session_2", user['id'], expired_expires)
        
        # Clean up expired sessions
        deleted_count = await db.cleanup_expired_sessions()
        
        assert deleted_count == 2
        
        # Verify active session still exists
        active_session = await db.get_session("active_session")
        assert active_session is not None
        
        # Verify expired sessions are gone
        expired_session = await db.get_session("expired_session_1")
        assert expired_session is None


class TestDataIntegrity:
    """Test data integrity and constraints"""
    
    @pytest.fixture
    async def db(self):
        database = MockDatabase()
        await database.connect()
        yield database
        await database.disconnect()
    
    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self, db):
        """Test foreign key constraint enforcement"""
        # Create user and exercise
        user = await db.create_user("fkuser", "fk@example.com", "hash")
        exercise = await db.create_exercise("FK Exercise", "Desc", "beginner", "basics")
        
        # Valid submission should work
        submission = await db.create_submission(user['id'], exercise['id'], "code")
        assert submission is not None
        
        # Submission with invalid exercise should fail
        with pytest.raises(ValueError, match="Exercise not found"):
            await db.create_submission(user['id'], 99999, "code")
    
    @pytest.mark.asyncio
    async def test_unique_constraints(self, db):
        """Test unique constraint enforcement"""
        # Create first user
        await db.create_user("unique1", "unique1@example.com", "hash1")
        
        # Try to create user with same username
        with pytest.raises(ValueError):
            await db.create_user("unique1", "different@example.com", "hash2")
        
        # Try to create user with same email
        with pytest.raises(ValueError):
            await db.create_user("different", "unique1@example.com", "hash3")
    
    @pytest.mark.asyncio
    async def test_progress_consistency(self, db):
        """Test progress tracking consistency"""
        # Create user and multiple exercises
        user = await db.create_user("proguser", "prog@example.com", "hash")
        
        exercises = []
        for i in range(3):
            exercise = await db.create_exercise(f"Exercise {i}", "Desc", "beginner", "basics", 10)
            exercises.append(exercise)
        
        # Complete exercises one by one and check progress consistency
        for i, exercise in enumerate(exercises):
            submission = await db.create_submission(user['id'], exercise['id'], "code")
            await db.update_submission(submission['id'], score=85, status='completed')
            
            progress = await db.get_user_progress(user['id'])
            expected_completed = i + 1
            expected_points = expected_completed * 10
            
            assert progress['topics']['basics']['completed'] == expected_completed
            assert progress['total_points'] == expected_points
    
    @pytest.mark.asyncio
    async def test_duplicate_successful_submissions(self, db):
        """Test that duplicate successful submissions don't double-count progress"""
        user = await db.create_user("dupuser", "dup@example.com", "hash")
        exercise = await db.create_exercise("Dup Exercise", "Desc", "beginner", "basics", 15)
        
        # Submit multiple times
        submission1 = await db.create_submission(user['id'], exercise['id'], "code1")
        submission2 = await db.create_submission(user['id'], exercise['id'], "code2")
        
        # Complete both with passing scores
        await db.update_submission(submission1['id'], score=85, status='completed')
        await db.update_submission(submission2['id'], score=90, status='completed')
        
        # Progress should only count it once
        progress = await db.get_user_progress(user['id'])
        assert progress['topics']['basics']['completed'] == 1
        assert progress['total_points'] == 15  # Only counted once


class TestPerformanceAndScaling:
    """Test database performance with larger datasets"""
    
    @pytest.fixture
    async def db(self):
        database = MockDatabase()
        await database.connect()
        yield database
        await database.disconnect()
    
    @pytest.mark.asyncio
    async def test_bulk_user_creation(self, db):
        """Test creating many users efficiently"""
        import time
        
        start_time = time.time()
        
        # Create many users
        users = []
        for i in range(100):
            user = await db.create_user(f"bulkuser{i}", f"bulk{i}@example.com", "hash")
            users.append(user)
        
        creation_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert creation_time < 30.0  # Adjust based on system performance
        assert len(users) == 100
        
        # Verify data integrity
        random_user = users[50]
        retrieved = await db.get_user_by_id(random_user['id'])
        assert retrieved['username'] == f"bulkuser50"
    
    @pytest.mark.asyncio
    async def test_large_exercise_queries(self, db):
        """Test querying large numbers of exercises"""
        # Create many exercises across different topics
        topics = ['basics', 'oop', 'advanced', 'data_structures', 'algorithms']
        difficulties = ['beginner', 'intermediate', 'advanced']
        
        for topic in topics:
            for difficulty in difficulties:
                for i in range(20):  # 20 exercises per topic/difficulty combination
                    await db.create_exercise(
                        f"{topic} {difficulty} {i}",
                        f"Description for {topic} {difficulty} exercise {i}",
                        difficulty,
                        topic,
                        10
                    )
        
        # Test various queries
        import time
        
        start_time = time.time()
        
        # Query all exercises
        all_exercises = await db.get_exercises(limit=1000)
        
        # Query by topic
        basics_exercises = await db.get_exercises(topic='basics', limit=100)
        
        # Query by difficulty
        beginner_exercises = await db.get_exercises(difficulty='beginner', limit=100)
        
        query_time = time.time() - start_time
        
        # Queries should be fast even with many exercises
        assert query_time < 5.0
        assert all_exercises['total'] == 300  # 5 topics × 3 difficulties × 20 exercises
        assert basics_exercises['total'] == 60  # 3 difficulties × 20 exercises
        assert beginner_exercises['total'] == 100  # 5 topics × 20 exercises
    
    @pytest.mark.asyncio
    async def test_concurrent_database_operations(self, db):
        """Test concurrent database operations"""
        import asyncio
        
        async def create_user_and_submissions(user_num):
            """Create user and some submissions"""
            user = await db.create_user(f"concurrent{user_num}", f"conc{user_num}@example.com", "hash")
            
            # Create exercise for this user
            exercise = await db.create_exercise(f"Exercise for user {user_num}", "Desc", "beginner", "basics")
            
            # Create multiple submissions
            for i in range(5):
                submission = await db.create_submission(user['id'], exercise['id'], f"code{i}")
                await db.update_submission(submission['id'], score=80, status='completed')
            
            return user
        
        # Run multiple operations concurrently
        tasks = [create_user_and_submissions(i) for i in range(10)]
        users = await asyncio.gather(*tasks)
        
        # Verify all operations completed successfully
        assert len(users) == 10
        
        # Verify data consistency
        for user in users:
            progress = await db.get_user_progress(user['id'])
            # Each user should have completed 5 exercises
            assert progress['topics']['basics']['completed'] == 5
    
    @pytest.mark.asyncio
    async def test_database_cleanup_performance(self, db):
        """Test performance of cleanup operations"""
        import time
        
        # Create many expired sessions
        user = await db.create_user("cleanupuser", "cleanup@example.com", "hash")
        expired_time = datetime.now() - timedelta(hours=1)
        
        # Create many expired sessions
        for i in range(1000):
            await db.create_session(f"expired_{i}", user['id'], expired_time)
        
        # Measure cleanup time
        start_time = time.time()
        deleted_count = await db.cleanup_expired_sessions()
        cleanup_time = time.time() - start_time
        
        # Cleanup should be efficient
        assert cleanup_time < 5.0
        assert deleted_count == 1000


class TestDatabaseMigrationSimulation:
    """Test database schema changes and migrations"""
    
    @pytest.fixture
    async def db(self):
        database = MockDatabase()
        await database.connect()
        yield database
        await database.disconnect()
    
    @pytest.mark.asyncio
    async def test_adding_new_column(self, db):
        """Test adding a new column to existing table"""
        # Add data to existing schema
        user = await db.create_user("migrateuser", "migrate@example.com", "hash")
        
        # Simulate adding new column
        cursor = db.connection.cursor()
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
        db.connection.commit()
        
        # Verify existing data still accessible
        retrieved_user = await db.get_user_by_id(user['id'])
        assert retrieved_user['username'] == "migrateuser"
        
        # New column should exist with NULL value
        assert 'last_login' in retrieved_user
        assert retrieved_user['last_login'] is None
    
    @pytest.mark.asyncio
    async def test_creating_new_table(self, db):
        """Test creating a new table in existing database"""
        # Create new table
        cursor = db.connection.cursor()
        cursor.execute('''
            CREATE TABLE achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_name TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        db.connection.commit()
        
        # Use new table
        user = await db.create_user("achieveuser", "achieve@example.com", "hash")
        
        cursor.execute('''
            INSERT INTO achievements (user_id, achievement_name)
            VALUES (?, ?)
        ''', (user['id'], "First Login"))
        db.connection.commit()
        
        # Verify data in new table
        cursor.execute("SELECT * FROM achievements WHERE user_id = ?", (user['id'],))
        achievement = cursor.fetchone()
        
        assert achievement is not None
        assert achievement[2] == "First Login"  # achievement_name column
    
    @pytest.mark.asyncio
    async def test_data_migration_simulation(self, db):
        """Test simulating data migration"""
        # Create some users with old format
        users = []
        for i in range(5):
            user = await db.create_user(f"olduser{i}", f"old{i}@example.com", "hash")
            users.append(user)
        
        # Simulate migration: update all users to have a standardized email domain
        cursor = db.connection.cursor()
        
        for user in users:
            new_email = f"migrated{user['id']}@newdomain.com"
            cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user['id']))
        
        db.connection.commit()
        
        # Verify migration worked
        for user in users:
            updated_user = await db.get_user_by_id(user['id'])
            assert updated_user['email'] == f"migrated{user['id']}@newdomain.com"


class TestDatabaseBackupAndRestore:
    """Test database backup and restore functionality"""
    
    @pytest.mark.asyncio
    async def test_database_backup_simulation(self):
        """Test database backup simulation"""
        # Create temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            db_path = temp_db.name
        
        try:
            # Create database with data
            db = MockDatabase(db_path)
            await db.connect()
            
            # Add test data
            user = await db.create_user("backupuser", "backup@example.com", "hash")
            exercise = await db.create_exercise("Backup Exercise", "Desc", "beginner", "basics")
            submission = await db.create_submission(user['id'], exercise['id'], "backup code")
            
            await db.disconnect()
            
            # Verify backup file exists and has data
            assert os.path.exists(db_path)
            assert os.path.getsize(db_path) > 0
            
            # Simulate restore by connecting to backup
            restore_db = MockDatabase(db_path)
            await restore_db.connect()
            
            # Verify data was restored
            restored_user = await restore_db.get_user_by_username("backupuser")
            assert restored_user is not None
            assert restored_user['email'] == "backup@example.com"
            
            restored_exercise = await restore_db.get_exercise_by_id(exercise['id'])
            assert restored_exercise is not None
            assert restored_exercise['title'] == "Backup Exercise"
            
            restored_submission = await restore_db.get_submission_by_id(submission['id'])
            assert restored_submission is not None
            assert restored_submission['code'] == "backup code"
            
            await restore_db.disconnect()
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(db_path)
            except FileNotFoundError:
                pass
    
    @pytest.mark.asyncio
    async def test_database_corruption_recovery(self):
        """Test recovery from database corruption"""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            db_path = temp_db.name
        
        try:
            # Create database with data
            db = MockDatabase(db_path)
            await db.connect()
            
            user = await db.create_user("corruptuser", "corrupt@example.com", "hash")
            await db.disconnect()
            
            # Simulate corruption by truncating file
            with open(db_path, 'w') as f:
                f.write("corrupted data")
            
            # Try to connect to corrupted database
            corrupt_db = MockDatabase(db_path)
            
            # This should fail due to corruption
            with pytest.raises(Exception):
                await corrupt_db.connect()
            
        finally:
            try:
                os.unlink(db_path)
            except FileNotFoundError:
                pass


class TestDatabaseConnectionPooling:
    """Test database connection pooling simulation"""
    
    @pytest.mark.asyncio
    async def test_connection_pool_simulation(self):
        """Test connection pool behavior simulation"""
        db = MockDatabase()
        
        # Simulate multiple connections
        connections = []
        for i in range(5):
            conn = await db.connect()
            connections.append(conn)
            # In real implementation, connections would be pooled
            db.connection_pool.append(conn)
        
        # Verify pool size
        assert len(db.connection_pool) == 5
        
        # Simulate connection reuse
        assert len(db.connection_pool) <= db.max_connections
        
        # Clean up
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_connection_limit_handling(self):
        """Test handling of connection limits"""
        db = MockDatabase()
        db.max_connections = 3
        
        # This is a simplified test - real connection pooling would be more complex
        # For now, just verify the limit is respected in our mock
        assert db.max_connections == 3
        
        # In a real implementation, this would test:
        # - Connection queue when limit is reached
        # - Connection timeout handling
        # - Connection recycling
        # - Error handling when pool is exhausted