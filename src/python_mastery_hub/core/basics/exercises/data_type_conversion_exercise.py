"""
Data Type Conversion Exercise - Practice converting between different Python data types.
"""

from typing import Dict, Any, List, Union
from ..base import CodeValidator, ExampleRunner


class DataTypeConversionExercise:
    """Interactive exercise for practicing data type conversions."""
    
    def __init__(self):
        self.title = "Data Type Conversion Challenge"
        self.description = "Convert between different Python data types safely and effectively"
        self.difficulty = "easy"
        self.validator = CodeValidator()
        self.runner = ExampleRunner()
    
    def get_instructions(self) -> Dict[str, Any]:
        """Get comprehensive exercise instructions."""
        return {
            "title": self.title,
            "description": self.description,
            "objectives": [
                "Convert string numbers to appropriate numeric types",
                "Handle conversion errors gracefully",
                "Convert between collections (list, tuple, set)",
                "Format numbers to strings with proper formatting",
                "Parse and validate user input data"
            ],
            "tasks": [
                "Convert string numbers to integers and floats",
                "Handle mixed data types in a list",
                "Convert between list, tuple, and set",
                "Format numbers as currency strings",
                "Parse CSV-like string data",
                "Validate and convert user input safely"
            ],
            "requirements": [
                "Use appropriate conversion functions (int, float, str)",
                "Handle ValueError exceptions for invalid conversions",
                "Preserve data integrity during conversions",
                "Use proper string formatting techniques"
            ]
        }
    
    def get_starter_code(self) -> str:
        """Get starter code template."""
        return '''
# Data Type Conversion Exercise

# Mixed data to convert
mixed_data = ['42', '3.14', 'hello', '100', '2.7', 'world', '0']
numbers_str = ['1', '2', '3.14', '4.5', 'invalid', '6']

# TODO: Convert string numbers to appropriate numeric types
converted_numbers = []

# TODO: Handle conversion errors gracefully
for item in numbers_str:
    try:
        # Your conversion logic here
        pass
    except ValueError:
        # Handle error
        pass

# TODO: Convert between collections
original_list = [1, 2, 3, 2, 4, 3]
# Convert to tuple
# Convert to set (removes duplicates)
# Convert back to list

# TODO: Format numbers as currency
prices = [19.99, 5.50, 100.0, 0.75]
# Format as currency strings

# TODO: Parse CSV-like data
csv_data = "John,25,Engineer,50000"
# Split and convert to appropriate types

print("Conversion completed!")
'''
    
    def get_solution(self) -> str:
        """Get complete solution with explanations."""
        return '''
# Data Type Conversion Exercise - Complete Solution

print("=== Data Type Conversion Exercise ===\\n")

# Mixed data to demonstrate conversions
mixed_data = ['42', '3.14', 'hello', '100', '2.7', 'world', '0']
numbers_str = ['1', '2', '3.14', '4.5', 'invalid', '6']

print("1. Smart Number Conversion")
print("=" * 30)

def smart_convert(value):
    """Convert string to appropriate numeric type or return original."""
    if not isinstance(value, str):
        return value
    
    # Try integer first
    try:
        if '.' not in value:
            return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return original if conversion fails
    return value

# Convert mixed data intelligently
converted_mixed = [smart_convert(item) for item in mixed_data]
print(f"Original:  {mixed_data}")
print(f"Converted: {converted_mixed}")
print(f"Types:     {[type(x).__name__ for x in converted_mixed]}\\n")

print("2. Safe Number Conversion with Error Handling")
print("=" * 45)

converted_numbers = []
errors = []

for item in numbers_str:
    try:
        # Determine if integer or float
        if '.' in item:
            converted = float(item)
        else:
            converted = int(item)
        converted_numbers.append(converted)
        print(f"✓ '{item}' -> {converted} ({type(converted).__name__})")
    except ValueError as e:
        errors.append(f"'{item}': {e}")
        print(f"✗ '{item}' -> Error: Cannot convert")

print(f"\\nSuccessfully converted: {converted_numbers}")
print(f"Conversion errors: {len(errors)}")

print("\\n3. Collection Type Conversions")
print("=" * 30)

original_list = [1, 2, 3, 2, 4, 3, 1]
print(f"Original list: {original_list}")

# Convert to tuple (immutable, ordered)
list_to_tuple = tuple(original_list)
print(f"As tuple:      {list_to_tuple}")

# Convert to set (mutable, unordered, unique)
list_to_set = set(original_list)
print(f"As set:        {list_to_set}")

# Convert back to list (from set - order may change)
set_to_list = list(list_to_set)
print(f"Back to list:  {set_to_list}")

# Demonstrate sorted unique list
unique_sorted = sorted(set(original_list))
print(f"Unique sorted: {unique_sorted}")

print("\\n4. String to Collection Conversions")
print("=" * 35)

text = "hello"
word_list = ["python", "programming", "data", "types"]

# String to list of characters
chars = list(text)
print(f"String '{text}' -> characters: {chars}")

# Join list to string
joined = " ".join(word_list)
print(f"Word list -> sentence: '{joined}'")

# Split string to list
sentence = "Python is awesome for data science"
words = sentence.split()
print(f"Sentence -> words: {words}")

print("\\n5. Number Formatting")
print("=" * 20)

prices = [19.99, 5.50, 100.0, 0.75, 1234.567]

print("Currency formatting:")
for price in prices:
    # Different formatting approaches
    currency1 = f"${price:.2f}"
    currency2 = "${:,.2f}".format(price)
    currency3 = "$%.2f" % price
    
    print(f"  {price:8.3f} -> {currency1} | {currency2} | {currency3}")

print("\\nOther number formats:")
number = 1234567.89
print(f"Scientific: {number:.2e}")
print(f"Percentage: {number/10000:.1%}")
print(f"Comma sep:  {number:,}")

print("\\n6. CSV Data Parsing")
print("=" * 18)

csv_data = "John,25,Engineer,50000"
print(f"CSV data: '{csv_data}'")

# Split and convert
parts = csv_data.split(',')
print(f"Split parts: {parts}")

# Convert to appropriate types
name = parts[0]              # String
age = int(parts[1])          # Integer
job = parts[2]               # String
salary = float(parts[3])     # Float (for calculations)

print(f"Parsed data:")
print(f"  Name:   {name} ({type(name).__name__})")
print(f"  Age:    {age} ({type(age).__name__})")
print(f"  Job:    {job} ({type(job).__name__})")
print(f"  Salary: ${salary:,.2f} ({type(salary).__name__})")

# Create structured data
person = {
    'name': name,
    'age': age,
    'job': job,
    'salary': salary
}
print(f"\\nStructured: {person}")

print("\\n7. Advanced Conversion Scenarios")
print("=" * 32)

# Boolean conversions
print("Boolean conversions:")
test_values = [0, 1, "", "hello", [], [1], None, {}, {"key": "value"}]
for value in test_values:
    print(f"  {str(value):12} -> {bool(value)}")

# String to boolean (custom logic)
def str_to_bool(s):
    """Convert string to boolean with custom logic."""
    if isinstance(s, str):
        return s.lower() in ('true', 'yes', '1', 'on', 'enabled')
    return bool(s)

bool_strings = ['true', 'false', 'yes', 'no', '1', '0', 'on', 'off']
print("\\nString to boolean:")
for s in bool_strings:
    print(f"  '{s}' -> {str_to_bool(s)}")

print("\\n8. Error-Safe Conversion Function")
print("=" * 33)

def safe_convert(value, target_type, default=None):
    """Safely convert value to target type with fallback."""
    try:
        if target_type == bool and isinstance(value, str):
            return str_to_bool(value)
        return target_type(value)
    except (ValueError, TypeError):
        return default

# Test safe conversion
test_conversions = [
    ("123", int, 0),
    ("3.14", float, 0.0),
    ("hello", int, -1),
    ("true", bool, False),
    ([1, 2, 3], str, "")
]

print("Safe conversions:")
for value, target, default in test_conversions:
    result = safe_convert(value, target, default)
    print(f"  {str(value):10} -> {target.__name__:5} = {result} ({type(result).__name__})")

print("\\n=== Exercise Complete! ===")
print("Key concepts demonstrated:")
print("- Intelligent type detection and conversion")
print("- Error handling with try/except")
print("- Collection type transformations")
print("- String formatting and parsing")
print("- Safe conversion utilities")
'''
    
    def check_solution(self, code: str) -> Dict[str, Any]:
        """Check and validate the student's solution."""
        feedback = []
        score = 0
        max_score = 12
        
        # Check syntax
        syntax_check = self.validator.validate_syntax(code)
        if not syntax_check["valid"]:
            return {
                "score": 0,
                "max_score": max_score,
                "feedback": [f"Syntax Error: {syntax_check['message']}"],
                "suggestions": ["Fix syntax errors before proceeding"]
            }
        
        # Check for required conversion functions
        conversion_checks = [
            ("int(", "Integer conversion function", 2),
            ("float(", "Float conversion function", 2),
            ("str(", "String conversion function", 1),
            ("try:", "Error handling with try block", 2),
            ("except", "Exception handling", 2),
            ("tuple(", "Tuple conversion", 1),
            ("list(", "List conversion", 1),
            ("set(", "Set conversion", 1)
        ]
        
        for pattern, description, points in conversion_checks:
            if pattern in code:
                feedback.append(f"✓ Used {description}")
                score += points
            else:
                feedback.append(f"✗ Missing {description}")
        
        # Check for advanced concepts
        if "ValueError" in code:
            feedback.append("✓ Proper exception handling for ValueError")
        
        # Calculate percentage
        percentage = (score / max_score) * 100
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "feedback": feedback,
            "suggestions": self._get_suggestions(score, max_score),
            "grade": self._calculate_grade(percentage)
        }
    
    def run_conversion_demo(self) -> Dict[str, Any]:
        """Run interactive conversion demonstration."""
        results = {}
        
        # String to number conversions
        string_numbers = ["42", "3.14", "invalid"]
        results["string_to_number"] = {}
        
        for s in string_numbers:
            try:
                if '.' in s:
                    converted = float(s)
                else:
                    converted = int(s)
                results["string_to_number"][s] = {"success": True, "value": converted, "type": type(converted).__name__}
            except ValueError:
                results["string_to_number"][s] = {"success": False, "error": "Invalid format"}
        
        # Collection conversions
        original = [1, 2, 3, 2, 4]
        results["collections"] = {
            "list": original,
            "tuple": tuple(original),
            "set": list(set(original)),  # Convert back to list for JSON serialization
            "unique_count": len(set(original))
        }
        
        return results
    
    def get_practice_problems(self) -> List[Dict[str, Any]]:
        """Get additional practice problems."""
        return [
            {
                "problem": "Convert temperature string '98.6F' to float (remove 'F')",
                "hint": "Use string slicing to remove the 'F' before converting",
                "solution": "temp_str = '98.6F'\\ntemp_float = float(temp_str[:-1])"
            },
            {
                "problem": "Parse date string '2023-12-25' into year, month, day integers",
                "hint": "Split by '-' and convert each part to int",
                "solution": "date_str = '2023-12-25'\\nyear, month, day = map(int, date_str.split('-'))"
            },
            {
                "problem": "Convert list of mixed types [1, '2', 3.0, '4.5'] to all floats",
                "hint": "Use list comprehension with float() conversion",
                "solution": "mixed = [1, '2', 3.0, '4.5']\\nall_floats = [float(x) for x in mixed]"
            }
        ]
    
    def _get_suggestions(self, score: int, max_score: int) -> List[str]:
        """Get suggestions based on score."""
        percentage = (score / max_score) * 100
        
        if percentage >= 90:
            return [
                "Excellent! You've mastered data type conversions.",
                "Try working with more complex nested data structures.",
                "Consider edge cases like empty strings and None values."
            ]
        elif percentage >= 70:
            return [
                "Good progress! Focus on error handling patterns.",
                "Practice with try/except blocks for safe conversions.",
                "Review collection type conversions."
            ]
        else:
            return [
                "Keep practicing basic conversion functions: int(), float(), str().",
                "Start with simple conversions before handling errors.",
                "Review the solution to understand proper patterns."
            ]
    
    def _calculate_grade(self, percentage: float) -> str:
        """Calculate letter grade from percentage."""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"