"""
Interactive REPL - Enhanced Python REPL with Learning Context

Provides an enhanced Python REPL with learning-specific features,
code suggestions, and contextual help for educational purposes.
"""

import argparse
import asyncio
import sys
import code
import readline
import rlcompleter
import io
import contextlib
from typing import Dict, List, Any, Optional, Callable
import inspect
import ast
import textwrap

from python_mastery_hub.cli.utils import colors
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)


class LearningREPL(code.InteractiveConsole):
    """Enhanced REPL with learning features."""
    
    def __init__(self, locals_dict: Optional[Dict] = None):
        """
        Initialize the learning REPL.
        
        Args:
            locals_dict: Local variables dictionary
        """
        super().__init__(locals_dict or {})
        
        self.command_history = []
        self.help_topics = self._initialize_help_topics()
        self.learning_mode = True
        self.show_tips = True
        self.auto_explain = False
        
        # Setup tab completion
        readline.set_completer(rlcompleter.Completer(self.locals).complete)
        readline.parse_and_bind("tab: complete")
        
        # Setup command history
        try:
            readline.read_history_file()
        except FileNotFoundError:
            pass
        
        # Add special commands to locals
        self._add_special_commands()
    
    def _add_special_commands(self) -> None:
        """Add special learning commands to the REPL."""
        self.locals.update({
            'help_topics': self._show_help_topics,
            'explain': self._explain_code,
            'tips': self._toggle_tips,
            'clear_screen': self._clear_screen,
            'learning_mode': self._toggle_learning_mode,
            'save_session': self._save_session,
            'load_examples': self._load_examples,
            'practice': self._start_practice,
            'quiz': self._start_quiz,
        })
    
    def _initialize_help_topics(self) -> Dict[str, str]:
        """Initialize help topics for the REPL."""
        return {
            'variables': """
Variables in Python:
- Assignment: name = value
- Multiple assignment: a, b, c = 1, 2, 3
- Swapping: a, b = b, a
- Type checking: type(variable)

Example:
>>> name = "Python"
>>> age = 30
>>> print(f"Hello {name}, you are {age} years old")
""",
            'data_types': """
Python Data Types:
- int: Whole numbers (42, -10)
- float: Decimal numbers (3.14, -2.5)
- str: Text ("Hello", 'World')
- bool: True/False
- list: [1, 2, 3]
- dict: {"key": "value"}
- tuple: (1, 2, 3)
- set: {1, 2, 3}

Try: type(42), type(3.14), type("hello")
""",
            'functions': """
Functions in Python:
- Definition: def function_name(parameters):
- Return values: return value
- Default parameters: def func(a, b=10):
- *args and **kwargs for variable arguments

Example:
>>> def greet(name, greeting="Hello"):
...     return f"{greeting}, {name}!"
>>> greet("Alice")
>>> greet("Bob", "Hi")
""",
            'loops': """
Loops in Python:
- for loop: for item in iterable:
- while loop: while condition:
- break: exit loop
- continue: skip to next iteration
- else clause: executes if loop completes normally

Example:
>>> for i in range(5):
...     print(f"Count: {i}")
>>> 
>>> numbers = [1, 2, 3, 4, 5]
>>> for num in numbers:
...     if num % 2 == 0:
...         print(f"{num} is even")
""",
            'conditionals': """
Conditional Statements:
- if condition:
- elif condition:
- else:
- Comparison operators: ==, !=, <, >, <=, >=
- Logical operators: and, or, not

Example:
>>> score = 85
>>> if score >= 90:
...     grade = "A"
... elif score >= 80:
...     grade = "B"
... else:
...     grade = "C"
>>> print(f"Grade: {grade}")
""",
            'lists': """
Lists in Python:
- Creation: my_list = [1, 2, 3]
- Access: my_list[0]
- Slicing: my_list[1:3]
- Methods: append(), remove(), pop(), insert()
- List comprehension: [x*2 for x in range(5)]

Example:
>>> fruits = ["apple", "banana", "orange"]
>>> fruits.append("grape")
>>> print(fruits[1:3])
>>> squares = [x**2 for x in range(1, 6)]
""",
            'dictionaries': """
Dictionaries in Python:
- Creation: my_dict = {"key": "value"}
- Access: my_dict["key"]
- Methods: keys(), values(), items(), get()
- Dict comprehension: {k: v for k, v in items}

Example:
>>> person = {"name": "Alice", "age": 30}
>>> person["city"] = "New York"
>>> for key, value in person.items():
...     print(f"{key}: {value}")
""",
            'classes': """
Classes in Python:
- Definition: class ClassName:
- Constructor: def __init__(self, parameters):
- Methods: def method_name(self, parameters):
- Inheritance: class Child(Parent):

Example:
>>> class Dog:
...     def __init__(self, name):
...         self.name = name
...     def bark(self):
...         return f"{self.name} says Woof!"
>>> buddy = Dog("Buddy")
>>> print(buddy.bark())
""",
        }
    
    def interact(self, banner: Optional[str] = None) -> None:
        """Start the interactive session with custom banner."""
        if banner is None:
            banner = self._create_banner()
        
        super().interact(banner)
    
    def _create_banner(self) -> str:
        """Create a custom banner for the REPL."""
        if not colors.supports_color():
            return """
Python Mastery Hub - Interactive Learning REPL
Type help_topics() for learning topics
Type tips() to toggle helpful tips
Type exit() or Ctrl+D to quit
"""
        
        return f"""
{colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║              🐍 Python Mastery Hub - Learning REPL 🐍         ║
╚══════════════════════════════════════════════════════════════╝{colors.RESET}

{colors.GREEN}Welcome to the enhanced learning REPL!{colors.RESET}

{colors.YELLOW}Special Commands:{colors.RESET}
  {colors.BLUE}help_topics(){colors.RESET}    - Show available help topics
  {colors.BLUE}explain(code){colors.RESET}    - Explain how code works
  {colors.BLUE}tips(){colors.RESET}           - Toggle helpful tips
  {colors.BLUE}practice(){colors.RESET}       - Start practice exercises
  {colors.BLUE}quiz(){colors.RESET}           - Start interactive quiz
  {colors.BLUE}clear_screen(){colors.RESET}   - Clear the screen

{colors.GRAY}Type exit() or Ctrl+D to quit{colors.RESET}
"""
    
    def push(self, line: str) -> bool:
        """Push a line to the interpreter and handle special features."""
        # Store command in history
        if line.strip():
            self.command_history.append(line)
        
        # Check for special commands
        if self._handle_special_commands(line):
            return False
        
        # Show tips if enabled
        if self.show_tips and self.learning_mode:
            self._show_contextual_tips(line)
        
        # Execute the line
        result = super().push(line)
        
        # Auto-explain if enabled
        if self.auto_explain and line.strip() and not result:
            self._explain_code(line)
        
        return result
    
    def _handle_special_commands(self, line: str) -> bool:
        """Handle special learning commands."""
        stripped = line.strip()
        
        if stripped == 'help_topics()':
            self._show_help_topics()
            return True
        elif stripped.startswith('explain(') and stripped.endswith(')'):
            # Extract code from explain() call
            code = stripped[8:-1].strip('\'"')
            self._explain_code(code)
            return True
        elif stripped == 'tips()':
            self._toggle_tips()
            return True
        elif stripped == 'clear_screen()':
            self._clear_screen()
            return True
        elif stripped == 'learning_mode()':
            self._toggle_learning_mode()
            return True
        elif stripped == 'practice()':
            self._start_practice()
            return True
        elif stripped == 'quiz()':
            self._start_quiz()
            return True
        
        return False
    
    def _show_help_topics(self) -> None:
        """Show available help topics."""
        colors.print_header("📚 Available Help Topics")
        
        for topic, description in self.help_topics.items():
            print(f"{colors.BLUE}{topic}{colors.RESET}")
            # Show first line of description
            first_line = description.strip().split('\n')[0]
            print(f"  {colors.GRAY}{first_line}{colors.RESET}")
        
        print(f"\n{colors.YELLOW}Usage:{colors.RESET} Type topic name to see details")
        print(f"Example: {colors.CYAN}variables{colors.RESET}")
    
    def _explain_code(self, code: str) -> None:
        """Provide explanation for code."""
        if not code or code in ['explain', 'explain()']:
            print(f"{colors.YELLOW}Usage: explain('your_code_here'){colors.RESET}")
            return
        
        try:
            # Parse the code to understand its structure
            tree = ast.parse(code)
            explanations = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    explanations.append("• Variable assignment detected")
                elif isinstance(node, ast.FunctionDef):
                    explanations.append(f"• Function definition: {node.name}")
                elif isinstance(node, ast.ClassDef):
                    explanations.append(f"• Class definition: {node.name}")
                elif isinstance(node, ast.For):
                    explanations.append("• For loop detected")
                elif isinstance(node, ast.While):
                    explanations.append("• While loop detected")
                elif isinstance(node, ast.If):
                    explanations.append("• Conditional statement detected")
                elif isinstance(node, ast.Import):
                    explanations.append("• Import statement")
                elif isinstance(node, ast.Call):
                    if hasattr(node.func, 'id'):
                        explanations.append(f"• Function call: {node.func.id}()")
            
            if explanations:
                print(f"{colors.GREEN}Code Analysis:{colors.RESET}")
                for explanation in set(explanations):  # Remove duplicates
                    print(f"  {explanation}")
            else:
                print(f"{colors.YELLOW}This appears to be a simple expression or statement.{colors.RESET}")
        
        except SyntaxError:
            print(f"{colors.RED}Invalid Python syntax in the provided code.{colors.RESET}")
        except Exception as e:
            print(f"{colors.RED}Could not analyze code: {e}{colors.RESET}")
    
    def _show_contextual_tips(self, line: str) -> None:
        """Show contextual tips based on the entered code."""
        stripped = line.strip()
        
        # Tips for common patterns
        if '=' in stripped and not any(op in stripped for op in ['==', '!=', '<=', '>=']):
            if stripped.count('=') == 1:
                print(f"{colors.GRAY}💡 Tip: You're assigning a value to a variable{colors.RESET}")
        
        elif stripped.startswith('def '):
            print(f"{colors.GRAY}💡 Tip: You're defining a function. Don't forget the colon and indentation!{colors.RESET}")
        
        elif stripped.startswith('class '):
            print(f"{colors.GRAY}💡 Tip: You're defining a class. Use PascalCase for class names.{colors.RESET}")
        
        elif stripped.startswith('for '):
            print(f"{colors.GRAY}💡 Tip: For loops iterate over sequences. Don't forget the colon!{colors.RESET}")
        
        elif stripped.startswith('if '):
            print(f"{colors.GRAY}💡 Tip: Conditional statements help control program flow.{colors.RESET}")
        
        elif 'import ' in stripped:
            print(f"{colors.GRAY}💡 Tip: Importing modules gives you access to additional functionality.{colors.RESET}")
    
    def _toggle_tips(self) -> None:
        """Toggle helpful tips on/off."""
        self.show_tips = not self.show_tips
        status = "enabled" if self.show_tips else "disabled"
        print(f"{colors.GREEN}Tips {status}{colors.RESET}")
    
    def _clear_screen(self) -> None:
        """Clear the screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self._create_banner())
    
    def _toggle_learning_mode(self) -> None:
        """Toggle learning mode features."""
        self.learning_mode = not self.learning_mode
        status = "enabled" if self.learning_mode else "disabled"
        print(f"{colors.GREEN}Learning mode {status}{colors.RESET}")
    
    def _save_session(self) -> None:
        """Save the current session to a file."""
        if not self.command_history:
            print(f"{colors.YELLOW}No commands to save{colors.RESET}")
            return
        
        filename = f"repl_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        try:
            with open(filename, 'w') as f:
                f.write("# Python Mastery Hub REPL Session\n")
                f.write(f"# Saved on {datetime.now().isoformat()}\n\n")
                for command in self.command_history:
                    f.write(f"{command}\n")
            
            print(f"{colors.GREEN}Session saved to {filename}{colors.RESET}")
        except Exception as e:
            print(f"{colors.RED}Failed to save session: {e}{colors.RESET}")
    
    def _load_examples(self, topic: str = None) -> None:
        """Load example code for a specific topic."""
        if not topic:
            print(f"{colors.YELLOW}Available topics:{colors.RESET}")
            for topic_name in self.help_topics.keys():
                print(f"  {colors.BLUE}{topic_name}{colors.RESET}")
            return
        
        if topic in self.help_topics:
            print(f"{colors.GREEN}Loading examples for: {topic}{colors.RESET}")
            print(self.help_topics[topic])
        else:
            print(f"{colors.RED}Topic '{topic}' not found{colors.RESET}")
    
    def _start_practice(self) -> None:
        """Start practice exercises."""
        exercises = [
            {
                'question': 'Create a variable named "age" and assign it the value 25',
                'solution': 'age = 25',
                'hint': 'Use the assignment operator (=)'
            },
            {
                'question': 'Create a list with the numbers 1, 2, 3, 4, 5',
                'solution': 'numbers = [1, 2, 3, 4, 5]',
                'hint': 'Use square brackets to create a list'
            },
            {
                'question': 'Write a function that returns the square of a number',
                'solution': 'def square(x):\n    return x ** 2',
                'hint': 'Use def to define a function, ** for exponentiation'
            }
        ]
        
        print(f"{colors.GREEN}🏃 Starting Practice Exercises{colors.RESET}\n")
        
        for i, exercise in enumerate(exercises, 1):
            print(f"{colors.BLUE}Exercise {i}:{colors.RESET} {exercise['question']}")
            
            user_input = input(f"{colors.CYAN}Your answer: {colors.RESET}")
            
            if user_input.strip() == exercise['solution']:
                print(f"{colors.GREEN}✅ Correct!{colors.RESET}\n")
            else:
                print(f"{colors.YELLOW}💡 Hint: {exercise['hint']}{colors.RESET}")
                print(f"{colors.GRAY}Solution: {exercise['solution']}{colors.RESET}\n")
    
    def _start_quiz(self) -> None:
        """Start an interactive quiz."""
        questions = [
            {
                'question': 'What keyword is used to define a function in Python?',
                'options': ['a) function', 'b) def', 'c) func', 'd) define'],
                'answer': 'b',
                'explanation': 'The "def" keyword is used to define functions in Python.'
            },
            {
                'question': 'Which of these is a mutable data type?',
                'options': ['a) tuple', 'b) string', 'c) list', 'd) int'],
                'answer': 'c',
                'explanation': 'Lists are mutable, meaning they can be changed after creation.'
            },
            {
                'question': 'How do you create a comment in Python?',
                'options': ['a) // comment', 'b) /* comment */', 'c) # comment', 'd) -- comment'],
                'answer': 'c',
                'explanation': 'Comments in Python start with the # symbol.'
            }
        ]
        
        print(f"{colors.GREEN}🧠 Starting Python Quiz{colors.RESET}\n")
        score = 0
        
        for i, q in enumerate(questions, 1):
            print(f"{colors.BLUE}Question {i}:{colors.RESET} {q['question']}")
            for option in q['options']:
                print(f"  {option}")
            
            answer = input(f"{colors.CYAN}Your answer (a/b/c/d): {colors.RESET}").lower()
            
            if answer == q['answer']:
                print(f"{colors.GREEN}✅ Correct!{colors.RESET}")
                score += 1
            else:
                print(f"{colors.RED}❌ Incorrect.{colors.RESET}")
            
            print(f"{colors.GRAY}Explanation: {q['explanation']}{colors.RESET}\n")
        
        print(f"{colors.BOLD}Quiz Complete!{colors.RESET}")
        print(f"Score: {colors.GREEN}{score}/{len(questions)}{colors.RESET}")
        
        if score == len(questions):
            print(f"{colors.GREEN}🎉 Perfect score! Excellent work!{colors.RESET}")
        elif score >= len(questions) // 2:
            print(f"{colors.YELLOW}👍 Good job! Keep learning!{colors.RESET}")
        else:
            print(f"{colors.BLUE}📚 Keep studying and try again!{colors.RESET}")


async def execute(args: argparse.Namespace) -> int:
    """Execute the interactive REPL."""
    try:
        # Initialize the learning REPL
        repl = LearningREPL()
        
        # Check for specific mode
        if hasattr(args, 'mode'):
            if args.mode == 'basic':
                repl.learning_mode = False
                repl.show_tips = False
            elif args.mode == 'advanced':
                repl.auto_explain = True
        
        # Start the interactive session
        try:
            repl.interact()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{colors.YELLOW}👋 Thanks for using Python Mastery Hub REPL!{colors.RESET}")
        
        # Save history
        try:
            readline.write_history_file()
        except:
            pass
        
        return 0
    
    except Exception as e:
        logger.error(f"REPL failed to start: {e}")
        colors.print_error(f"REPL failed to start: {e}")
        return 1


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Setup the REPL command parser."""
    parser.add_argument(
        '--mode',
        choices=['basic', 'learning', 'advanced'],
        default='learning',
        help='REPL mode (default: learning)'
    )
    
    parser.add_argument(
        '--no-tips',
        action='store_true',
        help='Disable helpful tips'
    )
    
    parser.add_argument(
        '--auto-explain',
        action='store_true',
        help='Automatically explain code after execution'
    )