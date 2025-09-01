# Location: src/python_mastery_hub/web/api/exercises.py

"""
Exercises API Router

Handles API endpoints for code exercises, submissions, evaluation,
and interactive coding challenges with real-time feedback.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator

from python_mastery_hub.web.middleware.auth import get_current_user
from python_mastery_hub.web.models.user import User
from python_mastery_hub.web.services.code_executor import CodeExecutor
from python_mastery_hub.web.services.progress_service import ProgressService
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class ExerciseInfo(BaseModel):
    """Exercise information."""
    id: str
    title: str
    description: str
    module_id: str
    difficulty: str
    estimated_minutes: int
    starter_code: str
    instructions: str
    hints: List[str] = []
    test_cases: List[Dict[str, Any]] = []


class ExerciseSubmission(BaseModel):
    """Exercise submission request."""
    exercise_id: str
    code: str
    language: str = "python"
    
    @validator('code')
    def validate_code(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Code cannot be empty')
        if len(v) > 50000:  # 50KB limit
            raise ValueError('Code too long (max 50KB)')
        return v


class TestResult(BaseModel):
    """Individual test case result."""
    test_id: str
    passed: bool
    expected_output: str
    actual_output: str
    error_message: Optional[str] = None
    execution_time: float


class SubmissionResult(BaseModel):
    """Exercise submission result."""
    submission_id: str
    exercise_id: str
    passed: bool
    score: float
    max_score: float
    percentage: float
    execution_time: float
    test_results: List[TestResult]
    feedback: List[str]
    hints_used: int
    attempt_number: int


class ExerciseAttempt(BaseModel):
    """Exercise attempt history."""
    id: str
    exercise_id: str
    submitted_at: str
    score: float
    passed: bool
    execution_time: float
    code_length: int


class ExerciseProgress(BaseModel):
    """Exercise progress summary."""
    exercise_id: str
    attempts: int
    best_score: float
    completed: bool
    first_attempt_date: Optional[str]
    completion_date: Optional[str]
    total_time_spent: int  # minutes


class CodeExecutionRequest(BaseModel):
    """Code execution request for testing."""
    code: str
    language: str = "python"
    input_data: Optional[str] = None
    timeout: int = 10  # seconds


class CodeExecutionResult(BaseModel):
    """Code execution result."""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float
    memory_usage: Optional[int] = None


class UserExerciseStats(BaseModel):
    """User exercise statistics."""
    total_exercises: int
    completed_exercises: int
    in_progress_exercises: int
    total_attempts: int
    average_score: float
    total_time_spent: int  # minutes
    completion_rate: float
    streak_days: int
    last_activity: Optional[str]


# Exercise database (in a real app, this would be in a database)
EXERCISES_DATA = {
    "basics_variables": {
        "id": "basics_variables",
        "title": "Variable Assignment and Types",
        "description": "Practice creating variables of different types and performing basic operations.",
        "module_id": "basics",
        "difficulty": "beginner",
        "estimated_minutes": 15,
        "starter_code": """# Create variables of different types
name = # Your code here
age = # Your code here  
height = # Your code here
is_student = # Your code here

# Print them using f-strings
print(f"Name: {name}")
print(f"Age: {age}")  
print(f"Height: {height}")
print(f"Student: {is_student}")""",
        "instructions": "Create variables 'name' (string), 'age' (int), 'height' (float), and 'is_student' (bool), then print them using f-strings.",
        "hints": [
            "Remember to use quotes for strings",
            "Boolean values are True or False (capitalized)",
            "Use f-strings for formatted output: f'text {variable}'"
        ],
        "test_cases": [
            {
                "id": "test_1",
                "description": "Check variable types",
                "expected_output": "Name: Alice\nAge: 25\nHeight: 5.6\nStudent: True",
                "test_code": "isinstance(name, str) and isinstance(age, int) and isinstance(height, float) and isinstance(is_student, bool)"
            }
        ]
    },
    "basics_loops": {
        "id": "basics_loops",
        "title": "For Loop Practice",
        "description": "Create a function that counts from 1 to n using a for loop.",
        "module_id": "basics",
        "difficulty": "beginner",
        "estimated_minutes": 20,
        "starter_code": """def count_to_n(n):
    \"\"\"Count from 1 to n using a for loop\"\"\"
    # Your code here
    pass

# Test your function
count_to_n(5)""",
        "instructions": "Complete the function to print numbers from 1 to n (inclusive) using a for loop and range().",
        "hints": [
            "Use range(1, n + 1) to include n",
            "Print each number in the loop",
            "Remember range is exclusive of the end value"
        ],
        "test_cases": [
            {
                "id": "test_1",
                "description": "Count to 5",
                "expected_output": "1\n2\n3\n4\n5",
                "input": "5"
            }
        ]
    },
    "oop_class_basics": {
        "id": "oop_class_basics",
        "title": "Create a Simple Class",
        "description": "Define a Person class with attributes and methods.",
        "module_id": "oop",
        "difficulty": "intermediate",
        "estimated_minutes": 25,
        "starter_code": """class Person:
    def __init__(self, name, age):
        # Initialize attributes here
        pass
    
    def greet(self):
        # Return a greeting message
        pass
    
    def have_birthday(self):
        # Increment age by 1
        pass

# Test your class
person = Person("Alice", 30)
print(person.greet())
person.have_birthday()
print(f"Age after birthday: {person.age}")""",
        "instructions": "Complete the Person class with name and age attributes, a greet method that returns a greeting, and a have_birthday method that increments age.",
        "hints": [
            "Use self.attribute_name to store instance variables",
            "The greet method should return a formatted string",
            "Don't forget the self parameter in methods"
        ],
        "test_cases": [
            {
                "id": "test_1",
                "description": "Check class functionality",
                "expected_output": "Hello, I'm Alice and I'm 30 years old\nAge after birthday: 31"
            }
        ]
    }
}


# Dependencies
async def get_code_executor() -> CodeExecutor:
    """Get code executor service."""
    return CodeExecutor()


async def get_progress_service() -> ProgressService:
    """Get progress service."""
    return ProgressService()


# Routes
@router.get("/", response_model=List[ExerciseInfo])
async def list_exercises(
    module_id: Optional[str] = None,
    difficulty: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get list of available exercises."""
    try:
        exercises = []
        
        for exercise_data in EXERCISES_DATA.values():
            # Apply filters
            if module_id and exercise_data['module_id'] != module_id:
                continue
            if difficulty and exercise_data['difficulty'] != difficulty:
                continue
            
            exercise = ExerciseInfo(
                id=exercise_data['id'],
                title=exercise_data['title'],
                description=exercise_data['description'],
                module_id=exercise_data['module_id'],
                difficulty=exercise_data['difficulty'],
                estimated_minutes=exercise_data['estimated_minutes'],
                starter_code=exercise_data['starter_code'],
                instructions=exercise_data['instructions'],
                hints=exercise_data['hints'],
                test_cases=exercise_data['test_cases']
            )
            exercises.append(exercise)
        
        return exercises
    
    except Exception as e:
        logger.error(f"Failed to list exercises: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exercises"
        )


@router.get("/{exercise_id}", response_model=ExerciseInfo)
async def get_exercise(
    exercise_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get specific exercise details."""
    try:
        if exercise_id not in EXERCISES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise '{exercise_id}' not found"
            )
        
        exercise_data = EXERCISES_DATA[exercise_id]
        
        return ExerciseInfo(
            id=exercise_data['id'],
            title=exercise_data['title'],
            description=exercise_data['description'],
            module_id=exercise_data['module_id'],
            difficulty=exercise_data['difficulty'],
            estimated_minutes=exercise_data['estimated_minutes'],
            starter_code=exercise_data['starter_code'],
            instructions=exercise_data['instructions'],
            hints=exercise_data['hints'],
            test_cases=exercise_data['test_cases']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exercise"
        )


@router.post("/{exercise_id}/submit", response_model=SubmissionResult)
async def submit_exercise(
    exercise_id: str,
    submission: ExerciseSubmission,
    current_user: User = Depends(get_current_user),
    code_executor: CodeExecutor = Depends(get_code_executor),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Submit exercise solution for evaluation."""
    try:
        if exercise_id not in EXERCISES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise '{exercise_id}' not found"
            )
        
        exercise_data = EXERCISES_DATA[exercise_id]
        
        # Generate submission ID
        submission_id = f"{current_user.id}_{exercise_id}_{int(datetime.now().timestamp())}"
        
        # Execute code and run tests
        test_results = []
        total_score = 0
        max_score = len(exercise_data['test_cases'])
        start_time = datetime.now()
        
        for test_case in exercise_data['test_cases']:
            try:
                # Execute user code with test case
                execution_result = await code_executor.execute_code(
                    code=submission.code,
                    language=submission.language,
                    input_data=test_case.get('input', ''),
                    timeout=10
                )
                
                # Check if test passed
                expected = test_case['expected_output'].strip()
                actual = execution_result.output.strip()
                passed = expected == actual
                
                if passed:
                    total_score += 1
                
                test_result = TestResult(
                    test_id=test_case['id'],
                    passed=passed,
                    expected_output=expected,
                    actual_output=actual,
                    error_message=execution_result.error,
                    execution_time=execution_result.execution_time
                )
                test_results.append(test_result)
                
            except Exception as test_error:
                test_result = TestResult(
                    test_id=test_case['id'],
                    passed=False,
                    expected_output=test_case['expected_output'],
                    actual_output="",
                    error_message=str(test_error),
                    execution_time=0.0
                )
                test_results.append(test_result)
        
        # Calculate results
        execution_time = (datetime.now() - start_time).total_seconds()
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        passed = percentage >= 70  # 70% passing threshold
        
        # Generate feedback
        feedback = []
        if passed:
            feedback.append("Great work! All tests passed.")
        else:
            feedback.append(f"Some tests failed. Score: {total_score}/{max_score}")
            failed_tests = [tr for tr in test_results if not tr.passed]
            if failed_tests:
                feedback.append(f"Failed {len(failed_tests)} test(s). Review the expected vs actual output.")
        
        # Get attempt number
        attempt_number = await progress_service.get_exercise_attempt_count(
            current_user.id, 
            exercise_id
        ) + 1
        
        # Save submission
        await progress_service.save_exercise_submission(
            user_id=current_user.id,
            exercise_id=exercise_id,
            submission_id=submission_id,
            code=submission.code,
            score=total_score,
            max_score=max_score,
            passed=passed,
            execution_time=execution_time
        )
        
        # Update progress if passed
        if passed:
            await progress_service.mark_topic_completed(
                user_id=current_user.id,
                module_id=exercise_data['module_id'],
                topic_id=exercise_id,
                score=percentage / 100,
                time_spent=int(execution_time / 60)
            )
        
        logger.info(f"Exercise submission {submission_id} evaluated: {percentage}% score")
        
        return SubmissionResult(
            submission_id=submission_id,
            exercise_id=exercise_id,
            passed=passed,
            score=total_score,
            max_score=max_score,
            percentage=percentage,
            execution_time=execution_time,
            test_results=test_results,
            feedback=feedback,
            hints_used=0,  # Would track this in a real implementation
            attempt_number=attempt_number
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit exercise"
        )


@router.post("/execute", response_model=CodeExecutionResult)
async def execute_code(
    execution_request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user),
    code_executor: CodeExecutor = Depends(get_code_executor)
):
    """Execute code for testing purposes (without submission)."""
    try:
        result = await code_executor.execute_code(
            code=execution_request.code,
            language=execution_request.language,
            input_data=execution_request.input_data,
            timeout=execution_request.timeout
        )
        
        return CodeExecutionResult(
            success=result.success,
            output=result.output,
            error=result.error,
            execution_time=result.execution_time,
            memory_usage=result.memory_usage
        )
    
    except Exception as e:
        logger.error(f"Failed to execute code: {e}")
        return CodeExecutionResult(
            success=False,
            output="",
            error=str(e),
            execution_time=0.0
        )


@router.get("/{exercise_id}/attempts", response_model=List[ExerciseAttempt])
async def get_exercise_attempts(
    exercise_id: str,
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get user's attempt history for an exercise."""
    try:
        attempts = await progress_service.get_exercise_attempts(
            current_user.id, 
            exercise_id
        )
        
        return [
            ExerciseAttempt(
                id=attempt['id'],
                exercise_id=attempt['exercise_id'],
                submitted_at=attempt['submitted_at'],
                score=attempt['score'],
                passed=attempt['passed'],
                execution_time=attempt['execution_time'],
                code_length=attempt['code_length']
            )
            for attempt in attempts
        ]
    
    except Exception as e:
        logger.error(f"Failed to get attempts for exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exercise attempts"
        )


@router.get("/{exercise_id}/progress", response_model=ExerciseProgress)
async def get_exercise_progress(
    exercise_id: str,
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get user's progress on a specific exercise."""
    try:
        progress_data = await progress_service.get_exercise_progress(
            current_user.id, 
            exercise_id
        )
        
        if not progress_data:
            return ExerciseProgress(
                exercise_id=exercise_id,
                attempts=0,
                best_score=0.0,
                completed=False,
                first_attempt_date=None,
                completion_date=None,
                total_time_spent=0
            )
        
        return ExerciseProgress(
            exercise_id=exercise_id,
            attempts=progress_data['attempts'],
            best_score=progress_data['best_score'],
            completed=progress_data['completed'],
            first_attempt_date=progress_data.get('first_attempt_date'),
            completion_date=progress_data.get('completion_date'),
            total_time_spent=progress_data['total_time_spent']
        )
    
    except Exception as e:
        logger.error(f"Failed to get progress for exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exercise progress"
        )


@router.get("/{exercise_id}/hint")
async def get_exercise_hint(
    exercise_id: str,
    hint_number: int = 1,
    current_user: User = Depends(get_current_user)
):
    """Get a hint for the exercise."""
    try:
        if exercise_id not in EXERCISES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise '{exercise_id}' not found"
            )
        
        exercise_data = EXERCISES_DATA[exercise_id]
        hints = exercise_data.get('hints', [])
        
        if hint_number < 1 or hint_number > len(hints):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hint {hint_number} not available. Exercise has {len(hints)} hints."
            )
        
        hint = hints[hint_number - 1]
        
        # In a real implementation, you might track hint usage
        # await progress_service.track_hint_usage(current_user.id, exercise_id, hint_number)
        
        return {
            "exercise_id": exercise_id,
            "hint_number": hint_number,
            "hint": hint,
            "total_hints": len(hints)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get hint for exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve hint"
        )


@router.get("/modules/{module_id}", response_model=List[ExerciseInfo])
async def get_module_exercises(
    module_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get all exercises for a specific module."""
    try:
        return await list_exercises(module_id=module_id, current_user=current_user)
    
    except Exception as e:
        logger.error(f"Failed to get exercises for module {module_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve module exercises"
        )


@router.get("/user/stats", response_model=UserExerciseStats)
async def get_user_exercise_stats(
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get user's overall exercise statistics."""
    try:
        stats_data = await progress_service.get_user_exercise_stats(current_user.id)
        
        return UserExerciseStats(
            total_exercises=stats_data.get('total_exercises', 0),
            completed_exercises=stats_data.get('completed_exercises', 0),
            in_progress_exercises=stats_data.get('in_progress_exercises', 0),
            total_attempts=stats_data.get('total_attempts', 0),
            average_score=stats_data.get('average_score', 0.0),
            total_time_spent=stats_data.get('total_time_spent', 0),
            completion_rate=stats_data.get('completion_rate', 0.0),
            streak_days=stats_data.get('streak_days', 0),
            last_activity=stats_data.get('last_activity')
        )
    
    except Exception as e:
        logger.error(f"Failed to get user exercise stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exercise statistics"
        )


@router.delete("/{exercise_id}/submissions/{submission_id}")
async def delete_submission(
    exercise_id: str,
    submission_id: str,
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Delete a specific exercise submission."""
    try:
        # Verify the submission belongs to the current user
        submission = await progress_service.get_submission(submission_id)
        if not submission or submission['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        await progress_service.delete_submission(submission_id)
        
        return {"message": "Submission deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete submission {submission_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete submission"
        )


@router.post("/{exercise_id}/reset")
async def reset_exercise_progress(
    exercise_id: str,
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Reset user's progress on a specific exercise."""
    try:
        if exercise_id not in EXERCISES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise '{exercise_id}' not found"
            )
        
        await progress_service.reset_exercise_progress(current_user.id, exercise_id)
        
        return {"message": f"Progress reset for exercise '{exercise_id}'"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset progress for exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset exercise progress"
        )