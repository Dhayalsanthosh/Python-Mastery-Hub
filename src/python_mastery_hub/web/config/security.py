# Location: src/python_mastery_hub/web/config/security.py

"""
Security Configuration

Manages security settings, encryption keys, password policies,
session management, and security-related configurations.
"""

import secrets
import hashlib
from typing import Dict, List, Optional, Any
from datetime import timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from python_mastery_hub.core.config import get_settings
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PasswordPolicy:
    """Password policy configuration and validation."""
    
    def __init__(self):
        self.min_length = getattr(settings, 'password_min_length', 8)
        self.max_length = getattr(settings, 'password_max_length', 128)
        self.require_uppercase = getattr(settings, 'password_require_uppercase', True)
        self.require_lowercase = getattr(settings, 'password_require_lowercase', True)
        self.require_digits = getattr(settings, 'password_require_digits', True)
        self.require_special = getattr(settings, 'password_require_special', False)
        self.forbidden_passwords = self._load_forbidden_passwords()
        self.max_password_age_days = getattr(settings, 'password_max_age_days', 90)
        self.password_history_count = getattr(settings, 'password_history_count', 5)
    
    def _load_forbidden_passwords(self) -> List[str]:
        """Load list of commonly used passwords to forbid."""
        return [
            'password', 'password123', '123456', '123456789', 'qwerty',
            'abc123', 'password1', 'admin', 'letmein', 'welcome',
            'monkey', '1234567890', 'iloveyou', 'princess', 'rockyou',
            'football', 'baseball', 'welcome123', 'ninja', 'mustang'
        ]
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password against policy."""
        issues = []
        score = 0
        
        # Length check
        if len(password) < self.min_length:
            issues.append(f"Password must be at least {self.min_length} characters long")
        elif len(password) >= self.min_length:
            score += 1
        
        if len(password) > self.max_length:
            issues.append(f"Password must not exceed {self.max_length} characters")
        
        # Character requirements
        if self.require_uppercase and not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        elif any(c.isupper() for c in password):
            score += 1
        
        if self.require_lowercase and not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        elif any(c.islower() for c in password):
            score += 1
        
        if self.require_digits and not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        elif any(c.isdigit() for c in password):
            score += 1
        
        if self.require_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                issues.append("Password must contain at least one special character")
        elif any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        
        # Common password check
        if password.lower() in [p.lower() for p in self.forbidden_passwords]:
            issues.append("Password is too common and easily guessable")
            score = max(0, score - 2)
        
        # Calculate strength
        if score >= 4:
            strength = "strong"
        elif score >= 2:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'strength': strength,
            'score': score
        }


class SessionPolicy:
    """Session management policy configuration."""
    
    def __init__(self):
        self.session_timeout_minutes = getattr(settings, 'session_timeout_minutes', 30)
        self.remember_me_duration_days = getattr(settings, 'remember_me_duration_days', 30)
        self.max_concurrent_sessions = getattr(settings, 'max_concurrent_sessions', 5)
        self.session_cleanup_interval_hours = getattr(settings, 'session_cleanup_interval_hours', 1)
        self.force_logout_on_password_change = getattr(settings, 'force_logout_on_password_change', True)
        self.ip_restriction_enabled = getattr(settings, 'session_ip_restriction_enabled', False)
        self.device_tracking_enabled = getattr(settings, 'session_device_tracking_enabled', True)
    
    @property
    def session_timeout_delta(self) -> timedelta:
        """Get session timeout as timedelta."""
        return timedelta(minutes=self.session_timeout_minutes)
    
    @property
    def remember_me_delta(self) -> timedelta:
        """Get remember me duration as timedelta."""
        return timedelta(days=self.remember_me_duration_days)


class RateLimitPolicy:
    """Rate limiting policy configuration."""
    
    def __init__(self):
        self.login_attempts_per_hour = getattr(settings, 'login_attempts_per_hour', 5)
        self.registration_attempts_per_hour = getattr(settings, 'registration_attempts_per_hour', 3)
        self.password_reset_attempts_per_hour = getattr(settings, 'password_reset_attempts_per_hour', 3)
        self.api_requests_per_minute = getattr(settings, 'api_requests_per_minute', 100)
        self.code_execution_per_minute = getattr(settings, 'code_execution_per_minute', 10)
        self.lockout_duration_minutes = getattr(settings, 'account_lockout_duration_minutes', 15)
        self.progressive_delays = getattr(settings, 'rate_limit_progressive_delays', True)


class EncryptionManager:
    """Manages encryption and decryption operations."""
    
    def __init__(self):
        self.secret_key = getattr(settings, 'secret_key', self._generate_secret_key())
        self.encryption_key = self._derive_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key."""
        return secrets.token_urlsafe(32)
    
    def _derive_encryption_key(self) -> bytes:
        """Derive encryption key from secret key."""
        password = self.secret_key.encode()
        salt = b'python_mastery_hub_salt'  # In production, use a random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> str:
        """Hash sensitive data with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine data and salt
        salted_data = f"{data}{salt}"
        
        # Create hash
        hash_obj = hashlib.sha256(salted_data.encode())
        hashed_data = hash_obj.hexdigest()
        
        # Return hash with salt for verification
        return f"{salt}${hashed_data}"
    
    def verify_hashed_data(self, data: str, hashed_data: str) -> bool:
        """Verify data against its hash."""
        try:
            salt, hash_value = hashed_data.split('$', 1)
            expected_hash = self.hash_sensitive_data(data, salt)
            return expected_hash == hashed_data
        except ValueError:
            return False


class SecurityHeaders:
    """Security headers configuration."""
    
    def __init__(self):
        self.environment = getattr(settings, 'environment', 'development')
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses."""
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
        }
        
        # Add HSTS in production
        if self.environment == 'production':
            headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        
        if self.environment == 'production':
            headers['Content-Security-Policy'] = '; '.join(csp_directives)
        
        return headers


class SecurityConfig:
    """Main security configuration class."""
    
    def __init__(self):
        self.password_policy = PasswordPolicy()
        self.session_policy = SessionPolicy()
        self.rate_limit_policy = RateLimitPolicy()
        self.encryption_manager = EncryptionManager()
        self.security_headers = SecurityHeaders()
        
        # Additional security settings
        self.require_https = getattr(settings, 'require_https', True)
        self.secure_cookies = getattr(settings, 'secure_cookies', True)
        self.csrf_protection_enabled = getattr(settings, 'csrf_protection_enabled', True)
        self.two_factor_auth_enabled = getattr(settings, 'two_factor_auth_enabled', False)
        self.email_verification_required = getattr(settings, 'email_verification_required', True)
        self.admin_approval_required = getattr(settings, 'admin_approval_required', False)
        
        # Security monitoring
        self.failed_login_threshold = getattr(settings, 'failed_login_threshold', 5)
        self.suspicious_activity_detection = getattr(settings, 'suspicious_activity_detection', True)
        self.security_logging_enabled = getattr(settings, 'security_logging_enabled', True)
        self.audit_trail_enabled = getattr(settings, 'audit_trail_enabled', True)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate security configuration."""
        issues = []
        warnings = []
        
        # Check critical security settings
        if not self.require_https and getattr(settings, 'environment') == 'production':
            issues.append("HTTPS should be required in production")
        
        if not self.secure_cookies and getattr(settings, 'environment') == 'production':
            issues.append("Secure cookies should be enabled in production")
        
        if not self.csrf_protection_enabled:
            warnings.append("CSRF protection is disabled")
        
        if not self.email_verification_required:
            warnings.append("Email verification is not required")
        
        # Check password policy
        if self.password_policy.min_length < 8:
            warnings.append("Minimum password length should be at least 8 characters")
        
        # Check session settings
        if self.session_policy.session_timeout_minutes > 60:
            warnings.append("Session timeout is longer than 1 hour")
        
        # Check rate limiting
        if self.rate_limit_policy.login_attempts_per_hour > 10:
            warnings.append("Login rate limit may be too permissive")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get summary of security configuration."""
        return {
            'password_policy': {
                'min_length': self.password_policy.min_length,
                'requires_uppercase': self.password_policy.require_uppercase,
                'requires_lowercase': self.password_policy.require_lowercase,
                'requires_digits': self.password_policy.require_digits,
                'requires_special': self.password_policy.require_special
            },
            'session_policy': {
                'timeout_minutes': self.session_policy.session_timeout_minutes,
                'remember_me_days': self.session_policy.remember_me_duration_days,
                'max_concurrent': self.session_policy.max_concurrent_sessions
            },
            'rate_limits': {
                'login_attempts_per_hour': self.rate_limit_policy.login_attempts_per_hour,
                'api_requests_per_minute': self.rate_limit_policy.api_requests_per_minute,
                'code_execution_per_minute': self.rate_limit_policy.code_execution_per_minute
            },
            'features': {
                'https_required': self.require_https,
                'csrf_protection': self.csrf_protection_enabled,
                'two_factor_auth': self.two_factor_auth_enabled,
                'email_verification': self.email_verification_required,
                'security_logging': self.security_logging_enabled,
                'audit_trail': self.audit_trail_enabled
            }
        }
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token."""
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token: str, session_token: str) -> bool:
        """Validate CSRF token against session."""
        # In a real implementation, you'd store and validate against session
        # For now, just check if token is properly formatted
        return len(token) == 43 and token.replace('-', '').replace('_', '').isalnum()
    
    def is_password_breached(self, password: str) -> bool:
        """Check if password appears in known breaches."""
        # In a real implementation, you'd check against Have I Been Pwned API
        # or a local database of breached passwords
        password_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        
        # Mock check against common passwords
        common_hashes = {
            # Hash of "password"
            "5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8",
            # Hash of "123456"
            "8D969EEF6ECAD3C29A3A629280E686CF0C3F5D5A86AFF3CA12020C923ADC6C92"
        }
        
        return password_hash in common_hashes
    
    def get_password_strength_requirements(self) -> Dict[str, Any]:
        """Get password strength requirements for frontend."""
        return {
            'minLength': self.password_policy.min_length,
            'maxLength': self.password_policy.max_length,
            'requireUppercase': self.password_policy.require_uppercase,
            'requireLowercase': self.password_policy.require_lowercase,
            'requireDigits': self.password_policy.require_digits,
            'requireSpecial': self.password_policy.require_special,
            'forbiddenPasswords': self.password_policy.forbidden_passwords[:10]  # Send only first 10
        }
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log security event."""
        if self.security_logging_enabled:
            logger.warning(f"Security event: {event_type}", extra={
                'event_type': event_type,
                'security_event': True,
                **details
            })


# Global security configuration instance
_security_config: Optional[SecurityConfig] = None


def get_security_config() -> SecurityConfig:
    """Get the global security configuration instance."""
    global _security_config
    
    if _security_config is None:
        _security_config = SecurityConfig()
    
    return _security_config


class SecurityAudit:
    """Security audit and compliance checker."""
    
    def __init__(self, security_config: SecurityConfig):
        self.config = security_config
    
    def run_security_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit."""
        audit_results = {
            'timestamp': str(datetime.now()),
            'overall_score': 0,
            'max_score': 100,
            'findings': [],
            'recommendations': []
        }
        
        # Password policy audit
        score, findings = self._audit_password_policy()
        audit_results['overall_score'] += score
        audit_results['findings'].extend(findings)
        
        # Session security audit
        score, findings = self._audit_session_security()
        audit_results['overall_score'] += score
        audit_results['findings'].extend(findings)
        
        # Rate limiting audit
        score, findings = self._audit_rate_limiting()
        audit_results['overall_score'] += score
        audit_results['findings'].extend(findings)
        
        # Security headers audit
        score, findings = self._audit_security_headers()
        audit_results['overall_score'] += score
        audit_results['findings'].extend(findings)
        
        # Generate recommendations based on findings
        audit_results['recommendations'] = self._generate_recommendations(audit_results['findings'])
        
        return audit_results
    
    def _audit_password_policy(self) -> tuple[int, List[Dict[str, Any]]]:
        """Audit password policy configuration."""
        score = 0
        findings = []
        
        if self.config.password_policy.min_length >= 8:
            score += 10
        else:
            findings.append({
                'type': 'warning',
                'category': 'password_policy',
                'message': f'Minimum password length is {self.config.password_policy.min_length}, recommend at least 8'
            })
        
        if self.config.password_policy.require_uppercase and self.config.password_policy.require_lowercase:
            score += 10
        else:
            findings.append({
                'type': 'info',
                'category': 'password_policy',
                'message': 'Password policy should require both uppercase and lowercase letters'
            })
        
        if self.config.password_policy.require_digits:
            score += 5
        
        if self.config.password_policy.require_special:
            score += 5
        
        return score, findings
    
    def _audit_session_security(self) -> tuple[int, List[Dict[str, Any]]]:
        """Audit session security configuration."""
        score = 0
        findings = []
        
        if self.config.session_policy.session_timeout_minutes <= 30:
            score += 10
        elif self.config.session_policy.session_timeout_minutes <= 60:
            score += 5
        else:
            findings.append({
                'type': 'warning',
                'category': 'session_security',
                'message': f'Session timeout is {self.config.session_policy.session_timeout_minutes} minutes, consider shorter timeout'
            })
        
        if self.config.session_policy.max_concurrent_sessions <= 5:
            score += 5
        
        if self.config.secure_cookies:
            score += 10
        else:
            findings.append({
                'type': 'error',
                'category': 'session_security',
                'message': 'Secure cookies should be enabled'
            })
        
        return score, findings
    
    def _audit_rate_limiting(self) -> tuple[int, List[Dict[str, Any]]]:
        """Audit rate limiting configuration."""
        score = 0
        findings = []
        
        if self.config.rate_limit_policy.login_attempts_per_hour <= 5:
            score += 10
        elif self.config.rate_limit_policy.login_attempts_per_hour <= 10:
            score += 5
        else:
            findings.append({
                'type': 'warning',
                'category': 'rate_limiting',
                'message': f'Login rate limit is {self.config.rate_limit_policy.login_attempts_per_hour}/hour, consider stricter limits'
            })
        
        if self.config.rate_limit_policy.code_execution_per_minute <= 10:
            score += 10
        
        return score, findings
    
    def _audit_security_headers(self) -> tuple[int, List[Dict[str, Any]]]:
        """Audit security headers configuration."""
        score = 0
        findings = []
        
        headers = self.config.security_headers.get_security_headers()
        
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy'
        ]
        
        for header in required_headers:
            if header in headers:
                score += 2
            else:
                findings.append({
                    'type': 'warning',
                    'category': 'security_headers',
                    'message': f'Missing security header: {header}'
                })
        
        if 'Content-Security-Policy' in headers:
            score += 10
        else:
            findings.append({
                'type': 'info',
                'category': 'security_headers',
                'message': 'Consider implementing Content Security Policy'
            })
        
        return score, findings
    
    def _generate_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = []
        
        error_count = len([f for f in findings if f['type'] == 'error'])
        warning_count = len([f for f in findings if f['type'] == 'warning'])
        
        if error_count > 0:
            recommendations.append(f"Address {error_count} critical security issues immediately")
        
        if warning_count > 0:
            recommendations.append(f"Review {warning_count} security warnings")
        
        recommendations.extend([
            "Regularly review and update security policies",
            "Monitor security logs for suspicious activity", 
            "Consider implementing two-factor authentication",
            "Perform regular security audits and penetration testing"
        ])
        
        return recommendations