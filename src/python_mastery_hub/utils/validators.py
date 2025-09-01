# src/python_mastery_hub/utils/validators.py
"""
Input Validation Utilities - Data Validation and Sanitization

Provides comprehensive validation functions for user inputs, configuration data,
and API parameters to ensure data integrity and security.
"""

import re
import json
import ast
import sys
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from pathlib import Path
from datetime import datetime, date
import logging
from email.utils import parseaddr
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.field:
            return f"Validation error in field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class ValidationRule:
    """Represents a single validation rule."""
    
    def __init__(
        self, 
        validator: Callable[[Any], bool], 
        message: str, 
        code: Optional[str] = None
    ):
        self.validator = validator
        self.message = message
        self.code = code or "invalid"
    
    def validate(self, value: Any) -> bool:
        """Apply validation rule to a value."""
        try:
            return self.validator(value)
        except Exception as e:
            logger.debug(f"Validation rule failed with exception: {e}")
            return False


class Validator:
    """Main validation class with chainable validation methods."""
    
    def __init__(self, field_name: Optional[str] = None):
        self.field_name = field_name
        self.rules: List[ValidationRule] = []
        self.required = False
        self.allow_none = True
    
    def is_required(self) -> 'Validator':
        """Mark field as required."""
        self.required = True
        self.allow_none = False
        return self
    
    def not_none(self) -> 'Validator':
        """Disallow None values."""
        self.allow_none = False
        return self
    
    def add_rule(self, validator: Callable[[Any], bool], message: str) -> 'Validator':
        """Add custom validation rule."""
        rule = ValidationRule(validator, message)
        self.rules.append(rule)
        return self
    
    def validate(self, value: Any) -> Tuple[bool, List[str]]:
        """
        Validate a value against all rules.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check if value is None
        if value is None:
            if self.required:
                errors.append("Field is required")
                return False, errors
            elif self.allow_none:
                return True, errors
        
        # Apply all validation rules
        for rule in self.rules:
            if not rule.validate(value):
                errors.append(rule.message)
        
        return len(errors) == 0, errors


# String Validators
class StringValidator(Validator):
    """Validator for string values."""
    
    def min_length(self, length: int) -> 'StringValidator':
        """Minimum string length."""
        self.add_rule(
            lambda x: isinstance(x, str) and len(x) >= length,
            f"Must be at least {length} characters long"
        )
        return self
    
    def max_length(self, length: int) -> 'StringValidator':
        """Maximum string length."""
        self.add_rule(
            lambda x: isinstance(x, str) and len(x) <= length,
            f"Must be no more than {length} characters long"
        )
        return self
    
    def length_between(self, min_len: int, max_len: int) -> 'StringValidator':
        """String length within range."""
        self.add_rule(
            lambda x: isinstance(x, str) and min_len <= len(x) <= max_len,
            f"Must be between {min_len} and {max_len} characters long"
        )
        return self
    
    def matches_pattern(self, pattern: str, message: Optional[str] = None) -> 'StringValidator':
        """Match regex pattern."""
        compiled_pattern = re.compile(pattern)
        self.add_rule(
            lambda x: isinstance(x, str) and compiled_pattern.match(x) is not None,
            message or f"Must match pattern: {pattern}"
        )
        return self
    
    def alphanumeric(self) -> 'StringValidator':
        """Only alphanumeric characters."""
        self.add_rule(
            lambda x: isinstance(x, str) and x.isalnum(),
            "Must contain only alphanumeric characters"
        )
        return self
    
    def alpha(self) -> 'StringValidator':
        """Only alphabetic characters."""
        self.add_rule(
            lambda x: isinstance(x, str) and x.isalpha(),
            "Must contain only alphabetic characters"
        )
        return self
    
    def numeric(self) -> 'StringValidator':
        """Only numeric characters."""
        self.add_rule(
            lambda x: isinstance(x, str) and x.isnumeric(),
            "Must contain only numeric characters"
        )
        return self
    
    def contains(self, substring: str) -> 'StringValidator':
        """Must contain substring."""
        self.add_rule(
            lambda x: isinstance(x, str) and substring in x,
            f"Must contain '{substring}'"
        )
        return self
    
    def not_contains(self, substring: str) -> 'StringValidator':
        """Must not contain substring."""
        self.add_rule(
            lambda x: isinstance(x, str) and substring not in x,
            f"Must not contain '{substring}'"
        )
        return self
    
    def one_of(self, choices: List[str]) -> 'StringValidator':
        """Must be one of the given choices."""
        self.add_rule(
            lambda x: isinstance(x, str) and x in choices,
            f"Must be one of: {', '.join(choices)}"
        )
        return self
    
    def not_empty(self) -> 'StringValidator':
        """Must not be empty string."""
        self.add_rule(
            lambda x: isinstance(x, str) and x.strip() != "",
            "Must not be empty"
        )
        return self


# Number Validators
class NumberValidator(Validator):
    """Validator for numeric values."""
    
    def min_value(self, min_val: Union[int, float]) -> 'NumberValidator':
        """Minimum value."""
        self.add_rule(
            lambda x: isinstance(x, (int, float)) and x >= min_val,
            f"Must be at least {min_val}"
        )
        return self
    
    def max_value(self, max_val: Union[int, float]) -> 'NumberValidator':
        """Maximum value."""
        self.add_rule(
            lambda x: isinstance(x, (int, float)) and x <= max_val,
            f"Must be no more than {max_val}"
        )
        return self
    
    def between(self, min_val: Union[int, float], max_val: Union[int, float]) -> 'NumberValidator':
        """Value within range."""
        self.add_rule(
            lambda x: isinstance(x, (int, float)) and min_val <= x <= max_val,
            f"Must be between {min_val} and {max_val}"
        )
        return self
    
    def positive(self) -> 'NumberValidator':
        """Must be positive."""
        self.add_rule(
            lambda x: isinstance(x, (int, float)) and x > 0,
            "Must be positive"
        )
        return self
    
    def non_negative(self) -> 'NumberValidator':
        """Must be non-negative."""
        self.add_rule(
            lambda x: isinstance(x, (int, float)) and x >= 0,
            "Must be non-negative"
        )
        return self
    
    def is_integer(self) -> 'NumberValidator':
        """Must be integer."""
        self.add_rule(
            lambda x: isinstance(x, int) or (isinstance(x, float) and x.is_integer()),
            "Must be an integer"
        )
        return self


# Email Validator
def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False
    
    # Additional validation using email.utils
    try:
        parsed_name, parsed_addr = parseaddr(email)
        return '@' in parsed_addr and '.' in parsed_addr.split('@')[1]
    except Exception:
        return False


# URL Validator
def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
    """Validate URL format."""
    if not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url)
        
        # Check if scheme and netloc are present
        if not result.scheme or not result.netloc:
            return False
        
        # Check allowed schemes
        if allowed_schemes and result.scheme not in allowed_schemes:
            return False
        
        return True
    except Exception:
        return False


# File Path Validator
def validate_file_path(path: Union[str, Path], must_exist: bool = False) -> bool:
    """Validate file path."""
    try:
        path_obj = Path(path)
        
        # Check if path is absolute or relative
        if path_obj.is_absolute():
            # For absolute paths, check if parent directories exist
            if must_exist:
                return path_obj.exists()
            else:
                return path_obj.parent.exists() if path_obj.parent != path_obj else True
        else:
            # For relative paths, just check format
            if must_exist:
                return path_obj.exists()
            else:
                return True
    except Exception:
        return False


# JSON Validator
def validate_json(json_str: str) -> bool:
    """Validate JSON string format."""
    if not isinstance(json_str, str):
        return False
    
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


# Python Code Validator
def validate_python_code(code: str, allow_imports: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate Python code syntax.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(code, str):
        return False, "Code must be a string"
    
    try:
        # Parse the code to check syntax
        tree = ast.parse(code)
        
        # Check for dangerous operations if imports not allowed
        if not allow_imports:
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    return False, "Import statements are not allowed"
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    dangerous_functions = ['exec', 'eval', 'compile', '__import__']
                    if node.func.id in dangerous_functions:
                        return False, f"Function '{node.func.id}' is not allowed"
        
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


# Date/Time Validators
def validate_date_string(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """Validate date string format."""
    if not isinstance(date_str, str):
        return False
    
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def validate_datetime_string(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> bool:
    """Validate datetime string format."""
    if not isinstance(datetime_str, str):
        return False
    
    try:
        datetime.strptime(datetime_str, format_str)
        return True
    except ValueError:
        return False


# Module/Topic ID Validator
def validate_module_id(module_id: str) -> bool:
    """Validate module ID format."""
    if not isinstance(module_id, str):
        return False
    
    # Module IDs should be lowercase, alphanumeric with underscores
    pattern = r'^[a-z][a-z0-9_]*[a-z0-9]$'
    return re.match(pattern, module_id) is not None


def validate_topic_name(topic_name: str) -> bool:
    """Validate topic name format."""
    if not isinstance(topic_name, str):
        return False
    
    # Topic names should be non-empty, reasonable length
    return 1 <= len(topic_name.strip()) <= 100


# Configuration Validators
def validate_config_dict(config: Dict[str, Any], required_keys: List[str]) -> Tuple[bool, List[str]]:
    """Validate configuration dictionary."""
    errors = []
    
    if not isinstance(config, dict):
        return False, ["Configuration must be a dictionary"]
    
    # Check required keys
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")
    
    return len(errors) == 0, errors


# Sanitization Functions
def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input."""
    if not isinstance(value, str):
        return ""
    
    # Strip whitespace
    sanitized = value.strip()
    
    # Remove control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    if not isinstance(filename, str):
        return "untitled"
    
    # Remove path separators and dangerous characters
    dangerous_chars = '<>:"/\\|?*'
    sanitized = ''.join(char for char in filename if char not in dangerous_chars)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


# Composite Validators
class FormValidator:
    """Validator for form-like data structures."""
    
    def __init__(self):
        self.field_validators: Dict[str, Validator] = {}
    
    def add_field(self, field_name: str, validator: Validator) -> 'FormValidator':
        """Add field validator."""
        self.field_validators[field_name] = validator
        return self
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate form data.
        
        Returns:
            Tuple of (is_valid, field_errors)
        """
        all_errors = {}
        is_valid = True
        
        for field_name, validator in self.field_validators.items():
            field_value = data.get(field_name)
            field_valid, field_errors = validator.validate(field_value)
            
            if not field_valid:
                all_errors[field_name] = field_errors
                is_valid = False
        
        return is_valid, all_errors


# Factory Functions
def string_validator(field_name: Optional[str] = None) -> StringValidator:
    """Create string validator."""
    return StringValidator(field_name)


def number_validator(field_name: Optional[str] = None) -> NumberValidator:
    """Create number validator."""
    return NumberValidator(field_name)


def email_validator(field_name: Optional[str] = None) -> StringValidator:
    """Create email validator."""
    return (StringValidator(field_name)
            .not_empty()
            .add_rule(validate_email, "Must be a valid email address"))


def url_validator(field_name: Optional[str] = None, allowed_schemes: Optional[List[str]] = None) -> StringValidator:
    """Create URL validator."""
    return (StringValidator(field_name)
            .not_empty()
            .add_rule(
                lambda x: validate_url(x, allowed_schemes),
                "Must be a valid URL"
            ))


def module_id_validator(field_name: Optional[str] = None) -> StringValidator:
    """Create module ID validator."""
    return (StringValidator(field_name)
            .not_empty()
            .length_between(2, 50)
            .add_rule(validate_module_id, "Must be a valid module ID"))


def topic_name_validator(field_name: Optional[str] = None) -> StringValidator:
    """Create topic name validator."""
    return (StringValidator(field_name)
            .not_empty()
            .length_between(1, 100)
            .add_rule(validate_topic_name, "Must be a valid topic name"))


# Validation Decorators
def validate_args(**validators):
    """Decorator to validate function arguments."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function argument names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate arguments
            for arg_name, validator in validators.items():
                if arg_name in bound_args.arguments:
                    value = bound_args.arguments[arg_name]
                    is_valid, errors = validator.validate(value)
                    if not is_valid:
                        raise ValidationError(
                            f"Invalid argument '{arg_name}': {'; '.join(errors)}"
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Utility Functions
def get_validation_summary(errors: Dict[str, List[str]]) -> str:
    """Get formatted validation error summary."""
    if not errors:
        return "No validation errors"
    
    summary_lines = []
    for field, field_errors in errors.items():
        for error in field_errors:
            summary_lines.append(f"• {field}: {error}")
    
    return "\n".join(summary_lines)


def validate_and_raise(validator: Validator, value: Any, field_name: Optional[str] = None) -> None:
    """Validate value and raise ValidationError if invalid."""
    is_valid, errors = validator.validate(value)
    if not is_valid:
        raise ValidationError("; ".join(errors), field_name, value)