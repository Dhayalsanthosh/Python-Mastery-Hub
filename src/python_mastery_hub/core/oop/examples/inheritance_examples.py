"""
Inheritance examples for the OOP module.
Demonstrates single inheritance, multiple inheritance, and method resolution order.
"""

from typing import Dict, Any


def get_inheritance_examples() -> Dict[str, Any]:
    """Get comprehensive inheritance examples."""
    return {
        "basic_inheritance": {
            "code": """
# Base class (parent)
class Animal:
    '''Base class for all animals.'''
    
    def __init__(self, name, species):
        self.name = name
        self.species = species
        self.energy = 100
    
    def eat(self, food):
        '''Animal eating behavior.'''
        self.energy += 10
        return f"{self.name} eats {food} and gains energy"
    
    def sleep(self):
        '''Animal sleeping behavior.'''
        self.energy = 100
        return f"{self.name} sleeps and restores energy"
    
    def make_sound(self):
        '''Generic animal sound - to be overridden.'''
        return f"{self.name} makes a sound"
    
    def __str__(self):
        return f"{self.name} the {self.species} (Energy: {self.energy})"

# Derived classes (children)
class Dog(Animal):
    '''Dog class inheriting from Animal.'''
    
    def __init__(self, name, breed):
        super().__init__(name, "Dog")  # Call parent constructor
        self.breed = breed
        self.tricks = []
    
    def make_sound(self):  # Override parent method
        '''Dog-specific sound.'''
        return f"{self.name} barks: Woof! Woof!"
    
    def learn_trick(self, trick):
        '''Dog-specific behavior.'''
        self.tricks.append(trick)
        return f"{self.name} learned {trick}"
    
    def perform_trick(self):
        '''Perform a random trick.'''
        if self.tricks:
            import random
            trick = random.choice(self.tricks)
            self.energy -= 5
            return f"{self.name} performs {trick}!"
        return f"{self.name} doesn't know any tricks yet"

class Cat(Animal):
    '''Cat class inheriting from Animal.'''
    
    def __init__(self, name, indoor=True):
        super().__init__(name, "Cat")
        self.indoor = indoor
        self.lives = 9
    
    def make_sound(self):  # Override parent method
        '''Cat-specific sound.'''
        return f"{self.name} meows: Meow!"
    
    def climb(self):
        '''Cat-specific behavior.'''
        if self.indoor:
            return f"{self.name} climbs the cat tree"
        else:
            return f"{self.name} climbs a real tree"
    
    def use_life(self):
        '''Use one of nine lives.'''
        if self.lives > 0:
            self.lives -= 1
            return f"{self.name} used a life. {self.lives} lives remaining"
        return f"{self.name} has no lives left!"

# Usage examples
print("=== Creating Animals ===")
buddy = Dog("Buddy", "Golden Retriever")
whiskers = Cat("Whiskers", indoor=True)

print(buddy)
print(whiskers)

print("\\n=== Inherited Methods ===")
print(buddy.eat("kibble"))
print(whiskers.eat("fish"))

print("\\n=== Overridden Methods ===")
print(buddy.make_sound())
print(whiskers.make_sound())

print("\\n=== Specific Methods ===")
print(buddy.learn_trick("sit"))
print(buddy.learn_trick("roll over"))
print(buddy.perform_trick())

print(whiskers.climb())
print(whiskers.use_life())

# Check inheritance
print(f"\\n=== Inheritance Check ===")
print(f"Is Buddy an Animal? {isinstance(buddy, Animal)}")
print(f"Is Buddy a Dog? {isinstance(buddy, Dog)}")
print(f"Is Whiskers a Dog? {isinstance(whiskers, Dog)}")
""",
            "output": "=== Creating Animals ===\nBuddy the Dog (Energy: 100)\nWhiskers the Cat (Energy: 100)\n\n=== Inherited Methods ===\nBuddy eats kibble and gains energy\nWhiskers eats fish and gains energy\n\n=== Overridden Methods ===\nBuddy barks: Woof! Woof!\nWhiskers meows: Meow!\n\n=== Specific Methods ===\nBuddy learned sit\nBuddy learned roll over\nBuddy performs sit!\nWhiskers climbs the cat tree\nWhiskers used a life. 8 lives remaining\n\n=== Inheritance Check ===\nIs Buddy an Animal? True\nIs Buddy a Dog? True\nIs Whiskers a Dog? False",
            "explanation": "Inheritance allows classes to inherit attributes and methods from parent classes while adding their own specific features"
        },
        
        "multiple_inheritance": {
            "code": """
# Multiple inheritance with mixins
class Flyable:
    '''Mixin for flying behavior.'''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.altitude = 0
    
    def fly(self, height):
        '''Flying behavior.'''
        self.altitude = height
        return f"Flying at {height} feet"
    
    def land(self):
        '''Landing behavior.'''
        self.altitude = 0
        return "Landed safely"

class Swimmable:
    '''Mixin for swimming behavior.'''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.depth = 0
    
    def swim(self, depth):
        '''Swimming behavior.'''
        self.depth = depth
        return f"Swimming at {depth} feet deep"
    
    def surface(self):
        '''Surface behavior.'''
        self.depth = 0
        return "Surfaced to the top"

class Bird(Animal, Flyable):
    '''Bird class with flying capability.'''
    
    def __init__(self, name, species, wingspan):
        super().__init__(name, species)
        self.wingspan = wingspan
    
    def make_sound(self):
        return f"{self.name} chirps: Tweet tweet!"

class Duck(Bird, Swimmable):
    '''Duck class that can both fly and swim.'''
    
    def __init__(self, name, color):
        super().__init__(name, "Duck", wingspan=24)
        self.color = color
    
    def make_sound(self):
        return f"{self.name} quacks: Quack quack!"
    
    def dive(self):
        '''Duck-specific diving behavior.'''
        return f"{self.name} dives underwater to find food"

# Usage examples
print("=== Multiple Inheritance ===")
eagle = Bird("Eagle", "Bald Eagle", wingspan=80)
donald = Duck("Donald", "white")

print(eagle)
print(donald)

print("\\n=== Flying Behavior ===")
print(eagle.fly(1000))
print(donald.fly(500))

print("\\n=== Swimming Behavior ===")
print(donald.swim(5))
print(donald.dive())
print(donald.surface())

print("\\n=== Method Resolution Order ===")
print(f"Duck MRO: {[cls.__name__ for cls in Duck.__mro__]}")
""",
            "output": "=== Multiple Inheritance ===\nEagle the Bald Eagle (Energy: 100)\nDonald the Duck (Energy: 100)\n\n=== Flying Behavior ===\nFlying at 1000 feet\nFlying at 500 feet\n\n=== Swimming Behavior ===\nSwimming at 5 feet deep\nDonald dives underwater to find food\nSurfaced to the top\n\n=== Method Resolution Order ===\nDuck MRO: ['Duck', 'Bird', 'Animal', 'Flyable', 'Swimmable', 'object']",
            "explanation": "Multiple inheritance allows classes to inherit from multiple parents, with MRO determining method lookup order"
        }
    }