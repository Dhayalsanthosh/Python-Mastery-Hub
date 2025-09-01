"""
Testing module - Clean import hub for all testing components.

This module provides comprehensive coverage of testing in Python including
unittest, pytest, mocking, TDD, integration testing, and performance testing.
"""

from .core import Testing
from .examples import (
    get_unittest_examples,
    get_pytest_examples,
    get_mocking_examples,
    get_tdd_examples,
    get_integration_examples,
    get_performance_examples
)
from .exercises import (
    get_unittest_exercise,
    get_tdd_exercise,
    get_mocking_exercise,
    get_integration_exercise
)

__all__ = [
    "Testing",
    # Examples
    "get_unittest_examples",
    "get_pytest_examples", 
    "get_mocking_examples",
    "get_tdd_examples",
    "get_integration_examples",
    "get_performance_examples",
    # Exercises
    "get_unittest_exercise",
    "get_tdd_exercise",
    "get_mocking_exercise",
    "get_integration_exercise"
]