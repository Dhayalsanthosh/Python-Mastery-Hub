# tests/integration/test_api_integration.py
"""
Integration tests for API functionality.
Tests complete API workflows, endpoint interactions, and system integration.
"""

import pytest
import json
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any


class MockAPIServer:
    """Mock API server for integration testing"""
    
    def __init__(self):
        self.users = {}
        self.exercises = {}
        self.submissions = {}
        self.sessions = {}
        self.progress = {}
        self.next_id = 1
        self.running = False
        self.request_log = []
        self.rate_limits = {}
    
    async def start_server(self, host='localhost', port=8000):
        """Start the API server"""
        self.running = True
        self.host = host
        self.port = port
        return {"status": "started", "url": f"http://{host}:{port}"}
    
    async def stop_server(self):
        """Stop the API server"""
        self.running = False
        return {"status": "stopped"}
    
    def log_request(self, method, endpoint, headers=None, data=None):
        """Log API request for testing"""
        self.request_log.append({
            "timestamp": datetime.now(),
            "method": method,
            "endpoint": endpoint,
            "headers": headers or {},
            "data": data
        })
    
    def check_rate_limit(self, client_ip, endpoint):
        """Check rate limiting"""
        key = f"{client_ip}:{endpoint}"
        now = time.time()
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Clean old requests (older than 1 hour)
        self.rate_limits[key] = [
            req_time for req_time in self.rate_limits[key] 
            if now - req_time < 3600
        ]
        
        # Check if limit exceeded (100 requests per hour)
        if len(self.rate_limits[key]) >= 100:
            return False, 429, {"error": "Rate limit exceeded"}
        
        # Record this request
        self.rate_limits[key].append(now)
        return True, 200, None
    
    async def handle_auth_register(self, data):
        """Handle user registration"""
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return 400, {"error": f"Missing required field: {field}"}
        
        # Check if user already exists
        for user in self.users.values():
            if user['username'] == data['username']:
                return 409, {"error": "Username already exists"}
            if user['email'] == data['email']:
                return 409, {"error": "Email already exists"}
        
        # Create user
        user_id = self.next_id
        self.next_id += 1
        
        user = {
            "id": user_id,
            "username": data['username'],
            "email": data['email'],
            "password_hash": f"hashed_{data['password']}",
            "created_at": datetime.now().isoformat(),
            "role": data.get('role', 'student'),
            "is_active": True
        }
        
        self.users[user_id] = user
        
        # Initialize progress
        self.progress[user_id] = {
            "user_id": user_id,
            "overall_progress": 0.0,
            "topics": {
                "basics": {"completed": 0, "total": 20, "progress": 0.0},
                "oop": {"completed": 0, "total": 15, "progress": 0.0},
                "advanced": {"completed": 0, "total": 10, "progress": 0.0}
            },
            "total_points": 0,
            "level": 1
        }
        
        return 201, {
            "user": {k: v for k, v in user.items() if k != 'password_hash'},
            "message": "User created successfully"
        }
    
    async def handle_auth_login(self, data):
        """Handle user login"""
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return 400, {"error": "Username and password required"}
        
        # Find user
        user = None
        for u in self.users.values():
            if u['username'] == username and u['password_hash'] == f"hashed_{password}":
                user = u
                break
        
        if not user:
            return 401, {"error": "Invalid credentials"}
        
        if not user['is_active']:
            return 403, {"error": "Account is deactivated"}
        
        # Create session
        session_id = f"session_{user['id']}_{int(time.time())}"
        session = {
            "session_id": session_id,
            "user_id": user['id'],
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24)
        }
        
        self.sessions[session_id] = session
        
        return 200, {
            "user": {k: v for k, v in user.items() if k != 'password_hash'},
            "token": f"jwt_token_{session_id}",
            "expires_at": session['expires_at'].isoformat()
        }
    
    async def handle_auth_logout(self, headers):
        """Handle user logout"""
        auth_header = headers.get('Authorization', '')
        if not auth_header.startswith('Bearer jwt_token_'):
            return 401, {"error": "Invalid token"}
        
        session_id = auth_header.replace('Bearer jwt_token_', '')
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        return 200, {"message": "Logged out successfully"}
    
    def authenticate_request(self, headers):
        """Authenticate API request"""
        auth_header = headers.get('Authorization', '')
        if not auth_header.startswith('Bearer jwt_token_'):
            return None
        
        session_id = auth_header.replace('Bearer jwt_token_', '')
        session = self.sessions.get(session_id)
        
        if not session or session['expires_at'] < datetime.now():
            return None
        
        user = self.users.get(session['user_id'])
        return user
    
    async def handle_get_exercises(self, params):
        """Handle get exercises endpoint"""
        topic = params.get('topic')
        difficulty = params.get('difficulty')
        limit = int(params.get('limit', 10))
        offset = int(params.get('offset', 0))
        
        # Filter exercises
        exercises = list(self.exercises.values())
        
        if topic:
            exercises = [ex for ex in exercises if ex['topic'] == topic]
        if difficulty:
            exercises = [ex for ex in exercises if ex['difficulty'] == difficulty]
        
        total = len(exercises)
        exercises = exercises[offset:offset + limit]
        
        return 200, {
            "exercises": exercises,
            "total": total,
            "page": (offset // limit) + 1,
            "per_page": limit
        }
    
    async def handle_create_exercise(self, data, user):
        """Handle create exercise endpoint"""
        if user['role'] not in ['admin', 'instructor']:
            return 403, {"error": "Insufficient permissions"}
        
        required_fields = ['title', 'description', 'difficulty', 'topic']
        for field in required_fields:
            if field not in data:
                return 400, {"error": f"Missing required field: {field}"}
        
        exercise_id = self.next_id
        self.next_id += 1
        
        exercise = {
            "id": exercise_id,
            "title": data['title'],
            "description": data['description'],
            "difficulty": data['difficulty'],
            "topic": data['topic'],
            "points": data.get('points', 10),
            "created_at": datetime.now().isoformat(),
            "created_by": user['id'],
            "is_active": True
        }
        
        self.exercises[exercise_id] = exercise
        
        # Update total counts in progress
        for progress in self.progress.values():
            if data['topic'] in progress['topics']:
                progress['topics'][data['topic']]['total'] += 1
        
        return 201, exercise
    
    async def handle_submit_solution(self, exercise_id, data, user):
        """Handle solution submission"""
        if exercise_id not in self.exercises:
            return 404, {"error": "Exercise not found"}
        
        if 'code' not in data:
            return 400, {"error": "Code is required"}
        
        exercise = self.exercises[exercise_id]
        
        # Simulate code execution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        submission_id = self.next_id
        self.next_id += 1
        
        # Mock scoring
        code_length = len(data['code'])
        base_score = min(100, code_length * 2)  # Simple scoring
        score = max(0, base_score + (exercise_id % 20) - 10)  # Add some variation
        
        submission = {
            "id": submission_id,
            "user_id": user['id'],
            "exercise_id": exercise_id,
            "code": data['code'],
            "language": data.get('language', 'python'),
            "score": score,
            "status": "completed",
            "submitted_at": datetime.now().isoformat(),
            "feedback": "Good solution!" if score >= 70 else "Needs improvement."
        }
        
        self.submissions[submission_id] = submission
        
        # Update user progress
        if score >= 70:  # Passing score
            user_progress = self.progress[user['id']]
            topic = exercise['topic']
            
            if topic in user_progress['topics']:
                user_progress['topics'][topic]['completed'] += 1
                user_progress['total_points'] += exercise['points']
                
                # Recalculate progress percentages
                for t, data in user_progress['topics'].items():
                    if data['total'] > 0:
                        data['progress'] = (data['completed'] / data['total']) * 100
                
                # Recalculate overall progress
                total_completed = sum(t['completed'] for t in user_progress['topics'].values())
                total_exercises = sum(t['total'] for t in user_progress['topics'].values())
                user_progress['overall_progress'] = (total_completed / total_exercises) * 100 if total_exercises > 0 else 0
                
                # Update level
                user_progress['level'] = min(user_progress['total_points'] // 100 + 1, 10)
        
        return 200, submission
    
    async def handle_get_progress(self, user):
        """Handle get user progress"""
        return 200, self.progress.get(user['id'], {})
    
    async def handle_get_leaderboard(self, params):
        """Handle get leaderboard"""
        limit = int(params.get('limit', 10))
        
        # Create leaderboard from progress data
        leaderboard = []
        
        for user_id, progress in self.progress.items():
            if user_id in self.users:
                user = self.users[user_id]
                leaderboard.append({
                    "rank": 0,  # Will be set after sorting
                    "user_id": user_id,
                    "username": user['username'],
                    "total_points": progress['total_points'],
                    "level": progress['level'],
                    "overall_progress": progress['overall_progress']
                })
        
        # Sort by points (descending)
        leaderboard.sort(key=lambda x: x['total_points'], reverse=True)
        
        # Add ranks
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1
        
        return 200, {
            "leaderboard": leaderboard[:limit],
            "total_users": len(leaderboard)
        }
    
    async def handle_get_user_profile(self, user):
        """Handle get user profile"""
        profile = {k: v for k, v in user.items() if k != 'password_hash'}
        
        # Add statistics
        user_submissions = [s for s in self.submissions.values() if s['user_id'] == user['id']]
        profile['statistics'] = {
            "total_submissions": len(user_submissions),
            "completed_submissions": len([s for s in user_submissions if s['status'] == 'completed']),
            "average_score": sum(s['score'] for s in user_submissions if s['score']) / len(user_submissions) if user_submissions else 0
        }
        
        return 200, profile
    
    async def process_request(self, method, endpoint, headers=None, data=None, params=None, client_ip='127.0.0.1'):
        """Process API request"""
        headers = headers or {}
        data = data or {}
        params = params or {}
        
        # Log request
        self.log_request(method, endpoint, headers, data)
        
        # Check rate limiting
        allowed, status_code, error_response = self.check_rate_limit(client_ip, endpoint)
        if not allowed:
            return status_code, error_response
        
        # Route requests
        if endpoint == '/api/auth/register' and method == 'POST':
            return await self.handle_auth_register(data)
        
        elif endpoint == '/api/auth/login' and method == 'POST':
            return await self.handle_auth_login(data)
        
        elif endpoint == '/api/auth/logout' and method == 'POST':
            return await self.handle_auth_logout(headers)
        
        elif endpoint == '/api/exercises' and method == 'GET':
            return await self.handle_get_exercises(params)
        
        elif endpoint == '/api/exercises' and method == 'POST':
            user = self.authenticate_request(headers)
            if not user:
                return 401, {"error": "Authentication required"}
            return await self.handle_create_exercise(data, user)
        
        elif endpoint.startswith('/api/exercises/') and endpoint.endswith('/submit') and method == 'POST':
            user = self.authenticate_request(headers)
            if not user:
                return 401, {"error": "Authentication required"}
            
            exercise_id = int(endpoint.split('/')[3])
            return await self.handle_submit_solution(exercise_id, data, user)
        
        elif endpoint == '/api/progress' and method == 'GET':
            user = self.authenticate_request(headers)
            if not user:
                return 401, {"error": "Authentication required"}
            return await self.handle_get_progress(user)
        
        elif endpoint == '/api/leaderboard' and method == 'GET':
            return await self.handle_get_leaderboard(params)
        
        elif endpoint == '/api/users/profile' and method == 'GET':
            user = self.authenticate_request(headers)
            if not user:
                return 401, {"error": "Authentication required"}
            return await self.handle_get_user_profile(user)
        
        else:
            return 404, {"error": "Endpoint not found"}


class TestAPIServerLifecycle:
    """Test API server lifecycle management"""
    
    @pytest.fixture
    async def api_server(self):
        server = MockAPIServer()
        await server.start_server()
        yield server
        await server.stop_server()
    
    @pytest.mark.asyncio
    async def test_server_startup_shutdown(self):
        """Test API server startup and shutdown"""
        server = MockAPIServer()
        
        # Server should not be running initially
        assert server.running is False
        
        # Start server
        result = await server.start_server(host='0.0.0.0', port=8080)
        assert server.running is True
        assert result["status"] == "started"
        assert result["url"] == "http://0.0.0.0:8080"
        
        # Stop server
        result = await server.stop_server()
        assert server.running is False
        assert result["status"] == "stopped"
    
    @pytest.mark.asyncio
    async def test_request_logging(self, api_server):
        """Test that API requests are logged"""
        initial_log_count = len(api_server.request_log)
        
        # Make some requests
        await api_server.process_request('GET', '/api/exercises')
        await api_server.process_request('POST', '/api/auth/login', data={'username': 'test'})
        
        # Check logs
        assert len(api_server.request_log) == initial_log_count + 2
        
        latest_logs = api_server.request_log[-2:]
        assert latest_logs[0]['method'] == 'GET'
        assert latest_logs[0]['endpoint'] == '/api/exercises'
        assert latest_logs[1]['method'] == 'POST'
        assert latest_logs[1]['endpoint'] == '/api/auth/login'


class TestAuthenticationFlow:
    """Test complete authentication workflows"""
    
    @pytest.fixture
    async def api_server(self):
        server = MockAPIServer()
        await server.start_server()
        yield server
        await server.stop_server()
    
    @pytest.mark.asyncio
    async def test_user_registration_flow(self, api_server):
        """Test user registration workflow"""
        # Register new user
        status, response = await api_server.process_request('POST', '/api/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123'
        })
        
        assert status == 201
        assert response['user']['username'] == 'newuser'
        assert response['user']['email'] == 'new@example.com'
        assert 'password_hash' not in response['user']  # Should not expose password hash
        assert response['message'] == 'User created successfully'
        
        # Verify user was created
        assert len(api_server.users) == 1
        user_id = response['user']['id']
        assert user_id in api_server.users
        assert user_id in api_server.progress  # Progress should be initialized
    
    @pytest.mark.asyncio
    async def test_duplicate_user_registration(self, api_server):
        """Test duplicate user registration handling"""
        user_data = {
            'username': 'duplicate',
            'email': 'dup@example.com',
            'password': 'password'
        }
        
        # First registration should succeed
        status1, response1 = await api_server.process_request('POST', '/api/auth/register', data=user_data)
        assert status1 == 201
        
        # Second registration with same username should fail
        status2, response2 = await api_server.process_request('POST', '/api/auth/register', data=user_data)
        assert status2 == 409
        assert "Username already exists" in response2['error']
        
        # Registration with same email should fail
        user_data['username'] = 'different'
        status3, response3 = await api_server.process_request('POST', '/api/auth/register', data=user_data)
        assert status3 == 409
        assert "Email already exists" in response3['error']
    
    @pytest.mark.asyncio
    async def test_login_logout_flow(self, api_server):
        """Test login and logout workflow"""
        # Register user first
        await api_server.process_request('POST', '/api/auth/register', data={
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'loginpass'
        })
        
        # Login
        status, response = await api_server.process_request('POST', '/api/auth/login', data={
            'username': 'loginuser',
            'password': 'loginpass'
        })
        
        assert status == 200
        assert response['user']['username'] == 'loginuser'
        assert 'token' in response
        assert 'expires_at' in response
        
        token = response['token']
        
        # Verify session was created
        assert len(api_server.sessions) == 1
        
        # Logout
        status, response = await api_server.process_request('POST', '/api/auth/logout', headers={
            'Authorization': f'Bearer {token}'
        })
        
        assert status == 200
        assert response['message'] == 'Logged out successfully'
        
        # Verify session was removed
        assert len(api_server.sessions) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_login_attempts(self, api_server):
        """Test invalid login attempts"""
        # Register user
        await api_server.process_request('POST', '/api/auth/register', data={
            'username': 'validuser',
            'email': 'valid@example.com',
            'password': 'correctpass'
        })
        
        # Invalid username
        status, response = await api_server.process_request('POST', '/api/auth/login', data={
            'username': 'wronguser',
            'password': 'correctpass'
        })
        assert status == 401
        assert "Invalid credentials" in response['error']
        
        # Invalid password
        status, response = await api_server.process_request('POST', '/api/auth/login', data={
            'username': 'validuser',
            'password': 'wrongpass'
        })
        assert status == 401
        assert "Invalid credentials" in response['error']
        
        # Missing credentials
        status, response = await api_server.process_request('POST', '/api/auth/login', data={})
        assert status == 400
        assert "Username and password required" in response['error']


class TestExerciseManagement:
    """Test exercise management workflows"""
    
    @pytest.fixture
    async def authenticated_server(self):
        server = MockAPIServer()
        await server.start_server()
        
        # Create and login admin user
        await server.process_request('POST', '/api/auth/register', data={
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'adminpass',
            'role': 'admin'
        })
        
        status, login_response = await server.process_request('POST', '/api/auth/login', data={
            'username': 'admin',
            'password': 'adminpass'
        })
        
        token = login_response['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        yield server, headers
        await server.stop_server()
    
    @pytest.mark.asyncio
    async def test_create_exercise_workflow(self, authenticated_server):
        """Test exercise creation workflow"""
        server, headers = authenticated_server
        
        # Create exercise
        exercise_data = {
            'title': 'Hello World Exercise',
            'description': 'Write a function that returns Hello World',
            'difficulty': 'beginner',
            'topic': 'basics',
            'points': 15
        }
        
        status, response = await server.process_request('POST', '/api/exercises', headers=headers, data=exercise_data)
        
        assert status == 201
        assert response['title'] == 'Hello World Exercise'
        assert response['difficulty'] == 'beginner'
        assert response['topic'] == 'basics'
        assert response['points'] == 15
        assert 'id' in response
        assert 'created_at' in response
        
        # Verify exercise was stored
        exercise_id = response['id']
        assert exercise_id in server.exercises
    
    @pytest.mark.asyncio
    async def test_get_exercises_workflow(self, authenticated_server):
        """Test getting exercises workflow"""
        server, headers = authenticated_server
        
        # Create multiple exercises
        exercises_to_create = [
            {'title': 'Basic 1', 'description': 'Desc 1', 'difficulty': 'beginner', 'topic': 'basics'},
            {'title': 'Basic 2', 'description': 'Desc 2', 'difficulty': 'intermediate', 'topic': 'basics'},
            {'title': 'OOP 1', 'description': 'Desc 3', 'difficulty': 'beginner', 'topic': 'oop'}
        ]
        
        for exercise_data in exercises_to_create:
            await server.process_request('POST', '/api/exercises', headers=headers, data=exercise_data)
        
        # Get all exercises
        status, response = await server.process_request('GET', '/api/exercises')
        assert status == 200
        assert response['total'] == 3
        assert len(response['exercises']) == 3
        
        # Filter by topic
        status, response = await server.process_request('GET', '/api/exercises', params={'topic': 'basics'})
        assert status == 200
        assert response['total'] == 2
        
        # Filter by difficulty
        status, response = await server.process_request('GET', '/api/exercises', params={'difficulty': 'beginner'})
        assert status == 200
        assert response['total'] == 2
        
        # Test pagination
        status, response = await server.process_request('GET', '/api/exercises', params={'limit': '2', 'offset': '0'})
        assert status == 200
        assert len(response['exercises']) == 2
        assert response['page'] == 1
    
    @pytest.mark.asyncio
    async def test_exercise_permissions(self, authenticated_server):
        """Test exercise creation permissions"""
        server, admin_headers = authenticated_server
        
        # Create student user
        await server.process_request('POST', '/api/auth/register', data={
            'username': 'student',
            'email': 'student@example.com',
            'password': 'studentpass',
            'role': 'student'
        })
        
        status, login_response = await server.process_request('POST', '/api/auth/login', data={
            'username': 'student',
            'password': 'studentpass'
        })
        
        student_headers = {'Authorization': f'Bearer {login_response["token"]}'}
        
        # Student should not be able to create exercises
        exercise_data = {
            'title': 'Unauthorized Exercise',
            'description': 'Should not be created',
            'difficulty': 'beginner',
            'topic': 'basics'
        }
        
        status, response = await server.process_request('POST', '/api/exercises', headers=student_headers, data=exercise_data)
        assert status == 403
        assert "Insufficient permissions" in response['error']


class TestSubmissionWorkflow:
    """Test exercise submission workflows"""
    
    @pytest.fixture
    async def exercise_environment(self):
        server = MockAPIServer()
        await server.start_server()
        
        # Create admin and exercise
        await server.process_request('POST', '/api/auth/register', data={
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'adminpass',
            'role': 'admin'
        })
        
        admin_login = await server.process_request('POST', '/api/auth/login', data={
            'username': 'admin',
            'password': 'adminpass'
        })
        
        admin_headers = {'Authorization': f'Bearer {admin_login[1]["token"]}'}
        
        # Create exercise
        exercise_response = await server.process_request('POST', '/api/exercises', headers=admin_headers, data={
            'title': 'Test Exercise',
            'description': 'Test description',
            'difficulty': 'beginner',
            'topic': 'basics',
            'points': 20
        })
        
        exercise_id = exercise_response[1]['id']
        
        # Create student
        await server.process_request('POST', '/api/auth/register', data={
            'username': 'student',
            'email': 'student@example.com',
            'password': 'studentpass'
        })
        
        student_login = await server.process_request('POST', '/api/auth/login', data={
            'username': 'student',
            'password': 'studentpass'
        })
        
        student_headers = {'Authorization': f'Bearer {student_login[1]["token"]}'}
        
        yield server, exercise_id, student_headers
        await server.stop_server()
    
    @pytest.mark.asyncio
    async def test_successful_submission_workflow(self, exercise_environment):
        """Test successful exercise submission"""
        server, exercise_id, student_headers = exercise_environment
        
        # Submit solution
        submission_data = {
            'code': 'def hello_world():\n    return "Hello, World!"',
            'language': 'python'
        }
        
        status, response = await server.process_request(
            'POST', 
            f'/api/exercises/{exercise_id}/submit',
            headers=student_headers,
            data=submission_data
        )
        
        assert status == 200
        assert response['exercise_id'] == exercise_id
        assert response['code'] == submission_data['code']
        assert response['language'] == 'python'
        assert response['status'] == 'completed'
        assert 'score' in response
        assert 'feedback' in response
        assert 'submitted_at' in response
        
        # Verify submission was stored
        submission_id = response['id']
        assert submission_id in server.submissions
    
    @pytest.mark.asyncio
    async def test_submission_updates_progress(self, exercise_environment):
        """Test that submissions update user progress"""
        server, exercise_id, student_headers = exercise_environment
        
        # Get initial progress
        status, initial_progress = await server.process_request('GET', '/api/progress', headers=student_headers)
        initial_completed = initial_progress['topics']['basics']['completed']
        initial_points = initial_progress['total_points']
        
        # Submit passing solution
        submission_data = {
            'code': 'def solution():\n    return "This is a long enough solution to get a good score"',
            'language': 'python'
        }
        
        status, submission_response = await server.process_request(
            'POST',
            f'/api/exercises/{exercise_id}/submit',
            headers=student_headers,
            data=submission_data
        )
        
        # Check updated progress if score is passing
        status, updated_progress = await server.process_request('GET', '/api/progress', headers=student_headers)
        
        if submission_response['score'] >= 70:
            assert updated_progress['topics']['basics']['completed'] == initial_completed + 1
            assert updated_progress['total_points'] == initial_points + 20
        else:
            # If failing score, progress shouldn't change
            assert updated_progress['topics']['basics']['completed'] == initial_completed
            assert updated_progress['total_points'] == initial_points
    
    @pytest.mark.asyncio
    async def test_submission_to_nonexistent_exercise(self, exercise_environment):
        """Test submission to non-existent exercise"""
        server, exercise_id, student_headers = exercise_environment
        
        status, response = await server.process_request(
            'POST',
            '/api/exercises/99999/submit',
            headers=student_headers,
            data={'code': 'def solution(): pass'}
        )
        
        assert status == 404
        assert "Exercise not found" in response['error']
    
    @pytest.mark.asyncio
    async def test_submission_requires_authentication(self, exercise_environment):
        """Test that submission requires authentication"""
        server, exercise_id, student_headers = exercise_environment
        
        # Submit without authentication
        status, response = await server.process_request(
            'POST',
            f'/api/exercises/{exercise_id}/submit',
            data={'code': 'def solution(): pass'}
        )
        
        assert status == 401
        assert "Authentication required" in response['error']


class TestProgressAndLeaderboard:
    """Test progress tracking and leaderboard functionality"""
    
    @pytest.fixture
    async def multi_user_environment(self):
        server = MockAPIServer()
        await server.start_server()
        
        # Create multiple users
        users = []
        for i in range(3):
            await server.process_request('POST', '/api/auth/register', data={
                'username': f'user{i+1}',
                'email': f'user{i+1}@example.com',
                'password': 'password'
            })
            
            login_response = await server.process_request('POST', '/api/auth/login', data={
                'username': f'user{i+1}',
                'password': 'password'
            })
            
            users.append({
                'id': login_response[1]['user']['id'],
                'username': f'user{i+1}',
                'headers': {'Authorization': f'Bearer {login_response[1]["token"]}'}
            })
        
        yield server, users
        await server.stop_server()
    
    @pytest.mark.asyncio
    async def test_progress_tracking_workflow(self, multi_user_environment):
        """Test progress tracking workflow"""
        server, users = multi_user_environment
        user = users[0]
        
        # Get initial progress
        status, progress = await server.process_request('GET', '/api/progress', headers=user['headers'])
        
        assert status == 200
        assert progress['user_id'] == user['id']
        assert 'overall_progress' in progress
        assert 'topics' in progress
        assert 'total_points' in progress
        assert 'level' in progress
        
        # Verify topics structure
        assert 'basics' in progress['topics']
        assert 'oop' in progress['topics']
        assert 'advanced' in progress['topics']
        
        for topic_data in progress['topics'].values():
            assert 'completed' in topic_data
            assert 'total' in topic_data
            assert 'progress' in topic_data
    
    @pytest.mark.asyncio
    async def test_leaderboard_workflow(self, multi_user_environment):
        """Test leaderboard workflow"""
        server, users = multi_user_environment
        
        # Get leaderboard
        status, leaderboard = await server.process_request('GET', '/api/leaderboard')
        
        assert status == 200
        assert 'leaderboard' in leaderboard
        assert 'total_users' in leaderboard
        
        # Should have all users
        assert leaderboard['total_users'] == 3
        assert len(leaderboard['leaderboard']) == 3
        
        # Check leaderboard structure
        for entry in leaderboard['leaderboard']:
            assert 'rank' in entry
            assert 'user_id' in entry
            assert 'username' in entry
            assert 'total_points' in entry
            assert 'level' in entry
            assert 'overall_progress' in entry
        
        # Check ranking order
        prev_points = float('inf')
        for entry in leaderboard['leaderboard']:
            assert entry['total_points'] <= prev_points
            prev_points = entry['total_points']
    
    @pytest.mark.asyncio
    async def test_user_profile_workflow(self, multi_user_environment):
        """Test user profile workflow"""
        server, users = multi_user_environment
        user = users[0]
        
        # Get user profile
        status, profile = await server.process_request('GET', '/api/users/profile', headers=user['headers'])
        
        assert status == 200
        assert profile['id'] == user['id']
        assert profile['username'] == user['username']
        assert 'email' in profile
        assert 'created_at' in profile
        assert 'statistics' in profile
        
        # Check statistics
        stats = profile['statistics']
        assert 'total_submissions' in stats
        assert 'completed_submissions' in stats
        assert 'average_score' in stats


class TestRateLimiting:
    """Test API rate limiting functionality"""
    
    @pytest.fixture
    async def api_server(self):
        server = MockAPIServer()
        await server.start_server()
        yield server
        await server.stop_server()
    
    @pytest.mark.asyncio
    async def test_rate_limiting_enforcement(self, api_server):
        """Test that rate limiting is enforced"""
        client_ip = '192.168.1.100'
        endpoint = '/api/exercises'
        
        # Make requests up to the limit
        for i in range(100):
            status, response = await api_server.process_request('GET', endpoint, client_ip=client_ip)
            assert status == 200
        
        # Next request should be rate limited
        status, response = await api_server.process_request('GET', endpoint, client_ip=client_ip)
        assert status == 429
        assert "Rate limit exceeded" in response['error']
    
    @pytest.mark.asyncio
    async def test_rate_limiting_per_client(self, api_server):
        """Test that rate limiting is per client IP"""
        client1_ip = '192.168.1.101'
        client2_ip = '192.168.1.102'
        endpoint = '/api/exercises'
        
        # Exhaust limit for client1
        for i in range(100):
            await api_server.process_request('GET', endpoint, client_ip=client1_ip)
        
        # Client1 should be rate limited
        status, response = await api_server.process_request('GET', endpoint, client_ip=client1_ip)
        assert status == 429
        
        # Client2 should still work
        status, response = await api_server.process_request('GET', endpoint, client_ip=client2_ip)
        assert status == 200


class TestAPIErrorHandling:
    """Test API error handling scenarios"""
    
    @pytest.fixture
    async def api_server(self):
        server = MockAPIServer()
        await server.start_server()
        yield server
        await server.stop_server()
    
    @pytest.mark.asyncio
    async def test_invalid_endpoints(self, api_server):
        """Test handling of invalid endpoints"""
        status, response = await api_server.process_request('GET', '/api/nonexistent')
        assert status == 404
        assert "Endpoint not found" in response['error']
        
        status, response = await api_server.process_request('POST', '/api/invalid/path')
        assert status == 404
        assert "Endpoint not found" in response['error']
    
    @pytest.mark.asyncio
    async def test_malformed_requests(self, api_server):
        """Test handling of malformed requests"""
        # Missing required fields in registration
        status, response = await api_server.process_request('POST', '/api/auth/register', data={
            'username': 'testuser'
            # Missing email and password
        })
        assert status == 400
        assert "Missing required field" in response['error']
        
        # Missing code in submission
        status, response = await api_server.process_request('POST', '/api/exercises/1/submit', data={
            'language': 'python'
            # Missing code
        })
        assert status == 401  # Will fail authentication first
    
    @pytest.mark.asyncio
    async def test_authentication_errors(self, api_server):
        """Test authentication error scenarios"""
        # Invalid token format
        headers = {'Authorization': 'InvalidToken'}
        status, response = await api_server.process_request('GET', '/api/progress', headers=headers)
        assert status == 401
        assert "Authentication required" in response['error']
        
        # Expired/invalid token
        headers = {'Authorization': 'Bearer jwt_token_invalid_session'}
        status, response = await api_server.process_request('GET', '/api/progress', headers=headers)
        assert status == 401
        assert "Authentication required" in response['error']


class TestConcurrentAPIOperations:
    """Test concurrent API operations"""
    
    @pytest.fixture
    async def concurrent_environment(self):
        server = MockAPIServer()
        await server.start_server()
        
        # Create multiple users for concurrent testing
        users = []
        for i in range(5):
            await server.process_request('POST', '/api/auth/register', data={
                'username': f'concurrent_user{i+1}',
                'email': f'concurrent{i+1}@example.com',
                'password': 'password'
            })
            
            login_response = await server.process_request('POST', '/api/auth/login', data={
                'username': f'concurrent_user{i+1}',
                'password': 'password'
            })
            
            users.append({
                'id': login_response[1]['user']['id'],
                'headers': {'Authorization': f'Bearer {login_response[1]["token"]}'}
            })
        
        yield server, users
        await server.stop_server()
    
    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self, concurrent_environment):
        """Test concurrent API requests"""
        server, users = concurrent_environment
        
        # Make concurrent requests from multiple users
        async def make_user_requests(user):
            tasks = [
                server.process_request('GET', '/api/exercises', headers=user['headers']),
                server.process_request('GET', '/api/progress', headers=user['headers']),
                server.process_request('GET', '/api/leaderboard'),
                server.process_request('GET', '/api/users/profile', headers=user['headers'])
            ]
            return await asyncio.gather(*tasks)
        
        # Run requests for all users concurrently
        all_tasks = [make_user_requests(user) for user in users]
        results = await asyncio.gather(*all_tasks)
        
        # All requests should succeed
        for user_results in results:
            for status, response in user_results:
                assert status == 200
    
    @pytest.mark.asyncio
    async def test_concurrent_submissions(self, concurrent_environment):
        """Test concurrent exercise submissions"""
        server, users = concurrent_environment
        
        # Create an exercise first (need admin user)
        await server.process_request('POST', '/api/auth/register', data={
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'adminpass',
            'role': 'admin'
        })
        
        admin_login = await server.process_request('POST', '/api/auth/login', data={
            'username': 'admin',
            'password': 'adminpass'
        })
        
        admin_headers = {'Authorization': f'Bearer {admin_login[1]["token"]}'}
        
        exercise_response = await server.process_request('POST', '/api/exercises', headers=admin_headers, data={
            'title': 'Concurrent Test Exercise',
            'description': 'Test exercise for concurrent submissions',
            'difficulty': 'beginner',
            'topic': 'basics',
            'points': 10
        })
        
        exercise_id = exercise_response[1]['id']
        
        # Submit solutions concurrently from all users
        async def submit_solution(user, solution_num):
            return await server.process_request(
                'POST',
                f'/api/exercises/{exercise_id}/submit',
                headers=user['headers'],
                data={'code': f'def solution{solution_num}(): return {solution_num}'}
            )
        
        submission_tasks = [submit_solution(user, i) for i, user in enumerate(users)]
        submission_results = await asyncio.gather(*submission_tasks)
        
        # All submissions should succeed
        for status, response in submission_results:
            assert status == 200
            assert 'score' in response
            assert response['status'] == 'completed'