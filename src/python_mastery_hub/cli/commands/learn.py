"""
Learn Command - Interactive Learning Module Access

Provides command-line access to all learning modules with interactive features.
"""

import argparse
import asyncio
from typing import List, Dict, Any
from pathlib import Path

from python_mastery_hub.core.basics import base as basics_base
from python_mastery_hub.core.oop import core as oop_core
from python_mastery_hub.core.advanced import base as advanced_base
from python_mastery_hub.core.data_structures import config as ds_config
from python_mastery_hub.core.algorithms import base as algo_base
from python_mastery_hub.core.async_programming import base as async_base
from python_mastery_hub.core.web_development import core as web_core
from python_mastery_hub.core.data_science import config as ds_science_config
from python_mastery_hub.core.testing import core as testing_core

from python_mastery_hub.cli.utils import colors, progress_bar
from python_mastery_hub.utils.progress_calculator import ProgressCalculator
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)


class LearningModuleManager:
    """Manages access to learning modules and tracks progress."""
    
    def __init__(self):
        self.modules = self._initialize_modules()
        self.progress_calc = ProgressCalculator()
    
    def _initialize_modules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available learning modules."""
        return {
            'basics': {
                'name': 'Python Basics',
                'description': 'Variables, data types, control flow, functions',
                'difficulty': 'Beginner',
                'estimated_time': '2-4 hours',
                'topics': [
                    'Variables and Assignment',
                    'Data Types (int, float, str, bool)',
                    'Control Flow (if/else, loops)',
                    'Functions and Scope',
                    'Error Handling Basics'
                ],
                'module': basics_base,
                'color': colors.GREEN
            },
            'oop': {
                'name': 'Object-Oriented Programming',
                'description': 'Classes, inheritance, polymorphism, design patterns',
                'difficulty': 'Intermediate',
                'estimated_time': '4-6 hours',
                'topics': [
                    'Classes and Objects',
                    'Inheritance and MRO',
                    'Polymorphism and Duck Typing',
                    'Abstract Base Classes',
                    'Design Patterns'
                ],
                'module': oop_core,
                'color': colors.BLUE
            },
            'advanced': {
                'name': 'Advanced Python',
                'description': 'Decorators, generators, metaclasses, descriptors',
                'difficulty': 'Advanced',
                'estimated_time': '6-8 hours',
                'topics': [
                    'Decorators and Closures',
                    'Generators and Iterators',
                    'Context Managers',
                    'Metaclasses',
                    'Descriptors'
                ],
                'module': advanced_base,
                'color': colors.PURPLE
            },
            'data_structures': {
                'name': 'Data Structures',
                'description': 'Lists, dicts, sets, custom collections',
                'difficulty': 'Intermediate',
                'estimated_time': '3-5 hours',
                'topics': [
                    'Built-in Collections',
                    'Custom Data Structures',
                    'Performance Analysis',
                    'Memory Optimization',
                    'Collections Module'
                ],
                'module': ds_config,
                'color': colors.CYAN
            },
            'algorithms': {
                'name': 'Algorithms',
                'description': 'Sorting, searching, dynamic programming',
                'difficulty': 'Intermediate-Advanced',
                'estimated_time': '5-7 hours',
                'topics': [
                    'Sorting Algorithms',
                    'Searching Techniques',
                    'Graph Algorithms',
                    'Dynamic Programming',
                    'Big O Analysis'
                ],
                'module': algo_base,
                'color': colors.YELLOW
            },
            'async': {
                'name': 'Async Programming',
                'description': 'asyncio, threading, multiprocessing',
                'difficulty': 'Advanced',
                'estimated_time': '6-8 hours',
                'topics': [
                    'Asyncio Fundamentals',
                    'Threading Concepts',
                    'Multiprocessing',
                    'Concurrent Futures',
                    'Performance Considerations'
                ],
                'module': async_base,
                'color': colors.MAGENTA
            },
            'web': {
                'name': 'Web Development',
                'description': 'APIs, databases, frameworks',
                'difficulty': 'Intermediate-Advanced',
                'estimated_time': '8-10 hours',
                'topics': [
                    'HTTP and REST APIs',
                    'Database Integration',
                    'Web Frameworks',
                    'Authentication',
                    'WebSockets'
                ],
                'module': web_core,
                'color': colors.RED
            },
            'data_science': {
                'name': 'Data Science',
                'description': 'NumPy, Pandas, visualization',
                'difficulty': 'Intermediate',
                'estimated_time': '6-8 hours',
                'topics': [
                    'NumPy Arrays',
                    'Pandas DataFrames',
                    'Data Visualization',
                    'Statistical Analysis',
                    'Machine Learning Basics'
                ],
                'module': ds_science_config,
                'color': colors.ORANGE
            },
            'testing': {
                'name': 'Testing & Quality',
                'description': 'Unit tests, TDD, mocking, quality assurance',
                'difficulty': 'Intermediate',
                'estimated_time': '4-6 hours',
                'topics': [
                    'Unit Testing with pytest',
                    'Test-Driven Development',
                    'Mocking and Fixtures',
                    'Integration Testing',
                    'Code Quality Tools'
                ],
                'module': testing_core,
                'color': colors.LIGHT_BLUE
            }
        }
    
    def list_modules(self) -> None:
        """Display all available learning modules."""
        print(f"\n{colors.BOLD}📚 Available Learning Modules{colors.RESET}\n")
        
        for module_id, module_info in self.modules.items():
            color = module_info['color']
            name = module_info['name']
            description = module_info['description']
            difficulty = module_info['difficulty']
            time = module_info['estimated_time']
            
            print(f"{color}🎯 {name}{colors.RESET}")
            print(f"   {description}")
            print(f"   Difficulty: {difficulty} | Time: {time}")
            print(f"   Command: {colors.GRAY}python-mastery-hub learn {module_id}{colors.RESET}")
            print()
    
    def show_module_details(self, module_id: str) -> None:
        """Show detailed information about a specific module."""
        if module_id not in self.modules:
            print(f"{colors.RED}❌ Module '{module_id}' not found{colors.RESET}")
            self.list_modules()
            return
        
        module = self.modules[module_id]
        color = module['color']
        
        print(f"\n{color}{colors.BOLD}📖 {module['name']}{colors.RESET}\n")
        print(f"Description: {module['description']}")
        print(f"Difficulty: {module['difficulty']}")
        print(f"Estimated Time: {module['estimated_time']}")
        print(f"\n{colors.BOLD}Topics Covered:{colors.RESET}")
        
        for i, topic in enumerate(module['topics'], 1):
            print(f"  {i}. {topic}")
        
        # Show progress if available
        progress = self.progress_calc.get_module_progress(module_id)
        if progress:
            print(f"\n{colors.BOLD}Your Progress:{colors.RESET}")
            progress_bar.show_progress(progress['completed'], progress['total'])
            print(f"Completed: {progress['completed']}/{progress['total']} topics")
        
        print(f"\n{colors.GREEN}Ready to start? Run:{colors.RESET}")
        print(f"  python-mastery-hub learn {module_id} --start")
        print()


async def execute(args: argparse.Namespace) -> int:
    """Execute the learn command."""
    manager = LearningModuleManager()
    
    # If no module specified, show available modules
    if not hasattr(args, 'module') or not args.module:
        manager.list_modules()
        return 0
    
    module_id = args.module
    
    # Show module details
    if hasattr(args, 'info') and args.info:
        manager.show_module_details(module_id)
        return 0
    
    # Start interactive learning
    if hasattr(args, 'start') and args.start:
        return await start_interactive_learning(module_id, args)
    
    # List topics for the module
    if hasattr(args, 'list_topics') and args.list_topics:
        manager.show_module_details(module_id)
        return 0
    
    # Default: show module info
    manager.show_module_details(module_id)
    return 0


async def start_interactive_learning(module_id: str, args: argparse.Namespace) -> int:
    """Start interactive learning session for a module."""
    manager = LearningModuleManager()
    
    if module_id not in manager.modules:
        print(f"{colors.RED}❌ Module '{module_id}' not found{colors.RESET}")
        return 1
    
    module = manager.modules[module_id]
    color = module['color']
    
    print(f"\n{color}{colors.BOLD}🚀 Starting {module['name']} Learning Session{colors.RESET}\n")
    
    # Interactive menu for topics
    topics = module['topics']
    while True:
        print(f"{colors.BOLD}Select a topic to explore:{colors.RESET}")
        for i, topic in enumerate(topics, 1):
            status = "✅" if manager.progress_calc.is_topic_completed(module_id, topic) else "⭕"
            print(f"  {i}. {status} {topic}")
        
        print(f"  0. {colors.RED}Exit{colors.RESET}")
        
        try:
            choice = input(f"\n{colors.CYAN}Enter your choice (0-{len(topics)}): {colors.RESET}")
            choice = int(choice)
            
            if choice == 0:
                print(f"{colors.YELLOW}👋 Learning session ended{colors.RESET}")
                break
            elif 1 <= choice <= len(topics):
                topic = topics[choice - 1]
                await explore_topic(module_id, topic, module)
            else:
                print(f"{colors.RED}❌ Invalid choice. Please try again.{colors.RESET}")
        
        except (ValueError, KeyboardInterrupt):
            print(f"\n{colors.YELLOW}👋 Learning session ended{colors.RESET}")
            break
    
    return 0


async def explore_topic(module_id: str, topic: str, module_info: Dict[str, Any]) -> None:
    """Explore a specific topic within a module."""
    color = module_info['color']
    
    print(f"\n{color}{colors.BOLD}📚 Exploring: {topic}{colors.RESET}\n")
    
    # Simulate loading content (in real implementation, this would load actual content)
    print(f"{colors.BLUE}Loading content...{colors.RESET}")
    await asyncio.sleep(1)  # Simulate loading time
    
    # Show topic content menu
    options = [
        "📖 Read Theory",
        "💻 Code Examples",
        "🏃 Interactive Exercise",
        "🧪 Quick Quiz",
        "📝 Summary Notes"
    ]
    
    print(f"{colors.BOLD}What would you like to do?{colors.RESET}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print(f"  0. {colors.YELLOW}← Back to topics{colors.RESET}")
    
    try:
        choice = input(f"\n{colors.CYAN}Enter your choice (0-{len(options)}): {colors.RESET}")
        choice = int(choice)
        
        if choice == 0:
            return
        elif 1 <= choice <= len(options):
            await handle_topic_action(choice, module_id, topic)
        else:
            print(f"{colors.RED}❌ Invalid choice{colors.RESET}")
    
    except (ValueError, KeyboardInterrupt):
        return


async def handle_topic_action(action: int, module_id: str, topic: str) -> None:
    """Handle the selected action for a topic."""
    actions = {
        1: "📖 Displaying theory and concepts...",
        2: "💻 Loading code examples...",
        3: "🏃 Starting interactive exercise...",
        4: "🧪 Preparing quiz questions...",
        5: "📝 Generating summary notes..."
    }
    
    print(f"\n{colors.GREEN}{actions[action]}{colors.RESET}")
    
    # Simulate processing time
    for i in range(3):
        print(".", end="", flush=True)
        await asyncio.sleep(0.5)
    
    print(f"\n{colors.BLUE}Content loaded! (This would show actual content in full implementation){colors.RESET}")
    
    # Mark as completed
    progress_calc = ProgressCalculator()
    progress_calc.mark_topic_completed(module_id, topic)
    
    print(f"{colors.GREEN}✅ Topic marked as completed!{colors.RESET}")
    
    input(f"\n{colors.GRAY}Press Enter to continue...{colors.RESET}")


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Setup the learn command parser."""
    parser.add_argument(
        'module',
        nargs='?',
        help='Learning module to access (basics, oop, advanced, etc.)'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        dest='list_modules',
        help='List all available modules'
    )
    
    parser.add_argument(
        '--info', '-i',
        action='store_true',
        help='Show detailed information about the module'
    )
    
    parser.add_argument(
        '--start', '-s',
        action='store_true',
        help='Start interactive learning session'
    )
    
    parser.add_argument(
        '--topics', '-t',
        action='store_true',
        dest='list_topics',
        help='List topics in the module'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Enable interactive mode'
    )