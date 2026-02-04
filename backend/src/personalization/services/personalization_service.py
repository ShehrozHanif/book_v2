"""Personalization service for adaptive difficulty and preference-aware responses."""

import logging
from typing import Dict, Any, Optional
from enum import Enum
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import User
from src.personalization.services.user_service import get_user_by_id

logger = logging.getLogger(__name__)


class DifficultyLevel(str, Enum):
    """Difficulty levels for response generation."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


def get_difficulty_level(skill_level: int) -> DifficultyLevel:
    """
    Determine difficulty level based on user skill level.

    Args:
        skill_level: User skill level (0-100)

    Returns:
        DifficultyLevel: Corresponding difficulty level
    """
    if skill_level < 30:
        return DifficultyLevel.BEGINNER
    elif skill_level < 70:
        return DifficultyLevel.INTERMEDIATE
    else:
        return DifficultyLevel.ADVANCED


class PersonalizationService:
    """Service for personalizing chat responses based on user profile."""

    def __init__(self, db: AsyncSession):
        """
        Initialize personalization service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_user_context(self, user_id: Optional[UUID]) -> Dict[str, Any]:
        """
        Get user context for personalization.

        Args:
            user_id: Optional user ID

        Returns:
            Dictionary with user context (skill_level, preferences, difficulty)
        """
        if not user_id:
            return {
                "authenticated": False,
                "skill_level": 50,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "preferences": {
                    "explanation_style": "example_first",
                    "code_language": "python",
                    "learning_pace": "medium",
                    "content_focus": "balanced"
                }
            }

        user = await get_user_by_id(self.db, user_id)
        if not user:
            return {
                "authenticated": False,
                "skill_level": 50,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "preferences": {
                    "explanation_style": "example_first",
                    "code_language": "python",
                    "learning_pace": "medium",
                    "content_focus": "balanced"
                }
            }

        difficulty = get_difficulty_level(user.skill_level)

        return {
            "authenticated": True,
            "user_id": str(user_id),
            "skill_level": user.skill_level,
            "difficulty": difficulty,
            "preferences": user.preferences_json or {
                "explanation_style": "example_first",
                "code_language": "python",
                "learning_pace": "medium",
                "content_focus": "balanced"
            }
        }

    def generate_difficulty_prompt(self,
                                   query: str,
                                   difficulty: DifficultyLevel,
                                   preferences: Dict[str, str]) -> str:
        """
        Generate a prompt modifier based on difficulty level and preferences.

        Args:
            query: Original user query
            difficulty: Difficulty level
            preferences: User preferences

        Returns:
            Modified prompt with difficulty and preference instructions
        """
        base_instructions = {
            DifficultyLevel.BEGINNER: (
                "Provide a simple, beginner-friendly explanation. "
                "Use analogies and everyday language. Avoid mathematical notation. "
                "Break concepts into small, easy-to-understand steps. "
                "Include a simple example if relevant."
            ),
            DifficultyLevel.INTERMEDIATE: (
                "Provide a balanced explanation with moderate depth. "
                "Include some mathematical notation where appropriate. "
                "Include code examples. Assume basic understanding of robotics concepts."
            ),
            DifficultyLevel.ADVANCED: (
                "Provide a rigorous, detailed explanation. "
                "Include mathematical derivations and formal definitions. "
                "Reference academic sources where appropriate. "
                "Assume strong background in robotics and programming. "
                "Include advanced code examples and optimizations."
            )
        }

        instructions = base_instructions.get(difficulty, base_instructions[DifficultyLevel.INTERMEDIATE])

        # Apply preference-based modifications
        style = preferences.get("explanation_style", "example_first")
        if style == "theory_first":
            instructions += " Start with theoretical concepts, then show examples."
        else:
            instructions += " Start with concrete examples, then explain the theory."

        pace = preferences.get("learning_pace", "medium")
        if pace == "slow":
            instructions += " Provide extra detail and explanations for each step."
        elif pace == "fast":
            instructions += " Be concise and skip lengthy derivations."

        code_language = preferences.get("code_language", "python")
        if code_language == "python":
            instructions += " Prefer Python for code examples."
        elif code_language == "cpp":
            instructions += " Prefer C++ for code examples."
        else:
            instructions += " Provide code examples in both Python and C++."

        focus = preferences.get("content_focus", "balanced")
        if focus == "simulation":
            instructions += " Focus on simulation and computational aspects."
        elif focus == "hardware":
            instructions += " Focus on hardware implementation and robotics."
        else:
            instructions += " Balance between simulation and hardware considerations."

        return f"{instructions}\n\nUser query: {query}"

    async def build_personalized_prompt(self,
                                       query: str,
                                       retrieved_context: str,
                                       user_id: Optional[UUID] = None,
                                       difficulty_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Build a personalized system prompt with context and difficulty.

        Args:
            query: User query
            retrieved_context: Retrieved textbook passages from RAG
            user_id: Optional user ID for personalization
            difficulty_override: Optional difficulty override ("simplify" or "advanced")

        Returns:
            Dictionary with personalized prompt and metadata
        """
        # Get user context
        context = await self.get_user_context(user_id)

        # Apply difficulty override if provided
        if difficulty_override == "simplify":
            context["difficulty"] = DifficultyLevel.BEGINNER
        elif difficulty_override == "advanced":
            context["difficulty"] = DifficultyLevel.ADVANCED

        # Generate difficulty-aware prompt
        difficulty_prompt = self.generate_difficulty_prompt(
            query,
            context["difficulty"],
            context["preferences"]
        )

        # Build system prompt
        system_prompt = (
            "You are a knowledgeable robotics assistant powered by a Humanoid Robotics textbook. "
            "Your role is to answer questions about robotics, ROS 2, and humanoid robots. "
            "Always cite the textbook when providing information. "
            "Be helpful, accurate, and adapt to the user's skill level. "
            "\n\n"
            f"{difficulty_prompt}"
            "\n\n"
            f"Relevant textbook context:\n{retrieved_context}"
        )

        return {
            "system_prompt": system_prompt,
            "user_context": context,
            "difficulty": context["difficulty"],
            "preferences": context["preferences"]
        }


async def get_personalization_service(db: AsyncSession) -> PersonalizationService:
    """
    Get personalization service instance.

    Args:
        db: Database session

    Returns:
        PersonalizationService instance
    """
    return PersonalizationService(db)
