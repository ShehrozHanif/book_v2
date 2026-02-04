"""FastAPI dependencies for authentication and authorization."""

from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.database.connection import get_db
from src.personalization.utils.auth import verify_access_token, extract_user_id_from_token
from src.personalization.services.user_service import get_user_by_id

# Security scheme for JWT token authentication
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials with Bearer token
        db: Database session

    Returns:
        User object if authenticated

    Raises:
        HTTPException: 401 if authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Verify token and extract payload
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user from database
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user account is deleted
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deleted",
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to get current user if authenticated, or None for anonymous access.

    Args:
        credentials: HTTP Authorization credentials with Bearer token (optional)
        db: Database session

    Returns:
        User object if authenticated, None if anonymous
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_access_token(token)

        if not payload:
            return None

        user_id_str = payload.get("sub")
        if not user_id_str:
            return None

        user_id = UUID(user_id_str)
        user = await get_user_by_id(db, user_id)

        # Return user only if not deleted
        if user and user.deleted_at is None:
            return user

        return None
    except Exception:
        # If any error occurs during optional auth, return None for anonymous access
        return None


async def require_user_match(
    current_user = Depends(get_current_user),
    user_id: Optional[UUID] = None
):
    """
    Dependency to ensure current user matches the user_id in the request.

    Args:
        current_user: Current authenticated user
        user_id: User ID from request path/body

    Returns:
        Current user if IDs match

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    if user_id and str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access other users' data",
        )

    return current_user


def get_user_id_from_path(user_id: UUID) -> UUID:
    """
    Dependency to extract and validate user_id from path parameters.

    Args:
        user_id: User ID from path parameter

    Returns:
        Validated UUID

    Raises:
        HTTPException: 400 if user_id is invalid
    """
    try:
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )


async def verify_user_owns_resource(
    current_user = Depends(get_current_user),
    resource_user_id: Optional[UUID] = None
):
    """
    Dependency to verify current user owns the resource being accessed.

    Args:
        current_user: Current authenticated user
        resource_user_id: User ID associated with the resource

    Returns:
        Current user if ownership verified

    Raises:
        HTTPException: 403 if user doesn't own resource
    """
    if resource_user_id and str(current_user.user_id) != str(resource_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Resource belongs to another user",
        )

    return current_user


def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        Token string if present, None otherwise
    """
    if not authorization:
        return None

    # Authorization header format: "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


class RateLimitChecker:
    """Rate limit checker for authentication endpoints."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        """
        Initialize rate limiter.

        Args:
            max_attempts: Maximum attempts allowed within window
            window_seconds: Time window in seconds
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts: dict[str, list[float]] = {}

    async def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if identifier has exceeded rate limit.

        Args:
            identifier: Unique identifier (e.g., email or IP)

        Returns:
            True if within rate limit, False if exceeded
        """
        import time

        current_time = time.time()

        # Initialize attempts list if not exists
        if identifier not in self.attempts:
            self.attempts[identifier] = []

        # Remove attempts outside the window
        self.attempts[identifier] = [
            attempt_time for attempt_time in self.attempts[identifier]
            if current_time - attempt_time < self.window_seconds
        ]

        # Check if limit exceeded
        if len(self.attempts[identifier]) >= self.max_attempts:
            return False

        # Record this attempt
        self.attempts[identifier].append(current_time)
        return True


# Global rate limiter instances
login_rate_limiter = RateLimitChecker(max_attempts=5, window_seconds=300)  # 5 attempts per 5 minutes
registration_rate_limiter = RateLimitChecker(max_attempts=3, window_seconds=3600)  # 3 attempts per hour
