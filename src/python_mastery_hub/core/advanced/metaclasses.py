"""
Metaclass examples and demonstrations for the Advanced Python module.
"""

from typing import Dict, List, Any, Type
from .base import TopicDemo


class MetaclassesDemo(TopicDemo):
    """Demonstration class for Python metaclasses."""
    
    def __init__(self):
        super().__init__("metaclasses")
    
    def _setup_examples(self) -> None:
        """Setup metaclass examples."""
        self.examples = {
            "basic_metaclasses": {
                "code": '''
class SingletonMeta(type):
    """Metaclass that implements the Singleton pattern."""
    
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ValidatedMeta(type):
    """Metaclass that adds validation to class attributes."""
    
    def __new__(mcs, name, bases, attrs):
        # Add validation for attributes ending with '_validated'
        validated_attrs = {k: v for k, v in attrs.items() if k.endswith('_validated')}
        
        if validated_attrs:
            original_setattr = attrs.get('__setattr__', lambda self, k, v: object.__setattr__(self, k, v))
            
            def validated_setattr(self, key, value):
                if key in validated_attrs:
                    validator = validated_attrs[key]
                    if callable(validator) and not validator(value):
                        raise ValueError(f"Invalid value for {key}: {value}")
                return original_setattr(self, key, value)
            
            attrs['__setattr__'] = validated_setattr
        
        return super().__new__(mcs, name, bases, attrs)

class AutoPropertyMeta(type):
    """Metaclass that automatically creates properties for private attributes."""
    
    def __new__(mcs, name, bases, attrs):
        # Find private attributes (starting with _)
        private_attrs = [k for k in attrs.keys() if k.startswith('_') and not k.startswith('__')]
        
        for attr in private_attrs:
            prop_name = attr[1:]  # Remove leading underscore
            
            if prop_name not in attrs:  # Don't override existing attributes
                # Create getter
                def make_getter(attr_name):
                    def getter(self):
                        return getattr(self, attr_name)
                    return getter
                
                # Create setter
                def make_setter(attr_name):
                    def setter(self, value):
                        setattr(self, attr_name, value)
                    return setter
                
                # Create property
                attrs[prop_name] = property(make_getter(attr), make_setter(attr))
        
        return super().__new__(mcs, name, bases, attrs)

# Usage examples
class Database(metaclass=SingletonMeta):
    """Database class using Singleton metaclass."""
    
    def __init__(self):
        self.connection_count = 0
        print("Database instance created")
    
    def connect(self):
        self.connection_count += 1
        return f"Connection #{self.connection_count}"

class Person(metaclass=ValidatedMeta):
    """Person class with validated attributes."""
    
    age_validated = lambda x: isinstance(x, int) and 0 <= x <= 150
    email_validated = lambda x: isinstance(x, str) and '@' in x
    
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email
    
    def __str__(self):
        return f"Person(name='{self.name}', age={self.age}, email='{self.email}')"

class BankAccount(metaclass=AutoPropertyMeta):
    """Bank account with automatic properties for private attributes."""
    
    def __init__(self, account_number, balance):
        self._account_number = account_number
        self._balance = balance
        self._transactions = []
    
    def deposit(self, amount):
        self._balance += amount
        self._transactions.append(f"Deposited ${amount}")
    
    def __str__(self):
        return f"Account {self._account_number}: ${self._balance}"
''',
                "explanation": "Metaclasses control class creation and can add functionality, validation, and patterns to all instances of a class"
            },
            
            "advanced_metaclasses": {
                "code": '''
class RegisteredMeta(type):
    """Metaclass that maintains a registry of all created classes."""
    
    registry = {}
    
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        mcs.registry[name] = cls
        print(f"Registered class: {name}")
        return cls
    
    @classmethod
    def get_registered_classes(mcs):
        return list(mcs.registry.keys())

class LoggingMeta(type):
    """Metaclass that adds logging to all methods."""
    
    def __new__(mcs, name, bases, attrs):
        # Wrap all callable attributes with logging
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not attr_name.startswith('_'):
                attrs[attr_name] = mcs._add_logging(attr_value, attr_name)
        
        return super().__new__(mcs, name, bases, attrs)
    
    @staticmethod
    def _add_logging(func, func_name):
        """Add logging wrapper to a function."""
        def logged_func(self, *args, **kwargs):
            print(f"Calling {func_name} with args={args}, kwargs={kwargs}")
            result = func(self, *args, **kwargs)
            print(f"  {func_name} returned: {result}")
            return result
        
        logged_func.__name__ = func.__name__
        logged_func.__doc__ = func.__doc__
        return logged_func

class APIEndpointMeta(type):
    """Metaclass for automatically registering API endpoints."""
    
    endpoints = {}
    
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Auto-register methods that start with specific prefixes
        for attr_name, attr_value in attrs.items():
            if callable(attr_value):
                if attr_name.startswith('get_'):
                    endpoint = f"/api/{attr_name[4:]}"
                    mcs.endpoints[endpoint] = ('GET', cls, attr_name)
                elif attr_name.startswith('post_'):
                    endpoint = f"/api/{attr_name[5:]}"
                    mcs.endpoints[endpoint] = ('POST', cls, attr_name)
                elif attr_name.startswith('put_'):
                    endpoint = f"/api/{attr_name[4:]}"
                    mcs.endpoints[endpoint] = ('PUT', cls, attr_name)
        
        return cls
    
    @classmethod
    def get_routes(mcs):
        """Return all registered routes."""
        return {endpoint: f"{method} -> {cls.__name__}.{method_name}" 
                for endpoint, (method, cls, method_name) in mcs.endpoints.items()}

# Usage examples
class BaseModel(metaclass=RegisteredMeta):
    """Base model class."""
    pass

class User(BaseModel):
    """User model."""
    pass

class Product(BaseModel):
    """Product model."""
    pass

class Calculator(metaclass=LoggingMeta):
    """Calculator with method call logging."""
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

class UserAPI(metaclass=APIEndpointMeta):
    """API class with auto-registered endpoints."""
    
    def get_users(self):
        return {"users": ["alice", "bob"]}
    
    def post_user(self, user_data):
        return {"created": user_data}
    
    def get_user_profile(self, user_id):
        return {"user_id": user_id, "profile": "data"}
    
    def put_user(self, user_id, user_data):
        return {"updated": user_id}
''',
                "explanation": "Advanced metaclasses can implement sophisticated patterns like registration, automatic decoration, and API routing"
            },
            
            "metaclass_inheritance": {
                "code": '''
class CombinedMeta(RegisteredMeta, LoggingMeta):
    """Metaclass that combines multiple metaclass behaviors."""
    
    def __new__(mcs, name, bases, attrs):
        # Call both parent metaclasses
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Add custom behavior specific to this metaclass
        if not hasattr(cls, '_metadata'):
            cls._metadata = {
                'created_at': time.time(),
                'methods': [name for name, obj in attrs.items() if callable(obj)],
                'attributes': [name for name, obj in attrs.items() if not callable(obj)]
            }
        
        return cls

class ValidationMeta(type):
    """Metaclass that enforces class-level validation rules."""
    
    def __new__(mcs, name, bases, attrs):
        # Ensure required attributes exist
        required_attrs = attrs.get('_required_attributes', [])
        
        for required_attr in required_attrs:
            if required_attr not in attrs:
                raise TypeError(f"Class {name} must define attribute '{required_attr}'")
        
        # Ensure required methods exist
        required_methods = attrs.get('_required_methods', [])
        
        for required_method in required_methods:
            if required_method not in attrs or not callable(attrs[required_method]):
                raise TypeError(f"Class {name} must define method '{required_method}'")
        
        return super().__new__(mcs, name, bases, attrs)

class TypedMeta(type):
    """Metaclass that enforces type annotations on methods."""
    
    def __new__(mcs, name, bases, attrs):
        import inspect
        
        # Check type annotations on all methods
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not attr_name.startswith('_'):
                sig = inspect.signature(attr_value)
                
                # Ensure return type is annotated
                if sig.return_annotation == inspect.Signature.empty:
                    print(f"Warning: Method {attr_name} lacks return type annotation")
                
                # Ensure parameters are annotated
                for param_name, param in sig.parameters.items():
                    if param_name != 'self' and param.annotation == inspect.Parameter.empty:
                        print(f"Warning: Parameter {param_name} in {attr_name} lacks type annotation")
        
        return super().__new__(mcs, name, bases, attrs)

# Usage examples
import time

class ServiceBase(metaclass=CombinedMeta):
    """Base service class with combined metaclass behaviors."""
    
    def process(self):
        return "processing"

class DataModel(metaclass=ValidationMeta):
    """Data model with validation requirements."""
    
    _required_attributes = ['table_name', 'primary_key']
    _required_methods = ['save', 'load']
    
    table_name = 'data_table'
    primary_key = 'id'
    
    def save(self):
        return f"Saving to {self.table_name}"
    
    def load(self, id):
        return f"Loading {id} from {self.table_name}"

class TypedService(metaclass=TypedMeta):
    """Service with enforced type annotations."""
    
    def calculate(self, x: int, y: int) -> int:
        return x + y
    
    def process_data(self, data: list) -> dict:
        return {"processed": len(data)}
    
    # This will generate warnings due to missing annotations
    def untyped_method(self, value):
        return value

# Demonstrate metaclass inheritance and MRO
print("Method Resolution Order:")
print(f"CombinedMeta MRO: {[cls.__name__ for cls in CombinedMeta.__mro__]}")
print(f"ServiceBase MRO: {[cls.__name__ for cls in ServiceBase.__mro__]}")
''',
                "explanation": "Metaclass inheritance allows combining multiple metaclass behaviors and follows method resolution order"
            }
        }
    
    def _setup_exercises(self) -> None:
        """Setup metaclass exercises."""
        from .exercises.orm_metaclass import ORMMetaclassExercise
        
        orm_exercise = ORMMetaclassExercise()
        
        self.exercises = [
            {
                "topic": "metaclasses",
                "title": "ORM Table Creator",
                "description": "Create a metaclass that automatically generates database table schemas",
                "difficulty": "expert",
                "exercise": orm_exercise
            }
        ]
    
    def get_explanation(self) -> str:
        """Get detailed explanation for metaclasses."""
        return ("Metaclasses control class creation and can modify class behavior, attributes, and methods "
                "at definition time, enabling powerful patterns like singletons, validation, and automatic registration.")
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for metaclasses."""
        return [
            "Use metaclasses sparingly - they're complex",
            "Consider class decorators as simpler alternatives",
            "Document metaclass behavior thoroughly",
            "Keep metaclass logic simple and focused",
            "Use __init_subclass__ for simpler class customization"
        ]