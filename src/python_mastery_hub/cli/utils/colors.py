"""
Terminal Colors and Formatting Utilities

Provides consistent color schemes and formatting for CLI output.
Supports both ANSI colors and fallback for systems without color support.
"""

import os
import sys
from typing import Optional


class Colors:
    """ANSI color codes and formatting constants."""
    
    # Basic Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright Colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Extended Colors (aliases for readability)
    GRAY = BRIGHT_BLACK
    LIGHT_RED = BRIGHT_RED
    LIGHT_GREEN = BRIGHT_GREEN
    LIGHT_YELLOW = BRIGHT_YELLOW
    LIGHT_BLUE = BRIGHT_BLUE
    LIGHT_MAGENTA = BRIGHT_MAGENTA
    LIGHT_CYAN = BRIGHT_CYAN
    
    # Background Colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Text Formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'
    
    # Semantic Colors for Python Mastery Hub
    SUCCESS = GREEN
    ERROR = RED
    WARNING = YELLOW
    INFO = BLUE
    DEBUG = GRAY
    
    # Learning Module Colors
    BASICS = GREEN
    OOP = BLUE
    ADVANCED = MAGENTA
    DATA_STRUCTURES = CYAN
    ALGORITHMS = YELLOW
    ASYNC = LIGHT_MAGENTA
    WEB = RED
    DATA_SCIENCE = LIGHT_BLUE
    TESTING = LIGHT_GREEN
    
    # Special Colors
    HEADER = BOLD + CYAN
    SUBHEADER = BOLD + BLUE
    HIGHLIGHT = BOLD + YELLOW
    MUTED = GRAY
    
    # Progress Colors
    PROGRESS_COMPLETE = GREEN
    PROGRESS_PARTIAL = YELLOW
    PROGRESS_NONE = RED
    
    # Code Syntax Colors
    KEYWORD = BLUE
    STRING = GREEN
    NUMBER = MAGENTA
    COMMENT = GRAY
    FUNCTION = CYAN
    CLASS = YELLOW


def supports_color() -> bool:
    """
    Check if the terminal supports ANSI color codes.
    
    Returns:
        bool: True if colors are supported, False otherwise
    """
    # Check if we're in a TTY
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Check environment variables
    if os.environ.get('NO_COLOR'):
        return False
    
    if os.environ.get('FORCE_COLOR'):
        return True
    
    # Check TERM environment variable
    term = os.environ.get('TERM', '').lower()
    if term in ('dumb', 'unknown'):
        return False
    
    # Most modern terminals support colors
    return True


def colorize(text: str, color: str, bold: bool = False, bg_color: Optional[str] = None) -> str:
    """
    Apply color and formatting to text.
    
    Args:
        text: Text to colorize
        color: ANSI color code
        bold: Whether to make text bold
        bg_color: Background color code (optional)
    
    Returns:
        str: Formatted text with color codes
    """
    if not supports_color():
        return text
    
    formatting = ""
    if bold:
        formatting += Colors.BOLD
    if bg_color:
        formatting += bg_color
    
    return f"{formatting}{color}{text}{Colors.RESET}"


def strip_colors(text: str) -> str:
    """
    Remove ANSI color codes from text.
    
    Args:
        text: Text with potential color codes
    
    Returns:
        str: Text without color codes
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def get_progress_color(percentage: float) -> str:
    """
    Get appropriate color for progress percentage.
    
    Args:
        percentage: Progress percentage (0-100)
    
    Returns:
        str: ANSI color code
    """
    if percentage >= 80:
        return Colors.PROGRESS_COMPLETE
    elif percentage >= 40:
        return Colors.PROGRESS_PARTIAL
    else:
        return Colors.PROGRESS_NONE


def print_header(text: str, char: str = "=", width: int = 60) -> None:
    """
    Print a formatted header.
    
    Args:
        text: Header text
        char: Character to use for border
        width: Total width of header
    """
    if not supports_color():
        print(f"\n{char * width}")
        print(f"{text:^{width}}")
        print(f"{char * width}\n")
        return
    
    border = char * width
    print(f"\n{Colors.HEADER}{border}{Colors.RESET}")
    print(f"{Colors.HEADER}{text:^{width}}{Colors.RESET}")
    print(f"{Colors.HEADER}{border}{Colors.RESET}\n")


def print_subheader(text: str, char: str = "-", width: int = 40) -> None:
    """
    Print a formatted subheader.
    
    Args:
        text: Subheader text
        char: Character to use for border
        width: Total width of subheader
    """
    if not supports_color():
        print(f"\n{text}")
        print(f"{char * len(text)}\n")
        return
    
    print(f"\n{Colors.SUBHEADER}{text}{Colors.RESET}")
    print(f"{Colors.SUBHEADER}{char * len(text)}{Colors.RESET}\n")


def print_success(message: str) -> None:
    """Print a success message."""
    icon = "✅" if supports_color() else "[SUCCESS]"
    print(f"{Colors.SUCCESS}{icon} {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print an error message."""
    icon = "❌" if supports_color() else "[ERROR]"
    print(f"{Colors.ERROR}{icon} {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    icon = "⚠️ " if supports_color() else "[WARNING]"
    print(f"{Colors.WARNING}{icon} {message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Print an info message."""
    icon = "ℹ️ " if supports_color() else "[INFO]"
    print(f"{Colors.INFO}{icon} {message}{Colors.RESET}")


def print_code_block(code: str, language: str = "python") -> None:
    """
    Print a formatted code block with syntax highlighting.
    
    Args:
        code: Code to display
        language: Programming language for highlighting
    """
    if not supports_color():
        print(f"\n{code}\n")
        return
    
    # Simple syntax highlighting for Python
    if language.lower() == "python":
        lines = code.split('\n')
        for line in lines:
            # Very basic highlighting - in production, use a proper syntax highlighter
            if line.strip().startswith('#'):
                print(f"{Colors.COMMENT}{line}{Colors.RESET}")
            elif 'def ' in line or 'class ' in line:
                print(f"{Colors.FUNCTION}{line}{Colors.RESET}")
            elif any(keyword in line for keyword in ['import', 'from', 'if', 'else', 'for', 'while', 'try', 'except']):
                print(f"{Colors.KEYWORD}{line}{Colors.RESET}")
            else:
                print(line)
    else:
        print(code)
    print()


def get_terminal_width() -> int:
    """Get the width of the terminal."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80  # Default width


# Create a singleton instance for easy importing
colors = Colors()

# Export commonly used items
__all__ = [
    'Colors', 'colors', 'supports_color', 'colorize', 'strip_colors',
    'get_progress_color', 'print_header', 'print_subheader',
    'print_success', 'print_error', 'print_warning', 'print_info',
    'print_code_block', 'get_terminal_width'
]