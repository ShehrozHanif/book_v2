"""Statistics service for learning analytics and progress visualization."""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import Progress, PracticeAttempt, Achievement

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for computing and aggregating user learning statistics."""

    def __init__(self, db: AsyncSession):
        """
        Initialize statistics service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_time_heatmap(self, user_id: UUID) -> Dict[int, int]:
        """
        Get time spent per chapter as a heatmap.

        Args:
            user_id: User ID

        Returns:
            Dictionary mapping chapter_id to hours spent
        """
        progress_records = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        records = progress_records.scalars().all()

        heatmap = {}
        for record in records:
            hours = record.time_spent_seconds / 3600  # Convert to hours
            heatmap[record.chapter_id] = round(hours, 1)

        return heatmap

    async def get_mastery_per_chapter(self, user_id: UUID) -> Dict[int, int]:
        """
        Get mastery score per chapter.

        Args:
            user_id: User ID

        Returns:
            Dictionary mapping chapter_id to mastery score (0-100)
        """
        progress_records = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        records = progress_records.scalars().all()

        mastery = {}
        for record in records:
            mastery[record.chapter_id] = record.mastery_score

        return mastery

    async def get_learning_curve(self, user_id: UUID, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get learning curve showing mastery improvement over time.

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            List of {date, avg_mastery, chapters_completed} for each day
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        progress_records = await self.db.execute(
            select(Progress).where(
                (Progress.user_id == user_id) &
                (Progress.updated_at >= cutoff_date)
            )
        )
        records = progress_records.scalars().all()

        if not records:
            return []

        # Group by day
        daily_stats = {}
        for record in records:
            date_key = record.updated_at.date().isoformat()

            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "date": date_key,
                    "mastery_scores": [],
                    "completed_chapters": 0
                }

            daily_stats[date_key]["mastery_scores"].append(record.mastery_score)
            if record.completion_status == "completed":
                daily_stats[date_key]["completed_chapters"] += 1

        # Compute averages
        result = []
        for date_key in sorted(daily_stats.keys()):
            stats = daily_stats[date_key]
            avg_mastery = (
                sum(stats["mastery_scores"]) / len(stats["mastery_scores"])
                if stats["mastery_scores"]
                else 0
            )

            result.append({
                "date": date_key,
                "avg_mastery": round(avg_mastery, 1),
                "chapters_completed": stats["completed_chapters"]
            })

        return result

    async def get_recommended_focus_areas(self, user_id: UUID, threshold: int = 60) -> List[Dict[str, Any]]:
        """
        Get recommended chapters for focus based on low mastery.

        Args:
            user_id: User ID
            threshold: Mastery threshold below which to recommend focus

        Returns:
            List of {chapter_id, mastery_score, reason} sorted by mastery
        """
        progress_records = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        records = progress_records.scalars().all()

        low_mastery = [
            {
                "chapter_id": r.chapter_id,
                "mastery_score": r.mastery_score,
                "completion_status": r.completion_status,
                "time_spent_hours": round(r.time_spent_seconds / 3600, 1),
                "reason": (
                    "Not completed" if r.completion_status != "completed" else
                    f"Low mastery ({r.mastery_score}%)"
                )
            }
            for r in records
            if r.mastery_score < threshold or r.completion_status != "completed"
        ]

        # Sort by mastery score ascending (lowest first)
        return sorted(low_mastery, key=lambda x: x["mastery_score"])

    async def get_overall_progress(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get overall learning progress statistics.

        Args:
            user_id: User ID

        Returns:
            Dictionary with comprehensive progress metrics
        """
        progress_records = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        records = progress_records.scalars().all()

        if not records:
            return {
                "total_chapters": 22,
                "chapters_started": 0,
                "chapters_in_progress": 0,
                "chapters_completed": 0,
                "completion_percentage": 0,
                "avg_mastery": 0,
                "total_time_hours": 0,
                "total_practice_attempts": 0,
                "avg_practice_score": 0
            }

        # Calculate statistics
        total_chapters = len(records)
        started = sum(1 for r in records if r.completion_status != "not_started")
        in_progress = sum(1 for r in records if r.completion_status == "in_progress")
        completed = sum(1 for r in records if r.completion_status == "completed")

        avg_mastery = (
            sum(r.mastery_score for r in records) / total_chapters
            if total_chapters
            else 0
        )

        total_time_hours = (
            sum(r.time_spent_seconds for r in records) / 3600
            if records
            else 0
        )

        total_practice_attempts = sum(r.practice_attempts for r in records)
        avg_practice_score = (
            sum(r.highest_practice_score for r in records if r.highest_practice_score > 0) /
            sum(1 for r in records if r.highest_practice_score > 0)
            if any(r.highest_practice_score > 0 for r in records)
            else 0
        )

        return {
            "total_chapters": total_chapters,
            "chapters_started": started,
            "chapters_in_progress": in_progress,
            "chapters_completed": completed,
            "completion_percentage": int((completed / total_chapters) * 100) if total_chapters else 0,
            "avg_mastery": round(avg_mastery, 1),
            "total_time_hours": round(total_time_hours, 1),
            "total_practice_attempts": total_practice_attempts,
            "avg_practice_score": round(avg_practice_score, 1)
        }

    async def get_achievements_summary(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get achievement statistics for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with achievement statistics
        """
        achievements = await self.db.execute(
            select(Achievement).where(Achievement.user_id == user_id)
        )
        records = achievements.scalars().all()

        if not records:
            return {
                "total_earned": 0,
                "total_points": 0,
                "achievements_by_category": {}
            }

        category_counts = {}
        total_points = 0

        for achievement in records:
            category = achievement.display_info_json.get("category", "other")
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
            total_points += achievement.display_info_json.get("points", 0)

        return {
            "total_earned": len(records),
            "total_points": total_points,
            "achievements_by_category": category_counts,
            "recent_achievements": [
                {
                    "type": a.achievement_type,
                    "title": a.display_info_json.get("title"),
                    "earned_date": a.earned_date.isoformat() if a.earned_date else None
                }
                for a in sorted(records, key=lambda a: a.earned_date or datetime.min, reverse=True)[:5]
            ]
        }

    async def get_comprehensive_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive user statistics for dashboard.

        Args:
            user_id: User ID

        Returns:
            Dictionary with all statistics
        """
        overall = await self.get_overall_progress(user_id)
        mastery = await self.get_mastery_per_chapter(user_id)
        heatmap = await self.get_time_heatmap(user_id)
        curve = await self.get_learning_curve(user_id)
        focus_areas = await self.get_recommended_focus_areas(user_id)
        achievements = await self.get_achievements_summary(user_id)

        return {
            "overall_progress": overall,
            "mastery_by_chapter": mastery,
            "time_spent_heatmap": heatmap,
            "learning_curve": curve,
            "recommended_focus_areas": focus_areas,
            "achievements": achievements,
            "generated_at": datetime.utcnow().isoformat()
        }


async def get_statistics_service(db: AsyncSession) -> StatisticsService:
    """
    Get statistics service instance.

    Args:
        db: Database session

    Returns:
        StatisticsService instance
    """
    return StatisticsService(db)
