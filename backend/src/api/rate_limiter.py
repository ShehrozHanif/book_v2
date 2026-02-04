"""Rate limiting middleware for API endpoints."""

import time
import logging
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter based on IP address."""

    def __init__(self, requests_per_period: int = 10, period_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests_per_period: Number of allowed requests
            period_seconds: Time period in seconds
        """
        self.requests_per_period = requests_per_period
        self.period_seconds = period_seconds
        self.request_history: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> Tuple[bool, Dict]:
        """
        Check if request is allowed for the given client.

        Args:
            client_id: Unique identifier for the client (e.g., IP address)

        Returns:
            Tuple of (is_allowed, rate_limit_info)
                - is_allowed: Boolean indicating if request should be allowed
                - rate_limit_info: Dictionary with rate limit details
        """
        now = time.time()
        request_times = self.request_history[client_id]

        # Remove timestamps outside the current window
        request_times[:] = [t for t in request_times if now - t < self.period_seconds]

        # Check if request is within limit
        is_allowed = len(request_times) < self.requests_per_period

        if is_allowed:
            request_times.append(now)

        remaining = self.requests_per_period - len(request_times)
        reset_time = int(now + self.period_seconds) if request_times else int(now)

        info = {
            "limit": self.requests_per_period,
            "remaining": max(0, remaining),
            "reset": reset_time,
            "window_seconds": self.period_seconds,
        }

        return is_allowed, info

    def cleanup(self):
        """Clean up old entries from request history (called periodically)."""
        now = time.time()
        to_remove = []

        for client_id, request_times in self.request_history.items():
            request_times[:] = [t for t in request_times if now - t < self.period_seconds * 10]

            if not request_times:
                to_remove.append(client_id)

        for client_id in to_remove:
            del self.request_history[client_id]


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.

    Handles proxied requests by checking X-Forwarded-For header.

    Args:
        request: FastAPI request object

    Returns:
        str: Client IP address
    """
    # Check for forwarded IP (behind proxy)
    if request.headers.get("x-forwarded-for"):
        return request.headers["x-forwarded-for"].split(",")[0].strip()

    # Check for other common proxy headers
    if request.headers.get("cf-connecting-ip"):
        return request.headers["cf-connecting-ip"]

    # Use direct connection IP
    return request.client.host if request.client else "unknown"


async def rate_limit_middleware(request: Request, limiter: RateLimiter):
    """
    Rate limit middleware to check request quotas.

    Args:
        request: FastAPI request object
        limiter: RateLimiter instance

    Returns:
        None if request allowed

    Raises:
        HTTPException: If rate limit exceeded
    """
    client_ip = get_client_ip(request)
    is_allowed, info = limiter.is_allowed(client_ip)

    # Add rate limit headers to response
    request.state.rate_limit_info = info

    if not is_allowed:
        logger.warning(f"Rate limit exceeded for client IP: {client_ip}")

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {info['limit']} requests per {info['window_seconds']} seconds",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset"]),
            },
        )

    return None


async def add_rate_limit_headers(request: Request, call_next):
    """
    Middleware to add rate limit headers to responses.

    Args:
        request: FastAPI request object
        call_next: Next middleware/handler

    Returns:
        Response with rate limit headers
    """
    response = await call_next(request)

    if hasattr(request.state, "rate_limit_info"):
        info = request.state.rate_limit_info
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])

    return response
