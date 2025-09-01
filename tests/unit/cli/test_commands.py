# tests/unit/cli/test_commands.py
"""
Test module for CLI command functionality.
Tests command parsing, validation, and execution.
"""

import pytest
import sys
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
from argparse import ArgumentParser, Namespace


class MockCLICommands:
    """Mock CLI commands class for testing"""
    
    def __init__(self):
        self.parser = ArgumentParser(description='Python Learning Platform CLI')
        self.setup_commands()
    
    def setup_commands(self):
        """Setup CLI command structure"""
        subparsers = self.parser.add_subparsers(dest='command', help='Available commands')
        
        # Start command
        start_parser = subparsers.add_parser('start', help='Start learning session')
        start_parser.add_argument('--topic', choices=['basics', 'oop', 'advanced'], 
                                default='basics', help='Learning topic')
        start_parser.add_argument('--level', type=int, default=1, help='Difficulty level')
        
        # Exercise command
        exercise_parser = subparsers.add_parser('exercise', help='Manage exercises')
        exercise_parser.add_argument('action', choices=['list', 'run', 'submit'])
        exercise_parser.add_argument('--id', type=int, help='Exercise ID')
        exercise_parser.add_argument('--file', help='Solution file path')
        
        # Progress command
        progress_parser = subparsers.add_parser('progress', help='View progress')
        progress_parser.add_argument('--user', help='Username')
        progress_parser.add_argument('--detailed', action='store_true', help='Detailed view')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_parser.add_argument('action', choices=['get', 'set', 'list'])
        config_parser.add_argument('--key', help='Configuration key')
        config_parser.add_argument('--value', help='Configuration value')
    
    def parse_args(self, args=None):
        """Parse command line arguments"""
        return self.parser.parse_args(args)
    
    def execute_start(self, args):
        """Execute start command"""
        return {
            'command': 'start',
            'topic': args.topic,
            'level': args.level,
            'status': 'success'
        }
    
    def execute_exercise(self, args):
        """Execute exercise command"""
        if args.action == 'list':
            return {'exercises': ['ex1', 'ex2', 'ex3'], 'count': 3}
        elif args.action == 'run':
            if not args.id:
                raise ValueError("Exercise ID required for run action")
            return {'exercise_id': args.id, 'status': 'running'}
        elif args.action == 'submit':
            if not args.id or not args.file:
                raise ValueError("Exercise ID and file required for submit action")
            return {'exercise_id': args.id, 'file': args.file, 'status': 'submitted'}
    
    def execute_progress(self, args):
        """Execute progress command"""
        return {
            'user': args.user or 'current_user',
            'detailed': args.detailed,
            'progress': 75.5
        }
    
    def execute_config(self, args):
        """Execute config command"""
        if args.action == 'list':
            return {'configs': {'theme': 'dark', 'auto_save': True}}
        elif args.action == 'get':
            if not args.key:
                raise ValueError("Key required for get action")
            return {'key': args.key, 'value': 'mock_value'}
        elif args.action == 'set':
            if not args.key or not args.value:
                raise ValueError("Key and value required for set action")
            return {'key': args.key, 'value': args.value, 'status': 'updated'}


class TestCLICommands:
    """Test CLI command functionality"""
    
    @pytest.fixture
    def cli_commands(self):
        """Create CLI commands instance"""
        return MockCLICommands()
    
    def test_parser_creation(self, cli_commands):
        """Test that parser is created correctly"""
        assert cli_commands.parser is not None
        assert cli_commands.parser.description == 'Python Learning Platform CLI'
    
    def test_start_command_default_args(self, cli_commands):
        """Test start command with default arguments"""
        args = cli_commands.parse_args(['start'])
        assert args.command == 'start'
        assert args.topic == 'basics'
        assert args.level == 1
    
    def test_start_command_with_args(self, cli_commands):
        """Test start command with custom arguments"""
        args = cli_commands.parse_args(['start', '--topic', 'oop', '--level', '3'])
        assert args.command == 'start'
        assert args.topic == 'oop'
        assert args.level == 3
    
    def test_start_command_execution(self, cli_commands):
        """Test start command execution"""
        args = cli_commands.parse_args(['start', '--topic', 'advanced', '--level', '2'])
        result = cli_commands.execute_start(args)
        
        assert result['command'] == 'start'
        assert result['topic'] == 'advanced'
        assert result['level'] == 2
        assert result['status'] == 'success'
    
    def test_exercise_list_command(self, cli_commands):
        """Test exercise list command"""
        args = cli_commands.parse_args(['exercise', 'list'])
        result = cli_commands.execute_exercise(args)
        
        assert result['count'] == 3
        assert 'ex1' in result['exercises']
    
    def test_exercise_run_command(self, cli_commands):
        """Test exercise run command"""
        args = cli_commands.parse_args(['exercise', 'run', '--id', '123'])
        result = cli_commands.execute_exercise(args)
        
        assert result['exercise_id'] == 123
        assert result['status'] == 'running'
    
    def test_exercise_run_command_missing_id(self, cli_commands):
        """Test exercise run command without ID"""
        args = cli_commands.parse_args(['exercise', 'run'])
        
        with pytest.raises(ValueError, match="Exercise ID required"):
            cli_commands.execute_exercise(args)
    
    def test_exercise_submit_command(self, cli_commands):
        """Test exercise submit command"""
        args = cli_commands.parse_args(['exercise', 'submit', '--id', '456', '--file', 'solution.py'])
        result = cli_commands.execute_exercise(args)
        
        assert result['exercise_id'] == 456
        assert result['file'] == 'solution.py'
        assert result['status'] == 'submitted'
    
    def test_exercise_submit_command_missing_args(self, cli_commands):
        """Test exercise submit command with missing arguments"""
        args = cli_commands.parse_args(['exercise', 'submit', '--id', '456'])
        
        with pytest.raises(ValueError, match="Exercise ID and file required"):
            cli_commands.execute_exercise(args)
    
    def test_progress_command_default(self, cli_commands):
        """Test progress command with default settings"""
        args = cli_commands.parse_args(['progress'])
        result = cli_commands.execute_progress(args)
        
        assert result['user'] == 'current_user'
        assert result['detailed'] is False
        assert result['progress'] == 75.5
    
    def test_progress_command_with_user(self, cli_commands):
        """Test progress command with specific user"""
        args = cli_commands.parse_args(['progress', '--user', 'john_doe', '--detailed'])
        result = cli_commands.execute_progress(args)
        
        assert result['user'] == 'john_doe'
        assert result['detailed'] is True
    
    def test_config_list_command(self, cli_commands):
        """Test config list command"""
        args = cli_commands.parse_args(['config', 'list'])
        result = cli_commands.execute_config(args)
        
        assert 'configs' in result
        assert result['configs']['theme'] == 'dark'
        assert result['configs']['auto_save'] is True
    
    def test_config_get_command(self, cli_commands):
        """Test config get command"""
        args = cli_commands.parse_args(['config', 'get', '--key', 'theme'])
        result = cli_commands.execute_config(args)
        
        assert result['key'] == 'theme'
        assert result['value'] == 'mock_value'
    
    def test_config_get_command_missing_key(self, cli_commands):
        """Test config get command without key"""
        args = cli_commands.parse_args(['config', 'get'])
        
        with pytest.raises(ValueError, match="Key required"):
            cli_commands.execute_config(args)
    
    def test_config_set_command(self, cli_commands):
        """Test config set command"""
        args = cli_commands.parse_args(['config', 'set', '--key', 'theme', '--value', 'light'])
        result = cli_commands.execute_config(args)
        
        assert result['key'] == 'theme'
        assert result['value'] == 'light'
        assert result['status'] == 'updated'
    
    def test_config_set_command_missing_args(self, cli_commands):
        """Test config set command with missing arguments"""
        args = cli_commands.parse_args(['config', 'set', '--key', 'theme'])
        
        with pytest.raises(ValueError, match="Key and value required"):
            cli_commands.execute_config(args)
    
    def test_invalid_command(self, cli_commands):
        """Test handling of invalid commands"""
        with pytest.raises(SystemExit):
            cli_commands.parse_args(['invalid_command'])
    
    def test_help_command(self, cli_commands):
        """Test help command output"""
        with pytest.raises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli_commands.parse_args(['--help'])
                output = mock_stdout.getvalue()
                assert 'Python Learning Platform CLI' in output


class TestCLIIntegration:
    """Test CLI integration scenarios"""
    
    @pytest.fixture
    def cli_commands(self):
        return MockCLICommands()
    
    def test_full_learning_session_flow(self, cli_commands):
        """Test complete learning session workflow"""
        # Start session
        start_args = cli_commands.parse_args(['start', '--topic', 'oop', '--level', '2'])
        start_result = cli_commands.execute_start(start_args)
        assert start_result['status'] == 'success'
        
        # List exercises
        list_args = cli_commands.parse_args(['exercise', 'list'])
        list_result = cli_commands.execute_exercise(list_args)
        assert list_result['count'] > 0
        
        # Run exercise
        run_args = cli_commands.parse_args(['exercise', 'run', '--id', '1'])
        run_result = cli_commands.execute_exercise(run_args)
        assert run_result['status'] == 'running'
        
        # Submit solution
        submit_args = cli_commands.parse_args(['exercise', 'submit', '--id', '1', '--file', 'my_solution.py'])
        submit_result = cli_commands.execute_exercise(submit_args)
        assert submit_result['status'] == 'submitted'
        
        # Check progress
        progress_args = cli_commands.parse_args(['progress', '--detailed'])
        progress_result = cli_commands.execute_progress(progress_args)
        assert 'progress' in progress_result
    
    @patch('sys.argv')
    def test_command_line_simulation(self, mock_argv, cli_commands):
        """Test simulation of actual command line usage"""
        # Simulate: python cli.py start --topic advanced
        mock_argv.__getitem__.return_value = ['cli.py', 'start', '--topic', 'advanced']
        
        args = cli_commands.parse_args(['start', '--topic', 'advanced'])
        result = cli_commands.execute_start(args)
        
        assert result['topic'] == 'advanced'
        assert result['status'] == 'success'
    
    def test_error_handling_chain(self, cli_commands):
        """Test error handling across multiple commands"""
        # Test invalid exercise ID
        with pytest.raises(ValueError):
            args = cli_commands.parse_args(['exercise', 'run'])
            cli_commands.execute_exercise(args)
        
        # Test invalid config operation
        with pytest.raises(ValueError):
            args = cli_commands.parse_args(['config', 'set', '--key', 'theme'])
            cli_commands.execute_config(args)
    
    def test_command_output_formatting(self, cli_commands):
        """Test that command outputs are properly formatted"""
        # Test progress command output structure
        args = cli_commands.parse_args(['progress', '--user', 'testuser'])
        result = cli_commands.execute_progress(args)
        
        # Ensure result has expected structure
        assert isinstance(result, dict)
        assert 'user' in result
        assert 'progress' in result
        assert isinstance(result['progress'], (int, float))
    
    def test_configuration_persistence_simulation(self, cli_commands):
        """Test configuration management workflow"""
        # Set a configuration
        set_args = cli_commands.parse_args(['config', 'set', '--key', 'auto_save', '--value', 'false'])
        set_result = cli_commands.execute_config(set_args)
        assert set_result['status'] == 'updated'
        
        # Get the configuration
        get_args = cli_commands.parse_args(['config', 'get', '--key', 'auto_save'])
        get_result = cli_commands.execute_config(get_args)
        assert get_result['key'] == 'auto_save'
        
        # List all configurations
        list_args = cli_commands.parse_args(['config', 'list'])
        list_result = cli_commands.execute_config(list_args)
        assert 'configs' in list_result