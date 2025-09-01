"""
Concurrent futures concepts for the async programming module.
"""

import concurrent.futures
import time
import random
from typing import Dict, List, Any, Optional, Callable
from .base import AsyncDemo, simulate_io_operation, simulate_cpu_work


class ConcurrentFuturesConcepts(AsyncDemo):
    """Demonstrates concurrent.futures module concepts."""
    
    def __init__(self):
        super().__init__("Concurrent Futures")
        self._setup_examples()
    
    def _setup_examples(self) -> None:
        """Setup concurrent futures examples."""
        self.examples = {
            "thread_vs_process_pools": {
                "code": '''
import concurrent.futures
import time
import random

def simulate_io_task(task_id, duration=1.0):
    """Simulate I/O-bound task."""
    time.sleep(duration)
    return f"I/O Task {task_id} completed in {duration:.2f}s"

def simulate_cpu_task(n):
    """Simulate CPU-bound task."""
    result = sum(i * i for i in range(n))
    return f"CPU Task result: {result}"

def executor_comparison():
    """Compare ThreadPoolExecutor vs ProcessPoolExecutor."""
    print("=== Executor Comparison ===")
    
    # I/O-bound tasks with ThreadPoolExecutor
    print("I/O-bound tasks with ThreadPoolExecutor:")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        io_futures = [executor.submit(simulate_io_task, i, 0.5) for i in range(8)]
        io_results = [future.result() for future in io_futures]
    
    io_time = time.time() - start_time
    print(f"ThreadPool time: {io_time:.2f}s")
    
    # CPU-bound tasks with ProcessPoolExecutor
    print("\\nCPU-bound tasks with ProcessPoolExecutor:")
    start_time = time.time()
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        cpu_futures = [executor.submit(simulate_cpu_task, 100000) for i in range(4)]
        cpu_results = [future.result() for future in cpu_futures]
    
    cpu_time = time.time() - start_time
    print(f"ProcessPool time: {cpu_time:.2f}s")

executor_comparison()
''',
                "explanation": "concurrent.futures provides a unified interface for both thread and process-based parallelism"
            },
            
            "future_management": {
                "code": '''
import concurrent.futures
import time
import random

def advanced_future_patterns():
    """Demonstrate advanced future management patterns."""
    print("=== Advanced Future Patterns ===")
    
    def task_with_timeout(duration, task_id):
        """Task that takes specified duration."""
        time.sleep(duration)
        return f"Task {task_id} completed after {duration}s"
    
    # Pattern 1: Timeout handling
    print("Pattern 1: Timeout handling")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(task_with_timeout, 2.0, 1)
        
        try:
            result = future.result(timeout=1.0)
            print(f"Result: {result}")
        except concurrent.futures.TimeoutError:
            print("Task timed out!")
            future.cancel()  # Try to cancel
    
    # Pattern 2: Processing results as they complete
    print("\\nPattern 2: Processing as completed")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks with different durations
        futures = {
            executor.submit(task_with_timeout, random.uniform(0.1, 1.0), i): i 
            for i in range(5)
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            task_id = futures[future]
            try:
                result = future.result()
                print(f"Completed: {result}")
            except Exception as e:
                print(f"Task {task_id} failed: {e}")
    
    # Pattern 3: Bulk operations with map
    print("\\nPattern 3: Bulk operations with map")
    
    task_durations = [0.1, 0.3, 0.2, 0.4, 0.1]
    task_ids = list(range(len(task_durations)))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(task_with_timeout, task_durations, task_ids))
        
        for result in results:
            print(f"Map result: {result}")

advanced_future_patterns()
''',
                "explanation": "Future objects provide fine-grained control over task execution and result handling"
            },
            
            "exception_handling": {
                "code": '''
import concurrent.futures
import random
import time

def unreliable_task(task_id, failure_rate=0.3):
    """Task that randomly fails."""
    time.sleep(random.uniform(0.1, 0.5))
    
    if random.random() < failure_rate:
        raise ValueError(f"Task {task_id} failed!")
    
    return f"Task {task_id} succeeded"

def exception_handling_patterns():
    """Demonstrate exception handling in concurrent execution."""
    print("=== Exception Handling Patterns ===")
    
    # Pattern 1: Individual exception handling
    print("Pattern 1: Individual exception handling")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(unreliable_task, i) for i in range(5)]
        
        for i, future in enumerate(futures):
            try:
                result = future.result()
                print(f"  Success: {result}")
            except ValueError as e:
                print(f"  Failed: {e}")
            except Exception as e:
                print(f"  Unexpected error: {e}")
    
    # Pattern 2: Collecting all results including exceptions
    print("\\nPattern 2: Collecting results with exceptions")
    
    def safe_task_executor(task_func, *args, **kwargs):
        """Wrapper that catches exceptions."""
        try:
            return ('success', task_func(*args, **kwargs))
        except Exception as e:
            return ('error', str(e))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        wrapped_futures = [
            executor.submit(safe_task_executor, unreliable_task, i) 
            for i in range(5)
        ]
        
        results = [future.result() for future in wrapped_futures]
        
        successes = [result[1] for result in results if result[0] == 'success']
        failures = [result[1] for result in results if result[0] == 'error']
        
        print(f"  Successes: {len(successes)}")
        print(f"  Failures: {len(failures)}")
    
    # Pattern 3: Using as_completed with exception handling
    print("\\nPattern 3: Exception handling with as_completed")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_id = {executor.submit(unreliable_task, i): i for i in range(5)}
        
        completed_count = 0
        for future in concurrent.futures.as_completed(future_to_id):
            task_id = future_to_id[future]
            completed_count += 1
            
            try:
                result = future.result()
                print(f"  Task {task_id} completed ({completed_count}/5): {result}")
            except Exception as e:
                print(f"  Task {task_id} failed ({completed_count}/5): {e}")

exception_handling_patterns()
''',
                "explanation": "Proper exception handling ensures robust concurrent execution"
            },
            
            "performance_monitoring": {
                "code": '''
import concurrent.futures
import time
import threading
from collections import defaultdict

class PerformanceMonitor:
    """Monitor performance of concurrent execution."""
    
    def __init__(self):
        self.stats = defaultdict(list)
        self.lock = threading.Lock()
        self.start_time = None
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.stats.clear()
    
    def record_task_start(self, task_id):
        """Record task start time."""
        with self.lock:
            self.stats[f'task_{task_id}_start'].append(time.time())
    
    def record_task_end(self, task_id, success=True):
        """Record task end time."""
        with self.lock:
            self.stats[f'task_{task_id}_end'].append(time.time())
            self.stats[f'task_{task_id}_success'].append(success)
    
    def get_summary(self):
        """Get performance summary."""
        if not self.start_time:
            return "Monitoring not started"
        
        total_time = time.time() - self.start_time
        
        # Calculate task statistics
        task_times = []
        successful_tasks = 0
        failed_tasks = 0
        
        task_ids = set()
        for key in self.stats.keys():
            if key.endswith('_start'):
                task_id = key.replace('_start', '')
                task_ids.add(task_id)
        
        for task_id in task_ids:
            start_times = self.stats.get(f'{task_id}_start', [])
            end_times = self.stats.get(f'{task_id}_end', [])
            success_flags = self.stats.get(f'{task_id}_success', [])
            
            if start_times and end_times:
                task_duration = end_times[0] - start_times[0]
                task_times.append(task_duration)
                
                if success_flags and success_flags[0]:
                    successful_tasks += 1
                else:
                    failed_tasks += 1
        
        avg_task_time = sum(task_times) / len(task_times) if task_times else 0
        throughput = len(task_times) / total_time if total_time > 0 else 0
        
        return {
            'total_time': total_time,
            'total_tasks': len(task_times),
            'successful_tasks': successful_tasks,
            'failed_tasks': failed_tasks,
            'average_task_time': avg_task_time,
            'throughput': throughput,
            'task_times': task_times
        }

def monitored_task(task_id, duration, monitor, failure_rate=0.1):
    """Task with performance monitoring."""
    monitor.record_task_start(task_id)
    
    try:
        time.sleep(duration)
        
        if random.random() < failure_rate:
            raise ValueError(f"Task {task_id} failed")
        
        monitor.record_task_end(task_id, success=True)
        return f"Task {task_id} completed successfully"
        
    except Exception as e:
        monitor.record_task_end(task_id, success=False)
        raise

def performance_monitoring_example():
    """Demonstrate performance monitoring."""
    print("=== Performance Monitoring Example ===")
    
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # Generate tasks with varying durations
    task_durations = [random.uniform(0.1, 0.5) for _ in range(10)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(monitored_task, i, duration, monitor)
            for i, duration in enumerate(task_durations)
        ]
        
        # Wait for all tasks to complete
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(('success', result))
            except Exception as e:
                results.append(('failure', str(e)))
    
    # Print performance summary
    summary = monitor.get_summary()
    
    print(f"\\nPerformance Summary:")
    print(f"Total execution time: {summary['total_time']:.3f}s")
    print(f"Total tasks: {summary['total_tasks']}")
    print(f"Successful tasks: {summary['successful_tasks']}")
    print(f"Failed tasks: {summary['failed_tasks']}")
    print(f"Average task time: {summary['average_task_time']:.3f}s")
    print(f"Throughput: {summary['throughput']:.2f} tasks/second")
    
    # Show results
    print(f"\\nTask Results:")
    for i, (status, result) in enumerate(results):
        print(f"  Task {i}: {status.upper()} - {result}")

performance_monitoring_example()
''',
                "explanation": "Performance monitoring helps optimize concurrent execution and identify bottlenecks"
            },
            
            "adaptive_concurrency": {
                "code": '''
import concurrent.futures
import time
import threading
from typing import Callable, Any

class AdaptiveConcurrencyManager:
    """Automatically adjusts concurrency based on performance."""
    
    def __init__(self, initial_workers=2, min_workers=1, max_workers=8):
        self.current_workers = initial_workers
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.performance_history = []
        self.lock = threading.Lock()
    
    def execute_with_adaptive_concurrency(self, tasks, task_func):
        """Execute tasks with adaptive concurrency adjustment."""
        print(f"Starting with {self.current_workers} workers")
        
        while tasks:
            # Take a batch of tasks
            batch_size = min(len(tasks), self.current_workers * 2)
            current_batch = tasks[:batch_size]
            tasks = tasks[batch_size:]
            
            # Execute current batch
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.current_workers) as executor:
                futures = [executor.submit(task_func, task) for task in current_batch]
                results = [future.result() for future in futures]
            
            execution_time = time.time() - start_time
            throughput = len(current_batch) / execution_time
            
            # Record performance
            with self.lock:
                self.performance_history.append({
                    'workers': self.current_workers,
                    'batch_size': len(current_batch),
                    'execution_time': execution_time,
                    'throughput': throughput
                })
            
            print(f"Batch completed: {len(current_batch)} tasks, "
                  f"{self.current_workers} workers, "
                  f"throughput: {throughput:.2f} tasks/sec")
            
            # Adjust concurrency based on performance
            if len(self.performance_history) >= 2:
                self._adjust_concurrency()
            
            if tasks:
                print(f"Remaining tasks: {len(tasks)}, "
                      f"adjusted to {self.current_workers} workers")
        
        return self.performance_history
    
    def _adjust_concurrency(self):
        """Adjust concurrency based on recent performance."""
        if len(self.performance_history) < 2:
            return
        
        recent = self.performance_history[-1]
        previous = self.performance_history[-2]
        
        # Compare throughput
        if recent['throughput'] > previous['throughput'] * 1.1:
            # Performance improved, consider increasing workers
            if self.current_workers < self.max_workers:
                self.current_workers = min(self.current_workers + 1, self.max_workers)
                print(f"  ↗ Increased workers to {self.current_workers}")
        elif recent['throughput'] < previous['throughput'] * 0.9:
            # Performance degraded, consider decreasing workers
            if self.current_workers > self.min_workers:
                self.current_workers = max(self.current_workers - 1, self.min_workers)
                print(f"  ↘ Decreased workers to {self.current_workers}")

def variable_duration_task(task_id):
    """Task with variable duration to test adaptive concurrency."""
    # Simulate different types of tasks
    if task_id % 3 == 0:
        duration = 0.5  # Long task
    elif task_id % 3 == 1:
        duration = 0.2  # Medium task
    else:
        duration = 0.1  # Short task
    
    time.sleep(duration)
    return f"Task {task_id} completed ({duration}s)"

def adaptive_concurrency_example():
    """Demonstrate adaptive concurrency management."""
    print("=== Adaptive Concurrency Example ===")
    
    # Create manager and tasks
    manager = AdaptiveConcurrencyManager(initial_workers=2, max_workers=6)
    tasks = list(range(30))  # 30 tasks
    
    # Execute with adaptive concurrency
    performance_history = manager.execute_with_adaptive_concurrency(
        tasks, variable_duration_task
    )
    
    # Analyze performance evolution
    print(f"\\nPerformance Evolution:")
    print(f"{'Batch':<5} {'Workers':<7} {'Tasks':<5} {'Time':<8} {'Throughput':<10}")
    print("-" * 45)
    
    for i, record in enumerate(performance_history):
        print(f"{i+1:<5} {record['workers']:<7} {record['batch_size']:<5} "
              f"{record['execution_time']:<8.3f} {record['throughput']:<10.2f}")
    
    # Summary
    if performance_history:
        avg_throughput = sum(r['throughput'] for r in performance_history) / len(performance_history)
        final_workers = performance_history[-1]['workers']
        
        print(f"\\nSummary:")
        print(f"Average throughput: {avg_throughput:.2f} tasks/sec")
        print(f"Final worker count: {final_workers}")

adaptive_concurrency_example()
''',
                "explanation": "Adaptive concurrency automatically optimizes the number of workers based on performance feedback"
            }
        }
    
    def get_explanation(self) -> str:
        """Get explanation for concurrent futures."""
        return (
            "The concurrent.futures module provides a high-level interface "
            "for asynchronously executing callables using threads or processes. "
            "It offers a unified API that works with both ThreadPoolExecutor "
            "and ProcessPoolExecutor, making it easy to write code that can "
            "be adapted for different types of workloads."
        )
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for concurrent futures."""
        return [
            "Choose ThreadPoolExecutor for I/O-bound tasks",
            "Choose ProcessPoolExecutor for CPU-bound tasks",
            "Use context managers (with statement) for automatic cleanup",
            "Handle timeouts appropriately with future.result(timeout=...)",
            "Use as_completed() for processing results as they finish",
            "Implement proper exception handling for robust execution",
            "Monitor performance to optimize worker count",
            "Use map() for simple parallel operations on sequences", 
            "Cancel futures when appropriate to free resources",
            "Be mindful of memory usage with large numbers of futures"
        ]


class FutureResultCollector:
    """Utility class for collecting and managing future results."""
    
    def __init__(self):
        self.results = {}
        self.exceptions = {}
        self.completion_times = {}
        self.lock = threading.Lock()
    
    def add_future(self, future_id: str, future: concurrent.futures.Future):
        """Add a future to be tracked."""
        def done_callback(fut):
            completion_time = time.time()
            
            with self.lock:
                self.completion_times[future_id] = completion_time
                
                try:
                    result = fut.result()
                    self.results[future_id] = result
                except Exception as e:
                    self.exceptions[future_id] = e
        
        future.add_done_callback(done_callback)
    
    def wait_for_all(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for all futures to complete and return summary."""
        start_time = time.time()
        
        while timeout is None or (time.time() - start_time) < timeout:
            with self.lock:
                total_futures = len(self.results) + len(self.exceptions)
                if len(self.completion_times) == total_futures:
                    break
            
            time.sleep(0.1)
        
        with self.lock:
            return {
                'successful_results': dict(self.results),
                'exceptions': dict(self.exceptions),
                'completion_times': dict(self.completion_times),
                'total_completed': len(self.completion_times)
            }


def demonstrate_future_patterns():
    """Demonstrate various future usage patterns."""
    print("=== Future Usage Patterns ===")
    
    def sample_task(task_id: int, duration: float) -> str:
        time.sleep(duration)
        if task_id == 3:  # Simulate one failure
            raise ValueError(f"Task {task_id} failed")
        return f"Task {task_id} result"
    
    # Pattern 1: Submit and collect
    print("Pattern 1: Submit and collect all results")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            f"task_{i}": executor.submit(sample_task, i, 0.5)
            for i in range(5)
        }
        
        collector = FutureResultCollector()
        for future_id, future in futures.items():
            collector.add_future(future_id, future)
        
        summary = collector.wait_for_all(timeout=5.0)
        
        print(f"  Successful: {len(summary['successful_results'])}")
        print(f"  Failed: {len(summary['exceptions'])}")
        print(f"  Total completed: {summary['total_completed']}")


if __name__ == "__main__":
    demonstrate_future_patterns()