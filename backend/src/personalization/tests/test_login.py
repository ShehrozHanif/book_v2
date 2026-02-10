"""Tests for user login endpoint."""

import pytest
from httpx import AsyncClient


class TestLogin:
    """Test cases for user login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, created_user, sample_user_data):
        """Test successful user login."""
        response = await client.post(
            "/api/v1/users/login",
            json={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == created_user.username
        assert str(data["user_id"]) == str(created_user.user_id)

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, created_user, sample_user_data):
        """Test login with wrong password."""
        response = await client.post(
            "/api/v1/users/login",
            json={
                "email": sample_user_data["email"],
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            "/api/v1/users/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePass123!"
            }
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_empty_credentials(self, client: AsyncClient):
        """Test login with empty credentials."""
        response = await client.post(
            "/api/v1/users/login",
            json={
                "email": "",
                "password": ""
            }
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_jwt_token_generation(self, client: AsyncClient, created_user, sample_user_data):
        """Test JWT token generation on login."""
        response = await client.post(
            "/api/v1/users/login",
            json={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify access token format
        access_token = data["access_token"]
        assert len(access_token) > 0
        assert access_token.count('.') == 2  # JWT has 3 parts separated by dots

        # Verify refresh token format
        refresh_token = data["refresh_token"]
        assert len(refresh_token) > 0
        assert refresh_token.count('.') == 2

    @pytest.mark.asyncio
    async def test_login_updates_last_login(self, client: AsyncClient, test_db, created_user, sample_user_data):
        """Test that login updates last_login_at timestamp."""
        from src.personalization.services import user_service

        # Get initial last_login_at
        user_before = await user_service.get_user_by_id(test_db, created_user.user_id)
        initial_last_login = user_before.last_login_at

        # Perform login
        response = await client.post(
            "/api/v1/users/login",
            json={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"]
            }
        )

        assert response.status_code == 200

        # Get updated last_login_at
        user_after = await user_service.get_user_by_id(test_db, created_user.user_id)
        updated_last_login = user_after.last_login_at

        # Verify timestamp was updated
        assert updated_last_login is not None
        if initial_last_login:
            assert updated_last_login > initial_last_login

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, client: AsyncClient):
        """Test login with invalid email format."""
        response = await client.post(
            "/api/v1/users/login",
            json={
                "email": "not-an-email",
                "password": "SomePass123!"
            }
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_case_insensitive_email(self, client: AsyncClient, created_user, sample_user_data):
        """Test login with different case email."""
        response = await client.post(
            "/api/v1/users/login",
            json={
                "email": sample_user_data["email"].upper(),
                "password": sample_user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
