"""Chat integration service for linking conversations to chapters and tracking time (T043)."""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.services.progress_service import (
    detect_chapter_from_conversation,
    update_time_spent,
    get_chapter_progress
)

logger = logging.getLogger(__name__)


class ChatIntegrationService:
    """Service for integrating chat with progress tracking."""

    def __init__(self, db: AsyncSession):
        """
        Initialize chat integration service.

        Args:
            db: Database session
        """
        self.db = db
        self.current_chapter_context: Dict[UUID, int] = {}  # user_id -> chapter_id

    def detect_chapter_from_query(self, query: str) -> Optional[int]:
        """
        Detect chapter ID from user query.

        Args:
            query: User's query text

        Returns:
            Chapter ID (1-22) if detected, None otherwise

        Examples:
            - "What is Chapter 5 about?" -> 5
            - "Explain Ch 12" -> 12
            - "I'm working on chapter 3" -> 3
        """
        return detect_chapter_from_conversation(query)

    async def process_chat_message(
        self,
        user_id: UUID,
        query: str,
        conversation_id: Optional[UUID] = None,
        time_spent_seconds: int = 0
    ) -> Dict[str, Any]:
        """
        Process a chat message and link it to a chapter if detected.

        Args:
            user_id: User ID
            query: User's query text
            conversation_id: Optional conversation ID
            time_spent_seconds: Time spent on this interaction (seconds)

        Returns:
            Dict with:
            - detected_chapter: int or None
            - chapter_linked: bool
            - time_tracked: bool
            - context_maintained: bool
        """
        # Detect chapter from query
        detected_chapter = self.detect_chapter_from_query(query)

        result = {
            "detected_chapter": detected_chapter,
            "chapter_linked": False,
            "time_tracked": False,
            "context_maintained": False
        }

        # If chapter detected, update context and link
        if detected_chapter:
            self.current_chapter_context[user_id] = detected_chapter
            result["chapter_linked"] = True
            result["context_maintained"] = True

            # Track time if provided
            if time_spent_seconds > 0:
                try:
                    await update_time_spent(
                        self.db,
                        user_id,
                        detected_chapter,
                        time_spent_seconds
                    )
                    result["time_tracked"] = True
                    logger.info(
                        f"Tracked {time_spent_seconds}s for user {user_id} on chapter {detected_chapter}"
                    )
                except Exception as e:
                    logger.error(f"Failed to track time: {e}")

        # If no chapter detected but we have context, use previous chapter
        elif user_id in self.current_chapter_context:
            detected_chapter = self.current_chapter_context[user_id]
            result["detected_chapter"] = detected_chapter
            result["context_maintained"] = True

            # Track time on context chapter
            if time_spent_seconds > 0:
                try:
                    await update_time_spent(
                        self.db,
                        user_id,
                        detected_chapter,
                        time_spent_seconds
                    )
                    result["time_tracked"] = True
                except Exception as e:
                    logger.error(f"Failed to track time on context chapter: {e}")

        return result

    async def get_current_chapter_context(self, user_id: UUID) -> Optional[int]:
        """
        Get the current chapter context for a user.

        Args:
            user_id: User ID

        Returns:
            Current chapter ID or None
        """
        return self.current_chapter_context.get(user_id)

    def clear_chapter_context(self, user_id: UUID) -> None:
        """
        Clear chapter context for a user.

        Args:
            user_id: User ID
        """
        if user_id in self.current_chapter_context:
            del self.current_chapter_context[user_id]

    async def suggest_related_chapters(
        self,
        user_id: UUID,
        current_chapter: int
    ) -> list[int]:
        """
        Suggest related chapters based on current chapter.

        Args:
            user_id: User ID
            current_chapter: Current chapter ID

        Returns:
            List of related chapter IDs

        Logic:
            - Suggest previous and next chapters
            - Suggest chapters in same module
        """
        related = []

        # Previous and next chapters
        if current_chapter > 1:
            related.append(current_chapter - 1)
        if current_chapter < 22:
            related.append(current_chapter + 1)

        # Chapters in same module
        module_ranges = {
            1: (1, 6),
            2: (7, 12),
            3: (13, 18),
            4: (19, 22)
        }

        for module_num, (start, end) in module_ranges.items():
            if start <= current_chapter <= end:
                for ch in range(start, end + 1):
                    if ch != current_chapter and ch not in related:
                        related.append(ch)
                break

        return sorted(related)

    async def get_chapter_context_summary(
        self,
        user_id: UUID,
        chapter_id: int
    ) -> Dict[str, Any]:
        """
        Get summary of user's progress on a specific chapter.

        Args:
            user_id: User ID
            chapter_id: Chapter ID

        Returns:
            Dict with chapter progress summary
        """
        progress = await get_chapter_progress(self.db, user_id, chapter_id)

        if not progress:
            return {
                "chapter_id": chapter_id,
                "status": "not_started",
                "time_spent_minutes": 0,
                "mastery_score": 0,
                "practice_attempts": 0
            }

        return {
            "chapter_id": chapter_id,
            "status": progress.completion_status,
            "time_spent_minutes": round(progress.time_spent_seconds / 60, 1),
            "mastery_score": progress.mastery_score,
            "practice_attempts": progress.practice_attempts,
            "last_accessed": progress.last_accessed_at.isoformat() if progress.last_accessed_at else None
        }

    async def track_conversation_time(
        self,
        user_id: UUID,
        chapter_id: Optional[int],
        session_start: datetime,
        session_end: datetime
    ) -> bool:
        """
        Track time spent in a conversation session.

        Args:
            user_id: User ID
            chapter_id: Chapter ID (if detected)
            session_start: Session start time
            session_end: Session end time

        Returns:
            True if time tracked successfully
        """
        if not chapter_id:
            return False

        time_spent = int((session_end - session_start).total_seconds())

        if time_spent <= 0:
            return False

        try:
            await update_time_spent(
                self.db,
                user_id,
                chapter_id,
                time_spent
            )
            logger.info(
                f"Tracked conversation time: {time_spent}s for user {user_id} on chapter {chapter_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to track conversation time: {e}")
            return False


async def get_chat_integration_service(db: AsyncSession) -> ChatIntegrationService:
    """
    Get chat integration service instance.

    Args:
        db: Database session

    Returns:
        ChatIntegrationService instance
    """
    return ChatIntegrationService(db)
