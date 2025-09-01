"""
Input Validation Utilities

Provides comprehensive input validation and sanitization functions
for CLI applications with user-friendly error messages and suggestions.
"""

import re
import ast
from typing import Any, List, Optional, Union, Callable, Dict, Tuple
from pathlib import Path
import email_validator

from .colors import colors


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.suggestions = suggestions or []


class InputValidator:
    """Comprehensive input validation class."""
    
    @staticmethod
    def validate_module_id(module_id: str) -> str:
        """
        Validate module identifier.
        
        Args:
            module_id: Module identifier to validate
            
        Returns:
            Validated module ID
            
        Raises:
            ValidationError: If module ID is invalid
        """
        valid_modules = [
            'basics', 'oop', 'advanced', 'data_structures', 'algorithms',
            'async_programming', 'web_development', 'data_science', 'testing'
        ]
        
        if not module_id:
            raise ValidationError(
                "Module ID cannot be empty",
                suggestions=valid_modules[:3]
            )
        
        module_id = module_id.lower().strip()
        
        # Handle common aliases
        aliases = {
            'basic': 'basics',
            'object_oriented': 'oop',
            'classes': 'oop',
            'async': 'async_programming',
            'web': 'web_development',
            'ds': 'data_science',
            'ml': 'data_science',
            'test': 'testing',
            'tests': 'testing'
        }
        
        if module_id in aliases:
            module_id = aliases[module_id]
        
        if module_id not in valid_modules:
            # Find closest matches
            suggestions = InputValidator._find_closest_matches(module_id, valid_modules)
            raise ValidationError(
                f"Unknown module: '{module_id}'",
                suggestions=suggestions
            )
        
        return module_id
    
    @staticmethod
    def validate_exercise_name(exercise_name: str, module_id: str) -> str:
        """
        Validate exercise name for a specific module.
        
        Args:
            exercise_name: Exercise name to validate
            module_id: Module identifier
            
        Returns:
            Validated exercise name
            
        Raises:
            ValidationError: If exercise name is invalid
        """
        if not exercise_name:
            raise ValidationError("Exercise name cannot be empty")
        
        exercise_name = exercise_name.lower().strip().replace('-', '_')
        
        # Define valid exercises per module
        module_exercises = {
            'basics': [
                'control_flow_exercise', 'data_type_conversion_exercise',
                'function_design_exercise', 'variable_assignment_exercise'
            ],
            'oop': [
                'employee_hierarchy_exercise', 'library_exercise',
                'observer_pattern_exercise', 'shape_calculator_exercise'
            ],
            'advanced': [
                'caching_director', 'file_pipeline',
                'orm_metaclass', 'transaction_manager'
            ],
            'data_structures': [
                'bst', 'cache', 'learning_path', 'linkedlist', 'registry'
            ],
            'algorithms': [
                'dijkstra_exercise', 'lcs_exercise', 'quicksort_exercise'
            ],
            'async_programming': [
                'async_scraper_exercise', 'parallel_processor_exercise',
                'producer_consumer_exercise'
            ],
            'web_development': [
                'flask_blog_exercise', 'jwt_auth_exercise',
                'microservice_exercise', 'rest_api_exercise',
                'websocket_chat_exercise'
            ],
            'data_science': [
                'dashboard', 'data_analysis', 'ml_pipeline'
            ],
            'testing': [
                'integration_exercise', 'mocking_exercise',
                'tdd_exercise', 'unittest_exercise'
            ]
        }
        
        valid_exercises = module_exercises.get(module_id, [])
        
        if exercise_name not in valid_exercises:
            suggestions = InputValidator._find_closest_matches(exercise_name, valid_exercises)
            raise ValidationError(
                f"Unknown exercise: '{exercise_name}' for module '{module_id}'",
                suggestions=suggestions
            )
        
        return exercise_name
    
    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = True, extensions: Optional[List[str]] = None) -> Path:
        """
        Validate file path.
        
        Args:
            file_path: File path to validate
            must_exist: Whether file must exist
            extensions: Allowed file extensions
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If file path is invalid
        """
        if not file_path:
            raise ValidationError("File path cannot be empty")
        
        path = Path(file_path).expanduser().resolve()
        
        if must_exist and not path.exists():
            raise ValidationError(f"File does not exist: {path}")
        
        if extensions:
            extensions = [ext.lower() for ext in extensions]
            if path.suffix.lower() not in extensions:
                raise ValidationError(
                    f"Invalid file extension. Expected: {', '.join(extensions)}",
                    suggestions=[f"file{ext}" for ext in extensions[:3]]
                )
        
        return path
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email address.
        
        Args:
            email: Email address to validate
            
        Returns:
            Validated email address
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email:
            raise ValidationError("Email address cannot be empty")
        
        email = email.strip().lower()
        
        try:
            # Use email-validator library if available, otherwise basic regex
            valid_email = email_validator.validate_email(email)
            return valid_email.email
        except ImportError:
            # Fallback to basic regex validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise ValidationError(
                    "Invalid email format",
                    suggestions=["user@example.com", "name@domain.org"]
                )
            return email
        except Exception:
            raise ValidationError(
                "Invalid email address",
                suggestions=["user@example.com", "name@domain.org"]
            )
    
    @staticmethod
    def validate_python_code(code: str, allow_empty: bool = False) -> str:
        """
        Validate Python code syntax.
        
        Args:
            code: Python code to validate
            allow_empty: Whether empty code is allowed
            
        Returns:
            Validated code
            
        Raises:
            ValidationError: If code has syntax errors
        """
        if not code.strip():
            if allow_empty:
                return code
            raise ValidationError("Code cannot be empty")
        
        try:
            ast.parse(code)
            return code
        except SyntaxError as e:
            error_msg = f"Syntax error: {e.msg}"
            if e.lineno:
                error_msg += f" (line {e.lineno})"
            
            suggestions = [
                "Check for missing colons",
                "Verify indentation",
                "Check parentheses matching"
            ]
            
            raise ValidationError(error_msg, suggestions=suggestions)
    
    @staticmethod
    def validate_integer(
        value: str, 
        min_value: Optional[int] = None, 
        max_value: Optional[int] = None
    ) -> int:
        """
        Validate integer input.
        
        Args:
            value: String value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated integer
            
        Raises:
            ValidationError: If value is not a valid integer
        """
        if not value.strip():
            raise ValidationError("Value cannot be empty")
        
        try:
            int_value = int(value.strip())
        except ValueError:
            raise ValidationError(
                f"'{value}' is not a valid integer",
                suggestions=["123", "-456", "0"]
            )
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(f"Value must be at least {min_value}")
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(f"Value must be at most {max_value}")
        
        return int_value
    
    @staticmethod
    def validate_float(
        value: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> float:
        """
        Validate float input.
        
        Args:
            value: String value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated float
            
        Raises:
            ValidationError: If value is not a valid float
        """
        if not value.strip():
            raise ValidationError("Value cannot be empty")
        
        try:
            float_value = float(value.strip())
        except ValueError:
            raise ValidationError(
                f"'{value}' is not a valid number",
                suggestions=["3.14", "-2.5", "0.0"]
            )
        
        if min_value is not None and float_value < min_value:
            raise ValidationError(f"Value must be at least {min_value}")
        
        if max_value is not None and float_value > max_value:
            raise ValidationError(f"Value must be at most {max_value}")
        
        return float_value
    
    @staticmethod
    def validate_choice(value: str, choices: List[str], case_sensitive: bool = False) -> str:
        """
        Validate choice from a list of options.
        
        Args:
            value: Value to validate
            choices: List of valid choices
            case_sensitive: Whether comparison is case sensitive
            
        Returns:
            Validated choice
            
        Raises:
            ValidationError: If choice is not valid
        """
        if not value:
            raise ValidationError(
                "Choice cannot be empty",
                suggestions=choices[:3]
            )
        
        if not case_sensitive:
            value = value.lower()
            choices_lower = [choice.lower() for choice in choices]
            
            if value in choices_lower:
                # Return original case choice
                return choices[choices_lower.index(value)]
        else:
            if value in choices:
                return value
        
        suggestions = InputValidator._find_closest_matches(value, choices)
        raise ValidationError(
            f"Invalid choice: '{value}'",
            suggestions=suggestions
        )
    
    @staticmethod
    def validate_url(url: str, schemes: Optional[List[str]] = None) -> str:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            schemes: Allowed URL schemes (default: http, https)
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError("URL cannot be empty")
        
        url = url.strip()
        schemes = schemes or ['http', 'https']
        
        # Basic URL pattern
        url_pattern = re.compile(
            r'^(?:(?P<scheme>[a-z][a-z0-9+.-]*):\/\/)?'  # scheme
            r'(?:(?P<user>[^\s:@\/]+)(?::(?P<password>[^\s@\/]*))?@)?'  # user info
            r'(?P<host>(?:[a-z0-9.-]+|\[[a-f0-9:]+\]))(?::(?P<port>\d+))?'  # host and port
            r'(?P<path>\/[^\s?#]*)?(?:\?(?P<query>[^\s#]*))?(?:#(?P<fragment>\S*))?$',  # path, query, fragment
            re.IGNORECASE
        )
        
        match = url_pattern.match(url)
        if not match:
            raise ValidationError(
                "Invalid URL format",
                suggestions=["https://example.com", "http://localhost:8000"]
            )
        
        scheme = match.group('scheme')
        if scheme and scheme.lower() not in schemes:
            raise ValidationError(
                f"Unsupported URL scheme: {scheme}",
                suggestions=[f"{s}://example.com" for s in schemes]
            )
        
        return url
    
    @staticmethod
    def validate_json(json_str: str) -> dict:
        """
        Validate JSON string.
        
        Args:
            json_str: JSON string to validate
            
        Returns:
            Parsed JSON object
            
        Raises:
            ValidationError: If JSON is invalid
        """
        if not json_str.strip():
            raise ValidationError("JSON cannot be empty")
        
        try:
            import json
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON: {e.msg}",
                suggestions=['{"key": "value"}', '[]', '{}']
            )
    
    @staticmethod
    def _find_closest_matches(target: str, options: List[str], max_matches: int = 3) -> List[str]:
        """
        Find closest string matches using simple similarity.
        
        Args:
            target: Target string
            options: List of options to match against
            max_matches: Maximum number of matches to return
            
        Returns:
            List of closest matches
        """
        def simple_similarity(s1: str, s2: str) -> float:
            """Calculate simple character-based similarity."""
            s1, s2 = s1.lower(), s2.lower()
            if s1 == s2:
                return 1.0
            
            # Check if one is substring of other
            if s1 in s2 or s2 in s1:
                return 0.8
            
            # Count common characters
            common = sum(1 for c in set(s1) if c in set(s2))
            total = len(set(s1) | set(s2))
            
            return common / total if total > 0 else 0.0
        
        similarities = [(option, simple_similarity(target, option)) for option in options]
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return options with similarity > 0.3
        matches = [option for option, sim in similarities if sim > 0.3]
        return matches[:max_matches]


def prompt_with_validation(
    prompt: str,
    validator: Callable[[str], Any],
    max_attempts: int = 3,
    show_suggestions: bool = True
) -> Any:
    """
    Prompt user with input validation and retry logic.
    
    Args:
        prompt: Prompt message
        validator: Validation function
        max_attempts: Maximum number of attempts
        show_suggestions: Whether to show suggestions on error
        
    Returns:
        Validated input value
        
    Raises:
        ValidationError: If validation fails after max attempts
    """
    for attempt in range(max_attempts):
        try:
            user_input = input(f"{colors.CYAN}{prompt}: {colors.RESET}")
            return validator(user_input)
        
        except ValidationError as e:
            colors.print_error(str(e))
            
            if show_suggestions and e.suggestions:
                print(f"{colors.YELLOW}Suggestions: {', '.join(e.suggestions)}{colors.RESET}")
            
            if attempt < max_attempts - 1:
                print(f"{colors.GRAY}Try again ({max_attempts - attempt - 1} attempts remaining)...{colors.RESET}")
    
    raise ValidationError(f"Validation failed after {max_attempts} attempts")


def validate_and_suggest(value: str, validator: Callable[[str], Any]) -> Tuple[bool, Any, Optional[str]]:
    """
    Validate input and return result with suggestion.
    
    Args:
        value: Value to validate
        validator: Validation function
        
    Returns:
        Tuple of (is_valid, validated_value_or_none, error_message)
    """
    try:
        validated_value = validator(value)
        return True, validated_value, None
    except ValidationError as e:
        error_msg = str(e)
        if e.suggestions:
            error_msg += f" (Suggestions: {', '.join(e.suggestions)})"
        return False, None, error_msg


# Convenience validators
def module_validator(module_id: str) -> str:
    """Convenience function for module validation."""
    return InputValidator.validate_module_id(module_id)


def exercise_validator(module_id: str) -> Callable[[str], str]:
    """Convenience function for exercise validation."""
    def validator(exercise_name: str) -> str:
        return InputValidator.validate_exercise_name(exercise_name, module_id)
    return validator


def integer_validator(min_val: int = None, max_val: int = None) -> Callable[[str], int]:
    """Convenience function for integer validation."""
    def validator(value: str) -> int:
        return InputValidator.validate_integer(value, min_val, max_val)
    return validator


def choice_validator(choices: List[str], case_sensitive: bool = False) -> Callable[[str], str]:
    """Convenience function for choice validation."""
    def validator(value: str) -> str:
        return InputValidator.validate_choice(value, choices, case_sensitive)
    return validator