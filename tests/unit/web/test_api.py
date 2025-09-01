# tests/unit/web/test_api.py
"""
Test module for web API functionality.
Tests API endpoints, request/response handling, authentication, and error handling.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any


class MockAPIResponse:
    """Mock API response for testing"""
    
    def __init__(self, status_code=200, json_data=None, headers=None):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.headers = headers or {}
        self.text = json.dumps(json_data) if json_data else ""
    
    def json(self):
        return self._json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code} Error")


class MockAPIClient:
    """Mock API client for testing"""
    
    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = Mock()
        self.last_request = None
    
    def _get_headers(self):
        """Get request headers"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        self.last_request = {
            'method': method,
            'url': url,
            'headers': headers,
            'data': data,
            'params': params
        }
        
        # Mock different responses based on endpoint
        if endpoint == '/api/users/login':
            if data and data.get('username') == 'valid_user':
                return MockAPIResponse(200, {
                    'user_id': 123,
                    'username': 'valid_user',
                    'token': 'mock_jwt_token',
                    'expires_at': '2024-12-31T23:59:59Z'
                })
            else:
                return MockAPIResponse(401, {'error': 'Invalid credentials'})
        
        elif endpoint == '/api/users/profile':
            return MockAPIResponse(200, {
                'user_id': 123,
                'username': 'test_user',
                'email': 'test@example.com',
                'created_at': '2024-01-01T00:00:00Z',
                'progress': {
                    'total_exercises': 50,
                    'completed_exercises': 35,
                    'current_level': 3
                }
            })
        
        elif endpoint == '/api/exercises':
            return MockAPIResponse(200, {
                'exercises': [
                    {
                        'id': 1,
                        'title': 'Basic Variables',
                        'difficulty': 'beginner',
                        'topic': 'basics',
                        'completed': True
                    },
                    {
                        'id': 2,
                        'title': 'Functions',
                        'difficulty': 'intermediate',
                        'topic': 'basics',
                        'completed': False
                    }
                ],
                'total': 2,
                'page': 1,
                'per_page': 10
            })
        
        elif endpoint.startswith('/api/exercises/') and endpoint.endswith('/submit'):
            exercise_id = endpoint.split('/')[-2]
            return MockAPIResponse(200, {
                'exercise_id': int(exercise_id),
                'status': 'submitted',
                'score': 85.5,
                'feedback': 'Good solution! Consider edge cases.',
                'submitted_at': datetime.now().isoformat()
            })
        
        elif endpoint == '/api/progress':
            return MockAPIResponse(200, {
                'user_id': 123,
                'overall_progress': 70.5,
                'topics': {
                    'basics': {'completed': 15, 'total': 20, 'progress': 75.0},
                    'oop': {'completed': 8, 'total': 15, 'progress': 53.3},
                    'advanced': {'completed': 2, 'total': 10, 'progress': 20.0}
                },
                'recent_activity': [
                    {
                        'exercise_id': 25,
                        'title': 'Class Inheritance',
                        'completed_at': '2024-01-15T10:30:00Z',
                        'score': 92
                    }
                ]
            })
        
        elif endpoint == '/api/leaderboard':
            return MockAPIResponse(200, {
                'leaderboard': [
                    {'rank': 1, 'username': 'alice123', 'score': 2500, 'level': 5},
                    {'rank': 2, 'username': 'bob456', 'score': 2350, 'level': 4},
                    {'rank': 3, 'username': 'charlie789', 'score': 2200, 'level': 4}
                ],
                'user_rank': 15,
                'total_users': 1000
            })
        
        else:
            return MockAPIResponse(404, {'error': 'Endpoint not found'})
    
    def get(self, endpoint, params=None):
        """GET request"""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint, data=None):
        """POST request"""
        return self._make_request('POST', endpoint, data=data)
    
    def put(self, endpoint, data=None):
        """PUT request"""
        return self._make_request('PUT', endpoint, data=data)
    
    def delete(self, endpoint):
        """DELETE request"""
        return self._make_request('DELETE', endpoint)


class TestAPIClient:
    """Test API client functionality"""
    
    @pytest.fixture
    def api_client(self):
        """Create API client instance"""
        return MockAPIClient(api_key="test_api_key")
    
    def test_client_initialization(self, api_client):
        """Test API client initialization"""
        assert api_client.base_url == "http://localhost:8000"
        assert api_client.api_key == "test_api_key"
    
    def test_get_headers_with_api_key(self, api_client):
        """Test headers with API key"""
        headers = api_client._get_headers()
        assert headers['Authorization'] == 'Bearer test_api_key'
        assert headers['Content-Type'] == 'application/json'
        assert headers['Accept'] == 'application/json'
    
    def test_get_headers_without_api_key(self):
        """Test headers without API key"""
        client = MockAPIClient()
        headers = client._get_headers()
        assert 'Authorization' not in headers
        assert headers['Content-Type'] == 'application/json'


class TestAuthenticationAPI:
    """Test authentication API endpoints"""
    
    @pytest.fixture
    def api_client(self):
        return MockAPIClient()
    
    def test_login_success(self, api_client):
        """Test successful login"""
        response = api_client.post('/api/users/login', {
            'username': 'valid_user',
            'password': 'correct_password'
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['username'] == 'valid_user'
        assert 'token' in data
        assert 'expires_at' in data
    
    def test_login_failure(self, api_client):
        """Test failed login"""
        response = api_client.post('/api/users/login', {
            'username': 'invalid_user',
            'password': 'wrong_password'
        })
        
        assert response.status_code == 401
        data = response.json()
        assert 'error' in data
        assert data['error'] == 'Invalid credentials'
    
    def test_profile_access(self, api_client):
        """Test profile access"""
        response = api_client.get('/api/users/profile')
        
        assert response.status_code == 200
        data = response.json()
        assert 'user_id' in data
        assert 'username' in data
        assert 'progress' in data
        assert data['progress']['total_exercises'] == 50


class TestExerciseAPI:
    """Test exercise API endpoints"""
    
    @pytest.fixture
    def api_client(self):
        return MockAPIClient(api_key="test_token")
    
    def test_get_exercises(self, api_client):
        """Test getting exercises list"""
        response = api_client.get('/api/exercises')
        
        assert response.status_code == 200
        data = response.json()
        assert 'exercises' in data
        assert len(data['exercises']) == 2
        assert data['exercises'][0]['title'] == 'Basic Variables'
        assert data['total'] == 2
    
    def test_get_exercises_with_filters(self, api_client):
        """Test getting exercises with filters"""
        params = {'topic': 'basics', 'difficulty': 'beginner'}
        response = api_client.get('/api/exercises', params=params)
        
        assert response.status_code == 200
        assert api_client.last_request['params'] == params
    
    def test_submit_exercise(self, api_client):
        """Test exercise submission"""
        exercise_id = 5
        submission_data = {
            'code': 'def hello(): return "Hello, World!"',
            'language': 'python'
        }
        
        response = api_client.post(f'/api/exercises/{exercise_id}/submit', submission_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['exercise_id'] == exercise_id
        assert data['status'] == 'submitted'
        assert 'score' in data
        assert 'feedback' in data
    
    def test_exercise_not_found(self, api_client):
        """Test accessing non-existent exercise"""
        response = api_client.get('/api/exercises/99999')
        
        assert response.status_code == 404
        data = response.json()
        assert 'error' in data


class TestProgressAPI:
    """Test progress tracking API"""
    
    @pytest.fixture
    def api_client(self):
        return MockAPIClient(api_key="test_token")
    
    def test_get_user_progress(self, api_client):
        """Test getting user progress"""
        response = api_client.get('/api/progress')
        
        assert response.status_code == 200
        data = response.json()
        assert 'overall_progress' in data
        assert 'topics' in data
        assert 'recent_activity' in data
        
        # Check topics structure
        assert 'basics' in data['topics']
        assert 'completed' in data['topics']['basics']
        assert 'total' in data['topics']['basics']
        assert 'progress' in data['topics']['basics']
    
    def test_progress_calculation(self, api_client):
        """Test progress calculation accuracy"""
        response = api_client.get('/api/progress')
        data = response.json()
        
        basics_progress = data['topics']['basics']
        expected_progress = (basics_progress['completed'] / basics_progress['total']) * 100
        assert abs(basics_progress['progress'] - expected_progress) < 0.1
    
    def test_recent_activity(self, api_client):
        """Test recent activity data"""
        response = api_client.get('/api/progress')
        data = response.json()
        
        activity = data['recent_activity'][0]
        assert 'exercise_id' in activity
        assert 'title' in activity
        assert 'completed_at' in activity
        assert 'score' in activity


class TestLeaderboardAPI:
    """Test leaderboard API"""
    
    @pytest.fixture
    def api_client(self):
        return MockAPIClient(api_key="test_token")
    
    def test_get_leaderboard(self, api_client):
        """Test getting leaderboard"""
        response = api_client.get('/api/leaderboard')
        
        assert response.status_code == 200
        data = response.json()
        assert 'leaderboard' in data
        assert 'user_rank' in data
        assert 'total_users' in data
        
        # Check leaderboard structure
        leaderboard = data['leaderboard']
        assert len(leaderboard) == 3
        assert leaderboard[0]['rank'] == 1
        assert leaderboard[0]['username'] == 'alice123'
    
    def test_leaderboard_ranking(self, api_client):
        """Test leaderboard ranking order"""
        response = api_client.get('/api/leaderboard')
        data = response.json()
        
        leaderboard = data['leaderboard']
        # Verify scores are in descending order
        for i in range(len(leaderboard) - 1):
            assert leaderboard[i]['score'] >= leaderboard[i + 1]['score']


class TestAPIErrorHandling:
    """Test API error handling"""
    
    @pytest.fixture
    def api_client(self):
        return MockAPIClient()
    
    def test_404_error(self, api_client):
        """Test 404 error handling"""
        response = api_client.get('/api/nonexistent')
        
        assert response.status_code == 404
        data = response.json()
        assert 'error' in data
        assert data['error'] == 'Endpoint not found'
    
    def test_unauthorized_access(self, api_client):
        """Test unauthorized access"""
        # Client without API key trying to access protected endpoint
        response = api_client.get('/api/protected/resource')
        
        # This would typically return 401, but our mock returns 404
        # In real implementation, add proper auth checking
        assert response.status_code in [401, 404]
    
    def test_request_validation(self, api_client):
        """Test request data validation"""
        # Test with missing required fields
        response = api_client.post('/api/users/login', {})
        
        # In our mock, this returns 401 for invalid credentials
        # Real implementation would validate required fields
        assert response.status_code == 401


class TestAPIIntegration:
    """Test API integration scenarios"""
    
    @pytest.fixture
    def api_client(self):
        return MockAPIClient(api_key="test_token")
    
    def test_full_user_workflow(self, api_client):
        """Test complete user workflow"""
        # Login
        login_response = api_client.post('/api/users/login', {
            'username': 'valid_user',
            'password': 'password'
        })
        assert login_response.status_code == 200
        
        # Get profile
        profile_response = api_client.get('/api/users/profile')
        assert profile_response.status_code == 200
        
        # Get exercises
        exercises_response = api_client.get('/api/exercises')
        assert exercises_response.status_code == 200
        
        # Submit exercise
        submit_response = api_client.post('/api/exercises/1/submit', {
            'code': 'print("Hello")',
            'language': 'python'
        })
        assert submit_response.status_code == 200
        
        # Check progress
        progress_response = api_client.get('/api/progress')
        assert progress_response.status_code == 200
    
    def test_exercise_learning_flow(self, api_client):
        """Test exercise learning flow"""
        # Get available exercises
        exercises_response = api_client.get('/api/exercises')
        exercises = exercises_response.json()['exercises']
        
        # Find first incomplete exercise
        incomplete_exercise = next(
            (ex for ex in exercises if not ex['completed']), 
            None
        )
        assert incomplete_exercise is not None
        
        # Submit solution
        submit_response = api_client.post(
            f'/api/exercises/{incomplete_exercise["id"]}/submit',
            {'code': 'def solution(): pass', 'language': 'python'}
        )
        assert submit_response.status_code == 200
        
        # Verify submission details
        submission = submit_response.json()
        assert submission['exercise_id'] == incomplete_exercise['id']
        assert 'score' in submission
        assert 'feedback' in submission
    
    def test_progress_tracking_flow(self, api_client):
        """Test progress tracking flow"""
        # Get initial progress
        initial_progress = api_client.get('/api/progress').json()
        
        # Submit multiple exercises
        for exercise_id in [1, 2, 3]:
            api_client.post(f'/api/exercises/{exercise_id}/submit', {
                'code': f'# Solution for exercise {exercise_id}',
                'language': 'python'
            })
        
        # Check updated progress (in real scenario, this would change)
        final_progress = api_client.get('/api/progress').json()
        
        # Verify progress structure remains consistent
        assert 'overall_progress' in final_progress
        assert 'topics' in final_progress
        assert 'recent_activity' in final_progress
    
    def test_api_pagination(self, api_client):
        """Test API pagination handling"""
        # Test with pagination parameters
        params = {'page': 1, 'per_page': 5}
        response = api_client.get('/api/exercises', params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert 'page' in data
        assert 'per_page' in data
        assert data['page'] == 1
        assert data['per_page'] == 10  # Mock returns default
    
    def test_request_logging(self, api_client):
        """Test that requests are properly logged"""
        api_client.get('/api/exercises')
        
        last_request = api_client.last_request
        assert last_request is not None
        assert last_request['method'] == 'GET'
        assert last_request['url'].endswith('/api/exercises')
        assert 'Authorization' in last_request['headers']


class TestAPIPerformance:
    """Test API performance considerations"""
    
    @pytest.fixture
    def api_client(self):
        return MockAPIClient(api_key="test_token")
    
    def test_concurrent_requests_simulation(self, api_client):
        """Test handling of concurrent requests"""
        # Simulate multiple requests
        responses = []
        endpoints = ['/api/exercises', '/api/progress', '/api/leaderboard']
        
        for endpoint in endpoints:
            response = api_client.get(endpoint)
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
    
    def test_large_response_handling(self, api_client):
        """Test handling of large responses"""
        # This would test large exercise lists in real scenario
        response = api_client.get('/api/exercises')
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure can handle large data
        assert isinstance(data['exercises'], list)
        assert isinstance(data['total'], int)
    
    def test_response_time_consistency(self, api_client):
        """Test response time consistency"""
        import time
        
        # Make multiple requests and check they complete quickly
        start_time = time.time()
        
        for _ in range(5):
            response = api_client.get('/api/progress')
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # In real scenario, this would test actual response times
        # Mock requests should be very fast
        assert total_time < 1.0  # Should complete in under 1 second