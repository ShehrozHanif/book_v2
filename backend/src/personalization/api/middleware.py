"""API middleware for caching and performance optimization."""

import json
from typing import Optional
from uuid import UUID
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from src.personalization.api.cache import (
    get_cache_manager,
    cache_key_user_specific,
    cache_key_user_chapter,
)
from src.personalization.api.cache_config import get_cache_config


class CachingMiddleware(BaseHTTPMiddleware):
    """Middleware for caching API responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and cache response if applicable.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response (cached or fresh)
        """
        # Only cache GET requests
        if request.method != "GET":
            response = await call_next(request)
            return response

        # Get cache config
        cache_config = get_cache_config()
        cache_ttl = cache_config.get_cache_ttl(request.url.path)

        # If endpoint not cached, proceed normally
        if cache_ttl is None:
            response = await call_next(request)
            return response

        # Build cache key
        cache_key = await self._build_cache_key(request, request.url.path)
        if not cache_key:
            # Can't build cache key, skip caching
            response = await call_next(request)
            return response

        # Try to get from cache
        cache_manager = await get_cache_manager()
        cached_response = await cache_manager.get(cache_key)

        if cached_response is not None:
            # Return cached response
            return StarletteResponse(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=dict(cached_response["headers"]),
                media_type=cached_response.get("media_type", "application/json"),
            )

        # Get fresh response
        response = await call_next(request)

        # Cache if response is successful
        if response.status_code == 200:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Store in cache
            cached_data = {
                "content": body,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "media_type": response.media_type,
            }
            await cache_manager.set(cache_key, cached_data, cache_ttl)

            # Return response with cached body
            return StarletteResponse(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        return response

    async def _build_cache_key(self, request: Request, path: str) -> Optional[str]:
        """
        Build cache key from request.

        Args:
            request: Request object
            path: Request path

        Returns:
            Cache key or None if can't build
        """
        try:
            # Extract user_id from Authorization header
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer "):
                return None

            # For now, we'll use path as key prefix
            # In production, extract user_id from token and use it
            # This is a simplified approach for the middleware

            if "/dashboard/metrics" in path:
                return f"dashboard-metrics:{auth_header[-16:]}"  # Use last 16 chars of token as ID
            elif "/learning-paths" in path:
                return f"learning-paths:{auth_header[-16:]}"
            elif "/achievements" in path:
                return f"achievements:{auth_header[-16:]}"
            elif "/progress" in path and "{chapter_id}" not in path:
                return f"progress:{auth_header[-16:]}"
            elif "/statistics" in path:
                return f"statistics:{auth_header[-16:]}"

            return None
        except Exception:
            return None


class CacheInvalidationMiddleware(BaseHTTPMiddleware):
    """Middleware for invalidating cache on mutations."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and invalidate cache if needed.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response
        """
        # Get response first
        response = await call_next(request)

        # Only invalidate cache for successful mutations
        if response.status_code >= 200 and response.status_code < 300:
            # Check what operation this is
            operation = self._get_operation_type(request)

            if operation:
                # Invalidate relevant caches
                cache_manager = await get_cache_manager()
                cache_config = get_cache_config()

                patterns = cache_config.get_invalidation_patterns(operation)

                # Extract user_id from auth header for pattern substitution
                auth_header = request.headers.get("authorization", "")
                user_id_part = auth_header[-16:] if auth_header else "unknown"

                for pattern in patterns:
                    # Simple substitution
                    invalidation_pattern = pattern.replace("{user_id}", user_id_part)
                    await cache_manager.invalidate_pattern(invalidation_pattern)

        return response

    def _get_operation_type(self, request: Request) -> Optional[str]:
        """
        Determine operation type from request.

        Args:
            request: Request object

        Returns:
            Operation type string or None
        """
        path = request.url.path
        method = request.method

        if method == "POST":
            if "/complete" in path:
                return "complete_chapter"
            elif "/retry" in path:
                return "retry_chapter"
            elif "/assessment" in path:
                return "submit_assessment"

        elif method == "PUT" or method == "PATCH":
            if "/preferences" in path:
                return "update_preferences"
            elif "/progress" in path:
                return "update_progress"

        return None
