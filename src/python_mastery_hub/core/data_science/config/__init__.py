"""
Configuration module for Data Science learning module.
"""

from .topics import TOPICS_CONFIG, get_topic_order, get_topic_dependencies

__all__ = [
    "TOPICS_CONFIG",
    "get_topic_order", 
    "get_topic_dependencies"
]