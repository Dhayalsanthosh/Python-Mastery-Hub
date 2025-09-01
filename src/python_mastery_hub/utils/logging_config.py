# src/python_mastery_hub/utils/logging_config.py
"""
Logging Configuration - Centralized Logging Setup

Provides consistent logging configuration across the entire application.
Supports different log levels, formatters, and output destinations.
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json
import threading


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        if not self._supports_color():
            return super().format(record)
        
        # Make a copy of the record to avoid modifying the original
        record_copy = logging.makeLogRecord(record.__dict__)
        
        # Add color to level name
        level_color = self.COLORS.get(record_copy.levelname, '')
        if level_color:
            record_copy.levelname = f"{level_color}{record_copy.levelname}{self.RESET}"
        
        return super().format(record_copy)
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors."""
        # Check for explicit environment variable
        if os.environ.get('NO_COLOR'):
            return False
        
        if os.environ.get('FORCE_COLOR'):
            return True
        
        return (
            hasattr(sys.stderr, "isatty") and 
            sys.stderr.isatty() and 
            not sys.platform.startswith('win')
        )


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        excluded_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
            'filename', 'module', 'lineno', 'funcName', 'created',
            'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'getMessage', 'exc_info',
            'exc_text', 'stack_info', 'taskName'
        }
        
        for key, value in record.__dict__.items():
            if key not in excluded_fields:
                # Ensure value is JSON serializable
                try:
                    json.dumps(value)
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)
        
        return json.dumps(log_data, separators=(',', ':'))


class LoggingConfig:
    """Centralized logging configuration manager."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize logging configuration.
        
        Args:
            log_dir: Directory for log files (default: ~/.python_mastery_hub/logs)
        """
        self.log_dir = log_dir or Path.home() / '.python_mastery_hub' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.formatters = self._create_formatters()
        self.handlers = {}
        self._configured = False
        self._lock = threading.RLock()
    
    def _create_formatters(self) -> Dict[str, logging.Formatter]:
        """Create different formatters for various use cases."""
        return {
            'console': ColoredFormatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%H:%M:%S'
            ),
            'file': logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ),
            'detailed': logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ),
            'json': StructuredFormatter(),
            'simple': logging.Formatter(
                fmt='%(levelname)s: %(message)s'
            )
        }
    
    def _create_console_handler(self, level: int = logging.INFO) -> logging.StreamHandler:
        """Create console handler with colored output."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(self.formatters['console'])
        return handler
    
    def _create_file_handler(
        self, 
        filename: str, 
        level: int = logging.DEBUG,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> logging.handlers.RotatingFileHandler:
        """Create rotating file handler."""
        file_path = self.log_dir / filename
        
        try:
            handler = logging.handlers.RotatingFileHandler(
                file_path, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
            )
            handler.setLevel(level)
            handler.setFormatter(self.formatters['file'])
            return handler
        except (OSError, PermissionError) as e:
            # Fallback to basic console logging if file logging fails
            print(f"Warning: Failed to create file handler for {file_path}: {e}", file=sys.stderr)
            fallback_handler = logging.StreamHandler(sys.stderr)
            fallback_handler.setLevel(level)
            fallback_handler.setFormatter(self.formatters['simple'])
            return fallback_handler
    
    def _create_error_handler(self) -> logging.handlers.RotatingFileHandler:
        """Create dedicated error handler."""
        handler = self._create_file_handler('errors.log', level=logging.ERROR)
        handler.setFormatter(self.formatters['detailed'])
        return handler
    
    def _create_debug_handler(self) -> logging.handlers.RotatingFileHandler:
        """Create debug handler for development."""
        handler = self._create_file_handler('debug.log', level=logging.DEBUG)
        handler.setFormatter(self.formatters['detailed'])
        return handler
    
    def _create_json_handler(self) -> logging.handlers.RotatingFileHandler:
        """Create JSON handler for structured logging."""
        handler = self._create_file_handler('app.jsonl', level=logging.INFO)
        handler.setFormatter(self.formatters['json'])
        return handler
    
    def setup_logging(
        self,
        level: int = logging.INFO,
        console: bool = True,
        file_logging: bool = True,
        error_logging: bool = True,
        debug_logging: bool = False,
        json_logging: bool = False
    ) -> None:
        """
        Setup logging configuration.
        
        Args:
            level: Root logging level
            console: Enable console logging
            file_logging: Enable general file logging
            error_logging: Enable error-specific logging
            debug_logging: Enable debug logging
            json_logging: Enable structured JSON logging
        """
        with self._lock:
            if self._configured:
                return
            
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(level)
            
            # Clear existing handlers to avoid duplicates
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Add console handler
            if console:
                try:
                    console_handler = self._create_console_handler(level)
                    root_logger.addHandler(console_handler)
                    self.handlers['console'] = console_handler
                except Exception as e:
                    print(f"Warning: Failed to create console handler: {e}", file=sys.stderr)
            
            # Add file handler
            if file_logging:
                try:
                    file_handler = self._create_file_handler('app.log', level)
                    root_logger.addHandler(file_handler)
                    self.handlers['file'] = file_handler
                except Exception as e:
                    print(f"Warning: Failed to create file handler: {e}", file=sys.stderr)
            
            # Add error handler
            if error_logging:
                try:
                    error_handler = self._create_error_handler()
                    root_logger.addHandler(error_handler)
                    self.handlers['error'] = error_handler
                except Exception as e:
                    print(f"Warning: Failed to create error handler: {e}", file=sys.stderr)
            
            # Add debug handler
            if debug_logging:
                try:
                    debug_handler = self._create_debug_handler()
                    root_logger.addHandler(debug_handler)
                    self.handlers['debug'] = debug_handler
                except Exception as e:
                    print(f"Warning: Failed to create debug handler: {e}", file=sys.stderr)
            
            # Add JSON handler
            if json_logging:
                try:
                    json_handler = self._create_json_handler()
                    root_logger.addHandler(json_handler)
                    self.handlers['json'] = json_handler
                except Exception as e:
                    print(f"Warning: Failed to create JSON handler: {e}", file=sys.stderr)
            
            self._configured = True
            
            # Log startup message
            logger = logging.getLogger(__name__)
            logger.info("Logging system initialized")
            logger.debug(f"Log directory: {self.log_dir}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    def set_level(self, level: int, handler_name: Optional[str] = None) -> None:
        """
        Set logging level for specific handler or all handlers.
        
        Args:
            level: New logging level
            handler_name: Specific handler name (None for all)
        """
        with self._lock:
            if handler_name:
                if handler_name in self.handlers:
                    self.handlers[handler_name].setLevel(level)
                else:
                    raise ValueError(f"Handler '{handler_name}' not found")
            else:
                logging.getLogger().setLevel(level)
                for handler in self.handlers.values():
                    handler.setLevel(level)
    
    def add_custom_handler(
        self, 
        name: str, 
        handler: logging.Handler, 
        formatter_name: str = 'file'
    ) -> None:
        """
        Add a custom handler.
        
        Args:
            name: Handler name
            handler: Handler instance
            formatter_name: Formatter to use
        """
        with self._lock:
            if formatter_name in self.formatters:
                handler.setFormatter(self.formatters[formatter_name])
            else:
                raise ValueError(f"Formatter '{formatter_name}' not found")
            
            logging.getLogger().addHandler(handler)
            self.handlers[name] = handler
    
    def remove_handler(self, name: str) -> bool:
        """
        Remove a handler by name.
        
        Args:
            name: Handler name
            
        Returns:
            True if handler was removed, False if not found
        """
        with self._lock:
            if name in self.handlers:
                handler = self.handlers[name]
                logging.getLogger().removeHandler(handler)
                del self.handlers[name]
                return True
            return False
    
    def create_module_logger(
        self, 
        module_name: str, 
        level: Optional[int] = None,
        file_name: Optional[str] = None
    ) -> logging.Logger:
        """
        Create a dedicated logger for a specific module.
        
        Args:
            module_name: Name of the module
            level: Logging level (None to inherit from root)
            file_name: Dedicated log file name
            
        Returns:
            Logger instance
        """
        logger = logging.getLogger(module_name)
        
        if level is not None:
            logger.setLevel(level)
        
        # Add dedicated file handler if requested
        if file_name:
            try:
                handler = self._create_file_handler(file_name)
                logger.addHandler(handler)
                # Prevent propagation to avoid duplicate logs
                logger.propagate = False
            except Exception as e:
                print(f"Warning: Failed to create module logger for {module_name}: {e}", file=sys.stderr)
        
        return logger
    
    def log_performance(self, operation: str, duration: float, **kwargs) -> None:
        """
        Log performance metrics.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            **kwargs: Additional metadata
        """
        perf_logger = logging.getLogger('performance')
        
        log_data = {
            'operation': operation,
            'duration_seconds': duration,
            'duration_ms': duration * 1000,
            **kwargs
        }
        
        perf_logger.info(
            f"Performance: {operation} took {duration:.3f}s",
            extra=log_data
        )
    
    def log_user_action(self, action: str, user_id: Optional[str] = None, **kwargs) -> None:
        """
        Log user actions for analytics.
        
        Args:
            action: Action name
            user_id: User identifier
            **kwargs: Additional metadata
        """
        action_logger = logging.getLogger('user_actions')
        
        log_data = {
            'action': action,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        action_logger.info(f"User action: {action}", extra=log_data)
    
    def cleanup_old_logs(self, days: int = 30) -> None:
        """
        Clean up log files older than specified days.
        
        Args:
            days: Number of days to keep logs
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        cleaned_count = 0
        for log_file in self.log_dir.glob('*.log*'):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    cleaned_count += 1
                    logging.getLogger(__name__).info(f"Deleted old log file: {log_file}")
            except OSError as e:
                logging.getLogger(__name__).warning(f"Failed to delete {log_file}: {e}")
        
        if cleaned_count > 0:
            logging.getLogger(__name__).info(f"Cleaned up {cleaned_count} old log files")
    
    def get_handler_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status information for all handlers."""
        with self._lock:
            status = {}
            for name, handler in self.handlers.items():
                status[name] = {
                    'level': logging.getLevelName(handler.level),
                    'class': handler.__class__.__name__,
                    'formatter': handler.formatter.__class__.__name__ if handler.formatter else None
                }
                
                # Add file-specific info
                if hasattr(handler, 'baseFilename'):
                    status[name]['file'] = handler.baseFilename
                    try:
                        file_path = Path(handler.baseFilename)
                        if file_path.exists():
                            status[name]['file_size'] = file_path.stat().st_size
                    except Exception:
                        pass
            
            return status


# Global logging configuration instance
_logging_config = LoggingConfig()


def setup_logging(
    level: int = logging.INFO,
    console: bool = True,
    file_logging: bool = True,
    error_logging: bool = True,
    debug_logging: bool = False,
    json_logging: bool = False
) -> None:
    """
    Setup global logging configuration.
    
    Args:
        level: Root logging level
        console: Enable console logging
        file_logging: Enable general file logging
        error_logging: Enable error-specific logging
        debug_logging: Enable debug logging
        json_logging: Enable structured JSON logging
    """
    _logging_config.setup_logging(
        level=level,
        console=console,
        file_logging=file_logging,
        error_logging=error_logging,
        debug_logging=debug_logging,
        json_logging=json_logging
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return _logging_config.get_logger(name)


def set_log_level(level: int, handler_name: Optional[str] = None) -> None:
    """
    Set logging level.
    
    Args:
        level: New logging level
        handler_name: Specific handler name (None for all)
    """
    _logging_config.set_level(level, handler_name)


def log_performance(operation: str, duration: float, **kwargs) -> None:
    """
    Log performance metrics.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional metadata
    """
    _logging_config.log_performance(operation, duration, **kwargs)


def log_user_action(action: str, user_id: Optional[str] = None, **kwargs) -> None:
    """
    Log user actions.
    
    Args:
        action: Action name
        user_id: User identifier
        **kwargs: Additional metadata
    """
    _logging_config.log_user_action(action, user_id, **kwargs)


def create_module_logger(
    module_name: str, 
    level: Optional[int] = None,
    file_name: Optional[str] = None
) -> logging.Logger:
    """
    Create a dedicated logger for a specific module.
    
    Args:
        module_name: Name of the module
        level: Logging level (None to inherit from root)
        file_name: Dedicated log file name
        
    Returns:
        Logger instance
    """
    return _logging_config.create_module_logger(module_name, level, file_name)


def cleanup_old_logs(days: int = 30) -> None:
    """
    Clean up old log files.
    
    Args:
        days: Number of days to keep logs
    """
    _logging_config.cleanup_old_logs(days)


def get_logging_status() -> Dict[str, Any]:
    """Get current logging configuration status."""
    return {
        'configured': _logging_config._configured,
        'log_directory': str(_logging_config.log_dir),
        'handlers': _logging_config.get_handler_status()
    }


class PerformanceLogger:
    """Context manager for logging performance metrics."""
    
    def __init__(self, operation: str, **kwargs):
        """
        Initialize performance logger.
        
        Args:
            operation: Operation name
            **kwargs: Additional metadata
        """
        self.operation = operation
        self.metadata = kwargs
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log performance."""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            log_performance(self.operation, duration, **self.metadata)


def timed_operation(operation: Optional[str] = None, **kwargs):
    """
    Decorator or context manager for timing operations.
    
    Usage as decorator:
        @timed_operation("my_function")
        def my_function():
            pass
    
    Usage as context manager:
        with timed_operation("my_operation"):
            # do something
            pass
    """
    def decorator(func):
        operation_name = operation or func.__name__
        def wrapper(*args, **func_kwargs):
            with PerformanceLogger(operation_name, **kwargs):
                return func(*args, **func_kwargs)
        return wrapper
    
    # If called with a function directly (no arguments)
    if callable(operation):
        func = operation
        return decorator(func)
    
    # If used as context manager or decorator with arguments
    if operation is None:
        raise ValueError("Operation name required when used as context manager")
    
    # Context manager usage
    if not callable(operation):
        return PerformanceLogger(operation, **kwargs)
    
    return decorator


# Initialize logging on import with basic configuration
try:
    setup_logging()
except Exception as e:
    # Fallback to basic console logging if setup fails
    print(f"Warning: Failed to initialize logging: {e}", file=sys.stderr)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )