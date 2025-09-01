# tests/unit/utils/test_validators.py
"""
Test module for data validation utilities.
Tests input validation, data sanitization, and validation rules.
"""

import pytest
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union
from unittest.mock import Mock, patch


class MockValidators:
    """Mock validation functions for testing"""
    
    @staticmethod
    def validate_required(value, field_name="field"):
        """Validate that a value is not empty"""
        if value is None or value == "" or (isinstance(value, (list, dict)) and len(value) == 0):
            return False, f"{field_name} is required"
        return True, None
    
    @staticmethod
    def validate_string(value, min_length=None, max_length=None, pattern=None, field_name="field"):
        """Validate string with length and pattern constraints"""
        if not isinstance(value, str):
            return False, f"{field_name} must be a string"
        
        if min_length is not None and len(value) < min_length:
            return False, f"{field_name} must be at least {min_length} characters long"
        
        if max_length is not None and len(value) > max_length:
            return False, f"{field_name} must be at most {max_length} characters long"
        
        if pattern is not None and not re.match(pattern, value):
            return False, f"{field_name} format is invalid"
        
        return True, None
    
    @staticmethod
    def validate_email(email, field_name="email"):
        """Validate email address format"""
        if not isinstance(email, str):
            return False, f"{field_name} must be a string"
        
        # Basic email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, f"{field_name} must be a valid email address"
        
        # Additional checks
        if len(email) > 254:  # RFC 5321 limit
            return False, f"{field_name} is too long"
        
        local, domain = email.rsplit('@', 1)
        if len(local) > 64:  # RFC 5321 limit for local part
            return False, f"{field_name} local part is too long"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone, field_name="phone"):
        """Validate phone number format"""
        if not isinstance(phone, str):
            return False, f"{field_name} must be a string"
        
        # Remove common separators
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        # Check if it starts with + for international format
        if cleaned_phone.startswith('+'):
            if len(cleaned_phone) < 8 or len(cleaned_phone) > 15:
                return False, f"{field_name} must be 7-14 digits after country code"
        else:
            if len(cleaned_phone) < 7 or len(cleaned_phone) > 15:
                return False, f"{field_name} must be 7-15 digits"
        
        return True, None
    
    @staticmethod
    def validate_number(value, min_value=None, max_value=None, field_name="field"):
        """Validate numeric value with range constraints"""
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                return False, f"{field_name} must be a number"
        
        if min_value is not None and value < min_value:
            return False, f"{field_name} must be at least {min_value}"
        
        if max_value is not None and value > max_value:
            return False, f"{field_name} must be at most {max_value}"
        
        return True, None
    
    @staticmethod
    def validate_integer(value, min_value=None, max_value=None, field_name="field"):
        """Validate integer value with range constraints"""
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                return False, f"{field_name} must be an integer"
        
        if min_value is not None and value < min_value:
            return False, f"{field_name} must be at least {min_value}"
        
        if max_value is not None and value > max_value:
            return False, f"{field_name} must be at most {max_value}"
        
        return True, None
    
    @staticmethod
    def validate_boolean(value, field_name="field"):
        """Validate boolean value"""
        if not isinstance(value, bool):
            if isinstance(value, str):
                if value.lower() in ('true', '1', 'yes', 'on'):
                    return True, None
                elif value.lower() in ('false', '0', 'no', 'off'):
                    return True, None
            return False, f"{field_name} must be a boolean value"
        
        return True, None
    
    @staticmethod
    def validate_date(value, min_date=None, max_date=None, field_name="field"):
        """Validate date value with range constraints"""
        if isinstance(value, str):
            try:
                # Try common date formats
                for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'):
                    try:
                        value = datetime.strptime(value, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return False, f"{field_name} must be a valid date (YYYY-MM-DD)"
            except ValueError:
                return False, f"{field_name} must be a valid date"
        
        elif isinstance(value, datetime):
            value = value.date()
        elif not isinstance(value, date):
            return False, f"{field_name} must be a date"
        
        if min_date is not None and value < min_date:
            return False, f"{field_name} must be after {min_date}"
        
        if max_date is not None and value > max_date:
            return False, f"{field_name} must be before {max_date}"
        
        return True, None
    
    @staticmethod
    def validate_url(url, field_name="url"):
        """Validate URL format"""
        if not isinstance(url, str):
            return False, f"{field_name} must be a string"
        
        url_pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*)?(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?$'
        
        if not re.match(url_pattern, url):
            return False, f"{field_name} must be a valid URL"
        
        return True, None
    
    @staticmethod
    def validate_choice(value, choices, field_name="field"):
        """Validate that value is in allowed choices"""
        if value not in choices:
            return False, f"{field_name} must be one of: {', '.join(map(str, choices))}"
        
        return True, None
    
    @staticmethod
    def validate_list(value, item_validator=None, min_length=None, max_length=None, field_name="field"):
        """Validate list with optional item validation"""
        if not isinstance(value, list):
            return False, f"{field_name} must be a list"
        
        if min_length is not None and len(value) < min_length:
            return False, f"{field_name} must have at least {min_length} items"
        
        if max_length is not None and len(value) > max_length:
            return False, f"{field_name} must have at most {max_length} items"
        
        if item_validator is not None:
            for i, item in enumerate(value):
                is_valid, error = item_validator(item, f"{field_name}[{i}]")
                if not is_valid:
                    return False, error
        
        return True, None
    
    @staticmethod
    def validate_dict(value, schema=None, field_name="field"):
        """Validate dictionary against schema"""
        if not isinstance(value, dict):
            return False, f"{field_name} must be a dictionary"
        
        if schema is not None:
            for key, validator in schema.items():
                if key in value:
                    is_valid, error = validator(value[key], f"{field_name}.{key}")
                    if not is_valid:
                        return False, error
                elif hasattr(validator, '__name__') and 'required' in validator.__name__:
                    return False, f"{field_name}.{key} is required"
        
        return True, None
    
    @staticmethod
    def validate_password_strength(password, field_name="password"):
        """Validate password strength"""
        if not isinstance(password, str):
            return False, f"{field_name} must be a string"
        
        errors = []
        
        if len(password) < 8:
            errors.append("at least 8 characters")
        
        if not re.search(r'[A-Z]', password):
            errors.append("at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("at least one special character")
        
        if errors:
            return False, f"{field_name} must contain " + ", ".join(errors)
        
        return True, None
    
    @staticmethod
    def sanitize_string(value, strip_html=True, max_length=None):
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        # Remove HTML tags if requested
        if strip_html:
            value = re.sub(r'<[^>]+>', '', value)
        
        # Truncate if too long
        if max_length is not None and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename for safe file system usage"""
        if not isinstance(filename, str):
            filename = str(filename)
        
        # Remove or replace unsafe characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Ensure it's not empty
        if not filename:
            filename = 'unnamed'
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            max_name_length = 255 - len(ext) - 1 if ext else 255
            filename = name[:max_name_length] + ('.' + ext if ext else '')
        
        return filename


class MockValidationSchema:
    """Mock validation schema class for testing"""
    
    def __init__(self, schema):
        self.schema = schema
        self.errors = []
    
    def validate(self, data):
        """Validate data against schema"""
        self.errors = []
        return self._validate_object(data, self.schema, "")
    
    def _validate_object(self, data, schema, path):
        """Recursively validate object"""
        is_valid = True
        
        for field, rules in schema.items():
            field_path = f"{path}.{field}" if path else field
            value = data.get(field)
            
            # Check if field is required
            if 'required' in rules and rules['required']:
                if value is None or value == "":
                    self.errors.append(f"{field_path} is required")
                    is_valid = False
                    continue
            
            # Skip validation if value is None and field is not required
            if value is None:
                continue
            
            # Apply validators
            for validator_name, validator_args in rules.items():
                if validator_name == 'required':
                    continue
                
                validator_func = getattr(MockValidators, f"validate_{validator_name}", None)
                if validator_func:
                    if isinstance(validator_args, dict):
                        field_valid, error = validator_func(value, field_name=field_path, **validator_args)
                    elif isinstance(validator_args, (list, tuple)):
                        field_valid, error = validator_func(value, *validator_args, field_name=field_path)
                    else:
                        field_valid, error = validator_func(value, field_name=field_path)
                    
                    if not field_valid:
                        self.errors.append(error)
                        is_valid = False
        
        return is_valid


class TestRequiredValidation:
    """Test required field validation"""
    
    def test_validate_required_with_value(self):
        """Test required validation with valid value"""
        is_valid, error = MockValidators.validate_required("test value")
        assert is_valid is True
        assert error is None
    
    def test_validate_required_with_none(self):
        """Test required validation with None"""
        is_valid, error = MockValidators.validate_required(None)
        assert is_valid is False
        assert "is required" in error
    
    def test_validate_required_with_empty_string(self):
        """Test required validation with empty string"""
        is_valid, error = MockValidators.validate_required("")
        assert is_valid is False
        assert "is required" in error
    
    def test_validate_required_with_empty_list(self):
        """Test required validation with empty list"""
        is_valid, error = MockValidators.validate_required([])
        assert is_valid is False
        assert "is required" in error
    
    def test_validate_required_with_zero(self):
        """Test required validation with zero (should be valid)"""
        is_valid, error = MockValidators.validate_required(0)
        assert is_valid is True
        assert error is None


class TestStringValidation:
    """Test string validation functions"""
    
    def test_validate_string_valid(self):
        """Test string validation with valid string"""
        is_valid, error = MockValidators.validate_string("hello world")
        assert is_valid is True
        assert error is None
    
    def test_validate_string_non_string(self):
        """Test string validation with non-string"""
        is_valid, error = MockValidators.validate_string(123)
        assert is_valid is False
        assert "must be a string" in error
    
    def test_validate_string_min_length(self):
        """Test string validation with minimum length"""
        is_valid, error = MockValidators.validate_string("hi", min_length=5)
        assert is_valid is False
        assert "at least 5 characters" in error
    
    def test_validate_string_max_length(self):
        """Test string validation with maximum length"""
        is_valid, error = MockValidators.validate_string("very long string", max_length=5)
        assert is_valid is False
        assert "at most 5 characters" in error
    
    def test_validate_string_pattern_match(self):
        """Test string validation with pattern that matches"""
        pattern = r'^\d{3}-\d{3}-\d{4}$'  # Phone pattern
        is_valid, error = MockValidators.validate_string("123-456-7890", pattern=pattern)
        assert is_valid is True
        assert error is None
    
    def test_validate_string_pattern_no_match(self):
        """Test string validation with pattern that doesn't match"""
        pattern = r'^\d{3}-\d{3}-\d{4}$'  # Phone pattern
        is_valid, error = MockValidators.validate_string("invalid-phone", pattern=pattern)
        assert is_valid is False
        assert "format is invalid" in error


class TestEmailValidation:
    """Test email validation functions"""
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@sub.domain.org",
            "a@b.co"
        ]
        
        for email in valid_emails:
            is_valid, error = MockValidators.validate_email(email)
            assert is_valid is True, f"Email {email} should be valid"
            assert error is None
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user space@domain.com",
            "user@domain",
            ""
        ]
        
        for email in invalid_emails:
            is_valid, error = MockValidators.validate_email(email)
            assert is_valid is False, f"Email {email} should be invalid"
            assert "valid email address" in error
    
    def test_validate_email_too_long(self):
        """Test email validation with overly long email"""
        long_email = "a" * 250 + "@example.com"
        is_valid, error = MockValidators.validate_email(long_email)
        assert is_valid is False
        assert "too long" in error
    
    def test_validate_email_long_local_part(self):
        """Test email validation with long local part"""
        long_local = "a" * 65 + "@example.com"
        is_valid, error = MockValidators.validate_email(long_local)
        assert is_valid is False
        assert "local part is too long" in error


class TestPhoneValidation:
    """Test phone number validation"""
    
    def test_validate_phone_valid_formats(self):
        """Test phone validation with valid formats"""
        valid_phones = [
            "+1234567890",
            "+1-234-567-8900",
            "123-456-7890",
            "(123) 456-7890",
            "1234567890"
        ]
        
        for phone in valid_phones:
            is_valid, error = MockValidators.validate_phone(phone)
            assert is_valid is True, f"Phone {phone} should be valid"
            assert error is None
    
    def test_validate_phone_invalid_length(self):
        """Test phone validation with invalid length"""
        invalid_phones = [
            "123",      # Too short
            "123456",   # Too short
            "1234567890123456789"  # Too long
        ]
        
        for phone in invalid_phones:
            is_valid, error = MockValidators.validate_phone(phone)
            assert is_valid is False, f"Phone {phone} should be invalid"
            assert "digits" in error


class TestNumberValidation:
    """Test number validation functions"""
    
    def test_validate_number_valid(self):
        """Test number validation with valid numbers"""
        valid_numbers = [42, 3.14, "123", "45.67"]
        
        for num in valid_numbers:
            is_valid, error = MockValidators.validate_number(num)
            assert is_valid is True, f"Number {num} should be valid"
            assert error is None
    
    def test_validate_number_invalid(self):
        """Test number validation with invalid values"""
        invalid_numbers = ["not a number", "abc", None, []]
        
        for num in invalid_numbers:
            is_valid, error = MockValidators.validate_number(num)
            assert is_valid is False, f"Value {num} should be invalid"
            assert "must be a number" in error
    
    def test_validate_number_range(self):
        """Test number validation with range constraints"""
        # Valid range
        is_valid, error = MockValidators.validate_number(50, min_value=0, max_value=100)
        assert is_valid is True
        
        # Below minimum
        is_valid, error = MockValidators.validate_number(-10, min_value=0, max_value=100)
        assert is_valid is False
        assert "at least 0" in error
        
        # Above maximum
        is_valid, error = MockValidators.validate_number(150, min_value=0, max_value=100)
        assert is_valid is False
        assert "at most 100" in error
    
    def test_validate_integer_valid(self):
        """Test integer validation with valid integers"""
        valid_integers = [42, "123", 0, -5]
        
        for num in valid_integers:
            is_valid, error = MockValidators.validate_integer(num)
            assert is_valid is True, f"Integer {num} should be valid"
            assert error is None
    
    def test_validate_integer_invalid(self):
        """Test integer validation with invalid values"""
        invalid_integers = [3.14, "3.14", "abc", None]
        
        for num in invalid_integers:
            is_valid, error = MockValidators.validate_integer(num)
            assert is_valid is False, f"Value {num} should be invalid"
            assert "must be an integer" in error


class TestBooleanValidation:
    """Test boolean validation"""
    
    def test_validate_boolean_valid(self):
        """Test boolean validation with valid values"""
        valid_booleans = [
            True, False,
            "true", "false",
            "True", "False",
            "1", "0",
            "yes", "no",
            "on", "off"
        ]
        
        for val in valid_booleans:
            is_valid, error = MockValidators.validate_boolean(val)
            assert is_valid is True, f"Boolean {val} should be valid"
            assert error is None
    
    def test_validate_boolean_invalid(self):
        """Test boolean validation with invalid values"""
        invalid_booleans = ["maybe", "123", None, []]
        
        for val in invalid_booleans:
            is_valid, error = MockValidators.validate_boolean(val)
            assert is_valid is False, f"Value {val} should be invalid"
            assert "must be a boolean" in error


class TestDateValidation:
    """Test date validation"""
    
    def test_validate_date_valid_formats(self):
        """Test date validation with valid formats"""
        valid_dates = [
            "2023-12-25",
            "12/25/2023",
            "25/12/2023",
            date(2023, 12, 25),
            datetime(2023, 12, 25, 10, 30, 0)
        ]
        
        for dt in valid_dates:
            is_valid, error = MockValidators.validate_date(dt)
            assert is_valid is True, f"Date {dt} should be valid"
            assert error is None
    
    def test_validate_date_invalid(self):
        """Test date validation with invalid values"""
        invalid_dates = ["invalid-date", "2023-13-01", "32/12/2023", 123, None]
        
        for dt in invalid_dates:
            is_valid, error = MockValidators.validate_date(dt)
            assert is_valid is False, f"Value {dt} should be invalid"
            assert "valid date" in error
    
    def test_validate_date_range(self):
        """Test date validation with range constraints"""
        test_date = date(2023, 6, 15)
        min_date = date(2023, 1, 1)
        max_date = date(2023, 12, 31)
        
        # Valid range
        is_valid, error = MockValidators.validate_date(test_date, min_date=min_date, max_date=max_date)
        assert is_valid is True
        
        # Before minimum
        early_date = date(2022, 12, 31)
        is_valid, error = MockValidators.validate_date(early_date, min_date=min_date, max_date=max_date)
        assert is_valid is False
        assert "must be after" in error
        
        # After maximum
        late_date = date(2024, 1, 1)
        is_valid, error = MockValidators.validate_date(late_date, min_date=min_date, max_date=max_date)
        assert is_valid is False
        assert "must be before" in error


class TestChoiceValidation:
    """Test choice validation"""
    
    def test_validate_choice_valid(self):
        """Test choice validation with valid choice"""
        choices = ["red", "green", "blue"]
        is_valid, error = MockValidators.validate_choice("red", choices)
        assert is_valid is True
        assert error is None
    
    def test_validate_choice_invalid(self):
        """Test choice validation with invalid choice"""
        choices = ["red", "green", "blue"]
        is_valid, error = MockValidators.validate_choice("yellow", choices)
        assert is_valid is False
        assert "must be one of" in error
        assert "red, green, blue" in error


class TestListValidation:
    """Test list validation"""
    
    def test_validate_list_valid(self):
        """Test list validation with valid list"""
        is_valid, error = MockValidators.validate_list([1, 2, 3])
        assert is_valid is True
        assert error is None
    
    def test_validate_list_invalid_type(self):
        """Test list validation with non-list"""
        is_valid, error = MockValidators.validate_list("not a list")
        assert is_valid is False
        assert "must be a list" in error
    
    def test_validate_list_length_constraints(self):
        """Test list validation with length constraints"""
        # Valid length
        is_valid, error = MockValidators.validate_list([1, 2, 3], min_length=2, max_length=5)
        assert is_valid is True
        
        # Too short
        is_valid, error = MockValidators.validate_list([1], min_length=2, max_length=5)
        assert is_valid is False
        assert "at least 2 items" in error
        
        # Too long
        is_valid, error = MockValidators.validate_list([1, 2, 3, 4, 5, 6], min_length=2, max_length=5)
        assert is_valid is False
        assert "at most 5 items" in error
    
    def test_validate_list_with_item_validator(self):
        """Test list validation with item validator"""
        def string_validator(value, field_name):
            return MockValidators.validate_string(value, field_name=field_name)
        
        # Valid list
        is_valid, error = MockValidators.validate_list(["a", "b", "c"], item_validator=string_validator)
        assert is_valid is True
        
        # Invalid item
        is_valid, error = MockValidators.validate_list(["a", 123, "c"], item_validator=string_validator)
        assert is_valid is False
        assert "field[1]" in error
        assert "must be a string" in error


class TestPasswordValidation:
    """Test password strength validation"""
    
    def test_validate_password_strong(self):
        """Test password validation with strong password"""
        strong_password = "SecurePass123!"
        is_valid, error = MockValidators.validate_password_strength(strong_password)
        assert is_valid is True
        assert error is None
    
    def test_validate_password_weak(self):
        """Test password validation with weak passwords"""
        weak_passwords = [
            ("short", "at least 8 characters"),
            ("nouppercase123!", "uppercase letter"),
            ("NOLOWERCASE123!", "lowercase letter"),
            ("NoDigitsHere!", "digit"),
            ("NoSpecialChars123", "special character")
        ]
        
        for password, expected_error in weak_passwords:
            is_valid, error = MockValidators.validate_password_strength(password)
            assert is_valid is False, f"Password '{password}' should be invalid"
            assert expected_error in error


class TestSanitization:
    """Test data sanitization functions"""
    
    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        result = MockValidators.sanitize_string("  hello world  ")
        assert result == "hello world"
    
    def test_sanitize_string_html(self):
        """Test HTML tag removal"""
        html_string = "<script>alert('xss')</script>Hello <b>World</b>"
        result = MockValidators.sanitize_string(html_string, strip_html=True)
        assert result == "Hello World"
        assert "<script>" not in result
        assert "<b>" not in result
    
    def test_sanitize_string_max_length(self):
        """Test string truncation"""
        long_string = "a" * 100
        result = MockValidators.sanitize_string(long_string, max_length=50)
        assert len(result) == 50
    
    def test_sanitize_filename_unsafe_chars(self):
        """Test filename sanitization with unsafe characters"""
        unsafe_filename = "file<>:\"/\\|?*.txt"
        result = MockValidators.sanitize_filename(unsafe_filename)
        assert result == "file_________.txt"
        assert all(c not in result for c in '<>:"/\\|?*')
    
    def test_sanitize_filename_control_chars(self):
        """Test filename sanitization with control characters"""
        filename_with_control = "file\x00\x1f\x7fname.txt"
        result = MockValidators.sanitize_filename(filename_with_control)
        assert "\x00" not in result
        assert "\x1f" not in result
        assert "\x7f" not in result
    
    def test_sanitize_filename_empty(self):
        """Test filename sanitization with empty result"""
        result = MockValidators.sanitize_filename("")
        assert result == "unnamed"
    
    def test_sanitize_filename_too_long(self):
        """Test filename sanitization with overly long filename"""
        long_filename = "a" * 300 + ".txt"
        result = MockValidators.sanitize_filename(long_filename)
        assert len(result) <= 255
        assert result.endswith(".txt")


class TestValidationSchema:
    """Test validation schema functionality"""
    
    def test_schema_validation_success(self):
        """Test successful schema validation"""
        schema = {
            "name": {"required": True, "string": {"min_length": 2, "max_length": 50}},
            "email": {"required": True, "email": True},
            "age": {"integer": {"min_value": 0, "max_value": 120}}
        }
        
        validator = MockValidationSchema(schema)
        
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
        
        is_valid = validator.validate(data)
        assert is_valid is True
        assert len(validator.errors) == 0
    
    def test_schema_validation_required_fields(self):
        """Test schema validation with missing required fields"""
        schema = {
            "name": {"required": True, "string": True},
            "email": {"required": True, "email": True},
            "age": {"integer": True}
        }
        
        validator = MockValidationSchema(schema)
        
        data = {
            "age": 30
            # Missing required name and email
        }
        
        is_valid = validator.validate(data)
        assert is_valid is False
        assert len(validator.errors) == 2
        assert any("name is required" in error for error in validator.errors)
        assert any("email is required" in error for error in validator.errors)
    
    def test_schema_validation_field_errors(self):
        """Test schema validation with field validation errors"""
        schema = {
            "name": {"required": True, "string": {"min_length": 5}},
            "email": {"required": True, "email": True},
            "age": {"integer": {"min_value": 18}}
        }
        
        validator = MockValidationSchema(schema)
        
        data = {
            "name": "Jo",  # Too short
            "email": "invalid-email",  # Invalid format
            "age": 15  # Too young
        }
        
        is_valid = validator.validate(data)
        assert is_valid is False
        assert len(validator.errors) >= 3
        assert any("at least 5 characters" in error for error in validator.errors)
        assert any("valid email address" in error for error in validator.errors)
        assert any("at least 18" in error for error in validator.errors)
    
    def test_schema_validation_optional_fields(self):
        """Test schema validation with optional fields"""
        schema = {
            "name": {"required": True, "string": True},
            "bio": {"string": {"max_length": 100}},  # Optional field
            "website": {"url": True}  # Optional field
        }
        
        validator = MockValidationSchema(schema)
        
        # Data with only required field
        data = {"name": "John Doe"}
        is_valid = validator.validate(data)
        assert is_valid is True
        
        # Data with optional fields
        data = {
            "name": "John Doe",
            "bio": "Software developer",
            "website": "https://johndoe.com"
        }
        is_valid = validator.validate(data)
        assert is_valid is True
    
    def test_schema_validation_complex_data(self):
        """Test schema validation with complex nested data"""
        schema = {
            "user": {
                "required": True,
                "dict": {
                    "name": {"required": True, "string": {"min_length": 2}},
                    "email": {"required": True, "email": True}
                }
            },
            "preferences": {
                "dict": {
                    "theme": {"choice": ["light", "dark"]},
                    "notifications": {"boolean": True}
                }
            }
        }
        
        validator = MockValidationSchema(schema)
        
        data = {
            "user": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        is_valid = validator.validate(data)
        assert is_valid is True


class TestValidationIntegration:
    """Test integration of multiple validation functions"""
    
    def test_user_registration_validation(self):
        """Test complete user registration validation"""
        def validate_user_registration(data):
            errors = []
            
            # Validate required fields
            for field in ["username", "email", "password"]:
                is_valid, error = MockValidators.validate_required(data.get(field), field)
                if not is_valid:
                    errors.append(error)
            
            # Validate username
            if "username" in data:
                is_valid, error = MockValidators.validate_string(
                    data["username"], 
                    min_length=3, 
                    max_length=30, 
                    pattern=r'^[a-zA-Z0-9_]+,
                    field_name="username"
                )
                if not is_valid:
                    errors.append(error)
            
            # Validate email
            if "email" in data:
                is_valid, error = MockValidators.validate_email(data["email"])
                if not is_valid:
                    errors.append(error)
            
            # Validate password
            if "password" in data:
                is_valid, error = MockValidators.validate_password_strength(data["password"])
                if not is_valid:
                    errors.append(error)
            
            # Validate optional age
            if "age" in data and data["age"] is not None:
                is_valid, error = MockValidators.validate_integer(
                    data["age"], 
                    min_value=13, 
                    max_value=120,
                    field_name="age"
                )
                if not is_valid:
                    errors.append(error)
            
            return len(errors) == 0, errors
        
        # Valid registration data
        valid_data = {
            "username": "johndoe123",
            "email": "john@example.com",
            "password": "SecurePass123!",
            "age": 25
        }
        
        is_valid, errors = validate_user_registration(valid_data)
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid registration data
        invalid_data = {
            "username": "jo",  # Too short
            "email": "invalid-email",  # Invalid format
            "password": "weak",  # Weak password
            "age": 10  # Too young
        }
        
        is_valid, errors = validate_user_registration(invalid_data)
        assert is_valid is False
        assert len(errors) >= 4
    
    def test_api_request_validation(self):
        """Test API request validation workflow"""
        def validate_api_request(method, path, data=None, headers=None):
            errors = []
            
            # Validate HTTP method
            valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
            is_valid, error = MockValidators.validate_choice(method, valid_methods, "method")
            if not is_valid:
                errors.append(error)
            
            # Validate path
            is_valid, error = MockValidators.validate_string(
                path, 
                min_length=1, 
                pattern=r'^/[a-zA-Z0-9/_-]*,
                field_name="path"
            )
            if not is_valid:
                errors.append(error)
            
            # Validate Content-Type for requests with body
            if method in ["POST", "PUT", "PATCH"] and data:
                content_type = headers.get("Content-Type") if headers else None
                is_valid, error = MockValidators.validate_required(content_type, "Content-Type")
                if not is_valid:
                    errors.append(error)
            
            # Validate Authorization header for protected endpoints
            if path.startswith("/api/protected/"):
                auth_header = headers.get("Authorization") if headers else None
                is_valid, error = MockValidators.validate_required(auth_header, "Authorization")
                if not is_valid:
                    errors.append(error)
                elif not auth_header.startswith("Bearer "):
                    errors.append("Authorization must be Bearer token")
            
            return len(errors) == 0, errors
        
        # Valid API request
        is_valid, errors = validate_api_request(
            "POST", 
            "/api/users",
            data={"name": "John"},
            headers={"Content-Type": "application/json"}
        )
        assert is_valid is True
        
        # Invalid API request
        is_valid, errors = validate_api_request(
            "INVALID",  # Invalid method
            "",  # Invalid path
            data={"name": "John"}
            # Missing Content-Type header
        )
        assert is_valid is False
        assert len(errors) >= 3
    
    def test_form_data_sanitization_and_validation(self):
        """Test form data sanitization and validation workflow"""
        def process_form_data(raw_data):
            # First sanitize the data
            sanitized_data = {}
            
            if "name" in raw_data:
                sanitized_data["name"] = MockValidators.sanitize_string(
                    raw_data["name"], 
                    strip_html=True, 
                    max_length=100
                )
            
            if "bio" in raw_data:
                sanitized_data["bio"] = MockValidators.sanitize_string(
                    raw_data["bio"], 
                    strip_html=True, 
                    max_length=500
                )
            
            if "profile_image" in raw_data:
                sanitized_data["profile_image"] = MockValidators.sanitize_filename(
                    raw_data["profile_image"]
                )
            
            # Then validate the sanitized data
            errors = []
            
            # Validate name
            if "name" in sanitized_data:
                is_valid, error = MockValidators.validate_string(
                    sanitized_data["name"], 
                    min_length=2, 
                    max_length=100,
                    field_name="name"
                )
                if not is_valid:
                    errors.append(error)
            
            # Validate bio
            if "bio" in sanitized_data:
                is_valid, error = MockValidators.validate_string(
                    sanitized_data["bio"], 
                    max_length=500,
                    field_name="bio"
                )
                if not is_valid:
                    errors.append(error)
            
            return sanitized_data, len(errors) == 0, errors
        
        # Form data with potentially malicious content
        raw_form_data = {
            "name": "  <script>alert('xss')</script>John Doe  ",
            "bio": "<b>Software developer</b> with <script>evil</script> interests",
            "profile_image": "user<>profile:image?.jpg"
        }
        
        sanitized_data, is_valid, errors = process_form_data(raw_form_data)
        
        # Check sanitization worked
        assert "<script>" not in sanitized_data["name"]
        assert sanitized_data["name"] == "John Doe"
        assert "<script>" not in sanitized_data["bio"]
        assert sanitized_data["bio"] == "Software developer with  interests"
        assert sanitized_data["profile_image"] == "user__profile_image_.jpg"
        
        # Check validation passed
        assert is_valid is True
        assert len(errors) == 0
    
    def test_bulk_data_validation(self):
        """Test validation of bulk data operations"""
        def validate_bulk_users(users_data):
            all_errors = []
            valid_users = []
            
            for i, user_data in enumerate(users_data):
                user_errors = []
                
                # Validate each user
                schema = {
                    "name": {"required": True, "string": {"min_length": 2, "max_length": 50}},
                    "email": {"required": True, "email": True},
                    "age": {"integer": {"min_value": 0, "max_value": 120}}
                }
                
                validator = MockValidationSchema(schema)
                is_valid = validator.validate(user_data)
                
                if is_valid:
                    valid_users.append(user_data)
                else:
                    for error in validator.errors:
                        user_errors.append(f"User {i+1}: {error}")
                    all_errors.extend(user_errors)
            
            return valid_users, all_errors
        
        # Mixed valid and invalid users
        users_data = [
            {"name": "John Doe", "email": "john@example.com", "age": 30},  # Valid
            {"name": "J", "email": "invalid-email", "age": 200},  # Invalid
            {"name": "Jane Smith", "email": "jane@example.com", "age": 25},  # Valid
            {"email": "missing@example.com", "age": 35},  # Missing name
        ]
        
        valid_users, errors = validate_bulk_users(users_data)
        
        assert len(valid_users) == 2  # Only 2 valid users
        assert len(errors) > 0  # Should have validation errors
        assert any("User 2:" in error for error in errors)
        assert any("User 4:" in error for error in errors)
    
    def test_conditional_validation(self):
        """Test conditional validation based on other field values"""
        def validate_conditional_form(data):
            errors = []
            
            # Validate account type
            account_types = ["personal", "business"]
            is_valid, error = MockValidators.validate_choice(
                data.get("account_type"), 
                account_types, 
                "account_type"
            )
            if not is_valid:
                errors.append(error)
                return False, errors
            
            # Conditional validation based on account type
            if data.get("account_type") == "business":
                # Business accounts require company name and tax ID
                is_valid, error = MockValidators.validate_required(
                    data.get("company_name"), 
                    "company_name"
                )
                if not is_valid:
                    errors.append(error)
                
                is_valid, error = MockValidators.validate_string(
                    data.get("tax_id"), 
                    min_length=9, 
                    max_length=15,
                    pattern=r'^[A-Z0-9-]+,
                    field_name="tax_id"
                )
                if not is_valid:
                    errors.append(error)
            
            elif data.get("account_type") == "personal":
                # Personal accounts require date of birth
                is_valid, error = MockValidators.validate_date(
                    data.get("date_of_birth"),
                    max_date=date.today() - timedelta(days=365*13),  # Must be at least 13 years old
                    field_name="date_of_birth"
                )
                if not is_valid:
                    errors.append(error)
            
            return len(errors) == 0, errors
        
        # Valid business account
        business_data = {
            "account_type": "business",
            "company_name": "Acme Corp",
            "tax_id": "12-3456789"
        }
        is_valid, errors = validate_conditional_form(business_data)
        assert is_valid is True
        
        # Valid personal account
        personal_data = {
            "account_type": "personal",
            "date_of_birth": "1990-01-01"
        }
        is_valid, errors = validate_conditional_form(personal_data)
        assert is_valid is True
        
        # Invalid business account (missing required fields)
        invalid_business_data = {
            "account_type": "business"
            # Missing company_name and tax_id
        }
        is_valid, errors = validate_conditional_form(invalid_business_data)
        assert is_valid is False
        assert len(errors) >= 2


class TestValidationPerformance:
    """Test validation performance and edge cases"""
    
    def test_validation_with_large_data(self):
        """Test validation performance with large datasets"""
        # Generate large list for validation
        large_list = list(range(1000))
        
        def integer_validator(value, field_name):
            return MockValidators.validate_integer(value, min_value=0, max_value=999, field_name=field_name)
        
        is_valid, error = MockValidators.validate_list(
            large_list, 
            item_validator=integer_validator,
            min_length=100,
            max_length=2000
        )
        
        assert is_valid is True
        assert error is None
    
    def test_validation_with_nested_structures(self):
        """Test validation with deeply nested data structures"""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep_value"
                        }
                    }
                }
            }
        }
        
        # Validate the nested structure exists
        assert "level1" in nested_data
        assert "level2" in nested_data["level1"]
        assert "level3" in nested_data["level1"]["level2"]
        assert "level4" in nested_data["level1"]["level2"]["level3"]
        assert nested_data["level1"]["level2"]["level3"]["level4"]["value"] == "deep_value"
    
    def test_validation_edge_cases(self):
        """Test validation with edge cases and boundary values"""
        # Test with boundary values
        boundary_tests = [
            # String length boundaries
            ("", MockValidators.validate_string, {"min_length": 1}),
            ("a", MockValidators.validate_string, {"min_length": 1}),
            ("a" * 255, MockValidators.validate_string, {"max_length": 255}),
            ("a" * 256, MockValidators.validate_string, {"max_length": 255}),
            
            # Number boundaries
            (0, MockValidators.validate_integer, {"min_value": 0}),
            (-1, MockValidators.validate_integer, {"min_value": 0}),
            (100, MockValidators.validate_integer, {"max_value": 100}),
            (101, MockValidators.validate_integer, {"max_value": 100}),
        ]
        
        for value, validator, kwargs in boundary_tests:
            is_valid, error = validator(value, **kwargs)
            # Each test should either pass or fail consistently
            assert isinstance(is_valid, bool)
            if not is_valid:
                assert isinstance(error, str)
                assert len(error) > 0
    
    def test_validation_error_messages(self):
        """Test that validation error messages are helpful and consistent"""
        # Test various validation failures to ensure good error messages
        test_cases = [
            (MockValidators.validate_required, [None], "is required"),
            (MockValidators.validate_email, ["invalid"], "valid email"),
            (MockValidators.validate_string, ["", {"min_length": 5}], "at least 5 characters"),
            (MockValidators.validate_integer, ["abc"], "must be an integer"),
            (MockValidators.validate_choice, ["invalid", ["a", "b", "c"]], "must be one of"),
        ]
        
        for validator, args, expected_error_text in test_cases:
            if len(args) == 2 and isinstance(args[1], dict):
                is_valid, error = validator(args[0], **args[1])
            else:
                is_valid, error = validator(*args)
            
            assert is_valid is False
            assert expected_error_text in error.lower()
            assert error.strip() != ""  # Error message should not be empty or just whitespace