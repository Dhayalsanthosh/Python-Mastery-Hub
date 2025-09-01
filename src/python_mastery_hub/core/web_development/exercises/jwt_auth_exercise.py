"""
JWT Authentication Exercise for Web Development Learning.

Implement a secure JWT-based authentication system with registration,
login, token refresh, and protected endpoints.
"""

from typing import Dict, Any


def get_exercise() -> Dict[str, Any]:
    """Get the complete JWT authentication exercise."""
    return {
        "title": "JWT Authentication System",
        "description": "Build a secure authentication system with JWT tokens, refresh tokens, and password security",
        "difficulty": "hard",
        "estimated_time": "4-5 hours",
        "learning_objectives": [
            "Implement user registration with validation",
            "Generate and validate JWT access tokens",
            "Handle refresh token mechanism for security",
            "Secure API endpoints with authentication middleware",
            "Implement proper password hashing and validation",
            "Handle token expiration and renewal",
            "Add role-based access control",
            "Implement logout and token revocation"
        ],
        "requirements": [
            "FastAPI for API framework",
            "PyJWT for token handling",
            "passlib[bcrypt] for password hashing",
            "python-multipart for form handling",
            "SQLAlchemy for user storage",
            "pydantic[email] for email validation"
        ],
        "starter_code": '''
"""
JWT Authentication System - Starter Code

Complete the TODO sections to build a secure authentication system.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import secrets
from enum import Enum

app = FastAPI(title="JWT Authentication System")

# Configuration - TODO: Move to environment variables in production
SECRET_KEY = secrets.token_urlsafe(32)  # Generate secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User roles
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

# In-memory storage (TODO: Replace with real database)
users_db: Dict[str, dict] = {}
refresh_tokens_db: Dict[str, dict] = {}  # token -> user info
blacklisted_tokens: set = set()  # For logout functionality

# TODO: Implement Pydantic models
class UserRegistration(BaseModel):
    """User registration model with validation."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        # TODO: Implement username validation
        # - Only alphanumeric and underscore
        # - Cannot start with number
        # - Reserved usernames check
        pass
    
    @validator('password')
    def validate_password(cls, v):
        # TODO: Implement strong password validation
        # - At least one uppercase letter
        # - At least one lowercase letter  
        # - At least one digit
        # - At least one special character
        # - Common password check
        pass

class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str

class User(BaseModel):
    """User response model (without sensitive data)."""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefresh(BaseModel):
    """Token refresh request model."""
    refresh_token: str

class PasswordChange(BaseModel):
    """Password change model."""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        # TODO: Reuse password validation from registration
        pass

# TODO: Implement password utilities
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # TODO: Implement password hashing
    pass

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # TODO: Implement password verification
    pass

# TODO: Implement JWT token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    # TODO: Implement access token creation
    # 1. Copy payload data
    # 2. Add expiration time
    # 3. Add token type claim
    # 4. Encode with secret key
    pass

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    # TODO: Implement refresh token creation
    # 1. Copy payload data
    # 2. Add longer expiration time
    # 3. Add token type claim
    # 4. Store in refresh_tokens_db
    # 5. Return encoded token
    pass

def verify_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """Verify and decode JWT token."""
    # TODO: Implement token verification
    # 1. Check if token is blacklisted
    # 2. Decode token with secret key
    # 3. Verify token type
    # 4. Check expiration
    # 5. Return payload
    # Handle: ExpiredSignatureError, JWTError
    pass

# TODO: Implement user management functions
def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username."""
    # TODO: Search users_db for matching username
    pass

def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email."""
    # TODO: Search users_db for matching email
    pass

def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID."""
    # TODO: Get user from users_db
    pass

def create_user(user_data: UserRegistration) -> dict:
    """Create a new user."""
    # TODO: Implement user creation
    # 1. Generate unique user ID
    # 2. Hash password
    # 3. Create user object
    # 4. Store in users_db
    # 5. Return user (without password)
    pass

# TODO: Implement authentication dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from JWT token."""
    # TODO: Implement current user extraction
    # 1. Extract token from credentials
    # 2. Verify token
    # 3. Get user ID from payload
    # 4. Fetch user from database
    # 5. Check if user is active
    # 6. Return user object
    pass

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current active user."""
    # TODO: Check if user is active
    pass

async def require_role(required_role: UserRole):
    """Dependency factory for role-based access control."""
    def role_checker(current_user: dict = Depends(get_current_active_user)) -> dict:
        # TODO: Implement role checking
        # 1. Get user role
        # 2. Check if user has required role
        # 3. Admin role should access everything
        # 4. Raise HTTPException if insufficient permissions
        pass
    return role_checker

# TODO: Implement authentication endpoints
@app.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistration):
    """Register a new user."""
    # TODO: Implement user registration
    # 1. Check if username already exists
    # 2. Check if email already exists
    # 3. Create new user
    # 4. Return user data (without password)
    pass

@app.post("/auth/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Authenticate user and return tokens."""
    # TODO: Implement user login
    # 1. Get user by username
    # 2. Verify password
    # 3. Check if user is active
    # 4. Update last_login timestamp
    # 5. Create access and refresh tokens
    # 6. Return token response
    pass

@app.post("/auth/refresh", response_model=Token)
async def refresh_access_token(token_data: TokenRefresh):
    """Refresh access token using refresh token."""
    # TODO: Implement token refresh
    # 1. Verify refresh token
    # 2. Check if token exists in refresh_tokens_db
    # 3. Get user from token payload
    # 4. Check if user still exists and is active
    # 5. Create new access and refresh tokens
    # 6. Revoke old refresh token
    # 7. Return new token response
    pass

@app.post("/auth/logout")
async def logout_user(
    token_data: TokenRefresh,
    current_user: dict = Depends(get_current_active_user)
):
    """Logout user by revoking refresh token."""
    # TODO: Implement user logout
    # 1. Add current access token to blacklist
    # 2. Remove refresh token from refresh_tokens_db
    # 3. Return success message
    pass

@app.post("/auth/logout-all")
async def logout_all_sessions(current_user: dict = Depends(get_current_active_user)):
    """Logout user from all sessions."""
    # TODO: Implement logout from all sessions
    # 1. Find all refresh tokens for user
    # 2. Remove all user's refresh tokens
    # 3. Return count of revoked sessions
    pass

# TODO: Implement protected endpoints
@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current user information."""
    # TODO: Return current user data
    pass

@app.put("/auth/me", response_model=User)
async def update_current_user(
    full_name: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Update current user information."""
    # TODO: Implement user profile update
    # 1. Update allowed fields
    # 2. Save changes
    # 3. Return updated user
    pass

@app.post("/auth/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_active_user)
):
    """Change user password."""
    # TODO: Implement password change
    # 1. Verify current password
    # 2. Hash new password
    # 3. Update user password
    # 4. Revoke all refresh tokens (force re-login)
    # 5. Return success message
    pass

# TODO: Implement admin endpoints
@app.get("/admin/users", response_model=List[User])
async def get_all_users(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """Get all users (admin only)."""
    # TODO: Return all users
    pass

@app.patch("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """Update user role (admin only)."""
    # TODO: Implement role update
    pass

@app.patch("/admin/users/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """Activate/deactivate user (admin only)."""
    # TODO: Toggle user active status
    pass

@app.get("/admin/tokens")
async def get_active_tokens(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """Get information about active refresh tokens."""
    # TODO: Return token statistics
    pass

# TODO: Add example protected resources
@app.get("/protected/basic")
async def protected_basic(current_user: dict = Depends(get_current_active_user)):
    """Basic protected endpoint."""
    return {"message": f"Hello {current_user['username']}, this is a protected endpoint!"}

@app.get("/protected/admin")
async def protected_admin(current_user: dict = Depends(require_role(UserRole.ADMIN))):
    """Admin-only protected endpoint."""
    return {"message": "This is an admin-only endpoint"}

@app.get("/protected/moderator")
async def protected_moderator(current_user: dict = Depends(require_role(UserRole.MODERATOR))):
    """Moderator-only protected endpoint."""
    return {"message": "This is a moderator-only endpoint"}

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "users_count": len(users_db),
        "active_tokens": len(refresh_tokens_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
        "testing_guide": '''
# Testing Your JWT Authentication System

## 1. Start the Server
```bash
uvicorn main:app --reload
```

## 2. Test User Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \\
     -H "Content-Type: application/json" \\
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "SecurePass123!",
       "full_name": "Test User"
     }'
```

## 3. Test User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \\
     -H "Content-Type: application/json" \\
     -d '{
       "username": "testuser",
       "password": "SecurePass123!"
     }'
```

## 4. Test Protected Endpoints
```bash
# Save the access token from login response
TOKEN="your_access_token_here"

# Test protected endpoint
curl -X GET "http://localhost:8000/auth/me" \\
     -H "Authorization: Bearer $TOKEN"

# Test role-based endpoint
curl -X GET "http://localhost:8000/protected/admin" \\
     -H "Authorization: Bearer $TOKEN"
```

## 5. Test Token Refresh
```bash
curl -X POST "http://localhost:8000/auth/refresh" \\
     -H "Content-Type: application/json" \\
     -d '{
       "refresh_token": "your_refresh_token_here"
     }'
```

## 6. Python Testing Script
```python
import requests
import json

base_url = "http://localhost:8000"

# Register user
response = requests.post(f"{base_url}/auth/register", json={
    "username": "testuser2",
    "email": "test2@example.com", 
    "password": "SecurePass123!",
    "full_name": "Test User 2"
})
print("Registration:", response.status_code, response.json())

# Login
response = requests.post(f"{base_url}/auth/login", json={
    "username": "testuser2",
    "password": "SecurePass123!"
})
tokens = response.json()
access_token = tokens["access_token"]

# Test protected endpoint
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{base_url}/auth/me", headers=headers)
print("User info:", response.json())
```
''',
        "solution_hints": [
            "Use secrets.token_urlsafe() for generating user IDs and tokens",
            "Store password hashes, never plain passwords",
            "Add 'sub' (subject) claim with user ID in JWT payload",
            "Use different expiration times for access and refresh tokens",
            "Validate tokens in dependency functions with proper error handling",
            "Check token blacklist before validating any token",
            "Update last_login timestamp on successful login",
            "Use enum values for role comparisons",
            "Implement password strength validation with regex patterns",
            "Store refresh tokens with metadata for tracking"
        ],
        "security_considerations": [
            "Use environment variables for SECRET_KEY in production",
            "Implement rate limiting on authentication endpoints",
            "Add CORS headers appropriately",
            "Validate all input data thoroughly",
            "Use HTTPS in production",
            "Implement account lockout after failed attempts",
            "Add logging for security events",
            "Consider implementing 2FA for enhanced security"
        ],
        "bonus_challenges": [
            "Add email verification for new registrations", 
            "Implement password reset via email",
            "Add rate limiting to prevent brute force attacks",
            "Implement account lockout after failed login attempts",
            "Add two-factor authentication (2FA)",
            "Create API key authentication for service accounts",
            "Add OAuth2 integration (Google, GitHub)",
            "Implement session management with Redis",
            "Add audit logging for all authentication events",
            "Create user profile picture upload functionality"
        ]
    }