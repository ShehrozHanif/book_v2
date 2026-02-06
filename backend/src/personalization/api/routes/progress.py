"""Progress tracking routes."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session as get_db
from src.personalization.models.schemas import (
    ProgressResponse, ProgressTrack, ProgressComplete,
    DashboardResponse, ChapterCompleteResponse, AchievementInfo
)
from src.personalization.models.db_models import User
from src.personalization.services import progress_service
from src.personalization.services.achievement_service import (
    get_achievement_service, ACHIEVEMENTS_CONFIG
)
from src.personalization.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/progress", tags=["progress"])


@router.post("/{chapter_id}/complete", response_model=Dict[str, Any])
async def mark_chapter_complete(
    chapter_id: int,
    completion_data: ProgressComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a chapter as completed.

    Args:
        chapter_id: Chapter ID (1-22)
        completion_data: Completion data with mastery_score and optional time_spent_seconds
        current_user: Current authenticated user
        db: Database session

    Returns:
        Response with updated progress, xp_earned, achievements_unlocked

    Raises:
        HTTPException 400: If chapter_id is invalid
        HTTPException 401: If not authenticated
    """
    user_id = current_user.user_id

    # Validate chapter_id
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    try:
        # Mark chapter complete
        progress = await progress_service.complete_chapter(
            db=db,
            user_id=user_id,
            chapter_id=chapter_id,
            mastery_score=completion_data.mastery_score,
            time_spent_seconds=completion_data.time_spent_seconds
        )

        # Award XP
        xp_earned = await progress_service.award_xp_for_chapter(db, user_id, chapter_id)

        # Update skill level
        await progress_service.update_skill_level(db, user_id)

        # Check for achievements
        achievement_service = await get_achievement_service(db)
        all_unlocked = []

        # 1. Check chapter completion achievements
        chapter_achievements = await achievement_service.check_achievements(
            user_id,
            "chapter_complete",
            {"chapter_id": chapter_id}
        )
        all_unlocked.extend(chapter_achievements)

        # 2. Check XP milestone achievements
        if xp_earned > 0:
            xp_achievements = await achievement_service.check_achievements(
                user_id,
                "xp_earned",
                {"total_xp": current_user.skill_level * 10}  # Approximate XP from skill
            )
            all_unlocked.extend(xp_achievements)

        # 3. Check mastery achievements
        if completion_data.mastery_score == 100:
            mastery_achievements = await achievement_service.check_achievements(
                user_id,
                "mastery_update",
                {
                    "mastery_score": completion_data.mastery_score,
                    "chapter_id": chapter_id
                }
            )
            all_unlocked.extend(mastery_achievements)

        # Format achievements
        achievements_unlocked = []
        for ach_type in all_unlocked:
            if ach_type in ACHIEVEMENTS_CONFIG:
                config = ACHIEVEMENTS_CONFIG[ach_type]
                achievements_unlocked.append({
                    "id": config["id"],
                    "title": config["title"],
                    "description": config["description"],
                    "icon": config["icon"],
                    "points": config["points"],
                    "rarity": config.get("rarity", "common")
                })

        return {
            "progress": {
                "progress_id": str(progress.progress_id),
                "user_id": str(progress.user_id),
                "chapter_id": progress.chapter_id,
                "completion_status": progress.completion_status,
                "time_spent_seconds": progress.time_spent_seconds,
                "mastery_score": progress.mastery_score,
                "last_accessed_at": progress.last_accessed_at.isoformat() if progress.last_accessed_at else None,
                "practice_attempts": progress.practice_attempts,
                "highest_practice_score": progress.highest_practice_score
            },
            "xp_earned": xp_earned,
            "achievements_unlocked": achievements_unlocked
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete chapter: {str(e)}"
        )


@router.get("", response_model=Dict[str, Any])
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's overall progress.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        User's overall progress including:
        - total_chapters_completed
        - completion_percentage
        - chapters_completed (list)
        - current_path_progress
        - total_time_invested_hours
        - total_xp_earned
        - average_mastery_score
        - chapter_details

    Raises:
        HTTPException 401: If not authenticated
    """
    user_id = current_user.user_id

    try:
        # Get progress summary
        progress_summary = await progress_service.get_user_progress_summary(db, user_id)

        # Get all progress records
        all_progress = await progress_service.get_user_progress(db, user_id)

        # Calculate metrics
        total_chapters = 22
        chapters_completed = progress_summary["chapters_completed"]
        completion_percentage = round((len(chapters_completed) / total_chapters) * 100, 1)
        total_time_hours = round(progress_summary["total_time"] / 3600, 1)

        # Calculate total XP (sum of mastery scores)
        total_xp = sum(progress_summary["mastery_scores"].values())

        # Calculate average mastery
        mastery_scores = progress_summary["mastery_scores"]
        avg_mastery = round(
            sum(mastery_scores.values()) / len(mastery_scores), 1
        ) if mastery_scores else 0.0

        # Get current path progress
        from src.personalization.services.learning_path_service import get_active_learning_path

        active_path = await get_active_learning_path(db, user_id)
        current_path_progress = None

        if active_path:
            chapters_in_path = len(active_path.chapters_array)
            completed_in_path = len([
                ch for ch in active_path.chapters_array
                if ch in chapters_completed
            ])
            path_progress_pct = round((completed_in_path / chapters_in_path) * 100, 1) if chapters_in_path > 0 else 0

            # Find next chapter
            next_chapter = None
            for chapter_id in active_path.chapters_array:
                if chapter_id not in chapters_completed:
                    next_chapter = chapter_id
                    break

            current_path_progress = {
                "path_id": active_path.path_name,
                "chapters_in_path": chapters_in_path,
                "completed": completed_in_path,
                "progress_percentage": path_progress_pct,
                "next_chapter": next_chapter
            }

        # Build chapter details
        chapter_details = {}
        for progress in all_progress:
            chapter_details[str(progress.chapter_id)] = {
                "completion_status": progress.completion_status,
                "mastery_score": progress.mastery_score,
                "time_spent": progress.time_spent_seconds,
                "practice_attempts": progress.practice_attempts
            }

        return {
            "total_chapters_completed": len(chapters_completed),
            "completion_percentage": completion_percentage,
            "chapters_completed": sorted(chapters_completed),
            "current_path_progress": current_path_progress,
            "total_time_invested_hours": total_time_hours,
            "total_xp_earned": total_xp,
            "average_mastery_score": avg_mastery,
            "chapter_details": chapter_details
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )


@router.post("/{user_id}/progress/{chapter_id}/start", response_model=ProgressResponse)
async def start_chapter_progress(
    user_id: UUID,
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start or resume progress on a chapter.

    Args:
        user_id: User ID (must match current user)
        chapter_id: Chapter ID (1-22)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Progress record

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 400: If chapter_id is invalid
    """
    # Verify user is accessing their own progress
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot track progress for other users"
        )

    # Validate chapter_id
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    try:
        progress = await progress_service.start_chapter(
            db=db,
            user_id=user_id,
            chapter_id=chapter_id
        )

        return ProgressResponse(
            progress_id=progress.progress_id,
            user_id=progress.user_id,
            chapter_id=progress.chapter_id,
            completion_status=progress.completion_status,
            time_spent_seconds=progress.time_spent_seconds,
            mastery_score=progress.mastery_score,
            last_accessed_at=progress.last_accessed_at,
            practice_attempts=progress.practice_attempts,
            highest_practice_score=progress.highest_practice_score
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start chapter: {str(e)}"
        )


@router.post("/{user_id}/progress/{chapter_id}/complete", response_model=ChapterCompleteResponse)
async def complete_chapter_progress(
    user_id: UUID,
    chapter_id: int,
    completion_data: ProgressComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a chapter as completed.

    Args:
        user_id: User ID (must match current user)
        chapter_id: Chapter ID (1-22)
        completion_data: Mastery score and optional time spent
        current_user: Current authenticated user
        db: Database session

    Returns:
        ChapterCompleteResponse with achievement info and next recommendation

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 400: If chapter_id is invalid or mastery_score invalid
    """
    # Verify user is accessing their own progress
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot track progress for other users"
        )

    # Validate chapter_id
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    try:
        # Mark chapter complete
        progress = await progress_service.complete_chapter(
            db=db,
            user_id=user_id,
            chapter_id=chapter_id,
            mastery_score=completion_data.mastery_score,
            time_spent_seconds=completion_data.time_spent_seconds
        )

        # Get next chapter suggestion
        next_chapter = await progress_service.suggest_next_chapter(db, user_id)

        # Check if achievement should be unlocked (will be implemented in Phase 5)
        achievement_unlocked = None

        # For now, unlock achievement for first chapter completion
        all_progress = await progress_service.get_user_progress(db, user_id)
        completed_count = len([p for p in all_progress if p.completion_status == "completed"])

        if completed_count == 1:
            achievement_unlocked = AchievementInfo(
                title="First Steps",
                description="Completed your first chapter!",
                icon_url="/badges/first_chapter.svg",
                points=10
            )

        return ChapterCompleteResponse(
            status="completed",
            achievement_unlocked=achievement_unlocked,
            next_recommendation=next_chapter
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete chapter: {str(e)}"
        )


@router.post("/{user_id}/progress/{chapter_id}/time", response_model=ProgressResponse)
async def track_chapter_time(
    user_id: UUID,
    chapter_id: int,
    time_data: ProgressTrack,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track time spent on a chapter.

    Args:
        user_id: User ID (must match current user)
        chapter_id: Chapter ID (1-22)
        time_data: Time increment in seconds
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated Progress record

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 400: If chapter_id is invalid
    """
    # Verify user is accessing their own progress
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot track progress for other users"
        )

    # Validate chapter_id
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    try:
        progress = await progress_service.track_time(
            db=db,
            user_id=user_id,
            chapter_id=chapter_id,
            time_spent_seconds=time_data.time_spent_seconds
        )

        return ProgressResponse(
            progress_id=progress.progress_id,
            user_id=progress.user_id,
            chapter_id=progress.chapter_id,
            completion_status=progress.completion_status,
            time_spent_seconds=progress.time_spent_seconds,
            mastery_score=progress.mastery_score,
            last_accessed_at=progress.last_accessed_at,
            practice_attempts=progress.practice_attempts,
            highest_practice_score=progress.highest_practice_score
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track time: {str(e)}"
        )


@router.get("/{user_id}/progress", response_model=DashboardResponse)
async def get_progress_dashboard(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive progress dashboard with all metrics.

    Args:
        user_id: User ID (must match current user)
        current_user: Current authenticated user
        db: Database session

    Returns:
        DashboardResponse with:
        - chapters_completed, modules_completed
        - total_learning_time_hours
        - current_skill_level
        - current_path info
        - achievements
        - learning_statistics

    Raises:
        HTTPException 403: If user_id doesn't match current user
    """
    # Verify user is accessing their own data
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' progress"
        )

    try:
        # Get progress dashboard data
        dashboard_data = await progress_service.get_progress_dashboard(db, user_id)

        # Get module completion
        module_completion = await progress_service.calculate_module_completion(db, user_id)
        modules_completed = len([pct for pct in module_completion.values() if pct == 100])

        # Get current path
        from src.personalization.services.learning_path_service import get_active_learning_path

        current_path = None
        active_path = await get_active_learning_path(db, user_id)
        if active_path:
            from src.personalization.models.schemas import LearningPathResponse
            current_path = LearningPathResponse(
                path_id=active_path.path_id,
                user_id=active_path.user_id,
                path_name=active_path.path_name,
                chapters=active_path.chapters_array,
                completion_percentage=active_path.completion_percentage,
                status=active_path.status,
                created_at=active_path.created_at,
                updated_at=active_path.updated_at
            )

        # Get achievements (placeholder for Phase 5)
        achievements = []

        return DashboardResponse(
            chapters_completed=dashboard_data["chapters_completed"],
            modules_completed=modules_completed,
            total_learning_time_hours=dashboard_data["total_time_hours"],
            current_skill_level=current_user.skill_level,
            current_path=current_path,
            achievements=achievements,
            learning_statistics=dashboard_data["progress_by_chapter"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard: {str(e)}"
        )


@router.get("/{user_id}/progress/{chapter_id}", response_model=ProgressResponse)
async def get_chapter_progress(
    user_id: UUID,
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get progress for a specific chapter.

    Args:
        user_id: User ID (must match current user)
        chapter_id: Chapter ID (1-22)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Progress record for the chapter

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 404: If no progress found for chapter
    """
    # Verify user is accessing their own data
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' progress"
        )

    # Validate chapter_id
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    progress_list = await progress_service.get_user_progress(db, user_id, chapter_id)

    if not progress_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No progress found for chapter {chapter_id}"
        )

    progress = progress_list[0]

    return ProgressResponse(
        progress_id=progress.progress_id,
        user_id=progress.user_id,
        chapter_id=progress.chapter_id,
        completion_status=progress.completion_status,
        time_spent_seconds=progress.time_spent_seconds,
        mastery_score=progress.mastery_score,
        last_accessed_at=progress.last_accessed_at,
        practice_attempts=progress.practice_attempts,
        highest_practice_score=progress.highest_practice_score
    )


@router.get("/{user_id}/achievements", response_model=Dict[str, Any])
async def get_user_achievements(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all achievements for a user.

    Args:
        user_id: User ID (must match current user)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Response with achievements list and statistics

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 404: If user not found
    """
    # Verify user is accessing their own achievements
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' achievements"
        )

    try:
        # Get achievement service
        achievement_service = await get_achievement_service(db)

        # Get all achievements
        achievements = await achievement_service.get_user_achievements(user_id)

        # Get statistics
        stats = await achievement_service.get_achievement_stats(user_id)

        # Build statistics by type
        by_type = {}
        for achievement in achievements:
            ach_type = achievement.get("id", "").split("_")[0] + "_" + achievement.get("id", "").split("_")[1] if "_" in achievement.get("id", "") else "other"

            # Better type categorization
            ach_id = achievement.get("id", "")
            if ach_id.startswith("ch_"):
                ach_type = "chapter_complete"
            elif ach_id.startswith("module_"):
                ach_type = "module_complete"
            elif ach_id.startswith("xp_"):
                ach_type = "xp_milestone"
            elif ach_id.startswith("streak_"):
                ach_type = "streak"
            elif ach_id == "perfect_score":
                ach_type = "mastery"
            else:
                ach_type = "milestone"

            if ach_type not in by_type:
                by_type[ach_type] = 0
            by_type[ach_type] += 1

        return {
            "achievements": achievements,
            "stats": {
                "total_achievements": stats["total_achievements"],
                "total_points": stats["total_points"],
                "by_type": by_type,
                "recent": stats["recent"]
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get achievements: {str(e)}"
        )
