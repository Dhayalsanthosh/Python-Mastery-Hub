"""
CLI Commands Package

Contains all command implementations for the Python Mastery Hub CLI.
Each command module provides specific functionality with argument parsing and execution.
"""

from . import learn
from . import progress
from . import test
from . import demo

# Export command modules
__all__ = [
    "learn",
    "progress", 
    "test",
    "demo",
]

# Command registry for dynamic loading
COMMANDS = {
    "learn": learn,
    "progress": progress,
    "test": test,
    "demo": demo,
}

def get_command(command_name: str):
    """Get command module by name."""
    return COMMANDS.get(command_name)

def list_commands():
    """Get list of available command names."""
    return list(COMMANDS.keys())