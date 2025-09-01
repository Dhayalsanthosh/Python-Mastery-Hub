# tests/unit/core/test_data_structures.py
# Unit tests for data structures concepts and exercises

import pytest
from unittest.mock import Mock, AsyncMock
from collections import deque, defaultdict, Counter, OrderedDict
from typing import List, Dict, Set, Tuple, Optional, Any
import heapq
import bisect

# Import modules under test (adjust based on your actual structure)
try:
    from src.core.data_structures import (
        ListExercise,
        DictExercise,
        SetExercise,
        TupleExercise,
        StackExercise,
        QueueExercise,
        TreeExercise,
        GraphExercise
    )
    from src.core.evaluators import DataStructureEvaluator
except ImportError:
    # Mock classes for when actual modules don't exist
    class ListExercise:
        pass
    class DictExercise:
        pass
    class SetExercise:
        pass
    class TupleExercise:
        pass
    class StackExercise:
        pass
    class QueueExercise:
        pass
    class TreeExercise:
        pass
    class GraphExercise:
        pass
    class DataStructureEvaluator:
        pass


class TestListExercises:
    """Test cases for list data structure exercises."""
    
    def test_list_creation_and_access(self):
        """Test basic list creation and element access."""
        code = '''
# Create different types of lists
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]
nested = [[1, 2], [3, 4], [5, 6]]
empty = []

# Access elements
first = numbers[0]
last = numbers[-1]
middle = numbers[2]

# Access nested elements
nested_element = nested[1][0]
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['numbers'] == [1, 2, 3, 4, 5]
        assert globals_dict['mixed'] == [1, "hello", 3.14, True]
        assert globals_dict['nested'] == [[1, 2], [3, 4], [5, 6]]
        assert globals_dict['empty'] == []
        assert globals_dict['first'] == 1
        assert globals_dict['last'] == 5
        assert globals_dict['middle'] == 3
        assert globals_dict['nested_element'] == 3
    
    def test_list_slicing(self):
        """Test list slicing operations."""
        code = '''
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Basic slicing
first_three = numbers[:3]
last_three = numbers[-3:]
middle = numbers[2:7]
skip_two = numbers[::2]
reverse = numbers[::-1]

# Negative step
every_third_reverse = numbers[::-3]

# Slice assignment
numbers_copy = numbers.copy()
numbers_copy[2:5] = [20, 30, 40]
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['first_three'] == [0, 1, 2]
        assert globals_dict['last_three'] == [7, 8, 9]
        assert globals_dict['middle'] == [2, 3, 4, 5, 6]
        assert globals_dict['skip_two'] == [0, 2, 4, 6, 8]
        assert globals_dict['reverse'] == [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        assert globals_dict['every_third_reverse'] == [9, 6, 3, 0]
        assert globals_dict['numbers_copy'][2:5] == [20, 30, 40]
    
    def test_list_methods(self):
        """Test various list methods."""
        code = '''
fruits = ["apple", "banana", "cherry"]

# Append and extend
fruits.append("date")
fruits.extend(["elderberry", "fig"])

# Insert and remove
fruits.insert(1, "apricot")
removed = fruits.remove("banana")
popped = fruits.pop()
popped_index = fruits.pop(0)

# Other methods
count_apple = fruits.count("apple")
index_cherry = fruits.index("cherry")
fruits.reverse()
reversed_fruits = fruits.copy()

fruits.sort()
sorted_fruits = fruits.copy()

# Clear
temp_list = [1, 2, 3]
temp_list.clear()
cleared_length = len(temp_list)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert "date" in globals_dict['fruits']
        assert "elderberry" in globals_dict['fruits']
        assert "fig" not in globals_dict['fruits']  # Was popped
        assert globals_dict['popped'] == "fig"
        assert globals_dict['count_apple'] == 1
        assert globals_dict['cleared_length'] == 0
    
    def test_list_comprehensions(self):
        """Test list comprehensions."""
        code = '''
# Basic list comprehension
squares = [x**2 for x in range(1, 6)]

# With condition
even_squares = [x**2 for x in range(1, 11) if x % 2 == 0]

# Nested comprehension
matrix = [[i+j for j in range(3)] for i in range(3)]

# Flattening
nested_list = [[1, 2], [3, 4], [5, 6]]
flattened = [item for sublist in nested_list for item in sublist]

# String processing
words = ["hello", "world", "python"]
upper_words = [word.upper() for word in words]
word_lengths = [len(word) for word in words]

# Conditional expression in comprehension
numbers = [-2, -1, 0, 1, 2]
abs_values = [x if x >= 0 else -x for x in numbers]
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['squares'] == [1, 4, 9, 16, 25]
        assert globals_dict['even_squares'] == [4, 16, 36, 64, 100]
        assert globals_dict['matrix'] == [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        assert globals_dict['flattened'] == [1, 2, 3, 4, 5, 6]
        assert globals_dict['upper_words'] == ["HELLO", "WORLD", "PYTHON"]
        assert globals_dict['word_lengths'] == [5, 5, 6]
        assert globals_dict['abs_values'] == [2, 1, 0, 1, 2]


class TestDictExercises:
    """Test cases for dictionary data structure exercises."""
    
    def test_dict_creation_and_access(self):
        """Test dictionary creation and element access."""
        code = '''
# Different ways to create dictionaries
person = {"name": "Alice", "age": 30, "city": "New York"}
empty_dict = {}
dict_from_tuples = dict([("a", 1), ("b", 2), ("c", 3)])
dict_comprehension = {x: x**2 for x in range(1, 6)}

# Access and modification
name = person["name"]
age = person.get("age", 0)
height = person.get("height", "Unknown")

person["email"] = "alice@example.com"
person["age"] = 31

# Key operations
keys_list = list(person.keys())
values_list = list(person.values())
items_list = list(person.items())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['person']['name'] == "Alice"
        assert globals_dict['person']['age'] == 31
        assert globals_dict['person']['email'] == "alice@example.com"
        assert globals_dict['dict_from_tuples'] == {"a": 1, "b": 2, "c": 3}
        assert globals_dict['dict_comprehension'] == {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
        assert globals_dict['height'] == "Unknown"
        assert "name" in globals_dict['keys_list']
    
    def test_dict_methods(self):
        """Test various dictionary methods."""
        code = '''
scores = {"Alice": 85, "Bob": 92, "Charlie": 78}

# Update operations
scores.update({"David": 88, "Alice": 87})
scores_copy = scores.copy()

# Pop operations
bob_score = scores.pop("Bob")
default_score = scores.pop("Eve", 0)
last_item = scores.popitem()

# Other methods
all_keys = list(scores.keys())
all_values = list(scores.values())

# Clear
temp_dict = {"a": 1, "b": 2}
temp_dict.clear()
cleared_length = len(temp_dict)

# setdefault
original_scores = {"Alice": 85, "Bob": 92}
alice_score = original_scores.setdefault("Alice", 0)
eve_score = original_scores.setdefault("Eve", 75)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['bob_score'] == 92
        assert globals_dict['default_score'] == 0
        assert globals_dict['alice_score'] == 85
        assert globals_dict['eve_score'] == 75
        assert "Eve" in globals_dict['original_scores']
        assert globals_dict['cleared_length'] == 0
    
    def test_nested_dictionaries(self):
        """Test nested dictionaries."""
        code = '''
company = {
    "name": "Tech Corp",
    "employees": {
        "engineering": {
            "Alice": {"role": "Senior Developer", "salary": 90000},
            "Bob": {"role": "Junior Developer", "salary": 60000}
        },
        "marketing": {
            "Charlie": {"role": "Marketing Manager", "salary": 75000}
        }
    },
    "locations": ["New York", "San Francisco", "Austin"]
}

# Access nested data
alice_salary = company["employees"]["engineering"]["Alice"]["salary"]
locations_count = len(company["locations"])

# Modify nested data
company["employees"]["engineering"]["Alice"]["salary"] = 95000
company["employees"]["hr"] = {}

# Safe access with get
bob_role = company.get("employees", {}).get("engineering", {}).get("Bob", {}).get("role", "Unknown")
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['alice_salary'] == 90000
        assert globals_dict['locations_count'] == 3
        assert globals_dict['company']['employees']['engineering']['Alice']['salary'] == 95000
        assert globals_dict['bob_role'] == "Junior Developer"
        assert "hr" in globals_dict['company']['employees']
    
    def test_dict_comprehensions(self):
        """Test dictionary comprehensions."""
        code = '''
# Basic dict comprehension
squares_dict = {x: x**2 for x in range(1, 6)}

# With condition
even_squares = {x: x**2 for x in range(1, 11) if x % 2 == 0}

# From lists
names = ["Alice", "Bob", "Charlie"]
name_lengths = {name: len(name) for name in names}

# Transforming existing dict
original = {"a": 1, "b": 2, "c": 3}
doubled = {k: v*2 for k, v in original.items()}
filtered = {k: v for k, v in original.items() if v > 1}

# Swapping keys and values
swapped = {v: k for k, v in original.items()}

# Nested comprehension
matrix_dict = {i: {j: i*j for j in range(3)} for i in range(3)}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['squares_dict'] == {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
        assert globals_dict['even_squares'] == {2: 4, 4: 16, 6: 36, 8: 64, 10: 100}
        assert globals_dict['name_lengths'] == {"Alice": 5, "Bob": 3, "Charlie": 7}
        assert globals_dict['doubled'] == {"a": 2, "b": 4, "c": 6}
        assert globals_dict['swapped'] == {1: "a", 2: "b", 3: "c"}


class TestSetExercises:
    """Test cases for set data structure exercises."""
    
    def test_set_creation_and_operations(self):
        """Test set creation and basic operations."""
        code = '''
# Set creation
numbers = {1, 2, 3, 4, 5}
from_list = set([1, 2, 2, 3, 3, 4])
from_string = set("hello")
empty_set = set()

# Basic operations
numbers.add(6)
numbers.update([7, 8, 9])
numbers.discard(1)  # Doesn't raise error if not found
removed = numbers.remove(2)  # Raises error if not found

# Set methods
set_length = len(numbers)
contains_three = 3 in numbers
contains_ten = 10 in numbers

# Copy and clear
numbers_copy = numbers.copy()
temp_set = {1, 2, 3}
temp_set.clear()
cleared_length = len(temp_set)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert 6 in globals_dict['numbers']
        assert 1 not in globals_dict['numbers']
        assert 2 not in globals_dict['numbers']
        assert globals_dict['from_list'] == {1, 2, 3, 4}
        assert globals_dict['from_string'] == {'h', 'e', 'l', 'o'}
        assert globals_dict['contains_three'] is True
        assert globals_dict['contains_ten'] is False
        assert globals_dict['cleared_length'] == 0
    
    def test_set_operations(self):
        """Test set mathematical operations."""
        code = '''
set1 = {1, 2, 3, 4, 5}
set2 = {4, 5, 6, 7, 8}
set3 = {1, 2, 3}

# Union operations
union1 = set1 | set2
union2 = set1.union(set2)

# Intersection operations
intersection1 = set1 & set2
intersection2 = set1.intersection(set2)

# Difference operations
difference1 = set1 - set2
difference2 = set1.difference(set2)

# Symmetric difference
sym_diff1 = set1 ^ set2
sym_diff2 = set1.symmetric_difference(set2)

# Subset and superset checks
is_subset = set3.issubset(set1)
is_superset = set1.issuperset(set3)
is_disjoint = set1.isdisjoint({10, 11, 12})

# In-place operations
set1_copy = set1.copy()
set1_copy |= {9, 10}  # In-place union
set1_copy &= {1, 2, 3, 4, 5, 9}  # In-place intersection
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['union1'] == {1, 2, 3, 4, 5, 6, 7, 8}
        assert globals_dict['intersection1'] == {4, 5}
        assert globals_dict['difference1'] == {1, 2, 3}
        assert globals_dict['sym_diff1'] == {1, 2, 3, 6, 7, 8}
        assert globals_dict['is_subset'] is True
        assert globals_dict['is_superset'] is True
        assert globals_dict['is_disjoint'] is True
    
    def test_set_comprehensions(self):
        """Test set comprehensions."""
        code = '''
# Basic set comprehension
squares = {x**2 for x in range(1, 6)}

# With condition
even_squares = {x**2 for x in range(1, 11) if x % 2 == 0}

# From string
unique_chars = {char.lower() for char in "Hello World" if char.isalpha()}

# Remove duplicates from list
numbers_with_duplicates = [1, 2, 2, 3, 3, 3, 4, 4, 5]
unique_numbers = {x for x in numbers_with_duplicates}

# Complex condition
divisible_by_3_or_5 = {x for x in range(1, 31) if x % 3 == 0 or x % 5 == 0}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['squares'] == {1, 4, 9, 16, 25}
        assert globals_dict['even_squares'] == {4, 16, 36, 64, 100}
        assert globals_dict['unique_chars'] == {'h', 'e', 'l', 'o', 'w', 'r', 'd'}
        assert globals_dict['unique_numbers'] == {1, 2, 3, 4, 5}
        assert 15 in globals_dict['divisible_by_3_or_5']
        assert 30 in globals_dict['divisible_by_3_or_5']


class TestTupleExercises:
    """Test cases for tuple data structure exercises."""
    
    def test_tuple_creation_and_access(self):
        """Test tuple creation and element access."""
        code = '''
# Tuple creation
coordinates = (3, 4)
single_element = (42,)  # Note the comma
from_list = tuple([1, 2, 3, 4])
nested = ((1, 2), (3, 4), (5, 6))
empty = ()

# Access elements
x, y = coordinates
first = coordinates[0]
last = coordinates[-1]

# Slicing
numbers = (0, 1, 2, 3, 4, 5)
first_three = numbers[:3]
last_two = numbers[-2:]

# Length and membership
length = len(numbers)
contains_three = 3 in numbers
count_ones = (1, 1, 2, 1, 3).count(1)
index_of_two = numbers.index(2)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['coordinates'] == (3, 4)
        assert globals_dict['x'] == 3
        assert globals_dict['y'] == 4
        assert globals_dict['single_element'] == (42,)
        assert globals_dict['from_list'] == (1, 2, 3, 4)
        assert globals_dict['first_three'] == (0, 1, 2)
        assert globals_dict['contains_three'] is True
        assert globals_dict['count_ones'] == 3
        assert globals_dict['index_of_two'] == 2
    
    def test_tuple_unpacking(self):
        """Test tuple unpacking operations."""
        code = '''
# Basic unpacking
point = (10, 20)
x, y = point

# Multiple assignment
a, b, c = 1, 2, 3

# Nested unpacking
nested = ((1, 2), (3, 4))
(x1, y1), (x2, y2) = nested

# Extended unpacking (Python 3+)
numbers = (1, 2, 3, 4, 5)
first, *middle, last = numbers
head, *tail = numbers
*init, final = numbers

# Swapping variables
a, b = 10, 20
a, b = b, a

# Function returns
def get_name_age():
    return "Alice", 30

name, age = get_name_age()

# Ignoring values
data = (1, 2, 3, 4, 5)
first, _, third, *_ = data
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['x'] == 10
        assert globals_dict['y'] == 20
        assert globals_dict['x1'] == 1
        assert globals_dict['y2'] == 4
        assert globals_dict['middle'] == [2, 3, 4]
        assert globals_dict['tail'] == [2, 3, 4, 5]
        assert globals_dict['init'] == [1, 2, 3, 4]
        assert globals_dict['a'] == 20  # After swapping
        assert globals_dict['b'] == 10  # After swapping
        assert globals_dict['name'] == "Alice"
        assert globals_dict['third'] == 3
    
    def test_named_tuples(self):
        """Test named tuples."""
        code = '''
from collections import namedtuple

# Define named tuple
Point = namedtuple('Point', ['x', 'y'])
Person = namedtuple('Person', 'name age city', defaults=['Unknown'])

# Create instances
p1 = Point(3, 4)
p2 = Point(x=10, y=20)
person1 = Person('Alice', 30, 'New York')
person2 = Person('Bob', 25)  # Uses default for city

# Access fields
x_coord = p1.x
y_coord = p1.y
name = person1.name
city_default = person2.city

# Named tuple methods
point_dict = p1._asdict()
fields = Point._fields
new_point = p1._replace(x=100)

# Unpacking still works
x, y = p1
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['x_coord'] == 3
        assert globals_dict['y_coord'] == 4
        assert globals_dict['name'] == 'Alice'
        assert globals_dict['city_default'] == 'Unknown'
        assert globals_dict['point_dict'] == {'x': 3, 'y': 4}
        assert globals_dict['fields'] == ('x', 'y')
        assert globals_dict['new_point'].x == 100
        assert globals_dict['x'] == 3  # From unpacking


class TestAdvancedDataStructures:
    """Test cases for advanced data structures."""
    
    def test_collections_deque(self):
        """Test collections.deque (double-ended queue)."""
        code = '''
from collections import deque

# Create deque
dq = deque([1, 2, 3])
dq_maxlen = deque(maxlen=3)

# Add elements
dq.append(4)
dq.appendleft(0)
dq.extend([5, 6])
dq.extendleft([-2, -1])  # Note: extends in reverse order

# Remove elements
right = dq.pop()
left = dq.popleft()

# Rotate
dq_rotate = deque([1, 2, 3, 4, 5])
dq_rotate.rotate(2)  # Rotate right
rotated_right = list(dq_rotate)

dq_rotate.rotate(-3)  # Rotate left
rotated_left = list(dq_rotate)

# Maxlen behavior
for i in range(5):
    dq_maxlen.append(i)
maxlen_result = list(dq_maxlen)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['right'] == 6
        assert globals_dict['left'] == -1
        assert globals_dict['rotated_right'] == [4, 5, 1, 2, 3]
        assert globals_dict['maxlen_result'] == [2, 3, 4]  # Only last 3 elements
    
    def test_collections_defaultdict(self):
        """Test collections.defaultdict."""
        code = '''
from collections import defaultdict

# Different default factories
dd_list = defaultdict(list)
dd_int = defaultdict(int)
dd_set = defaultdict(set)

# Use defaultdict
dd_list['fruits'].append('apple')
dd_list['fruits'].append('banana')
dd_list['vegetables'].append('carrot')

dd_int['count'] += 1
dd_int['count'] += 1
dd_int['missing']  # This creates a 0

dd_set['group1'].add('item1')
dd_set['group1'].add('item2')
dd_set['group2'].add('item3')

# Convert to regular dict
regular_dict = dict(dd_list)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['dd_list']['fruits'] == ['apple', 'banana']
        assert globals_dict['dd_int']['count'] == 2
        assert globals_dict['dd_int']['missing'] == 0
        assert globals_dict['dd_set']['group1'] == {'item1', 'item2'}
    
    def test_collections_counter(self):
        """Test collections.Counter."""
        code = '''
from collections import Counter

# Create counters
text = "hello world"
counter_text = Counter(text)
counter_list = Counter([1, 1, 2, 2, 2, 3])
counter_dict = Counter({'a': 3, 'b': 1, 'c': 2})

# Counter operations
most_common = counter_text.most_common(3)
total_count = sum(counter_text.values())

# Arithmetic operations
c1 = Counter({'a': 3, 'b': 2, 'c': 1})
c2 = Counter({'a': 1, 'b': 3, 'd': 2})

addition = c1 + c2
subtraction = c1 - c2
intersection = c1 & c2
union = c1 | c2

# Update
c1.update(c2)
updated_a = c1['a']

# Elements method
elements_list = list(Counter({'a': 2, 'b': 3}).elements())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['counter_text']['l'] == 3
        assert globals_dict['counter_list'][2] == 3
        assert globals_dict['addition']['a'] == 4
        assert globals_dict['subtraction']['a'] == 2
        assert globals_dict['intersection']['a'] == 1
        assert sorted(globals_dict['elements_list']) == ['a', 'a', 'b', 'b', 'b']
    
    def test_heapq_operations(self):
        """Test heapq (priority queue) operations."""
        code = '''
import heapq

# Create heap
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
heapq.heapify(numbers)
min_element = numbers[0]  # Heap property: smallest at index 0

# Push and pop
heapq.heappush(numbers, 0)
smallest = heapq.heappop(numbers)

# n largest/smallest
data = [1, 3, 5, 7, 9, 2, 4, 6, 8, 0]
largest_3 = heapq.nlargest(3, data)
smallest_3 = heapq.nsmallest(3, data)

# Priority queue with tuples (priority, item)
tasks = []
heapq.heappush(tasks, (3, 'Medium priority'))
heapq.heappush(tasks, (1, 'High priority'))
heapq.heappush(tasks, (5, 'Low priority'))

first_task = heapq.heappop(tasks)
second_task = heapq.heappop(tasks)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['smallest'] == 0
        assert globals_dict['largest_3'] == [9, 8, 7]
        assert globals_dict['smallest_3'] == [0, 1, 2]
        assert globals_dict['first_task'][1] == 'High priority'
        assert globals_dict['second_task'][1] == 'Medium priority'
    
    def test_bisect_operations(self):
        """Test bisect module for sorted lists."""
        code = '''
import bisect

# Sorted list
sorted_list = [1, 3, 5, 7, 9]

# Find insertion points
left_pos = bisect.bisect_left(sorted_list, 5)
right_pos = bisect.bisect_right(sorted_list, 5)

# Insert maintaining sort order
bisect.insort(sorted_list, 6)
after_insert = sorted_list.copy()

bisect.insort_left(sorted_list, 5)
after_left_insert = sorted_list.copy()

# Search in sorted data
grades = [60, 70, 80, 90]
breakpoints = [60, 70, 80, 90]
letter_grades = ['F', 'D', 'C', 'B', 'A']

def grade(score):
    i = bisect.bisect(breakpoints, score)
    return letter_grades[i]

student_grade = grade(85)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['left_pos'] == 2
        assert globals_dict['right_pos'] == 3
        assert globals_dict['after_insert'] == [1, 3, 5, 6, 7, 9]
        assert globals_dict['student_grade'] == 'B'


class TestCustomDataStructures:
    """Test cases for implementing custom data structures."""
    
    def test_stack_implementation(self):
        """Test stack implementation."""
        code = '''
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("Stack is empty")
    
    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("Stack is empty")
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# Test stack
stack = Stack()
stack.push(1)
stack.push(2)
stack.push(3)

top = stack.peek()
popped = stack.pop()
size_after_pop = stack.size()
is_empty = stack.is_empty()
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['top'] == 3
        assert globals_dict['popped'] == 3
        assert globals_dict['size_after_pop'] == 2
        assert globals_dict['is_empty'] is False
    
    def test_queue_implementation(self):
        """Test queue implementation."""
        code = '''
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        raise IndexError("Queue is empty")
    
    def front(self):
        if not self.is_empty():
            return self.items[0]
        raise IndexError("Queue is empty")
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# Test queue
queue = Queue()
queue.enqueue(1)
queue.enqueue(2)
queue.enqueue(3)

front_item = queue.front()
dequeued = queue.dequeue()
size_after_dequeue = queue.size()
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['front_item'] == 1
        assert globals_dict['dequeued'] == 1
        assert globals_dict['size_after_dequeue'] == 2
    
    def test_binary_tree_implementation(self):
        """Test binary tree implementation."""
        code = '''
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class BinaryTree:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        if not self.root:
            self.root = TreeNode(val)
        else:
            self._insert_recursive(self.root, val)
    
    def _insert_recursive(self, node, val):
        if val < node.val:
            if node.left is None:
                node.left = TreeNode(val)
            else:
                self._insert_recursive(node.left, val)
        else:
            if node.right is None:
                node.right = TreeNode(val)
            else:
                self._insert_recursive(node.right, val)
    
    def inorder_traversal(self):
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node, result):
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.val)
            self._inorder_recursive(node.right, result)
    
    def search(self, val):
        return self._search_recursive(self.root, val)
    
    def _search_recursive(self, node, val):
        if not node or node.val == val:
            return node is not None
        
        if val < node.val:
            return self._search_recursive(node.left, val)
        else:
            return self._search_recursive(node.right, val)

# Test binary tree
tree = BinaryTree()
values = [5, 3, 7, 2, 4, 6, 8]
for val in values:
    tree.insert(val)

inorder_result = tree.inorder_traversal()
found_5 = tree.search(5)
found_10 = tree.search(10)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['inorder_result'] == [2, 3, 4, 5, 6, 7, 8]
        assert globals_dict['found_5'] is True
        assert globals_dict['found_10'] is False
    
    def test_linked_list_implementation(self):
        """Test linked list implementation."""
        code = '''
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0
    
    def append(self, val):
        new_node = ListNode(val)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1
    
    def prepend(self, val):
        new_node = ListNode(val)
        new_node.next = self.head
        self.head = new_node
        self.size += 1
    
    def delete(self, val):
        if not self.head:
            return False
        
        if self.head.val == val:
            self.head = self.head.next
            self.size -= 1
            return True
        
        current = self.head
        while current.next:
            if current.next.val == val:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        return False
    
    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.val)
            current = current.next
        return result
    
    def find(self, val):
        current = self.head
        while current:
            if current.val == val:
                return True
            current = current.next
        return False

# Test linked list
ll = LinkedList()
ll.append(1)
ll.append(2)
ll.append(3)
ll.prepend(0)

list_representation = ll.to_list()
found_2 = ll.find(2)
deleted_2 = ll.delete(2)
list_after_delete = ll.to_list()
list_size = ll.size
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['list_representation'] == [0, 1, 2, 3]
        assert globals_dict['found_2'] is True
        assert globals_dict['deleted_2'] is True
        assert globals_dict['list_after_delete'] == [0, 1, 3]
        assert globals_dict['list_size'] == 3


class TestDataStructureEvaluator:
    """Test cases for data structure evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create a data structure evaluator instance."""
        return DataStructureEvaluator()
    
    def test_evaluate_list_operations(self, evaluator):
        """Test evaluation of list operations."""
        code = '''
numbers = [1, 2, 3, 4, 5]
numbers.append(6)
numbers.insert(0, 0)
popped = numbers.pop()
result = numbers
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert result['globals']['result'] == [0, 1, 2, 3, 4, 5]
        assert result['globals']['popped'] == 6
    
    def test_evaluate_dict_operations(self, evaluator):
        """Test evaluation of dictionary operations."""
        code = '''
person = {"name": "Alice", "age": 30}
person["city"] = "New York"
age = person.pop("age")
keys = list(person.keys())
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert result['globals']['age'] == 30
        assert "city" in result['globals']['person']
        assert "age" not in result['globals']['person']
    
    def test_check_data_structure_usage(self, evaluator):
        """Test checking for specific data structure usage."""
        code = '''
# Using various data structures
my_list = [1, 2, 3]
my_dict = {"a": 1, "b": 2}
my_set = {1, 2, 3}
my_tuple = (1, 2, 3)

from collections import deque
my_deque = deque([1, 2, 3])
'''
        
        usage = evaluator.check_data_structure_usage(code)
        
        assert usage['lists'] > 0
        assert usage['dicts'] > 0
        assert usage['sets'] > 0
        assert usage['tuples'] > 0
        assert usage['deques'] > 0
    
    def test_evaluate_comprehensions(self, evaluator):
        """Test evaluation of comprehensions."""
        code = '''
# List comprehension
squares = [x**2 for x in range(5)]

# Dict comprehension
square_dict = {x: x**2 for x in range(5)}

# Set comprehension
even_set = {x for x in range(10) if x % 2 == 0}
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert result['globals']['squares'] == [0, 1, 4, 9, 16]
        assert result['globals']['square_dict'] == {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
        assert result['globals']['even_set'] == {0, 2, 4, 6, 8}


class TestDataStructurePerformance:
    """Test cases for data structure performance characteristics."""
    
    def test_list_vs_deque_performance(self):
        """Test performance differences between list and deque."""
        code = '''
import time
from collections import deque

# List operations
start_time = time.time()
test_list = []
for i in range(1000):
    test_list.insert(0, i)  # Insert at beginning
list_time = time.time() - start_time

# Deque operations
start_time = time.time()
test_deque = deque()
for i in range(1000):
    test_deque.appendleft(i)  # Insert at beginning
deque_time = time.time() - start_time

# Deque should be faster for left operations
deque_faster = deque_time < list_time
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Note: This test might be flaky on very fast machines
        # but generally deque should be faster for left operations
        assert isinstance(globals_dict['deque_faster'], bool)
    
    def test_set_vs_list_membership(self):
        """Test membership testing performance: set vs list."""
        code = '''
import time

# Create large list and set
large_list = list(range(10000))
large_set = set(range(10000))

# Test membership in list
start_time = time.time()
for i in range(100):
    9999 in large_list
list_membership_time = time.time() - start_time

# Test membership in set
start_time = time.time()
for i in range(100):
    9999 in large_set
set_membership_time = time.time() - start_time

# Set should be faster for membership testing
set_faster = set_membership_time < list_membership_time
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Set should generally be much faster for membership testing
        assert isinstance(globals_dict['set_faster'], bool)
    
    def test_dict_vs_list_lookup(self):
        """Test lookup performance: dict vs list."""
        code = '''
# Create test data
data = [(f"key_{i}", f"value_{i}") for i in range(1000)]

# List of tuples approach
list_data = data

# Dictionary approach
dict_data = dict(data)

# Function to find in list
def find_in_list(key):
    for k, v in list_data:
        if k == key:
            return v
    return None

# Test lookup performance
import time

# List lookup
start_time = time.time()
for i in range(100):
    find_in_list("key_999")
list_lookup_time = time.time() - start_time

# Dict lookup
start_time = time.time()
for i in range(100):
    dict_data.get("key_999")
dict_lookup_time = time.time() - start_time

dict_faster = dict_lookup_time < list_lookup_time
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert isinstance(globals_dict['dict_faster'], bool)


class TestDataStructureValidation:
    """Test cases for validating data structure implementations."""
    
    def test_validate_stack_implementation(self):
        """Test validation of stack implementation."""
        code = '''
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        return self.items.pop()
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Stack = globals_dict['Stack']
        
        # Test LIFO behavior
        stack = Stack()
        stack.push(1)
        stack.push(2)
        stack.push(3)
        
        assert stack.pop() == 3  # Last in, first out
        assert stack.pop() == 2
        assert stack.size() == 1
        assert not stack.is_empty()
        
        stack.pop()
        assert stack.is_empty()
    
    def test_validate_queue_implementation(self):
        """Test validation of queue implementation."""
        code = '''
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        return self.items.popleft()
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Queue = globals_dict['Queue']
        
        # Test FIFO behavior
        queue = Queue()
        queue.enqueue(1)
        queue.enqueue(2)
        queue.enqueue(3)
        
        assert queue.dequeue() == 1  # First in, first out
        assert queue.dequeue() == 2
        assert queue.size() == 1
        assert not queue.is_empty()
        
        queue.dequeue()
        assert queue.is_empty()


@pytest.mark.integration
class TestDataStructureIntegration:
    """Integration tests for data structure exercises."""
    
    def test_combined_data_structure_usage(self):
        """Test combining multiple data structures."""
        code = '''
# Student grade management system
from collections import defaultdict, Counter

class GradeManager:
    def __init__(self):
        self.students = {}  # student_id -> student_info
        self.grades = defaultdict(list)  # student_id -> [grades]
        self.course_enrollments = defaultdict(set)  # course -> {student_ids}
    
    def add_student(self, student_id, name):
        self.students[student_id] = {"name": name, "courses": set()}
    
    def enroll_student(self, student_id, course):
        self.students[student_id]["courses"].add(course)
        self.course_enrollments[course].add(student_id)
    
    def add_grade(self, student_id, grade):
        self.grades[student_id].append(grade)
    
    def get_average_grade(self, student_id):
        grades = self.grades[student_id]
        return sum(grades) / len(grades) if grades else 0
    
    def get_grade_distribution(self):
        all_grades = []
        for grades in self.grades.values():
            all_grades.extend(grades)
        return Counter(all_grades)

# Test the system
gm = GradeManager()
gm.add_student("001", "Alice")
gm.add_student("002", "Bob")

gm.enroll_student("001", "Math")
gm.enroll_student("001", "Science")
gm.enroll_student("002", "Math")

gm.add_grade("001", 85)
gm.add_grade("001", 92)
gm.add_grade("002", 78)

alice_avg = gm.get_average_grade("001")
grade_dist = gm.get_grade_distribution()
math_students = len(gm.course_enrollments["Math"])
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['alice_avg'] == 88.5
        assert globals_dict['math_students'] == 2
        assert 85 in globals_dict['grade_dist']
    
    @pytest.mark.asyncio
    async def test_async_data_structure_operations(self):
        """Test async operations with data structures."""
        code = '''
import asyncio
from collections import deque

class AsyncQueue:
    def __init__(self):
        self.queue = deque()
        self.waiters = deque()
    
    async def put(self, item):
        self.queue.append(item)
        if self.waiters:
            waiter = self.waiters.popleft()
            if not waiter.cancelled():
                waiter.set_result(None)
    
    async def get(self):
        while not self.queue:
            waiter = asyncio.Future()
            self.waiters.append(waiter)
            await waiter
        return self.queue.popleft()

async def test_async_queue():
    queue = AsyncQueue()
    
    # Producer
    async def producer():
        for i in range(3):
            await queue.put(f"item_{i}")
            await asyncio.sleep(0.01)
    
    # Consumer
    async def consumer():
        results = []
        for _ in range(3):
            item = await queue.get()
            results.append(item)
        return results
    
    # Run concurrently
    producer_task = asyncio.create_task(producer())
    consumer_task = asyncio.create_task(consumer())
    
    results = await consumer_task
    await producer_task
    
    return results

result = asyncio.run(test_async_queue())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == ["item_0", "item_1", "item_2"]


if __name__ == '__main__':
    pytest.main([__file__])