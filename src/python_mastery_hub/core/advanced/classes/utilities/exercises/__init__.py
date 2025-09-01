"""
Exercise implementations for the Advanced Python module.

This package contains standalone exercise implementations that demonstrate
advanced Python concepts through practical, hands-on projects.
"""

from .caching_decorator import CachingDecoratorExercise
from .file_pipeline import FilePipelineExercise
from .transaction_manager import TransactionManagerExercise
from .orm_metaclass import ORMMetaclassExercise

__all__ = [
    'CachingDecoratorExercise',
    'FilePipelineExercise', 
    'TransactionManagerExercise',
    'ORMMetaclassExercise'
]