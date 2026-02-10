"""
Admin Translation Management API Routes (T047)

Endpoints for managing Urdu translations of chatbot response templates:
- GET /api/v1/admin/translations - List all templates with translation status
- PUT /api/v1/admin/translations/{template_id} - Update template Urdu translation
- POST /api/v1/admin/translations/{template_id}/review - Mark template as reviewed/published
- GET /api/v1/admin/translations/stale - List stale translations
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session
from src.personalization.models.db_models import User, ChatbotResponseTemplate, ChatbotResponseTranslationStatus
from src.personalization.utils.auth import get_current_user
from src.personalization.services import translation_service

router = APIRouter(prefix="/api/v1/admin", tags=["admin-translation"])
logger = logging.getLogger(__name__)


def verify_admin_role(user: User) -> User:
    """Verify user has admin/instructor role."""
    if not user or user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can manage translations"
        )
    return user


@router.get("/translations", response_model=list)
async def list_translations(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List all templates with translation status.

    Query Parameters:
    - status: Filter by status (draft, reviewed, published)
    - limit: Number of results (default: 10)
    - offset: Pagination offset (default: 0)
    """
    verify_admin_role(current_user)

    try:
        translations = await translation_service.list_translations(
            db=db,
            status=status_filter,
            limit=limit,
            offset=offset
        )
        logger.info(f"Listed translations: {len(translations)} items (filter: {status_filter})")
        return translations
    except Exception as e:
        logger.error(f"Error listing translations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/translations/metrics")
async def get_translation_metrics(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get translation completion metrics."""
    verify_admin_role(current_user)

    try:
        metrics = await translation_service.get_translation_metrics(db=db)
        logger.info("Retrieved translation metrics")
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/translations/stale")
async def list_stale_translations(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List stale translations (English content changed).

    Query Parameters:
    - limit: Number of results
    - offset: Pagination offset
    """
    verify_admin_role(current_user)

    try:
        stale = await translation_service.list_stale_translations(
            db=db,
            limit=limit,
            offset=offset
        )
        logger.info(f"Listed stale translations: {len(stale)} items")
        return stale
    except Exception as e:
        logger.error(f"Error listing stale translations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/translations/{template_id}")
async def get_translation(
    template_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get translation details for a specific template."""
    verify_admin_role(current_user)

    try:
        translation = await translation_service.get_translation(
            db=db,
            template_id=template_id
        )
        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found"
            )
        return translation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting translation {template_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put("/translations/{template_id}")
async def update_translation(
    template_id: int,
    update_data: dict,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update template Urdu translation.

    Request Body:
    {
        "urdu_translation": "نیا ترجمہ"
    }
    """
    verify_admin_role(current_user)

    if not update_data.get("urdu_translation"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="urdu_translation is required"
        )

    if not update_data["urdu_translation"].strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="urdu_translation cannot be empty"
        )

    try:
        translation = await translation_service.update_translation(
            db=db,
            template_id=template_id,
            urdu_translation=update_data["urdu_translation"]
        )
        logger.info(f"Updated translation for template {template_id}")
        return translation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating translation {template_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/translations/{template_id}/review")
async def mark_translation_reviewed(
    template_id: int,
    review_data: dict,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mark translation as reviewed or published.

    Request Body:
    {
        "status": "reviewed" or "published"
    }
    """
    verify_admin_role(current_user)

    status_value = review_data.get("status")
    if status_value not in ["reviewed", "published", "draft"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status must be 'draft', 'reviewed', or 'published'"
        )

    try:
        translation = await translation_service.update_translation_status(
            db=db,
            template_id=template_id,
            status=status_value
        )
        logger.info(f"Marked translation {template_id} as {status_value}")
        return translation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating translation status {template_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/translations/bulk-review")
async def bulk_mark_translations(
    bulk_data: dict,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mark multiple translations with the same status.

    Request Body:
    {
        "template_ids": [1, 2, 3],
        "status": "reviewed" or "published"
    }
    """
    verify_admin_role(current_user)

    template_ids = bulk_data.get("template_ids", [])
    status_value = bulk_data.get("status")

    if not template_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="template_ids is required"
        )

    if status_value not in ["reviewed", "published"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status must be 'reviewed' or 'published'"
        )

    try:
        results = await translation_service.bulk_update_status(
            db=db,
            template_ids=template_ids,
            status=status_value
        )
        logger.info(f"Bulk marked {len(results)} translations as {status_value}")
        return {
            "updated": len(results),
            "translations": results
        }
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/translations/bulk-publish")
async def bulk_publish_translations(
    bulk_data: dict,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Publish multiple translations at once.

    Request Body:
    {
        "template_ids": [1, 2, 3]
    }
    """
    verify_admin_role(current_user)

    template_ids = bulk_data.get("template_ids", [])

    if not template_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="template_ids is required"
        )

    try:
        results = await translation_service.bulk_update_status(
            db=db,
            template_ids=template_ids,
            status="published"
        )
        logger.info(f"Bulk published {len(results)} translations")
        return {
            "published": len(results),
            "translations": results
        }
    except Exception as e:
        logger.error(f"Error bulk publishing: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
