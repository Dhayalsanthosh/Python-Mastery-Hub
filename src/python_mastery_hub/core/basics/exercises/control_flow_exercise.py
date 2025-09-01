"""
Control Flow Exercise - Practice logical decision making and iteration patterns.
"""

from typing import Dict, Any, List
import random
from ..base import CodeValidator, ExampleRunner


class ControlFlowExercise:
    """Interactive exercise for practicing control flow structures."""
    
    def __init__(self):
        self.title = "Logic and Loop Challenge"
        self.description = "Solve problems using conditional statements and loops"
        self.difficulty = "medium"
        self.validator = CodeValidator()
        self.runner = ExampleRunner()
    
    def get_instructions(self) -> Dict[str, Any]:
        """Get comprehensive exercise instructions."""
        return {
            "title": self.title,
            "description": self.description,
            "objectives": [
                "Create complex conditional logic with if/elif/else",
                "Implement different types of loops (for, while)",
                "Use loop control statements (break, continue)",
                "Build nested loops for multi-dimensional problems",
                "Create efficient algorithms using proper control flow"
            ],
            "tasks": [
                "Build a number guessing game with attempt limits",
                "Create a grade calculator with multiple conditions",
                "Implement a simple menu system with user choices",
                "Generate multiplication tables using nested loops",
                "Find prime numbers using loop optimization",
                "Process data lists with filtering conditions"
            ],
            "requirements": [
                "Use proper indentation and code structure",
                "Implement input validation and error handling",
                "Use appropriate loop types for each problem",
                "Include break and continue statements where beneficial",
                "Add meaningful comments explaining logic"
            ]
        }
    
    def get_starter_code(self) -> str:
        """Get starter code template."""
        return '''
# Control Flow Exercise - Logic and Loops

import random

# 1. Number Guessing Game
def number_guessing_game():
    """Create a number guessing game with limited attempts."""
    target = random.randint(1, 100)
    max_attempts = 7
    attempts = 0
    
    print("Guess the number between 1 and 100!")
    print(f"You have {max_attempts} attempts.")
    
    # TODO: Implement game loop
    # - Get user input
    # - Check if guess is correct, too high, or too low
    # - Track attempts and provide feedback
    # - End game on correct guess or max attempts
    
    pass

# 2. Grade Calculator
def calculate_letter_grade(scores):
    """Calculate letter grades for a list of scores."""
    grades = []
    
    for score in scores:
        # TODO: Implement grade calculation logic
        # 90-100: A, 80-89: B, 70-79: C, 60-69: D, below 60: F
        pass
    
    return grades

# 3. Menu System
def interactive_menu():
    """Create an interactive menu system."""
    while True:
        print("\\n=== Main Menu ===")
        print("1. Calculate area")
        print("2. Convert temperature")
        print("3. Generate multiplication table")
        print("4. Exit")
        
        # TODO: Implement menu logic
        # - Get user choice
        # - Execute appropriate function
        # - Handle invalid input
        # - Exit condition
        
        pass

# 4. Pattern Generation
def generate_patterns():
    """Generate various patterns using nested loops."""
    
    # TODO: Create a right triangle pattern
    # *
    # **
    # ***
    # ****
    
    # TODO: Create a number pyramid
    #   1
    #  123
    # 12345
    
    pass

# Test your functions
if __name__ == "__main__":
    # Test the functions
    test_scores = [95, 87, 72, 65, 58, 91]
    print("Grade calculation test:")
    # grades = calculate_letter_grade(test_scores)
    # print(f"Scores: {test_scores}")
    # print(f"Grades: {grades}")
    
    print("\\nPattern generation:")
    # generate_patterns()
    
    print("\\nStarting guessing game:")
    # number_guessing_game()
'''
    
    def get_solution(self) -> str:
        """Get complete solution with explanations."""
        return '''
# Control Flow Exercise - Complete Solution

import random

print("=== Control Flow Exercise Solutions ===\\n")

# 1. Number Guessing Game
def number_guessing_game():
    """Advanced number guessing game with features."""
    target = random.randint(1, 100)
    max_attempts = 7
    attempts = 0
    
    print(f"🎯 Guess the number between 1 and 100!")
    print(f"You have {max_attempts} attempts.\\n")
    
    while attempts < max_attempts:
        try:
            # Get user input with validation
            guess = int(input(f"Attempt {attempts + 1}/{max_attempts}: Enter your guess: "))
            attempts += 1
            
            # Check guess against target
            if guess == target:
                print(f"🎉 Congratulations! You found the number {target} in {attempts} attempts!")
                return True
            elif guess < target:
                remaining = max_attempts - attempts
                if remaining > 0:
                    print(f"📈 Too low! Try a higher number. ({remaining} attempts left)")
                else:
                    print(f"📈 Too low! No attempts remaining.")
            else:  # guess > target
                remaining = max_attempts - attempts
                if remaining > 0:
                    print(f"📉 Too high! Try a lower number. ({remaining} attempts left)")
                else:
                    print(f"📉 Too high! No attempts remaining.")
            
            # Check if out of attempts
            if attempts == max_attempts:
                print(f"💀 Game over! The number was {target}")
                return False
                
        except ValueError:
            print("❌ Please enter a valid number!")
            # Don't count invalid input as an attempt
            attempts -= 1
    
    return False

# 2. Advanced Grade Calculator
def calculate_letter_grade(scores):
    """Calculate letter grades with detailed analysis."""
    grades = []
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    
    for score in scores:
        # Validate score
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            grade = 'Invalid'
        elif score >= 90:
            grade = 'A'
        elif score >= 80:
            grade = 'B'
        elif score >= 70:
            grade = 'C'
        elif score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        grades.append(grade)
        if grade in grade_counts:
            grade_counts[grade] += 1
    
    # Calculate statistics
    valid_scores = [s for s in scores if isinstance(s, (int, float)) and 0 <= s <= 100]
    if valid_scores:
        avg_score = sum(valid_scores) / len(valid_scores)
        max_score = max(valid_scores)
        min_score = min(valid_scores)
        
        print(f"📊 Grade Analysis:")
        print(f"   Average: {avg_score:.1f}")
        print(f"   Highest: {max_score}")
        print(f"   Lowest:  {min_score}")
        print(f"   Distribution: {grade_counts}")
    
    return grades

# 3. Interactive Menu System
def interactive_menu():
    """Comprehensive menu system with multiple options."""
    
    def calculate_area():
        """Calculate area of different shapes."""
        print("\\n--- Area Calculator ---")
        print("1. Rectangle")
        print("2. Circle")
        print("3. Triangle")
        
        try:
            choice = int(input("Choose shape (1-3): "))
            
            if choice == 1:
                length = float(input("Enter length: "))
                width = float(input("Enter width: "))
                area = length * width
                print(f"Rectangle area: {area:.2f}")
            elif choice == 2:
                radius = float(input("Enter radius: "))
                area = 3.14159 * radius ** 2
                print(f"Circle area: {area:.2f}")
            elif choice == 3:
                base = float(input("Enter base: "))
                height = float(input("Enter height: "))
                area = 0.5 * base * height
                print(f"Triangle area: {area:.2f}")
            else:
                print("Invalid choice!")
                
        except ValueError:
            print("Please enter valid numbers!")
    
    def convert_temperature():
        """Convert between temperature scales."""
        print("\\n--- Temperature Converter ---")
        print("1. Celsius to Fahrenheit")
        print("2. Fahrenheit to Celsius")
        
        try:
            choice = int(input("Choose conversion (1-2): "))
            temp = float(input("Enter temperature: "))
            
            if choice == 1:
                fahrenheit = (temp * 9/5) + 32
                print(f"{temp}°C = {fahrenheit:.1f}°F")
            elif choice == 2:
                celsius = (temp - 32) * 5/9
                print(f"{temp}°F = {celsius:.1f}°C")
            else:
                print("Invalid choice!")
                
        except ValueError:
            print("Please enter valid numbers!")
    
    def multiplication_table():
        """Generate multiplication table."""
        print("\\n--- Multiplication Table ---")
        try:
            number = int(input("Enter number for multiplication table: "))
            size = int(input("Enter table size (default 10): ") or "10")
            
            print(f"\\nMultiplication table for {number}:")
            for i in range(1, size + 1):
                result = number * i
                print(f"{number} × {i:2d} = {result:3d}")
                
        except ValueError:
            print("Please enter valid numbers!")
    
    # Main menu loop
    while True:
        print("\\n" + "="*30)
        print("      🧮 CALCULATOR MENU")
        print("="*30)
        print("1. 📐 Calculate area")
        print("2. 🌡️  Convert temperature") 
        print("3. ✖️  Multiplication table")
        print("4. 🎯 Number guessing game")
        print("5. 📊 Grade calculator")
        print("6. 🚪 Exit")
        print("="*30)
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == '1':
                calculate_area()
            elif choice == '2':
                convert_temperature()
            elif choice == '3':
                multiplication_table()
            elif choice == '4':
                number_guessing_game()
            elif choice == '5':
                scores_input = input("Enter scores separated by commas: ")
                try:
                    scores = [float(x.strip()) for x in scores_input.split(',')]
                    grades = calculate_letter_grade(scores)
                    print(f"\\nScores: {scores}")
                    print(f"Grades: {grades}")
                except ValueError:
                    print("Invalid score format!")
            elif choice == '6':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice! Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\\n\\n👋 Goodbye!")
            break

# 4. Advanced Pattern Generation
def generate_patterns():
    """Generate various patterns using nested loops."""
    
    print("=== Pattern Generation ===\\n")
    
    # Pattern 1: Right triangle
    print("1. Right Triangle Pattern:")
    size = 5
    for i in range(1, size + 1):
        print('*' * i)
    
    print("\\n2. Number Triangle:")
    for i in range(1, size + 1):
        numbers = ' '.join(str(j) for j in range(1, i + 1))
        print(numbers)
    
    print("\\n3. Centered Number Pyramid:")
    for i in range(1, size + 1):
        # Create spaces for centering
        spaces = ' ' * (size - i)
        # Create number sequence
        numbers = ''.join(str(j) for j in range(1, i + 1))
        print(spaces + numbers)
    
    print("\\n4. Diamond Pattern:")
    # Upper half
    for i in range(1, size + 1):
        spaces = ' ' * (size - i)
        stars = '*' * (2 * i - 1)
        print(spaces + stars)
    
    # Lower half
    for i in range(size - 1, 0, -1):
        spaces = ' ' * (size - i)
        stars = '*' * (2 * i - 1)
        print(spaces + stars)
    
    print("\\n5. Multiplication Table Grid:")
    print("   ", end="")
    for i in range(1, 6):
        print(f"{i:3}", end="")
    print()
    
    for i in range(1, 6):
        print(f"{i:2}:", end="")
        for j in range(1, 6):
            print(f"{i*j:3}", end="")
        print()

# 5. Prime Number Finder
def find_primes(limit):
    """Find prime numbers up to a given limit using optimized algorithm."""
    print(f"\\nFinding prime numbers up to {limit}:")
    
    if limit < 2:
        print("No primes less than 2")
        return []
    
    primes = []
    
    for num in range(2, limit + 1):
        is_prime = True
        
        # Only check up to square root for efficiency
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break  # Early exit when factor found
        
        if is_prime:
            primes.append(num)
    
    print(f"Found {len(primes)} primes: {primes}")
    return primes

# 6. Data Processing with Filtering
def process_student_data():
    """Process student data with various filtering conditions."""
    students = [
        {"name": "Alice", "age": 16, "grade": 95, "subjects": ["Math", "Science"]},
        {"name": "Bob", "age": 17, "grade": 87, "subjects": ["English", "History"]},
        {"name": "Charlie", "age": 16, "grade": 92, "subjects": ["Math", "Art"]},
        {"name": "Diana", "age": 18, "grade": 78, "subjects": ["Science", "Music"]},
        {"name": "Eve", "age": 17, "grade": 88, "subjects": ["Math", "Science", "Art"]}
    ]
    
    print("\\n=== Student Data Processing ===")
    
    # Filter 1: High achievers (grade >= 90)
    high_achievers = []
    for student in students:
        if student["grade"] >= 90:
            high_achievers.append(student["name"])
    
    print(f"High achievers (≥90): {high_achievers}")
    
    # Filter 2: Math students
    math_students = []
    for student in students:
        if "Math" in student["subjects"]:
            math_students.append(student["name"])
    
    print(f"Math students: {math_students}")
    
    # Filter 3: Students by age with detailed info
    print("\\nStudents by age group:")
    for age in [16, 17, 18]:
        age_group = [s["name"] for s in students if s["age"] == age]
        if age_group:
            print(f"  Age {age}: {', '.join(age_group)}")
    
    # Calculate statistics
    total_grade = sum(student["grade"] for student in students)
    avg_grade = total_grade / len(students)
    max_grade = max(student["grade"] for student in students)
    min_grade = min(student["grade"] for student in students)
    
    print(f"\\nGrade Statistics:")
    print(f"  Average: {avg_grade:.1f}")
    print(f"  Highest: {max_grade}")
    print(f"  Lowest: {min_grade}")

# Demonstration and Testing
def run_all_demos():
    """Run all control flow demonstrations."""
    print("🚀 Starting Control Flow Demonstrations\\n")
    
    # 1. Grade calculation demo
    print("1. Grade Calculator Demo:")
    test_scores = [95, 87, 72, 65, 58, 91, 83, 76]
    grades = calculate_letter_grade(test_scores)
    print(f"   Scores: {test_scores}")
    print(f"   Grades: {grades}")
    
    # 2. Pattern generation
    print("\\n2. Pattern Generation:")
    generate_patterns()
    
    # 3. Prime number finder
    find_primes(30)
    
    # 4. Student data processing
    process_student_data()
    
    print("\\n✅ All demonstrations completed!")

# Main execution
if __name__ == "__main__":
    print("Control Flow Exercise - Choose an option:")
    print("1. Run all demonstrations")
    print("2. Interactive menu system")
    print("3. Number guessing game only")
    
    try:
        choice = input("\\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            run_all_demos()
        elif choice == '2':
            interactive_menu()
        elif choice == '3':
            number_guessing_game()
        else:
            print("Running all demos by default...")
            run_all_demos()
            
    except KeyboardInterrupt:
        print("\\n\\nProgram interrupted. Goodbye!")
'''
    
    def check_solution(self, code: str) -> Dict[str, Any]:
        """Check and validate the student's solution."""
        feedback = []
        score = 0
        max_score = 15
        
        # Check syntax
        syntax_check = self.validator.validate_syntax(code)
        if not syntax_check["valid"]:
            return {
                "score": 0,
                "max_score": max_score,
                "feedback": [f"Syntax Error: {syntax_check['message']}"],
                "suggestions": ["Fix syntax errors before proceeding"]
            }
        
        # Check for control flow structures
        control_flow_checks = [
            ("if ", "Conditional statements", 2),
            ("elif ", "Multiple conditions", 1),
            ("else:", "Else clause", 1),
            ("for ", "For loop", 2),
            ("while ", "While loop", 2),
            ("break", "Break statement", 1),
            ("continue", "Continue statement", 1),
            ("range(", "Range function for loops", 1),
            ("in ", "Membership operator", 1),
            ("try:", "Error handling", 1),
            ("except", "Exception handling", 1),
            ("def ", "Function definition", 1)
        ]
        
        for pattern, description, points in control_flow_checks:
            if pattern in code:
                feedback.append(f"✓ Used {description}")
                score += points
            else:
                feedback.append(f"✗ Missing {description}")
        
        # Check for complexity and best practices
        complexity_check = self.validator.check_complexity(code)
        if complexity_check["functions"]:
            complex_functions = [f for f in complexity_check["functions"] if f["complex"]]
            if not complex_functions:
                feedback.append("✓ Functions have appropriate complexity")
            else:
                feedback.append(f"⚠ Some functions are complex: {[f['name'] for f in complex_functions]}")
        
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
    
    def get_practice_problems(self) -> List[Dict[str, Any]]:
        """Get additional practice problems."""
        return [
            {
                "problem": "Create a function that prints the Fibonacci sequence up to n terms",
                "hint": "Use a loop with two variables to track the previous two numbers",
                "solution": "def fibonacci(n):\\n    a, b = 0, 1\\n    for i in range(n):\\n        print(a, end=' ')\\n        a, b = b, a + b"
            },
            {
                "problem": "Write a function to check if a year is a leap year",
                "hint": "A leap year is divisible by 4, except for century years which must be divisible by 400",
                "solution": "def is_leap_year(year):\\n    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)"
            },
            {
                "problem": "Create a password strength checker with multiple criteria",
                "hint": "Check length, uppercase, lowercase, digits, and special characters",
                "solution": "def check_password_strength(password):\\n    criteria = [\\n        len(password) >= 8,\\n        any(c.isupper() for c in password),\\n        any(c.islower() for c in password),\\n        any(c.isdigit() for c in password)\\n    ]\\n    return sum(criteria)"
            }
        ]
    
    def _get_suggestions(self, score: int, max_score: int) -> List[str]:
        """Get suggestions based on score."""
        percentage = (score / max_score) * 100
        
        if percentage >= 90:
            return [
                "Outstanding work on control flow structures!",
                "Try implementing more complex algorithms like sorting or searching.",
                "Consider optimizing your loops for better performance."
            ]
        elif percentage >= 70:
            return [
                "Good understanding of basic control flow.",
                "Practice nested loops and complex conditionals.",
                "Add more error handling to make your code robust."
            ]
        else:
            return [
                "Focus on basic if/else and loop structures first.",
                "Practice simple problems before attempting complex ones.",
                "Review the difference between for and while loops."
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