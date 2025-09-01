# src/python_mastery_hub/utils/code_execution.py
"""
Safe Code Execution Utilities - Secure Python Code Execution

Provides utilities for safely executing Python code with sandboxing, 
time limits, and security restrictions for educational purposes.
"""

import ast
import sys
import io
import traceback
import time
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set, Union
from contextlib import contextmanager, redirect_stdout, redirect_stderr
import threading
import queue
import logging

logger = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Exception raised during code execution."""
    pass


class ExecutionTimeout(ExecutionError):
    """Exception raised when code execution times out."""
    pass


class SecurityViolation(ExecutionError):
    """Exception raised when code violates security restrictions."""
    pass


class ExecutionResult:
    """Container for code execution results."""
    
    def __init__(
        self,
        success: bool,
        output: str = "",
        error: str = "",
        execution_time: float = 0.0,
        return_value: Any = None,
        exception: Optional[Exception] = None
    ):
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.return_value = return_value
        self.exception = exception
    
    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        result = f"Execution {status} (took {self.execution_time:.3f}s)\n"
        
        if self.output:
            result += f"Output:\n{self.output}\n"
        
        if self.error:
            result += f"Error:\n{self.error}\n"
        
        if self.return_value is not None:
            result += f"Return Value: {self.return_value}\n"
        
        return result


class SecurityChecker:
    """Validates code for security violations."""
    
    # Dangerous built-in functions
    DANGEROUS_BUILTINS = {
        'eval', 'exec', 'compile', '__import__', 'open', 'input',
        'raw_input', 'file', 'reload', 'vars', 'locals', 'globals',
        'dir', 'hasattr', 'getattr', 'setattr', 'delattr',
        'callable', 'classmethod', 'staticmethod', 'property'
    }
    
    # Dangerous modules
    DANGEROUS_MODULES = {
        'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib',
        'http', 'ftplib', 'smtplib', 'telnetlib', 'threading',
        'multiprocessing', 'pickle', 'marshal', 'shelve',
        'dbm', 'sqlite3', 'ctypes', 'importlib'
    }
    
    # Allowed modules for educational purposes
    ALLOWED_MODULES = {
        'math', 'random', 'datetime', 'time', 'json', 're',
        'collections', 'itertools', 'functools', 'operator',
        'string', 'decimal', 'fractions', 'statistics',
        'copy', 'pprint', 'enum', 'dataclasses', 'typing'
    }
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
    
    def check_code(self, code: str) -> Tuple[bool, List[str]]:
        """
        Check code for security violations.
        
        Args:
            code: Python code to check
            
        Returns:
            Tuple of (is_safe, violations)
        """
        violations = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            violations.append(f"Syntax error: {e}")
            return False, violations
        
        # Check AST nodes for dangerous operations
        for node in ast.walk(tree):
            violation = self._check_node(node)
            if violation:
                violations.append(violation)
        
        return len(violations) == 0, violations
    
    def _check_node(self, node: ast.AST) -> Optional[str]:
        """Check individual AST node for violations."""
        
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if self._is_dangerous_module(alias.name):
                    return f"Dangerous import: {alias.name}"
        
        elif isinstance(node, ast.ImportFrom):
            if node.module and self._is_dangerous_module(node.module):
                return f"Dangerous import from: {node.module}"
        
        # Check function calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self.DANGEROUS_BUILTINS:
                    return f"Dangerous function call: {node.func.id}"
            
            elif isinstance(node.func, ast.Attribute):
                # Check for dangerous method calls
                if hasattr(node.func, 'attr'):
                    if node.func.attr in ['system', 'popen', 'spawn']:
                        return f"Dangerous method call: {node.func.attr}"
        
        # Check attribute access
        elif isinstance(node, ast.Attribute):
            dangerous_attrs = {
                '__globals__', '__locals__', '__builtins__', '__code__',
                '__dict__', '__class__', '__bases__', '__subclasses__'
            }
            if node.attr in dangerous_attrs:
                return f"Dangerous attribute access: {node.attr}"
        
        # Check for dangerous subscripts (like __builtins__['eval'])
        elif isinstance(node, ast.Subscript):
            if isinstance(node.slice, ast.Constant):
                if isinstance(node.slice.value, str) and node.slice.value in self.DANGEROUS_BUILTINS:
                    return f"Suspicious subscript access: {node.slice.value}"
        
        return None
    
    def _is_dangerous_module(self, module_name: str) -> bool:
        """Check if module is dangerous."""
        if not self.strict_mode and module_name in self.ALLOWED_MODULES:
            return False
        
        # Check exact matches
        if module_name in self.DANGEROUS_MODULES:
            return True
        
        # Check prefixes for submodules
        for dangerous in self.DANGEROUS_MODULES:
            if module_name.startswith(dangerous + '.'):
                return True
        
        return False


class SafeCodeExecutor:
    """Executes Python code safely with restrictions."""
    
    def __init__(
        self,
        timeout: float = 5.0,
        max_output_length: int = 10000,
        strict_mode: bool = True
    ):
        self.timeout = timeout
        self.max_output_length = max_output_length
        self.security_checker = SecurityChecker(strict_mode)
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
            context: Optional context variables
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        
        # Security check
        is_safe, violations = self.security_checker.check_code(code)
        if not is_safe:
            return ExecutionResult(
                success=False,
                error=f"Security violations: {'; '.join(violations)}",
                execution_time=time.time() - start_time,
                exception=SecurityViolation('; '.join(violations))
            )
        
        # Prepare execution context
        exec_context = self._prepare_context(context)
        
        # Execute with timeout
        try:
            return self._execute_with_timeout(code, exec_context, start_time)
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                exception=e
            )
    
    def _prepare_context(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare safe execution context."""
        # Start with minimal builtins
        safe_builtins = {
            'abs', 'all', 'any', 'bin', 'bool', 'bytearray', 'bytes',
            'chr', 'complex', 'dict', 'divmod', 'enumerate', 'filter',
            'float', 'format', 'frozenset', 'hex', 'id', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min',
            'next', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
            'reversed', 'round', 'set', 'slice', 'sorted', 'str',
            'sum', 'tuple', 'type', 'zip'
        }
        
        # Create restricted builtins
        restricted_builtins = {}
        for name in safe_builtins:
            if hasattr(__builtins__, name):
                restricted_builtins[name] = getattr(__builtins__, name)
        
        # Add safe exceptions
        safe_exceptions = [
            'ArithmeticError', 'AssertionError', 'AttributeError',
            'EOFError', 'Exception', 'FloatingPointError', 'GeneratorExit',
            'ImportError', 'IndexError', 'KeyError', 'KeyboardInterrupt',
            'LookupError', 'MemoryError', 'NameError', 'NotImplementedError',
            'OSError', 'OverflowError', 'ReferenceError', 'RuntimeError',
            'StopIteration', 'SyntaxError', 'SystemError', 'TypeError',
            'UnboundLocalError', 'UnicodeError', 'ValueError', 'ZeroDivisionError'
        ]
        
        for exc_name in safe_exceptions:
            if hasattr(__builtins__, exc_name):
                restricted_builtins[exc_name] = getattr(__builtins__, exc_name)
        
        # Create execution context
        exec_context = {
            '__builtins__': restricted_builtins,
            '__name__': '__main__',
            '__doc__': None,
            '__package__': None
        }
        
        # Add user context if provided
        if context:
            exec_context.update(context)
        
        return exec_context
    
    def _execute_with_timeout(
        self, 
        code: str, 
        exec_context: Dict[str, Any], 
        start_time: float
    ) -> ExecutionResult:
        """Execute code with timeout using threading."""
        
        # Use queue to get results from thread
        result_queue = queue.Queue()
        
        def target():
            """Target function for threaded execution."""
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # Try to execute as expression first, then as statement
                    try:
                        # Attempt to evaluate as expression
                        tree = ast.parse(code, mode='eval')
                        compiled_code = compile(tree, '<string>', 'eval')
                        return_value = eval(compiled_code, exec_context)
                    except SyntaxError:
                        # Execute as statement
                        tree = ast.parse(code, mode='exec')
                        compiled_code = compile(tree, '<string>', 'exec')
                        exec(compiled_code, exec_context)
                        return_value = None
                
                output = stdout_capture.getvalue()
                error = stderr_capture.getvalue()
                
                # Truncate output if too long
                if len(output) > self.max_output_length:
                    output = output[:self.max_output_length] + "\n... (output truncated)"
                
                result_queue.put(ExecutionResult(
                    success=True,
                    output=output,
                    error=error,
                    execution_time=time.time() - start_time,
                    return_value=return_value
                ))
                
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                stderr_output = stderr_capture.getvalue()
                if stderr_output:
                    error_msg = stderr_output + "\n" + error_msg
                
                result_queue.put(ExecutionResult(
                    success=False,
                    output=stdout_capture.getvalue(),
                    error=error_msg,
                    execution_time=time.time() - start_time,
                    exception=e
                ))
        
        # Start execution thread
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        
        # Wait for result with timeout
        try:
            result = result_queue.get(timeout=self.timeout)
            return result
        except queue.Empty:
            # Timeout occurred
            return ExecutionResult(
                success=False,
                error=f"Execution timed out after {self.timeout} seconds",
                execution_time=self.timeout,
                exception=ExecutionTimeout(f"Timeout after {self.timeout}s")
            )


class CodeValidator:
    """Validates Python code syntax and structure."""
    
    @staticmethod
    def validate_syntax(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Python code syntax.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Parse error: {str(e)}"
    
    @staticmethod
    def get_code_complexity(code: str) -> Dict[str, int]:
        """
        Analyze code complexity metrics.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Dictionary with complexity metrics
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {'error': 1}
        
        metrics = {
            'lines': len(code.split('\n')),
            'functions': 0,
            'classes': 0,
            'imports': 0,
            'loops': 0,
            'conditionals': 0,
            'try_blocks': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['functions'] += 1
            elif isinstance(node, ast.ClassDef):
                metrics['classes'] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics['imports'] += 1
            elif isinstance(node, (ast.For, ast.While)):
                metrics['loops'] += 1
            elif isinstance(node, ast.If):
                metrics['conditionals'] += 1
            elif isinstance(node, ast.Try):
                metrics['try_blocks'] += 1
        
        return metrics
    
    @staticmethod
    def extract_functions(code: str) -> List[Dict[str, Any]]:
        """
        Extract function definitions from code.
        
        Args:
            code: Python code to analyze
            
        Returns:
            List of function information dictionaries
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'line_number': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'returns': node.returns is not None
                }
                functions.append(func_info)
        
        return functions


class TestRunner:
    """Runs tests against code solutions."""
    
    def __init__(self, executor: Optional[SafeCodeExecutor] = None):
        self.executor = executor or SafeCodeExecutor()
    
    def run_tests(
        self, 
        code: str, 
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run test cases against code.
        
        Args:
            code: Python code to test
            test_cases: List of test case dictionaries
            
        Returns:
            Test results summary
        """
        results = {
            'total_tests': len(test_cases),
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'test_results': []
        }
        
        for i, test_case in enumerate(test_cases):
            test_result = self._run_single_test(code, test_case, i)
            results['test_results'].append(test_result)
            
            if test_result['status'] == 'passed':
                results['passed'] += 1
            elif test_result['status'] == 'failed':
                results['failed'] += 1
            else:
                results['errors'] += 1
        
        results['success_rate'] = results['passed'] / results['total_tests'] if results['total_tests'] > 0 else 0
        
        return results
    
    def _run_single_test(
        self, 
        code: str, 
        test_case: Dict[str, Any], 
        test_index: int
    ) -> Dict[str, Any]:
        """Run a single test case."""
        
        test_result = {
            'test_index': test_index,
            'description': test_case.get('description', f'Test {test_index + 1}'),
            'status': 'error',
            'expected': test_case.get('expected'),
            'actual': None,
            'error': None,
            'execution_time': 0.0
        }
        
        try:
            # Prepare test code
            test_setup = test_case.get('setup', '')
            test_input = test_case.get('input', {})
            
            # Combine setup and main code
            full_code = f"{test_setup}\n{code}" if test_setup else code
            
            # Execute with test context
            result = self.executor.execute(full_code, test_input)
            
            test_result['execution_time'] = result.execution_time
            test_result['actual'] = result.return_value
            
            if not result.success:
                test_result['status'] = 'error'
                test_result['error'] = result.error
            else:
                # Check if result matches expected
                expected = test_case.get('expected')
                if expected is not None:
                    if self._compare_results(result.return_value, expected):
                        test_result['status'] = 'passed'
                    else:
                        test_result['status'] = 'failed'
                        test_result['error'] = f"Expected {expected}, got {result.return_value}"
                else:
                    # No expected value, just check if it ran without error
                    test_result['status'] = 'passed'
        
        except Exception as e:
            test_result['status'] = 'error'
            test_result['error'] = str(e)
        
        return test_result
    
    def _compare_results(self, actual: Any, expected: Any) -> bool:
        """Compare actual and expected results."""
        try:
            if isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)):
                return list(actual) == list(expected)
            elif isinstance(expected, dict) and isinstance(actual, dict):
                return actual == expected
            elif isinstance(expected, float) and isinstance(actual, float):
                return abs(actual - expected) < 1e-9
            else:
                return actual == expected
        except Exception:
            return False


# Convenience functions
def execute_code(
    code: str, 
    timeout: float = 5.0,
    context: Optional[Dict[str, Any]] = None
) -> ExecutionResult:
    """
    Quick function to execute code safely.
    
    Args:
        code: Python code to execute
        timeout: Execution timeout in seconds
        context: Optional execution context
        
    Returns:
        ExecutionResult
    """
    executor = SafeCodeExecutor(timeout=timeout)
    return executor.execute(code, context)


def validate_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    Quick function to validate code syntax.
    
    Args:
        code: Python code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    return CodeValidator.validate_syntax(code)


def run_code_tests(code: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Quick function to run tests against code.
    
    Args:
        code: Python code to test
        test_cases: List of test cases
        
    Returns:
        Test results
    """
    runner = TestRunner()
    return runner.run_tests(code, test_cases)