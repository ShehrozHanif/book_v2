"""Tests for user profile endpoints."""

import pytest
from httpx import AsyncClient


class TestProfile:
    """Test cases for user profile operations."""

    @pytest.mark.asyncio
    async def test_get_profile_with_valid_token(self, client: AsyncClient, created_user, auth_headers):
        """Test getting profile with valid authentication token."""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == created_user.username
        assert data["email"] == created_user.email
        assert "user_id" in data
        assert "skill_level" in data
        assert "preferences" in data

    @pytest.mark.asyncio
    async def test_get_profile_with_invalid_token(self, client: AsyncClient):
        """Test getting profile with invalid token."""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_profile_success(self, client: AsyncClient, auth_headers):
        """Test successful profile update."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "bio": "Updated bio",
                "profile_picture_url": "https://example.com/newpic.jpg"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Updated bio"
        assert data["profile_picture_url"] == "https://example.com/newpic.jpg"

    @pytest.mark.asyncio
    async def test_update_profile_unauthorized(self, client: AsyncClient):
        """Test profile update without authentication."""
        response = await client.put(
            "/api/v1/users/me",
            json={
                "bio": "Updated bio"
            }
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_profile_preferences(self, client: AsyncClient, auth_headers):
        """Test updating user preferences."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "preferences": {
                    "explanation_style": "theory_first",
                    "code_language": "cpp",
                    "learning_pace": "fast",
                    "content_focus": "simulation"
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["preferences"]["explanation_style"] == "theory_first"
        assert data["preferences"]["code_language"] == "cpp"
        assert data["preferences"]["learning_pace"] == "fast"
        assert data["preferences"]["content_focus"] == "simulation"

    @pytest.mark.asyncio
    async def test_profile_data_persistence(self, client: AsyncClient, auth_headers):
        """Test that profile updates persist."""
        # Update profile
        update_response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "bio": "Persistent bio",
                "profile_picture_url": "https://example.com/persistent.jpg"
            }
        )
        assert update_response.status_code == 200

        # Fetch profile again
        get_response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["bio"] == "Persistent bio"
        assert data["profile_picture_url"] == "https://example.com/persistent.jpg"

    @pytest.mark.asyncio
    async def test_update_profile_with_duplicate_username(self, client: AsyncClient, auth_headers, test_db):
        """Test updating to a username that already exists."""
        from src.personalization.services import user_service

        # Create another user
        await user_service.create_user(
            db=test_db,
            username="existinguser",
            email="existing@example.com",
            password="ExistingPass123!"
        )

        # Try to update current user's username to existing one
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "username": "existinguser"
            }
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_profile_includes_timestamps(self, client: AsyncClient, auth_headers):
        """Test that profile includes created_at and last_login_at."""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "created_at" in data
        assert data["created_at"] is not None

    @pytest.mark.asyncio
    async def test_delete_account_success(self, client: AsyncClient, auth_headers, sample_user_data):
        """Test successful account deletion."""
        response = await client.delete(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "password": sample_user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "successfully deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_delete_account_wrong_password(self, client: AsyncClient, auth_headers):
        """Test account deletion with wrong password."""
        response = await client.delete(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
