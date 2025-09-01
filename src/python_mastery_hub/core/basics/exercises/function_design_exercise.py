"""
Function Design Exercise - Create well-structured functions with proper parameters and documentation.
"""

from typing import Dict, Any, List, Union, Optional, Callable
import math
from ..base import CodeValidator, ExampleRunner


class FunctionDesignExercise:
    """Interactive exercise for practicing function design and implementation."""
    
    def __init__(self):
        self.title = "Function Design Challenge"
        self.description = "Design functions for a calculator system with proper parameters and error handling"
        self.difficulty = "medium"
        self.validator = CodeValidator()
        self.runner = ExampleRunner()
    
    def get_instructions(self) -> Dict[str, Any]:
        """Get comprehensive exercise instructions."""
        return {
            "title": self.title,
            "description": self.description,
            "objectives": [
                "Design functions with clear single responsibilities",
                "Implement proper parameter handling and validation",
                "Use different parameter types (positional, keyword, default)",
                "Add comprehensive error handling and edge cases",
                "Write clear docstrings with parameter and return documentation",
                "Create a cohesive calculator system with multiple functions"
            ],
            "tasks": [
                "Create basic arithmetic functions (+, -, *, /, **, %)",
                "Add input validation with appropriate error messages",
                "Implement advanced operations (factorial, square root, logarithm)",
                "Create a main calculator function that coordinates operations",
                "Add memory functions (store, recall, clear)",
                "Design a history tracking system for calculations"
            ],
            "requirements": [
                "All functions must have comprehensive docstrings",
                "Use type hints for parameters and return values",
                "Handle edge cases like division by zero, negative square roots",
                "Implement at least one function with *args or **kwargs",
                "Create functions that return multiple values using tuples",
                "Use default parameters appropriately"
            ]
        }
    
    def get_starter_code(self) -> str:
        """Get starter code template."""
        return '''
# Function Design Exercise - Calculator System

import math
from typing import Union, Tuple, List, Optional

class Calculator:
    """A comprehensive calculator with memory and history features."""
    
    def __init__(self):
        self.memory = 0.0
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        # TODO: Implement addition
        pass
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        # TODO: Implement subtraction
        pass
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        # TODO: Implement multiplication
        pass
    
    def divide(self, a: float, b: float) -> float:
        """Divide a by b.
        
        Raises:
            ValueError: If b is zero
        """
        # TODO: Implement division with error handling
        pass
    
    def power(self, base: float, exponent: float = 2) -> float:
        """Raise base to the power of exponent."""
        # TODO: Implement power function
        pass
    
    def calculate(self, operation: str, *args, **kwargs) -> float:
        """Perform calculation based on operation string.
        
        Args:
            operation: Operation name ('add', 'subtract', etc.)
            *args: Arguments for the operation
            **kwargs: Keyword arguments
            
        Returns:
            Result of the calculation
            
        Raises:
            ValueError: If operation is not supported
        """
        # TODO: Implement operation dispatcher
        pass
    
    def memory_store(self, value: float) -> None:
        """Store value in memory."""
        # TODO: Implement memory store
        pass
    
    def memory_recall(self) -> float:
        """Recall value from memory."""
        # TODO: Implement memory recall
        pass
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        # TODO: Return history list
        pass

# Test your calculator
if __name__ == "__main__":
    calc = Calculator()
    
    # Test basic operations
    print("Testing calculator...")
    # result = calc.add(5, 3)
    # print(f"5 + 3 = {result}")
    
    # Test error handling
    # try:
    #     calc.divide(10, 0)
    # except ValueError as e:
    #     print(f"Error caught: {e}")
'''
    
    def get_solution(self) -> str:
        """Get complete solution with explanations."""
        return '''
# Function Design Exercise - Complete Calculator Solution

import math
from typing import Union, Tuple, List, Optional, Dict, Any
from datetime import datetime

class AdvancedCalculator:
    """
    A comprehensive calculator with memory, history, and advanced operations.
    
    This calculator supports basic arithmetic, advanced mathematical functions,
    memory operations, and maintains a history of all calculations.
    """
    
    def __init__(self):
        """Initialize calculator with empty memory and history."""
        self.memory: float = 0.0
        self.history: List[Dict[str, Any]] = []
        self._operation_count = 0
    
    def _log_operation(self, operation: str, args: tuple, result: float, error: str = None) -> None:
        """Log operation to history with timestamp."""
        self._operation_count += 1
        log_entry = {
            'id': self._operation_count,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation': operation,
            'arguments': args,
            'result': result,
            'error': error
        }
        self.history.append(log_entry)
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Add two numbers.
        
        Args:
            a: First number (int or float)
            b: Second number (int or float)
            
        Returns:
            float: Sum of a and b
            
        Example:
            >>> calc = AdvancedCalculator()
            >>> calc.add(5, 3)
            8.0
        """
        try:
            result = float(a) + float(b)
            self._log_operation('add', (a, b), result)
            return result
        except (TypeError, ValueError) as e:
            error_msg = f"Invalid input types for addition: {type(a)}, {type(b)}"
            self._log_operation('add', (a, b), None, error_msg)
            raise ValueError(error_msg) from e
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Subtract b from a.
        
        Args:
            a: Minuend (number to subtract from)
            b: Subtrahend (number to subtract)
            
        Returns:
            float: Difference (a - b)
        """
        try:
            result = float(a) - float(b)
            self._log_operation('subtract', (a, b), result)
            return result
        except (TypeError, ValueError) as e:
            error_msg = f"Invalid input types for subtraction: {type(a)}, {type(b)}"
            self._log_operation('subtract', (a, b), None, error_msg)
            raise ValueError(error_msg) from e
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: First factor
            b: Second factor
            
        Returns:
            float: Product of a and b
        """
        try:
            result = float(a) * float(b)
            self._log_operation('multiply', (a, b), result)
            return result
        except (TypeError, ValueError) as e:
            error_msg = f"Invalid input types for multiplication: {type(a)}, {type(b)}"
            self._log_operation('multiply', (a, b), None, error_msg)
            raise ValueError(error_msg) from e
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Divide a by b.
        
        Args:
            a: Dividend (number to be divided)
            b: Divisor (number to divide by)
            
        Returns:
            float: Quotient (a / b)
            
        Raises:
            ValueError: If b is zero (division by zero)
            ValueError: If inputs are not numeric
        """
        try:
            a_float = float(a)
            b_float = float(b)
            
            if b_float == 0:
                error_msg = f"Division by zero: {a} / {b}"
                self._log_operation('divide', (a, b), None, error_msg)
                raise ValueError(error_msg)
            
            result = a_float / b_float
            self._log_operation('divide', (a, b), result)
            return result
            
        except (TypeError, ValueError) as e:
            if "Division by zero" not in str(e):
                error_msg = f"Invalid input types for division: {type(a)}, {type(b)}"
                self._log_operation('divide', (a, b), None, error_msg)
                raise ValueError(error_msg) from e
            else:
                raise
    
    def power(self, base: Union[int, float], exponent: Union[int, float] = 2) -> float:
        """
        Raise base to the power of exponent.
        
        Args:
            base: Base number
            exponent: Exponent (default: 2 for square)
            
        Returns:
            float: base^exponent
            
        Raises:
            ValueError: For invalid operations like negative base with fractional exponent
        """
        try:
            base_float = float(base)
            exp_float = float(exponent)
            
            # Check for problematic cases
            if base_float < 0 and not exp_float.is_integer():
                error_msg = f"Cannot raise negative base {base} to fractional power {exponent}"
                self._log_operation('power', (base, exponent), None, error_msg)
                raise ValueError(error_msg)
            
            result = base_float ** exp_float
            self._log_operation('power', (base, exponent), result)
            return result
            
        except (TypeError, ValueError) as e:
            if "Cannot raise negative base" not in str(e):
                error_msg = f"Invalid input types for power: {type(base)}, {type(exponent)}"
                self._log_operation('power', (base, exponent), None, error_msg)
                raise ValueError(error_msg) from e
            else:
                raise
    
    def calculate(self, operation: str, *args, **kwargs) -> float:
        """
        Perform calculation based on operation string.
        
        Args:
            operation: Operation name ('add', 'subtract', 'multiply', 'divide', 'power')
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            float: Result of the calculation
            
        Raises:
            ValueError: If operation is not supported
            
        Example:
            >>> calc = AdvancedCalculator()
            >>> calc.calculate('add', 5, 3)
            8.0
            >>> calc.calculate('power', 2, exponent=3)
            8.0
        """
        operations = {
            'add': self.add,
            'subtract': self.subtract,
            'multiply': self.multiply,
            'divide': self.divide,
            'power': self.power
        }
        
        operation_lower = operation.lower()
        
        if operation_lower not in operations:
            available_ops = ', '.join(operations.keys())
            error_msg = f"Unknown operation '{operation}'. Available: {available_ops}"
            raise ValueError(error_msg)
        
        try:
            return operations[operation_lower](*args, **kwargs)
        except TypeError as e:
            error_msg = f"Invalid arguments for {operation}: {e}"
            raise ValueError(error_msg) from e
    
    def memory_store(self, value: Union[int, float]) -> None:
        """
        Store value in calculator memory.
        
        Args:
            value: Value to store in memory
        """
        try:
            self.memory = float(value)
            self._log_operation('memory_store', (value,), self.memory)
        except (TypeError, ValueError) as e:
            error_msg = f"Cannot store non-numeric value in memory: {value}"
            raise ValueError(error_msg) from e
    
    def memory_recall(self) -> float:
        """
        Recall value from calculator memory.
        
        Returns:
            float: Value stored in memory
        """
        self._log_operation('memory_recall', (), self.memory)
        return self.memory
    
    def memory_clear(self) -> None:
        """Clear calculator memory (set to 0)."""
        self.memory = 0.0
        self._log_operation('memory_clear', (), 0.0)
    
    def get_history(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get calculation history.
        
        Args:
            count: Number of recent entries to return (None for all)
            
        Returns:
            List[Dict]: List of calculation history entries
        """
        if count is None:
            return self.history.copy()
        else:
            return self.history[-count:] if count > 0 else []
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()
        self._operation_count = 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get calculator usage statistics.
        
        Returns:
            Dict: Statistics about calculator usage
        """
        if not self.history:
            return {"total_operations": 0, "operations_by_type": {}, "average_result": 0}
        
        operations_by_type = {}
        valid_results = []
        
        for entry in self.history:
            op_type = entry['operation']
            operations_by_type[op_type] = operations_by_type.get(op_type, 0) + 1
            
            if entry['result'] is not None and entry['operation'] not in ['memory_recall', 'memory_clear']:
                valid_results.append(entry['result'])
        
        return {
            "total_operations": len(self.history),
            "operations_by_type": operations_by_type,
            "average_result": sum(valid_results) / len(valid_results) if valid_results else 0,
            "memory_value": self.memory
        }
    
    def __str__(self) -> str:
        """String representation of calculator state."""
        return f"AdvancedCalculator(memory={self.memory}, operations={len(self.history)})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()

# Demonstration function
def run_calculator_demo():
    """Comprehensive demonstration of calculator features."""
    print("=== Advanced Calculator Demonstration ===\\n")
    
    calc = AdvancedCalculator()
    
    print("1. Basic Arithmetic Operations:")
    print("-" * 30)
    
    # Basic operations
    operations = [
        ('add', 15, 7),
        ('subtract', 20, 8),
        ('multiply', 6, 7),
        ('divide', 84, 12),
        ('power', 3, 4)
    ]
    
    for op, a, b in operations:
        try:
            result = calc.calculate(op, a, b)
            print(f"{a} {op} {b} = {result}")
        except ValueError as e:
            print(f"Error: {e}")
    
    print("\\n2. Error Handling Examples:")
    print("-" * 27)
    
    # Error scenarios
    try:
        calc.divide(10, 0)
    except ValueError as e:
        print(f"Division by zero: {e}")
    
    print("\\n3. Memory Operations:")
    print("-" * 20)
    
    calc.memory_store(42)
    print(f"Stored 42 in memory")
    
    memory_value = calc.memory_recall()
    print(f"Memory recall: {memory_value}")
    
    calc.memory_clear()
    print(f"Memory cleared: {calc.memory_recall()}")
    
    print("\\n4. Calculator Statistics:")
    print("-" * 23)
    
    stats = calc.get_statistics()
    print(f"Total operations: {stats['total_operations']}")
    print(f"Operations by type: {stats['operations_by_type']}")
    
    print("\\n5. Recent History:")
    print("-" * 16)
    
    recent_history = calc.get_history(5)
    for entry in recent_history:
        if entry['error']:
            print(f"{entry['timestamp']}: {entry['operation']} -> ERROR: {entry['error']}")
        else:
            print(f"{entry['timestamp']}: {entry['operation']} -> {entry['result']}")

# Main execution
if __name__ == "__main__":
    run_calculator_demo()
'''
    
    def check_solution(self, code: str) -> Dict[str, Any]:
        """Check and validate the student's solution."""
        feedback = []
        score = 0
        max_score = 20
        
        # Check syntax
        syntax_check = self.validator.validate_syntax(code)
        if not syntax_check["valid"]:
            return {
                "score": 0,
                "max_score": max_score,
                "feedback": [f"Syntax Error: {syntax_check['message']}"],
                "suggestions": ["Fix syntax errors before proceeding"]
            }
        
        # Check for required function components
        function_checks = [
            ("def ", "Function definitions", 3),
            ('"""', "Docstrings", 2),
            ("Args:", "Parameter documentation", 1),
            ("Returns:", "Return value documentation", 1),
            ("Raises:", "Exception documentation", 1),
            ("try:", "Error handling", 2),
            ("except", "Exception catching", 2),
            ("raise", "Exception raising", 1),
            ("float(", "Type conversion", 1),
            ("Union", "Type hints", 1),
            ("self.", "Instance methods", 2),
            ("def __init__", "Constructor", 1),
            ("*args", "Variable arguments", 1),
            ("**kwargs", "Keyword arguments", 1)
        ]
        
        for pattern, description, points in function_checks:
            if pattern in code:
                feedback.append(f"✓ Used {description}")
                score += points
            else:
                feedback.append(f"✗ Missing {description}")
        
        # Check for specific calculator operations
        operations = ["add", "subtract", "multiply", "divide", "power"]
        for op in operations:
            if f"def {op}" in code:
                feedback.append(f"✓ Implemented {op} operation")
            else:
                feedback.append(f"✗ Missing {op} operation")
        
        # Check naming conventions
        naming_issues = self.validator.check_naming_conventions(code)
        if not naming_issues:
            feedback.append("✓ Good naming conventions")
            score += 1
        else:
            feedback.extend([f"⚠ Naming: {issue}" for issue in naming_issues[:3]])
        
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
                "problem": "Create a function that calculates compound interest with flexible parameters",
                "hint": "Use default parameters for rate and compounding frequency",
                "solution": "def compound_interest(principal, rate=0.05, time=1, n=1):\\n    return principal * (1 + rate/n)**(n*time)"
            },
            {
                "problem": "Design a function that finds the greatest common divisor using recursion",
                "hint": "Use the Euclidean algorithm: gcd(a,b) = gcd(b, a%b)",
                "solution": "def gcd(a, b):\\n    if b == 0:\\n        return a\\n    return gcd(b, a % b)"
            },
            {
                "problem": "Create a function that validates and formats phone numbers",
                "hint": "Handle multiple input formats and return a standardized format",
                "solution": "def format_phone(phone):\\n    digits = ''.join(c for c in phone if c.isdigit())\\n    if len(digits) == 10:\\n        return f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'\\n    raise ValueError('Invalid phone number')"
            }
        ]
    
    def _get_suggestions(self, score: int, max_score: int) -> List[str]:
        """Get suggestions based on score."""
        percentage = (score / max_score) * 100
        
        if percentage >= 90:
            return [
                "Outstanding function design! Your code shows mastery of Python functions.",
                "Consider exploring advanced topics like decorators and closures.",
                "Try implementing more complex algorithms using your function design skills."
            ]
        elif percentage >= 70:
            return [
                "Good function structure. Focus on improving error handling.",
                "Add more comprehensive docstrings with examples.",
                "Practice with type hints and parameter validation."
            ]
        else:
            return [
                "Focus on basic function definition and parameter handling first.",
                "Review how to write proper docstrings with Args and Returns sections.",
                "Practice simple functions before attempting complex calculator operations.",
                "Study the solution to understand proper function structure and error handling."
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