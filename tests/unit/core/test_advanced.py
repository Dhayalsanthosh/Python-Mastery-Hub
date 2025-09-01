# tests/unit/core/test_advanced.py
# Unit tests for advanced Python concepts and exercises

import pytest
import asyncio
import inspect
from unittest.mock import Mock, AsyncMock, patch
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from functools import wraps
import threading
import time

# Import modules under test (adjust based on your actual structure)
try:
    from src.core.advanced import (
        DecoratorExercise,
        GeneratorExercise,
        ContextManagerExercise,
        MetaclassExercise,
        ConcurrencyExercise
    )
    from src.core.evaluators import AdvancedPythonEvaluator
except ImportError:
    # Mock classes for when actual modules don't exist
    class DecoratorExercise:
        pass
    class GeneratorExercise:
        pass
    class ContextManagerExercise:
        pass
    class MetaclassExercise:
        pass
    class ConcurrencyExercise:
        pass
    class AdvancedPythonEvaluator:
        pass


class TestDecoratorExercises:
    """Test cases for decorator exercises."""
    
    def test_simple_decorator(self):
        """Test creating a simple decorator."""
        code = '''
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Function {func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function():
    import time
    time.sleep(0.1)
    return "Done"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test decorator exists
        assert 'timing_decorator' in globals_dict
        assert 'slow_function' in globals_dict
        
        # Test decorated function works
        result = globals_dict['slow_function']()
        assert result == "Done"
    
    def test_decorator_with_arguments(self):
        """Test decorator that accepts arguments."""
        code = '''
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def say_hello(name):
    return f"Hello, {name}!"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        result = globals_dict['say_hello']("Alice")
        assert len(result) == 3
        assert all(greeting == "Hello, Alice!" for greeting in result)
    
    def test_class_decorator(self):
        """Test class-based decorator."""
        code = '''
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count} to {self.func.__name__}")
        return self.func(*args, **kwargs)
    
    def get_count(self):
        return self.count

@CountCalls
def add(a, b):
    return a + b
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        add_func = globals_dict['add']
        
        # Test function works
        assert add_func(2, 3) == 5
        assert add_func(5, 7) == 12
        
        # Test call counting
        assert add_func.get_count() == 2
    
    def test_property_decorator(self):
        """Test property decorator usage."""
        code = '''
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value
    
    @property
    def area(self):
        return 3.14159 * self._radius ** 2
    
    @property
    def diameter(self):
        return 2 * self._radius
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Circle = globals_dict['Circle']
        circle = Circle(5)
        
        assert circle.radius == 5
        assert abs(circle.area - 78.53975) < 0.001
        assert circle.diameter == 10
        
        # Test setter
        circle.radius = 10
        assert circle.radius == 10
        
        # Test validation
        with pytest.raises(ValueError):
            circle.radius = -1
    
    def test_functools_wraps(self):
        """Test proper use of functools.wraps."""
        code = '''
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def example_function():
    """This is an example function."""
    return "Hello, World!"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        func = globals_dict['example_function']
        
        # Test that function metadata is preserved
        assert func.__name__ == 'example_function'
        assert func.__doc__ == "This is an example function."
        assert func() == "Hello, World!"


class TestGeneratorExercises:
    """Test cases for generator exercises."""
    
    def test_simple_generator(self):
        """Test creating a simple generator."""
        code = '''
def count_up_to(max_value):
    count = 1
    while count <= max_value:
        yield count
        count += 1

# Create generator
counter = count_up_to(5)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        counter = globals_dict['counter']
        
        # Test generator
        assert inspect.isgenerator(counter)
        
        # Test values
        values = list(counter)
        assert values == [1, 2, 3, 4, 5]
    
    def test_fibonacci_generator(self):
        """Test Fibonacci sequence generator."""
        code = '''
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def take(n, generator):
    result = []
    for _ in range(n):
        result.append(next(generator))
    return result

fib = fibonacci()
first_ten = take(10, fib)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        first_ten = globals_dict['first_ten']
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert first_ten == expected
    
    def test_generator_expressions(self):
        """Test generator expressions."""
        code = '''
# Generator expression for squares
squares_gen = (x**2 for x in range(1, 6))
squares_list = list(squares_gen)

# Generator expression with condition
even_squares = (x**2 for x in range(1, 11) if x % 2 == 0)
even_squares_list = list(even_squares)

# Nested generator expression
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = (item for row in matrix for item in row)
flattened_list = list(flattened)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['squares_list'] == [1, 4, 9, 16, 25]
        assert globals_dict['even_squares_list'] == [4, 16, 36, 64, 100]
        assert globals_dict['flattened_list'] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    def test_generator_send_method(self):
        """Test generator send method."""
        code = '''
def accumulator():
    total = 0
    while True:
        value = yield total
        if value is not None:
            total += value

acc = accumulator()
next(acc)  # Prime the generator
result1 = acc.send(10)
result2 = acc.send(20)
result3 = acc.send(5)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result1'] == 10
        assert globals_dict['result2'] == 30
        assert globals_dict['result3'] == 35
    
    def test_generator_with_return(self):
        """Test generator with return statement."""
        code = '''
def generator_with_return():
    yield 1
    yield 2
    yield 3
    return "Done"

gen = generator_with_return()
values = []
try:
    while True:
        values.append(next(gen))
except StopIteration as e:
    return_value = e.value
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['values'] == [1, 2, 3]
        assert globals_dict['return_value'] == "Done"


class TestContextManagerExercises:
    """Test cases for context manager exercises."""
    
    def test_simple_context_manager(self):
        """Test creating a simple context manager."""
        code = '''
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        print(f"Opening file {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_value, traceback):
        print(f"Closing file {self.filename}")
        if self.file:
            self.file.close()
        return False

# Create a test file
import tempfile
import os

temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
temp_file.write("Test content")
temp_file.close()

# Test context manager
with FileManager(temp_file.name, 'r') as f:
    content = f.read()

# Cleanup
os.unlink(temp_file.name)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['content'] == "Test content"
    
    def test_contextlib_contextmanager(self):
        """Test using contextlib.contextmanager decorator."""
        code = '''
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    print("Timer started")
    try:
        yield
    finally:
        end = time.time()
        print(f"Timer ended. Elapsed: {end - start:.4f} seconds")

# Test the context manager
with timer():
    import time
    time.sleep(0.1)
    result = "Task completed"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == "Task completed"
    
    def test_nested_context_managers(self):
        """Test nested context managers."""
        code = '''
from contextlib import contextmanager

@contextmanager
def transaction():
    print("Begin transaction")
    try:
        yield
        print("Commit transaction")
    except Exception:
        print("Rollback transaction")
        raise

@contextmanager
def connection():
    print("Open connection")
    try:
        yield "connection"
    finally:
        print("Close connection")

# Test nested context managers
try:
    with connection() as conn:
        with transaction():
            result = f"Using {conn} in transaction"
except Exception as e:
    error = str(e)
else:
    error = None
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == "Using connection in transaction"
        assert globals_dict['error'] is None
    
    def test_exception_handling_in_context_manager(self):
        """Test exception handling in context managers."""
        code = '''
class ErrorHandler:
    def __init__(self, suppress_errors=False):
        self.suppress_errors = suppress_errors
        self.exception_occurred = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.exception_occurred = True
            print(f"Exception occurred: {exc_type.__name__}: {exc_value}")
            return self.suppress_errors  # Suppress or propagate
        return False

# Test with suppression
with ErrorHandler(suppress_errors=True) as handler1:
    raise ValueError("Test error")

suppressed = handler1.exception_occurred

# Test without suppression
try:
    with ErrorHandler(suppress_errors=False) as handler2:
        raise ValueError("Test error")
except ValueError:
    not_suppressed = True
else:
    not_suppressed = False
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['suppressed'] is True
        assert globals_dict['not_suppressed'] is True


class TestMetaclassExercises:
    """Test cases for metaclass exercises."""
    
    def test_simple_metaclass(self):
        """Test creating a simple metaclass."""
        code = '''
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    def __init__(self, value):
        self.value = value

# Test singleton behavior
s1 = Singleton("first")
s2 = Singleton("second")

same_instance = s1 is s2
value_unchanged = s1.value == "first"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['same_instance'] is True
        assert globals_dict['value_unchanged'] is True
    
    def test_attribute_validation_metaclass(self):
        """Test metaclass for attribute validation."""
        code = '''
class ValidatedMeta(type):
    def __new__(mcs, name, bases, attrs):
        # Validate that all methods have docstrings
        for key, value in attrs.items():
            if callable(value) and not key.startswith('_'):
                if not hasattr(value, '__doc__') or not value.__doc__:
                    raise ValueError(f"Method {key} must have a docstring")
        
        return super().__new__(mcs, name, bases, attrs)

class ValidatedClass(metaclass=ValidatedMeta):
    def method_with_doc(self):
        """This method has a docstring."""
        return "documented"

# Test that class creation succeeds
instance = ValidatedClass()
result = instance.method_with_doc()

# Test validation
try:
    class InvalidClass(metaclass=ValidatedMeta):
        def method_without_doc(self):
            return "undocumented"
    validation_failed = False
except ValueError:
    validation_failed = True
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == "documented"
        assert globals_dict['validation_failed'] is True
    
    def test_automatic_property_metaclass(self):
        """Test metaclass that automatically creates properties."""
        code = '''
class AutoPropertyMeta(type):
    def __new__(mcs, name, bases, attrs):
        # Convert attributes ending with '_' to properties
        new_attrs = {}
        for key, value in attrs.items():
            if key.endswith('_') and not key.startswith('_'):
                prop_name = key[:-1]
                private_name = f'_{key}'
                
                def make_getter(private_attr):
                    def getter(self):
                        return getattr(self, private_attr, None)
                    return getter
                
                def make_setter(private_attr):
                    def setter(self, value):
                        setattr(self, private_attr, value)
                    return setter
                
                new_attrs[prop_name] = property(
                    make_getter(private_name),
                    make_setter(private_name)
                )
                new_attrs[private_name] = value
            else:
                new_attrs[key] = value
        
        return super().__new__(mcs, name, bases, new_attrs)

class Person(metaclass=AutoPropertyMeta):
    name_ = ""
    age_ = 0

p = Person()
p.name = "Alice"
p.age = 30

name_value = p.name
age_value = p.age
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['name_value'] == "Alice"
        assert globals_dict['age_value'] == 30


class TestConcurrencyExercises:
    """Test cases for concurrency exercises."""
    
    def test_threading_basic(self):
        """Test basic threading."""
        code = '''
import threading
import time

results = []
lock = threading.Lock()

def worker(name, delay):
    time.sleep(delay)
    with lock:
        results.append(f"Worker {name} completed")

# Create and start threads
threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=(i, 0.1))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

completed_count = len(results)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['completed_count'] == 3
        assert len(globals_dict['results']) == 3
    
    @pytest.mark.asyncio
    async def test_asyncio_basic(self):
        """Test basic asyncio."""
        code = '''
import asyncio

async def async_worker(name, delay):
    await asyncio.sleep(delay)
    return f"Async worker {name} completed"

async def run_workers():
    tasks = []
    for i in range(3):
        task = asyncio.create_task(async_worker(i, 0.1))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# Run the async function
results = asyncio.run(run_workers())
completed_count = len(results)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['completed_count'] == 3
        assert len(globals_dict['results']) == 3
    
    def test_queue_usage(self):
        """Test using queue for thread communication."""
        code = '''
import queue
import threading
import time

# Create a queue
q = queue.Queue()
results = []

def producer():
    for i in range(5):
        q.put(f"item_{i}")
        time.sleep(0.01)
    q.put(None)  # Sentinel to signal completion

def consumer():
    while True:
        item = q.get()
        if item is None:
            break
        results.append(f"Processed {item}")
        q.task_done()

# Start threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()

processed_count = len(results)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['processed_count'] == 5
    
    def test_concurrent_futures(self):
        """Test concurrent.futures module."""
        code = '''
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def cpu_bound_task(n):
    # Simulate CPU-bound work
    result = sum(i * i for i in range(n))
    return result

def io_bound_task(delay):
    # Simulate I/O-bound work
    time.sleep(delay)
    return f"Task completed after {delay} seconds"

# Test ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit I/O-bound tasks
    io_futures = [executor.submit(io_bound_task, 0.1) for _ in range(3)]
    
    # Get results
    io_results = [future.result() for future in io_futures]

# Test with as_completed
with ThreadPoolExecutor(max_workers=2) as executor:
    cpu_futures = [executor.submit(cpu_bound_task, 1000) for _ in range(2)]
    
    cpu_results = []
    for future in as_completed(cpu_futures):
        cpu_results.append(future.result())

io_count = len(io_results)
cpu_count = len(cpu_results)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['io_count'] == 3
        assert globals_dict['cpu_count'] == 2


class TestAdvancedPythonEvaluator:
    """Test cases for advanced Python evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create an advanced Python evaluator instance."""
        return AdvancedPythonEvaluator()
    
    def test_evaluate_decorator(self, evaluator):
        """Test evaluation of decorator code."""
        code = '''
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def test_function():
    return "decorated"
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert 'my_decorator' in result['globals']
        assert 'test_function' in result['globals']
        
        # Test decorated function
        func = result['globals']['test_function']
        assert func() == "decorated"
    
    def test_evaluate_generator(self, evaluator):
        """Test evaluation of generator code."""
        code = '''
def count_generator(n):
    for i in range(n):
        yield i

gen = count_generator(3)
values = list(gen)
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert result['globals']['values'] == [0, 1, 2]
    
    def test_evaluate_context_manager(self, evaluator):
        """Test evaluation of context manager code."""
        code = '''
class TestContextManager:
    def __init__(self):
        self.entered = False
        self.exited = False
    
    def __enter__(self):
        self.entered = True
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.exited = True
        return False

with TestContextManager() as cm:
    status = cm.entered

final_status = cm.exited
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert result['globals']['status'] is True
        assert result['globals']['final_status'] is True
    
    def test_check_advanced_features(self, evaluator):
        """Test checking for advanced Python features."""
        code = '''
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def my_generator():
    yield 1
    yield 2

class MyContextManager:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return False
'''
        
        features = evaluator.check_advanced_features(code)
        
        assert 'decorators' in features
        assert 'generators' in features
        assert 'context_managers' in features
        assert features['decorators'] > 0
        assert features['generators'] > 0
        assert features['context_managers'] > 0


class TestAdvancedPatterns:
    """Test cases for advanced Python patterns."""
    
    def test_descriptor_pattern(self):
        """Test descriptor pattern implementation."""
        code = '''
class Descriptor:
    def __init__(self, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, None)
    
    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise TypeError("Value must be a string")
        obj.__dict__[self.name] = value
    
    def __delete__(self, obj):
        del obj.__dict__[self.name]

class Person:
    name = Descriptor('_name')
    
    def __init__(self, name):
        self.name = name

p = Person("Alice")
name_value = p.name

# Test validation
try:
    p.name = 123
    validation_error = False
except TypeError:
    validation_error = True
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['name_value'] == "Alice"
        assert globals_dict['validation_error'] is True
    
    def test_factory_pattern(self):
        """Test factory pattern implementation."""
        code = '''
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type.lower() == 'dog':
            return Dog()
        elif animal_type.lower() == 'cat':
            return Cat()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")

# Test factory
dog = AnimalFactory.create_animal('dog')
cat = AnimalFactory.create_animal('cat')

dog_sound = dog.speak()
cat_sound = cat.speak()
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['dog_sound'] == "Woof!"
        assert globals_dict['cat_sound'] == "Meow!"
    
    def test_observer_pattern(self):
        """Test observer pattern implementation."""
        code = '''
class Observable:
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer):
        self._observers.append(observer)
    
    def remove_observer(self, observer):
        self._observers.remove(observer)
    
    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer.update(self, *args, **kwargs)

class Observer:
    def __init__(self, name):
        self.name = name
        self.notifications = []
    
    def update(self, observable, *args, **kwargs):
        self.notifications.append(f"{self.name} received: {args}")

# Test observer pattern
subject = Observable()
observer1 = Observer("Observer1")
observer2 = Observer("Observer2")

subject.add_observer(observer1)
subject.add_observer(observer2)

subject.notify_observers("test message")

obs1_count = len(observer1.notifications)
obs2_count = len(observer2.notifications)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['obs1_count'] == 1
        assert globals_dict['obs2_count'] == 1


@pytest.mark.integration
class TestAdvancedIntegration:
    """Integration tests for advanced Python concepts."""
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager integration."""
        code = '''
import asyncio

class AsyncContextManager:
    async def __aenter__(self):
        await asyncio.sleep(0.01)
        return "async context"
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await asyncio.sleep(0.01)
        return False

async def test_async_context():
    async with AsyncContextManager() as ctx:
        return ctx

result = asyncio.run(test_async_context())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == "async context"
    
    def test_combining_advanced_features(self):
        """Test combining multiple advanced features."""
        code = '''
from functools import wraps
from contextlib import contextmanager

def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@contextmanager
def error_handling():
    try:
        yield
    except Exception as e:
        print(f"Error handled: {e}")

class DataProcessor:
    def __init__(self):
        self.data = []
    
    @logged
    def process_items(self, items):
        with error_handling():
            for item in self.data_generator(items):
                self.data.append(item * 2)
        return self.data
    
    def data_generator(self, items):
        for item in items:
            yield item

processor = DataProcessor()
result = processor.process_items([1, 2, 3, 4, 5])
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == [2, 4, 6, 8, 10]


if __name__ == '__main__':
    pytest.main([__file__])