"""
Core OOP learning module class and main functionality.
"""

from typing import Dict, List, Any
from python_mastery_hub.core import LearningModule

from .examples.classes_examples import get_classes_examples
from .examples.inheritance_examples import get_inheritance_examples
from .examples.polymorphism_examples import get_polymorphism_examples
from .examples.encapsulation_examples import get_encapsulation_examples
from .examples.design_patterns_examples import get_design_patterns_examples

from .exercises.library_exercise import get_library_exercise
from .exercises.employee_hierarchy_exercise import get_employee_hierarchy_exercise
from .exercises.shape_calculator_exercise import get_shape_calculator_exercise
from .exercises.observer_pattern_exercise import get_observer_pattern_exercise


class OOPConcepts(LearningModule):
    """Interactive learning module for Object-Oriented Programming."""
    
    def __init__(self):
        super().__init__(
            name="Object-Oriented Programming",
            description="Master OOP concepts with classes, inheritance, polymorphism, and design patterns",
            difficulty="intermediate"
        )
    
    def _setup_module(self) -> None:
        """Setup examples and exercises for OOP concepts."""
        self.examples = {
            "classes_and_objects": get_classes_examples(),
            "inheritance": get_inheritance_examples(),
            "polymorphism": get_polymorphism_examples(),
            "encapsulation": get_encapsulation_examples(),
            "design_patterns": get_design_patterns_examples(),
        }
        
        self.exercises = [
            {
                "topic": "classes_and_objects",
                "title": "Build a Library System",
                "description": "Create classes for books, authors, and library management",
                "difficulty": "medium",
                "function": get_library_exercise
            },
            {
                "topic": "inheritance",
                "title": "Employee Hierarchy",
                "description": "Design an employee system with different types and inheritance",
                "difficulty": "medium",
                "function": get_employee_hierarchy_exercise
            },
            {
                "topic": "polymorphism",
                "title": "Shape Calculator",
                "description": "Create different shapes with polymorphic area calculations",
                "difficulty": "hard",
                "function": get_shape_calculator_exercise
            },
            {
                "topic": "design_patterns",
                "title": "Implement Observer Pattern",
                "description": "Build a news publisher-subscriber system using Observer pattern",
                "difficulty": "hard",
                "function": get_observer_pattern_exercise
            },
        ]
    
    def get_topics(self) -> List[str]:
        """Return list of topics covered in this module."""
        return ["classes_and_objects", "inheritance", "polymorphism", "encapsulation", "design_patterns"]
    
    def demonstrate(self, topic: str) -> Dict[str, Any]:
        """Demonstrate a specific topic with examples."""
        if topic not in self.examples:
            raise ValueError(f"Topic '{topic}' not found in OOP module")
        
        return {
            "topic": topic,
            "examples": self.examples[topic],
            "explanation": self._get_topic_explanation(topic),
            "best_practices": self._get_best_practices(topic),
        }
    
    def _get_topic_explanation(self, topic: str) -> str:
        """Get detailed explanation for a topic."""
        explanations = {
            "classes_and_objects": "Classes are blueprints for creating objects (instances) with attributes and methods. Objects encapsulate data and behavior.",
            "inheritance": "Inheritance allows classes to inherit attributes and methods from parent classes, promoting code reuse and creating hierarchies.",
            "polymorphism": "Polymorphism enables objects of different types to be treated uniformly through a common interface or base class.",
            "encapsulation": "Encapsulation controls access to object internals, hiding implementation details and providing controlled interfaces.",
            "design_patterns": "Design patterns are reusable solutions to common problems in software design, promoting best practices and maintainability."
        }
        return explanations.get(topic, "No explanation available")
    
    def _get_best_practices(self, topic: str) -> List[str]:
        """Get best practices for a topic."""
        practices = {
            "classes_and_objects": [
                "Use clear, descriptive class names in PascalCase",
                "Keep classes focused on a single responsibility",
                "Implement __str__ and __repr__ methods for better debugging",
                "Use docstrings to document classes and methods",
                "Initialize all attributes in __init__"
            ],
            "inheritance": [
                "Prefer composition over inheritance when possible",
                "Use super() to call parent methods properly",
                "Keep inheritance hierarchies shallow and logical",
                "Override methods meaningfully, don't just change behavior arbitrarily",
                "Use abstract base classes to define interfaces"
            ],
            "polymorphism": [
                "Design interfaces before implementations",
                "Use duck typing when appropriate",
                "Implement abstract methods in abstract base classes",
                "Follow the Liskov Substitution Principle",
                "Use protocols for structural typing"
            ],
            "encapsulation": [
                "Use single underscore for protected members",
                "Use double underscore for private members sparingly",
                "Provide public interfaces for accessing private data",
                "Validate input in setter methods",
                "Use properties for computed attributes"
            ],
            "design_patterns": [
                "Learn common patterns but don't overuse them",
                "Choose the right pattern for the problem",
                "Keep patterns simple and understandable",
                "Document pattern usage in code comments",
                "Consider Python-specific alternatives to traditional patterns"
            ]
        }
        return practices.get(topic, [])