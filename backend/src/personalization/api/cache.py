"""In-memory caching system for API responses with TTL support.

This module implements a thread-safe, TTL-aware cache for API responses
to improve performance of frequently accessed endpoints.
"""

import time
import json
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime, timedelta
from uuid import UUID
import asyncio
from functools import wraps


class CacheEntry:
    """Represents a single cache entry with TTL support."""

    def __init__(self, value: Any, ttl_seconds: int):
        """
        Initialize cache entry.

        Args:
            value: The value to cache
            ttl_seconds: Time to live in seconds
        """
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
        self.hit_count = 0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() - self.created_at > self.ttl_seconds

    def refresh_access(self):
        """Update access time for metrics."""
        self.hit_count += 1


class CacheManager:
    """Thread-safe cache manager with TTL and pattern-based invalidation."""

    def __init__(self):
        """Initialize cache manager."""
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "expirations": 0,
        }

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                return None

            entry = self._cache[key]

            if entry.is_expired():
                del self._cache[key]
                self._stats["expirations"] += 1
                self._stats["misses"] += 1
                return None

            entry.refresh_access()
            self._stats["hits"] += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        async with self._lock:
            self._cache[key] = CacheEntry(value, ttl_seconds)

    async def delete(self, key: str) -> bool:
        """
        Delete specific cache entry.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["invalidations"] += 1
                return True
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache entries matching a pattern (e.g., "user:123:*").

        Args:
            pattern: Pattern with wildcards (supports * at end only)

        Returns:
            Number of entries invalidated
        """
        async with self._lock:
            if not pattern.endswith("*"):
                # Exact pattern, just delete that key
                if pattern in self._cache:
                    del self._cache[pattern]
                    self._stats["invalidations"] += 1
                    return 1
                return 0

            # Wildcard pattern: find all matching keys
            prefix = pattern[:-1]  # Remove trailing *
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]

            for key in keys_to_delete:
                del self._cache[key]

            self._stats["invalidations"] += len(keys_to_delete)
            return len(keys_to_delete)

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hit rate, memory usage, etc.
        """
        async with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                round((self._stats["hits"] / total_requests) * 100, 1)
                if total_requests > 0
                else 0
            )

            # Estimate memory usage (rough approximation)
            memory_bytes = sum(
                len(json.dumps(entry.value, default=str))
                for entry in self._cache.values()
            )

            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate_percent": hit_rate,
                "invalidations": self._stats["invalidations"],
                "expirations": self._stats["expirations"],
                "current_size": len(self._cache),
                "memory_usage_bytes": memory_bytes,
            }

    async def reset_stats(self) -> None:
        """Reset cache statistics."""
        async with self._lock:
            self._stats = {
                "hits": 0,
                "misses": 0,
                "invalidations": 0,
                "expirations": 0,
            }


# Global cache instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or create the global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_key_user_specific(endpoint: str, user_id: UUID) -> str:
    """Generate user-specific cache key."""
    return f"{endpoint}:{user_id}"


def cache_key_user_chapter(endpoint: str, user_id: UUID, chapter_id: int) -> str:
    """Generate user+chapter specific cache key."""
    return f"{endpoint}:{user_id}:{chapter_id}"


async def cached_endpoint(
    key: str,
    ttl_seconds: int,
    func: Callable,
    *args,
    **kwargs
) -> Any:
    """
    Execute a function with caching.

    Args:
        key: Cache key
        ttl_seconds: TTL for this cache entry
        func: Async function to call
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Cached or freshly computed value
    """
    cache = await get_cache_manager()

    # Try to get from cache
    cached_value = await cache.get(key)
    if cached_value is not None:
        return cached_value

    # Compute and cache
    value = await func(*args, **kwargs)
    await cache.set(key, value, ttl_seconds)
    return value


async def invalidate_user_cache(user_id: UUID) -> None:
    """
    Invalidate all cache entries for a specific user.

    Args:
        user_id: User ID to invalidate
    """
    cache = await get_cache_manager()
    await cache.invalidate_pattern(f"*:{user_id}:*")
    await cache.invalidate_pattern(f"*:{user_id}")


async def invalidate_user_chapter_cache(user_id: UUID, chapter_id: int) -> None:
    """
    Invalidate cache entries for a specific user+chapter.

    Args:
        user_id: User ID
        chapter_id: Chapter ID
    """
    cache = await get_cache_manager()
    await cache.invalidate_pattern(f"*:{user_id}:{chapter_id}")


class CacheDecorator:
    """Decorator for caching function results."""

    def __init__(self, ttl_seconds: int, key_builder: Optional[Callable] = None):
        """
        Initialize cache decorator.

        Args:
            ttl_seconds: Cache TTL in seconds
            key_builder: Optional function to build cache key from function args
        """
        self.ttl_seconds = ttl_seconds
        self.key_builder = key_builder

    def __call__(self, func: Callable) -> Callable:
        """Decorate an async function."""

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            cache = await get_cache_manager()

            # Build cache key
            if self.key_builder:
                key = self.key_builder(*args, **kwargs)
            else:
                # Default: use function name + str of all args
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value

            # Compute
            value = await func(*args, **kwargs)

            # Cache
            await cache.set(key, value, self.ttl_seconds)

            return value

        return wrapper
