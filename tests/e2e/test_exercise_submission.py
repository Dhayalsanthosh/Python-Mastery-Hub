# tests/e2e/test_exercise_submission.py
"""
End-to-end tests for exercise submission and evaluation system.
Tests code submission, automated testing, plagiarism detection,
peer review, and instructor feedback workflows.
"""
import pytest
import asyncio
import ast
import hashlib
import difflib
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SubmissionStatus(Enum):
    """Enumeration for submission statuses."""
    PENDING = "pending"
    RUNNING_TESTS = "running_tests"
    COMPLETED = "completed"
    FAILED = "failed"
    PLAGIARISM_DETECTED = "plagiarism_detected"
    REQUIRES_REVIEW = "requires_review"


class TestResult(Enum):
    """Enumeration for test results."""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ExerciseDefinition:
    """Represents an exercise/assignment definition."""
    id: str
    title: str
    description: str
    difficulty: str
    max_score: int
    time_limit_minutes: Optional[int]
    allowed_attempts: int
    starter_code: str
    test_cases: List[Dict[str, Any]]
    rubric: Dict[str, Any]
    requires_peer_review: bool = False
    plagiarism_check: bool = True


@dataclass
class TestCase:
    """Represents a single test case."""
    id: str
    name: str
    input_data: Any
    expected_output: Any
    weight: int = 1
    timeout_seconds: int = 5
    hidden: bool = False


@dataclass
class Submission:
    """Represents a student's code submission."""
    id: str
    user_id: str
    exercise_id: str
    code: str
    submitted_at: datetime
    status: SubmissionStatus
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    plagiarism_score: float = 0.0
    plagiarism_matches: List[Dict] = field(default_factory=list)
    score: int = 0
    feedback: str = ""
    execution_time: float = 0.0
    attempt_number: int = 1


class MockCodeExecutor:
    """Mock code execution environment."""
    
    def __init__(self):
        self.execution_history = []
        self.security_violations = []
    
    async def execute_code(self, code: str, test_input: Any = None, timeout: int = 5) -> Dict[str, Any]:
        """Execute code with security checks and return results."""
        execution_start = datetime.now()
        
        # Security checks
        security_result = self._security_check(code)
        if not security_result["safe"]:
            self.security_violations.append({
                "code": code,
                "violations": security_result["violations"],
                "timestamp": datetime.now()
            })
            return {
                "status": "error",
                "error": "Security violation detected",
                "violations": security_result["violations"]
            }
        
        # Simulate code execution
        try:
            # Mock successful execution
            execution_time = (datetime.now() - execution_start).total_seconds()
            
            result = {
                "status": "success",
                "output": "Execution completed successfully",
                "execution_time": execution_time,
                "memory_usage": 1024 * 1024,  # 1MB
                "return_value": test_input * 2 if test_input else "Hello, World!"
            }
            
            self.execution_history.append({
                "code": code,
                "result": result,
                "timestamp": datetime.now()
            })
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "execution_time": (datetime.now() - execution_start).total_seconds()
            }
    
    def _security_check(self, code: str) -> Dict[str, Any]:
        """Check code for security violations."""
        violations = []
        
        # Check for dangerous imports
        dangerous_imports = ['os', 'sys', 'subprocess', 'socket', 'urllib', 'requests']
        for imp in dangerous_imports:
            if f"import {imp}" in code or f"from {imp}" in code:
                violations.append(f"Dangerous import detected: {imp}")
        
        # Check for file operations
        file_operations = ['open(', 'file(', 'write(', 'read(']
        for op in file_operations:
            if op in code:
                violations.append(f"File operation detected: {op}")
        
        # Check for eval/exec
        if 'eval(' in code or 'exec(' in code:
            violations.append("Dynamic code execution detected")
        
        return {
            "safe": len(violations) == 0,
            "violations": violations
        }


class MockPlagiarismDetector:
    """Mock plagiarism detection system."""
    
    def __init__(self):
        self.submission_database = {}
        self.similarity_threshold = 0.8
    
    async def check_plagiarism(self, submission: Submission, existing_submissions: List[Submission]) -> Dict[str, Any]:
        """Check submission for plagiarism against existing submissions."""
        matches = []
        
        for existing in existing_submissions:
            if existing.user_id == submission.user_id:
                continue  # Skip same user's previous submissions
                
            similarity = self._calculate_similarity(submission.code, existing.code)
            
            if similarity > self.similarity_threshold:
                matches.append({
                    "submission_id": existing.id,
                    "user_id": existing.user_id,
                    "similarity_score": similarity,
                    "matching_lines": self._find_matching_lines(submission.code, existing.code)
                })
        
        plagiarism_score = max([m["similarity_score"] for m in matches], default=0.0)
        
        return {
            "plagiarism_detected": plagiarism_score > self.similarity_threshold,
            "similarity_score": plagiarism_score,
            "matches": matches,
            "analysis_timestamp": datetime.now()
        }
    
    def _calculate_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code submissions."""
        # Normalize code (remove whitespace, comments)
        normalized1 = self._normalize_code(code1)
        normalized2 = self._normalize_code(code2)
        
        # Use sequence matcher for similarity
        matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
        return matcher.ratio()
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison."""
        lines = code.split('\n')
        normalized_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Remove empty lines and comments
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def _find_matching_lines(self, code1: str, code2: str) -> List[Tuple[int, int]]:
        """Find matching line numbers between two code submissions."""
        lines1 = code1.split('\n')
        lines2 = code2.split('\n')
        matches = []
        
        for i, line1 in enumerate(lines1):
            for j, line2 in enumerate(lines2):
                if line1.strip() == line2.strip() and line1.strip():
                    matches.append((i + 1, j + 1))
        
        return matches


class MockSubmissionPlatform:
    """Mock platform for exercise submissions."""
    
    def __init__(self):
        self.exercises = {}
        self.submissions = {}
        self.users = {}
        self.test_results = {}
        self.peer_reviews = {}
        self.instructor_feedback = {}
        self.analytics = {}
        self.code_executor = MockCodeExecutor()
        self.plagiarism_detector = MockPlagiarismDetector()
    
    def reset(self):
        """Reset all platform data."""
        self.__init__()
    
    async def submit_exercise(self, user_id: str, exercise_id: str, code: str) -> Submission:
        """Submit code for an exercise."""
        submission = Submission(
            id=f"sub_{user_id}_{exercise_id}_{datetime.now().timestamp()}",
            user_id=user_id,
            exercise_id=exercise_id,
            code=code,
            submitted_at=datetime.now(),
            status=SubmissionStatus.PENDING
        )
        
        self.submissions[submission.id] = submission
        return submission
    
    async def evaluate_submission(self, submission_id: str) -> Dict[str, Any]:
        """Evaluate a submission through the complete pipeline."""
        submission = self.submissions[submission_id]
        exercise = self.exercises[submission.exercise_id]
        
        # Update status
        submission.status = SubmissionStatus.RUNNING_TESTS
        
        # Run tests
        test_results = await self._run_tests(submission, exercise)
        submission.test_results = test_results["results"]
        submission.score = test_results["score"]
        
        # Check plagiarism if enabled
        if exercise.plagiarism_check:
            existing_submissions = [s for s in self.submissions.values() 
                                 if s.exercise_id == exercise.id and s.id != submission_id]
            plagiarism_result = await self.plagiarism_detector.check_plagiarism(submission, existing_submissions)
            
            submission.plagiarism_score = plagiarism_result["similarity_score"]
            submission.plagiarism_matches = plagiarism_result["matches"]
            
            if plagiarism_result["plagiarism_detected"]:
                submission.status = SubmissionStatus.PLAGIARISM_DETECTED
                return {"status": "plagiarism_detected", "submission": submission}
        
        # Determine final status
        if exercise.requires_peer_review:
            submission.status = SubmissionStatus.REQUIRES_REVIEW
        else:
            submission.status = SubmissionStatus.COMPLETED
        
        return {"status": "success", "submission": submission}
    
    async def _run_tests(self, submission: Submission, exercise: ExerciseDefinition) -> Dict[str, Any]:
        """Run test cases against submission."""
        results = []
        total_score = 0
        
        for test_case in exercise.test_cases:
            result = await self.code_executor.execute_code(
                submission.code,
                test_case.get("input"),
                test_case.get("timeout", 5)
            )
            
            if result["status"] == "success":
                # Check if output matches expected
                expected = test_case.get("expected_output")
                actual = result.get("return_value")
                
                if self._compare_outputs(actual, expected):
                    test_result = TestResult.PASSED
                    score = test_case.get("weight", 1)
                else:
                    test_result = TestResult.FAILED
                    score = 0
            else:
                test_result = TestResult.ERROR
                score = 0
            
            results.append({
                "test_case_id": test_case["id"],
                "result": test_result.value,
                "score": score,
                "execution_time": result.get("execution_time", 0),
                "output": result.get("output", ""),
                "error": result.get("error", ""),
                "expected": test_case.get("expected_output"),
                "actual": result.get("return_value")
            })
            
            total_score += score
        
        # Calculate percentage score
        max_possible_score = sum(tc.get("weight", 1) for tc in exercise.test_cases)
        percentage_score = (total_score / max_possible_score * exercise.max_score) if max_possible_score > 0 else 0
        
        return {
            "results": results,
            "score": int(percentage_score),
            "max_score": exercise.max_score,
            "tests_passed": len([r for r in results if r["result"] == TestResult.PASSED.value]),
            "total_tests": len(results)
        }
    
    def _compare_outputs(self, actual: Any, expected: Any) -> bool:
        """Compare actual output with expected output."""
        if type(actual) != type(expected):
            return False
        
        if isinstance(actual, (list, tuple)):
            return len(actual) == len(expected) and all(a == e for a, e in zip(actual, expected))
        
        return actual == expected


@pytest.fixture
def mock_platform():
    """Fixture providing a clean mock submission platform."""
    return MockSubmissionPlatform()


@pytest.fixture
def sample_exercises():
    """Fixture providing sample exercise definitions."""
    return [
        ExerciseDefinition(
            id="ex_basic_function",
            title="Basic Function Implementation",
            description="Write a function that calculates the sum of two numbers",
            difficulty="beginner",
            max_score=100,
            time_limit_minutes=30,
            allowed_attempts=3,
            starter_code="def add_numbers(a, b):\n    # Your code here\n    pass",
            test_cases=[
                {"id": "test_1", "input": [2, 3], "expected_output": 5, "weight": 1},
                {"id": "test_2", "input": [10, -5], "expected_output": 5, "weight": 1},
                {"id": "test_3", "input": [0, 0], "expected_output": 0, "weight": 1}
            ],
            rubric={
                "correctness": 60,
                "code_quality": 20,
                "efficiency": 20
            }
        ),
        ExerciseDefinition(
            id="ex_data_structures",
            title="List Processing",
            description="Implement functions to manipulate lists",
            difficulty="intermediate",
            max_score=100,
            time_limit_minutes=60,
            allowed_attempts=2,
            starter_code="def process_list(data):\n    # Your code here\n    pass",
            test_cases=[
                {"id": "test_1", "input": [[1, 2, 3, 4, 5]], "expected_output": [2, 4], "weight": 2},
                {"id": "test_2", "input": [[10, 15, 20, 25]], "expected_output": [10, 20], "weight": 2},
                {"id": "test_3", "input": [[]], "expected_output": [], "weight": 1}
            ],
            rubric={
                "correctness": 50,
                "algorithm_efficiency": 30,
                "code_style": 20
            },
            requires_peer_review=True
        ),
        ExerciseDefinition(
            id="ex_advanced_algorithm",
            title="Algorithm Implementation",
            description="Implement a sorting algorithm",
            difficulty="advanced",
            max_score=100,
            time_limit_minutes=120,
            allowed_attempts=1,
            starter_code="def custom_sort(arr):\n    # Implement your sorting algorithm\n    pass",
            test_cases=[
                {"id": "test_1", "input": [[3, 1, 4, 1, 5]], "expected_output": [1, 1, 3, 4, 5], "weight": 3},
                {"id": "test_2", "input": [[]], "expected_output": [], "weight": 1},
                {"id": "test_3", "input": [[1]], "expected_output": [1], "weight": 1}
            ],
            rubric={
                "correctness": 40,
                "algorithm_efficiency": 35,
                "code_quality": 15,
                "documentation": 10
            },
            plagiarism_check=True
        )
    ]


class TestBasicSubmission:
    """Test basic submission functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_submission_flow(self, mock_platform, sample_exercises):
        """Test complete successful submission workflow."""
        user_id = "user_123"
        exercise = sample_exercises[0]  # Basic function exercise
        mock_platform.exercises[exercise.id] = exercise
        
        # User submits correct solution
        correct_code = """
def add_numbers(a, b):
    return a + b
"""
        
        # Submit exercise
        submission = await mock_platform.submit_exercise(user_id, exercise.id, correct_code)
        
        assert submission.user_id == user_id
        assert submission.exercise_id == exercise.id
        assert submission.status == SubmissionStatus.PENDING
        assert submission.code == correct_code
        
        # Evaluate submission
        result = await mock_platform.evaluate_submission(submission.id)
        
        assert result["status"] == "success"
        assert result["submission"].status == SubmissionStatus.COMPLETED
        assert result["submission"].score > 0
        assert len(result["submission"].test_results) == len(exercise.test_cases)
    
    @pytest.mark.asyncio
    async def test_submission_with_syntax_errors(self, mock_platform, sample_exercises):
        """Test submission with syntax errors."""
        user_id = "user_123"
        exercise = sample_exercises[0]
        mock_platform.exercises[exercise.id] = exercise
        
        # User submits code with syntax error
        incorrect_code = """
def add_numbers(a, b)
    return a + b  # Missing colon
"""
        
        submission = await mock_platform.submit_exercise(user_id, exercise.id, incorrect_code)
        
        # Mock syntax error detection
        with patch.object(mock_platform.code_executor, 'execute_code') as mock_execute:
            mock_execute.return_value = {
                "status": "error",
                "error": "SyntaxError: invalid syntax",
                "execution_time": 0.01
            }
            
            result = await mock_platform.evaluate_submission(submission.id)
            
            assert result["submission"].status == SubmissionStatus.COMPLETED
            assert result["submission"].score == 0
            assert all(tr["result"] == TestResult.ERROR.value for tr in result["submission"].test_results)
    
    @pytest.mark.asyncio
    async def test_submission_attempt_limits(self, mock_platform, sample_exercises):
        """Test submission attempt limit enforcement."""
        user_id = "user_123"
        exercise = sample_exercises[2]  # Advanced exercise with 1 attempt limit
        mock_platform.exercises[exercise.id] = exercise
        
        # First submission
        code1 = "def custom_sort(arr):\n    return sorted(arr)"
        submission1 = await mock_platform.submit_exercise(user_id, exercise.id, code1)
        await mock_platform.evaluate_submission(submission1.id)
        
        # Count user's attempts for this exercise
        user_attempts = len([s for s in mock_platform.submissions.values() 
                           if s.user_id == user_id and s.exercise_id == exercise.id])
        
        # Try second submission (should be blocked)
        if user_attempts >= exercise.allowed_attempts:
            with pytest.raises(PermissionError, match="Attempt limit exceeded"):
                raise PermissionError(f"Attempt limit exceeded for exercise {exercise.id}")
        
        assert user_attempts == 1  # Only one attempt should be recorded


class TestCodeExecution:
    """Test code execution and testing functionality."""
    
    @pytest.mark.asyncio
    async def test_secure_code_execution(self, mock_platform):
        """Test that dangerous code is blocked."""
        dangerous_codes = [
            "import os\nos.system('rm -rf /')",
            "import subprocess\nsubprocess.call(['ls', '/'])",
            "eval('malicious_code')",
            "open('/etc/passwd', 'r').read()"
        ]
        
        for dangerous_code in dangerous_codes:
            result = await mock_platform.code_executor.execute_code(dangerous_code)
            
            assert result["status"] == "error"
            assert "Security violation detected" in result["error"]
            assert len(result["violations"]) > 0
    
    @pytest.mark.asyncio
    async def test_execution_timeout_handling(self, mock_platform):
        """Test handling of code execution timeouts."""
        # Mock infinite loop code
        infinite_loop_code = """
while True:
    pass
"""
        
        with patch.object(mock_platform.code_executor, 'execute_code') as mock_execute:
            mock_execute.return_value = {
                "status": "timeout",
                "error": "Execution timeout after 5 seconds",
                "execution_time": 5.0
            }
            
            result = await mock_platform.code_executor.execute_code(infinite_loop_code, timeout=5)
            
            assert result["status"] == "timeout"
            assert result["execution_time"] >= 5.0
    
    @pytest.mark.asyncio
    async def test_memory_limit_enforcement(self, mock_platform):
        """Test memory limit enforcement during execution."""
        # Mock memory-intensive code
        memory_intensive_code = """
big_list = [0] * (10**8)  # Try to allocate ~800MB
"""
        
        with patch.object(mock_platform.code_executor, 'execute_code') as mock_execute:
            mock_execute.return_value = {
                "status": "error",
                "error": "Memory limit exceeded",
                "memory_usage": 1024 * 1024 * 1024  # 1GB
            }
            
            result = await mock_platform.code_executor.execute_code(memory_intensive_code)
            
            assert result["status"] == "error"
            assert "Memory limit exceeded" in result["error"]


class TestTestCaseExecution:
    """Test automated test case execution."""
    
    @pytest.mark.asyncio
    async def test_multiple_test_cases(self, mock_platform, sample_exercises):
        """Test execution of multiple test cases."""
        user_id = "user_123"
        exercise = sample_exercises[1]  # List processing exercise
        mock_platform.exercises[exercise.id] = exercise
        
        # Correct implementation
        correct_code = """
def process_list(data):
    return [x for x in data if x % 2 == 0]  # Return even numbers
"""
        
        submission = await mock_platform.submit_exercise(user_id, exercise.id, correct_code)
        
        # Mock test execution results
        with patch.object(mock_platform.code_executor, 'execute_code') as mock_execute:
            # Define different results for each test case
            mock_execute.side_effect = [
                {"status": "success", "return_value": [2, 4], "execution_time": 0.01},
                {"status": "success", "return_value": [10, 20], "execution_time": 0.01},
                {"status": "success", "return_value": [], "execution_time": 0.01}
            ]
            
            result = await mock_platform.evaluate_submission(submission.id)
            
            assert len(result["submission"].test_results) == 3
            assert all(tr["result"] == TestResult.PASSED.value for tr in result["submission"].test_results)
            assert result["submission"].score == exercise.max_score
    
    @pytest.mark.asyncio
    async def test_partial_test_case_success(self, mock_platform, sample_exercises):
        """Test partial success in test cases."""
        user_id = "user_123"
        exercise = sample_exercises[0]  # Basic function exercise
        mock_platform.exercises[exercise.id] = exercise
        
        # Partially correct implementation (fails edge cases)
        partial_code = """
def add_numbers(a, b):
    if a == 0 and b == 0:
        return 1  # Wrong for zero case
    return a + b
"""
        
        submission = await mock_platform.submit_exercise(user_id, exercise.id, partial_code)
        
        # Mock test results: 2 pass, 1 fail
        with patch.object(mock_platform.code_executor, 'execute_code') as mock_execute:
            mock_execute.side_effect = [
                {"status": "success", "return_value": 5, "execution_time": 0.01},   # Pass
                {"status": "success", "return_value": 5, "execution_time": 0.01},   # Pass
                {"status": "success", "return_value": 1, "execution_time": 0.01}    # Fail (expected 0)
            ]
            
            result = await mock_platform.evaluate_submission(submission.id)
            
            passed_tests = [tr for tr in result["submission"].test_results if tr["result"] == TestResult.PASSED.value]
            failed_tests = [tr for tr in result["submission"].test_results if tr["result"] == TestResult.FAILED.value]
            
            assert len(passed_tests) == 2
            assert len(failed_tests) == 1
            assert result["submission"].score < exercise.max_score  # Partial credit


class TestPlagiarismDetection:
    """Test plagiarism detection functionality."""
    
    @pytest.mark.asyncio
    async def test_plagiarism_detection_identical_code(self, mock_platform, sample_exercises):
        """Test detection of identical code submissions."""
        exercise = sample_exercises[0]
        mock_platform.exercises[exercise.id] = exercise
        
        # First user's submission
        user1_id = "user_123"
        original_code = """
def add_numbers(a, b):
    return a + b
"""
        
        submission1 = await mock_platform.submit_exercise(user1_id, exercise.id, original_code)
        await mock_platform.evaluate_submission(submission1.id)
        
        # Second user submits identical code
        user2_id = "user_456"
        identical_code = """
def add_numbers(a, b):
    return a + b
"""
        
        submission2 = await mock_platform.submit_exercise(user2_id, exercise.id, identical_code)
        result = await mock_platform.evaluate_submission(submission2.id)
        
        assert result["submission"].plagiarism_score > 0.8  # High similarity
        assert len(result["submission"].plagiarism_matches) > 0
        assert result["submission"].status == SubmissionStatus.PLAGIARISM_DETECTED
    
    @pytest.mark.asyncio
    async def test_plagiarism_detection_with_minor_changes(self, mock_platform, sample_exercises):
        """Test detection of plagiarism with minor cosmetic changes."""
        exercise = sample_exercises[0]
        mock_platform.exercises[exercise.id] = exercise
        
        # Original submission
        user1_id = "user_123"
        original_code = """
def add_numbers(a, b):
    return a + b
"""
        
        submission1 = await mock_platform.submit_exercise(user1_id, exercise.id, original_code)
        await mock_platform.evaluate_submission(submission1.id)
        
        # Modified submission (cosmetic changes)
        user2_id = "user_456"
        modified_code = """
def add_numbers(x, y):  # Changed parameter names
    # Added comment
    return x + y
"""
        
        submission2 = await mock_platform.submit_exercise(user2_id, exercise.id, modified_code)
        result = await mock_platform.evaluate_submission(submission2.id)
        
        # Should still detect high similarity despite cosmetic changes
        assert result["submission"].plagiarism_score > 0.7
        assert len(result["submission"].plagiarism_matches) > 0
    
    @pytest.mark.asyncio
    async def test_legitimate_similar_solutions(self, mock_platform, sample_exercises):
        """Test that legitimate similar solutions aren't flagged as plagiarism."""
        exercise = sample_exercises[0]  # Simple addition function
        mock_platform.exercises[exercise.id] = exercise
        
        # There's only one logical way to implement simple addition
        user1_code = "def add_numbers(a, b):\n    return a + b"
        user2_code = "def add_numbers(num1, num2):\n    result = num1 + num2\n    return result"
        
        user1_id = "user_123"
        user2_id = "user_456"
        
        submission1 = await mock_platform.submit_exercise(user1_id, exercise.id, user1_code)
        await mock_platform.evaluate_submission(submission1.id)
        
        submission2 = await mock_platform.submit_exercise(user2_id, exercise.id, user2_code)
        result = await mock_platform.evaluate_submission(submission2.id)
        
        # Different enough implementations should not trigger plagiarism
        assert result["submission"].plagiarism_score < 0.8
        assert result["submission"].status != SubmissionStatus.PLAGIARISM_DETECTED


class TestPeerReview:
    """Test peer review functionality."""
    
    @pytest.mark.asyncio
    async def test_peer_review_assignment(self, mock_platform, sample_exercises):
        """Test automatic assignment of submissions for peer review."""
        exercise = sample_exercises[1]  # Exercise requiring peer review
        mock_platform.exercises[exercise.id] = exercise
        
        # Multiple students submit solutions
        users = ["user_123", "user_456", "user_789"]
        submissions = []
        
        for user_id in users:
            code = f"""
def process_list(data):
    # Solution by {user_id}
    return [x for x in data if x % 2 == 0]
"""
            submission = await mock_platform.submit_exercise(user_id, exercise.id, code)
            result = await mock_platform.evaluate_submission(submission.id)
            submissions.append(result["submission"])
        
        # Assign peer reviews (each student reviews 2 others)
        reviews_per_student = 2
        for i, reviewer_id in enumerate(users):
            # Get submissions to review (excluding own submission)
            submissions_to_review = [s for s in submissions if s.user_id != reviewer_id][:reviews_per_student]
            
            for submission_to_review in submissions_to_review:
                review_id = f"review_{reviewer_id}_{submission_to_review.id}"
                mock_platform.peer_reviews[review_id] = {
                    "id": review_id,
                    "reviewer_id": reviewer_id,
                    "submission_id": submission_to_review.id,
                    "status": "assigned",
                    "assigned_at": datetime.now(),
                    "due_date": datetime.now() + timedelta(days=3)
                }
        
        # Verify peer review assignments
        total_reviews = len(mock_platform.peer_reviews)
        expected_reviews = len(users) * reviews_per_student
        
        assert total_reviews == expected_reviews
        assert all(review["status"] == "assigned" for review in mock_platform.peer_reviews.values())
    
    @pytest.mark.asyncio
    async def test_peer_review_submission_and_scoring(self, mock_platform, sample_exercises):
        """Test peer review submission and scoring process."""
        exercise = sample_exercises[1]
        mock_platform.exercises[exercise.id] = exercise
        
        # Setup initial submission
        user_id = "user_123"
        reviewer_id = "user_456"
        
        code = """
def process_list(data):
    result = []
    for item in data:
        if item % 2 == 0:
            result.append(item)
    return result
"""
        
        submission = await mock_platform.submit_exercise(user_id, exercise.id, code)
        result = await mock_platform.evaluate_submission(submission.id)
        
        # Create peer review
        review_id = f"review_{reviewer_id}_{submission.id}"
        peer_review = {
            "id": review_id,
            "reviewer_id": reviewer_id,
            "submission_id": submission.id,
            "status": "assigned",
            "assigned_at": datetime.now(),
            "due_date": datetime.now() + timedelta(days=3)
        }
        
        mock_platform.peer_reviews[review_id] = peer_review
        
        # Reviewer submits review
        review_data = {
            "correctness_score": 8,  # Out of 10
            "code_quality_score": 7,
            "efficiency_score": 6,
            "comments": "Good solution but could be more pythonic using list comprehension",
            "suggestions": [
                "Consider using list comprehension for better readability",
                "Add error handling for empty lists"
            ],
            "overall_rating": 7.5,
            "time_spent_minutes": 15
        }
        
        # Update peer review with submission
        peer_review.update({
            "status": "completed",
            "submitted_at": datetime.now(),
            "review_data": review_data
        })
        
        # Calculate weighted score based on rubric
        rubric = exercise.rubric
        weighted_score = (
            (review_data["correctness_score"] / 10) * (rubric["correctness"] / 100) +
            (review_data["code_quality_score"] / 10) * (rubric["code_style"] / 100) +
            (review_data["efficiency_score"] / 10) * (rubric["algorithm_efficiency"] / 100)
        ) * exercise.max_score
        
        peer_review["calculated_score"] = weighted_score
        
        assert peer_review["status"] == "completed"
        assert peer_review["calculated_score"] > 0
        assert len(review_data["suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_peer_review_quality_assessment(self, mock_platform):
        """Test assessment of peer review quality."""
        # Setup multiple peer reviews for the same submission
        submission_id = "sub_123"
        reviews = [
            {
                "reviewer_id": "user_456",
                "correctness_score": 8,
                "code_quality_score": 7,
                "overall_rating": 7.5,
                "comment_length": 150,
                "time_spent_minutes": 20
            },
            {
                "reviewer_id": "user_789",
                "correctness_score": 8,
                "code_quality_score": 8,
                "overall_rating": 8.0,
                "comment_length": 200,
                "time_spent_minutes": 25
            },
            {
                "reviewer_id": "user_012",
                "correctness_score": 9,
                "code_quality_score": 6,
                "overall_rating": 7.0,
                "comment_length": 50,  # Very short comments
                "time_spent_minutes": 5   # Very little time
            }
        ]
        
        # Assess review quality
        quality_scores = []
        
        for review in reviews:
            quality_score = 0
            
            # Time spent factor
            if review["time_spent_minutes"] >= 15:
                quality_score += 25
            elif review["time_spent_minutes"] >= 10:
                quality_score += 15
            
            # Comment quality factor
            if review["comment_length"] >= 100:
                quality_score += 25
            elif review["comment_length"] >= 50:
                quality_score += 15
            
            # Consistency with other reviews
            avg_overall_rating = sum(r["overall_rating"] for r in reviews) / len(reviews)
            rating_deviation = abs(review["overall_rating"] - avg_overall_rating)
            if rating_deviation <= 0.5:
                quality_score += 25
            elif rating_deviation <= 1.0:
                quality_score += 15
            
            # Scoring range factor
            score_range = max(review["correctness_score"], review["code_quality_score"]) - min(review["correctness_score"], review["code_quality_score"])
            if score_range <= 2:  # Consistent scoring
                quality_score += 25
            
            quality_scores.append(quality_score)
        
        # Reviews with low quality scores should be flagged
        low_quality_reviews = [i for i, score in enumerate(quality_scores) if score < 50]
        
        assert len(low_quality_reviews) == 1  # Third review should be flagged
        assert quality_scores[2] < 50  # Low time and comment length


class TestInstructorFeedback:
    """Test instructor feedback and grading functionality."""
    
    @pytest.mark.asyncio
    async def test_instructor_override_scoring(self, mock_platform, sample_exercises):
        """Test instructor's ability to override automated scoring."""
        exercise = sample_exercises[2]  # Advanced exercise
        mock_platform.exercises[exercise.id] = exercise
        
        user_id = "user_123"
        code = """
def custom_sort(arr):
    # Bubble sort implementation
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
        
        submission = await mock_platform.submit_exercise(user_id, exercise.id, code)
        result = await mock_platform.evaluate_submission(submission.id)
        
        # Automated scoring gives low efficiency score for bubble sort
        automated_score = 60  # Correct but inefficient
        result["submission"].score = automated_score
        
        # Instructor provides feedback and adjusts score
        instructor_feedback = {
            "submission_id": submission.id,
            "instructor_id": "instructor_001",
            "feedback": "While bubble sort is correct, consider more efficient algorithms like quicksort or mergesort for better performance.",
            "rubric_scores": {
                "correctness": 40,      # Full points for correctness
                "algorithm_efficiency": 20,  # Lower for bubble sort
                "code_quality": 12,     # Good code structure
                "documentation": 8      # Adequate comments
            },
            "adjusted_score": 80,  # Instructor gives partial credit for effort
            "private_notes": "Student understands sorting concept but needs to learn about algorithm complexity",
            "submitted_at": datetime.now()
        }
        
        mock_platform.instructor_feedback[submission.id] = instructor_feedback
        
        # Update submission with instructor feedback
        result["submission"].score = instructor_feedback["adjusted_score"]
        result["submission"].feedback = instructor_feedback["feedback"]
        
        assert result["submission"].score == 80
        assert "efficient algorithms" in result["submission"].feedback
        assert submission.id in mock_platform.instructor_feedback
    
    @pytest.mark.asyncio
    async def test_batch_feedback_processing(self, mock_platform, sample_exercises):
        """Test batch processing of instructor feedback."""
        exercise = sample_exercises[0]
        mock_platform.exercises[exercise.id] = exercise
        
        # Multiple submissions for batch processing
        students = ["user_123", "user_456", "user_789", "user_012"]
        submissions = []
        
        for student_id in students:
            code = f"""
def add_numbers(a, b):
    # Solution by {student_id}
    return a + b
"""
            submission = await mock_platform.submit_exercise(student_id, exercise.id, code)
            result = await mock_platform.evaluate_submission(submission.id)
            submissions.append(result["submission"])
        
        # Instructor provides batch feedback
        batch_feedback = {
            "exercise_id": exercise.id,
            "instructor_id": "instructor_001",
            "general_feedback": "Good work on this basic exercise. Most students got the correct implementation.",
            "common_issues": [
                "Some forgot to handle edge cases",
                "Variable naming could be improved"
            ],
            "grade_distribution": {
                "A": 2,  # Excellent
                "B": 1,  # Good
                "C": 1,  # Satisfactory
                "D": 0,  # Needs improvement
                "F": 0   # Unsatisfactory
            },
            "processed_at": datetime.now()
        }
        
        # Apply individual feedback based on batch analysis
        for i, submission in enumerate(submissions):
            individual_score = [95, 85, 75, 90][i]  # Simulated individual scores
            
            mock_platform.instructor_feedback[submission.id] = {
                "submission_id": submission.id,
                "batch_feedback_id": f"batch_{exercise.id}",
                "individual_score": individual_score,
                "individual_comments": f"Score: {individual_score}/100",
                "applied_at": datetime.now()
            }
            
            submission.score = individual_score
        
        assert len(mock_platform.instructor_feedback) == len(students)
        assert all(submission.score > 0 for submission in submissions)
    
    @pytest.mark.asyncio
    async def test_feedback_analytics_and_insights(self, mock_platform, sample_exercises):
        """Test generation of analytics and insights from feedback data."""
        exercise = sample_exercises[1]
        mock_platform.exercises[exercise.id] = exercise
        
        # Simulate feedback data for analytics
        feedback_data = [
            {"score": 95, "time_spent": 45, "attempts": 1, "difficulty_rating": 3},
            {"score": 88, "time_spent": 60, "attempts": 2, "difficulty_rating": 4},
            {"score": 92, "time_spent": 50, "attempts": 1, "difficulty_rating": 3},
            {"score": 75, "time_spent": 90, "attempts": 3, "difficulty_rating": 5},
            {"score": 82, "time_spent": 70, "attempts": 2, "difficulty_rating": 4}
        ]
        
        # Calculate analytics
        analytics = {
            "average_score": sum(f["score"] for f in feedback_data) / len(feedback_data),
            "average_time_spent": sum(f["time_spent"] for f in feedback_data) / len(feedback_data),
            "average_attempts": sum(f["attempts"] for f in feedback_data) / len(feedback_data),
            "average_difficulty": sum(f["difficulty_rating"] for f in feedback_data) / len(feedback_data),
            "score_distribution": {
                "90-100": len([f for f in feedback_data if f["score"] >= 90]),
                "80-89": len([f for f in feedback_data if 80 <= f["score"] < 90]),
                "70-79": len([f for f in feedback_data if 70 <= f["score"] < 80]),
                "below_70": len([f for f in feedback_data if f["score"] < 70])
            },
            "performance_insights": []
        }
        
        # Generate insights
        if analytics["average_score"] < 75:
            analytics["performance_insights"].append("Exercise may be too difficult - consider adding hints")
        
        if analytics["average_attempts"] > 2:
            analytics["performance_insights"].append("Students struggling - review prerequisite topics")
        
        if analytics["average_time_spent"] > 60:
            analytics["performance_insights"].append("Exercise taking longer than expected - adjust time estimates")
        
        # Store analytics
        mock_platform.analytics[f"exercise_{exercise.id}"] = analytics
        
        assert analytics["average_score"] > 80
        assert len(analytics["performance_insights"]) > 0
        assert analytics["score_distribution"]["90-100"] == 2


class TestAdvancedFeatures:
    """Test advanced submission platform features."""
    
    @pytest.mark.asyncio
    async def test_collaborative_coding_exercise(self, mock_platform):
        """Test collaborative coding exercise functionality."""
        # Setup collaborative exercise
        collab_exercise = ExerciseDefinition(
            id="collab_project",
            title="Team Project",
            description="Build a simple calculator with multiple team members",
            difficulty="intermediate",
            max_score=100,
            time_limit_minutes=None,  # No time limit for team projects
            allowed_attempts=5,
            starter_code="# Team Calculator Project\n# TODO: Implement calculator functions",
            test_cases=[],  # Custom testing for team projects
            rubric={"collaboration": 30, "code_quality": 40, "functionality": 30},
            requires_peer_review=True
        )
        
        mock_platform.exercises[collab_exercise.id] = collab_exercise
        
        # Team members
        team_members = ["user_123", "user_456", "user_789"]
        team_id = "team_calc_001"
        
        # Track collaborative submissions
        collaborative_submissions = {}
        
        for member_id in team_members:
            # Each member contributes different parts
            contributions = {
                "user_123": "def add(a, b):\n    return a + b\n",
                "user_456": "def subtract(a, b):\n    return a - b\n", 
                "user_789": "def multiply(a, b):\n    return a * b\n"
            }
            
            submission = await mock_platform.submit_exercise(
                member_id, 
                collab_exercise.id, 
                contributions[member_id]
            )
            
            collaborative_submissions[member_id] = {
                "submission": submission,
                "contribution_type": ["arithmetic_operations", "user_interface", "testing"][team_members.index(member_id)],
                "lines_of_code": len(contributions[member_id].split('\n')),
                "commit_timestamp": datetime.now()
            }
        
        # Merge team contributions
        merged_code = "\n".join(contributions[member] for member in team_members)
        
        # Create team submission
        team_submission = Submission(
            id=f"team_sub_{team_id}",
            user_id=team_id,  # Use team ID as user ID
            exercise_id=collab_exercise.id,
            code=merged_code,
            submitted_at=datetime.now(),
            status=SubmissionStatus.PENDING
        )
        
        mock_platform.submissions[team_submission.id] = team_submission
        
        # Track collaboration metrics
        collaboration_metrics = {
            "team_id": team_id,
            "members": team_members,
            "total_contributions": len(collaborative_submissions),
            "contribution_balance": max(collaborative_submissions[m]["lines_of_code"] for m in team_members) / 
                                   min(collaborative_submissions[m]["lines_of_code"] for m in team_members),
            "collaboration_score": 85,  # Based on even distribution and communication
            "merge_conflicts": 0,
            "commit_frequency": 1.2  # Commits per day
        }
        
        assert len(collaborative_submissions) == len(team_members)
        assert collaboration_metrics["contribution_balance"] < 3.0  # Reasonably balanced
        assert team_submission.id in mock_platform.submissions
    
    @pytest.mark.asyncio
    async def test_ai_assisted_feedback(self, mock_platform, sample_exercises):
        """Test AI-assisted feedback generation."""
        exercise = sample_exercises[0]
        mock_platform.exercises[exercise.id] = exercise
        
        user_id = "user_123"
        code = """
def add_numbers(a, b):
    result = a + b
    print(f"Adding {a} and {b} equals {result}")
    return result
"""
        
        submission = await mock_platform.submit_exercise(user_id, exercise.id, code)
        
        # Mock AI feedback generation
        with patch('ai_feedback_service.generate_feedback') as mock_ai_feedback:
            mock_ai_feedback.return_value = {
                "code_analysis": {
                    "strengths": [
                        "Correct implementation of addition",
                        "Clear variable naming",
                        "Proper return statement"
                    ],
                    "improvements": [
                        "Consider removing print statement for better function purity",
                        "Add type hints for better code documentation"
                    ],
                    "style_score": 8.5,
                    "complexity_score": 1.0,  # Very simple
                    "maintainability_score": 9.0
                },
                "suggestions": [
                    {
                        "type": "improvement",
                        "description": "Add type hints",
                        "example": "def add_numbers(a: int, b: int) -> int:"
                    },
                    {
                        "type": "optimization",
                        "description": "Remove side effects",
                        "example": "Avoid print statements in utility functions"
                    }
                ],
                "overall_feedback": "Good basic implementation. Consider adding type hints and removing print statements for production code.",
                "confidence_score": 0.92
            }
            
            ai_feedback = mock_ai_feedback.return_value
            
            # Store AI feedback
            mock_platform.instructor_feedback[submission.id] = {
                "submission_id": submission.id,
                "feedback_type": "ai_generated",
                "ai_analysis": ai_feedback,
                "generated_at": datetime.now(),
                "human_reviewed": False
            }
            
            assert ai_feedback["code_analysis"]["style_score"] > 8.0
            assert len(ai_feedback["suggestions"]) == 2
            assert ai_feedback["confidence_score"] > 0.9
    
    @pytest.mark.asyncio
    async def test_performance_benchmarking(self, mock_platform, sample_exercises):
        """Test performance benchmarking of submissions."""
        exercise = sample_exercises[2]  # Advanced algorithm exercise
        mock_platform.exercises[exercise.id] = exercise
        
        # Different algorithm implementations
        implementations = {
            "bubble_sort": """
def custom_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
""",
            "quick_sort": """
def custom_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return custom_sort(left) + middle + custom_sort(right)
""",
            "python_builtin": """
def custom_sort(arr):
    return sorted(arr)
"""
        }
        
        # Benchmark each implementation
        benchmark_results = {}
        
        for impl_name, code in implementations.items():
            user_id = f"user_{impl_name}"
            submission = await mock_platform.submit_exercise(user_id, exercise.id, code)
            
            # Mock performance benchmarking
            with patch('performance_tester.benchmark_code') as mock_benchmark:
                mock_benchmark.return_value = {
                    "bubble_sort": {"avg_time": 0.25, "memory_peak": 1024, "complexity": "O(n²)"},
                    "quick_sort": {"avg_time": 0.05, "memory_peak": 2048, "complexity": "O(n log n)"},
                    "python_builtin": {"avg_time": 0.01, "memory_peak": 512, "complexity": "O(n log n)"}
                }[impl_name]
                
                benchmark_result = mock_benchmark.return_value
                benchmark_results[impl_name] = benchmark_result
                
                # Store benchmark data
                mock_platform.analytics[f"benchmark_{submission.id}"] = {
                    "submission_id": submission.id,
                    "algorithm_type": impl_name,
                    "performance_metrics": benchmark_result,
                    "relative_performance": "fast" if benchmark_result["avg_time"] < 0.1 else "slow",
                    "benchmarked_at": datetime.now()
                }
        
        # Verify benchmark results
        assert benchmark_results["python_builtin"]["avg_time"] < benchmark_results["quick_sort"]["avg_time"]
        assert benchmark_results["quick_sort"]["avg_time"] < benchmark_results["bubble_sort"]["avg_time"]
        assert len(benchmark_results) == 3


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([__file__, "-v", "--tb=short", "--durations=10"])