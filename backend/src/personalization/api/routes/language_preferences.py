"""
Language Preference API Routes (T057)

Endpoints for managing user language preferences:
- GET /api/v1/users/me/language-preference - Get user's preference
- PUT /api/v1/users/me/language-preference - Set user's preference
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session
from src.personalization.models.db_models import User
from src.personalization.utils.auth import get_current_user
from src.personalization.services.language_preference_service import (
    get_user_preference,
    set_user_preference,
    validate_language,
)

router = APIRouter(prefix="/api/v1/users", tags=["language-preferences"])
logger = logging.getLogger(__name__)


@router.get("/me/language-preference")
async def get_language_preference(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's language preference.

    Returns:
        {
            "language": "english" or "urdu",
            "updated_at": "2026-02-10T12:00:00"
        }
    """
    try:
        preference = await get_user_preference(db, current_user.user_id)
        logger.info(f"Retrieved language preference for user {current_user.user_id}")
        return preference
    except Exception as e:
        logger.error(f"Error retrieving language preference: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put("/me/language-preference")
async def set_language_preference(
    preference_data: dict,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Set user's language preference.

    Request Body:
    {
        "language": "english" or "urdu"
    }

    Returns:
        Updated preference with timestamp
    """
    if "language" not in preference_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="language field is required"
        )

    language = preference_data.get("language", "").strip()

    if not language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="language cannot be empty"
        )

    # Validate language
    if not validate_language(language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language. Supported: english, urdu"
        )

    try:
        preference = await set_user_preference(db, current_user.user_id, language)
        logger.info(f"Set language preference for user {current_user.user_id} to {language}")
        return preference
    except Exception as e:
        logger.error(f"Error setting language preference: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{user_id}/language-preference")
async def get_user_language_preference(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get another user's language preference (for admin/profile viewing).

    Only admins can view other users' preferences.
    """
    # Allow user to view own preference
    if current_user.user_id == user_id:
        try:
            preference = await get_user_preference(db, user_id)
            logger.info(f"Retrieved language preference for user {user_id}")
            return preference
        except Exception as e:
            logger.error(f"Error retrieving language preference: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Only admins can view other users' preferences
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view other users' preferences"
        )

    try:
        preference = await get_user_preference(db, user_id)
        logger.info(f"Admin {current_user.user_id} retrieved language preference for user {user_id}")
        return preference
    except Exception as e:
        logger.error(f"Error retrieving user preference: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
