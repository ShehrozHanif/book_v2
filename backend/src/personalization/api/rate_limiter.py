"""
Rate Limiting for Translation Endpoints (T070)

Prevents abuse by limiting requests per user:
- Glossary searches: 100 requests per minute
- Translation endpoints: 50 requests per minute
- Analytics endpoints: 200 requests per hour (admin only)
"""

import logging
import time
from typing import Dict, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter with sliding window."""

    def __init__(self):
        """Initialize rate limiter."""
        # Dictionary of {user_id: {endpoint: [(timestamp, count)]}}
        self.requests: Dict[str, Dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.limits = {
            "/api/v1/glossary": {"requests": 100, "window_seconds": 60},
            "/api/v1/glossary/search": {"requests": 100, "window_seconds": 60},
            "/api/v1/admin/translations": {"requests": 50, "window_seconds": 60},
            "/api/v1/analytics": {"requests": 200, "window_seconds": 3600},
        }

    async def check_rate_limit(
        self, user_id: str, endpoint: str, ip_address: str = None
    ) -> bool:
        """
        Check if request is within rate limits.

        Args:
            user_id: User identifier
            endpoint: API endpoint path
            ip_address: Client IP address

        Returns:
            True if within limits, False if exceeded

        Raises:
            HTTPException: If rate limit exceeded
        """
        # Get rate limit for endpoint
        limit_config = self._get_limit_config(endpoint)
        if not limit_config:
            return True  # No limit for this endpoint

        limit_key = f"{user_id}:{endpoint}"
        now = time.time()
        window_seconds = limit_config["window_seconds"]
        max_requests = limit_config["requests"]

        # Clean up old requests
        self.requests[limit_key] = [
            timestamp
            for timestamp in self.requests[limit_key]
            if now - timestamp < window_seconds
        ]

        # Check if limit exceeded
        if len(self.requests[limit_key]) >= max_requests:
            logger.warning(
                f"Rate limit exceeded for user {user_id} on {endpoint}",
                extra={
                    "user_id": user_id,
                    "endpoint": endpoint,
                    "ip_address": ip_address,
                    "limit": max_requests,
                    "window_seconds": window_seconds,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {max_requests} requests per {window_seconds} seconds",
                headers={
                    "Retry-After": str(window_seconds),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Add current request
        self.requests[limit_key].append(now)

        return True

    def get_remaining_requests(self, user_id: str, endpoint: str) -> Tuple[int, int]:
        """
        Get remaining requests for user/endpoint.

        Returns:
            Tuple of (remaining_requests, reset_time_seconds)
        """
        limit_config = self._get_limit_config(endpoint)
        if not limit_config:
            return (limit_config["requests"], limit_config["window_seconds"])

        limit_key = f"{user_id}:{endpoint}"
        now = time.time()
        window_seconds = limit_config["window_seconds"]
        max_requests = limit_config["requests"]

        # Clean up old requests
        self.requests[limit_key] = [
            timestamp
            for timestamp in self.requests[limit_key]
            if now - timestamp < window_seconds
        ]

        remaining = max(0, max_requests - len(self.requests[limit_key]))

        # Calculate reset time
        if self.requests[limit_key]:
            oldest = min(self.requests[limit_key])
            reset_time = int((oldest + window_seconds - now))
        else:
            reset_time = 0

        return (remaining, reset_time)

    def _get_limit_config(self, endpoint: str) -> Dict:
        """Get rate limit config for endpoint."""
        # Check exact match
        if endpoint in self.limits:
            return self.limits[endpoint]

        # Check prefix match
        for pattern, config in self.limits.items():
            if endpoint.startswith(pattern):
                return config

        return None


class RateLimitMiddleware:
    """Middleware for enforcing rate limits."""

    def __init__(self, app, limiter: RateLimiter):
        """Initialize middleware."""
        self.app = app
        self.limiter = limiter

    async def __call__(self, request: Request, call_next):
        """Process request through rate limiter."""
        # Get user identifier (user_id if authenticated, IP if not)
        user_id = self._get_user_id(request)
        ip_address = request.client.host if request.client else "unknown"

        # Check rate limit
        try:
            await self.limiter.check_rate_limit(user_id, request.url.path, ip_address)
        except HTTPException as e:
            return e

        # Get remaining requests
        remaining, reset_time = self.limiter.get_remaining_requests(
            user_id, request.url.path
        )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(
            self.limiter._get_limit_config(request.url.path).get("requests", "N/A")
        )
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time()) + reset_time
        )

        return response

    def _get_user_id(self, request: Request) -> str:
        """Extract user ID from request."""
        # Try to get from auth header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In production, decode JWT to get user ID
            # For now, use a simple hash of the token
            token = auth_header[7:]
            return f"user:{hash(token)}"

        # Fall back to IP address
        ip = request.client.host if request.client else "unknown"
        return f"ip:{ip}"


# Limit configurations for different endpoints

ENDPOINT_LIMITS = {
    "glossary": {"requests": 100, "window_seconds": 60},  # 100 per minute
    "admin_translations": {"requests": 50, "window_seconds": 60},  # 50 per minute
    "analytics": {"requests": 200, "window_seconds": 3600},  # 200 per hour
    "language_preference": {"requests": 30, "window_seconds": 60},  # 30 per minute
    "notifications": {"requests": 200, "window_seconds": 3600},  # 200 per hour
}
