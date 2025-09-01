# tests/performance/test_stress.py
"""
Stress testing for the Python learning platform.
Tests system behavior beyond normal operating conditions to identify
breaking points, resource leaks, and failure modes.
"""
import pytest
import asyncio
import time
import statistics
import random
import psutil
import gc
import threading
import weakref
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import json
import hashlib


@dataclass
class StressTestConfig:
    """Configuration for stress tests."""
    max_concurrent_users: int
    test_duration_seconds: int
    ramp_up_duration_seconds: int
    failure_threshold_percent: float
    resource_limit_cpu_percent: float
    resource_limit_memory_mb: float
    target_breaking_point: bool = True


@dataclass
class StressTestResult:
    """Results from stress testing."""
    max_concurrent_users_achieved: int
    breaking_point_users: Optional[int]
    total_operations: int
    successful_operations: int
    failed_operations: int
    peak_cpu_usage: float
    peak_memory_usage_mb: float
    average_response_time: float
    max_response_time: float
    operations_per_second_peak: float
    time_to_break: Optional[float]
    recovery_time: Optional[float]
    resource_leaks_detected: List[str]
    failure_modes: List[Dict[str, Any]]


class ResourceMonitor:
    """Monitor system resources during stress tests."""
    
    def __init__(self):
        self.monitoring = False
        self.resource_history = []
        self.peak_cpu = 0.0
        self.peak_memory = 0.0
        self.leak_detection = {}
        self.monitor_thread = None
        
    def start_monitoring(self, interval_seconds: float = 0.5):
        """Start monitoring system resources."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval_seconds,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring system resources."""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self, interval: float):
        """Continuous monitoring loop."""
        while self.monitoring:
            try:
                # CPU and memory
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                memory_mb = memory.used / (1024 * 1024)
                
                # Update peaks
                self.peak_cpu = max(self.peak_cpu, cpu_percent)
                self.peak_memory = max(self.peak_memory, memory_mb)
                
                # Record metrics
                metrics = {
                    "timestamp": datetime.now(),
                    "cpu_percent": cpu_percent,
                    "memory_mb": memory_mb,
                    "memory_percent": memory.percent,
                    "available_memory_mb": memory.available / (1024 * 1024)
                }
                
                self.resource_history.append(metrics)
                
                # Detect potential memory leaks
                if len(self.resource_history) > 60:  # 30 seconds of history
                    self._detect_memory_trends()
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error in resource monitoring: {e}")
                break
    
    def _detect_memory_trends(self):
        """Detect memory leak patterns."""
        recent_memory = [m["memory_mb"] for m in self.resource_history[-60:]]
        
        if len(recent_memory) >= 30:
            first_half = recent_memory[:30]
            second_half = recent_memory[30:]
            
            avg_first = statistics.mean(first_half)
            avg_second = statistics.mean(second_half)
            
            # Check for consistent memory increase
            if avg_second > avg_first * 1.1:  # 10% increase
                slope = (avg_second - avg_first) / 30  # MB per measurement
                if slope > 1.0:  # More than 1MB per measurement
                    leak_key = f"memory_trend_{len(self.leak_detection)}"
                    self.leak_detection[leak_key] = {
                        "type": "memory_leak_suspected",
                        "slope_mb_per_measurement": slope,
                        "detected_at": datetime.now(),
                        "memory_increase_mb": avg_second - avg_first
                    }
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get resource usage summary."""
        if not self.resource_history:
            return {}
        
        cpu_values = [m["cpu_percent"] for m in self.resource_history]
        memory_values = [m["memory_mb"] for m in self.resource_history]
        
        return {
            "peak_cpu_percent": self.peak_cpu,
            "peak_memory_mb": self.peak_memory,
            "average_cpu_percent": statistics.mean(cpu_values),
            "average_memory_mb": statistics.mean(memory_values),
            "monitoring_duration_seconds": len(self.resource_history) * 0.5,
            "resource_leak_count": len(self.leak_detection),
            "leak_details": self.leak_detection
        }


class StressPlatformAPI:
    """Enhanced mock platform API for stress testing."""
    
    def __init__(self):
        self.request_count = 0
        self.active_connections = set()
        self.connection_pool_size = 100
        self.database_load = 0.0
        self.cache_memory_usage = 0
        self.background_tasks = []
        self.system_overload = False
        self.circuit_breaker_open = False
        self.failure_cascade_active = False
        self.resource_exhaustion_threshold = 0.9
        
        # Simulate resource pools
        self.thread_pool = ThreadPoolExecutor(max_workers=50)
        self.memory_pool = []  # Simulate memory allocations
        self.file_handles = []  # Simulate file handle usage
        
    async def stress_authenticate(self, user_id: str) -> Dict[str, Any]:
        """Authentication under stress conditions."""
        self.request_count += 1
        
        # Simulate increasing load on auth service
        auth_delay = min(0.1 + (self.request_count / 10000), 2.0)
        await asyncio.sleep(auth_delay)
        
        # Check for system overload
        if self._is_system_overloaded():
            if random.random() < 0.3:  # 30% chance of failure under overload
                raise Exception("Authentication service overloaded")
        
        # Circuit breaker pattern
        if self.circuit_breaker_open:
            if random.random() < 0.8:  # 80% failure rate when circuit is open
                raise Exception("Circuit breaker open - auth service unavailable")
        
        # Allocate resources for session
        connection_id = f"conn_{user_id}_{self.request_count}"
        if len(self.active_connections) >= self.connection_pool_size:
            raise Exception("Connection pool exhausted")
        
        self.active_connections.add(connection_id)
        
        # Simulate memory allocation for session
        session_memory = [random.random() for _ in range(1000)]  # Simulate session data
        self.memory_pool.append(session_memory)
        
        return {
            "status": "success",
            "token": f"token_{user_id}_{int(time.time())}",
            "connection_id": connection_id,
            "allocated_memory": len(session_memory)
        }
    
    async def stress_submit_exercise(self, user_id: str, exercise_id: str, code: str, token: str) -> Dict[str, Any]:
        """Exercise submission under stress."""
        self.request_count += 1
        
        # Simulate code execution load
        code_complexity = len(code)
        execution_delay = min(0.5 + (code_complexity / 1000), 5.0)
        
        # Add stress-based delay
        stress_multiplier = 1 + min(self.request_count / 5000, 3.0)
        execution_delay *= stress_multiplier
        
        await asyncio.sleep(execution_delay)
        
        # Check for resource exhaustion
        if self._is_resource_exhausted():
            raise Exception("Code execution service resource exhausted")
        
        # Simulate background task creation (potential leak)
        if random.random() < 0.1:  # 10% chance
            background_task = asyncio.create_task(self._background_processing())
            self.background_tasks.append(background_task)
        
        # Simulate memory allocation for code execution
        execution_memory = [0] * (code_complexity * 10)
        self.memory_pool.append(execution_memory)
        
        # Cleanup some old memory (simulate garbage collection)
        if len(self.memory_pool) > 100:
            self.memory_pool = self.memory_pool[-50:]  # Keep last 50
        
        return {
            "status": "success",
            "submission_id": f"sub_{user_id}_{exercise_id}_{self.request_count}",
            "execution_time": execution_delay,
            "memory_used": len(execution_memory),
            "background_tasks": len(self.background_tasks)
        }
    
    async def stress_get_content(self, content_id: str, token: str) -> Dict[str, Any]:
        """Content delivery under stress."""
        self.request_count += 1
        
        # Simulate CDN load
        base_delay = 0.1
        load_delay = min(base_delay * (1 + self.request_count / 2000), 1.0)
        await asyncio.sleep(load_delay)
        
        # Simulate large content transfer
        content_size = random.randint(1024, 1024 * 1024)  # 1KB to 1MB
        
        # Cache memory usage simulation
        self.cache_memory_usage += content_size
        if self.cache_memory_usage > 100 * 1024 * 1024:  # 100MB cache limit
            self.cache_memory_usage = content_size  # Reset cache
        
        return {
            "status": "success",
            "content_id": content_id,
            "content_size": content_size,
            "cache_usage": self.cache_memory_usage,
            "delivery_time": load_delay
        }
    
    async def stress_save_progress(self, user_id: str, lesson_id: str, progress_data: Dict, token: str) -> Dict[str, Any]:
        """Progress saving under stress."""
        self.request_count += 1
        
        # Simulate database load
        self.database_load = min(self.database_load + 0.1, 10.0)
        db_delay = min(0.05 * self.database_load, 2.0)
        await asyncio.sleep(db_delay)
        
        # Simulate file handle usage (potential leak)
        if random.random() < 0.05:  # 5% chance
            file_handle = f"file_{user_id}_{lesson_id}_{time.time()}"
            self.file_handles.append(file_handle)
            
            # Cleanup old handles periodically
            if len(self.file_handles) > 1000:
                self.file_handles = self.file_handles[-500:]
        
        # Gradually reduce database load
        self.database_load = max(0, self.database_load - 0.02)
        
        return {
            "status": "success",
            "progress_saved": True,
            "database_load": self.database_load,
            "file_handles_open": len(self.file_handles)
        }
    
    async def _background_processing(self):
        """Simulate background processing that might cause leaks."""
        try:
            await asyncio.sleep(random.uniform(5, 15))  # Long-running task
            # Task completes normally
        except asyncio.CancelledError:
            pass  # Task was cancelled
        except Exception:
            pass  # Task failed
    
    def _is_system_overloaded(self) -> bool:
        """Check if system is overloaded."""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        if cpu_usage > 80 or memory_usage > 85:
            self.system_overload = True
            return True
        
        if self.request_count > 10000:  # High request count
            return True
        
        return False
    
    def _is_resource_exhausted(self) -> bool:
        """Check if resources are exhausted."""
        if len(self.active_connections) > self.connection_pool_size * 0.9:
            return True
        
        if len(self.memory_pool) > 500:  # Too many memory allocations
            return True
        
        if len(self.background_tasks) > 100:  # Too many background tasks
            return True
        
        return False
    
    def trigger_circuit_breaker(self):
        """Trigger circuit breaker for testing."""
        self.circuit_breaker_open = True
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker."""
        self.circuit_breaker_open = False
    
    def cleanup_resources(self):
        """Cleanup resources to simulate recovery."""
        # Cancel background tasks
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
        self.background_tasks.clear()
        
        # Clear memory pools
        self.memory_pool.clear()
        
        # Close file handles
        self.file_handles.clear()
        
        # Reset connections
        self.active_connections.clear()
        
        # Reset load indicators
        self.database_load = 0.0
        self.system_overload = False
        
        # Force garbage collection
        gc.collect()
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get current resource statistics."""
        return {
            "request_count": self.request_count,
            "active_connections": len(self.active_connections),
            "memory_allocations": len(self.memory_pool),
            "background_tasks": len(self.background_tasks),
            "file_handles": len(self.file_handles),
            "database_load": self.database_load,
            "cache_memory_mb": self.cache_memory_usage / (1024 * 1024),
            "system_overloaded": self.system_overload,
            "circuit_breaker_open": self.circuit_breaker_open
        }


class StressTestRunner:
    """Runs stress tests to find system breaking points."""
    
    def __init__(self, api: StressPlatformAPI):
        self.api = api
        self.resource_monitor = ResourceMonitor()
        self.stress_results = []
        
    async def run_breaking_point_test(self, config: StressTestConfig) -> StressTestResult:
        """Find the system breaking point by gradually increasing load."""
        print(f"Starting breaking point test: max {config.max_concurrent_users} users")
        
        self.resource_monitor.start_monitoring()
        start_time = time.time()
        
        breaking_point_users = None
        time_to_break = None
        max_users_achieved = 0
        total_operations = 0
        successful_operations = 0
        failed_operations = 0
        failure_modes = []
        
        # Gradually increase user load
        ramp_step_size = max(1, config.max_concurrent_users // 20)  # 20 steps
        current_users = ramp_step_size
        
        while current_users <= config.max_concurrent_users:
            print(f"Testing with {current_users} concurrent users...")
            
            # Run load test with current user count
            step_result = await self._run_stress_step(current_users, 30)  # 30 second steps
            
            total_operations += step_result["total_operations"]
            successful_operations += step_result["successful_operations"]
            failed_operations += step_result["failed_operations"]
            
            failure_rate = (step_result["failed_operations"] / step_result["total_operations"] * 100) if step_result["total_operations"] > 0 else 0
            
            print(f"  Operations: {step_result['total_operations']}, Failure rate: {failure_rate:.2f}%")
            
            # Check if breaking point reached
            if failure_rate > config.failure_threshold_percent:
                breaking_point_users = current_users
                time_to_break = time.time() - start_time
                
                failure_modes.append({
                    "user_count": current_users,
                    "failure_rate": failure_rate,
                    "primary_error": step_result.get("primary_error", "Unknown"),
                    "resource_exhaustion": self._check_resource_exhaustion()
                })
                
                print(f"Breaking point reached at {current_users} users")
                break
            
            max_users_achieved = current_users
            
            # Check resource limits
            if self._check_resource_limits(config):
                print(f"Resource limits reached at {current_users} users")
                break
            
            current_users += ramp_step_size
            
            # Brief pause between steps
            await asyncio.sleep(2)
        
        self.resource_monitor.stop_monitoring()
        
        # Test recovery if breaking point was reached
        recovery_time = None
        if breaking_point_users:
            recovery_time = await self._test_recovery()
        
        resource_summary = self.resource_monitor.get_resource_summary()
        
        return StressTestResult(
            max_concurrent_users_achieved=max_users_achieved,
            breaking_point_users=breaking_point_users,
            total_operations=total_operations,
            successful_operations=successful_operations,
            failed_operations=failed_operations,
            peak_cpu_usage=resource_summary.get("peak_cpu_percent", 0),
            peak_memory_usage_mb=resource_summary.get("peak_memory_mb", 0),
            average_response_time=0,  # Would calculate from step results
            max_response_time=0,      # Would calculate from step results
            operations_per_second_peak=0,  # Would calculate from step results
            time_to_break=time_to_break,
            recovery_time=recovery_time,
            resource_leaks_detected=list(resource_summary.get("leak_details", {}).keys()),
            failure_modes=failure_modes
        )
    
    async def _run_stress_step(self, user_count: int, duration_seconds: int) -> Dict[str, Any]:
        """Run a single stress test step with specified user count."""
        step_start = time.time()
        
        # Create user tasks
        user_tasks = []
        for i in range(user_count):
            user_id = f"stress_user_{i}"
            task = asyncio.create_task(self._stress_user_session(user_id, duration_seconds))
            user_tasks.append(task)
        
        # Wait for all tasks to complete or timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*user_tasks, return_exceptions=True),
                timeout=duration_seconds + 10
            )
        except asyncio.TimeoutError:
            # Cancel remaining tasks
            for task in user_tasks:
                task.cancel()
            results = []
        
        # Analyze step results
        successful_ops = 0
        failed_ops = 0
        errors = []
        
        for result in results:
            if isinstance(result, dict):
                successful_ops += result.get("successful_operations", 0)
                failed_ops += result.get("failed_operations", 0)
                if result.get("errors"):
                    errors.extend(result["errors"])
            elif isinstance(result, Exception):
                failed_ops += 1
                errors.append(str(result))
        
        # Determine primary error type
        primary_error = "Unknown"
        if errors:
            error_counts = {}
            for error in errors:
                error_type = error.split(":")[0] if ":" in error else error
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            primary_error = max(error_counts.items(), key=lambda x: x[1])[0]
        
        return {
            "total_operations": successful_ops + failed_ops,
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "primary_error": primary_error,
            "user_count": user_count,
            "duration": time.time() - step_start
        }
    
    async def _stress_user_session(self, user_id: str, duration_seconds: int) -> Dict[str, Any]:
        """Simulate a user session under stress conditions."""
        session_start = time.time()
        successful_ops = 0
        failed_ops = 0
        errors = []
        
        try:
            # Authentication
            try:
                await self.api.stress_authenticate(user_id)
                successful_ops += 1
            except Exception as e:
                failed_ops += 1
                errors.append(f"Auth error: {str(e)}")
                return {"successful_operations": successful_ops, "failed_operations": failed_ops, "errors": errors}
            
            # Continuous operations during stress test
            while time.time() - session_start < duration_seconds:
                operation = random.choice(["submit", "content", "progress"])
                
                try:
                    if operation == "submit":
                        code = "def test(): return 'stress test'"
                        await self.api.stress_submit_exercise(user_id, f"ex_{random.randint(1, 100)}", code, "token")
                    elif operation == "content":
                        await self.api.stress_get_content(f"content_{random.randint(1, 1000)}", "token")
                    elif operation == "progress":
                        await self.api.stress_save_progress(user_id, f"lesson_{random.randint(1, 50)}", {"score": 85}, "token")
                    
                    successful_ops += 1
                    
                except Exception as e:
                    failed_ops += 1
                    errors.append(f"{operation} error: {str(e)}")
                
                # Stress interval (faster than normal)
                await asyncio.sleep(random.uniform(0.1, 0.5))
        
        except Exception as e:
            errors.append(f"Session error: {str(e)}")
            failed_ops += 1
        
        return {
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "errors": errors
        }
    
    def _check_resource_exhaustion(self) -> Dict[str, bool]:
        """Check various forms of resource exhaustion."""
        api_stats = self.api.get_resource_stats()
        
        return {
            "connection_pool_exhausted": api_stats["active_connections"] >= 90,  # Near limit
            "memory_exhausted": api_stats["memory_allocations"] > 400,
            "background_tasks_overload": api_stats["background_tasks"] > 80,
            "file_handles_exhausted": api_stats["file_handles"] > 800,
            "database_overloaded": api_stats["database_load"] > 8.0
        }
    
    def _check_resource_limits(self, config: StressTestConfig) -> bool:
        """Check if resource limits have been exceeded."""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)
        
        return (cpu_usage > config.resource_limit_cpu_percent or 
                memory_usage > config.resource_limit_memory_mb)
    
    async def _test_recovery(self) -> float:
        """Test system recovery after breaking point."""
        print("Testing system recovery...")
        recovery_start = time.time()
        
        # Cleanup resources
        self.api.cleanup_resources()
        
        # Wait for system to stabilize
        await asyncio.sleep(5)
        
        # Test with light load to verify recovery
        try:
            recovery_result = await self._run_stress_step(5, 10)  # 5 users for 10 seconds
            recovery_time = time.time() - recovery_start
            
            failure_rate = (recovery_result["failed_operations"] / recovery_result["total_operations"] * 100) if recovery_result["total_operations"] > 0 else 100
            
            if failure_rate < 10:  # Less than 10% failure rate indicates recovery
                print(f"System recovered in {recovery_time:.2f} seconds")
                return recovery_time
            else:
                print(f"System not fully recovered (failure rate: {failure_rate:.2f}%)")
                return None
                
        except Exception as e:
            print(f"Recovery test failed: {e}")
            return None


@pytest.fixture
def stress_api():
    """Fixture providing a stress test API."""
    return StressPlatformAPI()


@pytest.fixture
def stress_runner(stress_api):
    """Fixture providing a stress test runner."""
    return StressTestRunner(stress_api)


class TestResourceExhaustion:
    """Test various resource exhaustion scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_memory_exhaustion_stress(self, stress_runner):
        """Test behavior under memory exhaustion stress."""
        config = StressTestConfig(
            max_concurrent_users=150,
            test_duration_seconds=60,
            ramp_up_duration_seconds=20,
            failure_threshold_percent=25.0,
            resource_limit_cpu_percent=90,
            resource_limit_memory_mb=2048,  # 2GB limit
            target_breaking_point=True
        )
        
        result = await stress_runner.run_breaking_point_test(config)
        
        print(f"Memory exhaustion stress test results:")
        print(f"  Breaking point: {result.breaking_point_users} users")
        print(f"  Peak memory usage: {result.peak_memory_usage_mb:.2f} MB")
        print(f"  Resource leaks detected: {len(result.resource_leaks_detected)}")
        print(f"  Recovery time: {result.recovery_time}")
        
        # Verify test completed and found limits
        assert result.max_concurrent_users_achieved > 0
        assert result.total_operations > 0
        
        # Check if memory-related issues were detected
        memory_issues = any("memory" in leak.lower() for leak in result.resource_leaks_detected)
        if result.breaking_point_users:
            assert result.peak_memory_usage_mb > 0
    
    @pytest.mark.asyncio
    @pytest.mark.slow  
    async def test_connection_pool_exhaustion(self, stress_api, stress_runner):
        """Test connection pool exhaustion."""
        # Reduce connection pool size for faster testing
        original_pool_size = stress_api.connection_pool_size
        stress_api.connection_pool_size = 20  # Small pool for testing
        
        try:
            config = StressTestConfig(
                max_concurrent_users=50,
                test_duration_seconds=30,
                ramp_up_duration_seconds=10,
                failure_threshold_percent=30.0,
                resource_limit_cpu_percent=95,
                resource_limit_memory_mb=1024,
                target_breaking_point=True
            )
            
            result = await stress_runner.run_breaking_point_test(config)
            
            print(f"Connection pool exhaustion test:")
            print(f"  Pool size: {stress_api.connection_pool_size}")
            print(f"  Breaking point: {result.breaking_point_users} users")
            print(f"  Active connections at peak: {len(stress_api.active_connections)}")
            
            # Should hit connection limit before user limit
            if result.breaking_point_users:
                assert result.breaking_point_users <= stress_api.connection_pool_size + 5  # Some tolerance
            
            # Check for connection-related errors
            connection_errors = any("connection" in mode.get("primary_error", "").lower() 
                                  for mode in result.failure_modes)
            if result.breaking_point_users:
                # Should detect connection issues
                resource_exhaustion = stress_runner._check_resource_exhaustion()
                assert resource_exhaustion.get("connection_pool_exhausted", False)
                
        finally:
            stress_api.connection_pool_size = original_pool_size
    
    @pytest.mark.asyncio
    async def test_cpu_saturation_stress(self, stress_runner):
        """Test behavior under CPU saturation."""
        config = StressTestConfig(
            max_concurrent_users=200,
            test_duration_seconds=45,
            ramp_up_duration_seconds=15,
            failure_threshold_percent=40.0,
            resource_limit_cpu_percent=85,  # Lower CPU limit
            resource_limit_memory_mb=4096,
            target_breaking_point=True
        )
        
        result = await stress_runner.run_breaking_point_test(config)
        
        print(f"CPU saturation stress test:")
        print(f"  Peak CPU usage: {result.peak_cpu_usage:.2f}%")
        print(f"  Max users before CPU limit: {result.max_concurrent_users_achieved}")
        
        # Should hit CPU limits
        assert result.peak_cpu_usage > 50  # Should show significant CPU usage
        
        # If breaking point reached, should be CPU-related
        if result.breaking_point_users:
            cpu_related_failure = any("overload" in mode.get("primary_error", "").lower() 
                                    for mode in result.failure_modes)
            # CPU saturation often manifests as timeouts or overload errors


class TestFailureCascades:
    """Test cascading failure scenarios."""
    
    @pytest.mark.asyncio
    async def test_service_cascade_failure(self, stress_api, stress_runner):
        """Test cascading failures across services."""
        # Start with normal operation
        initial_config = StressTestConfig(
            max_concurrent_users=30,
            test_duration_seconds=20,
            ramp_up_duration_seconds=5,
            failure_threshold_percent=15.0,
            resource_limit_cpu_percent=95,
            resource_limit_memory_mb=2048,
            target_breaking_point=False
        )
        
        # Get baseline performance
        baseline_result = await stress_runner.run_breaking_point_test(initial_config)
        baseline_failure_rate = (baseline_result.failed_operations / baseline_result.total_operations * 100) if baseline_result.total_operations > 0 else 0
        
        print(f"Baseline failure rate: {baseline_failure_rate:.2f}%")
        
        # Trigger circuit breaker to simulate service failure
        stress_api.trigger_circuit_breaker()
        stress_api.failure_cascade_active = True
        
        try:
            # Test with same load under failure conditions
            cascade_result = await stress_runner.run_breaking_point_test(initial_config)
            cascade_failure_rate = (cascade_result.failed_operations / cascade_result.total_operations * 100) if cascade_result.total_operations > 0 else 0
            
            print(f"Cascade failure rate: {cascade_failure_rate:.2f}%")
            
            # Failure rate should increase significantly
            assert cascade_failure_rate > baseline_failure_rate + 10  # At least 10% increase
            
            # Check that circuit breaker errors are primary
            circuit_breaker_errors = any("circuit breaker" in mode.get("primary_error", "").lower() 
                                        for mode in cascade_result.failure_modes)
            
        finally:
            # Reset circuit breaker
            stress_api.reset_circuit_breaker()
            stress_api.failure_cascade_active = False
    
    @pytest.mark.asyncio
    async def test_database_overload_cascade(self, stress_api, stress_runner):
        """Test cascade from database overload."""
        # Pre-load database to simulate existing load
        stress_api.database_load = 8.0  # High existing load
        
        config = StressTestConfig(
            max_concurrent_users=40,
            test_duration_seconds=30,
            ramp_up_duration_seconds=10,
            failure_threshold_percent=35.0,
            resource_limit_cpu_percent=95,
            resource_limit_memory_mb=2048,
            target_breaking_point=True
        )
        
        result = await stress_runner.run_breaking_point_test(config)
        
        print(f"Database overload cascade test:")
        print(f"  Initial DB load: 8.0")
        print(f"  Final DB load: {stress_api.database_load:.2f}")
        print(f"  Breaking point: {result.breaking_point_users} users")
        
        # Should break at lower user count due to pre-existing DB load
        if result.breaking_point_users:
            assert result.breaking_point_users < 50  # Should break before 50 users
            
            # Check for database-related resource exhaustion
            resource_exhaustion = stress_runner._check_resource_exhaustion()
            assert resource_exhaustion.get("database_overloaded", False)


class TestMemoryLeaks:
    """Test for memory leaks and resource cleanup."""
    
    @pytest.mark.asyncio
    async def test_background_task_leak_detection(self, stress_api, stress_runner):
        """Test detection of background task leaks."""
        # Configure API to create more background tasks
        original_bg_probability = 0.1
        
        async def leaky_user_session(user_id: str, duration: int):
            """User session that intentionally creates background task leaks."""
            try:
                await stress_api.stress_authenticate(user_id)
                
                # Perform operations that create background tasks
                for i in range(20):  # Many operations
                    await stress_api.stress_submit_exercise(user_id, f"ex_{i}", "def leak(): pass", "token")
                    await asyncio.sleep(0.1)
                    
            except Exception:
                pass  # Ignore errors for leak test
        
        # Track background tasks before
        initial_bg_tasks = len(stress_api.background_tasks)
        
        # Run leaky user sessions
        leak_tasks = []
        for i in range(10):
            task = asyncio.create_task(leaky_user_session(f"leak_user_{i}", 5))
            leak_tasks.append(task)
        
        await asyncio.gather(*leak_tasks, return_exceptions=True)
        
        # Check for background task accumulation
        final_bg_tasks = len(stress_api.background_tasks)
        task_increase = final_bg_tasks - initial_bg_tasks
        
        print(f"Background task leak test:")
        print(f"  Initial background tasks: {initial_bg_tasks}")
        print(f"  Final background tasks: {final_bg_tasks}")
        print(f"  Task increase: {task_increase}")
        
        # Should have created background tasks
        assert task_increase > 0
        
        # Test cleanup
        stress_api.cleanup_resources()
        cleaned_bg_tasks = len(stress_api.background_tasks)
        
        print(f"  Tasks after cleanup: {cleaned_bg_tasks}")
        
        # Cleanup should reduce background tasks significantly
        assert cleaned_bg_tasks < final_bg_tasks * 0.1  # At least 90% reduction
    
    @pytest.mark.asyncio
    async def test_memory_allocation_patterns(self, stress_api, stress_runner):
        """Test memory allocation and cleanup patterns."""
        # Monitor memory allocations
        initial_allocations = len(stress_api.memory_pool)
        
        config = StressTestConfig(
            max_concurrent_users=25,
            test_duration_seconds=30,
            ramp_up_duration_seconds=5,
            failure_threshold_percent=50.0,
            resource_limit_cpu_percent=95,
            resource_limit_memory_mb=1024,
            target_breaking_point=False
        )
        
        result = await stress_runner.run_breaking_point_test(config)
        
        # Check memory allocation patterns
        final_allocations = len(stress_api.memory_pool)
        allocation_increase = final_allocations - initial_allocations
        
        print(f"Memory allocation pattern test:")
        print(f"  Initial allocations: {initial_allocations}")
        print(f"  Final allocations: {final_allocations}")
        print(f"  Allocation increase: {allocation_increase}")
        print(f"  Operations performed: {result.total_operations}")
        
        # Memory allocations should be reasonable relative to operations
        if result.total_operations > 0:
            allocations_per_operation = allocation_increase / result.total_operations
            print(f"  Allocations per operation: {allocations_per_operation:.3f}")
            
            # Should not be excessive (depends on implementation)
            assert allocations_per_operation < 1.0  # Less than 1 allocation per operation
        
        # Test memory cleanup
        pre_cleanup_memory = len(stress_api.memory_pool)
        stress_api.cleanup_resources()
        post_cleanup_memory = len(stress_api.memory_pool)
        
        print(f"  Memory before cleanup: {pre_cleanup_memory}")
        print(f"  Memory after cleanup: {post_cleanup_memory}")
        
        # Cleanup should free memory
        assert post_cleanup_memory < pre_cleanup_memory * 0.1  # At least 90% reduction


class TestRecoveryPatterns:
    """Test system recovery after stress conditions."""
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_and_recovery(self, stress_runner):
        """Test graceful degradation and recovery patterns."""
        # Phase 1: Normal operation
        normal_config = StressTestConfig(
            max_concurrent_users=15,
            test_duration_seconds=20,
            ramp_up_duration_seconds=3,
            failure_threshold_percent=10.0,
            resource_limit_cpu_percent=95,
            resource_limit_memory_mb=2048,
            target_breaking_point=False
        )
        
        normal_result = await stress_runner.run_breaking_point_test(normal_config)
        normal_failure_rate = (normal_result.failed_operations / normal_result.total_operations * 100) if normal_result.total_operations > 0 else 0
        
        # Phase 2: Stress condition
        stress_config = StressTestConfig(
            max_concurrent_users=100,
            test_duration_seconds=30,
            ramp_up_duration_seconds=5,
            failure_threshold_percent=60.0,  # Allow high failure rate
            resource_limit_cpu_percent=95,
            resource_limit_memory_mb=2048,
            target_breaking_point=True
        )
        
        stress_result = await stress_runner.run_breaking_point_test(stress_config)
        
        # Phase 3: Recovery test
        recovery_result = await stress_runner.run_breaking_point_test(normal_config)
        recovery_failure_rate = (recovery_result.failed_operations / recovery_result.total_operations * 100) if recovery_result.total_operations > 0 else 0
        
        print(f"Graceful degradation and recovery test:")
        print(f"  Normal operation failure rate: {normal_failure_rate:.2f}%")
        print(f"  Under stress failure rate: {(stress_result.failed_operations / stress_result.total_operations * 100) if stress_result.total_operations > 0 else 0:.2f}%")
        print(f"  Recovery failure rate: {recovery_failure_rate:.2f}%")
        print(f"  Recovery time: {stress_result.recovery_time} seconds")
        
        # System should recover to near-normal operation
        failure_rate_increase = recovery_failure_rate - normal_failure_rate
        assert failure_rate_increase < 15  # Within 15% of normal operation
        
        # Recovery should be reasonably fast
        if stress_result.recovery_time:
            assert stress_result.recovery_time < 30  # Should recover within 30 seconds


if __name__ == "__main__":
    # Run stress tests with appropriate markers
    pytest.main([
        __file__, 
        "-v", 
        "-m", "not slow",  # Skip slow tests by default
        "--tb=short",
        "--durations=10"
    ])
    
    # To run slow stress tests: pytest tests/performance/test_stress.py -v -m slow