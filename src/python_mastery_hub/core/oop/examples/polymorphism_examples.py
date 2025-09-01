"""
Polymorphism examples for the OOP module.
Demonstrates method overriding, duck typing, and interface-based polymorphism.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod
import math


def get_polymorphism_examples() -> Dict[str, Any]:
    """Get comprehensive polymorphism examples."""
    return {
        "method_overriding": {
            "code": """
from abc import ABC, abstractmethod
import math

# Abstract base class defining interface
class Shape(ABC):
    '''Abstract base class for all shapes.'''
    
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def area(self):
        '''Calculate area - must be implemented by subclasses.'''
        pass
    
    @abstractmethod
    def perimeter(self):
        '''Calculate perimeter - must be implemented by subclasses.'''
        pass
    
    def describe(self):
        '''Common description method.'''
        return f"This is a {self.name}"
    
    def __str__(self):
        return f"{self.name}: Area = {self.area():.2f}, Perimeter = {self.perimeter():.2f}"

class Rectangle(Shape):
    '''Rectangle implementation.'''
    
    def __init__(self, width, height):
        super().__init__("Rectangle")
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    '''Circle implementation.'''
    
    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius
    
    def area(self):
        return math.pi * self.radius ** 2
    
    def perimeter(self):
        return 2 * math.pi * self.radius

class Triangle(Shape):
    '''Triangle implementation.'''
    
    def __init__(self, a, b, c):
        super().__init__("Triangle")
        self.a, self.b, self.c = a, b, c
    
    def area(self):
        # Using Heron's formula
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))
    
    def perimeter(self):
        return self.a + self.b + self.c

# Polymorphic function
def calculate_total_area(shapes):
    '''Calculate total area of different shapes.'''
    total = 0
    for shape in shapes:
        print(f"Processing {shape.name}: {shape.area():.2f}")
        total += shape.area()
    return total

def display_shapes(shapes):
    '''Display information about shapes polymorphically.'''
    for shape in shapes:
        print(shape)  # Calls __str__ method
        print(f"  Description: {shape.describe()}")

# Usage examples
print("=== Polymorphism in Action ===")
shapes = [
    Rectangle(5, 3),
    Circle(4),
    Triangle(3, 4, 5),
    Rectangle(2, 7)
]

print("\\n=== Shape Information ===")
display_shapes(shapes)

print("\\n=== Total Area Calculation ===")
total_area = calculate_total_area(shapes)
print(f"Total area of all shapes: {total_area:.2f}")
""",
            "output": "=== Polymorphism in Action ===\n\n=== Shape Information ===\nRectangle: Area = 15.00, Perimeter = 16.00\n  Description: This is a Rectangle\nCircle: Area = 50.27, Perimeter = 25.13\n  Description: This is a Circle\nTriangle: Area = 6.00, Perimeter = 12.00\n  Description: This is a Triangle\nRectangle: Area = 14.00, Perimeter = 18.00\n  Description: This is a Rectangle\n\n=== Total Area Calculation ===\nProcessing Rectangle: 15.00\nProcessing Circle: 50.27\nProcessing Triangle: 6.00\nProcessing Rectangle: 14.00\nTotal area of all shapes: 85.27",
            "explanation": "Polymorphism allows objects of different types to be treated uniformly through a common interface"
        },
        
        "duck_typing": {
            "code": """
# Duck typing: "If it walks like a duck and quacks like a duck, it's a duck"

class Duck:
    def swim(self):
        return "Duck swimming"
    
    def quack(self):
        return "Quack!"

class Swan:
    def swim(self):
        return "Swan swimming gracefully"
    
    def quack(self):
        return "Honk!"

class Robot:
    def swim(self):
        return "Robot swimming with propellers"
    
    def quack(self):
        return "Beep boop quack!"

class Fish:
    def swim(self):
        return "Fish swimming underwater"
    
    # No quack method - will cause issues in some scenarios

# Polymorphic functions using duck typing
def make_it_swim(swimmer):
    '''Any object with swim() method can be used.'''
    return swimmer.swim()

def pond_sounds(creatures):
    '''Calls quack() on all creatures.'''
    sounds = []
    for creature in creatures:
        if hasattr(creature, 'quack'):
            sounds.append(creature.quack())
        else:
            sounds.append(f"{type(creature).__name__} is silent")
    return sounds

def water_activities(creatures):
    '''Demonstrates both swimming and quacking.'''
    for creature in creatures:
        print(f"{type(creature).__name__}:")
        print(f"  Swimming: {creature.swim()}")
        
        # Safe attribute access
        if hasattr(creature, 'quack'):
            print(f"  Sound: {creature.quack()}")
        else:
            print(f"  Sound: Silent")

# Usage examples
print("=== Duck Typing Examples ===")
creatures = [Duck(), Swan(), Robot(), Fish()]

print("\\n=== Swimming Activities ===")
for creature in creatures:
    print(f"{type(creature).__name__}: {make_it_swim(creature)}")

print("\\n=== Pond Sounds ===")
sounds = pond_sounds(creatures)
for i, sound in enumerate(sounds):
    creature_type = type(creatures[i]).__name__
    print(f"{creature_type}: {sound}")

print("\\n=== Complete Water Activities ===")
water_activities(creatures)

# Protocol example (Python 3.8+)
from typing import Protocol

class Swimmer(Protocol):
    '''Protocol defining swimming interface.'''
    def swim(self) -> str:
        ...

class Quacker(Protocol):
    '''Protocol defining quacking interface.'''
    def quack(self) -> str:
        ...

def enhanced_water_activity(swimmer: Swimmer, quacker: Quacker):
    '''Type-hinted function using protocols.'''
    return f"Activity: {swimmer.swim()} and {quacker.quack()}"

# This works with any objects that implement the protocols
duck = Duck()
result = enhanced_water_activity(duck, duck)
print(f"\\n=== Protocol Usage ===")
print(result)
""",
            "output": "=== Duck Typing Examples ===\n\n=== Swimming Activities ===\nDuck: Duck swimming\nSwan: Swan swimming gracefully\nRobot: Robot swimming with propellers\nFish: Fish swimming underwater\n\n=== Pond Sounds ===\nDuck: Quack!\nSwan: Honk!\nRobot: Beep boop quack!\nFish: Fish is silent\n\n=== Complete Water Activities ===\nDuck:\n  Swimming: Duck swimming\n  Sound: Quack!\nSwan:\n  Swimming: Swan swimming gracefully\n  Sound: Honk!\nRobot:\n  Swimming: Robot swimming with propellers\n  Sound: Beep boop quack!\nFish:\n  Swimming: Fish swimming underwater\n  Sound: Silent\n\n=== Protocol Usage ===\nActivity: Duck swimming and Quack!",
            "explanation": "Duck typing allows polymorphism based on method availability rather than inheritance"
        },
        
        "operator_overloading": {
            "code": """
class Vector:
    '''2D Vector class demonstrating operator overloading.'''
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __add__(self, other):
        '''Vector addition.'''
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        elif isinstance(other, (int, float)):
            return Vector(self.x + other, self.y + other)
        return NotImplemented
    
    def __radd__(self, other):
        '''Reverse addition (when Vector is on right side).'''
        return self.__add__(other)
    
    def __sub__(self, other):
        '''Vector subtraction.'''
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        elif isinstance(other, (int, float)):
            return Vector(self.x - other, self.y - other)
        return NotImplemented
    
    def __mul__(self, scalar):
        '''Scalar multiplication.'''
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented
    
    def __rmul__(self, scalar):
        '''Reverse scalar multiplication.'''
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        '''Scalar division.'''
        if isinstance(scalar, (int, float)) and scalar != 0:
            return Vector(self.x / scalar, self.y / scalar)
        return NotImplemented
    
    def __eq__(self, other):
        '''Equality comparison.'''
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False
    
    def __lt__(self, other):
        '''Less than comparison (by magnitude).'''
        if isinstance(other, Vector):
            return self.magnitude() < other.magnitude()
        return NotImplemented
    
    def __len__(self):
        '''Return magnitude as integer.'''
        return int(self.magnitude())
    
    def __getitem__(self, index):
        '''Allow indexing: v[0] = x, v[1] = y.'''
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Vector index out of range")
    
    def __setitem__(self, index, value):
        '''Allow assignment: v[0] = new_x.'''
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("Vector index out of range")
    
    def magnitude(self):
        '''Calculate vector magnitude.'''
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def dot(self, other):
        '''Dot product with another vector.'''
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        return NotImplemented

# Usage examples
print("=== Operator Overloading ===")

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(f"v1 = {v1}")
print(f"v2 = {v2}")

print("\\n=== Arithmetic Operations ===")
print(f"v1 + v2 = {v1 + v2}")
print(f"v1 - v2 = {v1 - v2}")
print(f"v1 * 2 = {v1 * 2}")
print(f"3 * v1 = {3 * v1}")
print(f"v1 / 2 = {v1 / 2}")

print("\\n=== Scalar Operations ===")
print(f"v1 + 5 = {v1 + 5}")
print(f"10 + v1 = {10 + v1}")

print("\\n=== Comparison Operations ===")
v3 = Vector(3, 4)  # Same as v1
print(f"v1 == v3: {v1 == v3}")
print(f"v1 == v2: {v1 == v2}")
print(f"v1 < v2: {v1 < v2}")

print("\\n=== Special Operations ===")
print(f"len(v1): {len(v1)}")
print(f"v1.magnitude(): {v1.magnitude():.2f}")
print(f"v1.dot(v2): {v1.dot(v2)}")

print("\\n=== Indexing ===")
print(f"v1[0] = {v1[0]}, v1[1] = {v1[1]}")
v1[0] = 10
print(f"After v1[0] = 10: {v1}")
""",
            "output": "=== Operator Overloading ===\nv1 = Vector(3, 4)\nv2 = Vector(1, 2)\n\n=== Arithmetic Operations ===\nv1 + v2 = Vector(4, 6)\nv1 - v2 = Vector(2, 2)\nv1 * 2 = Vector(6, 8)\n3 * v1 = Vector(9, 12)\nv1 / 2 = Vector(1.5, 2.0)\n\n=== Scalar Operations ===\nv1 + 5 = Vector(8, 9)\n10 + v1 = Vector(13, 14)\n\n=== Comparison Operations ===\nv1 == v3: True\nv1 == v2: False\nv1 < v2: False\n\n=== Special Operations ===\nlen(v1): 5\nv1.magnitude(): 5.00\nv1.dot(v2): 11\n\n=== Indexing ===\nv1[0] = 3, v1[1] = 4\nAfter v1[0] = 10: Vector(10, 4)",
            "explanation": "Operator overloading allows custom classes to work with Python's built-in operators in meaningful ways"
        }
    }