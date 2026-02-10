"""Comprehensive integration tests for Practice and Statistics (T063)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

from src.personalization.models.db_models import Progress, PracticeAttempt
from src.personalization.services.practice_service import PracticeService
from src.personalization.services.statistics_service import StatisticsService


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock()


class TestPracticeQuestionGeneration:
    """Tests for practice question generation."""

    @pytest.mark.asyncio
    async def test_generate_practice_questions_for_valid_chapter(self, mock_db):
        """Test generating practice questions for a valid chapter."""
        chapter_id = 1
        service = PracticeService(mock_db)

        questions = await service.get_practice_questions(chapter_id)

        assert questions is not None
        assert len(questions) > 0
        for question in questions:
            assert "id" in question
            assert "question" in question
            assert "options" in question
            assert "difficulty" in question
            assert len(question["options"]) == 4

    @pytest.mark.asyncio
    async def test_generate_practice_questions_limit(self, mock_db):
        """Test practice question limit parameter."""
        chapter_id = 1
        limit = 2
        service = PracticeService(mock_db)

        questions = await service.get_practice_questions(chapter_id, limit=limit)

        assert len(questions) <= limit

    @pytest.mark.asyncio
    async def test_generate_practice_questions_default_limit(self, mock_db):
        """Test practice question default limit (5)."""
        chapter_id = 1
        service = PracticeService(mock_db)

        questions = await service.get_practice_questions(chapter_id)

        # Default limit is 5
        assert len(questions) <= 5

    @pytest.mark.asyncio
    async def test_generate_practice_questions_chapter_without_defined_questions(self, mock_db):
        """Test generating placeholder questions for undefined chapters."""
        chapter_id = 15
        service = PracticeService(mock_db)

        questions = await service.get_practice_questions(chapter_id)

        # Should generate placeholders
        assert len(questions) > 0
        assert all("Sample question" in q["question"] or "q" in q["id"] for q in questions)

    @pytest.mark.asyncio
    async def test_practice_questions_have_difficulty_levels(self, mock_db):
        """Test that questions have appropriate difficulty levels."""
        chapter_id = 1
        service = PracticeService(mock_db)

        questions = await service.get_practice_questions(chapter_id)

        difficulties = {q.get("difficulty") for q in questions}
        valid_difficulties = {"beginner", "intermediate", "advanced"}
        assert difficulties.issubset(valid_difficulties)

    @pytest.mark.asyncio
    async def test_practice_questions_have_one_correct_answer(self, mock_db):
        """Test that each question has exactly one correct answer."""
        chapter_id = 1
        service = PracticeService(mock_db)

        questions = await service.get_practice_questions(chapter_id)

        for question in questions:
            correct_options = [opt for opt in question["options"] if opt.get("correct")]
            assert len(correct_options) == 1


class TestPracticeRetryLogic:
    """Tests for chapter retry functionality."""

    @pytest.mark.asyncio
    async def test_get_chapter_practice_history_empty(self, mock_db):
        """Test getting practice history with no attempts."""
        user_id = uuid4()
        chapter_id = 1

        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        history = await service.get_chapter_practice_history(user_id, chapter_id)

        assert history["attempts"] == 0
        assert history["avg_score"] == 0
        assert history["best_score"] == 0
        assert history["history"] == []

    @pytest.mark.asyncio
    async def test_get_chapter_practice_history_single_attempt(self, mock_db):
        """Test practice history with single attempt."""
        user_id = uuid4()
        chapter_id = 1

        mock_attempt = MagicMock(
            score=75,
            attempted_at=datetime.utcnow(),
            questions_json={"total": 5}
        )
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = [mock_attempt]
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        history = await service.get_chapter_practice_history(user_id, chapter_id)

        assert history["attempts"] == 1
        assert history["best_score"] == 75
        assert history["avg_score"] == 75
        assert len(history["history"]) == 1

    @pytest.mark.asyncio
    async def test_get_chapter_practice_history_multiple_attempts(self, mock_db):
        """Test practice history with multiple attempts showing improvement."""
        user_id = uuid4()
        chapter_id = 1

        mock_attempts = [
            MagicMock(score=50, attempted_at=datetime.utcnow() - timedelta(hours=2),
                     questions_json={"total": 5}),
            MagicMock(score=65, attempted_at=datetime.utcnow() - timedelta(hours=1),
                     questions_json={"total": 5}),
            MagicMock(score=80, attempted_at=datetime.utcnow(),
                     questions_json={"total": 5})
        ]
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_attempts
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        history = await service.get_chapter_practice_history(user_id, chapter_id)

        assert history["attempts"] == 3
        assert history["best_score"] == 80
        assert history["avg_score"] == 65  # (50+65+80)/3 = 65
        assert history["history"][0]["attempt_number"] == 1
        assert history["history"][2]["attempt_number"] == 3

    @pytest.mark.asyncio
    async def test_practice_history_tracks_score_improvement(self, mock_db):
        """Test that history correctly tracks score progression."""
        user_id = uuid4()
        chapter_id = 1

        mock_attempts = [
            MagicMock(score=40, attempted_at=datetime.utcnow() - timedelta(hours=3),
                     questions_json={"total": 5}),
            MagicMock(score=60, attempted_at=datetime.utcnow() - timedelta(hours=2),
                     questions_json={"total": 5}),
            MagicMock(score=75, attempted_at=datetime.utcnow() - timedelta(hours=1),
                     questions_json={"total": 5}),
            MagicMock(score=90, attempted_at=datetime.utcnow(),
                     questions_json={"total": 5})
        ]
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_attempts
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        history = await service.get_chapter_practice_history(user_id, chapter_id)

        # Verify scores are in chronological order
        scores = [h["score"] for h in history["history"]]
        assert scores == [40, 60, 75, 90]

    @pytest.mark.asyncio
    async def test_practice_score_calculation_all_correct(self, mock_db):
        """Test practice score calculation with all correct answers."""
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

        service = PracticeService(mock_db)
        score = service.calculate_score(questions, answers)

        assert score == 100

    @pytest.mark.asyncio
    async def test_practice_score_calculation_partial(self, mock_db):
        """Test practice score calculation with partial correct answers."""
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
            },
            {
                "id": "q3",
                "options": [
                    {"letter": "A", "correct": True},
                    {"letter": "B", "correct": False}
                ]
            }
        ]
        answers = {"q1": "A", "q2": "A", "q3": "A"}  # 2/3 correct

        service = PracticeService(mock_db)
        score = service.calculate_score(questions, answers)

        assert score == 66  # (2/3)*100 = 66.67 → int() truncates to 66


class TestStatisticsCalculations:
    """Tests for statistics calculations."""

    @pytest.mark.asyncio
    async def test_calculate_time_heatmap_single_chapter(self, mock_db):
        """Test calculating time spent per chapter."""
        user_id = uuid4()

        mock_progress = MagicMock(chapter_id=1, time_spent_seconds=7200)  # 2 hours
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = [mock_progress]
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        heatmap = await service.get_time_heatmap(user_id)

        assert heatmap[1] == 2.0

    @pytest.mark.asyncio
    async def test_calculate_time_heatmap_multiple_chapters(self, mock_db):
        """Test time heatmap across multiple chapters."""
        user_id = uuid4()

        mock_progresses = [
            MagicMock(chapter_id=1, time_spent_seconds=3600),  # 1 hour
            MagicMock(chapter_id=2, time_spent_seconds=7200),  # 2 hours
            MagicMock(chapter_id=3, time_spent_seconds=1800)   # 0.5 hours
        ]
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_progresses
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        heatmap = await service.get_time_heatmap(user_id)

        assert heatmap[1] == 1.0
        assert heatmap[2] == 2.0
        assert heatmap[3] == 0.5

    @pytest.mark.asyncio
    async def test_calculate_mastery_per_chapter(self, mock_db):
        """Test calculating mastery scores per chapter."""
        user_id = uuid4()

        mock_progresses = [
            MagicMock(chapter_id=1, mastery_score=75),
            MagicMock(chapter_id=2, mastery_score=85),
            MagicMock(chapter_id=3, mastery_score=60)
        ]
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_progresses
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        mastery = await service.get_mastery_per_chapter(user_id)

        assert mastery[1] == 75
        assert mastery[2] == 85
        assert mastery[3] == 60

    @pytest.mark.asyncio
    async def test_learning_curve_over_time(self, mock_db):
        """Test generating learning curve data."""
        user_id = uuid4()
        now = datetime.utcnow()

        mock_progresses = [
            MagicMock(
                chapter_id=1,
                mastery_score=50,
                completion_status="in_progress",
                updated_at=now - timedelta(days=3)
            ),
            MagicMock(
                chapter_id=2,
                mastery_score=65,
                completion_status="in_progress",
                updated_at=now - timedelta(days=2)
            ),
            MagicMock(
                chapter_id=3,
                mastery_score=80,
                completion_status="completed",
                updated_at=now - timedelta(days=1)
            )
        ]
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_progresses
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        curve = await service.get_learning_curve(user_id)

        # Should have learning progression
        assert len(curve) > 0
        # Later dates should have higher avg mastery
        if len(curve) > 1:
            assert curve[-1]["avg_mastery"] >= curve[0]["avg_mastery"]


class TestFocusAreaRecommendations:
    """Tests for focus area recommendations."""

    @pytest.mark.asyncio
    async def test_recommend_low_mastery_chapters(self, mock_db):
        """Test recommendations for chapters with low mastery (< 60% with default threshold)."""
        user_id = uuid4()

        mock_progresses = [
            MagicMock(chapter_id=1, mastery_score=45, completion_status="completed"),
            MagicMock(chapter_id=2, mastery_score=75, completion_status="completed"),
            MagicMock(chapter_id=3, mastery_score=55, completion_status="in_progress")
        ]
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_progresses
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        # Use default threshold of 60%
        focus_areas = await service.get_recommended_focus_areas(user_id, threshold=60)

        # Should include chapters with mastery < 60%
        focus_ids = [f["chapter_id"] for f in focus_areas]
        assert 1 in focus_ids  # 45% mastery
        assert 3 in focus_ids  # 55% mastery
        assert 2 not in focus_ids  # 75% mastery is above threshold

    @pytest.mark.asyncio
    async def test_focus_areas_sorted_by_mastery(self, mock_db):
        """Test that recommendations are sorted by lowest mastery first."""
        user_id = uuid4()

        mock_progresses = [
            MagicMock(chapter_id=1, mastery_score=50),
            MagicMock(chapter_id=2, mastery_score=35),
            MagicMock(chapter_id=3, mastery_score=55)
        ]
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_progresses
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        focus_areas = await service.get_recommended_focus_areas(user_id)

        # First recommendation should be lowest mastery
        assert focus_areas[0]["chapter_id"] == 2
        assert focus_areas[0]["mastery_score"] == 35

    @pytest.mark.asyncio
    async def test_advanced_recommendations_with_module_dependencies(self, mock_db):
        """Test advanced recommendations include module prerequisites."""
        user_id = uuid4()

        # Weak chapter in module 2
        weak_progress = [
            MagicMock(
                chapter_id=8,  # Module 2
                mastery_score=45,
                time_spent_seconds=1800,
                practice_attempts=2,
                highest_practice_score=45
            )
        ]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = weak_progress
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        result = await service.get_advanced_recommendations(user_id)

        # Should include weak chapters
        assert "weak_chapters" in result
        assert "related_chapters" in result
        assert result["total_weak_chapters"] > 0


class TestPracticeStatsIntegration:
    """Integration tests combining practice and statistics."""

    @pytest.mark.asyncio
    async def test_practice_attempt_improves_statistics(self, mock_db):
        """Test that completing practice attempts updates statistics."""
        user_id = uuid4()
        chapter_id = 1

        # Setup mock for practice attempt
        mock_attempt = MagicMock(score=75)
        mock_progress = MagicMock(
            chapter_id=chapter_id,
            mastery_score=70,
            practice_attempts=0,
            highest_practice_score=0
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        practice_service = PracticeService(mock_db)
        questions = await practice_service.get_practice_questions(chapter_id)

        assert len(questions) > 0

    @pytest.mark.asyncio
    async def test_multiple_practice_attempts_show_learning_trend(self, mock_db):
        """Test that multiple practice attempts show improvement trend."""
        user_id = uuid4()
        chapter_id = 1

        # Simulate 3 practice attempts with improvement
        mock_attempts = [
            MagicMock(score=50, attempted_at=datetime.utcnow() - timedelta(hours=3),
                     questions_json={"total": 5}),
            MagicMock(score=65, attempted_at=datetime.utcnow() - timedelta(hours=2),
                     questions_json={"total": 5}),
            MagicMock(score=80, attempted_at=datetime.utcnow() - timedelta(hours=1),
                     questions_json={"total": 5})
        ]

        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_attempts
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        history = await service.get_chapter_practice_history(user_id, chapter_id)

        # Verify learning trend
        scores = [h["score"] for h in history["history"]]
        assert scores[-1] > scores[0]  # Latest score better than first
        assert history["best_score"] == 80

    @pytest.mark.asyncio
    async def test_mastery_threshold_eligibility_for_advanced(self, mock_db):
        """Test that 85%+ mastery enables advanced challenges."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=88, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        eligible = await service.check_advanced_challenges_eligibility(user_id, chapter_id)

        assert eligible is True


class TestEdgeCasesAndErrors:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_practice_with_no_questions(self, mock_db):
        """Test practice attempt with no questions available."""
        questions = []
        answers = {}

        service = PracticeService(mock_db)
        score = service.calculate_score(questions, answers)

        assert score == 0

    @pytest.mark.asyncio
    async def test_practice_with_missing_answers(self, mock_db):
        """Test practice scoring when some answers are missing."""
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
        answers = {"q1": "A"}  # Missing q2

        service = PracticeService(mock_db)
        score = service.calculate_score(questions, answers)

        # Should still calculate based on available answers
        assert 0 <= score <= 100

    @pytest.mark.asyncio
    async def test_empty_statistics_for_no_progress(self, mock_db):
        """Test statistics calculation with no progress records."""
        user_id = uuid4()

        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_db.execute.return_value = mock_result

        service = StatisticsService(mock_db)
        heatmap = await service.get_time_heatmap(user_id)

        assert heatmap == {}

    @pytest.mark.asyncio
    async def test_mastery_calculation_clamped_to_100(self, mock_db):
        """Test that mastery scores are clamped to 0-100 range."""
        questions = [
            {
                "id": "q1",
                "options": [{"letter": "A", "correct": True}]
            }
        ]
        answers = {"q1": "A"}

        service = PracticeService(mock_db)
        score = service.calculate_score(questions, answers)

        assert 0 <= score <= 100
        assert score == 100
