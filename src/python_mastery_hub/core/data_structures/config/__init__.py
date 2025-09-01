"""
Configuration module for Data Structures learning module.
"""

from .topics import TOPICS_CONFIG, get_topic_order, get_topic_dependencies, get_difficulty_levels

__all__ = [
    "TOPICS_CONFIG",
    "get_topic_order", 
    "get_topic_dependencies",
    "get_difficulty_levels"
]