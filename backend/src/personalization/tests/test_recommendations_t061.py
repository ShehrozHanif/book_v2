"""Unit tests for Recommended Focus Areas Algorithm (T061)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.personalization.models.db_models import Progress
from src.personalization.services.statistics_service import StatisticsService


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock()


@pytest.fixture
def weak_progress_records():
    """Create sample weak progress records."""
    return [
        MagicMock(
            chapter_id=1,
            mastery_score=45,
            completion_status="completed",
            time_spent_seconds=1800,
            practice_attempts=2,
            highest_practice_score=45
        ),
        MagicMock(
            chapter_id=2,
            mastery_score=35,
            completion_status="completed",
            time_spent_seconds=2400,
            practice_attempts=3,
            highest_practice_score=35
        ),
        MagicMock(
            chapter_id=3,
            mastery_score=55,
            completion_status="completed",
            time_spent_seconds=1500,
            practice_attempts=2,
            highest_practice_score=55
        ),
        MagicMock(
            chapter_id=5,
            mastery_score=25,
            completion_status="in_progress",
            time_spent_seconds=3000,
            practice_attempts=5,
            highest_practice_score=25
        ),
    ]


class TestAdvancedRecommendations:
    """Tests for T061 advanced recommendations algorithm."""

    @pytest.mark.asyncio
    async def test_get_advanced_recommendations_success(self, mock_db, weak_progress_records):
        """Test successful recommendation generation."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = weak_progress_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.get_advanced_recommendations(user_id)

        assert "weak_chapters" in result
        assert "related_chapters" in result
        assert "practice_suggestions" in result
        assert "priority_order" in result
        assert "estimated_improvement_time" in result
        assert result["total_weak_chapters"] > 0

    @pytest.mark.asyncio
    async def test_recommendations_identifies_weak_chapters(self, mock_db, weak_progress_records):
        """Test that weak chapters (< 60% mastery) are identified."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = weak_progress_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.get_advanced_recommendations(user_id)

        weak_ids = [ch["chapter_id"] for ch in result["weak_chapters"]]
        # Should include chapters 1, 2, 3, 5 (all below 60%)
        assert len(weak_ids) > 0
        for chapter_id in weak_ids:
            assert chapter_id in [1, 2, 3, 5]

    @pytest.mark.asyncio
    async def test_recommendations_empty_progress(self, mock_db):
        """Test recommendations with no progress."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.get_advanced_recommendations(user_id)

        assert result["weak_chapters"] == []
        assert "total_weak_chapters" in result

    @pytest.mark.asyncio
    async def test_recommendations_all_good_performance(self, mock_db):
        """Test recommendations when all chapters are above threshold."""
        good_records = [
            MagicMock(chapter_id=i, mastery_score=75 + i,
                     time_spent_seconds=1500, practice_attempts=2)
            for i in range(5)
        ]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = good_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.get_advanced_recommendations(uuid4())

        assert result["weak_chapters"] == []
        assert "total_weak_chapters" in result


class TestIdentifyRelatedChapters:
    """Tests for related chapter identification."""

    def test_identify_related_chapters_basic(self, mock_db):
        """Test basic related chapter identification."""
        service = StatisticsService(mock_db)

        # Chapter 3 is weak - should suggest 1, 2
        related = service._identify_related_chapters([3])

        chapter_ids = [ch["chapter_id"] for ch in related]
        assert 1 in chapter_ids
        assert 2 in chapter_ids

    def test_identify_related_chapters_module_dependencies(self, mock_db):
        """Test module prerequisite identification."""
        service = StatisticsService(mock_db)

        # Chapter 8 in Module 2 - should suggest Module 1 chapters
        related = service._identify_related_chapters([8])

        relations = [(ch["chapter_id"], ch["relation_type"]) for ch in related]
        # Should have prerequisites (1-7) and foundation (Module 1)
        chapter_ids = [ch["chapter_id"] for ch in related]
        assert len(chapter_ids) > 0

    def test_identify_related_chapters_no_duplicates(self, mock_db):
        """Test that related chapters don't have duplicates."""
        service = StatisticsService(mock_db)

        related = service._identify_related_chapters([1, 2, 3])

        chapter_ids = [ch["chapter_id"] for ch in related]
        assert len(chapter_ids) == len(set(chapter_ids))


class TestGeneratePracticeSuggestions:
    """Tests for practice suggestion generation."""

    def test_generate_practice_suggestions_format(self, mock_db, weak_progress_records):
        """Test that practice suggestions have correct format."""
        service = StatisticsService(mock_db)

        suggestions = service._generate_practice_suggestions(weak_progress_records)

        for suggestion in suggestions:
            assert "chapter_id" in suggestion
            assert "current_score" in suggestion
            assert "target_score" in suggestion
            assert "suggested_attempts" in suggestion
            assert "rationale" in suggestion
            assert "difficulty_level" in suggestion
            assert "focus_areas" in suggestion

    def test_generate_practice_suggestions_difficulty_levels(self, mock_db):
        """Test that difficulty levels are appropriate."""
        easy_record = [MagicMock(chapter_id=1, mastery_score=25)]
        medium_records = [MagicMock(chapter_id=2, mastery_score=45)]
        hard_records = [MagicMock(chapter_id=3, mastery_score=55)]

        service = StatisticsService(mock_db)

        easy = service._generate_practice_suggestions(easy_record)
        medium = service._generate_practice_suggestions(medium_records)
        hard = service._generate_practice_suggestions(hard_records)

        assert easy[0]["difficulty_level"] == "easy"
        assert medium[0]["difficulty_level"] == "medium"
        assert hard[0]["difficulty_level"] == "medium"

    def test_generate_practice_suggestions_attempts_needed(self, mock_db):
        """Test that suggested attempts are proportional to gap."""
        low_score = [MagicMock(chapter_id=1, mastery_score=10)]
        high_score = [MagicMock(chapter_id=2, mastery_score=50)]

        service = StatisticsService(mock_db)

        low = service._generate_practice_suggestions(low_score)
        high = service._generate_practice_suggestions(high_score)

        # Gap of 50 points vs gap of 10 points
        # low: max(2, 50/15) = max(2, 3) = 3
        # high: max(2, 10/15) = max(2, 0) = 2
        assert low[0]["suggested_attempts"] > high[0]["suggested_attempts"]


class TestCalculatePriorityOrder:
    """Tests for priority order calculation."""

    def test_calculate_priority_order_format(self, mock_db, weak_progress_records):
        """Test that priority order has correct format."""
        service = StatisticsService(mock_db)

        priority = service._calculate_priority_order(weak_progress_records)

        for item in priority:
            assert "priority" in item
            assert "chapter_id" in item
            assert "current_mastery" in item
            assert "time_invested_hours" in item
            assert "efficiency_ratio" in item

    def test_calculate_priority_order_sorted(self, mock_db, weak_progress_records):
        """Test that chapters are properly ordered."""
        service = StatisticsService(mock_db)

        priority = service._calculate_priority_order(weak_progress_records)

        # Should be sorted by priority (1, 2, 3, ...)
        for i, item in enumerate(priority, 1):
            assert item["priority"] == i

    def test_calculate_priority_order_efficiency_ratio(self, mock_db):
        """Test that efficiency ratio is calculated correctly."""
        service = StatisticsService(mock_db)

        record = MagicMock(
            chapter_id=1,
            mastery_score=50,
            time_spent_seconds=3600  # 1 hour
        )
        priority = service._calculate_priority_order([record])

        # efficiency = 3600 / 50 = 72
        assert priority[0]["efficiency_ratio"] == 72.0


class TestEstimateImprovementTime:
    """Tests for improvement time estimation."""

    def test_estimate_improvement_time_format(self, mock_db, weak_progress_records):
        """Test that time estimates have correct format."""
        service = StatisticsService(mock_db)

        estimates = service._estimate_improvement_time(weak_progress_records)

        for chapter_id, estimate in estimates.items():
            assert "current_mastery" in estimate
            assert "target_mastery" in estimate
            assert "points_to_improve" in estimate
            assert "estimated_hours" in estimate
            assert "estimated_days" in estimate

    def test_estimate_improvement_time_calculations(self, mock_db):
        """Test that improvement time calculations are correct."""
        record = MagicMock(chapter_id=1, mastery_score=40)

        service = StatisticsService(mock_db)
        estimates = service._estimate_improvement_time([record])

        # Gap = 60 - 40 = 20, estimated hours = 20 / 5 = 4
        assert estimates[1]["points_to_improve"] == 20
        assert estimates[1]["estimated_hours"] == 4.0

    def test_estimate_improvement_time_minimum_hours(self, mock_db):
        """Test that minimum improvement time is respected."""
        record = MagicMock(chapter_id=1, mastery_score=59)

        service = StatisticsService(mock_db)
        estimates = service._estimate_improvement_time([record])

        # Gap = 1 point, but minimum is 0.5 hours
        assert estimates[1]["estimated_hours"] >= 0.5


class TestIdentifyFocusAreas:
    """Tests for focus area identification."""

    def test_identify_focus_areas_low_mastery(self, mock_db):
        """Test focus areas for very low mastery."""
        service = StatisticsService(mock_db)

        areas = service._identify_focus_areas(20)

        assert "Fundamental concepts" in areas or "Basic definitions" in areas

    def test_identify_focus_areas_medium_mastery(self, mock_db):
        """Test focus areas for medium mastery."""
        service = StatisticsService(mock_db)

        areas = service._identify_focus_areas(45)

        assert "Core principles" in areas or "Application examples" in areas

    def test_identify_focus_areas_high_mastery(self, mock_db):
        """Test focus areas for high mastery."""
        service = StatisticsService(mock_db)

        areas = service._identify_focus_areas(58)

        assert "Advanced topics" in areas or "Edge cases" in areas


class TestRecommendationsIntegration:
    """Integration tests for full recommendation flow."""

    @pytest.mark.asyncio
    async def test_full_recommendation_flow(self, mock_db):
        """Test complete recommendation generation flow."""
        user_id = uuid4()

        # Create mixed performance records
        mixed_records = [
            MagicMock(chapter_id=1, mastery_score=30, time_spent_seconds=3000, practice_attempts=5),
            MagicMock(chapter_id=2, mastery_score=45, time_spent_seconds=1500, practice_attempts=2),
            MagicMock(chapter_id=3, mastery_score=55, time_spent_seconds=1200, practice_attempts=2),
            MagicMock(chapter_id=4, mastery_score=75, time_spent_seconds=1000, practice_attempts=1),
            MagicMock(chapter_id=5, mastery_score=20, time_spent_seconds=2500, practice_attempts=4),
        ]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mixed_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.get_advanced_recommendations(user_id)

        # Verify structure
        assert len(result["weak_chapters"]) > 0
        assert len(result["practice_suggestions"]) > 0
        assert len(result["priority_order"]) > 0
        assert len(result["estimated_improvement_time"]) > 0

        # Verify weak chapters are actually weak (< 60%)
        for chapter in result["weak_chapters"]:
            assert chapter["current_mastery"] < 60

        # Verify priority starts at 1
        assert result["priority_order"][0]["priority"] == 1

    @pytest.mark.asyncio
    async def test_recommendations_with_custom_threshold(self, mock_db):
        """Test recommendations with custom mastery threshold."""
        user_id = uuid4()

        records = [
            MagicMock(chapter_id=1, mastery_score=65, time_spent_seconds=1500, practice_attempts=2),
            MagicMock(chapter_id=2, mastery_score=75, time_spent_seconds=1500, practice_attempts=2),
        ]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)

        # With default threshold (60%), no weak chapters
        result_default = await service.get_advanced_recommendations(user_id, mastery_threshold=60)
        assert len(result_default["weak_chapters"]) == 0

        # Reset mock for second call
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        # With threshold 70%, chapter 1 is weak
        result_custom = await service.get_advanced_recommendations(user_id, mastery_threshold=70)
        assert len(result_custom["weak_chapters"]) == 1
