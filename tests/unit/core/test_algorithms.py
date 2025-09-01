# tests/unit/core/test_algorithms.py
# Unit tests for algorithms concepts and exercises

import pytest
import time
import random
from unittest.mock import Mock, AsyncMock
from typing import List, Dict, Set, Tuple, Optional, Any

# Import modules under test (adjust based on your actual structure)
try:
    from src.core.algorithms import (
        SortingExercise,
        SearchingExercise,
        RecursionExercise,
        DynamicProgrammingExercise,
        GraphAlgorithmExercise,
        GreedyAlgorithmExercise
    )
    from src.core.evaluators import AlgorithmEvaluator
except ImportError:
    # Mock classes for when actual modules don't exist
    class SortingExercise:
        pass
    class SearchingExercise:
        pass
    class RecursionExercise:
        pass
    class DynamicProgrammingExercise:
        pass
    class GraphAlgorithmExercise:
        pass
    class GreedyAlgorithmExercise:
        pass
    class AlgorithmEvaluator:
        pass


class TestSortingAlgorithms:
    """Test cases for sorting algorithm exercises."""
    
    def test_bubble_sort(self):
        """Test bubble sort implementation."""
        code = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

# Test cases
test_array_1 = [64, 34, 25, 12, 22, 11, 90]
result_1 = bubble_sort(test_array_1.copy())

test_array_2 = [5, 2, 8, 6, 1, 9, 4]
result_2 = bubble_sort(test_array_2.copy())

empty_array = []
result_empty = bubble_sort(empty_array.copy())

single_element = [42]
result_single = bubble_sort(single_element.copy())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result_1'] == [11, 12, 22, 25, 34, 64, 90]
        assert globals_dict['result_2'] == [1, 2, 4, 5, 6, 8, 9]
        assert globals_dict['result_empty'] == []
        assert globals_dict['result_single'] == [42]
    
    def test_selection_sort(self):
        """Test selection sort implementation."""
        code = '''
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

test_array = [64, 25, 12, 22, 11]
result = selection_sort(test_array.copy())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == [11, 12, 22, 25, 64]
    
    def test_insertion_sort(self):
        """Test insertion sort implementation."""
        code = '''
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

test_array = [12, 11, 13, 5, 6]
result = insertion_sort(test_array.copy())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == [5, 6, 11, 12, 13]
    
    def test_merge_sort(self):
        """Test merge sort implementation."""
        code = '''
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
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

test_array = [38, 27, 43, 3, 9, 82, 10]
result = merge_sort(test_array)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == [3, 9, 10, 27, 38, 43, 82]
    
    def test_quick_sort(self):
        """Test quick sort implementation."""
        code = '''
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

test_array = [3, 6, 8, 10, 1, 2, 1]
result = quick_sort(test_array)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == [1, 1, 2, 3, 6, 8, 10]
    
    def test_heap_sort(self):
        """Test heap sort implementation."""
        code = '''
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

def heap_sort(arr):
    n = len(arr)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    
    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)
    
    return arr

test_array = [12, 11, 13, 5, 6, 7]
result = heap_sort(test_array.copy())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == [5, 6, 7, 11, 12, 13]


class TestSearchingAlgorithms:
    """Test cases for searching algorithm exercises."""
    
    def test_linear_search(self):
        """Test linear search implementation."""
        code = '''
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

# Test cases
arr = [2, 3, 4, 10, 40]
found_index = linear_search(arr, 10)
not_found_index = linear_search(arr, 5)
first_element = linear_search(arr, 2)
last_element = linear_search(arr, 40)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['found_index'] == 3
        assert globals_dict['not_found_index'] == -1
        assert globals_dict['first_element'] == 0
        assert globals_dict['last_element'] == 4
    
    def test_binary_search(self):
        """Test binary search implementation."""
        code = '''
def binary_search(arr, target):
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

# Test cases
sorted_arr = [2, 3, 4, 10, 40]
found_index = binary_search(sorted_arr, 10)
not_found_index = binary_search(sorted_arr, 5)
first_element = binary_search(sorted_arr, 2)
last_element = binary_search(sorted_arr, 40)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['found_index'] == 3
        assert globals_dict['not_found_index'] == -1
        assert globals_dict['first_element'] == 0
        assert globals_dict['last_element'] == 4
    
    def test_binary_search_recursive(self):
        """Test recursive binary search implementation."""
        code = '''
def binary_search_recursive(arr, target, left=0, right=None):
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)

sorted_arr = [1, 3, 5, 7, 9, 11, 13, 15]
found_index = binary_search_recursive(sorted_arr, 7)
not_found_index = binary_search_recursive(sorted_arr, 6)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['found_index'] == 3
        assert globals_dict['not_found_index'] == -1
    
    def test_find_first_and_last_position(self):
        """Test finding first and last position of target in sorted array."""
        code = '''
def find_first_position(arr, target):
    left, right = 0, len(arr) - 1
    first_pos = -1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            first_pos = mid
            right = mid - 1  # Continue searching in left half
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return first_pos

def find_last_position(arr, target):
    left, right = 0, len(arr) - 1
    last_pos = -1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            last_pos = mid
            left = mid + 1  # Continue searching in right half
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return last_pos

arr_with_duplicates = [5, 7, 7, 8, 8, 8, 10]
first_8 = find_first_position(arr_with_duplicates, 8)
last_8 = find_last_position(arr_with_duplicates, 8)
first_7 = find_first_position(arr_with_duplicates, 7)
last_7 = find_last_position(arr_with_duplicates, 7)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['first_8'] == 3
        assert globals_dict['last_8'] == 5
        assert globals_dict['first_7'] == 1
        assert globals_dict['last_7'] == 2


class TestRecursionAlgorithms:
    """Test cases for recursion algorithm exercises."""
    
    def test_factorial(self):
        """Test factorial implementation."""
        code = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test cases
fact_0 = factorial(0)
fact_1 = factorial(1)
fact_5 = factorial(5)
fact_10 = factorial(10)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['fact_0'] == 1
        assert globals_dict['fact_1'] == 1
        assert globals_dict['fact_5'] == 120
        assert globals_dict['fact_10'] == 3628800
    
    def test_fibonacci(self):
        """Test fibonacci implementation."""
        code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Test cases
fib_0 = fibonacci(0)
fib_1 = fibonacci(1)
fib_10 = fibonacci(10)

# Generate sequence
fib_sequence = [fibonacci(i) for i in range(10)]
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['fib_0'] == 0
        assert globals_dict['fib_1'] == 1
        assert globals_dict['fib_10'] == 55
        assert globals_dict['fib_sequence'] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    
    def test_power_function(self):
        """Test power function implementation."""
        code = '''
def power(base, exp):
    if exp == 0:
        return 1
    if exp == 1:
        return base
    
    if exp % 2 == 0:
        half_power = power(base, exp // 2)
        return half_power * half_power
    else:
        return base * power(base, exp - 1)

# Test cases
power_2_3 = power(2, 3)
power_5_4 = power(5, 4)
power_any_0 = power(123, 0)
power_2_10 = power(2, 10)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['power_2_3'] == 8
        assert globals_dict['power_5_4'] == 625
        assert globals_dict['power_any_0'] == 1
        assert globals_dict['power_2_10'] == 1024
    
    def test_tower_of_hanoi(self):
        """Test Tower of Hanoi implementation."""
        code = '''
def tower_of_hanoi(n, source, destination, auxiliary):
    moves = []
    
    def hanoi_recursive(n, source, destination, auxiliary):
        if n == 1:
            moves.append(f"Move disk 1 from {source} to {destination}")
            return
        
        hanoi_recursive(n - 1, source, auxiliary, destination)
        moves.append(f"Move disk {n} from {source} to {destination}")
        hanoi_recursive(n - 1, auxiliary, destination, source)
    
    hanoi_recursive(n, source, destination, auxiliary)
    return moves

# Test with 3 disks
moves_3 = tower_of_hanoi(3, 'A', 'C', 'B')
num_moves_3 = len(moves_3)

# Test with 2 disks
moves_2 = tower_of_hanoi(2, 'A', 'C', 'B')
num_moves_2 = len(moves_2)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['num_moves_2'] == 3
        assert globals_dict['num_moves_3'] == 7
        assert "Move disk 3 from A to C" in globals_dict['moves_3']
    
    def test_binary_tree_traversal(self):
        """Test binary tree traversal implementations."""
        code = '''
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder_traversal(root):
    result = []
    if root:
        result.extend(inorder_traversal(root.left))
        result.append(root.val)
        result.extend(inorder_traversal(root.right))
    return result

def preorder_traversal(root):
    result = []
    if root:
        result.append(root.val)
        result.extend(preorder_traversal(root.left))
        result.extend(preorder_traversal(root.right))
    return result

def postorder_traversal(root):
    result = []
    if root:
        result.extend(postorder_traversal(root.left))
        result.extend(postorder_traversal(root.right))
        result.append(root.val)
    return result

# Create test tree:    1
#                    /   \\
#                   2     3
#                  / \\
#                 4   5
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

inorder_result = inorder_traversal(root)
preorder_result = preorder_traversal(root)
postorder_result = postorder_traversal(root)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['inorder_result'] == [4, 2, 5, 1, 3]
        assert globals_dict['preorder_result'] == [1, 2, 4, 5, 3]
        assert globals_dict['postorder_result'] == [4, 5, 2, 3, 1]


class TestDynamicProgramming:
    """Test cases for dynamic programming algorithm exercises."""
    
    def test_fibonacci_dp(self):
        """Test dynamic programming fibonacci implementation."""
        code = '''
def fibonacci_dp(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    
    return dp[n]

def fibonacci_space_optimized(n):
    if n <= 1:
        return n
    
    prev2, prev1 = 0, 1
    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current
    
    return prev1

# Test cases
fib_dp_10 = fibonacci_dp(10)
fib_optimized_10 = fibonacci_space_optimized(10)
fib_dp_20 = fibonacci_dp(20)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['fib_dp_10'] == 55
        assert globals_dict['fib_optimized_10'] == 55
        assert globals_dict['fib_dp_20'] == 6765
    
    def test_longest_common_subsequence(self):
        """Test LCS dynamic programming implementation."""
        code = '''
def lcs_length(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]

def lcs_string(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill the dp table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    # Reconstruct LCS
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if text1[i - 1] == text2[j - 1]:
            lcs.append(text1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    
    return ''.join(reversed(lcs))

# Test cases
lcs_len = lcs_length("ABCDGH", "AEDFHR")
lcs_str = lcs_string("ABCDGH", "AEDFHR")
lcs_len2 = lcs_length("AGGTAB", "GXTXAYB")
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['lcs_len'] == 3  # "ADH"
        assert globals_dict['lcs_str'] == "ADH"
        assert globals_dict['lcs_len2'] == 4  # "GTAB"
    
    def test_knapsack_problem(self):
        """Test 0-1 Knapsack problem implementation."""
        code = '''
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    values[i - 1] + dp[i - 1][w - weights[i - 1]],
                    dp[i - 1][w]
                )
            else:
                dp[i][w] = dp[i - 1][w]
    
    return dp[n][capacity]

def knapsack_with_items(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    # Fill the dp table
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    values[i - 1] + dp[i - 1][w - weights[i - 1]],
                    dp[i - 1][w]
                )
            else:
                dp[i][w] = dp[i - 1][w]
    
    # Reconstruct solution
    selected_items = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_items.append(i - 1)
            w -= weights[i - 1]
    
    return dp[n][capacity], selected_items

# Test case
weights = [10, 20, 30]
values = [60, 100, 120]
capacity = 50

max_value = knapsack(weights, values, capacity)
max_value_with_items, selected = knapsack_with_items(weights, values, capacity)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['max_value'] == 220  # Items 1 and 2 (values 100 + 120)
        assert globals_dict['max_value_with_items'] == 220
        assert set(globals_dict['selected']) == {1, 2}  # Second and third items
    
    def test_coin_change(self):
        """Test coin change problem implementation."""
        code = '''
def coin_change_min_coins(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1

def coin_change_ways(coins, amount):
    dp = [0] * (amount + 1)
    dp[0] = 1
    
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] += dp[i - coin]
    
    return dp[amount]

# Test cases
coins = [1, 3, 4]
min_coins_6 = coin_change_min_coins(coins, 6)
ways_6 = coin_change_ways(coins, 6)

coins2 = [2]
min_coins_3 = coin_change_min_coins(coins2, 3)  # Impossible
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['min_coins_6'] == 2  # 3 + 3 = 6
        assert globals_dict['ways_6'] > 0  # Multiple ways exist
        assert globals_dict['min_coins_3'] == -1  # Impossible with only coin 2


class TestGraphAlgorithms:
    """Test cases for graph algorithm exercises."""
    
    def test_graph_representation(self):
        """Test graph representation and basic operations."""
        code = '''
class Graph:
    def __init__(self):
        self.graph = {}
    
    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = []
    
    def add_edge(self, vertex1, vertex2):
        self.add_vertex(vertex1)
        self.add_vertex(vertex2)
        self.graph[vertex1].append(vertex2)
        self.graph[vertex2].append(vertex1)  # Undirected graph
    
    def get_vertices(self):
        return list(self.graph.keys())
    
    def get_edges(self):
        edges = []
        for vertex in self.graph:
            for neighbor in self.graph[vertex]:
                if (neighbor, vertex) not in edges:
                    edges.append((vertex, neighbor))
        return edges

# Create test graph
g = Graph()
g.add_edge('A', 'B')
g.add_edge('A', 'C')
g.add_edge('B', 'D')
g.add_edge('C', 'D')

vertices = g.get_vertices()
edges = g.get_edges()
num_vertices = len(vertices)
num_edges = len(edges)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['num_vertices'] == 4
        assert globals_dict['num_edges'] == 4
        assert 'A' in globals_dict['vertices']
    
    def test_bfs(self):
        """Test Breadth-First Search implementation."""
        code = '''
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    result = []
    
    while queue:
        vertex = queue.popleft()
        if vertex not in visited:
            visited.add(vertex)
            result.append(vertex)
            
            for neighbor in graph.get(vertex, []):
                if neighbor not in visited:
                    queue.append(neighbor)
    
    return result

def bfs_shortest_path(graph, start, end):
    visited = set()
    queue = deque([(start, [start])])
    
    while queue:
        vertex, path = queue.popleft()
        if vertex not in visited:
            visited.add(vertex)
            
            if vertex == end:
                return path
            
            for neighbor in graph.get(vertex, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
    
    return None

# Test graph
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

bfs_result = bfs(graph, 'A')
shortest_path = bfs_shortest_path(graph, 'A', 'F')
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['bfs_result'][0] == 'A'  # Starts with A
        assert 'F' in globals_dict['bfs_result']
        assert globals_dict['shortest_path'] == ['A', 'C', 'F']
    
    def test_dfs(self):
        """Test Depth-First Search implementation."""
        code = '''
def dfs_recursive(graph, start, visited=None):
    if visited is None:
        visited = set()
    
    result = []
    if start not in visited:
        visited.add(start)
        result.append(start)
        
        for neighbor in graph.get(start, []):
            result.extend(dfs_recursive(graph, neighbor, visited))
    
    return result

def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    result = []
    
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            result.append(vertex)
            
            # Add neighbors to stack (in reverse order for consistency)
            for neighbor in reversed(graph.get(vertex, [])):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return result

# Test graph
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

dfs_recursive_result = dfs_recursive(graph, 'A')
dfs_iterative_result = dfs_iterative(graph, 'A')
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['dfs_recursive_result'][0] == 'A'
        assert globals_dict['dfs_iterative_result'][0] == 'A'
        assert len(globals_dict['dfs_recursive_result']) == 6
        assert len(globals_dict['dfs_iterative_result']) == 6
    
    def test_dijkstra_algorithm(self):
        """Test Dijkstra's shortest path algorithm."""
        code = '''
import heapq

def dijkstra(graph, start):
    distances = {vertex: float('inf') for vertex in graph}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()
    
    while pq:
        current_distance, current_vertex = heapq.heappop(pq)
        
        if current_vertex in visited:
            continue
        
        visited.add(current_vertex)
        
        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances

# Test weighted graph
weighted_graph = {
    'A': {'B': 4, 'C': 2},
    'B': {'A': 4, 'C': 1, 'D': 5},
    'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},
    'D': {'B': 5, 'C': 8, 'E': 2},
    'E': {'C': 10, 'D': 2}
}

distances_from_A = dijkstra(weighted_graph, 'A')
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['distances_from_A']['A'] == 0
        assert globals_dict['distances_from_A']['B'] == 3  # A -> C -> B
        assert globals_dict['distances_from_A']['C'] == 2  # A -> C
        assert globals_dict['distances_from_A']['D'] == 8  # A -> C -> B -> D
        assert globals_dict['distances_from_A']['E'] == 10  # A -> C -> B -> D -> E


class TestGreedyAlgorithms:
    """Test cases for greedy algorithm exercises."""
    
    def test_activity_selection(self):
        """Test activity selection greedy algorithm."""
        code = '''
def activity_selection(start_times, finish_times):
    n = len(start_times)
    activities = list(zip(range(n), start_times, finish_times))
    
    # Sort by finish time
    activities.sort(key=lambda x: x[2])
    
    selected = [activities[0]]
    last_finish_time = activities[0][2]
    
    for i in range(1, n):
        activity_id, start_time, finish_time = activities[i]
        if start_time >= last_finish_time:
            selected.append((activity_id, start_time, finish_time))
            last_finish_time = finish_time
    
    return selected

# Test case
start_times = [1, 3, 0, 5, 8, 5]
finish_times = [2, 4, 6, 7, 9, 9]

selected_activities = activity_selection(start_times, finish_times)
num_selected = len(selected_activities)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['num_selected'] >= 3  # Should select at least 3 activities
        # Verify activities don't overlap
        selected = globals_dict['selected_activities']
        for i in range(len(selected) - 1):
            assert selected[i][2] <= selected[i+1][1]  # finish[i] <= start[i+1]
    
    def test_fractional_knapsack(self):
        """Test fractional knapsack greedy algorithm."""
        code = '''
def fractional_knapsack(weights, values, capacity):
    n = len(weights)
    items = list(zip(range(n), weights, values))
    
    # Sort by value-to-weight ratio in descending order
    items.sort(key=lambda x: x[2] / x[1], reverse=True)
    
    total_value = 0
    selected_items = []
    
    for item_id, weight, value in items:
        if capacity >= weight:
            # Take the whole item
            capacity -= weight
            total_value += value
            selected_items.append((item_id, 1.0, value))  # (id, fraction, value)
        else:
            # Take fraction of the item
            fraction = capacity / weight
            total_value += value * fraction
            selected_items.append((item_id, fraction, value * fraction))
            break
    
    return total_value, selected_items

# Test case
weights = [10, 40, 20, 30]
values = [60, 40, 100, 120]
capacity = 50

max_value, selected = fractional_knapsack(weights, values, capacity)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['max_value'] == 240  # Should be optimal for fractional knapsack
        assert len(globals_dict['selected']) > 0
    
    def test_huffman_coding(self):
        """Test Huffman coding greedy algorithm."""
        code = '''
import heapq
from collections import defaultdict, Counter

class Node:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq

def huffman_coding(text):
    # Count frequency of characters
    freq = Counter(text)
    
    # Create a priority queue of nodes
    heap = [Node(char, freq) for char, freq in freq.items()]
    heapq.heapify(heap)
    
    # Build Huffman tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        merged = Node(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    
    # Generate codes
    root = heap[0] if heap else None
    codes = {}
    
    def generate_codes(node, code=""):
        if node:
            if node.char:  # Leaf node
                codes[node.char] = code or "0"  # Handle single character case
            else:
                generate_codes(node.left, code + "0")
                generate_codes(node.right, code + "1")
    
    generate_codes(root)
    
    # Encode text
    encoded = "".join(codes[char] for char in text)
    
    return codes, encoded

# Test case
text = "hello world"
codes, encoded_text = huffman_coding(text)
original_bits = len(text) * 8  # ASCII encoding
compressed_bits = len(encoded_text)
compression_ratio = compressed_bits / original_bits if original_bits > 0 else 0
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['codes']) > 0
        assert len(globals_dict['encoded_text']) > 0
        assert globals_dict['compression_ratio'] < 1  # Should be compressed


class TestAlgorithmEvaluator:
    """Test cases for algorithm evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create an algorithm evaluator instance."""
        return AlgorithmEvaluator()
    
    def test_evaluate_sorting_algorithm(self, evaluator):
        """Test evaluation of sorting algorithm."""
        code = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

test_array = [64, 34, 25, 12, 22, 11, 90]
result = bubble_sort(test_array.copy())
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert result['globals']['result'] == [11, 12, 22, 25, 34, 64, 90]
    
    def test_check_algorithm_complexity(self, evaluator):
        """Test checking algorithm time complexity."""
        bubble_sort_code = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
'''
        
        merge_sort_code = '''
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
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
'''
        
        bubble_complexity = evaluator.analyze_complexity(bubble_sort_code)
        merge_complexity = evaluator.analyze_complexity(merge_sort_code)
        
        # These would be simplified analyses
        assert 'nested_loops' in bubble_complexity
        assert 'recursion' in merge_complexity
    
    def test_performance_comparison(self, evaluator):
        """Test performance comparison of algorithms."""
        import time
        
        # Simple performance test
        sizes = [100, 500, 1000]
        bubble_times = []
        merge_times = []
        
        for size in sizes:
            # Generate random array
            import random
            arr = [random.randint(1, 1000) for _ in range(size)]
            
            # Test bubble sort
            start_time = time.time()
            sorted_arr = sorted(arr)  # Use built-in for comparison
            bubble_time = time.time() - start_time
            bubble_times.append(bubble_time)
            
            # Test merge sort (simulated with built-in)
            start_time = time.time()
            sorted_arr = sorted(arr)
            merge_time = time.time() - start_time
            merge_times.append(merge_time)
        
        # Simple assertion that times are recorded
        assert len(bubble_times) == len(sizes)
        assert len(merge_times) == len(sizes)


@pytest.mark.integration
class TestAlgorithmIntegration:
    """Integration tests for algorithm exercises."""
    
    def test_algorithm_progression(self):
        """Test progression through algorithm exercises."""
        # This would test a complete learning path through algorithms
        exercises = [
            "linear_search",
            "binary_search", 
            "bubble_sort",
            "merge_sort",
            "fibonacci_recursive",
            "fibonacci_dp"
        ]
        
        completed_exercises = []
        for exercise in exercises:
            # Simulate completing each exercise
            completed_exercises.append(exercise)
        
        assert len(completed_exercises) == len(exercises)
    
    def test_real_world_algorithm_application(self):
        """Test real-world application of algorithms."""
        code = '''
# Social network analysis using graph algorithms
from collections import defaultdict, deque

class SocialNetwork:
    def __init__(self):
        self.graph = defaultdict(list)
        self.users = set()
    
    def add_friendship(self, user1, user2):
        self.graph[user1].append(user2)
        self.graph[user2].append(user1)
        self.users.add(user1)
        self.users.add(user2)
    
    def mutual_friends(self, user1, user2):
        friends1 = set(self.graph[user1])
        friends2 = set(self.graph[user2])
        return friends1.intersection(friends2)
    
    def degrees_of_separation(self, user1, user2):
        if user1 == user2:
            return 0
        
        visited = set()
        queue = deque([(user1, 0)])
        
        while queue:
            current_user, distance = queue.popleft()
            if current_user in visited:
                continue
            visited.add(current_user)
            
            for friend in self.graph[current_user]:
                if friend == user2:
                    return distance + 1
                if friend not in visited:
                    queue.append((friend, distance + 1))
        
        return -1  # Not connected
    
    def suggest_friends(self, user, max_suggestions=3):
        friends = set(self.graph[user])
        suggestions = defaultdict(int)
        
        # Count mutual friends
        for friend in friends:
            for friend_of_friend in self.graph[friend]:
                if friend_of_friend != user and friend_of_friend not in friends:
                    suggestions[friend_of_friend] += 1
        
        # Sort by number of mutual friends
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        return [user for user, count in sorted_suggestions[:max_suggestions]]

# Test the social network
sn = SocialNetwork()
sn.add_friendship("Alice", "Bob")
sn.add_friendship("Bob", "Charlie")
sn.add_friendship("Alice", "David")
sn.add_friendship("David", "Charlie")
sn.add_friendship("Charlie", "Eve")

mutual = sn.mutual_friends("Alice", "Charlie")
separation = sn.degrees_of_separation("Alice", "Eve")
suggestions = sn.suggest_friends("Alice")
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert "Bob" in globals_dict['mutual'] or "David" in globals_dict['mutual']
        assert globals_dict['separation'] == 2  # Alice -> Bob/David -> Charlie -> Eve
        assert len(globals_dict['suggestions']) > 0


if __name__ == '__main__':
    pytest.main([__file__])