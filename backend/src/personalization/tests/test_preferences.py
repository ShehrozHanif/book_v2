"""Integration and unit tests for user preferences functionality."""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.services import user_service
from src.personalization.models.db_models import User


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def test_user():
    """Create a test user."""
    return User(
        user_id=uuid4(),
        username="test_learner",
        email="test@example.com",
        password_hash="hashed",
        skill_level=50,
        skill_confidence=50,
        preferences_json={
            "explanation_style": "example_first",
            "code_language": "python",
            "learning_pace": "medium",
            "content_focus": "balanced"
        }
    )


class TestUpdateUserPreferences:
    """Test user preference update functionality."""

    @pytest.mark.asyncio
    async def test_update_single_preference(self, mock_db, test_user):
        """Test updating a single preference."""
        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ):
            result = await user_service.update_user_preferences(
                db=mock_db,
                user_id=test_user.user_id,
                preferences={"explanation_style": "theory_first"}
            )

            assert result.preferences_json["explanation_style"] == "theory_first"
            # Other preferences should remain unchanged
            assert result.preferences_json["code_language"] == "python"

    @pytest.mark.asyncio
    async def test_update_multiple_preferences(self, mock_db, test_user):
        """Test updating multiple preferences at once."""
        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ):
            result = await user_service.update_user_preferences(
                db=mock_db,
                user_id=test_user.user_id,
                preferences={
                    "code_language": "cpp",
                    "learning_pace": "fast",
                    "content_focus": "hardware"
                }
            )

            assert result.preferences_json["code_language"] == "cpp"
            assert result.preferences_json["learning_pace"] == "fast"
            assert result.preferences_json["content_focus"] == "hardware"
            # Unchanged preference
            assert result.preferences_json["explanation_style"] == "example_first"

    @pytest.mark.asyncio
    async def test_update_preferences_invalid_field(self, mock_db, test_user):
        """Test that invalid preference field raises ValueError."""
        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ):
            with pytest.raises(ValueError) as exc_info:
                await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"invalid_field": "value"}
                )

            assert "unknown" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_preferences_invalid_explanation_style(self, mock_db, test_user):
        """Test that invalid explanation_style value raises ValueError."""
        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ):
            with pytest.raises(ValueError) as exc_info:
                await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"explanation_style": "invalid_value"}
                )

            assert "invalid" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_preferences_invalid_code_language(self, mock_db, test_user):
        """Test that invalid code_language value raises ValueError."""
        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ):
            with pytest.raises(ValueError) as exc_info:
                await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"code_language": "java"}
                )

            assert "invalid" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_preferences_invalid_learning_pace(self, mock_db, test_user):
        """Test that invalid learning_pace value raises ValueError."""
        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ):
            with pytest.raises(ValueError) as exc_info:
                await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"learning_pace": "ultrafast"}
                )

            assert "invalid" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_preferences_invalid_content_focus(self, mock_db, test_user):
        """Test that invalid content_focus value raises ValueError."""
        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ):
            with pytest.raises(ValueError) as exc_info:
                await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"content_focus": "theory"}
                )

            assert "invalid" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_preferences_valid_explanation_styles(self, mock_db, test_user):
        """Test all valid explanation_style values."""
        styles = ["theory_first", "example_first"]

        for style in styles:
            with patch(
                "src.personalization.services.user_service.get_user_by_id",
                new_callable=AsyncMock,
                return_value=test_user
            ):
                result = await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"explanation_style": style}
                )

                assert result.preferences_json["explanation_style"] == style

    @pytest.mark.asyncio
    async def test_update_preferences_valid_code_languages(self, mock_db, test_user):
        """Test all valid code_language values."""
        languages = ["python", "cpp", "both"]

        for lang in languages:
            with patch(
                "src.personalization.services.user_service.get_user_by_id",
                new_callable=AsyncMock,
                return_value=test_user
            ):
                result = await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"code_language": lang}
                )

                assert result.preferences_json["code_language"] == lang

    @pytest.mark.asyncio
    async def test_update_preferences_valid_learning_paces(self, mock_db, test_user):
        """Test all valid learning_pace values."""
        paces = ["slow", "medium", "fast"]

        for pace in paces:
            with patch(
                "src.personalization.services.user_service.get_user_by_id",
                new_callable=AsyncMock,
                return_value=test_user
            ):
                result = await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"learning_pace": pace}
                )

                assert result.preferences_json["learning_pace"] == pace

    @pytest.mark.asyncio
    async def test_update_preferences_valid_content_focus(self, mock_db, test_user):
        """Test all valid content_focus values."""
        focuses = ["simulation", "hardware", "balanced"]

        for focus in focuses:
            with patch(
                "src.personalization.services.user_service.get_user_by_id",
                new_callable=AsyncMock,
                return_value=test_user
            ):
                result = await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"content_focus": focus}
                )

                assert result.preferences_json["content_focus"] == focus

    @pytest.mark.asyncio
    async def test_update_preferences_user_not_found(self, mock_db):
        """Test that updating preferences for non-existent user returns None."""
        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=None
        ):
            result = await user_service.update_user_preferences(
                db=mock_db,
                user_id=uuid4(),
                preferences={"explanation_style": "theory_first"}
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_update_preferences_with_none_preferences_json(self, mock_db):
        """Test updating preferences when user has None preferences_json."""
        user = User(
            user_id=uuid4(),
            username="test",
            email="test@example.com",
            password_hash="hashed",
            preferences_json=None  # None instead of dict
        )

        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=user
        ):
            result = await user_service.update_user_preferences(
                db=mock_db,
                user_id=user.user_id,
                preferences={"explanation_style": "theory_first"}
            )

            assert result.preferences_json["explanation_style"] == "theory_first"

    @pytest.mark.asyncio
    async def test_error_message_includes_valid_options(self, mock_db, test_user):
        """Test that error message includes valid options."""
        with patch(
            "src.personalization.services.user_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ):
            with pytest.raises(ValueError) as exc_info:
                await user_service.update_user_preferences(
                    db=mock_db,
                    user_id=test_user.user_id,
                    preferences={"learning_pace": "invalid"}
                )

            error_msg = str(exc_info.value)
            assert "slow" in error_msg
            assert "medium" in error_msg
            assert "fast" in error_msg
