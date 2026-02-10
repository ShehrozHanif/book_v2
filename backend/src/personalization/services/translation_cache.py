"""
Translation Cache Invalidation Service (T053)

Manages cache invalidation when translations are updated:
- Invalidate cached responses when template translation changes
- Clear user-specific response cache
- Track cache hit/miss statistics
"""

import logging
from typing import Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class TranslationCacheManager:
    """
    Manages caching and invalidation of chatbot responses.

    When a translation is updated:
    1. Invalidate cached versions of that response
    2. Force new responses to be generated with updated translation
    3. Old chat history remains unchanged with original translation
    """

    def __init__(self):
        """Initialize cache manager."""
        self._cache: dict = {}
        self._invalidations: Set[int] = set()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
        }

    def get_cached_response(
        self,
        template_id: int,
        user_id: Optional[int] = None,
        language: str = "english"
    ) -> Optional[str]:
        """
        Get cached response for template.

        Args:
            template_id: Template ID
            user_id: Optional user ID for user-specific cache
            language: Language (english, urdu)

        Returns:
            Cached response or None if not found/invalid
        """
        cache_key = self._build_cache_key(template_id, user_id, language)

        # Check if invalidated
        if template_id in self._invalidations:
            logger.debug(f"Cache miss (invalidated): {cache_key}")
            self._stats["misses"] += 1
            return None

        # Check cache
        if cache_key in self._cache:
            logger.debug(f"Cache hit: {cache_key}")
            self._stats["hits"] += 1
            return self._cache[cache_key]

        logger.debug(f"Cache miss: {cache_key}")
        self._stats["misses"] += 1
        return None

    def set_cached_response(
        self,
        template_id: int,
        response: str,
        user_id: Optional[int] = None,
        language: str = "english"
    ) -> None:
        """
        Cache a response.

        Args:
            template_id: Template ID
            response: Response content
            user_id: Optional user ID for user-specific cache
            language: Language (english, urdu)
        """
        cache_key = self._build_cache_key(template_id, user_id, language)

        self._cache[cache_key] = {
            "response": response,
            "timestamp": datetime.utcnow(),
            "template_id": template_id,
            "user_id": user_id,
            "language": language,
        }

        logger.debug(f"Cached response: {cache_key}")

    def invalidate_template(self, template_id: int) -> int:
        """
        Invalidate all cached versions of a template.

        When a translation is updated, this removes all cached versions
        so new requests will use the updated translation.

        Args:
            template_id: Template ID to invalidate

        Returns:
            Number of cache entries removed
        """
        removed_count = 0

        # Add to invalidation set
        self._invalidations.add(template_id)

        # Remove matching cache entries
        keys_to_remove = [
            key for key in self._cache.keys()
            if key.startswith(f"template_{template_id}_")
        ]

        for key in keys_to_remove:
            del self._cache[key]
            removed_count += 1

        self._stats["invalidations"] += 1

        logger.info(f"Invalidated {removed_count} cache entries for template {template_id}")

        return removed_count

    def invalidate_user_cache(self, user_id: int) -> int:
        """
        Invalidate all cached responses for a specific user.

        Args:
            user_id: User ID

        Returns:
            Number of cache entries removed
        """
        removed_count = 0

        keys_to_remove = [
            key for key in self._cache.keys()
            if f"user_{user_id}" in key
        ]

        for key in keys_to_remove:
            del self._cache[key]
            removed_count += 1

        logger.info(f"Invalidated {removed_count} cache entries for user {user_id}")

        return removed_count

    def invalidate_language(self, language: str) -> int:
        """
        Invalidate all cached responses for a language.

        Args:
            language: Language to invalidate (english, urdu)

        Returns:
            Number of cache entries removed
        """
        removed_count = 0

        keys_to_remove = [
            key for key in self._cache.keys()
            if f"lang_{language}" in key
        ]

        for key in keys_to_remove:
            del self._cache[key]
            removed_count += 1

        logger.info(f"Invalidated {removed_count} cache entries for language {language}")

        return removed_count

    def clear_all(self) -> int:
        """
        Clear entire cache.

        Returns:
            Number of cache entries removed
        """
        count = len(self._cache)
        self._cache.clear()
        self._invalidations.clear()

        logger.info(f"Cleared entire cache ({count} entries)")

        return count

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with hits, misses, invalidations, size
        """
        hit_rate = (
            self._stats["hits"] / (self._stats["hits"] + self._stats["misses"] + 1)
            * 100
        )

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "invalidations": self._stats["invalidations"],
            "cache_size": len(self._cache),
        }

    def _build_cache_key(
        self,
        template_id: int,
        user_id: Optional[int] = None,
        language: str = "english"
    ) -> str:
        """Build cache key from components."""
        user_part = f"user_{user_id}" if user_id else "global"
        return f"template_{template_id}_{user_part}_lang_{language}"


# Global instance
_cache_manager: Optional[TranslationCacheManager] = None


def get_cache_manager() -> TranslationCacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = TranslationCacheManager()
    return _cache_manager


async def invalidate_translation_cache(template_id: int) -> int:
    """
    Invalidate cache when translation is updated.

    This function should be called whenever a translation is updated:
    - New responses will use the updated translation
    - Old chat history remains unchanged

    Args:
        template_id: Template ID whose translation was updated

    Returns:
        Number of cache entries invalidated
    """
    manager = get_cache_manager()
    return manager.invalidate_template(template_id)


async def get_cache_statistics() -> dict:
    """Get current cache statistics."""
    manager = get_cache_manager()
    return manager.get_stats()
