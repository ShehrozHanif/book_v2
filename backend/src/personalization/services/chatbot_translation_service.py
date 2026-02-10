"""
Chatbot Translation Service for managing Urdu translations of chatbot responses.

Handles:
1. Fetching response templates
2. Getting Urdu translations for responses
3. Template management with versioning
4. Translation status tracking
5. Glossary term detection and embedding (T041)
"""

from typing import Optional, List, Dict, Any, Set, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from uuid import UUID
import logging
import re

from src.personalization.models.db_models import (
    ChatbotResponseTemplate,
    ChatbotTranslation,
    ChatbotResponseTranslationStatus
)

logger = logging.getLogger(__name__)


class ChatbotTranslationService:
    """Service for managing chatbot response translations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the translation service.

        Args:
            db: AsyncSession for database operations
        """
        self.db = db

    async def get_response_template(self, template_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a response template by key.

        Args:
            template_key: Unique template identifier

        Returns:
            dict: Template with id, template_key, english_content, version, status
                  or None if not found
        """
        try:
            query = select(ChatbotResponseTemplate).where(
                ChatbotResponseTemplate.template_key == template_key
            )
            result = await self.db.execute(query)
            template = result.scalar_one_or_none()

            if not template:
                return None

            return template.to_dict()
        except Exception as e:
            logger.error(f"Error fetching template {template_key}: {str(e)}")
            return None

    async def get_urdu_translation(
        self,
        template_key: str
    ) -> Optional[str]:
        """
        Get Urdu translation for a response template.

        Args:
            template_key: Template identifier

        Returns:
            str: Urdu translated content or None if not available
        """
        try:
            # First get the template to find its ID
            template = await self.get_response_template(template_key)
            if not template:
                return None

            # Get the Urdu translation
            query = select(ChatbotTranslation).where(
                (ChatbotTranslation.response_template_id == template["id"]) &
                (ChatbotTranslation.language == "urdu") &
                (ChatbotTranslation.status == "published")
            )
            result = await self.db.execute(query)
            translation = result.scalar_one_or_none()

            return translation.translated_content if translation else None
        except Exception as e:
            logger.error(f"Error fetching Urdu translation for {template_key}: {str(e)}")
            return None

    async def get_translated_response(
        self,
        template_key: str,
        language: str = "english"
    ) -> Dict[str, Any]:
        """
        Get translated response in requested language.

        Args:
            template_key: Template identifier
            language: Target language (english, urdu)

        Returns:
            dict: Response with content and metadata
                  Format: {content, template_key, language, version}
        """
        try:
            if language.lower() not in ["english", "urdu"]:
                language = "english"

            template = await self.get_response_template(template_key)
            if not template:
                return {
                    "error": f"Template {template_key} not found",
                    "status": 404
                }

            if language.lower() == "english":
                return {
                    "content": template["english_content"],
                    "template_key": template["template_key"],
                    "language": "english",
                    "version": template["version"],
                    "rtl_enabled": False
                }

            # Get Urdu translation
            urdu_content = await self.get_urdu_translation(template_key)
            if not urdu_content:
                # Fallback to English if translation not available
                logger.warning(
                    f"Urdu translation for {template_key} not available, "
                    f"falling back to English"
                )
                return {
                    "content": template["english_content"],
                    "template_key": template["template_key"],
                    "language": "english",
                    "version": template["version"],
                    "note": "Urdu translation not yet available",
                    "rtl_enabled": False
                }

            return {
                "content": urdu_content,
                "template_key": template["template_key"],
                "language": "urdu",
                "version": template["version"],
                "rtl_enabled": True
            }
        except Exception as e:
            logger.error(f"Error getting translated response: {str(e)}")
            return {
                "error": "Internal server error",
                "status": 500
            }

    async def list_templates(
        self,
        status: Optional[str] = "published",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all response templates.

        Args:
            status: Filter by status (published, draft, archived) or None for all
            limit: Maximum results to return

        Returns:
            list: Templates matching criteria
        """
        try:
            query = select(ChatbotResponseTemplate)
            if status:
                query = query.where(ChatbotResponseTemplate.status == status)
            query = query.limit(limit)

            result = await self.db.execute(query)
            templates = result.scalars().all()

            return [t.to_dict() for t in templates]
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return []

    async def create_template(
        self,
        template_key: str,
        english_content: str,
        status: str = "published"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new response template.

        Args:
            template_key: Unique identifier for template
            english_content: English template content
            status: Publication status (published, draft, archived)

        Returns:
            dict: Created template or None if error
        """
        try:
            # Check if template already exists
            existing = await self.get_response_template(template_key)
            if existing:
                logger.warning(f"Template {template_key} already exists")
                return None

            template = ChatbotResponseTemplate(
                template_key=template_key,
                english_content=english_content,
                status=status,
                version=1
            )
            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)

            return template.to_dict()
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            await self.db.rollback()
            return None

    async def update_template(
        self,
        template_key: str,
        english_content: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing response template.

        Args:
            template_key: Template identifier
            english_content: New English content
            status: New status

        Returns:
            dict: Updated template or None if not found
        """
        try:
            template = await self.get_response_template(template_key)
            if not template:
                return None

            # Build update values
            update_values = {}
            if english_content:
                update_values["english_content"] = english_content
                update_values["version"] = template["version"] + 1
            if status:
                update_values["status"] = status

            if not update_values:
                return template

            # Execute update
            query = update(ChatbotResponseTemplate).where(
                ChatbotResponseTemplate.template_key == template_key
            ).values(**update_values)
            await self.db.execute(query)
            await self.db.commit()

            # Return updated template
            return await self.get_response_template(template_key)
        except Exception as e:
            logger.error(f"Error updating template: {str(e)}")
            await self.db.rollback()
            return None

    async def get_translation_status(
        self,
        template_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get translation coverage status for a template.

        Args:
            template_key: Template identifier

        Returns:
            dict: Status with template_id, english_version, urdu_version, status
                  or None if not found
        """
        try:
            template = await self.get_response_template(template_key)
            if not template:
                return None

            query = select(ChatbotResponseTranslationStatus).where(
                ChatbotResponseTranslationStatus.response_template_id == template["id"]
            )
            result = await self.db.execute(query)
            status_record = result.scalar_one_or_none()

            if not status_record:
                return None

            return status_record.to_dict()
        except Exception as e:
            logger.error(f"Error getting translation status: {str(e)}")
            return None

    def _detect_glossary_terms(
        self,
        content: str,
        glossary_terms: List[str]
    ) -> Set[str]:
        """
        Detect glossary terms present in content.

        Args:
            content: Text content to search
            glossary_terms: List of glossary terms to detect

        Returns:
            set: Terms found in content (case-insensitive)
        """
        found_terms = set()
        content_lower = content.lower()

        for term in glossary_terms:
            # Use word boundaries for accurate matching
            pattern = r'\b' + re.escape(term.lower()) + r'\b'
            if re.search(pattern, content_lower):
                # Find original case version in content
                for original_term in glossary_terms:
                    if original_term.lower() == term.lower():
                        found_terms.add(original_term)
                        break

        return found_terms

    async def get_glossary_terms_for_response(
        self,
        template_key: str,
        language: str = "english"
    ) -> Dict[str, Any]:
        """
        Get response with embedded glossary term metadata.

        Args:
            template_key: Template identifier
            language: Target language (english, urdu)

        Returns:
            dict: Response with glossary metadata
                  Format: {content, glossary_terms, template_key, language}
        """
        try:
            # Get base response
            response = await self.get_translated_response(template_key, language)

            if "error" in response:
                return response

            # Hardcoded common glossary terms for robotics context
            # In production, these would be fetched from glossary database
            glossary_terms = [
                "ROS", "Node", "Topic", "Service", "Action",
                "Publisher", "Subscriber", "Message", "Frame",
                "Transform", "Joint", "Link", "Sensor", "Actuator",
                "Kinematics", "Dynamics", "Control", "Algorithm"
            ]

            content = response.get("content", "")
            found_terms = self._detect_glossary_terms(content, glossary_terms)

            response["glossary_terms"] = list(found_terms)
            response["glossary_enabled"] = len(found_terms) > 0

            logger.info(
                f"Found {len(found_terms)} glossary terms in response {template_key}"
            )

            return response

        except Exception as e:
            logger.error(f"Error embedding glossary terms: {str(e)}")
            return {
                "error": "Internal server error",
                "status": 500
            }

    async def get_enhanced_response(
        self,
        template_key: str,
        language: str = "english",
        include_glossary: bool = True
    ) -> Dict[str, Any]:
        """
        Get fully enhanced response with translations and glossary metadata.

        Args:
            template_key: Template identifier
            language: Target language (english, urdu)
            include_glossary: Whether to embed glossary terms

        Returns:
            dict: Enhanced response with all metadata
        """
        try:
            if include_glossary:
                return await self.get_glossary_terms_for_response(
                    template_key,
                    language
                )
            else:
                return await self.get_translated_response(template_key, language)

        except Exception as e:
            logger.error(f"Error getting enhanced response: {str(e)}")
            return {
                "error": "Internal server error",
                "status": 500
            }


def get_chatbot_translation_service(db: AsyncSession) -> ChatbotTranslationService:
    """
    Factory function to create ChatbotTranslationService instance.

    Args:
        db: AsyncSession for database operations

    Returns:
        ChatbotTranslationService: Service instance
    """
    return ChatbotTranslationService(db)
