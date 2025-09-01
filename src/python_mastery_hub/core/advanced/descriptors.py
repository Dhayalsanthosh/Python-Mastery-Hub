"""
Descriptor examples and demonstrations for the Advanced Python module.
"""

from typing import Dict, List, Any, Type, Optional
from .base import TopicDemo


class DescriptorsDemo(TopicDemo):
    """Demonstration class for Python descriptors."""
    
    def __init__(self):
        super().__init__("descriptors")
    
    def _setup_examples(self) -> None:
        """Setup descriptor examples."""
        self.examples = {
            "basic_descriptors": {
                "code": '''
class TypedAttribute:
    """Descriptor that enforces type checking."""
    
    def __init__(self, expected_type, default=None):
        self.expected_type = expected_type
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        """Called when the descriptor is assigned to a class attribute."""
        self.name = name
        self.private_name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        """Get the attribute value."""
        if obj is None:
            return self
        return getattr(obj, self.private_name, self.default)
    
    def __set__(self, obj, value):
        """Set the attribute value with type checking."""
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{self.name} must be of type {self.expected_type.__name__}")
        setattr(obj, self.private_name, value)
    
    def __delete__(self, obj):
        """Delete the attribute."""
        if hasattr(obj, self.private_name):
            delattr(obj, self.private_name)

class RangeAttribute:
    """Descriptor that enforces value ranges."""
    
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, 0)
    
    def __set__(self, obj, value):
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} must be <= {self.max_value}")
        setattr(obj, self.private_name, value)

class LoggedAttribute:
    """Descriptor that logs all access to an attribute."""
    
    def __init__(self, initial_value=None):
        self.initial_value = initial_value
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        value = getattr(obj, self.private_name, self.initial_value)
        print(f"GET {self.name}: {value}")
        return value
    
    def __set__(self, obj, value):
        old_value = getattr(obj, self.private_name, self.initial_value)
        setattr(obj, self.private_name, value)
        print(f"SET {self.name}: {old_value} -> {value}")

# Usage example
class Student:
    """Student class using various descriptors."""
    
    name = TypedAttribute(str, "Unknown")
    age = RangeAttribute(min_value=0, max_value=150)
    grade = RangeAttribute(min_value=0, max_value=100)
    status = LoggedAttribute("enrolled")
    
    def __init__(self, name, age, grade):
        self.name = name
        self.age = age
        self.grade = grade
    
    def __str__(self):
        return f"Student(name='{self.name}', age={self.age}, grade={self.grade})"
''',
                "explanation": "Basic descriptors control attribute access through __get__, __set__, and __delete__ methods"
            },
            
            "advanced_descriptors": {
                "code": '''
class LazyProperty:
    """Descriptor for lazy-loaded properties."""
    
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        # Check if value is already computed
        attr_name = f'_lazy_{self.name}'
        if hasattr(obj, attr_name):
            print(f"Returning cached value for {self.name}")
            return getattr(obj, attr_name)
        
        # Compute and cache the value
        print(f"Computing {self.name} for the first time")
        value = self.func(obj)
        setattr(obj, attr_name, value)
        return value

class CachedProperty:
    """Descriptor that caches computed values with cache control."""
    
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        cache_attr = f'_cached_{self.name}'
        
        if not hasattr(obj, cache_attr):
            print(f"Computing {self.name}")
            value = self.func(obj)
            setattr(obj, cache_attr, value)
        else:
            print(f"Using cached {self.name}")
        
        return getattr(obj, cache_attr)
    
    def __set__(self, obj, value):
        """Allow manual setting of cached value."""
        cache_attr = f'_cached_{self.name}'
        setattr(obj, cache_attr, value)
        print(f"Manually set {self.name} to {value}")
    
    def __delete__(self, obj):
        """Clear the cache."""
        cache_attr = f'_cached_{self.name}'
        if hasattr(obj, cache_attr):
            delattr(obj, cache_attr)
            print(f"Cleared cache for {self.name}")

class ValidatedProperty:
    """Descriptor with validation and transformation."""
    
    def __init__(self, validator=None, transformer=None, default=None):
        self.validator = validator
        self.transformer = transformer
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, self.default)
    
    def __set__(self, obj, value):
        # Apply transformer if provided
        if self.transformer:
            value = self.transformer(value)
        
        # Apply validation if provided
        if self.validator and not self.validator(value):
            raise ValueError(f"Invalid value for {self.name}: {value}")
        
        setattr(obj, self.private_name, value)

class WeakProperty:
    """Descriptor that uses weak references to avoid memory leaks."""
    
    def __init__(self, default=None):
        import weakref
        self.data = weakref.WeakKeyDictionary()
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.data.get(obj, self.default)
    
    def __set__(self, obj, value):
        self.data[obj] = value
    
    def __delete__(self, obj):
        if obj in self.data:
            del self.data[obj]

# Usage examples
class DataProcessor:
    """Class demonstrating advanced descriptor usage."""
    
    def __init__(self, data):
        self.data = data
    
    @LazyProperty
    def processed_data(self):
        """Expensive data processing operation."""
        import time
        time.sleep(0.1)  # Simulate expensive computation
        return [x * 2 for x in self.data]
    
    @CachedProperty
    def statistics(self):
        """Calculate statistics on processed data."""
        processed = self.processed_data
        return {
            'mean': sum(processed) / len(processed),
            'max': max(processed),
            'min': min(processed)
        }

class ConfigurableModel:
    """Model with validated and transformed properties."""
    
    # Email property with validation and transformation
    email = ValidatedProperty(
        validator=lambda x: '@' in x and '.' in x,
        transformer=lambda x: x.lower().strip()
    )
    
    # Age property with range validation
    age = ValidatedProperty(
        validator=lambda x: isinstance(x, int) and 0 <= x <= 150,
        default=0
    )
    
    # Weak reference property to avoid circular references
    parent = WeakProperty()
    
    def __init__(self, email, age):
        self.email = email
        self.age = age

class Temperature:
    """Comparison between property and descriptor approaches."""
    
    # Using property decorator
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius_property(self):
        return self._celsius
    
    @celsius_property.setter
    def celsius_property(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        self._celsius = value
    
    # Using descriptor
    celsius_descriptor = RangeAttribute(min_value=-273.15)
''',
                "explanation": "Advanced descriptors provide powerful patterns for lazy loading, caching, validation, and memory management"
            },
            
            "descriptor_vs_property": {
                "code": '''
# Comparison of different approaches to attribute management

class PropertyApproach:
    """Using @property decorator."""
    
    def __init__(self, value=0):
        self._value = value
    
    @property
    def value(self):
        print("Getting value via property")
        return self._value
    
    @value.setter
    def value(self, val):
        print(f"Setting value via property: {val}")
        if val < 0:
            raise ValueError("Value must be non-negative")
        self._value = val

class DescriptorApproach:
    """Using custom descriptor."""
    
    value = ValidatedProperty(
        validator=lambda x: x >= 0,
        default=0
    )
    
    def __init__(self, value=0):
        self.value = value

class SlotDescriptor:
    """Descriptor that works with __slots__."""
    
    def __init__(self, slot_name):
        self.slot_name = slot_name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.slot_name)
    
    def __set__(self, obj, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Value must be numeric")
        setattr(obj, self.slot_name, value)

class OptimizedClass:
    """Class using __slots__ with descriptors for memory efficiency."""
    
    __slots__ = ['_x', '_y', '_z']
    
    x = SlotDescriptor('_x')
    y = SlotDescriptor('_y')
    z = SlotDescriptor('_z')
    
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

# Descriptor for method caching
class CachedMethod:
    """Descriptor that caches method results."""
    
    def __init__(self, func):
        self.func = func
        self.cache_attr = f'_cache_{func.__name__}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        # Return bound method with caching
        def cached_method(*args, **kwargs):
            if not hasattr(obj, self.cache_attr):
                setattr(obj, self.cache_attr, {})
            
            cache = getattr(obj, self.cache_attr)
            key = str(args) + str(sorted(kwargs.items()))
            
            if key not in cache:
                result = self.func(obj, *args, **kwargs)
                cache[key] = result
                print(f"Computed and cached {self.func.__name__}")
                return result
            else:
                print(f"Retrieved from cache {self.func.__name__}")
                return cache[key]
        
        return cached_method

class MathOperations:
    """Class with cached method descriptor."""
    
    @CachedMethod
    def fibonacci(self, n):
        """Calculate Fibonacci number with caching."""
        if n <= 1:
            return n
        return self.fibonacci(n-1) + self.fibonacci(n-2)
    
    @CachedMethod
    def factorial(self, n):
        """Calculate factorial with caching."""
        if n <= 1:
            return 1
        return n * self.factorial(n-1)
''',
                "explanation": "Descriptors vs properties comparison shows different approaches to attribute management with various trade-offs"
            }
        }