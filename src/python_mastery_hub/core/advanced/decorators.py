"""
Decorator examples and demonstrations for the Advanced Python module.
"""

import functools
import time
import inspect
import threading
from typing import Dict, List, Any, Callable, Optional
from .base import TopicDemo


class DecoratorsDemo(TopicDemo):
    """Demonstration class for Python decorators."""
    
    def __init__(self):
        super().__init__("decorators")
    
    def _setup_examples(self) -> None:
        """Setup decorator examples."""
        self.examples = {
            "function_decorators": {
                "code": '''
import functools
import time
from typing import Callable, Any

# Basic timing decorator
def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

# Decorator with parameters
def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry function calls on failure."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"All {max_attempts} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator

# Caching decorator
def memoize(func: Callable) -> Callable:
    """Simple memoization decorator."""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from arguments
        key = str(args) + str(sorted(kwargs.items()))
        
        if key in cache:
            print(f"Cache hit for {func.__name__}")
            return cache[key]
        
        result = func(*args, **kwargs)
        cache[key] = result
        print(f"Cache miss for {func.__name__} - result cached")
        return result
    
    wrapper.cache = cache  # Expose cache for inspection
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper

# Usage examples
@timing_decorator
@memoize
def fibonacci(n: int) -> int:
    """Calculate Fibonacci number (inefficient recursive version)."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@retry(max_attempts=3, delay=0.1)
def unreliable_network_call(success_rate: float = 0.3):
    """Simulate an unreliable network call."""
    import random
    if random.random() < success_rate:
        return "Success!"
    raise ConnectionError("Network request failed")
''',
                "explanation": "Function decorators modify or enhance function behavior without changing the original function code"
            },
            
            "class_decorators": {
                "code": '''
import json
from typing import Dict, Any

# Class decorator for adding serialization methods
def serializable(cls):
    """Class decorator to add JSON serialization methods."""
    
    def to_json(self) -> str:
        """Convert instance to JSON string."""
        return json.dumps(self.__dict__, default=str)
    
    def from_json(cls, json_str: str):
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to dictionary."""
        return self.__dict__.copy()
    
    # Add methods to the class
    cls.to_json = to_json
    cls.from_json = classmethod(from_json)
    cls.to_dict = to_dict
    
    return cls

# Decorator for adding validation
def validate_attributes(**validators):
    """Class decorator to add attribute validation."""
    def decorator(cls):
        original_setattr = cls.__setattr__
        
        def validated_setattr(self, name, value):
            if name in validators:
                validator = validators[name]
                if not validator(value):
                    raise ValueError(f"Invalid value for {name}: {value}")
            original_setattr(self, name, value)
        
        cls.__setattr__ = validated_setattr
        return cls
    
    return decorator

# Usage examples
@serializable
@validate_attributes(
    age=lambda x: isinstance(x, int) and 0 <= x <= 150,
    email=lambda x: isinstance(x, str) and '@' in x
)
class Person:
    """Person class with serialization and validation."""
    
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email
    
    def __str__(self):
        return f"Person(name='{self.name}', age={self.age}, email='{self.email}')"
''',
                "explanation": "Class decorators can modify entire classes, adding methods, validation, logging, and other behaviors"
            },
            
            "advanced_decorators": {
                "code": '''
import inspect
import threading
from typing import Callable, Any, Optional
from functools import wraps

# Decorator that preserves function signature
def preserve_signature(decorator_func):
    """Meta-decorator that preserves function signatures."""
    def decorator(func):
        sig = inspect.signature(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Bind arguments to parameters
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            return decorator_func(func, bound_args.args, bound_args.kwargs)
        
        # Preserve the original signature
        wrapper.__signature__ = sig
        return wrapper
    return decorator

# Thread-safe singleton decorator
def singleton(cls):
    """Thread-safe singleton class decorator."""
    instances = {}
    lock = threading.Lock()
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

# Rate limiting decorator
class RateLimiter:
    """Rate limiting decorator with configurable limits."""
    
    def __init__(self, calls_per_second: float):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_called = {}
        self.lock = threading.Lock()
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                key = id(func)
                
                if key in self.last_called:
                    elapsed = now - self.last_called[key]
                    if elapsed < self.min_interval:
                        sleep_time = self.min_interval - elapsed
                        time.sleep(sleep_time)
                
                self.last_called[key] = time.time()
                return func(*args, **kwargs)
        
        return wrapper

# Usage examples
@preserve_signature
def logged_execution(func, args, kwargs):
    """Log function execution with preserved signature."""
    print(f"Executing {func.__name__} with args={args}, kwargs={kwargs}")
    result = func(*args, **kwargs)
    print(f"  -> Result: {result}")
    return result

@singleton
class DatabaseManager:
    """Singleton database manager."""
    
    def __init__(self):
        self.connection_count = 0
        print("DatabaseManager initialized")
    
    def connect(self):
        self.connection_count += 1
        return f"Connection #{self.connection_count}"

@RateLimiter(calls_per_second=2.0)  # Max 2 calls per second
def api_call(endpoint: str):
    """Simulated API call with rate limiting."""
    return f"Called {endpoint} at {time.time():.2f}"
''',
                "explanation": "Advanced decorators can preserve signatures, implement patterns like singleton, add type checking, and control execution flow"
            }
        }
    
    def _setup_exercises(self) -> None:
        """Setup decorator exercises."""
        from .exercises.caching_decorator import CachingDecoratorExercise
        
        caching_exercise = CachingDecoratorExercise()
        
        self.exercises = [
            {
                "topic": "decorators",
                "title": "Build a Caching Decorator",
                "description": "Create a sophisticated caching decorator with TTL and size limits",
                "difficulty": "hard",
                "exercise": caching_exercise
            }
        ]
    
    def get_explanation(self) -> str:
        """Get detailed explanation for decorators."""
        return ("Decorators modify or enhance functions and classes without changing their source code, "
                "providing a clean way to add functionality like logging, timing, caching, and validation.")
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for decorators."""
        return [
            "Use functools.wraps to preserve function metadata",
            "Keep decorators simple and focused on single concerns",
            "Use parameterized decorators for configurable behavior",
            "Document decorator behavior clearly",
            "Consider performance impact of decorators"
        ]