"""Cache configuration for endpoints.

Defines which endpoints should be cached and with what TTL.
"""

from typing import Dict, Optional
from enum import Enum


class CacheConfig:
    """Configuration for cache behavior."""

    def __init__(self):
        """Initialize cache configuration."""
        # Endpoint cache configuration: path -> TTL in seconds
        self.endpoint_ttl: Dict[str, int] = {
            # Dashboard (60 second TTL)
            "/api/v1/dashboard/metrics": 60,
            # Learning paths (300 second TTL - 5 minutes)
            "/api/v1/learning-paths": 300,
            "/api/v1/learning-paths/recommended": 300,
            # Achievements (600 second TTL - 10 minutes)
            "/api/v1/users/{user_id}/achievements": 600,
            "/api/v1/progress/{user_id}/achievements": 600,
            # Progress (120 second TTL - 2 minutes)
            "/api/v1/users/{user_id}/progress": 120,
            "/api/v1/users/{user_id}/progress/{chapter_id}": 120,
            # Statistics (300 second TTL)
            "/api/v1/users/{user_id}/statistics": 300,
        }

        # Cache invalidation triggers
        # When these operations occur, invalidate these cache patterns
        self.invalidation_triggers: Dict[str, list] = {
            "complete_chapter": [
                "dashboard:{user_id}",
                "progress:{user_id}:*",
                "statistics:{user_id}",
                "achievements:{user_id}",
            ],
            "retry_chapter": [
                "progress:{user_id}:*",
                "statistics:{user_id}",
            ],
            "update_preferences": [
                "dashboard:{user_id}",
                "paths:{user_id}",
            ],
            "submit_assessment": [
                "dashboard:{user_id}",
                "paths:{user_id}",
                "statistics:{user_id}",
            ],
            "unlock_achievement": [
                "achievements:{user_id}",
                "dashboard:{user_id}",
            ],
        }

    def get_cache_ttl(self, endpoint_path: str) -> Optional[int]:
        """
        Get cache TTL for an endpoint.

        Args:
            endpoint_path: API endpoint path

        Returns:
            TTL in seconds if endpoint is cached, None otherwise
        """
        # Try exact match first
        if endpoint_path in self.endpoint_ttl:
            return self.endpoint_ttl[endpoint_path]

        # Try pattern matching for parameterized endpoints
        for pattern, ttl in self.endpoint_ttl.items():
            # Simple pattern matching: replace {param} with regex
            if self._match_pattern(endpoint_path, pattern):
                return ttl

        return None

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if a path matches a pattern with parameters.

        Args:
            path: Actual request path
            pattern: Pattern with {params}

        Returns:
            True if matches
        """
        import re

        # Replace {param} with ([^/]+) to create regex
        regex_pattern = pattern.replace("{", "(?P<").replace("}", ">[^/]+)")
        regex_pattern = f"^{regex_pattern}$"

        try:
            return bool(re.match(regex_pattern, path))
        except Exception:
            return False

    def get_invalidation_patterns(self, operation: str) -> list:
        """
        Get cache invalidation patterns for an operation.

        Args:
            operation: Operation name (e.g., 'complete_chapter')

        Returns:
            List of cache key patterns to invalidate
        """
        return self.invalidation_triggers.get(operation, [])


# Global cache config instance
_cache_config: Optional[CacheConfig] = None


def get_cache_config() -> CacheConfig:
    """Get or create the global cache configuration."""
    global _cache_config
    if _cache_config is None:
        _cache_config = CacheConfig()
    return _cache_config
