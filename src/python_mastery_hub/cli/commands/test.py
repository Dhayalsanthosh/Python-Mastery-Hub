"""
Test Command - Exercise and Assessment Execution

Provides command-line interface for running exercises, tests, and assessments
across all learning modules with comprehensive feedback and scoring.
"""

import argparse
import asyncio
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import traceback

from python_mastery_hub.cli.utils import colors, progress_bar
from python_mastery_hub.utils.progress_calculator import ProgressCalculator
from python_mastery_hub.utils.achievement_engine import AchievementEngine
from python_mastery_hub.utils.logging_config import get_logger, PerformanceLogger

logger = get_logger(__name__)


class ExerciseResult:
    """Represents the result of running an exercise."""
    
    def __init__(
        self,
        exercise_name: str,
        module_id: str,
        passed: bool,
        score: float,
        max_score: float,
        execution_time: float,
        feedback: List[str],
        errors: List[str] = None
    ):
        self.exercise_name = exercise_name
        self.module_id = module_id
        self.passed = passed
        self.score = score
        self.max_score = max_score
        self.execution_time = execution_time
        self.feedback = feedback
        self.errors = errors or []
        self.percentage = (score / max_score * 100) if max_score > 0 else 0


class TestRunner:
    """Manages test execution and result reporting."""
    
    def __init__(self):
        self.progress_calc = ProgressCalculator()
        self.achievement_engine = AchievementEngine()
        self.module_exercises = self._discover_exercises()
    
    def _discover_exercises(self) -> Dict[str, Dict[str, Any]]:
        """Discover available exercises across all modules."""
        modules = {
            'basics': {
                'name': 'Python Basics',
                'exercises': [
                    'control_flow_exercise',
                    'data_type_conversion_exercise',
                    'function_design_exercise',
                    'variable_assignment_exercise'
                ],
                'color': colors.GREEN
            },
            'oop': {
                'name': 'Object-Oriented Programming',
                'exercises': [
                    'employee_hierarchy_exercise',
                    'library_exercise',
                    'observer_pattern_exercise',
                    'shape_calculator_exercise'
                ],
                'color': colors.BLUE
            },
            'advanced': {
                'name': 'Advanced Python',
                'exercises': [
                    'caching_director',
                    'file_pipeline',
                    'orm_metaclass',
                    'transaction_manager'
                ],
                'color': colors.MAGENTA
            },
            'data_structures': {
                'name': 'Data Structures',
                'exercises': [
                    'bst',
                    'cache',
                    'learning_path',
                    'linkedlist',
                    'registry'
                ],
                'color': colors.CYAN
            },
            'algorithms': {
                'name': 'Algorithms',
                'exercises': [
                    'dijkstra_exercise',
                    'lcs_exercise',
                    'quicksort_exercise'
                ],
                'color': colors.YELLOW
            },
            'async_programming': {
                'name': 'Async Programming',
                'exercises': [
                    'async_scraper_exercise',
                    'parallel_processor_exercise',
                    'producer_consumer_exercise'
                ],
                'color': colors.LIGHT_MAGENTA
            },
            'web_development': {
                'name': 'Web Development',
                'exercises': [
                    'flask_blog_exercise',
                    'jwt_auth_exercise',
                    'microservice_exercise',
                    'rest_api_exercise',
                    'websocket_chat_exercise'
                ],
                'color': colors.RED
            },
            'data_science': {
                'name': 'Data Science',
                'exercises': [
                    'dashboard',
                    'data_analysis',
                    'ml_pipeline'
                ],
                'color': colors.LIGHT_BLUE
            },
            'testing': {
                'name': 'Testing & Quality',
                'exercises': [
                    'integration_exercise',
                    'mocking_exercise',
                    'tdd_exercise',
                    'unittest_exercise'
                ],
                'color': colors.LIGHT_GREEN
            }
        }
        return modules
    
    def list_available_tests(self, module_id: Optional[str] = None) -> None:
        """List all available tests/exercises."""
        colors.print_header("🧪 Available Tests and Exercises")
        
        modules_to_show = [module_id] if module_id else self.module_exercises.keys()
        
        for mod_id in modules_to_show:
            if mod_id not in self.module_exercises:
                colors.print_error(f"Module '{mod_id}' not found")
                continue
            
            module = self.module_exercises[mod_id]
            color = module['color']
            
            colors.print_subheader(f"{color}{module['name']}{colors.RESET}")
            
            for i, exercise in enumerate(module['exercises'], 1):
                # Check if exercise has been completed
                is_completed = self.progress_calc.is_topic_completed(mod_id, exercise)
                status = f"{colors.GREEN}✅{colors.RESET}" if is_completed else f"{colors.GRAY}⭕{colors.RESET}"
                
                exercise_name = exercise.replace('_', ' ').title()
                print(f"  {i:2d}. {status} {exercise_name}")
                print(f"      Command: {colors.GRAY}python-mastery-hub test {mod_id} {exercise}{colors.RESET}")
            
            print()
    
    async def run_exercise(
        self, 
        module_id: str, 
        exercise_name: str, 
        verbose: bool = False
    ) -> ExerciseResult:
        """
        Run a specific exercise and return results.
        
        Args:
            module_id: Module identifier
            exercise_name: Exercise name
            verbose: Enable verbose output
            
        Returns:
            ExerciseResult object
        """
        if module_id not in self.module_exercises:
            raise ValueError(f"Unknown module: {module_id}")
        
        module = self.module_exercises[module_id]
        if exercise_name not in module['exercises']:
            raise ValueError(f"Exercise '{exercise_name}' not found in module '{module_id}'")
        
        colors.print_header(f"🏃 Running Exercise: {exercise_name.replace('_', ' ').title()}")
        
        with PerformanceLogger(f"exercise_{module_id}_{exercise_name}") as perf:
            try:
                # Import the exercise module
                exercise_module = await self._import_exercise(module_id, exercise_name)
                
                if verbose:
                    colors.print_info(f"Loaded exercise module: {exercise_module.__name__}")
                
                # Run the exercise
                result = await self._execute_exercise(exercise_module, verbose)
                
                # Update progress if passed
                if result.passed:
                    self.progress_calc.mark_topic_completed(
                        module_id, 
                        exercise_name,
                        score=result.percentage / 100,
                        time_spent=int(result.execution_time / 60)
                    )
                    
                    # Check for achievements
                    achievements = self.achievement_engine.check_achievements(
                        'exercise_completed',
                        {
                            'module_id': module_id,
                            'exercise_name': exercise_name,
                            'score': result.percentage,
                            'execution_time': result.execution_time
                        }
                    )
                    
                    if achievements:
                        self._show_achievements(achievements)
                
                return result
                
            except Exception as e:
                logger.error(f"Exercise execution failed: {e}")
                return ExerciseResult(
                    exercise_name=exercise_name,
                    module_id=module_id,
                    passed=False,
                    score=0,
                    max_score=100,
                    execution_time=perf.start_time and (datetime.now() - perf.start_time).total_seconds() or 0,
                    feedback=[f"Exercise failed to run: {str(e)}"],
                    errors=[traceback.format_exc()]
                )
    
    async def _import_exercise(self, module_id: str, exercise_name: str):
        """Import an exercise module dynamically."""
        try:
            # Construct module path
            if module_id == 'advanced':
                module_path = f"python_mastery_hub.core.advanced.classes.utilities.exercises.{exercise_name}"
            else:
                module_path = f"python_mastery_hub.core.{module_id}.exercises.{exercise_name}"
            
            # Import the module
            return importlib.import_module(module_path)
            
        except ImportError as e:
            logger.error(f"Failed to import exercise {exercise_name}: {e}")
            raise ValueError(f"Exercise '{exercise_name}' could not be loaded")
    
    async def _execute_exercise(self, exercise_module, verbose: bool) -> ExerciseResult:
        """Execute an exercise module and collect results."""
        start_time = datetime.now()
        
        # Look for common exercise patterns
        exercise_class = None
        test_functions = []
        
        # Find exercise class or test functions
        for attr_name in dir(exercise_module):
            attr = getattr(exercise_module, attr_name)
            
            if (isinstance(attr, type) and 
                ('Exercise' in attr_name or 'Test' in attr_name) and
                attr_name != 'Exercise'):
                exercise_class = attr
                break
            elif (callable(attr) and 
                  (attr_name.startswith('test_') or attr_name.startswith('exercise_'))):
                test_functions.append((attr_name, attr))
        
        feedback = []
        errors = []
        total_score = 0
        max_score = 0
        
        try:
            if exercise_class:
                # Run class-based exercise
                if verbose:
                    colors.print_info(f"Running class-based exercise: {exercise_class.__name__}")
                
                exercise_instance = exercise_class()
                result = await self._run_class_exercise(exercise_instance, verbose)
                
                feedback.extend(result.get('feedback', []))
                errors.extend(result.get('errors', []))
                total_score = result.get('score', 0)
                max_score = result.get('max_score', 100)
                
            elif test_functions:
                # Run function-based tests
                if verbose:
                    colors.print_info(f"Running {len(test_functions)} test functions")
                
                for func_name, func in test_functions:
                    try:
                        if verbose:
                            print(f"  Running {func_name}...")
                        
                        if asyncio.iscoroutinefunction(func):
                            result = await func()
                        else:
                            result = func()
                        
                        if result is True or result is None:
                            total_score += 1
                            feedback.append(f"✅ {func_name}: PASSED")
                        elif isinstance(result, dict):
                            score = result.get('score', 0)
                            total_score += score
                            feedback.append(f"✅ {func_name}: {result.get('message', 'PASSED')}")
                        else:
                            feedback.append(f"❌ {func_name}: FAILED")
                            
                        max_score += 1
                        
                    except Exception as e:
                        errors.append(f"Error in {func_name}: {str(e)}")
                        feedback.append(f"❌ {func_name}: ERROR - {str(e)}")
                        max_score += 1
                        
                        if verbose:
                            logger.error(f"Test function {func_name} failed: {e}")
            
            else:
                # No recognizable exercise pattern
                feedback.append("❌ No executable exercise found in module")
                errors.append("Module does not contain recognizable exercise pattern")
                max_score = 1
        
        except Exception as e:
            errors.append(f"Exercise execution failed: {str(e)}")
            feedback.append(f"❌ Exercise failed: {str(e)}")
            max_score = max_score or 1
        
        execution_time = (datetime.now() - start_time).total_seconds()
        passed = len(errors) == 0 and total_score > 0
        
        return ExerciseResult(
            exercise_name=exercise_module.__name__.split('.')[-1],
            module_id='unknown',  # Will be set by caller
            passed=passed,
            score=total_score,
            max_score=max_score,
            execution_time=execution_time,
            feedback=feedback,
            errors=errors
        )
    
    async def _run_class_exercise(self, exercise_instance, verbose: bool) -> Dict[str, Any]:
        """Run a class-based exercise."""
        result = {'score': 0, 'max_score': 100, 'feedback': [], 'errors': []}
        
        try:
            # Look for run, execute, or test methods
            run_methods = []
            for method_name in dir(exercise_instance):
                if (method_name.startswith(('run', 'execute', 'test')) and 
                    not method_name.startswith('_') and
                    callable(getattr(exercise_instance, method_name))):
                    run_methods.append(method_name)
            
            if not run_methods:
                result['errors'].append("No runnable methods found in exercise class")
                return result
            
            for method_name in run_methods:
                if verbose:
                    print(f"    Running method: {method_name}")
                
                method = getattr(exercise_instance, method_name)
                
                try:
                    if asyncio.iscoroutinefunction(method):
                        method_result = await method()
                    else:
                        method_result = method()
                    
                    if isinstance(method_result, dict):
                        result['score'] += method_result.get('score', 0)
                        result['feedback'].extend(method_result.get('feedback', []))
                    else:
                        result['score'] += 1 if method_result else 0
                        result['feedback'].append(f"✅ {method_name}: PASSED" if method_result else f"❌ {method_name}: FAILED")
                
                except Exception as e:
                    result['errors'].append(f"Method {method_name} failed: {str(e)}")
                    result['feedback'].append(f"❌ {method_name}: ERROR - {str(e)}")
            
            result['max_score'] = len(run_methods)
            
        except Exception as e:
            result['errors'].append(f"Class exercise execution failed: {str(e)}")
        
        return result
    
    async def run_module_tests(self, module_id: str, verbose: bool = False) -> List[ExerciseResult]:
        """Run all tests for a specific module."""
        if module_id not in self.module_exercises:
            colors.print_error(f"Module '{module_id}' not found")
            return []
        
        module = self.module_exercises[module_id]
        exercises = module['exercises']
        
        colors.print_header(f"🧪 Running All Tests for {module['name']}")
        
        results = []
        
        # Create progress bar for module tests
        progress = progress_bar.ProgressBar(
            total=len(exercises),
            prefix=f"Testing {module['name']}",
            show_count=True,
            show_percentage=True
        )
        
        for exercise in exercises:
            try:
                if verbose:
                    colors.print_info(f"Running exercise: {exercise}")
                
                result = await self.run_exercise(module_id, exercise, verbose)
                result.module_id = module_id  # Ensure module_id is set
                results.append(result)
                
                progress.update()
                
            except Exception as e:
                logger.error(f"Failed to run exercise {exercise}: {e}")
                error_result = ExerciseResult(
                    exercise_name=exercise,
                    module_id=module_id,
                    passed=False,
                    score=0,
                    max_score=100,
                    execution_time=0,
                    feedback=[f"Failed to run: {str(e)}"],
                    errors=[str(e)]
                )
                results.append(error_result)
                progress.update()
        
        progress.close()
        
        # Show summary
        self._show_module_test_summary(module_id, results)
        
        return results
    
    def _show_exercise_result(self, result: ExerciseResult) -> None:
        """Display the result of a single exercise."""
        exercise_name = result.exercise_name.replace('_', ' ').title()
        
        # Header with pass/fail status
        if result.passed:
            colors.print_success(f"Exercise '{exercise_name}' PASSED")
        else:
            colors.print_error(f"Exercise '{exercise_name}' FAILED")
        
        # Score and timing info
        print(f"\n{colors.BOLD}Results:{colors.RESET}")
        print(f"Score: {colors.get_progress_color(result.percentage)}{result.score:.1f}/{result.max_score} ({result.percentage:.1f}%){colors.RESET}")
        print(f"Execution Time: {colors.BLUE}{result.execution_time:.2f}s{colors.RESET}")
        
        # Feedback
        if result.feedback:
            print(f"\n{colors.BOLD}Feedback:{colors.RESET}")
            for feedback in result.feedback:
                print(f"  {feedback}")
        
        # Errors
        if result.errors:
            print(f"\n{colors.BOLD}Errors:{colors.RESET}")
            for error in result.errors:
                print(f"  {colors.RED}{error}{colors.RESET}")
        
        print()
    
    def _show_module_test_summary(self, module_id: str, results: List[ExerciseResult]) -> None:
        """Show summary of module test results."""
        module = self.module_exercises[module_id]
        
        colors.print_header(f"📊 Test Summary for {module['name']}")
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        total_score = sum(r.score for r in results)
        max_total_score = sum(r.max_score for r in results)
        avg_time = sum(r.execution_time for r in results) / len(results) if results else 0
        
        overall_percentage = (total_score / max_total_score * 100) if max_total_score > 0 else 0
        
        print(f"Tests Passed: {colors.GREEN}{passed_tests}{colors.RESET}/{total_tests}")
        print(f"Overall Score: {colors.get_progress_color(overall_percentage)}{total_score}/{max_total_score} ({overall_percentage:.1f}%){colors.RESET}")
        print(f"Average Time: {colors.BLUE}{avg_time:.2f}s{colors.RESET}")
        
        # Progress bar for overall performance
        progress_bar.show_progress(
            passed_tests,
            total_tests,
            "Tests Passed",
            50
        )
        
        # Individual test results
        print(f"\n{colors.BOLD}Individual Results:{colors.RESET}")
        for result in results:
            status = f"{colors.GREEN}✅{colors.RESET}" if result.passed else f"{colors.RED}❌{colors.RESET}"
            exercise_name = result.exercise_name.replace('_', ' ').title()
            score_color = colors.get_progress_color(result.percentage)
            
            print(f"  {status} {exercise_name:<30} {score_color}{result.score:.1f}/{result.max_score} ({result.percentage:.1f}%){colors.RESET} - {result.execution_time:.2f}s")
        
        print()
        
        # Recommendations
        if passed_tests == total_tests:
            colors.print_success(f"🎉 Excellent! All tests passed for {module['name']}!")
            if overall_percentage == 100:
                colors.print_info("Perfect score! You've mastered this module!")
        elif passed_tests > total_tests // 2:
            colors.print_warning(f"Good progress! {total_tests - passed_tests} tests still need work.")
        else:
            colors.print_info(f"Keep practicing! Focus on the failed exercises to improve.")
    
    def _show_achievements(self, achievements: List) -> None:
        """Show newly unlocked achievements."""
        if not achievements:
            return
        
        colors.print_header("🏆 New Achievements Unlocked!")
        
        for achievement in achievements:
            badge = achievement.badge if hasattr(achievement, 'badge') else '🏅'
            name = achievement.name if hasattr(achievement, 'name') else 'Achievement'
            description = achievement.description if hasattr(achievement, 'description') else ''
            
            print(f"  {badge} {colors.BOLD}{name}{colors.RESET}")
            print(f"    {description}")
        
        print()


async def execute(args: argparse.Namespace) -> int:
    """Execute the test command."""
    runner = TestRunner()
    
    try:
        # List available tests
        if hasattr(args, 'list_tests') and args.list_tests:
            module_id = getattr(args, 'module', None)
            runner.list_available_tests(module_id)
            return 0
        
        # Run specific exercise
        if hasattr(args, 'module') and hasattr(args, 'exercise') and args.module and args.exercise:
            verbose = getattr(args, 'verbose', False)
            result = await runner.run_exercise(args.module, args.exercise, verbose)
            runner._show_exercise_result(result)
            return 0 if result.passed else 1
        
        # Run all tests for a module
        if hasattr(args, 'module') and args.module:
            verbose = getattr(args, 'verbose', False)
            results = await runner.run_module_tests(args.module, verbose)
            
            # Return success if more than half the tests passed
            passed_count = sum(1 for r in results if r.passed)
            return 0 if passed_count > len(results) // 2 else 1
        
        # Default: show available tests
        runner.list_available_tests()
        return 0
    
    except Exception as e:
        logger.error(f"Test command failed: {e}")
        colors.print_error(f"Test execution failed: {e}")
        return 1


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Setup the test command parser."""
    parser.add_argument(
        'module',
        nargs='?',
        help='Module to test (basics, oop, advanced, etc.)'
    )
    
    parser.add_argument(
        'exercise',
        nargs='?',
        help='Specific exercise to run'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        dest='list_tests',
        help='List available tests'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run all tests for the specified module'
    )