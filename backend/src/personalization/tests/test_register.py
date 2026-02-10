"""Tests for user registration endpoint."""

import pytest
from httpx import AsyncClient


class TestRegistration:
    """Test cases for user registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "newuser"

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, created_user):
        """Test registration with duplicate username."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": created_user.username,
                "email": "different@example.com",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, created_user):
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "differentuser",
                "email": created_user.email,
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "weak"
            }
        )

        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        """Test registration with missing required fields."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser"
                # Missing email and password
            }
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_username(self, client: AsyncClient):
        """Test registration with too short username."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "ab",  # Less than 3 characters
                "email": "test@example.com",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_password_without_uppercase(self, client: AsyncClient):
        """Test registration with password missing uppercase letter."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "securepass123!"
            }
        )

        assert response.status_code == 400
        assert "uppercase" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_password_without_lowercase(self, client: AsyncClient):
        """Test registration with password missing lowercase letter."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "SECUREPASS123!"
            }
        )

        assert response.status_code == 400
        assert "lowercase" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_password_without_digit(self, client: AsyncClient):
        """Test registration with password missing digit."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecurePass!"
            }
        )

        assert response.status_code == 400
        assert "digit" in response.json()["detail"].lower()
