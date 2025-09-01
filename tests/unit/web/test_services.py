# tests/unit/web/test_services.py
"""
Test module for web application services.
Tests business logic, service layer functionality, and data processing.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Optional
import asyncio


class MockUserService:
    """Mock User service for testing"""
    
    def __init__(self):
        self._users = {}
        self._next_id = 1
    
    async def create_user(self, username, email, password, role='student'):
        """Create a new user"""
        # Check if username/email already exists
        for user in self._users.values():
            if user['username'] == username:
                raise ValueError("Username already exists")
            if user['email'] == email:
                raise ValueError("Email already exists")
        
        user_id = self._next_id
        self._next_id += 1
        
        user = {
            'id': user_id,
            'username': username,
            'email': email,
            'password_hash': f"hashed_{password}",
            'role': role,
            'created_at': datetime.now(),
            'is_active': True,
            'last_login': None
        }
        
        self._users[user_id] = user
        return user
    
    async def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        for user in self._users.values():
            if user['username'] == username and user['password_hash'] == f"hashed_{password}":
                user['last_login'] = datetime.now()
                return user
        return None
    
    async def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self._users.get(user_id)
    
    async def get_user_by_username(self, username):
        """Get user by username"""
        for user in self._users.values():
        
            if user['username'] == username:
                return user
        return None
    
    async def update_user(self, user_id, **updates):
        """Update user information"""
        if user_id not in self._users:
            raise ValueError("User not found")
        
        user = self._users[user_id]
        user.update(updates)
        user['updated_at'] = datetime.now()
        return user
    
    async def deactivate_user(self, user_id):
        """Deactivate user account"""
        if user_id not in self._users:
            raise ValueError("User not found")
        
        self._users[user_id]['is_active'] = False
        return True
    
    async def get_user_stats(self, user_id):
        """Get user statistics"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return {
            'user_id': user_id,
            'exercises_completed': 25,
            'total_points': 500,
            'current_streak': 7,
            'rank': 42,
            'join_date': user['created_at'],
            'last_activity': user.get('last_login', user['created_at'])
        }


class MockExerciseService:
    """Mock Exercise service for testing"""
    
    def __init__(self):
        self._exercises = {}
        self._next_id = 1
        self._submissions = {}
        self._submission_id = 1
    
    async def create_exercise(self, title, description, difficulty, topic, points=10):
        """Create a new exercise"""
        exercise_id = self._next_id
        self._next_id += 1
        
        exercise = {
            'id': exercise_id,
            'title': title,
            'description': description,
            'difficulty': difficulty,
            'topic': topic,
            'points': points,
            'created_at': datetime.now(),
            'is_active': True,
            'test_cases': [],
            'solution_template': '',
            'hints': []
        }
        
        self._exercises[exercise_id] = exercise
        return exercise
    
    async def get_exercise_by_id(self, exercise_id):
        """Get exercise by ID"""
        return self._exercises.get(exercise_id)
    
    async def get_exercises(self, topic=None, difficulty=None, limit=10, offset=0):
        """Get exercises with optional filtering"""
        exercises = list(self._exercises.values())
        
        # Apply filters
        if topic:
            exercises = [ex for ex in exercises if ex['topic'] == topic]
        if difficulty:
            exercises = [ex for ex in exercises if ex['difficulty'] == difficulty]
        
        # Apply pagination
        total = len(exercises)
        exercises = exercises[offset:offset + limit]
        
        return {
            'exercises': exercises,
            'total': total,
            'page': (offset // limit) + 1,
            'per_page': limit
        }
    
    async def submit_solution(self, user_id, exercise_id, code, language='python'):
        """Submit solution for an exercise"""
        exercise = await self.get_exercise_by_id(exercise_id)
        if not exercise:
            raise ValueError("Exercise not found")
        
        submission_id = self._submission_id
        self._submission_id += 1
        
        submission = {
            'id': submission_id,
            'user_id': user_id,
            'exercise_id': exercise_id,
            'code': code,
            'language': language,
            'status': 'pending',
            'submitted_at': datetime.now(),
            'score': None,
            'feedback': None,
            'test_results': []
        }
        
        self._submissions[submission_id] = submission
        
        # Simulate processing
        await self._process_submission(submission_id)
        
        return self._submissions[submission_id]
    
    async def _process_submission(self, submission_id):
        """Process submission (mock evaluation)"""
        submission = self._submissions[submission_id]
        submission['status'] = 'running'
        
        # Simulate test execution
        await asyncio.sleep(0.1)  # Mock processing time
        
        # Mock test results
        test_results = [
            {'test_case': 1, 'passed': True, 'output': 'correct'},
            {'test_case': 2, 'passed': True, 'output': 'correct'},
            {'test_case': 3, 'passed': False, 'output': 'incorrect', 'error': 'AssertionError'}
        ]
        
        submission['test_results'] = test_results
        submission['score'] = sum(1 for result in test_results if result['passed']) / len(test_results) * 100
        submission['feedback'] = "Good attempt! Check edge cases."
        submission['status'] = 'completed'
        submission['completed_at'] = datetime.now()
    
    async def get_user_submissions(self, user_id, exercise_id=None):
        """Get user submissions"""
        submissions = [
            sub for sub in self._submissions.values() 
            if sub['user_id'] == user_id
        ]
        
        if exercise_id:
            submissions = [sub for sub in submissions if sub['exercise_id'] == exercise_id]
        
        return submissions
    
    async def get_exercise_statistics(self, exercise_id):
        """Get exercise statistics"""
        exercise = await self.get_exercise_by_id(exercise_id)
        if not exercise:
            raise ValueError("Exercise not found")
        
        submissions = [
            sub for sub in self._submissions.values() 
            if sub['exercise_id'] == exercise_id and sub['status'] == 'completed'
        ]
        
        if not submissions:
            return {
                'exercise_id': exercise_id,
                'total_submissions': 0,
                'average_score': 0,
                'completion_rate': 0
            }
        
        total_submissions = len(submissions)
        average_score = sum(sub['score'] for sub in submissions) / total_submissions
        completion_rate = sum(1 for sub in submissions if sub['score'] >= 70) / total_submissions * 100
        
        return {
            'exercise_id': exercise_id,
            'total_submissions': total_submissions,
            'average_score': round(average_score, 2),
            'completion_rate': round(completion_rate, 2)
        }


class MockProgressService:
    """Mock Progress service for testing"""
    
    def __init__(self):
        self._progress = {}
    
    async def get_user_progress(self, user_id):
        """Get comprehensive user progress"""
        if user_id not in self._progress:
            # Initialize progress for new user
            self._progress[user_id] = {
                'user_id': user_id,
                'overall_progress': 0.0,
                'topics': {
                    'basics': {'completed': 0, 'total': 20, 'points': 0},
                    'oop': {'completed': 0, 'total': 15, 'points': 0},
                    'advanced': {'completed': 0, 'total': 10, 'points': 0}
                },
                'total_points': 0,
                'current_level': 1,
                'streak_days': 0,
                'last_activity': datetime.now(),
                'achievements': []
            }
        
        progress = self._progress[user_id]
        
        # Calculate overall progress
        total_completed = sum(topic['completed'] for topic in progress['topics'].values())
        total_exercises = sum(topic['total'] for topic in progress['topics'].values())
        progress['overall_progress'] = (total_completed / total_exercises) * 100 if total_exercises > 0 else 0
        
        return progress
    
    async def update_progress(self, user_id, exercise_topic, exercise_points, score):
        """Update user progress after exercise completion"""
        progress = await self.get_user_progress(user_id)
        
        if exercise_topic in progress['topics']:
            topic_progress = progress['topics'][exercise_topic]
            topic_progress['completed'] += 1
            topic_progress['points'] += exercise_points
            
            progress['total_points'] += exercise_points
            progress['last_activity'] = datetime.now()
            
            # Update level based on points
            progress['current_level'] = min(progress['total_points'] // 100 + 1, 10)
            
            # Check for achievements
            await self._check_achievements(user_id, progress)
        
        return progress
    
    async def _check_achievements(self, user_id, progress):
        """Check and award achievements"""
        achievements = progress['achievements']
        
        # First exercise achievement
        if progress['total_points'] >= 10 and 'first_exercise' not in [a['type'] for a in achievements]:
            achievements.append({
                'type': 'first_exercise',
                'title': 'First Steps',
                'description': 'Completed your first exercise',
                'earned_at': datetime.now()
            })
        
        # Topic completion achievements
        for topic, topic_data in progress['topics'].items():
            achievement_type = f'{topic}_master'
            if (topic_data['completed'] >= topic_data['total'] and 
                achievement_type not in [a['type'] for a in achievements]):
                achievements.append({
                    'type': achievement_type,
                    'title': f'{topic.title()} Master',
                    'description': f'Completed all {topic} exercises',
                    'earned_at': datetime.now()
                })
    
    async def get_leaderboard(self, limit=10):
        """Get user leaderboard"""
        users_progress = []
        
        for user_id, progress in self._progress.items():
            users_progress.append({
                'user_id': user_id,
                'username': f'user_{user_id}',  # Mock username
                'total_points': progress['total_points'],
                'level': progress['current_level'],
                'overall_progress': progress['overall_progress']
            })
        
        # Sort by points (descending)
        users_progress.sort(key=lambda x: x['total_points'], reverse=True)
        
        # Add ranks
        for i, user in enumerate(users_progress):
            user['rank'] = i + 1
        
        return users_progress[:limit]
    
    async def get_user_achievements(self, user_id):
        """Get user achievements"""
        progress = await self.get_user_progress(user_id)
        return progress['achievements']


class MockNotificationService:
    """Mock Notification service for testing"""
    
    def __init__(self):
        self._notifications = {}
        self._next_id = 1
    
    async def send_notification(self, user_id, title, message, notification_type='info'):
        """Send notification to user"""
        notification_id = self._next_id
        self._next_id += 1
        
        notification = {
            'id': notification_id,
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'created_at': datetime.now(),
            'read': False
        }
        
        if user_id not in self._notifications:
            self._notifications[user_id] = []
        
        self._notifications[user_id].append(notification)
        return notification
    
    async def get_user_notifications(self, user_id, unread_only=False):
        """Get user notifications"""
        user_notifications = self._notifications.get(user_id, [])
        
        if unread_only:
            user_notifications = [n for n in user_notifications if not n['read']]
        
        return sorted(user_notifications, key=lambda x: x['created_at'], reverse=True)
    
    async def mark_as_read(self, user_id, notification_id):
        """Mark notification as read"""
        user_notifications = self._notifications.get(user_id, [])
        
        for notification in user_notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                return True
        
        return False
    
    async def mark_all_as_read(self, user_id):
        """Mark all notifications as read for user"""
        user_notifications = self._notifications.get(user_id, [])
        
        for notification in user_notifications:
            notification['read'] = True
        
        return len(user_notifications)


class TestUserService:
    """Test User service functionality"""
    
    @pytest.fixture
    def user_service(self):
        return MockUserService()
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_service):
        """Test user creation"""
        user = await user_service.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        assert user['username'] == "testuser"
        assert user['email'] == "test@example.com"
        assert user['password_hash'] == "hashed_password123"
        assert user['role'] == "student"
        assert user['is_active'] is True
    
    @pytest.mark.asyncio
    async def test_create_duplicate_user(self, user_service):
        """Test creating user with duplicate username"""
        await user_service.create_user("testuser", "test1@example.com", "password123")
        
        with pytest.raises(ValueError, match="Username already exists"):
            await user_service.create_user("testuser", "test2@example.com", "password456")
    
    @pytest.mark.asyncio
    async def test_create_duplicate_email(self, user_service):
        """Test creating user with duplicate email"""
        await user_service.create_user("user1", "test@example.com", "password123")
        
        with pytest.raises(ValueError, match="Email already exists"):
            await user_service.create_user("user2", "test@example.com", "password456")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, user_service):
        """Test successful user authentication"""
        await user_service.create_user("testuser", "test@example.com", "password123")
        
        user = await user_service.authenticate_user("testuser", "password123")
        
        assert user is not None
        assert user['username'] == "testuser"
        assert user['last_login'] is not None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_failure(self, user_service):
        """Test failed user authentication"""
        await user_service.create_user("testuser", "test@example.com", "password123")
        
        # Wrong password
        user = await user_service.authenticate_user("testuser", "wrongpassword")
        assert user is None
        
        # Wrong username
        user = await user_service.authenticate_user("wronguser", "password123")
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_service):
        """Test getting user by ID"""
        created_user = await user_service.create_user("testuser", "test@example.com", "password123")
        user_id = created_user['id']
        
        user = await user_service.get_user_by_id(user_id)
        
        assert user is not None
        assert user['id'] == user_id
        assert user['username'] == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_user_by_username(self, user_service):
        """Test getting user by username"""
        await user_service.create_user("testuser", "test@example.com", "password123")
        
        user = await user_service.get_user_by_username("testuser")
        
        assert user is not None
        assert user['username'] == "testuser"
        assert user['email'] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_update_user(self, user_service):
        """Test updating user information"""
        created_user = await user_service.create_user("testuser", "test@example.com", "password123")
        user_id = created_user['id']
        
        updated_user = await user_service.update_user(
            user_id,
            email="newemail@example.com",
            role="instructor"
        )
        
        assert updated_user['email'] == "newemail@example.com"
        assert updated_user['role'] == "instructor"
        assert 'updated_at' in updated_user
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_user(self, user_service):
        """Test updating non-existent user"""
        with pytest.raises(ValueError, match="User not found"):
            await user_service.update_user(999, email="test@example.com")
    
    @pytest.mark.asyncio
    async def test_deactivate_user(self, user_service):
        """Test user deactivation"""
        created_user = await user_service.create_user("testuser", "test@example.com", "password123")
        user_id = created_user['id']
        
        result = await user_service.deactivate_user(user_id)
        assert result is True
        
        user = await user_service.get_user_by_id(user_id)
        assert user['is_active'] is False
    
    @pytest.mark.asyncio
    async def test_get_user_stats(self, user_service):
        """Test getting user statistics"""
        created_user = await user_service.create_user("testuser", "test@example.com", "password123")
        user_id = created_user['id']
        
        stats = await user_service.get_user_stats(user_id)
        
        assert stats['user_id'] == user_id
        assert 'exercises_completed' in stats
        assert 'total_points' in stats
        assert 'current_streak' in stats
        assert 'rank' in stats


class TestExerciseService:
    """Test Exercise service functionality"""
    
    @pytest.fixture
    def exercise_service(self):
        return MockExerciseService()
    
    @pytest.mark.asyncio
    async def test_create_exercise(self, exercise_service):
        """Test exercise creation"""
        exercise = await exercise_service.create_exercise(
            title="Hello World",
            description="Print Hello World",
            difficulty="beginner",
            topic="basics",
            points=15
        )
        
        assert exercise['title'] == "Hello World"
        assert exercise['description'] == "Print Hello World"
        assert exercise['difficulty'] == "beginner"
        assert exercise['topic'] == "basics"
        assert exercise['points'] == 15
        assert exercise['is_active'] is True
    
    @pytest.mark.asyncio
    async def test_get_exercise_by_id(self, exercise_service):
        """Test getting exercise by ID"""
        created_exercise = await exercise_service.create_exercise(
            "Test Exercise", "Test Description", "beginner", "basics"
        )
        exercise_id = created_exercise['id']
        
        exercise = await exercise_service.get_exercise_by_id(exercise_id)
        
        assert exercise is not None
        assert exercise['id'] == exercise_id
        assert exercise['title'] == "Test Exercise"
    
    @pytest.mark.asyncio
    async def test_get_exercises_no_filter(self, exercise_service):
        """Test getting exercises without filters"""
        # Create multiple exercises
        await exercise_service.create_exercise("Exercise 1", "Desc 1", "beginner", "basics")
        await exercise_service.create_exercise("Exercise 2", "Desc 2", "intermediate", "oop")
        await exercise_service.create_exercise("Exercise 3", "Desc 3", "advanced", "basics")
        
        result = await exercise_service.get_exercises()
        
        assert len(result['exercises']) == 3
        assert result['total'] == 3
        assert result['page'] == 1
        assert result['per_page'] == 10
    
    @pytest.mark.asyncio
    async def test_get_exercises_with_topic_filter(self, exercise_service):
        """Test getting exercises with topic filter"""
        await exercise_service.create_exercise("Exercise 1", "Desc 1", "beginner", "basics")
        await exercise_service.create_exercise("Exercise 2", "Desc 2", "intermediate", "oop")
        await exercise_service.create_exercise("Exercise 3", "Desc 3", "advanced", "basics")
        
        result = await exercise_service.get_exercises(topic="basics")
        
        assert len(result['exercises']) == 2
        assert all(ex['topic'] == "basics" for ex in result['exercises'])
    
    @pytest.mark.asyncio
    async def test_get_exercises_with_difficulty_filter(self, exercise_service):
        """Test getting exercises with difficulty filter"""
        await exercise_service.create_exercise("Exercise 1", "Desc 1", "beginner", "basics")
        await exercise_service.create_exercise("Exercise 2", "Desc 2", "intermediate", "oop")
        await exercise_service.create_exercise("Exercise 3", "Desc 3", "beginner", "basics")
        
        result = await exercise_service.get_exercises(difficulty="beginner")
        
        assert len(result['exercises']) == 2
        assert all(ex['difficulty'] == "beginner" for ex in result['exercises'])
    
    @pytest.mark.asyncio
    async def test_get_exercises_pagination(self, exercise_service):
        """Test exercise pagination"""
        # Create multiple exercises
        for i in range(5):
            await exercise_service.create_exercise(f"Exercise {i}", f"Desc {i}", "beginner", "basics")
        
        result = await exercise_service.get_exercises(limit=2, offset=0)
        assert len(result['exercises']) == 2
        assert result['page'] == 1
        
        result = await exercise_service.get_exercises(limit=2, offset=2)
        assert len(result['exercises']) == 2
        assert result['page'] == 2
    
    @pytest.mark.asyncio
    async def test_submit_solution(self, exercise_service):
        """Test solution submission"""
        exercise = await exercise_service.create_exercise(
            "Test Exercise", "Test Description", "beginner", "basics"
        )
        
        submission = await exercise_service.submit_solution(
            user_id=123,
            exercise_id=exercise['id'],
            code="print('Hello, World!')",
            language="python"
        )
        
        assert submission['user_id'] == 123
        assert submission['exercise_id'] == exercise['id']
        assert submission['code'] == "print('Hello, World!')"
        assert submission['language'] == "python"
        assert submission['status'] == 'completed'
        assert submission['score'] is not None
    
    @pytest.mark.asyncio
    async def test_submit_solution_invalid_exercise(self, exercise_service):
        """Test submitting solution for invalid exercise"""
        with pytest.raises(ValueError, match="Exercise not found"):
            await exercise_service.submit_solution(
                user_id=123,
                exercise_id=999,
                code="test code",
                language="python"
            )
    
    @pytest.mark.asyncio
    async def test_get_user_submissions(self, exercise_service):
        """Test getting user submissions"""
        exercise = await exercise_service.create_exercise(
            "Test Exercise", "Test Description", "beginner", "basics"
        )
        
        # Submit solutions
        await exercise_service.submit_solution(123, exercise['id'], "code1", "python")
        await exercise_service.submit_solution(123, exercise['id'], "code2", "python")
        await exercise_service.submit_solution(456, exercise['id'], "code3", "python")
        
        user_submissions = await exercise_service.get_user_submissions(123)
        
        assert len(user_submissions) == 2
        assert all(sub['user_id'] == 123 for sub in user_submissions)
    
    @pytest.mark.asyncio
    async def test_get_exercise_statistics(self, exercise_service):
        """Test getting exercise statistics"""
        exercise = await exercise_service.create_exercise(
            "Test Exercise", "Test Description", "beginner", "basics"
        )
        
        # Submit multiple solutions
        await exercise_service.submit_solution(123, exercise['id'], "code1", "python")
        await exercise_service.submit_solution(456, exercise['id'], "code2", "python")
        
        stats = await exercise_service.get_exercise_statistics(exercise['id'])
        
        assert stats['exercise_id'] == exercise['id']
        assert stats['total_submissions'] == 2
        assert 'average_score' in stats
        assert 'completion_rate' in stats


class TestProgressService:
    """Test Progress service functionality"""
    
    @pytest.fixture
    def progress_service(self):
        return MockProgressService()
    
    @pytest.mark.asyncio
    async def test_get_user_progress_new_user(self, progress_service):
        """Test getting progress for new user"""
        progress = await progress_service.get_user_progress(123)
        
        assert progress['user_id'] == 123
        assert progress['overall_progress'] == 0.0
        assert 'topics' in progress
        assert 'basics' in progress['topics']
        assert 'oop' in progress['topics']
        assert 'advanced' in progress['topics']
        assert progress['current_level'] == 1
        assert progress['total_points'] == 0
    
    @pytest.mark.asyncio
    async def test_update_progress(self, progress_service):
        """Test updating user progress"""
        user_id = 123
        
        # Get initial progress
        initial_progress = await progress_service.get_user_progress(user_id)
        assert initial_progress['topics']['basics']['completed'] == 0
        
        # Update progress
        updated_progress = await progress_service.update_progress(
            user_id, 'basics', 15, 85
        )
        
        assert updated_progress['topics']['basics']['completed'] == 1
        assert updated_progress['topics']['basics']['points'] == 15
        assert updated_progress['total_points'] == 15
        assert updated_progress['current_level'] == 1
    
    @pytest.mark.asyncio
    async def test_level_progression(self, progress_service):
        """Test user level progression"""
        user_id = 123
        
        # Update progress multiple times to gain points
        for _ in range(12):  # 12 * 15 = 180 points
            await progress_service.update_progress(user_id, 'basics', 15, 85)
        
        progress = await progress_service.get_user_progress(user_id)
        
        assert progress['total_points'] == 180
        assert progress['current_level'] == 2  # 180 // 100 + 1 = 2
    
    @pytest.mark.asyncio
    async def test_achievements(self, progress_service):
        """Test achievement system"""
        user_id = 123
        
        # Complete first exercise to trigger achievement
        await progress_service.update_progress(user_id, 'basics', 15, 85)
        
        progress = await progress_service.get_user_progress(user_id)
        
        # Should have first exercise achievement
        achievements = progress['achievements']
        assert len(achievements) > 0
        assert any(a['type'] == 'first_exercise' for a in achievements)
    
    @pytest.mark.asyncio
    async def test_topic_master_achievement(self, progress_service):
        """Test topic master achievement"""
        user_id = 123
        
        # Complete all basics exercises
        for _ in range(20):  # Complete all 20 basics exercises
            await progress_service.update_progress(user_id, 'basics', 10, 85)
        
        progress = await progress_service.get_user_progress(user_id)
        achievements = progress['achievements']
        
        # Should have basics master achievement
        assert any(a['type'] == 'basics_master' for a in achievements)
    
    @pytest.mark.asyncio
    async def test_get_leaderboard(self, progress_service):
        """Test leaderboard functionality"""
        # Create progress for multiple users
        await progress_service.update_progress(123, 'basics', 50, 85)  # 50 points
        await progress_service.update_progress(456, 'basics', 100, 90)  # 100 points
        await progress_service.update_progress(789, 'basics', 75, 80)   # 75 points
        
        leaderboard = await progress_service.get_leaderboard(limit=3)
        
        assert len(leaderboard) == 3
        
        # Should be sorted by points (descending)
        assert leaderboard[0]['total_points'] >= leaderboard[1]['total_points']
        assert leaderboard[1]['total_points'] >= leaderboard[2]['total_points']
        
        # Check ranks
        assert leaderboard[0]['rank'] == 1
        assert leaderboard[1]['rank'] == 2
        assert leaderboard[2]['rank'] == 3
    
    @pytest.mark.asyncio
    async def test_get_user_achievements(self, progress_service):
        """Test getting user achievements"""
        user_id = 123
        
        # Trigger some achievements
        await progress_service.update_progress(user_id, 'basics', 15, 85)
        
        achievements = await progress_service.get_user_achievements(user_id)
        
        assert isinstance(achievements, list)
        assert len(achievements) > 0
        assert 'type' in achievements[0]
        assert 'title' in achievements[0]
        assert 'earned_at' in achievements[0]


class TestNotificationService:
    """Test Notification service functionality"""
    
    @pytest.fixture
    def notification_service(self):
        return MockNotificationService()
    
    @pytest.mark.asyncio
    async def test_send_notification(self, notification_service):
        """Test sending notification"""
        notification = await notification_service.send_notification(
            user_id=123,
            title="Test Notification",
            message="This is a test message",
            notification_type="info"
        )
        
        assert notification['user_id'] == 123
        assert notification['title'] == "Test Notification"
        assert notification['message'] == "This is a test message"
        assert notification['type'] == "info"
        assert notification['read'] is False
        assert 'id' in notification
        assert 'created_at' in notification
    
    @pytest.mark.asyncio
    async def test_get_user_notifications(self, notification_service):
        """Test getting user notifications"""
        user_id = 123
        
        # Send multiple notifications
        await notification_service.send_notification(user_id, "Title 1", "Message 1")
        await notification_service.send_notification(user_id, "Title 2", "Message 2")
        await notification_service.send_notification(456, "Title 3", "Message 3")  # Different user
        
        notifications = await notification_service.get_user_notifications(user_id)
        
        assert len(notifications) == 2
        assert all(n['user_id'] == user_id for n in notifications)
        
        # Should be sorted by created_at (newest first)
        assert notifications[0]['created_at'] >= notifications[1]['created_at']
    
    @pytest.mark.asyncio
    async def test_get_unread_notifications(self, notification_service):
        """Test getting unread notifications only"""
        user_id = 123
        
        # Send notifications
        n1 = await notification_service.send_notification(user_id, "Title 1", "Message 1")
        n2 = await notification_service.send_notification(user_id, "Title 2", "Message 2")
        
        # Mark one as read
        await notification_service.mark_as_read(user_id, n1['id'])
        
        unread_notifications = await notification_service.get_user_notifications(user_id, unread_only=True)
        
        assert len(unread_notifications) == 1
        assert unread_notifications[0]['id'] == n2['id']
        assert unread_notifications[0]['read'] is False
    
    @pytest.mark.asyncio
    async def test_mark_as_read(self, notification_service):
        """Test marking notification as read"""
        user_id = 123
        
        notification = await notification_service.send_notification(
            user_id, "Test Title", "Test Message"
        )
        
        # Mark as read
        result = await notification_service.mark_as_read(user_id, notification['id'])
        assert result is True
        
        # Verify it's marked as read
        notifications = await notification_service.get_user_notifications(user_id)
        assert notifications[0]['read'] is True
    
    @pytest.mark.asyncio
    async def test_mark_as_read_invalid_notification(self, notification_service):
        """Test marking invalid notification as read"""
        result = await notification_service.mark_as_read(123, 999)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_mark_all_as_read(self, notification_service):
        """Test marking all notifications as read"""
        user_id = 123
        
        # Send multiple notifications
        await notification_service.send_notification(user_id, "Title 1", "Message 1")
        await notification_service.send_notification(user_id, "Title 2", "Message 2")
        await notification_service.send_notification(user_id, "Title 3", "Message 3")
        
        # Mark all as read
        count = await notification_service.mark_all_as_read(user_id)
        assert count == 3
        
        # Verify all are read
        notifications = await notification_service.get_user_notifications(user_id)
        assert all(n['read'] is True for n in notifications)


class TestServiceIntegration:
    """Test service integration scenarios"""
    
    @pytest.fixture
    def services(self):
        return {
            'user': MockUserService(),
            'exercise': MockExerciseService(),
            'progress': MockProgressService(),
            'notification': MockNotificationService()
        }
    
    @pytest.mark.asyncio
    async def test_complete_user_learning_flow(self, services):
        """Test complete user learning workflow"""
        user_service = services['user']
        exercise_service = services['exercise']
        progress_service = services['progress']
        notification_service = services['notification']
        
        # Create user
        user = await user_service.create_user("student", "student@example.com", "password123")
        user_id = user['id']
        
        # Create exercise
        exercise = await exercise_service.create_exercise(
            "Hello World", "Print Hello World", "beginner", "basics", 15
        )
        
        # Submit solution
        submission = await exercise_service.submit_solution(
            user_id, exercise['id'], "print('Hello, World!')", "python"
        )
        
        # Update progress
        await progress_service.update_progress(user_id, "basics", 15, submission['score'])
        
        # Send achievement notification
        await notification_service.send_notification(
            user_id, "Achievement Unlocked!", "You completed your first exercise!"
        )
        
        # Verify the complete flow
        final_progress = await progress_service.get_user_progress(user_id)
        notifications = await notification_service.get_user_notifications(user_id)
        
        assert submission['status'] == 'completed'
        assert final_progress['topics']['basics']['completed'] == 1
        assert len(notifications) == 1
    
    @pytest.mark.asyncio
    async def test_user_authentication_and_activity(self, services):
        """Test user authentication and activity tracking"""
        user_service = services['user']
        exercise_service = services['exercise']
        
        # Create and authenticate user
        await user_service.create_user("testuser", "test@example.com", "password123")
        authenticated_user = await user_service.authenticate_user("testuser", "password123")
        
        assert authenticated_user is not None
        assert authenticated_user['last_login'] is not None
        
        # User submits exercise
        exercise = await exercise_service.create_exercise(
            "Test Exercise", "Test Description", "beginner", "basics"
        )
        
        submission = await exercise_service.submit_solution(
            authenticated_user['id'], exercise['id'], "test code", "python"
        )
        
        # Get user stats
        stats = await user_service.get_user_stats(authenticated_user['id'])
        
        assert submission['user_id'] == authenticated_user['id']
        assert 'exercises_completed' in stats
    
    @pytest.mark.asyncio
    async def test_progress_and_achievement_integration(self, services):
        """Test progress tracking and achievement integration"""
        progress_service = services['progress']
        notification_service = services['notification']
        
        user_id = 123
        
        # Complete several exercises to trigger achievements
        for i in range(5):
            await progress_service.update_progress(user_id, 'basics', 20, 85)
        
        progress = await progress_service.get_user_progress(user_id)
        achievements = await progress_service.get_user_achievements(user_id)
        
        # Send achievement notifications
        for achievement in achievements:
            await notification_service.send_notification(
                user_id,
                f"Achievement: {achievement['title']}",
                achievement['description'],
                "achievement"
            )
        
        notifications = await notification_service.get_user_notifications(user_id)
        
        assert progress['total_points'] == 100  # 5 * 20 points
        assert len(achievements) > 0
        assert len(notifications) == len(achievements)
    
    @pytest.mark.asyncio
    async def test_exercise_statistics_and_user_performance(self, services):
        """Test exercise statistics and user performance correlation"""
        exercise_service = services['exercise']
        
        # Create exercise
        exercise = await exercise_service.create_exercise(
            "Test Exercise", "Test Description", "intermediate", "oop"
        )
        
        # Multiple users submit solutions
        user_ids = [123, 456, 789]
        for user_id in user_ids:
            await exercise_service.submit_solution(
                user_id, exercise['id'], f"solution by user {user_id}", "python"
            )
        
        # Get exercise statistics
        stats = await exercise_service.get_exercise_statistics(exercise['id'])
        
        # Get user submissions
        for user_id in user_ids:
            submissions = await exercise_service.get_user_submissions(user_id, exercise['id'])
            assert len(submissions) == 1
            assert submissions[0]['exercise_id'] == exercise['id']
        
        assert stats['total_submissions'] == 3
        assert 'average_score' in stats
        assert 'completion_rate' in stats