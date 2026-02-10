"""Tests for JWT token validation and refresh."""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from jose import jwt

from src.personalization.utils.auth import (
    create_access_token, create_refresh_token,
    verify_access_token, verify_refresh_token,
    decode_token, SECRET_KEY, ALGORITHM
)


class TestJWT:
    """Test cases for JWT token operations."""

    @pytest.mark.asyncio
    async def test_valid_token_acceptance(self, client: AsyncClient, created_user):
        """Test that valid access token is accepted."""
        token = create_access_token({"sub": str(created_user.user_id), "username": created_user.username})

        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == created_user.username

    @pytest.mark.asyncio
    async def test_expired_token_rejection(self, client: AsyncClient, created_user):
        """Test that expired token is rejected."""
        # Create token that expired 1 hour ago
        expired_token = create_access_token(
            {"sub": str(created_user.user_id), "username": created_user.username},
            expires_delta=timedelta(hours=-1)
        )

        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_token_rejection(self, client: AsyncClient):
        """Test that malformed token is rejected."""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_token_rejection(self, client: AsyncClient):
        """Test that missing token is rejected."""
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_refresh_success(self, client: AsyncClient, created_user):
        """Test successful token refresh."""
        refresh_token = create_refresh_token({"sub": str(created_user.user_id), "username": created_user.username})

        response = await client.post(
            "/api/v1/users/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_token_refresh_with_expired_token(self, client: AsyncClient, created_user):
        """Test token refresh with expired refresh token."""
        # Create expired refresh token
        expired_data = {
            "sub": str(created_user.user_id),
            "username": created_user.username,
            "exp": datetime.utcnow() - timedelta(days=1),
            "iat": datetime.utcnow() - timedelta(days=2),
            "type": "refresh",
            "jti": "test_jti"
        }
        expired_token = jwt.encode(expired_data, SECRET_KEY, algorithm=ALGORITHM)

        response = await client.post(
            "/api/v1/users/refresh",
            json={"refresh_token": expired_token}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_decoding(self, created_user):
        """Test JWT token decoding."""
        token_data = {"sub": str(created_user.user_id), "username": created_user.username}
        token = create_access_token(token_data)

        payload = decode_token(token)

        assert payload["sub"] == str(created_user.user_id)
        assert payload["username"] == created_user.username
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    @pytest.mark.asyncio
    async def test_verify_access_token(self, created_user):
        """Test access token verification."""
        token = create_access_token({"sub": str(created_user.user_id), "username": created_user.username})

        payload = verify_access_token(token)

        assert payload is not None
        assert payload["sub"] == str(created_user.user_id)
        assert payload["type"] == "access"

    @pytest.mark.asyncio
    async def test_verify_refresh_token(self, created_user):
        """Test refresh token verification."""
        token = create_refresh_token({"sub": str(created_user.user_id), "username": created_user.username})

        payload = verify_refresh_token(token)

        assert payload is not None
        assert payload["sub"] == str(created_user.user_id)
        assert payload["type"] == "refresh"
        assert "jti" in payload

    @pytest.mark.asyncio
    async def test_access_token_cannot_refresh(self, client: AsyncClient, created_user):
        """Test that access token cannot be used for refresh."""
        # Create access token (not refresh token)
        access_token = create_access_token({"sub": str(created_user.user_id), "username": created_user.username})

        response = await client.post(
            "/api/v1/users/refresh",
            json={"refresh_token": access_token}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_with_invalid_signature(self, client: AsyncClient, created_user):
        """Test token with invalid signature is rejected."""
        # Create token with wrong secret key
        invalid_token = jwt.encode(
            {"sub": str(created_user.user_id), "username": created_user.username, "type": "access"},
            "wrong_secret_key",
            algorithm=ALGORITHM
        )

        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        assert response.status_code == 401
