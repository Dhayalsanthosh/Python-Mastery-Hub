"""
Performance analysis examples for the Data Structures module.
Covers time complexity, benchmarking, and optimization strategies.
"""

from typing import Dict, Any


class PerformanceExamples:
    """Performance analysis examples and demonstrations."""
    
    @staticmethod
    def get_time_complexity_analysis() -> Dict[str, Any]:
        """Get comprehensive time complexity analysis examples."""
        return {
            "code": '''
import time
import random
import sys
from collections import deque

def time_operation(func, *args, **kwargs):
    """Utility function to time operations."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return result, (end - start) * 1000  # Return result and time in ms

def test_membership_performance():
    """Compare list vs set membership testing - O(n) vs O(1)."""
    print("=== Membership Testing Performance ===")
    print("Operation: item in collection")
    print("List: O(n) - Set: O(1)")
    print()
    
    sizes = [100, 1000, 5000, 10000]
    
    print(f"{'Size':>6} {'List (ms)':>10} {'Set (ms)':>9} {'Ratio':>8}")
    print("-" * 40)
    
    for size in sizes:
        # Create test data
        data_list = list(range(size))
        data_set = set(range(size))
        search_item = size - 1  # Worst case for list (last item)
        
        # Time list membership (linear search)
        _, list_time = time_operation(lambda: search_item in data_list)
        
        # Time set membership (hash lookup)
        _, set_time = time_operation(lambda: search_item in data_set)
        
        ratio = list_time / set_time if set_time > 0 else float('inf')
        print(f"{size:>6} {list_time:>9.3f} {set_time:>8.3f} {ratio:>7.1f}x")

def test_lookup_performance():
    """Compare list vs dict for key-based lookups."""
    print("\\n=== Lookup Performance Comparison ===")
    print("Operation: find value by key")
    print("List: O(n) - Dict: O(1)")
    print()
    
    sizes = [100, 1000, 5000, 10000]
    
    print(f"{'Size':>6} {'List (ms)':>10} {'Dict (ms)':>10} {'Ratio':>8}")
    print("-" * 45)
    
    for size in sizes:
        # Create test data
        keys = [f"key_{i}" for i in range(size)]
        values = [f"value_{i}" for i in range(size)]
        
        # List of tuples (linear search required)
        data_list = list(zip(keys, values))
        
        # Dictionary (hash table)
        data_dict = dict(zip(keys, values))
        
        search_key = keys[-1]  # Worst case for list
        
        # Time list lookup
        def list_lookup():
            for key, value in data_list:
                if key == search_key:
                    return value
            return None
        
        _, list_time = time_operation(list_lookup)
        
        # Time dict lookup
        _, dict_time = time_operation(lambda: data_dict.get(search_key))
        
        ratio = list_time / dict_time if dict_time > 0 else float('inf')
        print(f"{size:>6} {list_time:>9.3f} {dict_time:>9.3f} {ratio:>7.1f}x")

def test_insertion_performance():
    """Compare insertion performance of different data structures."""
    print("\\n=== Insertion Performance Comparison ===")
    print("Testing different insertion patterns")
    print()
    
    n = 5000
    
    # List append at end - O(1) amortized
    def list_append_test():
        lst = []
        for i in range(n):
            lst.append(i)
        return lst
    
    # List insert at beginning - O(n) per operation
    def list_prepend_test():
        lst = []
        for i in range(min(n // 10, 500)):  # Reduced for performance
            lst.insert(0, i)
        return lst
    
    # Deque append at end - O(1)
    def deque_append_test():
        dq = deque()
        for i in range(n):
            dq.append(i)
        return dq
    
    # Deque append at beginning - O(1)
    def deque_prepend_test():
        dq = deque()
        for i in range(n):
            dq.appendleft(i)
        return dq
    
    # Set add - O(1) average
    def set_add_test():
        s = set()
        for i in range(n):
            s.add(i)
        return s
    
    # Dict insert - O(1) average
    def dict_insert_test():
        d = {}
        for i in range(n):
            d[i] = f"value_{i}"
        return d
    
    tests = [
        ("List append", list_append_test, "O(1) amortized"),
        ("List prepend", list_prepend_test, "O(n) per operation"),
        ("Deque append", deque_append_test, "O(1)"),
        ("Deque prepend", deque_prepend_test, "O(1)"),
        ("Set add", set_add_test, "O(1) average"),
        ("Dict insert", dict_insert_test, "O(1) average")
    ]
    
    print(f"{'Operation':>15} {'Time (ms)':>12} {'Complexity':>20}")
    print("-" * 50)
    
    for name, test_func, complexity in tests:
        _, exec_time = time_operation(test_func)
        print(f"{name:>15} {exec_time:>11.3f} {complexity:>20}")

def test_sorting_performance():
    """Compare sorting algorithm performance."""
    print("\\n=== Sorting Performance Comparison ===")
    print("Testing different sorting approaches")
    print()
    
    sizes = [1000, 5000, 10000]
    
    def bubble_sort(arr):
        """O(n²) sorting algorithm."""
        arr = arr.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr
    
    def quick_sort(arr):
        """O(n log n) average case sorting."""
        if len(arr) <= 1:
            return arr
        
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        
        return quick_sort(left) + middle + quick_sort(right)
    
    print(f"{'Size':>6} {'Bubble O(n²)':>15} {'Quick O(n log n)':>18} {'Built-in':>12} {'Ratio':>8}")
    print("-" * 70)
    
    for size in sizes:
        # Generate random data
        data = [random.randint(1, 1000) for _ in range(size)]
        
        # Test bubble sort (only for smaller sizes)
        if size <= 5000:
            _, bubble_time = time_operation(bubble_sort, data)
        else:
            bubble_time = float('inf')
        
        # Test quick sort
        _, quick_time = time_operation(quick_sort, data)
        
        # Test built-in sort (Timsort - optimized merge sort)
        _, builtin_time = time_operation(sorted, data)
        
        bubble_ratio = bubble_time / builtin_time if builtin_time > 0 and bubble_time != float('inf') else float('inf')
        
        bubble_str = f"{bubble_time:>14.1f}" if bubble_time != float('inf') else f"{'Too slow':>14}"
        ratio_str = f"{bubble_ratio:>7.0f}x" if bubble_ratio != float('inf') else f"{'---':>7}"
        
        print(f"{size:>6} {bubble_str} {quick_time:>17.3f} {builtin_time:>11.3f} {ratio_str}")

def analyze_memory_usage():
    """Analyze memory usage of different data structures."""
    print("\\n=== Memory Usage Analysis ===")
    print("Comparing memory overhead of data structures")
    print()
    
    def get_size_mb(obj):
        """Get size of object in MB."""
        return sys.getsizeof(obj) / (1024 * 1024)
    
    n = 100000
    
    # Create different data structures with same data
    data_list = list(range(n))
    data_tuple = tuple(range(n))
    data_set = set(range(n))
    data_dict = {i: i for i in range(n)}
    
    structures = [
        ("List", data_list),
        ("Tuple", data_tuple),
        ("Set", data_set),
        ("Dict", data_dict)
    ]
    
    print(f"{'Structure':>10} {'Size (MB)':>12} {'Per Item (bytes)':>18}")
    print("-" * 45)
    
    for name, structure in structures:
        size_mb = get_size_mb(structure)
        per_item = sys.getsizeof(structure) / len(structure)
        print(f"{name:>10} {size_mb:>11.3f} {per_item:>17.1f}")

def demonstrate_big_o_scaling():
    """Demonstrate how algorithms scale with input size."""
    print("\\n=== Big O Scaling Demonstration ===")
    print("Showing actual time scaling for different complexities")
    print()
    
    def constant_time_op(n):
        """O(1) - accessing dict by key."""
        data = {i: i for i in range(n)}
        return data.get(n // 2)
    
    def linear_time_op(n):
        """O(n) - finding item in list."""
        data = list(range(n))
        return n // 2 in data
    
    def quadratic_time_op(n):
        """O(n²) - nested loop operation."""
        count = 0
        for i in range(min(n, 1000)):  # Limited for performance
            for j in range(min(n, 1000)):
                count += 1
        return count
    
    def log_time_op(n):
        """O(log n) - binary search."""
        data = list(range(n))
        target = n // 2
        
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
    
    sizes = [100, 1000, 5000, 10000]
    
    operations = [
        ("O(1) - Dict lookup", constant_time_op),
        ("O(log n) - Binary search", log_time_op),
        ("O(n) - Linear search", linear_time_op),
        ("O(n²) - Nested loops", quadratic_time_op)
    ]
    
    print(f"{'Operation':>25} " + "".join([f"{size:>10}" for size in sizes]))
    print("-" * (25 + 10 * len(sizes)))
    
    for op_name, op_func in operations:
        times = []
        for size in sizes:
            _, exec_time = time_operation(op_func, size)
            times.append(exec_time)
        
        time_str = "".join([f"{t:>9.3f}ms" for t in times])
        print(f"{op_name:>25} {time_str}")

def demonstrate_performance_tips():
    """Show practical performance optimization tips."""
    print("\\n=== Performance Optimization Tips ===")
    print()
    
    # Tip 1: List comprehensions vs loops
    print("1. List comprehensions vs explicit loops:")
    n = 10000
    
    def explicit_loop():
        result = []
        for i in range(n):
            if i % 2 == 0:
                result.append(i * 2)
        return result
    
    def list_comprehension():
        return [i * 2 for i in range(n) if i % 2 == 0]
    
    _, loop_time = time_operation(explicit_loop)
    _, comp_time = time_operation(list_comprehension)
    
    print(f"   Explicit loop: {loop_time:.3f}ms")
    print(f"   List comprehension: {comp_time:.3f}ms")
    print(f"   Improvement: {loop_time/comp_time:.1f}x faster")
    
    # Tip 2: String concatenation methods
    print("\\n2. String concatenation methods:")
    strings = [f"string_{i}" for i in range(1000)]
    
    def concat_with_plus():
        result = ""
        for s in strings:
            result += s
        return result
    
    def concat_with_join():
        return "".join(strings)
    
    _, plus_time = time_operation(concat_with_plus)
    _, join_time = time_operation(concat_with_join)
    
    print(f"   Using + operator: {plus_time:.3f}ms")
    print(f"   Using join(): {join_time:.3f}ms")
    print(f"   Improvement: {plus_time/join_time:.1f}x faster")
    
    # Tip 3: Using appropriate data structure
    print("\\n3. Set vs List for membership testing:")
    data = list(range(5000))
    data_set = set(data)
    search_items = [100, 1000, 2500, 4999]
    
    def search_in_list():
        return [item in data for item in search_items]
    
    def search_in_set():
        return [item in data_set for item in search_items]
    
    _, list_search_time = time_operation(search_in_list)
    _, set_search_time = time_operation(search_in_set)
    
    print(f"   Searching in list: {list_search_time:.3f}ms")
    print(f"   Searching in set: {set_search_time:.3f}ms")
    print(f"   Improvement: {list_search_time/set_search_time:.1f}x faster")

# Run all performance tests
if __name__ == "__main__":
    test_membership_performance()
    test_lookup_performance()
    test_insertion_performance()
    test_sorting_performance()
    analyze_memory_usage()
    demonstrate_big_o_scaling()
    demonstrate_performance_tips()
    
    print("\\n=== Summary ===")
    print("Key takeaways:")
    print("• Choose data structures based on most common operations")
    print("• Hash-based structures (dict, set) excel at lookups")
    print("• Lists are good for sequential access and appending")
    print("• Deques are optimal for operations at both ends")
    print("• Always profile with realistic data before optimizing")
''',
            "explanation": "Understanding time complexity and benchmarking helps choose the right data structure for optimal performance in real applications"
        }