"""
Python Mastery Hub - A comprehensive Python learning platform.

This package provides interactive learning modules covering all aspects of Python
programming, from basics to advanced topics, with modern development practices.
"""

__version__ = "1.0.0"
__author__ = "Python Mastery Hub Team"
__email__ = "team@pythonmasteryhub.com"
__description__ = "A comprehensive, production-ready Python learning platform"

from typing import Dict, Any
import logging

# Configure package-level logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Package metadata
__metadata__: Dict[str, Any] = {
    "version": __version__,
    "author": __author__,
    "email": __email__,
    "description": __description__,
    "keywords": ["python", "learning", "education", "programming", "tutorial"],
    "license": "MIT",
    "python_requires": ">=3.11",
}

# Export main components
from python_mastery_hub.core import (
    BasicsConcepts,
    OOPConcepts,
    AdvancedConcepts,
    DataStructures,
    Algorithms,
    AsyncProgramming,
    WebDevelopment,
    DataScience,
    TestingConcepts,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__metadata__",
    "BasicsConcepts",
    "OOPConcepts", 
    "AdvancedConcepts",
    "DataStructures",
    "Algorithms",
    "AsyncProgramming",
    "WebDevelopment",
    "DataScience",
    "TestingConcepts",
]