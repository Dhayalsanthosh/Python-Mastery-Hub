"""
Utility modules for Data Structures learning module.
"""

from .explanations import EXPLANATIONS, get_explanation, get_all_explanations, search_explanations
from .best_practices import BEST_PRACTICES, get_best_practices, get_all_best_practices, search_best_practices, get_practices_by_difficulty

__all__ = [
    "EXPLANATIONS",
    "get_explanation",
    "get_all_explanations",
    "search_explanations",
    "BEST_PRACTICES", 
    "get_best_practices",
    "get_all_best_practices",
    "search_best_practices",
    "get_practices_by_difficulty"
]