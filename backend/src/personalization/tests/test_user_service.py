"""Unit tests for user service layer."""

import pytest
from uuid import uuid4

from src.personalization.services import user_service
from src.personalization.utils.auth import verify_password


class TestUserService:
    """Test cases for user service functions."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, test_db):
        """Test successful user creation."""
        user = await user_service.create_user(
            db=test_db,
            username="newuser",
            email="newuser@example.com",
            password="NewPass123!"
        )

        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.password_hash != "NewPass123!"  # Password should be hashed
        assert user.skill_level == 50  # Default value
        assert user.skill_confidence == 50  # Default value

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, test_db, created_user):
        """Test user creation with duplicate username."""
        with pytest.raises(ValueError, match="already exists"):
            await user_service.create_user(
                db=test_db,
                username=created_user.username,
                email="different@example.com",
                password="NewPass123!"
            )

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, test_db, created_user):
        """Test user creation with duplicate email."""
        with pytest.raises(ValueError, match="already exists"):
            await user_service.create_user(
                db=test_db,
                username="differentuser",
                email=created_user.email,
                password="NewPass123!"
            )

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, test_db, created_user, sample_user_data):
        """Test successful user authentication."""
        user = await user_service.authenticate_user(
            db=test_db,
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )

        assert user is not None
        assert user.user_id == created_user.user_id
        assert user.last_login_at is not None

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, test_db, sample_user_data, created_user):
        """Test authentication with wrong password."""
        user = await user_service.authenticate_user(
            db=test_db,
            email=sample_user_data["email"],
            password="WrongPassword123!"
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent(self, test_db):
        """Test authentication with non-existent email."""
        user = await user_service.authenticate_user(
            db=test_db,
            email="nonexistent@example.com",
            password="SomePass123!"
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_db, created_user):
        """Test retrieving user by ID."""
        user = await user_service.get_user_by_id(test_db, created_user.user_id)

        assert user is not None
        assert user.user_id == created_user.user_id
        assert user.username == created_user.username

    @pytest.mark.asyncio
    async def test_get_user_by_id_nonexistent(self, test_db):
        """Test retrieving non-existent user by ID."""
        user = await user_service.get_user_by_id(test_db, uuid4())

        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, test_db, created_user):
        """Test retrieving user by email."""
        user = await user_service.get_user_by_email(test_db, created_user.email)

        assert user is not None
        assert user.user_id == created_user.user_id
        assert user.email == created_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, test_db, created_user):
        """Test retrieving user by username."""
        user = await user_service.get_user_by_username(test_db, created_user.username)

        assert user is not None
        assert user.user_id == created_user.user_id
        assert user.username == created_user.username

    @pytest.mark.asyncio
    async def test_update_user_profile(self, test_db, created_user):
        """Test updating user profile."""
        updates = {
            "bio": "Test bio",
            "profile_picture_url": "https://example.com/pic.jpg"
        }

        user = await user_service.update_user_profile(
            db=test_db,
            user_id=created_user.user_id,
            updates=updates
        )

        assert user is not None
        assert user.bio == "Test bio"
        assert user.profile_picture_url == "https://example.com/pic.jpg"

    @pytest.mark.asyncio
    async def test_update_user_preferences(self, test_db, created_user):
        """Test updating user preferences."""
        preferences = {
            "explanation_style": "theory_first",
            "code_language": "cpp"
        }

        user = await user_service.update_user_preferences(
            db=test_db,
            user_id=created_user.user_id,
            preferences=preferences
        )

        assert user is not None
        assert user.preferences_json["explanation_style"] == "theory_first"
        assert user.preferences_json["code_language"] == "cpp"

    @pytest.mark.asyncio
    async def test_update_user_skill_level(self, test_db, created_user):
        """Test updating user skill level."""
        user = await user_service.update_user_skill_level(
            db=test_db,
            user_id=created_user.user_id,
            skill_level=75,
            skill_confidence=80
        )

        assert user is not None
        assert user.skill_level == 75
        assert user.skill_confidence == 80

    @pytest.mark.asyncio
    async def test_soft_delete_user(self, test_db, created_user):
        """Test soft deleting a user."""
        success = await user_service.soft_delete_user(test_db, created_user.user_id)

        assert success is True

        # Verify user is marked as deleted
        user = await user_service.get_user_by_id(test_db, created_user.user_id)
        assert user.deleted_at is not None

    @pytest.mark.asyncio
    async def test_change_user_password(self, test_db, created_user, sample_user_data):
        """Test changing user password."""
        success, error = await user_service.change_user_password(
            db=test_db,
            user_id=created_user.user_id,
            old_password=sample_user_data["password"],
            new_password="NewSecurePass123!"
        )

        assert success is True
        assert error is None

        # Verify new password works
        user = await user_service.get_user_by_id(test_db, created_user.user_id)
        assert verify_password("NewSecurePass123!", user.password_hash)

    @pytest.mark.asyncio
    async def test_change_user_password_wrong_old_password(self, test_db, created_user):
        """Test changing password with wrong old password."""
        success, error = await user_service.change_user_password(
            db=test_db,
            user_id=created_user.user_id,
            old_password="WrongPassword123!",
            new_password="NewSecurePass123!"
        )

        assert success is False
        assert "incorrect" in error.lower()

    @pytest.mark.asyncio
    async def test_reset_user_password(self, test_db, created_user):
        """Test resetting user password (admin/recovery)."""
        success = await user_service.reset_user_password(
            db=test_db,
            user_id=created_user.user_id,
            new_password="ResetPass123!"
        )

        assert success is True

        # Verify new password works
        user = await user_service.get_user_by_id(test_db, created_user.user_id)
        assert verify_password("ResetPass123!", user.password_hash)

    @pytest.mark.asyncio
    async def test_password_hashing(self):
        """Test password hashing functionality."""
        from src.personalization.utils.auth import hash_password

        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)
