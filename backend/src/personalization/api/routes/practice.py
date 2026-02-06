"""Practice and statistics routes."""

from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.database.connection import get_session as get_db
from src.personalization.models.db_models import User, Progress
from src.personalization.services.practice_service import get_practice_service
from src.personalization.services import progress_service
from src.personalization.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["practice"])


@router.post("/users/{user_id}/progress/{chapter_id}/practice", response_model=Dict[str, Any])
async def submit_practice_attempt(
    user_id: UUID,
    chapter_id: int,
    answers: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit practice attempt answers and get scoring results.

    Args:
        user_id: User ID (must match current user)
        chapter_id: Chapter ID (1-22)
        answers: JSON body with answers array
        current_user: Current authenticated user
        db: Database session

    Returns:
        Response with mastery_score, correct_answers, total_questions, attempt_number, highest_score

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 400: If chapter_id is invalid or no answers provided
    """
    # Verify user is accessing their own progress
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot submit practice for other users"
        )

    # Validate chapter_id
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    try:
        # Get answers from request body
        answers_list = answers.get("answers", [])
        if not answers_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No answers provided"
            )

        # Get practice service
        practice_svc = await get_practice_service(db)

        # Get practice questions for the chapter
        questions = await practice_svc.get_practice_questions(chapter_id)

        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No practice questions available for chapter {chapter_id}"
            )

        # Calculate score
        correct_count = practice_svc.calculate_score(questions, answers_list)
        total_questions = len(questions)
        mastery_score = (correct_count / total_questions * 100) if total_questions > 0 else 0

        # Save practice attempt
        attempt = await practice_svc.save_practice_attempt(
            user_id=user_id,
            chapter_id=chapter_id,
            questions=questions,
            answers=answers_list,
            score=int(mastery_score)
        )

        # Get practice history to find attempt number and highest score
        history_data = await practice_svc.get_chapter_practice_history(user_id, chapter_id)
        history = history_data.get("history", [])

        attempt_number = history_data.get("attempts", 1)
        highest_score = history_data.get("best_score", int(mastery_score))

        return {
            "mastery_score": round(mastery_score, 1),
            "correct_answers": correct_count,
            "total_questions": total_questions,
            "attempt_number": attempt_number,
            "highest_score": highest_score,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit practice attempt: {str(e)}"
        )


@router.post("/users/{user_id}/progress/{chapter_id}/retry", response_model=Dict[str, Any])
async def retry_chapter(
    user_id: UUID,
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retry a chapter - reset progress and generate new practice questions.

    Args:
        user_id: User ID (must match current user)
        chapter_id: Chapter ID (1-22)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Response with new practice questions and reset progress info

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 400: If chapter_id is invalid
    """
    # Verify user is accessing their own progress
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot retry practice for other users"
        )

    # Validate chapter_id
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    try:
        # Reset progress
        await progress_service.reset_chapter_progress(db, user_id, chapter_id)

        # Get fresh practice questions
        practice_svc = await get_practice_service(db)
        questions = await practice_svc.get_practice_questions(chapter_id)

        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No practice questions available for chapter {chapter_id}"
            )

        # Return new questions
        return {
            "chapter_id": chapter_id,
            "message": "Chapter reset for retry",
            "total_questions": len(questions),
            "questions": [
                {
                    "id": q.get("id"),
                    "question": q.get("question"),
                    "options": [
                        {
                            "letter": opt.get("letter"),
                            "text": opt.get("text")
                        }
                        for opt in q.get("options", [])
                    ],
                    "difficulty": q.get("difficulty")
                }
                for q in questions
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry chapter: {str(e)}"
        )


@router.get("/users/{user_id}/statistics", response_model=Dict[str, Any])
async def get_learning_statistics(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive learning statistics for a user.

    Args:
        user_id: User ID (must match current user)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Response with statistics including time_per_chapter, mastery, learning curve, recommendations

    Raises:
        HTTPException 403: If user_id doesn't match current user
    """
    # Verify user is accessing their own statistics
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' statistics"
        )

    try:
        # Get user progress
        progress_data = await progress_service.get_user_progress(db, user_id)

        # Build time per chapter
        time_per_chapter = {}
        mastery_per_chapter = {}
        total_time_seconds = 0

        for progress in progress_data:
            time_per_chapter[str(progress.chapter_id)] = progress.time_spent_seconds
            mastery_per_chapter[str(progress.chapter_id)] = progress.mastery_score
            total_time_seconds += progress.time_spent_seconds

        # Calculate learning curve (simplified - can be enhanced)
        learning_curve = {
            "skill_snapshots": [
                {
                    "timestamp": progress.created_at.isoformat() if progress.created_at else "",
                    "skill_level": progress.mastery_score
                }
                for progress in progress_data[:10]  # Last 10 chapters
            ],
            "improvement_rate_per_week": calculate_improvement_rate(progress_data)
        }

        # Identify recommended focus areas (chapters with mastery < 60%)
        recommended_focus_areas = [
            {
                "chapter_id": progress.chapter_id,
                "mastery_score": progress.mastery_score,
                "reason": "Below 60% mastery" if progress.mastery_score < 60 else "Below 70% mastery",
                "suggested_action": "Review practice questions" if progress.mastery_score < 60 else "Additional practice recommended"
            }
            for progress in progress_data
            if progress.mastery_score < 70
        ]

        return {
            "time_per_chapter": time_per_chapter,
            "total_time_hours": round(total_time_seconds / 3600, 1),
            "mastery_per_chapter": mastery_per_chapter,
            "learning_curve": learning_curve,
            "recommended_focus_areas": recommended_focus_areas[:5],  # Top 5 recommendations
            "overall_mastery": round(
                sum(mastery_per_chapter.values()) / len(mastery_per_chapter),
                1
            ) if mastery_per_chapter else 0,
            "chapters_completed": sum(1 for p in progress_data if p.completion_status == "completed"),
            "total_chapters": len(progress_data)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


def calculate_improvement_rate(progress_data: list) -> float:
    """
    Calculate weekly improvement rate based on mastery scores.

    Args:
        progress_data: List of progress records

    Returns:
        Improvement rate (points per week)
    """
    if len(progress_data) < 2:
        return 0.0

    # Calculate average improvement per chapter
    scores = [p.mastery_score for p in progress_data if p.mastery_score > 0]
    if len(scores) < 2:
        return 0.0

    total_improvement = scores[-1] - scores[0]
    num_chapters = len(scores)

    # Assume approximately 1 chapter per day = 7 per week
    weeks_equivalent = num_chapters / 7
    if weeks_equivalent > 0:
        return round(total_improvement / weeks_equivalent, 2)
    return 0.0
