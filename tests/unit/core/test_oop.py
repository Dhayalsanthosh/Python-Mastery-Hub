# tests/unit/core/test_oop.py
# Unit tests for Object-Oriented Programming concepts and exercises

import pytest
import inspect
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Import modules under test (adjust based on your actual structure)
try:
    from src.core.oop import (
        ClassExercise,
        InheritanceExercise,
        PolymorphismExercise,
        EncapsulationExercise,
        AbstractionExercise
    )
    from src.core.evaluators import OOPEvaluator
    from src.models.exercise import Exercise
except ImportError:
    # Mock classes for when actual modules don't exist
    class ClassExercise:
        pass
    class InheritanceExercise:
        pass
    class PolymorphismExercise:
        pass
    class EncapsulationExercise:
        pass
    class AbstractionExercise:
        pass
    class OOPEvaluator:
        pass
    class Exercise:
        pass


class TestBasicClassExercises:
    """Test cases for basic class definition exercises."""
    
    def test_simple_class_definition(self):
        """Test creating a simple class."""
        code = '''
class Person:
    pass
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert 'Person' in globals_dict
        assert inspect.isclass(globals_dict['Person'])
        
        # Test instantiation
        person = globals_dict['Person']()
        assert isinstance(person, globals_dict['Person'])
    
    def test_class_with_constructor(self):
        """Test class with __init__ method."""
        code = '''
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Person = globals_dict['Person']
        person = Person("Alice", 30)
        
        assert person.name == "Alice"
        assert person.age == 30
    
    def test_class_with_methods(self):
        """Test class with instance methods."""
        code = '''
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self.result
    
    def subtract(self, value):
        self.result -= value
        return self.result
    
    def get_result(self):
        return self.result
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Calculator = globals_dict['Calculator']
        calc = Calculator()
        
        assert calc.add(10) == 10
        assert calc.subtract(3) == 7
        assert calc.get_result() == 7
    
    def test_class_with_class_variables(self):
        """Test class with class variables."""
        code = '''
class Counter:
    count = 0
    
    def __init__(self):
        Counter.count += 1
        self.instance_number = Counter.count
    
    @classmethod
    def get_count(cls):
        return cls.count
    
    @staticmethod
    def reset_count():
        Counter.count = 0
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Counter = globals_dict['Counter']
        
        # Test class variable
        assert Counter.count == 0
        
        # Create instances
        c1 = Counter()
        assert Counter.count == 1
        assert c1.instance_number == 1
        
        c2 = Counter()
        assert Counter.count == 2
        assert c2.instance_number == 2
        
        # Test class method
        assert Counter.get_count() == 2
        
        # Test static method
        Counter.reset_count()
        assert Counter.count == 0
    
    def test_class_with_properties(self):
        """Test class with property decorators."""
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
    def circumference(self):
        return 2 * 3.14159 * self._radius
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Circle = globals_dict['Circle']
        circle = Circle(5)
        
        assert circle.radius == 5
        assert abs(circle.area - 78.53975) < 0.001
        assert abs(circle.circumference - 31.4159) < 0.001
        
        # Test setter
        circle.radius = 10
        assert circle.radius == 10
        
        # Test validation
        with pytest.raises(ValueError):
            circle.radius = -1


class TestInheritanceExercises:
    """Test cases for inheritance exercises."""
    
    def test_single_inheritance(self):
        """Test single inheritance."""
        code = '''
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return f"{self.name} makes a sound"

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed
    
    def speak(self):
        return f"{self.name} barks"
    
    def get_breed(self):
        return self.breed
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Animal = globals_dict['Animal']
        Dog = globals_dict['Dog']
        
        # Test base class
        animal = Animal("Generic Animal")
        assert animal.speak() == "Generic Animal makes a sound"
        
        # Test derived class
        dog = Dog("Buddy", "Golden Retriever")
        assert dog.name == "Buddy"
        assert dog.breed == "Golden Retriever"
        assert dog.speak() == "Buddy barks"
        assert dog.get_breed() == "Golden Retriever"
        
        # Test inheritance relationship
        assert isinstance(dog, Dog)
        assert isinstance(dog, Animal)
    
    def test_multiple_inheritance(self):
        """Test multiple inheritance."""
        code = '''
class Flyable:
    def fly(self):
        return "Flying in the sky"

class Swimmable:
    def swim(self):
        return "Swimming in water"

class Duck(Flyable, Swimmable):
    def __init__(self, name):
        self.name = name
    
    def quack(self):
        return f"{self.name} says quack"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Duck = globals_dict['Duck']
        duck = Duck("Donald")
        
        assert duck.fly() == "Flying in the sky"
        assert duck.swim() == "Swimming in water"
        assert duck.quack() == "Donald says quack"
        
        # Check MRO (Method Resolution Order)
        mro_names = [cls.__name__ for cls in Duck.__mro__]
        assert 'Duck' in mro_names
        assert 'Flyable' in mro_names
        assert 'Swimmable' in mro_names
    
    def test_method_resolution_order(self):
        """Test method resolution order in diamond inheritance."""
        code = '''
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        D = globals_dict['D']
        d = D()
        
        # Should follow MRO: D -> B -> C -> A
        assert d.method() == "B"
    
    def test_super_usage(self):
        """Test proper usage of super()."""
        code = '''
class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
    
    def start(self):
        return f"{self.brand} {self.model} is starting"

class Car(Vehicle):
    def __init__(self, brand, model, doors):
        super().__init__(brand, model)
        self.doors = doors
    
    def start(self):
        base_start = super().start()
        return f"{base_start} with {self.doors} doors"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Car = globals_dict['Car']
        car = Car("Toyota", "Camry", 4)
        
        assert car.brand == "Toyota"
        assert car.model == "Camry"
        assert car.doors == 4
        assert car.start() == "Toyota Camry is starting with 4 doors"


class TestPolymorphismExercises:
    """Test cases for polymorphism exercises."""
    
    def test_method_overriding(self):
        """Test method overriding for polymorphism."""
        code = '''
class Shape:
    def area(self):
        return 0
    
    def perimeter(self):
        return 0

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14159 * self.radius ** 2
    
    def perimeter(self):
        return 2 * 3.14159 * self.radius
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Rectangle = globals_dict['Rectangle']
        Circle = globals_dict['Circle']
        
        shapes = [
            Rectangle(5, 10),
            Circle(3)
        ]
        
        # Test polymorphic behavior
        areas = [shape.area() for shape in shapes]
        assert areas[0] == 50  # Rectangle area
        assert abs(areas[1] - 28.274) < 0.01  # Circle area
        
        perimeters = [shape.perimeter() for shape in shapes]
        assert perimeters[0] == 30  # Rectangle perimeter
        assert abs(perimeters[1] - 18.849) < 0.01  # Circle perimeter
    
    def test_duck_typing(self):
        """Test duck typing behavior."""
        code = '''
class Duck:
    def quack(self):
        return "Quack quack!"
    
    def walk(self):
        return "Duck is walking"

class Person:
    def quack(self):
        return "Person imitating duck: Quack!"
    
    def walk(self):
        return "Person is walking"

def make_it_quack_and_walk(duck_like):
    return {
        'quack': duck_like.quack(),
        'walk': duck_like.walk()
    }
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Duck = globals_dict['Duck']
        Person = globals_dict['Person']
        make_it_quack_and_walk = globals_dict['make_it_quack_and_walk']
        
        duck = Duck()
        person = Person()
        
        # Both should work with the function (duck typing)
        duck_result = make_it_quack_and_walk(duck)
        person_result = make_it_quack_and_walk(person)
        
        assert duck_result['quack'] == "Quack quack!"
        assert person_result['quack'] == "Person imitating duck: Quack!"
    
    def test_operator_overloading(self):
        """Test operator overloading."""
        code = '''
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Vector = globals_dict['Vector']
        
        v1 = Vector(3, 4)
        v2 = Vector(1, 2)
        
        # Test addition
        v3 = v1 + v2
        assert v3.x == 4 and v3.y == 6
        
        # Test subtraction
        v4 = v1 - v2
        assert v4.x == 2 and v4.y == 2
        
        # Test multiplication
        v5 = v1 * 2
        assert v5.x == 6 and v5.y == 8
        
        # Test equality
        v6 = Vector(3, 4)
        assert v1 == v6
        assert v1 != v2


class TestEncapsulationExercises:
    """Test cases for encapsulation exercises."""
    
    def test_private_attributes(self):
        """Test private attributes with name mangling."""
        code = '''
class BankAccount:
    def __init__(self, initial_balance):
        self.__balance = initial_balance
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            return True
        return False
    
    def withdraw(self, amount):
        if amount > 0 and amount <= self.__balance:
            self.__balance -= amount
            return True
        return False
    
    def get_balance(self):
        return self.__balance
    
    def _internal_method(self):
        return "This is protected"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        BankAccount = globals_dict['BankAccount']
        account = BankAccount(100)
        
        # Test public interface
        assert account.get_balance() == 100
        assert account.deposit(50) is True
        assert account.get_balance() == 150
        assert account.withdraw(30) is True
        assert account.get_balance() == 120
        
        # Test private attribute access (should be mangled)
        assert not hasattr(account, '__balance')
        assert hasattr(account, '_BankAccount__balance')
        
        # Test validation
        assert account.withdraw(200) is False  # Insufficient funds
        assert account.deposit(-10) is False   # Negative amount
    
    def test_property_based_encapsulation(self):
        """Test encapsulation using properties."""
        code = '''
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero is not possible")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9
    
    @property
    def kelvin(self):
        return self._celsius + 273.15
    
    @kelvin.setter
    def kelvin(self, value):
        self.celsius = value - 273.15
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Temperature = globals_dict['Temperature']
        temp = Temperature(25)
        
        # Test celsius
        assert temp.celsius == 25
        assert abs(temp.fahrenheit - 77) < 0.1
        assert abs(temp.kelvin - 298.15) < 0.1
        
        # Test fahrenheit setter
        temp.fahrenheit = 100
        assert abs(temp.celsius - 37.78) < 0.1
        
        # Test kelvin setter
        temp.kelvin = 300
        assert abs(temp.celsius - 26.85) < 0.1
        
        # Test validation
        with pytest.raises(ValueError):
            temp.celsius = -300


class TestAbstractionExercises:
    """Test cases for abstraction exercises."""
    
    def test_abstract_base_class(self):
        """Test abstract base class implementation."""
        code = '''
from abc import ABC, abstractmethod

class Animal(ABC):
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def make_sound(self):
        pass
    
    @abstractmethod
    def move(self):
        pass
    
    def sleep(self):
        return f"{self.name} is sleeping"

class Dog(Animal):
    def make_sound(self):
        return f"{self.name} barks"
    
    def move(self):
        return f"{self.name} runs"

class Bird(Animal):
    def make_sound(self):
        return f"{self.name} chirps"
    
    def move(self):
        return f"{self.name} flies"
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Animal = globals_dict['Animal']
        Dog = globals_dict['Dog']
        Bird = globals_dict['Bird']
        
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            Animal("Generic")
        
        # Can instantiate concrete classes
        dog = Dog("Buddy")
        bird = Bird("Tweety")
        
        assert dog.make_sound() == "Buddy barks"
        assert dog.move() == "Buddy runs"
        assert dog.sleep() == "Buddy is sleeping"
        
        assert bird.make_sound() == "Tweety chirps"
        assert bird.move() == "Tweety flies"
        assert bird.sleep() == "Tweety is sleeping"
    
    def test_interface_like_behavior(self):
        """Test interface-like behavior using abstract methods."""
        code = '''
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self):
        pass
    
    @abstractmethod
    def get_area(self):
        pass

class Rectangle(Drawable):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def draw(self):
        return f"Drawing rectangle {self.width}x{self.height}"
    
    def get_area(self):
        return self.width * self.height

class Circle(Drawable):
    def __init__(self, radius):
        self.radius = radius
    
    def draw(self):
        return f"Drawing circle with radius {self.radius}"
    
    def get_area(self):
        return 3.14159 * self.radius ** 2

def draw_shapes(shapes):
    results = []
    for shape in shapes:
        results.append({
            'draw': shape.draw(),
            'area': shape.get_area()
        })
    return results
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        Rectangle = globals_dict['Rectangle']
        Circle = globals_dict['Circle']
        draw_shapes = globals_dict['draw_shapes']
        
        shapes = [
            Rectangle(5, 10),
            Circle(3)
        ]
        
        results = draw_shapes(shapes)
        
        assert len(results) == 2
        assert results[0]['area'] == 50
        assert abs(results[1]['area'] - 28.274) < 0.01


class TestOOPEvaluator:
    """Test cases for OOP code evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create an OOP evaluator instance."""
        return OOPEvaluator()
    
    def test_evaluate_class_definition(self, evaluator):
        """Test evaluation of class definition."""
        code = '''
class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, I'm {self.name}"
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert 'Person' in result['globals']
        
        # Test class instantiation
        Person = result['globals']['Person']
        person = Person("Alice")
        assert person.greet() == "Hello, I'm Alice"
    
    def test_evaluate_inheritance(self, evaluator):
        """Test evaluation of inheritance."""
        code = '''
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def bark(self):
        return f"{self.name} barks"
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        Dog = result['globals']['Dog']
        dog = Dog("Buddy")
        
        assert dog.name == "Buddy"
        assert dog.bark() == "Buddy barks"
        assert isinstance(dog, result['globals']['Animal'])
    
    def test_check_class_structure(self, evaluator):
        """Test checking class structure requirements."""
        code = '''
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
    
    def get_result(self):
        return self.result
'''
        
        requirements = {
            'class_name': 'Calculator',
            'required_methods': ['__init__', 'add', 'get_result'],
            'required_attributes': ['result']
        }
        
        result = evaluator.check_class_structure(code, requirements)
        
        assert result['success'] is True
        assert result['class_found'] is True
        assert all(method in result['methods_found'] for method in requirements['required_methods'])
    
    def test_check_inheritance_chain(self, evaluator):
        """Test checking inheritance relationships."""
        code = '''
class Vehicle:
    pass

class Car(Vehicle):
    pass

class SportsCar(Car):
    pass
'''
        
        result = evaluator.check_inheritance(code, 'SportsCar', ['Car', 'Vehicle'])
        
        assert result['success'] is True
        assert result['inheritance_correct'] is True


@pytest.mark.integration
class TestOOPIntegration:
    """Integration tests for OOP exercises."""
    
    @pytest.mark.asyncio
    async def test_complete_oop_exercise_workflow(self):
        """Test complete workflow of solving an OOP exercise."""
        # This would test the entire flow from exercise retrieval
        # to solution evaluation for OOP concepts
        pass


if __name__ == '__main__':
    pytest.main([__file__])