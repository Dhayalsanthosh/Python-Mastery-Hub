"""
Error Handling Concepts - Exception handling, custom exceptions, and debugging.
"""

from typing import Dict, Any, List
import logging
import traceback


class ErrorHandlingConcepts:
    """Handles all error handling-related concepts and examples."""
    
    def __init__(self):
        self.topic = "error_handling"
        self.examples = self._setup_examples()
    
    def demonstrate(self) -> Dict[str, Any]:
        """Return comprehensive error handling demonstrations."""
        return {
            "topic": self.topic,
            "examples": self.examples,
            "explanation": self._get_explanation(),
            "best_practices": self._get_best_practices(),
        }
    
    def _setup_examples(self) -> Dict[str, Any]:
        """Setup comprehensive error handling examples."""
        return {
            "basic_exception_handling": {
                "code": '''
# Basic exception handling with try/except
def safe_divide(a, b):
    """Safely divide two numbers with error handling."""
    try:
        result = a / b
        return f"{a} / {b} = {result}"
    except ZeroDivisionError:
        return f"Error: Cannot divide {a} by zero!"
    except TypeError:
        return f"Error: Invalid types for division: {type(a).__name__}, {type(b).__name__}"
    except Exception as e:
        return f"Unexpected error: {e}"

# Test various scenarios
test_cases = [
    (10, 2),      # Normal case
    (10, 0),      # Zero division
    (10, "2"),    # Type error
    ("10", 2),    # Another type error
]

print("=== Basic Exception Handling ===")
for a, b in test_cases:
    print(safe_divide(a, b))

print("\\n=== Multiple Exception Types ===")
def process_data(data):
    """Process data with multiple exception handlers."""
    try:
        # Convert to integer
        number = int(data)
        
        # Perform calculation
        result = 100 / number
        
        # Access list element
        items = [1, 2, 3]
        selected = items[number]
        
        return f"Success: {result}, selected: {selected}"
        
    except ValueError as e:
        return f"ValueError: Cannot convert '{data}' to integer"
    except ZeroDivisionError:
        return f"ZeroDivisionError: Cannot divide by zero"
    except IndexError as e:
        return f"IndexError: {e}"
    except Exception as e:
        return f"Unexpected error: {type(e).__name__}: {e}"

test_data = ["5", "0", "abc", "10", "2"]
for data in test_data:
    print(f"Input '{data}': {process_data(data)}")
''',
                "output": "=== Basic Exception Handling ===\\n10 / 2 = 5.0\\nError: Cannot divide 10 by zero!\\nError: Invalid types for division: int, str\\nError: Invalid types for division: str, int\\n\\n=== Multiple Exception Types ===\\nInput '5': IndexError: list index out of range\\nInput '0': ZeroDivisionError: Cannot divide by zero\\nInput 'abc': ValueError: Cannot convert 'abc' to integer\\nInput '10': IndexError: list index out of range\\nInput '2': Success: 50.0, selected: 3",
                "explanation": "Exception handling allows programs to respond gracefully to errors instead of crashing"
            },
            
            "try_except_else_finally": {
                "code": '''
# Complete try/except/else/finally structure
def file_processor(filename, data):
    """Demonstrate complete exception handling structure."""
    file_handle = None
    
    try:
        print(f"Attempting to process file: {filename}")
        
        # Simulate file operations that might fail
        if filename == "readonly.txt":
            raise PermissionError("File is read-only")
        elif filename == "missing.txt":
            raise FileNotFoundError("File does not exist")
        elif not data:
            raise ValueError("No data provided")
        
        # Simulate successful file processing
        file_handle = f"Handle for {filename}"
        processed_data = data.upper()
        
        print(f"Processing data: {data} -> {processed_data}")
        
    except FileNotFoundError as e:
        print(f"File error: {e}")
        return None
    except PermissionError as e:
        print(f"Permission error: {e}")
        return None
    except ValueError as e:
        print(f"Data error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    else:
        # Executed only if no exception occurred
        print("File processed successfully!")
        return processed_data
    finally:
        # Always executed, regardless of exceptions
        if file_handle:
            print(f"Cleaning up: {file_handle}")
        print("File processing attempt completed")
        print("-" * 40)

# Test different scenarios
test_cases = [
    ("valid.txt", "hello world"),
    ("readonly.txt", "some data"),
    ("missing.txt", "some data"),
    ("valid.txt", ""),
    ("valid.txt", None)
]

print("=== Try/Except/Else/Finally Structure ===")
for filename, data in test_cases:
    result = file_processor(filename, data)
    print(f"Result: {result}\\n")
''',
                "output": "=== Try/Except/Else/Finally Structure ===\\nAttempting to process file: valid.txt\\nProcessing data: hello world -> HELLO WORLD\\nFile processed successfully!\\nCleaning up: Handle for valid.txt\\nFile processing attempt completed\\n----------------------------------------\\nResult: HELLO WORLD\\n\\nAttempting to process file: readonly.txt\\nPermission error: File is read-only\\nFile processing attempt completed\\n----------------------------------------\\nResult: None\\n\\nAttempting to process file: missing.txt\\nFile error: File does not exist\\nFile processing attempt completed\\n----------------------------------------\\nResult: None\\n\\nAttempting to process file: valid.txt\\nData error: No data provided\\nFile processing attempt completed\\n----------------------------------------\\nResult: None\\n\\nAttempting to process file: valid.txt\\nData error: No data provided\\nFile processing attempt completed\\n----------------------------------------\\nResult: None",
                "explanation": "The complete try/except/else/finally structure provides comprehensive error handling and cleanup"
            },
            
            "custom_exceptions": {
                "code": '''
# Custom exception classes
class ValidationError(Exception):
    """Base exception for validation errors."""
    def __init__(self, message, error_code=None, field_name=None):
        super().__init__(message)
        self.error_code = error_code
        self.field_name = field_name
        self.message = message
    
    def __str__(self):
        error_parts = [self.message]
        if self.field_name:
            error_parts.append(f"Field: {self.field_name}")
        if self.error_code:
            error_parts.append(f"Code: {self.error_code}")
        return " | ".join(error_parts)

class AgeValidationError(ValidationError):
    """Specific exception for age validation."""
    pass

class EmailValidationError(ValidationError):
    """Specific exception for email validation."""
    pass

class User:
    """User class with validation."""
    
    def __init__(self, name, age, email):
        self.name = self._validate_name(name)
        self.age = self._validate_age(age)
        self.email = self._validate_email(email)
    
    def _validate_name(self, name):
        if not isinstance(name, str):
            raise ValidationError(
                f"Name must be a string, got {type(name).__name__}",
                error_code="TYPE_ERROR",
                field_name="name"
            )
        if len(name.strip()) == 0:
            raise ValidationError(
                "Name cannot be empty",
                error_code="EMPTY_NAME",
                field_name="name"
            )
        return name.strip()
    
    def _validate_age(self, age):
        if not isinstance(age, int):
            raise AgeValidationError(
                f"Age must be an integer, got {type(age).__name__}",
                error_code="TYPE_ERROR",
                field_name="age"
            )
        if age < 0:
            raise AgeValidationError(
                f"Age cannot be negative: {age}",
                error_code="NEGATIVE_AGE",
                field_name="age"
            )
        if age > 150:
            raise AgeValidationError(
                f"Age seems unrealistic: {age}",
                error_code="UNREALISTIC_AGE",
                field_name="age"
            )
        return age
    
    def _validate_email(self, email):
        if not isinstance(email, str):
            raise EmailValidationError(
                f"Email must be a string, got {type(email).__name__}",
                error_code="TYPE_ERROR",
                field_name="email"
            )
        if "@" not in email or "." not in email:
            raise EmailValidationError(
                f"Invalid email format: {email}",
                error_code="INVALID_FORMAT",
                field_name="email"
            )
        return email.lower()
    
    def __repr__(self):
        return f"User(name='{self.name}', age={self.age}, email='{self.email}')"

# Test custom exceptions
test_users = [
    ("Alice", 25, "alice@email.com"),  # Valid
    ("", 30, "bob@email.com"),         # Empty name
    ("Charlie", -5, "charlie@email.com"),  # Negative age
    ("Diana", 200, "diana@email.com"),     # Unrealistic age
    ("Eve", 28, "invalid-email"),          # Invalid email
    (123, 35, "test@email.com"),           # Invalid name type
]

print("=== Custom Exception Handling ===")
for name, age, email in test_users:
    try:
        user = User(name, age, email)
        print(f"✓ Created: {user}")
    except AgeValidationError as e:
        print(f"✗ Age Error: {e}")
    except EmailValidationError as e:
        print(f"✗ Email Error: {e}")
    except ValidationError as e:
        print(f"✗ Validation Error: {e}")
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
''',
                "output": "=== Custom Exception Handling ===\\n✓ Created: User(name='Alice', age=25, email='alice@email.com')\\n✗ Validation Error: Name cannot be empty | Field: name | Code: EMPTY_NAME\\n✗ Age Error: Age cannot be negative: -5 | Field: age | Code: NEGATIVE_AGE\\n✗ Age Error: Age seems unrealistic: 200 | Field: age | Code: UNREALISTIC_AGE\\n✗ Email Error: Invalid email format: invalid-email | Field: email | Code: INVALID_FORMAT\\n✗ Validation Error: Name must be a string, got int | Field: name | Code: TYPE_ERROR",
                "explanation": "Custom exceptions provide domain-specific error handling with additional context and structured information"
            },
            
            "exception_chaining": {
                "code": '''
# Exception chaining and context
class DatabaseError(Exception):
    """Database operation error."""
    pass

class UserServiceError(Exception):
    """User service error."""
    pass

def simulate_database_operation(user_id):
    """Simulate a database operation that might fail."""
    if user_id == "invalid":
        raise ValueError("Invalid user ID format")
    elif user_id == "not_found":
        raise DatabaseError("User not found in database")
    elif user_id == "connection_error":
        raise ConnectionError("Database connection failed")
    else:
        return {"id": user_id, "name": "John Doe", "status": "active"}

def get_user_data(user_id):
    """High-level function that handles user operations."""
    try:
        print(f"Fetching user data for ID: {user_id}")
        user_data = simulate_database_operation(user_id)
        return user_data
    except ValueError as e:
        # Chain exceptions to preserve context
        raise UserServiceError(f"Invalid user ID provided: {user_id}") from e
    except DatabaseError as e:
        # Re-raise with additional context
        raise UserServiceError(f"Database error for user {user_id}") from e
    except Exception as e:
        # Wrap unexpected errors
        raise UserServiceError(f"Unexpected error for user {user_id}") from e

def process_user_request(user_id):
    """Process a user request with full exception context."""
    try:
        user_data = get_user_data(user_id)
        print(f"Success: {user_data}")
        return user_data
    except UserServiceError as e:
        print(f"Service Error: {e}")
        
        # Access the original exception
        if e.__cause__:
            print(f"Original error: {type(e.__cause__).__name__}: {e.__cause__}")
        
        # Print full traceback for debugging
        print("\\nFull traceback:")
        traceback.print_exc()
        return None

print("=== Exception Chaining ===")
test_user_ids = ["valid_id", "invalid", "not_found", "connection_error"]

for user_id in test_user_ids:
    print(f"\\n--- Processing user ID: {user_id} ---")
    process_user_request(user_id)
    print()
''',
                "output": "=== Exception Chaining ===\\n\\n--- Processing user ID: valid_id ---\\nFetching user data for ID: valid_id\\nSuccess: {'id': 'valid_id', 'name': 'John Doe', 'status': 'active'}\\n\\n\\n--- Processing user ID: invalid ---\\nFetching user data for ID: invalid\\nService Error: Invalid user ID provided: invalid\\nOriginal error: ValueError: Invalid user ID format\\n\\nFull traceback:\\n[Traceback details]\\n\\n--- Processing user ID: not_found ---\\nFetching user data for ID: not_found\\nService Error: Database error for user not_found\\nOriginal error: DatabaseError: User not found in database\\n\\nFull traceback:\\n[Traceback details]\\n\\n--- Processing user ID: connection_error ---\\nFetching user data for ID: connection_error\\nService Error: Unexpected error for user connection_error\\nOriginal error: ConnectionError: Database connection failed\\n\\nFull traceback:\\n[Traceback details]",
                "explanation": "Exception chaining preserves error context while allowing high-level error handling and debugging"
            },
            
            "logging_and_debugging": {
                "code": '''
# Logging and debugging with exceptions
import logging
import sys
from io import StringIO

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

class CalculatorError(Exception):
    """Calculator operation error."""
    pass

class Calculator:
    """Calculator with comprehensive error handling and logging."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.Calculator")
        self.operation_count = 0
    
    def _log_operation(self, operation, a, b, result=None, error=None):
        """Log operation details."""
        self.operation_count += 1
        
        if error:
            self.logger.error(
                f"Operation {self.operation_count}: {operation}({a}, {b}) failed - {error}",
                exc_info=True
            )
        else:
            self.logger.info(
                f"Operation {self.operation_count}: {operation}({a}, {b}) = {result}"
            )
    
    def divide(self, a, b):
        """Divide two numbers with logging."""
        try:
            self.logger.debug(f"Starting division: {a} / {b}")
            
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise CalculatorError(f"Invalid types: {type(a).__name__}, {type(b).__name__}")
            
            if b == 0:
                raise CalculatorError("Division by zero")
            
            result = a / b
            self._log_operation("divide", a, b, result)
            return result
            
        except CalculatorError as e:
            self._log_operation("divide", a, b, error=e)
            raise
        except Exception as e:
            error_msg = f"Unexpected error in division: {e}"
            self._log_operation("divide", a, b, error=error_msg)
            raise CalculatorError(error_msg) from e
    
    def safe_divide(self, a, b):
        """Safe division that returns None on error."""
        try:
            return self.divide(a, b)
        except CalculatorError as e:
            self.logger.warning(f"Safe divide failed: {e}")
            return None

# Capture logging output for demonstration
log_capture = StringIO()
handler = logging.StreamHandler(log_capture)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to capture logs
calc_logger = logging.getLogger(f"{__name__}.Calculator")
calc_logger.addHandler(handler)
calc_logger.setLevel(logging.DEBUG)

print("=== Logging and Debugging ===")
calc = Calculator()

# Test various operations
test_operations = [
    (10, 2),    # Normal
    (10, 0),    # Division by zero
    (10, "2"),  # Type error
    (15, 3),    # Normal
]

for a, b in test_operations:
    try:
        result = calc.divide(a, b)
        print(f"Result: {a} / {b} = {result}")
    except CalculatorError as e:
        print(f"Calculator Error: {e}")

print("\\n=== Safe Operations ===")
for a, b in test_operations:
    result = calc.safe_divide(a, b)
    print(f"Safe divide {a} / {b} = {result}")

# Show captured logs
print("\\n=== Captured Logs ===")
log_output = log_capture.getvalue()
for line in log_output.strip().split('\\n'):
    if line:
        print(line)
''',
                "output": "=== Logging and Debugging ===\\nResult: 10 / 2 = 5.0\\nCalculator Error: Division by zero\\nCalculator Error: Invalid types: int, str\\nResult: 15 / 3 = 5.0\\n\\n=== Safe Operations ===\\nSafe divide 10 / 2 = 5.0\\nSafe divide 10 / 0 = None\\nSafe divide 10 / 2 = None\\nSafe divide 15 / 3 = 5.0\\n\\n=== Captured Logs ===\\nDEBUG - Starting division: 10 / 2\\nINFO - Operation 1: divide(10, 2) = 5.0\\nDEBUG - Starting division: 10 / 0\\nERROR - Operation 2: divide(10, 0) failed - Division by zero\\nDEBUG - Starting division: 10 / 2\\nERROR - Operation 3: divide(10, 2) failed - Invalid types: int, str\\nDEBUG - Starting division: 15 / 3\\nINFO - Operation 4: divide(15, 3) = 5.0\\nWARNING - Safe divide failed: Division by zero\\nWARNING - Safe divide failed: Invalid types: int, str",
                "explanation": "Logging provides structured error tracking and debugging information for production applications"
            }
        }
    
    def _get_explanation(self) -> str:
        """Get detailed explanation for error handling."""
        return (
            "Exception handling allows programs to respond gracefully to errors instead of "
            "crashing. Python uses try/except blocks to catch and handle specific types of "
            "errors. The complete structure includes try/except/else/finally for comprehensive "
            "error handling and cleanup. Custom exceptions provide domain-specific error types "
            "with additional context. Exception chaining preserves error context while allowing "
            "high-level handling. Logging helps track errors and debug issues in production."
        )
    
    def _get_best_practices(self) -> List[str]:
        """Get best practices for error handling."""
        return [
            "Catch specific exceptions rather than using bare 'except' clauses",
            "Use try/except blocks around code that might fail, not entire functions",
            "Handle exceptions at the appropriate level - don't catch too early",
            "Use finally blocks for cleanup code that must always run",
            "Create custom exceptions for domain-specific errors with meaningful names",
            "Include relevant context in exception messages for easier debugging",
            "Use exception chaining (raise ... from ...) to preserve error context",
            "Log exceptions with appropriate levels (ERROR, WARNING, etc.)",
            "Don't ignore exceptions silently - always handle them appropriately",
            "Use else blocks in try statements for code that should only run on success",
            "Validate input early and raise meaningful exceptions for invalid data",
            "Consider using context managers (with statements) for resource management"
        ]