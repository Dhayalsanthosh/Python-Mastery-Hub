# tests/unit/cli/test_interactive.py
"""
Test module for CLI interactive functionality.
Tests interactive prompts, user input handling, and session management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO
import sys


class MockInteractiveCLI:
    """Mock interactive CLI for testing"""
    
    def __init__(self):
        self.session_active = False
        self.current_user = None
        self.current_topic = None
        self.history = []
        self.prompt_stack = []
    
    def start_interactive_session(self):
        """Start an interactive session"""
        self.session_active = True
        return "Interactive session started. Type 'help' for commands."
    
    def stop_interactive_session(self):
        """Stop the interactive session"""
        self.session_active = False
        self.current_user = None
        self.current_topic = None
        return "Interactive session ended."
    
    def process_input(self, user_input):
        """Process user input in interactive mode"""
        if not self.session_active:
            return "No active session. Use 'start' to begin."
        
        self.history.append(user_input)
        command = user_input.strip().lower()
        
        if command == 'help':
            return self.show_help()
        elif command == 'quit' or command == 'exit':
            return self.stop_interactive_session()
        elif command.startswith('login '):
            username = command.split(' ', 1)[1] if len(command.split(' ')) > 1 else None
            return self.login_user(username)
        elif command.startswith('topic '):
            topic = command.split(' ', 1)[1] if len(command.split(' ')) > 1 else None
            return self.set_topic(topic)
        elif command == 'status':
            return self.get_status()
        elif command == 'history':
            return self.get_history()
        elif command.startswith('exercise '):
            exercise_id = command.split(' ', 1)[1] if len(command.split(' ')) > 1 else None
            return self.start_exercise(exercise_id)
        else:
            return f"Unknown command: {command}. Type 'help' for available commands."
    
    def show_help(self):
        """Show available commands"""
        return """Available commands:
        help - Show this help message
        login <username> - Login as user
        topic <topic_name> - Set learning topic
        exercise <id> - Start exercise
        status - Show current status
        history - Show command history
        quit/exit - Exit interactive session"""
    
    def login_user(self, username):
        """Login user"""
        if not username:
            return "Error: Username required"
        self.current_user = username
        return f"Logged in as {username}"
    
    def set_topic(self, topic):
        """Set learning topic"""
        if not topic:
            return "Error: Topic name required"
        if not self.current_user:
            return "Error: Please login first"
        
        valid_topics = ['basics', 'oop', 'advanced', 'data_structures', 'algorithms']
        if topic not in valid_topics:
            return f"Error: Invalid topic. Valid topics: {', '.join(valid_topics)}"
        
        self.current_topic = topic
        return f"Topic set to: {topic}"
    
    def get_status(self):
        """Get current session status"""
        status = {
            'session_active': self.session_active,
            'user': self.current_user,
            'topic': self.current_topic,
            'commands_executed': len(self.history)
        }
        return f"Status: {status}"
    
    def get_history(self):
        """Get command history"""
        if not self.history:
            return "No command history"
        return f"Command history: {self.history}"
    
    def start_exercise(self, exercise_id):
        """Start an exercise"""
        if not self.current_user:
            return "Error: Please login first"
        if not self.current_topic:
            return "Error: Please set a topic first"
        if not exercise_id:
            return "Error: Exercise ID required"
        
        return f"Starting exercise {exercise_id} for topic {self.current_topic}"
    
    def prompt_user(self, message, input_type='string', validation=None):
        """Prompt user for input with validation"""
        self.prompt_stack.append({
            'message': message,
            'type': input_type,
            'validation': validation
        })
        return f"PROMPT: {message}"
    
    def validate_input(self, value, input_type, validation=None):
        """Validate user input"""
        if input_type == 'int':
            try:
                int_val = int(value)
                if validation and 'min' in validation and int_val < validation['min']:
                    return False, f"Value must be at least {validation['min']}"
                if validation and 'max' in validation and int_val > validation['max']:
                    return False, f"Value must be at most {validation['max']}"
                return True, int_val
            except ValueError:
                return False, "Invalid integer value"
        
        elif input_type == 'choice':
            if validation and 'choices' in validation:
                if value not in validation['choices']:
                    return False, f"Invalid choice. Options: {', '.join(validation['choices'])}"
            return True, value
        
        elif input_type == 'string':
            if validation and 'min_length' in validation and len(value) < validation['min_length']:
                return False, f"Minimum length: {validation['min_length']}"
            return True, value
        
        return True, value


class TestInteractiveCLI:
    """Test interactive CLI functionality"""
    
    @pytest.fixture
    def interactive_cli(self):
        """Create interactive CLI instance"""
        return MockInteractiveCLI()
    
    def test_start_interactive_session(self, interactive_cli):
        """Test starting interactive session"""
        result = interactive_cli.start_interactive_session()
        
        assert interactive_cli.session_active is True
        assert "Interactive session started" in result
    
    def test_stop_interactive_session(self, interactive_cli):
        """Test stopping interactive session"""
        interactive_cli.start_interactive_session()
        result = interactive_cli.stop_interactive_session()
        
        assert interactive_cli.session_active is False
        assert interactive_cli.current_user is None
        assert interactive_cli.current_topic is None
        assert "Interactive session ended" in result
    
    def test_help_command(self, interactive_cli):
        """Test help command"""
        interactive_cli.start_interactive_session()
        result = interactive_cli.process_input('help')
        
        assert "Available commands" in result
        assert "login" in result
        assert "topic" in result
        assert "quit" in result
    
    def test_login_command(self, interactive_cli):
        """Test login command"""
        interactive_cli.start_interactive_session()
        result = interactive_cli.process_input('login john_doe')
        
        assert interactive_cli.current_user == 'john_doe'
        assert "Logged in as john_doe" in result
    
    def test_login_without_username(self, interactive_cli):
        """Test login command without username"""
        interactive_cli.start_interactive_session()
        result = interactive_cli.process_input('login')
        
        assert interactive_cli.current_user is None
        assert "Error: Username required" in result
    
    def test_topic_command(self, interactive_cli):
        """Test topic command"""
        interactive_cli.start_interactive_session()
        interactive_cli.process_input('login test_user')
        result = interactive_cli.process_input('topic oop')
        
        assert interactive_cli.current_topic == 'oop'
        assert "Topic set to: oop" in result
    
    def test_topic_without_login(self, interactive_cli):
        """Test topic command without login"""
        interactive_cli.start_interactive_session()
        result = interactive_cli.process_input('topic oop')
        
        assert "Error: Please login first" in result
    
    def test_invalid_topic(self, interactive_cli):
        """Test setting invalid topic"""
        interactive_cli.start_interactive_session()
        interactive_cli.process_input('login test_user')
        result = interactive_cli.process_input('topic invalid_topic')
        
        assert "Error: Invalid topic" in result
        assert interactive_cli.current_topic is None
    
    def test_status_command(self, interactive_cli):
        """Test status command"""
        interactive_cli.start_interactive_session()
        interactive_cli.process_input('login test_user')
        interactive_cli.process_input('topic basics')
        result = interactive_cli.process_input('status')
        
        assert "session_active" in result
        assert "test_user" in result
        assert "basics" in result
    
    def test_history_command(self, interactive_cli):
        """Test history command"""
        interactive_cli.start_interactive_session()
        interactive_cli.process_input('login test_user')
        interactive_cli.process_input('topic basics')
        result = interactive_cli.process_input('history')
        
        assert "login test_user" in result
        assert "topic basics" in result
    
    def test_exercise_command(self, interactive_cli):
        """Test exercise command"""
        interactive_cli.start_interactive_session()
        interactive_cli.process_input('login test_user')
        interactive_cli.process_input('topic basics')
        result = interactive_cli.process_input('exercise 1')
        
        assert "Starting exercise 1 for topic basics" in result
    
    def test_exercise_without_login(self, interactive_cli):
        """Test exercise command without login"""
        interactive_cli.start_interactive_session()
        result = interactive_cli.process_input('exercise 1')
        
        assert "Error: Please login first" in result
    
    def test_exercise_without_topic(self, interactive_cli):
        """Test exercise command without topic"""
        interactive_cli.start_interactive_session()
        interactive_cli.process_input('login test_user')
        result = interactive_cli.process_input('exercise 1')
        
        assert "Error: Please set a topic first" in result
    
    def test_exercise_without_id(self, interactive_cli):
        """Test exercise command without ID"""
        interactive_cli.start_interactive_session()
        interactive_cli.process_input('login test_user')
        interactive_cli.process_input('topic basics')
        result = interactive_cli.process_input('exercise')
        
        assert "Error: Exercise ID required" in result
    
    def test_unknown_command(self, interactive_cli):
        """Test unknown command handling"""
        interactive_cli.start_interactive_session()
        result = interactive_cli.process_input('unknown_command')
        
        assert "Unknown command" in result
        assert "help" in result
    
    def test_quit_command(self, interactive_cli):
        """Test quit command"""
        interactive_cli.start_interactive_session()
        result = interactive_cli.process_input('quit')
        
        assert interactive_cli.session_active is False
        assert "Interactive session ended" in result
    
    def test_exit_command(self, interactive_cli):
        """Test exit command"""
        interactive_cli.start_interactive_session()
        result = interactive_cli.process_input('exit')
        
        assert interactive_cli.session_active is False
        assert "Interactive session ended" in result
    
    def test_input_without_session(self, interactive_cli):
        """Test processing input without active session"""
        result = interactive_cli.process_input('help')
        
        assert "No active session" in result


class TestInputValidation:
    """Test input validation functionality"""
    
    @pytest.fixture
    def interactive_cli(self):
        return MockInteractiveCLI()
    
    def test_validate_integer_input(self, interactive_cli):
        """Test integer input validation"""
        # Valid integer
        valid, result = interactive_cli.validate_input('42', 'int')
        assert valid is True
        assert result == 42
        
        # Invalid integer
        valid, result = interactive_cli.validate_input('not_a_number', 'int')
        assert valid is False
        assert "Invalid integer" in result
    
    def test_validate_integer_with_range(self, interactive_cli):
        """Test integer validation with range constraints"""
        validation = {'min': 1, 'max': 10}
        
        # Valid range
        valid, result = interactive_cli.validate_input('5', 'int', validation)
        assert valid is True
        assert result == 5
        
        # Below minimum
        valid, result = interactive_cli.validate_input('0', 'int', validation)
        assert valid is False
        assert "at least 1" in result
        
        # Above maximum
        valid, result = interactive_cli.validate_input('15', 'int', validation)
        assert valid is False
        assert "at most 10" in result
    
    def test_validate_choice_input(self, interactive_cli):
        """Test choice input validation"""
        validation = {'choices': ['option1', 'option2', 'option3']}
        
        # Valid choice
        valid, result = interactive_cli.validate_input('option2', 'choice', validation)
        assert valid is True
        assert result == 'option2'
        
        # Invalid choice
        valid, result = interactive_cli.validate_input('invalid_option', 'choice', validation)
        assert valid is False
        assert "Invalid choice" in result
        assert "option1, option2, option3" in result
    
    def test_validate_string_input(self, interactive_cli):
        """Test string input validation"""
        validation = {'min_length': 3}
        
        # Valid string
        valid, result = interactive_cli.validate_input('hello', 'string', validation)
        assert valid is True
        assert result == 'hello'
        
        # String too short
        valid, result = interactive_cli.validate_input('hi', 'string', validation)
        assert valid is False
        assert "Minimum length: 3" in result
    
    def test_prompt_user(self, interactive_cli):
        """Test user prompting functionality"""
        result = interactive_cli.prompt_user("Enter your name:", 'string')
        
        assert len(interactive_cli.prompt_stack) == 1
        assert interactive_cli.prompt_stack[0]['message'] == "Enter your name:"
        assert interactive_cli.prompt_stack[0]['type'] == 'string'
        assert "PROMPT: Enter your name:" in result


class TestInteractiveWorkflow:
    """Test complete interactive workflows"""
    
    @pytest.fixture
    def interactive_cli(self):
        return MockInteractiveCLI()
    
    def test_complete_learning_workflow(self, interactive_cli):
        """Test a complete learning session workflow"""
        # Start session
        start_result = interactive_cli.start_interactive_session()
        assert "Interactive session started" in start_result
        
        # Login
        login_result = interactive_cli.process_input('login student123')
        assert "Logged in as student123" in login_result
        
        # Set topic
        topic_result = interactive_cli.process_input('topic oop')
        assert "Topic set to: oop" in topic_result
        
        # Check status
        status_result = interactive_cli.process_input('status')
        assert "student123" in status_result
        assert "oop" in status_result
        
        # Start exercise
        exercise_result = interactive_cli.process_input('exercise 5')
        assert "Starting exercise 5 for topic oop" in exercise_result
        
        # Check history
        history_result = interactive_cli.process_input('history')
        assert "login student123" in history_result
        assert "topic oop" in history_result
        assert "exercise 5" in history_result
        
        # Exit session
        exit_result = interactive_cli.process_input('quit')
        assert "Interactive session ended" in exit_result
        assert interactive_cli.session_active is False
    
    @patch('builtins.input')
    def test_simulated_user_interaction(self, mock_input, interactive_cli):
        """Test simulated user interaction"""
        # Simulate user inputs
        mock_input.side_effect = ['login testuser', 'topic basics', 'exercise 1', 'quit']
        
        interactive_cli.start_interactive_session()
        
        # Process each input
        inputs = ['login testuser', 'topic basics', 'exercise 1', 'quit']
        results = []
        
        for user_input in inputs:
            result = interactive_cli.process_input(user_input)
            results.append(result)
        
        # Verify results
        assert "Logged in as testuser" in results[0]
        assert "Topic set to: basics" in results[1]
        assert "Starting exercise 1" in results[2]
        assert "Interactive session ended" in results[3]
    
    def test_error_recovery_workflow(self, interactive_cli):
        """Test error recovery in interactive session"""
        interactive_cli.start_interactive_session()
        
        # Try invalid commands and recover
        result1 = interactive_cli.process_input('invalid_command')
        assert "Unknown command" in result1
        
        # Should still be able to use valid commands
        result2 = interactive_cli.process_input('help')
        assert "Available commands" in result2
        
        # Try exercise without login
        result3 = interactive_cli.process_input('exercise 1')
        assert "Error: Please login first" in result3
        
        # Login and try again
        result4 = interactive_cli.process_input('login testuser')
        assert "Logged in as testuser" in result4
        
        # Should still need topic
        result5 = interactive_cli.process_input('exercise 1')
        assert "Error: Please set a topic first" in result5
    
    def test_session_state_persistence(self, interactive_cli):
        """Test that session state persists across commands"""
        interactive_cli.start_interactive_session()
        
        # Set initial state
        interactive_cli.process_input('login persistent_user')
        interactive_cli.process_input('topic advanced')
        
        # Verify state persists
        assert interactive_cli.current_user == 'persistent_user'
        assert interactive_cli.current_topic == 'advanced'
        
        # Execute more commands
        interactive_cli.process_input('exercise 10')
        interactive_cli.process_input('status')
        
        # State should still be there
        assert interactive_cli.current_user == 'persistent_user'
        assert interactive_cli.current_topic == 'advanced'
        assert len(interactive_cli.history) == 4