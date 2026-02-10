"""
Validation utilities for chatbot translation feature.

Handles:
1. Urdu access validation (require authentication)
2. User ID validation and matching
3. Language parameter validation
4. Request validation
"""

from fastapi import HTTPException, Request, status
from typing import Literal, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class ValidationError(HTTPException):
    """Custom validation error."""

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        super().__init__(status_code=status_code, detail=detail)


def validate_language(language: str) -> Literal['english', 'urdu']:
    """
    Validate and normalize language parameter.

    Args:
        language: Language string (english, urdu, ENGLISH, URDU, etc.)

    Returns:
        Normalized language (english or urdu)

    Raises:
        ValidationError: If language is not supported
    """
    normalized = language.lower().strip()

    if normalized not in ['english', 'urdu']:
        raise ValidationError(
            detail=f"Unsupported language: {language}. Supported languages: english, urdu",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    return normalized  # type: ignore


def validate_urdu_requires_auth(
    language: str,
    is_authenticated: bool
) -> None:
    """
    Validate that Urdu access requires authentication.

    Specification requirement: "urdu translation is available in Rag Chatbot only
    and when we click on urdu translation it ask for login for non-login user"

    Args:
        language: Target language
        is_authenticated: Whether user is authenticated

    Raises:
        HTTPException: 401 if requesting Urdu without authentication
    """
    normalized_lang = validate_language(language)

    if normalized_lang == 'urdu' and not is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for Urdu language content"
        )


def validate_user_id_match(
    request_user_id: Optional[str],
    path_user_id: str
) -> None:
    """
    Validate that authenticated user matches the user in the request path.

    Security check to prevent users from accessing other users' data.

    Args:
        request_user_id: User ID from JWT token
        path_user_id: User ID from request path parameter

    Raises:
        HTTPException: 403 if user doesn't match
    """
    if not request_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    if str(request_user_id) != str(path_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this user's data"
        )


def validate_template_key(template_key: str) -> str:
    """
    Validate template key format.

    Args:
        template_key: Template identifier

    Returns:
        Validated template key

    Raises:
        ValidationError: If template key is invalid
    """
    if not template_key:
        raise ValidationError(detail="Template key cannot be empty")

    if len(template_key) > 255:
        raise ValidationError(detail="Template key is too long (max 255 characters)")

    # Allow alphanumeric, underscore, and hyphen
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-')
    if not all(c in allowed_chars for c in template_key):
        raise ValidationError(
            detail="Template key can only contain letters, numbers, underscores, and hyphens"
        )

    return template_key


def validate_uuid(value: str) -> UUID:
    """
    Validate UUID format.

    Args:
        value: UUID string

    Returns:
        UUID object

    Raises:
        ValidationError: If not valid UUID
    """
    try:
        return UUID(value)
    except ValueError:
        raise ValidationError(
            detail=f"Invalid UUID format: {value}"
        )


def validate_pagination_params(
    limit: int = 100,
    offset: int = 0
) -> tuple[int, int]:
    """
    Validate pagination parameters.

    Args:
        limit: Maximum results
        offset: Pagination offset

    Returns:
        Tuple of (limit, offset)

    Raises:
        ValidationError: If parameters are invalid
    """
    if limit <= 0:
        raise ValidationError(detail="Limit must be greater than 0")

    if limit > 1000:
        raise ValidationError(detail="Limit cannot exceed 1000")

    if offset < 0:
        raise ValidationError(detail="Offset cannot be negative")

    return limit, offset


def validate_search_query(query: str, max_length: int = 100) -> str:
    """
    Validate search query.

    Args:
        query: Search query string
        max_length: Maximum query length

    Returns:
        Validated query

    Raises:
        ValidationError: If query is invalid
    """
    if not query or not query.strip():
        raise ValidationError(detail="Search query cannot be empty")

    if len(query) > max_length:
        raise ValidationError(
            detail=f"Search query is too long (max {max_length} characters)"
        )

    return query.strip()


class RequestValidator:
    """Utility class for validating requests."""

    @staticmethod
    def validate_urdu_with_auth(
        language: str,
        request: Request
    ) -> bool:
        """
        Check if Urdu is requested and validate authentication.

        Returns False if English (no auth needed), raises if Urdu without auth.

        Args:
            language: Target language
            request: FastAPI request

        Returns:
            True if auth is valid/not needed

        Raises:
            HTTPException: 401 if Urdu without auth
        """
        normalized = validate_language(language)

        if normalized == 'english':
            return True

        # Urdu requested - check authentication
        from src.personalization.api.auth_middleware import AuthMiddleware

        try:
            AuthMiddleware.get_authenticated_user(request)
            return True
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for Urdu language content"
            )

    @staticmethod
    def validate_user_access(
        request: Request,
        resource_user_id: str
    ) -> dict:
        """
        Validate user has access to a resource.

        Args:
            request: FastAPI request
            resource_user_id: User ID of resource owner

        Returns:
            User data from JWT token

        Raises:
            HTTPException: 401 if not authenticated, 403 if not authorized
        """
        from src.personalization.api.auth_middleware import (
            AuthMiddleware,
            raise_forbidden_if_not_user
        )

        user = AuthMiddleware.get_authenticated_user(request)
        auth_user_id = user.get('sub')
        raise_forbidden_if_not_user(auth_user_id, resource_user_id)

        return user


def log_validation_error(
    error_type: str,
    details: str,
    user_id: Optional[str] = None
) -> None:
    """
    Log validation errors for monitoring.

    Args:
        error_type: Type of validation error
        details: Error details
        user_id: User ID if available
    """
    user_context = f" (user: {user_id})" if user_id else ""
    logger.warning(
        f"Validation error [{error_type}]{user_context}: {details}"
    )
