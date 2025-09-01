# Location: src/python_mastery_hub/web/services/__init__.py

"""
Web Services Package

Contains service layer components for business logic, authentication,
code execution, progress tracking, and external integrations.
"""

from .auth_service import AuthService, TokenService, PasswordService
from .code_executor import CodeExecutor, ExecutionResult, CodeExecutionError
from .progress_service import ProgressService, ProgressTracker
from .email_service import EmailService, EmailTemplate, EmailProvider

__all__ = [
    # Authentication services
    "AuthService",
    "TokenService", 
    "PasswordService",
    
    # Code execution services
    "CodeExecutor",
    "ExecutionResult",
    "CodeExecutionError",
    
    # Progress tracking services
    "ProgressService",
    "ProgressTracker",
    
    # Email services
    "EmailService",
    "EmailTemplate",
    "EmailProvider",
]