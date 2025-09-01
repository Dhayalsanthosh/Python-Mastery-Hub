# tests/unit/utils/test_helpers.py
"""
Test module for utility helper functions.
Tests common utilities, data processing, formatting, and helper functions.
"""

import pytest
import os
import json
import tempfile
import hashlib
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, mock_open
from typing import Dict, List, Any, Optional


class MockHelpers:
    """Mock helper functions for testing"""
    
    @staticmethod
    def generate_unique_id(prefix="", length=8):
        """Generate unique identifier"""
        if prefix:
            return f"{prefix}_{uuid.uuid4().hex[:length]}"
        return uuid.uuid4().hex[:length]
    
    @staticmethod
    def hash_string(text, algorithm='sha256'):
        """Hash a string using specified algorithm"""
        if algorithm == 'md5':
            return hashlib.md5(text.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(text.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(text.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def verify_hash(text, hash_value, algorithm='sha256'):
        """Verify if text matches hash"""
        computed_hash = MockHelpers.hash_string(text, algorithm)
        return computed_hash == hash_value
    
    @staticmethod
    def safe_json_loads(json_string, default=None):
        """Safely load JSON with fallback"""
        try:
            return json.loads(json_string)
        except (json.JSONDecodeError, TypeError):
            return default
    
    @staticmethod
    def safe_json_dumps(obj, default=None):
        """Safely dump JSON with fallback"""
        try:
            return json.dumps(obj, default=str)
        except (TypeError, ValueError):
            return default
    
    @staticmethod
    def deep_merge_dicts(dict1, dict2):
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = MockHelpers.deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def flatten_dict(d, parent_key='', sep='.'):
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(MockHelpers.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def chunk_list(lst, chunk_size):
        """Split list into chunks of specified size"""
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    @staticmethod
    def remove_duplicates(lst, key=None):
        """Remove duplicates from list, optionally by key function"""
        if key is None:
            return list(dict.fromkeys(lst))
        
        seen = set()
        result = []
        for item in lst:
            k = key(item)
            if k not in seen:
                seen.add(k)
                result.append(item)
        return result
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename for safe file system usage"""
        import re
        # Remove or replace unsafe characters
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        safe_filename = safe_filename.strip('. ')
        # Limit length
        if len(safe_filename) > 255:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:250] + ext
        return safe_filename or 'unnamed'
    
    @staticmethod
    def format_bytes(bytes_value):
        """Format bytes to human readable format"""
        if bytes_value == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        while bytes_value >= 1024 and i < len(size_names) - 1:
            bytes_value /= 1024.0
            i += 1
        
        return f"{bytes_value:.2f} {size_names[i]}"
    
    @staticmethod
    def humanize_duration(seconds):
        """Convert seconds to human readable duration"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"
    
    @staticmethod
    def parse_duration(duration_str):
        """Parse duration string to seconds"""
        import re
        
        # Pattern to match duration like "2h30m", "45s", "1d12h"
        pattern = r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        match = re.match(pattern, duration_str.lower())
        
        if not match:
            raise ValueError(f"Invalid duration format: {duration_str}")
        
        days, hours, minutes, seconds = match.groups()
        
        total_seconds = 0
        if days:
            total_seconds += int(days) * 86400
        if hours:
            total_seconds += int(hours) * 3600
        if minutes:
            total_seconds += int(minutes) * 60
        if seconds:
            total_seconds += int(seconds)
        
        return total_seconds
    
    @staticmethod
    def retry_operation(func, max_retries=3, delay=1, exceptions=(Exception,)):
        """Retry operation with exponential backoff"""
        import time
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except exceptions as e:
                if attempt == max_retries:
                    raise e
                time.sleep(delay * (2 ** attempt))
        
        return None
    
    @staticmethod
    def batch_process(items, batch_size, processor_func):
        """Process items in batches"""
        results = []
        batches = MockHelpers.chunk_list(items, batch_size)
        
        for batch in batches:
            batch_result = processor_func(batch)
            if isinstance(batch_result, list):
                results.extend(batch_result)
            else:
                results.append(batch_result)
        
        return results
    
    @staticmethod
    def memoize(func):
        """Simple memoization decorator"""
        cache = {}
        
        def wrapper(*args, **kwargs):
            # Create cache key from args and kwargs
            key = str(args) + str(sorted(kwargs.items()))
            
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            
            return cache[key]
        
        wrapper.cache = cache
        wrapper.cache_clear = lambda: cache.clear()
        return wrapper
    
    @staticmethod
    def rate_limiter(max_calls, time_window):
        """Create a rate limiter decorator"""
        calls = []
        
        def decorator(func):
            def wrapper(*args, **kwargs):
                now = time.time()
                
                # Remove old calls outside the time window
                calls[:] = [call_time for call_time in calls if now - call_time < time_window]
                
                if len(calls) >= max_calls:
                    raise Exception("Rate limit exceeded")
                
                calls.append(now)
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    def validate_email(email):
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password, min_length=8, require_special=True, require_digits=True):
        """Validate password strength"""
        import re
        
        errors = []
        
        if len(password) < min_length:
            errors.append(f"Password must be at least {min_length} characters long")
        
        if require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def generate_random_string(length=10, include_digits=True, include_special=False):
        """Generate random string"""
        import random
        import string
        
        chars = string.ascii_letters
        if include_digits:
            chars += string.digits
        if include_special:
            chars += "!@#$%^&*"
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def is_valid_uuid(uuid_string):
        """Check if string is valid UUID"""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_file_extension(filename):
        """Get file extension safely"""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def ensure_directory_exists(directory_path):
        """Ensure directory exists, create if not"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception:
            return False


class TestUniqueIdGeneration:
    """Test unique ID generation functions"""
    
    def test_generate_unique_id_without_prefix(self):
        """Test generating unique ID without prefix"""
        id1 = MockHelpers.generate_unique_id()
        id2 = MockHelpers.generate_unique_id()
        
        assert len(id1) == 8
        assert len(id2) == 8
        assert id1 != id2
        assert all(c in '0123456789abcdef' for c in id1)
    
    def test_generate_unique_id_with_prefix(self):
        """Test generating unique ID with prefix"""
        user_id = MockHelpers.generate_unique_id("user", 6)
        
        assert user_id.startswith("user_")
        assert len(user_id) == 11  # "user_" + 6 chars
    
    def test_generate_unique_id_custom_length(self):
        """Test generating unique ID with custom length"""
        short_id = MockHelpers.generate_unique_id(length=4)
        long_id = MockHelpers.generate_unique_id(length=16)
        
        assert len(short_id) == 4
        assert len(long_id) == 16
    
    def test_is_valid_uuid(self):
        """Test UUID validation"""
        valid_uuid = str(uuid.uuid4())
        invalid_uuid = "not-a-uuid"
        
        assert MockHelpers.is_valid_uuid(valid_uuid) is True
        assert MockHelpers.is_valid_uuid(invalid_uuid) is False


class TestHashingFunctions:
    """Test hashing and verification functions"""
    
    def test_hash_string_sha256(self):
        """Test SHA256 hashing"""
        text = "hello world"
        hash_value = MockHelpers.hash_string(text, 'sha256')
        
        assert len(hash_value) == 64  # SHA256 produces 64 char hex string
        assert hash_value == hashlib.sha256(text.encode()).hexdigest()
    
    def test_hash_string_md5(self):
        """Test MD5 hashing"""
        text = "hello world"
        hash_value = MockHelpers.hash_string(text, 'md5')
        
        assert len(hash_value) == 32  # MD5 produces 32 char hex string
        assert hash_value == hashlib.md5(text.encode()).hexdigest()
    
    def test_hash_string_unsupported_algorithm(self):
        """Test unsupported hashing algorithm"""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            MockHelpers.hash_string("test", 'unsupported')
    
    def test_verify_hash_correct(self):
        """Test hash verification with correct hash"""
        text = "password123"
        hash_value = MockHelpers.hash_string(text)
        
        assert MockHelpers.verify_hash(text, hash_value) is True
    
    def test_verify_hash_incorrect(self):
        """Test hash verification with incorrect hash"""
        text = "password123"
        wrong_hash = "incorrect_hash"
        
        assert MockHelpers.verify_hash(text, wrong_hash) is False


class TestJSONOperations:
    """Test JSON handling functions"""
    
    def test_safe_json_loads_valid(self):
        """Test safe JSON loading with valid JSON"""
        json_string = '{"name": "John", "age": 30}'
        result = MockHelpers.safe_json_loads(json_string)
        
        assert result == {"name": "John", "age": 30}
    
    def test_safe_json_loads_invalid(self):
        """Test safe JSON loading with invalid JSON"""
        invalid_json = '{"name": "John", "age":}'
        result = MockHelpers.safe_json_loads(invalid_json, default={})
        
        assert result == {}
    
    def test_safe_json_loads_none_input(self):
        """Test safe JSON loading with None input"""
        result = MockHelpers.safe_json_loads(None, default=[])
        
        assert result == []
    
    def test_safe_json_dumps_valid(self):
        """Test safe JSON dumping with valid object"""
        obj = {"name": "John", "age": 30}
        result = MockHelpers.safe_json_dumps(obj)
        
        assert result == '{"name": "John", "age": 30}'
    
    def test_safe_json_dumps_with_datetime(self):
        """Test safe JSON dumping with datetime object"""
        obj = {"created": datetime.now()}
        result = MockHelpers.safe_json_dumps(obj)
        
        assert result is not None
        assert "created" in result


class TestDictionaryOperations:
    """Test dictionary manipulation functions"""
    
    def test_deep_merge_dicts_simple(self):
        """Test deep merging of simple dictionaries"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        
        result = MockHelpers.deep_merge_dicts(dict1, dict2)
        
        assert result == {"a": 1, "b": 3, "c": 4}
    
    def test_deep_merge_dicts_nested(self):
        """Test deep merging of nested dictionaries"""
        dict1 = {"user": {"name": "John", "age": 30}, "settings": {"theme": "dark"}}
        dict2 = {"user": {"email": "john@example.com"}, "settings": {"language": "en"}}
        
        result = MockHelpers.deep_merge_dicts(dict1, dict2)
        
        expected = {
            "user": {"name": "John", "age": 30, "email": "john@example.com"},
            "settings": {"theme": "dark", "language": "en"}
        }
        assert result == expected
    
    def test_flatten_dict_simple(self):
        """Test flattening simple nested dictionary"""
        nested_dict = {
            "user": {
                "profile": {
                    "name": "John",
                    "age": 30
                },
                "settings": {
                    "theme": "dark"
                }
            }
        }
        
        result = MockHelpers.flatten_dict(nested_dict)
        
        expected = {
            "user.profile.name": "John",
            "user.profile.age": 30,
            "user.settings.theme": "dark"
        }
        assert result == expected
    
    def test_flatten_dict_custom_separator(self):
        """Test flattening with custom separator"""
        nested_dict = {"a": {"b": {"c": 1}}}
        result = MockHelpers.flatten_dict(nested_dict, sep='_')
        
        assert result == {"a_b_c": 1}


class TestListOperations:
    """Test list manipulation functions"""
    
    def test_chunk_list_even_division(self):
        """Test chunking list with even division"""
        lst = [1, 2, 3, 4, 5, 6]
        chunks = MockHelpers.chunk_list(lst, 2)
        
        assert chunks == [[1, 2], [3, 4], [5, 6]]
    
    def test_chunk_list_uneven_division(self):
        """Test chunking list with uneven division"""
        lst = [1, 2, 3, 4, 5]
        chunks = MockHelpers.chunk_list(lst, 2)
        
        assert chunks == [[1, 2], [3, 4], [5]]
    
    def test_chunk_list_larger_chunk_size(self):
        """Test chunking list with larger chunk size than list"""
        lst = [1, 2, 3]
        chunks = MockHelpers.chunk_list(lst, 5)
        
        assert chunks == [[1, 2, 3]]
    
    def test_chunk_list_invalid_size(self):
        """Test chunking list with invalid chunk size"""
        lst = [1, 2, 3]
        
        with pytest.raises(ValueError, match="Chunk size must be positive"):
            MockHelpers.chunk_list(lst, 0)
    
    def test_remove_duplicates_simple(self):
        """Test removing duplicates from simple list"""
        lst = [1, 2, 2, 3, 1, 4]
        result = MockHelpers.remove_duplicates(lst)
        
        assert result == [1, 2, 3, 4]
    
    def test_remove_duplicates_with_key(self):
        """Test removing duplicates with key function"""
        lst = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"},
            {"id": 1, "name": "John Doe"}
        ]
        result = MockHelpers.remove_duplicates(lst, key=lambda x: x["id"])
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2


class TestStringOperations:
    """Test string manipulation functions"""
    
    def test_sanitize_filename_safe(self):
        """Test sanitizing safe filename"""
        filename = "document.txt"
        result = MockHelpers.sanitize_filename(filename)
        
        assert result == "document.txt"
    
    def test_sanitize_filename_unsafe_chars(self):
        """Test sanitizing filename with unsafe characters"""
        filename = "file<>:\"/\\|?*.txt"
        result = MockHelpers.sanitize_filename(filename)
        
        assert result == "file_________.txt"
        assert all(c not in result for c in '<>:"/\\|?*')
    
    def test_sanitize_filename_long(self):
        """Test sanitizing very long filename"""
        long_filename = "a" * 300 + ".txt"
        result = MockHelpers.sanitize_filename(long_filename)
        
        assert len(result) <= 255
        assert result.endswith(".txt")
    
    def test_sanitize_filename_empty(self):
        """Test sanitizing empty filename"""
        result = MockHelpers.sanitize_filename("")
        
        assert result == "unnamed"
    
    def test_generate_random_string_default(self):
        """Test generating random string with default settings"""
        result = MockHelpers.generate_random_string()
        
        assert len(result) == 10
        assert all(c.isalnum() for c in result)
    
    def test_generate_random_string_with_special(self):
        """Test generating random string with special characters"""
        result = MockHelpers.generate_random_string(length=8, include_special=True)
        
        assert len(result) == 8


class TestValidationFunctions:
    """Test validation functions"""
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@sub.domain.org"
        ]
        
        for email in valid_emails:
            assert MockHelpers.validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user space@domain.com"
        ]
        
        for email in invalid_emails:
            assert MockHelpers.validate_email(email) is False
    
    def test_validate_password_strong(self):
        """Test password validation with strong password"""
        strong_password = "SecurePass123!"
        is_valid, errors = MockHelpers.validate_password(strong_password)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_password_weak(self):
        """Test password validation with weak password"""
        weak_password = "weak"
        is_valid, errors = MockHelpers.validate_password(weak_password)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("at least 8 characters" in error for error in errors)
    
    def test_validate_password_no_digits(self):
        """Test password validation without digits"""
        password = "NoDigitsHere!"
        is_valid, errors = MockHelpers.validate_password(password)
        
        assert is_valid is False
        assert any("contain at least one digit" in error for error in errors)


class TestFormatting:
    """Test formatting functions"""
    
    def test_format_bytes_zero(self):
        """Test formatting zero bytes"""
        result = MockHelpers.format_bytes(0)
        assert result == "0 B"
    
    def test_format_bytes_kilobytes(self):
        """Test formatting kilobytes"""
        result = MockHelpers.format_bytes(1536)  # 1.5 KB
        assert result == "1.50 KB"
    
    def test_format_bytes_megabytes(self):
        """Test formatting megabytes"""
        result = MockHelpers.format_bytes(1048576 * 2.5)  # 2.5 MB
        assert result == "2.50 MB"
    
    def test_humanize_duration_seconds(self):
        """Test humanizing duration in seconds"""
        result = MockHelpers.humanize_duration(45.7)
        assert result == "45.7s"
    
    def test_humanize_duration_minutes(self):
        """Test humanizing duration in minutes"""
        result = MockHelpers.humanize_duration(150)  # 2.5 minutes
        assert result == "2.5m"
    
    def test_humanize_duration_hours(self):
        """Test humanizing duration in hours"""
        result = MockHelpers.humanize_duration(7200)  # 2 hours
        assert result == "2.0h"
    
    def test_humanize_duration_days(self):
        """Test humanizing duration in days"""
        result = MockHelpers.humanize_duration(172800)  # 2 days
        assert result == "2.0d"
    
    def test_parse_duration_simple(self):
        """Test parsing simple duration strings"""
        assert MockHelpers.parse_duration("30s") == 30
        assert MockHelpers.parse_duration("5m") == 300
        assert MockHelpers.parse_duration("2h") == 7200
        assert MockHelpers.parse_duration("1d") == 86400
    
    def test_parse_duration_complex(self):
        """Test parsing complex duration strings"""
        result = MockHelpers.parse_duration("1d2h30m45s")
        expected = 86400 + 7200 + 1800 + 45  # 1 day + 2 hours + 30 minutes + 45 seconds
        assert result == expected
    
    def test_parse_duration_invalid(self):
        """Test parsing invalid duration string"""
        with pytest.raises(ValueError, match="Invalid duration format"):
            MockHelpers.parse_duration("invalid")


class TestUtilityDecorators:
    """Test utility decorators and advanced functions"""
    
    def test_memoize_decorator(self):
        """Test memoization decorator"""
        call_count = 0
        
        @MockHelpers.memoize
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * x
        
        # First call
        result1 = expensive_function(5)
        assert result1 == 25
        assert call_count == 1
        
        # Second call with same argument (should use cache)
        result2 = expensive_function(5)
        assert result2 == 25
        assert call_count == 1  # Should not increment
        
        # Call with different argument
        result3 = expensive_function(3)
        assert result3 == 9
        assert call_count == 2
    
    def test_retry_operation_success(self):
        """Test retry operation that succeeds"""
        call_count = 0
        
        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = MockHelpers.retry_operation(operation, max_retries=3, delay=0.01)
        assert result == "success"
        assert call_count == 3
    
    def test_retry_operation_max_retries_exceeded(self):
        """Test retry operation that exceeds max retries"""
        def failing_operation():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            MockHelpers.retry_operation(failing_operation, max_retries=2, delay=0.01)
    
    def test_batch_process_simple(self):
        """Test batch processing with simple function"""
        items = list(range(10))
        
        def processor(batch):
            return [x * 2 for x in batch]
        
        result = MockHelpers.batch_process(items, batch_size=3, processor_func=processor)
        expected = [x * 2 for x in range(10)]
        
        assert result == expected
    
    def test_batch_process_aggregation(self):
        """Test batch processing with aggregation"""
        items = [1, 2, 3, 4, 5, 6]
        
        def sum_processor(batch):
            return sum(batch)
        
        result = MockHelpers.batch_process(items, batch_size=2, processor_func=sum_processor)
        
        assert result == [3, 7, 11]  # [1+2, 3+4, 5+6]


class TestFileOperations:
    """Test file-related utility functions"""
    
    def test_get_file_extension(self):
        """Test getting file extension"""
        assert MockHelpers.get_file_extension("document.txt") == ".txt"
        assert MockHelpers.get_file_extension("image.PNG") == ".png"
        assert MockHelpers.get_file_extension("file.tar.gz") == ".gz"
        assert MockHelpers.get_file_extension("no_extension") == ""
    
    def test_ensure_directory_exists(self):
        """Test ensuring directory exists"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = os.path.join(tmp_dir, "test", "nested", "dir")
            
            # Directory doesn't exist initially
            assert not os.path.exists(test_dir)
            
            # Create directory
            result = MockHelpers.ensure_directory_exists(test_dir)
            
            assert result is True
            assert os.path.exists(test_dir)
            assert os.path.isdir(test_dir)
    
    def test_ensure_directory_exists_already_exists(self):
        """Test ensuring directory exists when it already exists"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = MockHelpers.ensure_directory_exists(tmp_dir)
            
            assert result is True
            assert os.path.exists(tmp_dir)


class TestHelperIntegration:
    """Test integration of multiple helper functions"""
    
    def test_data_processing_workflow(self):
        """Test complete data processing workflow using multiple helpers"""
        # Sample data
        raw_data = [
            {"user": {"name": "John", "email": "JOHN@EXAMPLE.COM"}, "score": 85},
            {"user": {"name": "Jane", "email": "jane@example.com"}, "score": 92},
            {"user": {"name": "John", "email": "john@example.com"}, "score": 88},  # Duplicate
        ]
        
        # Process data in batches
        def process_batch(batch):
            processed = []
            for item in batch:
                # Flatten the nested structure
                flat_item = MockHelpers.flatten_dict(item)
                # Normalize email
                flat_item['user.email'] = flat_item['user.email'].lower()
                processed.append(flat_item)
            return processed
        
        processed_data = MockHelpers.batch_process(raw_data, 2, process_batch)
        
        # Remove duplicates based on email
        unique_data = MockHelpers.remove_duplicates(
            processed_data, 
            key=lambda x: x['user.email']
        )
        
        assert len(unique_data) == 2  # Should have 2 unique users
        assert all('user.name' in item for item in unique_data)
        assert all(item['user.email'].islower() for item in unique_data)
    
    def test_secure_data_handling(self):
        """Test secure data handling workflow"""
        # Generate secure identifiers
        user_id = MockHelpers.generate_unique_id("user", 8)
        session_id = MockHelpers.generate_unique_id("session", 12)
        
        # Hash sensitive data
        password = "SecurePassword123!"
        password_hash = MockHelpers.hash_string(password)
        
        # Create user data structure
        user_data = {
            "id": user_id,
            "session_id": session_id,
            "password_hash": password_hash,
            "metadata": {
                "created_at": datetime.now(),
                "last_login": None
            }
        }
        
        # Serialize safely
        serialized = MockHelpers.safe_json_dumps(user_data)
        assert serialized is not None
        
        # Deserialize safely
        deserialized = MockHelpers.safe_json_loads(serialized)
        assert deserialized is not None
        
        # Verify password hash
        assert MockHelpers.verify_hash(password, password_hash)
        assert user_id.startswith("user_")
        assert session_id.startswith("session_")
    
    def test_configuration_management(self):
        """Test configuration management using helpers"""
        # Base configuration
        base_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "app_db"
            },
            "security": {
                "session_timeout": "1h",
                "max_attempts": 3
            }
        }
        
        # Environment-specific overrides
        env_config = {
            "database": {
                "host": "prod-db.example.com",
                "ssl": True
            },
            "security": {
                "session_timeout": "30m"
            }
        }
        
        # Merge configurations
        final_config = MockHelpers.deep_merge_dicts(base_config, env_config)
        
        # Parse duration
        timeout_seconds = MockHelpers.parse_duration(final_config["security"]["session_timeout"])
        
        # Flatten for easy access
        flat_config = MockHelpers.flatten_dict(final_config)
        
        assert final_config["database"]["host"] == "prod-db.example.com"
        assert final_config["database"]["port"] == 5432  # Preserved from base
        assert final_config["database"]["ssl"] is True  # Added from env
        assert timeout_seconds == 1800  # 30 minutes
        assert flat_config["database.host"] == "prod-db.example.com"