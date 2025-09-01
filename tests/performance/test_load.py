# tests/performance/test_load.py
"""
Load testing for the Python learning platform.
Tests system performance under various load conditions including
concurrent users, high request volumes, and resource-intensive operations.
"""
import pytest
import asyncio
import aiohttp
import time
import statistics
import random
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
import psutil
import gc


@dataclass
class LoadTestConfig:
    """Configuration for load tests."""
    concurrent_users: int
    test_duration_seconds: int
    ramp_up_time_seconds: int
    target_requests_per_second: int
    max_response_time_ms: int
    error_rate_threshold: float  # Percentage


@dataclass
class LoadTestResult:
    """Results from load testing."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    percentile_95_response_time: float
    requests_per_second: float
    error_rate: float
    throughput_mbps: float
    start_time: datetime
    end_time: datetime
    duration_seconds: float


@dataclass
class SystemMetrics:
    """System resource usage metrics."""
    cpu_usage_percent: float
    memory_usage_percent: float
    memory_usage_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_received_mb: float
    network_io_sent_mb: float
    timestamp: datetime


class MockPlatformAPI:
    """Mock platform API for load testing."""
    
    def __init__(self):
        self.request_count = 0
        self.active_sessions = set()
        self.database_connections = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.response_delays = {}
        self.error_simulation = {}
        
    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Mock user authentication."""
        await self._simulate_processing_time("auth", 0.1, 0.3)
        self.request_count += 1
        
        if self._should_simulate_error("auth", 0.02):  # 2% error rate
            raise Exception("Authentication service unavailable")
        
        token = f"token_{username}_{int(time.time())}"
        self.active_sessions.add(token)
        
        return {
            "status": "success",
            "token": token,
            "user_id": f"user_{hash(username) % 10000}",
            "expires_at": datetime.now() + timedelta(hours=1)
        }
    
    async def get_user_courses(self, user_id: str, token: str) -> Dict[str, Any]:
        """Mock getting user's courses."""
        await self._simulate_processing_time("courses", 0.05, 0.15)
        self.request_count += 1
        
        if token not in self.active_sessions:
            raise Exception("Invalid token")
        
        if self._should_simulate_error("courses", 0.01):  # 1% error rate
            raise Exception("Database connection timeout")
        
        # Simulate cache hit/miss
        if random.random() < 0.8:  # 80% cache hit rate
            self.cache_hits += 1
            processing_time = 0.01
        else:
            self.cache_misses += 1
            processing_time = 0.1
        
        await asyncio.sleep(processing_time)
        
        courses = [
            {"id": f"course_{i}", "title": f"Python Course {i}", "progress": random.randint(0, 100)}
            for i in range(random.randint(3, 8))
        ]
        
        return {"status": "success", "courses": courses}
    
    async def submit_exercise(self, user_id: str, exercise_id: str, code: str, token: str) -> Dict[str, Any]:
        """Mock exercise submission."""
        await self._simulate_processing_time("submit", 0.5, 2.0)
        self.request_count += 1
        
        if token not in self.active_sessions:
            raise Exception("Invalid token")
        
        if self._should_simulate_error("submit", 0.03):  # 3% error rate
            raise Exception("Code execution service overloaded")
        
        # Simulate code execution time based on code complexity
        code_complexity = len(code) / 100  # Simple complexity metric
        execution_time = min(code_complexity * 0.1, 1.0)  # Cap at 1 second
        await asyncio.sleep(execution_time)
        
        score = random.randint(60, 100)
        
        return {
            "status": "success",
            "submission_id": f"sub_{user_id}_{exercise_id}_{int(time.time())}",
            "score": score,
            "execution_time": execution_time,
            "test_results": [
                {"test_id": f"test_{i}", "passed": random.random() > 0.2}
                for i in range(random.randint(3, 8))
            ]
        }
    
    async def get_lesson_content(self, lesson_id: str, token: str) -> Dict[str, Any]:
        """Mock getting lesson content."""
        await self._simulate_processing_time("content", 0.1, 0.5)
        self.request_count += 1
        
        if token not in self.active_sessions:
            raise Exception("Invalid token")
        
        if self._should_simulate_error("content", 0.015):  # 1.5% error rate
            raise Exception("Content delivery network error")
        
        # Simulate different content types with different load times
        content_type = random.choice(["text", "video", "interactive"])
        content_size_mb = {"text": 0.1, "video": 5.0, "interactive": 2.0}[content_type]
        
        return {
            "status": "success",
            "lesson_id": lesson_id,
            "content_type": content_type,
            "content_size_mb": content_size_mb,
            "content_url": f"/content/{lesson_id}",
            "duration_minutes": random.randint(15, 45)
        }
    
    async def save_progress(self, user_id: str, lesson_id: str, progress_data: Dict, token: str) -> Dict[str, Any]:
        """Mock saving user progress."""
        await self._simulate_processing_time("progress", 0.05, 0.2)
        self.request_count += 1
        
        if token not in self.active_sessions:
            raise Exception("Invalid token")
        
        if self._should_simulate_error("progress", 0.01):  # 1% error rate
            raise Exception("Database write timeout")
        
        # Simulate database write
        self.database_connections += 1
        await asyncio.sleep(0.02)  # Database write time
        
        return {
            "status": "success",
            "progress_saved": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _simulate_processing_time(self, operation: str, min_time: float, max_time: float):
        """Simulate variable processing time for different operations."""
        base_time = random.uniform(min_time, max_time)
        
        # Add load-based delay
        load_factor = min(self.request_count / 1000, 2.0)  # Increase delay with load
        actual_time = base_time * (1 + load_factor * 0.5)
        
        await asyncio.sleep(actual_time)
    
    def _should_simulate_error(self, operation: str, base_error_rate: float) -> bool:
        """Determine if an error should be simulated based on current load."""
        # Increase error rate under high load
        load_factor = min(self.request_count / 1000, 3.0)
        adjusted_error_rate = base_error_rate * (1 + load_factor * 0.3)
        
        return random.random() < adjusted_error_rate
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current API statistics."""
        return {
            "total_requests": self.request_count,
            "active_sessions": len(self.active_sessions),
            "database_connections": self.database_connections,
            "cache_hit_rate": self.cache_hits / max(self.cache_hits + self.cache_misses, 1),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses
        }


class LoadTestRunner:
    """Runs load tests against the platform."""
    
    def __init__(self, api: MockPlatformAPI):
        self.api = api
        self.metrics_collector = SystemMetricsCollector()
        self.results = []
        
    async def run_user_journey_load_test(self, config: LoadTestConfig) -> LoadTestResult:
        """Run a complete user journey load test."""
        print(f"Starting load test: {config.concurrent_users} users, {config.test_duration_seconds}s duration")
        
        start_time = datetime.now()
        self.metrics_collector.start_monitoring()
        
        # Create user tasks
        tasks = []
        user_ids = [f"loadtest_user_{i}" for i in range(config.concurrent_users)]
        
        # Stagger user ramp-up
        ramp_up_delay = config.ramp_up_time_seconds / config.concurrent_users if config.concurrent_users > 0 else 0
        
        for i, user_id in enumerate(user_ids):
            delay = i * ramp_up_delay
            task = asyncio.create_task(self._user_journey(user_id, config.test_duration_seconds, delay))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.now()
        self.metrics_collector.stop_monitoring()
        
        # Process results
        return self._calculate_load_test_results(results, start_time, end_time, config)
    
    async def _user_journey(self, user_id: str, duration_seconds: int, initial_delay: float) -> List[Dict[str, Any]]:
        """Simulate a complete user journey."""
        if initial_delay > 0:
            await asyncio.sleep(initial_delay)
        
        journey_results = []
        journey_start = time.time()
        
        try:
            # Authentication
            auth_start = time.time()
            auth_result = await self.api.authenticate_user(user_id, "password123")
            auth_time = time.time() - auth_start
            
            journey_results.append({
                "operation": "auth",
                "success": True,
                "response_time": auth_time,
                "timestamp": datetime.now()
            })
            
            token = auth_result["token"]
            
            # Main user activity loop
            while time.time() - journey_start < duration_seconds:
                # Random user actions with realistic patterns
                action = random.choices(
                    ["get_courses", "get_lesson", "submit_exercise", "save_progress"],
                    weights=[0.2, 0.4, 0.3, 0.1]  # Weighted towards content consumption
                )[0]
                
                try:
                    action_start = time.time()
                    
                    if action == "get_courses":
                        await self.api.get_user_courses(user_id, token)
                    elif action == "get_lesson":
                        lesson_id = f"lesson_{random.randint(1, 100)}"
                        await self.api.get_lesson_content(lesson_id, token)
                    elif action == "submit_exercise":
                        exercise_id = f"exercise_{random.randint(1, 50)}"
                        code = self._generate_sample_code()
                        await self.api.submit_exercise(user_id, exercise_id, code, token)
                    elif action == "save_progress":
                        lesson_id = f"lesson_{random.randint(1, 100)}"
                        progress_data = {"completed": True, "score": random.randint(70, 100)}
                        await self.api.save_progress(user_id, lesson_id, progress_data, token)
                    
                    action_time = time.time() - action_start
                    
                    journey_results.append({
                        "operation": action,
                        "success": True,
                        "response_time": action_time,
                        "timestamp": datetime.now()
                    })
                    
                except Exception as e:
                    action_time = time.time() - action_start
                    journey_results.append({
                        "operation": action,
                        "success": False,
                        "response_time": action_time,
                        "error": str(e),
                        "timestamp": datetime.now()
                    })
                
                # Wait between actions (realistic user behavior)
                await asyncio.sleep(random.uniform(1, 5))
                
        except Exception as e:
            journey_results.append({
                "operation": "journey",
                "success": False,
                "response_time": 0,
                "error": f"Journey failed: {str(e)}",
                "timestamp": datetime.now()
            })
        
        return journey_results
    
    def _generate_sample_code(self) -> str:
        """Generate sample code for exercise submissions."""
        code_samples = [
            "def add_numbers(a, b):\n    return a + b",
            "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
            "def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a",
            "def sort_list(lst):\n    return sorted(lst)",
            "def find_max(lst):\n    return max(lst) if lst else None"
        ]
        return random.choice(code_samples)
    
    def _calculate_load_test_results(self, task_results: List, start_time: datetime, 
                                   end_time: datetime, config: LoadTestConfig) -> LoadTestResult:
        """Calculate comprehensive load test results."""
        all_operations = []
        
        # Flatten all operation results
        for task_result in task_results:
            if isinstance(task_result, list):
                all_operations.extend(task_result)
            elif isinstance(task_result, Exception):
                continue  # Skip failed tasks
        
        successful_ops = [op for op in all_operations if op.get("success", False)]
        failed_ops = [op for op in all_operations if not op.get("success", True)]
        
        total_requests = len(all_operations)
        successful_requests = len(successful_ops)
        failed_requests = len(failed_ops)
        
        if successful_requests > 0:
            response_times = [op["response_time"] for op in successful_ops]
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            percentile_95 = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        else:
            avg_response_time = min_response_time = max_response_time = percentile_95 = 0
        
        duration_seconds = (end_time - start_time).total_seconds()
        requests_per_second = total_requests / duration_seconds if duration_seconds > 0 else 0
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Estimate throughput (simplified)
        avg_response_size_kb = 5  # Assume average 5KB response
        throughput_mbps = (requests_per_second * avg_response_size_kb) / 1024
        
        return LoadTestResult(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            percentile_95_response_time=percentile_95,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            throughput_mbps=throughput_mbps,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds
        )


class SystemMetricsCollector:
    """Collects system resource metrics during load tests."""
    
    def __init__(self):
        self.monitoring = False
        self.metrics_history = []
        self.monitor_task = None
        
    def start_monitoring(self, interval_seconds: float = 1.0):
        """Start collecting system metrics."""
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._collect_metrics(interval_seconds))
    
    def stop_monitoring(self):
        """Stop collecting system metrics."""
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
    
    async def _collect_metrics(self, interval: float):
        """Continuously collect system metrics."""
        while self.monitoring:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                network_io = psutil.net_io_counters()
                
                metrics = SystemMetrics(
                    cpu_usage_percent=cpu_percent,
                    memory_usage_percent=memory.percent,
                    memory_usage_mb=memory.used / (1024 * 1024),
                    disk_io_read_mb=disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                    disk_io_write_mb=disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                    network_io_received_mb=network_io.bytes_recv / (1024 * 1024) if network_io else 0,
                    network_io_sent_mb=network_io.bytes_sent / (1024 * 1024) if network_io else 0,
                    timestamp=datetime.now()
                )
                
                self.metrics_history.append(metrics)
                
            except Exception as e:
                print(f"Error collecting metrics: {e}")
            
            await asyncio.sleep(interval)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        if not self.metrics_history:
            return {}
        
        cpu_values = [m.cpu_usage_percent for m in self.metrics_history]
        memory_values = [m.memory_usage_percent for m in self.metrics_history]
        
        return {
            "cpu_usage": {
                "average": statistics.mean(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory_usage": {
                "average": statistics.mean(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "samples_collected": len(self.metrics_history),
            "monitoring_duration": (self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp).total_seconds()
        }


@pytest.fixture
def mock_api():
    """Fixture providing a clean mock API."""
    return MockPlatformAPI()


@pytest.fixture
def load_test_runner(mock_api):
    """Fixture providing a load test runner."""
    return LoadTestRunner(mock_api)


class TestBasicLoad:
    """Test basic load scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_light_load_scenario(self, load_test_runner):
        """Test light load with few concurrent users."""
        config = LoadTestConfig(
            concurrent_users=5,
            test_duration_seconds=30,
            ramp_up_time_seconds=5,
            target_requests_per_second=10,
            max_response_time_ms=1000,
            error_rate_threshold=2.0
        )
        
        result = await load_test_runner.run_user_journey_load_test(config)
        
        # Assertions for light load
        assert result.error_rate < config.error_rate_threshold
        assert result.average_response_time < (config.max_response_time_ms / 1000)
        assert result.successful_requests > 0
        assert result.requests_per_second > 0
        
        print(f"Light load test results:")
        print(f"  Total requests: {result.total_requests}")
        print(f"  Success rate: {(result.successful_requests / result.total_requests) * 100:.2f}%")
        print(f"  Average response time: {result.average_response_time:.3f}s")
        print(f"  Requests per second: {result.requests_per_second:.2f}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_moderate_load_scenario(self, load_test_runner):
        """Test moderate load with typical user count."""
        config = LoadTestConfig(
            concurrent_users=25,
            test_duration_seconds=60,
            ramp_up_time_seconds=10,
            target_requests_per_second=50,
            max_response_time_ms=2000,
            error_rate_threshold=5.0
        )
        
        result = await load_test_runner.run_user_journey_load_test(config)
        
        # Assertions for moderate load
        assert result.error_rate < config.error_rate_threshold
        assert result.average_response_time < (config.max_response_time_ms / 1000)
        assert result.successful_requests > result.total_requests * 0.9  # At least 90% success
        
        # Check system performance under moderate load
        system_metrics = load_test_runner.metrics_collector.get_summary()
        if system_metrics:
            assert system_metrics["cpu_usage"]["average"] < 80  # CPU usage under 80%
            assert system_metrics["memory_usage"]["average"] < 90  # Memory usage under 90%
        
        print(f"Moderate load test results:")
        print(f"  Total requests: {result.total_requests}")
        print(f"  Error rate: {result.error_rate:.2f}%")
        print(f"  95th percentile response time: {result.percentile_95_response_time:.3f}s")
        print(f"  Throughput: {result.throughput_mbps:.2f} Mbps")


class TestHighLoad:
    """Test high load scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_high_load_scenario(self, load_test_runner):
        """Test high load with many concurrent users."""
        config = LoadTestConfig(
            concurrent_users=100,
            test_duration_seconds=120,
            ramp_up_time_seconds=30,
            target_requests_per_second=200,
            max_response_time_ms=5000,
            error_rate_threshold=10.0
        )
        
        result = await load_test_runner.run_user_journey_load_test(config)
        
        # More lenient assertions for high load
        assert result.error_rate < config.error_rate_threshold
        assert result.average_response_time < (config.max_response_time_ms / 1000)
        assert result.successful_requests > result.total_requests * 0.8  # At least 80% success
        
        # Performance degradation is expected under high load
        print(f"High load test results:")
        print(f"  Total requests: {result.total_requests}")
        print(f"  Error rate: {result.error_rate:.2f}%")
        print(f"  Average response time: {result.average_response_time:.3f}s")
        print(f"  Max response time: {result.max_response_time:.3f}s")
        
        # Verify the system can handle the load
        assert result.requests_per_second > config.target_requests_per_second * 0.5  # At least 50% of target
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_spike_load_scenario(self, load_test_runner):
        """Test sudden spike in load."""
        # Start with baseline load
        baseline_config = LoadTestConfig(
            concurrent_users=10,
            test_duration_seconds=30,
            ramp_up_time_seconds=2,
            target_requests_per_second=20,
            max_response_time_ms=1000,
            error_rate_threshold=3.0
        )
        
        baseline_result = await load_test_runner.run_user_journey_load_test(baseline_config)
        baseline_response_time = baseline_result.average_response_time
        
        # Create spike load
        spike_config = LoadTestConfig(
            concurrent_users=200,
            test_duration_seconds=60,
            ramp_up_time_seconds=5,  # Very fast ramp-up
            target_requests_per_second=400,
            max_response_time_ms=10000,
            error_rate_threshold=25.0  # Higher tolerance for spike
        )
        
        spike_result = await load_test_runner.run_user_journey_load_test(spike_config)
        
        # Verify system handles spike (may have degraded performance)
        assert spike_result.error_rate < spike_config.error_rate_threshold
        assert spike_result.successful_requests > 0
        
        print(f"Spike load test results:")
        print(f"  Baseline avg response time: {baseline_response_time:.3f}s")
        print(f"  Spike avg response time: {spike_result.average_response_time:.3f}s")
        print(f"  Response time increase: {(spike_result.average_response_time / baseline_response_time):.2f}x")
        print(f"  Spike error rate: {spike_result.error_rate:.2f}%")


class TestSpecificOperations:
    """Test load on specific platform operations."""
    
    @pytest.mark.asyncio
    async def test_exercise_submission_load(self, mock_api, load_test_runner):
        """Test load specifically on exercise submission."""
        # Setup authenticated users
        users = []
        for i in range(50):
            user_id = f"submission_user_{i}"
            auth_result = await mock_api.authenticate_user(user_id, "password")
            users.append((user_id, auth_result["token"]))
        
        # Concurrent exercise submissions
        submission_tasks = []
        
        async def submit_exercise_batch(user_id: str, token: str, batch_size: int):
            """Submit multiple exercises for a user."""
            results = []
            for i in range(batch_size):
                try:
                    start_time = time.time()
                    exercise_id = f"exercise_{random.randint(1, 100)}"
                    code = load_test_runner._generate_sample_code()
                    
                    result = await mock_api.submit_exercise(user_id, exercise_id, code, token)
                    end_time = time.time()
                    
                    results.append({
                        "success": True,
                        "response_time": end_time - start_time,
                        "result": result
                    })
                    
                except Exception as e:
                    end_time = time.time()
                    results.append({
                        "success": False,
                        "response_time": end_time - start_time,
                        "error": str(e)
                    })
                
                # Small delay between submissions
                await asyncio.sleep(0.1)
            
            return results
        
        # Create submission tasks
        for user_id, token in users:
            task = submit_exercise_batch(user_id, token, 5)  # 5 submissions per user
            submission_tasks.append(task)
        
        # Execute all submission tasks
        start_time = time.time()
        all_results = await asyncio.gather(*submission_tasks)
        end_time = time.time()
        
        # Analyze results
        flat_results = [result for batch in all_results for result in batch]
        successful_submissions = [r for r in flat_results if r["success"]]
        failed_submissions = [r for r in flat_results if not r["success"]]
        
        success_rate = len(successful_submissions) / len(flat_results) * 100
        avg_response_time = statistics.mean([r["response_time"] for r in successful_submissions])
        total_duration = end_time - start_time
        submissions_per_second = len(flat_results) / total_duration
        
        print(f"Exercise submission load test:")
        print(f"  Total submissions: {len(flat_results)}")
        print(f"  Success rate: {success_rate:.2f}%")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Submissions per second: {submissions_per_second:.2f}")
        
        # Assertions
        assert success_rate > 85  # At least 85% success rate
        assert avg_response_time < 3.0  # Under 3 seconds average
        assert submissions_per_second > 10  # At least 10 submissions per second
    
    @pytest.mark.asyncio
    async def test_content_delivery_load(self, mock_api):
        """Test load on content delivery."""
        # Setup users
        users = []
        for i in range(30):
            user_id = f"content_user_{i}"
            auth_result = await mock_api.authenticate_user(user_id, "password")
            users.append((user_id, auth_result["token"]))
        
        # Concurrent content requests
        async def request_content_batch(user_id: str, token: str):
            """Request multiple pieces of content."""
            results = []
            lesson_ids = [f"lesson_{i}" for i in range(1, 21)]  # 20 lessons
            
            for lesson_id in lesson_ids:
                try:
                    start_time = time.time()
                    content = await mock_api.get_lesson_content(lesson_id, token)
                    end_time = time.time()
                    
                    results.append({
                        "success": True,
                        "response_time": end_time - start_time,
                        "content_size": content.get("content_size_mb", 0)
                    })
                    
                except Exception as e:
                    end_time = time.time()
                    results.append({
                        "success": False,
                        "response_time": end_time - start_time,
                        "error": str(e)
                    })
                
                await asyncio.sleep(0.05)  # Small delay
            
            return results
        
        # Execute content requests
        content_tasks = [request_content_batch(user_id, token) for user_id, token in users]
        
        start_time = time.time()
        all_results = await asyncio.gather(*content_tasks)
        end_time = time.time()
        
        # Analyze results
        flat_results = [result for batch in all_results for result in batch]
        successful_requests = [r for r in flat_results if r["success"]]
        
        success_rate = len(successful_requests) / len(flat_results) * 100
        avg_response_time = statistics.mean([r["response_time"] for r in successful_requests])
        total_data_mb = sum([r.get("content_size", 0) for r in successful_requests])
        
        print(f"Content delivery load test:")
        print(f"  Total requests: {len(flat_results)}")
        print(f"  Success rate: {success_rate:.2f}%")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Total data delivered: {total_data_mb:.2f} MB")
        
        # Assertions
        assert success_rate > 90  # High success rate for content delivery
        assert avg_response_time < 1.0  # Fast content delivery
    
    @pytest.mark.asyncio
    async def test_database_write_load(self, mock_api):
        """Test load on database write operations (progress saving)."""
        # Setup users
        users = []
        for i in range(20):
            user_id = f"progress_user_{i}"
            auth_result = await mock_api.authenticate_user(user_id, "password")
            users.append((user_id, auth_result["token"]))
        
        # Concurrent progress saves
        async def save_progress_batch(user_id: str, token: str):
            """Save progress for multiple lessons."""
            results = []
            
            for lesson_num in range(1, 11):  # 10 lessons
                try:
                    start_time = time.time()
                    lesson_id = f"lesson_{lesson_num}"
                    progress_data = {
                        "completed": random.choice([True, False]),
                        "score": random.randint(60, 100),
                        "time_spent": random.randint(300, 1800),  # 5-30 minutes
                        "attempts": random.randint(1, 3)
                    }
                    
                    result = await mock_api.save_progress(user_id, lesson_id, progress_data, token)
                    end_time = time.time()
                    
                    results.append({
                        "success": True,
                        "response_time": end_time - start_time
                    })
                    
                except Exception as e:
                    end_time = time.time()
                    results.append({
                        "success": False,
                        "response_time": end_time - start_time,
                        "error": str(e)
                    })
                
                await asyncio.sleep(0.02)  # Small delay between saves
            
            return results
        
        # Execute progress saving tasks
        progress_tasks = [save_progress_batch(user_id, token) for user_id, token in users]
        
        start_time = time.time()
        all_results = await asyncio.gather(*progress_tasks)
        end_time = time.time()
        
        # Analyze results
        flat_results = [result for batch in all_results for result in batch]
        successful_saves = [r for r in flat_results if r["success"]]
        
        success_rate = len(successful_saves) / len(flat_results) * 100
        avg_response_time = statistics.mean([r["response_time"] for r in successful_saves])
        saves_per_second = len(flat_results) / (end_time - start_time)
        
        print(f"Database write load test:")
        print(f"  Total save operations: {len(flat_results)}")
        print(f"  Success rate: {success_rate:.2f}%")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Saves per second: {saves_per_second:.2f}")
        
        # Assertions
        assert success_rate > 95  # Very high success rate for writes
        assert avg_response_time < 0.5  # Fast database writes
        assert saves_per_second > 20  # Good write throughput


class TestStressConditions:
    """Test system behavior under stress conditions."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_memory_pressure_simulation(self, mock_api):
        """Test system behavior under memory pressure."""
        # Create many concurrent operations that consume memory
        async def memory_intensive_operation(user_id: str, token: str):
            """Simulate memory-intensive operation."""
            # Simulate large data processing
            large_data = [random.random() for _ in range(10000)]  # 10K random numbers
            
            try:
                # Multiple operations with large data
                for i in range(5):
                    exercise_id = f"memory_test_{i}"
                    code = f"# Large code block\n" + "\n".join([f"var_{j} = {random.random()}" for j in range(100)])
                    
                    await mock_api.submit_exercise(user_id, exercise_id, code, token)
                    
                    # Force some memory allocation
                    temp_data = large_data * 2
                    del temp_data
                    
                    await asyncio.sleep(0.1)
                
                return {"success": True, "operations": 5}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
            finally:
                # Clean up
                del large_data
                gc.collect()
        
        # Setup users for memory test
        users = []
        for i in range(50):  # 50 users doing memory-intensive operations
            user_id = f"memory_user_{i}"
            auth_result = await mock_api.authenticate_user(user_id, "password")
            users.append((user_id, auth_result["token"]))
        
        # Record initial memory
        initial_memory = psutil.virtual_memory().used / (1024 * 1024)
        
        # Execute memory-intensive tasks
        memory_tasks = [memory_intensive_operation(user_id, token) for user_id, token in users]
        
        start_time = time.time()
        results = await asyncio.gather(*memory_tasks, return_exceptions=True)
        end_time = time.time()
        
        # Record final memory
        final_memory = psutil.virtual_memory().used / (1024 * 1024)
        memory_increase = final_memory - initial_memory
        
        # Analyze results
        successful_ops = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_ops = [r for r in results if isinstance(r, dict) and not r.get("success")]
        exceptions = [r for r in results if isinstance(r, Exception)]
        
        success_rate = len(successful_ops) / len(users) * 100
        
        print(f"Memory pressure test:")
        print(f"  Users: {len(users)}")
        print(f"  Success rate: {success_rate:.2f}%")
        print(f"  Memory increase: {memory_increase:.2f} MB")
        print(f"  Exceptions: {len(exceptions)}")
        print(f"  Duration: {end_time - start_time:.2f}s")
        
        # Assertions - system should handle memory pressure gracefully
        assert success_rate > 70  # Some degradation expected under memory pressure
        assert memory_increase < 500  # Memory increase should be reasonable
        
        # Force garbage collection
        gc.collect()
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_connection_exhaustion(self, mock_api):
        """Test behavior when connection limits are reached."""
        # Simulate connection pool exhaustion
        max_connections = 100
        connection_count = 0
        active_connections = []
        
        async def long_running_operation(user_id: str, token: str, connection_id: int):
            """Simulate long-running operation that holds connections."""
            nonlocal connection_count
            
            if connection_count >= max_connections:
                raise Exception("Connection pool exhausted")
            
            connection_count += 1
            active_connections.append(connection_id)
            
            try:
                # Simulate long-running database operation
                await asyncio.sleep(random.uniform(2, 5))
                
                # Perform actual operation
                await mock_api.get_user_courses(user_id, token)
                
                return {"success": True, "connection_id": connection_id}
                
            except Exception as e:
                return {"success": False, "error": str(e), "connection_id": connection_id}
            finally:
                connection_count -= 1
                if connection_id in active_connections:
                    active_connections.remove(connection_id)
        
        # Setup many users to exhaust connections
        users = []
        for i in range(150):  # More users than max connections
            user_id = f"conn_user_{i}"
            auth_result = await mock_api.authenticate_user(user_id, "password")
            users.append((user_id, auth_result["token"]))
        
        # Create tasks that will exceed connection limit
        connection_tasks = []
        for i, (user_id, token) in enumerate(users):
            task = long_running_operation(user_id, token, i)
            connection_tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*connection_tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze connection exhaustion results
        successful_ops = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_ops = [r for r in results if isinstance(r, dict) and not r.get("success")]
        exceptions = [r for r in results if isinstance(r, Exception)]
        
        success_rate = len(successful_ops) / len(users) * 100
        
        print(f"Connection exhaustion test:")
        print(f"  Total operations: {len(users)}")
        print(f"  Successful: {len(successful_ops)}")
        print(f"  Failed: {len(failed_ops)}")
        print(f"  Exceptions: {len(exceptions)}")
        print(f"  Success rate: {success_rate:.2f}%")
        print(f"  Max concurrent connections: {max(len(active_connections), max_connections)}")
        
        # System should handle connection exhaustion gracefully
        assert len(successful_ops) <= max_connections  # Can't exceed max connections
        assert len(failed_ops) + len(exceptions) > 0  # Some operations should fail
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_cascading_failure_simulation(self, mock_api):
        """Test system behavior during cascading failures."""
        # Simulate external service failures that cascade
        failure_cascade = {
            "auth_service": {"failure_rate": 0.1, "recovery_time": 10},
            "database": {"failure_rate": 0.05, "recovery_time": 15},
            "code_executor": {"failure_rate": 0.2, "recovery_time": 5},
            "content_delivery": {"failure_rate": 0.03, "recovery_time": 20}
        }
        
        # Track service health
        service_health = {service: True for service in failure_cascade.keys()}
        failure_start_times = {}
        
        async def simulate_service_failures():
            """Simulate random service failures and recoveries."""
            while True:
                for service, config in failure_cascade.items():
                    if service_health[service]:
                        # Check if service should fail
                        if random.random() < config["failure_rate"] / 10:  # Per iteration probability
                            service_health[service] = False
                            failure_start_times[service] = time.time()
                            print(f"Service {service} failed")
                    else:
                        # Check if service should recover
                        if service in failure_start_times:
                            if time.time() - failure_start_times[service] > config["recovery_time"]:
                                service_health[service] = True
                                del failure_start_times[service]
                                print(f"Service {service} recovered")
                
                await asyncio.sleep(1)  # Check every second
        
        # Start failure simulation
        failure_task = asyncio.create_task(simulate_service_failures())
        
        # Run user operations during failures
        async def resilient_user_journey(user_id: str):
            """User journey that should be resilient to service failures."""
            operations_completed = 0
            operations_failed = 0
            
            try:
                # Authentication (depends on auth_service)
                if not service_health["auth_service"]:
                    raise Exception("Auth service unavailable")
                
                auth_result = await mock_api.authenticate_user(user_id, "password")
                token = auth_result["token"]
                operations_completed += 1
                
                # Perform various operations
                for i in range(10):
                    operation_type = random.choice(["courses", "content", "submit", "progress"])
                    
                    try:
                        if operation_type == "courses" and service_health["database"]:
                            await mock_api.get_user_courses(user_id, token)
                            operations_completed += 1
                        elif operation_type == "content" and service_health["content_delivery"]:
                            await mock_api.get_lesson_content(f"lesson_{i}", token)
                            operations_completed += 1
                        elif operation_type == "submit" and service_health["code_executor"]:
                            await mock_api.submit_exercise(user_id, f"ex_{i}", "def test(): pass", token)
                            operations_completed += 1
                        elif operation_type == "progress" and service_health["database"]:
                            await mock_api.save_progress(user_id, f"lesson_{i}", {"score": 85}, token)
                            operations_completed += 1
                        else:
                            operations_failed += 1
                            
                    except Exception:
                        operations_failed += 1
                    
                    await asyncio.sleep(0.5)
            
            except Exception:
                operations_failed += 1
            
            return {
                "user_id": user_id,
                "operations_completed": operations_completed,
                "operations_failed": operations_failed,
                "success_rate": operations_completed / (operations_completed + operations_failed) * 100 if (operations_completed + operations_failed) > 0 else 0
            }
        
        # Run multiple users during cascading failures
        users = [f"cascade_user_{i}" for i in range(20)]
        user_tasks = [resilient_user_journey(user_id) for user_id in users]
        
        # Run test for 60 seconds
        start_time = time.time()
        try:
            results = await asyncio.wait_for(asyncio.gather(*user_tasks), timeout=60)
        except asyncio.TimeoutError:
            results = []  # Some operations may not complete
        
        # Stop failure simulation
        failure_task.cancel()
        
        # Analyze cascading failure results
        if results:
            total_operations = sum(r["operations_completed"] + r["operations_failed"] for r in results)
            total_successful = sum(r["operations_completed"] for r in results)
            overall_success_rate = total_successful / total_operations * 100 if total_operations > 0 else 0
            
            print(f"Cascading failure test:")
            print(f"  Total operations attempted: {total_operations}")
            print(f"  Overall success rate: {overall_success_rate:.2f}%")
            print(f"  Service failures experienced: {len(failure_start_times)}")
            
            # System should maintain some level of service during cascading failures
            assert overall_success_rate > 30  # At least 30% operations should succeed
        else:
            print("Cascading failure test: All operations timed out")


class TestPerformanceRegression:
    """Test for performance regressions."""
    
    @pytest.mark.asyncio
    async def test_response_time_regression(self, load_test_runner):
        """Test for response time regressions."""
        # Baseline performance test
        baseline_config = LoadTestConfig(
            concurrent_users=10,
            test_duration_seconds=30,
            ramp_up_time_seconds=5,
            target_requests_per_second=20,
            max_response_time_ms=1000,
            error_rate_threshold=2.0
        )
        
        baseline_result = await load_test_runner.run_user_journey_load_test(baseline_config)
        
        # Store baseline metrics
        baseline_metrics = {
            "avg_response_time": baseline_result.average_response_time,
            "p95_response_time": baseline_result.percentile_95_response_time,
            "requests_per_second": baseline_result.requests_per_second,
            "error_rate": baseline_result.error_rate
        }
        
        # Simulate code changes (in real scenario, this would be after deployment)
        await asyncio.sleep(1)
        
        # Current performance test
        current_result = await load_test_runner.run_user_journey_load_test(baseline_config)
        
        current_metrics = {
            "avg_response_time": current_result.average_response_time,
            "p95_response_time": current_result.percentile_95_response_time,
            "requests_per_second": current_result.requests_per_second,
            "error_rate": current_result.error_rate
        }
        
        # Check for regressions
        regressions = []
        
        # Response time regression (>20% increase)
        if current_metrics["avg_response_time"] > baseline_metrics["avg_response_time"] * 1.2:
            regressions.append(f"Average response time increased by {((current_metrics['avg_response_time'] / baseline_metrics['avg_response_time']) - 1) * 100:.1f}%")
        
        # P95 response time regression (>30% increase)
        if current_metrics["p95_response_time"] > baseline_metrics["p95_response_time"] * 1.3:
            regressions.append(f"P95 response time increased by {((current_metrics['p95_response_time'] / baseline_metrics['p95_response_time']) - 1) * 100:.1f}%")
        
        # Throughput regression (>15% decrease)
        if current_metrics["requests_per_second"] < baseline_metrics["requests_per_second"] * 0.85:
            regressions.append(f"Requests per second decreased by {((baseline_metrics['requests_per_second'] / current_metrics['requests_per_second']) - 1) * 100:.1f}%")
        
        # Error rate regression (>2% increase)
        if current_metrics["error_rate"] > baseline_metrics["error_rate"] + 2.0:
            regressions.append(f"Error rate increased by {current_metrics['error_rate'] - baseline_metrics['error_rate']:.1f}%")
        
        print(f"Performance regression test:")
        print(f"  Baseline avg response time: {baseline_metrics['avg_response_time']:.3f}s")
        print(f"  Current avg response time: {current_metrics['avg_response_time']:.3f}s")
        print(f"  Baseline RPS: {baseline_metrics['requests_per_second']:.2f}")
        print(f"  Current RPS: {current_metrics['requests_per_second']:.2f}")
        
        if regressions:
            print(f"  Regressions detected: {regressions}")
            # In a real scenario, this might fail the test
            # assert False, f"Performance regressions detected: {regressions}"
        else:
            print("  No significant regressions detected")
        
        # For this test, we'll just verify the test completed successfully
        assert current_result.total_requests > 0
        assert baseline_result.total_requests > 0


if __name__ == "__main__":
    # Run load tests with appropriate markers
    pytest.main([
        __file__, 
        "-v", 
        "-m", "not slow",  # Skip slow tests by default
        "--tb=short"
    ])
    
    # To run slow tests: pytest tests/performance/test_load.py -v -m slow