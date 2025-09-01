"""
Core learning modules for Python Mastery Hub.

This package contains all the interactive learning modules covering different
aspects of Python programming from basics to advanced topics.
"""

from typing import Dict, List, Type, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class LearningModule(ABC):
    """Abstract base class for all learning modules."""
    
    def __init__(self, name: str, description: str, difficulty: str):
        self.name = name
        self.description = description
        self.difficulty = difficulty  # "beginner", "intermediate", "advanced", "expert"
        self.examples: Dict[str, Any] = {}
        self.exercises: List[Dict[str, Any]] = []
        self._setup_module()
    
    @abstractmethod
    def _setup_module(self) -> None:
        """Setup the learning module with examples and exercises."""
        pass
    
    @abstractmethod
    def get_topics(self) -> List[str]:
        """Return list of topics covered in this module."""
        pass
    
    @abstractmethod
    def demonstrate(self, topic: str) -> Dict[str, Any]:
        """Demonstrate a specific topic with examples."""
        pass
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the module."""
        return {
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty,
            "topics": self.get_topics(),
            "example_count": len(self.examples),
            "exercise_count": len(self.exercises),
        }

# Import all learning modules
from python_mastery_hub.core.basics import BasicsConcepts
from python_mastery_hub.core.oop import OOPConcepts
from python_mastery_hub.core.advanced import AdvancedConcepts
from python_mastery_hub.core.data_structures import DataStructures
from python_mastery_hub.core.algorithms import Algorithms
from python_mastery_hub.core.async_programming import AsyncProgramming
from python_mastery_hub.core.web_development import WebDevelopment
from python_mastery_hub.core.data_science import DataScience
from python_mastery_hub.core.testing import TestingConcepts

# Registry of all available modules
MODULE_REGISTRY: Dict[str, Type[LearningModule]] = {
    "basics": BasicsConcepts,
    "oop": OOPConcepts,
    "advanced": AdvancedConcepts,
    "data_structures": DataStructures,
    "algorithms": Algorithms,
    "async_programming": AsyncProgramming,
    "web_development": WebDevelopment,
    "data_science": DataScience,
    "testing": TestingConcepts,
}

def get_module(module_name: str) -> LearningModule:
    """Get a learning module instance by name."""
    if module_name not in MODULE_REGISTRY:
        available = ", ".join(MODULE_REGISTRY.keys())
        raise ValueError(f"Module '{module_name}' not found. Available: {available}")
    
    return MODULE_REGISTRY[module_name]()

def list_modules() -> List[Dict[str, Any]]:
    """List all available learning modules with their information."""
    return [get_module(name).get_module_info() for name in MODULE_REGISTRY.keys()]

def get_learning_path(difficulty: str = "all") -> List[str]:
    """Get recommended learning path based on difficulty level."""
    paths = {
        "beginner": ["basics", "data_structures", "oop"],
        "intermediate": ["advanced", "algorithms", "testing"],
        "advanced": ["async_programming", "web_development", "data_science"],
        "all": [
            "basics", "data_structures", "oop", "advanced", 
            "algorithms", "testing", "async_programming", 
            "web_development", "data_science"
        ]
    }
    
    if difficulty not in paths:
        raise ValueError(f"Invalid difficulty: {difficulty}. Options: {list(paths.keys())}")
    
    return paths[difficulty]

__all__ = [
    "LearningModule",
    "MODULE_REGISTRY",
    "get_module",
    "list_modules", 
    "get_learning_path",
    "BasicsConcepts",
    "OOPConcepts",
    "AdvancedConcepts",
    "DataStructures",
    "Algorithms",
    "AsyncProgramming",
    "WebDevelopment",
    "DataScience",
    "TestingConcepts",
]