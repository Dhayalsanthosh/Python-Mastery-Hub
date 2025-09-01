"""
TDD (Test-Driven Development) examples for the Testing module.
Demonstrates the Red-Green-Refactor cycle with practical examples.
"""

from typing import Dict, Any


def get_tdd_examples() -> Dict[str, Any]:
    """Get comprehensive TDD examples."""
    return {
        "tdd_cycle_demo": {
            "code": '''
"""
TDD Demonstration: Building a Password Validator
This example shows the complete Red-Green-Refactor cycle.
"""

import unittest
import re

# Step 1: RED - Start with failing tests
class TestPasswordValidator(unittest.TestCase):
    """TDD example: Password validation."""
    
    def setUp(self):
        """Create a fresh validator for each test."""
        self.validator = PasswordValidator()  # This will fail initially
    
    # Test 1: Minimum length requirement
    def test_password_too_short_fails(self):
        """RED: Password must be at least 8 characters."""
        result = self.validator.validate("short")
        self.assertFalse(result.is_valid)
        self.assertIn("at least 8 characters", result.errors)
    
    def test_password_minimum_length_passes(self):
        """Password with exactly 8 characters should pass length check."""
        result = self.validator.validate("12345678")
        # Initially this might fail for other reasons, but length should pass
        self.assertNotIn("at least 8 characters", result.errors)

# Step 2: GREEN - Minimal implementation
class ValidationResult:
    """Result of password validation."""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
    
    def add_error(self, error):
        """Add an error and mark as invalid."""
        self.errors.append(error)
        self.is_valid = False

class PasswordValidator:
    """Password validator built using TDD."""
    
    def validate(self, password):
        """Validate password according to rules."""
        result = ValidationResult()
        
        # Rule 1: Minimum length (first implementation)
        if len(password) < 8:
            result.add_error("Password must be at least 8 characters long")
        
        return result

# Step 3: RED - Add more tests
class TestPasswordValidatorExpanded(unittest.TestCase):
    """Expanded tests for password validator."""
    
    def setUp(self):
        self.validator = PasswordValidator()
    
    # Previous tests still here...
    def test_password_too_short_fails(self):
        result = self.validator.validate("short")
        self.assertFalse(result.is_valid)
        self.assertIn("at least 8 characters", result.errors)
    
    # Test 2: Must contain uppercase letter
    def test_password_no_uppercase_fails(self):
        """RED: Password must contain uppercase letter."""
        result = self.validator.validate("lowercase123")
        self.assertFalse(result.is_valid)
        self.assertIn("uppercase letter", result.errors)
    
    def test_password_with_uppercase_passes_case_requirement(self):
        """Password with uppercase should pass case requirement."""
        result = self.validator.validate("Uppercase123")
        self.assertNotIn("uppercase letter", result.errors)
    
    # Test 3: Must contain lowercase letter
    def test_password_no_lowercase_fails(self):
        """RED: Password must contain lowercase letter."""
        result = self.validator.validate("UPPERCASE123")
        self.assertFalse(result.is_valid)
        self.assertIn("lowercase letter", result.errors)
    
    # Test 4: Must contain number
    def test_password_no_number_fails(self):
        """RED: Password must contain a number."""
        result = self.validator.validate("PasswordOnly")
        self.assertFalse(result.is_valid)
        self.assertIn("number", result.errors)
    
    # Test 5: Valid password passes all checks
    def test_valid_password_passes(self):
        """GREEN: Valid password should pass all checks."""
        result = self.validator.validate("ValidPass123")
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

# Step 4: GREEN - Expand implementation
class PasswordValidatorExpanded:
    """Expanded password validator with more rules."""
    
    def validate(self, password):
        """Validate password according to all rules."""
        result = ValidationResult()
        
        # Rule 1: Minimum length
        if len(password) < 8:
            result.add_error("Password must be at least 8 characters long")
        
        # Rule 2: Must contain uppercase letter
        if not re.search(r'[A-Z]', password):
            result.add_error("Password must contain at least one uppercase letter")
        
        # Rule 3: Must contain lowercase letter
        if not re.search(r'[a-z]', password):
            result.add_error("Password must contain at least one lowercase letter")
        
        # Rule 4: Must contain number
        if not re.search(r'\\d', password):
            result.add_error("Password must contain at least one number")
        
        return result

# Step 5: REFACTOR - Clean up the implementation
class PasswordValidatorRefactored:
    """Refactored password validator with clean separation of rules."""
    
    def __init__(self):
        self.rules = [
            self._check_length,
            self._check_uppercase,
            self._check_lowercase,
            self._check_number,
        ]
    
    def validate(self, password):
        """Validate password using all rules."""
        result = ValidationResult()
        
        for rule in self.rules:
            rule(password, result)
        
        return result
    
    def _check_length(self, password, result):
        """Check minimum length requirement."""
        if len(password) < 8:
            result.add_error("Password must be at least 8 characters long")
    
    def _check_uppercase(self, password, result):
        """Check uppercase letter requirement."""
        if not re.search(r'[A-Z]', password):
            result.add_error("Password must contain at least one uppercase letter")
    
    def _check_lowercase(self, password, result):
        """Check lowercase letter requirement."""
        if not re.search(r'[a-z]', password):
            result.add_error("Password must contain at least one lowercase letter")
    
    def _check_number(self, password, result):
        """Check number requirement."""
        if not re.search(r'\\d', password):
            result.add_error("Password must contain at least one number")

# Demonstration of TDD cycle
def demonstrate_tdd_cycle():
    """Demonstrate the TDD Red-Green-Refactor cycle."""
    print("=== TDD Cycle Demonstration ===")
    print()
    
    # Test the final refactored validator
    validator = PasswordValidatorRefactored()
    
    test_cases = [
        "short",           # Too short
        "toolongbutnocase", # No uppercase/numbers
        "TOOLONGBUTNOCASE", # No lowercase/numbers
        "ValidButNoNumber", # No numbers
        "ValidPass123",     # Valid password
    ]
    
    for password in test_cases:
        result = validator.validate(password)
        print(f"Password: '{password}'")
        print(f"Valid: {result.is_valid}")
        if result.errors:
            print(f"Errors: {', '.join(result.errors)}")
        print()

if __name__ == '__main__':
    demonstrate_tdd_cycle()
    
    # Run the tests
    print("\\n=== Running TDD Tests ===")
    unittest.main(verbosity=2, exit=False)
''',
            "explanation": "Complete TDD cycle demonstration showing Red-Green-Refactor with a password validator"
        },
        
        "tdd_best_practices": {
            "code": '''
"""
TDD Best Practices and Patterns
Demonstrates proper TDD techniques and common patterns.
"""

import unittest
from typing import List, Optional

# Example: Building a Shopping Cart with TDD
class ShoppingCart:
    """Shopping cart built using TDD principles."""
    
    def __init__(self):
        self.items = []
        self.discounts = []
    
    def add_item(self, item_name: str, price: float, quantity: int = 1):
        """Add item to cart."""
        if not item_name.strip():
            raise ValueError("Item name cannot be empty")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Check if item already exists
        for item in self.items:
            if item['name'] == item_name and item['price'] == price:
                item['quantity'] += quantity
                return
        
        # Add new item
        self.items.append({
            'name': item_name,
            'price': price,
            'quantity': quantity
        })
    
    def remove_item(self, item_name: str, quantity: int = None):
        """Remove item from cart."""
        for i, item in enumerate(self.items):
            if item['name'] == item_name:
                if quantity is None or quantity >= item['quantity']:
                    # Remove entire item
                    self.items.pop(i)
                else:
                    # Reduce quantity
                    item['quantity'] -= quantity
                return True
        return False
    
    def get_total(self) -> float:
        """Calculate total cart value."""
        subtotal = sum(item['price'] * item['quantity'] for item in self.items)
        
        # Apply discounts
        total_discount = sum(discount['amount'] for discount in self.discounts)
        
        return max(0, subtotal - total_discount)
    
    def apply_discount(self, discount_name: str, amount: float):
        """Apply discount to cart."""
        if amount < 0:
            raise ValueError("Discount amount cannot be negative")
        
        self.discounts.append({
            'name': discount_name,
            'amount': amount
        })
    
    def get_item_count(self) -> int:
        """Get total number of items in cart."""
        return sum(item['quantity'] for item in self.items)
    
    def is_empty(self) -> bool:
        """Check if cart is empty."""
        return len(self.items) == 0

class TestShoppingCartTDD(unittest.TestCase):
    """TDD tests for shopping cart - demonstrating best practices."""
    
    def setUp(self):
        """Arrange: Set up fresh cart for each test."""
        self.cart = ShoppingCart()
    
    # Test 1: Empty cart behavior
    def test_new_cart_is_empty(self):
        """Test that new cart starts empty."""
        # Act & Assert
        self.assertTrue(self.cart.is_empty())
        self.assertEqual(self.cart.get_total(), 0.0)
        self.assertEqual(self.cart.get_item_count(), 0)
    
    # Test 2: Adding single item
    def test_add_single_item(self):
        """Test adding a single item to cart."""
        # Act
        self.cart.add_item("Apple", 1.50)
        
        # Assert
        self.assertFalse(self.cart.is_empty())
        self.assertEqual(self.cart.get_item_count(), 1)
        self.assertEqual(self.cart.get_total(), 1.50)
    
    # Test 3: Adding multiple quantities
    def test_add_item_with_quantity(self):
        """Test adding item with specific quantity."""
        # Act
        self.cart.add_item("Apple", 1.50, 3)
        
        # Assert
        self.assertEqual(self.cart.get_item_count(), 3)
        self.assertEqual(self.cart.get_total(), 4.50)
    
    # Test 4: Adding same item twice (should combine)
    def test_add_same_item_twice_combines_quantity(self):
        """Test that adding same item twice combines quantities."""
        # Act
        self.cart.add_item("Apple", 1.50, 2)
        self.cart.add_item("Apple", 1.50, 3)
        
        # Assert
        self.assertEqual(self.cart.get_item_count(), 5)
        self.assertEqual(len(self.cart.items), 1)  # Only one item type
    
    # Test 5: Error conditions
    def test_add_item_validation(self):
        """Test validation when adding items."""
        # Test empty name
        with self.assertRaises(ValueError):
            self.cart.add_item("", 1.50)
        
        # Test negative price
        with self.assertRaises(ValueError):
            self.cart.add_item("Apple", -1.50)
        
        # Test zero quantity
        with self.assertRaises(ValueError):
            self.cart.add_item("Apple", 1.50, 0)
    
    # Test 6: Removing items
    def test_remove_item_completely(self):
        """Test removing item completely."""
        # Arrange
        self.cart.add_item("Apple", 1.50, 3)
        
        # Act
        result = self.cart.remove_item("Apple")
        
        # Assert
        self.assertTrue(result)
        self.assertTrue(self.cart.is_empty())
    
    def test_remove_item_partially(self):
        """Test removing partial quantity of item."""
        # Arrange
        self.cart.add_item("Apple", 1.50, 5)
        
        # Act
        result = self.cart.remove_item("Apple", 2)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(self.cart.get_item_count(), 3)
    
    def test_remove_nonexistent_item(self):
        """Test removing item that doesn't exist."""
        # Act
        result = self.cart.remove_item("Banana")
        
        # Assert
        self.assertFalse(result)
        self.assertTrue(self.cart.is_empty())
    
    # Test 7: Discounts
    def test_apply_discount(self):
        """Test applying discount to cart."""
        # Arrange
        self.cart.add_item("Apple", 1.50, 2)  # $3.00 total
        
        # Act
        self.cart.apply_discount("Student Discount", 0.50)
        
        # Assert
        self.assertEqual(self.cart.get_total(), 2.50)
    
    def test_discount_cannot_make_total_negative(self):
        """Test that discounts don't make total negative."""
        # Arrange
        self.cart.add_item("Apple", 1.50)
        
        # Act
        self.cart.apply_discount("Large Discount", 5.00)
        
        # Assert
        self.assertEqual(self.cart.get_total(), 0.0)  # Not negative
    
    # Test 8: Complex scenarios
    def test_complex_cart_scenario(self):
        """Test complex cart operations."""
        # Arrange & Act
        self.cart.add_item("Apple", 1.50, 3)    # $4.50
        self.cart.add_item("Banana", 0.75, 4)   # $3.00
        self.cart.add_item("Orange", 2.00, 1)   # $2.00
        # Total: $9.50
        
        self.cart.apply_discount("10% Off", 0.95)  # $8.55
        self.cart.remove_item("Banana", 2)         # Remove 2 bananas ($7.05)
        
        # Assert
        expected_total = (1.50 * 3) + (0.75 * 2) + (2.00 * 1) - 0.95
        self.assertAlmostEqual(self.cart.get_total(), expected_total, places=2)
        self.assertEqual(self.cart.get_item_count(), 6)  # 3 + 2 + 1

# TDD Best Practices Demonstration
class TDDBestPracticesDemo:
    """Demonstrates TDD best practices."""
    
    @staticmethod
    def demonstrate_arrange_act_assert():
        """Show the Arrange-Act-Assert pattern."""
        print("=== Arrange-Act-Assert Pattern ===")
        print("Each test should follow this structure:")
        print("1. Arrange: Set up test data and conditions")
        print("2. Act: Execute the method being tested")
        print("3. Assert: Verify the results")
        print()
    
    @staticmethod
    def demonstrate_test_naming():
        """Show good test naming conventions."""
        print("=== Test Naming Best Practices ===")
        print("Good test names:")
        print("- test_add_item_with_valid_data_succeeds")
        print("- test_remove_nonexistent_item_returns_false")
        print("- test_apply_negative_discount_raises_exception")
        print()
        print("Bad test names:")
        print("- test_add")
        print("- test_cart")
        print("- test_method1")
        print()
    
    @staticmethod
    def demonstrate_one_assertion_per_test():
        """Show why one logical assertion per test is good."""
        print("=== One Assertion Per Test ===")
        print("Each test should verify one specific behavior.")
        print("This makes tests easier to understand and debug.")
        print("Use helper methods to reduce duplication.")
        print()

if __name__ == '__main__':
    # Demonstrate best practices
    demo = TDDBestPracticesDemo()
    demo.demonstrate_arrange_act_assert()
    demo.demonstrate_test_naming()
    demo.demonstrate_one_assertion_per_test()
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
''',
            "explanation": "TDD best practices including proper test structure, naming conventions, and incremental development"
        }
    }