"""Achievement service for gamification and milestone tracking."""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import Achievement, Progress, LearningPath, User
from src.personalization.services.user_service import get_user_by_id

logger = logging.getLogger(__name__)


# Achievement definitions
ACHIEVEMENTS_CONFIG = {
    # Chapter Completion Achievements (22 chapters)
    "chapter_1_mastered": {
        "title": "Fundamentals Started",
        "description": "Completed Chapter 1: Fundamentals",
        "icon": "🚀",
        "points": 10,
        "category": "chapter"
    },
    "chapter_5_mastered": {
        "title": "Halfway Roboticist",
        "description": "Completed Chapter 5: Kinematics",
        "icon": "⚙️",
        "points": 15,
        "category": "chapter"
    },
    "chapter_10_mastered": {
        "title": "Fundamentals Expert",
        "description": "Completed Module 1 (Chapters 1-7)",
        "icon": "🏆",
        "points": 25,
        "category": "module"
    },
    "chapter_15_mastered": {
        "title": "Intermediate Master",
        "description": "Completed Module 2 (Chapters 8-14)",
        "icon": "🎯",
        "points": 30,
        "category": "module"
    },
    "all_chapters_completed": {
        "title": "Robotics Sage",
        "description": "Completed all 22 chapters",
        "icon": "🧙",
        "points": 100,
        "category": "completion"
    },

    # XP/Practice Milestones
    "xp_50": {
        "title": "Learning Starter",
        "description": "Earned 50 XP points",
        "icon": "⭐",
        "points": 50,
        "category": "xp"
    },
    "xp_100": {
        "title": "Century Club",
        "description": "Earned 100 XP points",
        "icon": "💯",
        "points": 100,
        "category": "xp"
    },
    "xp_250": {
        "title": "Knowledge Seeker",
        "description": "Earned 250 XP points",
        "icon": "🔍",
        "points": 250,
        "category": "xp"
    },
    "xp_500": {
        "title": "Expert Learner",
        "description": "Earned 500 XP points",
        "icon": "👨‍🎓",
        "points": 500,
        "category": "xp"
    },

    # Streak Achievements
    "streak_7_days": {
        "title": "Week Warrior",
        "description": "7 consecutive days of learning",
        "icon": "🔥",
        "points": 50,
        "category": "streak"
    },
    "streak_14_days": {
        "title": "Fortnight Friend",
        "description": "14 consecutive days of learning",
        "icon": "🔥🔥",
        "points": 100,
        "category": "streak"
    },
    "streak_30_days": {
        "title": "Month Master",
        "description": "30 consecutive days of learning",
        "icon": "🔥🔥🔥",
        "points": 250,
        "category": "streak"
    },

    # Mastery Achievements
    "perfect_practice": {
        "title": "Perfect Practice",
        "description": "Scored 100% on a practice attempt",
        "icon": "✨",
        "points": 30,
        "category": "mastery"
    },
    "high_mastery_5_chapters": {
        "title": "Mastery Seeker",
        "description": "Achieved 80%+ mastery in 5 chapters",
        "icon": "🎓",
        "points": 75,
        "category": "mastery"
    },
    "speedrun": {
        "title": "Speed Learner",
        "description": "Completed a chapter in less than 1 hour",
        "icon": "⚡",
        "points": 25,
        "category": "mastery"
    },

    # Special Achievements
    "early_adopter": {
        "title": "Early Adopter",
        "description": "Started learning in the first week",
        "icon": "🎖️",
        "points": 20,
        "category": "special"
    },
    "night_owl": {
        "title": "Night Owl",
        "description": "Completed learning sessions after 10 PM",
        "icon": "🦉",
        "points": 15,
        "category": "special"
    },
    "morning_person": {
        "title": "Morning Person",
        "description": "Completed learning sessions before 8 AM",
        "icon": "🌅",
        "points": 15,
        "category": "special"
    },
    "multi_learner": {
        "title": "Multi-Path Learner",
        "description": "Started learning on multiple learning paths",
        "icon": "🛣️",
        "points": 40,
        "category": "special"
    },

    # Engagement Achievements
    "question_master": {
        "title": "Question Master",
        "description": "Asked 50 questions in chat",
        "icon": "❓",
        "points": 35,
        "category": "engagement"
    },
    "conversation_enthusiast": {
        "title": "Conversation Enthusiast",
        "description": "Had 10+ conversation sessions",
        "icon": "💬",
        "points": 25,
        "category": "engagement"
    }
}


class AchievementService:
    """Service for managing achievements and gamification."""

    def __init__(self, db: AsyncSession):
        """
        Initialize achievement service.

        Args:
            db: Database session
        """
        self.db = db

    async def check_chapter_completion_achievement(self,
                                                   user_id: UUID,
                                                   chapter_id: int) -> Optional[str]:
        """
        Check if user should earn chapter completion achievement.

        Args:
            user_id: User ID
            chapter_id: Chapter ID (1-22)

        Returns:
            Achievement type if earned, None otherwise
        """
        progress = await self.db.execute(
            select(Progress).where(
                (Progress.user_id == user_id) & (Progress.chapter_id == chapter_id)
            )
        )
        record = progress.scalar_one_or_none()

        if record and record.completion_status == "completed":
            # Determine which achievement to unlock
            if chapter_id == 1:
                return "chapter_1_mastered"
            elif chapter_id == 5:
                return "chapter_5_mastered"
            elif chapter_id == 7:
                return "chapter_10_mastered"  # End of Module 1
            elif chapter_id == 14:
                return "chapter_15_mastered"  # End of Module 2
            elif chapter_id == 22:
                # Check if all chapters completed
                all_progress = await self.db.execute(
                    select(Progress).where(Progress.user_id == user_id)
                )
                all_records = all_progress.scalars().all()
                if all(p.completion_status == "completed" for p in all_records):
                    return "all_chapters_completed"

        return None

    async def check_xp_milestone_achievements(self, user_id: UUID) -> List[str]:
        """
        Check if user should earn XP milestone achievements.

        Args:
            user_id: User ID

        Returns:
            List of achievement types earned
        """
        user = await get_user_by_id(self.db, user_id)
        if not user:
            return []

        # Calculate total XP from progress (mastery scores)
        progress_records = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        records = progress_records.scalars().all()
        total_xp = sum(p.mastery_score for p in records)

        achievements = []
        if total_xp >= 500:
            achievements.append("xp_500")
        elif total_xp >= 250:
            achievements.append("xp_250")
        elif total_xp >= 100:
            achievements.append("xp_100")
        elif total_xp >= 50:
            achievements.append("xp_50")

        return achievements

    async def check_mastery_achievements(self, user_id: UUID) -> List[str]:
        """
        Check if user should earn mastery-related achievements.

        Args:
            user_id: User ID

        Returns:
            List of achievement types earned
        """
        achievements = []

        # Check for high mastery in multiple chapters
        progress_records = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        records = progress_records.scalars().all()

        high_mastery_count = sum(1 for p in records if p.mastery_score >= 80)
        if high_mastery_count >= 5:
            achievements.append("high_mastery_5_chapters")

        return achievements

    async def unlock_achievement(self,
                                user_id: UUID,
                                achievement_type: str) -> Optional[Achievement]:
        """
        Unlock an achievement for a user.

        Args:
            user_id: User ID
            achievement_type: Type of achievement to unlock

        Returns:
            Achievement record if successful, None if already earned or invalid
        """
        # Check if already earned
        existing = await self.db.execute(
            select(Achievement).where(
                (Achievement.user_id == user_id) &
                (Achievement.achievement_type == achievement_type)
            )
        )
        if existing.scalar_one_or_none():
            logger.debug(f"Achievement {achievement_type} already earned by user {user_id}")
            return None

        # Check if achievement exists
        if achievement_type not in ACHIEVEMENTS_CONFIG:
            logger.warning(f"Unknown achievement type: {achievement_type}")
            return None

        config = ACHIEVEMENTS_CONFIG[achievement_type]

        # Create achievement record
        achievement = Achievement(
            user_id=user_id,
            achievement_type=achievement_type,
            display_info_json={
                "title": config["title"],
                "description": config["description"],
                "icon": config["icon"],
                "points": config["points"],
                "category": config["category"]
            }
        )

        self.db.add(achievement)
        await self.db.commit()
        await self.db.refresh(achievement)

        logger.info(f"Achievement unlocked: {achievement_type} for user {user_id}")

        return achievement

    async def get_user_achievements(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get all achievements for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with earned and locked achievements
        """
        achievements = await self.db.execute(
            select(Achievement).where(Achievement.user_id == user_id)
        )
        earned = achievements.scalars().all()
        earned_ids = {a.achievement_type for a in earned}

        earned_list = [
            {
                "type": a.achievement_type,
                "title": a.display_info_json.get("title"),
                "description": a.display_info_json.get("description"),
                "icon": a.display_info_json.get("icon"),
                "points": a.display_info_json.get("points"),
                "earned_date": a.earned_date.isoformat() if a.earned_date else None
            }
            for a in earned
        ]

        locked_list = [
            {
                "type": ach_type,
                "title": config["title"],
                "description": config["description"],
                "icon": config["icon"],
                "points": config["points"],
                "earned": False
            }
            for ach_type, config in ACHIEVEMENTS_CONFIG.items()
            if ach_type not in earned_ids
        ]

        return {
            "earned_count": len(earned),
            "total_count": len(ACHIEVEMENTS_CONFIG),
            "total_points": sum(a.display_info_json.get("points", 0) for a in earned),
            "earned": earned_list,
            "locked": locked_list
        }

    async def process_progress_update(self, user_id: UUID, chapter_id: int) -> List[str]:
        """
        Process progress update and unlock related achievements.

        Args:
            user_id: User ID
            chapter_id: Updated chapter ID

        Returns:
            List of newly unlocked achievement types
        """
        unlocked = []

        # Check chapter completion
        chapter_ach = await self.check_chapter_completion_achievement(user_id, chapter_id)
        if chapter_ach:
            result = await self.unlock_achievement(user_id, chapter_ach)
            if result:
                unlocked.append(chapter_ach)

        # Check XP milestones
        xp_achs = await self.check_xp_milestone_achievements(user_id)
        for ach in xp_achs:
            result = await self.unlock_achievement(user_id, ach)
            if result:
                unlocked.append(ach)

        # Check mastery achievements
        mastery_achs = await self.check_mastery_achievements(user_id)
        for ach in mastery_achs:
            result = await self.unlock_achievement(user_id, ach)
            if result:
                unlocked.append(ach)

        return unlocked


async def get_achievement_service(db: AsyncSession) -> AchievementService:
    """
    Get achievement service instance.

    Args:
        db: Database session

    Returns:
        AchievementService instance
    """
    return AchievementService(db)
