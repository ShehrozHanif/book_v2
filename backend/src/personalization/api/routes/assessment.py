"""Assessment and learning path routes."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session as get_db
from src.personalization.models.schemas import (
    AssessmentRequest, AssessmentResponse, AssessmentQuestion,
    PathRecommendation, LearningPathCreate, LearningPathResponse
)
from src.personalization.models.db_models import User
from src.personalization.services import assessment_service, learning_path_service, user_service
from src.personalization.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["assessment", "learning-paths"])


@router.get("/{user_id}/assessment/questions", response_model=List[AssessmentQuestion])
async def get_assessment_questions(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get assessment questions for user to answer.

    Args:
        user_id: User ID (must match current user)
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of assessment questions without correct answers

    Raises:
        HTTPException 403: If user_id doesn't match current user
    """
    # Verify user is accessing their own assessment
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' assessments"
        )

    # Get questions without answers
    questions = assessment_service.get_assessment_questions()

    return [AssessmentQuestion(**q) for q in questions]


@router.post("/{user_id}/assessment", response_model=AssessmentResponse)
async def submit_assessment(
    user_id: UUID,
    assessment_request: AssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit assessment answers and get skill score with recommended paths.

    Args:
        user_id: User ID (must match current user)
        assessment_request: User's answers to assessment questions
        current_user: Current authenticated user
        db: Database session

    Returns:
        AssessmentResponse with skill score, tier, and path recommendations

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 400: If assessment submission fails
    """
    # Verify user is submitting their own assessment
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot submit assessment for other users"
        )

    try:
        # Create assessment and calculate score
        assessment, skill_score, skill_tier = await assessment_service.create_assessment(
            db=db,
            user_id=user_id,
            answers=assessment_request.answers
        )

        # Update user's skill level
        await user_service.update_user_skill_level(
            db=db,
            user_id=user_id,
            skill_level=skill_score,
            skill_confidence=skill_score  # Use score as initial confidence
        )

        # Get path recommendations
        recommendations = learning_path_service.recommend_learning_paths(
            skill_score=skill_score,
            skill_tier=skill_tier
        )

        # Convert to response format
        path_recommendations = [
            PathRecommendation(
                name=rec["name"],
                match_percentage=rec["match_percentage"],
                description=rec["description"],
                chapters=rec["chapters"],
                estimated_hours=rec["estimated_hours"]
            )
            for rec in recommendations
        ]

        return AssessmentResponse(
            assessment_id=assessment.assessment_id,
            skill_score=skill_score,
            skill_tier=skill_tier,
            recommended_paths=path_recommendations
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process assessment: {str(e)}"
        )


@router.post("/{user_id}/paths", response_model=List[PathRecommendation])
async def get_path_recommendations(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get learning path recommendations based on user's skill level.

    Args:
        user_id: User ID (must match current user)
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of recommended learning paths with match percentages

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 404: If user not found

    Note:
        Recommendations are based on user's current skill_level.
        If no assessment has been taken, uses default skill level (50).
    """
    # Verify user is accessing their own data
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' recommendations"
        )

    # Get user's current skill level
    skill_score = current_user.skill_level
    skill_tier = assessment_service.determine_skill_tier(skill_score)

    # Get recommendations
    recommendations = learning_path_service.recommend_learning_paths(
        skill_score=skill_score,
        skill_tier=skill_tier
    )

    return [
        PathRecommendation(
            name=rec["name"],
            match_percentage=rec["match_percentage"],
            description=rec["description"],
            chapters=rec["chapters"],
            estimated_hours=rec["estimated_hours"]
        )
        for rec in recommendations
    ]


@router.post("/{user_id}/paths/{path_key}/select", response_model=LearningPathResponse)
async def select_learning_path(
    user_id: UUID,
    path_key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Select a learning path for the user.

    Args:
        user_id: User ID (must match current user)
        path_key: Path configuration key (beginner, developer, researcher, etc.)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created LearningPath record

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 400: If path_key is invalid

    Note:
        If user already has an active path, it will be marked as abandoned
        and the new path will become active.
    """
    # Verify user is selecting their own path
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot select path for other users"
        )

    try:
        # Create learning path
        learning_path = await learning_path_service.create_learning_path(
            db=db,
            user_id=user_id,
            path_key=path_key
        )

        return LearningPathResponse(
            path_id=learning_path.path_id,
            user_id=learning_path.user_id,
            path_name=learning_path.path_name,
            chapters=learning_path.chapters_array,
            completion_percentage=learning_path.completion_percentage,
            status=learning_path.status,
            created_at=learning_path.created_at,
            updated_at=learning_path.updated_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create learning path: {str(e)}"
        )


@router.get("/{user_id}/paths", response_model=LearningPathResponse)
async def get_current_learning_path(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's current active learning path.

    Args:
        user_id: User ID (must match current user)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Active LearningPath or 404 if none selected

    Raises:
        HTTPException 403: If user_id doesn't match current user
        HTTPException 404: If no active learning path found
    """
    # Verify user is accessing their own data
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' learning paths"
        )

    # Get active path
    learning_path = await learning_path_service.get_active_learning_path(
        db=db,
        user_id=user_id
    )

    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active learning path found. Please select a path first."
        )

    return LearningPathResponse(
        path_id=learning_path.path_id,
        user_id=learning_path.user_id,
        path_name=learning_path.path_name,
        chapters=learning_path.chapters_array,
        completion_percentage=learning_path.completion_percentage,
        status=learning_path.status,
        created_at=learning_path.created_at,
        updated_at=learning_path.updated_at
    )


@router.get("/{user_id}/paths/all", response_model=List[LearningPathResponse])
async def get_all_learning_paths(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all learning paths for user (active, completed, abandoned).

    Args:
        user_id: User ID (must match current user)
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of all learning paths

    Raises:
        HTTPException 403: If user_id doesn't match current user
    """
    # Verify user is accessing their own data
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' learning paths"
        )

    # Get all paths
    paths = await learning_path_service.get_all_user_paths(
        db=db,
        user_id=user_id
    )

    return [
        LearningPathResponse(
            path_id=path.path_id,
            user_id=path.user_id,
            path_name=path.path_name,
            chapters=path.chapters_array,
            completion_percentage=path.completion_percentage,
            status=path.status,
            created_at=path.created_at,
            updated_at=path.updated_at
        )
        for path in paths
    ]
