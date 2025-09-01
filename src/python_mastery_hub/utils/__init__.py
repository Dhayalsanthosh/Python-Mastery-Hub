# src/python_mastery_hub/utils/__init__.py
"""
Python Mastery Hub Utils Package

Core utility modules providing shared functionality across the application
including progress tracking, achievements, logging, validation, and file handling.

Optional modules require additional dependencies:
- security_utils: requires 'bcrypt' (pip install bcrypt)
- metrics_collector: requires 'psutil' (pip install psutil)  
- data_exporters: Excel support requires 'openpyxl' (pip install openpyxl)
"""

# Core utilities - always available
from .progress_calculator import (
    ProgressCalculator, 
    TopicProgress, 
    ModuleProgress, 
    LearningSession
)

from .achievement_engine import (
    AchievementEngine, 
    Achievement, 
    AchievementCategory, 
    AchievementTier
)

from .logging_config import (
    setup_logging,
    get_logger,
    set_log_level,
    log_performance,
    log_user_action,
    create_module_logger,
    PerformanceLogger,
    timed_operation,
    cleanup_old_logs,
    get_logging_status
)

from .validators import (
    ValidationError,
    Validator,
    StringValidator,
    NumberValidator,
    FormValidator,
    validate_email,
    validate_url,
    validate_python_code,
    sanitize_string,
    string_validator,
    number_validator,
    email_validator
)

from .formatters import (
    TextFormatter,
    ColorCodes,
    formatter,
    format_duration,
    format_time_ago,
    format_percentage,
    format_progress_bar,
    format_table,
    format_json
)

from .file_handlers import (
    SafeFileHandler,
    JSONFileHandler,
    YAMLFileHandler,
    CSVFileHandler,
    ConfigFileHandler,
    DirectoryHandler,
    FileError,
    read_text,
    write_text,
    read_json,
    write_json,
    read_yaml,
    write_yaml,
    read_csv,
    write_csv
)

from .code_execution import (
    SafeCodeExecutor,
    CodeValidator,
    TestRunner,
    ExecutionResult,
    ExecutionError,
    SecurityViolation,
    execute_code,
    validate_code,
    run_code_tests
)

from .email_templates import (
    EmailTemplateManager,
    EmailRenderer,
    EmailTemplate,
    EmailPreferences,
    create_email_manager,
    render_welcome_email,
    render_achievement_email
)

from .cache_manager import (
    CacheManager,
    MemoryCache,
    FileCache,
    cached,
    get_cache,
    cache_get,
    cache_set,
    cache_delete,
    cache_clear,
    cache_stats
)

from .data_exporters import (
    DataExporter,
    CSVExporter,
    JSONExporter,
    HTMLReportExporter,
    ZipExporter,
    ExportConfig as DataExportConfig,
    create_exporter,
    export_learning_data,
    get_supported_formats
)

# Core exports - always available
__all__ = [
    # Progress tracking
    "ProgressCalculator",
    "TopicProgress", 
    "ModuleProgress",
    "LearningSession",
    
    # Achievement system
    "AchievementEngine",
    "Achievement",
    "AchievementCategory",
    "AchievementTier",
    
    # Logging utilities
    "setup_logging",
    "get_logger",
    "set_log_level",
    "log_performance",
    "log_user_action",
    "create_module_logger",
    "PerformanceLogger",
    "timed_operation",
    "cleanup_old_logs",
    "get_logging_status",
    
    # Validation
    "ValidationError",
    "Validator",
    "StringValidator", 
    "NumberValidator",
    "FormValidator",
    "validate_email",
    "validate_url",
    "validate_python_code",
    "sanitize_string",
    "string_validator",
    "number_validator",
    "email_validator",
    
    # Formatting
    "TextFormatter",
    "ColorCodes",
    "formatter",
    "format_duration",
    "format_time_ago",
    "format_percentage",
    "format_progress_bar",
    "format_table",
    "format_json",
    
    # File handling
    "SafeFileHandler",
    "JSONFileHandler",
    "YAMLFileHandler",
    "CSVFileHandler",
    "ConfigFileHandler",
    "DirectoryHandler",
    "FileError",
    "read_text",
    "write_text",
    "read_json",
    "write_json",
    "read_yaml",
    "write_yaml",
    "read_csv",
    "write_csv",
    
    # Code execution
    "SafeCodeExecutor",
    "CodeValidator",
    "TestRunner",
    "ExecutionResult",
    "ExecutionError",
    "SecurityViolation",
    "execute_code",
    "validate_code",
    "run_code_tests",
    
    # Email templates
    "EmailTemplateManager",
    "EmailRenderer",
    "EmailTemplate",
    "EmailPreferences",
    "create_email_manager",
    "render_welcome_email",
    "render_achievement_email",
    
    # Caching
    "CacheManager",
    "MemoryCache",
    "FileCache",
    "cached",
    "get_cache",
    "cache_get",
    "cache_set",
    "cache_delete",
    "cache_clear",
    "cache_stats",
    
    # Data export
    "DataExporter",
    "CSVExporter",
    "JSONExporter", 
    "HTMLReportExporter",
    "ZipExporter",
    "DataExportConfig",
    "create_exporter",
    "export_learning_data",
    "get_supported_formats",
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Python Mastery Hub"
__description__ = "Comprehensive utilities for the Python Mastery Hub learning platform"


# Optional module access functions
def get_security_utils():
    """
    Get security utilities module (requires bcrypt).
    
    Returns:
        security_utils module
        
    Raises:
        ImportError: If bcrypt is not installed
    """
    try:
        from . import security_utils
        return security_utils
    except ImportError as e:
        raise ImportError(
            "Security utilities require bcrypt. Install with: pip install bcrypt"
        ) from e


def get_metrics_collector():
    """
    Get metrics collector module (requires psutil).
    
    Returns:
        metrics_collector module
        
    Raises:
        ImportError: If psutil is not installed
    """
    try:
        from . import metrics_collector
        return metrics_collector
    except ImportError as e:
        raise ImportError(
            "Metrics collection requires psutil. Install with: pip install psutil"
        ) from e


def get_excel_exporter():
    """
    Get Excel export functionality (requires openpyxl).
    
    Returns:
        ExcelExporter class
        
    Raises:
        ImportError: If openpyxl is not installed
    """
    try:
        from .data_exporters import ExcelExporter
        return ExcelExporter
    except ImportError as e:
        raise ImportError(
            "Excel export requires openpyxl. Install with: pip install openpyxl"
        ) from e


def check_dependencies():
    """
    Check which optional dependencies are available.
    
    Returns:
        Dict[str, bool]: Availability status of optional features
    """
    features = {}
    
    # Check bcrypt for security
    try:
        import bcrypt
        features['security'] = True
    except ImportError:
        features['security'] = False
    
    # Check psutil for metrics
    try:
        import psutil
        features['metrics'] = True
    except ImportError:
        features['metrics'] = False
    
    # Check openpyxl for Excel export
    try:
        import openpyxl
        features['excel_export'] = True
    except ImportError:
        features['excel_export'] = False
    
    return features


# Convenience imports for optional modules (use with caution)
def import_security():
    """Import security utilities with clear error message if unavailable."""
    return get_security_utils()


def import_metrics():
    """Import metrics collector with clear error message if unavailable.""" 
    return get_metrics_collector()