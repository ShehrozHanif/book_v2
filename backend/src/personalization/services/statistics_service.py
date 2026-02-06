"""Statistics service for learning analytics and progress visualization."""

import logging
import statistics as stats_module
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

    async def calculate_advanced_learning_curve(
        self,
        user_id: UUID,
        max_snapshots: int = 50
    ) -> Dict[str, Any]:
        """
        Calculate advanced learning curve with skill snapshots over time.

        Args:
            user_id: User ID
            max_snapshots: Maximum number of snapshots to include

        Returns:
            Dict with skill_snapshots and improvement metrics

        Metrics:
            - skill_snapshots: List of {timestamp, skill_level} pairs
            - improvement_rate_per_week: Points per week improvement
            - average_skill_level: Mean mastery score
            - skill_std_dev: Standard deviation of scores
            - trend: "improving", "plateau", "declining"
        """
        # Get user's progress sorted by chapter_id (proxy for time)
        result = await self.db.execute(
            select(Progress)
            .where(Progress.user_id == user_id)
            .order_by(Progress.chapter_id)
        )
        progress_records = list(result.scalars().all())

        if not progress_records:
            return {
                "skill_snapshots": [],
                "improvement_rate_per_week": 0.0,
                "average_skill_level": 0.0,
                "skill_std_dev": 0.0,
                "trend": "insufficient_data",
                "total_snapshots": 0
            }

        # Extract mastery scores
        mastery_scores = [p.mastery_score for p in progress_records if p.mastery_score >= 0]

        if not mastery_scores:
            return {
                "skill_snapshots": [],
                "improvement_rate_per_week": 0.0,
                "average_skill_level": 0.0,
                "skill_std_dev": 0.0,
                "trend": "insufficient_data",
                "total_snapshots": 0
            }

        # Calculate snapshots (limit to max_snapshots)
        step = max(1, len(progress_records) // max_snapshots) if len(progress_records) > max_snapshots else 1
        skill_snapshots = [
            {
                "timestamp": progress_records[i].created_at.isoformat() if progress_records[i].created_at else "",
                "skill_level": progress_records[i].mastery_score,
                "chapter_id": progress_records[i].chapter_id
            }
            for i in range(0, len(progress_records), step)
        ]

        # Calculate statistics
        avg_skill = stats_module.mean(mastery_scores)
        std_dev = stats_module.stdev(mastery_scores) if len(mastery_scores) > 1 else 0.0

        # Calculate improvement rate
        improvement_rate = self._calculate_improvement_rate(mastery_scores)

        # Detect trend
        trend = self._detect_trend(mastery_scores)

        return {
            "skill_snapshots": skill_snapshots,
            "improvement_rate_per_week": improvement_rate,
            "average_skill_level": round(avg_skill, 1),
            "skill_std_dev": round(std_dev, 2),
            "trend": trend,
            "total_snapshots": len(skill_snapshots)
        }

    async def detect_plateaus_and_regressions(
        self,
        user_id: UUID,
        plateau_threshold: int = 3,
        regression_threshold: float = 10.0
    ) -> Dict[str, Any]:
        """
        Detect learning plateaus and regressions in user's progress.

        Args:
            user_id: User ID
            plateau_threshold: Number of consecutive chapters with similar scores to detect plateau
            regression_threshold: Minimum point drop to detect regression

        Returns:
            Dict with plateau and regression analysis

        Metrics:
            - plateaus: List of {start_chapter, end_chapter, avg_score, duration}
            - regressions: List of {from_chapter, to_chapter, score_drop, severity}
            - current_status: "improving", "plateau", "regression"
        """
        # Get user's progress
        result = await self.db.execute(
            select(Progress)
            .where(Progress.user_id == user_id)
            .order_by(Progress.chapter_id)
        )
        progress_records = list(result.scalars().all())

        if len(progress_records) < plateau_threshold:
            return {
                "plateaus": [],
                "regressions": [],
                "current_status": "insufficient_data",
                "plateau_count": 0,
                "regression_count": 0
            }

        plateaus = self._find_plateaus(progress_records, plateau_threshold)
        regressions = self._find_regressions(progress_records, regression_threshold)

        # Determine current status
        if regressions:
            current_status = "regression"
        elif plateaus:
            current_status = "plateau"
        else:
            current_status = "improving"

        return {
            "plateaus": plateaus,
            "regressions": regressions,
            "current_status": current_status,
            "plateau_count": len(plateaus),
            "regression_count": len(regressions)
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

    def _calculate_improvement_rate(self, mastery_scores: List[int]) -> float:
        """
        Calculate weekly improvement rate.

        Args:
            mastery_scores: List of mastery scores over time

        Returns:
            Improvement rate (points per week)
        """
        if len(mastery_scores) < 2:
            return 0.0

        first_score = mastery_scores[0]
        last_score = mastery_scores[-1]
        total_improvement = last_score - first_score
        num_chapters = len(mastery_scores)

        # Assume 1 chapter per day = 7 chapters per week
        weeks_equivalent = num_chapters / 7.0
        if weeks_equivalent > 0:
            return round(total_improvement / weeks_equivalent, 2)
        return 0.0

    def _detect_trend(self, mastery_scores: List[int]) -> str:
        """
        Detect overall trend in mastery scores.

        Args:
            mastery_scores: List of mastery scores

        Returns:
            "improving", "declining", "plateau", or "insufficient_data"
        """
        if len(mastery_scores) < 3:
            return "insufficient_data"

        # Split into first third, middle third, last third
        third = len(mastery_scores) // 3
        if third == 0:
            return "insufficient_data"

        first_avg = stats_module.mean(mastery_scores[:third]) if third > 0 else mastery_scores[0]
        last_avg = stats_module.mean(mastery_scores[-third:]) if third > 0 else mastery_scores[-1]

        improvement = last_avg - first_avg

        if improvement > 5:
            return "improving"
        elif improvement < -5:
            return "declining"
        else:
            return "plateau"

    def _find_plateaus(
        self,
        progress_records: List,
        threshold: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find consecutive chapters with similar mastery scores (plateaus).

        Args:
            progress_records: List of progress records
            threshold: Number of consecutive similar scores to detect plateau

        Returns:
            List of plateau periods
        """
        plateaus = []
        plateau_start = 0
        plateau_scores = [progress_records[0].mastery_score]

        for i in range(1, len(progress_records)):
            current_score = progress_records[i].mastery_score
            prev_score = progress_records[i - 1].mastery_score

            # Check if scores are within 5 points (similar)
            if abs(current_score - prev_score) <= 5:
                plateau_scores.append(current_score)
            else:
                # Plateau ended, check if it was long enough
                if len(plateau_scores) >= threshold:
                    plateau_avg = stats_module.mean(plateau_scores)
                    plateaus.append({
                        "start_chapter": progress_records[plateau_start].chapter_id,
                        "end_chapter": progress_records[i - 1].chapter_id,
                        "avg_score": round(plateau_avg, 1),
                        "duration": len(plateau_scores)
                    })
                # Reset for new potential plateau
                plateau_start = i
                plateau_scores = [current_score]

        # Check last plateau
        if len(plateau_scores) >= threshold:
            plateau_avg = stats_module.mean(plateau_scores)
            plateaus.append({
                "start_chapter": progress_records[plateau_start].chapter_id,
                "end_chapter": progress_records[-1].chapter_id,
                "avg_score": round(plateau_avg, 1),
                "duration": len(plateau_scores)
            })

        return plateaus

    def _find_regressions(
        self,
        progress_records: List,
        threshold: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Find significant drops in mastery scores (regressions).

        Args:
            progress_records: List of progress records
            threshold: Minimum points drop to detect regression

        Returns:
            List of regression events
        """
        regressions = []

        for i in range(1, len(progress_records)):
            current_score = progress_records[i].mastery_score
            prev_score = progress_records[i - 1].mastery_score
            score_drop = prev_score - current_score

            if score_drop >= threshold:
                severity = "severe" if score_drop >= 20 else "moderate"
                regressions.append({
                    "from_chapter": progress_records[i - 1].chapter_id,
                    "to_chapter": progress_records[i].chapter_id,
                    "score_drop": score_drop,
                    "severity": severity,
                    "previous_score": prev_score,
                    "current_score": current_score
                })

        return regressions


async def get_statistics_service(db: AsyncSession) -> StatisticsService:
    """
    Get statistics service instance.

    Args:
        db: Database session

    Returns:
        StatisticsService instance
    """
    return StatisticsService(db)
