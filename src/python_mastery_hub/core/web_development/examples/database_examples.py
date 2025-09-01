"""
Database Integration Examples for Web Development Learning.

SQLAlchemy ORM with FastAPI integration examples.
"""

from typing import Dict, Any


def get_database_examples() -> Dict[str, Any]:
    """Get database integration examples."""
    return {
        "sqlalchemy_integration": {
            "code": '''
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"))
    
    author = relationship("User", back_populates="posts")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: Optional[str] = None
    published: bool = False

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None

class PostResponse(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    author_id: int
    author: UserResponse
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(title="SQLAlchemy Integration Demo")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD operations for users
def create_user(db: Session, user: UserCreate):
    """Create a new user."""
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_update: UserBase):
    """Update user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# CRUD operations for posts
def create_post(db: Session, post: PostCreate, author_id: int):
    """Create a new post."""
    db_post = Post(**post.dict(), author_id=author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_post(db: Session, post_id: int):
    """Get post by ID."""
    return db.query(Post).filter(Post.id == post_id).first()

def get_posts(db: Session, skip: int = 0, limit: int = 100, published_only: bool = False):
    """Get posts with pagination."""
    query = db.query(Post)
    if published_only:
        query = query.filter(Post.published == True)
    return query.offset(skip).limit(limit).all()

# API Endpoints
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if username exists
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return create_user(db=db, user=user)

@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get users with pagination."""
    users = get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/posts/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post_for_user(user_id: int, post: PostCreate, db: Session = Depends(get_db)):
    """Create a new post for a user."""
    # Verify user exists
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return create_post(db=db, post=post, author_id=user_id)

@app.get("/posts/", response_model=List[PostResponse])
def read_posts(skip: int = 0, limit: int = 100, published_only: bool = False, db: Session = Depends(get_db)):
    """Get posts with pagination."""
    posts = get_posts(db, skip=skip, limit=limit, published_only=published_only)
    return posts

@app.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    """Get database statistics."""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_posts = db.query(Post).count()
    published_posts = db.query(Post).filter(Post.published == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_posts": total_posts,
        "published_posts": published_posts,
        "draft_posts": total_posts - published_posts
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
            "explanation": "SQLAlchemy ORM integration with FastAPI for database operations"
        }
    }