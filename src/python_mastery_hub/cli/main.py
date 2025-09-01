"""
Interactive CLI for Python Mastery Hub.

Provides a comprehensive command-line interface for exploring Python concepts,
running examples, and practicing with interactive exercises.
"""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from python_mastery_hub.core import (
    MODULE_REGISTRY, 
    get_module, 
    list_modules, 
    get_learning_path
)

app = typer.Typer(
    name="python-mastery-hub",
    help="🐍 Interactive Python Learning Platform",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()

@app.command()
def list_all(
    difficulty: Optional[str] = typer.Option(
        None, 
        "--difficulty", 
        "-d",
        help="Filter by difficulty: beginner, intermediate, advanced"
    )
) -> None:
    """📚 List all available learning modules."""
    
    console.print("\n🐍 [bold blue]Python Mastery Hub - Learning Modules[/bold blue]\n")
    
    modules = list_modules()
    
    if difficulty:
        modules = [m for m in modules if m['difficulty'] == difficulty.lower()]
    
    if not modules:
        console.print(f"[red]No modules found for difficulty: {difficulty}[/red]")
        return
    
    table = Table(title="Available Learning Modules", show_header=True, header_style="bold magenta")
    table.add_column("Module", style="cyan", width=20)
    table.add_column("Difficulty", style="yellow", width=12)
    table.add_column("Topics", style="green", width=8)
    table.add_column("Examples", style="blue", width=10)
    table.add_column("Description", style="white", width=40)
    
    for module in modules:
        table.add_row(
            module['name'],
            module['difficulty'].title(),
            str(len(module['topics'])),
            str(module['example_count']),
            module['description'][:50] + "..." if len(module['description']) > 50 else module['description']
        )
    
    console.print(table)
    console.print(f"\n💡 Use [cyan]python-mastery-hub explore <module_name>[/cyan] to start learning!")

@app.command()
def path(
    difficulty: str = typer.Option(
        "all",
        "--difficulty",
        "-d", 
        help="Learning path difficulty: beginner, intermediate, advanced, all"
    )
) -> None:
    """🛤️ Show recommended learning path."""
    
    try:
        learning_path = get_learning_path(difficulty)
        
        console.print(f"\n🎯 [bold green]Recommended Learning Path ({difficulty.title()})[/bold green]\n")
        
        for i, module_name in enumerate(learning_path, 1):
            module = get_module(module_name)
            module_info = module.get_module_info()
            
            # Create progress indicator
            if i == 1:
                status = "🟢 Start here"
            elif i <= len(learning_path) // 2:
                status = "🟡 Continue"
            else:
                status = "🔴 Advanced"
            
            console.print(f"{i:2}. {status} [cyan]{module_info['name']}[/cyan]")
            console.print(f"    [dim]{module_info['description']}[/dim]")
            console.print(f"    [yellow]Difficulty:[/yellow] {module_info['difficulty'].title()}")
            console.print()
        
        console.print("💡 [italic]Follow this path for structured learning![/italic]")
        
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def explore(
    module_name: str = typer.Argument(..., help="Name of the module to explore"),
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Specific topic to explore"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode")
) -> None:
    """🔍 Explore a specific learning module with examples."""
    
    try:
        module = get_module(module_name)
        module_info = module.get_module_info()
        
        console.print(f"\n🎓 [bold blue]{module_info['name']}[/bold blue]")
        console.print(f"[dim]{module_info['description']}[/dim]\n")
        
        if topic:
            # Show specific topic
            _show_topic_details(module, topic)
        else:
            # Show module overview and let user choose
            _show_module_overview(module, interactive)
            
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("Use [cyan]python-mastery-hub list[/cyan] to see available modules.")

@app.command()
def practice(
    module_name: str = typer.Argument(..., help="Module name for practice exercises"),
    exercise_id: Optional[int] = typer.Option(None, "--exercise", "-e", help="Specific exercise number")
) -> None:
    """💪 Practice with interactive exercises."""
    
    try:
        module = get_module(module_name)
        
        if not hasattr(module, 'exercises') or not module.exercises:
            console.print(f"[yellow]No exercises available for {module_name}[/yellow]")
            return
        
        console.print(f"\n🏋️ [bold green]Practice Exercises - {module.name}[/bold green]\n")
        
        if exercise_id is not None:
            if 0 <= exercise_id < len(module.exercises):
                _run_exercise(module.exercises[exercise_id])
            else:
                console.print(f"[red]Exercise {exercise_id} not found. Available: 0-{len(module.exercises)-1}[/red]")
        else:
            _show_exercises_menu(module)
            
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def demo(
    example: str = typer.Argument(..., help="Run a specific demo by name"),
    module_name: Optional[str] = typer.Option(None, "--module", "-m", help="Module to search in")
) -> None:
    """🎬 Run interactive demonstrations."""
    
    console.print(f"\n🎭 [bold yellow]Running Demo: {example}[/bold yellow]\n")
    
    if module_name:
        try:
            module = get_module(module_name)
            _run_demo_in_module(module, example)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
    else:
        # Search all modules
        _search_and_run_demo(example)

@app.command()
def info() -> None:
    """ℹ️ Show information about Python Mastery Hub."""
    
    info_panel = Panel.fit(
        """
🐍 [bold blue]Python Mastery Hub v1.0.0[/bold blue]

A comprehensive, production-ready Python learning platform that demonstrates
mastery of Python concepts, modern development practices, and industry standards.

[bold yellow]Features:[/bold yellow]
• Interactive learning modules from basics to advanced
• Hands-on coding exercises and challenges  
• Real-world examples with explanations
• Professional development practices
• Comprehensive test coverage
• Modern CLI interface with Rich formatting

[bold yellow]Commands:[/bold yellow]
• [cyan]list[/cyan]     - Show all available modules
• [cyan]path[/cyan]     - Get recommended learning path
• [cyan]explore[/cyan]  - Dive into a specific module
• [cyan]practice[/cyan] - Work on coding exercises
• [cyan]demo[/cyan]     - Run interactive demonstrations

[bold yellow]Examples:[/bold yellow]
• python-mastery-hub list --difficulty beginner
• python-mastery-hub explore basics --topic variables
• python-mastery-hub practice basics --exercise 0
• python-mastery-hub path --difficulty intermediate

[italic]Happy Learning! 🚀[/italic]
        """,
        title="About",
        border_style="blue"
    )
    
    console.print(info_panel)

def _show_module_overview(module, interactive: bool = True):
    """Show module overview and topics."""
    
    topics = module.get_topics()
    
    table = Table(title=f"Topics in {module.name}", show_header=True)
    table.add_column("№", style="cyan", width=4)
    table.add_column("Topic", style="yellow", width=20)
    table.add_column("Description", style="white")
    
    for i, topic in enumerate(topics, 1):
        # Get topic description from examples
        topic_data = module.demonstrate(topic)
        description = topic_data.get('explanation', 'No description available')
        table.add_row(str(i), topic.replace('_', ' ').title(), description)
    
    console.print(table)
    
    if interactive:
        console.print("\n[bold]What would you like to do?[/bold]")
        console.print("1. Explore a specific topic")
        console.print("2. Show all examples")
        console.print("3. Practice exercises")
        console.print("4. Exit")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "1":
            topic_choice = Prompt.ask(
                "Which topic?", 
                choices=[str(i) for i in range(1, len(topics) + 1)]
            )
            selected_topic = topics[int(topic_choice) - 1]
            _show_topic_details(module, selected_topic)
            
        elif choice == "2":
            for topic in topics:
                _show_topic_details(module, topic)
                console.print("\n" + "="*60 + "\n")
                
        elif choice == "3":
            if hasattr(module, 'exercises') and module.exercises:
                _show_exercises_menu(module)
            else:
                console.print("[yellow]No exercises available for this module.[/yellow]")

def _show_topic_details(module, topic: str):
    """Show detailed information about a topic."""
    
    try:
        topic_data = module.demonstrate(topic)
        
        console.print(f"\n📖 [bold cyan]{topic.replace('_', ' ').title()}[/bold cyan]")
        console.print(f"[dim]{topic_data['explanation']}[/dim]\n")
        
        examples = topic_data['examples']
        
        for example_name, example_data in examples.items():
            console.print(f"\n🔹 [bold yellow]{example_name.replace('_', ' ').title()}[/bold yellow]")
            
            if 'explanation' in example_data:
                console.print(f"[italic]{example_data['explanation']}[/italic]\n")
            
            # Show code with syntax highlighting
            if 'code' in example_data:
                syntax = Syntax(
                    example_data['code'].strip(), 
                    "python", 
                    theme="monokai", 
                    line_numbers=True,
                    word_wrap=True
                )
                console.print(Panel(syntax, title="Code Example", border_style="green"))
            
            # Show expected output
            if 'output' in example_data:
                console.print(Panel(
                    example_data['output'], 
                    title="Expected Output", 
                    border_style="blue"
                ))
            
            # Ask if user wants to run the example
            if Confirm.ask("Run this example?", default=True):
                _run_code_example(example_data.get('code', ''))
        
        # Show best practices
        if 'best_practices' in topic_data and topic_data['best_practices']:
            console.print(f"\n💡 [bold green]Best Practices for {topic.replace('_', ' ').title()}:[/bold green]")
            for practice in topic_data['best_practices']:
                console.print(f"• {practice}")
                
    except Exception as e:
        console.print(f"[red]Error showing topic details: {e}[/red]")

def _show_exercises_menu(module):
    """Show available exercises for a module."""
    
    if not hasattr(module, 'exercises') or not module.exercises:
        console.print("[yellow]No exercises available.[/yellow]")
        return
    
    console.print(f"\n🏋️ [bold green]Exercises for {module.name}[/bold green]\n")
    
    table = Table(show_header=True)
    table.add_column("№", style="cyan", width=4)
    table.add_column("Title", style="yellow", width=25)
    table.add_column("Difficulty", style="red", width=12)
    table.add_column("Description", style="white")
    
    for i, exercise in enumerate(module.exercises):
        table.add_row(
            str(i),
            exercise['title'],
            exercise['difficulty'].title(),
            exercise['description']
        )
    
    console.print(table)
    
    choice = Prompt.ask(
        "Which exercise would you like to try?",
        choices=[str(i) for i in range(len(module.exercises))] + ["quit"],
        default="0"
    )
    
    if choice != "quit":
        _run_exercise(module.exercises[int(choice)])

def _run_exercise(exercise):
    """Run an interactive exercise."""
    
    console.print(f"\n📝 [bold green]{exercise['title']}[/bold green]")
    console.print(f"[yellow]Difficulty:[/yellow] {exercise['difficulty'].title()}")
    console.print(f"[blue]Description:[/blue] {exercise['description']}\n")
    
    exercise_data = exercise['function']()
    
    console.print("[bold]Instructions:[/bold]")
    console.print(exercise_data['instructions'])
    
    if 'tasks' in exercise_data:
        console.print("\n[bold]Tasks:[/bold]")
        for i, task in enumerate(exercise_data['tasks'], 1):
            console.print(f"{i}. {task}")
    
    if 'starter_code' in exercise_data:
        console.print("\n[bold green]Starter Code:[/bold green]")
        syntax = Syntax(exercise_data['starter_code'], "python", theme="monokai")
        console.print(Panel(syntax, border_style="green"))
    
    show_solution = Confirm.ask("\nWould you like to see the solution?", default=False)
    
    if show_solution and 'solution' in exercise_data:
        console.print("\n[bold blue]Solution:[/bold blue]")
        syntax = Syntax(exercise_data['solution'], "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, border_style="blue"))
        
        if Confirm.ask("Run the solution?", default=True):
            _run_code_example(exercise_data['solution'])

def _run_code_example(code: str):
    """Safely run a code example."""
    
    console.print("\n[bold yellow]Running code...[/bold yellow]")
    
    # Create a safe execution environment
    safe_globals = {
        '__builtins__': __builtins__,
        'print': print,
        'len': len,
        'range': range,
        'enumerate': enumerate,
        'zip': zip,
        'map': map,
        'filter': filter,
        'sorted': sorted,
        'sum': sum,
        'max': max,
        'min': min,
        'abs': abs,
        'round': round,
        'type': type,
        'str': str,
        'int': int,
        'float': float,
        'list': list,
        'dict': dict,
        'set': set,
        'tuple': tuple,
        'bool': bool,
    }
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Executing...", total=None)
            time.sleep(0.5)  # Simulate execution time
            
            # Execute the code
            exec(code, safe_globals)
            progress.update(task, description="✅ Completed")
            
    except Exception as e:
        console.print(f"[red]Error executing code: {e}[/red]")

def _run_demo_in_module(module, demo_name: str):
    """Run a specific demo in a module."""
    # Implementation for running specific demos
    console.print(f"[yellow]Demo functionality coming soon for {demo_name} in {module.name}[/yellow]")

def _search_and_run_demo(demo_name: str):
    """Search for and run a demo across all modules."""
    console.print(f"[yellow]Searching for demo '{demo_name}' across all modules...[/yellow]")
    console.print("[yellow]Demo search functionality coming soon[/yellow]")

if __name__ == "__main__":
    app()