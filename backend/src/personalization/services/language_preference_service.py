"""
Language Preference Service for managing user language choices.

Handles:
1. Getting user's language preference
2. Setting/updating language preference
3. Default language handling
4. Preference persistence
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from uuid import UUID
import logging

from src.personalization.models.db_models import UserLanguagePreference

logger = logging.getLogger(__name__)

# Default language for all users
DEFAULT_LANGUAGE = "english"

# Supported languages
SUPPORTED_LANGUAGES = ["english", "urdu"]


class LanguagePreferenceService:
    """Service for managing user language preferences."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the language preference service.

        Args:
            db: AsyncSession for database operations
        """
        self.db = db

    async def get_user_language(self, user_id: UUID) -> str:
        """
        Get user's language preference.

        Returns default language if preference not set.

        Args:
            user_id: User ID

        Returns:
            str: Language preference (english, urdu)
        """
        try:
            query = select(UserLanguagePreference).where(
                UserLanguagePreference.user_id == user_id
            )
            result = await self.db.execute(query)
            preference = result.scalar_one_or_none()

            if not preference:
                return DEFAULT_LANGUAGE

            return preference.language
        except Exception as e:
            logger.error(f"Error getting user language preference: {str(e)}")
            return DEFAULT_LANGUAGE

    async def set_user_language(
        self,
        user_id: UUID,
        language: str
    ) -> bool:
        """
        Set or update user's language preference.

        Args:
            user_id: User ID
            language: Language to set (english, urdu)

        Returns:
            bool: True if successful, False if error
        """
        try:
            if language.lower() not in SUPPORTED_LANGUAGES:
                logger.warning(f"Unsupported language: {language}")
                return False

            # Check if preference exists
            query = select(UserLanguagePreference).where(
                UserLanguagePreference.user_id == user_id
            )
            result = await self.db.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing preference
                update_query = update(UserLanguagePreference).where(
                    UserLanguagePreference.user_id == user_id
                ).values(language=language.lower())
                await self.db.execute(update_query)
            else:
                # Create new preference
                new_preference = UserLanguagePreference(
                    user_id=user_id,
                    language=language.lower()
                )
                self.db.add(new_preference)

            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting user language: {str(e)}")
            await self.db.rollback()
            return False

    async def get_user_preference(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get full language preference object for a user.

        Args:
            user_id: User ID

        Returns:
            dict: Preference with user_id, language, updated_at
        """
        try:
            query = select(UserLanguagePreference).where(
                UserLanguagePreference.user_id == user_id
            )
            result = await self.db.execute(query)
            preference = result.scalar_one_or_none()

            if not preference:
                # Return default preference
                return {
                    "user_id": str(user_id),
                    "language": DEFAULT_LANGUAGE,
                    "updated_at": None
                }

            return preference.to_dict()
        except Exception as e:
            logger.error(f"Error getting user preference: {str(e)}")
            return {
                "user_id": str(user_id),
                "language": DEFAULT_LANGUAGE,
                "error": "Could not fetch preference"
            }

    async def validate_language(self, language: str) -> bool:
        """
        Validate if language is supported.

        Args:
            language: Language to validate

        Returns:
            bool: True if supported, False otherwise
        """
        return language.lower() in SUPPORTED_LANGUAGES

    async def get_supported_languages(self) -> list:
        """
        Get list of supported languages.

        Returns:
            list: Supported language codes
        """
        return SUPPORTED_LANGUAGES.copy()


def get_language_preference_service(db: AsyncSession) -> LanguagePreferenceService:
    """
    Factory function to create LanguagePreferenceService instance.

    Args:
        db: AsyncSession for database operations

    Returns:
        LanguagePreferenceService: Service instance
    """
    return LanguagePreferenceService(db)
