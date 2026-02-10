"""
Authentication validation middleware for Urdu translation feature.

Provides:
1. JWT token extraction and validation
2. User context injection into requests
3. Optional Urdu access restriction (requires authentication)
4. Error handling with proper HTTP status codes
"""

from fastapi import HTTPException, status, Request
from typing import Optional, Callable, Any
import jwt
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Get JWT settings from environment
JWT_SECRET = "your-secret-key"  # Should be loaded from .env
JWT_ALGORITHM = "HS256"


class AuthMiddleware:
    """Provides authentication utilities for Urdu translation feature."""

    @staticmethod
    def extract_token(request: Request) -> Optional[str]:
        """
        Extract JWT token from Authorization header.

        Expected format: "Bearer <token>"

        Returns:
            str: JWT token or None if not present
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verify JWT token and extract claims.

        Args:
            token: JWT token string

        Returns:
            dict: Token claims (user_id, email, etc.)

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user_id"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    @staticmethod
    def get_authenticated_user(request: Request) -> dict:
        """
        Get authenticated user from request.

        Args:
            request: FastAPI request object

        Returns:
            dict: User claims including user_id

        Raises:
            HTTPException: If user is not authenticated
        """
        token = AuthMiddleware.extract_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token"
            )

        return AuthMiddleware.verify_token(token)

    @staticmethod
    def require_authentication(func: Callable) -> Callable:
        """
        Decorator to require authentication for an endpoint.

        Usage:
            @require_authentication
            async def my_endpoint(request: Request):
                user = request.state.user
        """
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = AuthMiddleware.get_authenticated_user(request)
            request.state.user = user
            return await func(request, *args, **kwargs)

        return wrapper

    @staticmethod
    def require_urdu_authentication(func: Callable) -> Callable:
        """
        Decorator to require authentication for Urdu language access.

        Prevents guest/unauthenticated users from accessing Urdu content.
        Specification requirement: "ask for login for non-login user"

        Usage:
            @require_urdu_authentication
            async def my_endpoint(request: Request, language: str):
                # language can be "urdu" only if user is authenticated
        """
        @wraps(func)
        async def wrapper(request: Request, *args, language: str = None, **kwargs):
            # If language is not Urdu, allow guest access
            if language and language.lower() != "urdu":
                return await func(request, *args, language=language, **kwargs)

            # For Urdu, require authentication
            try:
                user = AuthMiddleware.get_authenticated_user(request)
                request.state.user = user
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required for Urdu language content"
                )

            return await func(request, *args, language=language, **kwargs)

        return wrapper

    @staticmethod
    def get_user_id_from_request(request: Request) -> str:
        """
        Safely extract user_id from authenticated request.

        Args:
            request: FastAPI request object

        Returns:
            str: User ID UUID

        Raises:
            HTTPException: If user is not authenticated
        """
        user = getattr(request.state, "user", None)
        if not user or "sub" not in user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        return user["sub"]


def validate_request_user_match(request_user_id: str, path_user_id: str) -> bool:
    """
    Validate that the authenticated user matches the user in the request path.

    Security check to prevent users from accessing other users' data.

    Args:
        request_user_id: User ID from JWT token
        path_user_id: User ID from request path parameter

    Returns:
        bool: True if users match, False otherwise
    """
    return str(request_user_id) == str(path_user_id)


def raise_forbidden_if_not_user(request_user_id: str, path_user_id: str) -> None:
    """
    Raise 403 Forbidden if user doesn't match the requested user.

    Args:
        request_user_id: User ID from JWT token
        path_user_id: User ID from request path parameter

    Raises:
        HTTPException: 403 Forbidden if user doesn't match
    """
    if not validate_request_user_match(request_user_id, path_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this user's data"
        )
