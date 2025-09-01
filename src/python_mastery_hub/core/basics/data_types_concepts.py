"""
Data Types Concepts - Numbers, strings, booleans, and collections.
"""

from typing import Dict, Any, List


class DataTypesConcepts:
    """Handles all data type-related concepts and examples."""
    
    def __init__(self):
        self.topic = "data_types"
        self.examples = self._setup_examples()
    
    def demonstrate(self) -> Dict[str, Any]:
        """Return comprehensive data type demonstrations."""
        return {
            "topic": self.topic,
            "examples": self.examples,
            "explanation": self._get_explanation(),
            "best_practices": self._get_best_practices(),
        }
    
    def _setup_examples(self) -> Dict[str, Any]:
        """Setup comprehensive data type examples."""
        return {
            "numeric_types": {
                "code": '''
# Numeric data types
integer_num = 42
float_num = 3.14159
complex_num = 3 + 4j

print(f"Integer: {integer_num} (type: {type(integer_num).__name__})")
print(f"Float: {float_num} (type: {type(float_num).__name__})")
print(f"Complex: {complex_num} (type: {type(complex_num).__name__})")

# Numeric operations
print(f"Integer division: {10 // 3}")
print(f"Float division: {10 / 3:.3f}")
print(f"Power: {2 ** 10}")
print(f"Modulo: {17 % 5}")

# Type conversion
print(f"int('42'): {int('42')}")
print(f"float('3.14'): {float('3.14')}")
print(f"str(42): '{str(42)}'")
''',
                "output": "Integer: 42 (type: int)\\nFloat: 3.14159 (type: float)\\nComplex: (3+4j) (type: complex)\\nInteger division: 3\\nFloat division: 3.333\\nPower: 1024\\nModulo: 2\\nint('42'): 42\\nfloat('3.14'): 3.14\\nstr(42): '42'",
                "explanation": "Python supports integers, floats, and complex numbers with rich operations and type conversion"
            },
            
            "string_operations": {
                "code": '''
# String data type and operations
text = "Python Mastery Hub"
multiline = \"\"\"This is a
multiline string
with multiple lines\"\"\"

# String methods
print(f"Original: '{text}'")
print(f"Upper: '{text.upper()}'")
print(f"Lower: '{text.lower()}'")
print(f"Title: '{text.title()}'")
print(f"Replace: '{text.replace('Python', 'Java')}'")
print(f"Split: {text.split()}")
print(f"Length: {len(text)}")

# String indexing and slicing
print(f"First char: '{text[0]}'")
print(f"Last char: '{text[-1]}'")
print(f"First word: '{text[:6]}'")
print(f"Last word: '{text[-3:]}'")

# String formatting
name, score = "Alice", 95.5
print(f"f-string: Student {name} scored {score:.1f}%")
print("format(): Student {} scored {:.1f}%".format(name, score))
print("%-formatting: Student %(name)s scored %(score).1f%%" % {"name": name, "score": score})
''',
                "output": "Original: 'Python Mastery Hub'\\nUpper: 'PYTHON MASTERY HUB'\\nLower: 'python mastery hub'\\nTitle: 'Python Mastery Hub'\\nReplace: 'Java Mastery Hub'\\nSplit: ['Python', 'Mastery', 'Hub']\\nLength: 18\\nFirst char: 'P'\\nLast char: 'b'\\nFirst word: 'Python'\\nLast word: 'Hub'\\nf-string: Student Alice scored 95.5%\\nformat(): Student Alice scored 95.5%\\n%-formatting: Student Alice scored 95.5%",
                "explanation": "Strings are immutable sequences with many useful methods and multiple formatting options"
            },
            
            "boolean_logic": {
                "code": '''
# Boolean data type and logic
is_active = True
is_premium = False

# Boolean operations
print(f"AND: {is_active and is_premium}")
print(f"OR: {is_active or is_premium}")
print(f"NOT: {not is_active}")
print(f"XOR: {is_active != is_premium}")

# Comparison operators
a, b = 10, 20
print(f"Equal: {a == b}")
print(f"Not equal: {a != b}")
print(f"Less than: {a < b}")
print(f"Greater or equal: {a >= b}")

# Truthy and falsy values
values = [0, 1, "", "hello", [], [1, 2], None, {}, {"key": "value"}]
print("\\nTruthiness test:")
for value in values:
    print(f"{repr(value):15} -> {bool(value)}")

# Chained comparisons
x = 15
print(f"\\nChained: 10 < {x} < 20 = {10 < x < 20}")
''',
                "output": "AND: False\\nOR: True\\nNOT: False\\nXOR: True\\nEqual: False\\nNot equal: True\\nLess than: True\\nGreater or equal: False\\n\\nTruthiness test:\\n0               -> False\\n1               -> True\\n''              -> False\\n'hello'         -> True\\n[]              -> False\\n[1, 2]          -> True\\nNone            -> False\\n{}              -> False\\n{'key': 'value'} -> True\\n\\nChained: 10 < 15 < 20 = True",
                "explanation": "Boolean logic and truthiness are fundamental to Python control flow and conditionals"
            },
            
            "list_operations": {
                "code": '''
# List - mutable, ordered collection
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]

print(f"Original list: {fruits}")

# List methods
fruits.append("date")
print(f"After append: {fruits}")

fruits.insert(1, "apricot")
print(f"After insert: {fruits}")

removed = fruits.pop()
print(f"After pop: {fruits}, removed: {removed}")

# List operations
combined = fruits + ["elderberry", "fig"]
print(f"Combined: {combined}")

print(f"Length: {len(fruits)}")
print(f"Index of 'banana': {fruits.index('banana')}")
print(f"'banana' in list: {'banana' in fruits}")

# List slicing
print(f"First two: {fruits[:2]}")
print(f"Last two: {fruits[-2:]}")
print(f"Reversed: {fruits[::-1]}")

# List comprehension
squares = [x**2 for x in numbers]
print(f"Squares: {squares}")
''',
                "output": "Original list: ['apple', 'banana', 'cherry']\\nAfter append: ['apple', 'banana', 'cherry', 'date']\\nAfter insert: ['apple', 'apricot', 'banana', 'cherry', 'date']\\nAfter pop: ['apple', 'apricot', 'banana', 'cherry'], removed: date\\nCombined: ['apple', 'apricot', 'banana', 'cherry', 'elderberry', 'fig']\\nLength: 4\\nIndex of 'banana': 2\\n'banana' in list: True\\nFirst two: ['apple', 'apricot']\\nLast two: ['banana', 'cherry']\\nReversed: ['cherry', 'banana', 'apricot', 'apple']\\nSquares: [1, 4, 9, 16, 25]",
                "explanation": "Lists are mutable, ordered collections that support many useful operations and methods"
            },
            
            "tuple_operations": {
                "code": '''
# Tuple - immutable, ordered collection
coordinates = (10, 20)
rgb_color = (255, 128, 0)
single_item_tuple = (42,)  # Note the comma

print(f"Coordinates: {coordinates}")
print(f"RGB Color: {rgb_color}")
print(f"Single tuple: {single_item_tuple}")

# Tuple unpacking
x, y = coordinates
r, g, b = rgb_color
print(f"Unpacked coordinates: x={x}, y={y}")
print(f"Unpacked color: r={r}, g={g}, b={b}")

# Tuple methods
mixed_tuple = (1, 2, 3, 2, 4, 2)
print(f"Count of 2: {mixed_tuple.count(2)}")
print(f"Index of 3: {mixed_tuple.index(3)}")

# Named tuples
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
point = Point(10, 20)
print(f"Named tuple: {point}")
print(f"Access by name: x={point.x}, y={point.y}")

# Tuple as dictionary key (immutable)
locations = {
    (0, 0): "origin",
    (1, 0): "east",
    (0, 1): "north"
}
print(f"Location map: {locations}")
''',
                "output": "Coordinates: (10, 20)\\nRGB Color: (255, 128, 0)\\nSingle tuple: (42,)\\nUnpacked coordinates: x=10, y=20\\nUnpacked color: r=255, g=128, b=0\\nCount of 2: 3\\nIndex of 3: 2\\nNamed tuple: Point(x=10, y=20)\\nAccess by name: x=10, y=20\\nLocation map: {(0, 0): 'origin', (1, 0): 'east', (0, 1): 'north'}",
                "explanation": "Tuples are immutable sequences useful for fixed collections and as dictionary keys"
            },
            
            "set_operations": {
                "code": '''
# Set - mutable, unordered collection of unique elements
fruits = {"apple", "banana", "cherry", "apple"}  # Duplicates removed
numbers = set([1, 2, 3, 4, 5, 5, 5])  # From list

print(f"Fruits set: {fruits}")
print(f"Numbers set: {numbers}")

# Set operations
fruits.add("date")
print(f"After add: {fruits}")

fruits.discard("banana")  # No error if not found
print(f"After discard: {fruits}")

# Mathematical set operations
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

print(f"Set 1: {set1}")
print(f"Set 2: {set2}")
print(f"Union: {set1 | set2}")
print(f"Intersection: {set1 & set2}")
print(f"Difference: {set1 - set2}")
print(f"Symmetric difference: {set1 ^ set2}")

# Set membership and comparisons
print(f"3 in set1: {3 in set1}")
print(f"set1 subset of {set1 | set2}: {set1.issubset(set1 | set2)}")

# Frozenset - immutable set
frozen = frozenset([1, 2, 3])
print(f"Frozenset: {frozen}")
''',
                "output": "Fruits set: {'cherry', 'banana', 'apple'}\\nNumbers set: {1, 2, 3, 4, 5}\\nAfter add: {'cherry', 'banana', 'apple', 'date'}\\nAfter discard: {'cherry', 'apple', 'date'}\\nSet 1: {1, 2, 3, 4}\\nSet 2: {3, 4, 5, 6}\\nUnion: {1, 2, 3, 4, 5, 6}\\nIntersection: {3, 4}\\nDifference: {1, 2}\\nSymmetric difference: {1, 2, 5, 6}\\n3 in set1: True\\nset1 subset of {1, 2, 3, 4, 5, 6}: True\\nFrozenset: frozenset({1, 2, 3})",
                "explanation": "Sets provide fast membership testing and mathematical set operations for unique collections"
            },
            
            "dictionary_operations": {
                "code": '''
# Dictionary - mutable, ordered (Python 3.7+) key-value mapping
student = {"name": "Alice", "age": 20, "grade": "A"}
scores = dict(math=95, science=88, english=92)

print(f"Student: {student}")
print(f"Scores: {scores}")

# Dictionary access and modification
print(f"Name: {student['name']}")
print(f"Age: {student.get('age', 'Unknown')}")
print(f"Grade: {student.get('major', 'Undeclared')}")

student["major"] = "Computer Science"
student.update({"age": 21, "gpa": 3.8})
print(f"Updated: {student}")

# Dictionary methods
print(f"Keys: {list(student.keys())}")
print(f"Values: {list(student.values())}")
print(f"Items: {list(student.items())}")

# Dictionary comprehension
squared_numbers = {x: x**2 for x in range(1, 6)}
print(f"Squared numbers: {squared_numbers}")

# Nested dictionaries
students = {
    "alice": {"age": 20, "courses": ["math", "science"]},
    "bob": {"age": 22, "courses": ["english", "history"]}
}
print(f"Alice's courses: {students['alice']['courses']}")

# Dictionary with default values
from collections import defaultdict
grade_counts = defaultdict(int)
grades = ["A", "B", "A", "C", "B", "A"]
for grade in grades:
    grade_counts[grade] += 1
print(f"Grade counts: {dict(grade_counts)}")
''',
                "output": "Student: {'name': 'Alice', 'age': 20, 'grade': 'A'}\\nScores: {'math': 95, 'science': 88, 'english': 92}\\nName: Alice\\nAge: 20\\nGrade: Undeclared\\nUpdated: {'name': 'Alice', 'age': 21, 'grade': 'A', 'major': 'Computer Science', 'gpa': 3.8}\\nKeys: ['name', 'age', 'grade', 'major', 'gpa']\\nValues: ['Alice', 21, 'A', 'Computer Science', 3.8]\\nItems: [('name', 'Alice'), ('age', 21), ('grade', 'A'), ('major', 'Computer Science'), ('gpa', 3.8)]\\nSquared numbers: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}\\nAlice's courses: ['math', 'science']\\nGrade counts: {'A': 3, 'B': 2, 'C': 1}",
                "explanation": "Dictionaries provide fast key-based lookup and are essential for structured data storage"
            }
        }
    
    def _get_explanation(self) -> str:
        """Get detailed explanation for data types."""
        return (
            "Python has several built-in data types that form the foundation of all programs. "
            "Numeric types (int, float, complex) handle mathematical operations. Strings provide "
            "text processing capabilities. Booleans enable logical operations. Collection types "
            "(list, tuple, set, dict) organize and manipulate groups of data. Understanding when "
            "to use each type and their characteristics (mutable vs immutable, ordered vs unordered) "
            "is crucial for effective Python programming."
        )
    
    def _get_best_practices(self) -> List[str]:
        """Get best practices for data types."""
        return [
            "Choose appropriate data types for your specific use case",
            "Use type hints to document expected types in function signatures",
            "Understand mutable vs immutable types to avoid unexpected behavior",
            "Prefer f-strings for string formatting in Python 3.6+",
            "Use sets for fast membership testing and eliminating duplicates",
            "Use tuples for immutable collections and as dictionary keys",
            "Use dictionaries for key-value relationships and fast lookups",
            "Use list comprehensions for simple transformations",
            "Be aware of truthiness rules for different types",
            "Use collections module for specialized data types when needed",
            "Validate input types early in functions to catch errors",
            "Use isinstance() instead of type() for type checking"
        ]