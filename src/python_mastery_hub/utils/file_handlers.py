# src/python_mastery_hub/utils/file_handlers.py
"""
File Handling Utilities - Safe File Operations and Management

Provides utilities for safe file operations, including reading, writing, 
backup management, and file system operations with proper error handling.
"""

import os
import shutil
import json
import yaml
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, BinaryIO, TextIO
from datetime import datetime
import tempfile
import hashlib
import logging
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)


class FileError(Exception):
    """Custom exception for file operation errors."""
    pass


class FileLock:
    """Simple file locking mechanism."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.lock_path = file_path.with_suffix(file_path.suffix + '.lock')
        self.lock = threading.Lock()
    
    def __enter__(self):
        self.lock.acquire()
        try:
            if self.lock_path.exists():
                raise FileError(f"File is locked: {self.file_path}")
            self.lock_path.touch()
            return self
        except Exception:
            self.lock.release()
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        finally:
            self.lock.release()


class SafeFileHandler:
    """Handler for safe file operations with backup and recovery."""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir
        if self.backup_dir:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def read_text_file(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """
        Safely read text file with error handling.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
            
        Returns:
            File content as string
            
        Raises:
            FileError: If file cannot be read
        """
        path = Path(file_path)
        
        try:
            if not path.exists():
                raise FileError(f"File does not exist: {path}")
            
            if not path.is_file():
                raise FileError(f"Path is not a file: {path}")
            
            with path.open('r', encoding=encoding) as f:
                return f.read()
                
        except UnicodeDecodeError as e:
            raise FileError(f"Encoding error reading {path}: {e}")
        except PermissionError as e:
            raise FileError(f"Permission denied reading {path}: {e}")
        except Exception as e:
            raise FileError(f"Error reading {path}: {e}")
    
    def write_text_file(
        self, 
        file_path: Union[str, Path], 
        content: str, 
        encoding: str = 'utf-8',
        create_backup: bool = True,
        atomic: bool = True
    ) -> None:
        """
        Safely write text file with backup and atomic operation.
        
        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding
            create_backup: Whether to create backup of existing file
            atomic: Whether to use atomic write operation
        """
        path = Path(file_path)
        
        try:
            # Create parent directories
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists and backup is requested
            if create_backup and path.exists() and self.backup_dir:
                self._create_backup(path)
            
            if atomic:
                self._atomic_write_text(path, content, encoding)
            else:
                with path.open('w', encoding=encoding) as f:
                    f.write(content)
            
            logger.debug(f"Successfully wrote file: {path}")
            
        except Exception as e:
            raise FileError(f"Error writing {path}: {e}")
    
    def read_binary_file(self, file_path: Union[str, Path]) -> bytes:
        """
        Safely read binary file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as bytes
        """
        path = Path(file_path)
        
        try:
            if not path.exists():
                raise FileError(f"File does not exist: {path}")
            
            with path.open('rb') as f:
                return f.read()
                
        except Exception as e:
            raise FileError(f"Error reading binary file {path}: {e}")
    
    def write_binary_file(
        self, 
        file_path: Union[str, Path], 
        content: bytes,
        create_backup: bool = True,
        atomic: bool = True
    ) -> None:
        """
        Safely write binary file.
        
        Args:
            file_path: Path to the file
            content: Binary content to write
            create_backup: Whether to create backup
            atomic: Whether to use atomic write
        """
        path = Path(file_path)
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if create_backup and path.exists() and self.backup_dir:
                self._create_backup(path)
            
            if atomic:
                self._atomic_write_binary(path, content)
            else:
                with path.open('wb') as f:
                    f.write(content)
            
            logger.debug(f"Successfully wrote binary file: {path}")
            
        except Exception as e:
            raise FileError(f"Error writing binary file {path}: {e}")
    
    def _atomic_write_text(self, path: Path, content: str, encoding: str) -> None:
        """Perform atomic text file write."""
        with tempfile.NamedTemporaryFile(
            mode='w', 
            encoding=encoding, 
            dir=path.parent, 
            delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            try:
                temp_file.write(content)
                temp_file.flush()
                os.fsync(temp_file.fileno())
                
                # Atomic move
                shutil.move(str(temp_path), str(path))
                
            except Exception:
                # Cleanup temp file on error
                if temp_path.exists():
                    temp_path.unlink()
                raise
    
    def _atomic_write_binary(self, path: Path, content: bytes) -> None:
        """Perform atomic binary file write."""
        with tempfile.NamedTemporaryFile(
            mode='wb', 
            dir=path.parent, 
            delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            try:
                temp_file.write(content)
                temp_file.flush()
                os.fsync(temp_file.fileno())
                
                # Atomic move
                shutil.move(str(temp_path), str(path))
                
            except Exception:
                # Cleanup temp file on error
                if temp_path.exists():
                    temp_path.unlink()
                raise
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create backup of existing file."""
        if not self.backup_dir:
            return file_path
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.warning(f"Failed to create backup of {file_path}: {e}")
            return file_path
    
    def delete_file(self, file_path: Union[str, Path], create_backup: bool = True) -> None:
        """
        Safely delete file with optional backup.
        
        Args:
            file_path: Path to the file
            create_backup: Whether to create backup before deletion
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"File does not exist for deletion: {path}")
            return
        
        try:
            if create_backup and self.backup_dir:
                self._create_backup(path)
            
            path.unlink()
            logger.debug(f"Successfully deleted file: {path}")
            
        except Exception as e:
            raise FileError(f"Error deleting {path}: {e}")
    
    def copy_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Safely copy file with error handling.
        
        Args:
            src: Source file path
            dst: Destination file path
        """
        src_path = Path(src)
        dst_path = Path(dst)
        
        try:
            if not src_path.exists():
                raise FileError(f"Source file does not exist: {src_path}")
            
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            
            logger.debug(f"Successfully copied {src_path} to {dst_path}")
            
        except Exception as e:
            raise FileError(f"Error copying {src_path} to {dst_path}: {e}")
    
    def move_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Safely move file with error handling.
        
        Args:
            src: Source file path
            dst: Destination file path
        """
        src_path = Path(src)
        dst_path = Path(dst)
        
        try:
            if not src_path.exists():
                raise FileError(f"Source file does not exist: {src_path}")
            
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src_path, dst_path)
            
            logger.debug(f"Successfully moved {src_path} to {dst_path}")
            
        except Exception as e:
            raise FileError(f"Error moving {src_path} to {dst_path}: {e}")


class JSONFileHandler(SafeFileHandler):
    """Specialized handler for JSON files."""
    
    def read_json(self, file_path: Union[str, Path]) -> Any:
        """
        Read JSON file with error handling.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        try:
            content = self.read_text_file(file_path)
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            raise FileError(f"Invalid JSON in {file_path}: {e}")
    
    def write_json(
        self, 
        file_path: Union[str, Path], 
        data: Any, 
        indent: int = 2,
        sort_keys: bool = True,
        create_backup: bool = True
    ) -> None:
        """
        Write JSON file with formatting.
        
        Args:
            file_path: Path to JSON file
            data: Data to serialize
            indent: JSON indentation
            sort_keys: Whether to sort dictionary keys
            create_backup: Whether to create backup
        """
        try:
            content = json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
            self.write_text_file(file_path, content, create_backup=create_backup)
            
        except TypeError as e:
            raise FileError(f"Cannot serialize data to JSON: {e}")


class YAMLFileHandler(SafeFileHandler):
    """Specialized handler for YAML files."""
    
    def read_yaml(self, file_path: Union[str, Path]) -> Any:
        """
        Read YAML file with error handling.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Parsed YAML data
        """
        try:
            content = self.read_text_file(file_path)
            return yaml.safe_load(content)
            
        except yaml.YAMLError as e:
            raise FileError(f"Invalid YAML in {file_path}: {e}")
    
    def write_yaml(
        self, 
        file_path: Union[str, Path], 
        data: Any,
        create_backup: bool = True
    ) -> None:
        """
        Write YAML file with formatting.
        
        Args:
            file_path: Path to YAML file
            data: Data to serialize
            create_backup: Whether to create backup
        """
        try:
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            self.write_text_file(file_path, content, create_backup=create_backup)
            
        except yaml.YAMLError as e:
            raise FileError(f"Cannot serialize data to YAML: {e}")


class CSVFileHandler(SafeFileHandler):
    """Specialized handler for CSV files."""
    
    def read_csv(
        self, 
        file_path: Union[str, Path], 
        has_header: bool = True,
        delimiter: str = ',',
        encoding: str = 'utf-8'
    ) -> List[Dict[str, str]]:
        """
        Read CSV file as list of dictionaries.
        
        Args:
            file_path: Path to CSV file
            has_header: Whether CSV has header row
            delimiter: CSV delimiter
            encoding: File encoding
            
        Returns:
            List of dictionaries representing rows
        """
        path = Path(file_path)
        
        try:
            with path.open('r', encoding=encoding, newline='') as f:
                if has_header:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    return list(reader)
                else:
                    reader = csv.reader(f, delimiter=delimiter)
                    rows = list(reader)
                    if not rows:
                        return []
                    
                    # Create keys based on column count
                    num_cols = len(rows[0])
                    headers = [f'column_{i}' for i in range(num_cols)]
                    
                    return [dict(zip(headers, row)) for row in rows]
                    
        except Exception as e:
            raise FileError(f"Error reading CSV {path}: {e}")
    
    def write_csv(
        self, 
        file_path: Union[str, Path], 
        data: List[Dict[str, Any]],
        fieldnames: Optional[List[str]] = None,
        delimiter: str = ',',
        encoding: str = 'utf-8',
        create_backup: bool = True
    ) -> None:
        """
        Write CSV file from list of dictionaries.
        
        Args:
            file_path: Path to CSV file
            data: List of dictionaries to write
            fieldnames: Field names for CSV header
            delimiter: CSV delimiter
            encoding: File encoding
            create_backup: Whether to create backup
        """
        if not data:
            raise FileError("No data provided for CSV write")
        
        path = Path(file_path)
        
        try:
            if fieldnames is None:
                fieldnames = list(data[0].keys())
            
            # Create backup if needed
            if create_backup and path.exists() and self.backup_dir:
                self._create_backup(path)
            
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with path.open('w', encoding=encoding, newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
            
            logger.debug(f"Successfully wrote CSV file: {path}")
            
        except Exception as e:
            raise FileError(f"Error writing CSV {path}: {e}")


class ConfigFileHandler:
    """Handler for configuration files with validation."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / '.python_mastery_hub'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.json_handler = JSONFileHandler()
        self.yaml_handler = YAMLFileHandler()
    
    def load_config(
        self, 
        config_name: str, 
        format_type: str = 'json',
        default_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file with fallback to defaults.
        
        Args:
            config_name: Name of config file (without extension)
            format_type: Config format ('json' or 'yaml')
            default_config: Default configuration to use if file doesn't exist
            
        Returns:
            Configuration dictionary
        """
        file_extension = '.json' if format_type == 'json' else '.yaml'
        config_path = self.config_dir / f"{config_name}{file_extension}"
        
        try:
            if config_path.exists():
                if format_type == 'json':
                    config = self.json_handler.read_json(config_path)
                else:
                    config = self.yaml_handler.read_yaml(config_path)
                
                # Merge with defaults if provided
                if default_config:
                    merged_config = default_config.copy()
                    merged_config.update(config)
                    return merged_config
                
                return config
            else:
                # Return default config and save it
                if default_config:
                    self.save_config(config_name, default_config, format_type)
                    return default_config.copy()
                
                return {}
                
        except Exception as e:
            logger.error(f"Error loading config {config_name}: {e}")
            return default_config.copy() if default_config else {}
    
    def save_config(
        self, 
        config_name: str, 
        config: Dict[str, Any], 
        format_type: str = 'json'
    ) -> None:
        """
        Save configuration file.
        
        Args:
            config_name: Name of config file
            config: Configuration dictionary to save
            format_type: Config format ('json' or 'yaml')
        """
        file_extension = '.json' if format_type == 'json' else '.yaml'
        config_path = self.config_dir / f"{config_name}{file_extension}"
        
        try:
            if format_type == 'json':
                self.json_handler.write_json(config_path, config)
            else:
                self.yaml_handler.write_yaml(config_path, config)
                
        except Exception as e:
            raise FileError(f"Error saving config {config_name}: {e}")


class DirectoryHandler:
    """Handler for directory operations."""
    
    @staticmethod
    def ensure_directory(dir_path: Union[str, Path]) -> Path:
        """
        Ensure directory exists, create if it doesn't.
        
        Args:
            dir_path: Path to directory
            
        Returns:
            Path object of the directory
        """
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def list_files(
        dir_path: Union[str, Path], 
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """
        List files in directory with optional pattern matching.
        
        Args:
            dir_path: Directory to search
            pattern: File pattern (e.g., "*.py", "test_*")
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        path = Path(dir_path)
        
        if not path.exists():
            return []
        
        if recursive:
            return list(path.rglob(pattern))
        else:
            return list(path.glob(pattern))
    
    @staticmethod
    def get_directory_size(dir_path: Union[str, Path]) -> int:
        """
        Calculate total size of directory in bytes.
        
        Args:
            dir_path: Directory path
            
        Returns:
            Total size in bytes
        """
        path = Path(dir_path)
        total_size = 0
        
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except (OSError, PermissionError) as e:
            logger.warning(f"Error calculating directory size for {path}: {e}")
        
        return total_size
    
    @staticmethod
    def clean_directory(
        dir_path: Union[str, Path], 
        older_than_days: Optional[int] = None,
        pattern: str = "*"
    ) -> int:
        """
        Clean directory by removing old files.
        
        Args:
            dir_path: Directory to clean
            older_than_days: Remove files older than this many days
            pattern: File pattern to match
            
        Returns:
            Number of files removed
        """
        path = Path(dir_path)
        
        if not path.exists():
            return 0
        
        removed_count = 0
        current_time = datetime.now().timestamp()
        
        try:
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    should_remove = False
                    
                    if older_than_days is not None:
                        file_age_days = (current_time - file_path.stat().st_mtime) / (24 * 3600)
                        should_remove = file_age_days > older_than_days
                    else:
                        should_remove = True
                    
                    if should_remove:
                        try:
                            file_path.unlink()
                            removed_count += 1
                            logger.debug(f"Removed file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Failed to remove {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error cleaning directory {path}: {e}")
        
        return removed_count


class FileSystemMonitor:
    """Monitor file system changes."""
    
    def __init__(self):
        self.watched_files: Dict[str, float] = {}
    
    def add_file(self, file_path: Union[str, Path]) -> None:
        """Add file to monitoring."""
        path = Path(file_path)
        if path.exists():
            self.watched_files[str(path)] = path.stat().st_mtime
    
    def check_changes(self) -> List[str]:
        """
        Check for file changes since last check.
        
        Returns:
            List of changed file paths
        """
        changed_files = []
        
        for file_path_str, last_mtime in self.watched_files.items():
            path = Path(file_path_str)
            
            if not path.exists():
                changed_files.append(file_path_str)
                continue
            
            current_mtime = path.stat().st_mtime
            if current_mtime > last_mtime:
                changed_files.append(file_path_str)
                self.watched_files[file_path_str] = current_mtime
        
        return changed_files


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
    """
    Calculate hash of file contents.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
        
    Returns:
        Hex digest of file hash
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileError(f"File does not exist: {path}")
    
    hash_func = getattr(hashlib, algorithm.lower(), None)
    if not hash_func:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    hasher = hash_func()
    
    try:
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    except Exception as e:
        raise FileError(f"Error calculating hash for {path}: {e}")


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get comprehensive file information.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileError(f"File does not exist: {path}")
    
    try:
        stat = path.stat()
        
        return {
            'path': str(path.absolute()),
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix,
            'size_bytes': stat.st_size,
            'size_human': _format_size(stat.st_size),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
            'is_file': path.is_file(),
            'is_directory': path.is_dir(),
            'is_symlink': path.is_symlink(),
            'permissions': oct(stat.st_mode)[-3:],
            'owner_readable': os.access(path, os.R_OK),
            'owner_writable': os.access(path, os.W_OK),
            'owner_executable': os.access(path, os.X_OK),
        }
        
    except Exception as e:
        raise FileError(f"Error getting file info for {path}: {e}")


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


@contextmanager
def temporary_file(suffix: str = '', prefix: str = 'tmp', dir: Optional[Path] = None):
    """
    Context manager for temporary files.
    
    Args:
        suffix: File suffix
        prefix: File prefix
        dir: Directory for temp file
        
    Yields:
        Path to temporary file
    """
    temp_file = None
    try:
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix, 
            prefix=prefix, 
            dir=dir, 
            delete=False
        )
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        yield temp_path
        
    finally:
        if temp_file and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary file {temp_path}: {e}")


@contextmanager
def temporary_directory(suffix: str = '', prefix: str = 'tmp', dir: Optional[Path] = None):
    """
    Context manager for temporary directories.
    
    Args:
        suffix: Directory suffix
        prefix: Directory prefix
        dir: Parent directory
        
    Yields:
        Path to temporary directory
    """
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
        temp_path = Path(temp_dir)
        
        yield temp_path
        
    finally:
        if temp_dir and temp_path.exists():
            try:
                shutil.rmtree(temp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary directory {temp_path}: {e}")


# Global instances for convenience
safe_file_handler = SafeFileHandler()
json_handler = JSONFileHandler()
yaml_handler = YAMLFileHandler()
csv_handler = CSVFileHandler()
config_handler = ConfigFileHandler()


# Convenience functions
def read_text(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """Read text file."""
    return safe_file_handler.read_text_file(file_path, encoding)


def write_text(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
    """Write text file."""
    safe_file_handler.write_text_file(file_path, content, encoding)


def read_json(file_path: Union[str, Path]) -> Any:
    """Read JSON file."""
    return json_handler.read_json(file_path)


def write_json(file_path: Union[str, Path], data: Any, indent: int = 2) -> None:
    """Write JSON file."""
    json_handler.write_json(file_path, data, indent)


def read_yaml(file_path: Union[str, Path]) -> Any:
    """Read YAML file."""
    return yaml_handler.read_yaml(file_path)


def write_yaml(file_path: Union[str, Path], data: Any) -> None:
    """Write YAML file."""
    yaml_handler.write_yaml(file_path, data)


def read_csv(file_path: Union[str, Path], has_header: bool = True) -> List[Dict[str, str]]:
    """Read CSV file."""
    return csv_handler.read_csv(file_path, has_header)


def write_csv(file_path: Union[str, Path], data: List[Dict[str, Any]]) -> None:
    """Write CSV file."""
    csv_handler.write_csv(file_path, data)