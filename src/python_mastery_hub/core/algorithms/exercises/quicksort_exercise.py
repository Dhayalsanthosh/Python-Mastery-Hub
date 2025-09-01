"""
QuickSort Exercise - Comprehensive implementation with multiple strategies and analysis.
"""

import random
import time
from typing import List, Tuple, Callable
from ..base import AlgorithmDemo


class QuickSortExercise(AlgorithmDemo):
    """Comprehensive QuickSort exercise with multiple implementations and analysis."""
    
    def __init__(self):
        super().__init__("quicksort_exercise")
    
    def _setup_examples(self) -> None:
        """Setup QuickSort exercise examples."""
        self.examples = {
            "basic_quicksort": {
                "code": self._get_basic_quicksort_code(),
                "explanation": "Basic QuickSort implementation with Lomuto partition scheme",
                "time_complexity": "O(n log n) average, O(n²) worst case",
                "space_complexity": "O(log n) average, O(n) worst case"
            },
            "advanced_quicksort": {
                "code": self._get_advanced_quicksort_code(),
                "explanation": "Advanced QuickSort with multiple pivot strategies and optimizations",
                "time_complexity": "O(n log n) with optimizations",
                "space_complexity": "O(log n) with tail recursion"
            },
            "iterative_quicksort": {
                "code": self._get_iterative_quicksort_code(),
                "explanation": "Iterative QuickSort using explicit stack",
                "time_complexity": "O(n log n) average case",
                "space_complexity": "O(log n) for stack"
            }
        }
    
    def _get_basic_quicksort_code(self) -> str:
        return '''
def quicksort_basic(arr, low=0, high=None):
    """Basic QuickSort implementation with detailed logging."""
    if high is None:
        high = len(arr) - 1
        arr = arr.copy()
        print(f"Starting QuickSort on: {arr}")
    
    if low < high:
        # Partition the array and get pivot index
        pivot_index = partition_lomuto(arr, low, high)
        print(f"Pivot {arr[pivot_index]} at index {pivot_index}: {arr[low:high+1]}")
        
        # Recursively sort elements before and after partition
        quicksort_basic(arr, low, pivot_index - 1)
        quicksort_basic(arr, pivot_index + 1, high)
    
    if high == len(arr) - 1:  # Final call
        print(f"Final sorted array: {arr}")
        return arr
    
    return arr

def partition_lomuto(arr, low, high):
    """Lomuto partition scheme - pivot is rightmost element."""
    pivot = arr[high]
    i = low - 1  # Index of smaller element
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def partition_hoare(arr, low, high):
    """Hoare partition scheme - more efficient but complex."""
    pivot = arr[low]
    i = low - 1
    j = high + 1
    
    while True:
        # Find element on left that should be on right
        i += 1
        while arr[i] < pivot:
            i += 1
        
        # Find element on right that should be on left
        j -= 1
        while arr[j] > pivot:
            j -= 1
        
        # If pointers crossed, partitioning is done
        if i >= j:
            return j
        
        # Swap elements
        arr[i], arr[j] = arr[j], arr[i]

# Example usage
test_array = [10, 7, 8, 9, 1, 5]
sorted_array = quicksort_basic(test_array)
'''
    
    def _get_advanced_quicksort_code(self) -> str:
        return '''
def quicksort_advanced(arr, low=0, high=None, pivot_strategy='median_of_three', cutoff=10):
    """Advanced QuickSort with multiple optimizations."""
    if high is None:
        high = len(arr) - 1
        arr = arr.copy()
        print(f"Starting advanced QuickSort on: {arr}")
        print(f"Pivot strategy: {pivot_strategy}, cutoff: {cutoff}")
    
    # Use insertion sort for small subarrays
    if high - low + 1 <= cutoff:
        insertion_sort_range(arr, low, high)
        return arr
    
    if low < high:
        # Choose pivot based on strategy
        choose_pivot(arr, low, high, pivot_strategy)
        
        # Partition and recursively sort
        pivot_index = partition_lomuto(arr, low, high)
        
        # Tail recursion optimization - sort smaller partition first
        if pivot_index - low < high - pivot_index:
            quicksort_advanced(arr, low, pivot_index - 1, pivot_strategy, cutoff)
            quicksort_advanced(arr, pivot_index + 1, high, pivot_strategy, cutoff)
        else:
            quicksort_advanced(arr, pivot_index + 1, high, pivot_strategy, cutoff)
            quicksort_advanced(arr, low, pivot_index - 1, pivot_strategy, cutoff)
    
    if high == len(arr) - 1:
        print(f"Final sorted array: {arr}")
        return arr
    
    return arr

def choose_pivot(arr, low, high, strategy):
    """Choose pivot based on strategy and move to end."""
    if strategy == 'first':
        arr[low], arr[high] = arr[high], arr[low]
    elif strategy == 'random':
        random_idx = random.randint(low, high)
        arr[random_idx], arr[high] = arr[high], arr[random_idx]
    elif strategy == 'median_of_three':
        median_of_three(arr, low, high)
    elif strategy == 'median_of_medians':
        median_idx = median_of_medians(arr, low, high)
        arr[median_idx], arr[high] = arr[high], arr[median_idx]
    # 'last' strategy requires no change

def median_of_three(arr, low, high):
    """Select median of first, middle, last as pivot."""
    mid = (low + high) // 2
    
    # Sort the three elements
    if arr[mid] < arr[low]:
        arr[low], arr[mid] = arr[mid], arr[low]
    if arr[high] < arr[low]:
        arr[low], arr[high] = arr[high], arr[low]
    if arr[high] < arr[mid]:
        arr[mid], arr[high] = arr[high], arr[mid]
    
    # Move median to end
    arr[mid], arr[high] = arr[high], arr[mid]

def median_of_medians(arr, low, high):
    """Median of medians for guaranteed O(n log n) worst case."""
    n = high - low + 1
    if n <= 5:
        return low + n // 2
    
    # Divide into groups of 5 and find medians
    medians = []
    for i in range(low, high + 1, 5):
        group_high = min(i + 4, high)
        insertion_sort_range(arr, i, group_high)
        medians.append(arr[i + (group_high - i) // 2])
    
    # Recursively find median of medians
    return median_of_medians(medians, 0, len(medians) - 1)

def insertion_sort_range(arr, low, high):
    """Insertion sort for small ranges."""
    for i in range(low + 1, high + 1):
        key = arr[i]
        j = i - 1
        while j >= low and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

# Example usage with different strategies
test_arrays = [
    [64, 34, 25, 12, 22, 11, 90],
    [5, 5, 5, 5, 5],  # All same elements
    [9, 8, 7, 6, 5, 4, 3, 2, 1],  # Reverse sorted
    list(range(100))  # Already sorted
]

strategies = ['last', 'first', 'random', 'median_of_three']

for i, test_array in enumerate(test_arrays[:2]):  # Test first two arrays
    print(f"\\n=== Test Array {i+1}: {test_array} ===")
    for strategy in strategies[:2]:  # Test first two strategies
        print(f"\\nTesting strategy: {strategy}")
        result = quicksort_advanced(test_array.copy(), pivot_strategy=strategy)
'''
    
    def _get_iterative_quicksort_code(self) -> str:
        return '''
def quicksort_iterative(arr):
    """Iterative QuickSort using explicit stack."""
    if len(arr) <= 1:
        return arr.copy()
    
    arr = arr.copy()
    stack = [(0, len(arr) - 1)]
    
    print(f"Starting iterative QuickSort on: {arr}")
    print("Stack operations:")
    
    while stack:
        low, high = stack.pop()
        print(f"  Processing range [{low}:{high}] = {arr[low:high+1]}")
        
        if low < high:
            # Partition the array
            pivot_index = partition_lomuto(arr, low, high)
            print(f"    Pivot {arr[pivot_index]} at index {pivot_index}")
            
            # Push subproblems onto stack
            # Push larger subproblem first for better space complexity
            if pivot_index - low > high - pivot_index:
                stack.append((low, pivot_index - 1))
                stack.append((pivot_index + 1, high))
                print(f"    Pushed [{low}:{pivot_index-1}] and [{pivot_index+1}:{high}]")
            else:
                stack.append((pivot_index + 1, high))
                stack.append((low, pivot_index - 1))
                print(f"    Pushed [{pivot_index+1}:{high}] and [{low}:{pivot_index-1}]")
    
    print(f"Final sorted array: {arr}")
    return arr

def quicksort_three_way(arr, low=0, high=None):
    """Three-way QuickSort for arrays with many duplicates."""
    if high is None:
        high = len(arr) - 1
        arr = arr.copy()
        print(f"Starting three-way QuickSort on: {arr}")
    
    if low >= high:
        return arr
    
    # Three-way partitioning
    lt, gt = three_way_partition(arr, low, high)
    
    print(f"Three-way partition: lt={lt}, gt={gt}, equal elements: {arr[lt:gt+1]}")
    
    # Recursively sort elements less than and greater than pivot
    quicksort_three_way(arr, low, lt - 1)
    quicksort_three_way(arr, gt + 1, high)
    
    if high == len(arr) - 1:
        print(f"Final sorted array: {arr}")
        return arr
    
    return arr

def three_way_partition(arr, low, high):
    """Three-way partitioning for duplicate elements."""
    pivot = arr[low]
    lt = low      # arr[low..lt-1] < pivot
    i = low + 1   # arr[lt..i-1] == pivot
    gt = high     # arr[gt+1..high] > pivot
    
    while i <= gt:
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
        else:
            i += 1
    
    return lt, gt

# Example usage
test_array = [64, 34, 25, 12, 22, 11, 90, 22, 11, 90]
print("=== Iterative QuickSort ===")
iterative_result = quicksort_iterative(test_array)

print("\\n=== Three-way QuickSort ===")
three_way_result = quicksort_three_way(test_array)
'''
    
    def demonstrate_quicksort_analysis(self):
        """Comprehensive analysis of QuickSort performance."""
        print("=== QuickSort Performance Analysis ===")
        
        def quicksort_with_stats(arr, strategy='median_of_three'):
            """QuickSort with performance statistics."""
            stats = {'comparisons': 0, 'swaps': 0, 'recursive_calls': 0}
            
            def quicksort_helper(arr, low, high):
                stats['recursive_calls'] += 1
                
                if low < high:
                    pivot_index = partition_with_stats(arr, low, high, stats)
                    quicksort_helper(arr, low, pivot_index - 1)
                    quicksort_helper(arr, pivot_index + 1, high)
            
            def partition_with_stats(arr, low, high, stats):
                pivot = arr[high]
                i = low - 1
                
                for j in range(low, high):
                    stats['comparisons'] += 1
                    if arr[j] <= pivot:
                        i += 1
                        if i != j:
                            arr[i], arr[j] = arr[j], arr[i]
                            stats['swaps'] += 1
                
                arr[i + 1], arr[high] = arr[high], arr[i + 1]
                stats['swaps'] += 1
                return i + 1
            
            arr_copy = arr.copy()
            start_time = time.time()
            quicksort_helper(arr_copy, 0, len(arr_copy) - 1)
            end_time = time.time()
            
            stats['time'] = (end_time - start_time) * 1000
            stats['sorted_array'] = arr_copy
            return stats
        
        # Test different input patterns
        test_cases = [
            ('Random', [random.randint(1, 100) for _ in range(20)]),
            ('Sorted', list(range(20))),
            ('Reverse', list(range(20, 0, -1))),
            ('Many Duplicates', [5, 3, 8, 3, 5, 8, 3, 5] * 3),
            ('Nearly Sorted', list(range(18)) + [19, 17])
        ]
        
        for case_name, test_data in test_cases:
            print(f"\n{case_name} Data: {test_data[:10]}{'...' if len(test_data) > 10 else ''}")
            stats = quicksort_with_stats(test_data)
            
            print(f"  Comparisons: {stats['comparisons']}")
            print(f"  Swaps: {stats['swaps']}")
            print(f"  Recursive calls: {stats['recursive_calls']}")
            print(f"  Time: {stats['time']:.3f}ms")
            print(f"  Correctly sorted: {stats['sorted_array'] == sorted(test_data)}")
    
    def get_exercise_tasks(self) -> List[str]:
        """Get list of exercise tasks for students."""
        return [
            "Implement basic QuickSort with Lomuto partition scheme",
            "Add Hoare partition scheme and compare performance",
            "Implement median-of-three pivot selection",
            "Add iterative version using explicit stack",
            "Implement three-way partitioning for duplicate elements",
            "Add performance analysis and statistics collection",
            "Compare with other sorting algorithms",
            "Handle edge cases (empty arrays, single elements, duplicates)",
            "Optimize for small subarrays using insertion sort",
            "Implement worst-case O(n log n) guarantee using median-of-medians"
        ]
    
    def get_starter_code(self) -> str:
        """Get starter code template for students."""
        return '''
def quicksort(arr, low=0, high=None):
    """
    Implement QuickSort algorithm.
    
    Args:
        arr: List to sort
        low: Starting index
        high: Ending index
    
    Returns:
        Sorted list
    """
    # TODO: Implement QuickSort logic here
    pass

def partition(arr, low, high):
    """
    Partition array around pivot element.
    
    Args:
        arr: Array to partition
        low: Starting index
        high: Ending index
    
    Returns:
        Index of pivot after partitioning
    """
    # TODO: Implement partitioning logic here
    pass

def choose_pivot(arr, low, high, strategy='last'):
    """
    Choose pivot element based on strategy.
    
    Args:
        arr: Array
        low: Starting index
        high: Ending index
        strategy: Pivot selection strategy
    """
    # TODO: Implement pivot selection strategies
    pass

# Test your implementation
if __name__ == "__main__":
    test_arrays = [
        [64, 34, 25, 12, 22, 11, 90],
        [1],
        [],
        [5, 5, 5, 5],
        [3, 1, 4, 1, 5, 9, 2, 6]
    ]
    
    for i, test_array in enumerate(test_arrays):
        print(f"Test {i+1}: {test_array}")
        result = quicksort(test_array.copy())
        print(f"Sorted: {result}")
        print(f"Correct: {result == sorted(test_array)}")
        print()
'''
    
    def validate_solution(self, student_quicksort_func) -> Tuple[bool, List[str]]:
        """Validate student's QuickSort implementation."""
        test_cases = [
            [],
            [1],
            [2, 1],
            [3, 1, 4, 1, 5, 9, 2, 6],
            [1, 1, 1, 1],
            list(range(10)),
            list(range(10, 0, -1)),
            [random.randint(1, 100) for _ in range(50)]
        ]
        
        feedback = []
        all_passed = True
        
        for i, test_case in enumerate(test_cases):
            try:
                result = student_quicksort_func(test_case.copy())
                expected = sorted(test_case)
                
                if result == expected:
                    feedback.append(f"✓ Test case {i+1} passed")
                else:
                    feedback.append(f"✗ Test case {i+1} failed: expected {expected}, got {result}")
                    all_passed = False
                    
            except Exception as e:
                feedback.append(f"✗ Test case {i+1} raised exception: {str(e)}")
                all_passed = False
        
        return all_passed, feedback