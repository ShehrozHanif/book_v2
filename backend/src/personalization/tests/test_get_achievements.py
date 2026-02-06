"""Integration tests for Get Achievements endpoint (T053)."""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import User
from src.personalization.api.routes.progress import get_user_achievements


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock(spec=AsyncSession)


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


class TestGetAchievementsEndpoint:
    """Tests for GET /achievements endpoint (T053)."""

    @pytest.mark.asyncio
    async def test_get_achievements_success(self, mock_db, test_user):
        """Test successfully retrieving achievements."""
        with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_service:
            mock_ach = AsyncMock()

            # Mock achievements
            achievements = [
                {
                    "id": "ch_1_complete",
                    "title": "Chapter 1 Master",
                    "description": "Completed Chapter 1",
                    "icon": "📚",
                    "points": 10,
                    "rarity": "common",
                    "earned_date": "2026-02-06T10:30:00"
                },
                {
                    "id": "xp_100",
                    "title": "Getting Started",
                    "description": "Earned 100 XP",
                    "icon": "⭐",
                    "points": 0,
                    "rarity": "common",
                    "earned_date": "2026-02-06T11:00:00"
                }
            ]

            # Mock stats
            stats = {
                "total_achievements": 2,
                "total_points": 10,
                "recent": achievements[:1]
            }

            mock_ach.get_user_achievements = AsyncMock(return_value=achievements)
            mock_ach.get_achievement_stats = AsyncMock(return_value=stats)
            mock_service.return_value = mock_ach

            result = await get_user_achievements(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # Verify response structure
            assert "achievements" in result
            assert "stats" in result
            assert len(result["achievements"]) == 2
            assert result["stats"]["total_achievements"] == 2
            assert result["stats"]["total_points"] == 10

    @pytest.mark.asyncio
    async def test_get_achievements_empty(self, mock_db, test_user):
        """Test retrieving achievements when user has none."""
        with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_service:
            mock_ach = AsyncMock()
            mock_ach.get_user_achievements = AsyncMock(return_value=[])
            mock_ach.get_achievement_stats = AsyncMock(return_value={
                "total_achievements": 0,
                "total_points": 0,
                "recent": []
            })
            mock_service.return_value = mock_ach

            result = await get_user_achievements(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            assert result["stats"]["total_achievements"] == 0
            assert result["stats"]["total_points"] == 0
            assert len(result["achievements"]) == 0

    @pytest.mark.asyncio
    async def test_get_achievements_by_type_chapter(self, mock_db, test_user):
        """Test achievement categorization by type (chapter)."""
        with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_service:
            mock_ach = AsyncMock()

            achievements = [
                {
                    "id": "ch_1_complete",
                    "title": "Chapter 1 Master",
                    "description": "Completed Chapter 1",
                    "icon": "📚",
                    "points": 10,
                    "rarity": "common",
                    "earned_date": "2026-02-06T10:30:00"
                },
                {
                    "id": "ch_2_complete",
                    "title": "Chapter 2 Master",
                    "description": "Completed Chapter 2",
                    "icon": "🔢",
                    "points": 10,
                    "rarity": "common",
                    "earned_date": "2026-02-06T10:40:00"
                }
            ]

            stats = {
                "total_achievements": 2,
                "total_points": 20,
                "recent": achievements[:1]
            }

            mock_ach.get_user_achievements = AsyncMock(return_value=achievements)
            mock_ach.get_achievement_stats = AsyncMock(return_value=stats)
            mock_service.return_value = mock_ach

            result = await get_user_achievements(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # Verify by_type categorization
            by_type = result["stats"]["by_type"]
            assert "chapter_complete" in by_type
            assert by_type["chapter_complete"] == 2

    @pytest.mark.asyncio
    async def test_get_achievements_by_type_mixed(self, mock_db, test_user):
        """Test achievement categorization by multiple types."""
        with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_service:
            mock_ach = AsyncMock()

            achievements = [
                {
                    "id": "ch_1_complete",
                    "title": "Chapter 1 Master",
                    "points": 10,
                    "rarity": "common",
                    "earned_date": "2026-02-06T10:30:00"
                },
                {
                    "id": "xp_100",
                    "title": "Getting Started",
                    "points": 0,
                    "rarity": "common",
                    "earned_date": "2026-02-06T11:00:00"
                },
                {
                    "id": "module_1_complete",
                    "title": "Module 1 Champion",
                    "points": 50,
                    "rarity": "rare",
                    "earned_date": "2026-02-06T11:30:00"
                },
                {
                    "id": "streak_7",
                    "title": "Week Warrior",
                    "points": 25,
                    "rarity": "uncommon",
                    "earned_date": "2026-02-06T12:00:00"
                }
            ]

            stats = {
                "total_achievements": 4,
                "total_points": 85,
                "recent": achievements[:1]
            }

            mock_ach.get_user_achievements = AsyncMock(return_value=achievements)
            mock_ach.get_achievement_stats = AsyncMock(return_value=stats)
            mock_service.return_value = mock_ach

            result = await get_user_achievements(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # Verify by_type has all categories
            by_type = result["stats"]["by_type"]
            assert "chapter_complete" in by_type
            assert "xp_milestone" in by_type
            assert "module_complete" in by_type
            assert "streak" in by_type
            assert by_type["chapter_complete"] == 1
            assert by_type["xp_milestone"] == 1
            assert by_type["module_complete"] == 1
            assert by_type["streak"] == 1

    @pytest.mark.asyncio
    async def test_get_achievements_forbidden(self, mock_db, test_user):
        """Test that users cannot access other users' achievements."""
        other_user = User(
            user_id=uuid4(),
            username="otheruser",
            email="other@example.com",
            password_hash="hashed_password",
            skill_level=50
        )

        from fastapi import HTTPException

        try:
            await get_user_achievements(
                user_id=other_user.user_id,
                current_user=test_user,
                db=mock_db
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 403
            assert "Cannot access other users' achievements" in str(e.detail)

    @pytest.mark.asyncio
    async def test_get_achievements_response_format(self, mock_db, test_user):
        """Test that achievement response has correct format."""
        with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_service:
            mock_ach = AsyncMock()

            achievements = [
                {
                    "id": "ch_1_complete",
                    "title": "Chapter 1 Master",
                    "description": "Completed Chapter 1",
                    "icon": "📚",
                    "points": 10,
                    "rarity": "common",
                    "earned_date": "2026-02-06T10:30:00"
                }
            ]

            stats = {
                "total_achievements": 1,
                "total_points": 10,
                "recent": achievements
            }

            mock_ach.get_user_achievements = AsyncMock(return_value=achievements)
            mock_ach.get_achievement_stats = AsyncMock(return_value=stats)
            mock_service.return_value = mock_ach

            result = await get_user_achievements(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # Verify achievement has all required fields
            achievement = result["achievements"][0]
            assert "id" in achievement
            assert "title" in achievement
            assert "description" in achievement
            assert "icon" in achievement
            assert "points" in achievement
            assert "rarity" in achievement
            assert "earned_date" in achievement

    @pytest.mark.asyncio
    async def test_get_achievements_stats_structure(self, mock_db, test_user):
        """Test that stats have correct structure."""
        with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_service:
            mock_ach = AsyncMock()

            achievements = [
                {
                    "id": "ch_1_complete",
                    "title": "Chapter 1 Master",
                    "points": 10,
                    "rarity": "common",
                    "earned_date": "2026-02-06T10:30:00"
                },
                {
                    "id": "ch_2_complete",
                    "title": "Chapter 2 Master",
                    "points": 10,
                    "rarity": "common",
                    "earned_date": "2026-02-06T10:40:00"
                }
            ]

            stats = {
                "total_achievements": 2,
                "total_points": 20,
                "recent": achievements[:1]
            }

            mock_ach.get_user_achievements = AsyncMock(return_value=achievements)
            mock_ach.get_achievement_stats = AsyncMock(return_value=stats)
            mock_service.return_value = mock_ach

            result = await get_user_achievements(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # Verify stats structure
            stats_obj = result["stats"]
            assert "total_achievements" in stats_obj
            assert "total_points" in stats_obj
            assert "by_type" in stats_obj
            assert "recent" in stats_obj
            assert isinstance(stats_obj["by_type"], dict)
            assert isinstance(stats_obj["recent"], list)

    @pytest.mark.asyncio
    async def test_get_achievements_recent_list(self, mock_db, test_user):
        """Test that recent achievements list contains latest achievements."""
        with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_service:
            mock_ach = AsyncMock()

            achievements = [
                {
                    "id": "ch_1_complete",
                    "title": "Chapter 1 Master",
                    "points": 10,
                    "rarity": "common",
                    "earned_date": "2026-02-06T10:30:00"
                },
                {
                    "id": "ch_2_complete",
                    "title": "Chapter 2 Master",
                    "points": 10,
                    "rarity": "common",
                    "earned_date": "2026-02-06T11:00:00"
                },
                {
                    "id": "xp_100",
                    "title": "Getting Started",
                    "points": 0,
                    "rarity": "common",
                    "earned_date": "2026-02-06T11:30:00"
                }
            ]

            stats = {
                "total_achievements": 3,
                "total_points": 20,
                "recent": achievements[:2]  # Last 2
            }

            mock_ach.get_user_achievements = AsyncMock(return_value=achievements)
            mock_ach.get_achievement_stats = AsyncMock(return_value=stats)
            mock_service.return_value = mock_ach

            result = await get_user_achievements(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # Verify recent list
            recent = result["stats"]["recent"]
            assert len(recent) <= 5  # Reasonable limit
            assert len(recent) == 2

    @pytest.mark.asyncio
    async def test_get_achievements_mastery_type(self, mock_db, test_user):
        """Test achievement categorization for mastery (perfect_score)."""
        with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_service:
            mock_ach = AsyncMock()

            achievements = [
                {
                    "id": "perfect_score",
                    "title": "Perfect Mastery",
                    "description": "Achieved 100% mastery",
                    "points": 50,
                    "rarity": "epic",
                    "earned_date": "2026-02-06T10:30:00"
                }
            ]

            stats = {
                "total_achievements": 1,
                "total_points": 50,
                "recent": achievements
            }

            mock_ach.get_user_achievements = AsyncMock(return_value=achievements)
            mock_ach.get_achievement_stats = AsyncMock(return_value=stats)
            mock_service.return_value = mock_ach

            result = await get_user_achievements(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # Verify mastery type
            by_type = result["stats"]["by_type"]
            assert "mastery" in by_type
            assert by_type["mastery"] == 1

    @pytest.mark.asyncio
    async def test_get_achievements_total_points_calculation(self, mock_db, test_user):
        """Test that total points are calculated correctly."""
        with patch("src.personalization.api.routes.progress.get_achievement_service") as mock_service:
            mock_ach = AsyncMock()

            achievements = [
                {"id": "ch_1_complete", "points": 10, "rarity": "common", "earned_date": "2026-02-06T10:30:00"},
                {"id": "ch_2_complete", "points": 10, "rarity": "common", "earned_date": "2026-02-06T10:40:00"},
                {"id": "module_1_complete", "points": 50, "rarity": "rare", "earned_date": "2026-02-06T11:00:00"},
                {"id": "xp_100", "points": 0, "rarity": "common", "earned_date": "2026-02-06T11:30:00"}
            ]

            stats = {
                "total_achievements": 4,
                "total_points": 70,  # 10 + 10 + 50 + 0
                "recent": achievements[:1]
            }

            mock_ach.get_user_achievements = AsyncMock(return_value=achievements)
            mock_ach.get_achievement_stats = AsyncMock(return_value=stats)
            mock_service.return_value = mock_ach

            result = await get_user_achievements(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # Verify total points
            assert result["stats"]["total_points"] == 70
