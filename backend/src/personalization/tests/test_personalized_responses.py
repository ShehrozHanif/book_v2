"""Integration tests for personalized chat responses based on skill level and preferences."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.services.personalization_service import (
    PersonalizationService, DifficultyLevel, get_difficulty_level
)
from src.personalization.models.db_models import User


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def beginner_user():
    """Create a beginner skill level user."""
    return User(
        user_id=uuid4(),
        username="beginner_learner",
        email="beginner@example.com",
        password_hash="hashed",
        skill_level=25,
        skill_confidence=30,
        preferences_json={
            "explanation_style": "example_first",
            "code_language": "python",
            "learning_pace": "slow",
            "content_focus": "balanced"
        }
    )


@pytest.fixture
def intermediate_user():
    """Create an intermediate skill level user."""
    return User(
        user_id=uuid4(),
        username="intermediate_learner",
        email="intermediate@example.com",
        password_hash="hashed",
        skill_level=50,
        skill_confidence=50,
        preferences_json={
            "explanation_style": "theory_first",
            "code_language": "python",
            "learning_pace": "medium",
            "content_focus": "simulation"
        }
    )


@pytest.fixture
def advanced_user():
    """Create an advanced skill level user."""
    return User(
        user_id=uuid4(),
        username="advanced_learner",
        email="advanced@example.com",
        password_hash="hashed",
        skill_level=85,
        skill_confidence=90,
        preferences_json={
            "explanation_style": "theory_first",
            "code_language": "cpp",
            "learning_pace": "fast",
            "content_focus": "hardware"
        }
    )


class TestDifficultyLevelMapping:
    """Test difficulty level mapping based on skill score."""

    def test_beginner_difficulty_threshold(self):
        """Test that skill < 30 maps to beginner."""
        assert get_difficulty_level(0) == DifficultyLevel.BEGINNER
        assert get_difficulty_level(15) == DifficultyLevel.BEGINNER
        assert get_difficulty_level(29) == DifficultyLevel.BEGINNER

    def test_intermediate_difficulty_threshold(self):
        """Test that 30 <= skill < 70 maps to intermediate."""
        assert get_difficulty_level(30) == DifficultyLevel.INTERMEDIATE
        assert get_difficulty_level(50) == DifficultyLevel.INTERMEDIATE
        assert get_difficulty_level(69) == DifficultyLevel.INTERMEDIATE

    def test_advanced_difficulty_threshold(self):
        """Test that skill >= 70 maps to advanced."""
        assert get_difficulty_level(70) == DifficultyLevel.ADVANCED
        assert get_difficulty_level(85) == DifficultyLevel.ADVANCED
        assert get_difficulty_level(100) == DifficultyLevel.ADVANCED


class TestPersonalizationService:
    """Test personalization service functionality."""

    @pytest.mark.asyncio
    async def test_get_user_context_unauthenticated(self, mock_db):
        """Test get_user_context for anonymous users."""
        service = PersonalizationService(mock_db)

        context = await service.get_user_context(None)

        assert context["authenticated"] is False
        assert context["skill_level"] == 50  # Default intermediate
        assert context["difficulty"] == DifficultyLevel.INTERMEDIATE
        assert context["preferences"]["code_language"] == "python"

    @pytest.mark.asyncio
    async def test_get_user_context_beginner(self, mock_db, beginner_user):
        """Test get_user_context for beginner user."""
        with patch(
            "src.personalization.services.personalization_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=beginner_user
        ):
            service = PersonalizationService(mock_db)
            context = await service.get_user_context(beginner_user.user_id)

            assert context["authenticated"] is True
            assert context["skill_level"] == 25
            assert context["difficulty"] == DifficultyLevel.BEGINNER
            assert context["preferences"]["learning_pace"] == "slow"

    @pytest.mark.asyncio
    async def test_get_user_context_advanced(self, mock_db, advanced_user):
        """Test get_user_context for advanced user."""
        with patch(
            "src.personalization.services.personalization_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=advanced_user
        ):
            service = PersonalizationService(mock_db)
            context = await service.get_user_context(advanced_user.user_id)

            assert context["authenticated"] is True
            assert context["skill_level"] == 85
            assert context["difficulty"] == DifficultyLevel.ADVANCED
            assert context["preferences"]["code_language"] == "cpp"

    def test_generate_difficulty_prompt_beginner(self, mock_db, beginner_user):
        """Test prompt generation for beginner."""
        service = PersonalizationService(mock_db)

        prompt = service.generate_difficulty_prompt(
            query="What is kinematics?",
            difficulty=DifficultyLevel.BEGINNER,
            preferences=beginner_user.preferences_json
        )

        assert "simple" in prompt.lower() or "beginner" in prompt.lower()
        assert "analogies" in prompt.lower()
        assert "example" in prompt.lower()
        assert "What is kinematics?" in prompt

    def test_generate_difficulty_prompt_advanced(self, mock_db, advanced_user):
        """Test prompt generation for advanced."""
        service = PersonalizationService(mock_db)

        prompt = service.generate_difficulty_prompt(
            query="What is inverse kinematics?",
            difficulty=DifficultyLevel.ADVANCED,
            preferences=advanced_user.preferences_json
        )

        assert "rigorous" in prompt.lower() or "mathematical" in prompt.lower()
        assert "derive" in prompt.lower() or "derivation" in prompt.lower()
        assert "academic" in prompt.lower() or "research" in prompt.lower()

    def test_generate_prompt_respects_explanation_style(self, mock_db):
        """Test that prompt respects explanation style preference."""
        service = PersonalizationService(mock_db)

        # Theory first
        theory_first_prefs = {
            "explanation_style": "theory_first",
            "code_language": "python",
            "learning_pace": "medium",
            "content_focus": "balanced"
        }
        prompt = service.generate_difficulty_prompt(
            "Explain dynamics",
            DifficultyLevel.INTERMEDIATE,
            theory_first_prefs
        )
        assert "theoretical" in prompt.lower() or "theory" in prompt.lower()

        # Example first
        example_first_prefs = {
            "explanation_style": "example_first",
            "code_language": "python",
            "learning_pace": "medium",
            "content_focus": "balanced"
        }
        prompt = service.generate_difficulty_prompt(
            "Explain dynamics",
            DifficultyLevel.INTERMEDIATE,
            example_first_prefs
        )
        assert "example" in prompt.lower()

    def test_generate_prompt_respects_code_language(self, mock_db):
        """Test that prompt respects code language preference."""
        service = PersonalizationService(mock_db)

        python_prefs = {
            "explanation_style": "example_first",
            "code_language": "python",
            "learning_pace": "medium",
            "content_focus": "balanced"
        }
        python_prompt = service.generate_difficulty_prompt(
            "Show ROS example",
            DifficultyLevel.INTERMEDIATE,
            python_prefs
        )
        assert "python" in python_prompt.lower()

        cpp_prefs = {
            "explanation_style": "example_first",
            "code_language": "cpp",
            "learning_pace": "medium",
            "content_focus": "balanced"
        }
        cpp_prompt = service.generate_difficulty_prompt(
            "Show ROS example",
            DifficultyLevel.INTERMEDIATE,
            cpp_prefs
        )
        assert "c++" in cpp_prompt.lower()

    def test_generate_prompt_respects_learning_pace(self, mock_db):
        """Test that prompt respects learning pace preference."""
        service = PersonalizationService(mock_db)

        slow_prefs = {
            "explanation_style": "example_first",
            "code_language": "python",
            "learning_pace": "slow",
            "content_focus": "balanced"
        }
        slow_prompt = service.generate_difficulty_prompt(
            "Explain ROS",
            DifficultyLevel.INTERMEDIATE,
            slow_prefs
        )
        assert "extra detail" in slow_prompt.lower() or "verbose" in slow_prompt.lower()

        fast_prefs = {
            "explanation_style": "example_first",
            "code_language": "python",
            "learning_pace": "fast",
            "content_focus": "balanced"
        }
        fast_prompt = service.generate_difficulty_prompt(
            "Explain ROS",
            DifficultyLevel.INTERMEDIATE,
            fast_prefs
        )
        assert "concise" in fast_prompt.lower()

    @pytest.mark.asyncio
    async def test_build_personalized_prompt_beginner(self, mock_db, beginner_user):
        """Test building personalized prompt for beginner user."""
        with patch(
            "src.personalization.services.personalization_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=beginner_user
        ):
            service = PersonalizationService(mock_db)

            result = await service.build_personalized_prompt(
                query="What is kinematics?",
                retrieved_context="Kinematics is the study of motion...",
                user_id=beginner_user.user_id,
                difficulty_override=None
            )

            assert "system_prompt" in result
            assert "user_context" in result
            assert "difficulty" in result
            assert result["difficulty"] == DifficultyLevel.BEGINNER
            assert "kinematics" in result["system_prompt"].lower()

    @pytest.mark.asyncio
    async def test_difficulty_override_simplify(self, mock_db, advanced_user):
        """Test difficulty override to simplify."""
        with patch(
            "src.personalization.services.personalization_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=advanced_user
        ):
            service = PersonalizationService(mock_db)

            # User is advanced but wants to simplify
            result = await service.build_personalized_prompt(
                query="Explain kinematics",
                retrieved_context="Kinematics definition...",
                user_id=advanced_user.user_id,
                difficulty_override="simplify"
            )

            assert result["difficulty"] == DifficultyLevel.BEGINNER

    @pytest.mark.asyncio
    async def test_difficulty_override_advanced(self, mock_db, beginner_user):
        """Test difficulty override to advanced."""
        with patch(
            "src.personalization.services.personalization_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=beginner_user
        ):
            service = PersonalizationService(mock_db)

            # User is beginner but wants to try advanced
            result = await service.build_personalized_prompt(
                query="Explain kinematics",
                retrieved_context="Kinematics definition...",
                user_id=beginner_user.user_id,
                difficulty_override="advanced"
            )

            assert result["difficulty"] == DifficultyLevel.ADVANCED

    @pytest.mark.asyncio
    async def test_personalization_context_in_system_prompt(self, mock_db, intermediate_user):
        """Test that personalization context is included in system prompt."""
        with patch(
            "src.personalization.services.personalization_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=intermediate_user
        ):
            service = PersonalizationService(mock_db)

            result = await service.build_personalized_prompt(
                query="What is dynamics?",
                retrieved_context="Dynamics is...",
                user_id=intermediate_user.user_id
            )

            system_prompt = result["system_prompt"]
            assert "Humanoid Robotics" in system_prompt
            assert ("educational assistant" in system_prompt or
                    "robotics assistant" in system_prompt)
