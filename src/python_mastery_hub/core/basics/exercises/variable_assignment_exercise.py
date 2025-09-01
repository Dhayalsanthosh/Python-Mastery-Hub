"""
Variable Assignment Exercise - Practice variable creation and manipulation.
"""

from typing import Dict, Any, List
from ..base import CodeValidator, ExampleRunner


class VariableAssignmentExercise:
    """Interactive exercise for practicing variable assignment patterns."""
    
    def __init__(self):
        self.title = "Variable Assignment Challenge"
        self.description = "Practice different ways to assign and manipulate variables"
        self.difficulty = "easy"
        self.validator = CodeValidator()
        self.runner = ExampleRunner()
    
    def get_instructions(self) -> Dict[str, Any]:
        """Get comprehensive exercise instructions."""
        return {
            "title": self.title,
            "description": self.description,
            "objectives": [
                "Create variables for a student profile",
                "Practice different assignment patterns",
                "Swap variable values elegantly",
                "Update and modify variables",
                "Work with different data types"
            ],
            "tasks": [
                "Create variables: name, age, grade, subjects (list), is_honors",
                "Use multiple assignment to create x, y, z = 1, 2, 3",
                "Swap the values of two variables without a temporary variable",
                "Update the student's grade using assignment operators",
                "Add a new subject to the subjects list",
                "Create a constant for MAX_SUBJECTS = 8"
            ],
            "requirements": [
                "Use descriptive variable names",
                "Follow Python naming conventions",
                "Demonstrate at least 3 different assignment patterns",
                "Include both mutable and immutable variables"
            ]
        }
    
    def get_starter_code(self) -> str:
        """Get starter code template."""
        return '''
# Variable Assignment Exercise
# Create variables for a student profile

# Basic assignment
name = 
age = 
grade = 
subjects = 
is_honors = 

# Multiple assignment
x, y, z = 

# Display student info
print(f"Student: {name}")
print(f"Age: {age}")
print(f"Grade: {grade}")
print(f"Subjects: {subjects}")
print(f"Honors student: {is_honors}")

# Variable swapping
# TODO: Swap age and grade (conceptually)

# Variable updates
# TODO: Update grade using += operator
# TODO: Add new subject to list

# Constants
# TODO: Create MAX_SUBJECTS constant
'''
    
    def get_solution(self) -> str:
        """Get complete solution with explanations."""
        return '''
# Variable Assignment Exercise - Complete Solution

# Basic assignment with different data types
name = "Alice Johnson"          # String
age = 16                        # Integer
grade = 85.5                    # Float
subjects = ["Math", "Science", "History"]  # List (mutable)
is_honors = True                # Boolean

print("=== Initial Student Profile ===")
print(f"Student: {name}")
print(f"Age: {age}")
print(f"Grade: {grade}")
print(f"Subjects: {subjects}")
print(f"Honors student: {is_honors}")

# Multiple assignment demonstration
x, y, z = 1, 2, 3
print(f"\\nMultiple assignment: x={x}, y={y}, z={z}")

# Tuple unpacking with different data types
first_name, last_name = name.split()
print(f"Name parts: first='{first_name}', last='{last_name}'")

# Variable swapping (Pythonic way)
original_age, original_grade = age, grade
print(f"\\nBefore swap: age={age}, grade={grade}")

# Elegant Python swap
age, grade = grade, age
print(f"After swap: age={age}, grade={grade}")

# Restore original values
age, grade = original_age, original_grade
print(f"Restored: age={age}, grade={grade}")

# Assignment operators
print("\\n=== Variable Updates ===")
print(f"Original grade: {grade}")

# Update grade using compound assignment
grade += 2.5  # Add bonus points
print(f"After bonus: {grade}")

grade *= 1.05  # 5% curve
print(f"After curve: {grade:.1f}")

# List operations (mutable object modification)
print(f"\\nOriginal subjects: {subjects}")

# Add new subject
subjects.append("Computer Science")
print(f"After adding subject: {subjects}")

# Add multiple subjects
subjects.extend(["Art", "Music"])
print(f"After adding more: {subjects}")

# Constants (naming convention)
MAX_SUBJECTS = 8
MAX_GRADE = 100.0
SCHOOL_NAME = "Python High School"

print(f"\\n=== School Information ===")
print(f"School: {SCHOOL_NAME}")
print(f"Maximum subjects: {MAX_SUBJECTS}")
print(f"Maximum grade: {MAX_GRADE}")
print(f"Current subject count: {len(subjects)}")

# Advanced assignment patterns
print("\\n=== Advanced Patterns ===")

# Unpacking with remainder
first_subject, *other_subjects, last_subject = subjects
print(f"First: {first_subject}")
print(f"Others: {other_subjects}")
print(f"Last: {last_subject}")

# Conditional assignment (ternary operator)
status = "Honors" if is_honors else "Regular"
print(f"Student status: {status}")

# Multiple assignment with different operations
min_grade, max_grade, avg_grade = 0, 100, grade
print(f"Grade range: {min_grade} - {max_grade}, current: {avg_grade:.1f}")

# Chained assignment
a = b = c = 0
print(f"Chained assignment: a={a}, b={b}, c={c}")

# Final student summary
print(f"\\n=== Final Student Profile ===")
print(f"Name: {name}")
print(f"Age: {age}")
print(f"Grade: {grade:.1f}")
print(f"Status: {status}")
print(f"Subjects ({len(subjects)}): {', '.join(subjects)}")
print(f"Honors: {is_honors}")
'''
    
    def check_solution(self, code: str) -> Dict[str, Any]:
        """Check and validate the student's solution."""
        feedback = []
        score = 0
        max_score = 10
        
        # Check syntax
        syntax_check = self.validator.validate_syntax(code)
        if not syntax_check["valid"]:
            return {
                "score": 0,
                "max_score": max_score,
                "feedback": [f"Syntax Error: {syntax_check['message']}"],
                "suggestions": ["Fix syntax errors before proceeding"]
            }
        
        # Check for required elements
        required_elements = [
            ("name =", "Student name variable"),
            ("age =", "Student age variable"),
            ("grade =", "Student grade variable"),
            ("subjects =", "Subjects list variable"),
            ("is_honors =", "Honors status variable"),
        ]
        
        for element, description in required_elements:
            if element in code:
                feedback.append(f"✓ Found {description}")
                score += 1
            else:
                feedback.append(f"✗ Missing {description}")
        
        # Check for advanced patterns
        advanced_patterns = [
            ("=", "Multiple assignment pattern"),
            ("+=", "Compound assignment operator"),
            (".append(", "List modification method"),
        ]
        
        for pattern, description in advanced_patterns:
            if pattern in code:
                feedback.append(f"✓ Used {description}")
                score += 1
        
        # Check naming conventions
        naming_issues = self.validator.check_naming_conventions(code)
        if naming_issues:
            feedback.extend([f"⚠ Naming: {issue}" for issue in naming_issues])
        else:
            feedback.append("✓ Good naming conventions")
            score += 1
        
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
    
    def run_interactive_demo(self) -> Dict[str, Any]:
        """Run an interactive demonstration of variable concepts."""
        print("=== Interactive Variable Assignment Demo ===\\n")
        
        # Basic assignment
        print("1. Basic Variable Assignment:")
        student_name = "Alex Smith"
        student_age = 17
        print(f"   name = '{student_name}'")
        print(f"   age = {student_age}\\n")
        
        # Multiple assignment
        print("2. Multiple Assignment:")
        a, b, c = 10, 20, 30
        print(f"   a, b, c = {a}, {b}, {c}\\n")
        
        # Variable swapping
        print("3. Variable Swapping:")
        x, y = 5, 10
        print(f"   Before: x={x}, y={y}")
        x, y = y, x
        print(f"   After swap: x={x}, y={y}\\n")
        
        # List operations
        print("4. List Operations:")
        hobbies = ["reading", "coding"]
        print(f"   Original: {hobbies}")
        hobbies.append("gaming")
        print(f"   After append: {hobbies}\\n")
        
        return {
            "demo_completed": True,
            "concepts_shown": [
                "Basic assignment",
                "Multiple assignment", 
                "Variable swapping",
                "List modification"
            ]
        }
    
    def get_practice_problems(self) -> List[Dict[str, Any]]:
        """Get additional practice problems."""
        return [
            {
                "problem": "Create variables for a book: title, author, pages, is_fiction",
                "hint": "Use appropriate data types for each piece of information",
                "solution": "title = 'Python Programming'\\nauthor = 'John Doe'\\npages = 350\\nis_fiction = False"
            },
            {
                "problem": "Swap three variables: a=1, b=2, c=3 to become a=3, b=1, c=2",
                "hint": "Use tuple unpacking for elegant rotation",
                "solution": "a, b, c = 1, 2, 3\\na, b, c = c, a, b"
            },
            {
                "problem": "Create a list of colors and add 'purple' using +=",
                "hint": "Remember that += for lists extends the list",
                "solution": "colors = ['red', 'blue', 'green']\\ncolors += ['purple']"
            }
        ]
    
    def _get_suggestions(self, score: int, max_score: int) -> List[str]:
        """Get suggestions based on score."""
        percentage = (score / max_score) * 100
        
        if percentage >= 90:
            return [
                "Excellent work! You've mastered variable assignment.",
                "Try the advanced practice problems for more challenge."
            ]
        elif percentage >= 70:
            return [
                "Good progress! Review the missing elements.",
                "Practice more with compound assignment operators.",
                "Try creating more complex data structures."
            ]
        else:
            return [
                "Keep practicing! Focus on the basic assignment patterns first.",
                "Review the solution code to see proper syntax.",
                "Start with simple variables before moving to complex ones."
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