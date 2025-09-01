"""
LRU Cache system exercise for the Data Structures module.

This module provides a comprehensive exercise for implementing an LRU (Least Recently Used)
cache system that demonstrates the combination of multiple data structures to achieve
optimal performance characteristics.
"""

from collections import OrderedDict
import time
import threading
import sys
from typing import Any, Optional, Dict, List, Tuple


class CacheExercise:
    """LRU Cache system implementation exercise."""
    
    @staticmethod
    def get_exercise() -> Dict[str, Any]:
        """Get the complete LRU Cache implementation exercise."""
        return {
            "title": "LRU Cache System Implementation",
            "difficulty": "hard",
            "topic": "advanced_collections",
            "estimated_time": "2-3 hours",
            "instructions": """
Design and implement a comprehensive LRU (Least Recently Used) cache system
that combines multiple data structures to achieve O(1) operations for both
get and put operations while maintaining cache size limits and providing
advanced features like TTL and statistics.

This exercise demonstrates practical application of:
- OrderedDict for maintaining insertion/access order
- Hash tables for O(1) lookups
- Time-based algorithms for TTL implementation
- Thread synchronization for concurrent access
- Memory management and monitoring
""",
            "learning_objectives": [
                "Understand LRU cache algorithms and their applications",
                "Combine OrderedDict with custom logic for optimal performance",
                "Implement O(1) time complexity for all cache operations",
                "Add TTL (Time To Live) functionality for automatic expiration",
                "Provide comprehensive cache statistics and monitoring",
                "Create thread-safe version for concurrent access",
                "Practice memory management and resource optimization"
            ],
            "tasks": [
                {
                    "step": 1,
                    "title": "Basic LRU Cache Implementation",
                    "description": "Implement core LRU cache functionality",
                    "requirements": [
                        "Initialize cache with capacity limit",
                        "get(key) - retrieve value and mark as recently used",
                        "put(key, value) - store value and handle capacity limits",
                        "delete(key) - remove specific key",
                        "clear() - remove all entries",
                        "Maintain O(1) complexity for all operations",
                        "Handle edge cases (empty cache, capacity of 1, etc.)"
                    ],
                    "hints": [
                        "OrderedDict maintains insertion order automatically",
                        "Use move_to_end() to mark items as recently used",
                        "Check capacity before adding new items",
                        "Remove from the beginning for LRU eviction"
                    ]
                },
                {
                    "step": 2,
                    "title": "Cache Statistics and Monitoring",
                    "description": "Add comprehensive monitoring and statistics",
                    "requirements": [
                        "Track hits, misses, and evictions",
                        "Calculate hit rate and other performance metrics",
                        "Monitor cache size and capacity utilization",
                        "Provide detailed statistics reporting",
                        "Track operation counts (puts, deletes, etc.)"
                    ],
                    "hints": [
                        "Use a dictionary to store various counters",
                        "Update counters in each operation",
                        "Calculate derived metrics like hit rate",
                        "Include timestamp information for monitoring"
                    ]
                },
                {
                    "step": 3,
                    "title": "TTL (Time To Live) Functionality",
                    "description": "Implement time-based expiration",
                    "requirements": [
                        "Add TTL parameter to cache initialization",
                        "Store timestamps for each cache entry",
                        "Automatic expiration of old entries",
                        "Cleanup mechanism for expired entries",
                        "Handle TTL in get/put operations"
                    ],
                    "hints": [
                        "Use time.time() for timestamps",
                        "Store timestamps in a separate dictionary",
                        "Check expiration before returning values",
                        "Clean up expired entries periodically"
                    ]
                },
                {
                    "step": 4,
                    "title": "Advanced Features",
                    "description": "Implement sophisticated cache features",
                    "requirements": [
                        "Memory usage estimation and limits",
                        "Peek operation (get without affecting LRU order)",
                        "Bulk operations (get_many, put_many)",
                        "Cache warming and preloading capabilities",
                        "Iterator support for cache contents"
                    ],
                    "hints": [
                        "Use sys.getsizeof() for memory estimation",
                        "Implement __contains__, __len__, __iter__",
                        "Consider using weak references for large objects",
                        "Add methods that don't affect LRU order"
                    ]
                },
                {
                    "step": 5,
                    "title": "Thread Safety",
                    "description": "Create thread-safe concurrent version",
                    "requirements": [
                        "Thread-safe operations using appropriate locks",
                        "Concurrent access monitoring and statistics",
                        "Performance optimization for multi-threaded use",
                        "Deadlock prevention and proper lock management",
                        "Per-thread operation tracking"
                    ],
                    "hints": [
                        "Use threading.RLock() for reentrant locks",
                        "Apply locks consistently across all operations",
                        "Track which threads are accessing the cache",
                        "Consider lock granularity for performance"
                    ]
                }
            ],
            "starter_code": CacheExercise._get_starter_code(),
            "test_cases": CacheExercise._get_test_cases(),
            "solution": CacheExercise._get_solution(),
            "extensions": [
                "Implement LFU (Least Frequently Used) eviction policy",
                "Add cache persistence to disk",
                "Implement distributed cache with consistent hashing",
                "Add cache warming from database/API",
                "Implement write-through and write-back policies"
            ]
        }
    
    @staticmethod
    def _get_starter_code() -> str:
        """Get the starter code template."""
        return '''
from collections import OrderedDict
import time
import threading
from typing import Any, Optional, Dict

class LRUCache:
    """LRU Cache implementation with TTL support."""
    
    def __init__(self, capacity: int, ttl: Optional[float] = None):
        """
        Initialize LRU Cache.
        
        Args:
            capacity: Maximum number of items to store
            ttl: Time to live in seconds (None for no expiration)
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.ttl = ttl
        # TODO: Initialize your data structures here
        # Hint: You'll need OrderedDict for the cache and dict for timestamps
        pass
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Get value by key and mark as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found and not expired, None otherwise
        """
        # TODO: Implement get operation
        # 1. Check if key exists
        # 2. Check if key has expired (if TTL is set)
        # 3. Move to end to mark as recently used
        # 4. Update statistics
        # 5. Return value or None
        pass
    
    def put(self, key: Any, value: Any) -> None:
        """
        Put key-value pair in cache.
        
        Args:
            key: The key to store
            value: The value to store
        """
        # TODO: Implement put operation
        # 1. Check if key already exists (update case)
        # 2. Check capacity and evict if necessary
        # 3. Add new entry with timestamp
        # 4. Update statistics
        pass
    
    def delete(self, key: Any) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: The key to delete
            
        Returns:
            True if key was deleted, False if not found
        """
        # TODO: Implement deletion
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        # TODO: Return statistics dictionary
        # Include: hits, misses, hit_rate, current_size, capacity, etc.
        pass

class ThreadSafeLRUCache(LRUCache):
    """Thread-safe version of LRU Cache."""
    
    def __init__(self, capacity: int, ttl: Optional[float] = None):
        super().__init__(capacity, ttl)
        # TODO: Add threading support
        # Hint: Use threading.RLock() for reentrant locks
        pass
    
    def get(self, key: Any) -> Optional[Any]:
        """Thread-safe get operation."""
        # TODO: Add locking around parent get() call
        pass
    
    def put(self, key: Any, value: Any) -> None:
        """Thread-safe put operation."""
        # TODO: Add locking around parent put() call
        pass

# Test your implementation
if __name__ == "__main__":
    print("=== Testing Basic LRU Cache ===")
    cache = LRUCache(3)
    
    # Test basic operations
    cache.put('a', 1)
    cache.put('b', 2)
    cache.put('c', 3)
    print(f"Cache after adding a,b,c: {list(cache.items()) if hasattr(cache, 'items') else 'Implement items() method'}")
    
    # Test LRU behavior
    print(f"Get 'a': {cache.get('a')}")
    cache.put('d', 4)  # Should evict 'b'
    print(f"Cache after getting 'a' and adding 'd': {list(cache.items()) if hasattr(cache, 'items') else 'Implement items() method'}")
    
    # Test statistics
    stats = cache.get_stats()
    print(f"Cache statistics: {stats}")
    
    print("\\n=== Testing TTL Cache ===")
    ttl_cache = LRUCache(5, ttl=1.0)  # 1 second TTL
    ttl_cache.put('temp', 'expires_soon')
    print(f"Get 'temp' immediately: {ttl_cache.get('temp')}")
    
    time.sleep(1.1)
    print(f"Get 'temp' after expiration: {ttl_cache.get('temp')}")
'''
    
    @staticmethod
    def _get_test_cases() -> List[Dict[str, Any]]:
        """Get comprehensive test cases."""
        return [
            {
                "name": "Basic Operations",
                "description": "Test fundamental cache operations",
                "code": """
cache = LRUCache(3)
cache.put('a', 1)
cache.put('b', 2)
cache.put('c', 3)

assert cache.get('a') == 1
assert cache.get('b') == 2
assert cache.get('c') == 3
assert cache.get('d') is None

# Test capacity limit
cache.put('d', 4)  # Should evict least recently used
assert len(cache) == 3
""",
                "expected_behavior": "Cache maintains capacity and provides correct values"
            },
            {
                "name": "LRU Eviction",
                "description": "Test least recently used eviction policy",
                "code": """
cache = LRUCache(3)
cache.put('a', 1)
cache.put('b', 2)
cache.put('c', 3)

# Make 'a' most recently used
cache.get('a')

# Add new item - should evict 'b' (least recently used)
cache.put('d', 4)

assert cache.get('a') == 1  # Still there
assert cache.get('b') is None  # Evicted
assert cache.get('c') == 3  # Still there
assert cache.get('d') == 4  # Newly added
""",
                "expected_behavior": "Least recently used items are evicted first"
            },
            {
                "name": "TTL Expiration",
                "description": "Test time-based expiration",
                "code": """
import time

cache = LRUCache(5, ttl=0.1)  # 100ms TTL
cache.put('temp', 'value')

assert cache.get('temp') == 'value'  # Should exist

time.sleep(0.15)  # Wait for expiration

assert cache.get('temp') is None  # Should be expired
""",
                "expected_behavior": "Items expire after TTL duration"
            },
            {
                "name": "Statistics Tracking",
                "description": "Test cache statistics",
                "code": """
cache = LRUCache(3)

# Generate some hits and misses
cache.put('a', 1)
cache.put('b', 2)

cache.get('a')  # Hit
cache.get('b')  # Hit
cache.get('c')  # Miss

stats = cache.get_stats()

assert stats['hits'] >= 2
assert stats['misses'] >= 1
assert 'hit_rate' in stats
assert stats['current_size'] == 2
""",
                "expected_behavior": "Statistics accurately track cache operations"
            },
            {
                "name": "Thread Safety",
                "description": "Test concurrent access",
                "code": """
import threading
import time

cache = ThreadSafeLRUCache(100)
results = []

def worker(worker_id):
    for i in range(50):
        key = f"key_{worker_id}_{i}"
        cache.put(key, i)
        value = cache.get(key)
        results.append(value == i)

threads = []
for i in range(4):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

assert all(results)  # All operations should succeed
""",
                "expected_behavior": "Cache handles concurrent access correctly"
            }
        ]
    
    @staticmethod
    def _get_solution() -> str:
        """Get the complete solution implementation."""
        return '''
from collections import OrderedDict
import time
import threading
import sys
from typing import Any, Optional, Dict, List, Iterator

class LRUCache:
    """
    Comprehensive LRU Cache implementation with TTL support.
    
    Features:
    - O(1) get and put operations
    - Configurable capacity with LRU eviction
    - Optional TTL (Time To Live) for automatic expiration
    - Comprehensive statistics tracking
    - Memory usage monitoring
    - Iterator support and utility methods
    """
    
    def __init__(self, capacity: int, ttl: Optional[float] = None):
        """
        Initialize LRU Cache.
        
        Args:
            capacity: Maximum number of items to store (must be > 0)
            ttl: Time to live in seconds (None for no expiration)
            
        Raises:
            ValueError: If capacity is not positive
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.ttl = ttl
        
        # Core data structures
        self.cache = OrderedDict()  # Maintains order for LRU
        self.timestamps = {}        # Track creation/update times
        self.access_times = {}      # Track last access times
        
        # Statistics tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0,
            'puts': 0,
            'deletes': 0
        }
    
    def _is_expired(self, key: Any) -> bool:
        """Check if a key has expired based on TTL."""
        if self.ttl is None:
            return False
        
        current_time = time.time()
        return current_time - self.timestamps.get(key, 0) > self.ttl
    
    def _cleanup_expired(self) -> None:
        """Remove all expired entries from the cache."""
        if self.ttl is None:
            return
        
        current_time = time.time()
        expired_keys = []
        
        # Find expired keys
        for key, timestamp in self.timestamps.items():
            if current_time - timestamp > self.ttl:
                expired_keys.append(key)
        
        # Remove expired keys
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
                if key in self.access_times:
                    del self.access_times[key]
                self.stats['expired'] += 1
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Get value by key and mark as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found and not expired, None otherwise
        """
        # Clean up expired entries first
        self._cleanup_expired()
        
        if key not in self.cache:
            self.stats['misses'] += 1
            return None
        
        # Check if the specific key has expired
        if self._is_expired(key):
            # Remove expired item
            del self.cache[key]
            del self.timestamps[key]
            if key in self.access_times:
                del self.access_times[key]
            self.stats['expired'] += 1
            self.stats['misses'] += 1
            return None
        
        # Move to end (mark as most recently used)
        self.cache.move_to_end(key)
        self.access_times[key] = time.time()
        self.stats['hits'] += 1
        return self.cache[key]
    
    def put(self, key: Any, value: Any) -> None:
        """
        Put key-value pair in cache.
        
        Args:
            key: The key to store
            value: The value to store
        """
        # Clean up expired entries first
        self._cleanup_expired()
        current_time = time.time()
        
        if key in self.cache:
            # Update existing key
            self.cache[key] = value
            self.timestamps[key] = current_time
            self.access_times[key] = current_time
            self.cache.move_to_end(key)
        else:
            # Add new key - check capacity first
            if len(self.cache) >= self.capacity:
                # Remove least recently used (first item in OrderedDict)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
                if oldest_key in self.access_times:
                    del self.access_times[oldest_key]
                self.stats['evictions'] += 1
            
            # Add new entry
            self.cache[key] = value
            self.timestamps[key] = current_time
            self.access_times[key] = current_time
        
        self.stats['puts'] += 1
    
    def delete(self, key: Any) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: The key to delete
            
        Returns:
            True if key was deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
            if key in self.access_times:
                del self.access_times[key]
            self.stats['deletes'] += 1
            return True
        return False
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self.cache.clear()
        self.timestamps.clear()
        self.access_times.clear()
    
    def peek(self, key: Any) -> Optional[Any]:
        """
        Peek at value without affecting LRU order.
        
        Args:
            key: The key to peek at
            
        Returns:
            The value if found and not expired, None otherwise
        """
        if key not in self.cache or self._is_expired(key):
            return None
        return self.cache[key]
    
    def contains(self, key: Any) -> bool:
        """
        Check if key exists in cache and is not expired.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists and is not expired
        """
        return key in self.cache and not self._is_expired(key)
    
    def size(self) -> int:
        """Get current cache size (excluding expired items)."""
        self._cleanup_expired()
        return len(self.cache)
    
    def capacity_remaining(self) -> int:
        """Get remaining capacity."""
        return self.capacity - self.size()
    
    def is_full(self) -> bool:
        """Check if cache is at capacity."""
        return self.size() >= self.capacity
    
    def is_empty(self) -> bool:
        """Check if cache is empty."""
        return self.size() == 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary containing detailed cache statistics
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.2f}%",
            'current_size': self.size(),
            'capacity': self.capacity,
            'capacity_utilization': f"{(self.size() / self.capacity * 100):.1f}%",
            'capacity_remaining': self.capacity_remaining(),
            'ttl': self.ttl,
            'is_full': self.is_full(),
            'is_empty': self.is_empty()
        }
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Estimate memory usage in bytes.
        
        Returns:
            Dictionary with memory usage statistics
        """
        total_size = 0
        
        # Calculate cache content size
        for key, value in self.cache.items():
            total_size += sys.getsizeof(key) + sys.getsizeof(value)
        
        # Add overhead for dictionaries and other structures
        total_size += sys.getsizeof(self.cache)
        total_size += sys.getsizeof(self.timestamps)
        total_size += sys.getsizeof(self.access_times)
        total_size += sys.getsizeof(self.stats)
        
        return {
            'total_bytes': total_size,
            'total_kb': total_size / 1024,
            'total_mb': total_size / (1024 * 1024),
            'avg_bytes_per_item': total_size / len(self.cache) if self.cache else 0
        }
    
    def keys(self) -> List[Any]:
        """Get all keys in LRU order (oldest first, newest last)."""
        self._cleanup_expired()
        return list(self.cache.keys())
    
    def values(self) -> List[Any]:
        """Get all values in LRU order."""
        self._cleanup_expired()
        return list(self.cache.values())
    
    def items(self) -> List[tuple]:
        """Get all key-value pairs in LRU order."""
        self._cleanup_expired()
        return list(self.cache.items())
    
    # Magic methods for Pythonic interface
    def __len__(self) -> int:
        return self.size()
    
    def __contains__(self, key: Any) -> bool:
        return self.contains(key)
    
    def __getitem__(self, key: Any) -> Any:
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key: Any, value: Any) -> None:
        self.put(key, value)
    
    def __delitem__(self, key: Any) -> None:
        if not self.delete(key):
            raise KeyError(key)
    
    def __iter__(self) -> Iterator[Any]:
        self._cleanup_expired()
        return iter(self.cache)
    
    def __repr__(self) -> str:
        return f"LRUCache(capacity={self.capacity}, size={self.size()}, ttl={self.ttl})"


class ThreadSafeLRUCache(LRUCache):
    """
    Thread-safe version of LRU Cache with concurrent access monitoring.
    
    This implementation uses a reentrant lock to ensure thread safety while
    maintaining the performance characteristics of the base LRU cache.
    """
    
    def __init__(self, capacity: int, ttl: Optional[float] = None):
        """
        Initialize thread-safe LRU Cache.
        
        Args:
            capacity: Maximum number of items to store
            ttl: Time to live in seconds (None for no expiration)
        """
        super().__init__(capacity, ttl)
        
        # Use RLock for reentrant locking (allows same thread to acquire multiple times)
        self.lock = threading.RLock()
        
        # Thread-specific statistics
        self.thread_stats = {}
        self.active_threads = set()
    
    def _get_thread_id(self) -> int:
        """Get current thread identifier."""
        return threading.get_ident()
    
    def _update_thread_stats(self, operation: str) -> None:
        """Update per-thread operation statistics."""
        thread_id = self._get_thread_id()
        
        if thread_id not in self.thread_stats:
            self.thread_stats[thread_id] = {
                'operations': 0,
                'last_access': time.time(),
                'operations_by_type': {}
            }
        
        self.thread_stats[thread_id]['operations'] += 1
        self.thread_stats[thread_id]['last_access'] = time.time()
        
        # Track operation types
        op_stats = self.thread_stats[thread_id]['operations_by_type']
        op_stats[operation] = op_stats.get(operation, 0) + 1
        
        self.active_threads.add(thread_id)
    
    def get(self, key: Any) -> Optional[Any]:
        """Thread-safe get operation."""
        with self.lock:
            self._update_thread_stats('get')
            return super().get(key)
    
    def put(self, key: Any, value: Any) -> None:
        """Thread-safe put operation."""
        with self.lock:
            self._update_thread_stats('put')
            super().put(key, value)
    
    def delete(self, key: Any) -> bool:
        """Thread-safe delete operation."""
        with self.lock:
            self._update_thread_stats('delete')
            return super().delete(key)
    
    def clear(self) -> None:
        """Thread-safe clear operation."""
        with self.lock:
            self._update_thread_stats('clear')
            super().clear()
    
    def peek(self, key: Any) -> Optional[Any]:
        """Thread-safe peek operation."""
        with self.lock:
            self._update_thread_stats('peek')
            return super().peek(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics including thread information."""
        with self.lock:
            stats = super().get_stats()
            
            # Add thread-specific information
            stats.update({
                'active_threads': len(self.active_threads),
                'total_threads_seen': len(self.thread_stats),
                'thread_stats': dict(self.thread_stats)  # Copy to avoid modification
            })
            
            return stats
    
    def get_thread_stats(self) -> Dict[int, Dict[str, Any]]:
        """Get detailed per-thread statistics."""
        with self.lock:
            return dict(self.thread_stats)
    
    def cleanup_thread_stats(self, max_age_seconds: float = 3600) -> int:
        """
        Clean up statistics for threads that haven't been active recently.
        
        Args:
            max_age_seconds: Maximum age for thread stats to keep
            
        Returns:
            Number of thread entries cleaned up
        """
        with self.lock:
            current_time = time.time()
            old_threads = []
            
            for thread_id, stats in self.thread_stats.items():
                if current_time - stats['last_access'] > max_age_seconds:
                    old_threads.append(thread_id)
            
            for thread_id in old_threads:
                del self.thread_stats[thread_id]
                self.active_threads.discard(thread_id)
            
            return len(old_threads)
    
    def __repr__(self) -> str:
        return f"ThreadSafeLRUCache(capacity={self.capacity}, size={self.size()}, ttl={self.ttl}, threads={len(self.active_threads)})"


# Comprehensive test suite
def run_comprehensive_tests():
    """Run comprehensive tests for the LRU cache implementation."""
    
    print("=== LRU Cache Comprehensive Test Suite ===\\n")
    
    # Test 1: Basic Operations
    print("Test 1: Basic Operations")
    cache = LRUCache(3)
    
    cache.put('a', 1)
    cache.put('b', 2)
    cache.put('c', 3)
    
    assert cache.get('a') == 1
    assert cache.get('b') == 2
    assert cache.get('c') == 3
    assert cache.get('nonexistent') is None
    assert len(cache) == 3
    
    print("✓ Basic operations work correctly")
    
    # Test 2: LRU Eviction
    print("\\nTest 2: LRU Eviction")
    cache = LRUCache(3)
    
    cache.put('a', 1)
    cache.put('b', 2)
    cache.put('c', 3)
    
    # Access 'a' to make it most recent
    cache.get('a')
    
    # Add 'd' - should evict 'b' (least recently used)
    cache.put('d', 4)
    
    assert cache.get('a') == 1  # Still there
    assert cache.get('b') is None  # Evicted
    assert cache.get('c') == 3  # Still there
    assert cache.get('d') == 4  # Newly added
    
    print("✓ LRU eviction works correctly")
    
    # Test 3: TTL Functionality
    print("\\nTest 3: TTL Functionality")
    ttl_cache = LRUCache(5, ttl=0.1)  # 100ms TTL
    
    ttl_cache.put('temp', 'value')
    assert ttl_cache.get('temp') == 'value'
    
    time.sleep(0.15)  # Wait for expiration
    assert ttl_cache.get('temp') is None
    
    print("✓ TTL expiration works correctly")
    
    # Test 4: Statistics
    print("\\nTest 4: Statistics Tracking")
    cache = LRUCache(3)
    
    cache.put('a', 1)
    cache.put('b', 2)
    
    cache.get('a')  # Hit
    cache.get('b')  # Hit
    cache.get('c')  # Miss
    
    stats = cache.get_stats()
    assert stats['hits'] == 2
    assert stats['misses'] == 1
    assert stats['puts'] == 2
    assert stats['current_size'] == 2
    
    print("✓ Statistics tracking works correctly")
    
    # Test 5: Thread Safety
    print("\\nTest 5: Thread Safety")
    thread_cache = ThreadSafeLRUCache(100)
    results = []
    errors = []
    
    def worker(worker_id):
        try:
            for i in range(50):
                key = f"key_{worker_id}_{i}"
                thread_cache.put(key, i)
                value = thread_cache.get(key)
                results.append(value == i)
        except Exception as e:
            errors.append(e)
    
    threads = []
    for i in range(4):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert all(results), "Some operations failed"
    
    thread_stats = thread_cache.get_stats()
    assert thread_stats['active_threads'] >= 1
    
    print("✓ Thread safety works correctly")
    
    # Test 6: Memory Usage
    print("\\nTest 6: Memory Usage Monitoring")
    cache = LRUCache(10)
    
    for i in range(5):
        cache.put(f"key_{i}", f"value_{i}" * 100)
    
    memory_stats = cache.get_memory_usage()
    assert memory_stats['total_bytes'] > 0
    assert memory_stats['avg_bytes_per_item'] > 0
    
    print("✓ Memory usage monitoring works correctly")
    
    # Test 7: Advanced Features
    print("\\nTest 7: Advanced Features")
    cache = LRUCache(5)
    
    cache.put('a', 1)
    cache.put('b', 2)
    cache.put('c', 3)
    
    # Test peek (doesn't affect LRU order)
    assert cache.peek('a') == 1
    
    # Test contains
    assert 'a' in cache
    assert 'd' not in cache
    
    # Test iteration
    keys = list(cache.keys())
    values = list(cache.values())
    items = list(cache.items())
    
    assert len(keys) == len(values) == len(items) == 3
    
    # Test dict-like interface
    cache['d'] = 4
    assert cache['d'] == 4
    
    del cache['a']
    assert 'a' not in cache
    
    print("✓ Advanced features work correctly")
    
    print("\\n=== All Tests Passed! ===")
    
    # Demo comprehensive usage
    print("\\n=== Comprehensive Usage Demo ===")
    
    # Create cache with TTL
    demo_cache = LRUCache(capacity=5, ttl=2.0)
    
    # Add some data
    for i in range(7):
        demo_cache.put(f"item_{i}", f"value_{i}")
    
    print(f"Cache contents: {demo_cache.items()}")
    print(f"Cache stats: {demo_cache.get_stats()}")
    print(f"Memory usage: {demo_cache.get_memory_usage()}")
    
    # Thread-safe version demo
    ts_cache = ThreadSafeLRUCache(capacity=10, ttl=5.0)
    
    def demo_worker(name):
        for i in range(3):
            key = f"{name}_item_{i}"
            ts_cache.put(key, f"value_from_{name}_{i}")
            retrieved = ts_cache.get(key)
            print(f"  {name}: stored and retrieved {key} = {retrieved}")
    
    print("\\nThread-safe cache demo:")
    
    # Create and start threads
    demo_threads = []
    for name in ['Alice', 'Bob', 'Charlie']:
        t = threading.Thread(target=demo_worker, args=(name,))
        demo_threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in demo_threads:
        t.join()
    
    print(f"\\nFinal thread-safe cache stats: {ts_cache.get_stats()}")
    print(f"Thread statistics: {ts_cache.get_thread_stats()}")


if __name__ == "__main__":
    # Run the comprehensive test suite
    run_comprehensive_tests()
'''

def get_exercise():
    """Get the cache exercise."""
    return CacheExercise.get_exercise()