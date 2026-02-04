"""User preferences API endpoints for personalization settings."""

import logging
from typing import Optional, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session
from src.personalization.api.dependencies import get_current_user
from src.personalization.services.user_service import (
    get_user_by_id,
    update_user_preferences
)
from src.personalization.models.db_models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["preferences"])


# ===== Request/Response Models =====
class PreferencesUpdateRequest(BaseModel):
    """Request model for updating user preferences."""

    explanation_style: Optional[str] = Field(
        None,
        description="Preference for explanation style",
        enum=["theory_first", "example_first"]
    )
    code_language: Optional[str] = Field(
        None,
        description="Preferred programming language for examples",
        enum=["python", "cpp", "both"]
    )
    learning_pace: Optional[str] = Field(
        None,
        description="Preferred learning pace",
        enum=["slow", "medium", "fast"]
    )
    content_focus: Optional[str] = Field(
        None,
        description="Content focus preference",
        enum=["simulation", "hardware", "balanced"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "explanation_style": "example_first",
                "code_language": "python",
                "learning_pace": "medium",
                "content_focus": "balanced"
            }
        }


class PreferencesResponse(BaseModel):
    """Response model for user preferences."""

    explanation_style: str = Field(..., description="Preference for explanation style")
    code_language: str = Field(..., description="Preferred programming language")
    learning_pace: str = Field(..., description="Preferred learning pace")
    content_focus: str = Field(..., description="Content focus preference")

    class Config:
        json_schema_extra = {
            "example": {
                "explanation_style": "example_first",
                "code_language": "python",
                "learning_pace": "medium",
                "content_focus": "balanced"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")


# ===== Endpoints =====
@router.get(
    "/{user_id}/preferences",
    response_model=PreferencesResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get user preferences",
    description="Retrieve learning preferences for a user.",
)
async def get_preferences(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PreferencesResponse:
    """
    Get user's learning preferences.

    Only users can retrieve their own preferences. Admins can retrieve any user's preferences.

    Args:
        user_id: User ID to retrieve preferences for
        session: Database session
        current_user: Current authenticated user

    Returns:
        User's preferences

    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Check authorization - users can only access their own, admins can access any
    if current_user.user_id != user_id and not current_user.is_admin:
        logger.warning(
            f"Unauthorized preference access attempt by {current_user.user_id} "
            f"for user {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own preferences"
        )

    user = await get_user_by_id(session, user_id)
    if not user:
        logger.warning(f"Preferences requested for non-existent user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Return preferences with defaults
    prefs = user.preferences_json or {}
    return PreferencesResponse(
        explanation_style=prefs.get("explanation_style", "example_first"),
        code_language=prefs.get("code_language", "python"),
        learning_pace=prefs.get("learning_pace", "medium"),
        content_focus=prefs.get("content_focus", "balanced")
    )


@router.put(
    "/{user_id}/preferences",
    response_model=PreferencesResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "User not found"},
        403: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Update user preferences",
    description="Update learning preferences for a user.",
)
async def update_preferences(
    user_id: UUID,
    request: PreferencesUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PreferencesResponse:
    """
    Update user's learning preferences.

    Only users can update their own preferences. Admins can update any user's preferences.

    Args:
        user_id: User ID to update
        request: Preferences update request
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated preferences

    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Check authorization
    if current_user.user_id != user_id and not current_user.is_admin:
        logger.warning(
            f"Unauthorized preference update attempt by {current_user.user_id} "
            f"for user {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own preferences"
        )

    user = await get_user_by_id(session, user_id)
    if not user:
        logger.warning(f"Preferences update requested for non-existent user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Build update dictionary from request (only include provided fields)
    updates = {}
    if request.explanation_style is not None:
        updates["explanation_style"] = request.explanation_style
    if request.code_language is not None:
        updates["code_language"] = request.code_language
    if request.learning_pace is not None:
        updates["learning_pace"] = request.learning_pace
    if request.content_focus is not None:
        updates["content_focus"] = request.content_focus

    # Update preferences
    updated_user = await update_user_preferences(session, user_id, updates)

    logger.info(
        f"Preferences updated for user {user_id}: {list(updates.keys())}"
    )

    prefs = updated_user.preferences_json or {}
    return PreferencesResponse(
        explanation_style=prefs.get("explanation_style", "example_first"),
        code_language=prefs.get("code_language", "python"),
        learning_pace=prefs.get("learning_pace", "medium"),
        content_focus=prefs.get("content_focus", "balanced")
    )


@router.post(
    "/{user_id}/preferences/reset",
    response_model=PreferencesResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        403: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Reset preferences to defaults",
    description="Reset a user's preferences to system defaults.",
)
async def reset_preferences(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PreferencesResponse:
    """
    Reset user's preferences to default values.

    Args:
        user_id: User ID to reset
        session: Database session
        current_user: Current authenticated user

    Returns:
        Reset preferences

    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Check authorization
    if current_user.user_id != user_id and not current_user.is_admin:
        logger.warning(
            f"Unauthorized preference reset attempt by {current_user.user_id} "
            f"for user {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only reset your own preferences"
        )

    user = await get_user_by_id(session, user_id)
    if not user:
        logger.warning(f"Preferences reset requested for non-existent user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Reset to defaults
    default_prefs = {
        "explanation_style": "example_first",
        "code_language": "python",
        "learning_pace": "medium",
        "content_focus": "balanced"
    }
    updated_user = await update_user_preferences(session, user_id, default_prefs)

    logger.info(f"Preferences reset to defaults for user {user_id}")

    return PreferencesResponse(
        explanation_style="example_first",
        code_language="python",
        learning_pace="medium",
        content_focus="balanced"
    )
