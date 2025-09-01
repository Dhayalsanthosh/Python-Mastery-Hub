"""
Control Flow Concepts - Conditionals, loops, and comprehensions.
"""

from typing import Dict, Any, List


class ControlFlowConcepts:
    """Handles all control flow-related concepts and examples."""
    
    def __init__(self):
        self.topic = "control_flow"
        self.examples = self._setup_examples()
    
    def demonstrate(self) -> Dict[str, Any]:
        """Return comprehensive control flow demonstrations."""
        return {
            "topic": self.topic,
            "examples": self.examples,
            "explanation": self._get_explanation(),
            "best_practices": self._get_best_practices(),
        }
    
    def _setup_examples(self) -> Dict[str, Any]:
        """Setup comprehensive control flow examples."""
        return {
            "conditional_statements": {
                "code": '''
# Conditional statements
def grade_calculator(score):
    """Calculate letter grade based on numeric score."""
    if score >= 90:
        grade = "A"
        message = "Excellent!"
    elif score >= 80:
        grade = "B" 
        message = "Good job!"
    elif score >= 70:
        grade = "C"
        message = "Satisfactory"
    elif score >= 60:
        grade = "D"
        message = "Needs improvement"
    else:
        grade = "F"
        message = "Failed"
    
    return f"Score: {score}, Grade: {grade}, {message}"

# Test different scores
scores = [95, 85, 75, 65, 55]
for score in scores:
    print(grade_calculator(score))

# Ternary operator (conditional expression)
age = 18
status = "adult" if age >= 18 else "minor"
print(f"Age {age} is classified as: {status}")

# Multiple conditions
weather = "sunny"
temperature = 75
activity = "beach" if weather == "sunny" and temperature > 70 else "indoor activities"
print(f"Weather: {weather}, Temp: {temperature}°F -> Suggestion: {activity}")
''',
                "output": "Score: 95, Grade: A, Excellent!\\nScore: 85, Grade: B, Good job!\\nScore: 75, Grade: C, Satisfactory\\nScore: 65, Grade: D, Needs improvement\\nScore: 55, Grade: F, Failed\\nAge 18 is classified as: adult\\nWeather: sunny, Temp: 75°F -> Suggestion: beach",
                "explanation": "Conditional statements control program flow based on boolean conditions using if/elif/else"
            },
            
            "for_loops": {
                "code": '''
# For loops - iteration over sequences
print("=== Basic For Loop ===")
fruits = ["apple", "banana", "cherry", "date"]
for fruit in fruits:
    print(f"I like {fruit}")

print("\\n=== For Loop with Range ===")
for i in range(5):
    print(f"Iteration {i}")

print("\\n=== For Loop with Enumerate ===")
for index, fruit in enumerate(fruits, start=1):
    print(f"{index}. {fruit.capitalize()}")

print("\\n=== For Loop with Zip ===")
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")

print("\\n=== Nested For Loops ===")
for i in range(3):
    for j in range(3):
        print(f"({i},{j})", end=" ")
    print()  # New line after each row

print("\\n=== For Loop with Dictionary ===")
student_grades = {"Alice": 95, "Bob": 87, "Charlie": 92}
for name, grade in student_grades.items():
    print(f"{name}: {grade}%")
''',
                "output": "=== Basic For Loop ===\\nI like apple\\nI like banana\\nI like cherry\\nI like date\\n\\n=== For Loop with Range ===\\nIteration 0\\nIteration 1\\nIteration 2\\nIteration 3\\nIteration 4\\n\\n=== For Loop with Enumerate ===\\n1. Apple\\n2. Banana\\n3. Cherry\\n4. Date\\n\\n=== For Loop with Zip ===\\nAlice is 25 years old\\nBob is 30 years old\\nCharlie is 35 years old\\n\\n=== Nested For Loops ===\\n(0,0) (0,1) (0,2) \\n(1,0) (1,1) (1,2) \\n(2,0) (2,1) (2,2) \\n\\n=== For Loop with Dictionary ===\\nAlice: 95%\\nBob: 87%\\nCharlie: 92%",
                "explanation": "For loops iterate over sequences using various patterns for different data structures"
            },
            
            "while_loops": {
                "code": '''
# While loops - conditional repetition
print("=== Basic While Loop ===")
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1

print("\\n=== While Loop with User Input Simulation ===")
# Simulating user input for demonstration
attempts = 0
max_attempts = 3
correct_password = "secret123"
user_inputs = ["wrong1", "wrong2", "secret123"]  # Simulated inputs

while attempts < max_attempts:
    password = user_inputs[attempts]  # Simulated input
    print(f"Attempt {attempts + 1}: Enter password: {password}")
    
    if password == correct_password:
        print("Access granted!")
        break
    else:
        attempts += 1
        remaining = max_attempts - attempts
        if remaining > 0:
            print(f"Incorrect password. {remaining} attempts remaining.")
        else:
            print("Access denied. Maximum attempts exceeded.")

print("\\n=== While Loop with Accumulator ===")
total = 0
number = 1
while total < 100:
    total += number
    print(f"Added {number}, total now: {total}")
    number += 1

print("\\n=== Infinite Loop Prevention ===")
safety_counter = 0
while True:
    safety_counter += 1
    print(f"Iteration {safety_counter}")
    
    if safety_counter >= 5:  # Safety break
        print("Breaking to prevent infinite loop")
        break
''',
                "output": "=== Basic While Loop ===\\nCount: 0\\nCount: 1\\nCount: 2\\nCount: 3\\nCount: 4\\n\\n=== While Loop with User Input Simulation ===\\nAttempt 1: Enter password: wrong1\\nIncorrect password. 2 attempts remaining.\\nAttempt 2: Enter password: wrong2\\nIncorrect password. 1 attempts remaining.\\nAttempt 3: Enter password: secret123\\nAccess granted!\\n\\n=== While Loop with Accumulator ===\\nAdded 1, total now: 1\\nAdded 2, total now: 3\\nAdded 3, total now: 6\\n...\\nAdded 14, total now: 105\\n\\n=== Infinite Loop Prevention ===\\nIteration 1\\nIteration 2\\nIteration 3\\nIteration 4\\nIteration 5\\nBreaking to prevent infinite loop",
                "explanation": "While loops repeat based on conditions and require careful handling to avoid infinite loops"
            },
            
            "loop_control": {
                "code": '''
# Loop control with break, continue, and else
print("=== Break and Continue ===")
for num in range(15):
    if num % 2 == 0:
        continue  # Skip even numbers
    if num > 10:
        break     # Stop when greater than 10
    print(f"Odd number: {num}")

print("\\n=== Loop with Else Clause ===")
def find_divisor(number, potential_divisors):
    """Demonstrate for...else construct."""
    for divisor in potential_divisors:
        if number % divisor == 0:
            print(f"{number} is divisible by {divisor}")
            break
    else:
        print(f"{number} is not divisible by any of {potential_divisors}")

find_divisor(15, [2, 3, 4])  # Found divisor
find_divisor(17, [2, 3, 4])  # No divisor found

print("\\n=== Nested Loop Control ===")
# Find first pair that sums to 10
target_sum = 10
numbers = [1, 3, 5, 7, 9, 2, 4, 6, 8]
found = False

for i, num1 in enumerate(numbers):
    for j, num2 in enumerate(numbers[i+1:], start=i+1):
        if num1 + num2 == target_sum:
            print(f"Found pair: {num1} + {num2} = {target_sum} at indices {i}, {j}")
            found = True
            break
    if found:
        break
else:
    print(f"No pair found that sums to {target_sum}")

print("\\n=== Pass Statement ===")
for i in range(5):
    if i == 2:
        pass  # Placeholder - do nothing
    else:
        print(f"Processing item {i}")
''',
                "output": "=== Break and Continue ===\\nOdd number: 1\\nOdd number: 3\\nOdd number: 5\\nOdd number: 7\\nOdd number: 9\\n\\n=== Loop with Else Clause ===\\n15 is divisible by 3\\n17 is not divisible by any of [2, 3, 4]\\n\\n=== Nested Loop Control ===\\nFound pair: 1 + 9 = 10 at indices 0, 4\\n\\n=== Pass Statement ===\\nProcessing item 0\\nProcessing item 1\\nProcessing item 3\\nProcessing item 4",
                "explanation": "Loop control statements provide fine-grained control over iteration flow"
            },
            
            "comprehensions": {
                "code": '''
# List, set, and dictionary comprehensions
numbers = range(10)
words = ["hello", "world", "python", "programming"]

print("=== List Comprehensions ===")
# Basic list comprehension
squares = [x**2 for x in numbers]
print(f"Squares: {squares}")

# List comprehension with condition
even_squares = [x**2 for x in numbers if x % 2 == 0]
print(f"Even squares: {even_squares}")

# List comprehension with transformation
upper_words = [word.upper() for word in words]
print(f"Uppercase words: {upper_words}")

# Nested list comprehension
matrix = [[i*j for j in range(1, 4)] for i in range(1, 4)]
print(f"Multiplication matrix: {matrix}")

print("\\n=== Set Comprehensions ===")
# Set comprehension removes duplicates
remainders = {x % 3 for x in range(15)}
print(f"Unique remainders (mod 3): {remainders}")

# Set comprehension with condition
vowels_in_words = {char for word in words for char in word.lower() if char in 'aeiou'}
print(f"Vowels found: {vowels_in_words}")

print("\\n=== Dictionary Comprehensions ===")
# Dictionary comprehension
word_lengths = {word: len(word) for word in words}
print(f"Word lengths: {word_lengths}")

# Dictionary comprehension with condition
long_words = {word: len(word) for word in words if len(word) > 5}
print(f"Long words: {long_words}")

# Dictionary from two lists
letters = ['a', 'b', 'c', 'd']
letter_numbers = {letter: i for i, letter in enumerate(letters, 1)}
print(f"Letter numbers: {letter_numbers}")

print("\\n=== Generator Expressions ===")
# Generator expression (lazy evaluation)
squares_gen = (x**2 for x in range(5))
print(f"Generator: {squares_gen}")
print(f"Generator values: {list(squares_gen)}")

# Memory efficient for large datasets
large_sum = sum(x**2 for x in range(1000))
print(f"Sum of squares 0-999: {large_sum}")
''',
                "output": "=== List Comprehensions ===\\nSquares: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]\\nEven squares: [0, 4, 16, 36, 64]\\nUppercase words: ['HELLO', 'WORLD', 'PYTHON', 'PROGRAMMING']\\nMultiplication matrix: [[1, 2, 3], [2, 4, 6], [3, 6, 9]]\\n\\n=== Set Comprehensions ===\\nUnique remainders (mod 3): {0, 1, 2}\\nVowels found: {'e', 'o', 'a', 'i'}\\n\\n=== Dictionary Comprehensions ===\\nWord lengths: {'hello': 5, 'world': 5, 'python': 6, 'programming': 11}\\nLong words: {'python': 6, 'programming': 11}\\nLetter numbers: {'a': 1, 'b': 2, 'c': 3, 'd': 4}\\n\\n=== Generator Expressions ===\\nGenerator: <generator object>\\nGenerator values: [0, 1, 4, 9, 16]\\nSum of squares 0-999: 332833500",
                "explanation": "Comprehensions provide concise, readable ways to create collections with optional filtering and transformation"
            },
            
            "match_statements": {
                "code": '''
# Match statements (Python 3.10+) - structural pattern matching
def process_data(data):
    """Demonstrate match statement patterns."""
    match data:
        case int() if data > 0:
            return f"Positive integer: {data}"
        case int() if data < 0:
            return f"Negative integer: {data}"
        case 0:
            return "Zero"
        case str() if len(data) > 0:
            return f"Non-empty string: '{data}'"
        case []:
            return "Empty list"
        case [x] if isinstance(x, int):
            return f"Single integer list: [{x}]"
        case [x, y]:
            return f"Two-item list: [{x}, {y}]"
        case [first, *rest]:
            return f"List starting with {first}, rest: {rest}"
        case {"name": name, "age": age}:
            return f"Person: {name}, age {age}"
        case {"type": "error", "message": msg}:
            return f"Error occurred: {msg}"
        case _:  # Default case
            return f"Unknown data type: {type(data).__name__}"

# Test different patterns
test_cases = [
    42,
    -5,
    0,
    "hello",
    "",
    [],
    [10],
    [1, 2],
    [1, 2, 3, 4],
    {"name": "Alice", "age": 25},
    {"type": "error", "message": "File not found"},
    {"unknown": "data"},
    3.14
]

print("=== Match Statement Examples ===")
for case in test_cases:
    result = process_data(case)
    print(f"Input: {case!r:20} -> {result}")

# Match with classes
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

def analyze_point(point):
    """Analyze point using match statement."""
    match point:
        case Point(0, 0):
            return "Origin point"
        case Point(0, y):
            return f"Point on Y-axis at y={y}"
        case Point(x, 0):
            return f"Point on X-axis at x={x}"
        case Point(x, y) if x == y:
            return f"Point on diagonal at ({x}, {y})"
        case Point(x, y):
            return f"Point in quadrant at ({x}, {y})"
        case _:
            return "Not a point"

print("\\n=== Class Pattern Matching ===")
points = [Point(0, 0), Point(0, 5), Point(3, 0), Point(4, 4), Point(2, 7)]
for point in points:
    print(f"{point} -> {analyze_point(point)}")
''',
                "output": "=== Match Statement Examples ===\\nInput: 42                   -> Positive integer: 42\\nInput: -5                   -> Negative integer: -5\\nInput: 0                    -> Zero\\nInput: 'hello'              -> Non-empty string: 'hello'\\nInput: ''                   -> Unknown data type: str\\nInput: []                   -> Empty list\\nInput: [10]                 -> Single integer list: [10]\\nInput: [1, 2]               -> Two-item list: [1, 2]\\nInput: [1, 2, 3, 4]         -> List starting with 1, rest: [2, 3, 4]\\nInput: {'name': 'Alice', 'age': 25} -> Person: Alice, age 25\\nInput: {'type': 'error', 'message': 'File not found'} -> Error occurred: File not found\\nInput: {'unknown': 'data'}  -> Unknown data type: dict\\nInput: 3.14                 -> Unknown data type: float\\n\\n=== Class Pattern Matching ===\\nPoint(0, 0) -> Origin point\\nPoint(0, 5) -> Point on Y-axis at y=5\\nPoint(3, 0) -> Point on X-axis at x=3\\nPoint(4, 4) -> Point on diagonal at (4, 4)\\nPoint(2, 7) -> Point in quadrant at (2, 7)",
                "explanation": "Match statements provide powerful pattern matching for complex data structures and types"
            }
        }
    
    def _get_explanation(self) -> str:
        """Get detailed explanation for control flow."""
        return (
            "Control flow statements determine the order in which code is executed. "
            "Conditional statements (if/elif/else) make decisions based on boolean conditions. "
            "Loops (for and while) repeat code blocks. For loops iterate over sequences, "
            "while while loops repeat based on conditions. Loop control statements (break, "
            "continue, pass) provide fine-grained control. Comprehensions offer concise ways "
            "to create collections with filtering and transformation. Match statements (Python 3.10+) "
            "provide powerful pattern matching capabilities for complex data structures."
        )
    
    def _get_best_practices(self) -> List[str]:
        """Get best practices for control flow."""
        return [
            "Keep conditions simple and readable - use parentheses for complex logic",
            "Use elif for multiple mutually exclusive conditions instead of nested ifs",
            "Prefer enumerate() over range(len()) for indexed iteration",
            "Use zip() to iterate over multiple sequences simultaneously",
            "Use comprehensions for simple transformations and filtering",
            "Avoid deeply nested loops - consider breaking into functions",
            "Use break and continue judiciously to avoid confusing logic",
            "Always ensure while loops have a way to terminate",
            "Use for...else to handle cases where loops complete without breaking",
            "Prefer match statements over long if/elif chains when available",
            "Use generator expressions for memory-efficient processing of large datasets",
            "Consider using all() and any() for boolean operations on sequences"
        ]