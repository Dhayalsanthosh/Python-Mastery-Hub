# tests/integration/test_web_integration.py
"""
Integration tests for web application functionality.
Tests complete web workflows, API interactions, and system integration.
"""

import pytest
import json
import time
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import aiohttp
from typing import Dict, List, Any


class MockWebApplication:
    """Mock web application for integration testing"""
    
    def __init__(self):
        self.users = {}
        self.exercises = {}
        self.submissions = {}
        self.sessions = {}
        self.progress = {}
        self.next_id = 1
        self.running = False
    
    async def start(self, host='localhost', port=8000):
        """Start the web application"""
        self.running = True
        self.host = host
        self.port = port
        return {"status": "started", "host": host, "port": port}
    
    async def stop(self):
        """Stop the web application"""
        self.running = False
        return {"status": "stopped"}
    
    async def create_user(self, username, email, password):
        """Create a new user"""
        user_id = self.next_id
        self.next_id += 1
        
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "password_hash": f"hashed_{password}",
            "created_at": datetime.now(),
            "is_active": True,
            "role": "student"
        }
        
        self.users[user_id] = user
        
        # Initialize progress
        self.progress[user_id] = {
            "user_id": user_id,
            "topics": {
                "basics": {"completed": 0, "total": 20},
                "oop": {"completed": 0, "total": 15},
                "advanced": {"completed": 0, "total": 10}
            },
            "total_points": 0,
            "level": 1
        }
        
        return user
    
    async def authenticate_user(self, username, password):
        """Authenticate user and create session"""
        for user in self.users.values():
            if (user["username"] == username and 
                user["password_hash"] == f"hashed_{password}"):
                
                # Create session
                session_id = f"session_{user['id']}_{int(time.time())}"
                session = {
                    "session_id": session_id,
                    "user_id": user["id"],
                    "created_at": datetime.now(),
                    "last_activity": datetime.now(),
                    "expires_at": datetime.now() + timedelta(hours=24)
                }
                
                self.sessions[session_id] = session
                
                return {
                    "user": user,
                    "session": session,
                    "token": f"jwt_token_{session_id}"
                }
        
        return None
    
    async def create_exercise(self, title, description, difficulty, topic, points=10):
        """Create a new exercise"""
        exercise_id = self.next_id
        self.next_id += 1
        
        exercise = {
            "id": exercise_id,
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "topic": topic,
            "points": points,
            "created_at": datetime.now(),
            "is_active": True,
            "test_cases": [],
            "template": "def solution():\n    # Your code here\n    pass"
        }
        
        self.exercises[exercise_id] = exercise
        return exercise
    
    async def submit_solution(self, user_id, exercise_id, code, language="python"):
        """Submit solution for an exercise"""
        if exercise_id not in self.exercises:
            raise ValueError("Exercise not found")
        
        submission_id = self.next_id
        self.next_id += 1
        
        # Simulate code execution and testing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Mock test results
        passed_tests = 2 if len(code) > 50 else 1
        total_tests = 3
        score = (passed_tests / total_tests) * 100
        
        submission = {
            "id": submission_id,
            "user_id": user_id,
            "exercise_id": exercise_id,
            "code": code,
            "language": language,
            "submitted_at": datetime.now(),
            "score": score,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "status": "completed",
            "feedback": "Good solution!" if score > 70 else "Needs improvement."
        }
        
        self.submissions[submission_id] = submission
        
        # Update user progress
        if user_id in self.progress:
            exercise = self.exercises[exercise_id]
            topic = exercise["topic"]
            self.progress[user_id]["topics"][topic]["completed"] += 1
            self.progress[user_id]["total_points"] += exercise["points"]
            
            # Update level based on points
            points = self.progress[user_id]["total_points"]
            self.progress[user_id]["level"] = min(points // 100 + 1, 10)
        
        return submission
    
    async def get_user_progress(self, user_id):
        """Get user progress"""
        if user_id not in self.progress:
            return None
        
        progress = self.progress[user_id].copy()
        
        # Calculate overall progress
        total_completed = sum(topic["completed"] for topic in progress["topics"].values())
        total_exercises = sum(topic["total"] for topic in progress["topics"].values())
        progress["overall_progress"] = (total_completed / total_exercises) * 100 if total_exercises > 0 else 0
        
        return progress
    
    async def get_exercises(self, topic=None, difficulty=None, limit=10, offset=0):
        """Get exercises with filtering and pagination"""
        exercises = list(self.exercises.values())
        
        # Apply filters
        if topic:
            exercises = [ex for ex in exercises if ex["topic"] == topic]
        if difficulty:
            exercises = [ex for ex in exercises if ex["difficulty"] == difficulty]
        
        # Apply pagination
        total = len(exercises)
        exercises = exercises[offset:offset + limit]
        
        return {
            "exercises": exercises,
            "total": total,
            "page": (offset // limit) + 1,
            "per_page": limit
        }
    
    async def get_leaderboard(self, limit=10):
        """Get user leaderboard"""
        user_scores = []
        
        for user_id, progress in self.progress.items():
            if user_id in self.users:
                user = self.users[user_id]
                user_scores.append({
                    "user_id": user_id,
                    "username": user["username"],
                    "total_points": progress["total_points"],
                    "level": progress["level"],
                    "overall_progress": (await self.get_user_progress(user_id))["overall_progress"]
                })
        
        # Sort by points
        user_scores.sort(key=lambda x: x["total_points"], reverse=True)
        
        # Add ranks
        for i, user in enumerate(user_scores):
            user["rank"] = i + 1
        
        return user_scores[:limit]


class MockHTTPClient:
    """Mock HTTP client for testing API interactions"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_token = None
        self.request_history = []
    
    async def post(self, endpoint, data=None, headers=None):
        """Make POST request"""
        return await self._make_request("POST", endpoint, data, headers)
    
    async def get(self, endpoint, params=None, headers=None):
        """Make GET request"""
        return await self._make_request("GET", endpoint, params, headers)
    
    async def put(self, endpoint, data=None, headers=None):
        """Make PUT request"""
        return await self._make_request("PUT", endpoint, data, headers)
    
    async def delete(self, endpoint, headers=None):
        """Make DELETE request"""
        return await self._make_request("DELETE", endpoint, None, headers)
    
    async def _make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request (mocked)"""
        request = {
            "method": method,
            "url": f"{self.base_url}{endpoint}",
            "data": data,
            "headers": headers or {},
            "timestamp": datetime.now()
        }
        
        # Add authentication header if token exists
        if self.session_token and "Authorization" not in request["headers"]:
            request["headers"]["Authorization"] = f"Bearer {self.session_token}"
        
        self.request_history.append(request)
        
        # Mock responses based on endpoint
        if endpoint == "/api/auth/login" and method == "POST":
            if data and data.get("username") == "testuser":
                self.session_token = "mock_jwt_token"
                return MockResponse(200, {
                    "success": True,
                    "user": {"id": 1, "username": "testuser"},
                    "token": self.session_token
                })
            else:
                return MockResponse(401, {"error": "Invalid credentials"})
        
        elif endpoint == "/api/auth/logout" and method == "POST":
            self.session_token = None
            return MockResponse(200, {"success": True, "message": "Logged out"})
        
        elif endpoint == "/api/users/profile" and method == "GET":
            if not self.session_token:
                return MockResponse(401, {"error": "Authentication required"})
            return MockResponse(200, {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "created_at": "2024-01-01T00:00:00Z"
            })
        
        elif endpoint == "/api/exercises" and method == "GET":
            return MockResponse(200, {
                "exercises": [
                    {"id": 1, "title": "Hello World", "difficulty": "beginner", "topic": "basics"},
                    {"id": 2, "title": "Variables", "difficulty": "beginner", "topic": "basics"}
                ],
                "total": 2,
                "page": 1,
                "per_page": 10
            })
        
        elif endpoint.startswith("/api/exercises/") and endpoint.endswith("/submit") and method == "POST":
            if not self.session_token:
                return MockResponse(401, {"error": "Authentication required"})
            
            exercise_id = int(endpoint.split("/")[3])
            return MockResponse(200, {
                "submission_id": 123,
                "exercise_id": exercise_id,
                "score": 85.5,
                "status": "completed",
                "feedback": "Good solution!"
            })
        
        elif endpoint == "/api/progress" and method == "GET":
            if not self.session_token:
                return MockResponse(401, {"error": "Authentication required"})
            return MockResponse(200, {
                "user_id": 1,
                "overall_progress": 65.5,
                "topics": {
                    "basics": {"completed": 8, "total": 12, "progress": 66.7},
                    "oop": {"completed": 3, "total": 8, "progress": 37.5}
                },
                "total_points": 180,
                "level": 2
            })
        
        elif endpoint == "/api/leaderboard" and method == "GET":
            return MockResponse(200, {
                "leaderboard": [
                    {"rank": 1, "username": "alice", "total_points": 250, "level": 3},
                    {"rank": 2, "username": "bob", "total_points": 200, "level": 2},
                    {"rank": 3, "username": "charlie", "total_points": 150, "level": 2}
                ]
            })
        
        else:
            return MockResponse(404, {"error": "Endpoint not found"})


class MockResponse:
    """Mock HTTP response"""
    
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data
    
    async def json(self):
        return self.data
    
    async def text(self):
        return json.dumps(self.data)


class TestWebApplicationLifecycle:
    """Test web application startup and shutdown"""
    
    @pytest.fixture
    async def web_app(self):
        app = MockWebApplication()
        await app.start()
        yield app
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_application_startup(self):
        """Test web application startup"""
        app = MockWebApplication()
        
        # App should not be running initially
        assert app.running is False
        
        # Start the application
        result = await app.start(host='127.0.0.1', port=8080)
        
        assert app.running is True
        assert result["status"] == "started"
        assert result["host"] == "127.0.0.1"
        assert result["port"] == 8080
        
        # Stop the application
        result = await app.stop()
        assert app.running is False
        assert result["status"] == "stopped"
    
    @pytest.mark.asyncio
    async def test_application_state_persistence(self, web_app):
        """Test that application state persists during runtime"""
        # Create some data
        user = await web_app.create_user("testuser", "test@example.com", "password123")
        exercise = await web_app.create_exercise("Test Exercise", "Description", "beginner", "basics")
        
        # Verify data exists
        assert user["id"] in web_app.users
        assert exercise["id"] in web_app.exercises
        
        # Data should persist throughout the application lifecycle
        assert len(web_app.users) == 1
        assert len(web_app.exercises) == 1


class TestUserAuthenticationFlow:
    """Test complete user authentication workflows"""
    
    @pytest.fixture
    async def web_app(self):
        app = MockWebApplication()
        await app.start()
        
        # Create test user
        await app.create_user("testuser", "test@example.com", "password123")
        
        yield app
        await app.stop()
    
    @pytest.fixture
    def http_client(self):
        return MockHTTPClient()
    
    @pytest.mark.asyncio
    async def test_user_registration_and_login_flow(self, web_app):
        """Test complete user registration and login flow"""
        # Create user
        user = await web_app.create_user("newuser", "new@example.com", "securepass")
        
        assert user["username"] == "newuser"
        assert user["email"] == "new@example.com"
        assert user["password_hash"] == "hashed_securepass"
        assert user["is_active"] is True
        
        # Authenticate user
        auth_result = await web_app.authenticate_user("newuser", "securepass")
        
        assert auth_result is not None
        assert auth_result["user"]["id"] == user["id"]
        assert "session" in auth_result
        assert "token" in auth_result
        
        # Verify session was created
        session_id = auth_result["session"]["session_id"]
        assert session_id in web_app.sessions
        assert web_app.sessions[session_id]["user_id"] == user["id"]
    
    @pytest.mark.asyncio
    async def test_api_authentication_workflow(self, http_client):
        """Test API authentication workflow"""
        # Login via API
        login_response = await http_client.post("/api/auth/login", {
            "username": "testuser",
            "password": "password123"
        })
        
        assert login_response.status_code == 200
        login_data = await login_response.json()
        assert login_data["success"] is True
        assert "token" in login_data
        assert http_client.session_token == "mock_jwt_token"
        
        # Access protected endpoint
        profile_response = await http_client.get("/api/users/profile")
        assert profile_response.status_code == 200
        
        profile_data = await profile_response.json()
        assert profile_data["username"] == "testuser"
        
        # Logout
        logout_response = await http_client.post("/api/auth/logout")
        assert logout_response.status_code == 200
        assert http_client.session_token is None
    
    @pytest.mark.asyncio
    async def test_authentication_failure_handling(self, http_client):
        """Test authentication failure scenarios"""
        # Invalid credentials
        login_response = await http_client.post("/api/auth/login", {
            "username": "wronguser",
            "password": "wrongpass"
        })
        
        assert login_response.status_code == 401
        login_data = await login_response.json()
        assert "error" in login_data
        assert http_client.session_token is None
        
        # Access protected endpoint without authentication
        profile_response = await http_client.get("/api/users/profile")
        assert profile_response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_session_expiration_handling(self, web_app):
        """Test session expiration handling"""
        # Create user and authenticate
        user = await web_app.create_user("expireuser", "expire@example.com", "password")
        auth_result = await web_app.authenticate_user("expireuser", "password")
        
        session_id = auth_result["session"]["session_id"]
        
        # Manually expire the session
        web_app.sessions[session_id]["expires_at"] = datetime.now() - timedelta(hours=1)
        
        # Session should be considered expired
        session = web_app.sessions[session_id]
        assert session["expires_at"] < datetime.now()


class TestExerciseWorkflow:
    """Test complete exercise workflow"""
    
    @pytest.fixture
    async def setup_environment(self):
        app = MockWebApplication()
        await app.start()
        
        # Create user and exercises
        user = await app.create_user("student", "student@example.com", "password")
        
        exercises = []
        for i in range(3):
            exercise = await app.create_exercise(
                f"Exercise {i+1}",
                f"Description for exercise {i+1}",
                "beginner" if i < 2 else "intermediate",
                "basics",
                10 + i * 5
            )
            exercises.append(exercise)
        
        yield app, user, exercises
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_complete_exercise_workflow(self, setup_environment):
        """Test complete exercise workflow from listing to submission"""
        app, user, exercises = setup_environment
        
        # List exercises
        exercise_list = await app.get_exercises()
        assert exercise_list["total"] == 3
        assert len(exercise_list["exercises"]) == 3
        
        # Get specific exercise
        exercise_id = exercises[0]["id"]
        exercise = app.exercises[exercise_id]
        assert exercise["title"] == "Exercise 1"
        assert exercise["difficulty"] == "beginner"
        
        # Submit solution
        code = "def solution():\n    return 'Hello, World!'"
        submission = await app.submit_solution(user["id"], exercise_id, code)
        
        assert submission["user_id"] == user["id"]
        assert submission["exercise_id"] == exercise_id
        assert submission["code"] == code
        assert submission["status"] == "completed"
        assert "score" in submission
        assert "feedback" in submission
        
        # Verify progress was updated
        progress = await app.get_user_progress(user["id"])
        assert progress["topics"]["basics"]["completed"] == 1
        assert progress["total_points"] == 10  # Points from first exercise
    
    @pytest.mark.asyncio
    async def test_exercise_filtering_and_pagination(self, setup_environment):
        """Test exercise filtering and pagination"""
        app, user, exercises = setup_environment
        
        # Filter by difficulty
        beginner_exercises = await app.get_exercises(difficulty="beginner")
        assert beginner_exercises["total"] == 2
        
        # Filter by topic
        basics_exercises = await app.get_exercises(topic="basics")
        assert basics_exercises["total"] == 3
        
        # Test pagination
        page1 = await app.get_exercises(limit=2, offset=0)
        assert len(page1["exercises"]) == 2
        assert page1["page"] == 1
        
        page2 = await app.get_exercises(limit=2, offset=2)
        assert len(page2["exercises"]) == 1
        assert page2["page"] == 2
    
    @pytest.mark.asyncio
    async def test_multiple_submissions_workflow(self, setup_environment):
        """Test workflow with multiple exercise submissions"""
        app, user, exercises = setup_environment
        
        submissions = []
        
        # Submit solutions for all exercises
        for i, exercise in enumerate(exercises):
            code = f"def solution():\n    return 'Solution {i+1}'"
            submission = await app.submit_solution(user["id"], exercise["id"], code)
            submissions.append(submission)
        
        # Verify all submissions
        assert len(submissions) == 3
        for i, submission in enumerate(submissions):
            assert submission["exercise_id"] == exercises[i]["id"]
            assert f"Solution {i+1}" in submission["code"]
        
        # Check final progress
        progress = await app.get_user_progress(user["id"])
        assert progress["topics"]["basics"]["completed"] == 3
        assert progress["total_points"] == 45  # 10 + 15 + 20 points
        assert progress["level"] == 1  # 45 points = level 1
    
    @pytest.mark.asyncio
    async def test_exercise_submission_via_api(self):
        """Test exercise submission via API"""
        client = MockHTTPClient()
        
        # Login first
        await client.post("/api/auth/login", {
            "username": "testuser",
            "password": "password123"
        })
        
        # Submit solution
        submission_response = await client.post("/api/exercises/1/submit", {
            "code": "def solution():\n    return 42",
            "language": "python"
        })
        
        assert submission_response.status_code == 200
        submission_data = await submission_response.json()
        
        assert submission_data["exercise_id"] == 1
        assert "score" in submission_data
        assert "feedback" in submission_data
        assert submission_data["status"] == "completed"


class TestProgressTrackingIntegration:
    """Test progress tracking across the application"""
    
    @pytest.fixture
    async def multi_user_environment(self):
        app = MockWebApplication()
        await app.start()
        
        # Create multiple users
        users = []
        for i in range(3):
            user = await app.create_user(f"user{i+1}", f"user{i+1}@example.com", "password")
            users.append(user)
        
        # Create exercises across different topics
        exercises = []
        topics = ["basics", "oop", "advanced"]
        for topic in topics:
            for j in range(2):
                exercise = await app.create_exercise(
                    f"{topic.title()} Exercise {j+1}",
                    f"Description for {topic} exercise {j+1}",
                    "beginner",
                    topic,
                    15
                )
                exercises.append(exercise)
        
        yield app, users, exercises
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_individual_progress_tracking(self, multi_user_environment):
        """Test individual user progress tracking"""
        app, users, exercises = multi_user_environment
        user = users[0]
        
        # Initial progress should be zero
        progress = await app.get_user_progress(user["id"])
        assert progress["total_points"] == 0
        assert progress["overall_progress"] == 0
        
        # Complete some exercises
        for i in range(3):
            exercise = exercises[i]
            await app.submit_solution(user["id"], exercise["id"], "def solution(): pass")
        
        # Check updated progress
        progress = await app.get_user_progress(user["id"])
        assert progress["total_points"] == 45  # 3 exercises * 15 points
        assert progress["overall_progress"] > 0
        
        # Check topic-specific progress
        basics_completed = progress["topics"]["basics"]["completed"]
        oop_completed = progress["topics"]["oop"]["completed"]
        
        assert basics_completed + oop_completed + progress["topics"]["advanced"]["completed"] == 3
    
    @pytest.mark.asyncio
    async def test_leaderboard_integration(self, multi_user_environment):
        """Test leaderboard integration with user progress"""
        app, users, exercises = multi_user_environment
        
        # Have different users complete different numbers of exercises
        user_scores = [1, 3, 2]  # Number of exercises each user completes
        
        for i, user in enumerate(users):
            for j in range(user_scores[i]):
                exercise = exercises[j]
                await app.submit_solution(user["id"], exercise["id"], "def solution(): pass")
        
        # Get leaderboard
        leaderboard = await app.get_leaderboard()
        
        # Should be sorted by points (descending)
        assert len(leaderboard) == 3
        assert leaderboard[0]["total_points"] >= leaderboard[1]["total_points"]
        assert leaderboard[1]["total_points"] >= leaderboard[2]["total_points"]
        
        # Check that ranks are assigned correctly
        for i, entry in enumerate(leaderboard):
            assert entry["rank"] == i + 1
            assert entry["username"] in [f"user{j+1}" for j in range(3)]
    
    @pytest.mark.asyncio
    async def test_progress_api_integration(self):
        """Test progress tracking via API"""
        client = MockHTTPClient()
        
        # Login
        await client.post("/api/auth/login", {
            "username": "testuser",
            "password": "password123"
        })
        
        # Get progress
        progress_response = await client.get("/api/progress")
        assert progress_response.status_code == 200
        
        progress_data = await progress_response.json()
        assert "overall_progress" in progress_data
        assert "topics" in progress_data
        assert "total_points" in progress_data
        assert "level" in progress_data
        
        # Get leaderboard
        leaderboard_response = await client.get("/api/leaderboard")
        assert leaderboard_response.status_code == 200
        
        leaderboard_data = await leaderboard_response.json()
        assert "leaderboard" in leaderboard_data
        assert isinstance(leaderboard_data["leaderboard"], list)


class TestConcurrentUserOperations:
    """Test concurrent operations by multiple users"""
    
    @pytest.fixture
    async def concurrent_environment(self):
        app = MockWebApplication()
        await app.start()
        
        # Create multiple users and exercises
        users = []
        for i in range(5):
            user = await app.create_user(f"concurrent_user{i+1}", f"user{i+1}@test.com", "password")
            users.append(user)
        
        exercises = []
        for i in range(10):
            exercise = await app.create_exercise(
                f"Concurrent Exercise {i+1}",
                f"Description {i+1}",
                "beginner",
                "basics",
                10
            )
            exercises.append(exercise)
        
        yield app, users, exercises
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_concurrent_submissions(self, concurrent_environment):
        """Test concurrent exercise submissions"""
        app, users, exercises = concurrent_environment
        
        # Create tasks for concurrent submissions
        async def submit_exercise(user, exercise):
            code = f"def solution(): return '{user['username']}_solution'"
            return await app.submit_solution(user["id"], exercise["id"], code)
        
        # Submit same exercise from multiple users concurrently
        tasks = []
        exercise = exercises[0]
        
        for user in users:
            task = submit_exercise(user, exercise)
            tasks.append(task)
        
        # Execute all submissions concurrently
        results = await asyncio.gather(*tasks)
        
        # All submissions should succeed
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["user_id"] == users[i]["id"]
            assert result["exercise_id"] == exercise["id"]
            assert f"{users[i]['username']}_solution" in result["code"]
    
    @pytest.mark.asyncio
    async def test_concurrent_progress_updates(self, concurrent_environment):
        """Test concurrent progress updates"""
        app, users, exercises = concurrent_environment
        
        # Have multiple users complete exercises concurrently
        async def complete_exercises(user, exercise_list):
            results = []
            for exercise in exercise_list[:3]:  # Each user completes 3 exercises
                code = f"def solution(): return '{user['username']}_answer'"
                result = await app.submit_solution(user["id"], exercise["id"], code)
                results.append(result)
            return results
        
        # Create concurrent tasks
        tasks = []
        for user in users:
            task = complete_exercises(user, exercises)
            tasks.append(task)
        
        # Execute concurrently
        all_results = await asyncio.gather(*tasks)
        
        # Verify all users have updated progress
        for i, user in enumerate(users):
            progress = await app.get_user_progress(user["id"])
            assert progress["total_points"] == 30  # 3 exercises * 10 points
            assert progress["topics"]["basics"]["completed"] == 3
        
        # Verify leaderboard reflects all users
        leaderboard = await app.get_leaderboard()
        assert len(leaderboard) == 5
        
        # All users should have same score since they completed same number of exercises
        for entry in leaderboard:
            assert entry["total_points"] == 30
    
    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self):
        """Test concurrent API requests from multiple clients"""
        clients = [MockHTTPClient() for _ in range(3)]
        
        # Login all clients concurrently
        login_tasks = []
        for client in clients:
            task = client.post("/api/auth/login", {
                "username": "testuser",
                "password": "password123"
            })
            login_tasks.append(task)
        
        login_results = await asyncio.gather(*login_tasks)
        
        # All logins should succeed
        for result in login_results:
            assert result.status_code == 200
        
        # Make concurrent API requests
        api_tasks = []
        for client in clients:
            api_tasks.extend([
                client.get("/api/exercises"),
                client.get("/api/progress"),
                client.get("/api/leaderboard")
            ])
        
        api_results = await asyncio.gather(*api_tasks)
        
        # All requests should succeed
        for result in api_results:
            assert result.status_code == 200


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios"""
    
    @pytest.fixture
    async def error_test_environment(self):
        app = MockWebApplication()
        await app.start()
        
        user = await app.create_user("erroruser", "error@test.com", "password")
        exercise = await app.create_exercise("Error Test", "Description", "beginner", "basics")
        
        yield app, user, exercise
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_invalid_exercise_submission(self, error_test_environment):
        """Test submission to non-existent exercise"""
        app, user, exercise = error_test_environment
        
        # Try to submit to non-existent exercise
        with pytest.raises(ValueError, match="Exercise not found"):
            await app.submit_solution(user["id"], 99999, "def solution(): pass")
    
    @pytest.mark.asyncio
    async def test_api_error_responses(self):
        """Test API error response handling"""
        client = MockHTTPClient()
        
        # Test accessing protected endpoint without authentication
        response = await client.get("/api/users/profile")
        assert response.status_code == 401
        
        error_data = await response.json()
        assert "error" in error_data
        
        # Test non-existent endpoint
        response = await client.get("/api/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_malformed_request_handling(self):
        """Test handling of malformed requests"""
        client = MockHTTPClient()
        
        # Test login with missing data
        response = await client.post("/api/auth/login", {})
        assert response.status_code == 401
        
        # Test login with malformed data
        response = await client.post("/api/auth/login", {
            "username": "testuser"
            # Missing password
        })
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_application_state_consistency(self, error_test_environment):
        """Test that application state remains consistent after errors"""
        app, user, exercise = error_test_environment
        
        initial_user_count = len(app.users)
        initial_exercise_count = len(app.exercises)
        
        # Attempt invalid operations
        try:
            await app.submit_solution(user["id"], 99999, "code")
        except ValueError:
            pass
        
        # State should remain unchanged
        assert len(app.users) == initial_user_count
        assert len(app.exercises) == initial_exercise_count
        
        # Valid operations should still work
        submission = await app.submit_solution(user["id"], exercise["id"], "def solution(): pass")
        assert submission["status"] == "completed"


class TestPerformanceAndScaling:
    """Test performance and scaling characteristics"""
    
    @pytest.mark.asyncio
    async def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        app = MockWebApplication()
        await app.start()
        
        # Create many users and exercises
        start_time = time.time()
        
        users = []
        for i in range(100):
            user = await app.create_user(f"user{i}", f"user{i}@test.com", "password")
            users.append(user)
        
        exercises = []
        for i in range(50):
            exercise = await app.create_exercise(f"Exercise {i}", "Description", "beginner", "basics")
            exercises.append(exercise)
        
        creation_time = time.time() - start_time
        
        # Operations should complete in reasonable time
        assert creation_time < 10.0  # Should complete in under 10 seconds
        
        # Test querying large datasets
        start_time = time.time()
        
        exercise_list = await app.get_exercises(limit=50)
        leaderboard = await app.get_leaderboard(limit=100)
        
        query_time = time.time() - start_time
        assert query_time < 5.0  # Queries should be fast
        
        # Verify data integrity
        assert len(exercise_list["exercises"]) == 50
        assert len(app.users) == 100
        
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_high_frequency_operations(self):
        """Test high-frequency operations"""
        app = MockWebApplication()
        await app.start()
        
        user = await app.create_user("speeduser", "speed@test.com", "password")
        exercise = await app.create_exercise("Speed Test", "Description", "beginner", "basics")
        
        # Perform many operations quickly
        start_time = time.time()
        
        for i in range(100):
            # Each iteration: submit solution and check progress
            await app.submit_solution(user["id"], exercise["id"], f"def solution(): return {i}")
            await app.get_user_progress(user["id"])
        
        total_time = time.time() - start_time
        
        # Should handle high frequency operations efficiently
        assert total_time < 30.0  # 200 operations in under 30 seconds
        
        # Verify final state
        progress = await app.get_user_progress(user["id"])
        assert progress["topics"]["basics"]["completed"] == 100
        
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self):
        """Test that memory usage remains stable"""
        app = MockWebApplication()
        await app.start()
        
        # Create initial data
        user = await app.create_user("memuser", "mem@test.com", "password")
        
        # Perform operations and check that data structures don't grow unbounded
        initial_submission_count = len(app.submissions)
        
        # Create and clean up data multiple times
        for cycle in range(10):
            # Create temporary data
            temp_exercises = []
            for i in range(10):
                exercise = await app.create_exercise(f"Temp {cycle}-{i}", "Temp", "beginner", "basics")
                temp_exercises.append(exercise)
            
            # Submit solutions
            for exercise in temp_exercises:
                await app.submit_solution(user["id"], exercise["id"], "def solution(): pass")
            
            # Clean up (in real app, this might be garbage collection or explicit cleanup)
            # For this test, we'll just verify counts are reasonable
            assert len(app.exercises) <= 100 + cycle * 10  # Bounded growth
            assert len(app.submissions) >= initial_submission_count
        
        await app.stop()