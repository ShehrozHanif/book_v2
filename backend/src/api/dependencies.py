"""Dependency injection utilities and middleware for API routes."""

import logging
from typing import Optional
from fastapi import HTTPException, status

from src.models.schemas import ChatRequest
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# SQL injection patterns to detect and prevent
DANGEROUS_SQL_PATTERNS = [
    "DROP",
    "DELETE",
    "INSERT",
    "UPDATE",
    "ALTER",
    "TRUNCATE",
    "--",
    ";",
    "/*",
    "*/",
    "xp_",
    "sp_",
    "UNION",
    "SELECT",
    "EXEC",
    "EXECUTE",
]


def validate_chat_request(request: ChatRequest) -> ChatRequest:
    """
    Validate and sanitize a chat request.

    This function:
    - Checks query is not empty
    - Enforces max query length
    - Detects potential SQL injection patterns
    - Sanitizes input text

    Args:
        request: ChatRequest to validate

    Returns:
        ChatRequest: Validated request

    Raises:
        HTTPException: If validation fails
    """
    # Check query is not empty or whitespace only
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty or contain only whitespace",
        )

    # Enforce max query length
    if len(request.query) > settings.MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query exceeds maximum length of {settings.MAX_QUERY_LENGTH} characters",
        )

    # Enforce min query length
    if len(request.query) < settings.MIN_QUERY_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query must be at least {settings.MIN_QUERY_LENGTH} character(s)",
        )

    # Check for dangerous SQL patterns
    query_upper = request.query.upper()
    for pattern in DANGEROUS_SQL_PATTERNS:
        if pattern in query_upper:
            logger.warning(f"Potential SQL injection detected - pattern: {pattern}, query: {request.query[:50]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid query - contains prohibited characters or patterns",
            )

    # Validate selected_text if provided
    if request.selected_text is not None:
        if len(request.selected_text) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected text exceeds maximum length of 2000 characters",
            )

    # Validate conversation_id format if provided
    if request.conversation_id is not None:
        if not _is_valid_uuid(request.conversation_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation_id format - must be a valid UUID",
            )

    # Validate user_id format if provided
    if request.user_id is not None:
        if not _is_valid_uuid(request.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format - must be a valid UUID",
            )

    logger.debug(f"Chat request validated successfully - query_length: {len(request.query)}")

    return request


def _is_valid_uuid(value: str) -> bool:
    """
    Check if a string is a valid UUID.

    Args:
        value: String to validate

    Returns:
        bool: True if valid UUID, False otherwise
    """
    try:
        from uuid import UUID

        UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize and normalize a string.

    Args:
        text: String to sanitize
        max_length: Optional maximum length to enforce

    Returns:
        str: Sanitized string

    Raises:
        ValueError: If text exceeds max_length
    """
    # Remove leading/trailing whitespace
    sanitized = text.strip()

    # Normalize whitespace (collapse multiple spaces)
    sanitized = " ".join(sanitized.split())

    # Enforce max length
    if max_length and len(sanitized) > max_length:
        raise ValueError(f"Text exceeds maximum length of {max_length} characters")

    return sanitized
