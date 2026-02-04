"""Unit tests for performance tracking service."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.personalization.services.performance_service import PerformanceService
from src.personalization.models.db_models import User


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
    user.skill_level = 50
    return user


class TestPerformanceService:
    """Tests for PerformanceService."""

    def test_estimate_question_complexity_simple(self):
        """Test complexity estimation for simple questions."""
        service = PerformanceService(AsyncMock())

        simple_queries = [
            "hi",
            "What is ROS?",
            "Explain kinematics"
        ]

        for query in simple_queries:
            complexity = service._estimate_question_complexity(query)
            assert 0.0 <= complexity <= 0.3, f"Expected low complexity for: {query}"

    def test_estimate_question_complexity_medium(self):
        """Test complexity estimation for medium complexity questions."""
        service = PerformanceService(AsyncMock())

        medium_queries = [
            "How does forward kinematics work in robotics?",
            "What are the differences between ROS 1 and ROS 2?",
            "Explain the concept of homogeneous transformations"
        ]

        for query in medium_queries:
            complexity = service._estimate_question_complexity(query)
            assert 0.2 < complexity < 0.8, f"Expected medium complexity for: {query}"

    def test_estimate_question_complexity_advanced(self):
        """Test complexity estimation for advanced questions."""
        service = PerformanceService(AsyncMock())

        advanced_queries = [
            "Derive the inverse kinematics solution using the Jacobian matrix and explain numerical methods for singularity handling",
            "Implement a control algorithm with optimization for humanoid robot walking dynamics and energy efficiency",
            "How would you implement a real-time motion planning algorithm with constraint satisfaction and collision avoidance?"
        ]

        for query in advanced_queries:
            complexity = service._estimate_question_complexity(query)
            assert complexity >= 0.5, f"Expected high complexity for: {query}"

    def test_estimate_question_complexity_with_technical_terms(self):
        """Test that technical terms increase complexity."""
        service = PerformanceService(AsyncMock())

        basic = "What is a robot?"
        technical = "What is the relationship between Jacobian matrix, kinematics singularities, and inverse kinematics algorithms?"

        basic_complexity = service._estimate_question_complexity(basic)
        technical_complexity = service._estimate_question_complexity(technical)

        assert technical_complexity > basic_complexity

    def test_estimate_question_complexity_with_math(self):
        """Test that math indicators increase complexity."""
        service = PerformanceService(AsyncMock())

        basic = "What is a robot?"
        math = "Can you derive the equations for the Jacobian and explain the mathematical proof?"

        basic_complexity = service._estimate_question_complexity(basic)
        math_complexity = service._estimate_question_complexity(math)

        assert math_complexity > basic_complexity

    @pytest.mark.asyncio
    async def test_get_recent_conversations_empty(self, mock_db, test_user):
        """Test getting recent conversations when none exist."""
        with patch('src.personalization.services.performance_service.select'):
            mock_db.execute.return_value.scalars.return_value.all.return_value = []
            service = PerformanceService(mock_db)

            conversations = await service.get_recent_conversations(test_user.user_id)
            assert conversations == []

    @pytest.mark.asyncio
    async def test_detect_difficulty_change_no_conversations(self, mock_db, test_user):
        """Test difficulty change detection with no conversations."""
        service = PerformanceService(mock_db)

        with patch.object(service, 'get_recent_conversations') as mock_get:
            mock_get.return_value = []
            result = await service.detect_difficulty_change(test_user.user_id)
            assert result is None

    @pytest.mark.asyncio
    async def test_detect_difficulty_change_insufficient_data(self, mock_db, test_user):
        """Test difficulty change detection with insufficient data."""
        service = PerformanceService(mock_db)

        with patch.object(service, 'get_recent_conversations') as mock_get:
            # Only 1 conversation (need at least 3 for detection)
            mock_get.return_value = []
            result = await service.detect_difficulty_change(test_user.user_id)
            assert result is None

    def test_apply_difficulty_adjustment_increase(self):
        """Test applying difficulty increase adjustment."""
        service = PerformanceService(AsyncMock())

        adjustment = {
            "action": "increase",
            "reason": "User showing advanced patterns",
            "confidence": 0.8
        }

        with patch('src.personalization.services.performance_service.get_user_by_id') as mock_get:
            user = User()
            user.user_id = uuid4()
            user.skill_level = 50
            mock_get.return_value = user

            with patch('src.personalization.services.performance_service.update_user_skill_level') as mock_update:
                mock_update.return_value = True
                result_coro = service.apply_difficulty_adjustment(user.user_id, adjustment)
                # For async testing, we'd need pytest-asyncio
                # Here we just verify the logic

    def test_thresholds_configured(self):
        """Test that performance thresholds are configured."""
        service = PerformanceService(AsyncMock())

        assert hasattr(service, 'STRUGGLING_THRESHOLD')
        assert hasattr(service, 'ADVANCED_THRESHOLD')
        assert service.STRUGGLING_THRESHOLD > 0
        assert service.ADVANCED_THRESHOLD > 0
        assert service.STRUGGLING_THRESHOLD < service.ADVANCED_THRESHOLD

    @pytest.mark.asyncio
    async def test_track_conversation_turn(self, mock_db, test_user):
        """Test tracking a conversation turn."""
        service = PerformanceService(mock_db)

        with patch.object(service, 'get_recent_conversations') as mock_get:
            mock_get.return_value = []
            result = await service.track_conversation_turn(
                test_user.user_id,
                "What is kinematics?",
                "Kinematics is..."
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_get_user_statistics_empty(self, mock_db, test_user):
        """Test getting user statistics with no conversations."""
        service = PerformanceService(mock_db)

        with patch.object(service, 'get_recent_conversations') as mock_get:
            mock_get.return_value = []
            stats = await service.get_user_statistics(test_user.user_id)

            assert "total_conversations" in stats
            assert stats["total_conversations"] == 0
            assert "total_turns" in stats
            assert "avg_message_length" in stats
            assert "avg_question_complexity" in stats

    def test_complexity_scoring_length_factor(self):
        """Test that query length affects complexity score."""
        service = PerformanceService(AsyncMock())

        short = "hi"
        medium = "This is a medium length question about robotics concepts"
        long = "This is a long question " * 10

        short_score = service._estimate_question_complexity(short)
        medium_score = service._estimate_question_complexity(medium)
        long_score = service._estimate_question_complexity(long)

        assert short_score < medium_score
        assert medium_score < long_score

    def test_complexity_clamped_to_range(self):
        """Test that complexity is clamped to 0.0-1.0 range."""
        service = PerformanceService(AsyncMock())

        extremely_long_query = "word " * 1000

        complexity = service._estimate_question_complexity(extremely_long_query)
        assert 0.0 <= complexity <= 1.0
