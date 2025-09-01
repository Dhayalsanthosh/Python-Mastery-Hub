# tests/unit/web/test_middleware.py
"""
Test module for web application middleware.
Tests authentication, authorization, request processing, and security middleware.
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Optional


class MockRequest:
    """Mock HTTP request for testing"""
    
    def __init__(self, method='GET', path='/', headers=None, body=None, 
                 user=None, session=None, remote_addr='127.0.0.1'):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body
        self.user = user
        self.session = session or {}
        self.remote_addr = remote_addr
        self.start_time = time.time()
        self.context = {}
    
    def get_header(self, name, default=None):
        """Get request header"""
        return self.headers.get(name.lower(), default)
    
    def get_json(self):
        """Get JSON body"""
        if self.body:
            return json.loads(self.body)
        return {}


class MockResponse:
    """Mock HTTP response for testing"""
    
    def __init__(self, status_code=200, headers=None, body=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body
        self.content_type = 'application/json'
    
    def set_header(self, name, value):
        """Set response header"""
        self.headers[name] = value
    
    def set_cookie(self, name, value, expires=None, secure=False, httponly=False):
        """Set response cookie"""
        cookie = f"{name}={value}"
        if expires:
            cookie += f"; Expires={expires}"
        if secure:
            cookie += "; Secure"
        if httponly:
            cookie += "; HttpOnly"
        
        if 'Set-Cookie' not in self.headers:
            self.headers['Set-Cookie'] = []
        self.headers['Set-Cookie'].append(cookie)


class MockAuthenticationMiddleware:
    """Mock authentication middleware for testing"""
    
    def __init__(self, secret_key="test_secret"):
        self.secret_key = secret_key
        self.sessions = {}
    
    async def __call__(self, request, call_next):
        """Process authentication middleware"""
        # Check for session token
        session_token = request.get_header('authorization')
        if session_token and session_token.startswith('Bearer '):
            token = session_token[7:]  # Remove 'Bearer ' prefix
            user = self._verify_token(token)
            if user:
                request.user = user
                request.context['authenticated'] = True
            else:
                request.context['auth_error'] = 'Invalid token'
        
        # Check for session cookie
        elif 'session_id' in request.session:
            session_id = request.session['session_id']
            if session_id in self.sessions:
                session_data = self.sessions[session_id]
                if session_data['expires'] > datetime.now():
                    request.user = session_data['user']
                    request.context['authenticated'] = True
                else:
                    # Session expired
                    del self.sessions[session_id]
                    request.context['auth_error'] = 'Session expired'
        
        response = await call_next(request)
        return response
    
    def _verify_token(self, token):
        """Verify JWT token (mock implementation)"""
        # Mock token verification
        if token == 'valid_token':
            return {
                'id': 123,
                'username': 'testuser',
                'role': 'student',
                'permissions': ['read', 'write']
            }
        elif token == 'admin_token':
            return {
                'id': 1,
                'username': 'admin',
                'role': 'admin',
                'permissions': ['read', 'write', 'admin']
            }
        return None
    
    def create_session(self, user, expires_in_hours=24):
        """Create user session"""
        session_id = f"session_{user['id']}_{int(time.time())}"
        expires = datetime.now() + timedelta(hours=expires_in_hours)
        
        self.sessions[session_id] = {
            'user': user,
            'created_at': datetime.now(),
            'expires': expires
        }
        
        return session_id


class MockAuthorizationMiddleware:
    """Mock authorization middleware for testing"""
    
    def __init__(self, permissions_map=None):
        self.permissions_map = permissions_map or {
            '/api/admin': ['admin'],
            '/api/exercises/create': ['admin', 'instructor'],
            '/api/exercises/edit': ['admin', 'instructor'],
            '/api/users/profile': ['read'],
            '/api/exercises/submit': ['write'],
        }
    
    async def __call__(self, request, call_next):
        """Process authorization middleware"""
        # Skip authorization for public endpoints
        if self._is_public_endpoint(request.path):
            return await call_next(request)
        
        # Check if user is authenticated
        if not hasattr(request, 'user') or request.user is None:
            return MockResponse(401, body='{"error": "Authentication required"}')
        
        # Check permissions
        required_permissions = self._get_required_permissions(request.path, request.method)
        if required_permissions and not self._has_permission(request.user, required_permissions):
            return MockResponse(403, body='{"error": "Insufficient permissions"}')
        
        response = await call_next(request)
        return response
    
    def _is_public_endpoint(self, path):
        """Check if endpoint is public"""
        public_endpoints = [
            '/api/auth/login',
            '/api/auth/register',
            '/api/exercises',  # GET only
            '/health',
            '/docs'
        ]
        return any(path.startswith(endpoint) for endpoint in public_endpoints)
    
    def _get_required_permissions(self, path, method):
        """Get required permissions for path and method"""
        # Check exact path match first
        if path in self.permissions_map:
            return self.permissions_map[path]
        
        # Check pattern matches
        for pattern, permissions in self.permissions_map.items():
            if path.startswith(pattern):
                return permissions
        
        # Default permissions based on method
        if method in ['POST', 'PUT', 'DELETE']:
            return ['write']
        return ['read']
    
    def _has_permission(self, user, required_permissions):
        """Check if user has required permissions"""
        user_permissions = user.get('permissions', [])
        user_role = user.get('role', '')
        
        # Admin has all permissions
        if user_role == 'admin' or 'admin' in user_permissions:
            return True
        
        # Check if user has any of the required permissions
        return any(perm in user_permissions for perm in required_permissions)


class MockRateLimitMiddleware:
    """Mock rate limiting middleware for testing"""
    
    def __init__(self, max_requests=100, window_seconds=3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {ip: [(timestamp, count), ...]}
    
    async def __call__(self, request, call_next):
        """Process rate limiting middleware"""
        client_ip = request.remote_addr
        current_time = time.time()
        
        # Clean old entries
        self._clean_old_entries(client_ip, current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            return MockResponse(
                429, 
                headers={'Retry-After': str(self.window_seconds)},
                body='{"error": "Rate limit exceeded"}'
            )
        
        # Record request
        self._record_request(client_ip, current_time)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_requests(client_ip, current_time)
        response.set_header('X-RateLimit-Limit', str(self.max_requests))
        response.set_header('X-RateLimit-Remaining', str(remaining))
        response.set_header('X-RateLimit-Window', str(self.window_seconds))
        
        return response
    
    def _clean_old_entries(self, client_ip, current_time):
        """Remove old entries outside the window"""
        if client_ip in self.requests:
            cutoff_time = current_time - self.window_seconds
            self.requests[client_ip] = [
                (timestamp, count) for timestamp, count in self.requests[client_ip]
                if timestamp > cutoff_time
            ]
    
    def _is_rate_limited(self, client_ip, current_time):
        """Check if client is rate limited"""
        if client_ip not in self.requests:
            return False
        
        total_requests = sum(count for _, count in self.requests[client_ip])
        return total_requests >= self.max_requests
    
    def _record_request(self, client_ip, current_time):
        """Record a request"""
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        self.requests[client_ip].append((current_time, 1))
    
    def _get_remaining_requests(self, client_ip, current_time):
        """Get remaining requests for client"""
        if client_ip not in self.requests:
            return self.max_requests
        
        used_requests = sum(count for _, count in self.requests[client_ip])
        return max(0, self.max_requests - used_requests)


class MockCORSMiddleware:
    """Mock CORS middleware for testing"""
    
    def __init__(self, allowed_origins=None, allowed_methods=None, 
                 allowed_headers=None, max_age=86400):
        self.allowed_origins = allowed_origins or ['*']
        self.allowed_methods = allowed_methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.allowed_headers = allowed_headers or ['Content-Type', 'Authorization']
        self.max_age = max_age
    
    async def __call__(self, request, call_next):
        """Process CORS middleware"""
        origin = request.get_header('origin')
        
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = MockResponse(200)
            self._add_cors_headers(response, origin)
            return response
        
        response = await call_next(request)
        self._add_cors_headers(response, origin)
        
        return response
    
    def _add_cors_headers(self, response, origin):
        """Add CORS headers to response"""
        # Check if origin is allowed
        if self._is_origin_allowed(origin):
            response.set_header('Access-Control-Allow-Origin', origin or '*')
        
        response.set_header('Access-Control-Allow-Methods', ', '.join(self.allowed_methods))
        response.set_header('Access-Control-Allow-Headers', ', '.join(self.allowed_headers))
        response.set_header('Access-Control-Max-Age', str(self.max_age))
        response.set_header('Access-Control-Allow-Credentials', 'true')
    
    def _is_origin_allowed(self, origin):
        """Check if origin is allowed"""
        if '*' in self.allowed_origins:
            return True
        return origin in self.allowed_origins


class MockLoggingMiddleware:
    """Mock logging middleware for testing"""
    
    def __init__(self):
        self.logs = []
    
    async def __call__(self, request, call_next):
        """Process logging middleware"""
        start_time = time.time()
        
        # Log request
        self._log_request(request)
        
        response = await call_next(request)
        
        # Log response
        end_time = time.time()
        duration = end_time - start_time
        self._log_response(request, response, duration)
        
        return response
    
    def _log_request(self, request):
        """Log incoming request"""
        log_entry = {
            'type': 'request',
            'timestamp': datetime.now(),
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.get_header('user-agent'),
            'user_id': getattr(request, 'user', {}).get('id') if hasattr(request, 'user') else None
        }
        self.logs.append(log_entry)
    
    def _log_response(self, request, response, duration):
        """Log response"""
        log_entry = {
            'type': 'response',
            'timestamp': datetime.now(),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'remote_addr': request.remote_addr
        }
        self.logs.append(log_entry)
    
    def get_logs(self, log_type=None, limit=None):
        """Get logs with optional filtering"""
        logs = self.logs
        
        if log_type:
            logs = [log for log in logs if log['type'] == log_type]
        
        if limit:
            logs = logs[-limit:]
        
        return logs


class TestAuthenticationMiddleware:
    """Test authentication middleware functionality"""
    
    @pytest.fixture
    def auth_middleware(self):
        return MockAuthenticationMiddleware()
    
    @pytest.fixture
    def mock_next(self):
        async def call_next(request):
            return MockResponse(200, body='{"message": "success"}')
        return call_next
    
    @pytest.mark.asyncio
    async def test_valid_bearer_token(self, auth_middleware, mock_next):
        """Test authentication with valid bearer token"""
        request = MockRequest(
            headers={'authorization': 'Bearer valid_token'}
        )
        
        response = await auth_middleware(request, mock_next)
        
        assert hasattr(request, 'user')
        assert request.user['username'] == 'testuser'
        assert request.context['authenticated'] is True
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_invalid_bearer_token(self, auth_middleware, mock_next):
        """Test authentication with invalid bearer token"""
        request = MockRequest(
            headers={'authorization': 'Bearer invalid_token'}
        )
        
        response = await auth_middleware(request, mock_next)
        
        assert not hasattr(request, 'user') or request.user is None
        assert 'auth_error' in request.context
        assert request.context['auth_error'] == 'Invalid token'
    
    @pytest.mark.asyncio
    async def test_session_authentication(self, auth_middleware, mock_next):
        """Test authentication with session"""
        user = {'id': 123, 'username': 'testuser', 'role': 'student'}
        session_id = auth_middleware.create_session(user)
        
        request = MockRequest(session={'session_id': session_id})
        
        response = await auth_middleware(request, mock_next)
        
        assert hasattr(request, 'user')
        assert request.user['username'] == 'testuser'
        assert request.context['authenticated'] is True
    
    @pytest.mark.asyncio
    async def test_expired_session(self, auth_middleware, mock_next):
        """Test authentication with expired session"""
        user = {'id': 123, 'username': 'testuser', 'role': 'student'}
        session_id = auth_middleware.create_session(user, expires_in_hours=-1)  # Expired
        
        request = MockRequest(session={'session_id': session_id})
        
        response = await auth_middleware(request, mock_next)
        
        assert not hasattr(request, 'user') or request.user is None
        assert 'auth_error' in request.context
        assert request.context['auth_error'] == 'Session expired'
    
    @pytest.mark.asyncio
    async def test_no_authentication(self, auth_middleware, mock_next):
        """Test request without authentication"""
        request = MockRequest()
        
        response = await auth_middleware(request, mock_next)
        
        assert not hasattr(request, 'user') or request.user is None
        assert 'authenticated' not in request.context
        assert response.status_code == 200  # Should still proceed


class TestAuthorizationMiddleware:
    """Test authorization middleware functionality"""
    
    @pytest.fixture
    def auth_middleware(self):
        return MockAuthorizationMiddleware()
    
    @pytest.fixture
    def mock_next(self):
        async def call_next(request):
            return MockResponse(200, body='{"message": "success"}')
        return call_next
    
    @pytest.mark.asyncio
    async def test_public_endpoint_access(self, auth_middleware, mock_next):
        """Test access to public endpoint"""
        request = MockRequest(path='/api/auth/login')
        
        response = await auth_middleware(request, mock_next)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_authenticated_user_access(self, auth_middleware, mock_next):
        """Test access with authenticated user"""
        request = MockRequest(
            path='/api/users/profile',
            user={'id': 123, 'role': 'student', 'permissions': ['read']}
        )
        
        response = await auth_middleware(request, mock_next)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_unauthenticated_user_access(self, auth_middleware, mock_next):
        """Test access without authentication"""
        request = MockRequest(path='/api/users/profile')
        
        response = await auth_middleware(request, mock_next)
        
        assert response.status_code == 401
        assert '"error": "Authentication required"' in response.body
    
    @pytest.mark.asyncio
    async def test_insufficient_permissions(self, auth_middleware, mock_next):
        """Test access with insufficient permissions"""
        request = MockRequest(
            path='/api/admin',
            user={'id': 123, 'role': 'student', 'permissions': ['read']}
        )
        
        response = await auth_middleware(request, mock_next)
        
        assert response.status_code == 403
        assert '"error": "Insufficient permissions"' in response.body
    
    @pytest.mark.asyncio
    async def test_admin_access(self, auth_middleware, mock_next):
        """Test admin access to protected endpoint"""
        request = MockRequest(
            path='/api/admin',
            user={'id': 1, 'role': 'admin', 'permissions': ['admin']}
        )
        
        response = await auth_middleware(request, mock_next)
        
        assert response.status_code == 200


class TestRateLimitMiddleware:
    """Test rate limiting middleware functionality"""
    
    @pytest.fixture
    def rate_limit_middleware(self):
        return MockRateLimitMiddleware(max_requests=5, window_seconds=60)
    
    @pytest.fixture
    def mock_next(self):
        async def call_next(request):
            return MockResponse(200, body='{"message": "success"}')
        return call_next
    
    @pytest.mark.asyncio
    async def test_within_rate_limit(self, rate_limit_middleware, mock_next):
        """Test request within rate limit"""
        request = MockRequest(remote_addr='192.168.1.1')
        
        response = await rate_limit_middleware(request, mock_next)
        
        assert response.status_code == 200
        assert 'X-RateLimit-Limit' in response.headers
        assert 'X-RateLimit-Remaining' in response.headers
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, rate_limit_middleware, mock_next):
        """Test rate limit exceeded"""
        request = MockRequest(remote_addr='192.168.1.2')
        
        # Make requests up to the limit
        for _ in range(5):
            await rate_limit_middleware(request, mock_next)
        
        # This should be rate limited
        response = await rate_limit_middleware(request, mock_next)
        
        assert response.status_code == 429
        assert '"error": "Rate limit exceeded"' in response.body
        assert 'Retry-After' in response.headers
    
    @pytest.mark.asyncio
    async def test_different_ips_separate_limits(self, rate_limit_middleware, mock_next):
        """Test that different IPs have separate rate limits"""
        request1 = MockRequest(remote_addr='192.168.1.3')
        request2 = MockRequest(remote_addr='192.168.1.4')
        
        # Exhaust limit for first IP
        for _ in range(5):
            await rate_limit_middleware(request1, mock_next)
        
        # Second IP should still work
        response = await rate_limit_middleware(request2, mock_next)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, rate_limit_middleware, mock_next):
        """Test rate limit headers"""
        request = MockRequest(remote_addr='192.168.1.5')
        
        response = await rate_limit_middleware(request, mock_next)
        
        assert response.headers['X-RateLimit-Limit'] == '5'
        assert int(response.headers['X-RateLimit-Remaining']) == 4
        assert response.headers['X-RateLimit-Window'] == '60'


class TestCORSMiddleware:
    """Test CORS middleware functionality"""
    
    @pytest.fixture
    def cors_middleware(self):
        return MockCORSMiddleware(
            allowed_origins=['https://example.com', 'https://app.example.com'],
            allowed_methods=['GET', 'POST', 'PUT', 'DELETE'],
            allowed_headers=['Content-Type', 'Authorization']
        )
    
    @pytest.fixture
    def mock_next(self):
        async def call_next(request):
            return MockResponse(200, body='{"message": "success"}')
        return call_next
    
    @pytest.mark.asyncio
    async def test_preflight_request(self, cors_middleware, mock_next):
        """Test CORS preflight request"""
        request = MockRequest(
            method='OPTIONS',
            headers={'origin': 'https://example.com'}
        )
        
        response = await cors_middleware(request, mock_next)
        
        assert response.status_code == 200
        assert response.headers['Access-Control-Allow-Origin'] == 'https://example.com'
        assert 'GET, POST, PUT, DELETE' in response.headers['Access-Control-Allow-Methods']
        assert 'Content-Type, Authorization' in response.headers['Access-Control-Allow-Headers']
    
    @pytest.mark.asyncio
    async def test_cors_headers_added(self, cors_middleware, mock_next):
        """Test CORS headers added to regular request"""
        request = MockRequest(
            method='GET',
            headers={'origin': 'https://example.com'}
        )
        
        response = await cors_middleware(request, mock_next)
        
        assert response.status_code == 200
        assert response.headers['Access-Control-Allow-Origin'] == 'https://example.com'
        assert 'Access-Control-Allow-Methods' in response.headers
    
    @pytest.mark.asyncio
    async def test_disallowed_origin(self, cors_middleware, mock_next):
        """Test request from disallowed origin"""
        request = MockRequest(
            method='GET',
            headers={'origin': 'https://malicious.com'}
        )
        
        response = await cors_middleware(request, mock_next)
        
        assert response.status_code == 200
        # Should not include CORS headers for disallowed origin
        assert 'Access-Control-Allow-Origin' not in response.headers
    
    @pytest.mark.asyncio
    async def test_wildcard_origin(self, mock_next):
        """Test wildcard origin"""
        cors_middleware = MockCORSMiddleware(allowed_origins=['*'])
        request = MockRequest(
            method='GET',
            headers={'origin': 'https://any-domain.com'}
        )
        
        response = await cors_middleware(request, mock_next)
        
        assert response.status_code == 200
        assert response.headers['Access-Control-Allow-Origin'] == 'https://any-domain.com'


class TestLoggingMiddleware:
    """Test logging middleware functionality"""
    
    @pytest.fixture
    def logging_middleware(self):
        return MockLoggingMiddleware()
    
    @pytest.fixture
    def mock_next(self):
        async def call_next(request):
            await asyncio.sleep(0.01)  # Simulate processing time
            return MockResponse(200, body='{"message": "success"}')
        return call_next
    
    @pytest.mark.asyncio
    async def test_request_response_logging(self, logging_middleware, mock_next):
        """Test request and response logging"""
        request = MockRequest(
            method='POST',
            path='/api/exercises',
            headers={'user-agent': 'test-client/1.0'},
            remote_addr='192.168.1.10'
        )
        
        response = await logging_middleware(request, mock_next)
        
        logs = logging_middleware.get_logs()
        
        assert len(logs) == 2  # Request and response logs
        
        request_log = logs[0]
        assert request_log['type'] == 'request'
        assert request_log['method'] == 'POST'
        assert request_log['path'] == '/api/exercises'
        assert request_log['remote_addr'] == '192.168.1.10'
        
        response_log = logs[1]
        assert response_log['type'] == 'response'
        assert response_log['status_code'] == 200
        assert response_log['duration_ms'] > 0
    
    @pytest.mark.asyncio
    async def test_authenticated_user_logging(self, logging_middleware, mock_next):
        """Test logging with authenticated user"""
        request = MockRequest(
            user={'id': 123, 'username': 'testuser'}
        )
        
        response = await logging_middleware(request, mock_next)
        
        logs = logging_middleware.get_logs(log_type='request')
        assert len(logs) == 1
        assert logs[0]['user_id'] == 123
    
    def test_log_filtering(self, logging_middleware):
        """Test log filtering functionality"""
        # Manually add logs for testing
        logging_middleware.logs = [
            {'type': 'request', 'timestamp': datetime.now()},
            {'type': 'response', 'timestamp': datetime.now()},
            {'type': 'request', 'timestamp': datetime.now()},
        ]
        
        request_logs = logging_middleware.get_logs(log_type='request')
        assert len(request_logs) == 2
        
        limited_logs = logging_middleware.get_logs(limit=2)
        assert len(limited_logs) == 2


class TestMiddlewareIntegration:
    """Test middleware integration and chaining"""
    
    @pytest.fixture
    def middleware_stack(self):
        return [
            MockLoggingMiddleware(),
            MockCORSMiddleware(),
            MockRateLimitMiddleware(max_requests=10, window_seconds=60),
            MockAuthenticationMiddleware(),
            MockAuthorizationMiddleware()
        ]
    
    @pytest.fixture
    def mock_next(self):
        async def call_next(request):
            return MockResponse(200, body='{"message": "success"}')
        return call_next
    
    @pytest.mark.asyncio
    async def test_middleware_chain_execution(self, middleware_stack, mock_next):
        """Test complete middleware chain execution"""
        async def process_request(request):
            handler = mock_next
            # Process middleware in reverse order (like a stack)
            for middleware in reversed(middleware_stack):
                current_handler = handler
                handler = lambda req, middleware=middleware, next_handler=current_handler: middleware(req, next_handler)
            return await handler(request)
        
        request = MockRequest(
            method='GET',
            path='/api/exercises',
            headers={
                'authorization': 'Bearer valid_token',
                'origin': 'https://example.com'
            },
            remote_addr='192.168.1.100'
        )
        
        response = await process_request(request)
        
        assert response.status_code == 200
        
        # Check that all middleware processed the request
        logging_middleware = middleware_stack[0]
        logs = logging_middleware.get_logs()
        assert len(logs) >= 2  # At least request and response logs
        
        # Check CORS headers
        assert 'Access-Control-Allow-Methods' in response.headers
        
        # Check rate limit headers
        assert 'X-RateLimit-Remaining' in response.headers
        
        # Check authentication worked
        assert hasattr(request, 'user')
        assert request.user['username'] == 'testuser'
    
    @pytest.mark.asyncio
    async def test_middleware_error_handling(self, middleware_stack, mock_next):
        """Test middleware error handling"""
        async def process_request(request):
            handler = mock_next
            for middleware in reversed(middleware_stack):
                current_handler = handler
                handler = lambda req, middleware=middleware, next_handler=current_handler: middleware(req, next_handler)
            return await handler(request)
        
        # Request that should be blocked by authorization
        request = MockRequest(
            method='POST',
            path='/api/admin',
            headers={'origin': 'https://example.com'},
            remote_addr='192.168.1.101'
        )
        # No authentication token
        
        response = await process_request(request)
        
        # Should be blocked by authorization middleware
        assert response.status_code == 401
        
        # But other middleware should still have processed
        logging_middleware = middleware_stack[0]
        logs = logging_middleware.get_logs()
        assert len(logs) >= 1  # Should have logged the request
    
    @pytest.mark.asyncio
    async def test_rate_limit_in_chain(self, middleware_stack, mock_next):
        """Test rate limiting in middleware chain"""
        async def process_request(request):
            handler = mock_next
            for middleware in reversed(middleware_stack):
                current_handler = handler
                handler = lambda req, middleware=middleware, next_handler=current_handler: middleware(req, next_handler)
            return await handler(request)
        
        base_request = MockRequest(
            method='GET',
            path='/api/exercises',
            headers={
                'authorization': 'Bearer valid_token',
                'origin': 'https://example.com'
            },
            remote_addr='192.168.1.102'
        )
        
        # Make requests up to rate limit
        rate_limit_middleware = next(m for m in middleware_stack if isinstance(m, MockRateLimitMiddleware))
        max_requests = rate_limit_middleware.max_requests
        
        for i in range(max_requests):
            request = MockRequest(
                method='GET',
                path='/api/exercises',
                headers=base_request.headers,
                remote_addr=base_request.remote_addr
            )
            response = await process_request(request)
            assert response.status_code == 200
        
        # Next request should be rate limited
        request = MockRequest(
            method='GET',
            path='/api/exercises',
            headers=base_request.headers,
            remote_addr=base_request.remote_addr
        )
        response = await process_request(request)
        assert response.status_code == 429