"""
Exercises module for Data Structures learning.

This module provides programming exercises for mastering data structures concepts.
Each exercise includes instructions, starter code, hints, and complete solutions.
"""

from .linkedlist import LinkedListExercise
from .bst import BSTExercise  
from .cache import CacheExercise
from .registry import ExerciseRegistry

# Simple convenience functions
def get_exercise(name: str):
    """Get exercise by name."""
    return ExerciseRegistry.get_exercise(name)

def list_exercises():
    """List all available exercises."""
    return ExerciseRegistry.list_all()

def get_learning_path():
    """Get recommended learning path."""
    return ExerciseRegistry.get_learning_path()

# Direct exercise access
def linkedlist_exercise():
    """Get the LinkedList exercise."""
    return get_exercise("linkedlist")

def bst_exercise():
    """Get the Binary Search Tree exercise."""
    return get_exercise("bst")

def cache_exercise():
    """Get the LRU Cache exercise."""
    return get_exercise("cache")

__all__ = [
    'LinkedListExercise',
    'BSTExercise', 
    'CacheExercise',
    'get_exercise',
    'list_exercises',
    'get_learning_path',
    'linkedlist_exercise',
    'bst_exercise',
    'cache_exercise'
]