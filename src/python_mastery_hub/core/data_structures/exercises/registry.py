"""
Exercise registry and management for the Data Structures module.
"""

from typing import Dict, List, Any
from .linkedlist import LinkedListExercise
from .bst import BSTExercise
from .cache import CacheExercise


class ExerciseRegistry:
    """Centralized registry for all exercises."""
    
    # Exercise metadata
    EXERCISES = {
        "linkedlist": {
            "class": LinkedListExercise,
            "title": "Linked List Implementation",
            "difficulty": "medium",
            "topic": "custom_structures",
            "estimated_time": "1-2 hours",
            "prerequisites": ["basic Python", "OOP concepts"],
            "skills": ["pointer manipulation", "memory management", "data structure design"]
        },
        "bst": {
            "class": BSTExercise,
            "title": "Binary Search Tree",
            "difficulty": "hard", 
            "topic": "custom_structures",
            "estimated_time": "2-3 hours",
            "prerequisites": ["recursion", "tree concepts", "linkedlist exercise"],
            "skills": ["tree algorithms", "recursive thinking", "balanced structures"]
        },
        "cache": {
            "class": CacheExercise,
            "title": "LRU Cache System",
            "difficulty": "hard",
            "topic": "advanced_collections", 
            "estimated_time": "2-3 hours",
            "prerequisites": ["dictionaries", "OrderedDict", "threading basics"],
            "skills": ["system design", "performance optimization", "concurrency"]
        }
    }
    
    @classmethod
    def get_exercise(cls, name: str) -> Dict[str, Any]:
        """Get specific exercise by name."""
        if name not in cls.EXERCISES:
            available = list(cls.EXERCISES.keys())
            raise KeyError(f"Exercise '{name}' not found. Available: {available}")
        
        exercise_class = cls.EXERCISES[name]["class"]
        exercise_data = exercise_class.get_exercise()
        
        # Add metadata
        exercise_data.update({
            "name": name,
            "metadata": {k: v for k, v in cls.EXERCISES[name].items() if k != "class"}
        })
        
        return exercise_data
    
    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        """List all available exercises."""
        return [
            {
                "name": name,
                "title": info["title"],
                "difficulty": info["difficulty"],
                "topic": info["topic"],
                "estimated_time": info["estimated_time"]
            }
            for name, info in cls.EXERCISES.items()
        ]
    
    @classmethod
    def get_by_difficulty(cls, difficulty: str) -> List[str]:
        """Get exercise names by difficulty level."""
        return [
            name for name, info in cls.EXERCISES.items()
            if info["difficulty"] == difficulty
        ]
    
    @classmethod
    def get_by_topic(cls, topic: str) -> List[str]:
        """Get exercise names by topic."""
        return [
            name for name, info in cls.EXERCISES.items()
            if info["topic"] == topic
        ]
    
    @classmethod
    def get_learning_path(cls) -> List[Dict[str, Any]]:
        """Get recommended learning path."""
        recommended_order = ["linkedlist", "bst", "cache"]
        
        path = []
        for i, name in enumerate(recommended_order):
            exercise_info = cls.EXERCISES[name]
            path.append({
                "position": i + 1,
                "name": name,
                "title": exercise_info["title"],
                "difficulty": exercise_info["difficulty"],
                "estimated_time": exercise_info["estimated_time"],
                "prerequisites": exercise_info["prerequisites"],
                "skills": exercise_info["skills"]
            })
        
        return path
    
    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Get exercise collection statistics."""
        difficulties = [info["difficulty"] for info in cls.EXERCISES.values()]
        topics = [info["topic"] for info in cls.EXERCISES.values()]
        
        return {
            "total_exercises": len(cls.EXERCISES),
            "difficulties": {
                "easy": difficulties.count("easy"),
                "medium": difficulties.count("medium"),
                "hard": difficulties.count("hard")
            },
            "topics": {
                "custom_structures": topics.count("custom_structures"),
                "advanced_collections": topics.count("advanced_collections")
            }
        }