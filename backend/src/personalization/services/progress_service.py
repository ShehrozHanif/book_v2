"""Progress tracking service for chapter-level learning progress."""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
import re

from src.personalization.models.db_models import Progress, LearningPath, User, Achievement


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


async def mark_chapter_complete(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: int
) -> Progress:
    """
    Mark a chapter as complete (convenience method without mastery score).

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Chapter ID (1-22)

    Returns:
        Updated Progress record

    Note:
        Uses default mastery score of 80 if not provided.
        For custom mastery score, use complete_chapter instead.
    """
    return await complete_chapter(
        db=db,
        user_id=user_id,
        chapter_id=chapter_id,
        mastery_score=80
    )


async def get_chapter_progress(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: int
) -> Optional[Progress]:
    """
    Get progress for a specific chapter.

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Chapter ID

    Returns:
        Progress record with mastery_score, time_spent, practice_attempts or None
    """
    result = await db.execute(
        select(Progress).where(
            and_(
                Progress.user_id == user_id,
                Progress.chapter_id == chapter_id
            )
        )
    )
    return result.scalar_one_or_none()


async def get_user_progress_summary(
    db: AsyncSession,
    user_id: UUID
) -> Dict[str, Any]:
    """
    Get user's overall progress summary.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dict with:
        - chapters_completed: List[int]
        - total_time: int (seconds)
        - mastery_scores: Dict[int, int] (chapter_id -> mastery_score)
    """
    progress_records = await get_user_progress(db, user_id)

    completed_chapters = [
        p.chapter_id for p in progress_records
        if p.completion_status == "completed"
    ]

    total_time = sum(p.time_spent_seconds for p in progress_records)

    mastery_scores = {
        p.chapter_id: p.mastery_score
        for p in progress_records
        if p.mastery_score > 0
    }

    return {
        "chapters_completed": completed_chapters,
        "total_time": total_time,
        "mastery_scores": mastery_scores
    }


async def calculate_mastery_score(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: int,
    correct_answers: int,
    total_questions: int,
    time_spent_seconds: int
) -> int:
    """
    Calculate mastery score for a chapter (0-100).

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Chapter ID
        correct_answers: Number of correct answers
        total_questions: Total questions answered
        time_spent_seconds: Time spent on chapter

    Returns:
        Mastery score (0-100)

    Formula:
        - Base: (correct_answers / total_questions) * 100
        - Time bonus: Up to 10 points if time < average (1800s = 30 min)
        - Practice efficiency: (1 / practice_attempts) * 10 bonus points
        - Max: 100 points, Min: 0 points
    """
    if total_questions == 0:
        return 0

    # Base score from correct answers
    base_score = (correct_answers / total_questions) * 100

    # Time bonus (faster than 30 minutes gets bonus)
    average_time = 1800  # 30 minutes
    time_bonus = 0
    if time_spent_seconds < average_time and time_spent_seconds > 0:
        time_ratio = 1 - (time_spent_seconds / average_time)
        time_bonus = min(10, time_ratio * 10)

    # Practice efficiency bonus
    progress = await get_chapter_progress(db, user_id, chapter_id)
    practice_bonus = 0
    if progress and progress.practice_attempts > 0:
        practice_bonus = min(10, 10 / progress.practice_attempts)

    # Calculate final score
    final_score = base_score + time_bonus + practice_bonus

    # Clamp to 0-100 range
    return max(0, min(100, int(final_score)))


async def update_time_spent(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: int,
    seconds_added: int
) -> Progress:
    """
    Update time spent on a chapter.

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Chapter ID
        seconds_added: Seconds to add to time_spent

    Returns:
        Updated Progress record
    """
    return await track_time(
        db=db,
        user_id=user_id,
        chapter_id=chapter_id,
        time_spent_seconds=seconds_added
    )


def detect_chapter_from_conversation(conversation_text: str) -> Optional[int]:
    """
    Detect chapter ID from conversation text.

    Args:
        conversation_text: User's conversation/query text

    Returns:
        Chapter ID (1-22) if detected, None otherwise

    Detection patterns:
        - "Chapter X"
        - "Ch X"
        - "chapter X"
        - "Ch. X"
    """
    if not conversation_text:
        return None

    # Pattern: Chapter X, Ch X, Ch. X (case insensitive)
    patterns = [
        r'\bchapter\s+(\d+)\b',
        r'\bch\.?\s+(\d+)\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, conversation_text, re.IGNORECASE)
        if match:
            chapter_id = int(match.group(1))
            if 1 <= chapter_id <= 22:
                return chapter_id

    return None


async def update_skill_level(
    db: AsyncSession,
    user_id: UUID
) -> int:
    """
    Update user's skill level based on average mastery across completed chapters.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Updated skill level (0-100)
    """
    # Get user
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return 50  # Default

    # Get completed progress
    progress_records = await db.execute(
        select(Progress).where(
            and_(
                Progress.user_id == user_id,
                Progress.completion_status == "completed"
            )
        )
    )
    completed = list(progress_records.scalars().all())

    if not completed:
        return user.skill_level

    # Calculate average mastery
    avg_mastery = sum(p.mastery_score for p in completed) / len(completed)

    # Update user skill level
    user.skill_level = int(avg_mastery)
    await db.commit()
    await db.refresh(user)

    return user.skill_level


async def award_xp_for_chapter(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: int
) -> int:
    """
    Award XP for completing a chapter.

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Chapter ID

    Returns:
        XP earned (50 points per chapter)
    """
    # XP is derived from mastery scores in achievements
    # For now, return fixed amount
    return 50


async def calculate_estimated_completion_date(
    db: AsyncSession,
    user_id: UUID,
    path_id: UUID
) -> Optional[str]:
    """
    Calculate estimated completion date for a learning path.

    Args:
        db: Database session
        user_id: User ID
        path_id: Learning path ID

    Returns:
        ISO format date string or None

    Algorithm:
        - Get average time per completed chapter
        - Multiply by remaining chapters
        - Add to current date
    """
    from src.personalization.services.learning_path_service import get_learning_path_by_id

    path = await get_learning_path_by_id(db, path_id)
    if not path:
        return None

    # Get user's completed progress
    progress_records = await get_user_progress(db, user_id)
    completed = [p for p in progress_records if p.completion_status == "completed"]

    if not completed:
        # No data, estimate 30 min per chapter
        avg_time_per_chapter = 1800
    else:
        total_time = sum(p.time_spent_seconds for p in completed)
        avg_time_per_chapter = total_time / len(completed)

    # Count remaining chapters in path
    completed_chapter_ids = {p.chapter_id for p in completed}
    remaining_chapters = [
        ch for ch in path.chapters_array
        if ch not in completed_chapter_ids
    ]

    if not remaining_chapters:
        return datetime.utcnow().isoformat()

    # Calculate estimated time
    estimated_seconds = len(remaining_chapters) * avg_time_per_chapter
    estimated_days = estimated_seconds / (3600 * 24)  # Convert to days

    # Add to current date
    completion_date = datetime.utcnow() + timedelta(days=estimated_days)

    return completion_date.date().isoformat()


async def get_learning_streak(
    db: AsyncSession,
    user_id: UUID
) -> int:
    """
    Get user's learning streak (consecutive days).

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Number of consecutive days with activity
    """
    # Get all progress records ordered by last access
    result = await db.execute(
        select(Progress)
        .where(Progress.user_id == user_id)
        .order_by(Progress.last_accessed_at.desc())
    )
    progress_records = list(result.scalars().all())

    if not progress_records:
        return 0

    # Track unique days with activity
    activity_dates = sorted(
        {p.last_accessed_at.date() for p in progress_records if p.last_accessed_at},
        reverse=True
    )

    if not activity_dates:
        return 0

    # Calculate streak
    streak = 1
    current_date = activity_dates[0]

    for i in range(1, len(activity_dates)):
        prev_date = activity_dates[i]
        if (current_date - prev_date).days == 1:
            streak += 1
            current_date = prev_date
        else:
            break

    return streak


async def reset_chapter_progress(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: int
) -> Optional[Progress]:
    """
    Reset chapter progress to allow for retry.

    Args:
        db: Database session
        user_id: User ID
        chapter_id: Chapter ID (1-22)

    Returns:
        Updated Progress record or None if not found

    Note:
        Resets completion_status to 'in_progress' and clears practice attempt history.
    """
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
        return None

    # Reset progress
    progress.completion_status = "in_progress"
    progress.mastery_score = 0
    progress.time_spent_seconds = 0
    progress.practice_attempts = 0
    progress.highest_practice_score = 0
    progress.last_accessed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(progress)

    return progress
