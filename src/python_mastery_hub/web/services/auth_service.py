# Location: src/python_mastery_hub/web/services/auth_service.py

"""
Authentication Service

Handles user authentication, registration, password management,
session management, and security-related operations.
"""

import secrets
import hashlib
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError

from python_mastery_hub.web.models.user import (
    User, UserCreate, UserLogin, UserUpdate, 
    PasswordReset, PasswordResetConfirm, UserRole
)
from python_mastery_hub.web.models.session import UserSession, AuthToken, TokenType
from python_mastery_hub.web.middleware.auth import (
    hash_password, verify_password, create_access_token, 
    create_refresh_token, verify_token
)
from python_mastery_hub.web.middleware.error_handling import (
    AuthenticationException, ValidationException, 
    BusinessLogicException, ResourceNotFoundException
)
from python_mastery_hub.utils.logging_config import get_logger
from python_mastery_hub.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class PasswordService:
    """Service for password-related operations."""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength and return analysis."""
        analysis = {
            "is_valid": True,
            "score": 0,
            "issues": [],
            "suggestions": []
        }
        
        # Length check
        if len(password) < 8:
            analysis["is_valid"] = False
            analysis["issues"].append("Password must be at least 8 characters long")
        elif len(password) >= 12:
            analysis["score"] += 2
        else:
            analysis["score"] += 1
        
        # Character variety checks
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not has_lower:
            analysis["is_valid"] = False
            analysis["issues"].append("Password must contain lowercase letters")
        
        if not has_upper:
            analysis["is_valid"] = False
            analysis["issues"].append("Password must contain uppercase letters")
        
        if not has_digit:
            analysis["is_valid"] = False
            analysis["issues"].append("Password must contain numbers")
        
        if not has_special:
            analysis["suggestions"].append("Consider adding special characters for stronger security")
        else:
            analysis["score"] += 1
        
        # Common patterns check
        common_patterns = ["123456", "password", "qwerty", "abc123"]
        if any(pattern in password.lower() for pattern in common_patterns):
            analysis["score"] -= 2
            analysis["issues"].append("Password contains common patterns")
        
        # Repetition check
        if len(set(password)) < len(password) * 0.6:
            analysis["score"] -= 1
            analysis["suggestions"].append("Avoid repeating characters")
        
        # Final score adjustment
        analysis["score"] = max(0, min(5, analysis["score"]))
        
        if analysis["score"] >= 4:
            analysis["strength"] = "strong"
        elif analysis["score"] >= 2:
            analysis["strength"] = "medium"
        else:
            analysis["strength"] = "weak"
        
        return analysis
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a cryptographically secure password."""
        import string
        
        # Ensure we have at least one of each character type
        password_chars = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
            secrets.choice("!@#$%^&*()_+-=")
        ]
        
        # Fill the rest randomly
        all_chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        for _ in range(length - 4):
            password_chars.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password securely."""
        return hash_password(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return verify_password(plain_password, hashed_password)


class TokenService:
    """Service for token management."""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a cryptographically secure token."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate email verification token."""
        return TokenService.generate_token(32)
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate password reset token."""
        return TokenService.generate_token(32)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate API key."""
        prefix = "pmh_"  # Python Mastery Hub prefix
        key = TokenService.generate_token(40)
        return f"{prefix}{key}"
    
    @staticmethod
    async def create_auth_token(
        user_id: str,
        token_type: TokenType,
        expires_hours: int = 24,
        scope: Optional[list] = None,
        metadata: Optional[Dict] = None
    ) -> AuthToken:
        """Create an authentication token."""
        token = AuthToken(
            token=TokenService.generate_token(),
            token_type=token_type,
            user_id=user_id,
            expires_at=datetime.now() + timedelta(hours=expires_hours),
            scope=scope or [],
            metadata=metadata or {}
        )
        
        # TODO: Save token to database
        # await database.execute(
        #     "INSERT INTO auth_tokens (...) VALUES (...)",
        #     token.dict()
        # )
        
        return token
    
    @staticmethod
    async def validate_token(token: str, token_type: TokenType) -> Optional[AuthToken]:
        """Validate and retrieve token."""
        # TODO: Query database for token
        # token_data = await database.fetch_one(
        #     "SELECT * FROM auth_tokens WHERE token = :token AND token_type = :type",
        #     {"token": token, "type": token_type.value}
        # )
        
        # Mock validation for demonstration
        if token == "mock_verification_token":
            return AuthToken(
                token=token,
                token_type=token_type,
                user_id="mock_user_id",
                expires_at=datetime.now() + timedelta(hours=24)
            )
        
        return None
    
    @staticmethod
    async def revoke_token(token: str) -> bool:
        """Revoke a token."""
        try:
            # TODO: Update token in database
            # await database.execute(
            #     "UPDATE auth_tokens SET revoked_at = :revoked_at WHERE token = :token",
            #     {"token": token, "revoked_at": datetime.now()}
            # )
            
            logger.info(f"Token revoked: {token[:10]}...")
            return True
        
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False


class AuthService:
    """Main authentication service."""
    
    def __init__(self):
        self.password_service = PasswordService()
        self.token_service = TokenService()
    
    async def register_user(self, user_data: UserCreate) -> Tuple[User, str]:
        """Register a new user."""
        try:
            # Validate email format
            try:
                validate_email(user_data.email)
            except EmailNotValidError:
                raise ValidationException("Invalid email format")
            
            # Check if user already exists
            existing_user = await self._get_user_by_email(user_data.email)
            if existing_user:
                raise BusinessLogicException("User with this email already exists")
            
            existing_username = await self._get_user_by_username(user_data.username)
            if existing_username:
                raise BusinessLogicException("Username already taken")
            
            # Validate password strength
            password_analysis = self.password_service.validate_password_strength(user_data.password)
            if not password_analysis["is_valid"]:
                raise ValidationException(
                    "Password does not meet requirements",
                    {"issues": password_analysis["issues"]}
                )
            
            # Hash password
            hashed_password = self.password_service.hash_password(user_data.password)
            
            # Create user
            user = User(
                id=self._generate_user_id(),
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                role=UserRole.STUDENT,
                is_active=True,
                is_verified=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Generate verification token
            verification_token = await self.token_service.create_auth_token(
                user.id,
                TokenType.EMAIL_VERIFICATION,
                expires_hours=24
            )
            
            # TODO: Save user to database
            # await database.execute(
            #     "INSERT INTO users (...) VALUES (...)",
            #     {**user.dict(), "password_hash": hashed_password}
            # )
            
            logger.info(f"User registered successfully: {user.username}")
            
            return user, verification_token.token
        
        except (ValidationException, BusinessLogicException):
            raise
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise BusinessLogicException("Registration failed")
    
    async def authenticate_user(self, login_data: UserLogin) -> Tuple[User, str, str]:
        """Authenticate user and return tokens."""
        try:
            # Get user by username or email
            user = await self._get_user_by_username_or_email(login_data.username_or_email)
            if not user:
                raise AuthenticationException("Invalid credentials")
            
            # Check if user is active
            if not user.is_active:
                raise AuthenticationException("Account is deactivated")
            
            # Get password hash from database
            password_hash = await self._get_user_password_hash(user.id)
            if not password_hash:
                raise AuthenticationException("Invalid credentials")
            
            # Verify password
            if not self.password_service.verify_password(login_data.password, password_hash):
                # Log failed login attempt
                await self._log_failed_login(user.id, login_data.username_or_email)
                raise AuthenticationException("Invalid credentials")
            
            # Check for too many failed attempts
            if await self._is_account_locked(user.id):
                raise AuthenticationException("Account temporarily locked due to failed login attempts")
            
            # Create session and tokens
            session_token = self.token_service.generate_token()
            
            # Generate JWT tokens
            token_data = {
                "sub": user.id,
                "username": user.username,
                "session_token": session_token
            }
            
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token({"sub": user.id})
            
            # Update user login info
            await self._update_user_login_info(user.id)
            
            # Clear failed login attempts
            await self._clear_failed_login_attempts(user.id)
            
            logger.info(f"User authenticated successfully: {user.username}")
            
            return user, access_token, refresh_token
        
        except AuthenticationException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise AuthenticationException("Authentication failed")
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token."""
        try:
            # Verify refresh token
            payload = verify_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            
            if not user_id:
                raise AuthenticationException("Invalid refresh token")
            
            # Get user
            user = await self._get_user_by_id(user_id)
            if not user or not user.is_active:
                raise AuthenticationException("User not found or inactive")
            
            # Generate new access token
            token_data = {
                "sub": user.id,
                "username": user.username
            }
            
            new_access_token = create_access_token(token_data)
            
            logger.info(f"Access token refreshed for user: {user.username}")
            
            return new_access_token
        
        except AuthenticationException:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise AuthenticationException("Token refresh failed")
    
    async def verify_email(self, token: str) -> bool:
        """Verify user email with verification token."""
        try:
            # Validate token
            auth_token = await self.token_service.validate_token(token, TokenType.EMAIL_VERIFICATION)
            if not auth_token or not auth_token.is_valid:
                raise AuthenticationException("Invalid or expired verification token")
            
            # Update user verification status
            success = await self._update_user_verification_status(auth_token.user_id, True)
            
            if success:
                # Mark token as used
                auth_token.mark_used()
                await self.token_service.revoke_token(token)
                
                logger.info(f"Email verified for user: {auth_token.user_id}")
                return True
            
            return False
        
        except AuthenticationException:
            raise
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False
    
    async def initiate_password_reset(self, email: str) -> str:
        """Initiate password reset process."""
        try:
            # Validate email
            try:
                validate_email(email)
            except EmailNotValidError:
                raise ValidationException("Invalid email format")
            
            # Check if user exists
            user = await self._get_user_by_email(email)
            if not user:
                # Don't reveal if email exists for security
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return "reset_token_sent"  # Fake success
            
            # Check if user is active
            if not user.is_active:
                raise BusinessLogicException("Account is deactivated")
            
            # Generate reset token
            reset_token = await self.token_service.create_auth_token(
                user.id,
                TokenType.RESET_PASSWORD,
                expires_hours=1  # Short expiry for security
            )
            
            logger.info(f"Password reset initiated for user: {user.username}")
            
            return reset_token.token
        
        except (ValidationException, BusinessLogicException):
            raise
        except Exception as e:
            logger.error(f"Error initiating password reset: {e}")
            raise BusinessLogicException("Password reset failed")
    
    async def reset_password(self, reset_data: PasswordResetConfirm) -> bool:
        """Reset user password with reset token."""
        try:
            # Validate token
            auth_token = await self.token_service.validate_token(reset_data.token, TokenType.RESET_PASSWORD)
            if not auth_token or not auth_token.is_valid:
                raise AuthenticationException("Invalid or expired reset token")
            
            # Validate new password
            password_analysis = self.password_service.validate_password_strength(reset_data.new_password)
            if not password_analysis["is_valid"]:
                raise ValidationException(
                    "Password does not meet requirements",
                    {"issues": password_analysis["issues"]}
                )
            
            # Hash new password
            new_password_hash = self.password_service.hash_password(reset_data.new_password)
            
            # Update password
            success = await self._update_user_password(auth_token.user_id, new_password_hash)
            
            if success:
                # Mark token as used
                auth_token.mark_used()
                await self.token_service.revoke_token(reset_data.token)
                
                # Revoke all user sessions for security
                await self._revoke_all_user_sessions(auth_token.user_id)
                
                logger.info(f"Password reset completed for user: {auth_token.user_id}")
                return True
            
            return False
        
        except (AuthenticationException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return False
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password (requires current password)."""
        try:
            # Get current password hash
            current_hash = await self._get_user_password_hash(user_id)
            if not current_hash:
                raise AuthenticationException("User not found")
            
            # Verify current password
            if not self.password_service.verify_password(current_password, current_hash):
                raise AuthenticationException("Current password is incorrect")
            
            # Validate new password
            password_analysis = self.password_service.validate_password_strength(new_password)
            if not password_analysis["is_valid"]:
                raise ValidationException(
                    "Password does not meet requirements",
                    {"issues": password_analysis["issues"]}
                )
            
            # Check if new password is different
            if self.password_service.verify_password(new_password, current_hash):
                raise ValidationException("New password must be different from current password")
            
            # Hash new password
            new_password_hash = self.password_service.hash_password(new_password)
            
            # Update password
            success = await self._update_user_password(user_id, new_password_hash)
            
            if success:
                logger.info(f"Password changed for user: {user_id}")
                return True
            
            return False
        
        except (AuthenticationException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False
    
    # Private helper methods
    def _generate_user_id(self) -> str:
        """Generate unique user ID."""
        import uuid
        return str(uuid.uuid4())
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        # TODO: Query database
        return None
    
    async def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        # TODO: Query database
        return None
    
    async def _get_user_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Get user by username or email."""
        # TODO: Query database
        return None
    
    async def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        # TODO: Query database
        return None
    
    async def _get_user_password_hash(self, user_id: str) -> Optional[str]:
        """Get user password hash."""
        # TODO: Query database
        return None
    
    async def _update_user_login_info(self, user_id: str) -> bool:
        """Update user login information."""
        # TODO: Update database
        return True
    
    async def _update_user_verification_status(self, user_id: str, verified: bool) -> bool:
        """Update user verification status."""
        # TODO: Update database
        return True
    
    async def _update_user_password(self, user_id: str, password_hash: str) -> bool:
        """Update user password."""
        # TODO: Update database
        return True
    
    async def _log_failed_login(self, user_id: str, attempted_identifier: str) -> None:
        """Log failed login attempt."""
        # TODO: Log to database/security system
        logger.warning(f"Failed login attempt for user {user_id} with identifier {attempted_identifier}")
    
    async def _is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked due to failed attempts."""
        # TODO: Check database for failed attempts count and timing
        return False
    
    async def _clear_failed_login_attempts(self, user_id: str) -> None:
        """Clear failed login attempts for user."""
        # TODO: Clear from database
        pass
    
    async def _revoke_all_user_sessions(self, user_id: str) -> None:
        """Revoke all sessions for a user."""
        # TODO: Update all user sessions in database
        pass