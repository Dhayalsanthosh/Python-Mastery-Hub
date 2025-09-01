# src/python_mastery_hub/utils/cache_manager.py
"""
Cache Management Utilities - Caching System for Performance

Provides caching mechanisms for frequently accessed data, including
in-memory caching, file-based caching, and cache invalidation strategies.
"""

import json
import pickle
import hashlib
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict
import weakref
import logging
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a single cache entry."""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float] = None
    access_count: int = 0
    last_accessed: float = 0
    size_bytes: int = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.last_accessed == 0:
            self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def access(self) -> None:
        """Mark entry as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()
    
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return time.time() - self.created_at


class MemoryCache:
    """In-memory cache with TTL and size limits."""
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: Optional[float] = 3600,  # 1 hour
        max_memory_mb: Optional[float] = 100
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024) if max_memory_mb else None
        
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._total_size = 0
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0,
            'deletes': 0,
            'memory_usage': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self.stats['misses'] += 1
                return default
            
            if entry.is_expired():
                self._remove_entry(key)
                self.stats['misses'] += 1
                return default
            
            entry.access()
            self.stats['hits'] += 1
            return entry.value
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Set value in cache."""
        with self._lock:
            # Calculate expiration time
            expires_at = None
            if ttl is not None:
                expires_at = time.time() + ttl
            elif self.default_ttl is not None:
                expires_at = time.time() + self.default_ttl
            
            # Estimate size
            size_bytes = self._estimate_size(value)
            
            # Remove existing entry if it exists
            if key in self._cache:
                self._remove_entry(key)
            
            # Check memory limit
            if self.max_memory_bytes and self._total_size + size_bytes > self.max_memory_bytes:
                self._evict_for_memory(size_bytes)
            
            # Check size limit
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                expires_at=expires_at,
                size_bytes=size_bytes,
                tags=tags or []
            )
            
            self._cache[key] = entry
            self._total_size += size_bytes
            self.stats['sets'] += 1
            self.stats['memory_usage'] = self._total_size
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                self.stats['deletes'] += 1
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._total_size = 0
            self.stats['memory_usage'] = 0
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())
    
    def has_key(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        with self._lock:
            entry = self._cache.get(key)
            return entry is not None and not entry.is_expired()
    
    def expire_by_tags(self, tags: List[str]) -> int:
        """Expire all entries with any of the given tags."""
        with self._lock:
            expired_count = 0
            keys_to_remove = []
            
            for key, entry in self._cache.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self._remove_entry(key)
                expired_count += 1
            
            return expired_count
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        with self._lock:
            expired_count = 0
            keys_to_remove = []
            
            for key, entry in self._cache.items():
                if entry.is_expired():
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self._remove_entry(key)
                expired_count += 1
            
            return expired_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                **self.stats,
                'total_entries': len(self._cache),
                'hit_rate': hit_rate,
                'memory_usage_mb': self._total_size / (1024 * 1024)
            }
    
    def get_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get information about a cache entry."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            return {
                'key': entry.key,
                'created_at': datetime.fromtimestamp(entry.created_at),
                'expires_at': datetime.fromtimestamp(entry.expires_at) if entry.expires_at else None,
                'access_count': entry.access_count,
                'last_accessed': datetime.fromtimestamp(entry.last_accessed),
                'age_seconds': entry.age_seconds(),
                'size_bytes': entry.size_bytes,
                'tags': entry.tags,
                'is_expired': entry.is_expired()
            }
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry and update size tracking."""
        entry = self._cache.pop(key, None)
        if entry:
            self._total_size -= entry.size_bytes
            self.stats['memory_usage'] = self._total_size
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
        self._remove_entry(lru_key)
        self.stats['evictions'] += 1
    
    def _evict_for_memory(self, needed_bytes: int) -> None:
        """Evict entries to free up memory."""
        while (self._total_size + needed_bytes > self.max_memory_bytes and 
               self._cache):
            self._evict_lru()
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value."""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, bool):
                return 1
            elif isinstance(value, (list, tuple)):
                return sum(self._estimate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(self._estimate_size(k) + self._estimate_size(v) 
                          for k, v in value.items())
            else:
                # Fallback to pickle size estimation
                return len(pickle.dumps(value))
        except Exception:
            return 1024  # Default estimate


class FileCache:
    """File-based cache with persistence."""
    
    def __init__(
        self, 
        cache_dir: Optional[Path] = None,
        default_ttl: Optional[float] = 86400,  # 24 hours
        max_files: int = 10000
    ):
        self.cache_dir = cache_dir or Path.home() / '.python_mastery_hub' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.max_files = max_files
        
        self._lock = threading.RLock()
        self._index_file = self.cache_dir / 'index.json'
        self._index = self._load_index()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from file cache."""
        with self._lock:
            cache_file = self._get_cache_file(key)
            
            if not cache_file.exists():
                return default
            
            try:
                # Check if expired
                if self._is_expired(key):
                    self.delete(key)
                    return default
                
                # Load value
                with cache_file.open('rb') as f:
                    value = pickle.load(f)
                
                # Update access time
                self._update_access(key)
                
                return value
                
            except Exception as e:
                logger.warning(f"Error reading cache file {cache_file}: {e}")
                self.delete(key)
                return default
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Set value in file cache."""
        with self._lock:
            try:
                # Calculate expiration
                expires_at = None
                if ttl is not None:
                    expires_at = time.time() + ttl
                elif self.default_ttl is not None:
                    expires_at = time.time() + self.default_ttl
                
                # Cleanup if at max files
                if len(self._index) >= self.max_files:
                    self._cleanup_old_files()
                
                # Save value
                cache_file = self._get_cache_file(key)
                with cache_file.open('wb') as f:
                    pickle.dump(value, f)
                
                # Update index
                self._index[key] = {
                    'created_at': time.time(),
                    'expires_at': expires_at,
                    'last_accessed': time.time(),
                    'file_size': cache_file.stat().st_size,
                    'tags': tags or []
                }
                
                self._save_index()
                
            except Exception as e:
                logger.error(f"Error setting cache key {key}: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete entry from file cache."""
        with self._lock:
            cache_file = self._get_cache_file(key)
            
            try:
                if cache_file.exists():
                    cache_file.unlink()
                
                if key in self._index:
                    del self._index[key]
                    self._save_index()
                    return True
                
            except Exception as e:
                logger.warning(f"Error deleting cache key {key}: {e}")
            
            return False
    
    def clear(self) -> None:
        """Clear all cache files."""
        with self._lock:
            try:
                for cache_file in self.cache_dir.glob('*.cache'):
                    cache_file.unlink()
                
                self._index.clear()
                self._save_index()
                
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
    
    def cleanup_expired(self) -> int:
        """Remove expired cache files."""
        with self._lock:
            expired_count = 0
            expired_keys = []
            
            for key in list(self._index.keys()):
                if self._is_expired(key):
                    expired_keys.append(key)
            
            for key in expired_keys:
                if self.delete(key):
                    expired_count += 1
            
            return expired_count
    
    def expire_by_tags(self, tags: List[str]) -> int:
        """Expire all entries with any of the given tags."""
        with self._lock:
            expired_count = 0
            keys_to_expire = []
            
            for key, info in self._index.items():
                entry_tags = info.get('tags', [])
                if any(tag in entry_tags for tag in tags):
                    keys_to_expire.append(key)
            
            for key in keys_to_expire:
                if self.delete(key):
                    expired_count += 1
            
            return expired_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_size = sum(info.get('file_size', 0) for info in self._index.values())
            
            return {
                'total_entries': len(self._index),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'cache_dir': str(self.cache_dir)
            }
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key."""
        # Use hash to avoid filesystem issues with special characters
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _load_index(self) -> Dict[str, Any]:
        """Load cache index from file."""
        if not self._index_file.exists():
            return {}
        
        try:
            with self._index_file.open('r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading cache index: {e}")
            return {}
    
    def _save_index(self) -> None:
        """Save cache index to file."""
        try:
            with self._index_file.open('w') as f:
                json.dump(self._index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache index: {e}")
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        info = self._index.get(key)
        if not info:
            return True
        
        expires_at = info.get('expires_at')
        if expires_at is None:
            return False
        
        return time.time() > expires_at
    
    def _update_access(self, key: str) -> None:
        """Update last access time for key."""
        if key in self._index:
            self._index[key]['last_accessed'] = time.time()
            # Don't save index on every access for performance
    
    def _cleanup_old_files(self) -> None:
        """Remove oldest files to stay under limit."""
        # Sort by last accessed time
        sorted_keys = sorted(
            self._index.keys(),
            key=lambda k: self._index[k].get('last_accessed', 0)
        )
        
        # Remove oldest 10% of files
        remove_count = max(1, len(sorted_keys) // 10)
        for key in sorted_keys[:remove_count]:
            self.delete(key)


class CacheManager:
    """Unified cache manager with multiple cache backends."""
    
    def __init__(
        self,
        memory_cache: Optional[MemoryCache] = None,
        file_cache: Optional[FileCache] = None,
        default_backend: str = 'memory'
    ):
        self.memory_cache = memory_cache or MemoryCache()
        self.file_cache = file_cache or FileCache()
        self.default_backend = default_backend
        
        # Auto-cleanup thread
        self._cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self._cleanup_interval = 300  # 5 minutes
        self._shutdown = threading.Event()
        self._cleanup_thread.start()
    
    def get(
        self, 
        key: str, 
        default: Any = None, 
        backend: Optional[str] = None
    ) -> Any:
        """Get value from cache."""
        backend = backend or self.default_backend
        
        if backend == 'memory':
            return self.memory_cache.get(key, default)
        elif backend == 'file':
            return self.file_cache.get(key, default)
        else:
            raise ValueError(f"Unknown cache backend: {backend}")
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        tags: Optional[List[str]] = None,
        backend: Optional[str] = None
    ) -> None:
        """Set value in cache."""
        backend = backend or self.default_backend
        
        if backend == 'memory':
            self.memory_cache.set(key, value, ttl, tags)
        elif backend == 'file':
            self.file_cache.set(key, value, ttl, tags)
        else:
            raise ValueError(f"Unknown cache backend: {backend}")
    
    def delete(self, key: str, backend: Optional[str] = None) -> bool:
        """Delete from cache."""
        backend = backend or self.default_backend
        
        if backend == 'memory':
            return self.memory_cache.delete(key)
        elif backend == 'file':
            return self.file_cache.delete(key)
        else:
            raise ValueError(f"Unknown cache backend: {backend}")
    
    def clear(self, backend: Optional[str] = None) -> None:
        """Clear cache."""
        if backend is None:
            self.memory_cache.clear()
            self.file_cache.clear()
        elif backend == 'memory':
            self.memory_cache.clear()
        elif backend == 'file':
            self.file_cache.clear()
        else:
            raise ValueError(f"Unknown cache backend: {backend}")
    
    def expire_by_tags(self, tags: List[str], backend: Optional[str] = None) -> int:
        """Expire entries by tags."""
        total_expired = 0
        
        if backend is None:
            total_expired += self.memory_cache.expire_by_tags(tags)
            total_expired += self.file_cache.expire_by_tags(tags)
        elif backend == 'memory':
            total_expired += self.memory_cache.expire_by_tags(tags)
        elif backend == 'file':
            total_expired += self.file_cache.expire_by_tags(tags)
        else:
            raise ValueError(f"Unknown cache backend: {backend}")
        
        return total_expired
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            'memory_cache': self.memory_cache.get_stats(),
            'file_cache': self.file_cache.get_stats()
        }
    
    def shutdown(self) -> None:
        """Shutdown cache manager."""
        self._shutdown.set()
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
    
    def _periodic_cleanup(self) -> None:
        """Periodic cleanup of expired entries."""
        while not self._shutdown.wait(self._cleanup_interval):
            try:
                self.memory_cache.cleanup_expired()
                self.file_cache.cleanup_expired()
            except Exception as e:
                logger.error(f"Error during cache cleanup: {e}")


# Cache decorators
def cached(
    ttl: Optional[float] = None,
    backend: str = 'memory',
    key_func: Optional[Callable] = None,
    tags: Optional[List[str]] = None,
    cache_manager: Optional[CacheManager] = None
):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        backend: Cache backend ('memory' or 'file')
        key_func: Function to generate cache key
        tags: Cache tags for invalidation
        cache_manager: Custom cache manager instance
    """
    def decorator(func: Callable) -> Callable:
        cache = cache_manager or _default_cache_manager
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = _generate_function_key(func, args, kwargs)
            
            # Try to get from cache
            result = cache.get(cache_key, backend=backend)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl, tags=tags, backend=backend)
            
            return result
        
        # Add cache control methods
        wrapper.cache_clear = lambda: cache.expire_by_tags([f"func:{func.__name__}"], backend)
        wrapper.cache_info = lambda: cache.get_stats()
        
        return wrapper
    
    return decorator


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = []
    
    # Add positional args
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    # Add keyword args
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float, bool)):
            key_parts.append(f"{key}={value}")
        else:
            key_parts.append(f"{key}={hash(str(value))}")
    
    return ":".join(key_parts)


def _generate_function_key(func: Callable, args: tuple, kwargs: dict) -> str:
    """Generate cache key for function call."""
    func_name = f"{func.__module__}.{func.__name__}"
    args_key = cache_key(*args, **kwargs)
    return f"func:{func_name}:{args_key}"


# Global cache manager instance
_default_cache_manager = CacheManager()


# Convenience functions
def get_cache() -> CacheManager:
    """Get default cache manager."""
    return _default_cache_manager


def cache_get(key: str, default: Any = None, backend: str = 'memory') -> Any:
    """Get value from default cache."""
    return _default_cache_manager.get(key, default, backend)


def cache_set(
    key: str, 
    value: Any, 
    ttl: Optional[float] = None, 
    backend: str = 'memory'
) -> None:
    """Set value in default cache."""
    _default_cache_manager.set(key, value, ttl, backend=backend)


def cache_delete(key: str, backend: str = 'memory') -> bool:
    """Delete from default cache."""
    return _default_cache_manager.delete(key, backend)


def cache_clear(backend: Optional[str] = None) -> None:
    """Clear default cache."""
    _default_cache_manager.clear(backend)


def cache_stats() -> Dict[str, Any]:
    """Get default cache statistics."""
    return _default_cache_manager.get_stats()