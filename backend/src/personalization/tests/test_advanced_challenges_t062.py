"""Unit tests for Advanced Challenges for High Mastery (T062)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.personalization.models.db_models import Progress
from src.personalization.services.practice_service import PracticeService


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock()


class TestAdvancedChallengesEligibility:
    """Tests for checking advanced challenges eligibility (mastery > 85%)."""

    @pytest.mark.asyncio
    async def test_check_eligibility_mastery_above_85(self, mock_db):
        """Test eligibility when mastery is above 85%."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=90, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        eligible = await service.check_advanced_challenges_eligibility(user_id, chapter_id)

        assert eligible is True

    @pytest.mark.asyncio
    async def test_check_eligibility_mastery_exactly_85(self, mock_db):
        """Test eligibility when mastery is exactly 85% (should be False - requires > 85)."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=85, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        eligible = await service.check_advanced_challenges_eligibility(user_id, chapter_id)

        assert eligible is False

    @pytest.mark.asyncio
    async def test_check_eligibility_mastery_below_85(self, mock_db):
        """Test eligibility when mastery is below 85%."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=75, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        eligible = await service.check_advanced_challenges_eligibility(user_id, chapter_id)

        assert eligible is False

    @pytest.mark.asyncio
    async def test_check_eligibility_no_progress_record(self, mock_db):
        """Test eligibility when user has no progress record."""
        user_id = uuid4()
        chapter_id = 1

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        eligible = await service.check_advanced_challenges_eligibility(user_id, chapter_id)

        assert eligible is False


class TestGetAdvancedChallenges:
    """Tests for retrieving advanced challenges."""

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_eligible_chapter_1(self, mock_db):
        """Test getting advanced challenges for eligible user on chapter 1."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=92, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        assert result is not None
        assert result["chapter_id"] == chapter_id
        assert result["user_mastery"] == 92
        assert "advanced_questions" in result
        assert "research_papers" in result
        assert result["challenge_type"] == "advanced_mastery"

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_ineligible(self, mock_db):
        """Test getting advanced challenges for ineligible user (mastery < 85%)."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=70, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_response_format(self, mock_db):
        """Test that response has all required fields."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=88, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        required_fields = [
            "chapter_id", "user_mastery", "advanced_questions",
            "research_papers", "challenge_type", "total_questions", "total_papers"
        ]
        for field in required_fields:
            assert field in result

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_questions_are_advanced(self, mock_db):
        """Test that returned questions have advanced difficulty level."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=90, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        # Should have advanced questions
        assert len(result["advanced_questions"]) > 0
        for question in result["advanced_questions"]:
            assert question.get("difficulty") == "advanced"
            assert "id" in question
            assert "question" in question
            assert "options" in question

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_papers_have_metadata(self, mock_db):
        """Test that research papers have required metadata."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=95, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        # Should have research papers
        assert len(result["research_papers"]) > 0
        for paper in result["research_papers"]:
            required_fields = ["id", "title", "authors", "year", "summary", "difficulty"]
            for field in required_fields:
                assert field in paper

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_chapter_2(self, mock_db):
        """Test getting advanced challenges for chapter 2."""
        user_id = uuid4()
        chapter_id = 2

        mock_progress = MagicMock(mastery_score=87, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        assert result is not None
        assert result["chapter_id"] == chapter_id

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_boundary_86_percent(self, mock_db):
        """Test getting advanced challenges at boundary (86% mastery - just above threshold)."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=86, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        assert result is not None
        assert result["user_mastery"] == 86

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_perfect_score(self, mock_db):
        """Test getting advanced challenges with perfect 100% mastery."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=100, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        assert result is not None
        assert result["user_mastery"] == 100


class TestAdvancedQuestionFormat:
    """Tests for advanced question format and structure."""

    @pytest.mark.asyncio
    async def test_advanced_questions_have_correct_options(self, mock_db):
        """Test that advanced questions have proper option structure."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=90, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        for question in result["advanced_questions"]:
            options = question.get("options", [])
            assert len(options) == 4
            for option in options:
                assert "letter" in option
                assert "text" in option
                assert "correct" in option

    @pytest.mark.asyncio
    async def test_advanced_questions_have_one_correct_answer(self, mock_db):
        """Test that each advanced question has exactly one correct answer."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=90, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result = await service.get_advanced_challenges(user_id, chapter_id)

        for question in result["advanced_questions"]:
            correct_count = sum(1 for opt in question.get("options", []) if opt.get("correct"))
            assert correct_count == 1


class TestAdvancedChallengesIntegration:
    """Integration tests for advanced challenges flow."""

    @pytest.mark.asyncio
    async def test_full_advanced_challenges_flow(self, mock_db):
        """Test complete flow from eligibility check to getting challenges."""
        user_id = uuid4()
        chapter_id = 1

        mock_progress = MagicMock(mastery_score=91, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)

        # Step 1: Check eligibility
        eligible = await service.check_advanced_challenges_eligibility(user_id, chapter_id)
        assert eligible is True

        # Step 2: Get advanced challenges
        challenges = await service.get_advanced_challenges(user_id, chapter_id)
        assert challenges is not None
        assert challenges["user_mastery"] == 91

    @pytest.mark.asyncio
    async def test_progression_from_low_to_high_mastery(self, mock_db):
        """Test that user becomes eligible after mastery improves."""
        user_id = uuid4()
        chapter_id = 1

        # Scenario 1: Low mastery
        mock_progress_low = MagicMock(mastery_score=70, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress_low
        mock_db.execute.return_value = mock_result

        service = PracticeService(mock_db)
        result_low = await service.get_advanced_challenges(user_id, chapter_id)
        assert result_low is None

        # Scenario 2: High mastery (after improvement)
        mock_progress_high = MagicMock(mastery_score=88, chapter_id=chapter_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress_high
        mock_db.execute.return_value = mock_result

        result_high = await service.get_advanced_challenges(user_id, chapter_id)
        assert result_high is not None

    @pytest.mark.asyncio
    async def test_multiple_chapters_advanced_challenges(self, mock_db):
        """Test getting advanced challenges for multiple chapters."""
        user_id = uuid4()

        for chapter_id in [1, 2]:
            mock_progress = MagicMock(mastery_score=90, chapter_id=chapter_id)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_progress
            mock_db.execute.return_value = mock_result

            service = PracticeService(mock_db)
            result = await service.get_advanced_challenges(user_id, chapter_id)

            assert result is not None
            assert result["chapter_id"] == chapter_id
