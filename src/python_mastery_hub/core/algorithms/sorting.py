"""
Sorting algorithms demonstrations for the Algorithms module.
"""

import time
import random
from typing import Dict, List, Any
from .base import AlgorithmDemo


class SortingAlgorithms(AlgorithmDemo):
    """Demonstration class for sorting algorithms."""
    
    def __init__(self):
        super().__init__("sorting_algorithms")
    
    def _setup_examples(self) -> None:
        """Setup sorting algorithm examples."""
        self.examples = {
            "bubble_sort": {
                "code": '''
def bubble_sort(arr):
    """Simple bubble sort with step-by-step visualization."""
    n = len(arr)
    arr = arr.copy()  # Don't modify original
    comparisons = 0
    swaps = 0
    
    print(f"Starting array: {arr}")
    
    for i in range(n):
        swapped = False
        
        for j in range(0, n - i - 1):
            comparisons += 1
            
            if arr[j] > arr[j + 1]:
                # Swap elements
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
                print(f"  Swapped {arr[j+1]} and {arr[j]}: {arr}")
        
        if not swapped:
            print(f"  No swaps in pass {i+1}, array is sorted!")
            break
        
        print(f"Pass {i+1} complete: {arr}")
    
    print(f"\\nFinal sorted array: {arr}")
    print(f"Total comparisons: {comparisons}")
    print(f"Total swaps: {swaps}")
    return arr

# Example usage
test_array = [64, 34, 25, 12, 22, 11, 90]
sorted_array = bubble_sort(test_array)
''',
                "explanation": "Bubble sort repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order",
                "time_complexity": "O(n²)",
                "space_complexity": "O(1)",
                "stable": True
            },
            
            "merge_sort": {
                "code": '''
def merge_sort(arr):
    """Efficient merge sort with divide-and-conquer approach."""
    if len(arr) <= 1:
        return arr
    
    # Divide
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]
    
    print(f"Dividing {arr} into {left_half} and {right_half}")
    
    # Conquer (recursive calls)
    left_sorted = merge_sort(left_half)
    right_sorted = merge_sort(right_half)
    
    # Merge
    merged = merge(left_sorted, right_sorted)
    print(f"Merging {left_sorted} and {right_sorted} → {merged}")
    
    return merged

def merge(left, right):
    """Merge two sorted arrays into one sorted array."""
    result = []
    i = j = 0
    
    # Compare elements from both arrays
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result

def merge_sort_analysis():
    """Analyze merge sort performance."""
    import time
    import random
    
    sizes = [100, 1000, 5000]
    
    print("=== Merge Sort Performance Analysis ===")
    for size in sizes:
        # Generate random data
        data = [random.randint(1, 1000) for _ in range(size)]
        
        # Time the sorting
        start_time = time.time()
        sorted_data = merge_sort(data.copy())
        end_time = time.time()
        
        # Verify it's sorted
        is_sorted = sorted_data == sorted(data)
        
        print(f"Size {size:5d}: {(end_time - start_time)*1000:6.2f}ms, Correct: {is_sorted}")

# Example usage
test_array = [38, 27, 43, 3, 9, 82, 10]
print("=== Merge Sort Example ===")
sorted_array = merge_sort(test_array)
print(f"\\nOriginal: {test_array}")
print(f"Sorted:   {sorted_array}")

print("\\n")
merge_sort_analysis()
''',
                "explanation": "Merge sort uses divide-and-conquer strategy, consistently performing in O(n log n) time",
                "time_complexity": "O(n log n)",
                "space_complexity": "O(n)",
                "stable": True
            },
            
            "quick_sort": {
                "code": '''
def quicksort(arr, low=0, high=None):
    """Efficient quicksort implementation with partitioning."""
    if high is None:
        high = len(arr) - 1
        arr = arr.copy()  # Don't modify original
        print(f"Starting quicksort on: {arr}")
    
    if low < high:
        # Partition the array and get pivot index
        pivot_index = partition(arr, low, high)
        print(f"Pivot {arr[pivot_index]} at index {pivot_index}: {arr[low:high+1]}")
        
        # Recursively sort elements before and after partition
        quicksort(arr, low, pivot_index - 1)
        quicksort(arr, pivot_index + 1, high)
    
    if high == len(arr) - 1:  # Final call
        print(f"Final sorted array: {arr}")
        return arr
    
    return arr

def partition(arr, low, high):
    """Partition array around pivot element."""
    # Choose rightmost element as pivot
    pivot = arr[high]
    
    # Index of smaller element (indicates right position of pivot)
    i = low - 1
    
    for j in range(low, high):
        # If current element is smaller than or equal to pivot
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    # Place pivot in correct position
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def quicksort_with_different_pivots():
    """Compare quicksort with different pivot selection strategies."""
    import random
    
    def quicksort_random_pivot(arr, low=0, high=None):
        """Quicksort with random pivot selection."""
        if high is None:
            high = len(arr) - 1
            arr = arr.copy()
        
        if low < high:
            # Random pivot selection
            random_index = random.randint(low, high)
            arr[random_index], arr[high] = arr[high], arr[random_index]
            
            pivot_index = partition(arr, low, high)
            quicksort_random_pivot(arr, low, pivot_index - 1)
            quicksort_random_pivot(arr, pivot_index + 1, high)
        
        return arr
    
    test_cases = [
        [3, 1, 4, 1, 5, 9, 2, 6],           # Random
        [1, 2, 3, 4, 5, 6, 7, 8],           # Already sorted (worst case)
        [8, 7, 6, 5, 4, 3, 2, 1],           # Reverse sorted
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n=== Test Case {i}: {test_case} ===")
        
        # Regular quicksort
        result1 = quicksort(test_case.copy())
        
        # Random pivot quicksort  
        result2 = quicksort_random_pivot(test_case.copy())
        
        print(f"Both methods produce same result: {result1 == result2}")

# Example usage
test_array = [10, 7, 8, 9, 1, 5]
sorted_array = quicksort(test_array)

quicksort_with_different_pivots()
''',
                "explanation": "Quicksort partitions array around a pivot, with average O(n log n) performance",
                "time_complexity": "O(n log n) average, O(n²) worst case",
                "space_complexity": "O(log n)",
                "stable": False
            },
            
            "heap_sort": {
                "code": '''
def heap_sort(arr):
    """Heap sort implementation using max heap."""
    arr = arr.copy()
    n = len(arr)
    
    print(f"Starting heap sort on: {arr}")
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    
    print(f"Max heap created: {arr}")
    
    # Extract elements from heap one by one
    for i in range(n - 1, 0, -1):
        # Move current root (maximum) to end
        arr[0], arr[i] = arr[i], arr[0]
        print(f"Extracted {arr[i]}, remaining heap: {arr[:i]}")
        
        # Call heapify on the reduced heap
        heapify(arr, i, 0)
    
    print(f"Final sorted array: {arr}")
    return arr

def heapify(arr, n, i):
    """Heapify a subtree rooted at index i."""
    largest = i  # Initialize largest as root
    left = 2 * i + 1  # Left child
    right = 2 * i + 2  # Right child
    
    # Check if left child exists and is greater than root
    if left < n and arr[left] > arr[largest]:
        largest = left
    
    # Check if right child exists and is greater than current largest
    if right < n and arr[right] > arr[largest]:
        largest = right
    
    # If largest is not root, swap and continue heapifying
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

# Example usage
test_array = [12, 11, 13, 5, 6, 7]
sorted_array = heap_sort(test_array)
''',
                "explanation": "Heap sort builds a max heap then repeatedly extracts the maximum element",
                "time_complexity": "O(n log n)",
                "space_complexity": "O(1)",
                "stable": False
            },
            
            "insertion_sort": {
                "code": '''
def insertion_sort(arr):
    """Insertion sort with step-by-step visualization."""
    arr = arr.copy()
    n = len(arr)
    
    print(f"Starting insertion sort on: {arr}")
    
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        
        print(f"\\nInserting {key} into sorted portion {arr[:i]}")
        
        # Move elements greater than key one position ahead
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
            print(f"  Moved {arr[j + 2]} right: {arr}")
        
        # Place key in correct position
        arr[j + 1] = key
        print(f"  Inserted {key} at position {j + 1}: {arr}")
    
    print(f"\\nFinal sorted array: {arr}")
    return arr

# Example usage
test_array = [64, 34, 25, 12, 22, 11, 90]
sorted_array = insertion_sort(test_array)
''',
                "explanation": "Insertion sort builds the sorted array one element at a time by inserting each element in its correct position",
                "time_complexity": "O(n²)",
                "space_complexity": "O(1)",
                "stable": True
            },
            
            "selection_sort": {
                "code": '''
def selection_sort(arr):
    """Selection sort with step-by-step visualization."""
    arr = arr.copy()
    n = len(arr)
    
    print(f"Starting selection sort on: {arr}")
    
    for i in range(n):
        # Find minimum element in remaining unsorted array
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        
        # Swap found minimum element with first element
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            print(f"Pass {i + 1}: Swapped {arr[min_idx]} and {arr[i]} → {arr}")
        else:
            print(f"Pass {i + 1}: {arr[i]} already in correct position → {arr}")
    
    print(f"\\nFinal sorted array: {arr}")
    return arr

# Example usage
test_array = [64, 34, 25, 12, 22, 11, 90]
sorted_array = selection_sort(test_array)
''',
                "explanation": "Selection sort repeatedly finds the minimum element and places it at the beginning",
                "time_complexity": "O(n²)",
                "space_complexity": "O(1)",
                "stable": False
            }
        }
    
    def _setup_exercises(self) -> None:
        """Setup sorting exercises."""
        from .exercises.quicksort_exercise import QuickSortExercise
        
        quicksort_exercise = QuickSortExercise()
        
        self.exercises = [
            {
                "topic": "sorting_algorithms",
                "title": "Implement Quick Sort",
                "description": "Build an efficient quicksort implementation with analysis",
                "difficulty": "medium",
                "exercise": quicksort_exercise
            }
        ]
    
    def get_explanation(self) -> str:
        """Get detailed explanation for sorting algorithms."""
        return ("Sorting algorithms arrange elements in a specific order, each with different "
                "time/space complexity trade-offs and stability characteristics.")
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for sorting algorithms."""
        return [
            "Choose the right algorithm based on data characteristics",
            "Consider stability requirements for sorting",
            "Use built-in sort functions for most practical applications",
            "Understand time and space complexity trade-offs",
            "Consider external sorting for very large datasets",
            "Test with different data patterns (sorted, reverse, random)",
            "Implement hybrid algorithms for better performance"
        ]
    
    def compare_algorithms(self, data_sizes: List[int] = None) -> Dict[str, Any]:
        """Compare performance of different sorting algorithms."""
        if data_sizes is None:
            data_sizes = [100, 500, 1000]
        
        algorithms = {
            'bubble_sort': self._bubble_sort_simple,
            'insertion_sort': self._insertion_sort_simple,
            'selection_sort': self._selection_sort_simple,
            'merge_sort': self._merge_sort_simple,
            'quick_sort': self._quick_sort_simple,
            'heap_sort': self._heap_sort_simple
        }
        
        results = {}
        
        for size in data_sizes:
            # Generate random test data
            test_data = [random.randint(1, 1000) for _ in range(size)]
            results[size] = {}
            
            for name, algorithm in algorithms.items():
                start_time = time.time()
                sorted_data = algorithm(test_data.copy())
                end_time = time.time()
                
                # Verify correctness
                is_correct = sorted_data == sorted(test_data)
                
                results[size][name] = {
                    'time_ms': (end_time - start_time) * 1000,
                    'correct': is_correct
                }
        
        return results
    
    def _bubble_sort_simple(self, arr):
        """Simple bubble sort without visualization."""
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr
    
    def _insertion_sort_simple(self, arr):
        """Simple insertion sort without visualization."""
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        return arr
    
    def _selection_sort_simple(self, arr):
        """Simple selection sort without visualization."""
        n = len(arr)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if arr[j] < arr[min_idx]:
                    min_idx = j
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
        return arr
    
    def _merge_sort_simple(self, arr):
        """Simple merge sort without visualization."""
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = self._merge_sort_simple(arr[:mid])
        right = self._merge_sort_simple(arr[mid:])
        
        return self._merge_simple(left, right)
    
    def _merge_simple(self, left, right):
        """Simple merge function."""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    def _quick_sort_simple(self, arr):
        """Simple quicksort without visualization."""
        if len(arr) <= 1:
            return arr
        
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        
        return self._quick_sort_simple(left) + middle + self._quick_sort_simple(right)
    
    def _heap_sort_simple(self, arr):
        """Simple heap sort without visualization."""
        def heapify(arr, n, i):
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2
            
            if left < n and arr[left] > arr[largest]:
                largest = left
            if right < n and arr[right] > arr[largest]:
                largest = right
            
            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]
                heapify(arr, n, largest)
        
        n = len(arr)
        
        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            heapify(arr, n, i)
        
        # Extract elements
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            heapify(arr, i, 0)
        
        return arr