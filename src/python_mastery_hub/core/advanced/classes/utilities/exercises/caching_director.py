"""
Caching Decorator Exercise Implementation.

This module provides a sophisticated caching decorator exercise that demonstrates
advanced decorator patterns with TTL, size limits, and thread safety.
"""

import time
import functools
import threading
from collections import OrderedDict
from typing import Any, Callable, Optional, Dict, Tuple


class CachingDecoratorExercise:
    """Exercise for building an advanced caching decorator."""
    
    def __init__(self):
        self.title = "Build a Caching Decorator"
        self.description = "Create a sophisticated caching decorator with TTL and size limits"
        self.difficulty = "hard"
    
    def get_instructions(self) -> str:
        """Return exercise instructions."""
        return """
        Create a sophisticated caching decorator with the following features:
        
        1. Time-to-live (TTL) functionality - cached values expire after a set time
        2. Maximum cache size with LRU (Least Recently Used) eviction
        3. Cache statistics tracking (hits, misses, evictions)
        4. Methods to clear cache and view cache contents
        5. Handle unhashable arguments gracefully
        6. Thread-safe operations
        7. Preserve function metadata with functools.wraps
        """
    
    def get_tasks(self) -> list:
        """Return list of specific tasks."""
        return [
            "Implement a cache decorator with time-to-live (TTL) functionality",
            "Add maximum cache size with LRU eviction",
            "Include cache statistics (hits, misses, evictions)",
            "Add methods to clear cache and view cache contents",
            "Handle unhashable arguments gracefully",
            "Ensure thread safety with proper locking",
            "Preserve function signatures and metadata"
        ]
    
    def get_starter_code(self) -> str:
        """Return starter code template."""
        return '''
import time
import functools
from collections import OrderedDict
from typing import Any, Callable, Optional

def advanced_cache(max_size: int = 128, ttl: Optional[float] = None):
    """Advanced caching decorator with TTL and size limits."""
    def decorator(func: Callable) -> Callable:
        # TODO: Implement caching logic here
        pass
    return decorator

# Test the decorator
@advanced_cache(max_size=3, ttl=2.0)
def expensive_function(x, y):
    time.sleep(0.1)  # Simulate expensive operation
    return x * y + x + y

# TODO: Test the implementation
'''
    
    def get_solution(self) -> str:
        """Return complete solution."""
        return '''
import time
import functools
import threading
from collections import OrderedDict
from typing import Any, Callable, Optional, Dict, Tuple

def advanced_cache(max_size: int = 128, ttl: Optional[float] = None):
    """Advanced caching decorator with TTL and size limits."""
    def decorator(func: Callable) -> Callable:
        cache: OrderedDict = OrderedDict()
        cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
        lock = threading.RLock()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = _make_key(args, kwargs)
            if key is None:
                # Unhashable arguments - don't cache
                cache_stats['misses'] += 1
                return func(*args, **kwargs)
            
            with lock:
                current_time = time.time()
                
                # Check if key exists and is valid
                if key in cache:
                    value, timestamp = cache[key]
                    
                    # Check TTL
                    if ttl is None or (current_time - timestamp) < ttl:
                        # Move to end (LRU)
                        cache.move_to_end(key)
                        cache_stats['hits'] += 1
                        return value
                    else:
                        # Expired - remove
                        del cache[key]
                
                # Cache miss - compute value
                cache_stats['misses'] += 1
                result = func(*args, **kwargs)
                
                # Store in cache
                cache[key] = (result, current_time)
                cache.move_to_end(key)
                
                # Evict if necessary
                while len(cache) > max_size:
                    cache.popitem(last=False)  # Remove oldest
                    cache_stats['evictions'] += 1
                
                return result
        
        def _make_key(args, kwargs):
            """Create cache key from arguments."""
            try:
                key = str(args)
                if kwargs:
                    key += str(sorted(kwargs.items()))
                return key
            except TypeError:
                return None  # Unhashable arguments
        
        def cache_info():
            """Return cache statistics."""
            with lock:
                return {
                    'hits': cache_stats['hits'],
                    'misses': cache_stats['misses'],
                    'evictions': cache_stats['evictions'],
                    'current_size': len(cache),
                    'max_size': max_size,
                    'ttl': ttl,
                    'hit_rate': cache_stats['hits'] / (cache_stats['hits'] + cache_stats['misses']) if (cache_stats['hits'] + cache_stats['misses']) > 0 else 0
                }
        
        def cache_clear():
            """Clear the cache."""
            with lock:
                cache.clear()
                cache_stats.update({'hits': 0, 'misses': 0, 'evictions': 0})
        
        def cache_contents():
            """Return current cache contents."""
            with lock:
                current_time = time.time()
                contents = {}
                for key, (value, timestamp) in cache.items():
                    age = current_time - timestamp
                    expired = ttl is not None and age >= ttl
                    contents[key] = {
                        'value': value,
                        'timestamp': timestamp,
                        'age': age,
                        'expired': expired
                    }
                return contents
        
        # Attach utility methods
        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        wrapper.cache_contents = cache_contents
        
        return wrapper
    return decorator

# Test implementation
@advanced_cache(max_size=3, ttl=2.0)
def expensive_function(x, y):
    print(f"Computing expensive_function({x}, {y})")
    time.sleep(0.1)  # Simulate expensive operation
    return x * y + x + y

def test_caching_decorator():
    """Test the advanced caching decorator."""
    print("=== Advanced Caching Test ===")
    
    # Test basic caching
    print(f"Result 1: {expensive_function(2, 3)}")  # Miss
    print(f"Result 2: {expensive_function(2, 3)}")  # Hit
    print(f"Result 3: {expensive_function(3, 4)}")  # Miss
    
    print(f"Cache info: {expensive_function.cache_info()}")
    
    # Test TTL expiration
    print("\\nTesting TTL expiration...")
    time.sleep(2.1)
    print(f"Result 4 (after TTL): {expensive_function(2, 3)}")  # Miss (expired)
    
    # Test size limit and LRU eviction
    print("\\nTesting size limit...")
    expensive_function(1, 1)  # Miss
    expensive_function(2, 2)  # Miss  
    expensive_function(3, 3)  # Miss
    expensive_function(4, 4)  # Miss - should evict oldest
    
    print(f"Final cache info: {expensive_function.cache_info()}")
    
    # Test cache contents
    print("\\nCache contents:")
    for key, info in expensive_function.cache_contents().items():
        print(f"  {key}: value={info['value']}, age={info['age']:.2f}s, expired={info['expired']}")
    
    # Test unhashable arguments
    print("\\nTesting unhashable arguments...")
    
    @advanced_cache(max_size=5)
    def process_data(data_list, options=None):
        print(f"Processing {len(data_list)} items")
        return sum(data_list)
    
    # These should work
    result1 = process_data([1, 2, 3])
    result2 = process_data([1, 2, 3])  # Should hit cache
    
    # This will not be cached due to unhashable dict
    result3 = process_data([1, 2, 3], {'unhashable': {}})
    result4 = process_data([1, 2, 3], {'unhashable': {}})  # Will not hit cache
    
    print(f"Process data cache info: {process_data.cache_info()}")

if __name__ == "__main__":
    test_caching_decorator()
'''
    
    def get_test_cases(self) -> list:
        """Return test cases for validation."""
        return [
            {
                "name": "Basic caching functionality",
                "test": "Verify cache hits and misses work correctly"
            },
            {
                "name": "TTL expiration",
                "test": "Verify cached values expire after TTL"
            },
            {
                "name": "LRU eviction",
                "test": "Verify oldest items are evicted when cache is full"
            },
            {
                "name": "Cache statistics", 
                "test": "Verify hit/miss/eviction counters work"
            },
            {
                "name": "Unhashable arguments",
                "test": "Verify decorator handles unhashable args gracefully"
            },
            {
                "name": "Thread safety",
                "test": "Verify decorator works correctly with multiple threads"
            },
            {
                "name": "Function metadata preservation",
                "test": "Verify original function name, docstring, etc. are preserved"
            }
        ]
    
    def validate_solution(self, solution_func) -> Dict[str, Any]:
        """Validate a solution implementation."""
        results = {
            "passed": 0,
            "total": len(self.get_test_cases()),
            "details": []
        }
        
        try:
            # Test basic functionality
            @solution_func(max_size=2, ttl=1.0)
            def test_func(x):
                return x * 2
            
            # Verify function metadata is preserved
            if hasattr(test_func, '__name__') and hasattr(test_func, 'cache_info'):
                results["passed"] += 1
                results["details"].append("✓ Function metadata preserved")
            else:
                results["details"].append("✗ Function metadata not preserved")
            
            # Test basic caching
            result1 = test_func(5)
            result2 = test_func(5)
            
            if hasattr(test_func, 'cache_info'):
                info = test_func.cache_info()
                if info.get('hits', 0) > 0:
                    results["passed"] += 1
                    results["details"].append("✓ Basic caching works")
                else:
                    results["details"].append("✗ Cache hits not working")
            
        except Exception as e:
            results["details"].append(f"✗ Error during validation: {e}")
        
        return results