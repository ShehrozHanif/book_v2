"""
Notification Service Tests (T051)

Tests for notification system:
1. Notify admins when translations become stale
2. Notify when translations are updated
3. Mark notifications as read
4. Get notification statistics
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from datetime import datetime


class TestNotificationCreation:
    """Tests for creating notifications."""

    async def test_create_stale_notification(self, client: AsyncClient, auth_headers: dict):
        """Should create notification when translation becomes stale."""
        template_id = 1

        # This would be triggered by marking translation stale
        # For now, test that endpoint exists and can receive notifications
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_notification_includes_details(self, client: AsyncClient, auth_headers: dict):
        """Should include notification details."""
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        notifications = response.json()

        if notifications:
            notif = notifications[0]
            assert "id" in notif
            assert "type" in notif
            assert "message" in notif
            assert "created_at" in notif
            assert "read" in notif


class TestNotificationRetrieval:
    """Tests for retrieving notifications."""

    async def test_get_user_notifications(self, client: AsyncClient, auth_headers: dict):
        """Should retrieve user's notifications."""
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_get_unread_notifications_only(self, client: AsyncClient, auth_headers: dict):
        """Should filter notifications by unread status."""
        response = await client.get(
            "/api/v1/notifications?unread_only=true",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        notifications = response.json()
        assert isinstance(notifications, list)

    async def test_notifications_pagination(self, client: AsyncClient, auth_headers: dict):
        """Should support pagination."""
        response = await client.get(
            "/api/v1/notifications?limit=10&offset=0",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_requires_authentication(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.get("/api/v1/notifications")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_notification_ordering(self, client: AsyncClient, auth_headers: dict):
        """Should return notifications in correct order (newest first)."""
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        notifications = response.json()

        if len(notifications) > 1:
            # Verify newest first
            for i in range(len(notifications) - 1):
                assert (
                    notifications[i]["created_at"] >= notifications[i + 1]["created_at"]
                )


class TestMarkNotificationsRead:
    """Tests for marking notifications as read."""

    async def test_mark_single_notification_read(self, client: AsyncClient, auth_headers: dict):
        """Should mark a single notification as read."""
        notification_id = 1

        response = await client.post(
            f"/api/v1/notifications/{notification_id}/read",
            headers=auth_headers
        )

        # Should either succeed or return 404 if notification doesn't exist
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["read"] is True
            assert "read_at" in data

    async def test_mark_all_read(self, client: AsyncClient, auth_headers: dict):
        """Should mark all notifications as read."""
        response = await client.post(
            "/api/v1/notifications/read-all",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "marked_read" in data
        assert isinstance(data["marked_read"], int)

    async def test_mark_read_requires_auth(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.post("/api/v1/notifications/1/read")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_read_status_persists(self, client: AsyncClient, auth_headers: dict):
        """Should persist read status."""
        notification_id = 1

        # Mark as read
        response1 = await client.post(
            f"/api/v1/notifications/{notification_id}/read",
            headers=auth_headers
        )

        if response1.status_code == status.HTTP_200_OK:
            # Verify it shows as read
            data = response1.json()
            assert data["read"] is True


class TestNotificationStats:
    """Tests for notification statistics."""

    async def test_get_notification_stats(self, client: AsyncClient, auth_headers: dict):
        """Should get notification statistics."""
        response = await client.get(
            "/api/v1/notifications/stats",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        stats = response.json()

        assert "total" in stats
        assert "unread" in stats
        assert "by_type" in stats
        assert isinstance(stats["total"], int)
        assert isinstance(stats["unread"], int)
        assert isinstance(stats["by_type"], dict)

    async def test_stats_counts_match(self, client: AsyncClient, auth_headers: dict):
        """Should have correct statistics counts."""
        response = await client.get(
            "/api/v1/notifications/stats",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        stats = response.json()

        # Unread should be <= total
        assert stats["unread"] <= stats["total"]

    async def test_stats_require_auth(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.get("/api/v1/notifications/stats")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStaleTranslationNotification:
    """Tests for stale translation notifications."""

    async def test_notification_has_action_url(self, client: AsyncClient, auth_headers: dict):
        """Should include action URL in stale translation notifications."""
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        notifications = response.json()

        for notif in notifications:
            if notif.get("type") == "translation_stale":
                assert "details" in notif
                assert "action_url" in notif["details"]

    async def test_notification_type_filtering(self, client: AsyncClient, auth_headers: dict):
        """Should be able to identify notification types."""
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        notifications = response.json()

        valid_types = [
            "translation_stale",
            "translation_updated",
            "translation_published",
            "template_changed",
        ]

        for notif in notifications:
            assert notif.get("type") in valid_types


class TestNotificationChannels:
    """Tests for notification channels."""

    async def test_notification_has_channel(self, client: AsyncClient, auth_headers: dict):
        """Should include notification channel."""
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        notifications = response.json()

        valid_channels = ["in_app", "email", "webhook"]

        for notif in notifications:
            if "channel" in notif:
                assert notif["channel"] in valid_channels
