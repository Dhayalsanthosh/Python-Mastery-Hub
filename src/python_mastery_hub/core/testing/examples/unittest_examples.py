"""
unittest examples for the Testing module.
Comprehensive examples of Python's unittest framework.
"""

from typing import Dict, Any


def get_unittest_examples() -> Dict[str, Any]:
    """Get comprehensive unittest examples."""
    return {
        "basic_unittest": {
            "code": '''
import unittest
from unittest import TestCase

# Example class to test
class Calculator:
    """Simple calculator for demonstration."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a, b):
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    def power(self, base, exponent):
        """Raise base to the power of exponent."""
        if not isinstance(base, (int, float)) or not isinstance(exponent, (int, float)):
            raise TypeError("Both arguments must be numbers")
        return base ** exponent

class TestCalculator(TestCase):
    """Test cases for Calculator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.calc = Calculator()
        print(f"Running test: {self._testMethodName}")
    
    def tearDown(self):
        """Clean up after each test method."""
        print(f"Finished test: {self._testMethodName}")
    
    def test_add_positive_numbers(self):
        """Test addition of positive numbers."""
        result = self.calc.add(3, 5)
        self.assertEqual(result, 8)
        self.assertIsInstance(result, (int, float))
    
    def test_add_negative_numbers(self):
        """Test addition with negative numbers."""
        result = self.calc.add(-3, -5)
        self.assertEqual(result, -8)
    
    def test_add_zero(self):
        """Test addition with zero."""
        result = self.calc.add(5, 0)
        self.assertEqual(result, 5)
    
    def test_subtract_basic(self):
        """Test basic subtraction."""
        result = self.calc.subtract(10, 3)
        self.assertEqual(result, 7)
    
    def test_multiply_basic(self):
        """Test basic multiplication."""
        result = self.calc.multiply(4, 5)
        self.assertEqual(result, 20)
    
    def test_multiply_by_zero(self):
        """Test multiplication by zero."""
        result = self.calc.multiply(5, 0)
        self.assertEqual(result, 0)
    
    def test_divide_basic(self):
        """Test basic division."""
        result = self.calc.divide(10, 2)
        self.assertEqual(result, 5.0)
    
    def test_divide_by_zero(self):
        """Test division by zero raises exception."""
        with self.assertRaises(ValueError):
            self.calc.divide(10, 0)
        
        # Alternative way to test exceptions
        with self.assertRaisesRegex(ValueError, "Cannot divide by zero"):
            self.calc.divide(5, 0)
    
    def test_power_basic(self):
        """Test power operation."""
        result = self.calc.power(2, 3)
        self.assertEqual(result, 8)
    
    def test_power_invalid_types(self):
        """Test power operation with invalid types."""
        with self.assertRaises(TypeError):
            self.calc.power("2", 3)
        
        with self.assertRaises(TypeError):
            self.calc.power(2, "3")

# Running tests
if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Basic unittest structure with setUp/tearDown and various assertion methods"
        },
        
        "assertion_methods": {
            "code": '''
import unittest
from unittest import TestCase

class TestAssertionMethods(TestCase):
    """Demonstrate various assertion methods."""
    
    def test_equality_assertions(self):
        """Test equality assertions."""
        self.assertEqual(1 + 1, 2)
        self.assertNotEqual(1 + 1, 3)
        
        # For floating point comparison
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=7)
        self.assertNotAlmostEqual(0.1 + 0.2, 0.4, places=7)
    
    def test_boolean_assertions(self):
        """Test boolean assertions."""
        self.assertTrue(True)
        self.assertFalse(False)
        
        # Test truthiness
        self.assertTrue([1, 2, 3])  # Non-empty list is truthy
        self.assertFalse([])        # Empty list is falsy
    
    def test_membership_assertions(self):
        """Test membership assertions."""
        items = [1, 2, 3, 4, 5]
        self.assertIn(3, items)
        self.assertNotIn(6, items)
        
        # For dictionaries
        data = {"a": 1, "b": 2}
        self.assertIn("a", data)
        self.assertNotIn("c", data)
    
    def test_type_assertions(self):
        """Test type assertions."""
        self.assertIsInstance("hello", str)
        self.assertNotIsInstance("hello", int)
        self.assertIsNone(None)
        self.assertIsNotNone("not none")
    
    def test_comparison_assertions(self):
        """Test comparison assertions."""
        self.assertGreater(5, 3)
        self.assertGreaterEqual(5, 5)
        self.assertLess(3, 5)
        self.assertLessEqual(3, 3)
    
    def test_collection_assertions(self):
        """Test collection assertions."""
        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        
        self.assertListEqual(list1, list2)
        self.assertTupleEqual((1, 2), (1, 2))
        self.assertDictEqual({"a": 1}, {"a": 1})
        self.assertSetEqual({1, 2, 3}, {3, 2, 1})
        
        # Same elements, different order
        self.assertCountEqual([1, 2, 3], [3, 2, 1])
    
    def test_regex_assertions(self):
        """Test regex assertions."""
        text = "Hello, World!"
        self.assertRegex(text, r"Hello.*World")
        self.assertNotRegex(text, r"goodbye")
    
    def test_custom_assertion_messages(self):
        """Test assertions with custom messages."""
        x = 10
        y = 5
        self.assertEqual(x, 10, f"Expected x to be 10, but got {x}")
        self.assertGreater(x, y, f"Expected {x} > {y}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
            "explanation": "Comprehensive coverage of unittest assertion methods for different data types"
        },
        
        "advanced_features": {
            "code": '''
import unittest
from unittest import TestCase, skip, skipIf, expectedFailure
import sys
import tempfile
import os

class BankAccount:
    """Bank account class for testing demonstrations."""
    
    def __init__(self, account_number, initial_balance=0):
        self.account_number = account_number
        self.balance = initial_balance
        self.transaction_history = []
    
    def deposit(self, amount):
        """Deposit money to account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += amount
        self.transaction_history.append(f"Deposit: +${amount}")
        return self.balance
    
    def withdraw(self, amount):
        """Withdraw money from account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        
        self.balance -= amount
        self.transaction_history.append(f"Withdrawal: -${amount}")
        return self.balance
    
    def get_balance(self):
        """Get current balance."""
        return self.balance
    
    def transfer_to(self, other_account, amount):
        """Transfer money to another account."""
        self.withdraw(amount)
        other_account.deposit(amount)
        
        self.transaction_history.append(f"Transfer out: -${amount} to {other_account.account_number}")
        other_account.transaction_history.append(f"Transfer in: +${amount} from {self.account_number}")

class TestBankAccountAdvanced(TestCase):
    """Advanced unittest features demonstration."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures (run once for the class)."""
        print("\\nSetting up class-level fixtures")
        cls.bank_name = "Test Bank"
        cls.interest_rate = 0.02
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level fixtures."""
        print("Cleaning up class-level fixtures")
    
    def setUp(self):
        """Set up test fixtures for each test."""
        self.account1 = BankAccount("ACC001", 1000)
        self.account2 = BankAccount("ACC002", 500)
    
    def test_deposit_valid_amount(self):
        """Test depositing a valid amount."""
        initial_balance = self.account1.get_balance()
        new_balance = self.account1.deposit(200)
        
        self.assertEqual(new_balance, initial_balance + 200)
        self.assertEqual(self.account1.get_balance(), 1200)
        self.assertIn("Deposit: +$200", self.account1.transaction_history)
    
    def test_withdraw_valid_amount(self):
        """Test withdrawing a valid amount."""
        initial_balance = self.account1.get_balance()
        new_balance = self.account1.withdraw(300)
        
        self.assertEqual(new_balance, initial_balance - 300)
        self.assertEqual(self.account1.get_balance(), 700)
    
    def test_withdraw_insufficient_funds(self):
        """Test withdrawing more than available balance."""
        with self.assertRaises(ValueError) as context:
            self.account1.withdraw(1500)
        
        self.assertIn("Insufficient funds", str(context.exception))
        self.assertEqual(self.account1.get_balance(), 1000)  # Balance unchanged
    
    def test_transfer_between_accounts(self):
        """Test money transfer between accounts."""
        transfer_amount = 200
        initial_balance1 = self.account1.get_balance()
        initial_balance2 = self.account2.get_balance()
        
        self.account1.transfer_to(self.account2, transfer_amount)
        
        self.assertEqual(self.account1.get_balance(), initial_balance1 - transfer_amount)
        self.assertEqual(self.account2.get_balance(), initial_balance2 + transfer_amount)
    
    @skip("Skipping this test for demonstration")
    def test_skipped_functionality(self):
        """This test is skipped."""
        self.fail("This test should be skipped")
    
    @skipIf(sys.version_info < (3, 8), "Requires Python 3.8+")
    def test_conditional_skip(self):
        """Test that only runs on Python 3.8+."""
        self.assertTrue(True)
    
    @expectedFailure
    def test_expected_failure(self):
        """Test that is expected to fail."""
        self.assertEqual(1, 2, "This test is expected to fail")
    
    def test_with_temporary_file(self):
        """Test using temporary files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test data")
            temp_file_path = temp_file.name
        
        try:
            # Test file operations
            with open(temp_file_path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "test data")
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_multiple_assertions(self):
        """Test with multiple assertions and detailed messages."""
        account = BankAccount("TEST001", 100)
        
        # Test initial state
        self.assertEqual(account.account_number, "TEST001", "Account number should match")
        self.assertEqual(account.get_balance(), 100, "Initial balance should be 100")
        self.assertEqual(len(account.transaction_history), 0, "No transactions initially")
        
        # Test after deposit
        account.deposit(50)
        self.assertEqual(account.get_balance(), 150, "Balance after deposit")
        self.assertEqual(len(account.transaction_history), 1, "One transaction after deposit")

    def test_parameterized_with_subtests(self):
        """Test with multiple cases using subTest."""
        test_cases = [
            (100, 50, 150),    # deposit
            (1000, 200, 1200), # larger deposit
            (500, 500, 1000),  # equal amounts
        ]
        
        for initial, deposit, expected in test_cases:
            with self.subTest(initial=initial, deposit=deposit, expected=expected):
                account = BankAccount("TEST", initial)
                account.deposit(deposit)
                self.assertEqual(account.get_balance(), expected)

# Custom test result class for detailed reporting
class DetailedTestResult(unittest.TextTestResult):
    """Custom test result class with detailed reporting."""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
    
    def addSuccess(self, test):
        """Handle successful test."""
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            self.stream.writeln(f"✓ {test._testMethodName} - PASSED")
    
    def addError(self, test, err):
        """Handle test error."""
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.writeln(f"✗ {test._testMethodName} - ERROR")
    
    def addFailure(self, test, err):
        """Handle test failure."""
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.writeln(f"✗ {test._testMethodName} - FAILED")

class CustomTestRunner(unittest.TextTestRunner):
    """Custom test runner with enhanced reporting."""
    
    resultclass = DetailedTestResult
    
    def run(self, test):
        """Run tests with custom reporting."""
        result = super().run(test)
        
        # Print summary
        print(f"\\n{'='*50}")
        print(f"Test Summary:")
        print(f"Successes: {result.success_count}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        print(f"Total: {result.testsRun}")
        print(f"{'='*50}")
        
        return result

# Test organization with test suites
class TestSuiteExample:
    """Example of organizing tests into suites."""
    
    @staticmethod
    def basic_operations_suite():
        """Suite for basic banking operations."""
        suite = unittest.TestSuite()
        suite.addTest(TestBankAccountAdvanced('test_deposit_valid_amount'))
        suite.addTest(TestBankAccountAdvanced('test_withdraw_valid_amount'))
        return suite
    
    @staticmethod
    def error_handling_suite():
        """Suite for error handling tests."""
        suite = unittest.TestSuite()
        suite.addTest(TestBankAccountAdvanced('test_withdraw_insufficient_funds'))
        return suite
    
    @staticmethod
    def advanced_features_suite():
        """Suite for advanced features."""
        suite = unittest.TestSuite()
        suite.addTest(TestBankAccountAdvanced('test_transfer_between_accounts'))
        suite.addTest(TestBankAccountAdvanced('test_multiple_assertions'))
        return suite

# Running tests with custom configuration
if __name__ == '__main__':
    # Run with custom test runner
    print("=== Running with Custom Test Runner ===")
    runner = CustomTestRunner(verbosity=2)
    
    # Run different test suites
    print("\\n--- Basic Operations ---")
    runner.run(TestSuiteExample.basic_operations_suite())
    
    print("\\n--- Error Handling ---")
    runner.run(TestSuiteExample.error_handling_suite())
    
    print("\\n--- Advanced Features ---")
    runner.run(TestSuiteExample.advanced_features_suite())
''',
            "explanation": "Advanced unittest features including fixtures, skipping tests, custom runners, and test organization"
        }
    }