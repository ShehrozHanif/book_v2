"""
Notification Service (T051)

Handles notifications for translation events:
- Notify admins when translations become stale
- Send notifications when translations are updated
- Track notification delivery status
- Support notification channels (in-app, email, webhook)
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import User

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of notifications."""
    TRANSLATION_STALE = "translation_stale"
    TRANSLATION_UPDATED = "translation_updated"
    TRANSLATION_PUBLISHED = "translation_published"
    TEMPLATE_CHANGED = "template_changed"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"


class NotificationService:
    """
    Service for managing notifications.

    Notifications are created for various translation events and can be
    delivered through multiple channels.
    """

    def __init__(self):
        """Initialize notification service."""
        self._notifications: Dict[int, List[Dict[str, Any]]] = {}
        self._stats = {
            "created": 0,
            "sent": 0,
            "failed": 0,
            "read": 0,
        }

    async def notify_stale_translation(
        self,
        db: AsyncSession,
        template_id: int,
        template_key: str,
        english_content: str,
        changed_at: datetime,
        channel: NotificationChannel = NotificationChannel.IN_APP
    ) -> Dict[str, Any]:
        """
        Notify admins that a translation has become stale.

        Args:
            db: Database session
            template_id: Template ID
            template_key: Template key
            english_content: English content that changed
            changed_at: When the change occurred
            channel: Notification delivery channel

        Returns:
            Notification details
        """
        notification = {
            "id": self._generate_notification_id(),
            "type": NotificationType.TRANSLATION_STALE,
            "channel": channel,
            "template_id": template_id,
            "template_key": template_key,
            "message": f"Translation for '{template_key}' is now stale - English content was updated",
            "details": {
                "english_content_preview": english_content[:100] + "..." if len(english_content) > 100 else english_content,
                "changed_at": changed_at.isoformat(),
                "action_url": f"/admin/translations/{template_id}",
            },
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "read": False,
            "read_at": None,
        }

        # Get all admins
        admins = await self._get_admin_users(db)

        for admin in admins:
            self._store_notification(admin.user_id, notification)

        self._stats["created"] += 1
        logger.info(f"Created stale translation notification for template {template_id}")

        return notification

    async def notify_translation_updated(
        self,
        db: AsyncSession,
        template_id: int,
        template_key: str,
        status: str,
        channel: NotificationChannel = NotificationChannel.IN_APP
    ) -> Dict[str, Any]:
        """
        Notify admins that a translation has been updated.

        Args:
            db: Database session
            template_id: Template ID
            template_key: Template key
            status: New status (draft, reviewed, published)
            channel: Notification delivery channel

        Returns:
            Notification details
        """
        status_text = {
            "draft": "saved as draft",
            "reviewed": "marked as reviewed",
            "published": "published",
        }.get(status, status)

        notification = {
            "id": self._generate_notification_id(),
            "type": NotificationType.TRANSLATION_UPDATED,
            "channel": channel,
            "template_id": template_id,
            "template_key": template_key,
            "message": f"Translation for '{template_key}' has been {status_text}",
            "details": {
                "new_status": status,
                "action_url": f"/admin/translations/{template_id}",
            },
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "read": False,
            "read_at": None,
        }

        # Get all admins
        admins = await self._get_admin_users(db)

        for admin in admins:
            self._store_notification(admin.user_id, notification)

        self._stats["created"] += 1
        logger.info(f"Created translation update notification for template {template_id}")

        return notification

    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.

        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Number of notifications to return
            offset: Pagination offset

        Returns:
            List of notifications
        """
        if user_id not in self._notifications:
            return []

        notifications = self._notifications[user_id]

        # Filter by read status if requested
        if unread_only:
            notifications = [n for n in notifications if not n.get("read")]

        # Sort by created_at descending (newest first)
        sorted_notifs = sorted(
            notifications,
            key=lambda x: x["created_at"],
            reverse=True
        )

        # Apply pagination
        return sorted_notifs[offset:offset + limit]

    async def mark_notification_read(
        self,
        user_id: int,
        notification_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Mark a notification as read.

        Args:
            user_id: User ID
            notification_id: Notification ID

        Returns:
            Updated notification or None if not found
        """
        if user_id not in self._notifications:
            return None

        for notif in self._notifications[user_id]:
            if notif["id"] == notification_id:
                notif["read"] = True
                notif["read_at"] = datetime.utcnow().isoformat()
                self._stats["read"] += 1
                logger.info(f"Marked notification {notification_id} as read for user {user_id}")
                return notif

        return None

    async def mark_all_notifications_read(self, user_id: int) -> int:
        """
        Mark all notifications as read for a user.

        Args:
            user_id: User ID

        Returns:
            Number of notifications marked as read
        """
        if user_id not in self._notifications:
            return 0

        count = 0
        for notif in self._notifications[user_id]:
            if not notif.get("read"):
                notif["read"] = True
                notif["read_at"] = datetime.utcnow().isoformat()
                count += 1

        self._stats["read"] += count
        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count

    async def get_notification_stats(self, user_id: int) -> Dict[str, int]:
        """
        Get notification statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Notification stats (total, unread, by type)
        """
        if user_id not in self._notifications:
            return {
                "total": 0,
                "unread": 0,
                "by_type": {},
            }

        notifications = self._notifications[user_id]
        unread = sum(1 for n in notifications if not n.get("read"))

        # Count by type
        by_type = {}
        for notif in notifications:
            ntype = notif.get("type")
            by_type[ntype] = by_type.get(ntype, 0) + 1

        return {
            "total": len(notifications),
            "unread": unread,
            "by_type": by_type,
        }

    async def send_notifications(self) -> Dict[str, int]:
        """
        Process and send pending notifications.

        In a real system, this would integrate with email/webhook services.
        For now, it marks notifications as sent.

        Returns:
            Stats on sent/failed notifications
        """
        sent = 0
        failed = 0

        for user_id, notifications in self._notifications.items():
            for notif in notifications:
                if notif.get("status") == "pending":
                    try:
                        # In real implementation, send via email/webhook/etc
                        notif["status"] = "sent"
                        notif["sent_at"] = datetime.utcnow().isoformat()
                        sent += 1
                    except Exception as e:
                        logger.error(f"Failed to send notification {notif.get('id')}: {e}")
                        notif["status"] = "failed"
                        failed += 1

        self._stats["sent"] += sent
        self._stats["failed"] += failed

        logger.info(f"Sent {sent} notifications, {failed} failed")
        return {"sent": sent, "failed": failed}

    def get_stats(self) -> Dict[str, int]:
        """Get notification service statistics."""
        return self._stats.copy()

    def _store_notification(self, user_id: int, notification: Dict[str, Any]) -> None:
        """Store a notification for a user."""
        if user_id not in self._notifications:
            self._notifications[user_id] = []
        self._notifications[user_id].append(notification)

    async def _get_admin_users(self, db: AsyncSession) -> List[User]:
        """Get all admin/instructor users."""
        try:
            result = await db.execute(
                select(User).where(User.role.in_(["admin", "instructor"]))
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching admin users: {e}")
            return []

    def _generate_notification_id(self) -> int:
        """Generate a unique notification ID."""
        import time
        return int(time.time() * 1000)


# Global instance
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get global notification service instance."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service


async def notify_translation_stale(
    db: AsyncSession,
    template_id: int,
    template_key: str,
    english_content: str,
    changed_at: datetime
) -> Dict[str, Any]:
    """
    Convenience function to notify admins of stale translation.

    Args:
        db: Database session
        template_id: Template ID
        template_key: Template key
        english_content: New English content
        changed_at: When the change occurred

    Returns:
        Notification details
    """
    service = get_notification_service()
    return await service.notify_stale_translation(
        db=db,
        template_id=template_id,
        template_key=template_key,
        english_content=english_content,
        changed_at=changed_at,
    )
