"""
Object-Oriented Programming Learning Module.

This module provides comprehensive coverage of OOP concepts including classes,
inheritance, polymorphism, encapsulation, and design patterns.
"""

from .core import OOPConcepts
from .examples import (
    get_classes_examples,
    get_inheritance_examples,
    get_polymorphism_examples,
    get_encapsulation_examples,
    get_design_patterns_examples
)
from .exercises import (
    get_library_exercise,
    get_employee_hierarchy_exercise,
    get_shape_calculator_exercise,
    get_observer_pattern_exercise
)

# Main module class
def create_oop_module():
    """Create and return the OOP learning module."""
    return OOPConcepts()

# Convenience functions
def get_all_topics():
    """Get list of all OOP topics."""
    return ["classes_and_objects", "inheritance", "polymorphism", "encapsulation", "design_patterns"]

def demonstrate_topic(topic: str):
    """Demonstrate a specific OOP topic."""
    module = create_oop_module()
    return module.demonstrate(topic)

__all__ = [
    'OOPConcepts',
    'create_oop_module',
    'demonstrate_topic',
    'get_all_topics',
    'get_classes_examples',
    'get_inheritance_examples', 
    'get_polymorphism_examples',
    'get_encapsulation_examples',
    'get_design_patterns_examples',
    'get_library_exercise',
    'get_employee_hierarchy_exercise',
    'get_shape_calculator_exercise',
    'get_observer_pattern_exercise'
]