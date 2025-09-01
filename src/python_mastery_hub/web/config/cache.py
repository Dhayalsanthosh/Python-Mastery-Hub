# Location: src/python_mastery_hub/web/config/cache.py

"""
Cache Configuration

Manages caching strategies, Redis connections, cache invalidation,
and performance optimization through caching layers.
"""

import json
import pickle
import asyncio
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib

import redis.asyncio as redis
from redis.asyncio import Redis

from python_mastery_hub.core.config import get_settings
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class CacheStrategy:
    """Cache strategy enumeration and configuration."""
    
    # Cache strategies
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    CACHE_ASIDE = "cache_aside"
    REFRESH_AHEAD = "refresh_ahead"
    
    # TTL configurations (in seconds)
    TTL_SHORT = 300      # 5 minutes
    TTL_MEDIUM = 3600    # 1 hour
    TTL_LONG = 86400     # 24 hours
    TTL_WEEK = 604800    # 7 days
    
    # Cache tiers
    TIER_L1 = "memory"   # In-memory cache
    TIER_L2 = "redis"    # Redis cache
    TIER_L3 = "database" # Database cache


class MemoryCache:
    """In-memory cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        if key in self.cache:
            entry = self.cache[key]
            
            # Check expiration
            if entry['expires_at'] and datetime.now() > entry['expires_at']:
                self.delete(key)
                self.misses += 1
                return None
            
            # Update access time
            self.access_times[key] = datetime.now()
            self.hits += 1
            return entry['value']
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in memory cache."""
        # Evict if at max capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
        
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
        self.access_times[key] = datetime.now()
    
    def delete(self, key: str) -> bool:
        """Delete value from memory cache."""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.access_times.clear()
        self.hits = 0
        self.misses = 0
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        self.delete(lru_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'memory_usage_estimate': sum(
                len(str(entry['value'])) for entry in self.cache.values()
            )
        }


class RedisCache:
    """Redis cache implementation."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.prefix = getattr(settings, 'cache_key_prefix', 'pmh:')
        self.default_ttl = getattr(settings, 'cache_default_ttl', CacheStrategy.TTL_MEDIUM)
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            redis_key = self._make_key(key)
            data = await self.redis.get(redis_key)
            
            if data is None:
                return None
            
            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return pickle.loads(data)
        
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize_json: bool = True
    ) -> bool:
        """Set value in Redis cache."""
        try:
            redis_key = self._make_key(key)
            ttl = ttl or self.default_ttl
            
            # Serialize data
            if serialize_json:
                try:
                    serialized_data = json.dumps(value)
                except (TypeError, ValueError):
                    # Fallback to pickle for complex objects
                    serialized_data = pickle.dumps(value)
                    serialize_json = False
            else:
                serialized_data = pickle.dumps(value)
            
            await self.redis.setex(redis_key, ttl, serialized_data)
            return True
        
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            redis_key = self._make_key(key)
            result = await self.redis.delete(redis_key)
            return result > 0
        
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        try:
            redis_key = self._make_key(key)
            return await self.redis.exists(redis_key) > 0
        
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            redis_pattern = self._make_key(pattern)
            keys = await self.redis.keys(redis_pattern)
            
            if keys:
                return await self.redis.delete(*keys)
            return 0
        
        except Exception as e:
            logger.error(f"Redis clear pattern error for {pattern}: {e}")
            return 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value in cache."""
        try:
            redis_key = self._make_key(key)
            return await self.redis.incrby(redis_key, amount)
        
        except Exception as e:
            logger.error(f"Redis increment error for key {key}: {e}")
            return 0
    
    async def set_hash(self, key: str, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set hash in Redis."""
        try:
            redis_key = self._make_key(key)
            
            # Convert values to strings for Redis hash
            string_mapping = {k: json.dumps(v) if not isinstance(v, str) else v 
                            for k, v in mapping.items()}
            
            await self.redis.hset(redis_key, mapping=string_mapping)
            
            if ttl:
                await self.redis.expire(redis_key, ttl)
            
            return True
        
        except Exception as e:
            logger.error(f"Redis set hash error for key {key}: {e}")
            return False
    
    async def get_hash(self, key: str) -> Optional[Dict[str, Any]]:
        """Get hash from Redis."""
        try:
            redis_key = self._make_key(key)
            hash_data = await self.redis.hgetall(redis_key)
            
            if not hash_data:
                return None
            
            # Convert bytes to strings and parse JSON values
            result = {}
            for k, v in hash_data.items():
                key_str = k.decode() if isinstance(k, bytes) else k
                value_str = v.decode() if isinstance(v, bytes) else v
                
                try:
                    result[key_str] = json.loads(value_str)
                except json.JSONDecodeError:
                    result[key_str] = value_str
            
            return result
        
        except Exception as e:
            logger.error(f"Redis get hash error for key {key}: {e}")
            return None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        try:
            info = await self.redis.info()
            
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0)
            }
        
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {}


class CacheManager:
    """Multi-tier cache manager."""
    
    def __init__(self):
        self.memory_cache = MemoryCache(max_size=getattr(settings, 'memory_cache_size', 1000))
        self.redis_cache: Optional[RedisCache] = None
        self.redis_client: Optional[Redis] = None
        self.cache_strategy = getattr(settings, 'cache_strategy', CacheStrategy.CACHE_ASIDE)
        self.enable_memory_cache = getattr(settings, 'enable_memory_cache', True)
        self.enable_redis_cache = getattr(settings, 'enable_redis_cache', True)
    
    async def initialize(self) -> None:
        """Initialize cache connections."""
        try:
            if self.enable_redis_cache:
                await self._initialize_redis()
            
            logger.info(f"Cache manager initialized with strategy: {self.cache_strategy}")
        
        except Exception as e:
            logger.error(f"Failed to initialize cache manager: {e}")
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection."""
        try:
            redis_url = getattr(settings, 'redis_url', None)
            
            if redis_url:
                self.redis_client = redis.from_url(redis_url)
            else:
                self.redis_client = redis.Redis(
                    host=getattr(settings, 'redis_host', 'localhost'),
                    port=getattr(settings, 'redis_port', 6379),
                    db=getattr(settings, 'redis_db', 0),
                    password=getattr(settings, 'redis_password', None),
                    decode_responses=False,
                    socket_timeout=getattr(settings, 'redis_socket_timeout', 5),
                    socket_connect_timeout=getattr(settings, 'redis_connect_timeout', 5),
                    retry_on_timeout=True,
                    max_connections=getattr(settings, 'redis_max_connections', 50)
                )
            
            # Test connection
            await self.redis_client.ping()
            
            self.redis_cache = RedisCache(self.redis_client)
            logger.info("Redis cache initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.enable_redis_cache = False
    
    async def get(self, key: str, use_memory: bool = True, use_redis: bool = True) -> Optional[Any]:
        """Get value from cache with tier fallback."""
        try:
            # Try memory cache first
            if use_memory and self.enable_memory_cache:
                value = self.memory_cache.get(key)
                if value is not None:
                    logger.debug(f"Cache hit (memory): {key}")
                    return value
            
            # Try Redis cache
            if use_redis and self.enable_redis_cache and self.redis_cache:
                value = await self.redis_cache.get(key)
                if value is not None:
                    logger.debug(f"Cache hit (redis): {key}")
                    
                    # Backfill memory cache
                    if use_memory and self.enable_memory_cache:
                        self.memory_cache.set(key, value, CacheStrategy.TTL_SHORT)
                    
                    return value
            
            logger.debug(f"Cache miss: {key}")
            return None
        
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        use_memory: bool = True,
        use_redis: bool = True
    ) -> bool:
        """Set value in cache across tiers."""
        try:
            success = True
            
            # Set in memory cache
            if use_memory and self.enable_memory_cache:
                self.memory_cache.set(key, value, ttl or CacheStrategy.TTL_SHORT)
            
            # Set in Redis cache
            if use_redis and self.enable_redis_cache and self.redis_cache:
                redis_success = await self.redis_cache.set(key, value, ttl)
                success = success and redis_success
            
            if success:
                logger.debug(f"Cache set: {key}")
            
            return success
        
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from all cache tiers."""
        try:
            memory_success = True
            redis_success = True
            
            # Delete from memory cache
            if self.enable_memory_cache:
                memory_success = self.memory_cache.delete(key)
            
            # Delete from Redis cache
            if self.enable_redis_cache and self.redis_cache:
                redis_success = await self.redis_cache.delete(key)
            
            success = memory_success or redis_success
            if success:
                logger.debug(f"Cache delete: {key}")
            
            return success
        
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern from all tiers."""
        try:
            total_deleted = 0
            
            # Clear from memory cache (simple pattern matching)
            if self.enable_memory_cache:
                keys_to_delete = []
                for key in self.memory_cache.cache.keys():
                    if pattern in key or key.startswith(pattern.replace('*', '')):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    if self.memory_cache.delete(key):
                        total_deleted += 1
            
            # Clear from Redis cache
            if self.enable_redis_cache and self.redis_cache:
                redis_deleted = await self.redis_cache.clear_pattern(pattern)
                total_deleted += redis_deleted
            
            logger.info(f"Cache clear pattern '{pattern}': {total_deleted} keys deleted")
            return total_deleted
        
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    async def get_or_set(
        self, 
        key: str, 
        func: Callable, 
        ttl: Optional[int] = None,
        *args, 
        **kwargs
    ) -> Any:
        """Get value from cache or compute and set it."""
        # Try to get from cache
        value = await self.get(key)
        
        if value is not None:
            return value
        
        # Compute value
        try:
            if asyncio.iscoroutinefunction(func):
                value = await func(*args, **kwargs)
            else:
                value = func(*args, **kwargs)
            
            # Set in cache
            await self.set(key, value, ttl)
            
            return value
        
        except Exception as e:
            logger.error(f"Cache get_or_set error for key {key}: {e}")
            raise
    
    def generate_key(self, *parts: Any) -> str:
        """Generate cache key from parts."""
        # Convert parts to strings and join
        key_parts = [str(part) for part in parts]
        key = ':'.join(key_parts)
        
        # Hash long keys
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            return f"hash:{key_hash}"
        
        return key
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {
            'strategy': self.cache_strategy,
            'memory_cache_enabled': self.enable_memory_cache,
            'redis_cache_enabled': self.enable_redis_cache
        }
        
        # Memory cache stats
        if self.enable_memory_cache:
            stats['memory_cache'] = self.memory_cache.get_stats()
        
        # Redis cache stats
        if self.enable_redis_cache and self.redis_cache:
            stats['redis_cache'] = await self.redis_cache.get_stats()
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform cache health check."""
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Test memory cache
        if self.enable_memory_cache:
            try:
                test_key = f"health_check_{datetime.now().timestamp()}"
                self.memory_cache.set(test_key, "test", 10)
                value = self.memory_cache.get(test_key)
                self.memory_cache.delete(test_key)
                
                health['checks']['memory_cache'] = {
                    'status': 'healthy' if value == "test" else 'unhealthy',
                    'latency_ms': 0  # Memory cache is synchronous
                }
            except Exception as e:
                health['checks']['memory_cache'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health['status'] = 'degraded'
        
        # Test Redis cache
        if self.enable_redis_cache and self.redis_cache:
            try:
                start_time = asyncio.get_event_loop().time()
                test_key = f"health_check_{datetime.now().timestamp()}"
                
                await self.redis_cache.set(test_key, "test", 10)
                value = await self.redis_cache.get(test_key)
                await self.redis_cache.delete(test_key)
                
                latency = (asyncio.get_event_loop().time() - start_time) * 1000
                
                health['checks']['redis_cache'] = {
                    'status': 'healthy' if value == "test" else 'unhealthy',
                    'latency_ms': round(latency, 2)
                }
            except Exception as e:
                health['checks']['redis_cache'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health['status'] = 'degraded'
        
        return health
    
    async def close(self) -> None:
        """Close cache connections."""
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            
            if self.enable_memory_cache:
                self.memory_cache.clear()
                logger.info("Memory cache cleared")
        
        except Exception as e:
            logger.error(f"Error closing cache connections: {e}")


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = CacheManager()
        await _cache_manager.initialize()
    
    return _cache_manager


def cache_key(*parts: Any) -> str:
    """Helper function to generate cache keys."""
    return ':'.join(str(part) for part in parts)


def cached(
    ttl: int = CacheStrategy.TTL_MEDIUM,
    key_prefix: str = "",
    use_memory: bool = True,
    use_redis: bool = True
):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = func.__name__
            key_parts = [key_prefix, func_name] if key_prefix else [func_name]
            
            # Add args and kwargs to key
            for arg in args:
                if hasattr(arg, 'id'):
                    key_parts.append(str(arg.id))
                else:
                    key_parts.append(str(arg))
            
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}:{v}")
            
            cache_key = ':'.join(key_parts)
            
            # Get cache manager
            cache = await get_cache_manager()
            
            # Try to get from cache
            cached_result = await cache.get(cache_key, use_memory, use_redis)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache result
            await cache.set(cache_key, result, ttl, use_memory, use_redis)
            
            return result
        
        return wrapper
    return decorator


class CacheInvalidator:
    """Manages cache invalidation strategies."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.invalidation_rules: Dict[str, List[str]] = {}
    
    def add_invalidation_rule(self, trigger_pattern: str, invalidate_patterns: List[str]) -> None:
        """Add cache invalidation rule."""
        self.invalidation_rules[trigger_pattern] = invalidate_patterns
    
    async def invalidate_on_trigger(self, trigger_key: str) -> int:
        """Invalidate caches based on trigger key."""
        total_invalidated = 0
        
        for trigger_pattern, invalidate_patterns in self.invalidation_rules.items():
            if trigger_pattern in trigger_key or trigger_key.startswith(trigger_pattern):
                for pattern in invalidate_patterns:
                    count = await self.cache.clear_pattern(pattern)
                    total_invalidated += count
                    logger.info(f"Invalidated {count} cache entries for pattern: {pattern}")
        
        return total_invalidated
    
    async def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache entries for a specific user."""
        patterns = [
            f"user:{user_id}:*",
            f"progress:{user_id}:*",
            f"session:{user_id}:*",
            f"achievements:{user_id}:*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            count = await self.cache.clear_pattern(pattern)
            total_invalidated += count
        
        logger.info(f"Invalidated {total_invalidated} cache entries for user {user_id}")
        return total_invalidated
    
    async def invalidate_exercise_cache(self, exercise_id: str) -> int:
        """Invalidate cache entries related to a specific exercise."""
        patterns = [
            f"exercise:{exercise_id}:*",
            f"submissions:{exercise_id}:*",
            "exercise:list:*",
            "exercise:stats:*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            count = await self.cache.clear_pattern(pattern)
            total_invalidated += count
        
        logger.info(f"Invalidated {total_invalidated} cache entries for exercise {exercise_id}")
        return total_invalidated


class CacheMetrics:
    """Cache performance metrics and monitoring."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.start_time = datetime.now()
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance metrics."""
        stats = await self.cache.get_stats()
        
        # Calculate derived metrics
        if 'memory_cache' in stats:
            memory_stats = stats['memory_cache']
            memory_stats['utilization_percent'] = (
                memory_stats['size'] / memory_stats['max_size'] * 100
            )
        
        if 'redis_cache' in stats:
            redis_stats = stats['redis_cache']
            total_ops = redis_stats.get('keyspace_hits', 0) + redis_stats.get('keyspace_misses', 0)
            if total_ops > 0:
                redis_stats['hit_rate_percent'] = (
                    redis_stats.get('keyspace_hits', 0) / total_ops * 100
                )
        
        # Add uptime
        uptime = datetime.now() - self.start_time
        stats['uptime_seconds'] = int(uptime.total_seconds())
        
        return stats
    
    async def get_cache_efficiency_report(self) -> Dict[str, Any]:
        """Generate cache efficiency report."""
        metrics = await self.get_performance_metrics()
        
        recommendations = []
        
        # Memory cache analysis
        if 'memory_cache' in metrics:
            memory = metrics['memory_cache']
            if memory['hit_rate'] < 50:
                recommendations.append("Consider increasing memory cache size or TTL")
            if memory['utilization_percent'] > 90:
                recommendations.append("Memory cache is near capacity, consider increasing size")
        
        # Redis cache analysis
        if 'redis_cache' in metrics:
            redis = metrics['redis_cache']
            if redis.get('hit_rate_percent', 0) < 70:
                recommendations.append("Redis hit rate is low, review caching strategy")
        
        return {
            'metrics': metrics,
            'recommendations': recommendations,
            'overall_health': 'good' if len(recommendations) == 0 else 'needs_attention'
        }