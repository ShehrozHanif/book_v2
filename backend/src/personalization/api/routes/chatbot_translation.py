"""
API routes for chatbot translation feature.

Endpoints:
1. GET /api/v1/chatbot/response/{template_key} - Get translated response
2. GET /api/v1/chatbot/templates - List templates
3. GET /api/v1/glossary/search - Search glossary terms
4. POST /api/v1/users/{user_id}/language - Set language preference
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
from typing import Optional, List
from uuid import UUID
import logging

from src.personalization.api.auth_middleware import (
    AuthMiddleware,
    raise_forbidden_if_not_user
)
from src.personalization.models.schemas import (
    ChatbotResponseRequest,
    ChatbotResponseData,
    ChatbotLanguageRequest,
    ChatbotLanguageResponse,
    GlossarySearchRequest,
    GlossaryTermSchema,
    UserLanguagePreferenceSchema
)
from src.personalization.services.chatbot_translation_service import (
    get_chatbot_translation_service
)
from src.personalization.services.glossary_service import (
    get_glossary_service
)
from src.personalization.services.language_preference_service import (
    get_language_preference_service
)
from src.database.connection import get_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["chatbot_translation"]
)


@router.get(
    "/chatbot/response/{template_key}",
    response_model=ChatbotResponseData,
    summary="Get translated chatbot response"
)
async def get_chatbot_response(
    template_key: str,
    language: str = "english",
    request: Request = None,
    db = Depends(get_session)
):
    """
    Get a chatbot response in requested language.

    Args:
        template_key: Unique template identifier
        language: Target language (english, urdu)
        request: HTTP request

    Returns:
        ChatbotResponseData: Response with content and metadata

    Raises:
        401: If Urdu requested without authentication
        404: If template not found
    """
    try:
        # Validate language parameter
        if language.lower() not in ["english", "urdu"]:
            language = "english"

        # Require authentication for Urdu responses
        if language.lower() == "urdu":
            try:
                user = AuthMiddleware.get_authenticated_user(request)
                request.state.user = user
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required for Urdu language content"
                )

        # Get translation service and fetch response
        translation_service = get_chatbot_translation_service(db)
        response = await translation_service.get_translated_response(
            template_key,
            language
        )

        if "error" in response:
            raise HTTPException(
                status_code=response.get("status", 500),
                detail=response.get("error")
            )

        return ChatbotResponseData(**response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chatbot response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch response"
        )


@router.get(
    "/chatbot/templates",
    response_model=List[dict],
    summary="List all response templates"
)
async def list_templates(
    status_filter: Optional[str] = "published",
    limit: int = 100,
    db = Depends(get_session)
):
    """
    List available response templates.

    Args:
        status_filter: Filter by status (published, draft, archived)
        limit: Maximum results

    Returns:
        list: Response templates
    """
    try:
        translation_service = get_chatbot_translation_service(db)
        templates = await translation_service.list_templates(
            status=status_filter,
            limit=limit
        )
        return templates
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch templates"
        )


@router.get(
    "/glossary/search",
    response_model=List[GlossaryTermSchema],
    summary="Search glossary terms"
)
async def search_glossary(
    q: str,
    language: str = "english",
    category: Optional[str] = None,
    limit: int = 20,
    db = Depends(get_session)
):
    """
    Search glossary terms by keyword.

    Args:
        q: Search query
        language: Search language (english, urdu)
        category: Filter by category
        limit: Maximum results

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
    "/glossary/terms",
    response_model=List[GlossaryTermSchema],
    summary="List all glossary terms"
)
async def list_glossary_terms(
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db = Depends(get_session)
):
    """
    List glossary terms with optional filtering.

    Args:
        category: Filter by category
        limit: Maximum results
        offset: Pagination offset

    Returns:
        list: Glossary terms
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
            detail="Failed to fetch glossary"
        )


@router.post(
    "/users/{user_id}/language",
    response_model=ChatbotLanguageResponse,
    summary="Set user language preference"
)
async def set_user_language(
    user_id: UUID,
    request_data: ChatbotLanguageRequest,
    request: Request = None,
    db = Depends(get_session)
):
    """
    Set user's language preference for chatbot.

    Requires: User authentication, matching user_id

    Args:
        user_id: User ID
        request_data: Language preference data
        request: HTTP request

    Returns:
        ChatbotLanguageResponse: Updated preference

    Raises:
        400: Invalid language
        401: Not authenticated
        403: User mismatch
    """
    try:
        # Require authentication
        user = AuthMiddleware.get_authenticated_user(request)
        request.state.user = user

        # Verify user is setting own preference
        auth_user_id = user.get("sub")
        raise_forbidden_if_not_user(auth_user_id, str(user_id))

        # Set language preference
        language_service = get_language_preference_service(db)

        # Validate language
        if not await language_service.validate_language(request_data.language):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {request_data.language}"
            )

        success = await language_service.set_user_language(
            user_id,
            request_data.language
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save preference"
            )

        # Get updated preference
        preference = await language_service.get_user_preference(user_id)

        return ChatbotLanguageResponse(
            user_id=str(user_id),
            language=preference["language"],
            message="Language preference updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting language preference: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preference"
        )


@router.get(
    "/users/{user_id}/language",
    response_model=UserLanguagePreferenceSchema,
    summary="Get user language preference"
)
async def get_user_language(
    user_id: UUID,
    request: Request = None,
    db = Depends(get_session)
):
    """
    Get user's language preference.

    Requires: User authentication, matching user_id

    Args:
        user_id: User ID
        request: HTTP request

    Returns:
        UserLanguagePreferenceSchema: User's language preference

    Raises:
        401: Not authenticated
        403: User mismatch
    """
    try:
        # Require authentication
        user = AuthMiddleware.get_authenticated_user(request)
        request.state.user = user

        # Verify user is getting own preference
        auth_user_id = user.get("sub")
        raise_forbidden_if_not_user(auth_user_id, str(user_id))

        # Get language preference
        language_service = get_language_preference_service(db)
        preference = await language_service.get_user_preference(user_id)

        return UserLanguagePreferenceSchema(**preference)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting language preference: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch preference"
        )
