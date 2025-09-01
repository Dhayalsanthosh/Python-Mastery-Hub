"""
Interactive Exercises Runner

Provides an interactive environment for running and managing exercises
with real-time feedback, hints, and progress tracking.
"""

import argparse
import asyncio
import sys
import io
import contextlib
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import traceback
import ast

from python_mastery_hub.cli.utils import colors, progress_bar
from python_mastery_hub.utils.progress_calculator import ProgressCalculator
from python_mastery_hub.utils.achievement_engine import AchievementEngine
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)


class Exercise:
    """Represents a single interactive exercise."""
    
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        instructions: str,
        starter_code: str = "",
        solution: str = "",
        hints: List[str] = None,
        test_cases: List[Dict[str, Any]] = None,
        difficulty: str = "intermediate"
    ):
        self.id = id
        self.title = title
        self.description = description
        self.instructions = instructions
        self.starter_code = starter_code
        self.solution = solution
        self.hints = hints or []
        self.test_cases = test_cases or []
        self.difficulty = difficulty
        self.attempts = 0
        self.hints_used = 0
        self.completed = False


class ExerciseRunner:
    """Interactive exercise runner and manager."""
    
    def __init__(self):
        self.progress_calc = ProgressCalculator()
        self.achievement_engine = AchievementEngine()
        self.exercises = self._load_exercises()
        self.current_exercise = None
    
    def _load_exercises(self) -> Dict[str, List[Exercise]]:
        """Load exercise definitions by module."""
        return {
            'basics': self._get_basics_exercises(),
            'oop': self._get_oop_exercises(),
            'advanced': self._get_advanced_exercises(),
            'data_structures': self._get_data_structures_exercises(),
            'algorithms': self._get_algorithms_exercises(),
            'async_programming': self._get_async_exercises(),
            'web_development': self._get_web_exercises(),
            'data_science': self._get_data_science_exercises(),
            'testing': self._get_testing_exercises()
        }
    
    def _get_basics_exercises(self) -> List[Exercise]:
        """Get basic Python exercises."""
        return [
            Exercise(
                id="variables_intro",
                title="Variable Assignment",
                description="Learn basic variable assignment and types",
                instructions="Create variables of different types and perform basic operations",
                starter_code="""# Create variables here
name = 
age = 
height = 
is_student = 

# Print them
""",
                solution="""name = "Alice"
age = 25
height = 5.6
is_student = True

print(f"Name: {name}")
print(f"Age: {age}")
print(f"Height: {height}")
print(f"Student: {is_student}")""",
                hints=[
                    "Remember to use quotes for strings",
                    "Boolean values are True or False",
                    "Use f-strings for formatted output"
                ],
                test_cases=[
                    {"input": "", "expected_output": "Name: Alice\nAge: 25\nHeight: 5.6\nStudent: True"},
                ],
                difficulty="beginner"
            ),
            Exercise(
                id="loops_practice",
                title="Loop Practice",
                description="Practice using for and while loops",
                instructions="Create a function that counts from 1 to n using a for loop",
                starter_code="""def count_to_n(n):
    # Your code here
    pass

# Test your function
count_to_n(5)""",
                solution="""def count_to_n(n):
    for i in range(1, n + 1):
        print(i)

count_to_n(5)""",
                hints=[
                    "Use range(1, n + 1) to include n",
                    "Print each number in the loop",
                    "Remember range is exclusive of the end value"
                ]
            ),
            Exercise(
                id="list_operations",
                title="List Operations",
                description="Practice common list operations",
                instructions="Create a function that processes a list of numbers",
                starter_code="""def process_numbers(numbers):
    # Calculate sum, average, and find max
    # Return as a dictionary
    pass

# Test
result = process_numbers([1, 2, 3, 4, 5])
print(result)""",
                solution="""def process_numbers(numbers):
    total = sum(numbers)
    average = total / len(numbers) if numbers else 0
    maximum = max(numbers) if numbers else None
    
    return {
        'sum': total,
        'average': average,
        'max': maximum
    }

result = process_numbers([1, 2, 3, 4, 5])
print(result)""",
                hints=[
                    "Use built-in functions sum() and max()",
                    "Check for empty lists to avoid errors",
                    "Return a dictionary with the results"
                ]
            )
        ]
    
    def _get_oop_exercises(self) -> List[Exercise]:
        """Get OOP exercises."""
        return [
            Exercise(
                id="simple_class",
                title="Create a Simple Class",
                description="Learn to define classes and methods",
                instructions="Create a Person class with name, age, and a greet method",
                starter_code="""class Person:
    def __init__(self, name, age):
        # Initialize attributes
        pass
    
    def greet(self):
        # Return greeting message
        pass

# Test your class
person = Person("Alice", 30)
print(person.greet())""",
                solution="""class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hello, I'm {self.name} and I'm {self.age} years old"

person = Person("Alice", 30)
print(person.greet())""",
                hints=[
                    "Use self.attribute_name to store instance variables",
                    "The greet method should return a formatted string",
                    "Don't forget the self parameter in methods"
                ]
            )
        ]
    
    def _get_advanced_exercises(self) -> List[Exercise]:
        """Get advanced Python exercises."""
        return [
            Exercise(
                id="decorator_practice",
                title="Create a Timing Decorator",
                description="Build a decorator that measures function execution time",
                instructions="Create a decorator that prints how long a function takes to run",
                starter_code="""import time
from functools import wraps

def timing_decorator(func):
    # Your decorator code here
    pass

@timing_decorator
def slow_function():
    time.sleep(0.1)
    return "Done!"

result = slow_function()
print(result)""",
                solution="""import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function():
    time.sleep(0.1)
    return "Done!"

result = slow_function()
print(result)""",
                hints=[
                    "Use @wraps(func) to preserve function metadata",
                    "Capture start time before calling the function",
                    "Calculate duration after the function completes"
                ],
                difficulty="advanced"
            )
        ]
    
    def _get_data_structures_exercises(self) -> List[Exercise]:
        """Get data structures exercises."""
        return []
    
    def _get_algorithms_exercises(self) -> List[Exercise]:
        """Get algorithms exercises."""
        return []
    
    def _get_async_exercises(self) -> List[Exercise]:
        """Get async programming exercises."""
        return []
    
    def _get_web_exercises(self) -> List[Exercise]:
        """Get web development exercises."""
        return []
    
    def _get_data_science_exercises(self) -> List[Exercise]:
        """Get data science exercises."""
        return []
    
    def _get_testing_exercises(self) -> List[Exercise]:
        """Get testing exercises."""
        return []
    
    async def show_menu(self) -> None:
        """Show the main exercise menu."""
        colors.print_header("Interactive Exercises")
        
        print(f"{colors.BOLD}Available Modules:{colors.RESET}")
        for i, (module_id, exercises) in enumerate(self.exercises.items(), 1):
            module_name = module_id.replace('_', ' ').title()
            exercise_count = len(exercises)
            print(f"  {i}. {module_name} ({exercise_count} exercises)")
        
        print(f"  0. Exit")
        
        while True:
            try:
                choice = input(f"\n{colors.CYAN}Select module (0-{len(self.exercises)}): {colors.RESET}")
                choice = int(choice)
                
                if choice == 0:
                    break
                elif 1 <= choice <= len(self.exercises):
                    module_id = list(self.exercises.keys())[choice - 1]
                    await self.show_module_exercises(module_id)
                else:
                    colors.print_error("Invalid choice. Please try again.")
                    
            except (ValueError, KeyboardInterrupt):
                break
    
    async def show_module_exercises(self, module_id: str) -> None:
        """Show exercises for a specific module."""
        if module_id not in self.exercises:
            colors.print_error(f"Module '{module_id}' not found")
            return
        
        exercises = self.exercises[module_id]
        module_name = module_id.replace('_', ' ').title()
        
        colors.print_header(f"{module_name} Exercises")
        
        if not exercises:
            print(f"{colors.YELLOW}No exercises available for this module yet.{colors.RESET}")
            input("Press Enter to continue...")
            return
        
        print(f"{colors.BOLD}Available Exercises:{colors.RESET}")
        for i, exercise in enumerate(exercises, 1):
            status = self._get_exercise_status(module_id, exercise.id)
            difficulty_color = self._get_difficulty_color(exercise.difficulty)
            
            print(f"  {i}. {status} {exercise.title}")
            print(f"     {exercise.description}")
            print(f"     Difficulty: {difficulty_color}{exercise.difficulty.title()}{colors.RESET}")
        
        print(f"  0. Back to modules")
        
        while True:
            try:
                choice = input(f"\n{colors.CYAN}Select exercise (0-{len(exercises)}): {colors.RESET}")
                choice = int(choice)
                
                if choice == 0:
                    break
                elif 1 <= choice <= len(exercises):
                    exercise = exercises[choice - 1]
                    await self.run_exercise(module_id, exercise)
                else:
                    colors.print_error("Invalid choice. Please try again.")
                    
            except (ValueError, KeyboardInterrupt):
                break
    
    async def run_exercise(self, module_id: str, exercise: Exercise) -> None:
        """Run an interactive exercise."""
        self.current_exercise = exercise
        exercise.attempts += 1
        
        colors.print_header(f"Exercise: {exercise.title}")
        
        print(f"{colors.BOLD}Description:{colors.RESET}")
        print(f"  {exercise.description}")
        print(f"\n{colors.BOLD}Instructions:{colors.RESET}")
        print(f"  {exercise.instructions}")
        
        # Show starter code if available
        if exercise.starter_code:
            print(f"\n{colors.BOLD}Starter Code:{colors.RESET}")
            colors.print_code_block(exercise.starter_code)
        
        print(f"\n{colors.BOLD}Commands:{colors.RESET}")
        print("  run - Execute your code")
        print("  hint - Get a hint")
        print("  solution - Show solution")
        print("  reset - Reset to starter code")
        print("  quit - Exit exercise")
        
        user_code = exercise.starter_code
        
        while True:
            try:
                command = input(f"\n{colors.CYAN}Enter command or code: {colors.RESET}").strip()
                
                if command.lower() == 'quit':
                    break
                elif command.lower() == 'run':
                    await self._execute_code(user_code, exercise)
                elif command.lower() == 'hint':
                    self._show_hint(exercise)
                elif command.lower() == 'solution':
                    self._show_solution(exercise)
                elif command.lower() == 'reset':
                    user_code = exercise.starter_code
                    print(f"{colors.GREEN}Code reset to starter template{colors.RESET}")
                elif command.lower().startswith('code '):
                    # Allow multiline code input
                    user_code = await self._get_multiline_code()
                else:
                    # Treat as code to add
                    if user_code and not user_code.endswith('\n'):
                        user_code += '\n'
                    user_code += command
                    
            except KeyboardInterrupt:
                break
        
        # Update progress if completed
        if exercise.completed:
            self.progress_calc.mark_topic_completed(
                module_id,
                exercise.id,
                score=self._calculate_score(exercise),
                time_spent=5  # Approximate time
            )
    
    async def _execute_code(self, code: str, exercise: Exercise) -> None:
        """Execute user code and provide feedback."""
        if not code.strip():
            colors.print_error("No code to execute")
            return
        
        print(f"\n{colors.BLUE}Executing code...{colors.RESET}")
        
        # Capture output
        old_stdout = sys.stdout
        captured_output = io.StringIO()
        
        try:
            sys.stdout = captured_output
            
            # Create execution environment
            exec_globals = {
                '__builtins__': __builtins__,
                'print': print,
                'input': lambda prompt="": "test_input",  # Mock input for exercises
            }
            
            # Execute code
            exec(code, exec_globals)
            
            output = captured_output.getvalue()
            
            # Check if exercise is completed correctly
            if self._check_solution(code, output, exercise):
                exercise.completed = True
                colors.print_success("Exercise completed successfully!")
                
                # Show completion stats
                score = self._calculate_score(exercise)
                print(f"Score: {score:.1f}%")
                print(f"Attempts: {exercise.attempts}")
                print(f"Hints used: {exercise.hints_used}")
            else:
                colors.print_warning("Exercise not yet complete. Keep trying!")
            
            # Show output
            if output:
                print(f"\n{colors.BOLD}Output:{colors.RESET}")
                print(output)
            
        except Exception as e:
            colors.print_error(f"Error executing code: {e}")
            if "SyntaxError" in str(type(e)):
                print(f"{colors.YELLOW}Hint: Check your syntax carefully{colors.RESET}")
        finally:
            sys.stdout = old_stdout
    
    def _check_solution(self, code: str, output: str, exercise: Exercise) -> bool:
        """Check if the user's solution is correct."""
        # This is a simplified check - in practice, you'd have more sophisticated testing
        if exercise.test_cases:
            for test_case in exercise.test_cases:
                expected = test_case.get('expected_output', '')
                if expected and expected.strip() not in output.strip():
                    return False
        
        # Basic checks based on exercise content
        if "count_to_n" in exercise.id and "for" in code and "range" in code:
            return True
        elif "process_numbers" in exercise.id and "sum(" in code and "max(" in code:
            return True
        elif "Person" in code and "def __init__" in code and "def greet" in code:
            return True
        
        return False
    
    def _show_hint(self, exercise: Exercise) -> None:
        """Show a hint for the current exercise."""
        if exercise.hints_used >= len(exercise.hints):
            colors.print_warning("No more hints available")
            return
        
        hint = exercise.hints[exercise.hints_used]
        exercise.hints_used += 1
        
        print(f"\n{colors.YELLOW}Hint {exercise.hints_used}/{len(exercise.hints)}:{colors.RESET}")
        print(f"  {hint}")
    
    def _show_solution(self, exercise: Exercise) -> None:
        """Show the solution for the current exercise."""
        if not exercise.solution:
            colors.print_warning("No solution available for this exercise")
            return
        
        confirm = input(f"{colors.YELLOW}Are you sure you want to see the solution? (y/n): {colors.RESET}")
        if confirm.lower() != 'y':
            return
        
        print(f"\n{colors.BOLD}Solution:{colors.RESET}")
        colors.print_code_block(exercise.solution)
        
        exercise.completed = True  # Mark as completed if they view solution
    
    async def _get_multiline_code(self) -> str:
        """Get multiline code input from user."""
        print(f"{colors.CYAN}Enter your code (press Ctrl+D or type 'END' on a new line to finish):{colors.RESET}")
        
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
        except EOFError:
            pass
        
        return '\n'.join(lines)
    
    def _get_exercise_status(self, module_id: str, exercise_id: str) -> str:
        """Get completion status for an exercise."""
        is_completed = self.progress_calc.is_topic_completed(module_id, exercise_id)
        return f"{colors.GREEN}[DONE]{colors.RESET}" if is_completed else f"{colors.GRAY}[TODO]{colors.RESET}"
    
    def _get_difficulty_color(self, difficulty: str) -> str:
        """Get color for difficulty level."""
        difficulty_colors = {
            'beginner': colors.GREEN,
            'intermediate': colors.YELLOW,
            'advanced': colors.RED
        }
        return difficulty_colors.get(difficulty.lower(), colors.GRAY)
    
    def _calculate_score(self, exercise: Exercise) -> float:
        """Calculate exercise completion score."""
        base_score = 100.0
        
        # Deduct points for hints used
        hint_penalty = min(exercise.hints_used * 10, 50)
        
        # Deduct points for multiple attempts
        attempt_penalty = min((exercise.attempts - 1) * 5, 25)
        
        return max(base_score - hint_penalty - attempt_penalty, 25.0)


async def execute(args: argparse.Namespace) -> int:
    """Execute the interactive exercises command."""
    try:
        runner = ExerciseRunner()
        await runner.show_menu()
        return 0
    
    except Exception as e:
        logger.error(f"Interactive exercises failed: {e}")
        colors.print_error(f"Failed to run exercises: {e}")
        return 1


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Setup the exercises command parser."""
    parser.add_argument(
        '--module', '-m',
        help='Start with a specific module'
    )
    
    parser.add_argument(
        '--difficulty', '-d',
        choices=['beginner', 'intermediate', 'advanced'],
        help='Filter by difficulty level'
    )