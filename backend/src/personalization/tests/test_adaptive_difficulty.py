"""Unit and integration tests for adaptive difficulty adjustment."""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.services.adaptive_difficulty_service import (
    AdaptiveDifficultyService, get_adaptive_difficulty_service
)
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


class TestAdaptiveDifficultyService:
    """Test adaptive difficulty service."""

    @pytest.mark.asyncio
    async def test_track_simplify_request_decreases_skill(self, mock_db, test_user):
        """Test that simplify request decreases skill level."""
        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ), patch(
            "src.personalization.services.adaptive_difficulty_service.update_user",
            new_callable=AsyncMock,
            return_value=None
        ):
            service = AdaptiveDifficultyService(mock_db)

            result = await service.track_simplify_request(test_user.user_id)

            assert result["success"] is True
            assert result["previous_skill_level"] == 50
            assert result["new_skill_level"] == 40
            assert result["adjustment"] == -10
            assert "beginner" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_track_simplify_request_cannot_go_below_zero(self, mock_db):
        """Test that skill level cannot go below 0."""
        user = User(
            user_id=uuid4(),
            username="test",
            email="test@example.com",
            password_hash="hashed",
            skill_level=5,
            skill_confidence=50
        )

        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=user
        ), patch(
            "src.personalization.services.adaptive_difficulty_service.update_user",
            new_callable=AsyncMock,
            return_value=None
        ):
            service = AdaptiveDifficultyService(mock_db)

            result = await service.track_simplify_request(user.user_id)

            assert result["success"] is True
            assert result["new_skill_level"] == 0  # Capped at 0

    @pytest.mark.asyncio
    async def test_track_advanced_request_increases_skill(self, mock_db, test_user):
        """Test that advanced request increases skill level."""
        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ), patch(
            "src.personalization.services.adaptive_difficulty_service.update_user",
            new_callable=AsyncMock,
            return_value=None
        ):
            service = AdaptiveDifficultyService(mock_db)

            result = await service.track_advanced_request(test_user.user_id)

            assert result["success"] is True
            assert result["previous_skill_level"] == 50
            assert result["new_skill_level"] == 60
            assert result["adjustment"] == 10
            assert "advanced" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_track_advanced_request_cannot_exceed_100(self, mock_db):
        """Test that skill level cannot exceed 100."""
        user = User(
            user_id=uuid4(),
            username="test",
            email="test@example.com",
            password_hash="hashed",
            skill_level=95,
            skill_confidence=90
        )

        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=user
        ), patch(
            "src.personalization.services.adaptive_difficulty_service.update_user",
            new_callable=AsyncMock,
            return_value=None
        ):
            service = AdaptiveDifficultyService(mock_db)

            result = await service.track_advanced_request(user.user_id)

            assert result["success"] is True
            assert result["new_skill_level"] == 100  # Capped at 100

    @pytest.mark.asyncio
    async def test_track_simplify_reduces_confidence(self, mock_db, test_user):
        """Test that simplify request reduces confidence."""
        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ), patch(
            "src.personalization.services.adaptive_difficulty_service.update_user",
            new_callable=AsyncMock,
            return_value=None
        ) as mock_update:
            service = AdaptiveDifficultyService(mock_db)

            await service.track_simplify_request(test_user.user_id)

            # Verify update was called with reduced confidence
            call_args = mock_update.call_args
            assert call_args[0][2]["skill_confidence"] == 40

    @pytest.mark.asyncio
    async def test_track_advanced_increases_confidence(self, mock_db, test_user):
        """Test that advanced request increases confidence."""
        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ), patch(
            "src.personalization.services.adaptive_difficulty_service.update_user",
            new_callable=AsyncMock,
            return_value=None
        ) as mock_update:
            service = AdaptiveDifficultyService(mock_db)

            await service.track_advanced_request(test_user.user_id)

            # Verify update was called with increased confidence
            call_args = mock_update.call_args
            assert call_args[0][2]["skill_confidence"] == 60

    @pytest.mark.asyncio
    async def test_update_skill_confidence_high_performance(self, mock_db, test_user):
        """Test confidence update with high performance."""
        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ), patch(
            "src.personalization.services.adaptive_difficulty_service.update_user",
            new_callable=AsyncMock,
            return_value=None
        ):
            service = AdaptiveDifficultyService(mock_db)

            result = await service.update_skill_confidence(
                test_user.user_id,
                performance_metric=90
            )

            assert result["success"] is True
            assert result["skill_confidence"] > test_user.skill_confidence
            assert result["skill_level"] > test_user.skill_level

    @pytest.mark.asyncio
    async def test_update_skill_confidence_low_performance(self, mock_db, test_user):
        """Test confidence update with low performance."""
        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ), patch(
            "src.personalization.services.adaptive_difficulty_service.update_user",
            new_callable=AsyncMock,
            return_value=None
        ):
            service = AdaptiveDifficultyService(mock_db)

            result = await service.update_skill_confidence(
                test_user.user_id,
                performance_metric=20
            )

            assert result["success"] is True
            assert result["skill_confidence"] < test_user.skill_confidence
            assert result["skill_level"] < test_user.skill_level

    @pytest.mark.asyncio
    async def test_update_skill_confidence_medium_performance(self, mock_db, test_user):
        """Test confidence update with medium performance (no change)."""
        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=test_user
        ), patch(
            "src.personalization.services.adaptive_difficulty_service.update_user",
            new_callable=AsyncMock,
            return_value=None
        ):
            service = AdaptiveDifficultyService(mock_db)

            result = await service.update_skill_confidence(
                test_user.user_id,
                performance_metric=50
            )

            assert result["success"] is True
            assert result["skill_confidence"] == test_user.skill_confidence
            assert result["skill_level"] == test_user.skill_level

    def test_get_recommended_difficulty_low_confidence(self):
        """Test difficulty recommendation with low confidence."""
        service = AdaptiveDifficultyService(AsyncMock())

        difficulty = service.get_recommended_difficulty(
            skill_level=80,
            skill_confidence=20
        )

        # Low confidence should recommend beginner regardless of skill
        assert difficulty == "beginner"

    def test_get_recommended_difficulty_high_skill_high_confidence(self):
        """Test difficulty recommendation with high skill and confidence."""
        service = AdaptiveDifficultyService(AsyncMock())

        difficulty = service.get_recommended_difficulty(
            skill_level=85,
            skill_confidence=90
        )

        assert difficulty == "advanced"

    def test_get_recommended_difficulty_medium_skill_medium_confidence(self):
        """Test difficulty recommendation with medium skill and confidence."""
        service = AdaptiveDifficultyService(AsyncMock())

        difficulty = service.get_recommended_difficulty(
            skill_level=50,
            skill_confidence=50
        )

        assert difficulty == "intermediate"

    def test_get_recommended_difficulty_beginner_skill(self):
        """Test difficulty recommendation for beginner skill."""
        service = AdaptiveDifficultyService(AsyncMock())

        difficulty = service.get_recommended_difficulty(
            skill_level=25,
            skill_confidence=80
        )

        assert difficulty == "beginner"

    @pytest.mark.asyncio
    async def test_service_factory(self, mock_db):
        """Test adaptive difficulty service factory function."""
        service = await get_adaptive_difficulty_service(mock_db)

        assert isinstance(service, AdaptiveDifficultyService)
        assert service.db == mock_db

    @pytest.mark.asyncio
    async def test_user_not_found_returns_failure(self, mock_db):
        """Test that non-existent user returns failure."""
        with patch(
            "src.personalization.services.adaptive_difficulty_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=None
        ):
            service = AdaptiveDifficultyService(mock_db)

            result = await service.track_simplify_request(uuid4())

            assert result["success"] is False
            assert "not found" in result["message"].lower()
