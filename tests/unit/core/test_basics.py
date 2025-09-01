# tests/unit/core/test_basics.py
# Unit tests for basic Python concepts and exercises

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Import modules under test (adjust based on your actual structure)
try:
    from src.core.basics import (
        VariableExercise, 
        DataTypeExercise, 
        OperatorExercise,
        BasicIOExercise,
        StringExercise
    )
    from src.core.evaluators import BasicPythonEvaluator
    from src.models.exercise import Exercise
    from src.services.exercise_service import ExerciseService
except ImportError:
    # Mock classes for when actual modules don't exist
    class VariableExercise:
        pass
    class DataTypeExercise:
        pass
    class OperatorExercise:
        pass
    class BasicIOExercise:
        pass
    class StringExercise:
        pass
    class BasicPythonEvaluator:
        pass
    class Exercise:
        pass
    class ExerciseService:
        pass


class TestVariableExercises:
    """Test cases for variable-related exercises."""
    
    @pytest.fixture
    def variable_exercise(self):
        """Create a variable assignment exercise."""
        return {
            'id': 'var_001',
            'title': 'Variable Assignment',
            'description': 'Assign the value 42 to variable x',
            'template_code': '# Assign 42 to variable x\n',
            'solution_code': 'x = 42',
            'test_cases': [
                {
                    'test': "assert 'x' in globals()",
                    'description': 'Variable x should exist'
                },
                {
                    'test': 'assert x == 42',
                    'description': 'Variable x should equal 42'
                }
            ]
        }
    
    def test_simple_variable_assignment(self, variable_exercise):
        """Test basic variable assignment validation."""
        # Test correct solution
        code = 'x = 42'
        globals_dict = {}
        exec(code, globals_dict)
        
        assert 'x' in globals_dict
        assert globals_dict['x'] == 42
    
    def test_variable_assignment_wrong_value(self, variable_exercise):
        """Test variable assignment with wrong value."""
        code = 'x = 43'  # Wrong value
        globals_dict = {}
        exec(code, globals_dict)
        
        assert 'x' in globals_dict
        assert globals_dict['x'] != 42
    
    def test_variable_assignment_wrong_name(self, variable_exercise):
        """Test variable assignment with wrong variable name."""
        code = 'y = 42'  # Wrong variable name
        globals_dict = {}
        exec(code, globals_dict)
        
        assert 'x' not in globals_dict
        assert 'y' in globals_dict
    
    def test_multiple_variable_assignment(self):
        """Test multiple variable assignments."""
        code = '''
x = 10
y = 20
z = x + y
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['x'] == 10
        assert globals_dict['y'] == 20
        assert globals_dict['z'] == 30
    
    def test_variable_reassignment(self):
        """Test variable reassignment."""
        code = '''
x = 10
x = 20
x = x + 5
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['x'] == 25
    
    @pytest.mark.parametrize("variable_name,value,expected", [
        ('name', '"Alice"', 'Alice'),
        ('age', '25', 25),
        ('height', '5.8', 5.8),
        ('is_student', 'True', True),
        ('grades', '[85, 90, 78]', [85, 90, 78])
    ])
    def test_variable_types(self, variable_name, value, expected):
        """Test variables with different data types."""
        code = f'{variable_name} = {value}'
        globals_dict = {}
        exec(code, globals_dict)
        
        assert variable_name in globals_dict
        assert globals_dict[variable_name] == expected


class TestDataTypeExercises:
    """Test cases for data type exercises."""
    
    def test_integer_operations(self):
        """Test integer data type operations."""
        code = '''
a = 10
b = 3
sum_result = a + b
diff_result = a - b
mult_result = a * b
div_result = a // b
mod_result = a % b
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['sum_result'] == 13
        assert globals_dict['diff_result'] == 7
        assert globals_dict['mult_result'] == 30
        assert globals_dict['div_result'] == 3
        assert globals_dict['mod_result'] == 1
    
    def test_float_operations(self):
        """Test floating point operations."""
        code = '''
a = 10.5
b = 2.5
sum_result = a + b
div_result = a / b
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['sum_result'] == 13.0
        assert globals_dict['div_result'] == 4.2
    
    def test_string_operations(self):
        """Test string operations."""
        code = '''
first_name = "John"
last_name = "Doe"
full_name = first_name + " " + last_name
name_length = len(full_name)
uppercase_name = full_name.upper()
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['full_name'] == "John Doe"
        assert globals_dict['name_length'] == 8
        assert globals_dict['uppercase_name'] == "JOHN DOE"
    
    def test_boolean_operations(self):
        """Test boolean operations."""
        code = '''
is_true = True
is_false = False
and_result = is_true and is_false
or_result = is_true or is_false
not_result = not is_true
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['and_result'] is False
        assert globals_dict['or_result'] is True
        assert globals_dict['not_result'] is False
    
    def test_list_operations(self):
        """Test list operations."""
        code = '''
numbers = [1, 2, 3, 4, 5]
list_length = len(numbers)
first_item = numbers[0]
last_item = numbers[-1]
numbers.append(6)
numbers_sum = sum(numbers)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['list_length'] == 5
        assert globals_dict['first_item'] == 1
        assert globals_dict['last_item'] == 5
        assert 6 in globals_dict['numbers']
        assert globals_dict['numbers_sum'] == 21
    
    def test_dictionary_operations(self):
        """Test dictionary operations."""
        code = '''
person = {"name": "Alice", "age": 30}
name = person["name"]
age = person["age"]
person["city"] = "New York"
keys_list = list(person.keys())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['name'] == "Alice"
        assert globals_dict['age'] == 30
        assert "city" in globals_dict['person']
        assert "name" in globals_dict['keys_list']


class TestOperatorExercises:
    """Test cases for operator exercises."""
    
    def test_arithmetic_operators(self):
        """Test arithmetic operators."""
        test_cases = [
            ('5 + 3', 8),
            ('10 - 4', 6),
            ('6 * 7', 42),
            ('15 / 3', 5.0),
            ('17 // 3', 5),
            ('17 % 3', 2),
            ('2 ** 3', 8)
        ]
        
        for expression, expected in test_cases:
            result = eval(expression)
            assert result == expected, f"Failed for {expression}: expected {expected}, got {result}"
    
    def test_comparison_operators(self):
        """Test comparison operators."""
        code = '''
a = 10
b = 20
equal = (a == b)
not_equal = (a != b)
greater = (b > a)
less = (a < b)
greater_equal = (a >= 10)
less_equal = (b <= 20)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['equal'] is False
        assert globals_dict['not_equal'] is True
        assert globals_dict['greater'] is True
        assert globals_dict['less'] is True
        assert globals_dict['greater_equal'] is True
        assert globals_dict['less_equal'] is True
    
    def test_logical_operators(self):
        """Test logical operators."""
        code = '''
x = True
y = False
and_op = x and y
or_op = x or y
not_op = not x
complex_op = (x and not y) or (not x and y)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['and_op'] is False
        assert globals_dict['or_op'] is True
        assert globals_dict['not_op'] is False
        assert globals_dict['complex_op'] is True
    
    def test_assignment_operators(self):
        """Test assignment operators."""
        code = '''
x = 10
x += 5
y = 20
y -= 3
z = 4
z *= 2
w = 16
w /= 4
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['x'] == 15
        assert globals_dict['y'] == 17
        assert globals_dict['z'] == 8
        assert globals_dict['w'] == 4.0


class TestBasicIOExercises:
    """Test cases for basic input/output exercises."""
    
    @patch('builtins.print')
    def test_print_statement(self, mock_print):
        """Test print statement functionality."""
        code = 'print("Hello, World!")'
        exec(code)
        
        mock_print.assert_called_once_with("Hello, World!")
    
    @patch('builtins.print')
    def test_print_variables(self, mock_print):
        """Test printing variables."""
        code = '''
name = "Alice"
age = 25
print(name)
print(age)
print(f"My name is {name} and I am {age} years old")
'''
        exec(code)
        
        assert mock_print.call_count == 3
        mock_print.assert_any_call("Alice")
        mock_print.assert_any_call(25)
    
    @patch('builtins.input', return_value='Alice')
    def test_input_statement(self, mock_input):
        """Test input statement functionality."""
        code = '''
name = input("Enter your name: ")
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        mock_input.assert_called_once_with("Enter your name: ")
        assert globals_dict['name'] == 'Alice'
    
    @patch('builtins.input', side_effect=['25', 'Alice'])
    def test_input_type_conversion(self, mock_input):
        """Test input with type conversion."""
        code = '''
age = int(input("Enter your age: "))
name = input("Enter your name: ")
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['age'] == 25
        assert globals_dict['name'] == 'Alice'
        assert isinstance(globals_dict['age'], int)
        assert isinstance(globals_dict['name'], str)


class TestStringExercises:
    """Test cases for string manipulation exercises."""
    
    def test_string_concatenation(self):
        """Test string concatenation."""
        code = '''
first = "Hello"
second = "World"
result = first + " " + second
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == "Hello World"
    
    def test_string_formatting(self):
        """Test string formatting methods."""
        code = '''
name = "Alice"
age = 25
f_string = f"My name is {name} and I am {age}"
format_method = "My name is {} and I am {}".format(name, age)
percent_format = "My name is %s and I am %d" % (name, age)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        expected = "My name is Alice and I am 25"
        assert globals_dict['f_string'] == expected
        assert globals_dict['format_method'] == expected
        assert globals_dict['percent_format'] == expected
    
    def test_string_methods(self):
        """Test various string methods."""
        code = '''
text = "  Hello World  "
upper_text = text.upper()
lower_text = text.lower()
stripped_text = text.strip()
replaced_text = text.replace("World", "Python")
split_text = "apple,banana,cherry".split(",")
joined_text = "-".join(["apple", "banana", "cherry"])
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['upper_text'] == "  HELLO WORLD  "
        assert globals_dict['lower_text'] == "  hello world  "
        assert globals_dict['stripped_text'] == "Hello World"
        assert globals_dict['replaced_text'] == "  Hello Python  "
        assert globals_dict['split_text'] == ["apple", "banana", "cherry"]
        assert globals_dict['joined_text'] == "apple-banana-cherry"
    
    def test_string_slicing(self):
        """Test string slicing operations."""
        code = '''
text = "Hello World"
first_char = text[0]
last_char = text[-1]
first_five = text[:5]
last_five = text[-5:]
middle = text[6:11]
every_second = text[::2]
reversed_text = text[::-1]
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['first_char'] == 'H'
        assert globals_dict['last_char'] == 'd'
        assert globals_dict['first_five'] == 'Hello'
        assert globals_dict['last_five'] == 'World'
        assert globals_dict['middle'] == 'World'
        assert globals_dict['every_second'] == 'HloWrd'
        assert globals_dict['reversed_text'] == 'dlroW olleH'


class TestBasicPythonEvaluator:
    """Test cases for the basic Python code evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create a basic Python evaluator instance."""
        return BasicPythonEvaluator()
    
    def test_evaluate_simple_assignment(self, evaluator):
        """Test evaluation of simple variable assignment."""
        code = 'x = 42'
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert 'x' in result['globals']
        assert result['globals']['x'] == 42
    
    def test_evaluate_syntax_error(self, evaluator):
        """Test evaluation of code with syntax error."""
        code = 'x = '  # Incomplete assignment
        result = evaluator.evaluate(code)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'SyntaxError' in result['error']['type']
    
    def test_evaluate_runtime_error(self, evaluator):
        """Test evaluation of code with runtime error."""
        code = 'x = 1 / 0'  # Division by zero
        result = evaluator.evaluate(code)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'ZeroDivisionError' in result['error']['type']
    
    def test_evaluate_with_output(self, evaluator):
        """Test evaluation of code that produces output."""
        code = 'print("Hello, World!")'
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert 'Hello, World!' in result['output']
    
    def test_evaluate_with_tests(self, evaluator):
        """Test evaluation with test cases."""
        code = 'x = 42'
        tests = [
            {
                'test': "assert 'x' in globals()",
                'description': 'Variable x should exist'
            },
            {
                'test': 'assert x == 42',
                'description': 'Variable x should equal 42'
            }
        ]
        
        result = evaluator.evaluate_with_tests(code, tests)
        
        assert result['success'] is True
        assert len(result['test_results']) == 2
        assert all(test['passed'] for test in result['test_results'])
    
    def test_evaluate_security_check(self, evaluator):
        """Test security checking for malicious code."""
        malicious_codes = [
            'import os; os.system("ls")',
            '__import__("subprocess").call(["ls"])',
            'exec("import os")',
            'eval("1+1")'
        ]
        
        for code in malicious_codes:
            result = evaluator.evaluate(code)
            assert result['success'] is False
            assert 'security' in result['error']['type'].lower()


class TestExerciseValidation:
    """Test cases for exercise validation."""
    
    def test_validate_exercise_structure(self):
        """Test validation of exercise data structure."""
        valid_exercise = {
            'id': 'test_001',
            'title': 'Test Exercise',
            'description': 'A test exercise for validation',
            'difficulty': 'beginner',
            'template_code': '# Your code here',
            'solution_code': 'x = 42',
            'test_cases': [
                {
                    'test': "assert 'x' in globals()",
                    'description': 'Variable x should exist'
                }
            ],
            'points': 10
        }
        
        # Should not raise any exceptions
        assert self._validate_exercise(valid_exercise) is True
    
    def test_validate_exercise_missing_fields(self):
        """Test validation with missing required fields."""
        invalid_exercise = {
            'id': 'test_001',
            'title': 'Test Exercise'
            # Missing other required fields
        }
        
        assert self._validate_exercise(invalid_exercise) is False
    
    def test_validate_exercise_invalid_difficulty(self):
        """Test validation with invalid difficulty level."""
        invalid_exercise = {
            'id': 'test_001',
            'title': 'Test Exercise',
            'description': 'A test exercise',
            'difficulty': 'invalid_level',  # Invalid difficulty
            'solution_code': 'x = 42',
            'test_cases': [],
            'points': 10
        }
        
        assert self._validate_exercise(invalid_exercise) is False
    
    def _validate_exercise(self, exercise_data):
        """Helper method to validate exercise data."""
        required_fields = ['id', 'title', 'description', 'difficulty', 'solution_code', 'test_cases', 'points']
        valid_difficulties = ['beginner', 'intermediate', 'advanced']
        
        # Check required fields
        for field in required_fields:
            if field not in exercise_data:
                return False
        
        # Check difficulty level
        if exercise_data['difficulty'] not in valid_difficulties:
            return False
        
        # Check test cases is a list
        if not isinstance(exercise_data['test_cases'], list):
            return False
        
        # Check points is positive integer
        if not isinstance(exercise_data['points'], int) or exercise_data['points'] <= 0:
            return False
        
        return True


@pytest.mark.integration
class TestBasicsIntegration:
    """Integration tests for basic Python concepts."""
    
    @pytest.fixture
    def exercise_service(self):
        """Create a mock exercise service."""
        service = Mock(spec=ExerciseService)
        service.get_exercise_by_id = AsyncMock()
        service.evaluate_solution = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_complete_exercise_workflow(self, exercise_service, sample_exercise):
        """Test the complete workflow of solving a basic exercise."""
        # Setup
        exercise_service.get_exercise_by_id.return_value = sample_exercise
        exercise_service.evaluate_solution.return_value = {
            'success': True,
            'score': 100,
            'feedback': 'Excellent work!'
        }
        
        # Simulate user solving exercise
        exercise = await exercise_service.get_exercise_by_id('ex_sample_001')
        user_solution = 'x = 42'
        
        # Evaluate solution
        result = await exercise_service.evaluate_solution(exercise['id'], user_solution)
        
        # Assertions
        assert result['success'] is True
        assert result['score'] == 100
        exercise_service.get_exercise_by_id.assert_called_once_with('ex_sample_001')
        exercise_service.evaluate_solution.assert_called_once_with('ex_sample_001', user_solution)


if __name__ == '__main__':
    pytest.main([__file__])