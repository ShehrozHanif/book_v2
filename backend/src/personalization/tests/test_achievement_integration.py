"""Integration tests for achievement integration with progress endpoints (T052)."""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import User, Progress, Achievement
from src.personalization.api.routes.progress import mark_chapter_complete


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = AsyncMock(spec=AsyncSession)
    return db


@pytest.fixture
def test_user():
    """Create test user."""
    return User(
        user_id=uuid4(),
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        skill_level=50
    )


@pytest.fixture
def progress_complete_data():
    """Create progress completion data."""
    from src.personalization.models.schemas import ProgressComplete
    return ProgressComplete(mastery_score=85, time_spent_seconds=600)


class TestAchievementIntegration:
    """Integration tests for achievement system with progress endpoints."""

    @pytest.mark.asyncio
    async def test_chapter_completion_returns_achievements(self, mock_db, test_user, progress_complete_data):
        """Test that chapter completion returns unlocked achievements."""
        # Mock progress creation
        mock_progress = MagicMock()
        mock_progress.progress_id = uuid4()
        mock_progress.user_id = test_user.user_id
        mock_progress.chapter_id = 1
        mock_progress.completion_status = "completed"
        mock_progress.time_spent_seconds = 600
        mock_progress.mastery_score = 85
        mock_progress.last_accessed_at = datetime.now()
        mock_progress.practice_attempts = 1
        mock_progress.highest_practice_score = 85

        # Mock XP earned
        with patch("src.personalization.api.routes.progress.progress_service") as mock_service:
            mock_service.complete_chapter = AsyncMock(return_value=mock_progress)
            mock_service.award_xp_for_chapter = AsyncMock(return_value=25)
            mock_service.update_skill_level = AsyncMock()

            # Mock achievement service
            with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_ach_service:
                mock_ach = AsyncMock()
                mock_ach.check_achievements = AsyncMock(return_value=["ch_1_complete", "first_chapter"])
                mock_ach_service.return_value = mock_ach

                result = await mark_chapter_complete(
                    chapter_id=1,
                    completion_data=progress_complete_data,
                    current_user=test_user,
                    db=mock_db
                )

                # Verify result structure
                assert "progress" in result
                assert "xp_earned" in result
                assert "achievements_unlocked" in result
                assert result["xp_earned"] == 25

    @pytest.mark.asyncio
    async def test_achievement_service_called_with_chapter_event(self, mock_db, test_user, progress_complete_data):
        """Test that achievement service is called with chapter_complete event."""
        mock_progress = MagicMock()
        mock_progress.progress_id = uuid4()
        mock_progress.user_id = test_user.user_id
        mock_progress.chapter_id = 1
        mock_progress.completion_status = "completed"
        mock_progress.time_spent_seconds = 600
        mock_progress.mastery_score = 85
        mock_progress.last_accessed_at = datetime.now()
        mock_progress.practice_attempts = 1
        mock_progress.highest_practice_score = 85

        with patch("src.personalization.api.routes.progress.progress_service") as mock_service:
            mock_service.complete_chapter = AsyncMock(return_value=mock_progress)
            mock_service.award_xp_for_chapter = AsyncMock(return_value=25)
            mock_service.update_skill_level = AsyncMock()

            with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_ach_service:
                mock_ach = AsyncMock()
                mock_ach.check_achievements = AsyncMock(return_value=[])
                mock_ach_service.return_value = mock_ach

                await mark_chapter_complete(
                    chapter_id=1,
                    completion_data=progress_complete_data,
                    current_user=test_user,
                    db=mock_db
                )

                # Verify achievement service was called with chapter_complete event
                assert mock_ach.check_achievements.call_count >= 1
                first_call = mock_ach.check_achievements.call_args_list[0]
                assert first_call[0][1] == "chapter_complete"  # event_type
                assert first_call[0][2]["chapter_id"] == 1  # chapter_id in event_data

    @pytest.mark.asyncio
    async def test_achievement_service_called_with_xp_event(self, mock_db, test_user, progress_complete_data):
        """Test that achievement service is called with xp_earned event."""
        mock_progress = MagicMock()
        mock_progress.progress_id = uuid4()
        mock_progress.user_id = test_user.user_id
        mock_progress.chapter_id = 1
        mock_progress.completion_status = "completed"
        mock_progress.time_spent_seconds = 600
        mock_progress.mastery_score = 85
        mock_progress.last_accessed_at = datetime.now()
        mock_progress.practice_attempts = 1
        mock_progress.highest_practice_score = 85

        with patch("src.personalization.api.routes.progress.progress_service") as mock_service:
            mock_service.complete_chapter = AsyncMock(return_value=mock_progress)
            mock_service.award_xp_for_chapter = AsyncMock(return_value=25)
            mock_service.update_skill_level = AsyncMock()

            with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_ach_service:
                mock_ach = AsyncMock()
                mock_ach.check_achievements = AsyncMock(return_value=[])
                mock_ach_service.return_value = mock_ach

                await mark_chapter_complete(
                    chapter_id=1,
                    completion_data=progress_complete_data,
                    current_user=test_user,
                    db=mock_db
                )

                # Verify achievement service was called with xp_earned event
                calls = mock_ach.check_achievements.call_args_list
                xp_calls = [c for c in calls if c[0][1] == "xp_earned"]
                assert len(xp_calls) > 0, "Expected at least one xp_earned event check"

    @pytest.mark.asyncio
    async def test_achievement_service_called_with_mastery_event(self, mock_db, test_user):
        """Test that achievement service is called with mastery_update event for 100% score."""
        from src.personalization.models.schemas import ProgressComplete

        # Create data with 100% mastery
        completion_data = ProgressComplete(mastery_score=100, time_spent_seconds=600)

        mock_progress = MagicMock()
        mock_progress.progress_id = uuid4()
        mock_progress.user_id = test_user.user_id
        mock_progress.chapter_id = 1
        mock_progress.completion_status = "completed"
        mock_progress.time_spent_seconds = 600
        mock_progress.mastery_score = 100
        mock_progress.last_accessed_at = datetime.now()
        mock_progress.practice_attempts = 1
        mock_progress.highest_practice_score = 100

        with patch("src.personalization.api.routes.progress.progress_service") as mock_service:
            mock_service.complete_chapter = AsyncMock(return_value=mock_progress)
            mock_service.award_xp_for_chapter = AsyncMock(return_value=25)
            mock_service.update_skill_level = AsyncMock()

            with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_ach_service:
                mock_ach = AsyncMock()
                mock_ach.check_achievements = AsyncMock(return_value=[])
                mock_ach_service.return_value = mock_ach

                await mark_chapter_complete(
                    chapter_id=1,
                    completion_data=completion_data,
                    current_user=test_user,
                    db=mock_db
                )

                # Verify achievement service was called with mastery_update event
                calls = mock_ach.check_achievements.call_args_list
                mastery_calls = [c for c in calls if c[0][1] == "mastery_update"]
                assert len(mastery_calls) > 0, "Expected mastery_update event check for 100% score"

    @pytest.mark.asyncio
    async def test_achievement_formatting(self, mock_db, test_user, progress_complete_data):
        """Test that achievements are properly formatted in response."""
        mock_progress = MagicMock()
        mock_progress.progress_id = uuid4()
        mock_progress.user_id = test_user.user_id
        mock_progress.chapter_id = 1
        mock_progress.completion_status = "completed"
        mock_progress.time_spent_seconds = 600
        mock_progress.mastery_score = 85
        mock_progress.last_accessed_at = datetime.now()
        mock_progress.practice_attempts = 1
        mock_progress.highest_practice_score = 85

        with patch("src.personalization.api.routes.progress.progress_service") as mock_service:
            mock_service.complete_chapter = AsyncMock(return_value=mock_progress)
            mock_service.award_xp_for_chapter = AsyncMock(return_value=25)
            mock_service.update_skill_level = AsyncMock()

            with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_ach_service:
                mock_ach = AsyncMock()
                mock_ach.check_achievements = AsyncMock(return_value=["ch_1_complete"])
                mock_ach_service.return_value = mock_ach

                result = await mark_chapter_complete(
                    chapter_id=1,
                    completion_data=progress_complete_data,
                    current_user=test_user,
                    db=mock_db
                )

                # Verify achievement format
                achievements = result["achievements_unlocked"]
                assert len(achievements) > 0
                achievement = achievements[0]
                assert "id" in achievement
                assert "title" in achievement
                assert "description" in achievement
                assert "icon" in achievement
                assert "points" in achievement
                assert "rarity" in achievement

    @pytest.mark.asyncio
    async def test_no_achievements_for_mastery_below_100(self, mock_db, test_user, progress_complete_data):
        """Test that mastery event is not triggered for scores below 100%."""
        from src.personalization.models.schemas import ProgressComplete

        # Progress data with 85% mastery (not 100%)
        completion_data = ProgressComplete(mastery_score=85, time_spent_seconds=600)

        mock_progress = MagicMock()
        mock_progress.progress_id = uuid4()
        mock_progress.user_id = test_user.user_id
        mock_progress.chapter_id = 1
        mock_progress.completion_status = "completed"
        mock_progress.time_spent_seconds = 600
        mock_progress.mastery_score = 85
        mock_progress.last_accessed_at = datetime.now()
        mock_progress.practice_attempts = 1
        mock_progress.highest_practice_score = 85

        with patch("src.personalization.api.routes.progress.progress_service") as mock_service:
            mock_service.complete_chapter = AsyncMock(return_value=mock_progress)
            mock_service.award_xp_for_chapter = AsyncMock(return_value=25)
            mock_service.update_skill_level = AsyncMock()

            with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_ach_service:
                mock_ach = AsyncMock()
                mock_ach.check_achievements = AsyncMock(return_value=[])
                mock_ach_service.return_value = mock_ach

                await mark_chapter_complete(
                    chapter_id=1,
                    completion_data=completion_data,
                    current_user=test_user,
                    db=mock_db
                )

                # Verify mastery event was NOT called (score < 100)
                calls = mock_ach.check_achievements.call_args_list
                mastery_calls = [c for c in calls if c[0][1] == "mastery_update"]
                assert len(mastery_calls) == 0, "Mastery event should not be triggered for scores below 100%"

    @pytest.mark.asyncio
    async def test_multiple_achievements_unlocked(self, mock_db, test_user):
        """Test that multiple achievements can be unlocked in one completion."""
        from src.personalization.models.schemas import ProgressComplete

        # 100% mastery for first chapter (should unlock multiple)
        completion_data = ProgressComplete(mastery_score=100, time_spent_seconds=600)

        mock_progress = MagicMock()
        mock_progress.progress_id = uuid4()
        mock_progress.user_id = test_user.user_id
        mock_progress.chapter_id = 1
        mock_progress.completion_status = "completed"
        mock_progress.time_spent_seconds = 600
        mock_progress.mastery_score = 100
        mock_progress.last_accessed_at = datetime.now()
        mock_progress.practice_attempts = 1
        mock_progress.highest_practice_score = 100

        with patch("src.personalization.api.routes.progress.progress_service") as mock_service:
            mock_service.complete_chapter = AsyncMock(return_value=mock_progress)
            mock_service.award_xp_for_chapter = AsyncMock(return_value=50)
            mock_service.update_skill_level = AsyncMock()

            with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_ach_service:
                mock_ach = AsyncMock()
                # Multiple achievements unlocked
                mock_ach.check_achievements = AsyncMock(
                    side_effect=[
                        ["ch_1_complete", "first_chapter"],  # chapter event
                        ["xp_100"],  # xp event
                        ["perfect_score"]  # mastery event
                    ]
                )
                mock_ach_service.return_value = mock_ach

                result = await mark_chapter_complete(
                    chapter_id=1,
                    completion_data=completion_data,
                    current_user=test_user,
                    db=mock_db
                )

                # Verify multiple achievements are returned
                achievements = result["achievements_unlocked"]
                assert len(achievements) == 4  # ch_1_complete, first_chapter, xp_100, perfect_score
                achievement_ids = [a["id"] for a in achievements]
                assert "ch_1_complete" in achievement_ids
                assert "first_chapter" in achievement_ids
                assert "xp_100" in achievement_ids
                assert "perfect_score" in achievement_ids
