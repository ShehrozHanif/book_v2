"""Integration tests for preferences endpoints."""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import User


@pytest.mark.asyncio
class TestPreferencesEndpoints:
    """Integration tests for preferences management endpoints."""

    async def test_get_preferences_own_profile(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test getting own preferences."""
        response = client.get(
            f"/api/v1/users/{test_user.user_id}/preferences",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "explanation_style" in data
        assert "code_language" in data
        assert "learning_pace" in data
        assert "content_focus" in data
        assert data["explanation_style"] == "example_first"

    async def test_get_preferences_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting preferences for nonexistent user."""
        nonexistent_id = uuid4()
        response = client.get(
            f"/api/v1/users/{nonexistent_id}/preferences",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_preferences_unauthorized(self, client: TestClient, auth_headers: dict):
        """Test unauthorized access to other user's preferences."""
        other_user_id = uuid4()
        response = client.get(
            f"/api/v1/users/{other_user_id}/preferences",
            headers=auth_headers
        )

        assert response.status_code == 403
        assert "can only view your own" in response.json()["detail"].lower()

    async def test_update_preferences_all_fields(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test updating all preference fields."""
        new_preferences = {
            "explanation_style": "theory_first",
            "code_language": "cpp",
            "learning_pace": "fast",
            "content_focus": "hardware"
        }

        response = client.put(
            f"/api/v1/users/{test_user.user_id}/preferences",
            json=new_preferences,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["explanation_style"] == "theory_first"
        assert data["code_language"] == "cpp"
        assert data["learning_pace"] == "fast"
        assert data["content_focus"] == "hardware"

    async def test_update_preferences_partial(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test updating partial preferences."""
        partial_update = {
            "learning_pace": "slow"
        }

        response = client.put(
            f"/api/v1/users/{test_user.user_id}/preferences",
            json=partial_update,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Updated field
        assert data["learning_pace"] == "slow"

        # Other fields should remain unchanged
        assert data["explanation_style"] == "example_first"
        assert data["code_language"] == "python"

    async def test_update_preferences_invalid_enum(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test updating with invalid enum value."""
        invalid_update = {
            "explanation_style": "invalid_value"
        }

        response = client.put(
            f"/api/v1/users/{test_user.user_id}/preferences",
            json=invalid_update,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    async def test_update_preferences_unauthorized(self, client: TestClient, auth_headers: dict):
        """Test unauthorized preference update."""
        other_user_id = uuid4()
        update = {
            "learning_pace": "fast"
        }

        response = client.put(
            f"/api/v1/users/{other_user_id}/preferences",
            json=update,
            headers=auth_headers
        )

        assert response.status_code == 403
        assert "can only update your own" in response.json()["detail"].lower()

    async def test_reset_preferences(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test resetting preferences to defaults."""
        # First update preferences
        new_prefs = {
            "explanation_style": "theory_first",
            "code_language": "cpp",
            "learning_pace": "fast",
            "content_focus": "hardware"
        }

        client.put(
            f"/api/v1/users/{test_user.user_id}/preferences",
            json=new_prefs,
            headers=auth_headers
        )

        # Now reset
        response = client.post(
            f"/api/v1/users/{test_user.user_id}/preferences/reset",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should be back to defaults
        assert data["explanation_style"] == "example_first"
        assert data["code_language"] == "python"
        assert data["learning_pace"] == "medium"
        assert data["content_focus"] == "balanced"

    async def test_reset_preferences_unauthorized(self, client: TestClient, auth_headers: dict):
        """Test unauthorized preference reset."""
        other_user_id = uuid4()

        response = client.post(
            f"/api/v1/users/{other_user_id}/preferences/reset",
            headers=auth_headers
        )

        assert response.status_code == 403
        assert "can only reset your own" in response.json()["detail"].lower()

    async def test_preferences_persist_across_requests(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test that preferences persist across multiple requests."""
        # Update preferences
        new_prefs = {
            "learning_pace": "slow",
            "code_language": "cpp"
        }

        client.put(
            f"/api/v1/users/{test_user.user_id}/preferences",
            json=new_prefs,
            headers=auth_headers
        )

        # Retrieve and verify
        for _ in range(3):
            response = client.get(
                f"/api/v1/users/{test_user.user_id}/preferences",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["learning_pace"] == "slow"
            assert data["code_language"] == "cpp"

    async def test_all_preference_combinations_valid(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test all valid preference combinations."""
        explanation_styles = ["theory_first", "example_first"]
        code_languages = ["python", "cpp", "both"]
        learning_paces = ["slow", "medium", "fast"]
        content_focuses = ["simulation", "hardware", "balanced"]

        for style in explanation_styles:
            for language in code_languages:
                for pace in learning_paces:
                    for focus in content_focuses:
                        update = {
                            "explanation_style": style,
                            "code_language": language,
                            "learning_pace": pace,
                            "content_focus": focus
                        }

                        response = client.put(
                            f"/api/v1/users/{test_user.user_id}/preferences",
                            json=update,
                            headers=auth_headers
                        )

                        assert response.status_code == 200
                        data = response.json()
                        assert data["explanation_style"] == style
                        assert data["code_language"] == language
                        assert data["learning_pace"] == pace
                        assert data["content_focus"] == focus
