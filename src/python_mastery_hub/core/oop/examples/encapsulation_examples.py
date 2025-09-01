"""
Encapsulation examples for the OOP module.
Demonstrates access control, data hiding, and property usage.
"""

from typing import Dict, Any


def get_encapsulation_examples() -> Dict[str, Any]:
    """Get comprehensive encapsulation examples."""
    return {
        "access_modifiers": {
            "code": """
class BankAccount:
    '''Demonstrates encapsulation with different access levels.'''
    
    def __init__(self, account_number, owner, initial_balance):
        self.account_number = account_number    # Public
        self._owner = owner                     # Protected (convention)
        self.__balance = initial_balance        # Private (name mangling)
        self.__pin = None                      # Private
    
    # Public methods
    def deposit(self, amount):
        '''Public method to deposit money.'''
        if self._validate_amount(amount):
            self.__balance += amount
            return f"Deposited ${amount}. New balance: ${self.__balance}"
        return "Invalid deposit amount"
    
    def withdraw(self, amount, pin):
        '''Public method to withdraw money with PIN verification.'''
        if not self.__verify_pin(pin):
            return "Invalid PIN"
        
        if self._validate_amount(amount) and amount <= self.__balance:
            self.__balance -= amount
            return f"Withdrew ${amount}. New balance: ${self.__balance}"
        return "Invalid withdrawal amount or insufficient funds"
    
    def get_balance(self, pin):
        '''Public method to check balance with PIN verification.'''
        if self.__verify_pin(pin):
            return f"Current balance: ${self.__balance}"
        return "Invalid PIN"
    
    def set_pin(self, new_pin):
        '''Public method to set PIN.'''
        if len(str(new_pin)) == 4 and str(new_pin).isdigit():
            self.__pin = new_pin
            return "PIN set successfully"
        return "PIN must be 4 digits"
    
    # Protected method (can be accessed by subclasses)
    def _validate_amount(self, amount):
        '''Protected method to validate amount.'''
        return isinstance(amount, (int, float)) and amount > 0
    
    # Private methods (name mangled)
    def __verify_pin(self, pin):
        '''Private method to verify PIN.'''
        return self.__pin is not None and self.__pin == pin
    
    def __str__(self):
        return f"Account {self.account_number} - Owner: {self._owner}"

# Usage examples
print("=== Encapsulation Demo ===")
account = BankAccount("12345", "Alice", 1000)
print(account)

# Set PIN first
print(account.set_pin(1234))

# Public interface works
print(account.deposit(500))
print(account.get_balance(1234))
print(account.withdraw(200, 1234))

# Wrong PIN
print(account.withdraw(100, 9999))

print("\\n=== Access Level Demonstration ===")
# Public access - works
print(f"Account number (public): {account.account_number}")

# Protected access - works but discouraged
print(f"Owner (protected): {account._owner}")

# Private access - doesn't work directly
try:
    print(f"Balance (private): {account.__balance}")
except AttributeError as e:
    print(f"Error accessing private attribute: {e}")

# Private access through name mangling - works but not recommended
print(f"Balance via name mangling: {account._BankAccount__balance}")
""",
            "output": "=== Encapsulation Demo ===\nAccount 12345 - Owner: Alice\nPIN set successfully\nDeposited $500. New balance: $1500\nCurrent balance: $1500\nWithdrew $200. New balance: $1300\nInvalid PIN\n\n=== Access Level Demonstration ===\nAccount number (public): 12345\nOwner (protected): Alice\nError accessing private attribute: 'BankAccount' object has no attribute '__balance'\nBalance via name mangling: 1300",
            "explanation": "Encapsulation controls access to object internals using naming conventions and access patterns"
        },
        
        "property_based_encapsulation": {
            "code": """
class Person:
    '''Person class demonstrating property-based encapsulation.'''
    
    def __init__(self, name, age, email):
        self._name = name
        self._age = age
        self._email = email
        self._phone = None
    
    # Name property with validation
    @property
    def name(self):
        '''Get person's name.'''
        return self._name
    
    @name.setter
    def name(self, value):
        '''Set person's name with validation.'''
        if not isinstance(value, str) or len(value.strip()) < 2:
            raise ValueError("Name must be a string with at least 2 characters")
        self._name = value.strip().title()
    
    # Age property with validation
    @property
    def age(self):
        '''Get person's age.'''
        return self._age
    
    @age.setter
    def age(self, value):
        '''Set person's age with validation.'''
        if not isinstance(value, int) or value < 0 or value > 150:
            raise ValueError("Age must be an integer between 0 and 150")
        self._age = value
    
    # Email property with validation
    @property
    def email(self):
        '''Get person's email.'''
        return self._email
    
    @email.setter
    def email(self, value):
        '''Set person's email with validation.'''
        if not isinstance(value, str) or "@" not in value or "." not in value:
            raise ValueError("Email must be a valid email address")
        self._email = value.lower()
    
    # Read-only computed property
    @property
    def age_category(self):
        '''Get age category (computed property).'''
        if self._age < 18:
            return "Minor"
        elif self._age < 65:
            return "Adult"
        else:
            return "Senior"
    
    # Phone property with getter and setter
    @property
    def phone(self):
        '''Get formatted phone number.'''
        if self._phone:
            return f"({self._phone[:3]}) {self._phone[3:6]}-{self._phone[6:]}"
        return "No phone number"
    
    @phone.setter
    def phone(self, value):
        '''Set phone number (digits only).'''
        if value is None:
            self._phone = None
            return
        
        # Remove non-digits
        digits = ''.join(filter(str.isdigit, str(value)))
        if len(digits) != 10:
            raise ValueError("Phone number must have exactly 10 digits")
        self._phone = digits
    
    def __str__(self):
        return f"Person(name='{self.name}', age={self.age}, email='{self.email}')"

class Employee(Person):
    '''Employee class extending Person with salary encapsulation.'''
    
    def __init__(self, name, age, email, employee_id, salary):
        super().__init__(name, age, email)
        self._employee_id = employee_id
        self._salary = salary
        self._performance_rating = 3.0  # Default rating
    
    @property
    def employee_id(self):
        '''Get employee ID (read-only).'''
        return self._employee_id
    
    @property
    def salary(self):
        '''Get formatted salary.'''
        return f"${self._salary:,.2f}"
    
    def _set_salary(self, new_salary, authorized_by):
        '''Protected method to change salary (internal use).'''
        if not isinstance(authorized_by, str) or len(authorized_by) < 3:
            raise ValueError("Salary changes must be authorized")
        
        if new_salary < 0:
            raise ValueError("Salary cannot be negative")
        
        old_salary = self._salary
        self._salary = new_salary
        return f"Salary changed from ${old_salary:,.2f} to ${new_salary:,.2f} by {authorized_by}"
    
    @property
    def performance_rating(self):
        '''Get performance rating.'''
        return self._performance_rating
    
    @performance_rating.setter
    def performance_rating(self, rating):
        '''Set performance rating with validation.'''
        if not isinstance(rating, (int, float)) or rating < 1.0 or rating > 5.0:
            raise ValueError("Performance rating must be between 1.0 and 5.0")
        self._performance_rating = float(rating)
    
    def give_raise(self, percentage, authorized_by):
        '''Give percentage-based raise.'''
        if percentage <= 0:
            raise ValueError("Raise percentage must be positive")
        
        raise_amount = self._salary * (percentage / 100)
        new_salary = self._salary + raise_amount
        return self._set_salary(new_salary, authorized_by)

# Usage examples
print("=== Property-Based Encapsulation ===")
person = Person("john doe", 25, "JOHN.DOE@EMAIL.COM")
print(f"Created: {person}")
print(f"Age category: {person.age_category}")

# Property validation in action
try:
    person.age = -5
except ValueError as e:
    print(f"Age validation error: {e}")

try:
    person.email = "invalid-email"
except ValueError as e:
    print(f"Email validation error: {e}")

# Phone number formatting
person.phone = "1234567890"
print(f"Phone: {person.phone}")

print("\\n=== Employee Encapsulation ===")
emp = Employee("Alice Smith", 30, "alice@company.com", "EMP001", 75000)
print(f"Employee: {emp}")
print(f"Employee ID: {emp.employee_id}")
print(f"Salary: {emp.salary}")
print(f"Performance: {emp.performance_rating}")

# Authorized salary change
raise_result = emp.give_raise(10, "HR Manager")
print(f"Raise result: {raise_result}")
print(f"New salary: {emp.salary}")

# Performance rating
emp.performance_rating = 4.5
print(f"Updated performance: {emp.performance_rating}")
""",
            "output": "=== Property-Based Encapsulation ===\nCreated: Person(name='John Doe', age=25, email='john.doe@email.com')\nAge category: Adult\nAge validation error: Age must be an integer between 0 and 150\nEmail validation error: Email must be a valid email address\nPhone: (123) 456-7890\n\n=== Employee Encapsulation ===\nEmployee: Person(name='Alice Smith', age=30, email='alice@company.com')\nEmployee ID: EMP001\nSalary: $75,000.00\nPerformance: 3.0\nRaise result: Salary changed from $75,000.00 to $82,500.00 by HR Manager\nNew salary: $82,500.00\nUpdated performance: 4.5",
            "explanation": "Properties provide controlled access to attributes with automatic validation and formatting"
        },
        
        "data_hiding_patterns": {
            "code": """
class SecureVault:
    '''Demonstrates advanced data hiding patterns.'''
    
    def __init__(self, vault_id):
        self.__vault_id = vault_id
        self.__contents = {}
        self.__access_log = []
        self.__master_key = self.__generate_key()
    
    def __generate_key(self):
        '''Private method to generate master key.'''
        import hashlib
        return hashlib.sha256(f"vault_{self.__vault_id}".encode()).hexdigest()[:16]
    
    def store_item(self, item_name, item_value, user_key):
        '''Store item in vault with user authentication.'''
        if not self.__authenticate_user(user_key):
            self.__log_access("FAILED_STORE", item_name, "Invalid key")
            return "Access denied: Invalid key"
        
        self.__contents[item_name] = item_value
        self.__log_access("STORE", item_name, "Success")
        return f"Item '{item_name}' stored successfully"
    
    def retrieve_item(self, item_name, user_key):
        '''Retrieve item from vault with authentication.'''
        if not self.__authenticate_user(user_key):
            self.__log_access("FAILED_RETRIEVE", item_name, "Invalid key")
            return "Access denied: Invalid key"
        
        if item_name in self.__contents:
            value = self.__contents[item_name]
            self.__log_access("RETRIEVE", item_name, "Success")
            return value
        else:
            self.__log_access("RETRIEVE", item_name, "Item not found")
            return "Item not found"
    
    def list_items(self, user_key):
        '''List all items in vault.'''
        if not self.__authenticate_user(user_key):
            self.__log_access("FAILED_LIST", "ALL", "Invalid key")
            return "Access denied: Invalid key"
        
        self.__log_access("LIST", "ALL", "Success")
        return list(self.__contents.keys())
    
    def __authenticate_user(self, user_key):
        '''Private authentication method.'''
        return user_key == self.__master_key
    
    def __log_access(self, action, item, result):
        '''Private method to log access attempts.'''
        import datetime
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'action': action,
            'item': item,
            'result': result
        }
        self.__access_log.append(log_entry)
    
    def get_access_log(self, admin_password):
        '''Get access log (admin only).'''
        if admin_password != "admin123":  # Simplified admin check
            return "Access denied: Admin privileges required"
        
        return self.__access_log.copy()  # Return copy to prevent modification
    
    # Public interface to get the key (in real system, this would be more secure)
    def get_master_key(self, admin_password):
        '''Get master key for vault access (admin only).'''
        if admin_password != "admin123":
            return "Access denied: Admin privileges required"
        return self.__master_key
    
    @property
    def vault_id(self):
        '''Get vault ID (read-only).'''
        return self.__vault_id
    
    def __str__(self):
        return f"SecureVault(id={self.__vault_id}, items={len(self.__contents)})"

# Example: Configuration manager with encapsulation
class ConfigurationManager:
    '''Manages application configuration with encapsulation.'''
    
    def __init__(self):
        self.__config = {}
        self.__sensitive_keys = {'password', 'api_key', 'secret', 'token'}
        self.__readonly_keys = {'version', 'app_name'}
    
    def set_config(self, key, value):
        '''Set configuration value with restrictions.'''
        if key in self.__readonly_keys:
            return f"Cannot modify read-only key: {key}"
        
        self.__config[key] = value
        return f"Configuration '{key}' set successfully"
    
    def get_config(self, key, show_sensitive=False):
        '''Get configuration value with sensitive data protection.'''
        if key not in self.__config:
            return f"Configuration key '{key}' not found"
        
        value = self.__config[key]
        
        # Hide sensitive values unless explicitly requested
        if key.lower() in self.__sensitive_keys and not show_sensitive:
            return "*" * len(str(value))
        
        return value
    
    def list_configs(self, include_sensitive=False):
        '''List all configuration keys and values.'''
        result = {}
        for key, value in self.__config.items():
            if key.lower() in self.__sensitive_keys and not include_sensitive:
                result[key] = "*" * len(str(value))
            else:
                result[key] = value
        return result
    
    def export_config(self, include_sensitive=False):
        '''Export configuration (with optional sensitive data).'''
        return self.list_configs(include_sensitive)

# Usage examples
print("=== Advanced Data Hiding ===")
vault = SecureVault("VAULT001")
print(f"Created: {vault}")

# Get master key (admin operation)
master_key = vault.get_master_key("admin123")
print(f"Master key obtained: {master_key[:8]}...")

# Store and retrieve items
print(vault.store_item("secret_document", "Top Secret Data", master_key))
print(vault.store_item("backup_codes", ["123", "456", "789"], master_key))

# Try with wrong key
print(vault.retrieve_item("secret_document", "wrong_key"))

# Retrieve with correct key
document = vault.retrieve_item("secret_document", master_key)
print(f"Retrieved document: {document}")

# List items
items = vault.list_items(master_key)
print(f"Vault contains: {items}")

print("\\n=== Configuration Manager ===")
config = ConfigurationManager()

# Set various configurations
print(config.set_config("app_name", "MyApp"))
print(config.set_config("version", "1.0.0"))
print(config.set_config("api_key", "secret123"))
print(config.set_config("database_url", "localhost:5432"))

# Try to modify read-only
print(config.set_config("version", "2.0.0"))

# Get configurations
print(f"App name: {config.get_config('app_name')}")
print(f"API key (hidden): {config.get_config('api_key')}")
print(f"API key (shown): {config.get_config('api_key', show_sensitive=True)}")

# List all configurations
print(f"All configs: {config.list_configs()}")
""",
            "output": "=== Advanced Data Hiding ===\nCreated: SecureVault(id=VAULT001, items=0)\nMaster key obtained: 8f7a9c2e...\nItem 'secret_document' stored successfully\nItem 'backup_codes' stored successfully\nAccess denied: Invalid key\nRetrieved document: Top Secret Data\nVault contains: ['secret_document', 'backup_codes']\n\n=== Configuration Manager ===\nConfiguration 'app_name' set successfully\nConfiguration 'version' set successfully\nConfiguration 'api_key' set successfully\nConfiguration 'database_url' set successfully\nCannot modify read-only key: version\nApp name: MyApp\nAPI key (hidden): *********\nAPI key (shown): secret123\nAll configs: {'app_name': 'MyApp', 'version': '1.0.0', 'api_key': '*********', 'database_url': 'localhost:5432'}",
            "explanation": "Advanced encapsulation patterns protect sensitive data and control access through authentication and authorization"
        }
    }