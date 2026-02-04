"""Authentication utilities for JWT token management and password hashing."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration (will be loaded from config)
SECRET_KEY = None
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def init_auth_config(secret_key: str, algorithm: str = "HS256",
                     access_expire: int = 30, refresh_expire: int = 7):
    """Initialize authentication configuration."""
    global SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
    SECRET_KEY = secret_key
    ALGORITHM = algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = access_expire
    REFRESH_TOKEN_EXPIRE_DAYS = refresh_expire


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY not initialized. Call init_auth_config() first.")

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: Dictionary of claims to encode in the token

    Returns:
        Encoded JWT refresh token string
    """
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY not initialized. Call init_auth_config() first.")

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)  # Unique token ID for tracking/revocation
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary of decoded token claims

    Raises:
        JWTError: If token is invalid or expired
    """
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY not initialized. Call init_auth_config() first.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify an access token and return payload.

    Args:
        token: JWT access token string

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = decode_token(token)

        # Verify it's an access token
        if payload.get("type") != "access":
            return None

        # Check if token has required claims
        if "sub" not in payload:
            return None

        return payload
    except JWTError:
        return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a refresh token and return payload.

    Args:
        token: JWT refresh token string

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = decode_token(token)

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return None

        # Check if token has required claims
        if "sub" not in payload or "jti" not in payload:
            return None

        return payload
    except JWTError:
        return None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user_id from a JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID string if token is valid, None otherwise
    """
    payload = verify_access_token(token)
    if payload:
        return payload.get("sub")
    return None


def generate_password_reset_token(user_id: str) -> str:
    """
    Generate a password reset token.

    Args:
        user_id: User ID to generate token for

    Returns:
        Password reset token string
    """
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY not initialized. Call init_auth_config() first.")

    expire = datetime.utcnow() + timedelta(hours=1)  # Reset tokens expire in 1 hour

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "password_reset",
        "jti": secrets.token_urlsafe(32)
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return user_id.

    Args:
        token: Password reset token string

    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        payload = decode_token(token)

        # Verify it's a password reset token
        if payload.get("type") != "password_reset":
            return None

        # Check if token has required claims
        if "sub" not in payload:
            return None

        return payload.get("sub")
    except JWTError:
        return None


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password meets security requirements.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 100:
        return False, "Password must be less than 100 characters"

    # Check for at least one uppercase, one lowercase, and one digit
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain at least one uppercase letter, one lowercase letter, and one digit"

    return True, None
