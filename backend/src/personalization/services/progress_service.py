"""Progress tracking service for chapter-level learning progress."""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import Progress, LearningPath, User


async def start_chapter(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: int
) -> Progress:
    """
    Start or resume a chapter for user.

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Chapter ID (1-22)

    Returns:
        Progress record

    Note:
        If progress already exists, updates last_accessed_at.
        If new, creates with status 'in_progress'.
    """
    # Check if progress already exists
    result = await db.execute(
        select(Progress).where(
            and_(
                Progress.user_id == user_id,
                Progress.chapter_id == chapter_id
            )
        )
    )
    progress = result.scalar_one_or_none()

    if progress:
        # Update last accessed time
        progress.last_accessed_at = datetime.utcnow()
    else:
        # Create new progress record
        progress = Progress(
            user_id=user_id,
            chapter_id=chapter_id,
            completion_status="in_progress",
            time_spent_seconds=0,
            mastery_score=0,
            last_accessed_at=datetime.utcnow(),
            practice_attempts=0,
            highest_practice_score=0
        )
        db.add(progress)

    await db.commit()
    await db.refresh(progress)

    return progress


async def complete_chapter(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: int,
    mastery_score: int,
    time_spent_seconds: Optional[int] = None
) -> Progress:
    """
    Mark a chapter as completed.

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Chapter ID (1-22)
        mastery_score: Mastery score (0-100)
        time_spent_seconds: Optional time spent to add

    Returns:
        Updated Progress record

    Raises:
        ValueError: If progress not found
    """
    # Get existing progress
    result = await db.execute(
        select(Progress).where(
            and_(
                Progress.user_id == user_id,
                Progress.chapter_id == chapter_id
            )
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        # Create if doesn't exist
        progress = Progress(
            user_id=user_id,
            chapter_id=chapter_id,
            completion_status="completed",
            time_spent_seconds=time_spent_seconds or 0,
            mastery_score=mastery_score,
            last_accessed_at=datetime.utcnow(),
            practice_attempts=0,
            highest_practice_score=0
        )
        db.add(progress)
    else:
        # Update existing
        progress.completion_status = "completed"
        progress.mastery_score = mastery_score
        if time_spent_seconds is not None:
            progress.time_spent_seconds += time_spent_seconds
        progress.last_accessed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(progress)

    # Update learning path progress if user has an active path
    from src.personalization.services.learning_path_service import get_active_learning_path, update_path_progress

    active_path = await get_active_learning_path(db, user_id)
    if active_path and chapter_id in active_path.chapters_array:
        await update_path_progress(db, user_id, active_path.path_id)

    return progress


async def track_time(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: int,
    time_spent_seconds: int
) -> Progress:
    """
    Track time spent on a chapter.

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Chapter ID
        time_spent_seconds: Time increment in seconds

    Returns:
        Updated Progress record
    """
    # Get or create progress
    result = await db.execute(
        select(Progress).where(
            and_(
                Progress.user_id == user_id,
                Progress.chapter_id == chapter_id
            )
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = await start_chapter(db, user_id, chapter_id)

    # Update time
    progress.time_spent_seconds += time_spent_seconds
    progress.last_accessed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(progress)

    return progress


async def get_user_progress(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: Optional[int] = None
) -> List[Progress]:
    """
    Get user's progress records.

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Optional specific chapter ID

    Returns:
        List of Progress records
    """
    if chapter_id:
        result = await db.execute(
            select(Progress).where(
                and_(
                    Progress.user_id == user_id,
                    Progress.chapter_id == chapter_id
                )
            )
        )
        progress = result.scalar_one_or_none()
        return [progress] if progress else []
    else:
        result = await db.execute(
            select(Progress)
            .where(Progress.user_id == user_id)
            .order_by(Progress.chapter_id)
        )
        return list(result.scalars().all())


async def get_progress_dashboard(
    db: AsyncSession,
    user_id: UUID
) -> Dict[str, Any]:
    """
    Get comprehensive progress dashboard data.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dict with dashboard metrics:
        - chapters_completed: int
        - chapters_in_progress: int
        - total_time_hours: float
        - average_mastery: float
        - progress_by_chapter: Dict[int, Dict]
    """
    # Get all progress
    progress_records = await get_user_progress(db, user_id)

    if not progress_records:
        return {
            "chapters_completed": 0,
            "chapters_in_progress": 0,
            "total_time_hours": 0.0,
            "average_mastery": 0.0,
            "progress_by_chapter": {}
        }

    # Calculate metrics
    completed = [p for p in progress_records if p.completion_status == "completed"]
    in_progress = [p for p in progress_records if p.completion_status == "in_progress"]

    total_seconds = sum(p.time_spent_seconds for p in progress_records)
    total_hours = round(total_seconds / 3600, 2)

    if completed:
        avg_mastery = round(sum(p.mastery_score for p in completed) / len(completed), 1)
    else:
        avg_mastery = 0.0

    # Progress by chapter
    progress_by_chapter = {}
    for p in progress_records:
        progress_by_chapter[p.chapter_id] = {
            "completion_status": p.completion_status,
            "mastery_score": p.mastery_score,
            "time_spent_hours": round(p.time_spent_seconds / 3600, 2),
            "practice_attempts": p.practice_attempts,
            "highest_practice_score": p.highest_practice_score,
            "last_accessed": p.last_accessed_at.isoformat() if p.last_accessed_at else None
        }

    return {
        "chapters_completed": len(completed),
        "chapters_in_progress": len(in_progress),
        "total_time_hours": total_hours,
        "average_mastery": avg_mastery,
        "progress_by_chapter": progress_by_chapter
    }


async def calculate_module_completion(
    db: AsyncSession,
    user_id: UUID
) -> Dict[int, int]:
    """
    Calculate completion percentage for each module.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dict mapping module number to completion percentage

    Note:
        Module structure (22 chapters across 4 modules):
        - Module 1: Chapters 1-6
        - Module 2: Chapters 7-12
        - Module 3: Chapters 13-18
        - Module 4: Chapters 19-22
    """
    module_ranges = {
        1: (1, 6),
        2: (7, 12),
        3: (13, 18),
        4: (19, 22)
    }

    module_completion = {}

    for module_num, (start, end) in module_ranges.items():
        # Get completed chapters in this module
        result = await db.execute(
            select(func.count(Progress.progress_id))
            .where(
                and_(
                    Progress.user_id == user_id,
                    Progress.chapter_id >= start,
                    Progress.chapter_id <= end,
                    Progress.completion_status == "completed"
                )
            )
        )
        completed_count = result.scalar()

        total_chapters = end - start + 1
        completion_pct = round((completed_count / total_chapters) * 100)
        module_completion[module_num] = completion_pct

    return module_completion


def detect_chapter_completion_heuristic(
    time_spent_seconds: int,
    practice_score: int,
    user_interactions: int
) -> bool:
    """
    Heuristic to detect if chapter should be marked complete.

    Args:
        time_spent_seconds: Time spent on chapter
        practice_score: Practice score (0-100)
        user_interactions: Number of interactions

    Returns:
        True if chapter likely complete, False otherwise

    Heuristic criteria (any 2 of 3):
        1. Spent at least 20 minutes (1200 seconds)
        2. Practice score >= 70
        3. At least 10 interactions
    """
    criteria_met = 0

    if time_spent_seconds >= 1200:  # 20 minutes
        criteria_met += 1

    if practice_score >= 70:
        criteria_met += 1

    if user_interactions >= 10:
        criteria_met += 1

    return criteria_met >= 2


async def suggest_next_chapter(
    db: AsyncSession,
    user_id: UUID
) -> Optional[Dict[str, Any]]:
    """
    Suggest next chapter for user to study.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dict with next chapter suggestion or None

    Algorithm:
        1. If user has active learning path, suggest next in path
        2. Otherwise, suggest next sequential uncompleted chapter
        3. If all complete, suggest chapter with lowest mastery
    """
    from src.personalization.services.learning_path_service import (
        get_active_learning_path,
        get_next_chapter_in_path
    )

    # Check if user has active learning path
    active_path = await get_active_learning_path(db, user_id)

    if active_path:
        next_chapter = await get_next_chapter_in_path(db, user_id, active_path.path_id)
        if next_chapter:
            return {
                "chapter_id": next_chapter,
                "reason": f"Next chapter in {active_path.path_name}",
                "from_path": True
            }

    # Find first uncompleted chapter (sequential)
    for chapter_id in range(1, 23):
        result = await db.execute(
            select(Progress).where(
                and_(
                    Progress.user_id == user_id,
                    Progress.chapter_id == chapter_id,
                    Progress.completion_status == "completed"
                )
            )
        )
        if not result.scalar_one_or_none():
            return {
                "chapter_id": chapter_id,
                "reason": "Next uncompleted chapter in sequence",
                "from_path": False
            }

    # All chapters complete - suggest lowest mastery chapter for review
    result = await db.execute(
        select(Progress)
        .where(Progress.user_id == user_id)
        .order_by(Progress.mastery_score.asc())
        .limit(1)
    )
    lowest_mastery = result.scalar_one_or_none()

    if lowest_mastery:
        return {
            "chapter_id": lowest_mastery.chapter_id,
            "reason": f"Review chapter with lowest mastery ({lowest_mastery.mastery_score}%)",
            "from_path": False
        }

    return None
