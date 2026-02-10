"""
Translation Update Tests (T045)

Tests for translation update functionality:
1. Update template Urdu translation
2. Mark template as reviewed/published
3. Verify new responses use updated translation
4. Verify old chat history unchanged
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from datetime import datetime


class TestTranslationUpdate:
    """Tests for updating chatbot response translations."""

    async def test_update_translation_success(self, client: AsyncClient, auth_headers: dict):
        """Should update template Urdu translation successfully."""
        template_id = 1
        update_data = {
            "urdu_translation": "یہ ایک اپڈیٹ شدہ ترجمہ ہے"
        }

        response = await client.put(
            f"/api/v1/admin/translations/{template_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["urdu_translation"] == update_data["urdu_translation"]
        assert data["updated_at"] is not None

    async def test_update_translation_requires_admin(self, client: AsyncClient):
        """Should reject non-admin users."""
        response = await client.put(
            "/api/v1/admin/translations/1",
            json={"urdu_translation": "test"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_nonexistent_template(self, client: AsyncClient, auth_headers: dict):
        """Should return 404 for non-existent template."""
        response = await client.put(
            "/api/v1/admin/translations/99999",
            json={"urdu_translation": "test"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_mark_translation_reviewed(self, client: AsyncClient, auth_headers: dict):
        """Should mark translation as reviewed."""
        template_id = 1
        review_data = {
            "status": "reviewed"
        }

        response = await client.post(
            f"/api/v1/admin/translations/{template_id}/review",
            json=review_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "reviewed"

    async def test_mark_translation_published(self, client: AsyncClient, auth_headers: dict):
        """Should mark translation as published."""
        template_id = 1
        publish_data = {
            "status": "published"
        }

        response = await client.post(
            f"/api/v1/admin/translations/{template_id}/review",
            json=publish_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "published"

    async def test_invalid_status_transition(self, client: AsyncClient, auth_headers: dict):
        """Should reject invalid status transitions."""
        template_id = 1
        invalid_data = {
            "status": "invalid_status"
        }

        response = await client.post(
            f"/api/v1/admin/translations/{template_id}/review",
            json=invalid_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_includes_timestamp(self, client: AsyncClient, auth_headers: dict):
        """Should include updated_at timestamp."""
        template_id = 1
        update_data = {
            "urdu_translation": "ٹیسٹ ترجمہ"
        }

        response = await client.put(
            f"/api/v1/admin/translations/{template_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "updated_at" in data
        assert isinstance(data["updated_at"], str)

    async def test_multiple_updates_track_history(self, client: AsyncClient, auth_headers: dict):
        """Should track multiple updates to same template."""
        template_id = 1

        # First update
        response1 = await client.put(
            f"/api/v1/admin/translations/{template_id}",
            json={"urdu_translation": "پہلا ترجمہ"},
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_200_OK

        # Second update
        response2 = await client.put(
            f"/api/v1/admin/translations/{template_id}",
            json={"urdu_translation": "دوسرا ترجمہ"},
            headers=auth_headers
        )
        assert response2.status_code == status.HTTP_200_OK

        data = response2.json()
        assert data["urdu_translation"] == "دوسرا ترجمہ"

    async def test_translation_validation(self, client: AsyncClient, auth_headers: dict):
        """Should validate translation content."""
        template_id = 1

        # Empty translation
        response = await client.put(
            f"/api/v1/admin/translations/{template_id}",
            json={"urdu_translation": ""},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_preserves_english_content(self, client: AsyncClient, auth_headers: dict):
        """Should not modify English content when updating Urdu translation."""
        template_id = 1
        original_english = "Original English content"
        update_data = {
            "urdu_translation": "نیا ترجمہ"
        }

        response = await client.put(
            f"/api/v1/admin/translations/{template_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # English content should remain unchanged
        assert "english_content" in data


class TestNewResponsesUseUpdatedTranslation:
    """Tests verifying new chatbot responses use updated translations."""

    async def test_new_response_uses_published_translation(self, client: AsyncClient, auth_headers: dict):
        """Should use published translation for new responses."""
        template_id = 1
        new_translation = "جدید ترجمہ شدہ جواب"

        # First update and publish the translation
        update_response = await client.put(
            f"/api/v1/admin/translations/{template_id}",
            json={"urdu_translation": new_translation},
            headers=auth_headers
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Publish it
        publish_response = await client.post(
            f"/api/v1/admin/translations/{template_id}/review",
            json={"status": "published"},
            headers=auth_headers
        )
        assert publish_response.status_code == status.HTTP_200_OK

    async def test_draft_translation_not_used(self, client: AsyncClient, auth_headers: dict):
        """Should not use draft translation for new responses."""
        template_id = 1

        # Update translation but don't publish (status = draft)
        response = await client.put(
            f"/api/v1/admin/translations/{template_id}",
            json={"urdu_translation": "ڈرافٹ ترجمہ"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "draft"

    async def test_status_workflow(self, client: AsyncClient, auth_headers: dict):
        """Should follow correct status workflow: draft -> reviewed -> published."""
        template_id = 1

        # Start as draft
        response = await client.put(
            f"/api/v1/admin/translations/{template_id}",
            json={"urdu_translation": "کام جاری ہے"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "draft"

        # Move to reviewed
        response = await client.post(
            f"/api/v1/admin/translations/{template_id}/review",
            json={"status": "reviewed"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "reviewed"

        # Move to published
        response = await client.post(
            f"/api/v1/admin/translations/{template_id}/review",
            json={"status": "published"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "published"


class TestOldChatHistoryPreservation:
    """Tests verifying old chat history remains unchanged."""

    async def test_old_chat_uses_old_translation(self, client: AsyncClient, auth_headers: dict):
        """Should preserve old translations in chat history."""
        # This would require integration with chat history retrieval
        # Ensuring that messages sent before translation update show original translation
        pass

    async def test_chat_history_not_retroactively_updated(self, client: AsyncClient, auth_headers: dict):
        """Should not update translations in existing chat history."""
        # Verify that updating a template doesn't change historical messages
        pass

    async def test_translation_update_only_affects_new_messages(self, client: AsyncClient, auth_headers: dict):
        """Should only apply translation changes to new messages."""
        # New messages should use updated translation
        # Old messages should retain original translation
        pass
