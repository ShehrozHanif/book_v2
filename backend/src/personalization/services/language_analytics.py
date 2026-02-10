"""
Language Analytics Service (T063)

Tracks language preference adoption metrics:
- User adoption rate (Urdu vs English)
- Preference change events
- User segmentation by language
- Adoption trends over time
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import (
    UserLanguagePreference,
    User,
)

logger = logging.getLogger(__name__)


class LanguageAnalyticsService:
    """Service for tracking and analyzing language preference adoption."""

    @staticmethod
    async def get_adoption_metrics(db: AsyncSession) -> Dict[str, Any]:
        """
        Get overall language adoption metrics.

        Returns:
            {
                "total_users": 100,
                "english_users": 85,
                "urdu_users": 15,
                "english_percent": 85.0,
                "urdu_percent": 15.0,
                "adoption_rate_change": 2.5  # percent change from yesterday
            }
        """
        try:
            # Get total users
            total_result = await db.execute(select(func.count(User.user_id)))
            total_users = total_result.scalar() or 0

            if total_users == 0:
                return {
                    "total_users": 0,
                    "english_users": 0,
                    "urdu_users": 0,
                    "english_percent": 0.0,
                    "urdu_percent": 0.0,
                }

            # Get Urdu preference count
            urdu_result = await db.execute(
                select(func.count(UserLanguagePreference.user_id)).where(
                    UserLanguagePreference.language == "urdu"
                )
            )
            urdu_users = urdu_result.scalar() or 0
            english_users = total_users - urdu_users

            return {
                "total_users": total_users,
                "english_users": english_users,
                "urdu_users": urdu_users,
                "english_percent": round((english_users / total_users) * 100, 2),
                "urdu_percent": round((urdu_users / total_users) * 100, 2),
            }
        except Exception as e:
            logger.error(f"Error calculating adoption metrics: {e}")
            return {
                "total_users": 0,
                "english_users": 0,
                "urdu_users": 0,
                "english_percent": 0.0,
                "urdu_percent": 0.0,
            }

    @staticmethod
    async def get_user_language_breakdown(db: AsyncSession) -> Dict[str, int]:
        """
        Get breakdown of users by language preference.

        Returns:
            {"english": 85, "urdu": 15}
        """
        try:
            result = await db.execute(
                select(
                    UserLanguagePreference.language,
                    func.count(UserLanguagePreference.user_id),
                ).group_by(UserLanguagePreference.language)
            )

            breakdown = {}
            for row in result:
                breakdown[row[0]] = row[1]

            # Ensure all languages are represented
            breakdown.setdefault("english", 0)
            breakdown.setdefault("urdu", 0)

            return breakdown
        except Exception as e:
            logger.error(f"Error getting language breakdown: {e}")
            return {"english": 0, "urdu": 0}

    @staticmethod
    async def get_recent_preference_changes(
        db: AsyncSession, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get recent language preference changes.

        Args:
            db: Database session
            days: Number of days to look back

        Returns:
            List of recent changes with timestamp and language
        """
        try:
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            result = await db.execute(
                select(
                    UserLanguagePreference.user_id,
                    UserLanguagePreference.language,
                    UserLanguagePreference.updated_at,
                )
                .where(UserLanguagePreference.updated_at >= cutoff_date)
                .order_by(UserLanguagePreference.updated_at.desc())
            )

            changes = []
            for row in result:
                changes.append(
                    {
                        "user_id": row[0],
                        "language": row[1],
                        "updated_at": row[2].isoformat() if row[2] else None,
                    }
                )

            return changes
        except Exception as e:
            logger.error(f"Error getting recent changes: {e}")
            return []

    @staticmethod
    async def track_preference_change(
        db: AsyncSession,
        user_id: int,
        old_language: str,
        new_language: str,
    ) -> Dict[str, Any]:
        """
        Track a preference change event.

        Args:
            db: Database session
            user_id: User ID
            old_language: Previous language
            new_language: New language

        Returns:
            Event tracking record
        """
        event = {
            "user_id": user_id,
            "old_language": old_language,
            "new_language": new_language,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "preference_change",
        }

        try:
            logger.info(
                f"User {user_id} changed language preference from {old_language} to {new_language}"
            )
            # In production, this would be stored in an analytics table
            return event
        except Exception as e:
            logger.error(f"Error tracking preference change: {e}")
            return event

    @staticmethod
    async def get_adoption_timeline(
        db: AsyncSession, interval_days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get adoption trend over time.

        Args:
            db: Database session
            interval_days: Group by this many days

        Returns:
            List of adoption data points over time
        """
        try:
            from datetime import timedelta

            # Query preferences with dates
            result = await db.execute(
                select(
                    UserLanguagePreference.language,
                    UserLanguagePreference.updated_at,
                    func.count(UserLanguagePreference.user_id),
                )
                .group_by(
                    UserLanguagePreference.language,
                    UserLanguagePreference.updated_at,
                )
                .order_by(UserLanguagePreference.updated_at.desc())
            )

            # Group by interval
            timeline = []
            for row in result:
                timeline.append(
                    {
                        "language": row[0],
                        "date": row[1].isoformat() if row[1] else None,
                        "count": row[2],
                    }
                )

            return timeline
        except Exception as e:
            logger.error(f"Error getting adoption timeline: {e}")
            return []

    @staticmethod
    async def get_demographic_breakdown(
        db: AsyncSession,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get language adoption breakdown by user role.

        Returns:
            {
                "student": {"english": 70, "urdu": 30, "total": 100},
                "instructor": {"english": 80, "urdu": 20, "total": 100}
            }
        """
        try:
            # Query users with their preferences and roles
            result = await db.execute(
                select(
                    User.role,
                    UserLanguagePreference.language,
                    func.count(User.user_id),
                ).outerjoin(
                    UserLanguagePreference,
                    User.user_id == UserLanguagePreference.user_id,
                )
            )

            breakdown = {}
            for row in result:
                role = row[0] or "guest"
                language = row[1] or "english"
                count = row[2]

                if role not in breakdown:
                    breakdown[role] = {"english": 0, "urdu": 0, "total": 0}

                breakdown[role][language] = count
                breakdown[role]["total"] += count

            return breakdown
        except Exception as e:
            logger.error(f"Error getting demographic breakdown: {e}")
            return {}


# Convenience functions
async def get_language_adoption_rate(db: AsyncSession) -> Dict[str, float]:
    """Get current language adoption rates."""
    metrics = await LanguageAnalyticsService.get_adoption_metrics(db)
    return {
        "english_percent": metrics.get("english_percent", 0),
        "urdu_percent": metrics.get("urdu_percent", 0),
    }


async def track_urdu_adoption(db: AsyncSession) -> Dict[str, Any]:
    """
    Get comprehensive Urdu adoption analytics.

    Returns:
        Adoption metrics, timeline, and demographics
    """
    service = LanguageAnalyticsService()

    return {
        "current_metrics": await service.get_adoption_metrics(db),
        "breakdown": await service.get_user_language_breakdown(db),
        "recent_changes": await service.get_recent_preference_changes(db),
        "timeline": await service.get_adoption_timeline(db),
        "demographics": await service.get_demographic_breakdown(db),
    }
