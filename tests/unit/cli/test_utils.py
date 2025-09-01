# tests/unit/cli/test_utils.py
"""
Test module for CLI utility functions.
Tests formatting, file handling, configuration management, and helper functions.
"""

import pytest
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, mock_open
from pathlib import Path


class MockCLIUtils:
    """Mock CLI utilities for testing"""
    
    @staticmethod
    def format_table(data, headers=None, max_width=80):
        """Format data as a table"""
        if not data:
            return "No data to display"
        
        if headers is None:
            headers = list(data[0].keys()) if isinstance(data[0], dict) else []
        
        # Calculate column widths
        if isinstance(data[0], dict):
            col_widths = {h: len(str(h)) for h in headers}
            for row in data:
                for header in headers:
                    col_widths[header] = max(col_widths[header], len(str(row.get(header, ''))))
        else:
            col_widths = [max(len(str(headers[i])), max(len(str(row[i])) for row in data)) 
                         for i in range(len(headers))]
        
        # Build table
        lines = []
        if isinstance(data[0], dict):
            # Header
            header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
            lines.append(header_line)
            lines.append("-" * len(header_line))
            
            # Data rows
            for row in data:
                data_line = " | ".join(str(row.get(h, '')).ljust(col_widths[h]) for h in headers)
                lines.append(data_line)
        else:
            # Simple list format
            header_line = " | ".join(str(headers[i]).ljust(col_widths[i]) for i in range(len(headers)))
            lines.append(header_line)
            lines.append("-" * len(header_line))
            
            for row in data:
                data_line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
                lines.append(data_line)
        
        return "\n".join(lines)
    
    @staticmethod
    def format_progress_bar(current, total, width=50, char='█'):
        """Format a progress bar"""
        if total <= 0:
            return f"[{'?' * width}] ?%"
        
        percentage = min(current / total, 1.0)
        filled_width = int(width * percentage)
        bar = char * filled_width + '-' * (width - filled_width)
        
        return f"[{bar}] {percentage * 100:.1f}%"
    
    @staticmethod
    def format_duration(seconds):
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    @staticmethod
    def colorize_text(text, color):
        """Add color codes to text"""
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'reset': '\033[0m'
        }
        
        if color not in colors:
            return text
        
        return f"{colors[color]}{text}{colors['reset']}"
    
    @staticmethod
    def truncate_text(text, max_length, suffix='...'):
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def validate_file_path(file_path, must_exist=True, must_be_file=True):
        """Validate file path"""
        path = Path(file_path)
        
        if must_exist and not path.exists():
            return False, f"Path does not exist: {file_path}"
        
        if must_be_file and path.exists() and not path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        return True, "Valid path"
    
    @staticmethod
    def create_config_dir(config_path):
        """Create configuration directory"""
        path = Path(config_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True, f"Config directory created: {config_path}"
        except Exception as e:
            return False, f"Failed to create config directory: {str(e)}"
    
    @staticmethod
    def load_config(config_file):
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return True, config
        except FileNotFoundError:
            return False, "Configuration file not found"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in config file: {str(e)}"
        except Exception as e:
            return False, f"Error loading config: {str(e)}"
    
    @staticmethod
    def save_config(config_file, config_data):
        """Save configuration to file"""
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True, "Configuration saved successfully"
        except Exception as e:
            return False, f"Error saving config: {str(e)}"
    
    @staticmethod
    def get_user_input(prompt, input_type='string', default=None, choices=None):
        """Get user input with validation"""
        while True:
            if default:
                display_prompt = f"{prompt} [{default}]: "
            else:
                display_prompt = f"{prompt}: "
            
            if choices:
                display_prompt = f"{prompt} ({'/'.join(choices)}): "
            
            user_input = input(display_prompt).strip()
            
            if not user_input and default:
                return default
            
            if choices and user_input not in choices:
                print(f"Invalid choice. Please select from: {', '.join(choices)}")
                continue
            
            if input_type == 'int':
                try:
                    return int(user_input)
                except ValueError:
                    print("Please enter a valid integer.")
                    continue
            elif input_type == 'float':
                try:
                    return float(user_input)
                except ValueError:
                    print("Please enter a valid number.")
                    continue
            
            return user_input
    
    @staticmethod
    def parse_time_string(time_str):
        """Parse time string to datetime"""
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%H:%M:%S',
            '%H:%M'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse time string: {time_str}")


class TestFormatting:
    """Test formatting utility functions"""
    
    def test_format_table_with_dict_data(self):
        """Test table formatting with dictionary data"""
        data = [
            {'name': 'John', 'age': 25, 'score': 95.5},
            {'name': 'Jane', 'age': 30, 'score': 87.2},
            {'name': 'Bob', 'age': 22, 'score': 92.1}
        ]
        
        result = MockCLIUtils.format_table(data)
        
        assert 'name' in result
        assert 'age' in result
        assert 'score' in result
        assert 'John' in result
        assert '95.5' in result
        assert '|' in result  # Table delimiter
        assert '-' in result  # Header separator
    
    def test_format_table_with_list_data(self):
        """Test table formatting with list data"""
        headers = ['Name', 'Score', 'Grade']
        data = [
            ['Alice', 95, 'A'],
            ['Bob', 87, 'B'],
            ['Carol', 92, 'A-']
        ]
        
        result = MockCLIUtils.format_table(data, headers)
        
        assert 'Name' in result
        assert 'Score' in result
        assert 'Alice' in result
        assert '95' in result
        assert '|' in result
    
    def test_format_table_empty_data(self):
        """Test table formatting with empty data"""
        result = MockCLIUtils.format_table([])
        assert result == "No data to display"
    
    def test_format_progress_bar(self):
        """Test progress bar formatting"""
        # 50% progress
        result = MockCLIUtils.format_progress_bar(50, 100)
        assert '[' in result
        assert ']' in result
        assert '50.0%' in result
        assert '█' in result
        assert '-' in result
    
    def test_format_progress_bar_complete(self):
        """Test progress bar at 100%"""
        result = MockCLIUtils.format_progress_bar(100, 100)
        assert '100.0%' in result
        assert '█' in result
        assert '-' not in result
    
    def test_format_progress_bar_zero_total(self):
        """Test progress bar with zero total"""
        result = MockCLIUtils.format_progress_bar(10, 0)
        assert '?' in result
        assert '?%' in result
    
    def test_format_duration_seconds(self):
        """Test duration formatting for seconds"""
        result = MockCLIUtils.format_duration(45.7)
        assert result == "45.7s"
    
    def test_format_duration_minutes(self):
        """Test duration formatting for minutes"""
        result = MockCLIUtils.format_duration(150)  # 2.5 minutes
        assert result == "2.5m"
    
    def test_format_duration_hours(self):
        """Test duration formatting for hours"""
        result = MockCLIUtils.format_duration(7200)  # 2 hours
        assert result == "2.0h"
    
    def test_format_file_size_bytes(self):
        """Test file size formatting for bytes"""
        result = MockCLIUtils.format_file_size(512)
        assert result == "512.0B"
    
    def test_format_file_size_kb(self):
        """Test file size formatting for kilobytes"""
        result = MockCLIUtils.format_file_size(2048)
        assert result == "2.0KB"
    
    def test_format_file_size_mb(self):
        """Test file size formatting for megabytes"""
        result = MockCLIUtils.format_file_size(1048576)  # 1 MB
        assert result == "1.0MB"
    
    def test_format_file_size_zero(self):
        """Test file size formatting for zero bytes"""
        result = MockCLIUtils.format_file_size(0)
        assert result == "0B"
    
    def test_colorize_text(self):
        """Test text colorization"""
        result = MockCLIUtils.colorize_text("Hello", "red")
        assert '\033[91m' in result  # Red color code
        assert '\033[0m' in result   # Reset code
        assert 'Hello' in result
    
    def test_colorize_text_invalid_color(self):
        """Test text colorization with invalid color"""
        result = MockCLIUtils.colorize_text("Hello", "invalid")
        assert result == "Hello"  # Should return original text
    
    def test_truncate_text_short(self):
        """Test text truncation for short text"""
        result = MockCLIUtils.truncate_text("Short", 10)
        assert result == "Short"
    
    def test_truncate_text_long(self):
        """Test text truncation for long text"""
        result = MockCLIUtils.truncate_text("This is a very long text", 10)
        assert len(result) == 10
        assert result.endswith("...")
        assert result == "This is..."
    
    def test_truncate_text_custom_suffix(self):
        """Test text truncation with custom suffix"""
        result = MockCLIUtils.truncate_text("Long text here", 10, suffix=">>")
        assert result.endswith(">>")
        assert len(result) == 10


class TestFileOperations:
    """Test file operation utilities"""
    
    def test_validate_file_path_exists(self):
        """Test file path validation for existing file"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name
        
        try:
            valid, message = MockCLIUtils.validate_file_path(tmp_path)
            assert valid is True
            assert "Valid path" in message
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_path_not_exists(self):
        """Test file path validation for non-existing file"""
        valid, message = MockCLIUtils.validate_file_path("/non/existent/file.txt")
        assert valid is False
        assert "does not exist" in message
    
    def test_validate_file_path_directory(self):
        """Test file path validation for directory"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            valid, message = MockCLIUtils.validate_file_path(tmp_dir, must_be_file=True)
            assert valid is False
            assert "not a file" in message
    
    def test_create_config_dir(self):
        """Test configuration directory creation"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = os.path.join(tmp_dir, "config", "subdir")
            
            success, message = MockCLIUtils.create_config_dir(config_path)
            assert success is True
            assert os.path.exists(config_path)
            assert "created" in message
    
    def test_load_config_valid_file(self):
        """Test loading valid configuration file"""
        config_data = {"theme": "dark", "auto_save": True, "timeout": 30}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(config_data, tmp)
            tmp_path = tmp.name
        
        try:
            success, loaded_config = MockCLIUtils.load_config(tmp_path)
            assert success is True
            assert loaded_config == config_data
        finally:
            os.unlink(tmp_path)
    
    def test_load_config_missing_file(self):
        """Test loading missing configuration file"""
        success, message = MockCLIUtils.load_config("/non/existent/config.json")
        assert success is False
        assert "not found" in message
    
    def test_load_config_invalid_json(self):
        """Test loading invalid JSON configuration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write("{ invalid json }")
            tmp_path = tmp.name
        
        try:
            success, message = MockCLIUtils.load_config(tmp_path)
            assert success is False
            assert "Invalid JSON" in message
        finally:
            os.unlink(tmp_path)
    
    def test_save_config(self):
        """Test saving configuration file"""
        config_data = {"setting1": "value1", "setting2": 42}
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success, message = MockCLIUtils.save_config(tmp_path, config_data)
            assert success is True
            assert "saved successfully" in message
            
            # Verify file contents
            with open(tmp_path, 'r') as f:
                saved_data = json.load(f)
            assert saved_data == config_data
        finally:
            os.unlink(tmp_path)


class TestUserInput:
    """Test user input utilities"""
    
    @patch('builtins.input')
    def test_get_user_input_string(self, mock_input):
        """Test getting string input from user"""
        mock_input.return_value = "test_input"
        
        result = MockCLIUtils.get_user_input("Enter text")
        assert result == "test_input"
        mock_input.assert_called_once_with("Enter text: ")
    
    @patch('builtins.input')
    def test_get_user_input_with_default(self, mock_input):
        """Test getting input with default value"""
        mock_input.return_value = ""  # Empty input
        
        result = MockCLIUtils.get_user_input("Enter text", default="default_value")
        assert result == "default_value"
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_integer(self, mock_print, mock_input):
        """Test getting integer input"""
        mock_input.side_effect = ["not_a_number", "42"]
        
        result = MockCLIUtils.get_user_input("Enter number", input_type='int')
        assert result == 42
        assert mock_input.call_count == 2
        mock_print.assert_called_with("Please enter a valid integer.")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_float(self, mock_print, mock_input):
        """Test getting float input"""
        mock_input.side_effect = ["invalid", "3.14"]
        
        result = MockCLIUtils.get_user_input("Enter number", input_type='float')
        assert result == 3.14
        assert mock_input.call_count == 2
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_choices(self, mock_print, mock_input):
        """Test getting input with choices"""
        mock_input.side_effect = ["invalid_choice", "option2"]
        choices = ["option1", "option2", "option3"]
        
        result = MockCLIUtils.get_user_input("Choose option", choices=choices)
        assert result == "option2"
        assert mock_input.call_count == 2
        mock_print.assert_called_with("Invalid choice. Please select from: option1, option2, option3")


class TestTimeUtils:
    """Test time parsing utilities"""
    
    def test_parse_time_string_full_datetime(self):
        """Test parsing full datetime string"""
        time_str = "2024-01-15 14:30:45"
        result = MockCLIUtils.parse_time_string(time_str)
        
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 45
    
    def test_parse_time_string_date_only(self):
        """Test parsing date-only string"""
        time_str = "2024-01-15"
        result = MockCLIUtils.parse_time_string(time_str)
        
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
    
    def test_parse_time_string_time_only(self):
        """Test parsing time-only string"""
        time_str = "14:30:45"
        result = MockCLIUtils.parse_time_string(time_str)
        
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 45
    
    def test_parse_time_string_invalid(self):
        """Test parsing invalid time string"""
        with pytest.raises(ValueError, match="Unable to parse time string"):
            MockCLIUtils.parse_time_string("invalid_time")


class TestUtilsIntegration:
    """Test integration of multiple utility functions"""
    
    def test_complete_config_workflow(self):
        """Test complete configuration workflow"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = os.path.join(tmp_dir, "config")
            config_file = os.path.join(config_dir, "settings.json")
            
            # Create config directory
            success, _ = MockCLIUtils.create_config_dir(config_dir)
            assert success is True
            
            # Save initial config
            initial_config = {"theme": "dark", "timeout": 30}
            success, _ = MockCLIUtils.save_config(config_file, initial_config)
            assert success is True
            
            # Load and verify config
            success, loaded_config = MockCLIUtils.load_config(config_file)
            assert success is True
            assert loaded_config == initial_config
            
            # Update config
            updated_config = {**loaded_config, "theme": "light", "new_setting": True}
            success, _ = MockCLIUtils.save_config(config_file, updated_config)
            assert success is True
            
            # Verify updated config
            success, final_config = MockCLIUtils.load_config(config_file)
            assert success is True
            assert final_config["theme"] == "light"
            assert final_config["new_setting"] is True
    
    def test_file_validation_workflow(self):
        """Test file validation workflow"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test non-existent file
            file_path = os.path.join(tmp_dir, "test.txt")
            valid, _ = MockCLIUtils.validate_file_path(file_path)
            assert valid is False
            
            # Create file
            with open(file_path, 'w') as f:
                f.write("test content")
            
            # Test existing file
            valid, _ = MockCLIUtils.validate_file_path(file_path)
            assert valid is True
            
            # Test directory validation
            valid, _ = MockCLIUtils.validate_file_path(tmp_dir, must_be_file=True)
            assert valid is False
    
    def test_formatting_integration(self):
        """Test formatting functions integration"""
        # Create sample data
        data = [
            {"name": "Task 1", "progress": 75, "duration": 3600},
            {"name": "Task 2", "progress": 50, "duration": 1800},
            {"name": "Task 3", "progress": 100, "duration": 7200}
        ]
        
        # Format table
        table = MockCLIUtils.format_table(data)
        assert "Task 1" in table
        assert "75" in table
        
        # Format progress bars for each task
        for task in data:
            progress_bar = MockCLIUtils.format_progress_bar(task["progress"], 100)
            assert f"{task['progress']}.0%" in progress_bar
            
            duration_str = MockCLIUtils.format_duration(task["duration"])
            if task["duration"] >= 3600:
                assert "h" in duration_str
            else:
                assert "m" in duration_str or "s" in duration_str