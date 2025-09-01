"""
Data Structures Learning Module.

Comprehensive coverage of Python data structures including built-in collections,
custom implementations, and advanced data structure concepts.
"""

from typing import Dict, List, Any
from python_mastery_hub.core import LearningModule

# Import example modules
from .examples.builtin_examples import BuiltinExamples
from .examples.advanced_examples import AdvancedExamples
from .examples.custom_examples import CustomExamples
from .examples.performance_examples import PerformanceExamples
from .examples.applications_examples import ApplicationsExamples

# Import exercise modules
from .exercises.linkedlist import LinkedListExercise
from .exercises.bst import BSTExercise
from .exercises.cache import CacheExercise

# Import utilities
from .utils.explanations import EXPLANATIONS
from .utils.best_practices import BEST_PRACTICES
from .config.topics import TOPICS_CONFIG


class DataStructures(LearningModule):
    """Interactive learning module for Data Structures."""
    
    def __init__(self):
        super().__init__(
            name="Data Structures & Collections",
            description="Master Python data structures from built-ins to custom implementations",
            difficulty="intermediate"
        )
        self._setup_module()
    
    def _setup_module(self) -> None:
        """Setup examples and exercises for data structures."""
        self.examples = {
            "built_in_collections": {
                "list_operations": BuiltinExamples.get_list_operations(),
                "dictionary_operations": BuiltinExamples.get_dictionary_operations(),
                "set_operations": BuiltinExamples.get_set_operations(),
            },
            "advanced_collections": {
                "collections_module": AdvancedExamples.get_collections_module(),
            },
            "custom_structures": {
                "linked_list_implementation": CustomExamples.get_linked_list_implementation(),
                "stack_and_queue": CustomExamples.get_stack_and_queue(),
            },
            "performance_analysis": {
                "time_complexity_analysis": PerformanceExamples.get_time_complexity_analysis(),
            },
            "practical_applications": {
                "real_world_applications": ApplicationsExamples.get_real_world_applications(),
            },
        }
        
        self.exercises = [
            {
                "topic": "custom_structures",
                "title": "Implement a LinkedList",
                "description": "Build a complete linked list with all standard operations",
                "difficulty": "medium",
                "function": LinkedListExercise.get_exercise
            },
            {
                "topic": "custom_structures", 
                "title": "Build a Binary Search Tree",
                "description": "Implement a BST with insertion, deletion, and traversal",
                "difficulty": "hard",
                "function": BSTExercise.get_exercise
            },
            {
                "topic": "advanced_collections",
                "title": "Design a Cache System",
                "description": "Build an LRU cache using OrderedDict and custom logic",
                "difficulty": "hard",
                "function": CacheExercise.get_exercise
            }
        ]
    
    def get_topics(self) -> List[str]:
        """Return list of topics covered in this module."""
        return list(TOPICS_CONFIG.keys())
    
    def demonstrate(self, topic: str) -> Dict[str, Any]:
        """Demonstrate a specific topic with examples."""
        if topic not in self.examples:
            raise ValueError(f"Topic '{topic}' not found in data structures module")
        
        return {
            "topic": topic,
            "examples": self.examples[topic],
            "explanation": EXPLANATIONS.get(topic, "No explanation available"),
            "best_practices": BEST_PRACTICES.get(topic, []),
        }


# Make the module importable
__all__ = ["DataStructures"]