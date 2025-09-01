"""
Base classes and utilities for the Advanced Python module.
"""

from typing import Dict, List, Any
from python_mastery_hub.core import LearningModule


class AdvancedConcepts(LearningModule):
    """Interactive learning module for Advanced Python concepts."""
    
    def __init__(self):
        super().__init__(
            name="Advanced Python Concepts",
            description="Master advanced Python features like decorators, generators, metaclasses, and more",
            difficulty="advanced"
        )
    
    def _setup_module(self) -> None:
        """Setup examples and exercises for advanced Python concepts."""
        # Import demonstrations lazily to avoid circular imports
        from .decorators import DecoratorsDemo
        from .generators import GeneratorsDemo
        from .context_managers import ContextManagersDemo
        from .metaclasses import MetaclassesDemo
        from .descriptors import DescriptorsDemo
        
        # Initialize demonstrations
        self.decorators_demo = DecoratorsDemo()
        self.generators_demo = GeneratorsDemo()
        self.context_managers_demo = ContextManagersDemo()
        self.metaclasses_demo = MetaclassesDemo()
        self.descriptors_demo = DescriptorsDemo()
        
        # Aggregate examples from all demonstrations
        self.examples = {
            "decorators": self.decorators_demo.examples,
            "generators": self.generators_demo.examples,
            "context_managers": self.context_managers_demo.examples,
            "metaclasses": self.metaclasses_demo.examples,
            "descriptors": self.descriptors_demo.examples,
        }
        
        # Aggregate exercises from all demonstrations
        self.exercises = []
        self.exercises.extend(self.decorators_demo.exercises)
        self.exercises.extend(self.generators_demo.exercises)
        self.exercises.extend(self.context_managers_demo.exercises)
        self.exercises.extend(self.metaclasses_demo.exercises)
        self.exercises.extend(self.descriptors_demo.exercises)
    
    def get_topics(self) -> List[str]:
        """Return list of topics covered in this module."""
        return ["decorators", "generators", "context_managers", "metaclasses", "descriptors"]
    
    def demonstrate(self, topic: str) -> Dict[str, Any]:
        """Demonstrate a specific topic with examples."""
        if topic not in self.examples:
            raise ValueError(f"Topic '{topic}' not found in advanced module")
        
        # Get the appropriate demo instance
        demo_map = {
            "decorators": self.decorators_demo,
            "generators": self.generators_demo,
            "context_managers": self.context_managers_demo,
            "metaclasses": self.metaclasses_demo,
            "descriptors": self.descriptors_demo,
        }
        
        demo = demo_map[topic]
        
        return {
            "topic": topic,
            "examples": self.examples[topic],
            "explanation": demo.get_explanation(),
            "best_practices": demo.get_best_practices(),
        }


class TopicDemo:
    """Base class for topic-specific demonstrations."""
    
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.examples = {}
        self.exercises = []
        self._setup_examples()
        self._setup_exercises()
    
    def _setup_examples(self) -> None:
        """Setup examples for this topic. Override in subclasses."""
        pass
    
    def _setup_exercises(self) -> None:
        """Setup exercises for this topic. Override in subclasses."""
        pass
    
    def get_explanation(self) -> str:
        """Get explanation for this topic. Override in subclasses."""
        return f"No explanation available for {self.topic_name}"
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for this topic. Override in subclasses."""
        return []
    
    def demonstrate(self, example_name: str = None) -> Dict[str, Any]:
        """Demonstrate specific example or all examples."""
        if example_name:
            if example_name not in self.examples:
                raise ValueError(f"Example '{example_name}' not found in {self.topic_name}")
            return self.examples[example_name]
        
        return {
            "topic": self.topic_name,
            "examples": self.examples,
            "explanation": self.get_explanation(),
            "best_practices": self.get_best_practices(),
        }