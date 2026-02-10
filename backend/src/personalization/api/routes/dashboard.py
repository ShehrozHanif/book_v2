"""Dashboard metrics routes for Phase 3."""

from typing import Dict, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session as get_db
from src.personalization.models.db_models import User
from src.personalization.services import progress_service
from src.personalization.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


def get_skill_tier(skill_level: int) -> str:
    """
    Get skill tier from skill level.

    Args:
        skill_level: Skill level (0-100)

    Returns:
        Skill tier name
    """
    if skill_level < 40:
        return "Beginner"
    elif skill_level < 70:
        return "Intermediate"
    else:
        return "Advanced"


@router.get("/metrics", response_model=Dict[str, Any])
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive dashboard metrics.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dashboard data with:
        - user: username, skill_level, skill_tier
        - progress: chapters_completed, total_chapters, completion_percentage, etc.
        - learning_path: current path info
        - achievements: badges earned
        - statistics: average mastery, streaks, etc.

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 404: If user not found
    """
    user_id = current_user.user_id

    try:
        # Get progress dashboard data
        dashboard_data = await progress_service.get_progress_dashboard(db, user_id)

        # Get user progress summary
        progress_summary = await progress_service.get_user_progress_summary(db, user_id)

        # Calculate completion percentage
        total_chapters = 22
        chapters_completed = len(progress_summary["chapters_completed"])
        completion_percentage = round((chapters_completed / total_chapters) * 100, 1)

        # Get active learning path
        from src.personalization.services.learning_path_service import get_active_learning_path

        active_path = await get_active_learning_path(db, user_id)

        learning_path_info = None
        if active_path:
            chapters_in_path = len(active_path.chapters_array)
            completed_in_path = len([
                ch for ch in active_path.chapters_array
                if ch in progress_summary["chapters_completed"]
            ])
            path_progress_pct = round((completed_in_path / chapters_in_path) * 100, 1) if chapters_in_path > 0 else 0

            # Find next uncompleted chapter in path
            next_chapter = None
            for chapter_id in active_path.chapters_array:
                if chapter_id not in progress_summary["chapters_completed"]:
                    next_chapter = chapter_id
                    break

            # Get estimated completion date
            estimated_completion = await progress_service.calculate_estimated_completion_date(
                db, user_id, active_path.path_id
            )

            learning_path_info = {
                "current_path": active_path.path_name,
                "chapters_in_path": chapters_in_path,
                "chapters_completed": completed_in_path,
                "progress_percentage": path_progress_pct,
                "estimated_completion_date": estimated_completion
            }

        # Get achievements
        from src.personalization.services.achievement_service import get_achievement_service

        achievement_service = await get_achievement_service(db)
        achievements_data = await achievement_service.get_user_achievements(user_id)

        badges_earned = achievements_data.get("earned", [])
        badges_list = [
            {
                "title": badge.get("title"),
                "earned_date": badge.get("earned_date")
            }
            for badge in badges_earned
        ]

        # Calculate statistics
        mastery_scores = progress_summary["mastery_scores"]
        avg_mastery = round(
            sum(mastery_scores.values()) / len(mastery_scores), 1
        ) if mastery_scores else 0.0

        # Find most/least mastered chapters
        most_mastered_chapter = None
        least_mastered_chapter = None
        if mastery_scores:
            most_mastered_chapter = max(mastery_scores.items(), key=lambda x: x[1])[0]
            least_mastered_chapter = min(mastery_scores.items(), key=lambda x: x[1])[0]

        # Get learning streak
        learning_streak = await progress_service.get_learning_streak(db, user_id)

        # Get last activity
        all_progress = await progress_service.get_user_progress(db, user_id)
        last_activity = None
        if all_progress:
            latest = max(all_progress, key=lambda p: p.last_accessed_at)
            last_activity = latest.last_accessed_at.isoformat() if latest.last_accessed_at else None

        # Calculate total XP (sum of mastery scores)
        total_xp = sum(mastery_scores.values())

        # Build response
        return {
            "user": {
                "username": current_user.username,
                "skill_level": current_user.skill_level,
                "skill_tier": get_skill_tier(current_user.skill_level)
            },
            "progress": {
                "chapters_completed": chapters_completed,
                "total_chapters": total_chapters,
                "completion_percentage": completion_percentage,
                "total_time_hours": round(progress_summary["total_time"] / 3600, 1),
                "total_xp": total_xp
            },
            "learning_path": learning_path_info,
            "achievements": {
                "badges_earned": len(badges_list),
                "badges": badges_list
            },
            "statistics": {
                "average_mastery_score": avg_mastery,
                "most_mastered_chapter": most_mastered_chapter,
                "least_mastered_chapter": least_mastered_chapter,
                "learning_streak": learning_streak,
                "last_activity": last_activity
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard metrics: {str(e)}"
        )
