"""
Best practices for each Data Structures topic.
"""

from typing import Dict, List

BEST_PRACTICES: Dict[str, List[str]] = {
    "built_in_collections": [
        "Choose the right collection type for your use case",
        "Use sets for membership testing and removing duplicates",
        "Prefer dictionaries over lists for key-based lookups",
        "Use list comprehensions for simple transformations",
        "Consider memory usage for large collections",
        "Use tuple for immutable sequences and as dictionary keys",
        "Leverage dict.get() to avoid KeyError exceptions",
        "Use enumerate() instead of range(len()) for indexed iteration"
    ],
    
    "advanced_collections": [
        "Use defaultdict to avoid KeyError exceptions",
        "Use Counter for frequency analysis and statistical operations",
        "Use deque for efficient operations at both ends",
        "Use namedtuple for simple data containers with named fields",
        "Consider OrderedDict when insertion order matters (pre-Python 3.7)",
        "Use ChainMap for configuration management with multiple sources",
        "Import collections types at module level for better performance",
        "Choose the right specialized collection to avoid reimplementing common patterns"
    ],
    
    "custom_structures": [
        "Implement only when built-in types are insufficient",
        "Follow standard naming conventions and interfaces",
        "Provide clear documentation and usage examples",
        "Include proper error handling and boundary conditions",
        "Consider thread safety for concurrent use",
        "Implement __str__ and __repr__ for debugging",
        "Add type hints for better code documentation",
        "Test thoroughly with edge cases and large datasets"
    ],
    
    "performance_analysis": [
        "Profile before optimizing - measure actual performance",
        "Understand Big O notation for time complexity analysis",
        "Consider both time and space complexity trade-offs",
        "Benchmark with realistic data sizes and patterns",
        "Choose data structures based on most common operations",
        "Use timeit module for accurate micro-benchmarking",
        "Consider cache effects and memory locality",
        "Document performance characteristics in your code"
    ],
    
    "practical_applications": [
        "Start with built-in collections before custom implementations",
        "Consider using libraries like heapq for specialized needs",
        "Design for scalability and maintainability",
        "Document the rationale for data structure choices",
        "Test with edge cases and large datasets",
        "Consider thread safety in concurrent applications",
        "Use appropriate algorithms with your data structures",
        "Monitor memory usage in production applications"
    ]
}

def get_best_practices(topic: str) -> List[str]:
    """Get best practices for a specific topic."""
    return BEST_PRACTICES.get(topic, [])

def get_all_best_practices() -> Dict[str, List[str]]:
    """Get all available best practices."""
    return BEST_PRACTICES.copy()

def search_best_practices(keyword: str) -> Dict[str, List[str]]:
    """Search for best practices containing a keyword."""
    results = {}
    keyword_lower = keyword.lower()
    
    for topic, practices in BEST_PRACTICES.items():
        matching_practices = [
            practice for practice in practices 
            if keyword_lower in practice.lower()
        ]
        if matching_practices:
            results[topic] = matching_practices
    
    return results

def get_practices_by_difficulty() -> Dict[str, List[str]]:
    """Group practices by difficulty level."""
    beginner_keywords = ["basic", "simple", "start", "use", "choose"]
    intermediate_keywords = ["consider", "design", "implement", "understand"]
    advanced_keywords = ["optimize", "thread safety", "scalability", "monitor"]
    
    grouped = {"beginner": [], "intermediate": [], "advanced": []}
    
    for topic, practices in BEST_PRACTICES.items():
        for practice in practices:
            practice_lower = practice.lower()
            
            if any(keyword in practice_lower for keyword in beginner_keywords):
                grouped["beginner"].append(f"{topic}: {practice}")
            elif any(keyword in practice_lower for keyword in advanced_keywords):
                grouped["advanced"].append(f"{topic}: {practice}")
            else:
                grouped["intermediate"].append(f"{topic}: {practice}")
    
    return grouped