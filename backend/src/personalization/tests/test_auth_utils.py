"""Unit tests for authentication utilities."""

import pytest
from datetime import timedelta

from src.personalization.utils.auth import (
    hash_password, verify_password,
    validate_password_strength,
    create_access_token, create_refresh_token,
    verify_access_token, verify_refresh_token,
    decode_token,
    generate_password_reset_token, verify_password_reset_token,
    init_auth_config
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password("testpassword123!", hashed) is False


class TestPasswordValidation:
    """Test password strength validation."""

    def test_valid_password(self):
        """Test validation of strong password."""
        is_valid, error = validate_password_strength("SecurePass123!")
        assert is_valid is True
        assert error is None

    def test_too_short_password(self):
        """Test password that's too short."""
        is_valid, error = validate_password_strength("Short1")
        assert is_valid is False
        assert "8 characters" in error

    def test_too_long_password(self):
        """Test password that's too long."""
        is_valid, error = validate_password_strength("A" * 101 + "1a")
        assert is_valid is False
        assert "100 characters" in error

    def test_no_uppercase_password(self):
        """Test password without uppercase letter."""
        is_valid, error = validate_password_strength("securepass123!")
        assert is_valid is False
        assert "uppercase" in error.lower()

    def test_no_lowercase_password(self):
        """Test password without lowercase letter."""
        is_valid, error = validate_password_strength("SECUREPASS123!")
        assert is_valid is False
        assert "lowercase" in error.lower()

    def test_no_digit_password(self):
        """Test password without digit."""
        is_valid, error = validate_password_strength("SecurePass!")
        assert is_valid is False
        assert "digit" in error.lower()


class TestJWTOperations:
    """Test JWT token creation and verification."""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Initialize auth config for tests."""
        init_auth_config(
            secret_key="test_secret_key_12345",
            access_expire=30,
            refresh_expire=7
        )

    def test_create_access_token(self):
        """Test access token creation."""
        token_data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(token_data)

        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT format

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        token_data = {"sub": "user123", "username": "testuser"}
        token = create_refresh_token(token_data)

        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT format

    def test_decode_token(self):
        """Test token decoding."""
        token_data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(token_data)

        payload = decode_token(token)

        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_access_token(self):
        """Test access token verification."""
        token_data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(token_data)

        payload = verify_access_token(token)

        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"

    def test_verify_refresh_token(self):
        """Test refresh token verification."""
        token_data = {"sub": "user123", "username": "testuser"}
        token = create_refresh_token(token_data)

        payload = verify_refresh_token(token)

        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"
        assert "jti" in payload

    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        payload = verify_access_token("invalid.token.here")

        assert payload is None

    def test_verify_expired_token(self):
        """Test verification of expired token."""
        token_data = {"sub": "user123", "username": "testuser"}
        # Create token that expires immediately
        token = create_access_token(token_data, expires_delta=timedelta(seconds=-1))

        payload = verify_access_token(token)

        assert payload is None

    def test_access_token_cannot_be_refresh_token(self):
        """Test that access token is not validated as refresh token."""
        token_data = {"sub": "user123", "username": "testuser"}
        access_token = create_access_token(token_data)

        payload = verify_refresh_token(access_token)

        assert payload is None

    def test_refresh_token_cannot_be_access_token(self):
        """Test that refresh token is not validated as access token."""
        token_data = {"sub": "user123", "username": "testuser"}
        refresh_token = create_refresh_token(token_data)

        payload = verify_access_token(refresh_token)

        assert payload is None


class TestPasswordReset:
    """Test password reset token operations."""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Initialize auth config for tests."""
        init_auth_config(
            secret_key="test_secret_key_12345",
            access_expire=30,
            refresh_expire=7
        )

    def test_generate_password_reset_token(self):
        """Test password reset token generation."""
        user_id = "user123"
        token = generate_password_reset_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT format

    def test_verify_password_reset_token(self):
        """Test password reset token verification."""
        user_id = "user123"
        token = generate_password_reset_token(user_id)

        verified_user_id = verify_password_reset_token(token)

        assert verified_user_id == user_id

    def test_verify_invalid_reset_token(self):
        """Test verification of invalid reset token."""
        verified_user_id = verify_password_reset_token("invalid.token.here")

        assert verified_user_id is None

    def test_reset_token_cannot_be_access_token(self):
        """Test that access token is not validated as reset token."""
        token_data = {"sub": "user123", "username": "testuser"}
        access_token = create_access_token(token_data)

        verified_user_id = verify_password_reset_token(access_token)

        assert verified_user_id is None
