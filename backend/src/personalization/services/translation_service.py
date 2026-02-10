"""
Translation Service (T048)

Handles translation management, status tracking, and stale detection:
- List translations with status filtering
- Update translations and track versions
- Detect stale translations when English content changes
- Calculate translation metrics
"""

import logging
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import (
    ChatbotResponseTemplate,
    ChatbotResponseTranslationStatus,
    User
)
from src.personalization.services.translation_cache import invalidate_translation_cache
from src.personalization.services.notification_service import notify_translation_stale

logger = logging.getLogger(__name__)


async def list_translations(
    db: AsyncSession,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    List all templates with translation status.

    Args:
        db: Database session
        status: Filter by status (draft, reviewed, published)
        limit: Number of results to return
        offset: Pagination offset

    Returns:
        List of translations with metadata
    """
    try:
        query = select(ChatbotResponseTranslationStatus).join(
            ChatbotResponseTemplate
        )

        if status:
            query = query.where(ChatbotResponseTranslationStatus.status == status)

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        translations = result.scalars().all()

        return [
            {
                "id": t.id,
                "template_id": t.template_id,
                "template_key": t.chatbot_response_template.key if hasattr(t, 'chatbot_response_template') else None,
                "english_content": t.chatbot_response_template.content if hasattr(t, 'chatbot_response_template') else None,
                "urdu_translation": t.urdu_translation,
                "status": t.status,
                "is_stale": t.is_stale,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                "stale_since": t.stale_since.isoformat() if t.stale_since else None,
            }
            for t in translations
        ]
    except Exception as e:
        logger.error(f"Error listing translations: {e}")
        return []


async def get_translation(
    db: AsyncSession,
    template_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get translation details for a specific template.

    Args:
        db: Database session
        template_id: Template ID

    Returns:
        Translation details or None if not found
    """
    try:
        result = await db.execute(
            select(ChatbotResponseTranslationStatus).where(
                ChatbotResponseTranslationStatus.template_id == template_id
            )
        )
        translation = result.scalar_one_or_none()

        if not translation:
            return None

        template = await db.execute(
            select(ChatbotResponseTemplate).where(
                ChatbotResponseTemplate.id == template_id
            )
        )
        template_obj = template.scalar_one_or_none()

        return {
            "id": translation.id,
            "template_id": template_id,
            "template_key": template_obj.key if template_obj else None,
            "english_content": template_obj.content if template_obj else None,
            "urdu_translation": translation.urdu_translation,
            "status": translation.status,
            "is_stale": translation.is_stale,
            "updated_at": translation.updated_at.isoformat() if translation.updated_at else None,
            "stale_since": translation.stale_since.isoformat() if translation.stale_since else None,
            "english_version": _hash_content(template_obj.content if template_obj else ""),
        }
    except Exception as e:
        logger.error(f"Error getting translation {template_id}: {e}")
        return None


async def update_translation(
    db: AsyncSession,
    template_id: int,
    urdu_translation: str
) -> Dict[str, Any]:
    """
    Update template Urdu translation.

    Args:
        db: Database session
        template_id: Template ID
        urdu_translation: New Urdu translation

    Returns:
        Updated translation details
    """
    try:
        # Verify template exists
        template_result = await db.execute(
            select(ChatbotResponseTemplate).where(
                ChatbotResponseTemplate.id == template_id
            )
        )
        template = template_result.scalar_one_or_none()
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Get or create translation status
        trans_result = await db.execute(
            select(ChatbotResponseTranslationStatus).where(
                ChatbotResponseTranslationStatus.template_id == template_id
            )
        )
        translation = trans_result.scalar_one_or_none()

        if not translation:
            translation = ChatbotResponseTranslationStatus(
                template_id=template_id,
                urdu_translation=urdu_translation,
                status="draft",
                is_stale=False
            )
            db.add(translation)
        else:
            translation.urdu_translation = urdu_translation
            translation.updated_at = datetime.utcnow()
            # Reset stale flag when translation is updated
            translation.is_stale = False
            translation.stale_since = None

        await db.commit()
        logger.info(f"Updated translation for template {template_id}")

        # Invalidate cache so new responses use updated translation
        await invalidate_translation_cache(template_id)

        return {
            "id": translation.id,
            "template_id": template_id,
            "english_content": template.content,
            "urdu_translation": translation.urdu_translation,
            "status": translation.status,
            "is_stale": translation.is_stale,
            "updated_at": translation.updated_at.isoformat() if translation.updated_at else None,
        }
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating translation {template_id}: {e}")
        await db.rollback()
        raise


async def update_translation_status(
    db: AsyncSession,
    template_id: int,
    status: str
) -> Dict[str, Any]:
    """
    Update translation status (draft, reviewed, published).

    Args:
        db: Database session
        template_id: Template ID
        status: New status

    Returns:
        Updated translation details
    """
    try:
        # Verify template exists
        template_result = await db.execute(
            select(ChatbotResponseTemplate).where(
                ChatbotResponseTemplate.id == template_id
            )
        )
        template = template_result.scalar_one_or_none()
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Get translation
        trans_result = await db.execute(
            select(ChatbotResponseTranslationStatus).where(
                ChatbotResponseTranslationStatus.template_id == template_id
            )
        )
        translation = trans_result.scalar_one_or_none()
        if not translation:
            raise ValueError(f"Translation for template {template_id} not found")

        translation.status = status
        translation.updated_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Updated translation status for template {template_id} to {status}")

        # Invalidate cache when publishing new translation
        if status == "published":
            await invalidate_translation_cache(template_id)

        return {
            "id": translation.id,
            "template_id": template_id,
            "english_content": template.content,
            "urdu_translation": translation.urdu_translation,
            "status": translation.status,
            "is_stale": translation.is_stale,
            "updated_at": translation.updated_at.isoformat() if translation.updated_at else None,
        }
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating translation status {template_id}: {e}")
        await db.rollback()
        raise


async def list_stale_translations(
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    List stale translations (English content changed).

    Args:
        db: Database session
        limit: Number of results
        offset: Pagination offset

    Returns:
        List of stale translations
    """
    try:
        query = select(ChatbotResponseTranslationStatus).where(
            ChatbotResponseTranslationStatus.is_stale == True
        ).limit(limit).offset(offset)

        result = await db.execute(query)
        translations = result.scalars().all()

        return [
            {
                "id": t.id,
                "template_id": t.template_id,
                "template_key": getattr(t, 'template_key', None),
                "urdu_translation": t.urdu_translation,
                "is_stale": t.is_stale,
                "stale_since": t.stale_since.isoformat() if t.stale_since else None,
                "status": t.status,
            }
            for t in translations
        ]
    except Exception as e:
        logger.error(f"Error listing stale translations: {e}")
        return []


async def mark_translation_stale(
    db: AsyncSession,
    template_id: int
) -> bool:
    """
    Mark translation as stale (English content was updated).

    When a template's English content changes, its Urdu translation is marked
    as stale and admins are notified.

    Args:
        db: Database session
        template_id: Template ID

    Returns:
        True if marked stale, False otherwise
    """
    try:
        # Get the template for notification details
        template_result = await db.execute(
            select(ChatbotResponseTemplate).where(
                ChatbotResponseTemplate.id == template_id
            )
        )
        template = template_result.scalar_one_or_none()

        if not template:
            logger.warning(f"Template {template_id} not found for stale marking")
            return False

        # Get the translation
        trans_result = await db.execute(
            select(ChatbotResponseTranslationStatus).where(
                ChatbotResponseTranslationStatus.template_id == template_id
            )
        )
        translation = trans_result.scalar_one_or_none()

        if translation:
            translation.is_stale = True
            translation.stale_since = datetime.utcnow()
            await db.commit()
            logger.info(f"Marked translation {template_id} as stale")

            # Notify admins of stale translation
            await notify_translation_stale(
                db=db,
                template_id=template_id,
                template_key=template.key,
                english_content=template.content,
                changed_at=datetime.utcnow()
            )

            return True

        return False
    except Exception as e:
        logger.error(f"Error marking translation stale {template_id}: {e}")
        await db.rollback()
        return False


async def get_translation_metrics(
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Get translation completion metrics.

    Returns:
        - total_templates: Total number of templates
        - translated: Number with Urdu translation
        - reviewed: Number marked as reviewed
        - published: Number marked as published
        - percentages for each status
    """
    try:
        result = await db.execute(select(ChatbotResponseTranslationStatus))
        all_translations = result.scalars().all()

        total = len(all_translations)
        if total == 0:
            return {
                "total_templates": 0,
                "translated": 0,
                "reviewed": 0,
                "published": 0,
                "translation_percent": 0,
                "review_percent": 0,
                "published_percent": 0,
                "stale_count": 0,
            }

        translated = sum(1 for t in all_translations if t.urdu_translation)
        reviewed = sum(1 for t in all_translations if t.status == "reviewed")
        published = sum(1 for t in all_translations if t.status == "published")
        stale = sum(1 for t in all_translations if t.is_stale)

        return {
            "total_templates": total,
            "translated": translated,
            "reviewed": reviewed,
            "published": published,
            "translation_percent": round((translated / total * 100) if total > 0 else 0, 2),
            "review_percent": round((reviewed / total * 100) if total > 0 else 0, 2),
            "published_percent": round((published / total * 100) if total > 0 else 0, 2),
            "stale_count": stale,
        }
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {
            "total_templates": 0,
            "translated": 0,
            "reviewed": 0,
            "published": 0,
            "translation_percent": 0,
            "review_percent": 0,
            "published_percent": 0,
            "stale_count": 0,
        }


async def bulk_update_status(
    db: AsyncSession,
    template_ids: List[int],
    status: str
) -> List[Dict[str, Any]]:
    """
    Update status for multiple translations.

    Args:
        db: Database session
        template_ids: List of template IDs
        status: New status

    Returns:
        List of updated translations
    """
    try:
        result = await db.execute(
            select(ChatbotResponseTranslationStatus).where(
                ChatbotResponseTranslationStatus.template_id.in_(template_ids)
            )
        )
        translations = result.scalars().all()

        updated = []
        for translation in translations:
            translation.status = status
            translation.updated_at = datetime.utcnow()
            updated.append({
                "id": translation.id,
                "template_id": translation.template_id,
                "status": translation.status,
            })

        await db.commit()
        logger.info(f"Bulk updated {len(updated)} translations to {status}")

        return updated
    except Exception as e:
        logger.error(f"Error bulk updating translations: {e}")
        await db.rollback()
        return []


def _hash_content(content: str) -> str:
    """Generate hash of content for version tracking."""
    return hashlib.md5(content.encode()).hexdigest()
