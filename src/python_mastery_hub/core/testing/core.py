"""
Core Testing class implementation.

Main class for the Testing learning module with setup and topic management.
"""

from typing import Dict, List, Any
from python_mastery_hub.core import LearningModule
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


class Testing(LearningModule):
    """Interactive learning module for Testing in Python."""
    
    def __init__(self):
        super().__init__(
            name="Testing",
            description="Master testing with unittest, pytest, mocking, and TDD practices",
            difficulty="intermediate"
        )
    
    def _setup_module(self) -> None:
        """Setup examples and exercises for testing."""
        self.examples = {
            "unittest_basics": get_unittest_examples(),
            "pytest_fundamentals": get_pytest_examples(),
            "mocking_techniques": get_mocking_examples(),
            "tdd_approach": get_tdd_examples(),
            "integration_testing": get_integration_examples(),
            "performance_testing": get_performance_examples(),
        }
        
        self.exercises = [
            {
                "topic": "unittest_basics",
                "title": "Advanced Unit Testing",
                "description": "Master unittest framework with fixtures and advanced assertions",
                "difficulty": "medium",
                "function": get_unittest_exercise
            },
            {
                "topic": "tdd_approach",
                "title": "TDD Calculator Development", 
                "description": "Build a calculator using Test-Driven Development",
                "difficulty": "medium",
                "function": get_tdd_exercise
            },
            {
                "topic": "mocking_techniques",
                "title": "API Client Testing",
                "description": "Test an API client with comprehensive mocking",
                "difficulty": "hard",
                "function": get_mocking_exercise
            },
            {
                "topic": "integration_testing",
                "title": "Database Integration Tests",
                "description": "Create integration tests for database operations",
                "difficulty": "hard", 
                "function": get_integration_exercise
            }
        ]
    
    def get_topics(self) -> List[str]:
        """Return list of topics covered in this module."""
        return [
            "unittest_basics",
            "pytest_fundamentals", 
            "mocking_techniques",
            "tdd_approach",
            "integration_testing",
            "performance_testing"
        ]
    
    def demonstrate(self, topic: str) -> Dict[str, Any]:
        """Demonstrate a specific topic with examples."""
        if topic not in self.examples:
            raise ValueError(f"Topic '{topic}' not found in testing module")
        
        return {
            "topic": topic,
            "examples": self.examples[topic],
            "explanation": self._get_topic_explanation(topic),
            "best_practices": self._get_best_practices(topic),
        }
    
    def _get_topic_explanation(self, topic: str) -> str:
        """Get detailed explanation for a topic."""
        explanations = {
            "unittest_basics": "unittest provides a comprehensive framework for writing and running tests in Python with fixtures, assertions, and test organization",
            "pytest_fundamentals": "Pytest provides a more flexible and feature-rich testing framework than unittest with fixtures, parametrization, and plugins",
            "mocking_techniques": "Mocking allows testing code in isolation by replacing dependencies with controllable fake objects for reliable unit tests",
            "tdd_approach": "TDD follows Red-Green-Refactor cycle to ensure code quality and comprehensive test coverage through test-first development",
            "integration_testing": "Integration testing ensures that components work correctly together in real environments with actual databases and services",
            "performance_testing": "Performance testing ensures that code meets speed, memory, and scalability requirements under various load conditions"
        }
        return explanations.get(topic, "No explanation available")
    
    def _get_best_practices(self, topic: str) -> List[str]:
        """Get best practices for a topic."""
        practices = {
            "unittest_basics": [
                "Use descriptive test method names that explain what is being tested",
                "Follow Arrange-Act-Assert pattern for clear test structure",
                "Test one specific behavior at a time",
                "Use setUp and tearDown for consistent test fixtures",
                "Write tests for both positive and negative cases",
                "Use appropriate assertion methods for better error messages",
                "Keep tests independent and isolated from each other"
            ],
            "pytest_fundamentals": [
                "Use fixtures for test setup and teardown to reduce duplication",
                "Leverage parametrized tests for testing multiple inputs efficiently",
                "Use markers to organize and filter tests logically",
                "Write clear assertion messages for better debugging",
                "Keep tests independent and isolated from each other",
                "Use conftest.py for shared fixtures across test files",
                "Leverage pytest plugins for additional functionality"
            ],
            "mocking_techniques": [
                "Mock external dependencies, not internal business logic",
                "Use patch decorators for cleaner and more readable test code",
                "Verify mock calls to ensure correct interaction patterns",
                "Reset mocks between tests to avoid test interference",
                "Mock at the right level of abstraction for your tests",
                "Use spec parameter to catch interface changes early",
                "Mock return values and side effects appropriately"
            ],
            "tdd_approach": [
                "Write failing tests first (Red phase)",
                "Write minimal code to make tests pass (Green phase)",
                "Refactor with confidence knowing tests will catch regressions",
                "Keep tests simple, focused, and easy to understand",
                "Commit frequently during the TDD cycle",
                "Don't skip the refactoring phase",
                "Let tests drive your design decisions"
            ],
            "integration_testing": [
                "Test with real databases and external services when possible",
                "Use test containers for consistent and isolated environments",
                "Clean up test data between tests to avoid interference",
                "Test error conditions and edge cases thoroughly",
                "Monitor test execution time and optimize slow tests",
                "Use transactions for database test isolation",
                "Test the complete user workflow end-to-end"
            ],
            "performance_testing": [
                "Set realistic and measurable performance expectations",
                "Test with representative data sizes and scenarios",
                "Use profiling tools to identify actual bottlenecks",
                "Consider both time complexity and memory usage",
                "Automate performance regression testing in CI/CD",
                "Test under various load conditions",
                "Focus on the most critical performance paths first"
            ]
        }
        return practices.get(topic, [])