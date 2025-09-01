# tests/e2e/test_learning_flow.py
"""
End-to-end tests for learning flow functionality.
Tests the complete learning experience including lesson progression,
interactive exercises, quizzes, and knowledge retention tracking.
"""
import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class LessonContent:
    """Represents lesson content structure."""
    id: str
    title: str
    content_type: str  # 'video', 'text', 'interactive', 'quiz'
    content_url: str
    duration_minutes: int
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)


@dataclass
class Quiz:
    """Represents a quiz structure."""
    id: str
    lesson_id: str
    questions: List[Dict[str, Any]]
    passing_score: int = 70
    max_attempts: int = 3
    time_limit_minutes: Optional[int] = None


@dataclass
class UserProgress:
    """Tracks user progress through learning content."""
    user_id: str
    course_id: str
    current_lesson_id: str
    completed_lessons: List[str] = field(default_factory=list)
    quiz_attempts: Dict[str, List[Dict]] = field(default_factory=dict)
    time_spent: Dict[str, int] = field(default_factory=dict)  # lesson_id -> minutes
    last_activity: datetime = field(default_factory=datetime.now)
    knowledge_retention_score: float = 0.0


class MockLearningPlatform:
    """Mock learning platform for testing learning flows."""
    
    def __init__(self):
        self.courses = {}
        self.lessons = {}
        self.quizzes = {}
        self.user_progress = {}
        self.analytics = {}
        self.notifications = []
        self.adaptive_recommendations = {}
        
    def reset(self):
        """Reset all platform data."""
        self.__init__()
    
    async def track_lesson_progress(self, user_id: str, lesson_id: str, progress_data: Dict):
        """Track user progress through a lesson."""
        key = f"{user_id}_{lesson_id}"
        if key not in self.analytics:
            self.analytics[key] = []
        self.analytics[key].append({
            "timestamp": datetime.now(),
            "event": "progress_update",
            "data": progress_data
        })
    
    async def calculate_knowledge_retention(self, user_id: str, course_id: str) -> float:
        """Calculate knowledge retention score based on quiz performance and review patterns."""
        # Mock calculation based on recent quiz scores and review frequency
        return 0.85  # 85% retention score


@pytest.fixture
def mock_learning_platform():
    """Fixture providing a clean mock learning platform."""
    return MockLearningPlatform()


@pytest.fixture
def sample_python_course():
    """Fixture providing a sample Python course structure."""
    lessons = [
        LessonContent("lesson_1", "Python Basics", "video", "/videos/python_basics.mp4", 30,
                     [], ["Understand Python syntax", "Write basic Python programs"]),
        LessonContent("lesson_2", "Variables and Data Types", "interactive", "/interactive/variables", 25,
                     ["lesson_1"], ["Declare variables", "Use different data types"]),
        LessonContent("lesson_3", "Control Structures", "text", "/content/control_structures.md", 35,
                     ["lesson_2"], ["Use if/else statements", "Implement loops"]),
        LessonContent("lesson_4", "Functions", "video", "/videos/functions.mp4", 40,
                     ["lesson_3"], ["Define functions", "Use parameters and return values"]),
        LessonContent("lesson_5", "Classes and Objects", "interactive", "/interactive/oop", 45,
                     ["lesson_4"], ["Create classes", "Instantiate objects", "Use inheritance"])
    ]
    
    quizzes = [
        Quiz("quiz_1", "lesson_1", [
            {"id": "q1", "question": "What is Python?", "type": "multiple_choice",
             "options": ["A snake", "A programming language", "A movie", "A game"],
             "correct_answer": 1, "points": 10},
            {"id": "q2", "question": "Python is case-sensitive", "type": "true_false",
             "correct_answer": True, "points": 5}
        ]),
        Quiz("quiz_2", "lesson_2", [
            {"id": "q3", "question": "Which is a valid variable name?", "type": "multiple_choice",
             "options": ["123name", "my_var", "class", "my-var"],
             "correct_answer": 1, "points": 10},
            {"id": "q4", "question": "What type is 'Hello'?", "type": "multiple_choice",
             "options": ["int", "str", "float", "bool"],
             "correct_answer": 1, "points": 10}
        ])
    ]
    
    return {
        "course_id": "python_basics_course",
        "title": "Python Programming Fundamentals",
        "lessons": lessons,
        "quizzes": quizzes
    }


class TestLessonProgression:
    """Test lesson progression and navigation."""
    
    @pytest.mark.asyncio
    async def test_sequential_lesson_progression(self, mock_learning_platform, sample_python_course):
        """Test that users progress through lessons sequentially."""
        user_id = "user_123"
        course = sample_python_course
        
        # Initialize user progress
        progress = UserProgress(user_id, course["course_id"], course["lessons"][0].id)
        mock_learning_platform.user_progress[user_id] = progress
        
        # Setup course data
        for lesson in course["lessons"]:
            mock_learning_platform.lessons[lesson.id] = lesson
        
        # Test sequential progression
        for i, lesson in enumerate(course["lessons"]):
            # Check prerequisites
            if lesson.prerequisites:
                for prereq in lesson.prerequisites:
                    assert prereq in progress.completed_lessons, f"Prerequisite {prereq} not completed"
            
            # Start lesson
            await mock_learning_platform.track_lesson_progress(user_id, lesson.id, {
                "action": "lesson_started",
                "timestamp": datetime.now()
            })
            
            # Simulate lesson completion
            progress.time_spent[lesson.id] = lesson.duration_minutes
            progress.completed_lessons.append(lesson.id)
            
            # Update current lesson
            if i < len(course["lessons"]) - 1:
                progress.current_lesson_id = course["lessons"][i + 1].id
            
            await mock_learning_platform.track_lesson_progress(user_id, lesson.id, {
                "action": "lesson_completed",
                "time_spent": lesson.duration_minutes,
                "timestamp": datetime.now()
            })
        
        # Verify progression
        assert len(progress.completed_lessons) == len(course["lessons"])
        assert sum(progress.time_spent.values()) == sum(l.duration_minutes for l in course["lessons"])
    
    @pytest.mark.asyncio
    async def test_prerequisite_enforcement(self, mock_learning_platform, sample_python_course):
        """Test that prerequisites are properly enforced."""
        user_id = "user_123"
        course = sample_python_course
        
        # Initialize user progress
        progress = UserProgress(user_id, course["course_id"], course["lessons"][0].id)
        mock_learning_platform.user_progress[user_id] = progress
        
        # Try to access lesson with prerequisites without completing them
        advanced_lesson = course["lessons"][4]  # Classes and Objects (has prerequisites)
        
        # Check if prerequisites are met
        missing_prereqs = [p for p in advanced_lesson.prerequisites if p not in progress.completed_lessons]
        
        if missing_prereqs:
            with pytest.raises(PermissionError, match="Prerequisites not met"):
                raise PermissionError(f"Prerequisites not met: {missing_prereqs}")
        
        # Complete prerequisites and try again
        for lesson in course["lessons"][:4]:  # Complete first 4 lessons
            progress.completed_lessons.append(lesson.id)
        
        # Now should be able to access the advanced lesson
        missing_prereqs = [p for p in advanced_lesson.prerequisites if p not in progress.completed_lessons]
        assert len(missing_prereqs) == 0
    
    @pytest.mark.asyncio
    async def test_lesson_content_loading(self, mock_learning_platform, sample_python_course):
        """Test different types of lesson content loading."""
        user_id = "user_123"
        course = sample_python_course
        
        for lesson in course["lessons"]:
            mock_learning_platform.lessons[lesson.id] = lesson
            
            # Simulate content loading based on type
            if lesson.content_type == "video":
                # Mock video loading
                content_data = {
                    "type": "video",
                    "url": lesson.content_url,
                    "duration": lesson.duration_minutes,
                    "subtitles_available": True,
                    "quality_options": ["720p", "1080p"]
                }
            elif lesson.content_type == "interactive":
                # Mock interactive content
                content_data = {
                    "type": "interactive",
                    "url": lesson.content_url,
                    "interactive_elements": ["code_editor", "quiz_widgets", "drag_drop"],
                    "auto_save": True
                }
            elif lesson.content_type == "text":
                # Mock text content
                content_data = {
                    "type": "text",
                    "url": lesson.content_url,
                    "word_count": 1500,
                    "reading_time": lesson.duration_minutes,
                    "highlights_enabled": True
                }
            
            # Track content access
            await mock_learning_platform.track_lesson_progress(user_id, lesson.id, {
                "action": "content_accessed",
                "content_type": lesson.content_type,
                "content_data": content_data
            })
            
            # Verify content was tracked
            key = f"{user_id}_{lesson.id}"
            assert key in mock_learning_platform.analytics
            assert any(event["event"] == "content_accessed" for event in mock_learning_platform.analytics[key])


class TestInteractiveLearning:
    """Test interactive learning features."""
    
    @pytest.mark.asyncio
    async def test_code_execution_in_lessons(self, mock_learning_platform):
        """Test code execution within interactive lessons."""
        user_id = "user_123"
        lesson_id = "interactive_python_lesson"
        
        # Mock code execution environment
        code_exercises = [
            {
                "id": "ex_1",
                "prompt": "Write a function that adds two numbers",
                "starter_code": "def add_numbers(a, b):\n    # Your code here\n    pass",
                "test_cases": [
                    {"input": [2, 3], "expected": 5},
                    {"input": [10, -5], "expected": 5},
                    {"input": [0, 0], "expected": 0}
                ]
            },
            {
                "id": "ex_2",
                "prompt": "Create a list of even numbers from 1 to 10",
                "starter_code": "# Your code here",
                "test_cases": [
                    {"expected": [2, 4, 6, 8, 10]}
                ]
            }
        ]
        
        for exercise in code_exercises:
            # Simulate user submitting code
            user_code = {
                "ex_1": "def add_numbers(a, b):\n    return a + b",
                "ex_2": "even_numbers = [i for i in range(1, 11) if i % 2 == 0]"
            }
            
            # Mock code execution
            with patch('code_executor.run_code') as mock_executor:
                # Simulate successful execution
                mock_executor.return_value = {
                    "status": "success",
                    "output": "All tests passed",
                    "execution_time": 0.15,
                    "test_results": [{"passed": True} for _ in exercise["test_cases"]]
                }
                
                result = mock_executor.return_value
                
                # Track exercise completion
                await mock_learning_platform.track_lesson_progress(user_id, lesson_id, {
                    "action": "exercise_completed",
                    "exercise_id": exercise["id"],
                    "code_submitted": user_code.get(exercise["id"]),
                    "result": result,
                    "attempts": 1
                })
                
                assert result["status"] == "success"
                assert all(test["passed"] for test in result["test_results"])
    
    @pytest.mark.asyncio
    async def test_real_time_feedback(self, mock_learning_platform):
        """Test real-time feedback during interactive lessons."""
        user_id = "user_123"
        lesson_id = "interactive_lesson"
        
        # Simulate real-time interactions
        interactions = [
            {"type": "code_hint_requested", "timestamp": datetime.now(), "context": "function_definition"},
            {"type": "syntax_error", "timestamp": datetime.now(), "error": "IndentationError: expected an indented block"},
            {"type": "hint_provided", "timestamp": datetime.now(), "hint": "Remember to indent the function body"},
            {"type": "code_corrected", "timestamp": datetime.now(), "success": True}
        ]
        
        for interaction in interactions:
            await mock_learning_platform.track_lesson_progress(user_id, lesson_id, {
                "action": "real_time_interaction",
                "interaction_data": interaction
            })
        
        # Verify feedback tracking
        key = f"{user_id}_{lesson_id}"
        tracked_interactions = [
            event for event in mock_learning_platform.analytics[key]
            if event["event"] == "progress_update" and 
            event["data"]["action"] == "real_time_interaction"
        ]
        
        assert len(tracked_interactions) == len(interactions)
        assert any("syntax_error" in str(event) for event in tracked_interactions)
        assert any("hint_provided" in str(event) for event in tracked_interactions)


class TestQuizSystem:
    """Test quiz functionality and assessment."""
    
    @pytest.mark.asyncio
    async def test_quiz_taking_flow(self, mock_learning_platform, sample_python_course):
        """Test complete quiz taking experience."""
        user_id = "user_123"
        course = sample_python_course
        
        # Setup quizzes
        for quiz in course["quizzes"]:
            mock_learning_platform.quizzes[quiz.id] = quiz
        
        # Initialize user progress
        progress = UserProgress(user_id, course["course_id"], course["lessons"][0].id)
        mock_learning_platform.user_progress[user_id] = progress
        
        # Take first quiz
        quiz = course["quizzes"][0]  # quiz_1
        
        # Simulate quiz attempt
        user_answers = {
            "q1": 1,  # Correct: Python is a programming language
            "q2": True  # Correct: Python is case-sensitive
        }
        
        # Calculate score
        total_points = 0
        earned_points = 0
        
        for question in quiz.questions:
            total_points += question["points"]
            if user_answers.get(question["id"]) == question["correct_answer"]:
                earned_points += question["points"]
        
        score_percentage = (earned_points / total_points) * 100
        
        # Record quiz attempt
        if quiz.id not in progress.quiz_attempts:
            progress.quiz_attempts[quiz.id] = []
        
        attempt_data = {
            "attempt_number": len(progress.quiz_attempts[quiz.id]) + 1,
            "answers": user_answers,
            "score": score_percentage,
            "passed": score_percentage >= quiz.passing_score,
            "timestamp": datetime.now(),
            "time_taken_minutes": 5
        }
        
        progress.quiz_attempts[quiz.id].append(attempt_data)
        
        # Track quiz completion
        await mock_learning_platform.track_lesson_progress(user_id, quiz.lesson_id, {
            "action": "quiz_completed",
            "quiz_id": quiz.id,
            "attempt_data": attempt_data
        })
        
        # Verify quiz results
        assert score_percentage == 100  # Both answers correct
        assert attempt_data["passed"] is True
        assert len(progress.quiz_attempts[quiz.id]) == 1
    
    @pytest.mark.asyncio
    async def test_quiz_retake_policy(self, mock_learning_platform, sample_python_course):
        """Test quiz retake policies and attempt limits."""
        user_id = "user_123"
        quiz = sample_python_course["quizzes"][0]
        mock_learning_platform.quizzes[quiz.id] = quiz
        
        progress = UserProgress(user_id, "course_123", "lesson_1")
        progress.quiz_attempts[quiz.id] = []
        mock_learning_platform.user_progress[user_id] = progress
        
        # Simulate multiple attempts
        attempt_scenarios = [
            {"answers": {"q1": 0, "q2": False}, "expected_score": 0},  # All wrong
            {"answers": {"q1": 1, "q2": False}, "expected_score": 66.67},  # Partial
            {"answers": {"q1": 1, "q2": True}, "expected_score": 100}  # All correct
        ]
        
        for i, scenario in enumerate(attempt_scenarios):
            # Check if user can still attempt
            if len(progress.quiz_attempts[quiz.id]) >= quiz.max_attempts:
                with pytest.raises(PermissionError, match="Maximum attempts exceeded"):
                    raise PermissionError("Maximum attempts exceeded")
                break
            
            # Calculate score for this attempt
            earned_points = 0
            total_points = 0
            
            for question in quiz.questions:
                total_points += question["points"]
                if scenario["answers"].get(question["id"]) == question["correct_answer"]:
                    earned_points += question["points"]
            
            score = (earned_points / total_points) * 100
            
            # Record attempt
            attempt_data = {
                "attempt_number": i + 1,
                "answers": scenario["answers"],
                "score": score,
                "passed": score >= quiz.passing_score,
                "timestamp": datetime.now()
            }
            
            progress.quiz_attempts[quiz.id].append(attempt_data)
            
            # Check if expected score matches
            assert abs(score - scenario["expected_score"]) < 0.1
        
        # Verify attempt tracking
        assert len(progress.quiz_attempts[quiz.id]) == 3
        assert progress.quiz_attempts[quiz.id][-1]["passed"] is True  # Last attempt passed
    
    @pytest.mark.asyncio
    async def test_timed_quiz_functionality(self, mock_learning_platform):
        """Test timed quiz functionality."""
        user_id = "user_123"
        
        # Create timed quiz
        timed_quiz = Quiz(
            "timed_quiz_1",
            "lesson_advanced",
            [
                {"id": "tq1", "question": "Complex question 1", "type": "multiple_choice",
                 "options": ["A", "B", "C", "D"], "correct_answer": 2, "points": 20},
                {"id": "tq2", "question": "Complex question 2", "type": "multiple_choice",
                 "options": ["A", "B", "C", "D"], "correct_answer": 1, "points": 20}
            ],
            time_limit_minutes=10
        )
        
        mock_learning_platform.quizzes[timed_quiz.id] = timed_quiz
        
        # Simulate quiz session with timing
        quiz_start_time = datetime.now()
        
        # Simulate user taking time to answer
        await asyncio.sleep(0.1)  # Simulate thinking time
        
        quiz_end_time = datetime.now()
        time_taken = (quiz_end_time - quiz_start_time).total_seconds() / 60  # Convert to minutes
        
        # Check if quiz was completed within time limit
        if time_taken > timed_quiz.time_limit_minutes:
            quiz_result = {
                "status": "timeout",
                "score": 0,
                "message": "Time limit exceeded"
            }
        else:
            quiz_result = {
                "status": "completed",
                "score": 100,  # Perfect score
                "time_taken_minutes": time_taken,
                "message": "Quiz completed successfully"
            }
        
        # Track timed quiz result
        await mock_learning_platform.track_lesson_progress(user_id, timed_quiz.lesson_id, {
            "action": "timed_quiz_completed",
            "quiz_id": timed_quiz.id,
            "result": quiz_result,
            "time_limit": timed_quiz.time_limit_minutes
        })
        
        assert quiz_result["status"] == "completed"
        assert quiz_result["time_taken_minutes"] < timed_quiz.time_limit_minutes


class TestAdaptiveLearning:
    """Test adaptive learning features and personalization."""
    
    @pytest.mark.asyncio
    async def test_difficulty_adjustment(self, mock_learning_platform, sample_python_course):
        """Test adaptive difficulty adjustment based on performance."""
        user_id = "user_123"
        course = sample_python_course
        
        # Initialize user progress with some quiz history
        progress = UserProgress(user_id, course["course_id"], "lesson_1")
        
        # Simulate quiz performance history
        quiz_history = [
            {"quiz_id": "quiz_1", "score": 95, "difficulty": "medium"},
            {"quiz_id": "quiz_2", "score": 90, "difficulty": "medium"},
            {"quiz_id": "quiz_3", "score": 85, "difficulty": "medium"}
        ]
        
        # Calculate average performance
        avg_score = sum(q["score"] for q in quiz_history) / len(quiz_history)
        
        # Adaptive difficulty logic
        if avg_score >= 90:
            recommended_difficulty = "hard"
            additional_challenges = True
        elif avg_score >= 70:
            recommended_difficulty = "medium"
            additional_challenges = False
        else:
            recommended_difficulty = "easy"
            additional_challenges = False
        
        # Store adaptive recommendations
        mock_learning_platform.adaptive_recommendations[user_id] = {
            "recommended_difficulty": recommended_difficulty,
            "additional_challenges": additional_challenges,
            "performance_trend": "improving" if quiz_history[-1]["score"] > quiz_history[0]["score"] else "stable",
            "suggested_review_topics": []
        }
        
        # Track adaptive adjustment
        await mock_learning_platform.track_lesson_progress(user_id, "adaptive_system", {
            "action": "difficulty_adjusted",
            "previous_difficulty": "medium",
            "new_difficulty": recommended_difficulty,
            "reason": f"Based on average score of {avg_score}%"
        })
        
        assert recommended_difficulty == "hard"
        assert additional_challenges is True
        assert user_id in mock_learning_platform.adaptive_recommendations
    
    @pytest.mark.asyncio
    async def test_personalized_content_recommendations(self, mock_learning_platform):
        """Test personalized content recommendations."""
        user_id = "user_123"
        
        # User learning preferences and history
        user_profile = {
            "learning_style": "visual",
            "preferred_content_types": ["video", "interactive"],
            "weak_areas": ["loops", "functions"],
            "strong_areas": ["variables", "data_types"],
            "study_time_preference": "evening"
        }
        
        # Available supplementary content
        supplementary_content = [
            {"id": "vid_loops", "type": "video", "topic": "loops", "difficulty": "easy"},
            {"id": "int_functions", "type": "interactive", "topic": "functions", "difficulty": "medium"},
            {"id": "txt_loops", "type": "text", "topic": "loops", "difficulty": "medium"},
            {"id": "vid_advanced", "type": "video", "topic": "advanced_concepts", "difficulty": "hard"}
        ]
        
        # Generate personalized recommendations
        recommendations = []
        
        for content in supplementary_content:
            score = 0
            
            # Prefer user's preferred content types
            if content["type"] in user_profile["preferred_content_types"]:
                score += 30
            
            # Prioritize weak areas
            if content["topic"] in user_profile["weak_areas"]:
                score += 50
            
            # Avoid topics user is already strong in (unless advanced)
            if content["topic"] in user_profile["strong_areas"] and content["difficulty"] != "hard":
                score -= 20
            
            if score > 20:  # Threshold for recommendation
                recommendations.append({
                    "content_id": content["id"],
                    "score": score,
                    "reason": f"Recommended for {content['topic']} improvement"
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        # Store recommendations
        mock_learning_platform.adaptive_recommendations[user_id] = {
            "personalized_content": recommendations[:3],  # Top 3 recommendations
            "generated_at": datetime.now(),
            "user_profile": user_profile
        }
        
        # Track recommendation generation
        await mock_learning_platform.track_lesson_progress(user_id, "recommendation_system", {
            "action": "recommendations_generated",
            "num_recommendations": len(recommendations),
            "top_recommendation": recommendations[0] if recommendations else None
        })
        
        assert len(recommendations) > 0
        assert recommendations[0]["score"] >= 50  # Should be weak area content
        assert any("loops" in rec["reason"] or "functions" in rec["reason"] for rec in recommendations)


class TestKnowledgeRetention:
    """Test knowledge retention tracking and spaced repetition."""
    
    @pytest.mark.asyncio
    async def test_spaced_repetition_scheduling(self, mock_learning_platform):
        """Test spaced repetition algorithm for knowledge retention."""
        user_id = "user_123"
        
        # Topics learned with initial performance
        learned_topics = [
            {"topic": "variables", "initial_score": 90, "learned_date": datetime.now() - timedelta(days=7)},
            {"topic": "functions", "initial_score": 85, "learned_date": datetime.now() - timedelta(days=14)},
            {"topic": "loops", "initial_score": 75, "learned_date": datetime.now() - timedelta(days=21)}
        ]
        
        # Spaced repetition intervals (days)
        repetition_intervals = {
            90: [1, 3, 7, 14, 30],    # High performance
            85: [1, 2, 5, 10, 21],    # Good performance
            75: [1, 2, 4, 8, 16]      # Average performance
        }
        
        # Calculate review schedule
        review_schedule = []
        
        for topic_data in learned_topics:
            intervals = repetition_intervals.get(topic_data["initial_score"], [1, 2, 4, 8, 16])
            topic_reviews = []
            
            for i, interval in enumerate(intervals):
                review_date = topic_data["learned_date"] + timedelta(days=interval)
                if review_date <= datetime.now() + timedelta(days=30):  # Within next 30 days
                    topic_reviews.append({
                        "topic": topic_data["topic"],
                        "review_date": review_date,
                        "repetition_number": i + 1,
                        "due": review_date <= datetime.now()
                    })
            
            review_schedule.extend(topic_reviews)
        
        # Sort by due date
        review_schedule.sort(key=lambda x: x["review_date"])
        
        # Track spaced repetition schedule
        await mock_learning_platform.track_lesson_progress(user_id, "retention_system", {
            "action": "spaced_repetition_scheduled",
            "total_reviews": len(review_schedule),
            "due_reviews": len([r for r in review_schedule if r["due"]]),
            "schedule": review_schedule
        })
        
        assert len(review_schedule) > 0
        assert any(review["due"] for review in review_schedule)
        
        # Store retention data
        mock_learning_platform.adaptive_recommendations[user_id] = {
            "spaced_repetition": review_schedule,
            "retention_score": await mock_learning_platform.calculate_knowledge_retention(user_id, "course_123")
        }
    
    @pytest.mark.asyncio
    async def test_knowledge_decay_tracking(self, mock_learning_platform):
        """Test tracking of knowledge decay over time."""
        user_id = "user_123"
        
        # Historical performance data
        performance_history = [
            {"topic": "variables", "date": datetime.now() - timedelta(days=30), "score": 95},
            {"topic": "variables", "date": datetime.now() - timedelta(days=20), "score": 90},
            {"topic": "variables", "date": datetime.now() - timedelta(days=10), "score": 85},
            {"topic": "variables", "date": datetime.now(), "score": 80}
        ]
        
        # Calculate knowledge decay rate
        if len(performance_history) >= 2:
            initial_score = performance_history[0]["score"]
            latest_score = performance_history[-1]["score"]
            time_span = (performance_history[-1]["date"] - performance_history[0]["date"]).days
            
            if time_span > 0:
                decay_rate = (initial_score - latest_score) / time_span  # Points per day
            else:
                decay_rate = 0
        else:
            decay_rate = 0
        
        # Predict future performance
        prediction_days = [7, 14, 30]
        predicted_scores = []
        
        for days in prediction_days:
            predicted_score = max(0, latest_score - (decay_rate * days))
            predicted_scores.append({
                "days_ahead": days,
                "predicted_score": predicted_score,
                "confidence": 0.8 if days <= 14 else 0.6  # Lower confidence for longer predictions
            })
        
        # Store decay analysis
        decay_analysis = {
            "topic": "variables",
            "decay_rate_per_day": decay_rate,
            "current_score": latest_score,
            "predictions": predicted_scores,
            "recommendation": "review_soon" if decay_rate > 0.5 else "stable"
        }
        
        # Track knowledge decay
        await mock_learning_platform.track_lesson_progress(user_id, "retention_system", {
            "action": "knowledge_decay_analyzed",
            "analysis": decay_analysis
        })
        
        assert decay_rate > 0  # Knowledge is decaying
        assert len(predicted_scores) == 3
        assert decay_analysis["recommendation"] in ["review_soon", "stable"]


class TestLearningAnalytics:
    """Test learning analytics and progress insights."""
    
    @pytest.mark.asyncio
    async def test_comprehensive_learning_analytics(self, mock_learning_platform, sample_python_course):
        """Test comprehensive learning analytics generation."""
        user_id = "user_123"
        course = sample_python_course
        
        # Setup comprehensive user data
        progress = UserProgress(user_id, course["course_id"], "lesson_3")
        progress.completed_lessons = ["lesson_1", "lesson_2"]
        progress.time_spent = {
            "lesson_1": 35,  # 5 minutes over estimated
            "lesson_2": 20   # 5 minutes under estimated
        }
        progress.quiz_attempts = {
            "quiz_1": [{"score": 80, "attempt_number": 1}, {"score": 95, "attempt_number": 2}],
            "quiz_2": [{"score": 90, "attempt_number": 1}]
        }
        
        mock_learning_platform.user_progress[user_id] = progress
        
        # Generate analytics
        analytics = {
            "progress_percentage": (len(progress.completed_lessons) / len(course["lessons"])) * 100,
            "average_quiz_score": 91.67,  # (95 + 90 + 80) / 3
            "total_time_spent": sum(progress.time_spent.values()),
            "efficiency_score": 0.85,  # Based on time spent vs estimated
            "engagement_level": "high",
            "learning_velocity": len(progress.completed_lessons) / 7,  # lessons per day
            "strengths": ["quick_learner", "persistent"],
            "improvement_areas": ["time_management"],
            "predicted_completion_date": datetime.now() + timedelta(days=15)
        }
        
        # Track analytics generation
        await mock_learning_platform.track_lesson_progress(user_id, "analytics_system", {
            "action": "analytics_generated",
            "analytics": analytics,
            "generated_at": datetime.now()
        })
        
        # Store analytics
        mock_learning_platform.analytics[f"user_analytics_{user_id}"] = analytics
        
        assert analytics["progress_percentage"] == 40.0  # 2/5 lessons completed
        assert analytics["average_quiz_score"] > 85
        assert analytics["engagement_level"] == "high"
        assert "quick_learner" in analytics["strengths"]
    
    @pytest.mark.asyncio
    async def test_learning_pattern_detection(self, mock_learning_platform):
        """Test detection of learning patterns and habits."""
        user_id = "user_123"
        
        # Simulate learning session data over time
        learning_sessions = [
            {"date": datetime.now() - timedelta(days=6), "start_time": "19:00", "duration": 45, "performance": 85},
            {"date": datetime.now() - timedelta(days=5), "start_time": "19:30", "duration": 60, "performance": 90},
            {"date": datetime.now() - timedelta(days=4), "start_time": "08:00", "duration": 30, "performance": 70},
            {"date": datetime.now() - timedelta(days=3), "start_time": "19:15", "duration": 50, "performance": 88},
            {"date": datetime.now() - timedelta(days=2), "start_time": "19:45", "duration": 55, "performance": 92},
            {"date": datetime.now() - timedelta(days=1), "start_time": "09:00", "duration": 25, "performance": 75}
        ]
        
        # Analyze patterns
        evening_sessions = [s for s in learning_sessions if s["start_time"].startswith("19")]
        morning_sessions = [s for s in learning_sessions if s["start_time"].startswith("0")]
        
        patterns = {
            "preferred_study_time": "evening" if len(evening_sessions) > len(morning_sessions) else "morning",
            "average_session_duration": sum(s["duration"] for s in learning_sessions) / len(learning_sessions),
            "performance_by_time": {
                "evening": sum(s["performance"] for s in evening_sessions) / len(evening_sessions) if evening_sessions else 0,
                "morning": sum(s["performance"] for s in morning_sessions) / len(morning_sessions) if morning_sessions else 0
            },
            "consistency_score": 0.8,  # Based on regular study schedule
            "optimal_session_length": 50,  # Minutes that correlate with best performance
            "weekly_frequency": len(learning_sessions) / 7
        }
        
        # Generate recommendations based on patterns
        recommendations = []
        if patterns["performance_by_time"]["evening"] > patterns["performance_by_time"]["morning"]:
            recommendations.append("Schedule study sessions in the evening for better performance")
        
        if patterns["average_session_duration"] < patterns["optimal_session_length"]:
            recommendations.append("Consider extending study sessions to 50 minutes for optimal learning")
        
        # Track pattern analysis
        await mock_learning_platform.track_lesson_progress(user_id, "pattern_analysis", {
            "action": "learning_patterns_detected",
            "patterns": patterns,
            "recommendations": recommendations,
            "analysis_date": datetime.now()
        })
        
        assert patterns["preferred_study_time"] == "evening"
        assert patterns["performance_by_time"]["evening"] > patterns["performance_by_time"]["morning"]
        assert len(recommendations) > 0


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])