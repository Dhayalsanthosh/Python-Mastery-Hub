"""
Topic configuration and metadata for the Data Structures module.
"""

from typing import Dict, List, Any

TOPICS_CONFIG: Dict[str, Dict[str, Any]] = {
    "built_in_collections": {
        "name": "Built-in Collections",
        "description": "Python's fundamental data structures: lists, dicts, sets, and tuples",
        "prerequisites": ["python_basics"],
        "difficulty": "beginner",
        "estimated_time": "2-3 hours",
        "subtopics": [
            "list_operations",
            "dictionary_operations", 
            "set_operations",
            "tuple_usage",
            "comprehensions"
        ]
    },
    
    "advanced_collections": {
        "name": "Advanced Collections",
        "description": "Specialized containers from the collections module",
        "prerequisites": ["built_in_collections"],
        "difficulty": "intermediate",
        "estimated_time": "2-3 hours",
        "subtopics": [
            "defaultdict",
            "counter",
            "deque",
            "namedtuple",
            "ordereddict",
            "chainmap"
        ]
    },
    
    "custom_structures": {
        "name": "Custom Data Structures",
        "description": "Implementing fundamental data structures from scratch",
        "prerequisites": ["built_in_collections"],
        "difficulty": "intermediate",
        "estimated_time": "4-5 hours",
        "subtopics": [
            "linked_lists",
            "stacks_queues",
            "trees",
            "graphs",
            "hash_tables"
        ]
    },
    
    "performance_analysis": {
        "name": "Performance Analysis",
        "description": "Understanding time and space complexity of data structures",
        "prerequisites": ["built_in_collections", "custom_structures"],
        "difficulty": "intermediate",
        "estimated_time": "2-3 hours",
        "subtopics": [
            "big_o_notation",
            "time_complexity",
            "space_complexity",
            "benchmarking",
            "optimization"
        ]
    },
    
    "practical_applications": {
        "name": "Practical Applications",
        "description": "Real-world use cases and problem-solving with data structures",
        "prerequisites": ["advanced_collections", "custom_structures"],
        "difficulty": "advanced",
        "estimated_time": "3-4 hours",
        "subtopics": [
            "caching_systems",
            "graph_algorithms",
            "text_processing",
            "task_scheduling",
            "data_analysis"
        ]
    }
}

def get_topic_order() -> List[str]:
    """Return recommended learning order for topics."""
    return [
        "built_in_collections",
        "advanced_collections", 
        "custom_structures",
        "performance_analysis",
        "practical_applications"
    ]

def get_topic_dependencies() -> Dict[str, List[str]]:
    """Return dependency mapping for topics."""
    dependencies = {}
    for topic, config in TOPICS_CONFIG.items():
        dependencies[topic] = config.get("prerequisites", [])
    return dependencies

def get_difficulty_levels() -> Dict[str, List[str]]:
    """Group topics by difficulty level."""
    levels = {"beginner": [], "intermediate": [], "advanced": []}
    for topic, config in TOPICS_CONFIG.items():
        difficulty = config.get("difficulty", "intermediate")
        if difficulty in levels:
            levels[difficulty].append(topic)
    return levels