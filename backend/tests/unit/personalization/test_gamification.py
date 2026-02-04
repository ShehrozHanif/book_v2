"""Unit tests for gamification services."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from src.personalization.services.achievement_service import AchievementService
from src.personalization.services.practice_service import PracticeService
from src.personalization.services.statistics_service import StatisticsService
from src.personalization.models.db_models import User, Progress, Achievement, PracticeAttempt


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def test_user():
    """Create a test user."""
    user = User()
    user.user_id = uuid4()
    user.username = "test_user"
    user.email = "test@example.com"
    return user


class TestAchievementService:
    """Tests for AchievementService."""

    @pytest.mark.asyncio
    async def test_unlock_achievement_success(self, mock_db, test_user):
        """Test successfully unlocking an achievement."""
        service = AchievementService(mock_db)

        with patch('src.personalization.services.achievement_service.get_user_by_id'):
            # Mock the achievement not existing
            mock_db.execute.return_value.scalar_one_or_none.return_value = None

            achievement = await service.unlock_achievement(test_user.user_id, "century_club")

            # Verify add and commit were called
            assert mock_db.add.called
            assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_unlock_achievement_already_earned(self, mock_db, test_user):
        """Test unlocking an already earned achievement."""
        service = AchievementService(mock_db)

        # Mock the achievement as already existing
        existing = Achievement()
        mock_db.execute.return_value.scalar_one_or_none.return_value = existing

        achievement = await service.unlock_achievement(test_user.user_id, "century_club")

        assert achievement is None

    @pytest.mark.asyncio
    async def test_unlock_achievement_invalid_type(self, mock_db, test_user):
        """Test unlocking an invalid achievement type."""
        service = AchievementService(mock_db)

        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        achievement = await service.unlock_achievement(test_user.user_id, "invalid_achievement")

        assert achievement is None

    @pytest.mark.asyncio
    async def test_get_user_achievements_empty(self, mock_db, test_user):
        """Test getting achievements when user has none."""
        service = AchievementService(mock_db)

        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        achievements = await service.get_user_achievements(test_user.user_id)

        assert achievements["earned_count"] == 0
        assert achievements["locked_count"] > 0

    def test_achievements_config_has_required_fields(self):
        """Test that all achievements have required configuration fields."""
        from src.personalization.services.achievement_service import ACHIEVEMENTS_CONFIG

        for ach_type, config in ACHIEVEMENTS_CONFIG.items():
            assert "title" in config
            assert "description" in config
            assert "icon" in config
            assert "points" in config
            assert "category" in config
            assert config["points"] > 0


class TestPracticeService:
    """Tests for PracticeService."""

    def test_calculate_score_all_correct(self):
        """Test score calculation with all correct answers."""
        service = PracticeService(AsyncMock())

        questions = [
            {
                "id": "q1",
                "options": [
                    {"letter": "A", "correct": True},
                    {"letter": "B", "correct": False}
                ]
            },
            {
                "id": "q2",
                "options": [
                    {"letter": "A", "correct": False},
                    {"letter": "B", "correct": True}
                ]
            }
        ]

        answers = {"q1": "A", "q2": "B"}

        score = service.calculate_score(questions, answers)
        assert score == 100

    def test_calculate_score_all_wrong(self):
        """Test score calculation with all wrong answers."""
        service = PracticeService(AsyncMock())

        questions = [
            {
                "id": "q1",
                "options": [
                    {"letter": "A", "correct": True},
                    {"letter": "B", "correct": False}
                ]
            },
            {
                "id": "q2",
                "options": [
                    {"letter": "A", "correct": False},
                    {"letter": "B", "correct": True}
                ]
            }
        ]

        answers = {"q1": "B", "q2": "A"}

        score = service.calculate_score(questions, answers)
        assert score == 0

    def test_calculate_score_partial(self):
        """Test score calculation with partial correct."""
        service = PracticeService(AsyncMock())

        questions = [
            {"id": f"q{i}", "options": [{"letter": "A", "correct": True}]}
            for i in range(5)
        ]

        answers = {"q0": "A", "q1": "A", "q3": "A"}  # 3 out of 5

        score = service.calculate_score(questions, answers)
        assert 40 <= score <= 60  # Accounts for missing answers

    def test_calculate_score_empty(self):
        """Test score calculation with no questions."""
        service = PracticeService(AsyncMock())

        score = service.calculate_score([], {})
        assert score == 0

    async def test_get_practice_questions_default(self, mock_db):
        """Test getting default practice questions."""
        service = PracticeService(mock_db)

        questions = await service.get_practice_questions(1, limit=5)

        assert isinstance(questions, list)
        assert len(questions) <= 5
        for q in questions:
            assert "id" in q
            assert "question" in q
            assert "options" in q
            assert "difficulty" in q


class TestStatisticsService:
    """Tests for StatisticsService."""

    @pytest.mark.asyncio
    async def test_get_time_heatmap_empty(self, mock_db):
        """Test getting time heatmap with no progress."""
        service = StatisticsService(mock_db)

        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        heatmap = await service.get_time_heatmap(uuid4())

        assert heatmap == {}

    @pytest.mark.asyncio
    async def test_get_mastery_per_chapter_empty(self, mock_db):
        """Test getting mastery with no progress."""
        service = StatisticsService(mock_db)

        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        mastery = await service.get_mastery_per_chapter(uuid4())

        assert mastery == {}

    @pytest.mark.asyncio
    async def test_get_learning_curve_empty(self, mock_db):
        """Test getting learning curve with no progress."""
        service = StatisticsService(mock_db)

        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        curve = await service.get_learning_curve(uuid4())

        assert curve == []

    @pytest.mark.asyncio
    async def test_get_overall_progress_empty(self, mock_db):
        """Test getting overall progress with no chapters."""
        service = StatisticsService(mock_db)

        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        progress = await service.get_overall_progress(uuid4())

        assert progress["total_chapters"] == 22
        assert progress["chapters_completed"] == 0
        assert progress["completion_percentage"] == 0
        assert progress["avg_mastery"] == 0

    @pytest.mark.asyncio
    async def test_get_recommended_focus_areas_empty(self, mock_db):
        """Test getting focus recommendations with no progress."""
        service = StatisticsService(mock_db)

        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        focus = await service.get_recommended_focus_areas(uuid4())

        assert focus == []
