"""
Glossary API Routes for Technical Terminology Support

Endpoints for managing and retrieving technical terms with bilingual support:
1. GET /api/v1/glossary - List all glossary terms
2. GET /api/v1/glossary/{term_id} - Get specific term
3. GET /api/v1/glossary/search - Search for terms
4. POST /api/v1/glossary/feedback - Submit glossary feedback

Features:
- Bilingual term definitions (English + Urdu)
- Pronunciation guides (transliterated)
- Consistency validation
- Feedback collection
- Authentication-gated Urdu access
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from typing import Optional, List
from uuid import UUID
import logging

from src.personalization.api.auth_middleware import (
    AuthMiddleware,
    raise_forbidden_if_not_user
)
from src.personalization.models.schemas import (
    GlossaryTermSchema,
)
from src.personalization.services.glossary_service import (
    get_glossary_service
)
from src.database.connection import get_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["glossary"]
)


@router.get(
    "/glossary",
    response_model=List[GlossaryTermSchema],
    summary="List all glossary terms"
)
async def list_glossary_terms(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db = Depends(get_session)
):
    """
    List all glossary terms with optional filtering.

    Args:
        category: Filter by category (robotics, control, kinematics, etc.)
        limit: Maximum results to return (1-200)
        offset: Pagination offset

    Returns:
        list: Glossary terms with definitions and translations
    """
    try:
        glossary_service = get_glossary_service(db)
        terms = await glossary_service.list_terms(
            category=category,
            limit=limit,
            offset=offset
        )
        return terms
    except Exception as e:
        logger.error(f"Error listing glossary terms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch glossary terms"
        )


@router.get(
    "/glossary/{term_id}",
    response_model=GlossaryTermSchema,
    summary="Get glossary term by ID"
)
async def get_glossary_term(
    term_id: str,
    db = Depends(get_session)
):
    """
    Get a specific glossary term by English term name.

    Args:
        term_id: English term name (e.g., "ROS 2 Node")

    Returns:
        GlossaryTermSchema: Term with full details

    Raises:
        404: If term not found
    """
    try:
        glossary_service = get_glossary_service(db)
        term = await glossary_service.get_term(term_id)

        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Glossary term '{term_id}' not found"
            )

        return term
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting glossary term: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch term"
        )


@router.get(
    "/glossary/search",
    response_model=List[GlossaryTermSchema],
    summary="Search glossary terms"
)
async def search_glossary_terms(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    language: str = Query("english", regex="^(english|urdu)$", description="Search language"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db = Depends(get_session)
):
    """
    Search glossary terms by keyword.

    Args:
        q: Search query (required)
        language: Search in english or urdu (default: english)
        category: Optional category filter
        limit: Maximum results (1-100)

    Returns:
        list: Matching glossary terms
    """
    try:
        glossary_service = get_glossary_service(db)
        terms = await glossary_service.search_terms(
            query_text=q,
            language=language,
            category=category,
            limit=limit
        )
        return terms
    except Exception as e:
        logger.error(f"Error searching glossary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search glossary"
        )


@router.get(
    "/glossary/categories",
    response_model=List[str],
    summary="Get all glossary categories"
)
async def get_glossary_categories(
    db = Depends(get_session)
):
    """
    Get list of all available glossary categories.

    Returns:
        list: Category names (robotics, control, kinematics, etc.)
    """
    try:
        glossary_service = get_glossary_service(db)
        categories = await glossary_service.get_categories()
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )


@router.post(
    "/glossary/feedback",
    summary="Submit glossary feedback"
)
async def submit_glossary_feedback(
    feedback_type: str = Query(..., regex="^(suggestion|correction|new_term)$"),
    content: str = Query(..., min_length=10, max_length=500),
    glossary_term_id: Optional[str] = Query(None),
    suggested_term: Optional[str] = Query(None),
    request: Request = None,
    db = Depends(get_session)
):
    """
    Submit feedback about glossary terms.

    Args:
        feedback_type: Type of feedback (suggestion, correction, new_term)
        content: Feedback content (10-500 characters)
        glossary_term_id: Related term ID (if applicable)
        suggested_term: New term name (for new_term type)
        request: HTTP request

    Returns:
        dict: Feedback submission status

    Raises:
        400: Invalid input
        401: Not authenticated
    """
    try:
        # Get authenticated user
        user = AuthMiddleware.get_authenticated_user(request)
        request.state.user = user
        user_id = UUID(user.get("sub"))

        glossary_service = get_glossary_service(db)

        feedback = await glossary_service.create_feedback(
            user_id=user_id,
            feedback_type=feedback_type,
            content=content,
            glossary_term_id=UUID(glossary_term_id) if glossary_term_id else None,
            suggested_term=suggested_term
        )

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit feedback"
            )

        logger.info(
            f"User {user_id} submitted {feedback_type} feedback: {content[:50]}..."
        )

        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": str(feedback.get("id"))
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


@router.get(
    "/glossary/stats",
    summary="Get glossary statistics"
)
async def get_glossary_stats(
    db = Depends(get_session)
):
    """
    Get glossary statistics (total terms, categories, etc.).

    Returns:
        dict: Statistics including term count, category count, etc.
    """
    try:
        glossary_service = get_glossary_service(db)

        # Get all terms and categories
        all_terms = await glossary_service.list_terms(limit=10000)
        categories = await glossary_service.get_categories()

        return {
            "total_terms": len(all_terms),
            "total_categories": len(categories),
            "categories": categories,
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error getting glossary stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )
