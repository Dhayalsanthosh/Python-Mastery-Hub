"""
Built-in collections examples for the Data Structures module.
Covers lists, dictionaries, sets, and tuples.
"""

from typing import Dict, Any


class BuiltinExamples:
    """Built-in collections examples and demonstrations."""
    
    @staticmethod
    def get_list_operations() -> Dict[str, Any]:
        """Get comprehensive list operations examples."""
        return {
            "code": '''
# Comprehensive list operations
numbers = [1, 2, 3, 4, 5]
print(f"Original list: {numbers}")

# Adding elements
numbers.append(6)  # Add to end
numbers.insert(0, 0)  # Insert at beginning
numbers.extend([7, 8, 9])  # Add multiple elements
print(f"After additions: {numbers}")

# Removing elements
numbers.remove(5)  # Remove first occurrence of 5
popped = numbers.pop()  # Remove and return last element
del numbers[1]  # Delete by index
print(f"After removals: {numbers}, popped: {popped}")

# List slicing and manipulation
first_half = numbers[:len(numbers)//2]
second_half = numbers[len(numbers)//2:]
print(f"First half: {first_half}")
print(f"Second half: {second_half}")

# List comprehensions with conditions
squared_evens = [x**2 for x in numbers if x % 2 == 0]
print(f"Squared even numbers: {squared_evens}")

# Nested lists and flattening
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [item for row in matrix for item in row]
print(f"Matrix: {matrix}")
print(f"Flattened: {flattened}")

# List sorting and reversing
mixed_numbers = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_asc = sorted(mixed_numbers)
sorted_desc = sorted(mixed_numbers, reverse=True)
mixed_numbers.sort()  # In-place sorting
print(f"Sorted ascending: {sorted_asc}")
print(f"Sorted descending: {sorted_desc}")
print(f"Original sorted in-place: {mixed_numbers}")

# Advanced list operations
people = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "London"},
    {"name": "Charlie", "age": 35, "city": "Tokyo"}
]

# Sorting by custom key
sorted_by_age = sorted(people, key=lambda person: person["age"])
sorted_by_name = sorted(people, key=lambda person: person["name"])

print(f"Sorted by age: {[p['name'] for p in sorted_by_age]}")
print(f"Sorted by name: {[p['name'] for p in sorted_by_name]}")

# List operations with any() and all()
ages = [p["age"] for p in people]
print(f"Any age > 30? {any(age > 30 for age in ages)}")
print(f"All ages > 20? {all(age > 20 for age in ages)}")
''',
            "explanation": "Lists are mutable, ordered collections that support indexing, slicing, and comprehensive manipulation operations"
        }
    
    @staticmethod
    def get_dictionary_operations() -> Dict[str, Any]:
        """Get comprehensive dictionary operations examples."""
        return {
            "code": '''
# Comprehensive dictionary operations
student = {
    'name': 'Alice',
    'age': 21,
    'grades': [85, 92, 78, 96],
    'major': 'Computer Science'
}
print(f"Original student: {student}")

# Adding and updating items
student['gpa'] = 3.8
student.update({'year': 'Senior', 'scholarship': True})
print(f"After updates: {student}")

# Dictionary methods
print(f"Keys: {list(student.keys())}")
print(f"Values: {list(student.values())}")
print(f"Items: {list(student.items())}")

# Safe access methods
age = student.get('age', 0)
height = student.get('height', 'Unknown')
print(f"Age: {age}, Height: {height}")

# Dictionary comprehensions
grade_squared = {f"grade_{i}": grade**2 for i, grade in enumerate(student['grades'])}
print(f"Squared grades: {grade_squared}")

# Merging dictionaries
default_info = {'status': 'active', 'credits': 120}
complete_info = {**default_info, **student}
print(f"Merged info keys: {list(complete_info.keys())}")

# Nested dictionaries
course_grades = {
    'Math': {'midterm': 85, 'final': 92, 'assignments': [88, 90, 87]},
    'Physics': {'midterm': 78, 'final': 82, 'assignments': [85, 88, 83]},
    'CS': {'midterm': 95, 'final': 98, 'assignments': [92, 95, 97]}
}

# Calculate average for each course
for course, grades in course_grades.items():
    avg_assignment = sum(grades['assignments']) / len(grades['assignments'])
    course_avg = (grades['midterm'] + grades['final'] + avg_assignment) / 3
    print(f"{course} average: {course_avg:.2f}")

# Dictionary filtering and mapping
high_performers = {course: grades for course, grades in course_grades.items() 
                  if (grades['midterm'] + grades['final']) / 2 > 85}
print(f"High performing courses: {list(high_performers.keys())}")

# Advanced dictionary patterns
from collections import defaultdict

# Group students by grade level
students = [
    {'name': 'Alice', 'grade': 'A', 'year': 'Senior'},
    {'name': 'Bob', 'grade': 'B', 'year': 'Junior'},
    {'name': 'Charlie', 'grade': 'A', 'year': 'Senior'},
    {'name': 'Diana', 'grade': 'B', 'year': 'Junior'}
]

grouped_by_year = defaultdict(list)
for student in students:
    grouped_by_year[student['year']].append(student['name'])

print(f"Students by year: {dict(grouped_by_year)}")
''',
            "explanation": "Dictionaries are mutable mappings that provide fast key-based lookup and flexible data organization"
        }
    
    @staticmethod
    def get_set_operations() -> Dict[str, Any]:
        """Get comprehensive set operations examples."""
        return {
            "code": '''
# Comprehensive set operations
set_a = {1, 2, 3, 4, 5}
set_b = {4, 5, 6, 7, 8}
set_c = {1, 2, 3}

print(f"Set A: {set_a}")
print(f"Set B: {set_b}")
print(f"Set C: {set_c}")

# Set operations
union = set_a | set_b  # Union
intersection = set_a & set_b  # Intersection
difference = set_a - set_b  # Difference
symmetric_diff = set_a ^ set_b  # Symmetric difference

print(f"Union (A | B): {union}")
print(f"Intersection (A & B): {intersection}")
print(f"Difference (A - B): {difference}")
print(f"Symmetric Difference (A ^ B): {symmetric_diff}")

# Set relationships
print(f"Is C subset of A? {set_c.issubset(set_a)}")
print(f"Is A superset of C? {set_a.issuperset(set_c)}")
print(f"Are A and B disjoint? {set_a.isdisjoint(set_b)}")

# Set modifications
set_a_copy = set_a.copy()
set_a_copy.add(10)
set_a_copy.update([11, 12, 13])
set_a_copy.discard(1)  # Remove if exists, no error if not
print(f"Modified set A: {set_a_copy}")

# Practical example: finding unique elements
data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5]
unique_elements = set(data)
print(f"Original data: {data}")
print(f"Unique elements: {unique_elements}")

# Set comprehensions
squares_set = {x**2 for x in range(10) if x % 2 == 0}
print(f"Even squares set: {squares_set}")

# Removing duplicates from list while preserving order
def remove_duplicates_ordered(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

original = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
deduplicated = remove_duplicates_ordered(original)
print(f"Original with duplicates: {original}")
print(f"Deduplicated ordered: {deduplicated}")

# Set operations with strings
words_a = {"python", "java", "javascript", "go"}
words_b = {"javascript", "rust", "go", "swift"}

common_languages = words_a & words_b
unique_to_a = words_a - words_b
all_languages = words_a | words_b

print(f"Common languages: {common_languages}")
print(f"Unique to set A: {unique_to_a}")
print(f"All languages: {all_languages}")

# Performance comparison: list vs set membership
import time

large_list = list(range(10000))
large_set = set(range(10000))
search_item = 9999

# Time list membership
start = time.time()
result_list = search_item in large_list
list_time = time.time() - start

# Time set membership  
start = time.time()
result_set = search_item in large_set
set_time = time.time() - start

print(f"List membership: {list_time:.6f}s")
print(f"Set membership: {set_time:.6f}s")
print(f"Set is ~{list_time/set_time:.0f}x faster")
''',
            "explanation": "Sets are unordered collections of unique elements that provide fast membership testing and mathematical set operations"
        }