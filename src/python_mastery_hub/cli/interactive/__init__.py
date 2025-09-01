"""
CLI Interactive Package

Interactive components for the Python Mastery Hub CLI including
REPL, exercise runners, and interactive quizzes.
"""

from . import repl
from . import exercises  
from . import quiz

# Export interactive modules
__all__ = [
    "repl",
    "exercises",
    "quiz",
]

# Interactive mode registry
INTERACTIVE_MODES = {
    "repl": repl,
    "exercises": exercises,
    "quiz": quiz,
}

def get_interactive_mode(mode_name: str):
    """Get interactive mode module by name."""
    return INTERACTIVE_MODES.get(mode_name)

def list_interactive_modes():
    """Get list of available interactive mode names."""
    return list(INTERACTIVE_MODES.keys())