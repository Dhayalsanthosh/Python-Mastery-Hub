"""
CLI Utilities Package

Common utilities for the Python Mastery Hub CLI including
colors, progress bars, and input validation.
"""

from . import colors
from . import progress_bar
from . import input_validation

# Export utility modules
__all__ = [
    "colors",
    "progress_bar", 
    "input_validation",
]

# Convenience imports for common utilities
from .colors import (
    Colors,
    print_header,
    print_subheader,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_code_block
)

from .progress_bar import (
    ProgressBar,
    SpinnerProgress,
    show_progress,
    show_module_progress,
    animated_loading
)

from .input_validation import (
    InputValidator,
    ValidationError,
    prompt_with_validation,
    validate_and_suggest,
    module_validator,
    exercise_validator,
    integer_validator,
    choice_validator
)