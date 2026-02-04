"""User authentication and profile management routes."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session as get_db
from src.personalization.models.schemas import (
    UserCreate, UserLogin, TokenResponse, UserProfile,
    UserUpdate, UserResponse, UserPreferences
)
from src.personalization.models.db_models import User
from src.personalization.services import user_service
from src.personalization.utils.auth import (
    create_access_token, create_refresh_token,
    verify_refresh_token, validate_password_strength, init_auth_config
)
from src.personalization.api.dependencies import (
    get_current_user, login_rate_limiter, registration_rate_limiter
)
from src.config import get_settings

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# Initialize auth config
settings = get_settings()
init_auth_config(
    secret_key=settings.SECRET_KEY,
    access_expire=30,
    refresh_expire=7
)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    Args:
        user_data: User registration data (username, email, password)
        request: Request object for rate limiting
        db: Database session

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException 400: If username/email already exists or password invalid
        HTTPException 429: If rate limit exceeded
    """
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not await registration_rate_limiter.check_rate_limit(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later.",
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    try:
        # Create user
        user = await user_service.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )

        # Generate tokens
        token_data = {"sub": str(user.user_id), "username": user.username}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.user_id,
            username=user.username
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again.",
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.

    Args:
        credentials: User login credentials (email, password)
        request: Request object for rate limiting
        db: Database session

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 429: If rate limit exceeded
    """
    # Rate limiting
    if not await login_rate_limiter.check_rate_limit(credentials.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )

    # Authenticate user
    user = await user_service.authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    token_data = {"sub": str(user.user_id), "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=user.user_id,
        username=user.username
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Args:
        refresh_token: Valid refresh token
        db: Database session

    Returns:
        TokenResponse with new access token and refresh token

    Raises:
        HTTPException 401: If refresh token is invalid or expired
    """
    # Verify refresh token
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    # Verify user still exists
    user = await user_service.get_user_by_id(db, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account deleted",
        )

    # Generate new tokens
    token_data = {"sub": str(user.user_id), "username": user.username}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user_id=user.user_id,
        username=user.username
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (client-side token removal, server acknowledgment).

    Args:
        current_user: Current authenticated user

    Returns:
        204 No Content

    Note:
        In a JWT-based system, actual logout is handled client-side by
        removing the tokens. This endpoint serves as a logout event hook
        for logging/analytics purposes. For token revocation, implement
        a token blacklist in production.
    """
    # In production, you might want to:
    # 1. Add token to blacklist/revocation list
    # 2. Log logout event
    # 3. Clear any session data
    # 4. Send analytics event

    # For now, just acknowledge the logout
    return None


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.

    Args:
        current_user: Current authenticated user

    Returns:
        UserProfile with complete user information
    """
    return UserProfile(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        skill_level=current_user.skill_level,
        skill_confidence=current_user.skill_confidence,
        profile_picture_url=current_user.profile_picture_url,
        bio=current_user.bio,
        preferences=UserPreferences(**current_user.preferences_json),
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )


@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current authenticated user's profile.

    Args:
        updates: Fields to update (username, email, bio, profile_picture_url, preferences)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated UserProfile

    Raises:
        HTTPException 400: If username/email already exists
    """
    try:
        # Prepare update data
        update_data = {}

        if updates.username is not None:
            update_data["username"] = updates.username

        if updates.email is not None:
            update_data["email"] = updates.email

        if updates.bio is not None:
            update_data["bio"] = updates.bio

        if updates.profile_picture_url is not None:
            update_data["profile_picture_url"] = updates.profile_picture_url

        # Update basic profile fields
        if update_data:
            user = await user_service.update_user_profile(
                db=db,
                user_id=current_user.user_id,
                updates=update_data
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            current_user = user

        # Update preferences if provided
        if updates.preferences is not None:
            user = await user_service.update_user_preferences(
                db=db,
                user_id=current_user.user_id,
                preferences=updates.preferences.model_dump()
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            current_user = user

        return UserProfile(
            user_id=current_user.user_id,
            username=current_user.username,
            email=current_user.email,
            skill_level=current_user.skill_level,
            skill_confidence=current_user.skill_confidence,
            profile_picture_url=current_user.profile_picture_url,
            bio=current_user.bio,
            preferences=UserPreferences(**current_user.preferences_json),
            created_at=current_user.created_at,
            last_login_at=current_user.last_login_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user profile by user ID (requires authentication).

    Args:
        user_id: User ID to retrieve
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserProfile for the requested user

    Raises:
        HTTPException 404: If user not found
        HTTPException 403: If trying to access deleted user

    Note:
        In production, you may want to restrict this to only allow
        users to view their own profile, or implement privacy settings.
    """
    user = await user_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deleted"
        )

    return UserProfile(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        skill_level=user.skill_level,
        skill_confidence=user.skill_confidence,
        profile_picture_url=user.profile_picture_url,
        bio=user.bio,
        preferences=UserPreferences(**user.preferences_json),
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )
