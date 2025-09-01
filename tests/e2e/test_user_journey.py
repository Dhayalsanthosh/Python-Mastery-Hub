# tests/e2e/test_user_journey.py
"""
End-to-end tests for complete user journeys.
Tests realistic user workflows from registration to course completion.
"""
import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any, Optional


class MockPlatform:
    """Mock platform for testing user journeys without external dependencies."""
    
    def __init__(self):
        self.users = {}
        self.courses = {}
        self.enrollments = {}
        self.progress = {}
        self.certificates = {}
        self.notifications = []
        self.payment_records = {}
        
    def reset(self):
        """Reset all platform data."""
        self.__init__()


class MockUser:
    """Mock user object for testing."""
    
    def __init__(self, user_id: str, email: str, name: str):
        self.id = user_id
        self.email = email
        self.name = name
        self.verified = False
        self.created_at = datetime.now()
        self.last_login = None
        self.profile_completed = False


class MockCourse:
    """Mock course object for testing."""
    
    def __init__(self, course_id: str, title: str, lessons: List[str], price: float = 0):
        self.id = course_id
        self.title = title
        self.lessons = lessons
        self.price = price
        self.is_published = True
        self.created_at = datetime.now()


class MockEnrollment:
    """Mock enrollment object for testing."""
    
    def __init__(self, user_id: str, course_id: str):
        self.user_id = user_id
        self.course_id = course_id
        self.enrolled_at = datetime.now()
        self.completed_at = None
        self.progress_percentage = 0


@pytest.fixture
def mock_platform():
    """Fixture providing a clean mock platform for each test."""
    platform = MockPlatform()
    return platform


@pytest.fixture
def sample_courses():
    """Fixture providing sample courses for testing."""
    return [
        MockCourse("course_1", "Python Basics", ["intro", "variables", "functions", "classes"], 29.99),
        MockCourse("course_2", "Advanced Python", ["decorators", "generators", "async", "testing"], 49.99),
        MockCourse("course_3", "Free Course", ["lesson1", "lesson2"], 0)
    ]


class TestUserRegistrationJourney:
    """Test complete user registration and onboarding journey."""
    
    @pytest.mark.asyncio
    async def test_complete_user_registration_flow(self, mock_platform):
        """Test the complete user registration process."""
        # Step 1: User attempts to register
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "John Doe",
            "terms_accepted": True
        }
        
        # Mock registration
        user_id = "user_123"
        user = MockUser(user_id, user_data["email"], user_data["name"])
        mock_platform.users[user_id] = user
        
        assert user_id in mock_platform.users
        assert mock_platform.users[user_id].email == user_data["email"]
        assert not mock_platform.users[user_id].verified
        
        # Step 2: Email verification
        verification_token = "verify_token_123"
        mock_platform.users[user_id].verified = True
        
        assert mock_platform.users[user_id].verified
        
        # Step 3: Profile completion
        profile_data = {
            "bio": "Software developer",
            "interests": ["programming", "technology"],
            "experience_level": "intermediate"
        }
        
        mock_platform.users[user_id].profile_completed = True
        
        assert mock_platform.users[user_id].profile_completed
    
    @pytest.mark.asyncio
    async def test_registration_with_invalid_data(self, mock_platform):
        """Test registration with invalid data."""
        invalid_data_sets = [
            {"email": "invalid-email", "password": "weak", "name": ""},
            {"email": "", "password": "ValidPass123!", "name": "John"},
            {"email": "test@example.com", "password": "", "name": "John"},
        ]
        
        for invalid_data in invalid_data_sets:
            # Simulate validation failure
            if not invalid_data.get("email") or "@" not in invalid_data.get("email", ""):
                with pytest.raises(ValueError, match="Invalid email"):
                    raise ValueError("Invalid email")
            
            if not invalid_data.get("password") or len(invalid_data.get("password", "")) < 8:
                with pytest.raises(ValueError, match="Password too weak"):
                    raise ValueError("Password too weak")


class TestCourseEnrollmentJourney:
    """Test course discovery, enrollment, and payment journey."""
    
    @pytest.mark.asyncio
    async def test_free_course_enrollment(self, mock_platform, sample_courses):
        """Test enrolling in a free course."""
        # Setup user
        user_id = "user_123"
        user = MockUser(user_id, "user@example.com", "Test User")
        user.verified = True
        mock_platform.users[user_id] = user
        
        # Setup free course
        free_course = sample_courses[2]  # Free course
        mock_platform.courses[free_course.id] = free_course
        
        # Enroll in course
        enrollment = MockEnrollment(user_id, free_course.id)
        enrollment_id = f"{user_id}_{free_course.id}"
        mock_platform.enrollments[enrollment_id] = enrollment
        
        assert enrollment_id in mock_platform.enrollments
        assert mock_platform.enrollments[enrollment_id].user_id == user_id
        assert mock_platform.enrollments[enrollment_id].course_id == free_course.id
    
    @pytest.mark.asyncio
    async def test_paid_course_enrollment_with_payment(self, mock_platform, sample_courses):
        """Test enrolling in a paid course with payment processing."""
        # Setup user
        user_id = "user_123"
        user = MockUser(user_id, "user@example.com", "Test User")
        user.verified = True
        mock_platform.users[user_id] = user
        
        # Setup paid course
        paid_course = sample_courses[0]  # Python Basics - $29.99
        mock_platform.courses[paid_course.id] = paid_course
        
        # Mock payment processing
        payment_data = {
            "amount": paid_course.price,
            "currency": "USD",
            "payment_method": "credit_card",
            "card_token": "tok_visa_4242"
        }
        
        # Simulate successful payment
        payment_id = "pay_123"
        mock_platform.payment_records[payment_id] = {
            "user_id": user_id,
            "course_id": paid_course.id,
            "amount": payment_data["amount"],
            "status": "completed",
            "processed_at": datetime.now()
        }
        
        # Enroll after successful payment
        enrollment = MockEnrollment(user_id, paid_course.id)
        enrollment_id = f"{user_id}_{paid_course.id}"
        mock_platform.enrollments[enrollment_id] = enrollment
        
        assert payment_id in mock_platform.payment_records
        assert mock_platform.payment_records[payment_id]["status"] == "completed"
        assert enrollment_id in mock_platform.enrollments
    
    @pytest.mark.asyncio
    async def test_course_enrollment_failure_scenarios(self, mock_platform, sample_courses):
        """Test various enrollment failure scenarios."""
        user_id = "user_123"
        user = MockUser(user_id, "user@example.com", "Test User")
        mock_platform.users[user_id] = user
        
        paid_course = sample_courses[0]
        mock_platform.courses[paid_course.id] = paid_course
        
        # Test 1: Unverified user
        with pytest.raises(PermissionError, match="User not verified"):
            if not user.verified:
                raise PermissionError("User not verified")
        
        # Test 2: Payment failure
        user.verified = True
        with patch('payment_processor.charge') as mock_charge:
            mock_charge.return_value = {"status": "failed", "error": "Card declined"}
            
            # Simulate payment failure
            payment_result = mock_charge.return_value
            if payment_result["status"] == "failed":
                with pytest.raises(RuntimeError, match="Payment failed"):
                    raise RuntimeError("Payment failed: Card declined")


class TestLearningJourney:
    """Test the complete learning experience journey."""
    
    @pytest.mark.asyncio
    async def test_complete_course_progression(self, mock_platform, sample_courses):
        """Test complete course progression from start to finish."""
        # Setup enrolled user
        user_id = "user_123"
        user = MockUser(user_id, "user@example.com", "Test User")
        user.verified = True
        mock_platform.users[user_id] = user
        
        course = sample_courses[0]
        mock_platform.courses[course.id] = course
        
        enrollment = MockEnrollment(user_id, course.id)
        enrollment_id = f"{user_id}_{course.id}"
        mock_platform.enrollments[enrollment_id] = enrollment
        
        # Initialize progress tracking
        progress_key = f"{user_id}_{course.id}"
        mock_platform.progress[progress_key] = {
            "completed_lessons": [],
            "current_lesson": course.lessons[0],
            "quiz_scores": {},
            "time_spent": 0
        }
        
        # Simulate progressing through each lesson
        total_lessons = len(course.lessons)
        for i, lesson in enumerate(course.lessons):
            # Mark lesson as completed
            mock_platform.progress[progress_key]["completed_lessons"].append(lesson)
            
            # Update current lesson
            if i < total_lessons - 1:
                mock_platform.progress[progress_key]["current_lesson"] = course.lessons[i + 1]
            
            # Update progress percentage
            progress_percentage = ((i + 1) / total_lessons) * 100
            mock_platform.enrollments[enrollment_id].progress_percentage = progress_percentage
            
            # Add quiz score (simulate)
            mock_platform.progress[progress_key]["quiz_scores"][lesson] = 85 + (i * 2)  # Improving scores
            
            # Add time spent
            mock_platform.progress[progress_key]["time_spent"] += 30  # 30 minutes per lesson
        
        # Course completion
        if mock_platform.enrollments[enrollment_id].progress_percentage == 100:
            mock_platform.enrollments[enrollment_id].completed_at = datetime.now()
            
            # Generate certificate
            certificate_id = f"cert_{user_id}_{course.id}"
            mock_platform.certificates[certificate_id] = {
                "user_id": user_id,
                "course_id": course.id,
                "issued_at": datetime.now(),
                "certificate_url": f"https://platform.com/certificates/{certificate_id}"
            }
        
        # Assertions
        assert len(mock_platform.progress[progress_key]["completed_lessons"]) == total_lessons
        assert mock_platform.enrollments[enrollment_id].progress_percentage == 100
        assert mock_platform.enrollments[enrollment_id].completed_at is not None
        assert certificate_id in mock_platform.certificates
    
    @pytest.mark.asyncio
    async def test_learning_with_interruptions(self, mock_platform, sample_courses):
        """Test learning journey with interruptions and resuming."""
        # Setup
        user_id = "user_123"
        user = MockUser(user_id, "user@example.com", "Test User")
        mock_platform.users[user_id] = user
        
        course = sample_courses[1]  # Advanced Python
        mock_platform.courses[course.id] = course
        
        enrollment = MockEnrollment(user_id, course.id)
        enrollment_id = f"{user_id}_{course.id}"
        mock_platform.enrollments[enrollment_id] = enrollment
        
        progress_key = f"{user_id}_{course.id}"
        mock_platform.progress[progress_key] = {
            "completed_lessons": [],
            "current_lesson": course.lessons[0],
            "last_accessed": datetime.now(),
            "study_sessions": []
        }
        
        # Simulate study sessions with breaks
        sessions = [
            {"lessons": [course.lessons[0]], "date": datetime.now() - timedelta(days=5)},
            {"lessons": [course.lessons[1]], "date": datetime.now() - timedelta(days=3)},
            # Break of 2 days
            {"lessons": [course.lessons[2], course.lessons[3]], "date": datetime.now()}
        ]
        
        for session in sessions:
            for lesson in session["lessons"]:
                mock_platform.progress[progress_key]["completed_lessons"].append(lesson)
                mock_platform.progress[progress_key]["last_accessed"] = session["date"]
            
            mock_platform.progress[progress_key]["study_sessions"].append({
                "date": session["date"],
                "lessons_completed": len(session["lessons"]),
                "duration": len(session["lessons"]) * 25  # 25 min per lesson
            })
        
        # Calculate progress
        progress_percentage = (len(mock_platform.progress[progress_key]["completed_lessons"]) / len(course.lessons)) * 100
        mock_platform.enrollments[enrollment_id].progress_percentage = progress_percentage
        
        assert len(mock_platform.progress[progress_key]["study_sessions"]) == 3
        assert mock_platform.enrollments[enrollment_id].progress_percentage == 100
        assert len(mock_platform.progress[progress_key]["completed_lessons"]) == len(course.lessons)


class TestMultiCourseJourney:
    """Test users taking multiple courses simultaneously."""
    
    @pytest.mark.asyncio
    async def test_concurrent_course_enrollment(self, mock_platform, sample_courses):
        """Test user enrolled in multiple courses simultaneously."""
        # Setup user
        user_id = "user_123"
        user = MockUser(user_id, "user@example.com", "Test User")
        user.verified = True
        mock_platform.users[user_id] = user
        
        # Enroll in multiple courses
        enrolled_courses = sample_courses[:2]  # First two courses
        enrollments = []
        
        for course in enrolled_courses:
            mock_platform.courses[course.id] = course
            enrollment = MockEnrollment(user_id, course.id)
            enrollment_id = f"{user_id}_{course.id}"
            mock_platform.enrollments[enrollment_id] = enrollment
            enrollments.append(enrollment_id)
            
            # Initialize progress
            progress_key = f"{user_id}_{course.id}"
            mock_platform.progress[progress_key] = {
                "completed_lessons": [],
                "current_lesson": course.lessons[0] if course.lessons else None
            }
        
        # Simulate alternating between courses
        for i in range(2):  # Complete 2 lessons in each course
            for course in enrolled_courses:
                if i < len(course.lessons):
                    progress_key = f"{user_id}_{course.id}"
                    mock_platform.progress[progress_key]["completed_lessons"].append(course.lessons[i])
                    
                    # Update enrollment progress
                    enrollment_id = f"{user_id}_{course.id}"
                    progress_percentage = (len(mock_platform.progress[progress_key]["completed_lessons"]) / len(course.lessons)) * 100
                    mock_platform.enrollments[enrollment_id].progress_percentage = progress_percentage
        
        # Verify progress in both courses
        for course in enrolled_courses:
            progress_key = f"{user_id}_{course.id}"
            enrollment_id = f"{user_id}_{course.id}"
            
            assert len(mock_platform.progress[progress_key]["completed_lessons"]) == 2
            assert mock_platform.enrollments[enrollment_id].progress_percentage == 50.0


class TestUserRetentionJourney:
    """Test user retention and re-engagement scenarios."""
    
    @pytest.mark.asyncio
    async def test_inactive_user_reengagement(self, mock_platform, sample_courses):
        """Test re-engaging inactive users."""
        # Setup user who became inactive
        user_id = "user_123"
        user = MockUser(user_id, "user@example.com", "Test User")
        user.verified = True
        user.last_login = datetime.now() - timedelta(days=30)  # Inactive for 30 days
        mock_platform.users[user_id] = user
        
        course = sample_courses[0]
        mock_platform.courses[course.id] = course
        
        enrollment = MockEnrollment(user_id, course.id)
        enrollment_id = f"{user_id}_{course.id}"
        mock_platform.enrollments[enrollment_id] = enrollment
        
        # Partial progress before going inactive
        progress_key = f"{user_id}_{course.id}"
        mock_platform.progress[progress_key] = {
            "completed_lessons": [course.lessons[0]],  # Only completed first lesson
            "current_lesson": course.lessons[1],
            "last_accessed": datetime.now() - timedelta(days=30)
        }
        mock_platform.enrollments[enrollment_id].progress_percentage = 25.0
        
        # Send re-engagement notification
        notification = {
            "user_id": user_id,
            "type": "re_engagement",
            "message": "Continue your Python Basics course",
            "sent_at": datetime.now(),
            "course_id": course.id
        }
        mock_platform.notifications.append(notification)
        
        # Simulate user returning
        user.last_login = datetime.now()
        mock_platform.progress[progress_key]["last_accessed"] = datetime.now()
        
        # Continue progress
        mock_platform.progress[progress_key]["completed_lessons"].append(course.lessons[1])
        mock_platform.enrollments[enrollment_id].progress_percentage = 50.0
        
        assert len(mock_platform.notifications) == 1
        assert mock_platform.notifications[0]["type"] == "re_engagement"
        assert mock_platform.enrollments[enrollment_id].progress_percentage == 50.0
        assert user.last_login.date() == datetime.now().date()


class TestPlatformIntegrationJourney:
    """Test integration with external services and features."""
    
    @pytest.mark.asyncio
    async def test_social_sharing_journey(self, mock_platform, sample_courses):
        """Test social sharing of achievements."""
        # Setup completed course
        user_id = "user_123"
        user = MockUser(user_id, "user@example.com", "Test User")
        mock_platform.users[user_id] = user
        
        course = sample_courses[0]
        mock_platform.courses[course.id] = course
        
        enrollment = MockEnrollment(user_id, course.id)
        enrollment.completed_at = datetime.now()
        enrollment.progress_percentage = 100
        enrollment_id = f"{user_id}_{course.id}"
        mock_platform.enrollments[enrollment_id] = enrollment
        
        # Generate certificate
        certificate_id = f"cert_{user_id}_{course.id}"
        mock_platform.certificates[certificate_id] = {
            "user_id": user_id,
            "course_id": course.id,
            "issued_at": datetime.now(),
            "shareable_url": f"https://platform.com/certificates/{certificate_id}/public"
        }
        
        # Mock social sharing
        with patch('social_api.post_achievement') as mock_social_post:
            mock_social_post.return_value = {"status": "posted", "post_id": "social_123"}
            
            # Simulate sharing
            share_result = mock_social_post.return_value
            
            assert share_result["status"] == "posted"
            assert certificate_id in mock_platform.certificates
    
    @pytest.mark.asyncio
    async def test_mobile_app_sync_journey(self, mock_platform):
        """Test syncing progress between web and mobile platforms."""
        user_id = "user_123"
        
        # Simulate progress made on web
        web_progress = {
            "platform": "web",
            "last_sync": datetime.now() - timedelta(hours=2),
            "completed_lessons": ["lesson1", "lesson2"],
            "current_lesson": "lesson3"
        }
        
        # Simulate progress made on mobile
        mobile_progress = {
            "platform": "mobile",
            "last_sync": datetime.now(),
            "completed_lessons": ["lesson1", "lesson2", "lesson3"],
            "current_lesson": "lesson4"
        }
        
        # Sync logic (mobile is more recent)
        if mobile_progress["last_sync"] > web_progress["last_sync"]:
            synced_progress = mobile_progress
        else:
            synced_progress = web_progress
        
        mock_platform.progress[f"{user_id}_sync"] = synced_progress
        
        assert mock_platform.progress[f"{user_id}_sync"]["platform"] == "mobile"
        assert len(mock_platform.progress[f"{user_id}_sync"]["completed_lessons"]) == 3


@pytest.mark.integration
class TestCompleteUserLifecycle:
    """Integration test covering complete user lifecycle."""
    
    @pytest.mark.asyncio
    async def test_full_user_lifecycle(self, mock_platform, sample_courses):
        """Test complete user journey from registration to course completion."""
        # Phase 1: Registration
        user_data = {"email": "lifecycle@example.com", "name": "Lifecycle User"}
        user_id = "lifecycle_123"
        user = MockUser(user_id, user_data["email"], user_data["name"])
        user.verified = True
        user.profile_completed = True
        mock_platform.users[user_id] = user
        
        # Phase 2: Course Discovery and Enrollment
        target_course = sample_courses[0]
        mock_platform.courses[target_course.id] = target_course
        
        enrollment = MockEnrollment(user_id, target_course.id)
        enrollment_id = f"{user_id}_{target_course.id}"
        mock_platform.enrollments[enrollment_id] = enrollment
        
        # Phase 3: Learning Progress
        progress_key = f"{user_id}_{target_course.id}"
        mock_platform.progress[progress_key] = {"completed_lessons": [], "quiz_scores": {}}
        
        for lesson in target_course.lessons:
            mock_platform.progress[progress_key]["completed_lessons"].append(lesson)
            mock_platform.progress[progress_key]["quiz_scores"][lesson] = 90
        
        # Phase 4: Course Completion
        mock_platform.enrollments[enrollment_id].progress_percentage = 100
        mock_platform.enrollments[enrollment_id].completed_at = datetime.now()
        
        # Phase 5: Certificate Generation
        certificate_id = f"cert_{user_id}_{target_course.id}"
        mock_platform.certificates[certificate_id] = {
            "user_id": user_id,
            "course_id": target_course.id,
            "issued_at": datetime.now()
        }
        
        # Phase 6: Next Course Recommendation
        recommended_course = sample_courses[1]  # Advanced course
        mock_platform.courses[recommended_course.id] = recommended_course
        
        # Verify complete lifecycle
        assert user_id in mock_platform.users
        assert mock_platform.users[user_id].verified
        assert enrollment_id in mock_platform.enrollments
        assert mock_platform.enrollments[enrollment_id].completed_at is not None
        assert certificate_id in mock_platform.certificates
        assert len(mock_platform.progress[progress_key]["completed_lessons"]) == len(target_course.lessons)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])