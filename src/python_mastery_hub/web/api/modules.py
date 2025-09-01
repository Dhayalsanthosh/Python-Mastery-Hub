# Location: src/python_mastery_hub/web/api/modules.py

"""
Modules API Router

Handles learning module endpoints including content delivery,
progress tracking, and adaptive learning path management.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from python_mastery_hub.web.middleware.auth import get_current_user
from python_mastery_hub.web.models.user import User
from python_mastery_hub.web.models.progress import ModuleProgress, TopicProgress, ProgressStatus
from python_mastery_hub.web.services.progress_service import ProgressService
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class TopicInfo(BaseModel):
    """Topic information."""
    id: str
    title: str
    description: str
    content_type: str  # lesson, exercise, quiz, project
    difficulty: str
    estimated_minutes: int
    prerequisites: List[str] = []
    learning_objectives: List[str] = []
    content_url: Optional[str] = None
    video_url: Optional[str] = None
    is_locked: bool = False
    order: int = 0


class ModuleInfo(BaseModel):
    """Module information."""
    id: str
    title: str
    description: str
    category: str
    difficulty: str
    estimated_hours: int
    prerequisites: List[str] = []
    learning_objectives: List[str] = []
    topics: List[TopicInfo] = []
    instructor: Optional[str] = None
    rating: float = 0.0
    review_count: int = 0
    enrolled_count: int = 0
    is_premium: bool = False
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime


class ModuleEnrollment(BaseModel):
    """Module enrollment information."""
    module_id: str
    user_id: str
    enrolled_at: datetime
    progress: ModuleProgress
    last_accessed: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    certificate_issued: bool = False


class TopicContent(BaseModel):
    """Topic content details."""
    id: str
    title: str
    content_type: str
    content: str  # HTML or Markdown content
    video_url: Optional[str] = None
    code_examples: List[Dict[str, str]] = []
    exercises: List[str] = []  # Exercise IDs
    quiz_questions: List[Dict[str, Any]] = []
    resources: List[Dict[str, str]] = []
    next_topic: Optional[str] = None
    previous_topic: Optional[str] = None


class LearningPath(BaseModel):
    """Personalized learning path."""
    user_id: str
    recommended_modules: List[str]
    current_module: Optional[str] = None
    next_topics: List[str] = []
    skill_gaps: List[str] = []
    estimated_completion_time: int  # hours
    difficulty_level: str
    learning_style_match: float


class ModuleReview(BaseModel):
    """Module review/rating."""
    id: str
    module_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None
    helpful_count: int = 0
    created_at: datetime
    updated_at: datetime


class ModuleStats(BaseModel):
    """Module statistics."""
    module_id: str
    total_enrollments: int
    active_learners: int
    completion_rate: float
    average_rating: float
    average_completion_time: int  # hours
    difficulty_rating: float
    topic_performance: Dict[str, float]


# Module database (in a real app, this would be in a database)
MODULES_DATA = {
    "python-basics": {
        "id": "python-basics",
        "title": "Python Fundamentals",
        "description": "Learn the core concepts of Python programming including variables, data types, control structures, and functions.",
        "category": "Programming Basics",
        "difficulty": "beginner",
        "estimated_hours": 20,
        "prerequisites": [],
        "learning_objectives": [
            "Understand Python syntax and basic concepts",
            "Work with variables and data types",
            "Use control structures (if/else, loops)",
            "Write and call functions",
            "Handle basic input/output operations"
        ],
        "topics": [
            {
                "id": "variables-datatypes",
                "title": "Variables and Data Types",
                "description": "Introduction to Python variables and built-in data types",
                "content_type": "lesson",
                "difficulty": "beginner",
                "estimated_minutes": 45,
                "prerequisites": [],
                "learning_objectives": [
                    "Declare and use variables",
                    "Understand different data types",
                    "Perform type conversions"
                ],
                "order": 1
            },
            {
                "id": "control-structures",
                "title": "Control Structures",
                "description": "Learn about if statements, loops, and flow control",
                "content_type": "lesson",
                "difficulty": "beginner",
                "estimated_minutes": 60,
                "prerequisites": ["variables-datatypes"],
                "learning_objectives": [
                    "Use conditional statements",
                    "Implement loops",
                    "Control program flow"
                ],
                "order": 2
            },
            {
                "id": "functions",
                "title": "Functions",
                "description": "Writing and using functions in Python",
                "content_type": "lesson",
                "difficulty": "beginner",
                "estimated_minutes": 50,
                "prerequisites": ["control-structures"],
                "learning_objectives": [
                    "Define functions",
                    "Use parameters and return values",
                    "Understand scope"
                ],
                "order": 3
            }
        ],
        "instructor": "Dr. Sarah Chen",
        "rating": 4.8,
        "review_count": 1247,
        "enrolled_count": 15230,
        "is_premium": False,
        "tags": ["python", "programming", "beginner", "fundamentals"],
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-03-10T14:30:00Z"
    },
    "python-oop": {
        "id": "python-oop",
        "title": "Object-Oriented Programming in Python",
        "description": "Master object-oriented programming concepts including classes, inheritance, polymorphism, and design patterns.",
        "category": "Advanced Programming",
        "difficulty": "intermediate",
        "estimated_hours": 25,
        "prerequisites": ["python-basics"],
        "learning_objectives": [
            "Understand OOP principles",
            "Create and use classes",
            "Implement inheritance and polymorphism",
            "Apply design patterns"
        ],
        "topics": [
            {
                "id": "classes-objects",
                "title": "Classes and Objects",
                "description": "Introduction to classes and object creation",
                "content_type": "lesson",
                "difficulty": "intermediate",
                "estimated_minutes": 55,
                "prerequisites": [],
                "learning_objectives": [
                    "Define classes",
                    "Create objects",
                    "Use instance variables and methods"
                ],
                "order": 1
            },
            {
                "id": "inheritance",
                "title": "Inheritance and Polymorphism",
                "description": "Advanced OOP concepts for code reuse",
                "content_type": "lesson",
                "difficulty": "intermediate",
                "estimated_minutes": 70,
                "prerequisites": ["classes-objects"],
                "learning_objectives": [
                    "Implement inheritance",
                    "Use polymorphism",
                    "Override methods"
                ],
                "order": 2
            }
        ],
        "instructor": "Prof. Michael Rodriguez",
        "rating": 4.6,
        "review_count": 892,
        "enrolled_count": 8456,
        "is_premium": True,
        "tags": ["python", "oop", "intermediate", "classes"],
        "created_at": "2024-02-01T09:00:00Z",
        "updated_at": "2024-03-15T16:45:00Z"
    }
}

TOPIC_CONTENT = {
    "variables-datatypes": {
        "id": "variables-datatypes",
        "title": "Variables and Data Types",
        "content_type": "lesson",
        "content": """
        <h2>Variables and Data Types in Python</h2>
        
        <h3>What are Variables?</h3>
        <p>Variables in Python are containers for storing data values. Unlike other programming languages, Python has no command for declaring a variable.</p>
        
        <h3>Creating Variables</h3>
        <pre><code>
# Creating variables
name = "Alice"
age = 25
height = 5.6
is_student = True
        </code></pre>
        
        <h3>Python Data Types</h3>
        <ul>
            <li><strong>str</strong> - String (text)</li>
            <li><strong>int</strong> - Integer (whole numbers)</li>
            <li><strong>float</strong> - Floating point (decimal numbers)</li>
            <li><strong>bool</strong> - Boolean (True/False)</li>
            <li><strong>list</strong> - Ordered collection</li>
            <li><strong>dict</strong> - Key-value pairs</li>
        </ul>
        
        <h3>Type Checking</h3>
        <pre><code>
print(type(name))      # <class 'str'>
print(type(age))       # <class 'int'>
print(type(height))    # <class 'float'>
print(type(is_student)) # <class 'bool'>
        </code></pre>
        """,
        "video_url": "https://example.com/videos/variables-datatypes.mp4",
        "code_examples": [
            {
                "title": "Variable Assignment",
                "code": "x = 10\ny = \"Hello\"\nz = [1, 2, 3]"
            },
            {
                "title": "Type Conversion",
                "code": "age_str = \"25\"\nage_int = int(age_str)\nprint(type(age_int))"
            }
        ],
        "exercises": ["basics_variables"],
        "resources": [
            {
                "title": "Python Variables Documentation",
                "url": "https://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator"
            }
        ],
        "next_topic": "control-structures",
        "previous_topic": None
    }
}


# Dependencies
async def get_progress_service() -> ProgressService:
    """Get progress service."""
    return ProgressService()


# Routes
@router.get("/", response_model=List[ModuleInfo])
async def list_modules(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    search: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get list of available learning modules."""
    try:
        modules = []
        
        for module_data in MODULES_DATA.values():
            # Apply filters
            if category and module_data['category'] != category:
                continue
            if difficulty and module_data['difficulty'] != difficulty:
                continue
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                if not any(tag in module_data['tags'] for tag in tag_list):
                    continue
            if search and search.lower() not in module_data['title'].lower() and search.lower() not in module_data['description'].lower():
                continue
            
            # Check if user has access (premium modules)
            if module_data['is_premium'] and (not current_user or not current_user.is_verified):
                continue
            
            # Convert topics
            topics = []
            for topic_data in module_data['topics']:
                topic = TopicInfo(**topic_data)
                
                # Check if topic is locked based on prerequisites
                if current_user:
                    # TODO: Check user progress to determine if topic is locked
                    topic.is_locked = False
                else:
                    topic.is_locked = True
                
                topics.append(topic)
            
            module = ModuleInfo(
                id=module_data['id'],
                title=module_data['title'],
                description=module_data['description'],
                category=module_data['category'],
                difficulty=module_data['difficulty'],
                estimated_hours=module_data['estimated_hours'],
                prerequisites=module_data['prerequisites'],
                learning_objectives=module_data['learning_objectives'],
                topics=topics,
                instructor=module_data.get('instructor'),
                rating=module_data['rating'],
                review_count=module_data['review_count'],
                enrolled_count=module_data['enrolled_count'],
                is_premium=module_data['is_premium'],
                tags=module_data['tags'],
                created_at=datetime.fromisoformat(module_data['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(module_data['updated_at'].replace('Z', '+00:00'))
            )
            modules.append(module)
        
        return modules
    
    except Exception as e:
        logger.error(f"Failed to list modules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve modules"
        )


@router.get("/{module_id}", response_model=ModuleInfo)
async def get_module(
    module_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get specific module details."""
    try:
        if module_id not in MODULES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_id}' not found"
            )
        
        module_data = MODULES_DATA[module_id]
        
        # Check access for premium modules
        if module_data['is_premium'] and (not current_user or not current_user.is_verified):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Premium module access required"
            )
        
        # Convert topics
        topics = []
        for topic_data in module_data['topics']:
            topic = TopicInfo(**topic_data)
            
            # Check if topic is locked
            if current_user:
                # TODO: Check prerequisites and user progress
                topic.is_locked = False
            else:
                topic.is_locked = True
            
            topics.append(topic)
        
        return ModuleInfo(
            id=module_data['id'],
            title=module_data['title'],
            description=module_data['description'],
            category=module_data['category'],
            difficulty=module_data['difficulty'],
            estimated_hours=module_data['estimated_hours'],
            prerequisites=module_data['prerequisites'],
            learning_objectives=module_data['learning_objectives'],
            topics=topics,
            instructor=module_data.get('instructor'),
            rating=module_data['rating'],
            review_count=module_data['review_count'],
            enrolled_count=module_data['enrolled_count'],
            is_premium=module_data['is_premium'],
            tags=module_data['tags'],
            created_at=datetime.fromisoformat(module_data['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(module_data['updated_at'].replace('Z', '+00:00'))
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get module {module_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve module"
        )


@router.post("/{module_id}/enroll")
async def enroll_in_module(
    module_id: str,
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Enroll user in a learning module."""
    try:
        if module_id not in MODULES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_id}' not found"
            )
        
        module_data = MODULES_DATA[module_id]
        
        # Check access for premium modules
        if module_data['is_premium'] and not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Premium module access required"
            )
        
        # Check prerequisites
        # TODO: Implement prerequisite checking
        # for prereq in module_data['prerequisites']:
        #     if not await progress_service.has_completed_module(current_user.id, prereq):
        #         raise HTTPException(
        #             status_code=status.HTTP_400_BAD_REQUEST,
        #             detail=f"Prerequisite module '{prereq}' not completed"
        #         )
        
        # TODO: Create enrollment record
        # enrollment = await progress_service.enroll_user_in_module(current_user.id, module_id)
        
        logger.info(f"User {current_user.username} enrolled in module {module_id}")
        
        return {
            "message": f"Successfully enrolled in module '{module_data['title']}'",
            "module_id": module_id,
            "enrolled_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enroll in module {module_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enroll in module"
        )


@router.get("/{module_id}/topics/{topic_id}", response_model=TopicContent)
async def get_topic_content(
    module_id: str,
    topic_id: str,
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get topic content and materials."""
    try:
        if module_id not in MODULES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_id}' not found"
            )
        
        if topic_id not in TOPIC_CONTENT:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic '{topic_id}' not found"
            )
        
        module_data = MODULES_DATA[module_id]
        
        # Check access for premium modules
        if module_data['is_premium'] and not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Premium module access required"
            )
        
        # TODO: Check if user is enrolled and topic prerequisites are met
        # enrollment = await progress_service.get_module_enrollment(current_user.id, module_id)
        # if not enrollment:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Must be enrolled in module to access content"
        #     )
        
        topic_content = TOPIC_CONTENT[topic_id]
        
        # Track topic access
        await progress_service.update_topic_progress(
            current_user.id,
            {
                "topic_id": topic_id,
                "module_id": module_id,
                "time_spent": 0,
                "status": ProgressStatus.IN_PROGRESS
            }
        )
        
        return TopicContent(**topic_content)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get topic content {module_id}/{topic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve topic content"
        )


@router.post("/{module_id}/topics/{topic_id}/complete")
async def complete_topic(
    module_id: str,
    topic_id: str,
    time_spent: int = Query(..., description="Time spent in minutes"),
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Mark topic as completed."""
    try:
        if module_id not in MODULES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_id}' not found"
            )
        
        # Mark topic as completed
        success = await progress_service.mark_topic_completed(
            user_id=current_user.id,
            module_id=module_id,
            topic_id=topic_id,
            score=1.0,  # Full score for completion
            time_spent=time_spent
        )
        
        if success:
            return {
                "message": "Topic marked as completed",
                "topic_id": topic_id,
                "completed_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark topic as completed"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete topic {module_id}/{topic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete topic"
        )


@router.get("/{module_id}/progress", response_model=ModuleProgress)
async def get_module_progress(
    module_id: str,
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get user's progress in a specific module."""
    try:
        progress = await progress_service.get_module_progress(current_user.id, module_id)
        
        if not progress:
            # Return empty progress if user hasn't started
            return ModuleProgress(
                module_id=module_id,
                title=MODULES_DATA.get(module_id, {}).get('title', 'Unknown Module'),
                status=ProgressStatus.NOT_STARTED,
                overall_score=0.0,
                completion_percentage=0.0,
                topics_completed=0,
                total_topics=len(MODULES_DATA.get(module_id, {}).get('topics', [])),
                time_spent=0
            )
        
        return progress
    
    except Exception as e:
        logger.error(f"Failed to get module progress {module_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve module progress"
        )


@router.get("/{module_id}/stats", response_model=ModuleStats)
async def get_module_stats(
    module_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get module statistics and analytics."""
    try:
        if module_id not in MODULES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_id}' not found"
            )
        
        module_data = MODULES_DATA[module_id]
        
        # TODO: Get real stats from database
        # stats = await progress_service.get_module_statistics(module_id)
        
        # Mock stats for demonstration
        return ModuleStats(
            module_id=module_id,
            total_enrollments=module_data['enrolled_count'],
            active_learners=int(module_data['enrolled_count'] * 0.3),
            completion_rate=0.68,
            average_rating=module_data['rating'],
            average_completion_time=module_data['estimated_hours'],
            difficulty_rating=3.5,
            topic_performance={
                "variables-datatypes": 0.89,
                "control-structures": 0.76,
                "functions": 0.72
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get module stats {module_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve module statistics"
        )


@router.get("/categories")
async def get_categories():
    """Get available module categories."""
    try:
        categories = set()
        for module_data in MODULES_DATA.values():
            categories.add(module_data['category'])
        
        return {
            "categories": sorted(list(categories)),
            "count": len(categories)
        }
    
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )


@router.get("/tags")
async def get_tags():
    """Get available module tags."""
    try:
        tags = set()
        for module_data in MODULES_DATA.values():
            tags.update(module_data['tags'])
        
        return {
            "tags": sorted(list(tags)),
            "count": len(tags)
        }
    
    except Exception as e:
        logger.error(f"Failed to get tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tags"
        )


@router.get("/recommendations", response_model=LearningPath)
async def get_learning_recommendations(
    current_user: User = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get personalized learning recommendations."""
    try:
        # TODO: Implement recommendation algorithm based on:
        # - User's current progress
        # - Learning preferences
        # - Skill gaps
        # - Similar users' paths
        
        # Mock recommendations for demonstration
        user_progress = await progress_service.get_user_progress(current_user.id)
        
        recommended_modules = []
        if not user_progress or user_progress.modules_completed == 0:
            recommended_modules = ["python-basics"]
        else:
            recommended_modules = ["python-oop", "data-structures"]
        
        return LearningPath(
            user_id=current_user.id,
            recommended_modules=recommended_modules,
            current_module="python-basics" if user_progress and user_progress.modules_completed == 0 else None,
            next_topics=["variables-datatypes", "control-structures"],
            skill_gaps=["object-oriented programming", "data structures"],
            estimated_completion_time=45,
            difficulty_level="beginner",
            learning_style_match=0.85
        )
    
    except Exception as e:
        logger.error(f"Failed to get learning recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recommendations"
        )


@router.post("/{module_id}/reviews", response_model=ModuleReview)
async def create_module_review(
    module_id: str,
    rating: int = Query(..., ge=1, le=5),
    review_text: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Create or update module review."""
    try:
        if module_id not in MODULES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_id}' not found"
            )
        
        # TODO: Check if user has completed the module
        # has_completed = await progress_service.has_completed_module(current_user.id, module_id)
        # if not has_completed:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Must complete module before reviewing"
        #     )
        
        # TODO: Create or update review in database
        review = ModuleReview(
            id=f"{current_user.id}_{module_id}",
            module_id=module_id,
            user_id=current_user.id,
            rating=rating,
            review_text=review_text,
            helpful_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        logger.info(f"Review created for module {module_id} by user {current_user.username}")
        
        return review
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create review for module {module_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )


@router.get("/{module_id}/reviews")
async def get_module_reviews(
    module_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|rating|helpful_count)$")
):
    """Get module reviews and ratings."""
    try:
        if module_id not in MODULES_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_id}' not found"
            )
        
        # TODO: Get reviews from database
        # reviews = await get_module_reviews_from_db(module_id, skip, limit, sort_by)
        
        # Mock reviews for demonstration
        reviews = [
            {
                "id": "review1",
                "module_id": module_id,
                "user_id": "user1",
                "username": "learning_enthusiast",
                "rating": 5,
                "review_text": "Excellent module! Very well structured and easy to follow.",
                "helpful_count": 12,
                "created_at": datetime.now() - timedelta(days=5),
                "updated_at": datetime.now() - timedelta(days=5)
            },
            {
                "id": "review2",
                "module_id": module_id,
                "user_id": "user2",
                "username": "code_newbie",
                "rating": 4,
                "review_text": "Great content, but could use more examples.",
                "helpful_count": 8,
                "created_at": datetime.now() - timedelta(days=2),
                "updated_at": datetime.now() - timedelta(days=2)
            }
        ]
        
        return {
            "reviews": reviews,
            "total": len(reviews),
            "average_rating": 4.5,
            "rating_distribution": {
                "5": 60,
                "4": 25,
                "3": 10,
                "2": 3,
                "1": 2
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reviews for module {module_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reviews"
        )


@router.get("/search")
async def search_modules(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Search modules by title, description, or content."""
    try:
        results = []
        query = q.lower()
        
        for module_data in MODULES_DATA.values():
            # Skip premium modules for non-verified users
            if module_data['is_premium'] and (not current_user or not current_user.is_verified):
                continue
            
            # Apply filters
            if category and module_data['category'] != category:
                continue
            if difficulty and module_data['difficulty'] != difficulty:
                continue
            
            # Search in title, description, and tags
            searchable_text = (
                module_data['title'] + " " + 
                module_data['description'] + " " + 
                " ".join(module_data['tags'])
            ).lower()
            
            if query in searchable_text:
                # Calculate relevance score
                title_match = query in module_data['title'].lower()
                desc_match = query in module_data['description'].lower()
                tag_match = query in " ".join(module_data['tags']).lower()
                
                relevance = 0
                if title_match:
                    relevance += 3
                if desc_match:
                    relevance += 2
                if tag_match:
                    relevance += 1
                
                results.append({
                    "module": {
                        "id": module_data['id'],
                        "title": module_data['title'],
                        "description": module_data['description'],
                        "category": module_data['category'],
                        "difficulty": module_data['difficulty'],
                        "rating": module_data['rating'],
                        "enrolled_count": module_data['enrolled_count'],
                        "is_premium": module_data['is_premium'],
                        "tags": module_data['tags']
                    },
                    "relevance": relevance
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return {
            "query": q,
            "results": [r['module'] for r in results],
            "total": len(results),
            "filters_applied": {
                "category": category,
                "difficulty": difficulty
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to search modules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search modules"
        )