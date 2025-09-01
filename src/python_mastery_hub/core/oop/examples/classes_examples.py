"""
Classes and Objects examples for the OOP module.
Demonstrates fundamental class definition, instantiation, and object usage.
"""

from typing import Dict, Any


def get_classes_examples() -> Dict[str, Any]:
    """Get comprehensive class and object examples."""
    return {
        "basic_class_definition": {
            "code": """
# Basic class definition and instantiation
class Student:
    '''A class representing a student.'''
    
    # Class variable (shared by all instances)
    school_name = "Python Mastery University"
    
    def __init__(self, name, age, student_id):
        # Instance variables (unique to each instance)
        self.name = name
        self.age = age
        self.student_id = student_id
        self.grades = []
    
    def add_grade(self, subject, grade):
        '''Add a grade for a subject.'''
        self.grades.append({'subject': subject, 'grade': grade})
    
    def get_average_grade(self):
        '''Calculate average grade.'''
        if not self.grades:
            return 0
        total = sum(grade['grade'] for grade in self.grades)
        return round(total / len(self.grades), 2)
    
    def __str__(self):
        '''String representation of the student.'''
        return f"Student({self.name}, ID: {self.student_id})"
    
    def __repr__(self):
        '''Developer representation of the student.'''
        return f"Student(name='{self.name}', age={self.age}, student_id='{self.student_id}')"

# Create instances
alice = Student("Alice Johnson", 20, "S001")
bob = Student("Bob Smith", 19, "S002")

# Add grades
alice.add_grade("Math", 95)
alice.add_grade("Physics", 88)
alice.add_grade("Chemistry", 92)

bob.add_grade("Math", 87)
bob.add_grade("Physics", 91)

print(f"Alice: {alice}")
print(f"Alice's average: {alice.get_average_grade()}")
print(f"Bob: {bob}")
print(f"Bob's average: {bob.get_average_grade()}")
print(f"School: {Student.school_name}")
""",
            "output": "Alice: Student(Alice Johnson, ID: S001)\nAlice's average: 91.67\nBob: Student(Bob Smith, ID: S002)\nBob's average: 89.0\nSchool: Python Mastery University",
            "explanation": "Classes define blueprints for objects with attributes and methods"
        },
        
        "class_methods_and_static_methods": {
            "code": """
from datetime import datetime

class BankAccount:
    '''A bank account class demonstrating different method types.'''
    
    # Class variable
    bank_name = "Python Bank"
    interest_rate = 0.05
    
    def __init__(self, account_number, owner, initial_balance=0):
        self.account_number = account_number
        self.owner = owner
        self.balance = initial_balance
        self.transactions = []
    
    # Instance method
    def deposit(self, amount):
        '''Deposit money to the account.'''
        if amount > 0:
            self.balance += amount
            self.transactions.append(f"Deposited ${amount}")
            return self.balance
        raise ValueError("Deposit amount must be positive")
    
    def withdraw(self, amount):
        '''Withdraw money from the account.'''
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.transactions.append(f"Withdrew ${amount}")
        return self.balance
    
    # Class method - works with the class, not instance
    @classmethod
    def create_savings_account(cls, account_number, owner, initial_deposit):
        '''Factory method to create a savings account.'''
        account = cls(account_number, owner, initial_deposit)
        account.account_type = "Savings"
        account.transactions.append("Account created as Savings")
        return account
    
    @classmethod
    def set_interest_rate(cls, new_rate):
        '''Update interest rate for all accounts.'''
        cls.interest_rate = new_rate
    
    # Static method - doesn't access class or instance
    @staticmethod
    def validate_account_number(account_number):
        '''Validate account number format.'''
        return len(account_number) == 10 and account_number.isdigit()
    
    @staticmethod
    def calculate_compound_interest(principal, rate, time):
        '''Calculate compound interest.'''
        return principal * ((1 + rate) ** time)
    
    def __str__(self):
        return f"Account {self.account_number} - {self.owner}: ${self.balance}"

# Usage examples
print("=== Instance Methods ===")
account1 = BankAccount("1234567890", "Alice", 1000)
print(account1)
account1.deposit(500)
print(f"After deposit: {account1}")

print("\\n=== Class Methods ===")
savings = BankAccount.create_savings_account("9876543210", "Bob", 2000)
print(f"Savings account: {savings}")
print(f"Account type: {getattr(savings, 'account_type', 'Standard')}")

print("\\n=== Static Methods ===")
print(f"Valid account number: {BankAccount.validate_account_number('1234567890')}")
print(f"Invalid account number: {BankAccount.validate_account_number('123')}")
interest = BankAccount.calculate_compound_interest(1000, 0.05, 5)
print(f"Compound interest: ${interest:.2f}")
""",
            "output": "=== Instance Methods ===\nAccount 1234567890 - Alice: $1000\nAfter deposit: Account 1234567890 - Alice: $1500\n\n=== Class Methods ===\nSavings account: Account 9876543210 - Bob: $2000\nAccount type: Savings\n\n=== Static Methods ===\nValid account number: True\nInvalid account number: False\nCompound interest: $1276.28",
            "explanation": "Different method types serve different purposes: instance methods for object operations, class methods for class-level operations, static methods for utility functions"
        },
        
        "property_decorators": {
            "code": """
class Temperature:
    '''Temperature class demonstrating property decorators.'''
    
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        '''Get temperature in Celsius.'''
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        '''Set temperature in Celsius with validation.'''
        if value < -273.15:
            raise ValueError("Temperature cannot be below absolute zero")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        '''Get temperature in Fahrenheit.'''
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        '''Set temperature using Fahrenheit.'''
        self.celsius = (value - 32) * 5/9
    
    @property
    def kelvin(self):
        '''Get temperature in Kelvin.'''
        return self._celsius + 273.15
    
    @kelvin.setter
    def kelvin(self, value):
        '''Set temperature using Kelvin.'''
        self.celsius = value - 273.15
    
    def __str__(self):
        return f"{self._celsius}°C ({self.fahrenheit}°F, {self.kelvin}K)"

# Usage examples
temp = Temperature(25)
print(f"Initial: {temp}")

# Using property setters
temp.fahrenheit = 86
print(f"Set to 86°F: {temp}")

temp.kelvin = 300
print(f"Set to 300K: {temp}")

# Property validation
try:
    temp.celsius = -300  # Below absolute zero
except ValueError as e:
    print(f"Error: {e}")

# Properties work like attributes
print(f"Current Celsius: {temp.celsius}")
print(f"Current Fahrenheit: {temp.fahrenheit}")
print(f"Current Kelvin: {temp.kelvin}")
""",
            "output": "Initial: 25°C (77.0°F, 298.15K)\nSet to 86°F: 30.0°C (86.0°F, 303.15K)\nSet to 300K: 26.85°C (80.33°F, 300.0K)\nError: Temperature cannot be below absolute zero\nCurrent Celsius: 26.85\nCurrent Fahrenheit: 80.33\nCurrent Kelvin: 300.0",
            "explanation": "Property decorators provide controlled access to attributes with validation and computed properties"
        },
        
        "data_classes": {
            "code": """
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

@dataclass
class Product:
    '''Product using dataclass for automatic method generation.'''
    name: str
    price: float
    category: str
    in_stock: bool = True
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        '''Called after __init__ to perform additional setup.'''
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        
        # Auto-generate tags if none provided
        if not self.tags:
            self.tags = [self.category.lower(), 'new-product']
    
    def apply_discount(self, percentage: float) -> float:
        '''Apply discount and return new price.'''
        if 0 <= percentage <= 100:
            discount_amount = self.price * (percentage / 100)
            self.price -= discount_amount
            return self.price
        raise ValueError("Discount percentage must be between 0 and 100")
    
    @property
    def is_expensive(self) -> bool:
        '''Check if product is expensive (over $100).'''
        return self.price > 100

@dataclass
class ShoppingCart:
    '''Shopping cart using dataclass.'''
    customer_name: str
    items: List[Product] = field(default_factory=list)
    discount_code: str = ""
    
    def add_item(self, product: Product, quantity: int = 1):
        '''Add product to cart.'''
        for _ in range(quantity):
            self.items.append(product)
    
    def remove_item(self, product_name: str) -> bool:
        '''Remove first instance of product by name.'''
        for item in self.items:
            if item.name == product_name:
                self.items.remove(item)
                return True
        return False
    
    @property
    def total_cost(self) -> float:
        '''Calculate total cost of items in cart.'''
        return sum(item.price for item in self.items)
    
    @property
    def item_count(self) -> int:
        '''Get total number of items.'''
        return len(self.items)

# Usage examples
print("=== DataClass Examples ===")

# Create products
laptop = Product("Gaming Laptop", 1299.99, "Electronics")
book = Product("Python Guide", 29.99, "Books", tags=["programming", "education"])
headphones = Product("Wireless Headphones", 199.99, "Electronics")

print(f"Laptop: {laptop}")
print(f"Book: {book}")
print(f"Is laptop expensive? {laptop.is_expensive}")

# Apply discount
laptop.apply_discount(10)  # 10% off
print(f"Laptop after 10% discount: {laptop.price}")

# Create shopping cart
cart = ShoppingCart("Alice")
cart.add_item(laptop)
cart.add_item(book, quantity=2)
cart.add_item(headphones)

print(f"\\nCart for {cart.customer_name}:")
print(f"Items: {cart.item_count}")
print(f"Total cost: ${cart.total_cost:.2f}")

# Remove item
cart.remove_item("Python Guide")
print(f"After removing book - Items: {cart.item_count}, Cost: ${cart.total_cost:.2f}")
""",
            "output": "=== DataClass Examples ===\nLaptop: Product(name='Gaming Laptop', price=1299.99, category='Electronics', in_stock=True, tags=['electronics', 'new-product'], created_at=datetime.datetime(2024, 1, 1, 12, 0, 0))\nBook: Product(name='Python Guide', price=29.99, category='Books', in_stock=True, tags=['programming', 'education'], created_at=datetime.datetime(2024, 1, 1, 12, 0, 0))\nIs laptop expensive? True\nLaptop after 10% discount: 1169.991\n\nCart for Alice:\nItems: 4\nTotal cost: $1429.97\nAfter removing book - Items: 3, Cost: $1399.98",
            "explanation": "DataClasses automatically generate common methods like __init__, __str__, and __repr__, reducing boilerplate code"
        }
    }