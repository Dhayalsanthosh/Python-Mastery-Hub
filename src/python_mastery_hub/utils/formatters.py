# src/python_mastery_hub/utils/formatters.py
"""
Output Formatting Utilities - Text and Data Formatting

Provides formatting functions for consistent display of data across the application.
Handles text formatting, table generation, progress bars, and rich text output.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import textwrap
import logging

logger = logging.getLogger(__name__)


class ColorCodes:
    """ANSI color codes for terminal output."""
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Text styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'
    
    @classmethod
    def supports_color(cls) -> bool:
        """Check if terminal supports colors."""
        import sys
        return (
            hasattr(sys.stdout, "isatty") and 
            sys.stdout.isatty() and 
            not sys.platform.startswith('win')
        )


class TextFormatter:
    """Utility class for text formatting."""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and ColorCodes.supports_color()
    
    def colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are supported."""
        if not self.use_colors:
            return text
        return f"{color}{text}{ColorCodes.RESET}"
    
    def bold(self, text: str) -> str:
        """Make text bold."""
        return self.colorize(text, ColorCodes.BOLD)
    
    def italic(self, text: str) -> str:
        """Make text italic."""
        return self.colorize(text, ColorCodes.ITALIC)
    
    def underline(self, text: str) -> str:
        """Underline text."""
        return self.colorize(text, ColorCodes.UNDERLINE)
    
    def red(self, text: str) -> str:
        """Red text."""
        return self.colorize(text, ColorCodes.RED)
    
    def green(self, text: str) -> str:
        """Green text."""
        return self.colorize(text, ColorCodes.GREEN)
    
    def yellow(self, text: str) -> str:
        """Yellow text."""
        return self.colorize(text, ColorCodes.YELLOW)
    
    def blue(self, text: str) -> str:
        """Blue text."""
        return self.colorize(text, ColorCodes.BLUE)
    
    def cyan(self, text: str) -> str:
        """Cyan text."""
        return self.colorize(text, ColorCodes.CYAN)
    
    def magenta(self, text: str) -> str:
        """Magenta text."""
        return self.colorize(text, ColorCodes.MAGENTA)
    
    def success(self, text: str) -> str:
        """Format success message."""
        return self.green(f"✓ {text}")
    
    def error(self, text: str) -> str:
        """Format error message."""
        return self.red(f"✗ {text}")
    
    def warning(self, text: str) -> str:
        """Format warning message."""
        return self.yellow(f"⚠ {text}")
    
    def info(self, text: str) -> str:
        """Format info message."""
        return self.blue(f"ℹ {text}")
    
    def header(self, text: str, level: int = 1) -> str:
        """Format header text."""
        if level == 1:
            return self.bold(self.blue(f"\n{'='*50}\n{text.center(50)}\n{'='*50}"))
        elif level == 2:
            return self.bold(self.cyan(f"\n{'-'*30}\n{text}\n{'-'*30}"))
        else:
            return self.bold(f"\n{text}")
    
    def wrap_text(self, text: str, width: int = 80, indent: str = "") -> str:
        """Wrap text to specified width."""
        return textwrap.fill(text, width=width, initial_indent=indent, subsequent_indent=indent)


# Global formatter instance
formatter = TextFormatter()


def format_duration(seconds: Union[int, float]) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_time_ago(timestamp: Union[datetime, str]) -> str:
    """Format timestamp as 'X time ago'."""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            return "Unknown time"
    
    now = datetime.now()
    if timestamp.tzinfo:
        # If timestamp has timezone info, make now timezone aware
        from datetime import timezone
        now = now.replace(tzinfo=timezone.utc)
    
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """Format percentage with proper symbol."""
    return f"{value:.{decimal_places}f}%"


def format_number(number: Union[int, float], thousands_sep: str = ",") -> str:
    """Format number with thousands separator."""
    if isinstance(number, float):
        return f"{number:,.2f}".replace(",", thousands_sep)
    else:
        return f"{number:,}".replace(",", thousands_sep)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_json(data: Any, indent: int = 2, sort_keys: bool = True) -> str:
    """Format JSON data with proper indentation."""
    try:
        return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to format JSON: {e}")
        return str(data)


def format_progress_bar(
    current: int, 
    total: int, 
    width: int = 50, 
    fill_char: str = "█", 
    empty_char: str = "░",
    show_percentage: bool = True,
    show_numbers: bool = True
) -> str:
    """Create a progress bar string."""
    if total == 0:
        percentage = 0
        filled_width = 0
    else:
        percentage = (current / total) * 100
        filled_width = int((current / total) * width)
    
    empty_width = width - filled_width
    bar = fill_char * filled_width + empty_char * empty_width
    
    parts = [f"[{bar}]"]
    
    if show_percentage:
        parts.append(f"{percentage:.1f}%")
    
    if show_numbers:
        parts.append(f"({current}/{total})")
    
    return " ".join(parts)


def format_table(
    data: List[Dict[str, Any]], 
    headers: Optional[List[str]] = None,
    max_width: Optional[int] = None,
    align: Dict[str, str] = None
) -> str:
    """Format data as a table."""
    if not data:
        return "No data to display"
    
    # Determine headers
    if headers is None:
        headers = list(data[0].keys())
    
    # Determine column widths
    col_widths = {}
    for header in headers:
        col_widths[header] = len(str(header))
        for row in data:
            value = str(row.get(header, ""))
            col_widths[header] = max(col_widths[header], len(value))
    
    # Apply max width if specified
    if max_width:
        total_width = sum(col_widths.values()) + len(headers) * 3 - 1
        if total_width > max_width:
            # Reduce column widths proportionally
            reduction_factor = max_width / total_width
            for header in headers:
                col_widths[header] = max(10, int(col_widths[header] * reduction_factor))
    
    # Alignment settings
    alignment = align or {}
    
    # Build table
    lines = []
    
    # Header
    header_line = " | ".join(
        str(header).ljust(col_widths[header])[:col_widths[header]]
        for header in headers
    )
    lines.append(header_line)
    
    # Separator
    separator = "-+-".join("-" * col_widths[header] for header in headers)
    lines.append(separator)
    
    # Data rows
    for row in data:
        row_parts = []
        for header in headers:
            value = str(row.get(header, ""))
            if len(value) > col_widths[header]:
                value = value[:col_widths[header]-3] + "..."
            
            align_type = alignment.get(header, "left")
            if align_type == "right":
                value = value.rjust(col_widths[header])
            elif align_type == "center":
                value = value.center(col_widths[header])
            else:
                value = value.ljust(col_widths[header])
            
            row_parts.append(value)
        
        lines.append(" | ".join(row_parts))
    
    return "\n".join(lines)


def format_list(items: List[str], bullet: str = "•", indent: str = "  ") -> str:
    """Format list of items with bullets."""
    if not items:
        return "No items"
    
    return "\n".join(f"{indent}{bullet} {item}" for item in items)


def format_numbered_list(items: List[str], start: int = 1, indent: str = "  ") -> str:
    """Format numbered list of items."""
    if not items:
        return "No items"
    
    width = len(str(start + len(items) - 1))
    return "\n".join(
        f"{indent}{i:>{width}}. {item}" 
        for i, item in enumerate(items, start)
    )


def format_key_value_pairs(
    data: Dict[str, Any], 
    separator: str = ": ", 
    indent: str = "",
    max_key_width: Optional[int] = None
) -> str:
    """Format dictionary as key-value pairs."""
    if not data:
        return "No data"
    
    # Calculate key width
    if max_key_width is None:
        key_width = max(len(str(key)) for key in data.keys())
    else:
        key_width = max_key_width
    
    lines = []
    for key, value in data.items():
        key_str = str(key).ljust(key_width)
        value_str = str(value)
        lines.append(f"{indent}{key_str}{separator}{value_str}")
    
    return "\n".join(lines)


def format_code_block(code: str, language: str = "python", line_numbers: bool = False) -> str:
    """Format code block with syntax highlighting indicators."""
    lines = code.split('\n')
    
    if line_numbers:
        width = len(str(len(lines)))
        formatted_lines = []
        for i, line in enumerate(lines, 1):
            formatted_lines.append(f"{i:>{width}} | {line}")
        lines = formatted_lines
    
    # Simple syntax highlighting markers
    if language.lower() == "python":
        for i, line in enumerate(lines):
            # Highlight comments
            if "#" in line:
                parts = line.split("#", 1)
                if len(parts) == 2:
                    lines[i] = parts[0] + formatter.green(f"#{parts[1]}")
    
    formatted_code = "\n".join(lines)
    
    # Add code block markers
    return f"```{language}\n{formatted_code}\n```"


def format_diff(old_text: str, new_text: str) -> str:
    """Format text difference (simplified diff)."""
    old_lines = old_text.split('\n')
    new_lines = new_text.split('\n')
    
    result_lines = []
    
    # Simple line-by-line comparison
    max_lines = max(len(old_lines), len(new_lines))
    
    for i in range(max_lines):
        old_line = old_lines[i] if i < len(old_lines) else None
        new_line = new_lines[i] if i < len(new_lines) else None
        
        if old_line is None:
            result_lines.append(formatter.green(f"+ {new_line}"))
        elif new_line is None:
            result_lines.append(formatter.red(f"- {old_line}"))
        elif old_line != new_line:
            result_lines.append(formatter.red(f"- {old_line}"))
            result_lines.append(formatter.green(f"+ {new_line}"))
        else:
            result_lines.append(f"  {old_line}")
    
    return "\n".join(result_lines)


def format_module_progress(module_progress: Dict[str, Any]) -> str:
    """Format module progress information."""
    if not module_progress:
        return "No progress data available"
    
    completed = module_progress.get('completed', 0)
    total = module_progress.get('total', 0)
    percentage = module_progress.get('percentage', 0)
    total_time = module_progress.get('total_time_minutes', 0)
    
    lines = [
        formatter.header(f"Module Progress", level=2),
        f"Topics Completed: {formatter.bold(str(completed))} / {total}",
        f"Progress: {format_progress_bar(completed, total)} {format_percentage(percentage)}",
        f"Time Spent: {format_duration(total_time * 60)}"
    ]
    
    if module_progress.get('start_date'):
        lines.append(f"Started: {format_time_ago(module_progress['start_date'])}")
    
    if module_progress.get('last_completion'):
        lines.append(f"Last Activity: {format_time_ago(module_progress['last_completion'])}")
    
    return "\n".join(lines)


def format_learning_statistics(stats: Dict[str, Any]) -> str:
    """Format learning statistics."""
    if not stats:
        return "No statistics available"
    
    lines = [
        formatter.header("Learning Statistics", level=1),
        "",
        formatter.bold("Overview:"),
        f"Modules Started: {format_number(stats.get('modules_started', 0))}",
        f"Topics Completed: {format_number(stats.get('completed_topics', 0))} / {format_number(stats.get('total_topics', 0))}",
        f"Total Study Time: {format_duration(stats.get('total_time_minutes', 0) * 60)}",
        f"Average Score: {format_percentage(stats.get('average_score', 0) * 100) if stats.get('average_score') else 'N/A'}",
        "",
        formatter.bold("Streaks:"),
        f"Current Streak: {stats.get('current_streak', 0)} days",
        f"Longest Streak: {stats.get('longest_streak', 0)} days",
        f"Total Learning Days: {stats.get('total_days', 0)}",
        ""
    ]
    
    # Weekly activity
    weekly_activity = stats.get('weekly_activity', {})
    if weekly_activity:
        lines.append(formatter.bold("Weekly Activity:"))
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for day, name in zip(days, day_names):
            activity = weekly_activity.get(day, 0)
            bar = "█" * min(activity, 10) + "░" * (10 - min(activity, 10))
            lines.append(f"{name}: [{bar}] {activity}")
        lines.append("")
    
    # Module statistics
    module_stats = stats.get('module_stats', {})
    if module_stats:
        lines.append(formatter.bold("Module Progress:"))
        module_data = []
        for module_id, module_info in module_stats.items():
            module_data.append({
                'Module': module_id.replace('_', ' ').title(),
                'Progress': f"{module_info['completed']}/{module_info['total']}",
                'Percentage': format_percentage(module_info['percentage']),
                'Time': format_duration(module_info['time_spent'] * 60)
            })
        
        if module_data:
            lines.append(format_table(module_data))
    
    return "\n".join(lines)


def format_achievement_list(achievements: List[Dict[str, Any]]) -> str:
    """Format list of achievements."""
    if not achievements:
        return "No achievements earned yet"
    
    lines = [formatter.header("Achievements", level=2)]
    
    for achievement in achievements:
        badge = achievement.get('badge', '🏆')
        name = achievement.get('name', 'Unknown Achievement')
        description = achievement.get('description', '')
        tier = achievement.get('tier', 'Bronze')
        points = achievement.get('points', 0)
        earned_date = achievement.get('earned_date', '')
        
        # Color by tier
        if tier == 'Diamond':
            tier_color = formatter.magenta
        elif tier == 'Platinum':
            tier_color = formatter.cyan
        elif tier == 'Gold':
            tier_color = formatter.yellow
        elif tier == 'Silver':
            tier_color = lambda x: formatter.colorize(x, ColorCodes.BRIGHT_WHITE)
        else:  # Bronze
            tier_color = lambda x: formatter.colorize(x, ColorCodes.YELLOW)
        
        achievement_line = f"{badge} {formatter.bold(name)} {tier_color(f'[{tier}]')} ({points} pts)"
        lines.append(achievement_line)
        
        if description:
            lines.append(f"   {formatter.italic(description)}")
        
        if earned_date:
            lines.append(f"   Earned: {format_time_ago(earned_date)}")
        
        lines.append("")  # Empty line between achievements
    
    return "\n".join(lines)


def format_topic_list(topics: List[Dict[str, Any]]) -> str:
    """Format list of topics with completion status."""
    if not topics:
        return "No topics available"
    
    lines = []
    for i, topic in enumerate(topics, 1):
        name = topic.get('name', f'Topic {i}')
        completed = topic.get('completed', False)
        completion_date = topic.get('completion_date')
        
        # Status indicator
        status = formatter.success("✓") if completed else "◯"
        
        topic_line = f"{status} {name}"
        
        if completed and completion_date:
            topic_line += f" ({format_time_ago(completion_date)})"
        
        lines.append(topic_line)
    
    return "\n".join(lines)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_validation_errors(errors: Dict[str, List[str]]) -> str:
    """Format validation errors in a readable format."""
    if not errors:
        return "No validation errors"
    
    lines = [formatter.error("Validation Errors:")]
    
    for field, field_errors in errors.items():
        lines.append(f"\n{formatter.bold(field)}:")
        for error in field_errors:
            lines.append(f"  • {error}")
    
    return "\n".join(lines)


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI color codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def get_terminal_width() -> int:
    """Get terminal width, fallback to 80 if not available."""
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except (ImportError, OSError):
        return 80