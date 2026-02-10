"""Unit tests for Achievement Service."""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import User, Achievement
from src.personalization.services.achievement_service import (
    AchievementService,
    get_achievement_service,
    ACHIEVEMENTS_CONFIG
)


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
def achievement_service(mock_db):
    """Create achievement service with mock database."""
    return AchievementService(mock_db)


class TestChapterAchievements:
    """Tests for chapter completion achievements."""

    @pytest.mark.asyncio
    async def test_check_chapter_event_valid(self, achievement_service, mock_db, test_user):
        """Test checking chapter completion achievements with valid data."""
        # Setup mock to return no existing achievement
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        result = await achievement_service.check_achievements(
            test_user.user_id,
            "chapter_complete",
            {"chapter_id": 3}
        )

        assert "ch_3_complete" in result

    @pytest.mark.asyncio
    async def test_chapter_missing_data(self, achievement_service, test_user):
        """Test handling missing chapter_id."""
        result = await achievement_service.check_achievements(
            test_user.user_id,
            "chapter_complete",
            {}
        )
        assert result == []


class TestXPAchievements:
    """Tests for XP milestone achievements."""

    @pytest.mark.asyncio
    async def test_xp_100_milestone(self, achievement_service, mock_db, test_user):
        """Test 100 XP milestone achievement."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        result = await achievement_service.check_achievements(
            test_user.user_id,
            "xp_earned",
            {"total_xp": 100}
        )
        assert "xp_100" in result

    @pytest.mark.asyncio
    async def test_xp_500_milestone(self, achievement_service, mock_db, test_user):
        """Test 500 XP milestone achievement."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        result = await achievement_service.check_achievements(
            test_user.user_id,
            "xp_earned",
            {"total_xp": 500}
        )
        assert "xp_500" in result
        assert "xp_100" in result

    @pytest.mark.asyncio
    async def test_xp_multiple_milestones(self, achievement_service, mock_db, test_user):
        """Test multiple XP milestones crossed at once."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        result = await achievement_service.check_achievements(
            test_user.user_id,
            "xp_earned",
            {"total_xp": 5000}
        )
        assert "xp_100" in result
        assert "xp_500" in result
        assert "xp_1000" in result
        assert "xp_5000" in result

    @pytest.mark.asyncio
    async def test_xp_below_threshold(self, achievement_service, test_user):
        """Test that XP below threshold is not awarded."""
        result = await achievement_service.check_achievements(
            test_user.user_id,
            "xp_earned",
            {"total_xp": 50}
        )
        assert "xp_100" not in result


class TestModuleAchievements:
    """Tests for module completion achievements."""

    @pytest.mark.asyncio
    async def test_module_completion(self, achievement_service, mock_db, test_user):
        """Test module completion achievement."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        result = await achievement_service.check_achievements(
            test_user.user_id,
            "module_complete",
            {"module_id": 1}
        )
        assert "module_1_complete" in result


class TestStreakAchievements:
    """Tests for learning streak achievements."""

    @pytest.mark.asyncio
    async def test_7_day_streak(self, achievement_service, mock_db, test_user):
        """Test 7-day streak achievement."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        result = await achievement_service.check_achievements(
            test_user.user_id,
            "streak_update",
            {"current_streak": 7}
        )
        assert "streak_7" in result

    @pytest.mark.asyncio
    async def test_30_day_streak(self, achievement_service, mock_db, test_user):
        """Test 30-day streak achievement."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        result = await achievement_service.check_achievements(
            test_user.user_id,
            "streak_update",
            {"current_streak": 30}
        )
        assert "streak_30" in result
        assert "streak_7" in result

    @pytest.mark.asyncio
    async def test_streak_below_threshold(self, achievement_service, test_user):
        """Test that streak below threshold is not awarded."""
        result = await achievement_service.check_achievements(
            test_user.user_id,
            "streak_update",
            {"current_streak": 3}
        )
        assert "streak_7" not in result


class TestMasteryAchievements:
    """Tests for mastery (100% score) achievements."""

    @pytest.mark.asyncio
    async def test_perfect_mastery(self, achievement_service, mock_db, test_user):
        """Test 100% mastery achievement."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        result = await achievement_service.check_achievements(
            test_user.user_id,
            "mastery_update",
            {"mastery_score": 100, "chapter_id": 1}
        )
        assert "perfect_score" in result

    @pytest.mark.asyncio
    async def test_mastery_below_100(self, achievement_service, test_user):
        """Test that mastery below 100% is not awarded."""
        result = await achievement_service.check_achievements(
            test_user.user_id,
            "mastery_update",
            {"mastery_score": 99, "chapter_id": 1}
        )
        assert "perfect_score" not in result


class TestGetUserAchievements:
    """Tests for retrieving user achievements."""

    @pytest.mark.asyncio
    async def test_get_empty_achievements(self, achievement_service, mock_db, test_user):
        """Test getting achievements for user with none."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await achievement_service.get_user_achievements(test_user.user_id)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_achievements_format(self, achievement_service, mock_db, test_user):
        """Test that achievements have correct format."""
        mock_ach = MagicMock()
        mock_ach.achievement_type = "ch_1_complete"
        mock_ach.display_info_json = {
            "title": "Chapter 1 Master",
            "description": "Completed Chapter 1",
            "icon": "📚",
            "points": 10,
            "rarity": "common"
        }
        mock_ach.earned_date = datetime.now()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_ach]
        mock_db.execute.return_value = mock_result

        result = await achievement_service.get_user_achievements(test_user.user_id)

        assert len(result) == 1
        assert result[0]["id"] == "ch_1_complete"
        assert result[0]["title"] == "Chapter 1 Master"
        assert result[0]["points"] == 10


class TestGetAchievementStats:
    """Tests for achievement statistics."""

    @pytest.mark.asyncio
    async def test_empty_stats(self, achievement_service, mock_db, test_user):
        """Test stats for user with no achievements."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        stats = await achievement_service.get_achievement_stats(test_user.user_id)

        assert stats["total_achievements"] == 0
        assert stats["total_points"] == 0
        assert stats["recent"] == []

    @pytest.mark.asyncio
    async def test_stats_with_achievements(self, achievement_service, mock_db, test_user):
        """Test stats calculation with achievements."""
        mock_ach1 = MagicMock()
        mock_ach1.achievement_type = "ch_1_complete"
        mock_ach1.display_info_json = {
            "title": "Chapter 1 Master",
            "description": "Completed Chapter 1",
            "icon": "📚",
            "points": 10,
            "rarity": "common"
        }
        mock_ach1.earned_date = datetime.now()

        mock_ach2 = MagicMock()
        mock_ach2.achievement_type = "xp_100"
        mock_ach2.display_info_json = {
            "title": "Getting Started",
            "description": "Earned 100 XP",
            "icon": "⭐",
            "points": 0,
            "rarity": "common"
        }
        mock_ach2.earned_date = datetime.now()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_ach1, mock_ach2]
        mock_db.execute.return_value = mock_result

        stats = await achievement_service.get_achievement_stats(test_user.user_id)

        assert stats["total_achievements"] == 2
        assert stats["total_points"] == 10


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_invalid_user_id(self, achievement_service):
        """Test handling of invalid user ID."""
        result = await achievement_service.check_achievements(
            None,
            "chapter_complete",
            {"chapter_id": 1}
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_unknown_event_type(self, achievement_service, test_user):
        """Test handling of unknown event type."""
        result = await achievement_service.check_achievements(
            test_user.user_id,
            "unknown_event",
            {}
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_missing_event_data(self, achievement_service, test_user):
        """Test handling of missing event data."""
        result = await achievement_service.check_achievements(
            test_user.user_id,
            "chapter_complete",
            {}
        )
        assert result == []


class TestFactoryFunction:
    """Tests for factory function."""

    @pytest.mark.asyncio
    async def test_get_achievement_service(self, mock_db):
        """Test factory function creates service correctly."""
        service = await get_achievement_service(mock_db)

        assert isinstance(service, AchievementService)
        assert service.db is mock_db


class TestAchievementsConfig:
    """Tests for achievements configuration loading."""

    def test_achievements_loaded(self):
        """Test that achievements configuration was loaded."""
        assert len(ACHIEVEMENTS_CONFIG) > 0

    def test_achievement_structure(self):
        """Test that achievements have required structure."""
        required_fields = ["id", "title", "description", "icon", "points", "rarity"]

        for ach_id, config in ACHIEVEMENTS_CONFIG.items():
            for field in required_fields:
                assert field in config, f"Missing field {field} in achievement {ach_id}"

    def test_chapter_achievements_exist(self):
        """Test that chapter achievements exist."""
        for i in range(1, 23):
            assert f"ch_{i}_complete" in ACHIEVEMENTS_CONFIG

    def test_module_achievements_exist(self):
        """Test that module achievements exist."""
        for i in range(1, 5):
            assert f"module_{i}_complete" in ACHIEVEMENTS_CONFIG

    def test_xp_milestone_achievements_exist(self):
        """Test that XP milestone achievements exist."""
        for milestone in ["xp_100", "xp_500", "xp_1000", "xp_5000"]:
            assert milestone in ACHIEVEMENTS_CONFIG

    def test_streak_achievements_exist(self):
        """Test that streak achievements exist."""
        assert "streak_7" in ACHIEVEMENTS_CONFIG
        assert "streak_30" in ACHIEVEMENTS_CONFIG

    def test_first_chapter_achievement(self):
        """Test first chapter achievement exists."""
        assert "first_chapter" in ACHIEVEMENTS_CONFIG

    def test_perfect_mastery_achievement(self):
        """Test perfect mastery achievement exists."""
        assert "perfect_score" in ACHIEVEMENTS_CONFIG
