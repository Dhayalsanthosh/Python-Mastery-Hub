"""
Progress Command - Learning Progress Tracking and Visualization

Manages and displays user learning progress across all modules and topics.
Provides detailed analytics and achievement tracking.
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from python_mastery_hub.cli.utils import colors, progress_bar
from python_mastery_hub.utils.progress_calculator import ProgressCalculator
from python_mastery_hub.utils.achievement_engine import AchievementEngine
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)


class ProgressManager:
    """Manages user progress tracking and analytics."""
    
    def __init__(self):
        self.progress_calc = ProgressCalculator()
        self.achievement_engine = AchievementEngine()
        self.modules = self._get_module_definitions()
    
    def _get_module_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get module definitions with metadata."""
        return {
            'basics': {
                'name': 'Python Basics',
                'topics': [
                    'Variables and Assignment',
                    'Data Types (int, float, str, bool)',
                    'Control Flow (if/else, loops)',
                    'Functions and Scope',
                    'Error Handling Basics'
                ],
                'color': colors.GREEN,
                'difficulty': 'Beginner',
                'estimated_hours': 4
            },
            'oop': {
                'name': 'Object-Oriented Programming',
                'topics': [
                    'Classes and Objects',
                    'Inheritance and MRO',
                    'Polymorphism and Duck Typing',
                    'Abstract Base Classes',
                    'Design Patterns'
                ],
                'color': colors.BLUE,
                'difficulty': 'Intermediate',
                'estimated_hours': 6
            },
            'advanced': {
                'name': 'Advanced Python',
                'topics': [
                    'Decorators and Closures',
                    'Generators and Iterators',
                    'Context Managers',
                    'Metaclasses',
                    'Descriptors'
                ],
                'color': colors.MAGENTA,
                'difficulty': 'Advanced',
                'estimated_hours': 8
            },
            'data_structures': {
                'name': 'Data Structures',
                'topics': [
                    'Built-in Collections',
                    'Custom Data Structures',
                    'Performance Analysis',
                    'Memory Optimization',
                    'Collections Module'
                ],
                'color': colors.CYAN,
                'difficulty': 'Intermediate',
                'estimated_hours': 5
            },
            'algorithms': {
                'name': 'Algorithms',
                'topics': [
                    'Sorting Algorithms',
                    'Searching Techniques',
                    'Graph Algorithms',
                    'Dynamic Programming',
                    'Big O Analysis'
                ],
                'color': colors.YELLOW,
                'difficulty': 'Intermediate-Advanced',
                'estimated_hours': 7
            },
            'async': {
                'name': 'Async Programming',
                'topics': [
                    'Asyncio Fundamentals',
                    'Threading Concepts',
                    'Multiprocessing',
                    'Concurrent Futures',
                    'Performance Considerations'
                ],
                'color': colors.LIGHT_MAGENTA,
                'difficulty': 'Advanced',
                'estimated_hours': 8
            },
            'web': {
                'name': 'Web Development',
                'topics': [
                    'HTTP and REST APIs',
                    'Database Integration',
                    'Web Frameworks',
                    'Authentication',
                    'WebSockets'
                ],
                'color': colors.RED,
                'difficulty': 'Intermediate-Advanced',
                'estimated_hours': 10
            },
            'data_science': {
                'name': 'Data Science',
                'topics': [
                    'NumPy Arrays',
                    'Pandas DataFrames',
                    'Data Visualization',
                    'Statistical Analysis',
                    'Machine Learning Basics'
                ],
                'color': colors.LIGHT_BLUE,
                'difficulty': 'Intermediate',
                'estimated_hours': 8
            },
            'testing': {
                'name': 'Testing & Quality',
                'topics': [
                    'Unit Testing with pytest',
                    'Test-Driven Development',
                    'Mocking and Fixtures',
                    'Integration Testing',
                    'Code Quality Tools'
                ],
                'color': colors.LIGHT_GREEN,
                'difficulty': 'Intermediate',
                'estimated_hours': 6
            }
        }
    
    def show_overall_progress(self) -> None:
        """Display overall learning progress summary."""
        colors.print_header("Python Mastery Hub - Progress Overview")
        
        total_modules = len(self.modules)
        completed_modules = 0
        total_topics = 0
        completed_topics = 0
        total_hours = 0
        estimated_remaining = 0
        
        progress_data = {}
        
        for module_id, module_info in self.modules.items():
            progress = self.progress_calc.get_module_progress(module_id)
            module_total = len(module_info['topics'])
            module_completed = progress.get('completed', 0) if progress else 0
            
            total_topics += module_total
            completed_topics += module_completed
            total_hours += module_info['estimated_hours']
            
            if module_completed == module_total:
                completed_modules += 1
            else:
                estimated_remaining += module_info['estimated_hours']
            
            progress_data[module_id] = {
                'name': module_info['name'],
                'completed': module_completed,
                'total': module_total,
                'color': module_info['color']
            }
        
        # Overall statistics
        overall_percentage = (completed_topics / total_topics * 100) if total_topics > 0 else 0
        
        print(f"{colors.BOLD}Overall Statistics{colors.RESET}")
        print("=" * 70)
        print(f"Modules Completed: {colors.GREEN}{completed_modules}{colors.RESET}/{total_modules}")
        print(f"Topics Completed:  {colors.GREEN}{completed_topics}{colors.RESET}/{total_topics}")
        print(f"Total Time:        {colors.CYAN}{total_hours}{colors.RESET} hours estimated")
        print(f"Remaining Time:    {colors.YELLOW}{estimated_remaining}{colors.RESET} hours estimated")
        print(f"Overall Progress:  {colors.get_progress_color(overall_percentage)}{overall_percentage:.1f}%{colors.RESET}")
        print()
        
        # Overall progress bar
        progress_bar.show_progress(
            completed_topics, 
            total_topics, 
            "Overall Progress", 
            60
        )
        print()
        
        # Module-by-module breakdown
        progress_bar.show_module_progress(progress_data)
        
        # Recent achievements
        self._show_recent_achievements()
        
        # Learning streak
        self._show_learning_streak()
    
    def show_module_progress(self, module_id: str) -> None:
        """Display detailed progress for a specific module."""
        if module_id not in self.modules:
            colors.print_error(f"Module '{module_id}' not found")
            return
        
        module_info = self.modules[module_id]
        progress = self.progress_calc.get_module_progress(module_id)
        
        color = module_info['color']
        name = module_info['name']
        
        colors.print_header(f"{name} - Detailed Progress")
        
        print(f"{colors.BOLD}Module Information{colors.RESET}")
        print("=" * 50)
        print(f"Module: {color}{name}{colors.RESET}")
        print(f"Difficulty: {module_info['difficulty']}")
        print(f"Estimated Time: {module_info['estimated_hours']} hours")
        print()
        
        # Topic progress
        print(f"{colors.BOLD}Topic Progress{colors.RESET}")
        print("=" * 50)
        
        completed_count = 0
        for i, topic in enumerate(module_info['topics'], 1):
            is_completed = self.progress_calc.is_topic_completed(module_id, topic)
            status = f"{colors.GREEN}[DONE]{colors.RESET}" if is_completed else f"{colors.GRAY}[TODO]{colors.RESET}"
            
            if is_completed:
                completed_count += 1
                topic_text = f"{colors.GREEN}{topic}{colors.RESET}"
            else:
                topic_text = topic
            
            print(f"  {i:2d}. {status} {topic_text}")
        
        print()
        
        # Progress summary
        total_topics = len(module_info['topics'])
        percentage = (completed_count / total_topics * 100) if total_topics > 0 else 0
        
        progress_bar.show_progress(
            completed_count,
            total_topics,
            f"{name} Progress",
            50
        )
        
        print(f"\n{colors.BOLD}Progress Summary:{colors.RESET}")
        print(f"Completed: {colors.GREEN}{completed_count}{colors.RESET}/{total_topics} topics ({percentage:.1f}%)")
        
        if completed_count == total_topics:
            print(f"{colors.GREEN}Congratulations! Module completed!{colors.RESET}")
        else:
            remaining = total_topics - completed_count
            print(f"Remaining: {colors.YELLOW}{remaining}{colors.RESET} topics")
        
        print()
    
    def show_achievements(self) -> None:
        """Display user achievements and badges."""
        colors.print_header("Achievements & Badges")
        
        achievements = self.achievement_engine.get_user_achievements()
        
        if not achievements:
            print(f"{colors.YELLOW}No achievements yet. Start learning to unlock badges!{colors.RESET}")
            return
        
        # Group achievements by category
        categories = {}
        for achievement in achievements:
            category = achievement.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(achievement)
        
        for category, category_achievements in categories.items():
            colors.print_subheader(f"{category}")
            
            for achievement in category_achievements:
                badge = achievement.get('badge', '')
                name = achievement.get('name', 'Unknown Achievement')
                description = achievement.get('description', '')
                earned_date = achievement.get('earned_date', 'Unknown')
                
                print(f"  {badge} {colors.BOLD}{name}{colors.RESET}")
                print(f"     {description}")
                print(f"     {colors.GRAY}Earned: {earned_date}{colors.RESET}")
                print()
    
    def show_statistics(self) -> None:
        """Display detailed learning statistics."""
        colors.print_header("Learning Statistics")
        
        stats = self.progress_calc.get_learning_statistics()
        
        # Time-based statistics
        colors.print_subheader("Time Statistics")
        print(f"Total Learning Days: {colors.CYAN}{stats.get('total_days', 0)}{colors.RESET}")
        print(f"Current Streak: {colors.GREEN}{stats.get('current_streak', 0)}{colors.RESET} days")
        print(f"Longest Streak: {colors.YELLOW}{stats.get('longest_streak', 0)}{colors.RESET} days")
        print(f"Average Daily Progress: {colors.BLUE}{stats.get('avg_daily_progress', 0):.1f}{colors.RESET} topics")
        print()
        
        # Module statistics
        colors.print_subheader("Module Statistics")
        module_stats = stats.get('module_stats', {})
        
        for module_id, module_stat in module_stats.items():
            module_name = self.modules.get(module_id, {}).get('name', module_id.title())
            completed = module_stat.get('completed', 0)
            total = module_stat.get('total', 0)
            percentage = (completed / total * 100) if total > 0 else 0
            
            print(f"{module_name:<25} {completed:2d}/{total:<2d} topics ({percentage:5.1f}%)")
        
        print()
        
        # Weekly activity
        self._show_weekly_activity(stats)
    
    def _show_recent_achievements(self) -> None:
        """Show recently earned achievements."""
        recent_achievements = self.achievement_engine.get_recent_achievements(days=7)
        
        if not recent_achievements:
            return
        
        colors.print_subheader("Recent Achievements")
        
        for achievement in recent_achievements:
            badge = achievement.get('badge', '')
            name = achievement.get('name', 'Unknown Achievement')
            earned_date = achievement.get('earned_date', 'Unknown')
            
            print(f"  {badge} {colors.BOLD}{name}{colors.RESET} - {colors.GRAY}{earned_date}{colors.RESET}")
        print()
    
    def _show_learning_streak(self) -> None:
        """Show current learning streak information."""
        streak_data = self.progress_calc.get_learning_streak()
        
        if not streak_data:
            return
        
        colors.print_subheader("Learning Streak")
        
        current_streak = streak_data.get('current_streak', 0)
        longest_streak = streak_data.get('longest_streak', 0)
        last_activity = streak_data.get('last_activity', 'Never')
        
        # Streak visualization
        if current_streak > 0:
            fire_icons = "*" * min(current_streak, 10)
            if current_streak > 10:
                fire_icons += f" (+{current_streak - 10})"
            
            print(f"Current Streak: {colors.GREEN}{fire_icons}{colors.RESET} {current_streak} days")
        else:
            print(f"Current Streak: {colors.GRAY}0 days{colors.RESET}")
        
        print(f"Longest Streak: {colors.YELLOW}{longest_streak}{colors.RESET} days")
        print(f"Last Activity: {colors.BLUE}{last_activity}{colors.RESET}")
        
        # Streak motivation
        if current_streak == 0:
            print(f"\n{colors.CYAN}Start your learning streak today!{colors.RESET}")
        elif current_streak < 7:
            print(f"\n{colors.CYAN}Keep going! You're building a great habit!{colors.RESET}")
        elif current_streak < 30:
            print(f"\n{colors.GREEN}Amazing! You're on fire!{colors.RESET}")
        else:
            print(f"\n{colors.MAGENTA}Incredible dedication! You're a Python master in the making!{colors.RESET}")
        
        print()
    
    def _show_weekly_activity(self, stats: Dict[str, Any]) -> None:
        """Show weekly activity chart."""
        weekly_activity = stats.get('weekly_activity', {})
        
        if not weekly_activity:
            return
        
        colors.print_subheader("Weekly Activity")
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        max_activity = max(weekly_activity.values()) if weekly_activity.values() else 1
        
        for day in days:
            activity = weekly_activity.get(day.lower(), 0)
            bar_length = int((activity / max_activity) * 20) if max_activity > 0 else 0
            
            bar = "=" * bar_length + "-" * (20 - bar_length)
            color = colors.GREEN if activity > 0 else colors.GRAY
            
            print(f"{day}: {color}[{bar}]{colors.RESET} {activity} topics")
        
        print()
    
    def export_progress(self, format_type: str = 'json', output_file: Optional[str] = None) -> None:
        """
        Export progress data to file.
        
        Args:
            format_type: Export format ('json', 'csv', 'txt')
            output_file: Output file path (auto-generated if None)
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"python_mastery_progress_{timestamp}.{format_type}"
        
        try:
            if format_type == 'json':
                self._export_json(output_file)
            elif format_type == 'csv':
                self._export_csv(output_file)
            elif format_type == 'txt':
                self._export_txt(output_file)
            else:
                colors.print_error(f"Unsupported format: {format_type}")
                return
            
            colors.print_success(f"Progress exported to: {output_file}")
        
        except Exception as e:
            colors.print_error(f"Export failed: {e}")
    
    def _export_json(self, output_file: str) -> None:
        """Export progress data as JSON."""
        progress_data = {
            'export_date': datetime.now().isoformat(),
            'overall_stats': self.progress_calc.get_learning_statistics(),
            'modules': {},
            'achievements': self.achievement_engine.get_user_achievements()
        }
        
        for module_id, module_info in self.modules.items():
            progress = self.progress_calc.get_module_progress(module_id)
            progress_data['modules'][module_id] = {
                'name': module_info['name'],
                'progress': progress,
                'topics': module_info['topics']
            }
        
        with open(output_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
    
    def _export_csv(self, output_file: str) -> None:
        """Export progress data as CSV."""
        import csv
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Module', 'Topic', 'Completed', 'Completion_Date'])
            
            for module_id, module_info in self.modules.items():
                for topic in module_info['topics']:
                    is_completed = self.progress_calc.is_topic_completed(module_id, topic)
                    completion_date = self.progress_calc.get_topic_completion_date(module_id, topic)
                    
                    writer.writerow([
                        module_info['name'],
                        topic,
                        'Yes' if is_completed else 'No',
                        completion_date or ''
                    ])
    
    def _export_txt(self, output_file: str) -> None:
        """Export progress data as formatted text."""
        with open(output_file, 'w') as f:
            f.write("Python Mastery Hub - Progress Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Overall statistics
            stats = self.progress_calc.get_learning_statistics()
            f.write("Overall Statistics:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Learning Days: {stats.get('total_days', 0)}\n")
            f.write(f"Current Streak: {stats.get('current_streak', 0)} days\n")
            f.write(f"Longest Streak: {stats.get('longest_streak', 0)} days\n\n")
            
            # Module progress
            for module_id, module_info in self.modules.items():
                progress = self.progress_calc.get_module_progress(module_id)
                completed = progress.get('completed', 0) if progress else 0
                total = len(module_info['topics'])
                percentage = (completed / total * 100) if total > 0 else 0
                
                f.write(f"Module: {module_info['name']}\n")
                f.write(f"Progress: {completed}/{total} topics ({percentage:.1f}%)\n")
                f.write("Topics:\n")
                
                for topic in module_info['topics']:
                    status = "DONE" if self.progress_calc.is_topic_completed(module_id, topic) else "TODO"
                    f.write(f"  [{status}] {topic}\n")
                
                f.write("\n")


async def execute(args: argparse.Namespace) -> int:
    """Execute the progress command."""
    manager = ProgressManager()
    
    try:
        # Show overall progress (default)
        if not hasattr(args, 'action') or args.action == 'show' or not args.action:
            manager.show_overall_progress()
            return 0
        
        # Show specific module progress
        if args.action == 'module':
            if not hasattr(args, 'module_id') or not args.module_id:
                colors.print_error("Please specify a module ID")
                return 1
            
            manager.show_module_progress(args.module_id)
            return 0
        
        # Show achievements
        if args.action == 'achievements':
            manager.show_achievements()
            return 0
        
        # Show detailed statistics
        if args.action == 'stats':
            manager.show_statistics()
            return 0
        
        # Export progress
        if args.action == 'export':
            format_type = getattr(args, 'format', 'json')
            output_file = getattr(args, 'output', None)
            manager.export_progress(format_type, output_file)
            return 0
        
        # Reset progress (with confirmation)
        if args.action == 'reset':
            return await reset_progress(args)
        
        colors.print_error(f"Unknown action: {args.action}")
        return 1
    
    except Exception as e:
        logger.error(f"Progress command failed: {e}")
        colors.print_error(f"Command failed: {e}")
        return 1


async def reset_progress(args: argparse.Namespace) -> int:
    """Reset user progress with confirmation."""
    module_id = getattr(args, 'module_id', None)
    
    if module_id:
        message = f"Are you sure you want to reset progress for module '{module_id}'?"
    else:
        message = "Are you sure you want to reset ALL progress? This cannot be undone!"
    
    colors.print_warning(message)
    confirmation = input(f"{colors.CYAN}Type 'yes' to confirm: {colors.RESET}")
    
    if confirmation.lower() != 'yes':
        colors.print_info("Reset cancelled")
        return 0
    
    try:
        progress_calc = ProgressCalculator()
        
        if module_id:
            progress_calc.reset_module_progress(module_id)
            colors.print_success(f"Progress reset for module: {module_id}")
        else:
            progress_calc.reset_all_progress()
            colors.print_success("All progress has been reset")
        
        return 0
    
    except Exception as e:
        colors.print_error(f"Reset failed: {e}")
        return 1


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Setup the progress command parser."""
    subparsers = parser.add_subparsers(
        dest='action',
        help='Progress command actions'
    )
    
    # Show progress (default)
    show_parser = subparsers.add_parser(
        'show',
        help='Show overall progress summary'
    )
    
    # Module-specific progress
    module_parser = subparsers.add_parser(
        'module',
        help='Show progress for specific module'
    )
    module_parser.add_argument(
        'module_id',
        help='Module identifier (basics, oop, advanced, etc.)'
    )
    
    # Achievements
    achievements_parser = subparsers.add_parser(
        'achievements',
        help='Show achievements and badges'
    )
    
    # Statistics
    stats_parser = subparsers.add_parser(
        'stats',
        help='Show detailed learning statistics'
    )
    
    # Export
    export_parser = subparsers.add_parser(
        'export',
        help='Export progress data'
    )
    export_parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv', 'txt'],
        default='json',
        help='Export format (default: json)'
    )
    export_parser.add_argument(
        '--output', '-o',
        help='Output file path'
    )
    
    # Reset
    reset_parser = subparsers.add_parser(
        'reset',
        help='Reset progress (with confirmation)'
    )
    reset_parser.add_argument(
        'module_id',
        nargs='?',
        help='Module to reset (omit to reset all)'
    )
    
    # Global options
    parser.add_argument(
        '--show', '-s',
        action='store_const',
        const='show',
        dest='action',
        help='Show overall progress (default action)'
    )