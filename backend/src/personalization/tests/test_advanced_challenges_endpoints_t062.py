"""Tests for Advanced Challenges endpoints (T062)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import HTTPException

from src.personalization.api.routes.practice import get_advanced_challenges
from src.personalization.models.db_models import User


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_current_user():
    """Create mock current user."""
    user = MagicMock(spec=User)
    user.user_id = uuid4()
    return user


class TestGetAdvancedChallengesEndpoint:
    """Tests for get advanced challenges endpoint."""

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_eligible_user(self, mock_db, mock_current_user):
        """Test getting advanced challenges for eligible user."""
        user_id = mock_current_user.user_id
        chapter_id = 1

        mock_advanced_challenges = {
            "chapter_id": chapter_id,
            "user_mastery": 90,
            "advanced_questions": [
                {
                    "id": "q1_adv_1",
                    "question": "Advanced question",
                    "options": [
                        {"letter": "A", "text": "Option 1", "correct": True},
                        {"letter": "B", "text": "Option 2", "correct": False},
                        {"letter": "C", "text": "Option 3", "correct": False},
                        {"letter": "D", "text": "Option 4", "correct": False}
                    ],
                    "difficulty": "advanced"
                }
            ],
            "research_papers": [
                {
                    "id": "paper1_1",
                    "title": "Research Paper",
                    "authors": "Author",
                    "year": 2024,
                    "summary": "Summary",
                    "difficulty": "advanced",
                    "relevance_to_chapter": 0.95
                }
            ],
            "challenge_type": "advanced_mastery",
            "total_questions": 1,
            "total_papers": 1
        }

        with patch(
            "src.personalization.api.routes.practice.get_practice_service"
        ) as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_advanced_challenges.return_value = mock_advanced_challenges
            mock_get_service.return_value = mock_service

            result = await get_advanced_challenges(
                user_id=user_id,
                chapter_id=chapter_id,
                current_user=mock_current_user,
                db=mock_db
            )

            assert result["chapter_id"] == chapter_id
            assert result["user_mastery"] == 90
            assert "advanced_questions" in result
            assert "research_papers" in result
            assert result["challenge_type"] == "advanced_mastery"

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_ineligible_user(self, mock_db, mock_current_user):
        """Test getting advanced challenges for ineligible user (returns 404)."""
        user_id = mock_current_user.user_id
        chapter_id = 1

        with patch(
            "src.personalization.api.routes.practice.get_practice_service"
        ) as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_advanced_challenges.return_value = None
            mock_get_service.return_value = mock_service

            with pytest.raises(HTTPException) as exc_info:
                await get_advanced_challenges(
                    user_id=user_id,
                    chapter_id=chapter_id,
                    current_user=mock_current_user,
                    db=mock_db
                )

            assert exc_info.value.status_code == 404
            assert "not eligible" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_wrong_user(self, mock_db, mock_current_user):
        """Test getting advanced challenges with wrong user ID (403 Forbidden)."""
        wrong_user_id = uuid4()
        chapter_id = 1

        with pytest.raises(HTTPException) as exc_info:
            await get_advanced_challenges(
                user_id=wrong_user_id,
                chapter_id=chapter_id,
                current_user=mock_current_user,
                db=mock_db
            )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_invalid_chapter_low(self, mock_db, mock_current_user):
        """Test with invalid chapter ID (0)."""
        user_id = mock_current_user.user_id
        chapter_id = 0

        with pytest.raises(HTTPException) as exc_info:
            await get_advanced_challenges(
                user_id=user_id,
                chapter_id=chapter_id,
                current_user=mock_current_user,
                db=mock_db
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_invalid_chapter_high(self, mock_db, mock_current_user):
        """Test with invalid chapter ID (> 22)."""
        user_id = mock_current_user.user_id
        chapter_id = 23

        with pytest.raises(HTTPException) as exc_info:
            await get_advanced_challenges(
                user_id=user_id,
                chapter_id=chapter_id,
                current_user=mock_current_user,
                db=mock_db
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_response_format(self, mock_db, mock_current_user):
        """Test response has all required fields."""
        user_id = mock_current_user.user_id
        chapter_id = 1

        mock_advanced_challenges = {
            "chapter_id": chapter_id,
            "user_mastery": 88,
            "advanced_questions": [],
            "research_papers": [],
            "challenge_type": "advanced_mastery",
            "total_questions": 0,
            "total_papers": 0
        }

        with patch(
            "src.personalization.api.routes.practice.get_practice_service"
        ) as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_advanced_challenges.return_value = mock_advanced_challenges
            mock_get_service.return_value = mock_service

            result = await get_advanced_challenges(
                user_id=user_id,
                chapter_id=chapter_id,
                current_user=mock_current_user,
                db=mock_db
            )

            required_fields = [
                "chapter_id", "user_mastery", "advanced_questions",
                "research_papers", "challenge_type", "total_questions",
                "total_papers", "timestamp"
            ]
            for field in required_fields:
                assert field in result

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_chapter_2(self, mock_db, mock_current_user):
        """Test getting advanced challenges for chapter 2."""
        user_id = mock_current_user.user_id
        chapter_id = 2

        mock_advanced_challenges = {
            "chapter_id": chapter_id,
            "user_mastery": 87,
            "advanced_questions": [],
            "research_papers": [],
            "challenge_type": "advanced_mastery",
            "total_questions": 0,
            "total_papers": 0
        }

        with patch(
            "src.personalization.api.routes.practice.get_practice_service"
        ) as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_advanced_challenges.return_value = mock_advanced_challenges
            mock_get_service.return_value = mock_service

            result = await get_advanced_challenges(
                user_id=user_id,
                chapter_id=chapter_id,
                current_user=mock_current_user,
                db=mock_db
            )

            assert result["chapter_id"] == chapter_id

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_perfect_mastery(self, mock_db, mock_current_user):
        """Test with perfect 100% mastery."""
        user_id = mock_current_user.user_id
        chapter_id = 1

        mock_advanced_challenges = {
            "chapter_id": chapter_id,
            "user_mastery": 100,
            "advanced_questions": [],
            "research_papers": [],
            "challenge_type": "advanced_mastery",
            "total_questions": 0,
            "total_papers": 0
        }

        with patch(
            "src.personalization.api.routes.practice.get_practice_service"
        ) as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_advanced_challenges.return_value = mock_advanced_challenges
            mock_get_service.return_value = mock_service

            result = await get_advanced_challenges(
                user_id=user_id,
                chapter_id=chapter_id,
                current_user=mock_current_user,
                db=mock_db
            )

            assert result["user_mastery"] == 100

    @pytest.mark.asyncio
    async def test_get_advanced_challenges_service_error(self, mock_db, mock_current_user):
        """Test handling of service error."""
        user_id = mock_current_user.user_id
        chapter_id = 1

        with patch(
            "src.personalization.api.routes.practice.get_practice_service"
        ) as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_advanced_challenges.side_effect = Exception("Database error")
            mock_get_service.return_value = mock_service

            with pytest.raises(HTTPException) as exc_info:
                await get_advanced_challenges(
                    user_id=user_id,
                    chapter_id=chapter_id,
                    current_user=mock_current_user,
                    db=mock_db
                )

            assert exc_info.value.status_code == 500
            assert "Failed to get advanced challenges" in exc_info.value.detail
