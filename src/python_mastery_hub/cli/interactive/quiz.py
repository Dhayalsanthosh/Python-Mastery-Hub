"""
Interactive Quiz System

Provides interactive quizzes for testing Python knowledge with
multiple choice questions, code challenges, and progress tracking.
"""

import argparse
import asyncio
import random
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass

from python_mastery_hub.cli.utils import colors, progress_bar
from python_mastery_hub.utils.progress_calculator import ProgressCalculator
from python_mastery_hub.utils.achievement_engine import AchievementEngine
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class QuizQuestion:
    """Represents a single quiz question."""
    id: str
    question: str
    question_type: str  # 'multiple_choice', 'true_false', 'code', 'fill_blank'
    options: List[str] = None
    correct_answer: Union[str, int] = None
    explanation: str = ""
    difficulty: str = "intermediate"
    topic: str = ""
    points: int = 1


@dataclass
class QuizResult:
    """Quiz completion result."""
    total_questions: int
    correct_answers: int
    score_percentage: float
    time_taken: float
    difficulty: str
    topic: str


class QuizEngine:
    """Interactive quiz engine and manager."""
    
    def __init__(self):
        self.progress_calc = ProgressCalculator()
        self.achievement_engine = AchievementEngine()
        self.questions = self._load_questions()
        self.current_quiz = []
        self.quiz_start_time = None
    
    def _load_questions(self) -> Dict[str, List[QuizQuestion]]:
        """Load quiz questions by module and topic."""
        return {
            'basics': self._get_basics_questions(),
            'oop': self._get_oop_questions(),
            'advanced': self._get_advanced_questions(),
            'data_structures': self._get_data_structures_questions(),
            'algorithms': self._get_algorithms_questions(),
            'async_programming': self._get_async_questions(),
            'web_development': self._get_web_questions(),
            'data_science': self._get_data_science_questions(),
            'testing': self._get_testing_questions()
        }
    
    def _get_basics_questions(self) -> List[QuizQuestion]:
        """Get basic Python quiz questions."""
        return [
            QuizQuestion(
                id="var_assignment",
                question="Which of the following is the correct way to assign a value to a variable in Python?",
                question_type="multiple_choice",
                options=[
                    "variable = value",
                    "value -> variable", 
                    "variable := value",
                    "set variable = value"
                ],
                correct_answer=0,
                explanation="In Python, we use the = operator for assignment: variable = value",
                difficulty="beginner",
                topic="variables"
            ),
            QuizQuestion(
                id="data_types",
                question="What data type is the result of: type(3.14)?",
                question_type="multiple_choice",
                options=[
                    "int",
                    "float",
                    "str", 
                    "type"
                ],
                correct_answer=3,
                explanation="The type() function returns a type object, so type(3.14) returns <class 'float'>",
                difficulty="beginner",
                topic="data_types"
            ),
            QuizQuestion(
                id="string_methods",
                question="True or False: String methods in Python modify the original string.",
                question_type="true_false",
                correct_answer="False",
                explanation="Strings are immutable in Python. String methods return new strings rather than modifying the original.",
                difficulty="intermediate",
                topic="strings"
            ),
            QuizQuestion(
                id="list_indexing",
                question="What will be the output of: [1, 2, 3, 4, 5][-2]",
                question_type="multiple_choice",
                options=[
                    "2",
                    "3",
                    "4",
                    "IndexError"
                ],
                correct_answer=2,
                explanation="Negative indexing starts from the end. -2 refers to the second-to-last element, which is 4.",
                difficulty="intermediate",
                topic="lists"
            ),
            QuizQuestion(
                id="for_loop_range",
                question="Complete the code: for i in _____(5): print(i)  # prints 0,1,2,3,4",
                question_type="fill_blank",
                correct_answer="range",
                explanation="The range() function generates a sequence of numbers from 0 to n-1.",
                difficulty="beginner",
                topic="loops"
            )
        ]
    
    def _get_oop_questions(self) -> List[QuizQuestion]:
        """Get OOP quiz questions."""
        return [
            QuizQuestion(
                id="class_definition",
                question="Which keyword is used to define a class in Python?",
                question_type="multiple_choice",
                options=[
                    "def",
                    "class",
                    "object",
                    "struct"
                ],
                correct_answer=1,
                explanation="The 'class' keyword is used to define a class in Python.",
                difficulty="beginner",
                topic="classes"
            ),
            QuizQuestion(
                id="inheritance",
                question="True or False: Python supports multiple inheritance.",
                question_type="true_false",
                correct_answer="True",
                explanation="Python supports multiple inheritance, allowing a class to inherit from multiple parent classes.",
                difficulty="intermediate",
                topic="inheritance"
            ),
            QuizQuestion(
                id="method_types",
                question="What decorator is used to create a class method?",
                question_type="multiple_choice",
                options=[
                    "@staticmethod",
                    "@classmethod",
                    "@property",
                    "@method"
                ],
                correct_answer=1,
                explanation="@classmethod decorator is used to create class methods that receive the class as the first argument.",
                difficulty="intermediate",
                topic="methods"
            )
        ]
    
    def _get_advanced_questions(self) -> List[QuizQuestion]:
        """Get advanced Python quiz questions."""
        return [
            QuizQuestion(
                id="decorators",
                question="What is the primary purpose of decorators in Python?",
                question_type="multiple_choice",
                options=[
                    "To make code look prettier",
                    "To modify or extend function behavior",
                    "To create new data types",
                    "To handle exceptions"
                ],
                correct_answer=1,
                explanation="Decorators are used to modify or extend the behavior of functions or classes without permanently modifying them.",
                difficulty="advanced",
                topic="decorators"
            ),
            QuizQuestion(
                id="generators",
                question="Which keyword is used to create a generator function?",
                question_type="multiple_choice",
                options=[
                    "return",
                    "yield",
                    "generate",
                    "next"
                ],
                correct_answer=1,
                explanation="The 'yield' keyword is used to create generator functions that can pause and resume execution.",
                difficulty="advanced",
                topic="generators"
            )
        ]
    
    def _get_data_structures_questions(self) -> List[QuizQuestion]:
        """Get data structures quiz questions."""
        return []
    
    def _get_algorithms_questions(self) -> List[QuizQuestion]:
        """Get algorithms quiz questions."""
        return []
    
    def _get_async_questions(self) -> List[QuizQuestion]:
        """Get async programming quiz questions."""
        return []
    
    def _get_web_questions(self) -> List[QuizQuestion]:
        """Get web development quiz questions."""
        return []
    
    def _get_data_science_questions(self) -> List[QuizQuestion]:
        """Get data science quiz questions."""
        return []
    
    def _get_testing_questions(self) -> List[QuizQuestion]:
        """Get testing quiz questions."""
        return []
    
    async def show_quiz_menu(self) -> None:
        """Show the main quiz selection menu."""
        colors.print_header("Interactive Python Quizzes")
        
        print(f"{colors.BOLD}Quiz Options:{colors.RESET}")
        print("  1. Quick Quiz (5 random questions)")
        print("  2. Module-specific Quiz")
        print("  3. Difficulty-based Quiz")
        print("  4. Topic Review Quiz")
        print("  5. Challenge Quiz (advanced)")
        print("  0. Exit")
        
        while True:
            try:
                choice = input(f"\n{colors.CYAN}Select quiz type (0-5): {colors.RESET}")
                choice = int(choice)
                
                if choice == 0:
                    break
                elif choice == 1:
                    await self.quick_quiz()
                elif choice == 2:
                    await self.module_quiz()
                elif choice == 3:
                    await self.difficulty_quiz()
                elif choice == 4:
                    await self.topic_quiz()
                elif choice == 5:
                    await self.challenge_quiz()
                else:
                    colors.print_error("Invalid choice. Please try again.")
                    
            except (ValueError, KeyboardInterrupt):
                break
    
    async def quick_quiz(self) -> None:
        """Run a quick 5-question quiz."""
        colors.print_header("Quick Quiz - 5 Random Questions")
        
        # Get random questions from all modules
        all_questions = []
        for module_questions in self.questions.values():
            all_questions.extend(module_questions)
        
        if len(all_questions) < 5:
            colors.print_error("Not enough questions available")
            return
        
        quiz_questions = random.sample(all_questions, 5)
        await self.run_quiz(quiz_questions, "Mixed Topics", "mixed")
    
    async def module_quiz(self) -> None:
        """Run a quiz for a specific module."""
        colors.print_header("Module-specific Quiz")
        
        print(f"{colors.BOLD}Available Modules:{colors.RESET}")
        modules = list(self.questions.keys())
        
        for i, module in enumerate(modules, 1):
            module_name = module.replace('_', ' ').title()
            question_count = len(self.questions[module])
            print(f"  {i}. {module_name} ({question_count} questions)")
        
        print("  0. Back to main menu")
        
        try:
            choice = input(f"\n{colors.CYAN}Select module (0-{len(modules)}): {colors.RESET}")
            choice = int(choice)
            
            if choice == 0:
                return
            elif 1 <= choice <= len(modules):
                module = modules[choice - 1]
                module_questions = self.questions[module]
                
                if not module_questions:
                    colors.print_warning(f"No questions available for {module}")
                    return
                
                module_name = module.replace('_', ' ').title()
                await self.run_quiz(module_questions, module_name, module)
            else:
                colors.print_error("Invalid choice")
                
        except (ValueError, KeyboardInterrupt):
            pass
    
    async def difficulty_quiz(self) -> None:
        """Run a quiz filtered by difficulty."""
        colors.print_header("Difficulty-based Quiz")
        
        difficulties = ["beginner", "intermediate", "advanced"]
        
        print(f"{colors.BOLD}Select Difficulty:{colors.RESET}")
        for i, difficulty in enumerate(difficulties, 1):
            print(f"  {i}. {difficulty.title()}")
        print("  0. Back to main menu")
        
        try:
            choice = input(f"\n{colors.CYAN}Select difficulty (0-{len(difficulties)}): {colors.RESET}")
            choice = int(choice)
            
            if choice == 0:
                return
            elif 1 <= choice <= len(difficulties):
                difficulty = difficulties[choice - 1]
                
                # Filter questions by difficulty
                filtered_questions = []
                for module_questions in self.questions.values():
                    for question in module_questions:
                        if question.difficulty == difficulty:
                            filtered_questions.append(question)
                
                if not filtered_questions:
                    colors.print_warning(f"No {difficulty} questions available")
                    return
                
                # Take up to 10 questions
                quiz_questions = random.sample(filtered_questions, min(10, len(filtered_questions)))
                await self.run_quiz(quiz_questions, f"{difficulty.title()} Quiz", difficulty)
            else:
                colors.print_error("Invalid choice")
                
        except (ValueError, KeyboardInterrupt):
            pass
    
    async def topic_quiz(self) -> None:
        """Run a quiz on a specific topic."""
        colors.print_header("Topic Review Quiz")
        
        # Get all unique topics
        topics = set()
        for module_questions in self.questions.values():
            for question in module_questions:
                if question.topic:
                    topics.add(question.topic)
        
        topic_list = sorted(list(topics))
        
        if not topic_list:
            colors.print_warning("No topic-specific questions available")
            return
        
        print(f"{colors.BOLD}Available Topics:{colors.RESET}")
        for i, topic in enumerate(topic_list, 1):
            print(f"  {i}. {topic.replace('_', ' ').title()}")
        print("  0. Back to main menu")
        
        try:
            choice = input(f"\n{colors.CYAN}Select topic (0-{len(topic_list)}): {colors.RESET}")
            choice = int(choice)
            
            if choice == 0:
                return
            elif 1 <= choice <= len(topic_list):
                topic = topic_list[choice - 1]
                
                # Filter questions by topic
                topic_questions = []
                for module_questions in self.questions.values():
                    for question in module_questions:
                        if question.topic == topic:
                            topic_questions.append(question)
                
                if not topic_questions:
                    colors.print_warning(f"No questions available for {topic}")
                    return
                
                topic_name = topic.replace('_', ' ').title()
                await self.run_quiz(topic_questions, f"{topic_name} Review", topic)
            else:
                colors.print_error("Invalid choice")
                
        except (ValueError, KeyboardInterrupt):
            pass
    
    async def challenge_quiz(self) -> None:
        """Run a challenging quiz with advanced questions."""
        colors.print_header("Challenge Quiz - Advanced Level")
        
        # Get only advanced questions
        advanced_questions = []
        for module_questions in self.questions.values():
            for question in module_questions:
                if question.difficulty == "advanced":
                    advanced_questions.append(question)
        
        if len(advanced_questions) < 3:
            colors.print_warning("Not enough advanced questions available")
            return
        
        print(f"{colors.YELLOW}Warning: This quiz contains advanced Python concepts!{colors.RESET}")
        confirm = input(f"{colors.CYAN}Are you ready for the challenge? (y/n): {colors.RESET}")
        
        if confirm.lower() != 'y':
            return
        
        # Take up to 10 advanced questions
        quiz_questions = random.sample(advanced_questions, min(10, len(advanced_questions)))
        await self.run_quiz(quiz_questions, "Challenge Quiz", "advanced")
    
    async def run_quiz(self, questions: List[QuizQuestion], quiz_name: str, category: str) -> None:
        """Run a quiz with the given questions."""
        self.current_quiz = questions
        self.quiz_start_time = time.time()
        
        colors.print_header(f"Starting: {quiz_name}")
        
        print(f"Total Questions: {len(questions)}")
        print(f"Category: {category}")
        print(f"\nInstructions:")
        print("- Answer each question carefully")
        print("- Type the number of your choice for multiple choice")
        print("- Type 'True' or 'False' for true/false questions")
        print("- Type your answer for fill-in-the-blank questions")
        print("- You can type 'skip' to skip a question")
        
        input(f"\n{colors.GREEN}Press Enter to start the quiz...{colors.RESET}")
        
        correct_answers = 0
        total_points = 0
        max_points = sum(q.points for q in questions)
        
        for i, question in enumerate(questions, 1):
            print(f"\n{colors.BOLD}Question {i}/{len(questions)}{colors.RESET}")
            
            # Show progress bar
            progress_bar.show_progress(i-1, len(questions), "Progress", 30)
            
            answer_correct = await self.ask_question(question)
            if answer_correct:
                correct_answers += 1
                total_points += question.points
        
        # Calculate results
        quiz_time = time.time() - self.quiz_start_time
        score_percentage = (total_points / max_points * 100) if max_points > 0 else 0
        
        result = QuizResult(
            total_questions=len(questions),
            correct_answers=correct_answers,
            score_percentage=score_percentage,
            time_taken=quiz_time,
            difficulty=category,
            topic=quiz_name
        )
        
        await self.show_quiz_results(result)
        
        # Update progress
        if score_percentage >= 70:  # Passing grade
            self.progress_calc.mark_topic_completed(
                category,
                f"quiz_{quiz_name.lower().replace(' ', '_')}",
                score=score_percentage / 100,
                time_spent=int(quiz_time / 60)
            )
    
    async def ask_question(self, question: QuizQuestion) -> bool:
        """Ask a single question and get user response."""
        print(f"\n{colors.BLUE}{question.question}{colors.RESET}")
        
        if question.question_type == "multiple_choice":
            return await self._handle_multiple_choice(question)
        elif question.question_type == "true_false":
            return await self._handle_true_false(question)
        elif question.question_type == "fill_blank":
            return await self._handle_fill_blank(question)
        else:
            colors.print_error(f"Unknown question type: {question.question_type}")
            return False
    
    async def _handle_multiple_choice(self, question: QuizQuestion) -> bool:
        """Handle multiple choice questions."""
        for i, option in enumerate(question.options):
            print(f"  {i + 1}. {option}")
        
        while True:
            try:
                answer = input(f"\n{colors.CYAN}Your answer (1-{len(question.options)}) or 'skip': {colors.RESET}")
                
                if answer.lower() == 'skip':
                    colors.print_warning("Question skipped")
                    return False
                
                answer_index = int(answer) - 1
                
                if 0 <= answer_index < len(question.options):
                    correct = answer_index == question.correct_answer
                    self._show_answer_feedback(correct, question)
                    return correct
                else:
                    colors.print_error("Invalid choice. Please try again.")
                    
            except (ValueError, KeyboardInterrupt):
                colors.print_error("Invalid input. Please enter a number.")
    
    async def _handle_true_false(self, question: QuizQuestion) -> bool:
        """Handle true/false questions."""
        while True:
            answer = input(f"\n{colors.CYAN}Your answer (True/False) or 'skip': {colors.RESET}")
            
            if answer.lower() == 'skip':
                colors.print_warning("Question skipped")
                return False
            
            if answer.lower() in ['true', 't', '1']:
                user_answer = "True"
            elif answer.lower() in ['false', 'f', '0']:
                user_answer = "False"
            else:
                colors.print_error("Please enter 'True' or 'False'")
                continue
            
            correct = user_answer == question.correct_answer
            self._show_answer_feedback(correct, question)
            return correct
    
    async def _handle_fill_blank(self, question: QuizQuestion) -> bool:
        """Handle fill-in-the-blank questions."""
        answer = input(f"\n{colors.CYAN}Your answer or 'skip': {colors.RESET}")
        
        if answer.lower() == 'skip':
            colors.print_warning("Question skipped")
            return False
        
        correct = answer.lower().strip() == question.correct_answer.lower().strip()
        self._show_answer_feedback(correct, question)
        return correct
    
    def _show_answer_feedback(self, correct: bool, question: QuizQuestion) -> None:
        """Show feedback for the user's answer."""
        if correct:
            colors.print_success("Correct!")
        else:
            colors.print_error("Incorrect")
            
            # Show correct answer
            if question.question_type == "multiple_choice":
                correct_option = question.options[question.correct_answer]
                print(f"{colors.YELLOW}Correct answer: {question.correct_answer + 1}. {correct_option}{colors.RESET}")
            else:
                print(f"{colors.YELLOW}Correct answer: {question.correct_answer}{colors.RESET}")
        
        # Show explanation if available
        if question.explanation:
            print(f"{colors.GRAY}Explanation: {question.explanation}{colors.RESET}")
    
    async def show_quiz_results(self, result: QuizResult) -> None:
        """Display quiz completion results."""
        colors.print_header("Quiz Results")
        
        # Determine grade
        if result.score_percentage >= 90:
            grade = "A"
            grade_color = colors.GREEN
            message = "Excellent work!"
        elif result.score_percentage >= 80:
            grade = "B"
            grade_color = colors.LIGHT_GREEN
            message = "Great job!"
        elif result.score_percentage >= 70:
            grade = "C"
            grade_color = colors.YELLOW
            message = "Good effort!"
        elif result.score_percentage >= 60:
            grade = "D"
            grade_color = colors.YELLOW
            message = "Keep practicing!"
        else:
            grade = "F"
            grade_color = colors.RED
            message = "Review the material and try again!"
        
        print(f"{colors.BOLD}Quiz: {result.topic}{colors.RESET}")
        print(f"Questions Answered: {result.correct_answers}/{result.total_questions}")
        print(f"Score: {grade_color}{result.score_percentage:.1f}%{colors.RESET}")
        print(f"Grade: {grade_color}{grade}{colors.RESET}")
        print(f"Time Taken: {result.time_taken:.1f} seconds")
        print(f"\n{grade_color}{message}{colors.RESET}")
        
        # Show progress bar
        progress_bar.show_progress(
            result.correct_answers,
            result.total_questions,
            "Correct Answers",
            40
        )
        
        # Check for achievements
        if result.score_percentage == 100:
            colors.print_success("Perfect Score! You've mastered this topic!")
        elif result.score_percentage >= 90:
            colors.print_success("Outstanding performance!")
        
        input(f"\n{colors.GRAY}Press Enter to continue...{colors.RESET}")


async def execute(args: argparse.Namespace) -> int:
    """Execute the interactive quiz command."""
    try:
        engine = QuizEngine()
        await engine.show_quiz_menu()
        return 0
    
    except Exception as e:
        logger.error(f"Interactive quiz failed: {e}")
        colors.print_error(f"Failed to run quiz: {e}")
        return 1


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Setup the quiz command parser."""
    parser.add_argument(
        '--module', '-m',
        help='Run quiz for specific module'
    )
    
    parser.add_argument(
        '--difficulty', '-d',
        choices=['beginner', 'intermediate', 'advanced'],
        help='Filter questions by difficulty'
    )
    
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=10,
        help='Number of questions (default: 10)'
    )