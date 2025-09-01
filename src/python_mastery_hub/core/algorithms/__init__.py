"""
Algorithms Learning Module.

Comprehensive coverage of fundamental algorithms including sorting, searching,
dynamic programming, graph algorithms, and algorithmic thinking patterns.
"""

from .base import Algorithms
from .sorting import SortingAlgorithms
from .searching import SearchingAlgorithms
from .dynamic_programming import DynamicProgramming
from .graph_algorithms import GraphAlgorithms
from .algorithmic_patterns import AlgorithmicPatterns

__all__ = [
    'Algorithms',
    'SortingAlgorithms',
    'SearchingAlgorithms',
    'DynamicProgramming',
    'GraphAlgorithms',
    'AlgorithmicPatterns'
]