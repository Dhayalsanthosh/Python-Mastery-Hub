"""
Common utilities and base classes for the async programming module.
"""

import time
import asyncio
import threading
from typing import Dict, List, Any, Optional, Callable, Awaitable
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Performance metrics for comparing different approaches."""
    execution_time: float
    throughput: float  # items per second
    resource_usage: str
    approach_name: str
    
    def __str__(self):
        return (f"{self.approach_name}: {self.execution_time:.3f}s, "
                f"{self.throughput:.1f} items/sec, {self.resource_usage}")


class AsyncDemo(ABC):
    """Base class for async programming demonstrations."""
    
    def __init__(self, name: str):
        self.name = name
        self.examples = {}
    
    @abstractmethod
    def _setup_examples(self) -> None:
        """Setup examples for this demo."""
        pass
    
    def demonstrate(self) -> Dict[str, Any]:
        """Return demonstration content."""
        return {
            "name": self.name,
            "examples": self.examples,
            "explanation": self.get_explanation(),
            "best_practices": self.get_best_practices()
        }
    
    @abstractmethod
    def get_explanation(self) -> str:
        """Get explanation for this concept."""
        pass
    
    @abstractmethod
    def get_best_practices(self) -> List[str]:
        """Get best practices for this concept."""
        pass


class TimingContextManager:
    """Context manager for timing code execution."""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        print(f"Starting {self.description}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"{self.description} completed in {duration:.3f}s")
    
    @property
    def duration(self) -> float:
        """Get the duration of the timed operation."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


class AsyncTimingContextManager:
    """Async context manager for timing async operations."""
    
    def __init__(self, description: str = "Async Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        print(f"Starting {self.description}...")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"{self.description} completed in {duration:.3f}s")
    
    @property
    def duration(self) -> float:
        """Get the duration of the timed operation."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


def benchmark_approaches(*approaches: Callable) -> List[PerformanceMetrics]:
    """Benchmark multiple approaches and return performance metrics."""
    metrics = []
    
    for approach in approaches:
        start_time = time.time()
        
        # Run the approach
        if asyncio.iscoroutinefunction(approach):
            result = asyncio.run(approach())
        else:
            result = approach()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Extract metrics if the approach returns them
        if isinstance(result, dict) and 'items_processed' in result:
            throughput = result['items_processed'] / execution_time
            resource_usage = result.get('resource_usage', 'CPU')
        else:
            throughput = 1.0 / execution_time  # Default throughput
            resource_usage = 'Unknown'
        
        metrics.append(PerformanceMetrics(
            execution_time=execution_time,
            throughput=throughput,
            resource_usage=resource_usage,
            approach_name=approach.__name__
        ))
    
    return metrics


def print_performance_comparison(metrics: List[PerformanceMetrics]):
    """Print a formatted comparison of performance metrics."""
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    
    # Sort by execution time
    sorted_metrics = sorted(metrics, key=lambda m: m.execution_time)
    
    for i, metric in enumerate(sorted_metrics):
        print(f"{i+1}. {metric}")
        
        if i == 0:
            print("   ← FASTEST")
        elif i == len(sorted_metrics) - 1:
            print("   ← SLOWEST")
    
    # Calculate speedup
    if len(sorted_metrics) >= 2:
        fastest = sorted_metrics[0]
        slowest = sorted_metrics[-1]
        speedup = slowest.execution_time / fastest.execution_time
        print(f"\nSpeedup: {speedup:.2f}x ({fastest.approach_name} vs {slowest.approach_name})")


class ProgressTracker:
    """Track progress of long-running operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = 0
    
    def update(self, increment: int = 1):
        """Update progress."""
        self.current += increment
        
        # Only print updates occasionally to avoid spam
        now = time.time()
        if now - self.last_update > 1.0 or self.current == self.total:
            self._print_progress()
            self.last_update = now
    
    def _print_progress(self):
        """Print current progress."""
        percentage = (self.current / self.total) * 100
        elapsed = time.time() - self.start_time
        
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            print(f"{self.description}: {self.current}/{self.total} "
                  f"({percentage:.1f}%) - ETA: {eta:.1f}s")
        else:
            print(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")


class ThreadSafeCounter:
    """Thread-safe counter for use in concurrent examples."""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self, amount: int = 1) -> int:
        """Increment counter and return new value."""
        with self._lock:
            self._value += amount
            return self._value
    
    def decrement(self, amount: int = 1) -> int:
        """Decrement counter and return new value."""
        with self._lock:
            self._value -= amount
            return self._value
    
    @property
    def value(self) -> int:
        """Get current value."""
        with self._lock:
            return self._value
    
    def reset(self, new_value: int = 0):
        """Reset counter to new value."""
        with self._lock:
            self._value = new_value


def simulate_io_operation(duration: float, operation_name: str = "I/O operation"):
    """Simulate a blocking I/O operation."""
    print(f"Starting {operation_name} (blocking for {duration}s)")
    time.sleep(duration)
    print(f"Completed {operation_name}")
    return f"Result from {operation_name}"


async def simulate_async_io_operation(duration: float, operation_name: str = "async I/O operation"):
    """Simulate a non-blocking async I/O operation."""
    print(f"Starting {operation_name} (async wait for {duration}s)")
    await asyncio.sleep(duration)
    print(f"Completed {operation_name}")
    return f"Result from {operation_name}"


def simulate_cpu_work(iterations: int, operation_name: str = "CPU work"):
    """Simulate CPU-intensive work."""
    print(f"Starting {operation_name} ({iterations:,} iterations)")
    start = time.time()
    
    # Do some actual CPU work
    result = sum(i * i for i in range(iterations))
    
    duration = time.time() - start
    print(f"Completed {operation_name} in {duration:.3f}s, result: {result}")
    return result


class ResourceMonitor:
    """Monitor resource usage during operations."""
    
    def __init__(self):
        self.measurements = []
        self.start_time = None
    
    def start_monitoring(self):
        """Start monitoring resources."""
        self.start_time = time.time()
        self.measurements = []
    
    def record_measurement(self, description: str, **kwargs):
        """Record a measurement."""
        if self.start_time:
            timestamp = time.time() - self.start_time
            measurement = {
                'timestamp': timestamp,
                'description': description,
                **kwargs
            }
            self.measurements.append(measurement)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of measurements."""
        if not self.measurements:
            return {'message': 'No measurements recorded'}
        
        total_time = self.measurements[-1]['timestamp'] if self.measurements else 0
        
        return {
            'total_measurements': len(self.measurements),
            'total_time': total_time,
            'measurements': self.measurements
        }


# Common example functions used across modules
def create_sample_data(size: int, data_type: str = "numbers") -> List[Any]:
    """Create sample data for testing."""
    import random
    
    if data_type == "numbers":
        return [random.randint(1, 1000) for _ in range(size)]
    elif data_type == "strings":
        return [f"item_{i:04d}" for i in range(size)]
    elif data_type == "mixed":
        return [
            random.choice([
                random.randint(1, 100),
                f"string_{i}",
                random.random()
            ])
            for i in range(size)
        ]
    else:
        raise ValueError(f"Unknown data type: {data_type}")


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f}μs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def format_throughput(items_per_second: float) -> str:
    """Format throughput in human-readable format."""
    if items_per_second >= 1000000:
        return f"{items_per_second / 1000000:.2f}M items/sec"
    elif items_per_second >= 1000:
        return f"{items_per_second / 1000:.2f}K items/sec"
    else:
        return f"{items_per_second:.1f} items/sec"