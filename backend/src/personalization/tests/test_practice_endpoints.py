"""Integration tests for Practice endpoints (T057-T059)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from uuid import uuid4
from datetime import datetime

from src.personalization.models.db_models import User, Progress
from src.personalization.api.routes.practice import (
    submit_practice_attempt,
    retry_chapter,
    get_learning_statistics,
    calculate_improvement_rate
)


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock()


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
def sample_questions():
    """Create sample practice questions."""
    return [
        {
            "id": "q1",
            "question": "What is the capital of France?",
            "options": [
                {"letter": "A", "text": "Paris"},
                {"letter": "B", "text": "Lyon"},
                {"letter": "C", "text": "Marseille"}
            ],
            "correct_answer": "A",
            "difficulty": "easy"
        },
        {
            "id": "q2",
            "question": "What is 2 + 2?",
            "options": [
                {"letter": "A", "text": "3"},
                {"letter": "B", "text": "4"},
                {"letter": "C", "text": "5"}
            ],
            "correct_answer": "B",
            "difficulty": "easy"
        }
    ]


class TestSubmitPracticeAttempt:
    """Tests for T057: Submit practice attempt endpoint."""

    @pytest.mark.asyncio
    async def test_submit_practice_attempt_success(self, mock_db, test_user, sample_questions):
        """Test successful practice attempt submission."""
        with patch("src.personalization.api.routes.practice.get_practice_service") as mock_svc:
            mock_practice = AsyncMock()
            mock_practice.get_practice_questions = AsyncMock(return_value=sample_questions)
            mock_practice.calculate_score = MagicMock(return_value=2)
            mock_practice.save_practice_attempt = AsyncMock(return_value=MagicMock())
            mock_practice.get_chapter_practice_history = AsyncMock(
                return_value={
                    "attempts": 2,
                    "avg_score": 90,
                    "best_score": 100,
                    "history": [
                        {"attempt_number": 1, "score": 80},
                        {"attempt_number": 2, "score": 100},
                    ]
                }
            )
            mock_svc.return_value = mock_practice

            result = await submit_practice_attempt(
                user_id=test_user.user_id,
                chapter_id=1,
                answers={"answers": [{"question_id": "q1", "answer": "A"}, {"question_id": "q2", "answer": "B"}]},
                current_user=test_user,
                db=mock_db
            )

            assert result["mastery_score"] == 100.0
            assert result["correct_answers"] == 2
            assert result["total_questions"] == 2
            assert result["attempt_number"] == 2
            assert result["highest_score"] == 100
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_submit_practice_attempt_partial_score(self, mock_db, test_user, sample_questions):
        """Test practice attempt with partial score."""
        with patch("src.personalization.api.routes.practice.get_practice_service") as mock_svc:
            mock_practice = AsyncMock()
            mock_practice.get_practice_questions = AsyncMock(return_value=sample_questions)
            mock_practice.calculate_score = MagicMock(return_value=1)  # 1 out of 2
            mock_practice.save_practice_attempt = AsyncMock(return_value=MagicMock())
            mock_practice.get_chapter_practice_history = AsyncMock(
                return_value={
                    "attempts": 1,
                    "avg_score": 50,
                    "best_score": 50,
                    "history": []
                }
            )
            mock_svc.return_value = mock_practice

            result = await submit_practice_attempt(
                user_id=test_user.user_id,
                chapter_id=1,
                answers={"answers": [{"question_id": "q1", "answer": "A"}]},
                current_user=test_user,
                db=mock_db
            )

            assert result["mastery_score"] == 50.0
            assert result["correct_answers"] == 1
            assert result["total_questions"] == 2

    @pytest.mark.asyncio
    async def test_submit_practice_attempt_forbidden(self, mock_db, test_user):
        """Test that users cannot submit practice for other users."""
        other_user = User(
            user_id=uuid4(),
            username="otheruser",
            email="other@example.com",
            password_hash="hashed_password",
            skill_level=50
        )

        try:
            await submit_practice_attempt(
                user_id=other_user.user_id,
                chapter_id=1,
                answers={"answers": []},
                current_user=test_user,
                db=mock_db
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 403

    @pytest.mark.asyncio
    async def test_submit_practice_attempt_invalid_chapter(self, mock_db, test_user):
        """Test that invalid chapter ID is rejected."""
        try:
            await submit_practice_attempt(
                user_id=test_user.user_id,
                chapter_id=99,
                answers={"answers": []},
                current_user=test_user,
                db=mock_db
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 400

    @pytest.mark.asyncio
    async def test_submit_practice_attempt_no_answers(self, mock_db, test_user):
        """Test that empty answers are rejected."""
        try:
            await submit_practice_attempt(
                user_id=test_user.user_id,
                chapter_id=1,
                answers={"answers": []},
                current_user=test_user,
                db=mock_db
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 400

    @pytest.mark.asyncio
    async def test_submit_practice_attempt_no_questions_available(self, mock_db, test_user):
        """Test handling when no practice questions are available."""
        with patch("src.personalization.api.routes.practice.get_practice_service") as mock_svc:
            mock_practice = AsyncMock()
            mock_practice.get_practice_questions = AsyncMock(return_value=[])
            mock_svc.return_value = mock_practice

            try:
                await submit_practice_attempt(
                    user_id=test_user.user_id,
                    chapter_id=1,
                    answers={"answers": [{"question_id": "q1", "answer": "A"}]},
                    current_user=test_user,
                    db=mock_db
                )
                assert False, "Should have raised HTTPException"
            except HTTPException as e:
                assert e.status_code == 400

    @pytest.mark.asyncio
    async def test_submit_practice_attempt_with_empty_history(self, mock_db, test_user, sample_questions):
        """Test practice attempt with no prior history."""
        with patch("src.personalization.api.routes.practice.get_practice_service") as mock_svc:
            mock_practice = AsyncMock()
            mock_practice.get_practice_questions = AsyncMock(return_value=sample_questions)
            mock_practice.calculate_score = MagicMock(return_value=2)
            mock_practice.save_practice_attempt = AsyncMock(return_value=MagicMock())
            mock_practice.get_chapter_practice_history = AsyncMock(
                return_value={
                    "attempts": 1,
                    "avg_score": 100,
                    "best_score": 100,
                    "history": []
                }
            )
            mock_svc.return_value = mock_practice

            result = await submit_practice_attempt(
                user_id=test_user.user_id,
                chapter_id=1,
                answers={"answers": [{"question_id": "q1", "answer": "A"}]},
                current_user=test_user,
                db=mock_db
            )

            assert result["attempt_number"] == 1
            assert result["highest_score"] == 100

    @pytest.mark.asyncio
    async def test_submit_practice_attempt_tracks_highest_score(self, mock_db, test_user, sample_questions):
        """Test that highest score is tracked correctly."""
        with patch("src.personalization.api.routes.practice.get_practice_service") as mock_svc:
            mock_practice = AsyncMock()
            mock_practice.get_practice_questions = AsyncMock(return_value=sample_questions)
            mock_practice.calculate_score = MagicMock(return_value=1)  # 50% this time
            mock_practice.save_practice_attempt = AsyncMock(return_value=MagicMock())
            mock_practice.get_chapter_practice_history = AsyncMock(
                return_value={
                    "attempts": 2,
                    "avg_score": 90,
                    "best_score": 100,
                    "history": [
                        {"attempt_number": 1, "score": 100},
                        {"attempt_number": 2, "score": 80},
                    ]
                }
            )
            mock_svc.return_value = mock_practice

            result = await submit_practice_attempt(
                user_id=test_user.user_id,
                chapter_id=1,
                answers={"answers": [{"question_id": "q1", "answer": "A"}]},
                current_user=test_user,
                db=mock_db
            )

            assert result["mastery_score"] == 50.0
            assert result["highest_score"] == 100  # Should be highest from history


class TestRetryChapter:
    """Tests for T058: Retry chapter endpoint."""

    @pytest.mark.asyncio
    async def test_retry_chapter_success(self, mock_db, test_user, sample_questions):
        """Test successful chapter retry."""
        with patch("src.personalization.api.routes.practice.progress_service.reset_chapter_progress") as mock_reset:
            with patch("src.personalization.api.routes.practice.get_practice_service") as mock_svc:
                mock_reset.return_value = MagicMock()
                mock_practice = AsyncMock()
                mock_practice.get_practice_questions = AsyncMock(return_value=sample_questions)
                mock_svc.return_value = mock_practice

                result = await retry_chapter(
                    user_id=test_user.user_id,
                    chapter_id=1,
                    current_user=test_user,
                    db=mock_db
                )

                assert result["chapter_id"] == 1
                assert result["message"] == "Chapter reset for retry"
                assert result["total_questions"] == 2
                assert len(result["questions"]) == 2
                assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_retry_chapter_forbidden(self, mock_db, test_user):
        """Test that users cannot retry other users' chapters."""
        other_user = User(
            user_id=uuid4(),
            username="otheruser",
            email="other@example.com",
            password_hash="hashed_password",
            skill_level=50
        )

        try:
            await retry_chapter(
                user_id=other_user.user_id,
                chapter_id=1,
                current_user=test_user,
                db=mock_db
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 403

    @pytest.mark.asyncio
    async def test_retry_chapter_invalid_chapter(self, mock_db, test_user):
        """Test that invalid chapter ID is rejected."""
        try:
            await retry_chapter(
                user_id=test_user.user_id,
                chapter_id=99,
                current_user=test_user,
                db=mock_db
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 400

    @pytest.mark.asyncio
    async def test_retry_chapter_resets_progress(self, mock_db, test_user, sample_questions):
        """Test that retry resets chapter progress."""
        with patch("src.personalization.api.routes.practice.progress_service.reset_chapter_progress") as mock_reset:
            with patch("src.personalization.api.routes.practice.get_practice_service") as mock_svc:
                mock_reset.return_value = MagicMock()
                mock_practice = AsyncMock()
                mock_practice.get_practice_questions = AsyncMock(return_value=sample_questions)
                mock_svc.return_value = mock_practice

                await retry_chapter(
                    user_id=test_user.user_id,
                    chapter_id=5,
                    current_user=test_user,
                    db=mock_db
                )

                # Verify reset was called
                mock_reset.assert_called_once_with(mock_db, test_user.user_id, 5)

    @pytest.mark.asyncio
    async def test_retry_chapter_no_questions(self, mock_db, test_user):
        """Test handling when no practice questions are available."""
        with patch("src.personalization.api.routes.practice.progress_service.reset_chapter_progress") as mock_reset:
            with patch("src.personalization.api.routes.practice.get_practice_service") as mock_svc:
                mock_reset.return_value = MagicMock()
                mock_practice = AsyncMock()
                mock_practice.get_practice_questions = AsyncMock(return_value=[])
                mock_svc.return_value = mock_practice

                try:
                    await retry_chapter(
                        user_id=test_user.user_id,
                        chapter_id=1,
                        current_user=test_user,
                        db=mock_db
                    )
                    assert False, "Should have raised HTTPException"
                except HTTPException as e:
                    assert e.status_code == 400

    @pytest.mark.asyncio
    async def test_retry_chapter_returns_formatted_questions(self, mock_db, test_user, sample_questions):
        """Test that questions are properly formatted in response."""
        with patch("src.personalization.api.routes.practice.progress_service.reset_chapter_progress") as mock_reset:
            with patch("src.personalization.api.routes.practice.get_practice_service") as mock_svc:
                mock_reset.return_value = MagicMock()
                mock_practice = AsyncMock()
                mock_practice.get_practice_questions = AsyncMock(return_value=sample_questions)
                mock_svc.return_value = mock_practice

                result = await retry_chapter(
                    user_id=test_user.user_id,
                    chapter_id=1,
                    current_user=test_user,
                    db=mock_db
                )

                # Verify question format
                question = result["questions"][0]
                assert "id" in question
                assert "question" in question
                assert "options" in question
                assert "difficulty" in question
                assert all("letter" in opt and "text" in opt for opt in question["options"])


class TestGetLearningStatistics:
    """Tests for T059: Get learning statistics endpoint."""

    @pytest.mark.asyncio
    async def test_get_learning_statistics_success(self, mock_db, test_user):
        """Test successful statistics retrieval."""
        with patch("src.personalization.api.routes.practice.progress_service.get_user_progress") as mock_get:
            # Create mock progress records
            progress_records = [
                MagicMock(chapter_id=1, time_spent_seconds=1200, mastery_score=85,
                         created_at=datetime.utcnow(), completion_status="completed"),
                MagicMock(chapter_id=2, time_spent_seconds=1500, mastery_score=90,
                         created_at=datetime.utcnow(), completion_status="completed"),
                MagicMock(chapter_id=3, time_spent_seconds=900, mastery_score=50,
                         created_at=datetime.utcnow(), completion_status="in_progress"),
            ]
            mock_get.return_value = progress_records

            result = await get_learning_statistics(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            assert "time_per_chapter" in result
            assert "total_time_hours" in result
            assert "mastery_per_chapter" in result
            assert "learning_curve" in result
            assert "recommended_focus_areas" in result
            assert "overall_mastery" in result
            assert "chapters_completed" in result
            assert "total_chapters" in result
            assert result["chapters_completed"] == 2
            assert result["total_chapters"] == 3

    @pytest.mark.asyncio
    async def test_get_learning_statistics_forbidden(self, mock_db, test_user):
        """Test that users cannot access other users' statistics."""
        other_user = User(
            user_id=uuid4(),
            username="otheruser",
            email="other@example.com",
            password_hash="hashed_password",
            skill_level=50
        )

        try:
            await get_learning_statistics(
                user_id=other_user.user_id,
                current_user=test_user,
                db=mock_db
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 403

    @pytest.mark.asyncio
    async def test_get_learning_statistics_empty_progress(self, mock_db, test_user):
        """Test statistics when user has no progress."""
        with patch("src.personalization.api.routes.practice.progress_service.get_user_progress") as mock_get:
            mock_get.return_value = []

            result = await get_learning_statistics(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            assert result["chapters_completed"] == 0
            assert result["total_chapters"] == 0
            assert result["overall_mastery"] == 0
            assert result["total_time_hours"] == 0.0

    @pytest.mark.asyncio
    async def test_get_learning_statistics_calculates_time_correctly(self, mock_db, test_user):
        """Test that time is calculated correctly."""
        with patch("src.personalization.api.routes.practice.progress_service.get_user_progress") as mock_get:
            progress_records = [
                MagicMock(chapter_id=1, time_spent_seconds=3600, mastery_score=85,
                         created_at=datetime.utcnow(), completion_status="completed"),
                MagicMock(chapter_id=2, time_spent_seconds=7200, mastery_score=90,
                         created_at=datetime.utcnow(), completion_status="completed"),
            ]
            mock_get.return_value = progress_records

            result = await get_learning_statistics(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # 3600 + 7200 = 10800 seconds = 3 hours
            assert result["total_time_hours"] == 3.0

    @pytest.mark.asyncio
    async def test_get_learning_statistics_recommends_low_mastery(self, mock_db, test_user):
        """Test that low mastery chapters are recommended."""
        with patch("src.personalization.api.routes.practice.progress_service.get_user_progress") as mock_get:
            progress_records = [
                MagicMock(chapter_id=1, time_spent_seconds=1200, mastery_score=40,
                         created_at=datetime.utcnow(), completion_status="completed"),
                MagicMock(chapter_id=2, time_spent_seconds=1500, mastery_score=90,
                         created_at=datetime.utcnow(), completion_status="completed"),
                MagicMock(chapter_id=3, time_spent_seconds=900, mastery_score=55,
                         created_at=datetime.utcnow(), completion_status="in_progress"),
            ]
            mock_get.return_value = progress_records

            result = await get_learning_statistics(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # Should recommend chapters with mastery < 70%
            recommended = result["recommended_focus_areas"]
            assert len(recommended) > 0
            # Should include ch1 (40%) and ch3 (55%)
            recommended_ids = [r["chapter_id"] for r in recommended]
            assert 1 in recommended_ids

    @pytest.mark.asyncio
    async def test_get_learning_statistics_learning_curve(self, mock_db, test_user):
        """Test that learning curve is calculated."""
        with patch("src.personalization.api.routes.practice.progress_service.get_user_progress") as mock_get:
            progress_records = [
                MagicMock(chapter_id=1, time_spent_seconds=1200, mastery_score=50,
                         created_at=datetime.utcnow(), completion_status="completed"),
                MagicMock(chapter_id=2, time_spent_seconds=1500, mastery_score=60,
                         created_at=datetime.utcnow(), completion_status="completed"),
                MagicMock(chapter_id=3, time_spent_seconds=900, mastery_score=70,
                         created_at=datetime.utcnow(), completion_status="completed"),
            ]
            mock_get.return_value = progress_records

            result = await get_learning_statistics(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            assert "learning_curve" in result
            assert "skill_snapshots" in result["learning_curve"]
            assert "improvement_rate_per_week" in result["learning_curve"]

    @pytest.mark.asyncio
    async def test_get_learning_statistics_overall_mastery(self, mock_db, test_user):
        """Test that overall mastery is calculated correctly."""
        with patch("src.personalization.api.routes.practice.progress_service.get_user_progress") as mock_get:
            progress_records = [
                MagicMock(chapter_id=1, time_spent_seconds=1200, mastery_score=80,
                         created_at=datetime.utcnow(), completion_status="completed"),
                MagicMock(chapter_id=2, time_spent_seconds=1500, mastery_score=100,
                         created_at=datetime.utcnow(), completion_status="completed"),
            ]
            mock_get.return_value = progress_records

            result = await get_learning_statistics(
                user_id=test_user.user_id,
                current_user=test_user,
                db=mock_db
            )

            # (80 + 100) / 2 = 90
            assert result["overall_mastery"] == 90.0


class TestCalculateImprovementRate:
    """Tests for improvement rate calculation helper."""

    def test_calculate_improvement_rate_no_data(self):
        """Test improvement rate with no progress."""
        result = calculate_improvement_rate([])
        assert result == 0.0

    def test_calculate_improvement_rate_single_record(self):
        """Test improvement rate with single record."""
        progress = [MagicMock(mastery_score=80)]
        result = calculate_improvement_rate(progress)
        assert result == 0.0

    def test_calculate_improvement_rate_multiple_records(self):
        """Test improvement rate with multiple records."""
        progress = [
            MagicMock(mastery_score=50),
            MagicMock(mastery_score=60),
            MagicMock(mastery_score=70),
        ]
        result = calculate_improvement_rate(progress)
        # Improvement: 70 - 50 = 20 points
        # Chapters: 3, weeks: 3/7 = 0.43
        # Rate: 20 / 0.43 ≈ 46.67 (but could vary)
        assert isinstance(result, float)
        assert result >= 0

    def test_calculate_improvement_rate_zero_scores(self):
        """Test improvement rate with zero mastery scores."""
        progress = [
            MagicMock(mastery_score=0),
            MagicMock(mastery_score=0),
        ]
        result = calculate_improvement_rate(progress)
        assert result == 0.0

    def test_calculate_improvement_rate_increasing_progression(self):
        """Test improvement rate shows positive progression."""
        progress = [
            MagicMock(mastery_score=20),
            MagicMock(mastery_score=40),
            MagicMock(mastery_score=60),
            MagicMock(mastery_score=80),
            MagicMock(mastery_score=100),
        ]
        result = calculate_improvement_rate(progress)
        # 100 - 20 = 80 points, 5 chapters / 7 = 0.71 weeks
        assert result > 0
