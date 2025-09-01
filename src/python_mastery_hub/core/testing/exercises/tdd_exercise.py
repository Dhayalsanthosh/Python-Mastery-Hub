"""
TDD (Test-Driven Development) exercise for the Testing module.
Build a calculator using the Red-Green-Refactor cycle.
"""

from typing import Dict, Any


def get_tdd_exercise() -> Dict[str, Any]:
    """Get the TDD Calculator exercise."""
    return {
        "title": "TDD Calculator Development",
        "difficulty": "medium",
        "estimated_time": "2-3 hours",
        "instructions": """
Build a calculator using Test-Driven Development (TDD) principles.
Follow the Red-Green-Refactor cycle:
1. RED: Write a failing test
2. GREEN: Write minimal code to make it pass  
3. REFACTOR: Improve the code while keeping tests green

This exercise teaches you to let tests drive your design and ensure
comprehensive test coverage from the start.
""",
        "learning_objectives": [
            "Practice the Red-Green-Refactor TDD cycle",
            "Learn to write tests before implementation",
            "Experience how tests drive code design",
            "Build confidence in refactoring with good test coverage",
            "Understand the benefits of incremental development"
        ],
        "tasks": [
            {
                "step": 1,
                "title": "Start with Empty String",
                "description": "RED: Write a test for empty string returning 0",
                "requirements": [
                    "Write test_empty_string_returns_zero()",
                    "Test should fail initially",
                    "Create minimal Calculator class to pass"
                ]
            },
            {
                "step": 2,
                "title": "Single Number",
                "description": "Add support for single numbers",
                "requirements": [
                    "Write test for single number input",
                    "Update add() method to handle single numbers",
                    "Ensure previous test still passes"
                ]
            },
            {
                "step": 3,
                "title": "Two Numbers",
                "description": "Add support for two comma-separated numbers",
                "requirements": [
                    "Write test for two numbers: '1,2' -> 3",
                    "Update implementation to split and sum",
                    "Refactor if needed while keeping tests green"
                ]
            },
            {
                "step": 4,
                "title": "Multiple Numbers",
                "description": "Support any amount of numbers",
                "requirements": [
                    "Write test for multiple numbers: '1,2,3,4' -> 10",
                    "Refactor to handle arbitrary number of inputs",
                    "Consider edge cases"
                ]
            },
            {
                "step": 5,
                "title": "Newline Separators",
                "description": "Support newlines as separators",
                "requirements": [
                    "Write test for newlines: '1\\n2,3' -> 6",
                    "Update parsing logic",
                    "Handle mixed separators"
                ]
            },
            {
                "step": 6,
                "title": "Custom Delimiters",
                "description": "Support custom delimiters",
                "requirements": [
                    "Write test for custom delimiter: '//;\\n1;2' -> 3",
                    "Parse delimiter specification",
                    "Support different delimiter formats"
                ]
            },
            {
                "step": 7,
                "title": "Negative Numbers",
                "description": "Handle negative numbers with exceptions",
                "requirements": [
                    "Write test for negative number exception",
                    "Include all negative numbers in error message",
                    "Don't break positive number functionality"
                ]
            },
            {
                "step": 8,
                "title": "Ignore Large Numbers",
                "description": "Ignore numbers greater than 1000",
                "requirements": [
                    "Write test for numbers > 1000 being ignored",
                    "Numbers <= 1000 should still be included",
                    "Maintain all previous functionality"
                ]
            }
        ],
        "starter_code": '''
import unittest

# Start with just the test - no implementation yet!
class TestStringCalculator(unittest.TestCase):
    """TDD String Calculator Tests - Start Here!"""
    
    def test_empty_string_returns_zero(self):
        """RED: This test should fail initially."""
        calc = StringCalculator()  # This class doesn't exist yet!
        result = calc.add("")
        self.assertEqual(result, 0)

# TODO: Create StringCalculator class to make the test pass
# Follow TDD: Write minimal code to pass the test, then refactor

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
        "hints": [
            "Start with the simplest possible implementation",
            "Only write enough code to make the current test pass",
            "Run tests frequently to ensure you don't break existing functionality",
            "Refactor regularly but only when tests are green",
            "Let the tests guide your design decisions",
            "Use string methods like split() and join() for parsing",
            "Regular expressions can help with custom delimiters",
            "Consider using a list to collect parsing errors"
        ],
        "solution": '''
import unittest
import re

class StringCalculator:
    """String calculator implemented using TDD principles."""
    
    def add(self, numbers):
        """Add numbers from a string with various delimiter support."""
        if not numbers:
            return 0
        
        # Handle custom delimiters
        if numbers.startswith("//"):
            delimiter_line, numbers = numbers[2:].split("\\n", 1)
            delimiters = self._parse_delimiters(delimiter_line)
        else:
            delimiters = [",", "\\n"]
        
        # Split the numbers using all delimiters
        number_list = self._split_by_delimiters(numbers, delimiters)
        
        # Convert to integers and validate
        integers = []
        negative_numbers = []
        
        for num_str in number_list:
            if num_str.strip():  # Skip empty strings
                num = int(num_str.strip())
                
                if num < 0:
                    negative_numbers.append(num)
                elif num <= 1000:  # Ignore numbers > 1000
                    integers.append(num)
        
        # Check for negative numbers
        if negative_numbers:
            raise ValueError(f"Negative numbers not allowed: {', '.join(map(str, negative_numbers))}")
        
        return sum(integers)
    
    def _parse_delimiters(self, delimiter_line):
        """Parse custom delimiters from the delimiter line."""
        delimiters = []
        
        # Handle multiple delimiters in brackets: [del1][del2]
        bracket_pattern = r'\\[([^\\]]+)\\]'
        bracket_matches = re.findall(bracket_pattern, delimiter_line)
        
        if bracket_matches:
            delimiters.extend(bracket_matches)
        else:
            # Single character delimiter
            delimiters.append(delimiter_line)
        
        return delimiters
    
    def _split_by_delimiters(self, text, delimiters):
        """Split text by multiple delimiters."""
        # Start with the original text in a list
        parts = [text]
        
        # Split by each delimiter
        for delimiter in delimiters:
            new_parts = []
            for part in parts:
                # Split each part by the current delimiter
                new_parts.extend(part.split(delimiter))
            parts = new_parts
        
        return parts

class TestStringCalculator(unittest.TestCase):
    """Complete test suite for String Calculator."""
    
    def setUp(self):
        self.calc = StringCalculator()
    
    def test_empty_string_returns_zero(self):
        """Test that empty string returns 0."""
        result = self.calc.add("")
        self.assertEqual(result, 0)
    
    def test_single_number_returns_number(self):
        """Test that single number returns the number itself."""
        result = self.calc.add("1")
        self.assertEqual(result, 1)
        
        result = self.calc.add("5")
        self.assertEqual(result, 5)
    
    def test_two_numbers_comma_separated(self):
        """Test adding two numbers separated by comma."""
        result = self.calc.add("1,2")
        self.assertEqual(result, 3)
        
        result = self.calc.add("5,10")
        self.assertEqual(result, 15)
    
    def test_multiple_numbers_comma_separated(self):
        """Test adding multiple numbers."""
        result = self.calc.add("1,2,3")
        self.assertEqual(result, 6)
        
        result = self.calc.add("1,2,3,4,5")
        self.assertEqual(result, 15)
    
    def test_newlines_as_separators(self):
        """Test that newlines can be used as separators."""
        result = self.calc.add("1\\n2,3")
        self.assertEqual(result, 6)
        
        result = self.calc.add("1\\n2\\n3")
        self.assertEqual(result, 6)
    
    def test_custom_delimiters(self):
        """Test custom delimiters specified at the beginning."""
        result = self.calc.add("//;\\n1;2")
        self.assertEqual(result, 3)
        
        result = self.calc.add("//|\\n1|2|3")
        self.assertEqual(result, 6)
    
    def test_negative_numbers_raise_exception(self):
        """Test that negative numbers raise an exception."""
        with self.assertRaises(ValueError) as context:
            self.calc.add("1,-2,3")
        
        self.assertIn("Negative numbers not allowed", str(context.exception))
        self.assertIn("-2", str(context.exception))
    
    def test_multiple_negative_numbers_in_exception(self):
        """Test that all negative numbers are listed in exception."""
        with self.assertRaises(ValueError) as context:
            self.calc.add("1,-2,-3,4,-5")
        
        exception_message = str(context.exception)
        self.assertIn("-2", exception_message)
        self.assertIn("-3", exception_message)
        self.assertIn("-5", exception_message)
    
    def test_numbers_greater_than_1000_ignored(self):
        """Test that numbers > 1000 are ignored."""
        result = self.calc.add("2,1001")
        self.assertEqual(result, 2)
        
        result = self.calc.add("1000,1001,2")
        self.assertEqual(result, 1002)
    
    def test_custom_delimiters_any_length(self):
        """Test custom delimiters of any length."""
        result = self.calc.add("//[***]\\n1***2***3")
        self.assertEqual(result, 6)
        
        result = self.calc.add("//[abc]\\n1abc2abc3")
        self.assertEqual(result, 6)
    
    def test_multiple_custom_delimiters(self):
        """Test multiple custom delimiters."""
        result = self.calc.add("//[*][%]\\n1*2%3")
        self.assertEqual(result, 6)
        
        result = self.calc.add("//[***][%%]\\n1***2%%3")
        self.assertEqual(result, 6)

if __name__ == '__main__':
    # Demonstrate TDD process
    print("=== TDD String Calculator ===")
    print("This implementation was built using Test-Driven Development")
    print("Each feature was added one test at a time, following Red-Green-Refactor")
    print()
    
    # Run all tests
    unittest.main(verbosity=2)
'''
    }