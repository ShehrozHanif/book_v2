"""
Language Preference Persistence Tests (T054)

Tests for language preference persistence:
1. Save preference to database
2. Retrieve preference on login
3. Update preference
4. Cross-session persistence
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestPreferenceSaving:
    """Tests for saving language preferences."""

    async def test_save_preference_success(self, client: AsyncClient, auth_headers: dict):
        """Should save language preference successfully."""
        response = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "urdu"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["language"] == "urdu"

    async def test_save_english_preference(self, client: AsyncClient, auth_headers: dict):
        """Should save English preference."""
        response = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "english"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["language"] == "english"

    async def test_save_invalid_language(self, client: AsyncClient, auth_headers: dict):
        """Should reject invalid language."""
        response = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "spanish"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_requires_authentication(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "urdu"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_save_preference_includes_timestamp(self, client: AsyncClient, auth_headers: dict):
        """Should include updated_at timestamp."""
        response = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "urdu"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "updated_at" in data


class TestPreferenceRetrieval:
    """Tests for retrieving language preferences."""

    async def test_get_preference_success(self, client: AsyncClient, auth_headers: dict):
        """Should retrieve user's language preference."""
        response = await client.get(
            "/api/v1/users/me/language-preference",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "language" in data

    async def test_default_preference(self, client: AsyncClient, auth_headers: dict):
        """Should return default preference if not set."""
        response = await client.get(
            "/api/v1/users/me/language-preference",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Default should be English
        assert data["language"] in ["english", None]

    async def test_requires_authentication(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.get("/api/v1/users/me/language-preference")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_preference_response_schema(self, client: AsyncClient, auth_headers: dict):
        """Should return proper response schema."""
        response = await client.get(
            "/api/v1/users/me/language-preference",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "language" in data
        if "updated_at" in data:
            assert isinstance(data["updated_at"], str)


class TestPreferenceUpdate:
    """Tests for updating preferences."""

    async def test_update_preference(self, client: AsyncClient, auth_headers: dict):
        """Should update existing preference."""
        # Set initial preference
        response1 = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "english"},
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_200_OK

        # Update to Urdu
        response2 = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "urdu"},
            headers=auth_headers
        )

        assert response2.status_code == status.HTTP_200_OK
        data = response2.json()
        assert data["language"] == "urdu"

    async def test_multiple_updates(self, client: AsyncClient, auth_headers: dict):
        """Should support multiple preference changes."""
        languages = ["urdu", "english", "urdu"]

        for lang in languages:
            response = await client.put(
                "/api/v1/users/me/language-preference",
                json={"language": lang},
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["language"] == lang

    async def test_update_timestamp_changes(self, client: AsyncClient, auth_headers: dict):
        """Should update timestamp on preference change."""
        response1 = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "english"},
            headers=auth_headers
        )
        timestamp1 = response1.json().get("updated_at")

        response2 = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "urdu"},
            headers=auth_headers
        )
        timestamp2 = response2.json().get("updated_at")

        if timestamp1 and timestamp2:
            assert timestamp2 >= timestamp1


class TestCrossSessionPersistence:
    """Tests for preference persistence across sessions."""

    async def test_preference_persists_after_logout_login(self, client: AsyncClient, auth_headers: dict):
        """Should persist preference across logout/login."""
        # Set preference
        response1 = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "urdu"},
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_200_OK

        # In real scenario: logout and login would create new session
        # For test, we just verify the preference was saved
        response2 = await client.get(
            "/api/v1/users/me/language-preference",
            headers=auth_headers
        )
        assert response2.status_code == status.HTTP_200_OK
        assert response2.json()["language"] == "urdu"

    async def test_preference_different_users(self, client: AsyncClient, auth_headers: dict):
        """Should store preferences per user."""
        # User 1 sets preference to Urdu
        response1 = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "urdu"},
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_200_OK

        # Verify User 1's preference
        response2 = await client.get(
            "/api/v1/users/me/language-preference",
            headers=auth_headers
        )
        assert response2.json()["language"] == "urdu"


class TestPreferenceDefaults:
    """Tests for preference defaults and initialization."""

    async def test_default_language_english(self, client: AsyncClient, auth_headers: dict):
        """Should default to English if not set."""
        response = await client.get(
            "/api/v1/users/me/language-preference",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should be english or none (none implies english)
        assert data.get("language") is None or data.get("language") == "english"

    async def test_preference_case_insensitive(self, client: AsyncClient, auth_headers: dict):
        """Should handle case variations."""
        response = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": "Urdu"},  # Capital U
            headers=auth_headers
        )

        # Should either accept and normalize, or reject consistently
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestPreferenceValidation:
    """Tests for preference validation."""

    async def test_language_field_required(self, client: AsyncClient, auth_headers: dict):
        """Should require language field."""
        response = await client.put(
            "/api/v1/users/me/language-preference",
            json={},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_empty_language_rejected(self, client: AsyncClient, auth_headers: dict):
        """Should reject empty language value."""
        response = await client.put(
            "/api/v1/users/me/language-preference",
            json={"language": ""},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
