"""
Searching algorithms demonstrations for the Algorithms module.
"""

import time
import random
from typing import Dict, List, Any, Optional
from .base import AlgorithmDemo


class SearchingAlgorithms(AlgorithmDemo):
    """Demonstration class for searching algorithms."""
    
    def __init__(self):
        super().__init__("searching_algorithms")
    
    def _setup_examples(self) -> None:
        """Setup searching algorithm examples."""
        self.examples = {
            "linear_search": {
                "code": '''
def linear_search(arr, target):
    """Linear search through array element by element."""
    comparisons = 0
    
    print(f"Searching for {target} in {arr}")
    
    for i, element in enumerate(arr):
        comparisons += 1
        print(f"  Step {comparisons}: Checking index {i}, value {element}")
        
        if element == target:
            print(f"  ✓ Found {target} at index {i}")
            print(f"  Total comparisons: {comparisons}")
            return i
    
    print(f"  ✗ {target} not found in array")
    print(f"  Total comparisons: {comparisons}")
    return -1

def linear_search_all_occurrences(arr, target):
    """Find all occurrences of target in array."""
    indices = []
    
    for i, element in enumerate(arr):
        if element == target:
            indices.append(i)
    
    return indices

# Example usage
test_array = [64, 34, 25, 12, 22, 11, 90, 22]

print("=== Linear Search Examples ===")
linear_search(test_array, 22)
print()
linear_search(test_array, 99)

print("\\n=== Find All Occurrences ===")
all_22s = linear_search_all_occurrences(test_array, 22)
print(f"All occurrences of 22: {all_22s}")
''',
                "explanation": "Linear search checks each element sequentially, with O(n) time complexity",
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "prerequisites": "None - works on unsorted arrays"
            },
            
            "binary_search": {
                "code": '''
def binary_search(arr, target):
    """Binary search on sorted array."""
    left, right = 0, len(arr) - 1
    comparisons = 0
    
    print(f"Binary search for {target} in {arr}")
    
    while left <= right:
        comparisons += 1
        mid = (left + right) // 2
        mid_value = arr[mid]
        
        print(f"  Step {comparisons}: Range [{left}:{right}], mid={mid}, value={mid_value}")
        
        if mid_value == target:
            print(f"  ✓ Found {target} at index {mid}")
            print(f"  Total comparisons: {comparisons}")
            return mid
        elif mid_value < target:
            print(f"    {mid_value} < {target}, search right half")
            left = mid + 1
        else:
            print(f"    {mid_value} > {target}, search left half")
            right = mid - 1
    
    print(f"  ✗ {target} not found")
    print(f"  Total comparisons: {comparisons}")
    return -1

def binary_search_recursive(arr, target, left=0, right=None, depth=0):
    """Recursive implementation of binary search."""
    if right is None:
        right = len(arr) - 1
    
    indent = "  " * depth
    print(f"{indent}Searching range [{left}:{right}]")
    
    if left > right:
        print(f"{indent}✗ Target {target} not found")
        return -1
    
    mid = (left + right) // 2
    mid_value = arr[mid]
    
    print(f"{indent}Mid index {mid}, value {mid_value}")
    
    if mid_value == target:
        print(f"{indent}✓ Found {target} at index {mid}")
        return mid
    elif mid_value < target:
        print(f"{indent}{mid_value} < {target}, search right")
        return binary_search_recursive(arr, target, mid + 1, right, depth + 1)
    else:
        print(f"{indent}{mid_value} > {target}, search left")
        return binary_search_recursive(arr, target, left, mid - 1, depth + 1)

# Example usage
sorted_array = [11, 12, 22, 25, 34, 64, 90]

print("=== Binary Search Example ===")
binary_search(sorted_array, 25)
print()
binary_search(sorted_array, 99)

print("\\n=== Recursive Binary Search ===")
binary_search_recursive(sorted_array, 25)
''',
                "explanation": "Binary search efficiently finds elements in sorted arrays with O(log n) time complexity",
                "time_complexity": "O(log n)",
                "space_complexity": "O(1) iterative, O(log n) recursive",
                "prerequisites": "Array must be sorted"
            },
            
            "interpolation_search": {
                "code": '''
def interpolation_search(arr, target):
    """Interpolation search for uniformly distributed sorted arrays."""
    left, right = 0, len(arr) - 1
    comparisons = 0
    
    print(f"Interpolation search for {target} in {arr}")
    
    while left <= right and target >= arr[left] and target <= arr[right]:
        comparisons += 1
        
        # If array has only one element
        if left == right:
            if arr[left] == target:
                print(f"  ✓ Found {target} at index {left}")
                return left
            else:
                print(f"  ✗ {target} not found")
                return -1
        
        # Calculate probe position using interpolation formula
        pos = left + ((target - arr[left]) * (right - left)) // (arr[right] - arr[left])
        
        # Ensure pos is within bounds
        pos = max(left, min(pos, right))
        
        print(f"  Step {comparisons}: Range [{left}:{right}], probe={pos}, value={arr[pos]}")
        
        if arr[pos] == target:
            print(f"  ✓ Found {target} at index {pos}")
            print(f"  Total comparisons: {comparisons}")
            return pos
        elif arr[pos] < target:
            print(f"    {arr[pos]} < {target}, search right half")
            left = pos + 1
        else:
            print(f"    {arr[pos]} > {target}, search left half")
            right = pos - 1
    
    print(f"  ✗ {target} not found")
    print(f"  Total comparisons: {comparisons}")
    return -1

# Example usage with uniformly distributed data
uniform_array = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
print("=== Interpolation Search Example ===")
interpolation_search(uniform_array, 70)
''',
                "explanation": "Interpolation search estimates target position based on value distribution, more efficient than binary search for uniformly distributed data",
                "time_complexity": "O(log log n) average, O(n) worst case",
                "space_complexity": "O(1)",
                "prerequisites": "Sorted array with uniform distribution"
            },
            
            "exponential_search": {
                "code": '''
def exponential_search(arr, target):
    """Exponential search for unbounded/large sorted arrays."""
    n = len(arr)
    
    print(f"Exponential search for {target}")
    
    # If target is at first position
    if arr[0] == target:
        print(f"  ✓ Found {target} at index 0")
        return 0
    
    # Find range for binary search by repeatedly doubling
    bound = 1
    while bound < n and arr[bound] < target:
        print(f"  Checking bound {bound}, value {arr[bound]}")
        bound *= 2
    
    # Perform binary search in found range
    left = bound // 2
    right = min(bound, n - 1)
    
    print(f"  Binary search in range [{left}:{right}]")
    
    return binary_search_range(arr, target, left, right)

def binary_search_range(arr, target, left, right):
    """Binary search within a specific range."""
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            print(f"    ✓ Found {target} at index {mid}")
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    print(f"    ✗ {target} not found in range")
    return -1

# Example usage
large_array = list(range(1, 101, 2))  # [1, 3, 5, 7, ..., 99]
print("=== Exponential Search Example ===")
exponential_search(large_array, 47)
''',
                "explanation": "Exponential search finds range for target then applies binary search, useful for unbounded arrays",
                "time_complexity": "O(log n)",
                "space_complexity": "O(1)",
                "prerequisites": "Sorted array"
            },
            
            "ternary_search": {
                "code": '''
def ternary_search(arr, target):
    """Ternary search divides array into three parts."""
    left, right = 0, len(arr) - 1
    comparisons = 0
    
    print(f"Ternary search for {target} in {arr}")
    
    while left <= right:
        comparisons += 1
        
        # Divide array into three parts
        mid1 = left + (right - left) // 3
        mid2 = right - (right - left) // 3
        
        print(f"  Step {comparisons}: Range [{left}:{right}], mid1={mid1}({arr[mid1]}), mid2={mid2}({arr[mid2]})")
        
        if arr[mid1] == target:
            print(f"  ✓ Found {target} at index {mid1}")
            print(f"  Total comparisons: {comparisons}")
            return mid1
        elif arr[mid2] == target:
            print(f"  ✓ Found {target} at index {mid2}")
            print(f"  Total comparisons: {comparisons}")
            return mid2
        elif target < arr[mid1]:
            print(f"    {target} < {arr[mid1]}, search left third")
            right = mid1 - 1
        elif target > arr[mid2]:
            print(f"    {target} > {arr[mid2]}, search right third")
            left = mid2 + 1
        else:
            print(f"    {arr[mid1]} < {target} < {arr[mid2]}, search middle third")
            left = mid1 + 1
            right = mid2 - 1
    
    print(f"  ✗ {target} not found")
    print(f"  Total comparisons: {comparisons}")
    return -1

# Example usage
sorted_array = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
print("=== Ternary Search Example ===")
ternary_search(sorted_array, 15)
''',
                "explanation": "Ternary search divides the search space into three parts instead of two",
                "time_complexity": "O(log₃ n)",
                "space_complexity": "O(1)",
                "prerequisites": "Sorted array"
            }
        }
    
    def _setup_exercises(self) -> None:
        """Setup searching exercises."""
        # Searching algorithms are generally straightforward, 
        # so we focus on comparative analysis exercises
        self.exercises = [
            {
                "topic": "searching_algorithms",
                "title": "Search Algorithm Comparison",
                "description": "Compare different search algorithms on various data types",
                "difficulty": "medium",
                "exercise": None  # Implementation included in examples
            }
        ]
    
    def get_explanation(self) -> str:
        """Get detailed explanation for searching algorithms."""
        return ("Searching algorithms find elements in data structures, with efficiency "
                "depending on data organization and algorithm choice.")
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for searching algorithms."""
        return [
            "Use binary search only on sorted data",
            "Consider hash tables for O(1) average-case lookups",
            "Implement proper bounds checking",
            "Handle edge cases like empty arrays",
            "Choose appropriate search algorithm based on data structure",
            "For repeated searches, consider preprocessing data",
            "Use interpolation search for uniformly distributed data"
        ]
    
    def compare_search_performance(self, data_sizes: List[int] = None) -> Dict[str, Any]:
        """Compare performance of different search algorithms."""
        if data_sizes is None:
            data_sizes = [1000, 10000, 100000]
        
        results = {}
        
        for size in data_sizes:
            # Generate sorted test data
            sorted_data = list(range(0, size * 2, 2))  # Even numbers
            target = random.choice(sorted_data)
            
            results[size] = {}
            
            # Linear search
            start_time = time.time()
            linear_result = self._linear_search_simple(sorted_data, target)
            linear_time = (time.time() - start_time) * 1000
            
            # Binary search
            start_time = time.time()
            binary_result = self._binary_search_simple(sorted_data, target)
            binary_time = (time.time() - start_time) * 1000
            
            # Interpolation search (for uniform data)
            start_time = time.time()
            interp_result = self._interpolation_search_simple(sorted_data, target)
            interp_time = (time.time() - start_time) * 1000
            
            results[size] = {
                'linear': {'time_ms': linear_time, 'result': linear_result},
                'binary': {'time_ms': binary_time, 'result': binary_result},
                'interpolation': {'time_ms': interp_time, 'result': interp_result},
                'target': target
            }
        
        return results
    
    def _linear_search_simple(self, arr, target):
        """Simple linear search without visualization."""
        for i, element in enumerate(arr):
            if element == target:
                return i
        return -1
    
    def _binary_search_simple(self, arr, target):
        """Simple binary search without visualization."""
        left, right = 0, len(arr) - 1
        
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return -1
    
    def _interpolation_search_simple(self, arr, target):
        """Simple interpolation search without visualization."""
        left, right = 0, len(arr) - 1
        
        while left <= right and target >= arr[left] and target <= arr[right]:
            if left == right:
                return left if arr[left] == target else -1
            
            # Interpolation formula
            pos = left + ((target - arr[left]) * (right - left)) // (arr[right] - arr[left])
            pos = max(left, min(pos, right))
            
            if arr[pos] == target:
                return pos
            elif arr[pos] < target:
                left = pos + 1
            else:
                right = pos - 1
        
        return -1
    
    def search_variations(self) -> Dict[str, Any]:
        """Demonstrate various search algorithm variations."""
        return {
            "find_first_occurrence": self._find_first_occurrence_example(),
            "find_last_occurrence": self._find_last_occurrence_example(),
            "find_insertion_point": self._find_insertion_point_example(),
            "search_in_rotated_array": self._search_rotated_array_example()
        }
    
    def _find_first_occurrence_example(self) -> Dict[str, str]:
        """Example of finding first occurrence in sorted array with duplicates."""
        return {
            "code": '''
def find_first_occurrence(arr, target):
    """Find first occurrence of target in sorted array with duplicates."""
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            result = mid
            right = mid - 1  # Continue searching left
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result

# Example: [1, 2, 2, 2, 3, 4, 5]
arr = [1, 2, 2, 2, 3, 4, 5]
first_2 = find_first_occurrence(arr, 2)  # Returns index 1
''',
            "explanation": "Modified binary search to find the leftmost occurrence of a target value"
        }
    
    def _find_last_occurrence_example(self) -> Dict[str, str]:
        """Example of finding last occurrence in sorted array with duplicates."""
        return {
            "code": '''
def find_last_occurrence(arr, target):
    """Find last occurrence of target in sorted array with duplicates."""
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            result = mid
            left = mid + 1  # Continue searching right
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result

# Example: [1, 2, 2, 2, 3, 4, 5]
arr = [1, 2, 2, 2, 3, 4, 5]
last_2 = find_last_occurrence(arr, 2)  # Returns index 3
''',
            "explanation": "Modified binary search to find the rightmost occurrence of a target value"
        }
    
    def _find_insertion_point_example(self) -> Dict[str, str]:
        """Example of finding insertion point for maintaining sorted order."""
        return {
            "code": '''
def find_insertion_point(arr, target):
    """Find index where target should be inserted to maintain sorted order."""
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    
    return left

# Example: [1, 3, 5, 7, 9]
arr = [1, 3, 5, 7, 9]
insert_pos = find_insertion_point(arr, 6)  # Returns index 3
''',
            "explanation": "Binary search variation to find correct insertion position"
        }
    
    def _search_rotated_array_example(self) -> Dict[str, str]:
        """Example of searching in rotated sorted array."""
        return {
            "code": '''
def search_rotated_array(arr, target):
    """Search in rotated sorted array."""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        
        # Check which half is sorted
        if arr[left] <= arr[mid]:  # Left half is sorted
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # Right half is sorted
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1

# Example: [4, 5, 6, 7, 0, 1, 2] (rotated sorted array)
arr = [4, 5, 6, 7, 0, 1, 2]
result = search_rotated_array(arr, 0)  # Returns index 4
''',
            "explanation": "Binary search adapted for rotated sorted arrays"
        }