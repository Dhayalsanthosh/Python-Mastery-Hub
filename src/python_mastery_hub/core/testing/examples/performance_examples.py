"""
Performance testing examples for the Testing module.
Demonstrates testing code speed, memory usage, and scalability.
"""

from typing import Dict, Any


def get_performance_examples() -> Dict[str, Any]:
    """Get comprehensive performance testing examples."""
    return {
        "basic_performance": {
            "code": '''
import unittest
import time
import cProfile
import io
import pstats
from contextlib import contextmanager
from typing import List, Callable

class PerformanceTestCase(unittest.TestCase):
    """Base class for performance testing."""
    
    @contextmanager
    def assertExecutionTime(self, max_time: float, message: str = ""):
        """Context manager to assert execution time."""
        start_time = time.time()
        yield
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.assertLessEqual(
            execution_time, max_time,
            f"Execution took {execution_time:.4f}s, expected <= {max_time}s. {message}"
        )
    
    def profile_function(self, func: Callable, *args, **kwargs) -> tuple:
        """Profile a function and return result and stats."""
        profiler = cProfile.Profile()
        
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        # Capture stats
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 functions
        
        return result, stats_stream.getvalue()
    
    def benchmark_function(self, func: Callable, iterations: int = 1000, 
                          *args, **kwargs) -> dict:
        """Benchmark a function over multiple iterations."""
        times = []
        
        for _ in range(iterations):
            start_time = time.time()
            func(*args, **kwargs)
            end_time = time.time()
            times.append(end_time - start_time)
        
        return {
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': sum(times) / len(times),
            'total_time': sum(times),
            'iterations': iterations
        }

# Example algorithms for performance testing
class SortingAlgorithms:
    """Various sorting algorithms for performance comparison."""
    
    @staticmethod
    def bubble_sort(data: List[int]) -> List[int]:
        """Inefficient bubble sort for comparison."""
        arr = data.copy()
        n = len(arr)
        
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        
        return arr
    
    @staticmethod
    def quick_sort(data: List[int]) -> List[int]:
        """Efficient quick sort."""
        if len(data) <= 1:
            return data
        
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        
        return SortingAlgorithms.quick_sort(left) + middle + SortingAlgorithms.quick_sort(right)
    
    @staticmethod
    def python_sort(data: List[int]) -> List[int]:
        """Python's built-in sort."""
        return sorted(data)

class TestSortingPerformance(PerformanceTestCase):
    """Performance tests for sorting algorithms."""
    
    def setUp(self):
        """Set up test data of different sizes."""
        import random
        self.small_data = [random.randint(1, 1000) for _ in range(100)]
        self.medium_data = [random.randint(1, 1000) for _ in range(1000)]
        self.large_data = [random.randint(1, 1000) for _ in range(5000)]
    
    def test_bubble_sort_performance(self):
        """Test bubble sort performance on different data sizes."""
        # Small data should complete quickly
        with self.assertExecutionTime(0.1, "Bubble sort on small data"):
            SortingAlgorithms.bubble_sort(self.small_data)
        
        # Medium data should complete within reasonable time
        with self.assertExecutionTime(5.0, "Bubble sort on medium data"):
            SortingAlgorithms.bubble_sort(self.medium_data)
    
    def test_quick_sort_performance(self):
        """Test quick sort performance."""
        with self.assertExecutionTime(0.01, "Quick sort on small data"):
            SortingAlgorithms.quick_sort(self.small_data)
        
        with self.assertExecutionTime(0.1, "Quick sort on medium data"):
            SortingAlgorithms.quick_sort(self.medium_data)
        
        with self.assertExecutionTime(0.5, "Quick sort on large data"):
            SortingAlgorithms.quick_sort(self.large_data)
    
    def test_python_sort_performance(self):
        """Test Python's built-in sort performance."""
        with self.assertExecutionTime(0.005, "Python sort on small data"):
            SortingAlgorithms.python_sort(self.small_data)
        
        with self.assertExecutionTime(0.01, "Python sort on medium data"):
            SortingAlgorithms.python_sort(self.medium_data)
        
        with self.assertExecutionTime(0.05, "Python sort on large data"):
            SortingAlgorithms.python_sort(self.large_data)
    
    def test_sorting_algorithm_comparison(self):
        """Compare different sorting algorithms."""
        import random
        test_data = [random.randint(1, 1000) for _ in range(500)]
        
        # Benchmark all sorting methods
        bubble_stats = self.benchmark_function(
            SortingAlgorithms.bubble_sort, 10, test_data
        )
        
        quick_stats = self.benchmark_function(
            SortingAlgorithms.quick_sort, 100, test_data
        )
        
        python_stats = self.benchmark_function(
            SortingAlgorithms.python_sort, 1000, test_data
        )
        
        print(f"\\nSorting Performance Comparison (500 elements):")
        print(f"Bubble Sort (10 runs): {bubble_stats['avg_time']:.6f}s avg")
        print(f"Quick Sort (100 runs): {quick_stats['avg_time']:.6f}s avg")
        print(f"Python Sort (1000 runs): {python_stats['avg_time']:.6f}s avg")
        
        # Python sort should be fastest
        self.assertLess(python_stats['avg_time'], quick_stats['avg_time'])
        self.assertLess(quick_stats['avg_time'], bubble_stats['avg_time'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Basic performance testing with timing assertions and algorithm benchmarking"
        },
        
        "memory_performance": {
            "code": '''
import unittest
import sys
import gc
from typing import Generator

class MemoryPerformanceTest(unittest.TestCase):
    """Test memory usage and performance."""
    
    def setUp(self):
        """Set up memory tracking."""
        gc.collect()  # Clean up before testing
    
    def get_memory_usage(self):
        """Get current memory usage (simplified)."""
        # This is a basic implementation
        # In practice, you might use psutil or memory_profiler
        return sys.getsizeof(gc.get_objects())
    
    def test_list_vs_generator_memory(self):
        """Compare memory usage of lists vs generators."""
        def create_large_list(n):
            return [i ** 2 for i in range(n)]
        
        def create_large_generator(n):
            return (i ** 2 for i in range(n))
        
        n = 100000
        
        # Test list creation
        start_memory = self.get_memory_usage()
        large_list = create_large_list(n)
        list_memory = self.get_memory_usage() - start_memory
        
        # Use some of the list to prevent optimization
        _ = sum(large_list[:10])
        
        # Test generator creation
        start_memory = self.get_memory_usage()
        large_gen = create_large_generator(n)
        gen_memory = self.get_memory_usage() - start_memory
        
        # Use some of the generator
        _ = sum(next(large_gen) for _ in range(10))
        
        print(f"\\nMemory Usage Comparison:")
        print(f"List memory impact: {list_memory}")
        print(f"Generator memory impact: {gen_memory}")
        
        # Generator should use less memory
        self.assertLess(gen_memory, list_memory)
    
    def test_string_concatenation_memory(self):
        """Test memory efficiency of string operations."""
        def concatenate_with_plus(strings):
            result = ""
            for s in strings:
                result += s
            return result
        
        def concatenate_with_join(strings):
            return "".join(strings)
        
        test_strings = [f"string_{i}" for i in range(1000)]
        
        # Test + operator
        start_memory = self.get_memory_usage()
        result_plus = concatenate_with_plus(test_strings[:100])  # Smaller set for + operator
        plus_memory = self.get_memory_usage() - start_memory
        
        # Test join
        start_memory = self.get_memory_usage()
        result_join = concatenate_with_join(test_strings)
        join_memory = self.get_memory_usage() - start_memory
        
        print(f"\\nString Concatenation Memory:")
        print(f"+ operator memory impact: {plus_memory}")
        print(f"join() memory impact: {join_memory}")
        
        # Both should produce valid results
        self.assertIsInstance(result_plus, str)
        self.assertIsInstance(result_join, str)

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Memory performance testing comparing different data structures and operations"
        },
        
        "scalability_testing": {
            "code": '''
import unittest
import time
import random
from typing import List, Dict

class ScalabilityTest(unittest.TestCase):
    """Test how algorithms scale with input size."""
    
    def test_algorithm_scalability(self):
        """Test how algorithm performance scales with input size."""
        def linear_search(data: List[int], target: int) -> int:
            """O(n) linear search."""
            for i, value in enumerate(data):
                if value == target:
                    return i
            return -1
        
        def binary_search(data: List[int], target: int) -> int:
            """O(log n) binary search on sorted data."""
            left, right = 0, len(data) - 1
            
            while left <= right:
                mid = (left + right) // 2
                if data[mid] == target:
                    return mid
                elif data[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1
            return -1
        
        # Test different data sizes
        sizes = [1000, 5000, 10000, 25000]
        
        linear_times = []
        binary_times = []
        
        for size in sizes:
            # Create sorted test data
            data = list(range(size))
            target = size // 2  # Middle element
            
            # Time linear search
            start_time = time.time()
            for _ in range(100):  # Multiple iterations for accuracy
                linear_search(data, target)
            linear_time = (time.time() - start_time) / 100
            linear_times.append(linear_time)
            
            # Time binary search
            start_time = time.time()
            for _ in range(1000):  # More iterations since it's faster
                binary_search(data, target)
            binary_time = (time.time() - start_time) / 1000
            binary_times.append(binary_time)
        
        print(f"\\nScalability Test Results:")
        for i, size in enumerate(sizes):
            print(f"Size {size}: Linear={linear_times[i]:.6f}s, Binary={binary_times[i]:.6f}s")
        
        # Test scalability properties
        # Linear search should scale linearly
        ratio_2_to_1 = linear_times[1] / linear_times[0]
        ratio_4_to_1 = linear_times[3] / linear_times[0]
        
        # Binary search should scale logarithmically (much slower growth)
        binary_ratio_2_to_1 = binary_times[1] / binary_times[0]
        binary_ratio_4_to_1 = binary_times[3] / binary_times[0]
        
        print(f"\\nScaling ratios:")
        print(f"Linear search 5k/1k: {ratio_2_to_1:.2f}x")
        print(f"Linear search 25k/1k: {ratio_4_to_1:.2f}x")
        print(f"Binary search 5k/1k: {binary_ratio_2_to_1:.2f}x")
        print(f"Binary search 25k/1k: {binary_ratio_4_to_1:.2f}x")
        
        # Binary search should scale much better
        self.assertLess(binary_ratio_4_to_1, ratio_4_to_1)
    
    def test_load_simulation(self):
        """Simulate load testing with concurrent operations."""
        def simulate_database_operation():
            """Simulate a database operation."""
            time.sleep(0.001)  # Simulate I/O delay
            return {"result": "success", "timestamp": time.time()}
        
        def simulate_user_requests(num_requests: int) -> List[Dict]:
            """Simulate multiple user requests."""
            results = []
            start_time = time.time()
            
            for _ in range(num_requests):
                result = simulate_database_operation()
                results.append(result)
            
            end_time = time.time()
            
            return {
                "results": results,
                "total_time": end_time - start_time,
                "requests_per_second": num_requests / (end_time - start_time)
            }
        
        # Test different load levels
        load_levels = [10, 50, 100, 200]
        
        for load in load_levels:
            performance = simulate_user_requests(load)
            
            print(f"\\nLoad test - {load} requests:")
            print(f"Total time: {performance['total_time']:.3f}s")
            print(f"Requests/second: {performance['requests_per_second']:.1f}")
            
            # Assert reasonable performance
            self.assertLess(performance['total_time'], load * 0.01)  # Should be faster than 10ms per request
            self.assertEqual(len(performance['results']), load)

# Performance monitoring and reporting
class PerformanceMonitor:
    """Monitor and report performance metrics."""
    
    def __init__(self):
        self.metrics = []
    
    def record_metric(self, name: str, value: float, unit: str = "seconds"):
        """Record a performance metric."""
        self.metrics.append({
            "name": name,
            "value": value,
            "unit": unit,
            "timestamp": time.time()
        })
    
    def get_summary(self) -> Dict:
        """Get performance summary."""
        if not self.metrics:
            return {"message": "No metrics recorded"}
        
        return {
            "total_metrics": len(self.metrics),
            "metrics": self.metrics,
            "slowest_operation": max(self.metrics, key=lambda m: m["value"]),
            "fastest_operation": min(self.metrics, key=lambda m: m["value"])
        }

class TestPerformanceMonitoring(unittest.TestCase):
    """Test performance monitoring capabilities."""
    
    def setUp(self):
        """Set up performance monitor."""
        self.monitor = PerformanceMonitor()
    
    def test_performance_monitoring(self):
        """Test performance monitoring and reporting."""
        # Simulate various operations
        operations = [
            ("fast_operation", 0.001),
            ("medium_operation", 0.01),
            ("slow_operation", 0.1),
            ("another_fast_operation", 0.002)
        ]
        
        for name, duration in operations:
            start_time = time.time()
            time.sleep(duration)  # Simulate work
            actual_duration = time.time() - start_time
            self.monitor.record_metric(name, actual_duration)
        
        # Get performance summary
        summary = self.monitor.get_summary()
        
        # Verify monitoring
        self.assertEqual(summary["total_metrics"], 4)
        self.assertIn("slowest_operation", summary)
        self.assertIn("fastest_operation", summary)
        
        # Slowest should be the 0.1s operation
        slowest = summary["slowest_operation"]
        self.assertEqual(slowest["name"], "slow_operation")
        
        print(f"\\nPerformance Summary:")
        print(f"Total metrics: {summary['total_metrics']}")
        print(f"Slowest: {slowest['name']} ({slowest['value']:.4f}s)")
        print(f"Fastest: {summary['fastest_operation']['name']} ({summary['fastest_operation']['value']:.4f}s)")

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Scalability testing and load simulation to verify performance under different conditions"
        }
    }