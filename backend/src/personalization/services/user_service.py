"""User service layer for business logic operations."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import User
from src.personalization.utils.auth import hash_password, verify_password


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str
) -> User:
    """
    Create a new user account.

    Args:
        db: Database session
        username: Unique username
        email: User email address
        password: Plain text password (will be hashed)

    Returns:
        Created User object

    Raises:
        ValueError: If username or email already exists
    """
    # Check if username already exists
    existing_username = await db.execute(
        select(User).where(User.username == username)
    )
    if existing_username.scalar_one_or_none():
        raise ValueError(f"Username '{username}' already exists")

    # Check if email already exists
    existing_email = await db.execute(
        select(User).where(User.email == email.lower())
    )
    if existing_email.scalar_one_or_none():
        raise ValueError(f"Email '{email}' already exists")

    # Hash password
    password_hash = hash_password(password)

    # Create new user
    new_user = User(
        username=username,
        email=email.lower(),
        password_hash=password_hash,
        skill_level=50,  # Default medium skill level
        skill_confidence=50,  # Default medium confidence
        preferences_json={
            "explanation_style": "example_first",
            "code_language": "python",
            "learning_pace": "medium",
            "content_focus": "balanced"
        }
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
) -> Optional[User]:
    """
    Authenticate user with email and password.

    Args:
        db: Database session
        email: User email address
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    # Find user by email
    result = await db.execute(
        select(User).where(
            and_(
                User.email == email.lower(),
                User.deleted_at.is_(None)  # Exclude deleted users
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Verify password
    if not verify_password(password, user.password_hash):
        return None

    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    return user


async def get_user_by_id(
    db: AsyncSession,
    user_id: UUID
) -> Optional[User]:
    """
    Retrieve user by ID.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(
    db: AsyncSession,
    email: str
) -> Optional[User]:
    """
    Retrieve user by email.

    Args:
        db: Database session
        email: User email address

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(
        select(User).where(
            and_(
                User.email == email.lower(),
                User.deleted_at.is_(None)
            )
        )
    )
    return result.scalar_one_or_none()


async def get_user_by_username(
    db: AsyncSession,
    username: str
) -> Optional[User]:
    """
    Retrieve user by username.

    Args:
        db: Database session
        username: Username

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(
        select(User).where(
            and_(
                User.username == username,
                User.deleted_at.is_(None)
            )
        )
    )
    return result.scalar_one_or_none()


async def update_user_profile(
    db: AsyncSession,
    user_id: UUID,
    updates: Dict[str, Any]
) -> Optional[User]:
    """
    Update user profile information.

    Args:
        db: Database session
        user_id: User UUID
        updates: Dictionary of fields to update

    Returns:
        Updated User object if successful, None if user not found

    Raises:
        ValueError: If trying to update to an existing username/email
    """
    # Get user
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # Check for username uniqueness if updating
    if 'username' in updates and updates['username'] != user.username:
        existing = await get_user_by_username(db, updates['username'])
        if existing:
            raise ValueError(f"Username '{updates['username']}' already exists")

    # Check for email uniqueness if updating
    if 'email' in updates and updates['email'].lower() != user.email:
        existing = await get_user_by_email(db, updates['email'])
        if existing:
            raise ValueError(f"Email '{updates['email']}' already exists")

    # Update allowed fields
    allowed_fields = ['username', 'email', 'bio', 'profile_picture_url']
    for field, value in updates.items():
        if field in allowed_fields:
            if field == 'email':
                value = value.lower()
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


async def update_user_preferences(
    db: AsyncSession,
    user_id: UUID,
    preferences: Dict[str, str]
) -> Optional[User]:
    """
    Update user learning preferences.

    Args:
        db: Database session
        user_id: User UUID
        preferences: Dictionary of preference updates

    Returns:
        Updated User object if successful, None if user not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # Update preferences (merge with existing)
    current_prefs = user.preferences_json or {}
    current_prefs.update(preferences)
    user.preferences_json = current_prefs

    await db.commit()
    await db.refresh(user)

    return user


async def update_user_skill_level(
    db: AsyncSession,
    user_id: UUID,
    skill_level: int,
    skill_confidence: Optional[int] = None
) -> Optional[User]:
    """
    Update user skill level and optionally confidence.

    Args:
        db: Database session
        user_id: User UUID
        skill_level: New skill level (0-100)
        skill_confidence: Optional confidence level (0-100)

    Returns:
        Updated User object if successful, None if user not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    user.skill_level = max(0, min(100, skill_level))  # Clamp to 0-100
    if skill_confidence is not None:
        user.skill_confidence = max(0, min(100, skill_confidence))

    await db.commit()
    await db.refresh(user)

    return user


async def soft_delete_user(
    db: AsyncSession,
    user_id: UUID
) -> bool:
    """
    Soft delete a user account (sets deleted_at timestamp).

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        True if successful, False if user not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return False

    user.deleted_at = datetime.utcnow()
    await db.commit()

    return True


async def anonymize_user_data(
    db: AsyncSession,
    user_id: UUID
) -> bool:
    """
    Anonymize user data for GDPR compliance.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        True if successful, False if user not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return False

    # Anonymize personal data
    user.username = f"deleted_user_{user_id.hex[:8]}"
    user.email = f"deleted_{user_id.hex[:8]}@deleted.local"
    user.password_hash = "DELETED"
    user.bio = None
    user.profile_picture_url = None
    user.deleted_at = datetime.utcnow()

    await db.commit()

    return True


async def change_user_password(
    db: AsyncSession,
    user_id: UUID,
    old_password: str,
    new_password: str
) -> tuple[bool, Optional[str]]:
    """
    Change user password with old password verification.

    Args:
        db: Database session
        user_id: User UUID
        old_password: Current password for verification
        new_password: New password to set

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return False, "User not found"

    # Verify old password
    if not verify_password(old_password, user.password_hash):
        return False, "Current password is incorrect"

    # Hash and set new password
    user.password_hash = hash_password(new_password)
    await db.commit()

    return True, None


async def reset_user_password(
    db: AsyncSession,
    user_id: UUID,
    new_password: str
) -> bool:
    """
    Reset user password (for admin/recovery use).

    Args:
        db: Database session
        user_id: User UUID
        new_password: New password to set

    Returns:
        True if successful, False if user not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return False

    user.password_hash = hash_password(new_password)
    await db.commit()

    return True
