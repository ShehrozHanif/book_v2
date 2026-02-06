"""Service for adaptive difficulty adjustment based on user performance."""

import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import User
from src.personalization.services.user_service import get_user_by_id, update_user

logger = logging.getLogger(__name__)


class AdaptiveDifficultyService:
    """Service for tracking performance and adjusting difficulty."""

    def __init__(self, db: AsyncSession):
        """
        Initialize adaptive difficulty service.

        Args:
            db: Database session
        """
        self.db = db
        self.simplify_threshold = 3  # After 3 simplify requests, decrease skill
        self.advance_threshold = 5   # After 5 correct advanced answers, increase skill
        self.skill_adjustment = 10   # Points to adjust skill level

    async def track_simplify_request(self, user_id: UUID) -> Dict[str, Any]:
        """
        Track user requesting simplified response.

        Args:
            user_id: User ID

        Returns:
            Dictionary with updated skill level and adjustment info
        """
        user = await get_user_by_id(self.db, user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return {"success": False, "message": "User not found"}

        # Decrease skill level if pattern detected
        new_skill_level = max(0, user.skill_level - self.skill_adjustment)

        await update_user(
            self.db,
            user_id,
            {
                "skill_level": new_skill_level,
                "skill_confidence": max(0, user.skill_confidence - 10)
            }
        )

        logger.info(
            f"User {user_id} requested simplification: "
            f"skill {user.skill_level} → {new_skill_level}"
        )

        return {
            "success": True,
            "previous_skill_level": user.skill_level,
            "new_skill_level": new_skill_level,
            "adjustment": -self.skill_adjustment,
            "message": "Response difficulty adjusted to beginner level"
        }

    async def track_advanced_request(self, user_id: UUID) -> Dict[str, Any]:
        """
        Track user requesting more advanced content.

        Args:
            user_id: User ID

        Returns:
            Dictionary with updated skill level and adjustment info
        """
        user = await get_user_by_id(self.db, user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return {"success": False, "message": "User not found"}

        # Increase skill level if pattern detected
        new_skill_level = min(100, user.skill_level + self.skill_adjustment)

        await update_user(
            self.db,
            user_id,
            {
                "skill_level": new_skill_level,
                "skill_confidence": min(100, user.skill_confidence + 10)
            }
        )

        logger.info(
            f"User {user_id} requested advanced content: "
            f"skill {user.skill_level} → {new_skill_level}"
        )

        return {
            "success": True,
            "previous_skill_level": user.skill_level,
            "new_skill_level": new_skill_level,
            "adjustment": self.skill_adjustment,
            "message": "Response difficulty adjusted to advanced level"
        }

    async def update_skill_confidence(
        self,
        user_id: UUID,
        performance_metric: float
    ) -> Dict[str, Any]:
        """
        Update user's skill confidence based on performance.

        Args:
            user_id: User ID
            performance_metric: Performance score (0-100)

        Returns:
            Dictionary with updated confidence and skill level
        """
        user = await get_user_by_id(self.db, user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return {"success": False, "message": "User not found"}

        # Increase confidence if performance is high
        if performance_metric > 80:
            new_confidence = min(100, user.skill_confidence + 5)
        # Decrease confidence if performance is low
        elif performance_metric < 40:
            new_confidence = max(0, user.skill_confidence - 5)
        else:
            new_confidence = user.skill_confidence

        # Adjust skill level based on performance
        if performance_metric > 85:
            new_skill_level = min(100, user.skill_level + 5)
        elif performance_metric < 30:
            new_skill_level = max(0, user.skill_level - 5)
        else:
            new_skill_level = user.skill_level

        await update_user(
            self.db,
            user_id,
            {
                "skill_level": new_skill_level,
                "skill_confidence": new_confidence
            }
        )

        return {
            "success": True,
            "skill_level": new_skill_level,
            "skill_confidence": new_confidence,
            "performance": performance_metric
        }

    def get_recommended_difficulty(self, skill_level: int, skill_confidence: int) -> str:
        """
        Get recommended difficulty based on skill and confidence.

        Args:
            skill_level: User skill level (0-100)
            skill_confidence: User skill confidence (0-100)

        Returns:
            Recommended difficulty: 'beginner', 'intermediate', or 'advanced'
        """
        # If confidence is low, use lower difficulty
        if skill_confidence < 30:
            return "beginner"

        # Otherwise, map skill level to difficulty
        if skill_level < 30:
            return "beginner"
        elif skill_level < 70:
            return "intermediate"
        else:
            return "advanced"


async def get_adaptive_difficulty_service(db: AsyncSession) -> AdaptiveDifficultyService:
    """
    Get adaptive difficulty service instance.

    Args:
        db: Database session

    Returns:
        AdaptiveDifficultyService instance
    """
    return AdaptiveDifficultyService(db)
