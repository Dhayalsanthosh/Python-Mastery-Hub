"""
Progress Bar Utilities for CLI

Provides various progress visualization components for terminal output.
Supports different styles and animations for progress tracking.
"""

import time
import sys
from typing import Optional, List, Dict, Any
from math import ceil

from .colors import Colors, supports_color, get_progress_color, get_terminal_width


class ProgressBar:
    """Customizable progress bar for terminal display."""
    
    def __init__(
        self,
        total: int,
        width: Optional[int] = None,
        fill_char: str = "█",
        empty_char: str = "░",
        show_percentage: bool = True,
        show_count: bool = True,
        show_rate: bool = False,
        prefix: str = "",
        suffix: str = ""
    ):
        """
        Initialize progress bar.
        
        Args:
            total: Total number of items
            width: Width of progress bar (auto-detected if None)
            fill_char: Character for completed portion
            empty_char: Character for remaining portion
            show_percentage: Whether to show percentage
            show_count: Whether to show count (current/total)
            show_rate: Whether to show rate (items/sec)
            prefix: Text to show before progress bar
            suffix: Text to show after progress bar
        """
        self.total = total
        self.current = 0
        self.width = width or min(50, get_terminal_width() - 30)
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.show_percentage = show_percentage
        self.show_count = show_count
        self.show_rate = show_rate
        self.prefix = prefix
        self.suffix = suffix
        self.start_time = time.time()
        self.last_update = self.start_time
    
    def update(self, amount: int = 1) -> None:
        """
        Update progress by specified amount.
        
        Args:
            amount: Amount to increment progress
        """
        self.current = min(self.current + amount, self.total)
        self.display()
    
    def set_progress(self, current: int) -> None:
        """
        Set absolute progress value.
        
        Args:
            current: Current progress value
        """
        self.current = min(max(current, 0), self.total)
        self.display()
    
    def display(self) -> None:
        """Display the current progress bar."""
        if not supports_color():
            self._display_simple()
            return
        
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        filled_width = int((self.current / self.total) * self.width) if self.total > 0 else 0
        
        # Choose color based on progress
        color = get_progress_color(percentage)
        
        # Build progress bar
        filled = self.fill_char * filled_width
        empty = self.empty_char * (self.width - filled_width)
        bar = f"{color}{filled}{Colors.RESET}{Colors.DIM}{empty}{Colors.RESET}"
        
        # Build additional info
        info_parts = []
        
        if self.show_percentage:
            info_parts.append(f"{percentage:5.1f}%")
        
        if self.show_count:
            info_parts.append(f"{self.current:>{len(str(self.total))}}/{self.total}")
        
        if self.show_rate and self.current > 0:
            elapsed = time.time() - self.start_time
            rate = self.current / elapsed if elapsed > 0 else 0
            info_parts.append(f"{rate:.1f}/s")
        
        info = " | ".join(info_parts)
        
        # Combine all parts
        parts = []
        if self.prefix:
            parts.append(f"{Colors.BOLD}{self.prefix}{Colors.RESET}")
        
        parts.append(f"[{bar}]")
        
        if info:
            parts.append(info)
        
        if self.suffix:
            parts.append(self.suffix)
        
        # Print with carriage return for in-place update
        line = " ".join(parts)
        print(f"\r{line}", end="", flush=True)
        
        # Add newline if complete
        if self.current >= self.total:
            print()
    
    def _display_simple(self) -> None:
        """Display simple progress bar without colors."""
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        filled_width = int((self.current / self.total) * self.width) if self.total > 0 else 0
        
        filled = "=" * filled_width
        empty = "-" * (self.width - filled_width)
        bar = f"[{filled}{empty}]"
        
        info = f"{percentage:5.1f}% ({self.current}/{self.total})"
        
        line = f"{self.prefix} {bar} {info} {self.suffix}".strip()
        print(f"\r{line}", end="", flush=True)
        
        if self.current >= self.total:
            print()
    
    def close(self) -> None:
        """Close the progress bar and move to next line."""
        if self.current < self.total:
            self.current = self.total
            self.display()
        print()


class SpinnerProgress:
    """Animated spinner for indeterminate progress."""
    
    def __init__(
        self,
        message: str = "Loading",
        frames: Optional[List[str]] = None,
        interval: float = 0.1
    ):
        """
        Initialize spinner.
        
        Args:
            message: Message to display with spinner
            frames: Animation frames (default: spinning line)
            interval: Time between frame updates
        """
        self.message = message
        self.frames = frames or ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.interval = interval
        self.current_frame = 0
        self.running = False
        self.start_time = time.time()
    
    def start(self) -> None:
        """Start the spinner animation."""
        self.running = True
        self.start_time = time.time()
    
    def update(self) -> None:
        """Update spinner frame."""
        if not self.running:
            return
        
        if supports_color():
            frame = self.frames[self.current_frame]
            elapsed = time.time() - self.start_time
            print(f"\r{Colors.CYAN}{frame}{Colors.RESET} {self.message} ({elapsed:.1f}s)", end="", flush=True)
        else:
            print(f"\r{self.message}...", end="", flush=True)
        
        self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def stop(self, final_message: Optional[str] = None) -> None:
        """Stop the spinner and optionally show final message."""
        self.running = False
        if final_message:
            print(f"\r{Colors.GREEN}✓{Colors.RESET} {final_message}")
        else:
            print(f"\r{Colors.GREEN}✓{Colors.RESET} {self.message} completed")


class MultiProgressBar:
    """Multiple progress bars for tracking parallel tasks."""
    
    def __init__(self, tasks: List[Dict[str, Any]]):
        """
        Initialize multi-progress display.
        
        Args:
            tasks: List of task dictionaries with 'name' and 'total' keys
        """
        self.tasks = []
        for task in tasks:
            self.tasks.append({
                'name': task['name'],
                'total': task['total'],
                'current': 0,
                'bar': ProgressBar(
                    total=task['total'],
                    prefix=task['name'][:20],
                    width=30,
                    show_count=True,
                    show_percentage=True
                )
            })
    
    def update_task(self, task_index: int, amount: int = 1) -> None:
        """Update progress for a specific task."""
        if 0 <= task_index < len(self.tasks):
            task = self.tasks[task_index]
            task['current'] = min(task['current'] + amount, task['total'])
            self._display_all()
    
    def _display_all(self) -> None:
        """Display all progress bars."""
        # Clear lines
        for _ in range(len(self.tasks)):
            print("\033[A\033[K", end="")
        
        # Display each progress bar
        for task in self.tasks:
            task['bar'].set_progress(task['current'])


def show_progress(current: int, total: int, prefix: str = "Progress", width: int = 50) -> None:
    """
    Show a simple progress bar.
    
    Args:
        current: Current progress value
        total: Total value
        prefix: Text to show before progress bar
        width: Width of progress bar
    """
    bar = ProgressBar(total=total, prefix=prefix, width=width)
    bar.set_progress(current)


def show_module_progress(modules: Dict[str, Dict[str, Any]]) -> None:
    """
    Show progress for multiple learning modules.
    
    Args:
        modules: Dictionary of module progress data
    """
    print(f"\n{Colors.BOLD}📊 Learning Progress Overview{Colors.RESET}\n")
    
    for module_id, progress in modules.items():
        name = progress.get('name', module_id.title())
        completed = progress.get('completed', 0)
        total = progress.get('total', 1)
        percentage = (completed / total * 100) if total > 0 else 0
        
        # Create mini progress bar
        width = 30
        filled = int((completed / total) * width) if total > 0 else 0
        color = get_progress_color(percentage)
        
        if supports_color():
            bar_filled = "█" * filled
            bar_empty = "░" * (width - filled)
            bar = f"{color}{bar_filled}{Colors.RESET}{Colors.DIM}{bar_empty}{Colors.RESET}"
        else:
            bar_filled = "=" * filled
            bar_empty = "-" * (width - filled)
            bar = f"[{bar_filled}{bar_empty}]"
        
        print(f"{name:<25} {bar} {percentage:5.1f}% ({completed}/{total})")
    
    print()


def animated_loading(message: str, duration: float = 2.0) -> None:
    """
    Show an animated loading message.
    
    Args:
        message: Loading message
        duration: How long to show animation
    """
    spinner = SpinnerProgress(message)
    spinner.start()
    
    start_time = time.time()
    while time.time() - start_time < duration:
        spinner.update()
        time.sleep(spinner.interval)
    
    spinner.stop()


def show_completion_celebration(module_name: str) -> None:
    """
    Show a celebration animation for module completion.
    
    Args:
        module_name: Name of completed module
    """
    if not supports_color():
        print(f"Congratulations! You've completed {module_name}!")
        return
    
    # Celebration frames
    frames = ["🎉", "🎊", "✨", "🌟", "💫", "⭐"]
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 CONGRATULATIONS! 🎉{Colors.RESET}\n")
    
    for _ in range(3):
        for frame in frames:
            print(f"\r{frame} You've completed {Colors.BOLD}{module_name}{Colors.RESET}! {frame}", end="", flush=True)
            time.sleep(0.2)
    
    print(f"\n\n{Colors.YELLOW}🏆 Achievement Unlocked: {module_name} Master! 🏆{Colors.RESET}\n")


# Export commonly used functions
__all__ = [
    'ProgressBar', 'SpinnerProgress', 'MultiProgressBar',
    'show_progress', 'show_module_progress', 'animated_loading',
    'show_completion_celebration'
]