# src/python_mastery_hub/utils/security_utils.py
"""
Security Helper Functions - Security and Authentication Utilities

Provides security utilities including password hashing, token generation,
input sanitization, and authentication helpers for the learning platform.
"""

import hashlib
import secrets
import hmac
import base64
import re
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
import logging
from dataclasses import dataclass
from urllib.parse import quote, unquote
import bcrypt

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Base exception for security-related errors."""
    pass


class AuthenticationError(SecurityError):
    """Exception raised for authentication failures."""
    pass


class AuthorizationError(SecurityError):
    """Exception raised for authorization failures."""
    pass


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digits: bool = True
    password_require_special: bool = True
    token_expiry_hours: int = 24
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 120


class PasswordManager:
    """Manages password hashing and validation."""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig(secret_key=self._generate_secret_key())
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        if not self.validate_password_strength(password)[0]:
            raise SecurityError("Password does not meet security requirements")
        
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed_password: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.warning(f"Password verification error: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength against security policy.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check length
        if len(password) < self.config.password_min_length:
            errors.append(f"Password must be at least {self.config.password_min_length} characters long")
        
        # Check character requirements
        if self.config.password_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.config.password_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.config.password_require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.config.password_require_special and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>?]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common weak patterns
        if password.lower() in ['password', '123456', 'qwerty', 'admin', 'letmein']:
            errors.append("Password is too common and easily guessable")
        
        # Check for sequential characters
        if self._has_sequential_chars(password):
            errors.append("Password should not contain sequential characters")
        
        return len(errors) == 0, errors
    
    def generate_secure_password(self, length: int = 12) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Length of password to generate
            
        Returns:
            Secure random password
        """
        if length < self.config.password_min_length:
            length = self.config.password_min_length
        
        # Character sets
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        # Ensure at least one character from each required set
        password_chars = []
        
        if self.config.password_require_lowercase:
            password_chars.append(secrets.choice(lowercase))
        if self.config.password_require_uppercase:
            password_chars.append(secrets.choice(uppercase))
        if self.config.password_require_digits:
            password_chars.append(secrets.choice(digits))
        if self.config.password_require_special:
            password_chars.append(secrets.choice(special))
        
        # Fill remaining length with random characters
        all_chars = lowercase + uppercase + digits + special
        remaining_length = length - len(password_chars)
        
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(all_chars))
        
        # Shuffle the password characters
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters in password."""
        sequences = ['abcdefghijklmnopqrstuvwxyz', '0123456789', 'qwertyuiopasdfghjklzxcvbnm']
        
        for sequence in sequences:
            for i in range(len(sequence) - 2):
                if sequence[i:i+3].lower() in password.lower():
                    return True
                if sequence[i:i+3][::-1].lower() in password.lower():
                    return True
        
        return False
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key."""
        return secrets.token_urlsafe(32)


class TokenManager:
    """Manages secure token generation and validation."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode('utf-8')
    
    def generate_token(
        self, 
        payload: Dict[str, Any], 
        expires_in_hours: int = 24
    ) -> str:
        """
        Generate a secure token with payload.
        
        Args:
            payload: Data to include in token
            expires_in_hours: Token expiration time
            
        Returns:
            Secure token string
        """
        # Add expiration time
        payload['exp'] = time.time() + (expires_in_hours * 3600)
        payload['iat'] = time.time()
        
        # Encode payload
        payload_json = json.dumps(payload, sort_keys=True)
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8')
        
        # Generate signature
        signature = hmac.new(
            self.secret_key,
            payload_b64.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8')
        
        return f"{payload_b64}.{signature_b64}"
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify and decode token.
        
        Args:
            token: Token to verify
            
        Returns:
            Tuple of (is_valid, payload)
        """
        try:
            # Split token
            if '.' not in token:
                return False, None
            
            payload_b64, signature_b64 = token.split('.', 1)
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key,
                payload_b64.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            provided_signature = base64.urlsafe_b64decode(signature_b64)
            
            if not hmac.compare_digest(expected_signature, provided_signature):
                return False, None
            
            # Decode payload
            payload_json = base64.urlsafe_b64decode(payload_b64).decode('utf-8')
            payload = json.loads(payload_json)
            
            # Check expiration
            if 'exp' in payload and time.time() > payload['exp']:
                return False, None
            
            return True, payload
            
        except Exception as e:
            logger.warning(f"Token verification error: {e}")
            return False, None
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF protection token."""
        return secrets.token_urlsafe(32)
    
    def generate_api_key(self, prefix: str = "") -> str:
        """Generate API key."""
        key = secrets.token_urlsafe(32)
        return f"{prefix}{key}" if prefix else key


class InputSanitizer:
    """Sanitizes user input to prevent security vulnerabilities."""
    
    @staticmethod
    def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(text, str):
            return ""
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
        
        # Strip whitespace
        sanitized = sanitized.strip()
        
        # Truncate if needed
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def sanitize_html(html: str) -> str:
        """
        Basic HTML sanitization (removes script tags and dangerous attributes).
        
        Args:
            html: HTML content to sanitize
            
        Returns:
            Sanitized HTML
        """
        if not isinstance(html, str):
            return ""
        
        # Remove script tags and their content
        html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html, flags=re.IGNORECASE)
        
        # Remove dangerous attributes
        dangerous_attrs = ['onload', 'onclick', 'onmouseover', 'onerror', 'javascript:']
        for attr in dangerous_attrs:
            html = re.sub(rf'{attr}[^>]*', '', html, flags=re.IGNORECASE)
        
        return html
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe file operations.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        if not isinstance(filename, str):
            return "unnamed"
        
        # Remove path separators and dangerous characters
        dangerous_chars = '<>:"/\\|?*'
        sanitized = ''.join(char for char in filename if char not in dangerous_chars)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure not empty
        if not sanitized:
            sanitized = "unnamed"
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            name = name[:250 - len(ext)]
            sanitized = f"{name}.{ext}" if ext else name
        
        return sanitized
    
    @staticmethod
    def escape_sql(value: str) -> str:
        """
        Escape string for SQL (basic protection).
        
        Args:
            value: String to escape
            
        Returns:
            Escaped string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Replace single quotes with two single quotes
        return value.replace("'", "''")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid email format
        """
        if not isinstance(email, str):
            return False
        
        # Basic email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, List[str]]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not isinstance(username, str):
            return False, ["Username must be a string"]
        
        # Length check
        if len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        if len(username) > 50:
            errors.append("Username must be no more than 50 characters long")
        
        # Character check
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            errors.append("Username can only contain letters, numbers, underscores, dots, and hyphens")
        
        # Must start with alphanumeric
        if username and not username[0].isalnum():
            errors.append("Username must start with a letter or number")
        
        # Reserved usernames
        reserved = ['admin', 'root', 'user', 'test', 'guest', 'api', 'www', 'mail', 'ftp']
        if username.lower() in reserved:
            errors.append("Username is reserved")
        
        return len(errors) == 0, errors


class RateLimiter:
    """Rate limiting for API endpoints and user actions."""
    
    def __init__(self):
        self._attempts: Dict[str, List[float]] = {}
        self._lock = {}
    
    def is_rate_limited(
        self, 
        identifier: str, 
        max_attempts: int, 
        window_minutes: int
    ) -> bool:
        """
        Check if identifier is rate limited.
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_attempts: Maximum attempts allowed
            window_minutes: Time window in minutes
            
        Returns:
            True if rate limited
        """
        now = time.time()
        window_seconds = window_minutes * 60
        cutoff_time = now - window_seconds
        
        # Clean old attempts
        if identifier in self._attempts:
            self._attempts[identifier] = [
                attempt_time for attempt_time in self._attempts[identifier]
                if attempt_time > cutoff_time
            ]
        else:
            self._attempts[identifier] = []
        
        # Check if over limit
        return len(self._attempts[identifier]) >= max_attempts
    
    def record_attempt(self, identifier: str) -> None:
        """Record an attempt for the identifier."""
        now = time.time()
        
        if identifier not in self._attempts:
            self._attempts[identifier] = []
        
        self._attempts[identifier].append(now)
    
    def reset_attempts(self, identifier: str) -> None:
        """Reset attempts for identifier."""
        if identifier in self._attempts:
            del self._attempts[identifier]
    
    def get_attempt_count(self, identifier: str, window_minutes: int) -> int:
        """Get current attempt count for identifier."""
        now = time.time()
        window_seconds = window_minutes * 60
        cutoff_time = now - window_seconds
        
        if identifier not in self._attempts:
            return 0
        
        recent_attempts = [
            attempt_time for attempt_time in self._attempts[identifier]
            if attempt_time > cutoff_time
        ]
        
        return len(recent_attempts)


class SessionManager:
    """Manages user sessions securely."""
    
    def __init__(self, token_manager: TokenManager, timeout_minutes: int = 120):
        self.token_manager = token_manager
        self.timeout_minutes = timeout_minutes
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """
        Create new user session.
        
        Args:
            user_id: User identifier
            user_data: Additional session data
            
        Returns:
            Session token
        """
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            'user_id': user_id,
            'created_at': time.time(),
            'last_activity': time.time(),
            'data': user_data
        }
        
        self._sessions[session_id] = session_data
        
        # Generate session token
        token_payload = {
            'session_id': session_id,
            'user_id': user_id
        }
        
        return self.token_manager.generate_token(token_payload, expires_in_hours=self.timeout_minutes / 60)
    
    def validate_session(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate session token.
        
        Args:
            token: Session token
            
        Returns:
            Tuple of (is_valid, session_data)
        """
        # Verify token
        is_valid, payload = self.token_manager.verify_token(token)
        if not is_valid or not payload:
            return False, None
        
        session_id = payload.get('session_id')
        if not session_id or session_id not in self._sessions:
            return False, None
        
        session = self._sessions[session_id]
        
        # Check session timeout
        if time.time() - session['last_activity'] > (self.timeout_minutes * 60):
            self.destroy_session(token)
            return False, None
        
        # Update last activity
        session['last_activity'] = time.time()
        
        return True, session
    
    def destroy_session(self, token: str) -> bool:
        """
        Destroy session.
        
        Args:
            token: Session token
            
        Returns:
            True if session was destroyed
        """
        is_valid, payload = self.token_manager.verify_token(token)
        if not is_valid or not payload:
            return False
        
        session_id = payload.get('session_id')
        if session_id and session_id in self._sessions:
            del self._sessions[session_id]
            return True
        
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions."""
        now = time.time()
        timeout_seconds = self.timeout_minutes * 60
        
        expired_sessions = []
        for session_id, session in self._sessions.items():
            if now - session['last_activity'] > timeout_seconds:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        return len(expired_sessions)


# Security utility functions
def generate_secure_random(length: int = 32) -> str:
    """Generate cryptographically secure random string."""
    return secrets.token_urlsafe(length)


def constant_time_compare(a: str, b: str) -> bool:
    """Compare strings in constant time to prevent timing attacks."""
    return hmac.compare_digest(a.encode('utf-8'), b.encode('utf-8'))


def hash_data(data: str, salt: Optional[str] = None) -> str:
    """Hash data with optional salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    combined = f"{data}{salt}"
    hash_obj = hashlib.sha256(combined.encode('utf-8'))
    return f"{salt}:{hash_obj.hexdigest()}"


def verify_hash(data: str, hashed_data: str) -> bool:
    """Verify data against hash."""
    try:
        salt, hash_value = hashed_data.split(':', 1)
        expected_hash = hash_data(data, salt)
        return constant_time_compare(expected_hash, hashed_data)
    except ValueError:
        return False


def encode_data(data: Dict[str, Any], key: str) -> str:
    """Encode data with simple encryption."""
    json_data = json.dumps(data)
    encoded = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    
    # Simple XOR encryption with key
    encrypted = []
    for i, char in enumerate(encoded):
        key_char = key[i % len(key)]
        encrypted.append(chr(ord(char) ^ ord(key_char)))
    
    return base64.b64encode(''.join(encrypted).encode('utf-8')).decode('utf-8')


def decode_data(encoded_data: str, key: str) -> Optional[Dict[str, Any]]:
    """Decode encrypted data."""
    try:
        encrypted = base64.b64decode(encoded_data).decode('utf-8')
        
        # Decrypt with XOR
        decrypted = []
        for i, char in enumerate(encrypted):
            key_char = key[i % len(key)]
            decrypted.append(chr(ord(char) ^ ord(key_char)))
        
        decoded = base64.b64decode(''.join(decrypted)).decode('utf-8')
        return json.loads(decoded)
    except Exception:
        return None


# Global instances
_security_config = SecurityConfig(secret_key=generate_secure_random())
password_manager = PasswordManager(_security_config)
token_manager = TokenManager(_security_config.secret_key)
rate_limiter = RateLimiter()
session_manager = SessionManager(token_manager)


# Convenience functions
def hash_password(password: str) -> str:
    """Hash password using default manager."""
    return password_manager.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password using default manager."""
    return password_manager.verify_password(password, hashed_password)


def generate_token(payload: Dict[str, Any], expires_in_hours: int = 24) -> str:
    """Generate token using default manager."""
    return token_manager.generate_token(payload, expires_in_hours)


def verify_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Verify token using default manager."""
    return token_manager.verify_token(token)


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize input using default sanitizer."""
    return InputSanitizer.sanitize_string(text, max_length)


def is_rate_limited(identifier: str, max_attempts: int, window_minutes: int) -> bool:
    """Check rate limit using default limiter."""
    return rate_limiter.is_rate_limited(identifier, max_attempts, window_minutes)


def record_rate_limit_attempt(identifier: str) -> None:
    """Record rate limit attempt using default limiter."""
    rate_limiter.record_attempt(identifier)