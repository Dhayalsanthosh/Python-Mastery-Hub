# tests/performance/benchmarks/api_benchmarks.py
"""
API performance benchmarks for the Python learning platform.
Tests REST API endpoints, authentication, request/response handling,
and various API usage patterns under different load conditions.
"""
import asyncio
import aiohttp
import time
import json
import random
import string
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import concurrent.futures
from urllib.parse import urljoin
import ssl
import certifi

from .benchmark_runner import BenchmarkRunner, BenchmarkConfig, benchmark, async_benchmark


@dataclass
class APIMetrics:
    """Metrics for API performance."""
    response_time: float
    status_code: int
    response_size_bytes: int
    request_size_bytes: int
    connection_time: Optional[float] = None
    dns_lookup_time: Optional[float] = None
    ssl_handshake_time: Optional[float] = None


class MockAPIServer:
    """Mock API server for benchmarking purposes."""
    
    def __init__(self):
        self.request_count = 0
        self.active_sessions = {}
        self.response_delays = {}
        self.error_rates = {}
        self.rate_limits = {}
        
    async def handle_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None) -> Dict[str, Any]:
        """Handle API request with simulated processing."""
        self.request_count += 1
        
        # Simulate processing delay based on endpoint
        delay = self._get_endpoint_delay(endpoint)
        await asyncio.sleep(delay)
        
        # Check rate limiting
        if self._is_rate_limited(endpoint):
            return {
                "status_code": 429,
                "data": {"error": "Rate limit exceeded"},
                "headers": {"Retry-After": "60"}
            }
        
        # Simulate endpoint-specific logic
        if endpoint == "/auth/login":
            return await self._handle_login(data)
        elif endpoint == "/auth/logout":
            return await self._handle_logout(headers)
        elif endpoint.startswith("/users/"):
            return await self._handle_user_operations(method, endpoint, data)
        elif endpoint.startswith("/courses/"):
            return await self._handle_course_operations(method, endpoint, data)
        elif endpoint.startswith("/submissions/"):
            return await self._handle_submission_operations(method, endpoint, data)
        elif endpoint == "/health":
            return await self._handle_health_check()
        else:
            return {
                "status_code": 404,
                "data": {"error": "Endpoint not found"},
                "headers": {}
            }
    
    def _get_endpoint_delay(self, endpoint: str) -> float:
        """Get simulated processing delay for endpoint."""
        base_delays = {
            "/auth/login": 0.1,
            "/auth/logout": 0.05,
            "/users/": 0.02,
            "/courses/": 0.03,
            "/submissions/": 0.15,  # Code execution takes longer
            "/health": 0.001
        }
        
        base_delay = 0.02  # Default delay
        for prefix, delay in base_delays.items():
            if endpoint.startswith(prefix):
                base_delay = delay
                break
        
        # Add load-based delay
        load_factor = min(self.request_count / 1000, 2.0)
        return base_delay * (1 + load_factor * 0.5)
    
    def _is_rate_limited(self, endpoint: str) -> bool:
        """Check if endpoint is rate limited."""
        # Simulate rate limiting for submission endpoints
        if endpoint.startswith("/submissions/"):
            return random.random() < 0.02  # 2% chance
        return False
    
    async def _handle_login(self, data: dict) -> Dict[str, Any]:
        """Handle login request."""
        if not data or "username" not in data or "password" not in data:
            return {
                "status_code": 400,
                "data": {"error": "Missing credentials"},
                "headers": {}
            }
        
        # Simulate authentication
        if random.random() < 0.95:  # 95% success rate
            token = f"token_{data['username']}_{int(time.time())}"
            self.active_sessions[token] = {
                "username": data["username"],
                "created_at": time.time(),
                "expires_at": time.time() + 3600
            }
            
            return {
                "status_code": 200,
                "data": {
                    "token": token,
                    "user_id": hash(data["username"]) % 10000,
                    "expires_in": 3600
                },
                "headers": {"Set-Cookie": f"auth_token={token}; HttpOnly"}
            }
        else:
            return {
                "status_code": 401,
                "data": {"error": "Invalid credentials"},
                "headers": {}
            }
    
    async def _handle_logout(self, headers: dict) -> Dict[str, Any]:
        """Handle logout request."""
        token = self._extract_token(headers)
        if token and token in self.active_sessions:
            del self.active_sessions[token]
            return {
                "status_code": 200,
                "data": {"message": "Logged out successfully"},
                "headers": {}
            }
        else:
            return {
                "status_code": 401,
                "data": {"error": "Invalid token"},
                "headers": {}
            }
    
    async def _handle_user_operations(self, method: str, endpoint: str, data: dict) -> Dict[str, Any]:
        """Handle user-related operations."""
        if method == "GET":
            if "/profile" in endpoint:
                return {
                    "status_code": 200,
                    "data": {
                        "id": random.randint(1, 10000),
                        "username": f"user_{random.randint(1, 1000)}",
                        "email": f"user{random.randint(1, 1000)}@example.com",
                        "created_at": "2024-01-01T00:00:00Z"
                    },
                    "headers": {}
                }
            else:
                # List users
                users = [
                    {
                        "id": i,
                        "username": f"user_{i}",
                        "email": f"user{i}@example.com"
                    }
                    for i in range(1, random.randint(10, 50))
                ]
                return {
                    "status_code": 200,
                    "data": {"users": users, "total": len(users)},
                    "headers": {}
                }
        
        elif method == "POST":
            return {
                "status_code": 201,
                "data": {
                    "id": random.randint(1, 10000),
                    "message": "User created successfully"
                },
                "headers": {}
            }
        
        elif method == "PUT":
            return {
                "status_code": 200,
                "data": {"message": "User updated successfully"},
                "headers": {}
            }
        
        elif method == "DELETE":
            return {
                "status_code": 200,
                "data": {"message": "User deleted successfully"},
                "headers": {}
            }
        
        return {"status_code": 405, "data": {"error": "Method not allowed"}, "headers": {}}
    
    async def _handle_course_operations(self, method: str, endpoint: str, data: dict) -> Dict[str, Any]:
        """Handle course-related operations."""
        if method == "GET":
            courses = [
                {
                    "id": i,
                    "title": f"Python Course {i}",
                    "description": f"Description for course {i}",
                    "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                    "enrolled_count": random.randint(10, 500)
                }
                for i in range(1, random.randint(20, 100))
            ]
            return {
                "status_code": 200,
                "data": {"courses": courses, "total": len(courses)},
                "headers": {}
            }
        
        return {"status_code": 405, "data": {"error": "Method not allowed"}, "headers": {}}
    
    async def _handle_submission_operations(self, method: str, endpoint: str, data: dict) -> Dict[str, Any]:
        """Handle submission-related operations."""
        if method == "POST":
            # Simulate code execution time
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            return {
                "status_code": 200,
                "data": {
                    "submission_id": f"sub_{random.randint(1, 100000)}",
                    "score": random.randint(60, 100),
                    "execution_time": random.uniform(0.1, 1.0),
                    "test_results": [
                        {"test_id": f"test_{i}", "passed": random.random() > 0.2}
                        for i in range(random.randint(3, 8))
                    ]
                },
                "headers": {}
            }
        
        elif method == "GET":
            submissions = [
                {
                    "id": f"sub_{i}",
                    "exercise_id": f"ex_{random.randint(1, 100)}",
                    "score": random.randint(60, 100),
                    "submitted_at": "2024-01-01T00:00:00Z"
                }
                for i in range(1, random.randint(10, 50))
            ]
            return {
                "status_code": 200,
                "data": {"submissions": submissions, "total": len(submissions)},
                "headers": {}
            }
        
        return {"status_code": 405, "data": {"error": "Method not allowed"}, "headers": {}}
    
    async def _handle_health_check(self) -> Dict[str, Any]:
        """Handle health check request."""
        return {
            "status_code": 200,
            "data": {
                "status": "healthy",
                "timestamp": time.time(),
                "request_count": self.request_count,
                "active_sessions": len(self.active_sessions)
            },
            "headers": {}
        }
    
    def _extract_token(self, headers: dict) -> Optional[str]:
        """Extract authentication token from headers."""
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None


class APIBenchmarks:
    """API performance benchmark suite."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.runner = BenchmarkRunner("api_benchmarks")
        self.base_url = base_url
        self.mock_server = MockAPIServer()
        self.auth_tokens = {}
        
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all API benchmarks."""
        benchmarks = {
            "health_check": (
                BenchmarkConfig("health_check", "Health check endpoint", iterations=100),
                self.benchmark_health_check,
                (),
                {}
            ),
            "authentication": (
                BenchmarkConfig("authentication", "Authentication performance", iterations=50),
                self.benchmark_authentication,
                (),
                {}
            ),
            "user_operations": (
                BenchmarkConfig("user_operations", "User CRUD operations", iterations=40),
                self.benchmark_user_operations,
                (),
                {}
            ),
            "course_listing": (
                BenchmarkConfig("course_listing", "Course listing performance", iterations=60),
                self.benchmark_course_listing,
                (),
                {}
            ),
            "code_submission": (
                BenchmarkConfig("code_submission", "Code submission performance", iterations=20),
                self.benchmark_code_submission,
                (),
                {}
            ),
            "concurrent_requests": (
                BenchmarkConfig("concurrent_requests", "Concurrent request handling", iterations=15),
                self.benchmark_concurrent_requests,
                (),
                {}
            ),
            "payload_sizes": (
                BenchmarkConfig("payload_sizes", "Different payload sizes", iterations=30),
                self.benchmark_payload_sizes,
                (),
                {}
            ),
            "error_handling": (
                BenchmarkConfig("error_handling", "Error response handling", iterations=40),
                self.benchmark_error_handling,
                (),
                {}
            )
        }
        
        return self.runner.run_benchmark_suite(benchmarks)
    
    @async_benchmark("health_check", iterations=100)
    async def benchmark_health_check(self):
        """Benchmark health check endpoint."""
        response = await self.mock_server.handle_request("GET", "/health")
        return response["status_code"]
    
    @async_benchmark("authentication", iterations=50)
    async def benchmark_authentication(self):
        """Benchmark authentication performance."""
        # Login
        login_data = {
            "username": f"benchmark_user_{random.randint(1, 1000)}",
            "password": "password123"
        }
        
        login_response = await self.mock_server.handle_request("POST", "/auth/login", login_data)
        
        if login_response["status_code"] == 200:
            token = login_response["data"]["token"]
            
            # Logout
            headers = {"Authorization": f"Bearer {token}"}
            logout_response = await self.mock_server.handle_request("POST", "/auth/logout", headers=headers)
            
            return 1 if logout_response["status_code"] == 200 else 0
        
        return 0
    
    @async_benchmark("user_operations", iterations=40)
    async def benchmark_user_operations(self):
        """Benchmark user CRUD operations."""
        operations_completed = 0
        
        # Create user
        create_data = {
            "username": f"api_user_{random.randint(1, 10000)}",
            "email": f"apiuser{random.randint(1, 10000)}@example.com",
            "password": "password123"
        }
        
        create_response = await self.mock_server.handle_request("POST", "/users/", create_data)
        if create_response["status_code"] == 201:
            operations_completed += 1
            user_id = create_response["data"]["id"]
            
            # Get user
            get_response = await self.mock_server.handle_request("GET", f"/users/{user_id}/profile")
            if get_response["status_code"] == 200:
                operations_completed += 1
            
            # Update user
            update_data = {"email": f"updated{random.randint(1, 10000)}@example.com"}
            update_response = await self.mock_server.handle_request("PUT", f"/users/{user_id}", update_data)
            if update_response["status_code"] == 200:
                operations_completed += 1
        
        return operations_completed
    
    @async_benchmark("course_listing", iterations=60)
    async def benchmark_course_listing(self):
        """Benchmark course listing performance."""
        response = await self.mock_server.handle_request("GET", "/courses/")
        
        if response["status_code"] == 200:
            return len(response["data"]["courses"])
        
        return 0
    
    @async_benchmark("code_submission", iterations=20)
    async def benchmark_code_submission(self):
        """Benchmark code submission performance."""
        submission_data = {
            "exercise_id": f"exercise_{random.randint(1, 100)}",
            "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Result: {result}")
""",
            "language": "python"
        }
        
        response = await self.mock_server.handle_request("POST", "/submissions/", submission_data)
        
        if response["status_code"] == 200:
            return response["data"]["score"]
        
        return 0
    
    @async_benchmark("concurrent_requests", iterations=15)
    async def benchmark_concurrent_requests(self):
        """Benchmark concurrent request handling."""
        async def make_concurrent_request():
            return await self.mock_server.handle_request("GET", "/health")
        
        # Make 10 concurrent requests
        tasks = [make_concurrent_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        successful_requests = sum(1 for r in responses if r["status_code"] == 200)
        return successful_requests
    
    @async_benchmark("payload_sizes", iterations=30)
    async def benchmark_payload_sizes(self):
        """Benchmark different payload sizes."""
        payload_sizes = [
            ("small", "x" * 100),          # 100 bytes
            ("medium", "x" * 10000),       # 10KB
            ("large", "x" * 100000),       # 100KB
        ]
        
        total_responses = 0
        
        for size_name, payload in payload_sizes:
            submission_data = {
                "exercise_id": f"payload_test_{size_name}",
                "code": f"# {payload}\nprint('Test')",
                "language": "python"
            }
            
            response = await self.mock_server.handle_request("POST", "/submissions/", submission_data)
            if response["status_code"] == 200:
                total_responses += 1
        
        return total_responses
    
    @async_benchmark("error_handling", iterations=40)
    async def benchmark_error_handling(self):
        """Benchmark error response handling."""
        error_scenarios = [
            ("GET", "/nonexistent", None),          # 404
            ("POST", "/auth/login", {}),            # 400 - missing data
            ("GET", "/users/999999", None),         # 404 - user not found
            ("POST", "/auth/logout", None),         # 401 - no token
        ]
        
        handled_errors = 0
        
        for method, endpoint, data in error_scenarios:
            response = await self.mock_server.handle_request(method, endpoint, data)
            if response["status_code"] >= 400:
                handled_errors += 1
        
        return handled_errors
    
    def benchmark_api_response_patterns(self) -> Dict[str, Any]:
        """Benchmark different API response patterns."""
        response_patterns = {
            "json_small": {"type": "small_json", "data_size": 1024},
            "json_large": {"type": "large_json", "data_size": 102400},
            "paginated": {"type": "paginated", "page_size": 50},
            "nested_objects": {"type": "nested", "depth": 5}
        }
        
        results = {}
        
        for pattern_name, config in response_patterns.items():
            print(f"Benchmarking response pattern: {pattern_name}")
            
            async def execute_response_pattern():
                if config["type"] == "small_json":
                    # Small JSON response
                    response = await self.mock_server.handle_request("GET", "/users/1/profile")
                elif config["type"] == "large_json":
                    # Large JSON response (course list)
                    response = await self.mock_server.handle_request("GET", "/courses/")
                elif config["type"] == "paginated":
                    # Paginated response
                    response = await self.mock_server.handle_request("GET", "/courses/?page=1&limit=50")
                else:  # nested_objects
                    # Nested object response
                    response = await self.mock_server.handle_request("GET", "/users/1/progress")
                
                return len(json.dumps(response["data"]).encode('utf-8'))
            
            config_obj = BenchmarkConfig(
                name=f"response_{pattern_name}",
                description=f"Response pattern: {pattern_name}",
                iterations=25
            )
            
            benchmark_result = asyncio.run(
                self.runner.run_benchmark(config_obj, execute_response_pattern)
            )
            
            results[pattern_name] = benchmark_result
        
        return results
    
    def benchmark_authentication_patterns(self) -> Dict[str, Any]:
        """Benchmark different authentication patterns."""
        auth_patterns = {
            "jwt_token": "JWT token authentication",
            "session_cookie": "Session cookie authentication", 
            "api_key": "API key authentication",
            "oauth": "OAuth token authentication"
        }
        
        results = {}
        
        for pattern_name, description in auth_patterns.items():
            print(f"Benchmarking authentication: {pattern_name}")
            
            async def execute_auth_pattern():
                if pattern_name == "jwt_token":
                    # Simulate JWT token validation
                    await asyncio.sleep(0.005)  # JWT parsing/validation time
                elif pattern_name == "session_cookie":
                    # Simulate session lookup
                    await asyncio.sleep(0.002)  # Session store lookup
                elif pattern_name == "api_key":
                    # Simulate API key validation
                    await asyncio.sleep(0.001)  # Simple key lookup
                else:  # oauth
                    # Simulate OAuth token validation
                    await asyncio.sleep(0.010)  # External validation
                
                # Simulate authenticated request
                response = await self.mock_server.handle_request("GET", "/users/profile")
                return response["status_code"]
            
            config = BenchmarkConfig(
                name=f"auth_{pattern_name}",
                description=description,
                iterations=50
            )
            
            benchmark_result = asyncio.run(
                self.runner.run_benchmark(config, execute_auth_pattern)
            )
            
            results[pattern_name] = benchmark_result
        
        return results
    
    def benchmark_api_scaling(self) -> Dict[str, Any]:
        """Benchmark API performance under different load levels."""
        scaling_tests = [
            (1, "Single user"),
            (10, "Light load"),
            (50, "Moderate load"),
            (100, "Heavy load")
        ]
        
        results = {}
        
        for concurrent_users, description in scaling_tests:
            print(f"Benchmarking API scaling: {description} ({concurrent_users} users)")
            
            async def execute_scaling_test():
                async def user_session():
                    # Simulate typical user session
                    operations = 0
                    
                    # Health check
                    await self.mock_server.handle_request("GET", "/health")
                    operations += 1
                    
                    # Get courses
                    await self.mock_server.handle_request("GET", "/courses/")
                    operations += 1
                    
                    # Submit code (some users)
                    if random.random() < 0.3:  # 30% of users submit code
                        submission_data = {
                            "exercise_id": f"scaling_ex_{random.randint(1, 20)}",
                            "code": "def test(): return 'hello'",
                            "language": "python"
                        }
                        await self.mock_server.handle_request("POST", "/submissions/", submission_data)
                        operations += 1
                    
                    return operations
                
                # Execute concurrent user sessions
                tasks = [user_session() for _ in range(concurrent_users)]
                results = await asyncio.gather(*tasks)
                
                return sum(results)
            
            config = BenchmarkConfig(
                name=f"scaling_{concurrent_users}_users",
                description=f"API performance with {concurrent_users} concurrent users",
                iterations=10 if concurrent_users > 50 else 15
            )
            
            benchmark_result = asyncio.run(
                self.runner.run_benchmark(config, execute_scaling_test)
            )
            
            results[f"scale_{concurrent_users}"] = benchmark_result
        
        return results
    
    def benchmark_rate_limiting(self) -> Dict[str, Any]:
        """Benchmark rate limiting behavior."""
        print("Benchmarking rate limiting behavior...")
        
        async def execute_rate_limit_test():
            requests_made = 0
            rate_limited_count = 0
            
            # Make rapid requests to trigger rate limiting
            for _ in range(100):
                response = await self.mock_server.handle_request("POST", "/submissions/", {
                    "exercise_id": "rate_limit_test",
                    "code": "print('test')",
                    "language": "python"
                })
                
                requests_made += 1
                
                if response["status_code"] == 429:
                    rate_limited_count += 1
                
                # Small delay to simulate realistic request pattern
                await asyncio.sleep(0.01)
            
            return rate_limited_count
        
        config = BenchmarkConfig(
            name="rate_limiting",
            description="Rate limiting behavior test",
            iterations=5
        )
        
        result = asyncio.run(
            self.runner.run_benchmark(config, execute_rate_limit_test)
        )
        
        return {"rate_limiting": result}


# Standalone benchmark execution
def run_api_benchmarks():
    """Run all API benchmarks."""
    print("Running API Performance Benchmarks")
    print("=" * 50)
    
    benchmarks = APIBenchmarks()
    
    # Run main benchmark suite
    print("Running core API benchmarks...")
    main_results = asyncio.run(benchmarks.run_all_benchmarks())
    
    # Run specialized benchmarks
    print("\nRunning response pattern benchmarks...")
    response_results = benchmarks.benchmark_api_response_patterns()
    
    print("\nRunning authentication pattern benchmarks...")
    auth_results = benchmarks.benchmark_authentication_patterns()
    
    print("\nRunning API scaling benchmarks...")
    scaling_results = benchmarks.benchmark_api_scaling()
    
    print("\nRunning rate limiting benchmarks...")
    rate_limit_results = benchmarks.benchmark_rate_limiting()
    
    # Combine all results
    all_results = {
        **main_results,
        **response_results,
        **auth_results,
        **scaling_results,
        **rate_limit_results
    }
    
    # Generate comprehensive report
    report = benchmarks.runner.generate_performance_report(
        all_results,
        "api_benchmark_report.md"
    )
    
    print(f"\nAPI benchmarks completed!")
    print(f"Total benchmarks run: {len(all_results)}")
    
    # Performance summary
    if main_results:
        health_check_result = main_results.get("health_check")
        if health_check_result:
            print(f"Health check avg response time: {health_check_result.mean_time * 1000:.3f} ms")
        
        auth_result = main_results.get("authentication")
        if auth_result:
            print(f"Authentication avg time: {auth_result.mean_time * 1000:.3f} ms")
        
        submission_result = main_results.get("code_submission")
        if submission_result:
            print(f"Code submission avg time: {submission_result.mean_time * 1000:.3f} ms")
    
    return all_results


def run_api_stress_test():
    """Run API stress test with extreme load."""
    print("\nRunning API Stress Test")
    print("=" * 40)
    
    benchmarks = APIBenchmarks()
    
    async def extreme_load_test():
        """Test API under extreme concurrent load."""
        print("Starting extreme load test (200 concurrent users)...")
        
        async def aggressive_user_session():
            """Aggressive user session with rapid requests."""
            operations = 0
            errors = 0
            
            try:
                for _ in range(20):  # 20 rapid operations per user
                    operation_type = random.choice(["health", "courses", "submit"])
                    
                    if operation_type == "health":
                        response = await benchmarks.mock_server.handle_request("GET", "/health")
                    elif operation_type == "courses":
                        response = await benchmarks.mock_server.handle_request("GET", "/courses/")
                    else:  # submit
                        response = await benchmarks.mock_server.handle_request("POST", "/submissions/", {
                            "exercise_id": f"stress_ex_{random.randint(1, 50)}",
                            "code": "def stress_test(): pass",
                            "language": "python"
                        })
                    
                    if response["status_code"] < 400:
                        operations += 1
                    else:
                        errors += 1
                    
                    # Very small delay
                    await asyncio.sleep(0.001)
            
            except Exception:
                errors += 1
            
            return operations, errors
        
        # Create 200 concurrent aggressive users
        start_time = time.time()
        tasks = [aggressive_user_session() for _ in range(200)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Process results
        total_operations = 0
        total_errors = 0
        exceptions = 0
        
        for result in results:
            if isinstance(result, tuple):
                ops, errs = result
                total_operations += ops
                total_errors += errs
            else:
                exceptions += 1
        
        duration = end_time - start_time
        operations_per_second = total_operations / duration
        error_rate = (total_errors / (total_operations + total_errors)) * 100 if (total_operations + total_errors) > 0 else 0
        
        print(f"Extreme load test results:")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Total operations: {total_operations}")
        print(f"  Total errors: {total_errors}")
        print(f"  Exceptions: {exceptions}")
        print(f"  Operations per second: {operations_per_second:.2f}")
        print(f"  Error rate: {error_rate:.2f}%")
        print(f"  Server request count: {benchmarks.mock_server.request_count}")
        
        return {
            "operations_per_second": operations_per_second,
            "error_rate": error_rate,
            "total_operations": total_operations
        }
    
    # Run stress test
    stress_results = asyncio.run(extreme_load_test())
    
    return stress_results


if __name__ == "__main__":
    # Run comprehensive API benchmarks
    api_results = run_api_benchmarks()
    
    # Run stress test
    stress_results = run_api_stress_test()
    
    print(f"\n{'='*60}")
    print("All API benchmarks and stress tests completed!")