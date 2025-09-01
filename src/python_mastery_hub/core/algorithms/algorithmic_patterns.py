"""
Algorithmic patterns demonstrations for the Algorithms module.
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from .base import AlgorithmDemo


class AlgorithmicPatterns(AlgorithmDemo):
    """Demonstration class for algorithmic patterns."""
    
    def __init__(self):
        super().__init__("algorithmic_patterns")
    
    def _setup_examples(self) -> None:
        """Setup algorithmic patterns examples."""
        self.examples = {
            "two_pointers": {
                "code": '''
def two_sum_sorted(arr, target):
    """Two-pointer technique for two sum in sorted array."""
    left, right = 0, len(arr) - 1
    
    print(f"Finding two numbers in {arr} that sum to {target}")
    
    while left < right:
        current_sum = arr[left] + arr[right]
        print(f"  Check: arr[{left}] + arr[{right}] = {arr[left]} + {arr[right]} = {current_sum}")
        
        if current_sum == target:
            print(f"  ✓ Found: {arr[left]} + {arr[right]} = {target}")
            return [left, right]
        elif current_sum < target:
            print(f"    {current_sum} < {target}, move left pointer right")
            left += 1
        else:
            print(f"    {current_sum} > {target}, move right pointer left")
            right -= 1
    
    print("  ✗ No solution found")
    return []

def remove_duplicates(arr):
    """Remove duplicates from sorted array using two pointers."""
    if not arr:
        return 0
    
    print(f"Removing duplicates from {arr}")
    
    # Two pointers: slow for unique elements, fast for scanning
    slow = 0
    
    for fast in range(1, len(arr)):
        if arr[fast] != arr[slow]:
            slow += 1
            arr[slow] = arr[fast]
            print(f"  Found unique element {arr[fast]} at position {slow}")
    
    unique_length = slow + 1
    print(f"  Array after removing duplicates: {arr[:unique_length]}")
    return unique_length

def palindrome_check(s):
    """Check if string is palindrome using two pointers."""
    # Clean string: remove non-alphanumeric and convert to lowercase
    cleaned = ''.join(char.lower() for char in s if char.isalnum())
    print(f"Checking palindrome: '{s}' → '{cleaned}'")
    
    left, right = 0, len(cleaned) - 1
    
    while left < right:
        print(f"  Compare: '{cleaned[left]}' vs '{cleaned[right]}'")
        if cleaned[left] != cleaned[right]:
            print(f"  ✗ Not a palindrome")
            return False
        left += 1
        right -= 1
    
    print(f"  ✓ Is a palindrome")
    return True

def three_sum(arr, target=0):
    """Find triplets that sum to target using two pointers."""
    arr.sort()
    result = []
    n = len(arr)
    
    print(f"Finding triplets in {arr} that sum to {target}")
    
    for i in range(n - 2):
        # Skip duplicates for first element
        if i > 0 and arr[i] == arr[i - 1]:
            continue
        
        left, right = i + 1, n - 1
        
        while left < right:
            current_sum = arr[i] + arr[left] + arr[right]
            
            if current_sum == target:
                triplet = [arr[i], arr[left], arr[right]]
                result.append(triplet)
                print(f"  Found triplet: {triplet}")
                
                # Skip duplicates
                while left < right and arr[left] == arr[left + 1]:
                    left += 1
                while left < right and arr[right] == arr[right - 1]:
                    right -= 1
                
                left += 1
                right -= 1
            elif current_sum < target:
                left += 1
            else:
                right -= 1
    
    return result

# Example usage
sorted_array = [2, 7, 11, 15, 20, 25]
two_sum_sorted(sorted_array, 22)

nums_with_dups = [1, 1, 2, 2, 2, 3, 4, 4, 5]
unique_count = remove_duplicates(nums_with_dups)

palindrome_check("A man a plan a canal Panama")

test_array = [-1, 0, 1, 2, -1, -4]
triplets = three_sum(test_array, 0)
print(f"All triplets: {triplets}")
''',
                "explanation": "Two pointers technique efficiently solves array and string problems with O(n) time complexity",
                "time_complexity": "O(n) for most two-pointer problems",
                "space_complexity": "O(1) additional space"
            },
            
            "sliding_window": {
                "code": '''
def max_sum_subarray(arr, k):
    """Find maximum sum of subarray of size k using sliding window."""
    n = len(arr)
    if n < k:
        return None
    
    print(f"Finding max sum of subarray size {k} in {arr}")
    
    # Calculate sum of first window
    window_sum = sum(arr[:k])
    max_sum = window_sum
    
    print(f"Initial window [0:{k}]: {arr[:k]}, sum = {window_sum}")
    
    # Slide the window
    for i in range(k, n):
        # Remove first element of previous window and add last element of current window
        window_sum = window_sum - arr[i - k] + arr[i]
        max_sum = max(max_sum, window_sum)
        
        window_start = i - k + 1
        current_window = arr[window_start:i+1]
        print(f"Window [{window_start}:{i+1}]: {current_window}, sum = {window_sum}")
    
    print(f"Maximum subarray sum: {max_sum}")
    return max_sum

def longest_substring_without_repeating(s):
    """Find longest substring without repeating characters."""
    n = len(s)
    char_index = {}
    max_length = 0
    start = 0
    
    print(f"Finding longest substring without repeating chars in '{s}'")
    
    for end in range(n):
        char = s[end]
        
        # If character is already in current window, move start
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
            print(f"  Found repeat '{char}', move start to {start}")
        
        char_index[char] = end
        current_length = end - start + 1
        max_length = max(max_length, current_length)
        
        current_substring = s[start:end+1]
        print(f"  Window [{start}:{end+1}]: '{current_substring}', length = {current_length}")
    
    print(f"Longest substring length: {max_length}")
    return max_length

def min_window_substring(s, t):
    """Find minimum window substring containing all characters of t."""
    from collections import Counter, defaultdict
    
    if not s or not t:
        return ""
    
    # Count characters in t
    target_count = Counter(t)
    required = len(target_count)
    
    # Sliding window counters
    window_count = defaultdict(int)
    formed = 0  # Number of unique chars in window with desired frequency
    
    left = right = 0
    min_len = float('inf')
    min_left = 0
    
    print(f"Finding minimum window in '{s}' containing '{t}'")
    print(f"Target count: {dict(target_count)}")
    
    while right < len(s):
        # Add character from right to window
        char = s[right]
        window_count[char] += 1
        
        # Check if frequency of current character matches target
        if char in target_count and window_count[char] == target_count[char]:
            formed += 1
        
        # Try to contract window from left
        while left <= right and formed == required:
            char = s[left]
            
            # Update minimum window if this window is smaller
            if right - left + 1 < min_len:
                min_len = right - left + 1
                min_left = left
                current_window = s[left:right+1]
                print(f"  New min window: '{current_window}', length = {min_len}")
            
            # Remove character from left of window
            window_count[char] -= 1
            if char in target_count and window_count[char] < target_count[char]:
                formed -= 1
            
            left += 1
        
        right += 1
    
    result = "" if min_len == float('inf') else s[min_left:min_left + min_len]
    print(f"Minimum window substring: '{result}'")
    return result

def sliding_window_maximum(arr, k):
    """Find maximum in each sliding window of size k."""
    from collections import deque
    
    if not arr or k == 0:
        return []
    
    # Deque to store indices
    dq = deque()
    result = []
    
    print(f"Finding sliding window maximum in {arr} with window size {k}")
    
    for i in range(len(arr)):
        # Remove indices outside current window
        while dq and dq[0] <= i - k:
            dq.popleft()
        
        # Remove indices of elements smaller than current element
        while dq and arr[dq[-1]] < arr[i]:
            dq.pop()
        
        dq.append(i)
        
        # Add maximum to result if window is complete
        if i >= k - 1:
            max_element = arr[dq[0]]
            result.append(max_element)
            window = arr[i-k+1:i+1]
            print(f"  Window {window}: max = {max_element}")
    
    return result

# Example usage
arr1 = [1, 4, 2, 10, 23, 3, 1, 0, 20]
max_sum_subarray(arr1, 4)

print("\\n" + "="*50)
longest_substring_without_repeating("abcabcbb")

print("\\n" + "="*50)
min_window_substring("ADOBECODEBANC", "ABC")

print("\\n" + "="*50)
test_array = [1, 3, -1, -3, 5, 3, 6, 7]
result = sliding_window_maximum(test_array, 3)
print(f"Sliding window maximums: {result}")
''',
                "explanation": "Sliding window technique efficiently processes subarrays or substrings with optimal time complexity",
                "time_complexity": "O(n) for most sliding window problems",
                "space_complexity": "O(k) for window storage"
            },
            
            "fast_slow_pointers": {
                "code": '''
class ListNode:
    """Simple linked list node for demonstration."""
    def __init__(self, val=0):
        self.val = val
        self.next = None
    
    def __repr__(self):
        return f"Node({self.val})"

def has_cycle(head):
    """Detect cycle in linked list using Floyd's algorithm."""
    if not head or not head.next:
        return False
    
    slow = fast = head
    
    print("Detecting cycle using fast/slow pointers:")
    step = 0
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        step += 1
        
        print(f"  Step {step}: slow at {slow.val}, fast at {fast.val if fast else 'None'}")
        
        if slow == fast:
            print("  ✓ Cycle detected!")
            return True
    
    print("  ✗ No cycle found")
    return False

def find_cycle_start(head):
    """Find the start of cycle in linked list."""
    if not head or not head.next:
        return None
    
    # Phase 1: Detect cycle
    slow = fast = head
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None  # No cycle
    
    # Phase 2: Find cycle start
    print("Phase 2: Finding cycle start")
    start = head
    
    while start != slow:
        start = start.next
        slow = slow.next
        print(f"  Moving start to {start.val}, slow to {slow.val}")
    
    print(f"  Cycle starts at node {start.val}")
    return start

def find_middle(head):
    """Find middle node of linked list."""
    if not head:
        return None
    
    slow = fast = head
    
    print("Finding middle using fast/slow pointers:")
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        print(f"  slow at {slow.val}, fast at {fast.val if fast else 'None'}")
    
    print(f"  Middle node: {slow.val}")
    return slow

def is_happy_number(n):
    """Check if number is happy using fast/slow pointers."""
    def get_sum_of_squares(num):
        total = 0
        while num > 0:
            digit = num % 10
            total += digit * digit
            num //= 10
        return total
    
    slow = fast = n
    
    print(f"Checking if {n} is a happy number:")
    
    while True:
        slow = get_sum_of_squares(slow)
        fast = get_sum_of_squares(get_sum_of_squares(fast))
        
        print(f"  slow = {slow}, fast = {fast}")
        
        if fast == 1:
            print("  ✓ Happy number!")
            return True
        
        if slow == fast:
            print("  ✗ Not a happy number (cycle detected)")
            return False

def remove_nth_from_end(head, n):
    """Remove nth node from end using two pointers."""
    dummy = ListNode(0)
    dummy.next = head
    
    first = second = dummy
    
    # Move first pointer n+1 steps ahead
    for _ in range(n + 1):
        first = first.next
    
    print(f"Removing {n}th node from end:")
    print(f"  Initial gap of {n+1} created")
    
    # Move both pointers until first reaches end
    while first:
        first = first.next
        second = second.next
        if first:
            print(f"  first at {first.val}, second at {second.val}")
    
    # Remove the node
    node_to_remove = second.next
    second.next = second.next.next
    print(f"  Removed node {node_to_remove.val}")
    
    return dummy.next

# Helper function to create linked list
def create_linked_list(values):
    """Create linked list from list of values."""
    if not values:
        return None
    
    head = ListNode(values[0])
    current = head
    
    for val in values[1:]:
        current.next = ListNode(val)
        current = current.next
    
    return head

def print_linked_list(head, max_nodes=10):
    """Print linked list (with cycle protection)."""
    values = []
    current = head
    count = 0
    
    while current and count < max_nodes:
        values.append(current.val)
        current = current.next
        count += 1
    
    if current:
        values.append("...")
    
    print(f"List: {' -> '.join(map(str, values))}")

# Example usage
print("=== Fast/Slow Pointers (Floyd's Algorithm) ===")

# Create linked list: 1 -> 2 -> 3 -> 4 -> 5
head = create_linked_list([1, 2, 3, 4, 5])
print_linked_list(head)

# Test cycle detection
has_cycle(head)

# Create cycle: 1 -> 2 -> 3 -> 4 -> 5 -> 3 (back to 3)
head_with_cycle = create_linked_list([1, 2, 3, 4, 5])
# Manually create cycle for demonstration
current = head_with_cycle
cycle_node = None
while current.next:
    if current.val == 3:
        cycle_node = current
    current = current.next
current.next = cycle_node  # Create cycle

print("\\nList with cycle:")
has_cycle(head_with_cycle)
find_cycle_start(head_with_cycle)

print("\\nFinding middle:")
head2 = create_linked_list([1, 2, 3, 4, 5, 6, 7])
print_linked_list(head2)
find_middle(head2)

print("\\nHappy number check:")
is_happy_number(19)
is_happy_number(4)
''',
                "explanation": "Fast/slow pointers (Floyd's algorithm) detect cycles and solve linked list problems efficiently",
                "time_complexity": "O(n) for cycle detection and middle finding",
                "space_complexity": "O(1) constant space"
            },
            
            "divide_and_conquer": {
                "code": '''
def merge_sort_divide_conquer(arr):
    """Merge sort using divide and conquer approach."""
    if len(arr) <= 1:
        return arr
    
    # Divide
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]
    
    print(f"Dividing {arr} into {left_half} and {right_half}")
    
    # Conquer (recursive calls)
    left_sorted = merge_sort_divide_conquer(left_half)
    right_sorted = merge_sort_divide_conquer(right_half)
    
    # Combine
    merged = merge_arrays(left_sorted, right_sorted)
    print(f"Merging {left_sorted} and {right_sorted} → {merged}")
    
    return merged

def merge_arrays(left, right):
    """Merge two sorted arrays."""
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

def quick_select(arr, k):
    """Find kth smallest element using quick select."""
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def quick_select_helper(arr, low, high, k):
        if low == high:
            return arr[low]
        
        pivot_index = partition(arr, low, high)
        
        print(f"Partition around {arr[pivot_index]}: {arr[low:high+1]}")
        print(f"Looking for {k}th smallest (0-indexed)")
        
        if k == pivot_index:
            return arr[k]
        elif k < pivot_index:
            print(f"Search left partition")
            return quick_select_helper(arr, low, pivot_index - 1, k)
        else:
            print(f"Search right partition")
            return quick_select_helper(arr, pivot_index + 1, high, k)
    
    arr_copy = arr.copy()
    print(f"Finding {k+1}th smallest element in {arr}")
    result = quick_select_helper(arr_copy, 0, len(arr_copy) - 1, k)
    print(f"Result: {result}")
    return result

def maximum_subarray_divide_conquer(arr):
    """Find maximum subarray sum using divide and conquer."""
    def max_crossing_sum(arr, low, mid, high):
        """Find max sum crossing the midpoint."""
        left_sum = float('-inf')
        sum_val = 0
        
        for i in range(mid, low - 1, -1):
            sum_val += arr[i]
            if sum_val > left_sum:
                left_sum = sum_val
        
        right_sum = float('-inf')
        sum_val = 0
        
        for i in range(mid + 1, high + 1):
            sum_val += arr[i]
            if sum_val > right_sum:
                right_sum = sum_val
        
        return left_sum + right_sum
    
    def max_subarray_helper(arr, low, high):
        """Recursive helper for maximum subarray."""
        if low == high:
            return arr[low]
        
        mid = (low + high) // 2
        
        # Find maximum subarray in left half
        left_max = max_subarray_helper(arr, low, mid)
        
        # Find maximum subarray in right half
        right_max = max_subarray_helper(arr, mid + 1, high)
        
        # Find maximum subarray crossing midpoint
        cross_max = max_crossing_sum(arr, low, mid, high)
        
        result = max(left_max, right_max, cross_max)
        print(f"Range [{low}:{high}]: left_max={left_max}, right_max={right_max}, cross_max={cross_max}, result={result}")
        
        return result
    
    print(f"Finding maximum subarray sum in {arr}")
    return max_subarray_helper(arr, 0, len(arr) - 1)

def closest_pair_points(points):
    """Find closest pair of points using divide and conquer."""
    import math
    
    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def brute_force(points):
        """Brute force for small number of points."""
        min_dist = float('inf')
        n = len(points)
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = distance(points[i], points[j])
                if dist < min_dist:
                    min_dist = dist
        
        return min_dist
    
    def closest_pair_rec(px, py):
        """Recursive closest pair function."""
        n = len(px)
        
        # Base case: use brute force for small arrays
        if n <= 3:
            return brute_force(px)
        
        # Divide
        mid = n // 2
        midpoint = px[mid]
        
        pyl = [point for point in py if point[0] <= midpoint[0]]
        pyr = [point for point in py if point[0] > midpoint[0]]
        
        # Conquer
        dl = closest_pair_rec(px[:mid], pyl)
        dr = closest_pair_rec(px[mid:], pyr)
        
        # Find minimum of the two
        d = min(dl, dr)
        
        # Create strip array of points close to midpoint
        strip = [point for point in py if abs(point[0] - midpoint[0]) < d]
        
        # Find closest points in strip
        strip_min = d
        for i in range(len(strip)):
            j = i + 1
            while j < len(strip) and (strip[j][1] - strip[i][1]) < strip_min:
                strip_min = min(strip_min, distance(strip[i], strip[j]))
                j += 1
        
        return min(d, strip_min)
    
    # Sort points by x and y coordinates
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    
    print(f"Finding closest pair among {len(points)} points")
    result = closest_pair_rec(px, py)
    print(f"Minimum distance: {result:.3f}")
    return result

# Example usage
print("=== Divide and Conquer Algorithms ===")

# Merge sort
test_array = [38, 27, 43, 3, 9, 82, 10]
print(f"Original array: {test_array}")
sorted_array = merge_sort_divide_conquer(test_array)
print(f"Sorted array: {sorted_array}")

print("\\n" + "="*50)

# Quick select
test_array2 = [3, 2, 1, 5, 6, 4]
quick_select(test_array2, 2)  # Find 3rd smallest (0-indexed)

print("\\n" + "="*50)

# Maximum subarray
test_array3 = [-2, -3, 4, -1, -2, 1, 5, -3]
max_sum = maximum_subarray_divide_conquer(test_array3)
print(f"Maximum subarray sum: {max_sum}")

print("\\n" + "="*50)

# Closest pair of points
test_points = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
closest_pair_points(test_points)
''',
                "explanation": "Divide and conquer breaks problems into smaller subproblems, solves recursively, then combines results",
                "time_complexity": "Often O(n log n) due to divide step and linear combine step",
                "space_complexity": "O(log n) for recursion stack in most cases"
            },
            
            "greedy_algorithms": {
                "code": '''
def activity_selection(activities):
    """Activity selection problem using greedy approach."""
    # Sort activities by finish time
    sorted_activities = sorted(activities, key=lambda x: x[1])
    
    print("Activity Selection Problem:")
    print(f"Activities (start, finish): {activities}")
    print(f"Sorted by finish time: {sorted_activities}")
    
    selected = [sorted_activities[0]]
    last_finish_time = sorted_activities[0][1]
    
    print(f"\\nSelected activities:")
    print(f"  Activity {sorted_activities[0]} (first activity)")
    
    for i in range(1, len(sorted_activities)):
        start_time, finish_time = sorted_activities[i]
        
        if start_time >= last_finish_time:
            selected.append(sorted_activities[i])
            last_finish_time = finish_time
            print(f"  Activity {sorted_activities[i]} (start >= {last_finish_time})")
        else:
            print(f"  Skipped {sorted_activities[i]} (conflict with previous)")
    
    print(f"\\nTotal activities selected: {len(selected)}")
    return selected

def fractional_knapsack(items, capacity):
    """Fractional knapsack using greedy approach."""
    # Calculate value-to-weight ratio and sort
    for item in items:
        item['ratio'] = item['value'] / item['weight']
    
    sorted_items = sorted(items, key=lambda x: x['ratio'], reverse=True)
    
    print("Fractional Knapsack Problem:")
    print(f"Capacity: {capacity}")
    print(f"Items sorted by value/weight ratio:")
    for item in sorted_items:
        print(f"  {item['name']}: value={item['value']}, weight={item['weight']}, ratio={item['ratio']:.2f}")
    
    total_value = 0
    current_weight = 0
    knapsack = []
    
    print(f"\\nFilling knapsack:")
    
    for item in sorted_items:
        if current_weight + item['weight'] <= capacity:
            # Take entire item
            knapsack.append({'name': item['name'], 'fraction': 1.0, 'value': item['value']})
            current_weight += item['weight']
            total_value += item['value']
            print(f"  Take full {item['name']}: +{item['value']} value")
        else:
            # Take fraction of item
            remaining_capacity = capacity - current_weight
            fraction = remaining_capacity / item['weight']
            value_taken = fraction * item['value']
            
            knapsack.append({'name': item['name'], 'fraction': fraction, 'value': value_taken})
            total_value += value_taken
            current_weight = capacity
            
            print(f"  Take {fraction:.2f} of {item['name']}: +{value_taken:.2f} value")
            break
    
    print(f"\\nTotal value: {total_value:.2f}")
    return knapsack, total_value

def huffman_coding(frequencies):
    """Huffman coding using greedy approach."""
    import heapq
    
    class Node:
        def __init__(self, char, freq):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None
        
        def __lt__(self, other):
            return self.freq < other.freq
    
    # Create min heap
    heap = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)
    
    print("Huffman Coding:")
    print(f"Character frequencies: {frequencies}")
    
    # Build Huffman tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        
        heapq.heappush(heap, merged)
        print(f"  Merged nodes with frequencies {left.freq} and {right.freq}")
    
    # Generate codes
    root = heap[0]
    codes = {}
    
    def generate_codes(node, code=""):
        if node:
            if node.char:  # Leaf node
                codes[node.char] = code if code else "0"
            else:
                generate_codes(node.left, code + "0")
                generate_codes(node.right, code + "1")
    
    generate_codes(root)
    
    print(f"\\nGenerated codes:")
    for char, code in sorted(codes.items()):
        print(f"  '{char}': {code}")
    
    return codes

def job_scheduling(jobs):
    """Job scheduling with deadlines using greedy approach."""
    # Sort jobs by profit in descending order
    sorted_jobs = sorted(jobs, key=lambda x: x['profit'], reverse=True)
    
    print("Job Scheduling with Deadlines:")
    print(f"Jobs sorted by profit:")
    for job in sorted_jobs:
        print(f"  {job['name']}: profit={job['profit']}, deadline={job['deadline']}")
    
    # Find maximum deadline
    max_deadline = max(job['deadline'] for job in jobs)
    
    # Initialize result array
    result = [None] * max_deadline
    total_profit = 0
    
    print(f"\\nScheduling process:")
    
    for job in sorted_jobs:
        # Find latest available slot before deadline
        for slot in range(min(max_deadline, job['deadline']) - 1, -1, -1):
            if result[slot] is None:
                result[slot] = job['name']
                total_profit += job['profit']
                print(f"  Scheduled {job['name']} at time slot {slot+1}: +{job['profit']} profit")
                break
        else:
            print(f"  Could not schedule {job['name']} (no available slots)")
    
    scheduled = [job for job in result if job is not None]
    print(f"\\nScheduled jobs: {scheduled}")
    print(f"Total profit: {total_profit}")
    return scheduled, total_profit

# Example usage
print("=== Greedy Algorithms ===")

# Activity selection
activities = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
selected_activities = activity_selection(activities)

print("\\n" + "="*60)

# Fractional knapsack
items = [
    {'name': 'item1', 'value': 60, 'weight': 10},
    {'name': 'item2', 'value': 100, 'weight': 20},
    {'name': 'item3', 'value': 120, 'weight': 30}
]
knapsack_result, max_value = fractional_knapsack(items, 50)

print("\\n" + "="*60)

# Huffman coding
char_frequencies = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
huffman_codes = huffman_coding(char_frequencies)

print("\\n" + "="*60)

# Job scheduling
jobs = [
    {'name': 'J1', 'profit': 20, 'deadline': 2},
    {'name': 'J2', 'profit': 15, 'deadline': 2},
    {'name': 'J3', 'profit': 10, 'deadline': 1},
    {'name': 'J4', 'profit': 5, 'deadline': 3},
    {'name': 'J5', 'profit': 1, 'deadline': 3}
]
scheduled_jobs, profit = job_scheduling(jobs)
''',
                "explanation": "Greedy algorithms make locally optimal choices at each step, hoping to find global optimum",
                "time_complexity": "Varies by problem, often O(n log n) due to sorting step",
                "space_complexity": "Usually O(1) to O(n) depending on data structures used"
            }
        }
    
    def demonstrate_pattern_comparison(self):
        """Compare different algorithmic patterns."""
        print("=== Algorithmic Patterns Comparison ===")
        
        # Two pointers vs brute force for two sum
        def two_sum_brute_force(arr, target):
            for i in range(len(arr)):
                for j in range(i + 1, len(arr)):
                    if arr[i] + arr[j] == target:
                        return [i, j]
            return []
        
        def two_sum_two_pointers(arr, target):
            left, right = 0, len(arr) - 1
            while left < right:
                current_sum = arr[left] + arr[right]
                if current_sum == target:
                    return [left, right]
                elif current_sum < target:
                    left += 1
                else:
                    right -= 1
            return []
        
        test_array = [2, 7, 11, 15]
        target = 9
        
        print(f"Two Sum in {test_array} with target {target}:")
        print(f"  Brute force result: {two_sum_brute_force(test_array, target)}")
        print(f"  Two pointers result: {two_sum_two_pointers(test_array, target)}")
        
        # Sliding window vs brute force for max subarray
        def max_subarray_brute_force(arr, k):
            max_sum = float('-inf')
            for i in range(len(arr) - k + 1):
                current_sum = sum(arr[i:i+k])
                max_sum = max(max_sum, current_sum)
            return max_sum
        
        def max_subarray_sliding_window(arr, k):
            window_sum = sum(arr[:k])
            max_sum = window_sum
            for i in range(k, len(arr)):
                window_sum = window_sum - arr[i-k] + arr[i]
                max_sum = max(max_sum, window_sum)
            return max_sum
        
        test_array2 = [1, 4, 2, 10, 23, 3, 1, 0, 20]
        k = 4
        
        print(f"\\nMax subarray sum of size {k} in {test_array2}:")
        print(f"  Brute force result: {max_subarray_brute_force(test_array2, k)}")
        print(f"  Sliding window result: {max_subarray_sliding_window(test_array2, k)}")
    
    def get_pattern_guide(self) -> Dict[str, Any]:
        """Get guide for when to use each pattern."""
        return {
            "two_pointers": {
                "when_to_use": [
                    "Sorted array problems",
                    "Palindrome checking",
                    "Finding pairs with specific sum",
                    "Removing duplicates"
                ],
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "variations": ["Fast/slow pointers", "Left/right pointers", "Three pointers"]
            },
            "sliding_window": {
                "when_to_use": [
                    "Subarray/substring problems",
                    "Fixed or variable window size",
                    "Maximum/minimum in windows",
                    "String pattern matching"
                ],
                "time_complexity": "O(n)",
                "space_complexity": "O(k) where k is window size",
                "variations": ["Fixed window", "Variable window", "Multiple windows"]
            },
            "fast_slow_pointers": {
                "when_to_use": [
                    "Cycle detection in linked lists",
                    "Finding middle of linked list",
                    "Detecting patterns in sequences",
                    "Happy number problems"
                ],
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "variations": ["Floyd's algorithm", "Tortoise and hare"]
            },
            "divide_and_conquer": {
                "when_to_use": [
                    "Problems that can be broken into subproblems",
                    "Sorting algorithms",
                    "Finding maximum/minimum",
                    "Closest pair problems"
                ],
                "time_complexity": "Usually O(n log n)",
                "space_complexity": "O(log n) for recursion",
                "variations": ["Binary search", "Merge sort", "Quick sort"]
            },
            "greedy": {
                "when_to_use": [
                    "Optimization problems",
                    "Activity selection",
                    "Huffman coding",
                    "Minimum spanning tree"
                ],
                "time_complexity": "Often O(n log n) due to sorting",
                "space_complexity": "Usually O(1) to O(n)",
                "note": "Works only when greedy choice leads to optimal solution"
            }
        }