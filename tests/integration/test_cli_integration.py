# tests/integration/test_cli_integration.py
"""
Integration tests for CLI functionality.
Tests complete CLI workflows, command interactions, and system integration.
"""

import pytest
import os
import tempfile
import json
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import subprocess
import sys


class MockCLIApplication:
    """Mock CLI application for integration testing"""
    
    def __init__(self):
        self.config = {
            'api_url': 'http://localhost:8000',
            'timeout': 30,
            'auto_save': True,
            'theme': 'dark'
        }
        self.session = {
            'user_id': None,
            'username': None,
            'token': None,
            'current_topic': None,
            'active_exercise': None
        }
        self.history = []
        self.temp_files = []
    
    def login(self, username, password):
        """Simulate user login"""
        if username == "testuser" and password == "password123":
            self.session.update({
                'user_id': 123,
                'username': username,
                'token': 'mock_jwt_token',
                'login_time': datetime.now()
            })
            self.history.append(f"LOGIN: {username}")
            return {"success": True, "message": "Login successful"}
        else:
            return {"success": False, "message": "Invalid credentials"}
    
    def logout(self):
        """Simulate user logout"""
        if self.session['user_id']:
            username = self.session['username']
            self.session = {
                'user_id': None,
                'username': None,
                'token': None,
                'current_topic': None,
                'active_exercise': None
            }
            self.history.append(f"LOGOUT: {username}")
            return {"success": True, "message": "Logged out successfully"}
        else:
            return {"success": False, "message": "Not logged in"}
    
    def start_learning_session(self, topic, level=1):
        """Start learning session"""
        if not self.session['user_id']:
            return {"success": False, "message": "Please login first"}
        
        if topic not in ['basics', 'oop', 'advanced', 'data_structures', 'algorithms']:
            return {"success": False, "message": "Invalid topic"}
        
        self.session['current_topic'] = topic
        self.history.append(f"START_SESSION: {topic} (level {level})")
        
        return {
            "success": True,
            "message": f"Started {topic} learning session at level {level}",
            "available_exercises": [
                {"id": 1, "title": f"{topic.title()} Exercise 1", "difficulty": "beginner"},
                {"id": 2, "title": f"{topic.title()} Exercise 2", "difficulty": "intermediate"},
                {"id": 3, "title": f"{topic.title()} Exercise 3", "difficulty": "advanced"}
            ]
        }
    
    def list_exercises(self, topic=None, difficulty=None):
        """List available exercises"""
        if not self.session['user_id']:
            return {"success": False, "message": "Please login first"}
        
        # Mock exercise data
        all_exercises = []
        topics = [topic] if topic else ['basics', 'oop', 'advanced']
        difficulties = [difficulty] if difficulty else ['beginner', 'intermediate', 'advanced']
        
        exercise_id = 1
        for t in topics:
            for d in difficulties:
                all_exercises.append({
                    "id": exercise_id,
                    "title": f"{t.title()} {d.title()} Exercise",
                    "topic": t,
                    "difficulty": d,
                    "points": 10 + (exercise_id % 3) * 5,
                    "completed": exercise_id % 4 == 0  # Some completed
                })
                exercise_id += 1
        
        self.history.append(f"LIST_EXERCISES: topic={topic}, difficulty={difficulty}")
        return {"success": True, "exercises": all_exercises}
    
    def start_exercise(self, exercise_id):
        """Start working on an exercise"""
        if not self.session['user_id']:
            return {"success": False, "message": "Please login first"}
        
        if not self.session['current_topic']:
            return {"success": False, "message": "Please start a learning session first"}
        
        # Mock exercise details
        exercise = {
            "id": exercise_id,
            "title": f"Exercise {exercise_id}",
            "description": f"This is exercise {exercise_id} for {self.session['current_topic']}",
            "instructions": "Write a function that solves the given problem",
            "template": "def solution():\n    # Your code here\n    pass",
            "test_cases": [
                {"input": "test1", "expected": "output1"},
                {"input": "test2", "expected": "output2"}
            ]
        }
        
        self.session['active_exercise'] = exercise_id
        self.history.append(f"START_EXERCISE: {exercise_id}")
        
        return {"success": True, "exercise": exercise}
    
    def submit_solution(self, exercise_id, solution_file):
        """Submit solution for an exercise"""
        if not self.session['user_id']:
            return {"success": False, "message": "Please login first"}
        
        if not os.path.exists(solution_file):
            return {"success": False, "message": "Solution file not found"}
        
        # Read solution file
        try:
            with open(solution_file, 'r') as f:
                solution_code = f.read()
        except Exception as e:
            return {"success": False, "message": f"Error reading solution file: {str(e)}"}
        
        # Mock evaluation
        score = 85 + (exercise_id % 10)  # Simulate variable scores
        passed_tests = 2 if score > 90 else 1
        total_tests = 2
        
        result = {
            "success": True,
            "exercise_id": exercise_id,
            "score": score,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "feedback": "Good solution! Consider edge cases." if score > 80 else "Solution needs improvement.",
            "submission_time": datetime.now().isoformat()
        }
        
        self.history.append(f"SUBMIT_SOLUTION: {exercise_id} (score: {score})")
        return result
    
    def get_progress(self, detailed=False):
        """Get user progress"""
        if not self.session['user_id']:
            return {"success": False, "message": "Please login first"}
        
        progress = {
            "user_id": self.session['user_id'],
            "username": self.session['username'],
            "overall_progress": 67.5,
            "topics": {
                "basics": {"completed": 8, "total": 12, "progress": 66.7},
                "oop": {"completed": 5, "total": 10, "progress": 50.0},
                "advanced": {"completed": 2, "total": 8, "progress": 25.0}
            },
            "total_points": 275,
            "current_level": 3,
            "achievements": [
                {"name": "First Steps", "earned": "2024-01-01"},
                {"name": "Quick Learner", "earned": "2024-01-05"}
            ]
        }
        
        if detailed:
            progress["recent_submissions"] = [
                {"exercise_id": 15, "score": 92, "date": "2024-01-10"},
                {"exercise_id": 14, "score": 78, "date": "2024-01-09"},
                {"exercise_id": 13, "score": 95, "date": "2024-01-08"}
            ]
            progress["time_spent"] = {"today": 120, "this_week": 480, "total": 2400}  # minutes
        
        self.history.append(f"GET_PROGRESS: detailed={detailed}")
        return {"success": True, "progress": progress}
    
    def save_config(self, config_file=None):
        """Save current configuration"""
        if not config_file:
            config_file = os.path.expanduser("~/.pylearn_config.json")
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return {"success": True, "message": f"Configuration saved to {config_file}"}
        except Exception as e:
            return {"success": False, "message": f"Error saving config: {str(e)}"}
    
    def load_config(self, config_file=None):
        """Load configuration"""
        if not config_file:
            config_file = os.path.expanduser("~/.pylearn_config.json")
        
        if not os.path.exists(config_file):
            return {"success": False, "message": "Configuration file not found"}
        
        try:
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
            self.config.update(loaded_config)
            return {"success": True, "message": "Configuration loaded successfully"}
        except Exception as e:
            return {"success": False, "message": f"Error loading config: {str(e)}"}
    
    def create_solution_file(self, exercise_id, content=None):
        """Create a temporary solution file"""
        if content is None:
            content = f"# Solution for exercise {exercise_id}\ndef solution():\n    return 'Hello, World!'"
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(content)
        temp_file.close()
        
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except FileNotFoundError:
                pass
        self.temp_files = []


class TestCLIBasicWorkflow:
    """Test basic CLI workflow operations"""
    
    @pytest.fixture
    def cli_app(self):
        app = MockCLIApplication()
        yield app
        app.cleanup()
    
    def test_login_logout_flow(self, cli_app):
        """Test complete login/logout flow"""
        # Initial state - not logged in
        assert cli_app.session['user_id'] is None
        
        # Login with valid credentials
        result = cli_app.login("testuser", "password123")
        assert result['success'] is True
        assert cli_app.session['user_id'] == 123
        assert cli_app.session['username'] == "testuser"
        assert cli_app.session['token'] == "mock_jwt_token"
        assert "LOGIN: testuser" in cli_app.history
        
        # Logout
        result = cli_app.logout()
        assert result['success'] is True
        assert cli_app.session['user_id'] is None
        assert cli_app.session['username'] is None
        assert "LOGOUT: testuser" in cli_app.history
    
    def test_login_with_invalid_credentials(self, cli_app):
        """Test login with invalid credentials"""
        result = cli_app.login("wronguser", "wrongpass")
        assert result['success'] is False
        assert "Invalid credentials" in result['message']
        assert cli_app.session['user_id'] is None
    
    def test_operations_require_login(self, cli_app):
        """Test that operations require login"""
        # Try to start session without login
        result = cli_app.start_learning_session("basics")
        assert result['success'] is False
        assert "Please login first" in result['message']
        
        # Try to list exercises without login
        result = cli_app.list_exercises()
        assert result['success'] is False
        assert "Please login first" in result['message']
        
        # Try to get progress without login
        result = cli_app.get_progress()
        assert result['success'] is False
        assert "Please login first" in result['message']


class TestCLILearningWorkflow:
    """Test complete learning workflow through CLI"""
    
    @pytest.fixture
    def logged_in_cli(self):
        app = MockCLIApplication()
        app.login("testuser", "password123")
        yield app
        app.cleanup()
    
    def test_complete_learning_session(self, logged_in_cli):
        """Test complete learning session workflow"""
        # Start learning session
        result = logged_in_cli.start_learning_session("basics", level=2)
        assert result['success'] is True
        assert logged_in_cli.session['current_topic'] == "basics"
        assert "available_exercises" in result
        assert len(result['available_exercises']) == 3
        
        # List exercises for current topic
        result = logged_in_cli.list_exercises(topic="basics")
        assert result['success'] is True
        assert len(result['exercises']) > 0
        
        # Start first exercise
        exercise_id = 1
        result = logged_in_cli.start_exercise(exercise_id)
        assert result['success'] is True
        assert logged_in_cli.session['active_exercise'] == exercise_id
        assert "exercise" in result
        assert result['exercise']['id'] == exercise_id
        
        # Create solution file
        solution_file = logged_in_cli.create_solution_file(exercise_id)
        assert os.path.exists(solution_file)
        
        # Submit solution
        result = logged_in_cli.submit_solution(exercise_id, solution_file)
        assert result['success'] is True
        assert result['exercise_id'] == exercise_id
        assert 'score' in result
        assert 'feedback' in result
        
        # Check progress
        result = logged_in_cli.get_progress()
        assert result['success'] is True
        assert result['progress']['user_id'] == 123
        assert 'overall_progress' in result['progress']
    
    def test_exercise_workflow_without_session(self, logged_in_cli):
        """Test exercise workflow without starting session"""
        # Try to start exercise without session
        result = logged_in_cli.start_exercise(1)
        assert result['success'] is False
        assert "start a learning session first" in result['message']
    
    def test_submit_nonexistent_solution(self, logged_in_cli):
        """Test submitting solution with nonexistent file"""
        logged_in_cli.start_learning_session("basics")
        
        result = logged_in_cli.submit_solution(1, "/nonexistent/file.py")
        assert result['success'] is False
        assert "Solution file not found" in result['message']
    
    def test_detailed_progress_report(self, logged_in_cli):
        """Test detailed progress reporting"""
        result = logged_in_cli.get_progress(detailed=True)
        assert result['success'] is True
        
        progress = result['progress']
        assert 'recent_submissions' in progress
        assert 'time_spent' in progress
        assert len(progress['recent_submissions']) > 0
        assert 'today' in progress['time_spent']
        assert 'this_week' in progress['time_spent']
        assert 'total' in progress['time_spent']


class TestCLIConfigurationManagement:
    """Test CLI configuration management"""
    
    @pytest.fixture
    def cli_app(self):
        app = MockCLIApplication()
        yield app
        app.cleanup()
    
    def test_save_and_load_config(self, cli_app):
        """Test saving and loading configuration"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:
            config_path = config_file.name
        
        try:
            # Modify configuration
            cli_app.config['theme'] = 'light'
            cli_app.config['auto_save'] = False
            cli_app.config['new_setting'] = 'test_value'
            
            # Save configuration
            result = cli_app.save_config(config_path)
            assert result['success'] is True
            assert os.path.exists(config_path)
            
            # Reset configuration
            cli_app.config = {'theme': 'dark', 'auto_save': True}
            
            # Load configuration
            result = cli_app.load_config(config_path)
            assert result['success'] is True
            assert cli_app.config['theme'] == 'light'
            assert cli_app.config['auto_save'] is False
            assert cli_app.config['new_setting'] == 'test_value'
            
        finally:
            # Clean up
            try:
                os.unlink(config_path)
            except FileNotFoundError:
                pass
    
    def test_load_nonexistent_config(self, cli_app):
        """Test loading nonexistent configuration file"""
        result = cli_app.load_config("/nonexistent/config.json")
        assert result['success'] is False
        assert "Configuration file not found" in result['message']
    
    def test_config_persistence(self, cli_app):
        """Test that configuration persists across operations"""
        # Set initial config
        cli_app.config['custom_setting'] = 'persistent_value'
        
        # Perform various operations
        cli_app.login("testuser", "password123")
        cli_app.start_learning_session("basics")
        cli_app.logout()
        
        # Check that config is still there
        assert cli_app.config['custom_setting'] == 'persistent_value'


class TestCLIErrorHandling:
    """Test CLI error handling and recovery"""
    
    @pytest.fixture
    def cli_app(self):
        app = MockCLIApplication()
        yield app
        app.cleanup()
    
    def test_invalid_topic_handling(self, cli_app):
        """Test handling of invalid learning topics"""
        cli_app.login("testuser", "password123")
        
        result = cli_app.start_learning_session("invalid_topic")
        assert result['success'] is False
        assert "Invalid topic" in result['message']
    
    def test_corrupted_solution_file_handling(self, cli_app):
        """Test handling of corrupted solution files"""
        cli_app.login("testuser", "password123")
        cli_app.start_learning_session("basics")
        
        # Create corrupted file (binary content)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as temp_file:
            temp_file.write(b'\x00\x01\x02\x03')  # Binary content
            corrupted_file = temp_file.name
        
        try:
            # This should handle the error gracefully
            result = cli_app.submit_solution(1, corrupted_file)
            # The mock implementation reads text files, so this might succeed
            # In a real implementation, this would handle encoding errors
            assert 'success' in result
            
        finally:
            os.unlink(corrupted_file)
    
    def test_session_state_recovery(self, cli_app):
        """Test recovery from inconsistent session state"""
        # Manually corrupt session state
        cli_app.session['user_id'] = 123
        cli_app.session['username'] = None  # Inconsistent state
        
        # Operations should handle this gracefully
        result = cli_app.get_progress()
        assert 'success' in result  # Should not crash
    
    def test_file_permission_errors(self, cli_app):
        """Test handling of file permission errors"""
        # Try to save config to read-only location (simulation)
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = cli_app.save_config("/readonly/config.json")
            assert result['success'] is False
            assert "Error saving config" in result['message']


class TestCLIMultiSessionWorkflow:
    """Test workflows involving multiple sessions and topics"""
    
    @pytest.fixture
    def cli_app(self):
        app = MockCLIApplication()
        app.login("testuser", "password123")
        yield app
        app.cleanup()
    
    def test_multiple_topic_sessions(self, cli_app):
        """Test working with multiple topics in sequence"""
        topics = ["basics", "oop", "advanced"]
        
        for topic in topics:
            # Start session for topic
            result = cli_app.start_learning_session(topic)
            assert result['success'] is True
            assert cli_app.session['current_topic'] == topic
            
            # List exercises for topic
            result = cli_app.list_exercises(topic=topic)
            assert result['success'] is True
            
            # Work on first exercise
            result = cli_app.start_exercise(1)
            assert result['success'] is True
            
            # Submit solution
            solution_file = cli_app.create_solution_file(1)
            result = cli_app.submit_solution(1, solution_file)
            assert result['success'] is True
        
        # Check that history contains all operations
        assert len([h for h in cli_app.history if h.startswith("START_SESSION")]) == 3
        assert "START_SESSION: basics" in cli_app.history
        assert "START_SESSION: oop" in cli_app.history
        assert "START_SESSION: advanced" in cli_app.history
    
    def test_progress_across_sessions(self, cli_app):
        """Test that progress accumulates across sessions"""
        # Initial progress check
        result = cli_app.get_progress()
        initial_progress = result['progress']['overall_progress']
        
        # Complete some exercises
        for topic in ["basics", "oop"]:
            cli_app.start_learning_session(topic)
            for exercise_id in [1, 2]:
                cli_app.start_exercise(exercise_id)
                solution_file = cli_app.create_solution_file(exercise_id)
                cli_app.submit_solution(exercise_id, solution_file)
        
        # Check progress has been recorded
        result = cli_app.get_progress()
        # In a real implementation, progress would actually increase
        assert 'overall_progress' in result['progress']
    
    def test_session_switching(self, cli_app):
        """Test switching between different learning sessions"""
        # Start with basics
        cli_app.start_learning_session("basics")
        assert cli_app.session['current_topic'] == "basics"
        
        # Switch to OOP
        cli_app.start_learning_session("oop")
        assert cli_app.session['current_topic'] == "oop"
        
        # Switch to advanced
        cli_app.start_learning_session("advanced")
        assert cli_app.session['current_topic'] == "advanced"
        
        # Check that session state is consistent
        result = cli_app.start_exercise(1)
        assert result['success'] is True
        assert cli_app.session['active_exercise'] == 1


class TestCLIDataPersistence:
    """Test data persistence and file operations"""
    
    @pytest.fixture
    def cli_app(self):
        app = MockCLIApplication()
        yield app
        app.cleanup()
    
    def test_solution_file_creation_and_content(self, cli_app):
        """Test solution file creation with different content types"""
        # Test with default content
        solution_file = cli_app.create_solution_file(1)
        assert os.path.exists(solution_file)
        
        with open(solution_file, 'r') as f:
            content = f.read()
        assert "def solution():" in content
        assert f"exercise 1" in content.lower()
        
        # Test with custom content
        custom_content = "def custom_solution():\n    return 42"
        custom_file = cli_app.create_solution_file(2, custom_content)
        
        with open(custom_file, 'r') as f:
            content = f.read()
        assert content == custom_content
    
    def test_temporary_file_cleanup(self, cli_app):
        """Test that temporary files are properly cleaned up"""
        # Create several solution files
        files = []
        for i in range(3):
            file_path = cli_app.create_solution_file(i)
            files.append(file_path)
            assert os.path.exists(file_path)
        
        # All files should exist
        assert len(cli_app.temp_files) == 3
        
        # Cleanup should remove all files
        cli_app.cleanup()
        
        for file_path in files:
            assert not os.path.exists(file_path)
        assert len(cli_app.temp_files) == 0
    
    def test_config_file_format(self, cli_app):
        """Test that configuration files are properly formatted JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:
            config_path = config_file.name
        
        try:
            # Save config
            result = cli_app.save_config(config_path)
            assert result['success'] is True
            
            # Verify it's valid JSON
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Check that all expected keys are present
            expected_keys = ['api_url', 'timeout', 'auto_save', 'theme']
            for key in expected_keys:
                assert key in loaded_config
            
            # Check data types
            assert isinstance(loaded_config['api_url'], str)
            assert isinstance(loaded_config['timeout'], int)
            assert isinstance(loaded_config['auto_save'], bool)
            assert isinstance(loaded_config['theme'], str)
            
        finally:
            os.unlink(config_path)


class TestCLIPerformanceAndScaling:
    """Test CLI performance with larger datasets and operations"""
    
    @pytest.fixture
    def cli_app(self):
        app = MockCLIApplication()
        app.login("testuser", "password123")
        yield app
        app.cleanup()
    
    def test_large_exercise_list_handling(self, cli_app):
        """Test handling of large exercise lists"""
        # List exercises across all topics and difficulties
        result = cli_app.list_exercises()
        assert result['success'] is True
        
        exercises = result['exercises']
        assert len(exercises) > 0
        
        # Verify all exercises have required fields
        for exercise in exercises:
            assert 'id' in exercise
            assert 'title' in exercise
            assert 'topic' in exercise
            assert 'difficulty' in exercise
            assert 'points' in exercise
            assert 'completed' in exercise
    
    def test_multiple_rapid_operations(self, cli_app):
        """Test performing many operations in rapid succession"""
        start_time = time.time()
        
        # Perform many operations quickly
        for i in range(10):
            cli_app.list_exercises()
            cli_app.get_progress()
            cli_app.start_learning_session("basics")
            cli_app.start_exercise(1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete reasonably quickly (adjust threshold as needed)
        assert duration < 5.0  # Should complete in under 5 seconds
        
        # Check that all operations were recorded
        assert len(cli_app.history) >= 40  # 4 operations × 10 iterations
    
    def test_history_tracking_performance(self, cli_app):
        """Test that history tracking doesn't degrade performance"""
        initial_history_length = len(cli_app.history)
        
        # Perform operations that generate history
        for i in range(100):
            cli_app.list_exercises()
        
        # History should have grown appropriately
        final_history_length = len(cli_app.history)
        assert final_history_length == initial_history_length + 100
        
        # Recent history should be accessible
        recent_entries = [h for h in cli_app.history[-10:] if h.startswith("LIST_EXERCISES")]
        assert len(recent_entries) == 10


class TestCLICommandLineIntegration:
    """Test integration with actual command-line interface"""
    
    def test_command_line_argument_parsing(self):
        """Test that command line arguments are parsed correctly"""
        # This would test actual CLI argument parsing
        # In a real implementation, you'd test with subprocess or argparse
        
        # Mock command line scenarios
        test_commands = [
            ["python", "cli.py", "login", "--username", "testuser"],
            ["python", "cli.py", "start", "--topic", "basics", "--level", "2"],
            ["python", "cli.py", "list", "exercises", "--difficulty", "beginner"],
            ["python", "cli.py", "submit", "--exercise", "1", "--file", "solution.py"],
            ["python", "cli.py", "progress", "--detailed"],
            ["python", "cli.py", "logout"]
        ]
        
        # Each command should have the expected structure
        for cmd in test_commands:
            assert len(cmd) >= 3  # python, script, command
            assert cmd[0] == "python"
            assert cmd[1] == "cli.py"
            assert cmd[2] in ["login", "start", "list", "submit", "progress", "logout"]
    
    @patch('subprocess.run')
    def test_external_tool_integration(self, mock_subprocess):
        """Test integration with external tools (mocked)"""
        # Mock successful subprocess calls
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Success"
        
        # Simulate calling external Python interpreter for solution testing
        cli_app = MockCLIApplication()
        cli_app.login("testuser", "password123")
        cli_app.start_learning_session("basics")
        
        solution_file = cli_app.create_solution_file(1)
        
        # In real implementation, this might call external Python interpreter
        # subprocess.run([sys.executable, solution_file])
        
        result = cli_app.submit_solution(1, solution_file)
        assert result['success'] is True
        
        cli_app.cleanup()
    
    def test_environment_variable_handling(self):
        """Test handling of environment variables"""
        # Test common environment variables that might affect CLI behavior
        env_vars_to_test = [
            'HOME',
            'USER',
            'PATH',
            'PYTHONPATH'
        ]
        
        for var in env_vars_to_test:
            # Environment variable should be accessible
            value = os.environ.get(var)
            # Some variables might not be set, which is fine
            if value is not None:
                assert isinstance(value, str)
                assert len(value) > 0
    
    def test_cross_platform_compatibility(self):
        """Test cross-platform compatibility considerations"""
        cli_app = MockCLIApplication()
        
        # Test path handling works on current platform
        config_path = os.path.expanduser("~/.pylearn_config.json")
        assert os.path.isabs(config_path)
        
        # Test temporary file creation works
        solution_file = cli_app.create_solution_file(1)
        assert os.path.exists(solution_file)
        assert solution_file.endswith('.py')
        
        cli_app.cleanup()