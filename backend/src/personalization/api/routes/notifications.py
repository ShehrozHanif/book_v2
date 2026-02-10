"""
Notification API Routes (T051)

Endpoints for managing user notifications:
- GET /api/v1/notifications - Get user's notifications
- POST /api/v1/notifications/{id}/read - Mark as read
- POST /api/v1/notifications/read-all - Mark all as read
- GET /api/v1/notifications/stats - Get notification stats
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session
from src.personalization.models.db_models import User
from src.personalization.utils.auth import get_current_user
from src.personalization.services.notification_service import get_notification_service

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list)
async def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications for current user.

    Query Parameters:
    - unread_only: Only return unread notifications (default: false)
    - limit: Number of notifications (default: 20)
    - offset: Pagination offset (default: 0)
    """
    service = get_notification_service()

    try:
        notifications = await service.get_user_notifications(
            user_id=current_user.user_id,
            unread_only=unread_only,
            limit=limit,
            offset=offset
        )
        logger.info(f"Retrieved {len(notifications)} notifications for user {current_user.user_id}")
        return notifications
    except Exception as e:
        logger.error(f"Error retrieving notifications: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user)
):
    """Mark a specific notification as read."""
    service = get_notification_service()

    try:
        result = await service.mark_notification_read(
            user_id=current_user.user_id,
            notification_id=notification_id
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        logger.info(f"Marked notification {notification_id} as read")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read for current user."""
    service = get_notification_service()

    try:
        count = await service.mark_all_notifications_read(
            user_id=current_user.user_id
        )
        logger.info(f"Marked {count} notifications as read for user {current_user.user_id}")
        return {"marked_read": count}
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/stats")
async def get_notification_stats(
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics for current user."""
    service = get_notification_service()

    try:
        stats = await service.get_notification_stats(user_id=current_user.user_id)
        logger.info(f"Retrieved notification stats for user {current_user.user_id}")
        return stats
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
