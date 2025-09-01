"""
Functions Concepts - Function definition, parameters, and advanced features.
"""

from typing import Dict, Any, List, Callable, Union


class FunctionsConcepts:
    """Handles all function-related concepts and examples."""
    
    def __init__(self):
        self.topic = "functions"
        self.examples = self._setup_examples()
    
    def demonstrate(self) -> Dict[str, Any]:
        """Return comprehensive function demonstrations."""
        return {
            "topic": self.topic,
            "examples": self.examples,
            "explanation": self._get_explanation(),
            "best_practices": self._get_best_practices(),
        }
    
    def _setup_examples(self) -> Dict[str, Any]:
        """Setup comprehensive function examples."""
        return {
            "basic_functions": {
                "code": '''
# Basic function definition and usage
def greet(name, greeting="Hello"):
    """A function that greets someone with a customizable greeting.
    
    Args:
        name (str): The name of the person to greet
        greeting (str): The greeting to use (default: "Hello")
    
    Returns:
        str: The formatted greeting message
    """
    return f"{greeting}, {name}!"

def calculate_area(length, width):
    """Calculate the area of a rectangle.
    
    Args:
        length (float): The length of the rectangle
        width (float): The width of the rectangle
    
    Returns:
        float: The area of the rectangle
    """
    area = length * width
    return area

def print_info():
    """Function with no parameters or return value."""
    print("This function prints information but returns None")

# Function calls
print(greet("Alice"))
print(greet("Bob", "Hi"))
print(f"Area of 5x3 rectangle: {calculate_area(5, 3)}")

result = print_info()
print(f"print_info() returned: {result}")

# Function introspection
print(f"Function name: {greet.__name__}")
print(f"Function docstring: {greet.__doc__}")
''',
                "output": "Hello, Alice!\\nHi, Bob!\\nArea of 5x3 rectangle: 15\\nThis function prints information but returns None\\nprint_info() returned: None\\nFunction name: greet\\nFunction docstring: A function that greets someone with a customizable greeting.",
                "explanation": "Functions encapsulate reusable code with parameters, return values, and documentation"
            },
            
            "parameter_types": {
                "code": '''
# Different types of function parameters
def flexible_function(required, default="default", *args, **kwargs):
    """Demonstrates different parameter types.
    
    Args:
        required: A required positional parameter
        default: A parameter with default value
        *args: Variable number of positional arguments
        **kwargs: Variable number of keyword arguments
    """
    print(f"Required: {required}")
    print(f"Default: {default}")
    print(f"Args: {args}")
    print(f"Kwargs: {kwargs}")
    print("-" * 40)

# Different ways to call the function
print("=== Basic call ===")
flexible_function("must_have")

print("\\n=== With custom default ===")
flexible_function("must_have", "custom_default")

print("\\n=== With extra positional args ===")
flexible_function("must_have", "custom", 1, 2, 3)

print("\\n=== With keyword arguments ===")
flexible_function("must_have", extra1="value1", extra2="value2")

print("\\n=== Unpacking arguments ===")
data = ["required_value", "default_value", 1, 2, 3]
extra_data = {"key1": "val1", "key2": "val2"}
flexible_function(*data, **extra_data)

# Keyword-only parameters (Python 3+)
def keyword_only_function(name, *, age, city="Unknown"):
    """Function with keyword-only parameters after *."""
    return f"{name} is {age} years old and lives in {city}"

print("\\n=== Keyword-only parameters ===")
print(keyword_only_function("Alice", age=25, city="New York"))
# print(keyword_only_function("Bob", 30))  # This would raise TypeError

# Positional-only parameters (Python 3.8+)
def positional_only_function(name, age, /, city="Unknown"):
    """Function with positional-only parameters before /."""
    return f"{name}, {age}, {city}"

print(positional_only_function("Charlie", 35, "Boston"))
''',
                "output": "=== Basic call ===\\nRequired: must_have\\nDefault: default\\nArgs: ()\\nKwargs: {}\\n----------------------------------------\\n\\n=== With custom default ===\\nRequired: must_have\\nDefault: custom_default\\nArgs: ()\\nKwargs: {}\\n----------------------------------------\\n\\n=== With extra positional args ===\\nRequired: must_have\\nDefault: custom\\nArgs: (1, 2, 3)\\nKwargs: {}\\n----------------------------------------\\n\\n=== With keyword arguments ===\\nRequired: must_have\\nDefault: default\\nArgs: ()\\nKwargs: {'extra1': 'value1', 'extra2': 'value2'}\\n----------------------------------------\\n\\n=== Unpacking arguments ===\\nRequired: required_value\\nDefault: default_value\\nArgs: (1, 2, 3)\\nKwargs: {'key1': 'val1', 'key2': 'val2'}\\n----------------------------------------\\n\\n=== Keyword-only parameters ===\\nAlice is 25 years old and lives in New York\\nCharlie, 35, Boston",
                "explanation": "Python functions support flexible parameter patterns including defaults, *args, **kwargs, and keyword/positional-only parameters"
            },
            
            "lambda_functions": {
                "code": '''
# Lambda functions and functional programming
print("=== Basic Lambda Functions ===")
# Basic lambda
square = lambda x: x**2
print(f"Square of 5: {square(5)}")

# Lambda with multiple parameters
add = lambda x, y: x + y
print(f"3 + 4 = {add(3, 4)}")

# Lambda with conditional
max_func = lambda a, b: a if a > b else b
print(f"Max of 10 and 7: {max_func(10, 7)}")

print("\\n=== Lambda with Built-in Functions ===")
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Map: apply function to each element
squares = list(map(lambda x: x**2, numbers))
print(f"Squares: {squares}")

# Filter: keep elements that match condition
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Even numbers: {evens}")

# Reduce: accumulate values (need to import functools.reduce)
from functools import reduce
sum_all = reduce(lambda x, y: x + y, numbers)
print(f"Sum of all numbers: {sum_all}")

print("\\n=== Lambda for Sorting ===")
students = [("Alice", 85), ("Bob", 90), ("Charlie", 78), ("Diana", 92)]

# Sort by grade (second element)
sorted_by_grade = sorted(students, key=lambda student: student[1], reverse=True)
print(f"Students by grade: {sorted_by_grade}")

# Sort by name length
sorted_by_name_length = sorted(students, key=lambda student: len(student[0]))
print(f"Students by name length: {sorted_by_name_length}")

print("\\n=== Lambda in Data Processing ===")
data = [
    {"name": "Alice", "age": 25, "salary": 50000},
    {"name": "Bob", "age": 30, "salary": 60000},
    {"name": "Charlie", "age": 35, "salary": 70000}
]

# Extract names
names = list(map(lambda person: person["name"], data))
print(f"Names: {names}")

# Filter high earners
high_earners = list(filter(lambda person: person["salary"] > 55000, data))
print(f"High earners: {[p['name'] for p in high_earners]}")

# Calculate average salary
total_salary = reduce(lambda total, person: total + person["salary"], data, 0)
avg_salary = total_salary / len(data)
print(f"Average salary: ${avg_salary:,.2f}")
''',
                "output": "=== Basic Lambda Functions ===\\nSquare of 5: 25\\n3 + 4 = 7\\nMax of 10 and 7: 10\\n\\n=== Lambda with Built-in Functions ===\\nSquares: [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]\\nEven numbers: [2, 4, 6, 8, 10]\\nSum of all numbers: 55\\n\\n=== Lambda for Sorting ===\\nStudents by grade: [('Diana', 92), ('Bob', 90), ('Alice', 85), ('Charlie', 78)]\\nStudents by name length: [('Bob', 90), ('Alice', 85), ('Diana', 92), ('Charlie', 78)]\\n\\n=== Lambda in Data Processing ===\\nNames: ['Alice', 'Bob', 'Charlie']\\nHigh earners: ['Bob', 'Charlie']\\nAverage salary: $60,000.00",
                "explanation": "Lambda functions provide concise anonymous functions, ideal for functional programming patterns"
            },
            
            "scope_and_closures": {
                "code": '''
# Variable scope and closures
global_var = "I'm global"

def outer_function(x):
    """Demonstrate scope and closures."""
    outer_var = f"I'm in outer, x={x}"
    
    def inner_function(y):
        """Inner function with access to outer scope."""
        inner_var = f"I'm in inner, y={y}"
        # Access variables from different scopes
        return f"Inner: {inner_var}, Outer: {outer_var}, Global: {global_var}"
    
    return inner_function

# Create a closure
closure = outer_function(10)
result = closure(20)
print("Closure result:", result)

print("\\n=== Closure with State ===")
def create_counter(start=0):
    """Create a counter function with persistent state."""
    count = start
    
    def counter():
        nonlocal count
        count += 1
        return count
    
    def get_count():
        return count
    
    def reset(value=0):
        nonlocal count
        count = value
    
    # Return multiple functions
    counter.get = get_count
    counter.reset = reset
    return counter

# Create counter instances
counter1 = create_counter()
counter2 = create_counter(100)

print(f"Counter 1: {counter1()}, {counter1()}, {counter1()}")
print(f"Counter 2: {counter2()}, {counter2()}")
print(f"Counter 1 current: {counter1.get()}")
print(f"Counter 2 current: {counter2.get()}")

counter1.reset(50)
print(f"Counter 1 after reset: {counter1()}")

print("\\n=== LEGB Rule Demonstration ===")
x = "global x"

def demo_legb():
    x = "enclosing x"
    
    def inner():
        x = "local x"
        print(f"Local scope: {x}")
        
        # Access different scopes
        def show_scopes():
            print(f"Inner local: {x}")
            # print(f"Enclosing: {enclosing_x}")  # Would need nonlocal
            print(f"Global: {globals()['x']}")
            print(f"Built-in example: {len('hello')}")
        
        show_scopes()
    
    print(f"Enclosing scope: {x}")
    inner()

demo_legb()
print(f"Global scope: {x}")
''',
                "output": "Closure result: Inner: I'm in inner, y=20, Outer: I'm in outer, x=10, Global: I'm global\\n\\n=== Closure with State ===\\nCounter 1: 1, 2, 3\\nCounter 2: 101, 102\\nCounter 1 current: 3\\nCounter 2 current: 102\\nCounter 1 after reset: 51\\n\\n=== LEGB Rule Demonstration ===\\nEnclosing scope: enclosing x\\nLocal scope: local x\\nInner local: local x\\nGlobal: global x\\nBuilt-in example: 5\\nGlobal scope: global x",
                "explanation": "Python follows LEGB rule (Local, Enclosing, Global, Built-in) for variable resolution and supports closures for persistent state"
            },
            
            "decorators": {
                "code": '''
# Function decorators
print("=== Basic Decorator ===")
def timing_decorator(func):
    """Decorator to measure function execution time."""
    import time
    
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    
    return wrapper

@timing_decorator
def slow_function():
    """A function that takes some time."""
    import time
    time.sleep(0.1)
    return "Done!"

result = slow_function()
print(f"Result: {result}")

print("\\n=== Decorator with Parameters ===")
def repeat(times):
    """Decorator factory that repeats function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            results = []
            for i in range(times):
                result = func(*args, **kwargs)
                results.append(result)
                print(f"Execution {i+1}: {result}")
            return results
        return wrapper
    return decorator

@repeat(3)
def greet_person(name):
    return f"Hello, {name}!"

results = greet_person("Alice")
print(f"All results: {results}")

print("\\n=== Multiple Decorators ===")
def bold_decorator(func):
    """Add bold formatting."""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return f"**{result}**"
    return wrapper

def italic_decorator(func):
    """Add italic formatting."""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return f"*{result}*"
    return wrapper

@bold_decorator
@italic_decorator
def format_text(text):
    return text.upper()

formatted = format_text("hello world")
print(f"Formatted text: {formatted}")

print("\\n=== Class-based Decorator ===")
class CountCalls:
    """Decorator class to count function calls."""
    
    def __init__(self, func):
        self.func = func
        self.call_count = 0
    
    def __call__(self, *args, **kwargs):
        self.call_count += 1
        print(f"{self.func.__name__} called {self.call_count} times")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello(name):
    return f"Hello, {name}!"

say_hello("Alice")
say_hello("Bob")
say_hello("Charlie")
''',
                "output": "=== Basic Decorator ===\\nslow_function took 0.1001 seconds\\nResult: Done!\\n\\n=== Decorator with Parameters ===\\nExecution 1: Hello, Alice!\\nExecution 2: Hello, Alice!\\nExecution 3: Hello, Alice!\\nAll results: ['Hello, Alice!', 'Hello, Alice!', 'Hello, Alice!']\\n\\n=== Multiple Decorators ===\\nFormatted text: ***HELLO WORLD***\\n\\n=== Class-based Decorator ===\\nsay_hello called 1 times\\nsay_hello called 2 times\\nsay_hello called 3 times",
                "explanation": "Decorators modify function behavior without changing the function itself, supporting both function and class-based implementations"
            },
            
            "higher_order_functions": {
                "code": '''
# Higher-order functions - functions that operate on other functions
print("=== Functions as First-Class Objects ===")

def add(x, y):
    return x + y

def multiply(x, y):
    return x * y

def subtract(x, y):
    return x - y

# Store functions in data structures
operations = {
    "add": add,
    "multiply": multiply,
    "subtract": subtract
}

# Use functions as values
def calculate(operation_name, x, y):
    """Higher-order function that takes operation name."""
    operation = operations.get(operation_name)
    if operation:
        return operation(x, y)
    else:
        return "Unknown operation"

print(f"Add: {calculate('add', 5, 3)}")
print(f"Multiply: {calculate('multiply', 5, 3)}")

print("\\n=== Passing Functions as Arguments ===")
def apply_operation(func, values):
    """Apply a function to a list of value pairs."""
    results = []
    for x, y in values:
        result = func(x, y)
        results.append(result)
    return results

value_pairs = [(1, 2), (3, 4), (5, 6)]
additions = apply_operation(add, value_pairs)
multiplications = apply_operation(multiply, value_pairs)

print(f"Additions: {additions}")
print(f"Multiplications: {multiplications}")

print("\\n=== Returning Functions ===")
def create_multiplier(factor):
    """Return a function that multiplies by a given factor."""
    def multiplier(x):
        return x * factor
    return multiplier

# Create specific multiplier functions
double = create_multiplier(2)
triple = create_multiplier(3)

print(f"Double 5: {double(5)}")
print(f"Triple 4: {triple(4)}")

print("\\n=== Function Composition ===")
def compose(f, g):
    """Compose two functions: returns f(g(x))."""
    def composed(x):
        return f(g(x))
    return composed

def square(x):
    return x ** 2

def increment(x):
    return x + 1

# Compose functions
square_then_increment = compose(increment, square)
increment_then_square = compose(square, increment)

print(f"Square then increment 5: {square_then_increment(5)}")  # (5^2) + 1 = 26
print(f"Increment then square 5: {increment_then_square(5)}")  # (5+1)^2 = 36

print("\\n=== Partial Function Application ===")
from functools import partial

def power(base, exponent):
    return base ** exponent

# Create specialized functions using partial
square_func = partial(power, exponent=2)
cube_func = partial(power, exponent=3)

print(f"Square of 4: {square_func(4)}")
print(f"Cube of 3: {cube_func(3)}")

# Partial with multiple arguments
def greet_with_title(title, first_name, last_name):
    return f"{title} {first_name} {last_name}"

greet_dr = partial(greet_with_title, "Dr.")
greet_prof = partial(greet_with_title, "Prof.")

print(f"Doctor greeting: {greet_dr('Jane', 'Smith')}")
print(f"Professor greeting: {greet_prof('John', 'Doe')}")
''',
                "output": "=== Functions as First-Class Objects ===\\nAdd: 8\\nMultiply: 15\\n\\n=== Passing Functions as Arguments ===\\nAdditions: [3, 7, 11]\\nMultiplications: [2, 12, 30]\\n\\n=== Returning Functions ===\\nDouble 5: 10\\nTriple 4: 12\\n\\n=== Function Composition ===\\nSquare then increment 5: 26\\nIncrement then square 5: 36\\n\\n=== Partial Function Application ===\\nSquare of 4: 16\\nCube of 3: 27\\nDoctor greeting: Dr. Jane Smith\\nProfessor greeting: Prof. John Doe",
                "explanation": "Higher-order functions treat functions as first-class objects, enabling powerful patterns like composition and partial application"
            }
        }
    
    def _get_explanation(self) -> str:
        """Get detailed explanation for functions."""
        return (
            "Functions are reusable blocks of code that perform specific tasks. They help "
            "organize code, avoid repetition, and create modular programs. Python functions "
            "support flexible parameter patterns, default values, variable arguments, and "
            "keyword arguments. Advanced features include closures, decorators, and treating "
            "functions as first-class objects. Understanding scope (LEGB rule) and functional "
            "programming concepts enables writing more elegant and maintainable code."
        )
    
    def _get_best_practices(self) -> List[str]:
        """Get best practices for functions."""
        return [
            "Keep functions small and focused on a single task",
            "Use descriptive function names that indicate what they do",
            "Write comprehensive docstrings with Args, Returns, and Raises sections",
            "Prefer keyword arguments for functions with many parameters",
            "Use type hints to document expected parameter and return types",
            "Return meaningful values or None explicitly - avoid implicit returns",
            "Avoid global variables - pass data through parameters",
            "Use default parameter values judiciously - avoid mutable defaults",
            "Handle edge cases and validate input parameters when necessary",
            "Consider using decorators for cross-cutting concerns like logging",
            "Use lambda functions for simple, one-line operations only",
            "Prefer pure functions (no side effects) when possible for easier testing"
        ]