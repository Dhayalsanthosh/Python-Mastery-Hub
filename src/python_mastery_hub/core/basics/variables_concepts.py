"""
Variables Concepts - Variable assignment, scope, and naming conventions.
"""

from typing import Dict, Any, List


class VariablesConcepts:
    """Handles all variable-related concepts and examples."""
    
    def __init__(self):
        self.topic = "variables"
        self.examples = self._setup_examples()
    
    def demonstrate(self) -> Dict[str, Any]:
        """Return comprehensive variable demonstrations."""
        return {
            "topic": self.topic,
            "examples": self.examples,
            "explanation": self._get_explanation(),
            "best_practices": self._get_best_practices(),
        }
    
    def _setup_examples(self) -> Dict[str, Any]:
        """Setup comprehensive variable examples."""
        return {
            "basic_assignment": {
                "code": '''
# Basic variable assignment
name = "Alice"
age = 30
height = 5.6
is_student = False

print(f"Name: {name}, Age: {age}, Height: {height}, Student: {is_student}")
''',
                "output": "Name: Alice, Age: 30, Height: 5.6, Student: False",
                "explanation": "Variables store data and can hold different types of values"
            },
            
            "multiple_assignment": {
                "code": '''
# Multiple assignment techniques
x, y, z = 1, 2, 3
a = b = c = 0
first, *middle, last = [1, 2, 3, 4, 5]

print(f"x={x}, y={y}, z={z}")
print(f"a={a}, b={b}, c={c}")
print(f"first={first}, middle={middle}, last={last}")
''',
                "output": "x=1, y=2, z=3\\na=0, b=0, c=0\\nfirst=1, middle=[2, 3, 4], last=5",
                "explanation": "Python supports multiple assignment patterns for efficiency"
            },
            
            "variable_swapping": {
                "code": '''
# Elegant variable swapping
a, b = 10, 20
print(f"Before swap: a={a}, b={b}")

# Pythonic swap
a, b = b, a
print(f"After swap: a={a}, b={b}")
''',
                "output": "Before swap: a=10, b=20\\nAfter swap: a=20, b=10",
                "explanation": "Python allows elegant variable swapping without temporary variables"
            },
            
            "variable_scope": {
                "code": '''
# Variable scope demonstration
global_var = "I'm global"

def scope_demo():
    local_var = "I'm local"
    global global_var
    global_var = "Modified global"
    
    def inner_function():
        nonlocal local_var
        local_var = "Modified local"
        inner_var = "I'm inner"
        return inner_var
    
    inner_result = inner_function()
    return local_var, inner_result

result = scope_demo()
print(f"Global: {global_var}")
print(f"Returned: {result}")
''',
                "output": "Global: Modified global\\nReturned: ('Modified local', \"I'm inner\")",
                "explanation": "Understanding variable scope is crucial for proper Python programming"
            },
            
            "naming_conventions": {
                "code": '''
# Proper naming conventions
# Good variable names
user_name = "john_doe"
total_price = 99.99
is_valid = True
MAX_ATTEMPTS = 3  # Constants in UPPER_CASE

# Class names use PascalCase
class StudentRecord:
    def __init__(self, student_id):
        self.student_id = student_id  # Instance variable
        self._private_data = "protected"  # Convention for protected
        self.__really_private = "private"  # Name mangling
    
    def get_student_info(self):  # Method names use snake_case
        return f"Student ID: {self.student_id}"

# Demonstrate naming
student = StudentRecord("STU001")
print(student.get_student_info())
print(f"User: {user_name}, Price: ${total_price}")
''',
                "output": "Student ID: STU001\\nUser: john_doe, Price: $99.99",
                "explanation": "Consistent naming conventions improve code readability and maintainability"
            }
        }
    
    def _get_explanation(self) -> str:
        """Get detailed explanation for variables."""
        return (
            "Variables are containers for storing data values. Python variables are "
            "dynamically typed, meaning you don't need to declare their type explicitly. "
            "The type is determined by the value assigned. Understanding variable scope "
            "(global, local, nonlocal) and following naming conventions are essential "
            "for writing clean, maintainable Python code."
        )
    
    def _get_best_practices(self) -> List[str]:
        """Get best practices for variables."""
        return [
            "Use descriptive variable names that clearly indicate purpose",
            "Follow snake_case naming convention for variables and functions",
            "Use UPPER_CASE for constants that shouldn't change",
            "Initialize variables before use to avoid NameError",
            "Avoid global variables when possible - prefer function parameters",
            "Use meaningful names instead of single letters (except for short loops)",
            "Don't use Python keywords or built-in function names as variables",
            "Group related variable assignments for better organization",
            "Use tuple unpacking for multiple assignments when appropriate",
            "Be consistent with naming patterns throughout your codebase"
        ]