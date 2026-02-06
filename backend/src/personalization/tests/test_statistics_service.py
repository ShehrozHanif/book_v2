"""Unit tests for Statistics Service - Learning Curve Calculations (T060)."""

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
def mock_progress_records():
    """Create sample progress records."""
    return [
        MagicMock(
            chapter_id=1,
            mastery_score=40,
            completion_status="completed",
            time_spent_seconds=1200,
            created_at=datetime(2026, 2, 1),
            practice_attempts=1,
            highest_practice_score=40
        ),
        MagicMock(
            chapter_id=2,
            mastery_score=50,
            completion_status="completed",
            time_spent_seconds=1500,
            created_at=datetime(2026, 2, 2),
            practice_attempts=2,
            highest_practice_score=50
        ),
        MagicMock(
            chapter_id=3,
            mastery_score=52,
            completion_status="completed",
            time_spent_seconds=1400,
            created_at=datetime(2026, 2, 3),
            practice_attempts=2,
            highest_practice_score=52
        ),
        MagicMock(
            chapter_id=4,
            mastery_score=55,
            completion_status="completed",
            time_spent_seconds=1600,
            created_at=datetime(2026, 2, 4),
            practice_attempts=2,
            highest_practice_score=55
        ),
        MagicMock(
            chapter_id=5,
            mastery_score=75,
            completion_status="completed",
            time_spent_seconds=1800,
            created_at=datetime(2026, 2, 5),
            practice_attempts=3,
            highest_practice_score=75
        ),
    ]


class TestAdvancedLearningCurve:
    """Tests for advanced learning curve calculation."""

    @pytest.mark.asyncio
    async def test_calculate_learning_curve_success(self, mock_db, mock_progress_records):
        """Test successful learning curve calculation."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_progress_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.calculate_advanced_learning_curve(user_id)

        assert "skill_snapshots" in result
        assert "improvement_rate_per_week" in result
        assert "average_skill_level" in result
        assert "skill_std_dev" in result
        assert "trend" in result
        assert result["total_snapshots"] > 0

    @pytest.mark.asyncio
    async def test_learning_curve_empty_progress(self, mock_db):
        """Test learning curve with no progress."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.calculate_advanced_learning_curve(user_id)

        assert result["skill_snapshots"] == []
        assert result["improvement_rate_per_week"] == 0.0
        assert result["trend"] == "insufficient_data"

    @pytest.mark.asyncio
    async def test_learning_curve_skill_snapshots(self, mock_db, mock_progress_records):
        """Test that skill snapshots are properly formatted."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_progress_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.calculate_advanced_learning_curve(user_id)

        snapshots = result["skill_snapshots"]
        assert len(snapshots) > 0
        for snapshot in snapshots:
            assert "timestamp" in snapshot
            assert "skill_level" in snapshot
            assert "chapter_id" in snapshot

    @pytest.mark.asyncio
    async def test_learning_curve_calculates_average_skill(self, mock_db, mock_progress_records):
        """Test that average skill level is calculated correctly."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_progress_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.calculate_advanced_learning_curve(user_id)

        # Average of [40, 50, 52, 55, 75] = 54.4
        assert result["average_skill_level"] == 54.4

    @pytest.mark.asyncio
    async def test_learning_curve_calculates_std_dev(self, mock_db, mock_progress_records):
        """Test that standard deviation is calculated."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_progress_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.calculate_advanced_learning_curve(user_id)

        assert result["skill_std_dev"] > 0

    @pytest.mark.asyncio
    async def test_learning_curve_detects_improving_trend(self, mock_db):
        """Test that improving trend is detected."""
        improving_records = [
            MagicMock(chapter_id=i, mastery_score=40 + (i * 10),
                     created_at=datetime.now(), completion_status="completed")
            for i in range(5)
        ]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = improving_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.calculate_advanced_learning_curve(uuid4())

        assert result["trend"] == "improving"

    @pytest.mark.asyncio
    async def test_learning_curve_detects_declining_trend(self, mock_db):
        """Test that declining trend is detected."""
        declining_records = [
            MagicMock(chapter_id=i, mastery_score=100 - (i * 15),
                     created_at=datetime.now(), completion_status="completed")
            for i in range(5)
        ]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = declining_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.calculate_advanced_learning_curve(uuid4())

        assert result["trend"] == "declining"

    @pytest.mark.asyncio
    async def test_learning_curve_detects_plateau_trend(self, mock_db):
        """Test that plateau trend is detected."""
        plateau_records = [
            MagicMock(chapter_id=i, mastery_score=70 + (i % 2),
                     created_at=datetime.now(), completion_status="completed")
            for i in range(5)
        ]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = plateau_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.calculate_advanced_learning_curve(uuid4())

        assert result["trend"] == "plateau"


class TestPlateausAndRegressions:
    """Tests for plateau and regression detection."""

    @pytest.mark.asyncio
    async def test_detect_plateaus_and_regressions_success(self, mock_db, mock_progress_records):
        """Test successful detection of plateaus and regressions."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_progress_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.detect_plateaus_and_regressions(user_id)

        assert "plateaus" in result
        assert "regressions" in result
        assert "current_status" in result
        assert "plateau_count" in result
        assert "regression_count" in result

    @pytest.mark.asyncio
    async def test_detect_plateaus_insufficient_data(self, mock_db):
        """Test that insufficient_data status is returned with few records."""
        user_id = uuid4()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [
            MagicMock(chapter_id=1, mastery_score=50)
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.detect_plateaus_and_regressions(user_id)

        assert result["current_status"] == "insufficient_data"

    @pytest.mark.asyncio
    async def test_detects_plateau_status(self, mock_db):
        """Test that plateau status is detected."""
        plateau_records = [
            MagicMock(chapter_id=i, mastery_score=70)
            for i in range(5)
        ]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = plateau_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.detect_plateaus_and_regressions(uuid4())

        assert result["current_status"] == "plateau"
        assert result["plateau_count"] > 0

    @pytest.mark.asyncio
    async def test_detects_regression_status(self, mock_db):
        """Test that regression status is detected."""
        regression_records = [
            MagicMock(chapter_id=1, mastery_score=90),
            MagicMock(chapter_id=2, mastery_score=70),
            MagicMock(chapter_id=3, mastery_score=60),
            MagicMock(chapter_id=4, mastery_score=40),
        ]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = regression_records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.detect_plateaus_and_regressions(uuid4())

        assert result["current_status"] == "regression"
        assert result["regression_count"] > 0

    @pytest.mark.asyncio
    async def test_regression_severity_moderate(self, mock_db):
        """Test that moderate regressions are properly classified."""
        records = [
            MagicMock(chapter_id=1, mastery_score=80),
            MagicMock(chapter_id=2, mastery_score=75),  # Similar
            MagicMock(chapter_id=3, mastery_score=65),  # 15 point drop
            MagicMock(chapter_id=4, mastery_score=64),  # Similar
        ]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.detect_plateaus_and_regressions(uuid4(), regression_threshold=10.0)

        assert result["regression_count"] == 1
        assert result["regressions"][0]["severity"] == "moderate"

    @pytest.mark.asyncio
    async def test_regression_severity_severe(self, mock_db):
        """Test that severe regressions are properly classified."""
        records = [
            MagicMock(chapter_id=1, mastery_score=90),
            MagicMock(chapter_id=2, mastery_score=89),  # Similar
            MagicMock(chapter_id=3, mastery_score=65),  # 25 point drop (severe)
            MagicMock(chapter_id=4, mastery_score=64),  # Similar
        ]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = records
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.detect_plateaus_and_regressions(uuid4())

        assert result["regression_count"] == 1
        assert result["regressions"][0]["severity"] == "severe"


class TestImprovementRateCalculation:
    """Tests for improvement rate calculation."""

    def test_improvement_rate_positive(self):
        """Test improvement rate with positive improvement."""
        service = StatisticsService(AsyncMock())
        scores = [40, 50, 60, 70, 80]
        rate = service._calculate_improvement_rate(scores)

        assert rate > 0
        # 40 point improvement over 5 chapters = 5/7 weeks = 56 points/week
        assert rate == 56.0

    def test_improvement_rate_negative(self):
        """Test improvement rate with negative improvement."""
        service = StatisticsService(AsyncMock())
        scores = [80, 70, 60, 50, 40]
        rate = service._calculate_improvement_rate(scores)

        assert rate < 0

    def test_improvement_rate_flat(self):
        """Test improvement rate with flat performance."""
        service = StatisticsService(AsyncMock())
        scores = [70, 70, 70, 70, 70]
        rate = service._calculate_improvement_rate(scores)

        assert rate == 0.0

    def test_improvement_rate_insufficient_data(self):
        """Test improvement rate with insufficient data."""
        service = StatisticsService(AsyncMock())

        # Single score
        assert service._calculate_improvement_rate([70]) == 0.0

        # Empty list
        assert service._calculate_improvement_rate([]) == 0.0


class TestTrendDetection:
    """Tests for trend detection."""

    def test_detect_improving_trend(self):
        """Test improving trend detection."""
        service = StatisticsService(AsyncMock())
        scores = [30, 35, 40, 70, 75, 80]
        trend = service._detect_trend(scores)

        assert trend == "improving"

    def test_detect_declining_trend(self):
        """Test declining trend detection."""
        service = StatisticsService(AsyncMock())
        scores = [80, 75, 70, 40, 35, 30]
        trend = service._detect_trend(scores)

        assert trend == "declining"

    def test_detect_plateau_trend(self):
        """Test plateau trend detection."""
        service = StatisticsService(AsyncMock())
        scores = [70, 70, 72, 71, 70]
        trend = service._detect_trend(scores)

        assert trend == "plateau"

    def test_detect_trend_insufficient_data(self):
        """Test trend detection with insufficient data."""
        service = StatisticsService(AsyncMock())
        scores = [70]
        trend = service._detect_trend(scores)

        assert trend == "insufficient_data"


class TestPlateauDetection:
    """Tests for plateau detection."""

    def test_find_plateaus_single_plateau(self, mock_db):
        """Test finding a single plateau."""
        records = [
            MagicMock(chapter_id=1, mastery_score=70),
            MagicMock(chapter_id=2, mastery_score=71),
            MagicMock(chapter_id=3, mastery_score=70),
            MagicMock(chapter_id=4, mastery_score=72),
        ]
        service = StatisticsService(mock_db)
        plateaus = service._find_plateaus(records, threshold=3)

        assert len(plateaus) > 0

    def test_find_plateaus_no_plateaus(self, mock_db):
        """Test when no plateaus are found."""
        records = [
            MagicMock(chapter_id=i, mastery_score=30 + (i * 20))
            for i in range(5)
        ]
        service = StatisticsService(mock_db)
        plateaus = service._find_plateaus(records, threshold=3)

        assert len(plateaus) == 0


class TestRegressionDetection:
    """Tests for regression detection."""

    def test_find_single_regression(self, mock_db):
        """Test finding a single regression."""
        records = [
            MagicMock(chapter_id=1, mastery_score=80),
            MagicMock(chapter_id=2, mastery_score=60),
        ]
        service = StatisticsService(mock_db)
        regressions = service._find_regressions(records, threshold=10.0)

        assert len(regressions) == 1
        assert regressions[0]["score_drop"] == 20

    def test_find_no_regressions(self, mock_db):
        """Test when no regressions are found."""
        records = [
            MagicMock(chapter_id=i, mastery_score=40 + (i * 10))
            for i in range(5)
        ]
        service = StatisticsService(mock_db)
        regressions = service._find_regressions(records, threshold=15.0)

        assert len(regressions) == 0

    def test_regression_data_accuracy(self, mock_db):
        """Test that regression data is accurate."""
        records = [
            MagicMock(chapter_id=3, mastery_score=85),
            MagicMock(chapter_id=4, mastery_score=65),
        ]
        service = StatisticsService(mock_db)
        regressions = service._find_regressions(records)

        assert regressions[0]["from_chapter"] == 3
        assert regressions[0]["to_chapter"] == 4
        assert regressions[0]["previous_score"] == 85
        assert regressions[0]["current_score"] == 65
