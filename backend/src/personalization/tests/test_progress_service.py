"""Tests for progress service (T042)."""

import pytest
from datetime import datetime, timedelta
from src.personalization.services import progress_service
from src.personalization.models.db_models import Progress


class TestProgressService:
    """Test progress tracking service."""

    @pytest.mark.asyncio
    async def test_mark_chapter_complete(self, test_db, test_user):
        """Test marking a chapter as complete."""
        user_id = test_user.user_id
        chapter_id = 1

        # Mark chapter complete
        progress = await progress_service.mark_chapter_complete(
            db=test_db,
            user_id=user_id,
            chapter_id=chapter_id
        )

        assert progress is not None
        assert progress.user_id == user_id
        assert progress.chapter_id == chapter_id
        assert progress.completion_status == "completed"
        assert progress.mastery_score == 80  # Default score

    @pytest.mark.asyncio
    async def test_calculate_mastery_score_basic(self, test_db, test_user):
        """Test basic mastery score calculation."""
        user_id = test_user.user_id
        chapter_id = 2

        # 8 out of 10 correct = 80% base
        score = await progress_service.calculate_mastery_score(
            db=test_db,
            user_id=user_id,
            chapter_id=chapter_id,
            correct_answers=8,
            total_questions=10,
            time_spent_seconds=1500  # 25 minutes (faster than average)
        )

        # Should be base 80 + time bonus
        assert 80 <= score <= 100

    @pytest.mark.asyncio
    async def test_calculate_mastery_score_range(self, test_db, test_user):
        """Test mastery score is in 0-100 range."""
        user_id = test_user.user_id
        chapter_id = 3

        # Perfect score
        score_perfect = await progress_service.calculate_mastery_score(
            db=test_db,
            user_id=user_id,
            chapter_id=chapter_id,
            correct_answers=10,
            total_questions=10,
            time_spent_seconds=900  # 15 minutes
        )
        assert 0 <= score_perfect <= 100

        # Zero score
        score_zero = await progress_service.calculate_mastery_score(
            db=test_db,
            user_id=user_id,
            chapter_id=chapter_id,
            correct_answers=0,
            total_questions=10,
            time_spent_seconds=1800
        )
        assert score_zero == 0

    @pytest.mark.asyncio
    async def test_time_based_bonus(self, test_db, test_user):
        """Test time-based mastery bonus."""
        user_id = test_user.user_id
        chapter_id = 4

        # Same correct answers, different times
        score_fast = await progress_service.calculate_mastery_score(
            db=test_db,
            user_id=user_id,
            chapter_id=chapter_id,
            correct_answers=7,
            total_questions=10,
            time_spent_seconds=900  # 15 minutes (fast)
        )

        score_slow = await progress_service.calculate_mastery_score(
            db=test_db,
            user_id=user_id,
            chapter_id=chapter_id,
            correct_answers=7,
            total_questions=10,
            time_spent_seconds=2400  # 40 minutes (slow)
        )

        # Fast completion should get higher score
        assert score_fast > score_slow

    @pytest.mark.asyncio
    async def test_practice_attempt_calculation(self, test_db, test_user):
        """Test practice attempts affect mastery."""
        user_id = test_user.user_id
        chapter_id = 5

        # Create progress with practice attempts
        progress = await progress_service.start_chapter(test_db, user_id, chapter_id)
        progress.practice_attempts = 2
        await test_db.commit()

        # Calculate score with practice attempts
        score = await progress_service.calculate_mastery_score(
            db=test_db,
            user_id=user_id,
            chapter_id=chapter_id,
            correct_answers=8,
            total_questions=10,
            time_spent_seconds=1500
        )

        # Should include practice efficiency bonus
        assert 80 <= score <= 100

    @pytest.mark.asyncio
    async def test_progress_percentage_calculation(self, test_db, test_user):
        """Test progress percentage calculation."""
        user_id = test_user.user_id

        # Complete 5 chapters
        for chapter_id in range(1, 6):
            await progress_service.complete_chapter(
                db=test_db,
                user_id=user_id,
                chapter_id=chapter_id,
                mastery_score=85
            )

        # Get progress summary
        summary = await progress_service.get_user_progress_summary(test_db, user_id)

        assert len(summary["chapters_completed"]) == 5
        assert summary["total_time"] >= 0

    @pytest.mark.asyncio
    async def test_xp_calculation(self, test_db, test_user):
        """Test XP calculation for chapter completion."""
        user_id = test_user.user_id
        chapter_id = 6

        # Award XP
        xp = await progress_service.award_xp_for_chapter(test_db, user_id, chapter_id)

        # Should be 50 points per chapter
        assert xp == 50

    @pytest.mark.asyncio
    async def test_path_progress_tracking(self, test_db, test_user):
        """Test learning path progress tracking."""
        from src.personalization.services.learning_path_service import create_learning_path

        user_id = test_user.user_id

        # Create learning path
        path = await create_learning_path(
            db=test_db,
            user_id=user_id,
            path_name="Test Path",
            chapters=[1, 2, 3, 4]
        )

        # Complete 2 chapters in path
        await progress_service.complete_chapter(test_db, user_id, 1, 80)
        await progress_service.complete_chapter(test_db, user_id, 2, 85)

        # Get progress
        summary = await progress_service.get_user_progress_summary(test_db, user_id)

        assert 1 in summary["chapters_completed"]
        assert 2 in summary["chapters_completed"]

    @pytest.mark.asyncio
    async def test_skill_level_update(self, test_db, test_user):
        """Test skill level updates after completion."""
        user_id = test_user.user_id

        # Complete chapters with different mastery
        await progress_service.complete_chapter(test_db, user_id, 1, 70)
        await progress_service.complete_chapter(test_db, user_id, 2, 80)
        await progress_service.complete_chapter(test_db, user_id, 3, 90)

        # Update skill level
        skill_level = await progress_service.update_skill_level(test_db, user_id)

        # Should be average: (70 + 80 + 90) / 3 = 80
        assert 75 <= skill_level <= 85

    @pytest.mark.asyncio
    async def test_update_time_spent(self, test_db, test_user):
        """Test updating time spent on chapter."""
        user_id = test_user.user_id
        chapter_id = 7

        # Start chapter
        await progress_service.start_chapter(test_db, user_id, chapter_id)

        # Update time (30 minutes)
        progress = await progress_service.update_time_spent(
            test_db, user_id, chapter_id, 1800
        )

        assert progress.time_spent_seconds == 1800

        # Update again (add 15 minutes)
        progress = await progress_service.update_time_spent(
            test_db, user_id, chapter_id, 900
        )

        assert progress.time_spent_seconds == 2700  # 30 + 15 minutes

    @pytest.mark.asyncio
    async def test_detect_chapter_from_conversation(self):
        """Test chapter detection from conversation text."""
        # Test various patterns
        assert progress_service.detect_chapter_from_conversation("I'm studying Chapter 5") == 5
        assert progress_service.detect_chapter_from_conversation("What is Ch 12 about?") == 12
        assert progress_service.detect_chapter_from_conversation("Tell me about chapter 22") == 22
        assert progress_service.detect_chapter_from_conversation("Ch. 1 is confusing") == 1

        # Test invalid
        assert progress_service.detect_chapter_from_conversation("No chapter here") is None
        assert progress_service.detect_chapter_from_conversation("Chapter 25") is None  # Out of range
        assert progress_service.detect_chapter_from_conversation("") is None

    @pytest.mark.asyncio
    async def test_get_learning_streak(self, test_db, test_user):
        """Test learning streak calculation."""
        user_id = test_user.user_id

        # Create progress on consecutive days
        now = datetime.utcnow()

        for i in range(5):
            progress = Progress(
                user_id=user_id,
                chapter_id=i + 1,
                completion_status="in_progress",
                time_spent_seconds=600,
                mastery_score=0,
                last_accessed_at=now - timedelta(days=i)
            )
            test_db.add(progress)

        await test_db.commit()

        # Get streak
        streak = await progress_service.get_learning_streak(test_db, user_id)

        assert streak >= 1  # At least 1 day streak

    @pytest.mark.asyncio
    async def test_get_chapter_progress(self, test_db, test_user):
        """Test getting progress for specific chapter."""
        user_id = test_user.user_id
        chapter_id = 8

        # Create progress
        await progress_service.start_chapter(test_db, user_id, chapter_id)

        # Get progress
        progress = await progress_service.get_chapter_progress(test_db, user_id, chapter_id)

        assert progress is not None
        assert progress.chapter_id == chapter_id
        assert progress.user_id == user_id

    @pytest.mark.asyncio
    async def test_estimated_completion_date(self, test_db, test_user):
        """Test estimated completion date calculation."""
        from src.personalization.services.learning_path_service import create_learning_path

        user_id = test_user.user_id

        # Create path
        path = await create_learning_path(
            test_db, user_id, "Test Path", [1, 2, 3, 4, 5]
        )

        # Complete some chapters
        await progress_service.complete_chapter(test_db, user_id, 1, 80, 1800)
        await progress_service.complete_chapter(test_db, user_id, 2, 85, 1500)

        # Get estimated completion
        est_date = await progress_service.calculate_estimated_completion_date(
            test_db, user_id, path.path_id
        )

        assert est_date is not None
        # Should be a valid ISO date string
        from datetime import date
        parsed_date = date.fromisoformat(est_date)
        assert parsed_date >= date.today()
