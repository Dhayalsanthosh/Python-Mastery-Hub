"""
REST API Exercise for Web Development Learning.

Build a complete REST API with advanced features including CRUD operations,
filtering, pagination, validation, and error handling.
"""

from typing import Dict, Any


def get_exercise() -> Dict[str, Any]:
    """Get the REST API exercise."""
    return {
        "title": "Build a Complete REST API",
        "description": "Create a full-featured REST API for a task management system",
        "difficulty": "hard",
        "estimated_time": "4-6 hours",
        "learning_objectives": [
            "Implement CRUD operations with proper HTTP methods",
            "Add request/response validation with Pydantic",
            "Implement filtering, sorting, and pagination",
            "Handle errors gracefully with appropriate status codes",
            "Add comprehensive API documentation",
            "Implement proper data relationships"
        ],
        "requirements": [
            "FastAPI framework",
            "Pydantic for validation",
            "SQLAlchemy for database ORM",
            "pytest for testing",
            "uvicorn for server"
        ],
        "starter_code": '''
"""
Task Management API - Starter Code

Complete the TODO sections to build a full REST API.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI app
app = FastAPI(
    title="Task Management API",
    description="A comprehensive task management system",
    version="1.0.0"
)

# Enums
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # TODO: Add relationship to tasks
    # tasks = relationship("Task", back_populates="assignee")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    status = Column(String, default=TaskStatus.TODO)
    priority = Column(String, default=Priority.MEDIUM)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # TODO: Add foreign key and relationship
    # assignee_id = Column(Integer, ForeignKey("users.id"))
    # assignee = relationship("User", back_populates="tasks")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$')
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    assignee_id: Optional[int] = None
    # TODO: Add assignee relationship
    # assignee: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

class PaginatedTasksResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int
    size: int
    pages: int

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# TODO: Implement CRUD operations

# User CRUD operations
def create_user(db: Session, user: UserCreate):
    """Create a new user."""
    # TODO: Implement user creation
    # 1. Check if username/email already exists
    # 2. Create new User instance
    # 3. Add to database and commit
    # 4. Return created user
    pass

def get_user(db: Session, user_id: int):
    """Get user by ID."""
    # TODO: Implement get user by ID
    pass

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get users with pagination."""
    # TODO: Implement paginated user retrieval
    pass

# Task CRUD operations
def create_task(db: Session, task: TaskCreate):
    """Create a new task."""
    # TODO: Implement task creation
    # 1. Validate assignee exists if provided
    # 2. Create new Task instance
    # 3. Add to database and commit
    # 4. Return created task
    pass

def get_task(db: Session, task_id: int):
    """Get task by ID."""
    # TODO: Implement get task by ID
    pass

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    priority: Optional[Priority] = None,
    assignee_id: Optional[int] = None
):
    """Get tasks with filtering and pagination."""
    # TODO: Implement filtered and paginated task retrieval
    # 1. Start with base query
    # 2. Apply filters if provided
    # 3. Apply pagination
    # 4. Return results
    pass

def update_task(db: Session, task_id: int, task_update: TaskUpdate):
    """Update a task."""
    # TODO: Implement task update
    # 1. Get existing task
    # 2. Update only provided fields
    # 3. Update updated_at timestamp
    # 4. Commit and return updated task
    pass

def delete_task(db: Session, task_id: int):
    """Delete a task."""
    # TODO: Implement task deletion
    pass

# TODO: Implement API endpoints

# User endpoints
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # TODO: Implement user creation endpoint
    # 1. Call create_user function
    # 2. Handle potential errors (duplicate username/email)
    # 3. Return created user
    pass

@app.get("/users", response_model=List[UserResponse])
async def get_users_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get users with pagination."""
    # TODO: Implement get users endpoint
    pass

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user."""
    # TODO: Implement get user endpoint
    # 1. Call get_user function
    # 2. Handle user not found
    # 3. Return user
    pass

# Task endpoints
@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    # TODO: Implement task creation endpoint
    pass

@app.get("/tasks", response_model=PaginatedTasksResponse)
async def get_tasks_endpoint(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    priority: Optional[Priority] = None,
    assignee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get tasks with filtering and pagination."""
    # TODO: Implement get tasks endpoint with advanced features
    # 1. Calculate skip value from page and size
    # 2. Call get_tasks with filters
    # 3. Calculate total pages
    # 4. Return paginated response
    pass

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task."""
    # TODO: Implement get task endpoint
    pass

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a task."""
    # TODO: Implement task update endpoint
    pass

@app.delete("/tasks/{task_id}")
async def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    # TODO: Implement task deletion endpoint
    pass

# TODO: Add additional endpoints

@app.get("/tasks/stats")
async def get_task_stats(db: Session = Depends(get_db)):
    """Get task statistics."""
    # TODO: Implement task statistics endpoint
    # Return counts by status, priority, overdue tasks, etc.
    pass

@app.get("/users/{user_id}/tasks", response_model=List[TaskResponse])
async def get_user_tasks(
    user_id: int,
    status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db)
):
    """Get tasks assigned to a specific user."""
    # TODO: Implement user tasks endpoint
    pass

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
        "solution_hints": [
            "Start by implementing the database models and relationships",
            "Implement CRUD operations one by one, testing each",
            "Add proper error handling for common scenarios",
            "Use SQLAlchemy query methods for filtering and pagination",
            "Test your API endpoints using FastAPI's automatic docs at /docs"
        ],
        "testing_guide": '''
# Testing Your REST API

1. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Access API documentation:**
   Visit http://localhost:8000/docs

3. **Test with curl:**
   ```bash
   # Create a user
   curl -X POST "http://localhost:8000/users" \\
        -H "Content-Type: application/json" \\
        -d '{"username": "john_doe", "email": "john@example.com", "full_name": "John Doe"}'

   # Create a task
   curl -X POST "http://localhost:8000/tasks" \\
        -H "Content-Type: application/json" \\
        -d '{"title": "Complete API", "description": "Finish the REST API exercise", "priority": "high"}'

   # Get tasks with filtering
   curl "http://localhost:8000/tasks?status=todo&priority=high&page=1&size=10"
   ```

4. **Write unit tests:**
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from main import app

   client = TestClient(app)

   def test_create_user():
       response = client.post("/users", json={
           "username": "testuser",
           "email": "test@example.com"
       })
       assert response.status_code == 201
       assert response.json()["username"] == "testuser"
   ```
''',
        "bonus_challenges": [
            "Add search functionality across task titles and descriptions",
            "Implement task comments with a separate Comment model",
            "Add file attachment support for tasks",
            "Implement task dependencies (blocking relationships)",
            "Add email notifications for task assignments",
            "Create task templates for recurring tasks",
            "Add time tracking functionality",
            "Implement task labels/tags with many-to-many relationships"
        ]
    }