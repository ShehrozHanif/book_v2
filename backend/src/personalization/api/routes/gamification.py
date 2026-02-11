"""Gamification API endpoints for achievements, practice, and statistics."""

import logging
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session
from src.personalization.api.dependencies import get_current_user
from sqlalchemy import select
from src.personalization.models.db_models import User, Progress
from src.personalization.services.achievement_service import get_achievement_service
from src.personalization.services.practice_service import get_practice_service
from src.personalization.services.statistics_service import get_statistics_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["gamification"])


# ===== Request/Response Models =====
class PracticeAnswerRequest(BaseModel):
    """Request model for submitting practice answers."""

    answers: Dict[str, str] = Field(
        ...,
        description="Mapping of question IDs to selected answer letters"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answers": {
                    "q1_1": "A",
                    "q1_2": "B",
                    "q1_3": "A",
                    "q1_4": "C",
                    "q1_5": "D"
                }
            }
        }


class PracticeQuestion(BaseModel):
    """Practice question model."""

    id: str
    question: str
    options: list
    difficulty: str


class PracticeResponse(BaseModel):
    """Response model for practice attempt."""

    score: int = Field(..., description="Score 0-100")
    message: str = Field(..., description="Feedback message")
    passed: bool = Field(..., description="Whether user passed (>=60%)")


class AchievementInfo(BaseModel):
    """Achievement information model."""

    type: str
    title: str
    description: str
    icon: str
    points: int
    earned_date: str = None


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")


# ===== Achievement Endpoints =====
@router.get(
    "/{user_id}/achievements",
    response_model=Dict[str, Any],
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get user achievements",
    description="Retrieve all achievements for a user (earned and locked).",
)
async def get_achievements(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get all achievements for a user.

    Args:
        user_id: User ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Dictionary with earned and locked achievements

    Raises:
        HTTPException: If user not found
    """
    # Authorization check - users can view their own or admins can view any
    if current_user.user_id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own achievements"
        )

    achievement_service = await get_achievement_service(session)
    achievements = await achievement_service.get_user_achievements(user_id)

    logger.info(f"Retrieved achievements for user {user_id}")

    return achievements


# ===== Practice Endpoints =====
@router.get(
    "/{user_id}/chapters/{chapter_id}/practice",
    response_model=Dict[str, Any],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid chapter ID"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get practice questions",
    description="Retrieve practice questions for a specific chapter.",
)
async def get_practice_questions(
    user_id: UUID,
    chapter_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get practice questions for a chapter.

    Args:
        user_id: User ID
        chapter_id: Chapter ID (1-22)
        session: Database session
        current_user: Current authenticated user

    Returns:
        Dictionary with practice questions

    Raises:
        HTTPException: If chapter invalid or user not found
    """
    # Authorization check
    if current_user.user_id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own practice"
        )

    # Validate chapter ID
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    practice_service = await get_practice_service(session)
    questions = await practice_service.get_practice_questions(chapter_id, limit=5)

    logger.info(f"Retrieved {len(questions)} practice questions for user {user_id}, chapter {chapter_id}")

    return {
        "chapter_id": chapter_id,
        "question_count": len(questions),
        "questions": questions
    }


@router.post(
    "/{user_id}/chapters/{chapter_id}/practice",
    response_model=PracticeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid chapter or answers"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Submit practice answers",
    description="Submit answers to practice questions and get scored.",
)
async def submit_practice_answers(
    user_id: UUID,
    chapter_id: int,
    request: PracticeAnswerRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PracticeResponse:
    """
    Submit practice answers and get scored.

    Args:
        user_id: User ID
        chapter_id: Chapter ID (1-22)
        request: Practice answers
        session: Database session
        current_user: Current authenticated user

    Returns:
        Practice score and feedback

    Raises:
        HTTPException: If invalid chapter or unauthorized
    """
    # Authorization check
    if current_user.user_id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own practice"
        )

    # Validate chapter ID
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    practice_service = await get_practice_service(session)

    # Get questions for scoring
    questions = await practice_service.get_practice_questions(chapter_id, limit=5)

    # Save attempt and get score
    attempt = await practice_service.save_practice_attempt(
        user_id,
        chapter_id,
        questions,
        request.answers
    )

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save practice attempt"
        )

    # Determine if passed (60% or higher)
    passed = attempt.score >= 60

    message = (
        f"Great work! You scored {attempt.score}%" if passed
        else f"You scored {attempt.score}%. Try again to improve!"
    )

    logger.info(f"Practice submitted: user={user_id}, chapter={chapter_id}, score={attempt.score}")

    # Update Progress record with practice results so dashboard reflects quiz scores
    try:
        result = await session.execute(
            select(Progress).where(
                Progress.user_id == user_id,
                Progress.chapter_id == chapter_id
            )
        )
        progress = result.scalar_one_or_none()
        if progress:
            progress.practice_attempts = (progress.practice_attempts or 0) + 1
            if attempt.score > (progress.highest_practice_score or 0):
                progress.highest_practice_score = attempt.score
            # Update mastery_score to reflect best practice score
            if attempt.score > (progress.mastery_score or 0):
                progress.mastery_score = attempt.score
            await session.commit()
        else:
            # Create a new Progress record if one doesn't exist
            new_progress = Progress(
                user_id=user_id,
                chapter_id=chapter_id,
                completion_status='in_progress',
                mastery_score=attempt.score,
                practice_attempts=1,
                highest_practice_score=attempt.score,
            )
            session.add(new_progress)
            await session.commit()
    except Exception as e:
        logger.warning(f"Failed to update progress after practice: {e}")

    return PracticeResponse(
        score=attempt.score,
        message=message,
        passed=passed
    )


@router.get(
    "/{user_id}/chapters/{chapter_id}/practice/history",
    response_model=Dict[str, Any],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid chapter ID"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get practice history",
    description="Retrieve practice attempt history for a chapter.",
)
async def get_practice_history(
    user_id: UUID,
    chapter_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get practice history for a chapter.

    Args:
        user_id: User ID
        chapter_id: Chapter ID (1-22)
        session: Database session
        current_user: Current authenticated user

    Returns:
        Practice history and statistics

    Raises:
        HTTPException: If chapter invalid or unauthorized
    """
    # Authorization check
    if current_user.user_id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own practice history"
        )

    # Validate chapter ID
    if not (1 <= chapter_id <= 22):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter ID must be between 1 and 22"
        )

    practice_service = await get_practice_service(session)
    history = await practice_service.get_chapter_practice_history(user_id, chapter_id)

    logger.info(f"Retrieved practice history for user {user_id}, chapter {chapter_id}")

    return history


# ===== Statistics Endpoints =====
@router.get(
    "/{user_id}/statistics",
    response_model=Dict[str, Any],
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get comprehensive statistics",
    description="Retrieve comprehensive learning statistics for dashboard.",
)
async def get_statistics(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get comprehensive statistics for user.

    Args:
        user_id: User ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Comprehensive user statistics

    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Authorization check
    if current_user.user_id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own statistics"
        )

    statistics_service = await get_statistics_service(session)
    stats = await statistics_service.get_comprehensive_statistics(user_id)

    logger.info(f"Retrieved statistics for user {user_id}")

    return stats


@router.get(
    "/{user_id}/statistics/overview",
    response_model=Dict[str, Any],
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get progress overview",
    description="Get quick overview of learning progress.",
)
async def get_progress_overview(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get quick progress overview.

    Args:
        user_id: User ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Quick overview of progress

    Raises:
        HTTPException: If unauthorized
    """
    # Authorization check
    if current_user.user_id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own statistics"
        )

    statistics_service = await get_statistics_service(session)
    overview = await statistics_service.get_overall_progress(user_id)

    logger.info(f"Retrieved progress overview for user {user_id}")

    return overview
