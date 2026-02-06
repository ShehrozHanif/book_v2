"""Privacy and GDPR compliance service for user data management."""

import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import (
    User,
    Progress,
    Achievement,
    PracticeAttempt,
    LearningPath,
)

logger = logging.getLogger(__name__)


class PrivacyService:
    """Service for privacy and GDPR compliance operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize privacy service.

        Args:
            db: Database session
        """
        self.db = db

    async def collect_user_data(self, user_id: UUID) -> Dict[str, Any]:
        """
        Collect all user data for export.

        Gathers data from multiple entities:
        - User profile and preferences
        - Learning progress per chapter
        - Achievements and badges
        - Practice attempts and scores
        - Learning paths and selections
        - User preferences settings

        Args:
            user_id: User ID to collect data for

        Returns:
            Dictionary containing all user data organized by category

        Raises:
            ValueError: If user not found
        """
        # Fetch user
        user_result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User {user_id} not found")

        # Fetch related data
        progress_result = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress_records = progress_result.scalars().all()

        achievements_result = await self.db.execute(
            select(Achievement).where(Achievement.user_id == user_id)
        )
        achievements = achievements_result.scalars().all()

        practice_result = await self.db.execute(
            select(PracticeAttempt).where(PracticeAttempt.user_id == user_id)
        )
        practice_attempts = practice_result.scalars().all()

        learning_paths_result = await self.db.execute(
            select(LearningPath).where(LearningPath.user_id == user_id)
        )
        learning_paths = learning_paths_result.scalars().all()

        # Compile comprehensive data export
        collected_data = {
            "export_date": datetime.utcnow().isoformat(),
            "export_version": "1.0",
            "user": self._serialize_user(user),
            "progress": [self._serialize_progress(p) for p in progress_records],
            "achievements": [self._serialize_achievement(a) for a in achievements],
            "practice_attempts": [self._serialize_practice_attempt(p) for p in practice_attempts],
            "learning_paths": [self._serialize_learning_path(lp) for lp in learning_paths],
            "summary": {
                "total_chapters_attempted": len(progress_records),
                "total_achievements": len(achievements),
                "total_practice_attempts": len(practice_attempts),
                "total_learning_paths": len(learning_paths),
                "avg_mastery": self._calculate_avg_mastery(progress_records),
                "total_time_hours": self._calculate_total_time(progress_records),
            }
        }

        logger.info(
            f"Collected user data export for {user_id}: "
            f"{len(progress_records)} chapters, "
            f"{len(achievements)} achievements, "
            f"{len(practice_attempts)} practice attempts"
        )

        return collected_data

    async def delete_user_account_cascading(self, user_id: UUID) -> bool:
        """
        Delete user account and all associated data (soft delete with cascading).

        This performs a cascading delete:
        1. Mark user as deleted
        2. Delete all related records (via cascade)
        3. Log the deletion for audit trail
        4. Return success status

        Args:
            user_id: User ID to delete

        Returns:
            True if deletion successful, False otherwise

        Raises:
            ValueError: If user not found
        """
        try:
            # Fetch user
            user_result = await self.db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {user_id} not found")

            # Delete all related records (cascade deletes)
            # Delete progress records
            await self.db.execute(
                select(Progress).where(Progress.user_id == user_id)
            )
            progress = (await self.db.execute(
                select(Progress).where(Progress.user_id == user_id)
            )).scalars().all()
            for p in progress:
                await self.db.delete(p)

            # Delete achievements
            achievements = (await self.db.execute(
                select(Achievement).where(Achievement.user_id == user_id)
            )).scalars().all()
            for a in achievements:
                await self.db.delete(a)

            # Delete practice attempts
            practice_attempts = (await self.db.execute(
                select(PracticeAttempt).where(PracticeAttempt.user_id == user_id)
            )).scalars().all()
            for pa in practice_attempts:
                await self.db.delete(pa)

            # Delete learning paths
            learning_paths = (await self.db.execute(
                select(LearningPath).where(LearningPath.user_id == user_id)
            )).scalars().all()
            for lp in learning_paths:
                await self.db.delete(lp)

            # Soft delete user (mark as deleted)
            user.is_deleted = True
            user.deleted_at = datetime.utcnow()

            await self.db.commit()

            logger.info(
                f"Successfully deleted account for user {user_id}: "
                f"deleted {len(progress)} progress records, "
                f"{len(achievements)} achievements, "
                f"{len(practice_attempts)} practice attempts"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to delete account for user {user_id}: {str(e)}")
            await self.db.rollback()
            return False

    async def anonymize_deleted_user_data(self, user_id: UUID) -> bool:
        """
        Anonymize data for deleted users (removes PII but keeps analytics).

        This is useful for GDPR "right to be forgotten" where analytics need
        to be preserved but personal information removed.

        Args:
            user_id: User ID to anonymize

        Returns:
            True if anonymization successful, False otherwise
        """
        try:
            user_result = await self.db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {user_id} not found")

            # Anonymize user data (keep ID for referential integrity)
            user.username = f"deleted_user_{user_id.hex[:8]}"
            user.email = f"deleted_{user_id.hex[:8]}@deleted.invalid"
            user.password_hash = None
            user.bio = None
            user.preferences_json = None

            await self.db.commit()

            logger.info(f"Anonymized data for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to anonymize user {user_id}: {str(e)}")
            await self.db.rollback()
            return False

    # ===== Helper Methods =====

    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Serialize user data for export."""
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "skill_level": user.skill_level,
            "skill_confidence": user.skill_confidence,
            "bio": user.bio,
            "is_deleted": user.is_deleted,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
        }

    def _serialize_progress(self, progress: Progress) -> Dict[str, Any]:
        """Serialize progress record for export."""
        return {
            "chapter_id": progress.chapter_id,
            "mastery_score": progress.mastery_score,
            "completion_status": progress.completion_status,
            "time_spent_seconds": progress.time_spent_seconds,
            "practice_attempts": progress.practice_attempts,
            "highest_practice_score": progress.highest_practice_score,
            "created_at": progress.created_at.isoformat() if progress.created_at else None,
            "updated_at": progress.updated_at.isoformat() if progress.updated_at else None,
        }

    def _serialize_achievement(self, achievement: Achievement) -> Dict[str, Any]:
        """Serialize achievement record for export."""
        return {
            "achievement_id": str(achievement.achievement_id),
            "achievement_type": achievement.achievement_type,
            "display_info": achievement.display_info_json,
            "earned_date": achievement.earned_date.isoformat() if achievement.earned_date else None,
        }

    def _serialize_practice_attempt(self, attempt: PracticeAttempt) -> Dict[str, Any]:
        """Serialize practice attempt for export."""
        return {
            "attempt_id": str(attempt.attempt_id),
            "chapter_id": attempt.chapter_id,
            "score": attempt.score,
            "questions": attempt.questions_json,
            "attempted_at": attempt.attempted_at.isoformat() if attempt.attempted_at else None,
        }

    def _serialize_learning_path(self, path: LearningPath) -> Dict[str, Any]:
        """Serialize learning path for export."""
        return {
            "path_id": str(path.path_id),
            "path_type": path.path_type,
            "difficulty": path.difficulty,
            "selected_at": path.selected_at.isoformat() if path.selected_at else None,
        }

    def _calculate_avg_mastery(self, progress_records: List[Progress]) -> Optional[float]:
        """Calculate average mastery score across all chapters."""
        if not progress_records:
            return None
        scores = [p.mastery_score for p in progress_records if p.mastery_score > 0]
        if not scores:
            return None
        return round(sum(scores) / len(scores), 1)

    def _calculate_total_time(self, progress_records: List[Progress]) -> float:
        """Calculate total time spent in hours."""
        total_seconds = sum(p.time_spent_seconds for p in progress_records)
        return round(total_seconds / 3600, 1)


async def get_privacy_service(db: AsyncSession) -> PrivacyService:
    """
    Get privacy service instance.

    Args:
        db: Database session

    Returns:
        PrivacyService instance
    """
    return PrivacyService(db)
