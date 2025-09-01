# File: security/policies/password_policy.py
"""
Password Policy Implementation
Enforces secure password requirements and validation rules
"""

import re
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PasswordStrength(Enum):
    """Password strength levels"""
    WEAK = 1
    FAIR = 2
    GOOD = 3
    STRONG = 4
    VERY_STRONG = 5


@dataclass
class PasswordPolicyConfig:
    """Password policy configuration"""
    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special_chars: bool = True
    min_special_chars: int = 1
    forbidden_sequences: List[str] = None
    max_repeated_chars: int = 3
    password_history_count: int = 12
    password_expiry_days: int = 90
    account_lockout_attempts: int = 5
    lockout_duration_minutes: int = 30
    
    def __post_init__(self):
        if self.forbidden_sequences is None:
            self.forbidden_sequences = [
                "123456", "654321", "abcdef", "fedcba",
                "qwerty", "asdfgh", "zxcvbn", "password"
            ]


class PasswordValidator:
    """Validates passwords against policy requirements"""
    
    def __init__(self, config: PasswordPolicyConfig = None):
        self.config = config or PasswordPolicyConfig()
        self.special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
    def validate_password(self, password: str, username: str = None) -> Tuple[bool, List[str]]:
        """
        Validate password against policy requirements
        
        Args:
            password: Password to validate
            username: Username to check for similarity
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Length validation
        if len(password) < self.config.min_length:
            errors.append(f"Password must be at least {self.config.min_length} characters long")
        
        if len(password) > self.config.max_length:
            errors.append(f"Password must not exceed {self.config.max_length} characters")
        
        # Character requirement validation
        if self.config.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
            
        if self.config.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
            
        if self.config.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
            
        if self.config.require_special_chars:
            special_count = sum(1 for char in password if char in self.special_chars)
            if special_count < self.config.min_special_chars:
                errors.append(f"Password must contain at least {self.config.min_special_chars} special character(s)")
        
        # Check for forbidden sequences
        password_lower = password.lower()
        for sequence in self.config.forbidden_sequences:
            if sequence.lower() in password_lower:
                errors.append(f"Password contains forbidden sequence: {sequence}")
        
        # Check for repeated characters
        if self._has_excessive_repeated_chars(password):
            errors.append(f"Password cannot have more than {self.config.max_repeated_chars} repeated characters in sequence")
        
        # Check username similarity
        if username and self._is_similar_to_username(password, username):
            errors.append("Password cannot be similar to username")
        
        return len(errors) == 0, errors
    
    def calculate_strength(self, password: str) -> PasswordStrength:
        """Calculate password strength score"""
        score = 0
        
        # Length scoring
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Character diversity
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;\':",./<>?]', password):
            score += 1
        
        # Pattern complexity
        if not self._has_common_patterns(password):
            score += 1
        
        # Map score to strength
        if score <= 2:
            return PasswordStrength.WEAK
        elif score <= 4:
            return PasswordStrength.FAIR
        elif score <= 6:
            return PasswordStrength.GOOD
        elif score <= 7:
            return PasswordStrength.STRONG
        else:
            return PasswordStrength.VERY_STRONG
    
    def _has_excessive_repeated_chars(self, password: str) -> bool:
        """Check for excessive repeated characters"""
        count = 1
        for i in range(1, len(password)):
            if password[i] == password[i-1]:
                count += 1
                if count > self.config.max_repeated_chars:
                    return True
            else:
                count = 1
        return False
    
    def _is_similar_to_username(self, password: str, username: str) -> bool:
        """Check if password is too similar to username"""
        password_lower = password.lower()
        username_lower = username.lower()
        
        # Direct containment
        if username_lower in password_lower or password_lower in username_lower:
            return True
        
        # Reverse containment
        if username_lower[::-1] in password_lower:
            return True
        
        return False
    
    def _has_common_patterns(self, password: str) -> bool:
        """Check for common patterns"""
        patterns = [
            r'(.)\1{2,}',  # Repeated characters
            r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
            r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
            r'(qwe|wer|ert|rty|tyu|yui|uio|iop|asd|sdf|dfg|fgh|ghj|hjk|jkl|zxc|xcv|cvb|vbn|bnm)',  # Keyboard patterns
        ]
        
        for pattern in patterns:
            if re.search(pattern, password.lower()):
                return True
        return False


class PasswordGenerator:
    """Generates secure passwords"""
    
    def __init__(self, config: PasswordPolicyConfig = None):
        self.config = config or PasswordPolicyConfig()
    
    def generate_password(self, length: int = None) -> str:
        """Generate a secure password"""
        if length is None:
            length = max(self.config.min_length, 16)
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        # Ensure required characters
        password_chars = []
        if self.config.require_lowercase:
            password_chars.append(secrets.choice(lowercase))
        if self.config.require_uppercase:
            password_chars.append(secrets.choice(uppercase))
        if self.config.require_digits:
            password_chars.append(secrets.choice(digits))
        if self.config.require_special_chars:
            for _ in range(self.config.min_special_chars):
                password_chars.append(secrets.choice(special))
        
        # Fill remaining length with random characters
        all_chars = lowercase + uppercase + digits + special
        remaining_length = length - len(password_chars)
        
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)


class PasswordManager:
    """Manages password policies and user passwords"""
    
    def __init__(self, config: PasswordPolicyConfig = None):
        self.config = config or PasswordPolicyConfig()
        self.validator = PasswordValidator(self.config)
        self.generator = PasswordGenerator(self.config)
        self.password_history: Dict[str, List[str]] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.locked_accounts: Dict[str, datetime] = {}
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password with salt using PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        password_hash, _ = self.hash_password(password, salt)
        return secrets.compare_digest(password_hash, stored_hash)
    
    def can_use_password(self, user_id: str, new_password: str) -> Tuple[bool, List[str]]:
        """Check if password can be used (not in history)"""
        if user_id not in self.password_history:
            return True, []
        
        errors = []
        user_history = self.password_history[user_id]
        
        for old_password_hash in user_history:
            # In real implementation, you'd store salt with hash
            # This is simplified for demonstration
            if hashlib.sha256(new_password.encode()).hexdigest() == old_password_hash:
                errors.append("Password has been used recently and cannot be reused")
                break
        
        return len(errors) == 0, errors
    
    def add_to_password_history(self, user_id: str, password: str):
        """Add password to user's history"""
        if user_id not in self.password_history:
            self.password_history[user_id] = []
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.password_history[user_id].append(password_hash)
        
        # Keep only recent passwords
        if len(self.password_history[user_id]) > self.config.password_history_count:
            self.password_history[user_id] = self.password_history[user_id][-self.config.password_history_count:]
    
    def is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if user_id not in self.locked_accounts:
            return False
        
        locked_until = self.locked_accounts[user_id]
        if datetime.utcnow() > locked_until:
            # Unlock account
            del self.locked_accounts[user_id]
            if user_id in self.failed_attempts:
                del self.failed_attempts[user_id]
            return False
        
        return True
    
    def record_failed_attempt(self, user_id: str):
        """Record a failed login attempt"""
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
        
        self.failed_attempts[user_id].append(datetime.utcnow())
        
        # Remove old attempts (older than lockout duration)
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.config.lockout_duration_minutes)
        self.failed_attempts[user_id] = [
            attempt for attempt in self.failed_attempts[user_id]
            if attempt > cutoff_time
        ]
        
        # Check if account should be locked
        if len(self.failed_attempts[user_id]) >= self.config.account_lockout_attempts:
            self.locked_accounts[user_id] = datetime.utcnow() + timedelta(
                minutes=self.config.lockout_duration_minutes
            )
    
    def clear_failed_attempts(self, user_id: str):
        """Clear failed attempts for successful login"""
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
    
    def is_password_expired(self, last_changed: datetime) -> bool:
        """Check if password has expired"""
        if self.config.password_expiry_days <= 0:
            return False
        
        expiry_date = last_changed + timedelta(days=self.config.password_expiry_days)
        return datetime.utcnow() > expiry_date
    
    def set_password(self, user_id: str, password: str, username: str = None) -> Tuple[bool, List[str], Optional[Tuple[str, str]]]:
        """
        Set password for user with full validation
        
        Returns:
            Tuple of (success, errors, (password_hash, salt))
        """
        # Check if account is locked
        if self.is_account_locked(user_id):
            return False, ["Account is locked due to too many failed attempts"], None
        
        # Validate password
        is_valid, validation_errors = self.validator.validate_password(password, username)
        if not is_valid:
            return False, validation_errors, None
        
        # Check password history
        can_use, history_errors = self.can_use_password(user_id, password)
        if not can_use:
            return False, history_errors, None
        
        # Hash password
        password_hash, salt = self.hash_password(password)
        
        # Add to history
        self.add_to_password_history(user_id, password)
        
        return True, [], (password_hash, salt)


# Example usage and testing
if __name__ == "__main__":
    # Initialize password manager
    config = PasswordPolicyConfig(
        min_length=12,
        require_special_chars=True,
        min_special_chars=2
    )
    
    password_manager = PasswordManager(config)
    
    # Test password generation
    generated_password = password_manager.generator.generate_password(16)
    print(f"Generated password: {generated_password}")
    
    # Test password validation
    test_password = "MySecureP@ssw0rd123!"
    is_valid, errors = password_manager.validator.validate_password(test_password, "testuser")
    
    print(f"\nPassword validation for '{test_password}':")
    print(f"Valid: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Test password strength
    strength = password_manager.validator.calculate_strength(test_password)
    print(f"Password strength: {strength.name}")
    
    # Test password setting
    success, errors, hash_salt = password_manager.set_password("user123", test_password, "testuser")
    print(f"\nSet password result: {success}")
    if not success:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    elif hash_salt:
        print(f"Password hash: {hash_salt[0][:20]}...")
        print(f"Salt: {hash_salt[1][:20]}...")