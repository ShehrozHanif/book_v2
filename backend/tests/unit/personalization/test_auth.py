"""Unit tests for authentication utilities."""

import pytest
from datetime import datetime, timedelta
from jose import jwt

from src.personalization.utils.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, verify_access_token, verify_refresh_token,
    extract_user_id_from_token, validate_password_strength,
    init_auth_config, SECRET_KEY, ALGORITHM
)


@pytest.fixture(autouse=True)
def setup_auth():
    """Setup authentication configuration for tests."""
    init_auth_config(
        secret_key="test_secret_key_minimum_32_chars_long_for_security",
        algorithm="HS256",
        access_expire=30,
        refresh_expire=7
    )


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password_creates_different_hashes(self):
        """Test that hashing same password twice produces different hashes."""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Bcrypt uses salt, so hashes differ
        assert hash1.startswith("$2b$")  # Bcrypt format

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        password_hash = hash_password(password)

        assert verify_password(password, password_hash) is True

    def test_verify_password_failure(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        password_hash = hash_password(password)

        assert verify_password(wrong_password, password_hash) is False

    def test_verify_password_empty_string(self):
        """Test password verification with empty password."""
        password = "TestPassword123!"
        password_hash = hash_password(password)

        assert verify_password("", password_hash) is False

    def test_hash_password_special_characters(self):
        """Test hashing password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        password_hash = hash_password(password)

        assert verify_password(password, password_hash) is True


class TestPasswordValidation:
    """Tests for password strength validation."""

    def test_validate_strong_password(self):
        """Test validation of strong password."""
        is_valid, error = validate_password_strength("SecurePass123!")
        assert is_valid is True
        assert error is None

    def test_validate_password_too_short(self):
        """Test validation of password that's too short."""
        is_valid, error = validate_password_strength("Short1!")
        assert is_valid is False
        assert "at least 8 characters" in error

    def test_validate_password_too_long(self):
        """Test validation of password that's too long."""
        long_password = "A" * 101 + "1a"
        is_valid, error = validate_password_strength(long_password)
        assert is_valid is False
        assert "less than 100 characters" in error

    def test_validate_password_no_uppercase(self):
        """Test validation of password without uppercase letter."""
        is_valid, error = validate_password_strength("lowercase123!")
        assert is_valid is False
        assert "uppercase letter" in error

    def test_validate_password_no_lowercase(self):
        """Test validation of password without lowercase letter."""
        is_valid, error = validate_password_strength("UPPERCASE123!")
        assert is_valid is False
        assert "lowercase letter" in error

    def test_validate_password_no_digit(self):
        """Test validation of password without digit."""
        is_valid, error = validate_password_strength("NoDigitsHere!")
        assert is_valid is False
        assert "digit" in error


class TestTokenCreation:
    """Tests for JWT token creation."""

    def test_create_access_token(self):
        """Test creation of access token."""
        data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        payload = decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_custom_expiry(self):
        """Test creation of access token with custom expiry."""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)

        payload = decode_token(token)
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])

        time_diff = exp_time - iat_time
        # Allow for small timing differences
        assert 59 <= time_diff.total_seconds() / 60 <= 61

    def test_create_refresh_token(self):
        """Test creation of refresh token."""
        data = {"sub": "user123", "username": "testuser"}
        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        payload = decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "refresh"
        assert "jti" in payload  # Unique token ID
        assert "exp" in payload
        assert "iat" in payload

    def test_refresh_token_has_unique_jti(self):
        """Test that refresh tokens have unique JTI."""
        data = {"sub": "user123"}
        token1 = create_refresh_token(data)
        token2 = create_refresh_token(data)

        payload1 = decode_token(token1)
        payload2 = decode_token(token2)

        assert payload1["jti"] != payload2["jti"]


class TestTokenVerification:
    """Tests for JWT token verification."""

    def test_verify_access_token_valid(self):
        """Test verification of valid access token."""
        data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(data)

        payload = verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"

    def test_verify_access_token_invalid(self):
        """Test verification of invalid access token."""
        payload = verify_access_token("invalid.token.here")
        assert payload is None

    def test_verify_access_token_wrong_type(self):
        """Test that refresh token fails access token verification."""
        data = {"sub": "user123"}
        refresh_token = create_refresh_token(data)

        payload = verify_access_token(refresh_token)
        assert payload is None  # Should fail because type is 'refresh'

    def test_verify_refresh_token_valid(self):
        """Test verification of valid refresh token."""
        data = {"sub": "user123", "username": "testuser"}
        token = create_refresh_token(data)

        payload = verify_refresh_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"
        assert "jti" in payload

    def test_verify_refresh_token_invalid(self):
        """Test verification of invalid refresh token."""
        payload = verify_refresh_token("invalid.token.here")
        assert payload is None

    def test_verify_refresh_token_wrong_type(self):
        """Test that access token fails refresh token verification."""
        data = {"sub": "user123"}
        access_token = create_access_token(data)

        payload = verify_refresh_token(access_token)
        assert payload is None  # Should fail because type is 'access'

    def test_extract_user_id_from_token_valid(self):
        """Test extracting user ID from valid token."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        data = {"sub": user_id}
        token = create_access_token(data)

        extracted_id = extract_user_id_from_token(token)
        assert extracted_id == user_id

    def test_extract_user_id_from_token_invalid(self):
        """Test extracting user ID from invalid token."""
        extracted_id = extract_user_id_from_token("invalid.token.here")
        assert extracted_id is None

    def test_decode_expired_token(self):
        """Test decoding expired token raises error."""
        # Create token that's already expired
        data = {"sub": "user123", "exp": datetime.utcnow() - timedelta(hours=1)}
        from src.personalization.utils.auth import SECRET_KEY, ALGORITHM
        expired_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

        from jose import JWTError
        with pytest.raises(JWTError):
            decode_token(expired_token)

    def test_decode_token_missing_sub(self):
        """Test verification fails for token missing 'sub' claim."""
        data = {"username": "testuser"}  # No 'sub'
        token = create_access_token(data)

        payload = verify_access_token(token)
        assert payload is None


class TestTokenSecurity:
    """Tests for token security features."""

    def test_token_cannot_be_modified(self):
        """Test that modified token fails verification."""
        data = {"sub": "user123"}
        token = create_access_token(data)

        # Try to modify token
        parts = token.split(".")
        modified_token = parts[0] + ".modified." + parts[2]

        payload = verify_access_token(modified_token)
        assert payload is None

    def test_tokens_are_different_for_same_data(self):
        """Test that tokens created at different times are different."""
        data = {"sub": "user123"}

        token1 = create_access_token(data)
        import time
        time.sleep(0.1)  # Small delay
        token2 = create_access_token(data)

        assert token1 != token2  # Different due to different iat/exp

    def test_token_without_initialization_raises_error(self):
        """Test that token creation without init raises error."""
        # Reset SECRET_KEY to None
        import src.personalization.utils.auth as auth_module
        original_key = auth_module.SECRET_KEY
        auth_module.SECRET_KEY = None

        with pytest.raises(ValueError, match="SECRET_KEY not initialized"):
            create_access_token({"sub": "user123"})

        # Restore
        auth_module.SECRET_KEY = original_key


class TestAuthConfiguration:
    """Tests for authentication configuration."""

    def test_init_auth_config(self):
        """Test initializing auth configuration."""
        init_auth_config(
            secret_key="custom_secret_key_32_chars_long!",
            algorithm="HS256",
            access_expire=60,
            refresh_expire=14
        )

        from src.personalization.utils.auth import (
            SECRET_KEY, ALGORITHM,
            ACCESS_TOKEN_EXPIRE_MINUTES,
            REFRESH_TOKEN_EXPIRE_DAYS
        )

        assert SECRET_KEY == "custom_secret_key_32_chars_long!"
        assert ALGORITHM == "HS256"
        assert ACCESS_TOKEN_EXPIRE_MINUTES == 60
        assert REFRESH_TOKEN_EXPIRE_DAYS == 14

    def test_token_uses_configured_expiry(self):
        """Test that token uses configured expiry time."""
        init_auth_config(
            secret_key="test_key_32_characters_long_ok!",
            access_expire=15  # 15 minutes
        )

        data = {"sub": "user123"}
        token = create_access_token(data)
        payload = decode_token(token)

        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        time_diff = exp_time - iat_time

        # Should be approximately 15 minutes
        assert 14 <= time_diff.total_seconds() / 60 <= 16
