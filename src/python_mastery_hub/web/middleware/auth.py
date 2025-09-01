# Location: src/python_mastery_hub/web/middleware/auth.py

"""
Authentication Middleware

Handles JWT token validation, user authentication, and authorization
for protected routes.
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext

from python_mastery_hub.web.models.user import User, UserRole
from python_mastery_hub.web.models.session import UserSession, SessionStatus
from python_mastery_hub.utils.logging_config import get_logger
from python_mastery_hub.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer(auto_error=False)


class AuthenticationError(Exception):
    """Custom authentication error."""
    pass


class AuthorizationError(Exception):
    """Custom authorization error."""
    pass


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        # Verify token type
        if payload.get("type") != token_type:
            raise AuthenticationError(f"Invalid token type. Expected {token_type}")
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            raise AuthenticationError("Token has expired")
        
        return payload
    
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID from database."""
    # This would typically query your database
    # For now, returning a mock user for demonstration
    try:
        # TODO: Replace with actual database query
        # user_data = await database.fetch_one(
        #     "SELECT * FROM users WHERE id = :user_id AND is_active = true",
        #     {"user_id": user_id}
        # )
        
        # Mock user data for demonstration
        if user_id == "mock_user_id":
            from datetime import datetime
            return User(
                id=user_id,
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                role=UserRole.STUDENT,
                is_active=True,
                is_verified=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        return None
    
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return None


async def get_session_by_token(session_token: str) -> Optional[UserSession]:
    """Get session by token from database."""
    try:
        # TODO: Replace with actual database query
        # session_data = await database.fetch_one(
        #     "SELECT * FROM user_sessions WHERE session_token = :token AND status = 'active'",
        #     {"token": session_token}
        # )
        
        # Mock session for demonstration
        if session_token == "mock_session_token":
            from datetime import datetime, timedelta
            return UserSession(
                id="mock_session_id",
                user_id="mock_user_id",
                session_token=session_token,
                status=SessionStatus.ACTIVE,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24)
            )
        
        return None
    
    except Exception as e:
        logger.error(f"Error fetching session {session_token}: {e}")
        return None


async def update_session_activity(session: UserSession) -> None:
    """Update session last accessed time."""
    try:
        session.update_activity()
        
        # TODO: Update session in database
        # await database.execute(
        #     "UPDATE user_sessions SET last_accessed = :last_accessed, page_views = :page_views WHERE id = :session_id",
        #     {
        #         "last_accessed": session.last_accessed,
        #         "page_views": session.page_views,
        #         "session_id": session.id
        #     }
        # )
        
        logger.debug(f"Updated session activity for session {session.id}")
    
    except Exception as e:
        logger.error(f"Error updating session activity: {e}")


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get current authenticated user."""
    if not credentials:
        return None
    
    try:
        # Verify JWT token
        payload = verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        session_token = payload.get("session_token")
        
        if not user_id:
            return None
        
        # Get user from database
        user = await get_user_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        # Verify session if session_token is present
        if session_token:
            session = await get_session_by_token(session_token)
            if not session or not session.is_active:
                logger.warning(f"Invalid or expired session for user {user_id}")
                return None
            
            # Update session activity
            await update_session_activity(session)
        
        # Add user to request state for later use
        request.state.user = user
        
        return user
    
    except AuthenticationError as e:
        logger.warning(f"Authentication failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        return None


async def require_authenticated_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Require authenticated user or raise 401."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def require_verified_user(
    current_user: User = Depends(require_authenticated_user)
) -> User:
    """Require verified user or raise 403."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


async def require_admin(
    current_user: User = Depends(require_verified_user)
) -> User:
    """Require admin user or raise 403."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def require_instructor_or_admin(
    current_user: User = Depends(require_verified_user)
) -> User:
    """Require instructor or admin user or raise 403."""
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor or admin privileges required"
        )
    return current_user


def check_permissions(required_permissions: list, user_permissions: list) -> bool:
    """Check if user has required permissions."""
    return all(perm in user_permissions for perm in required_permissions)


async def require_permissions(
    required_permissions: list,
    current_user: User = Depends(require_verified_user)
) -> User:
    """Require specific permissions or raise 403."""
    # TODO: Implement permission system
    # user_permissions = await get_user_permissions(current_user.id)
    # if not check_permissions(required_permissions, user_permissions):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions"
    #     )
    return current_user


async def create_user_session(
    user: User,
    request: Request,
    remember_me: bool = False,
    expires_hours: int = 24
) -> tuple[str, str, UserSession]:
    """Create a new user session and return tokens."""
    try:
        # Extract device info from request
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else None
        
        # Create session
        session_data = {
            "user_id": user.id,
            "device_info": {
                "user_agent": user_agent,
                "ip_address": ip_address
            },
            "remember_me": remember_me,
            "expires_hours": expires_hours if not remember_me else 168  # 1 week for remember me
        }
        
        # TODO: Save session to database
        # session = await create_session(session_data)
        
        # Mock session for demonstration
        from datetime import timedelta
        session = UserSession(
            user_id=user.id,
            session_token="mock_session_token",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_hours),
            remember_me=remember_me
        )
        
        # Create JWT tokens
        token_data = {
            "sub": user.id,
            "username": user.username,
            "session_token": session.session_token
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": user.id})
        
        # Update user login info
        # TODO: Update user last_login and login_count in database
        
        logger.info(f"Created session for user {user.id}")
        
        return access_token, refresh_token, session
    
    except Exception as e:
        logger.error(f"Error creating user session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


async def revoke_session(session_token: str) -> bool:
    """Revoke a user session."""
    try:
        # TODO: Update session status in database
        # result = await database.execute(
        #     "UPDATE user_sessions SET status = 'revoked', revoked_at = :revoked_at WHERE session_token = :token",
        #     {"token": session_token, "revoked_at": datetime.now()}
        # )
        
        logger.info(f"Revoked session {session_token}")
        return True
    
    except Exception as e:
        logger.error(f"Error revoking session: {e}")
        return False


async def revoke_all_user_sessions(user_id: str, except_session: Optional[str] = None) -> int:
    """Revoke all sessions for a user except optionally one."""
    try:
        # TODO: Update all user sessions in database
        # query = "UPDATE user_sessions SET status = 'revoked', revoked_at = :revoked_at WHERE user_id = :user_id AND status = 'active'"
        # params = {"user_id": user_id, "revoked_at": datetime.now()}
        
        # if except_session:
        #     query += " AND session_token != :except_session"
        #     params["except_session"] = except_session
        
        # result = await database.execute(query, params)
        # revoked_count = result.rowcount
        
        logger.info(f"Revoked all sessions for user {user_id}")
        return 1  # Mock return value
    
    except Exception as e:
        logger.error(f"Error revoking user sessions: {e}")
        return 0


# Dependency aliases for cleaner imports
get_current_user_optional = get_current_user
get_current_user_required = require_authenticated_user