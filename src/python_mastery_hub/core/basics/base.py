"""
Base utilities and common functionality for the Python Basics module.
"""

from typing import Any, Dict, List, Union, Callable
import sys
import inspect
import ast


class CodeValidator:
    """Validates Python code for common issues and best practices."""
    
    @staticmethod
    def validate_syntax(code: str) -> Dict[str, Any]:
        """Validate Python syntax."""
        try:
            ast.parse(code)
            return {"valid": True, "message": "Syntax is valid"}
        except SyntaxError as e:
            return {
                "valid": False,
                "message": f"Syntax error: {e.msg}",
                "line": e.lineno,
                "offset": e.offset
            }
    
    @staticmethod
    def check_naming_conventions(code: str) -> List[str]:
        """Check for proper naming conventions."""
        issues = []
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.islower() or '_' not in node.name and len(node.name) > 8:
                        issues.append(f"Function '{node.name}' should use snake_case")
                
                elif isinstance(node, ast.ClassDef):
                    if not node.name[0].isupper():
                        issues.append(f"Class '{node.name}' should use PascalCase")
                
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id.isupper() and len(target.id) < 3:
                                issues.append(f"Constant '{target.id}' should be descriptive")
        
        except SyntaxError:
            pass  # Syntax issues handled elsewhere
        
        return issues
    
    @staticmethod
    def check_complexity(code: str) -> Dict[str, Any]:
        """Check code complexity metrics."""
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count statements in function
                    statements = sum(1 for _ in ast.walk(node) if isinstance(_, ast.stmt))
                    functions.append({
                        "name": node.name,
                        "statements": statements,
                        "complex": statements > 20
                    })
            
            return {"functions": functions}
        
        except SyntaxError:
            return {"functions": []}


class ExampleRunner:
    """Safely executes code examples and captures output."""
    
    def __init__(self):
        self.output_buffer = []
    
    def capture_output(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Capture function output and return value."""
        import io
        import contextlib
        
        # Capture stdout
        stdout_buffer = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(stdout_buffer):
                result = func(*args, **kwargs)
            
            output = stdout_buffer.getvalue()
            
            return {
                "success": True,
                "result": result,
                "output": output,
                "error": None
            }
        
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "output": stdout_buffer.getvalue(),
                "error": str(e)
            }
    
    def safe_eval(self, expression: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Safely evaluate a Python expression."""
        if context is None:
            context = {}
        
        try:
            # Basic safety checks
            forbidden = ['import', '__', 'exec', 'eval', 'open', 'input']
            if any(word in expression for word in forbidden):
                raise ValueError("Expression contains forbidden operations")
            
            result = eval(expression, {"__builtins__": {}}, context)
            
            return {
                "success": True,
                "result": result,
                "error": None
            }
        
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }


class ConceptTester:
    """Tests understanding of Python concepts."""
    
    def __init__(self):
        self.test_cases = {}
    
    def create_variable_test(self) -> Dict[str, Any]:
        """Create tests for variable concepts."""
        return {
            "test_name": "Variable Assignment",
            "questions": [
                {
                    "question": "What will be the value of 'c' after: a, b = 1, 2; c = a; a = 3",
                    "options": ["1", "2", "3", "Error"],
                    "correct": 0,
                    "explanation": "c gets the value of a (1) before a is reassigned to 3"
                },
                {
                    "question": "Which is the correct way to swap variables a and b?",
                    "options": [
                        "a, b = b, a",
                        "temp = a; a = b; b = temp",
                        "Both are correct",
                        "Neither is correct"
                    ],
                    "correct": 2,
                    "explanation": "Both methods work, but Python's tuple unpacking is more elegant"
                }
            ]
        }
    
    def create_data_type_test(self) -> Dict[str, Any]:
        """Create tests for data type concepts."""
        return {
            "test_name": "Data Types",
            "questions": [
                {
                    "question": "What is the result of: bool([])",
                    "options": ["True", "False", "Error", "None"],
                    "correct": 1,
                    "explanation": "Empty lists are falsy in Python"
                },
                {
                    "question": "Which data type is immutable?",
                    "options": ["list", "dict", "set", "tuple"],
                    "correct": 3,
                    "explanation": "Tuples are immutable sequences"
                }
            ]
        }
    
    def grade_test(self, answers: List[int], test: Dict[str, Any]) -> Dict[str, Any]:
        """Grade a test and provide feedback."""
        questions = test["questions"]
        correct_count = 0
        feedback = []
        
        for i, (answer, question) in enumerate(zip(answers, questions)):
            is_correct = answer == question["correct"]
            if is_correct:
                correct_count += 1
            
            feedback.append({
                "question_num": i + 1,
                "correct": is_correct,
                "explanation": question["explanation"],
                "correct_answer": question["options"][question["correct"]]
            })
        
        score = (correct_count / len(questions)) * 100
        
        return {
            "score": score,
            "correct": correct_count,
            "total": len(questions),
            "feedback": feedback,
            "grade": self._calculate_letter_grade(score)
        }
    
    def _calculate_letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


class PythonVersionChecker:
    """Check Python version compatibility for examples."""
    
    @staticmethod
    def get_version_info() -> Dict[str, Any]:
        """Get current Python version information."""
        version = sys.version_info
        return {
            "major": version.major,
            "minor": version.minor,
            "micro": version.micro,
            "version_string": f"{version.major}.{version.minor}.{version.micro}",
            "is_python3": version.major >= 3
        }
    
    @staticmethod
    def check_feature_compatibility(feature: str) -> bool:
        """Check if a Python feature is available in current version."""
        version = sys.version_info
        
        feature_requirements = {
            "f_strings": (3, 6),
            "assignment_expressions": (3, 8),
            "positional_only_params": (3, 8),
            "match_statements": (3, 10),
            "exception_groups": (3, 11),
            "type_unions": (3, 10)
        }
        
        if feature in feature_requirements:
            required_major, required_minor = feature_requirements[feature]
            return (version.major, version.minor) >= (required_major, required_minor)
        
        return True  # Assume compatible if unknown


class InteractiveDemo:
    """Create interactive demonstrations for concepts."""
    
    def __init__(self):
        self.demo_history = []
    
    def variable_scope_demo(self) -> Dict[str, Any]:
        """Interactive variable scope demonstration."""
        global_var = "global"
        
        def outer_function():
            outer_var = "outer"
            
            def inner_function():
                inner_var = "inner"
                return {
                    "inner": inner_var,
                    "outer": outer_var,
                    "global": global_var
                }
            
            return inner_function()
        
        result = outer_function()
        
        return {
            "demo": "Variable Scope",
            "result": result,
            "explanation": "Inner functions can access variables from outer scopes (LEGB rule)"
        }
    
    def mutable_vs_immutable_demo(self) -> Dict[str, Any]:
        """Demonstrate mutable vs immutable types."""
        # Immutable example
        original_tuple = (1, 2, 3)
        tuple_copy = original_tuple
        # tuple_copy[0] = 10  # This would raise an error
        
        # Mutable example
        original_list = [1, 2, 3]
        list_copy = original_list
        list_copy[0] = 10  # This modifies both lists
        
        return {
            "demo": "Mutable vs Immutable",
            "immutable_result": {
                "original": original_tuple,
                "copy": tuple_copy,
                "are_same": original_tuple is tuple_copy
            },
            "mutable_result": {
                "original": original_list,
                "copy": list_copy,
                "are_same": original_list is list_copy,
                "both_modified": True
            },
            "explanation": "Mutable objects can be changed in place, immutable objects cannot"
        }
    
    def record_demo(self, demo_name: str, result: Any):
        """Record a demo execution for later reference."""
        self.demo_history.append({
            "name": demo_name,
            "result": result,
            "timestamp": __import__("time").time()
        })


# Utility functions for common operations
def format_code_output(code: str, output: str) -> str:
    """Format code and output for display."""
    return f"""
Code:
{code}

Output:
{output}
""".strip()


def create_progress_tracker():
    """Create a simple progress tracker for learning."""
    return {
        "completed_topics": [],
        "current_topic": None,
        "exercises_completed": 0,
        "total_exercises": 0,
        "start_time": __import__("time").time()
    }


def calculate_completion_percentage(tracker: Dict[str, Any], total_topics: int) -> float:
    """Calculate learning progress percentage."""
    completed = len(tracker.get("completed_topics", []))
    return (completed / total_topics) * 100 if total_topics > 0 else 0