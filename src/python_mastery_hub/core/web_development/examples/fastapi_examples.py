"""
FastAPI Examples for Web Development Learning.

Comprehensive FastAPI examples from basic to advanced concepts.
"""

from typing import Dict, Any


def get_fastapi_basics() -> Dict[str, Any]:
    """Get basic FastAPI examples."""
    return {
        "basic_fastapi": {
            "code": '''
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import uvicorn

# Create FastAPI application
app = FastAPI(
    title="FastAPI Demo",
    description="A comprehensive FastAPI demonstration",
    version="1.0.0"
)

# Pydantic models for request/response validation
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    author_id: int

class Post(PostBase):
    id: int
    author_id: int
    author_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# In-memory storage
users_db = {}
posts_db = {}
user_counter = 1
post_counter = 1

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with HTML response."""
    return """
    <html>
        <head><title>FastAPI Demo</title></head>
        <body>
            <h1>Welcome to FastAPI Demo!</h1>
            <p>Visit <a href="/docs">API Documentation</a> for interactive docs.</p>
            <ul>
                <li><a href="/users">Users API</a></li>
                <li><a href="/posts">Posts API</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
        </body>
    </html>
    """

# User endpoints
@app.get("/users", response_model=List[User])
async def get_users():
    """Get all users."""
    return list(users_db.values())

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get specific user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user."""
    global user_counter
    
    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user['email'] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": user_counter,
        "name": user.name,
        "email": user.email,
        "created_at": datetime.now()
    }
    
    users_db[user_counter] = new_user
    user_counter += 1
    
    return new_user

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserBase):
    """Update an existing user."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if new email conflicts with other users
    for uid, existing_user in users_db.items():
        if uid != user_id and existing_user['email'] == user_update.email:
            raise HTTPException(status_code=400, detail="Email already taken")
    
    users_db[user_id].update({
        "name": user_update.name,
        "email": user_update.email
    })
    
    return users_db[user_id]

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete a user."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    deleted_user = users_db.pop(user_id)
    
    # Also delete user's posts
    user_posts = [pid for pid, post in posts_db.items() if post['author_id'] == user_id]
    for pid in user_posts:
        del posts_db[pid]
    
    return {
        "message": f"User {deleted_user['name']} and {len(user_posts)} posts deleted"
    }

# Post endpoints
@app.get("/posts", response_model=List[Post])
async def get_posts():
    """Get all posts."""
    return list(posts_db.values())

@app.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: int):
    """Get specific post by ID."""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts_db[post_id]

@app.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate):
    """Create a new post."""
    global post_counter
    
    # Verify author exists
    if post.author_id not in users_db:
        raise HTTPException(status_code=400, detail="Author not found")
    
    new_post = {
        "id": post_counter,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "author_name": users_db[post.author_id]['name'],
        "created_at": datetime.now()
    }
    
    posts_db[post_counter] = new_post
    post_counter += 1
    
    return new_post

@app.get("/users/{user_id}/posts", response_model=List[Post])
async def get_user_posts(user_id: int):
    """Get all posts by a specific user."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_posts = [post for post in posts_db.values() if post['author_id'] == user_id]
    return user_posts

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "users_count": len(users_db),
        "posts_count": len(posts_db)
    }

# Query parameters example
@app.get("/search/posts")
async def search_posts(q: Optional[str] = None, limit: int = 10):
    """Search posts with query parameters."""
    all_posts = list(posts_db.values())
    
    if q:
        # Simple text search in title and content
        filtered_posts = [
            post for post in all_posts 
            if q.lower() in post['title'].lower() or q.lower() in post['content'].lower()
        ]
    else:
        filtered_posts = all_posts
    
    return {
        "query": q,
        "total_found": len(filtered_posts),
        "results": filtered_posts[:limit]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
            "explanation": "Basic FastAPI application with automatic validation and documentation"
        }
    }


def get_fastapi_advanced() -> Dict[str, Any]:
    """Get advanced FastAPI examples."""
    return {
        "fastapi_advanced": {
            "code": '''
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Advanced FastAPI Demo",
    description="Advanced FastAPI features demonstration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Advanced Pydantic models
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(1, ge=1, le=5)

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    status: str = "pending"
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Global storage
tasks_db: Dict[int, Task] = {}
task_counter = 1

# Dependency injection examples
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from token."""
    # In a real app, you'd validate the JWT token here
    token = credentials.credentials
    if token != "valid-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"id": 1, "username": "demo_user"}

async def get_task_or_404(task_id: int) -> Task:
    """Dependency to get task or raise 404."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]

# Background tasks
async def send_notification(task_id: int, message: str):
    """Simulate sending a notification."""
    await asyncio.sleep(1)  # Simulate async operation
    logger.info(f"Notification sent for task {task_id}: {message}")

# Advanced endpoints
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create a new task with background notification."""
    global task_counter
    
    new_task = Task(
        id=task_counter,
        title=task.title,
        description=task.description,
        priority=task.priority,
        created_at=datetime.now()
    )
    
    tasks_db[task_counter] = new_task
    
    # Add background task
    background_tasks.add_task(
        send_notification,
        task_counter,
        f"Task '{task.title}' created successfully"
    )
    
    task_counter += 1
    logger.info(f"Task created by user {current_user['username']}")
    
    return new_task

@app.get("/tasks", response_model=List[Task])
async def get_tasks(
    status_filter: Optional[str] = None,
    priority_min: Optional[int] = None,
    priority_max: Optional[int] = None,
    limit: int = Field(10, ge=1, le=100),
    offset: int = Field(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get tasks with advanced filtering and pagination."""
    all_tasks = list(tasks_db.values())
    
    # Apply filters
    if status_filter:
        all_tasks = [t for t in all_tasks if t.status == status_filter]
    
    if priority_min is not None:
        all_tasks = [t for t in all_tasks if t.priority >= priority_min]
    
    if priority_max is not None:
        all_tasks = [t for t in all_tasks if t.priority <= priority_max]
    
    # Apply pagination
    paginated_tasks = all_tasks[offset:offset + limit]
    
    return paginated_tasks

@app.put("/tasks/{task_id}/complete", response_model=Task)
async def complete_task(
    task: Task = Depends(get_task_or_404),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    """Mark task as completed."""
    task.status = "completed"
    task.completed_at = datetime.now()
    
    # Add background notification
    background_tasks.add_task(
        send_notification,
        task.id,
        f"Task '{task.title}' completed"
    )
    
    return task

@app.get("/tasks/stats")
async def get_task_stats(current_user: dict = Depends(get_current_user)):
    """Get task statistics."""
    all_tasks = list(tasks_db.values())
    
    stats = {
        "total_tasks": len(all_tasks),
        "pending_tasks": len([t for t in all_tasks if t.status == "pending"]),
        "completed_tasks": len([t for t in all_tasks if t.status == "completed"]),
        "avg_priority": sum(t.priority for t in all_tasks) / len(all_tasks) if all_tasks else 0
    }
    
    # Group by priority
    priority_breakdown = {}
    for task in all_tasks:
        priority = task.priority
        if priority not in priority_breakdown:
            priority_breakdown[priority] = 0
        priority_breakdown[priority] += 1
    
    stats["priority_breakdown"] = priority_breakdown
    
    return stats

# Middleware example
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests."""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return HTTPException(status_code=400, detail=str(exc))

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    logger.info("FastAPI application starting up...")
    
    # Create some sample data
    sample_tasks = [
        {"title": "Learn FastAPI", "description": "Study FastAPI documentation", "priority": 1},
        {"title": "Build API", "description": "Create REST API endpoints", "priority": 2},
        {"title": "Write tests", "description": "Add comprehensive test coverage", "priority": 3}
    ]
    
    global task_counter
    for task_data in sample_tasks:
        task = Task(
            id=task_counter,
            **task_data,
            created_at=datetime.now()
        )
        tasks_db[task_counter] = task
        task_counter += 1

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("FastAPI application shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
            "explanation": "Advanced FastAPI with dependency injection, middleware, and background tasks"
        }
    }