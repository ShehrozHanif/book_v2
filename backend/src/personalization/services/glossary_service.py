"""
Glossary Service for managing technical terminology with bilingual support.

Handles:
1. Fetching glossary terms in English and Urdu
2. Searching terms by keyword
3. Managing glossary feedback/suggestions
4. Caching for performance
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_, func
from uuid import UUID
import logging

from src.personalization.models.db_models import (
    GlossaryTerm,
    GlossaryFeedback
)

logger = logging.getLogger(__name__)


class GlossaryService:
    """Service for managing technical glossary terms."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the glossary service.

        Args:
            db: AsyncSession for database operations
        """
        self.db = db

    async def get_term(
        self,
        english_term: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a glossary term by English term.

        Args:
            english_term: English term to search for

        Returns:
            dict: Term with english_term, urdu_translation, pronunciation,
                  definitions, category, status
                  or None if not found
        """
        try:
            query = select(GlossaryTerm).where(
                GlossaryTerm.english_term.ilike(f"%{english_term}%")
            )
            result = await self.db.execute(query)
            term = result.scalar_one_or_none()

            if not term:
                return None

            return term.to_dict()
        except Exception as e:
            logger.error(f"Error fetching glossary term '{english_term}': {str(e)}")
            return None

    async def search_terms(
        self,
        query_text: str,
        language: str = "english",
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search glossary terms by keyword.

        Args:
            query_text: Search keyword
            language: Search in english_term or urdu_translation
            category: Filter by category (robotics, control, kinematics, etc.)
            limit: Maximum results

        Returns:
            list: Matching terms with full metadata
        """
        try:
            if language.lower() == "urdu":
                search_column = GlossaryTerm.urdu_translation
            else:
                search_column = GlossaryTerm.english_term

            query = select(GlossaryTerm).where(
                search_column.ilike(f"%{query_text}%")
            )

            if category:
                query = query.where(GlossaryTerm.category.ilike(f"%{category}%"))

            query = query.where(
                GlossaryTerm.status == "published"
            ).limit(limit)

            result = await self.db.execute(query)
            terms = result.scalars().all()

            return [t.to_dict() for t in terms]
        except Exception as e:
            logger.error(f"Error searching glossary: {str(e)}")
            return []

    async def list_terms(
        self,
        category: Optional[str] = None,
        status: str = "published",
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all glossary terms with optional filtering.

        Args:
            category: Filter by category
            status: Filter by status (published, under_review)
            limit: Maximum results
            offset: Pagination offset

        Returns:
            list: Glossary terms
        """
        try:
            query = select(GlossaryTerm).where(
                GlossaryTerm.status == status
            )

            if category:
                query = query.where(
                    GlossaryTerm.category.ilike(f"%{category}%")
                )

            query = query.offset(offset).limit(limit)

            result = await self.db.execute(query)
            terms = result.scalars().all()

            return [t.to_dict() for t in terms]
        except Exception as e:
            logger.error(f"Error listing glossary terms: {str(e)}")
            return []

    async def create_term(
        self,
        english_term: str,
        urdu_translation: str,
        pronunciation_transliterated: str,
        definition_english: str,
        definition_urdu: str,
        category: Optional[str] = None,
        status: str = "published"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new glossary term.

        Args:
            english_term: English term
            urdu_translation: Urdu translation
            pronunciation_transliterated: Phonetic pronunciation in Latin characters
            definition_english: English definition
            definition_urdu: Urdu definition
            category: Category (robotics, control, kinematics, etc.)
            status: Publication status

        Returns:
            dict: Created term or None if error
        """
        try:
            # Check if term already exists
            existing = await self.get_term(english_term)
            if existing:
                logger.warning(f"Glossary term '{english_term}' already exists")
                return None

            term = GlossaryTerm(
                english_term=english_term,
                urdu_translation=urdu_translation,
                pronunciation_transliterated=pronunciation_transliterated,
                definition_english=definition_english,
                definition_urdu=definition_urdu,
                category=category,
                status=status
            )
            self.db.add(term)
            await self.db.commit()
            await self.db.refresh(term)

            return term.to_dict()
        except Exception as e:
            logger.error(f"Error creating glossary term: {str(e)}")
            await self.db.rollback()
            return None

    async def update_term(
        self,
        english_term: str,
        urdu_translation: Optional[str] = None,
        pronunciation_transliterated: Optional[str] = None,
        definition_english: Optional[str] = None,
        definition_urdu: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing glossary term.

        Args:
            english_term: Term to update
            urdu_translation: New Urdu translation
            pronunciation_transliterated: New pronunciation
            definition_english: New English definition
            definition_urdu: New Urdu definition
            category: New category
            status: New status

        Returns:
            dict: Updated term or None if not found
        """
        try:
            term = await self.get_term(english_term)
            if not term:
                return None

            # Build update values
            update_values = {}
            if urdu_translation:
                update_values["urdu_translation"] = urdu_translation
            if pronunciation_transliterated:
                update_values["pronunciation_transliterated"] = pronunciation_transliterated
            if definition_english:
                update_values["definition_english"] = definition_english
            if definition_urdu:
                update_values["definition_urdu"] = definition_urdu
            if category is not None:
                update_values["category"] = category
            if status:
                update_values["status"] = status

            if not update_values:
                return term

            # Execute update
            query = update(GlossaryTerm).where(
                GlossaryTerm.english_term == english_term
            ).values(**update_values)
            await self.db.execute(query)
            await self.db.commit()

            # Return updated term
            return await self.get_term(english_term)
        except Exception as e:
            logger.error(f"Error updating glossary term: {str(e)}")
            await self.db.rollback()
            return None

    async def get_categories(self) -> List[str]:
        """
        Get list of all glossary categories.

        Returns:
            list: Unique categories
        """
        try:
            query = select(GlossaryTerm.category).where(
                GlossaryTerm.category.isnot(None)
            ).distinct()
            result = await self.db.execute(query)
            categories = result.scalars().all()

            return list(set(c for c in categories if c))
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []

    async def create_feedback(
        self,
        user_id: UUID,
        feedback_type: str,
        content: str,
        glossary_term_id: Optional[UUID] = None,
        suggested_term: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create glossary feedback/suggestion from user.

        Args:
            user_id: User submitting feedback
            feedback_type: Type (suggestion, correction, new_term)
            content: Feedback content
            glossary_term_id: Related term (if applicable)
            suggested_term: Suggested term (for new_term type)

        Returns:
            dict: Created feedback or None if error
        """
        try:
            feedback = GlossaryFeedback(
                user_id=user_id,
                glossary_term_id=glossary_term_id,
                suggested_term=suggested_term,
                feedback_type=feedback_type,
                content=content,
                status="pending"
            )
            self.db.add(feedback)
            await self.db.commit()
            await self.db.refresh(feedback)

            return feedback.to_dict()
        except Exception as e:
            logger.error(f"Error creating glossary feedback: {str(e)}")
            await self.db.rollback()
            return None

    async def get_pending_feedback(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get pending glossary feedback for admin review.

        Args:
            limit: Maximum results

        Returns:
            list: Pending feedback items
        """
        try:
            query = select(GlossaryFeedback).where(
                GlossaryFeedback.status == "pending"
            ).limit(limit)

            result = await self.db.execute(query)
            feedback_items = result.scalars().all()

            return [f.to_dict() for f in feedback_items]
        except Exception as e:
            logger.error(f"Error getting pending feedback: {str(e)}")
            return []


def get_glossary_service(db: AsyncSession) -> GlossaryService:
    """
    Factory function to create GlossaryService instance.

    Args:
        db: AsyncSession for database operations

    Returns:
        GlossaryService: Service instance
    """
    return GlossaryService(db)
