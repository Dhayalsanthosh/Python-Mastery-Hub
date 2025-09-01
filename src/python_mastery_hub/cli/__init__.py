"""
Python Mastery Hub CLI Package

Command-line interface for the Python learning platform providing
interactive learning, progress tracking, and exercise execution.
"""

from .main import main, PythonMasteryHubCLI

__version__ = "1.0.0"
__author__ = "Python Mastery Hub"
__description__ = "Interactive Python Learning Platform CLI"

# Export main components
__all__ = [
    "main",
    "PythonMasteryHubCLI",
]