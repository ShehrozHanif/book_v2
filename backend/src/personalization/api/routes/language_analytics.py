"""
Language Analytics API Routes (T063)

Endpoints for tracking and viewing language adoption metrics:
- GET /api/v1/analytics/language-adoption - adoption metrics
- GET /api/v1/analytics/language-demographics - breakdown by user role
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session
from src.personalization.models.db_models import User
from src.personalization.api.dependencies import get_current_user
from src.personalization.services.language_analytics import (
    LanguageAnalyticsService,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["language-analytics"])
logger = logging.getLogger(__name__)


@router.get("/language-adoption")
async def get_language_adoption_metrics(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get language adoption metrics (admin only).

    Returns:
        {
            "total_users": 100,
            "english_users": 85,
            "urdu_users": 15,
            "english_percent": 85.0,
            "urdu_percent": 15.0
        }
    """
    # Only admins can view analytics
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view analytics"
        )

    try:
        metrics = await LanguageAnalyticsService.get_adoption_metrics(db)
        logger.info(f"Admin {current_user.user_id} retrieved adoption metrics")
        return metrics
    except Exception as e:
        logger.error(f"Error retrieving adoption metrics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/language-breakdown")
async def get_language_breakdown(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get language adoption breakdown (admin only).

    Returns:
        {"english": 85, "urdu": 15}
    """
    # Only admins can view analytics
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view analytics"
        )

    try:
        breakdown = await LanguageAnalyticsService.get_user_language_breakdown(db)
        logger.info(f"Admin {current_user.user_id} retrieved language breakdown")
        return breakdown
    except Exception as e:
        logger.error(f"Error retrieving language breakdown: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/language-timeline")
async def get_language_timeline(
    days: int = 30,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get language adoption trend over time (admin only).

    Query Parameters:
    - days: Number of days to look back (default: 30)

    Returns:
        List of adoption data points
    """
    # Only admins can view analytics
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view analytics"
        )

    try:
        timeline = await LanguageAnalyticsService.get_adoption_timeline(
            db, interval_days=max(1, min(days, 365))
        )
        logger.info(f"Admin {current_user.user_id} retrieved adoption timeline")
        return timeline
    except Exception as e:
        logger.error(f"Error retrieving adoption timeline: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/language-demographics")
async def get_language_demographics(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get language adoption breakdown by user role (admin only).

    Returns:
        {
            "student": {"english": 70, "urdu": 30, "total": 100},
            "instructor": {"english": 80, "urdu": 20, "total": 100}
        }
    """
    # Only admins can view analytics
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view analytics"
        )

    try:
        demographics = await LanguageAnalyticsService.get_demographic_breakdown(db)
        logger.info(f"Admin {current_user.user_id} retrieved demographic breakdown")
        return demographics
    except Exception as e:
        logger.error(f"Error retrieving demographic breakdown: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/language-recent-changes")
async def get_recent_changes(
    days: int = 7,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get recent language preference changes (admin only).

    Query Parameters:
    - days: Number of days to look back (default: 7)

    Returns:
        List of recent preference changes
    """
    # Only admins can view analytics
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view analytics"
        )

    try:
        changes = await LanguageAnalyticsService.get_recent_preference_changes(
            db, days=max(1, min(days, 365))
        )
        logger.info(f"Admin {current_user.user_id} retrieved recent changes")
        return changes
    except Exception as e:
        logger.error(f"Error retrieving recent changes: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
