"""
Demo Command - Interactive Code Demonstrations

Provides command-line interface for running interactive code demonstrations
and examples across all learning modules with live execution and explanations.
"""

import argparse
import asyncio
import importlib
import sys
import io
import contextlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import inspect

from python_mastery_hub.cli.utils import colors, progress_bar
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)


class CodeDemo:
    """Represents a single code demonstration."""
    
    def __init__(
        self,
        name: str,
        description: str,
        code: str,
        explanation: str,
        expected_output: Optional[str] = None,
        interactive: bool = False
    ):
        self.name = name
        self.description = description
        self.code = code
        self.explanation = explanation
        self.expected_output = expected_output
        self.interactive = interactive


class DemoRunner:
    """Manages demo execution and interactive demonstrations."""
    
    def __init__(self):
        self.module_demos = self._discover_demos()
    
    def _discover_demos(self) -> Dict[str, Dict[str, Any]]:
        """Discover available demonstrations across all modules."""
        return {
            'basics': {
                'name': 'Python Basics',
                'demos': [
                    'variables_demo',
                    'data_types_demo',
                    'control_flow_demo',
                    'functions_demo',
                    'error_handling_demo'
                ],
                'color': colors.GREEN,
                'icon': '📚'
            },
            'oop': {
                'name': 'Object-Oriented Programming',
                'demos': [
                    'classes_demo',
                    'inheritance_demo',
                    'polymorphism_demo',
                    'encapsulation_demo',
                    'design_patterns_demo'
                ],
                'color': colors.BLUE,
                'icon': '🏗️'
            },
            'advanced': {
                'name': 'Advanced Python',
                'demos': [
                    'decorators_demo',
                    'generators_demo',
                    'context_managers_demo',
                    'metaclasses_demo',
                    'descriptors_demo'
                ],
                'color': colors.MAGENTA,
                'icon': '🚀'
            },
            'data_structures': {
                'name': 'Data Structures',
                'demos': [
                    'builtin_collections_demo',
                    'custom_structures_demo',
                    'performance_demo',
                    'advanced_collections_demo'
                ],
                'color': colors.CYAN,
                'icon': '📊'
            },
            'algorithms': {
                'name': 'Algorithms',
                'demos': [
                    'sorting_demo',
                    'searching_demo',
                    'graph_algorithms_demo',
                    'dynamic_programming_demo'
                ],
                'color': colors.YELLOW,
                'icon': '⚡'
            },
            'async_programming': {
                'name': 'Async Programming',
                'demos': [
                    'asyncio_demo',
                    'threading_demo',
                    'multiprocessing_demo',
                    'concurrent_futures_demo'
                ],
                'color': colors.LIGHT_MAGENTA,
                'icon': '🔄'
            },
            'web_development': {
                'name': 'Web Development',
                'demos': [
                    'flask_demo',
                    'fastapi_demo',
                    'database_demo',
                    'rest_api_demo',
                    'websocket_demo'
                ],
                'color': colors.RED,
                'icon': '🌐'
            },
            'data_science': {
                'name': 'Data Science',
                'demos': [
                    'numpy_demo',
                    'pandas_demo',
                    'visualization_demo',
                    'statistics_demo',
                    'ml_demo'
                ],
                'color': colors.LIGHT_BLUE,
                'icon': '📈'
            },
            'testing': {
                'name': 'Testing & Quality',
                'demos': [
                    'unittest_demo',
                    'pytest_demo',
                    'mocking_demo',
                    'tdd_demo',
                    'integration_demo'
                ],
                'color': colors.LIGHT_GREEN,
                'icon': '🧪'
            }
        }
    
    def list_available_demos(self, module_id: Optional[str] = None) -> None:
        """List all available demonstrations."""
        colors.print_header("🎬 Available Code Demonstrations")
        
        modules_to_show = [module_id] if module_id else self.module_demos.keys()
        
        for mod_id in modules_to_show:
            if mod_id not in self.module_demos:
                colors.print_error(f"Module '{mod_id}' not found")
                continue
            
            module = self.module_demos[mod_id]
            color = module['color']
            icon = module['icon']
            
            colors.print_subheader(f"{icon} {color}{module['name']}{colors.RESET}")
            
            for i, demo in enumerate(module['demos'], 1):
                demo_name = demo.replace('_demo', '').replace('_', ' ').title()
                print(f"  {i:2d}. {demo_name}")
                print(f"      Command: {colors.GRAY}python-mastery-hub demo {mod_id} {demo}{colors.RESET}")
            
            print()
    
    async def run_demo(
        self, 
        module_id: str, 
        demo_name: str, 
        interactive: bool = False,
        step_by_step: bool = False
    ) -> None:
        """
        Run a specific demonstration.
        
        Args:
            module_id: Module identifier
            demo_name: Demo name
            interactive: Enable interactive mode
            step_by_step: Run demo step by step
        """
        if module_id not in self.module_demos:
            colors.print_error(f"Unknown module: {module_id}")
            return
        
        module = self.module_demos[module_id]
        if demo_name not in module['demos']:
            colors.print_error(f"Demo '{demo_name}' not found in module '{module_id}'")
            return
        
        icon = module['icon']
        color = module['color']
        demo_title = demo_name.replace('_demo', '').replace('_', ' ').title()
        
        colors.print_header(f"{icon} {color}{demo_title} Demonstration{colors.RESET}")
        
        try:
            # Load demo content
            demo_content = await self._load_demo_content(module_id, demo_name)
            
            if step_by_step:
                await self._run_step_by_step_demo(demo_content, interactive)
            else:
                await self._run_full_demo(demo_content, interactive)
        
        except Exception as e:
            logger.error(f"Demo execution failed: {e}")
            colors.print_error(f"Demo failed to run: {e}")
    
    async def _load_demo_content(self, module_id: str, demo_name: str) -> List[CodeDemo]:
        """Load demonstration content from module."""
        try:
            # Try to import the demo module
            if module_id == 'advanced':
                module_path = f"python_mastery_hub.core.advanced.{demo_name}"
            else:
                module_path = f"python_mastery_hub.core.{module_id}.examples.{demo_name}"
            
            demo_module = importlib.import_module(module_path)
            
            # Extract demos from module
            demos = []
            
            # Look for demo functions or classes
            for attr_name in dir(demo_module):
                if attr_name.startswith('_'):
                    continue
                
                attr = getattr(demo_module, attr_name)
                
                if callable(attr) and hasattr(attr, '__doc__') and attr.__doc__:
                    # Function-based demo
                    source_code = inspect.getsource(attr)
                    demo = CodeDemo(
                        name=attr_name.replace('_', ' ').title(),
                        description=attr.__doc__.strip(),
                        code=source_code,
                        explanation=attr.__doc__.strip(),
                        interactive=True
                    )
                    demos.append(demo)
            
            # If no demos found, create a generic one
            if not demos:
                demos.append(await self._create_generic_demo(module_id, demo_name))
            
            return demos
        
        except ImportError:
            # Create a placeholder demo
            return [await self._create_generic_demo(module_id, demo_name)]
    
    async def _create_generic_demo(self, module_id: str, demo_name: str) -> CodeDemo:
        """Create a generic demo for modules without specific demo content."""
        demo_title = demo_name.replace('_demo', '').replace('_', ' ').title()
        
        # Generic examples based on module type
        if module_id == 'basics':
            code = self._get_basics_demo_code(demo_name)
        elif module_id == 'oop':
            code = self._get_oop_demo_code(demo_name)
        elif module_id == 'advanced':
            code = self._get_advanced_demo_code(demo_name)
        else:
            code = f"""
# {demo_title} Demo
print("This is a demonstration of {demo_title}")
print("In a full implementation, this would show:")
print("- Practical examples")
print("- Interactive code execution")
print("- Step-by-step explanations")
"""
        
        return CodeDemo(
            name=demo_title,
            description=f"Interactive demonstration of {demo_title} concepts",
            code=code.strip(),
            explanation=f"This demo shows the fundamentals of {demo_title}",
            interactive=True
        )
    
    def _get_basics_demo_code(self, demo_name: str) -> str:
        """Get demo code for basics module."""
        demos = {
            'variables_demo': '''
# Variables and Assignment Demo
name = "Python Mastery Hub"
version = 1.0
is_active = True

print(f"Welcome to {name} v{version}")
print(f"Status: {'Active' if is_active else 'Inactive'}")

# Multiple assignment
x, y, z = 1, 2, 3
print(f"Multiple assignment: x={x}, y={y}, z={z}")

# Swapping variables
a, b = 10, 20
print(f"Before swap: a={a}, b={b}")
a, b = b, a
print(f"After swap: a={a}, b={b}")
''',
            'data_types_demo': '''
# Data Types Demo
# Integers
age = 25
print(f"Age: {age} (type: {type(age).__name__})")

# Floats
price = 19.99
print(f"Price: ${price} (type: {type(price).__name__})")

# Strings
message = "Hello, Python!"
print(f"Message: '{message}' (type: {type(message).__name__})")

# Booleans
is_valid = True
print(f"Valid: {is_valid} (type: {type(is_valid).__name__})")

# Lists
fruits = ["apple", "banana", "orange"]
print(f"Fruits: {fruits} (type: {type(fruits).__name__})")

# Dictionaries
person = {"name": "Alice", "age": 30}
print(f"Person: {person} (type: {type(person).__name__})")
''',
            'control_flow_demo': '''
# Control Flow Demo
# If-else statements
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Score: {score}, Grade: {grade}")

# For loops
print("\\nCounting to 5:")
for i in range(1, 6):
    print(f"Count: {i}")

# While loop
print("\\nCountdown:")
countdown = 3
while countdown > 0:
    print(f"T-minus {countdown}")
    countdown -= 1
print("Blast off! 🚀")

# List comprehension
squares = [x**2 for x in range(1, 6)]
print(f"\\nSquares: {squares}")
'''
        }
        return demos.get(demo_name, "# Demo code not available")
    
    def _get_oop_demo_code(self, demo_name: str) -> str:
        """Get demo code for OOP module."""
        demos = {
            'classes_demo': '''
# Classes and Objects Demo
class Dog:
    species = "Canis lupus"  # Class variable
    
    def __init__(self, name, age):
        self.name = name  # Instance variable
        self.age = age
    
    def bark(self):
        return f"{self.name} says Woof!"
    
    def get_info(self):
        return f"{self.name} is {self.age} years old"

# Create objects
buddy = Dog("Buddy", 3)
max_dog = Dog("Max", 5)

print(buddy.bark())
print(buddy.get_info())
print(f"Species: {Dog.species}")
''',
            'inheritance_demo': '''
# Inheritance Demo
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass
    
    def info(self):
        return f"This is {self.name}"

class Dog(Animal):
    def speak(self):
        return f"{self.name} barks: Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} meows: Meow!"

# Create instances
animals = [Dog("Buddy"), Cat("Whiskers")]

for animal in animals:
    print(animal.info())
    print(animal.speak())
    print()
'''
        }
        return demos.get(demo_name, "# OOP demo code not available")
    
    def _get_advanced_demo_code(self, demo_name: str) -> str:
        """Get demo code for advanced module."""
        demos = {
            'decorators_demo': '''
# Decorators Demo
import time
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
    """A function that takes some time to execute."""
    time.sleep(0.1)
    return "Task completed!"

# Usage
result = slow_function()
print(result)
''',
            'generators_demo': '''
# Generators Demo
def fibonacci_generator(n):
    """Generate Fibonacci sequence up to n numbers."""
    a, b = 0, 1
    count = 0
    while count < n:
        yield a
        a, b = b, a + b
        count += 1

# Using the generator
print("Fibonacci sequence (first 10 numbers):")
for num in fibonacci_generator(10):
    print(num, end=" ")
print()

# Generator expression
squares = (x**2 for x in range(1, 6))
print("\\nSquares using generator expression:")
for square in squares:
    print(square, end=" ")
print()
'''
        }
        return demos.get(demo_name, "# Advanced demo code not available")
    
    async def _run_full_demo(self, demos: List[CodeDemo], interactive: bool) -> None:
        """Run the complete demonstration."""
        for i, demo in enumerate(demos, 1):
            if len(demos) > 1:
                colors.print_subheader(f"Part {i}: {demo.name}")
            
            # Show explanation
            print(f"{colors.BLUE}📖 Explanation:{colors.RESET}")
            print(f"   {demo.explanation}")
            print()
            
            # Show code
            print(f"{colors.BLUE}💻 Code:{colors.RESET}")
            colors.print_code_block(demo.code)
            
            if interactive:
                choice = input(f"{colors.CYAN}Run this code? (y/n/q): {colors.RESET}").lower()
                if choice == 'q':
                    break
                elif choice == 'n':
                    continue
            
            # Execute code
            print(f"{colors.GREEN}▶️  Output:{colors.RESET}")
            await self._execute_code_safely(demo.code)
            
            if i < len(demos):
                input(f"\n{colors.GRAY}Press Enter to continue to next part...{colors.RESET}")
                print()
    
    async def _run_step_by_step_demo(self, demos: List[CodeDemo], interactive: bool) -> None:
        """Run demonstration step by step."""
        for demo in demos:
            colors.print_subheader(f"Step-by-Step: {demo.name}")
            
            # Split code into logical steps
            code_lines = demo.code.strip().split('\n')
            steps = self._group_code_into_steps(code_lines)
            
            for i, step in enumerate(steps, 1):
                print(f"{colors.YELLOW}Step {i}:{colors.RESET}")
                step_code = '\n'.join(step)
                colors.print_code_block(step_code)
                
                if interactive:
                    choice = input(f"{colors.CYAN}Execute this step? (y/n/q): {colors.RESET}").lower()
                    if choice == 'q':
                        return
                    elif choice == 'n':
                        continue
                
                print(f"{colors.GREEN}Output:{colors.RESET}")
                await self._execute_code_safely(step_code)
                
                if i < len(steps):
                    input(f"\n{colors.GRAY}Press Enter for next step...{colors.RESET}")
                print()
    
    def _group_code_into_steps(self, code_lines: List[str]) -> List[List[str]]:
        """Group code lines into logical steps."""
        steps = []
        current_step = []
        
        for line in code_lines:
            if line.strip() == '' and current_step:
                # Empty line - end current step
                steps.append(current_step)
                current_step = []
            elif line.strip().startswith('#') and current_step:
                # Comment starting new section
                steps.append(current_step)
                current_step = [line]
            else:
                current_step.append(line)
        
        if current_step:
            steps.append(current_step)
        
        return steps
    
    async def _execute_code_safely(self, code: str) -> None:
        """Execute code safely and capture output."""
        # Capture stdout
        old_stdout = sys.stdout
        captured_output = io.StringIO()
        
        try:
            sys.stdout = captured_output
            
            # Create a safe execution environment
            exec_globals = {
                '__builtins__': __builtins__,
                'print': print,
                'len': len,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sum': sum,
                'max': max,
                'min': min,
                'sorted': sorted,
                'type': type,
                'isinstance': isinstance,
                'time': __import__('time'),
                'datetime': __import__('datetime'),
                'functools': __import__('functools'),
                'itertools': __import__('itertools'),
            }
            
            # Execute the code
            exec(code, exec_globals)
            
        except Exception as e:
            print(f"{colors.RED}Error: {e}{colors.RESET}")
        finally:
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            if output:
                print(output.rstrip())
            else:
                print(f"{colors.GRAY}(No output){colors.RESET}")


async def execute(args: argparse.Namespace) -> int:
    """Execute the demo command."""
    runner = DemoRunner()
    
    try:
        # List available demos
        if hasattr(args, 'list_demos') and args.list_demos:
            module_id = getattr(args, 'module', None)
            runner.list_available_demos(module_id)
            return 0
        
        # Run specific demo
        if hasattr(args, 'module') and hasattr(args, 'demo') and args.module and args.demo:
            interactive = getattr(args, 'interactive', False)
            step_by_step = getattr(args, 'step_by_step', False)
            
            await runner.run_demo(args.module, args.demo, interactive, step_by_step)
            return 0
        
        # Show module demos
        if hasattr(args, 'module') and args.module:
            runner.list_available_demos(args.module)
            return 0
        
        # Default: show all available demos
        runner.list_available_demos()
        return 0
    
    except Exception as e:
        logger.error(f"Demo command failed: {e}")
        colors.print_error(f"Demo execution failed: {e}")
        return 1


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Setup the demo command parser."""
    parser.add_argument(
        'module',
        nargs='?',
        help='Module to demo (basics, oop, advanced, etc.)'
    )
    
    parser.add_argument(
        'demo',
        nargs='?',
        help='Specific demo to run'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        dest='list_demos',
        help='List available demonstrations'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run demo in interactive mode'
    )
    
    parser.add_argument(
        '--step-by-step', '-s',
        action='store_true',
        help='Run demo step by step'
    )