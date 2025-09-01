"""
Context manager examples and demonstrations for the Advanced Python module.
"""

import contextlib
import tempfile
import sys
import io
import time
from typing import Dict, List, Any, Iterator, Generator
from .base import TopicDemo


class ContextManagersDemo(TopicDemo):
    """Demonstration class for Python context managers."""
    
    def __init__(self):
        super().__init__("context_managers")
    
    def _setup_examples(self) -> None:
        """Setup context manager examples."""
        self.examples = {
            "basic_context_managers": {
                "code": '''
import contextlib
import tempfile
import time
from typing import Any

class FileManager:
    """Custom context manager for file operations."""
    
    def __init__(self, filename: str, mode: str = 'r'):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        print(f"Opening file: {self.filename}")
        try:
            self.file = open(self.filename, self.mode)
            return self.file
        except FileNotFoundError:
            # Create a temporary file for demo
            self.file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
            self.file.write("Hello, World!\\nThis is a demo file.\\nLine 3")
            self.file.seek(0)
            return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Closing file: {self.filename}")
        if self.file:
            self.file.close()
        
        if exc_type is not None:
            print(f"Exception occurred: {exc_type.__name__}: {exc_val}")
            return False  # Don't suppress the exception
        
        print("File operation completed successfully")
        return True

class TimingContext:
    """Context manager for timing code execution."""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
    
    def __enter__(self):
        print(f"Starting: {self.description}")
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        print(f"{self.description} completed in {duration:.4f} seconds")
        
        if exc_type is not None:
            print(f"Exception during {self.description}: {exc_val}")
        
        return False  # Don't suppress exceptions

class DatabaseTransaction:
    """Context manager for database-like transactions."""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.transaction_id = None
        self.operations = []
    
    def __enter__(self):
        import random
        self.transaction_id = random.randint(1000, 9999)
        print(f"Starting transaction {self.transaction_id} on {self.db_name}")
        return self
    
    def execute(self, operation: str):
        """Execute an operation within the transaction."""
        self.operations.append(operation)
        print(f"  Executing: {operation}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"  Rolling back transaction {self.transaction_id}")
            print(f"  Reason: {exc_val}")
        else:
            print(f"  Committing transaction {self.transaction_id}")
            print(f"  Operations committed: {len(self.operations)}")
        
        print(f"Transaction {self.transaction_id} closed")
        return False

# Usage examples
with FileManager("demo.txt", "r") as file:
    content = file.read()
    print(f"File content length: {len(content)} characters")

with TimingContext("Data processing"):
    # Simulate some work
    time.sleep(0.1)
    data = [i**2 for i in range(1000)]
    result = sum(data)

with DatabaseTransaction("user_db") as tx:
    tx.execute("INSERT INTO users (name) VALUES ('Alice')")
    tx.execute("UPDATE users SET email='alice@example.com' WHERE name='Alice'")
''',
                "explanation": "Context managers ensure proper resource management and cleanup using the __enter__ and __exit__ methods"
            },
            
            "contextlib_decorators": {
                "code": '''
import contextlib
import sys
import io
from typing import Iterator, Any

@contextlib.contextmanager
def temporary_attribute(obj: Any, attr_name: str, temp_value: Any) -> Iterator[None]:
    """Temporarily change an object's attribute."""
    # Save original value
    original_value = getattr(obj, attr_name, None)
    has_original = hasattr(obj, attr_name)
    
    # Set temporary value
    setattr(obj, attr_name, temp_value)
    print(f"Set {attr_name} to {temp_value}")
    
    try:
        yield
    finally:
        # Restore original value
        if has_original:
            setattr(obj, attr_name, original_value)
            print(f"Restored {attr_name} to {original_value}")
        else:
            delattr(obj, attr_name)
            print(f"Removed temporary attribute {attr_name}")

@contextlib.contextmanager
def suppressed_output() -> Iterator[tuple]:
    """Capture and suppress stdout/stderr."""
    # Save original stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # Create string buffers
    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()
    
    try:
        # Redirect output
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr
        yield captured_stdout, captured_stderr
    finally:
        # Restore original output
        sys.stdout = original_stdout
        sys.stderr = original_stderr

@contextlib.contextmanager
def error_handler(error_types: tuple, default_value: Any = None) -> Iterator[Any]:
    """Context manager that handles specific exceptions."""
    try:
        yield
    except error_types as e:
        print(f"Handled exception: {type(e).__name__}: {e}")
        return default_value

@contextlib.contextmanager
def conditional_context(condition: bool, context_manager):
    """Conditionally apply a context manager."""
    if condition:
        with context_manager as value:
            yield value
    else:
        yield None

class ConfigManager:
    """Configuration manager for demonstration."""
    
    def __init__(self):
        self.debug = False
        self.log_level = "INFO"
        self.max_connections = 100

@contextlib.contextmanager
def temporary_config(**config_changes):
    """Temporarily modify configuration."""
    config = ConfigManager()
    original_values = {}
    
    # Save original values and apply changes
    for key, value in config_changes.items():
        if hasattr(config, key):
            original_values[key] = getattr(config, key)
            setattr(config, key, value)
            print(f"Config: {key} = {value}")
    
    try:
        yield config
    finally:
        # Restore original values
        for key, original_value in original_values.items():
            setattr(config, key, original_value)
            print(f"Restored: {key} = {original_value}")

# Usage examples
class TestObject:
    def __init__(self):
        self.value = "original"

obj = TestObject()
print(f"Original value: {obj.value}")

with temporary_attribute(obj, "value", "temporary"):
    print(f"Inside context: {obj.value}")

print(f"After context: {obj.value}")

# Multiple context managers using ExitStack
with contextlib.ExitStack() as stack:
    # Add multiple context managers dynamically
    config = stack.enter_context(temporary_config(debug=True, max_connections=50))
    obj_context = stack.enter_context(temporary_attribute(obj, "value", "stack_managed"))
    
    print(f"Config in stack: debug={config.debug}, max_connections={config.max_connections}")
    print(f"Object value in stack: {obj.value}")
''',
                "explanation": "The contextlib module provides decorators and utilities for creating context managers with less boilerplate code"
            },
            
            "nested_contexts": {
                "code": '''
import contextlib
from typing import Any, Optional

class Resource:
    """Sample resource class for demonstration."""
    
    def __init__(self, name: str):
        self.name = name
        self.acquired = False
    
    def __enter__(self):
        print(f"Acquiring resource: {self.name}")
        self.acquired = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Releasing resource: {self.name}")
        self.acquired = False
        return False

@contextlib.contextmanager
def managed_resource(name: str, might_fail: bool = False):
    """Context manager that might fail during resource acquisition."""
    resource = None
    try:
        print(f"Setting up {name}")
        if might_fail and name == "failing_resource":
            raise RuntimeError(f"Failed to setup {name}")
        
        resource = Resource(name)
        with resource:
            yield resource
    
    except Exception as e:
        print(f"Error with {name}: {e}")
        raise
    finally:
        print(f"Cleanup for {name} complete")

# Nested context managers
def nested_context_example():
    """Demonstrate nested context managers."""
    
    try:
        with Resource("Database"):
            with Resource("Cache"):
                with Resource("Logger"):
                    print("  Using all resources")
                    
                    # Inner operation that might fail
                    with managed_resource("processor"):
                        print("  Processing data...")
    
    except Exception as e:
        print(f"Operation failed: {e}")

# ExitStack for dynamic resource management
def dynamic_context_example():
    """Demonstrate dynamic context management with ExitStack."""
    
    resource_names = ["db", "cache", "logger", "monitor"]
    
    with contextlib.ExitStack() as stack:
        resources = []
        
        for name in resource_names:
            try:
                resource = stack.enter_context(Resource(name))
                resources.append(resource)
                print(f"  Successfully acquired {name}")
            except Exception as e:
                print(f"  Failed to acquire {name}: {e}")
                continue
        
        print(f"\\n  Operating with {len(resources)} resources")
        
        # Simulate work with resources
        for resource in resources:
            if resource.acquired:
                print(f"  Working with {resource.name}")

# Suppressing specific exceptions
@contextlib.contextmanager
def ignore_errors(*exception_types):
    """Context manager to ignore specific exception types."""
    try:
        yield
    except exception_types as e:
        print(f"Ignoring {type(e).__name__}: {e}")

def error_handling_example():
    """Demonstrate error handling in context managers."""
    
    with ignore_errors(ValueError, TypeError):
        # This will be silently handled
        int("not_a_number")
    
    print("Continuing after ignored error...")
    
    # This will still raise because it's not in the ignored types
    try:
        with ignore_errors(ValueError):
            raise RuntimeError("This won't be ignored")
    except RuntimeError as e:
        print(f"RuntimeError was not ignored: {e}")
''',
                "explanation": "Nested context managers and ExitStack provide sophisticated resource management patterns"
            }
        }
    
    def _setup_exercises(self) -> None:
        """Setup context manager exercises."""
        from .exercises.transaction_manager import TransactionManagerExercise
        
        transaction_exercise = TransactionManagerExercise()
        
        self.exercises = [
            {
                "topic": "context_managers",
                "title": "Database Transaction Manager",
                "description": "Implement a context manager for database transactions",
                "difficulty": "hard",
                "exercise": transaction_exercise
            }
        ]
    
    def get_explanation(self) -> str:
        """Get detailed explanation for context managers."""
        return ("Context managers ensure proper resource management and cleanup using the 'with' statement protocol, "
                "guaranteeing that setup and teardown code runs even when exceptions occur.")
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for context managers."""
        return [
            "Always handle exceptions in __exit__ method",
            "Use contextlib.contextmanager for simple cases",
            "Ensure resources are properly cleaned up",
            "Return False from __exit__ to propagate exceptions",
            "Use ExitStack for managing multiple contexts"
        ]