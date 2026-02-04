"""Performance tracking service for detecting user skill changes and conversation patterns."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.personalization.services.user_service import (
    get_user_by_id,
    update_user_skill_level
)
from src.models.database import Conversation, Message

logger = logging.getLogger(__name__)


class PerformanceService:
    """Service for tracking user performance and adjusting difficulty."""

    # Heuristics for difficulty detection
    STRUGGLING_THRESHOLD = 0.3  # If >30% of recent messages are basic questions
    ADVANCED_THRESHOLD = 0.7    # If >70% of recent messages are complex questions

    def __init__(self, db: AsyncSession):
        """
        Initialize performance service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_recent_conversations(self,
                                      user_id: UUID,
                                      limit: int = 10) -> list:
        """
        Get recent conversations for a user.

        Args:
            user_id: User ID
            limit: Maximum number of conversations to retrieve

        Returns:
            List of recent conversations
        """
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .options(selectinload(Conversation.messages))
        )
        return result.scalars().all()

    def _estimate_question_complexity(self, query: str) -> float:
        """
        Estimate complexity of a question (0.0-1.0).

        Simple heuristic based on:
        - Query length (longer often means more complex)
        - Presence of technical terms
        - Presence of code-related keywords
        - Presence of mathematical symbols

        Args:
            query: User query text

        Returns:
            Complexity score (0.0-1.0)
        """
        score = 0.0

        # Length-based scoring
        if len(query) < 30:
            score += 0.1
        elif len(query) < 100:
            score += 0.3
        elif len(query) < 300:
            score += 0.6
        else:
            score += 1.0

        # Technical term detection
        technical_terms = [
            "algorithm", "implementation", "optimization", "architecture",
            "framework", "library", "API", "protocol", "synchronization",
            "kinematics", "dynamics", "control", "inverse", "forward",
            "quaternion", "matrix", "transformation", "jacobian"
        ]
        term_count = sum(1 for term in technical_terms if term.lower() in query.lower())
        score += min(0.3, term_count * 0.05)

        # Code-related keywords
        code_keywords = ["code", "implement", "algorithm", "function", "method"]
        has_code_keywords = any(kw in query.lower() for kw in code_keywords)
        if has_code_keywords:
            score += 0.2

        # Math-related indicators
        math_indicators = ["equation", "formula", "calculate", "derive", "proof", "theorem"]
        has_math = any(ind in query.lower() for ind in math_indicators)
        if has_math:
            score += 0.2

        return min(1.0, score)

    async def detect_difficulty_change(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Detect if user should have difficulty adjusted based on recent patterns.

        Args:
            user_id: User ID

        Returns:
            Dictionary with adjustment recommendation or None
            Format: {
                "action": "increase" | "decrease",
                "reason": str,
                "confidence": float (0.0-1.0)
            }
        """
        conversations = await self.get_recent_conversations(user_id, limit=10)
        if not conversations:
            return None

        # Collect complexity scores from recent messages
        complexity_scores = []
        for conv in conversations:
            if conv.messages:
                for msg in conv.messages[:1]:  # Just check user's messages
                    if msg.role == "user":
                        complexity = self._estimate_question_complexity(msg.content)
                        complexity_scores.append(complexity)

        if len(complexity_scores) < 3:
            return None

        avg_complexity = sum(complexity_scores) / len(complexity_scores)
        advanced_count = sum(1 for s in complexity_scores if s >= 0.7)
        struggling_count = sum(1 for s in complexity_scores if s <= 0.3)

        advanced_ratio = advanced_count / len(complexity_scores) if complexity_scores else 0
        struggling_ratio = struggling_count / len(complexity_scores) if complexity_scores else 0

        # Detect patterns
        if advanced_ratio >= self.ADVANCED_THRESHOLD:
            return {
                "action": "increase",
                "reason": f"User showing advanced question patterns ({advanced_ratio:.1%})",
                "confidence": min(advanced_ratio, 1.0)
            }
        elif struggling_ratio >= self.STRUGGLING_THRESHOLD:
            return {
                "action": "decrease",
                "reason": f"User showing basic question patterns ({struggling_ratio:.1%})",
                "confidence": min(struggling_ratio, 1.0)
            }

        return None

    async def apply_difficulty_adjustment(self,
                                         user_id: UUID,
                                         adjustment: Dict[str, Any],
                                         min_change: int = 5,
                                         max_change: int = 10) -> bool:
        """
        Apply difficulty adjustment to user's skill level.

        Args:
            user_id: User ID
            adjustment: Adjustment recommendation from detect_difficulty_change
            min_change: Minimum skill level change
            max_change: Maximum skill level change

        Returns:
            True if adjustment applied, False otherwise
        """
        user = await get_user_by_id(self.db, user_id)
        if not user:
            return False

        change_amount = int(min_change + (adjustment["confidence"] * (max_change - min_change)))

        if adjustment["action"] == "increase":
            new_skill_level = min(100, user.skill_level + change_amount)
        else:  # decrease
            new_skill_level = max(0, user.skill_level - change_amount)

        await update_user_skill_level(self.db, user_id, new_skill_level)

        logger.info(
            f"Difficulty adjustment for user {user_id}: "
            f"{user.skill_level} -> {new_skill_level} "
            f"({adjustment['action']}, confidence: {adjustment['confidence']:.1%})"
        )

        return True

    async def track_conversation_turn(self,
                                     user_id: UUID,
                                     query: str,
                                     response: str,
                                     conversation_id: Optional[UUID] = None) -> bool:
        """
        Track a conversation turn for performance analysis.

        Args:
            user_id: User ID
            query: User's query
            response: Bot's response
            conversation_id: Optional conversation ID

        Returns:
            True if tracking successful
        """
        # Estimate complexity of user's question
        complexity = self._estimate_question_complexity(query)

        logger.debug(
            f"Tracked conversation turn for user {user_id}: "
            f"complexity={complexity:.2f}, "
            f"conversation_id={conversation_id}"
        )

        # Check if difficulty adjustment is needed (every 10 turns)
        conversations = await self.get_recent_conversations(user_id, limit=1)
        if conversations and len(conversations[0].messages) % 10 == 0:
            adjustment = await self.detect_difficulty_change(user_id)
            if adjustment:
                await self.apply_difficulty_adjustment(user_id, adjustment)

        return True

    async def get_user_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get user performance statistics.

        Args:
            user_id: User ID

        Returns:
            Dictionary with performance metrics
        """
        conversations = await self.get_recent_conversations(user_id, limit=50)

        total_messages = sum(len(conv.messages) for conv in conversations)
        avg_message_length = sum(
            sum(len(msg.content) for msg in conv.messages)
            for conv in conversations
        ) / max(1, total_messages)

        complexity_scores = []
        for conv in conversations:
            for msg in conv.messages:
                if msg.role == "user":
                    complexity = self._estimate_question_complexity(msg.content)
                    complexity_scores.append(complexity)

        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0

        return {
            "total_conversations": len(conversations),
            "total_turns": total_messages,
            "avg_message_length": avg_message_length,
            "avg_question_complexity": avg_complexity,
            "recent_complexity_trend": complexity_scores[-10:] if complexity_scores else []
        }


async def get_performance_service(db: AsyncSession) -> PerformanceService:
    """
    Get performance service instance.

    Args:
        db: Database session

    Returns:
        PerformanceService instance
    """
    return PerformanceService(db)
