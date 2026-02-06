"""Achievement Detection Service for gamification."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.personalization.models.db_models import Achievement, User

logger = logging.getLogger(__name__)

# Load achievements configuration
ACHIEVEMENTS_FILE = Path(__file__).parent.parent / "data" / "achievements.json"
ACHIEVEMENTS_CONFIG = {}


def _load_achievements():
    """Load achievements from JSON file."""
    global ACHIEVEMENTS_CONFIG
    try:
        if ACHIEVEMENTS_FILE.exists():
            with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for ach in data.get("achievements", []):
                    ACHIEVEMENTS_CONFIG[ach["id"]] = {
                        "id": ach["id"],
                        "type": ach.get("type", ""),
                        "title": ach.get("title", ""),
                        "description": ach.get("description", ""),
                        "icon": ach.get("icon", ""),
                        "points": ach.get("points", 0),
                        "rarity": ach.get("rarity", "common"),
                        "threshold": ach.get("threshold"),
                        "chapter": ach.get("chapter"),
                        "module": ach.get("module")
                    }
                logger.info(f"Loaded {len(ACHIEVEMENTS_CONFIG)} achievements")
        else:
            logger.warning(f"Achievements file not found: {ACHIEVEMENTS_FILE}")
    except Exception as e:
        logger.error(f"Failed to load achievements: {e}")


# Load on module import
_load_achievements()


class AchievementService:
    """Service for detecting and managing user achievements."""

    def __init__(self, db: AsyncSession):
        """Initialize achievement service.

        Args:
            db: Async database session
        """
        self.db = db

    async def check_achievements(
        self,
        user_id: UUID,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> List[str]:
        """Check and unlock achievements for a user event.

        Args:
            user_id: User UUID
            event_type: Type of event (chapter_complete, xp_earned, module_complete, streak_update, mastery_update)
            event_data: Event context data

        Returns:
            List of newly unlocked achievement IDs
        """
        if not user_id or not event_type:
            return []

        try:
            # Route to appropriate checker
            if event_type == "chapter_complete":
                return await self._check_chapter(user_id, event_data)
            elif event_type == "xp_earned":
                return await self._check_xp(user_id, event_data)
            elif event_type == "module_complete":
                return await self._check_module(user_id, event_data)
            elif event_type == "streak_update":
                return await self._check_streak(user_id, event_data)
            elif event_type == "mastery_update":
                return await self._check_mastery(user_id, event_data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                return []
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []

    async def process_progress_update(
        self,
        user_id: UUID,
        chapter_id: int
    ) -> List[str]:
        """Process achievement unlocks for chapter completion.

        Args:
            user_id: User UUID
            chapter_id: Completed chapter ID

        Returns:
            List of newly unlocked achievement IDs
        """
        unlocked = []

        # Check chapter completion achievement
        ach_id = f"ch_{chapter_id}_complete"
        if ach_id in ACHIEVEMENTS_CONFIG and await self._award_achievement(user_id, ach_id):
            unlocked.append(ach_id)

        # Check first chapter bonus
        if chapter_id == 1 and await self._award_achievement(user_id, "first_chapter"):
            unlocked.append("first_chapter")

        return unlocked

    async def _check_chapter(
        self,
        user_id: UUID,
        event_data: Dict[str, Any]
    ) -> List[str]:
        """Check for chapter completion achievements.

        Args:
            user_id: User UUID
            event_data: Must contain chapter_id

        Returns:
            List of newly unlocked achievement IDs
        """
        unlocked = []
        chapter_id = event_data.get("chapter_id")

        if not chapter_id:
            return unlocked

        # Award chapter-specific achievement
        ach_id = f"ch_{chapter_id}_complete"
        if ach_id in ACHIEVEMENTS_CONFIG and await self._award_achievement(user_id, ach_id):
            unlocked.append(ach_id)

        # Award first chapter bonus
        if chapter_id == 1 and await self._award_achievement(user_id, "first_chapter"):
            unlocked.append("first_chapter")

        return unlocked

    async def _check_xp(
        self,
        user_id: UUID,
        event_data: Dict[str, Any]
    ) -> List[str]:
        """Check for XP milestone achievements.

        Args:
            user_id: User UUID
            event_data: Must contain total_xp

        Returns:
            List of newly unlocked achievement IDs
        """
        unlocked = []
        total_xp = event_data.get("total_xp", 0)

        # Check milestones: 100, 500, 1000, 5000
        milestones = [
            ("xp_100", 100),
            ("xp_500", 500),
            ("xp_1000", 1000),
            ("xp_5000", 5000)
        ]

        for ach_id, threshold in milestones:
            if total_xp >= threshold and ach_id in ACHIEVEMENTS_CONFIG:
                if await self._award_achievement(user_id, ach_id):
                    unlocked.append(ach_id)

        return unlocked

    async def _check_module(
        self,
        user_id: UUID,
        event_data: Dict[str, Any]
    ) -> List[str]:
        """Check for module completion achievements.

        Args:
            user_id: User UUID
            event_data: Must contain module_id

        Returns:
            List of newly unlocked achievement IDs
        """
        unlocked = []
        module_id = event_data.get("module_id")

        if not module_id:
            return unlocked

        ach_id = f"module_{module_id}_complete"
        if ach_id in ACHIEVEMENTS_CONFIG and await self._award_achievement(user_id, ach_id):
            unlocked.append(ach_id)

        return unlocked

    async def _check_streak(
        self,
        user_id: UUID,
        event_data: Dict[str, Any]
    ) -> List[str]:
        """Check for learning streak achievements.

        Args:
            user_id: User UUID
            event_data: Must contain current_streak (in days)

        Returns:
            List of newly unlocked achievement IDs
        """
        unlocked = []
        current_streak = event_data.get("current_streak", 0)

        # Check thresholds: 7 days, 30 days
        streak_milestones = [
            ("streak_7", 7),
            ("streak_30", 30)
        ]

        for ach_id, threshold in streak_milestones:
            if current_streak >= threshold and ach_id in ACHIEVEMENTS_CONFIG:
                if await self._award_achievement(user_id, ach_id):
                    unlocked.append(ach_id)

        return unlocked

    async def _check_mastery(
        self,
        user_id: UUID,
        event_data: Dict[str, Any]
    ) -> List[str]:
        """Check for mastery achievements (100% score).

        Args:
            user_id: User UUID
            event_data: Must contain mastery_score and chapter_id

        Returns:
            List of newly unlocked achievement IDs
        """
        unlocked = []
        mastery_score = event_data.get("mastery_score", 0)
        chapter_id = event_data.get("chapter_id")

        if mastery_score != 100 or not chapter_id:
            return unlocked

        # For mastery, use unique ID with chapter to allow multiple awards
        ach_id = f"perfect_score_ch{chapter_id}"
        config = ACHIEVEMENTS_CONFIG.get("perfect_score")

        if config and await self._award_achievement_with_chapter(user_id, "perfect_score", chapter_id):
            unlocked.append("perfect_score")

        return unlocked

    async def _award_achievement(
        self,
        user_id: UUID,
        achievement_id: str
    ) -> bool:
        """Award an achievement to a user (prevents duplicates).

        Args:
            user_id: User UUID
            achievement_id: Achievement ID from config

        Returns:
            True if achievement was newly awarded, False if already owned
        """
        if achievement_id not in ACHIEVEMENTS_CONFIG:
            return False

        try:
            # Check if already awarded
            query = select(Achievement).where(
                and_(
                    Achievement.user_id == user_id,
                    Achievement.achievement_type == achievement_id
                )
            )
            result = await self.db.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                return False  # Already owned

            # Create new achievement record
            config = ACHIEVEMENTS_CONFIG[achievement_id]
            achievement = Achievement(
                user_id=user_id,
                achievement_type=achievement_id,
                display_info_json={
                    "title": config["title"],
                    "description": config["description"],
                    "icon": config["icon"],
                    "points": config["points"],
                    "rarity": config["rarity"]
                },
                earned_date=datetime.utcnow()
            )
            self.db.add(achievement)
            await self.db.commit()
            logger.info(f"Awarded achievement {achievement_id} to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to award achievement {achievement_id}: {e}")
            return False

    async def _award_achievement_with_chapter(
        self,
        user_id: UUID,
        achievement_id: str,
        chapter_id: int
    ) -> bool:
        """Award an achievement per chapter (allows duplicates per chapter).

        Args:
            user_id: User UUID
            achievement_id: Achievement ID from config
            chapter_id: Chapter ID for uniqueness

        Returns:
            True if achievement was newly awarded, False if already owned for chapter
        """
        if achievement_id not in ACHIEVEMENTS_CONFIG:
            return False

        try:
            # Check if already awarded for this chapter
            query = select(Achievement).where(
                and_(
                    Achievement.user_id == user_id,
                    Achievement.achievement_type == achievement_id
                )
            )
            result = await self.db.execute(query)
            existing_achievements = result.scalars().all()

            # Check if already awarded for this specific chapter
            for existing in existing_achievements:
                if existing.display_info_json.get("chapter_id") == chapter_id:
                    return False  # Already owned for this chapter

            # Create new achievement record with chapter info
            config = ACHIEVEMENTS_CONFIG[achievement_id]
            display_info = {
                "title": config["title"],
                "description": config["description"],
                "icon": config["icon"],
                "points": config["points"],
                "rarity": config["rarity"],
                "chapter_id": chapter_id
            }

            achievement = Achievement(
                user_id=user_id,
                achievement_type=achievement_id,
                display_info_json=display_info,
                earned_date=datetime.utcnow()
            )
            self.db.add(achievement)
            await self.db.commit()
            logger.info(f"Awarded achievement {achievement_id} (chapter {chapter_id}) to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to award achievement {achievement_id}: {e}")
            return False

    async def get_user_achievements(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all earned achievements for a user.

        Args:
            user_id: User UUID

        Returns:
            List of achievement dictionaries sorted by date (newest first)
        """
        if not user_id:
            return []

        try:
            query = select(Achievement).where(
                Achievement.user_id == user_id
            ).order_by(Achievement.earned_date.desc())

            result = await self.db.execute(query)
            achievements = result.scalars().all()

            return [
                {
                    "id": ach.achievement_type,
                    "title": ach.display_info_json.get("title", ""),
                    "description": ach.display_info_json.get("description", ""),
                    "icon": ach.display_info_json.get("icon", ""),
                    "points": ach.display_info_json.get("points", 0),
                    "rarity": ach.display_info_json.get("rarity", "common"),
                    "earned_date": ach.earned_date.isoformat() if ach.earned_date else None,
                    "display_info": ach.display_info_json
                }
                for ach in achievements
            ]
        except Exception as e:
            logger.error(f"Failed to get achievements for user {user_id}: {e}")
            return []

    async def get_achievement_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Get achievement statistics for a user.

        Args:
            user_id: User UUID

        Returns:
            Dictionary with stats: total_achievements, total_points, recent
        """
        if not user_id:
            return {
                "total_achievements": 0,
                "total_points": 0,
                "recent": []
            }

        try:
            achievements = await self.get_user_achievements(user_id)

            total_points = sum(ach["points"] for ach in achievements)
            recent = achievements[:5]  # Last 5

            return {
                "total_achievements": len(achievements),
                "total_points": total_points,
                "recent": recent
            }
        except Exception as e:
            logger.error(f"Failed to get achievement stats for user {user_id}: {e}")
            return {
                "total_achievements": 0,
                "total_points": 0,
                "recent": []
            }


async def get_achievement_service(db: AsyncSession) -> AchievementService:
    """Get achievement service instance.

    Args:
        db: Async database session

    Returns:
        AchievementService instance
    """
    return AchievementService(db)
