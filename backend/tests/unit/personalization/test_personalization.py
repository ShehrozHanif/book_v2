"""Unit tests for personalization service."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.personalization.services.personalization_service import (
    PersonalizationService,
    DifficultyLevel,
    get_difficulty_level
)
from src.personalization.models.db_models import User


# Test fixtures
@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def user_beginner():
    """Create a beginner user."""
    user = User()
    user.user_id = uuid4()
    user.username = "beginner_user"
    user.email = "beginner@example.com"
    user.skill_level = 25
    user.preferences_json = {
        "explanation_style": "example_first",
        "code_language": "python",
        "learning_pace": "slow",
        "content_focus": "simulation"
    }
    return user


@pytest.fixture
def user_intermediate():
    """Create an intermediate user."""
    user = User()
    user.user_id = uuid4()
    user.username = "intermediate_user"
    user.email = "intermediate@example.com"
    user.skill_level = 50
    user.preferences_json = {
        "explanation_style": "theory_first",
        "code_language": "both",
        "learning_pace": "medium",
        "content_focus": "balanced"
    }
    return user


@pytest.fixture
def user_advanced():
    """Create an advanced user."""
    user = User()
    user.user_id = uuid4()
    user.username = "advanced_user"
    user.email = "advanced@example.com"
    user.skill_level = 85
    user.preferences_json = {
        "explanation_style": "theory_first",
        "code_language": "cpp",
        "learning_pace": "fast",
        "content_focus": "hardware"
    }
    return user


# Tests for difficulty level detection
class TestDifficultyLevel:
    """Tests for difficulty level detection."""

    def test_beginner_difficulty(self):
        """Test beginner difficulty level."""
        assert get_difficulty_level(0) == DifficultyLevel.BEGINNER
        assert get_difficulty_level(15) == DifficultyLevel.BEGINNER
        assert get_difficulty_level(29) == DifficultyLevel.BEGINNER

    def test_intermediate_difficulty(self):
        """Test intermediate difficulty level."""
        assert get_difficulty_level(30) == DifficultyLevel.INTERMEDIATE
        assert get_difficulty_level(50) == DifficultyLevel.INTERMEDIATE
        assert get_difficulty_level(69) == DifficultyLevel.INTERMEDIATE

    def test_advanced_difficulty(self):
        """Test advanced difficulty level."""
        assert get_difficulty_level(70) == DifficultyLevel.ADVANCED
        assert get_difficulty_level(85) == DifficultyLevel.ADVANCED
        assert get_difficulty_level(100) == DifficultyLevel.ADVANCED


# Tests for PersonalizationService
class TestPersonalizationService:
    """Tests for PersonalizationService."""

    @pytest.mark.asyncio
    async def test_get_user_context_anonymous(self, mock_db):
        """Test getting context for anonymous user."""
        service = PersonalizationService(mock_db)
        context = await service.get_user_context(None)

        assert context["authenticated"] is False
        assert context["skill_level"] == 50
        assert context["difficulty"] == DifficultyLevel.INTERMEDIATE
        assert "preferences" in context

    @pytest.mark.asyncio
    async def test_get_user_context_beginner(self, mock_db, user_beginner):
        """Test getting context for beginner user."""
        with patch('src.personalization.services.personalization_service.get_user_by_id') as mock_get:
            mock_get.return_value = user_beginner
            service = PersonalizationService(mock_db)
            context = await service.get_user_context(user_beginner.user_id)

            assert context["authenticated"] is True
            assert context["skill_level"] == 25
            assert context["difficulty"] == DifficultyLevel.BEGINNER
            assert context["preferences"]["explanation_style"] == "example_first"

    @pytest.mark.asyncio
    async def test_get_user_context_advanced(self, mock_db, user_advanced):
        """Test getting context for advanced user."""
        with patch('src.personalization.services.personalization_service.get_user_by_id') as mock_get:
            mock_get.return_value = user_advanced
            service = PersonalizationService(mock_db)
            context = await service.get_user_context(user_advanced.user_id)

            assert context["authenticated"] is True
            assert context["skill_level"] == 85
            assert context["difficulty"] == DifficultyLevel.ADVANCED
            assert context["preferences"]["code_language"] == "cpp"

    @pytest.mark.asyncio
    async def test_get_user_context_nonexistent(self, mock_db):
        """Test getting context for nonexistent user."""
        with patch('src.personalization.services.personalization_service.get_user_by_id') as mock_get:
            mock_get.return_value = None
            service = PersonalizationService(mock_db)
            context = await service.get_user_context(uuid4())

            assert context["authenticated"] is False
            assert context["skill_level"] == 50

    def test_generate_difficulty_prompt_beginner(self):
        """Test prompt generation for beginner."""
        service = PersonalizationService(AsyncMock())
        query = "What is kinematics?"
        preferences = {
            "explanation_style": "example_first",
            "code_language": "python",
            "learning_pace": "slow",
            "content_focus": "simulation"
        }

        prompt = service.generate_difficulty_prompt(query, DifficultyLevel.BEGINNER, preferences)

        assert "simple" in prompt.lower() or "beginner" in prompt.lower()
        assert "avoid mathematical" in prompt.lower() or "mathematical" in prompt.lower()
        assert "Start with concrete examples" in prompt
        assert "provide extra detail" in prompt.lower()
        assert "Python" in prompt
        assert "simulation" in prompt.lower()

    def test_generate_difficulty_prompt_intermediate(self):
        """Test prompt generation for intermediate."""
        service = PersonalizationService(AsyncMock())
        query = "Implement inverse kinematics"
        preferences = {
            "explanation_style": "theory_first",
            "code_language": "both",
            "learning_pace": "medium",
            "content_focus": "balanced"
        }

        prompt = service.generate_difficulty_prompt(query, DifficultyLevel.INTERMEDIATE, preferences)

        assert "balanced" in prompt.lower()
        assert "mathematical notation" in prompt.lower()
        assert "Start with theoretical" in prompt
        assert "code examples" in prompt.lower()

    def test_generate_difficulty_prompt_advanced(self):
        """Test prompt generation for advanced."""
        service = PersonalizationService(AsyncMock())
        query = "Derive Jacobian transformation matrices"
        preferences = {
            "explanation_style": "theory_first",
            "code_language": "cpp",
            "learning_pace": "fast",
            "content_focus": "hardware"
        }

        prompt = service.generate_difficulty_prompt(query, DifficultyLevel.ADVANCED, preferences)

        assert "rigorous" in prompt.lower()
        assert "mathematical derivations" in prompt.lower()
        assert "academic sources" in prompt.lower()
        assert "C++" in prompt
        assert "hardware" in prompt.lower()
        assert "concise" in prompt.lower()

    @pytest.mark.asyncio
    async def test_build_personalized_prompt_beginner(self, mock_db, user_beginner):
        """Test building personalized prompt for beginner."""
        with patch('src.personalization.services.personalization_service.get_user_by_id') as mock_get:
            mock_get.return_value = user_beginner
            service = PersonalizationService(mock_db)

            query = "What is kinematics?"
            context = "Kinematics is the study of motion..."

            prompt_data = await service.build_personalized_prompt(
                query, context, user_beginner.user_id
            )

            assert "system_prompt" in prompt_data
            assert "user_context" in prompt_data
            assert prompt_data["difficulty"] == DifficultyLevel.BEGINNER
            assert "Provide a simple" in prompt_data["system_prompt"]

    @pytest.mark.asyncio
    async def test_build_personalized_prompt_with_override(self, mock_db, user_beginner):
        """Test building personalized prompt with difficulty override."""
        with patch('src.personalization.services.personalization_service.get_user_by_id') as mock_get:
            mock_get.return_value = user_beginner
            service = PersonalizationService(mock_db)

            query = "What is kinematics?"
            context = "Kinematics is the study of motion..."

            prompt_data = await service.build_personalized_prompt(
                query, context, user_beginner.user_id, difficulty_override="advanced"
            )

            assert prompt_data["difficulty"] == DifficultyLevel.ADVANCED
            assert "rigorous" in prompt_data["system_prompt"].lower()

    @pytest.mark.asyncio
    async def test_build_personalized_prompt_simplify_override(self, mock_db, user_advanced):
        """Test simplify difficulty override."""
        with patch('src.personalization.services.personalization_service.get_user_by_id') as mock_get:
            mock_get.return_value = user_advanced
            service = PersonalizationService(mock_db)

            query = "Explain complex theory"
            context = "Complex context..."

            prompt_data = await service.build_personalized_prompt(
                query, context, user_advanced.user_id, difficulty_override="simplify"
            )

            assert prompt_data["difficulty"] == DifficultyLevel.BEGINNER
            assert "simple" in prompt_data["system_prompt"].lower()
