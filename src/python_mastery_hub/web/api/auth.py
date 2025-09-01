# Location: src/python_mastery_hub/web/api/auth.py

"""
Authentication API Router

Handles user authentication, registration, password management,
email verification, and session management endpoints.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from python_mastery_hub.web.models.user import (
    User, UserCreate, UserLogin, UserUpdate, UserResponse,
    PasswordReset, PasswordResetConfirm, EmailVerification
)
from python_mastery_hub.web.models.session import UserSession, SessionListItem
from python_mastery_hub.web.middleware.auth import (
    get_current_user, require_authenticated_user,
    create_user_session, revoke_session, revoke_all_user_sessions
)
from python_mastery_hub.web.middleware.rate_limiting import rate_limit
from python_mastery_hub.web.middleware.error_handling import (
    AuthenticationException, ValidationException, BusinessLogicException
)
from python_mastery_hub.web.services.auth_service import AuthService
from python_mastery_hub.web.services.email_service import EmailService
from python_mastery_hub.utils.logging_config import get_logger
from python_mastery_hub.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()

# Security
security = HTTPBearer(auto_error=False)


# Response Models
class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    """Change password request model."""
    current_password: str
    new_password: str
    confirm_new_password: str


class ProfileUpdateResponse(BaseModel):
    """Profile update response model."""
    message: str
    user: UserResponse


# Dependencies
async def get_auth_service() -> AuthService:
    """Get authentication service."""
    return AuthService()


async def get_email_service() -> EmailService:
    """Get email service."""
    return EmailService()


# Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@rate_limit(limit=3, window=3600)  # 3 registrations per hour
async def register(
    user_data: UserCreate,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Register a new user account."""
    try:
        # Register user
        user, verification_token = await auth_service.register_user(user_data)
        
        # Send verification email
        if verification_token:
            try:
                await email_service.send_verification_email(user, verification_token)
                logger.info(f"Verification email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send verification email: {e}")
                # Don't fail registration if email fails
        
        # Send welcome email
        try:
            await email_service.send_welcome_email(user)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
        
        logger.info(f"User registered successfully: {user.username}")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login,
            profile=user.profile,
            preferences=user.preferences,
            stats=user.stats
        )
    
    except (ValidationException, BusinessLogicException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=LoginResponse)
@rate_limit(limit=5, window=300)  # 5 login attempts per 5 minutes
async def login(
    login_data: UserLogin,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return tokens."""
    try:
        # Authenticate user
        user, access_token, refresh_token = await auth_service.authenticate_user(login_data)
        
        # Create session
        access_token, refresh_token, session = await create_user_session(
            user, 
            request, 
            login_data.remember_me,
            expires_hours=168 if login_data.remember_me else 24  # 7 days vs 24 hours
        )
        
        # Set secure cookies
        cookie_settings = {
            "httponly": True,
            "secure": settings.environment == "production",
            "samesite": "lax"
        }
        
        if login_data.remember_me:
            cookie_settings["max_age"] = 7 * 24 * 3600  # 7 days
        
        response.set_cookie("access_token", access_token, **cookie_settings)
        response.set_cookie("refresh_token", refresh_token, **cookie_settings)
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                last_login=user.last_login,
                profile=user.profile,
                preferences=user.preferences,
                stats=user.stats
            )
        )
    
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token."""
    try:
        new_access_token = await auth_service.refresh_access_token(refresh_request.refresh_token)
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """Logout user and invalidate session."""
    try:
        # Get session token from request
        session_token = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Would extract session token from JWT in real implementation
            session_token = "current_session_token"
        
        # Revoke session
        if session_token:
            await revoke_session(session_token)
        
        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        logger.info(f"User logged out: {current_user.username if current_user else 'unknown'}")
        
        return {"message": "Logged out successfully"}
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/verify-email")
async def verify_email(
    verification: EmailVerification,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify user email address."""
    try:
        success = await auth_service.verify_email(verification.token)
        
        if success:
            return {"message": "Email verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
    
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


@router.post("/forgot-password")
@rate_limit(limit=3, window=3600)  # 3 requests per hour
async def forgot_password(
    password_reset: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Initiate password reset process."""
    try:
        reset_token = await auth_service.initiate_password_reset(password_reset.email)
        
        # Send reset email (even if user doesn't exist for security)
        if reset_token and reset_token != "reset_token_sent":
            # Get user for email (in real implementation)
            # user = await get_user_by_email(password_reset.email)
            # if user:
            #     await email_service.send_password_reset_email(user, reset_token)
            pass
        
        # Always return success to avoid email enumeration
        return {"message": "If an account with that email exists, a password reset link has been sent"}
    
    except Exception as e:
        logger.error(f"Password reset initiation error: {e}")
        # Return success even on error to avoid revealing information
        return {"message": "If an account with that email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password using reset token."""
    try:
        success = await auth_service.reset_password(reset_data)
        
        if success:
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    
    except (AuthenticationException, ValidationException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/change-password")
async def change_password(
    password_change: ChangePasswordRequest,
    current_user: User = Depends(require_authenticated_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change user password (requires current password)."""
    try:
        # Validate confirm password
        if password_change.new_password != password_change.confirm_new_password:
            raise ValidationException("New passwords do not match")
        
        success = await auth_service.change_password(
            current_user.id,
            password_change.current_password,
            password_change.new_password
        )
        
        if success:
            # Revoke all other sessions for security
            await revoke_all_user_sessions(current_user.id)
            
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
    
    except (AuthenticationException, ValidationException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(require_authenticated_user)
):
    """Get current user profile."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        profile=current_user.profile,
        preferences=current_user.preferences,
        stats=current_user.stats
    )


@router.put("/me", response_model=ProfileUpdateResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(require_authenticated_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update current user profile."""
    try:
        # TODO: Implement user profile update
        # updated_user = await auth_service.update_user_profile(current_user.id, user_update)
        
        logger.info(f"Profile updated for user: {current_user.username}")
        
        return ProfileUpdateResponse(
            message="Profile updated successfully",
            user=UserResponse(
                id=current_user.id,
                username=current_user.username,
                email=current_user.email,
                full_name=current_user.full_name,
                role=current_user.role,
                is_active=current_user.is_active,
                is_verified=current_user.is_verified,
                created_at=current_user.created_at,
                last_login=current_user.last_login,
                profile=current_user.profile,
                preferences=current_user.preferences,
                stats=current_user.stats
            )
        )
    
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.get("/sessions", response_model=List[SessionListItem])
async def get_user_sessions(
    current_user: User = Depends(require_authenticated_user)
):
    """Get user's active sessions."""
    try:
        # TODO: Get user sessions from database
        # sessions = await get_user_sessions_from_db(current_user.id)
        
        # Mock sessions for demonstration
        sessions = [
            SessionListItem(
                id="session1",
                device_info={
                    "browser": "Chrome",
                    "operating_system": "Windows 10",
                    "ip_address": "192.168.1.100"
                },
                created_at=datetime.now() - timedelta(hours=2),
                last_accessed=datetime.now() - timedelta(minutes=5),
                is_current=True,
                location="New York, US"
            )
        ]
        
        return sessions
    
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )


@router.delete("/sessions/{session_id}")
async def revoke_user_session(
    session_id: str,
    current_user: User = Depends(require_authenticated_user)
):
    """Revoke a specific user session."""
    try:
        # TODO: Verify session belongs to user and revoke it
        # success = await revoke_user_specific_session(current_user.id, session_id)
        success = True
        
        if success:
            return {"message": "Session revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session revocation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke session"
        )


@router.delete("/sessions")
async def revoke_all_sessions(
    current_user: User = Depends(require_authenticated_user)
):
    """Revoke all user sessions except current one."""
    try:
        # Get current session token to exclude it
        current_session_token = "current_session_token"  # Would extract from JWT
        
        revoked_count = await revoke_all_user_sessions(
            current_user.id, 
            except_session=current_session_token
        )
        
        return {
            "message": f"Revoked {revoked_count} session(s) successfully",
            "revoked_count": revoked_count
        }
    
    except Exception as e:
        logger.error(f"Revoke all sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke sessions"
        )


@router.post("/resend-verification")
@rate_limit(limit=3, window=3600)  # 3 requests per hour
async def resend_verification_email(
    current_user: User = Depends(require_authenticated_user),
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Resend email verification."""
    try:
        if current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Generate new verification token
        verification_token = await auth_service.token_service.create_auth_token(
            current_user.id,
            "email_verification",
            expires_hours=24
        )
        
        # Send verification email
        await email_service.send_verification_email(current_user, verification_token.token)
        
        return {"message": "Verification email sent successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )


@router.get("/check-username/{username}")
async def check_username_availability(username: str):
    """Check if username is available."""
    try:
        # TODO: Check username availability in database
        # is_available = await check_username_in_db(username)
        is_available = True  # Mock
        
        return {
            "username": username,
            "available": is_available,
            "message": "Username is available" if is_available else "Username is already taken"
        }
    
    except Exception as e:
        logger.error(f"Username check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check username availability"
        )


@router.get("/check-email/{email}")
async def check_email_availability(email: str):
    """Check if email is available."""
    try:
        # TODO: Check email availability in database
        # is_available = await check_email_in_db(email)
        is_available = True  # Mock
        
        return {
            "email": email,
            "available": is_available,
            "message": "Email is available" if is_available else "Email is already registered"
        }
    
    except Exception as e:
        logger.error(f"Email check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check email availability"
        )