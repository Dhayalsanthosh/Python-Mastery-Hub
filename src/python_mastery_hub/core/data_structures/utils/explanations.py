"""
Topic explanations for the Data Structures module.
"""

from typing import Dict

EXPLANATIONS: Dict[str, str] = {
    "built_in_collections": """
Python's built-in collections (list, dict, set, tuple) provide fundamental data storage 
and manipulation capabilities. These data structures are highly optimized and form the 
foundation of most Python programs:

- Lists: Ordered, mutable sequences supporting indexing and slicing
- Dictionaries: Key-value mappings providing fast lookups and flexible data organization
- Sets: Unordered collections of unique elements with mathematical set operations
- Tuples: Immutable sequences useful for fixed data and as dictionary keys

Understanding when and how to use each collection type is crucial for writing efficient 
and readable Python code. Each has different performance characteristics and use cases.
""",

    "advanced_collections": """
The collections module provides specialized container types that extend Python's built-in 
collections with additional functionality:

- defaultdict: Automatically creates missing values, eliminating KeyError exceptions
- Counter: Efficiently counts hashable objects and provides frequency analysis
- deque: Double-ended queue with O(1) operations at both ends
- namedtuple: Creates tuple subclasses with named fields for better code readability
- OrderedDict: Maintains insertion order (less critical in Python 3.7+)
- ChainMap: Combines multiple dictionaries into a single view

These collections solve common programming patterns more elegantly than basic types alone.
""",

    "custom_structures": """
Custom data structures help understand fundamental computer science concepts and provide 
solutions when built-in types are insufficient:

- Linked Lists: Dynamic structures demonstrating pointer-based memory management
- Stacks: LIFO (Last In, First Out) structures for function calls, parsing, and undo operations
- Queues: FIFO (First In, First Out) structures for scheduling and breadth-first algorithms
- Trees: Hierarchical structures for searching, sorting, and representing relationships
- Graphs: Network structures for modeling connections and pathfinding

Building these from scratch reinforces algorithmic thinking and memory management concepts.
""",

    "performance_analysis": """
Understanding time and space complexity helps choose the right data structure for optimal 
performance. Big O notation describes how algorithms scale with input size:

- Time Complexity: How execution time grows with input size
- Space Complexity: How memory usage grows with input size
- Common complexities: O(1), O(log n), O(n), O(n log n), O(n²)

Different operations on the same data structure can have different complexities. For example, 
list access is O(1) but search is O(n), while dict access and search are both O(1) average case.

Profiling and benchmarking with realistic data sizes validates theoretical analysis.
""",

    "practical_applications": """
Real-world applications demonstrate how data structures solve common programming problems 
efficiently:

- Caching Systems: LRU caches using OrderedDict for web applications and databases
- Graph Algorithms: BFS/DFS for social networks, pathfinding, and dependency resolution
- Text Processing: Tries for autocomplete, frequency analysis for natural language processing
- Task Scheduling: Priority queues for job scheduling and event-driven systems
- Data Analysis: Efficient aggregation and filtering using appropriate data structures

Understanding these patterns helps recognize when to apply specific data structures to 
solve complex problems elegantly and efficiently.
"""
}

def get_explanation(topic: str) -> str:
    """Get explanation for a specific topic."""
    return EXPLANATIONS.get(topic, "No explanation available for this topic.")

def get_all_explanations() -> Dict[str, str]:
    """Get all available explanations."""
    return EXPLANATIONS.copy()

def search_explanations(keyword: str) -> Dict[str, str]:
    """Search for explanations containing a keyword."""
    results = {}
    keyword_lower = keyword.lower()
    
    for topic, explanation in EXPLANATIONS.items():
        if keyword_lower in explanation.lower():
            results[topic] = explanation
    
    return results