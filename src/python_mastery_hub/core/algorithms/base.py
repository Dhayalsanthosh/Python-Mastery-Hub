"""
Base classes and utilities for the Algorithms module.
"""

from typing import Dict, List, Any
from python_mastery_hub.core import LearningModule


class Algorithms(LearningModule):
    """Interactive learning module for Algorithms."""
    
    def __init__(self):
        super().__init__(
            name="Algorithms & Problem Solving",
            description="Master fundamental algorithms and algorithmic thinking patterns",
            difficulty="intermediate"
        )
    
    def _setup_module(self) -> None:
        """Setup examples and exercises for algorithms."""
        # Import demonstrations lazily to avoid circular imports
        from .sorting import SortingAlgorithms
        from .searching import SearchingAlgorithms
        from .dynamic_programming import DynamicProgramming
        from .graph_algorithms import GraphAlgorithms
        from .algorithmic_patterns import AlgorithmicPatterns
        
        # Initialize demonstrations
        self.sorting_demo = SortingAlgorithms()
        self.searching_demo = SearchingAlgorithms()
        self.dp_demo = DynamicProgramming()
        self.graph_demo = GraphAlgorithms()
        self.patterns_demo = AlgorithmicPatterns()
        
        # Aggregate examples from all demonstrations
        self.examples = {
            "sorting_algorithms": self.sorting_demo.examples,
            "searching_algorithms": self.searching_demo.examples,
            "dynamic_programming": self.dp_demo.examples,
            "graph_algorithms": self.graph_demo.examples,
            "algorithmic_patterns": self.patterns_demo.examples,
        }
        
        # Aggregate exercises from all demonstrations
        self.exercises = []
        self.exercises.extend(self.sorting_demo.exercises)
        self.exercises.extend(self.searching_demo.exercises)
        self.exercises.extend(self.dp_demo.exercises)
        self.exercises.extend(self.graph_demo.exercises)
        self.exercises.extend(self.patterns_demo.exercises)
    
    def get_topics(self) -> List[str]:
        """Return list of topics covered in this module."""
        return ["sorting_algorithms", "searching_algorithms", "dynamic_programming", 
                "graph_algorithms", "algorithmic_patterns"]
    
    def demonstrate(self, topic: str) -> Dict[str, Any]:
        """Demonstrate a specific topic with examples."""
        if topic not in self.examples:
            raise ValueError(f"Topic '{topic}' not found in algorithms module")
        
        # Get the appropriate demo instance
        demo_map = {
            "sorting_algorithms": self.sorting_demo,
            "searching_algorithms": self.searching_demo,
            "dynamic_programming": self.dp_demo,
            "graph_algorithms": self.graph_demo,
            "algorithmic_patterns": self.patterns_demo,
        }
        
        demo = demo_map[topic]
        
        return {
            "topic": topic,
            "examples": self.examples[topic],
            "explanation": demo.get_explanation(),
            "best_practices": demo.get_best_practices(),
        }


class AlgorithmDemo:
    """Base class for algorithm-specific demonstrations."""
    
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