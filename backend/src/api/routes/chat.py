"""Chat API endpoints for RAG chatbot."""

import logging
import time
from typing import Optional, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from src.database.connection import get_session
from src.api.dependencies import validate_chat_request
from src.api.rate_limiter import get_client_ip
from src.config import get_settings
from src.services.chat_service import get_chat_service
from src.services.embedding_service import get_embedding_service
from src.services.qdrant_client import get_qdrant_service
from src.personalization.services.personalization_service import get_personalization_service
from src.personalization.services.performance_service import get_performance_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
settings = get_settings()


# ===== Pydantic Models for Embed Endpoint =====
class TextbookChunk(BaseModel):
    """Schema for a single textbook passage chunk."""

    content: str = Field(
        ...,
        description="Actual paragraph or section text (200-500 words recommended)",
        min_length=10,
        max_length=5000,
    )
    module: str = Field(
        ...,
        description="Module identifier (e.g., 'Module 1')",
        min_length=1,
        max_length=100,
    )
    chapter: str = Field(
        ...,
        description="Chapter identifier (e.g., 'Chapter 1: Fundamentals')",
        min_length=1,
        max_length=200,
    )
    section: str = Field(
        ...,
        description="Section identifier (e.g., '1.1 Introduction to ROS 2')",
        min_length=1,
        max_length=200,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "ROS 2 (Robot Operating System 2) is a flexible middleware for writing robot software...",
                "module": "Module 1",
                "chapter": "Chapter 1: Fundamentals",
                "section": "1.1 Introduction to ROS 2",
            }
        }


class EmbedRequest(BaseModel):
    """Schema for textbook content embedding request."""

    chunks: List[TextbookChunk] = Field(
        ...,
        description="List of textbook chunks to embed and index",
        min_items=1,
    )
    collection_name: Optional[str] = Field(
        default="textbook_chunks",
        description="Qdrant collection name (optional, defaults to 'textbook_chunks')",
        max_length=100,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chunks": [
                    {
                        "content": "ROS 2 is a flexible middleware...",
                        "module": "Module 1",
                        "chapter": "Chapter 1",
                        "section": "1.1 Introduction",
                    }
                ],
                "collection_name": "textbook_chunks",
            }
        }


class EmbedResponse(BaseModel):
    """Schema for textbook content embedding response."""

    success: bool = Field(..., description="Whether embedding succeeded")
    chunks_embedded: int = Field(
        ...,
        description="Number of chunks successfully embedded and indexed",
    )
    collection: str = Field(
        ...,
        description="Qdrant collection name used for storage",
    )
    message: str = Field(..., description="Status message with details")


@router.post(
    "",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Chat with RAG bot",
    description="Send a query to the RAG-powered chatbot and receive a response with relevant textbook passages.",
)
async def chat(
    request: ChatRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """
    Process a chat request through the RAG pipeline.

    This endpoint implements the complete RAG (Retrieval-Augmented Generation) workflow:
    1. Validates the user query
    2. Embeds the query using OpenAI embeddings
    3. Retrieves relevant textbook passages from Qdrant vector database
    4. Loads conversation history for multi-turn support
    5. Generates response using LLM with retrieved context
    6. Stores messages in database for conversation tracking
    7. Returns response with citations, retrieved passages, and relevance scores

    Args:
        request: ChatRequest containing query and optional conversation context
        http_request: FastAPI request object for rate limiting info
        session: Database session for storing conversation data

    Returns:
        ChatResponse with bot response, retrieved passages, scores, and timing

    Raises:
        HTTPException: For validation errors (400) or processing failures (500)
    """
    start_time = time.time()
    client_ip = get_client_ip(http_request)

    try:
        # Step 1: Validate request
        validated = validate_chat_request(request)
        logger.debug(f"Request validated - IP: {client_ip}")

        # Step 2: Get services
        chat_service = await get_chat_service(session)
        personalization_service = await get_personalization_service(session)
        performance_service = await get_performance_service(session)

        # DEBUG: Log service instances
        logger.info(f"[HTTP] ChatService instance ID: {id(chat_service)}")
        logger.info(f"[HTTP] RetrievalService instance ID: {id(chat_service.retrieval_service)}")

        # Step 3: Convert user_id if provided
        user_uuid = None
        if validated.user_id:
            try:
                from uuid import UUID
                user_uuid = UUID(validated.user_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id format: {validated.user_id}")

        # Step 4: Process query through RAG pipeline with personalization
        response = await chat_service.process_query(
            query=validated.query,
            conversation_id=validated.conversation_id,
            user_id=validated.user_id,
            difficulty_override=validated.difficulty_override
        )

        # Step 5: Apply personalization to response if user authenticated
        if user_uuid:
            # Track this conversation turn for performance analysis
            await performance_service.track_conversation_turn(
                user_id=user_uuid,
                query=validated.query,
                response=response.response,
                conversation_id=None
            )

        logger.info(
            f"Chat response generated in {response.processing_time_ms:.0f}ms - "
            f"conversation_id: {response.conversation_id}, "
            f"passages_retrieved: {len(response.retrieved_passages)}, "
            f"personalized: {user_uuid is not None}, "
            f"ip: {client_ip}"
        )

        return response

    except HTTPException as e:
        # Re-raise HTTP exceptions from validation
        logger.warning(f"HTTP validation error ({e.status_code}): {e.detail}")
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat request",
        )


@router.post(
    "/embed",
    response_model=EmbedResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request format or content"},
        500: {"model": ErrorResponse, "description": "Embedding or indexing failed"},
    },
    summary="Embed and index textbook content",
    description="Admin endpoint to embed textbook passages and index them in Qdrant vector database for RAG retrieval.",
)
async def embed_content(
    request: EmbedRequest,
    session: AsyncSession = Depends(get_session),
) -> EmbedResponse:
    """
    Embed and index textbook content for RAG retrieval.

    This admin endpoint implements the complete content ingestion pipeline:
    1. Validates textbook chunks (content, metadata)
    2. Creates Qdrant collection if needed
    3. Generates embeddings via OpenAI API (text-embedding-3-small, 1536-dim vectors)
    4. Upserts vectors to Qdrant with metadata (module, chapter, section)
    5. Returns success count and status

    Args:
        request: EmbedRequest with list of TextbookChunk objects
        session: Database session for potential future use

    Returns:
        EmbedResponse with success status, chunk count, collection name, and message

    Raises:
        HTTPException 400: If chunks list is empty or validation fails
        HTTPException 500: If embedding or Qdrant upsert fails

    Example Request:
        POST /api/v1/chat/embed
        {
            "chunks": [
                {
                    "content": "ROS 2 (Robot Operating System 2) is a flexible middleware...",
                    "module": "Module 1",
                    "chapter": "Chapter 1: Fundamentals",
                    "section": "1.1 Introduction to ROS 2"
                },
                {
                    "content": "The core concept in ROS 2 is the ability to design complex...",
                    "module": "Module 1",
                    "chapter": "Chapter 1: Fundamentals",
                    "section": "1.2 Core Concepts"
                }
            ],
            "collection_name": "textbook_chunks"
        }

    Example Response:
        {
            "success": true,
            "chunks_embedded": 2,
            "collection": "textbook_chunks",
            "message": "Successfully embedded 2 passages into Qdrant"
        }
    """
    start_time = time.time()

    try:
        # Step 1: Validate input
        if not request.chunks:
            logger.warning("Embed request received with empty chunks list")
            raise ValueError("No chunks provided")

        logger.info(
            f"Embedding request received - chunks: {len(request.chunks)}, "
            f"collection: {request.collection_name}"
        )

        # Step 2: Get service instances
        embedding_service = get_embedding_service()
        qdrant_service = get_qdrant_service()

        # Step 3: Create Qdrant collection if needed
        try:
            await qdrant_service.create_collection()
            logger.info(f"Collection '{request.collection_name}' ready for indexing")
        except Exception as e:
            logger.warning(f"Collection creation warning (may already exist): {e}")

        # Step 4: Prepare chunks for embedding
        # Convert Pydantic models to dicts
        chunk_dicts = [
            {
                "content": chunk.content,
                "module": chunk.module,
                "chapter": chunk.chapter,
                "section": chunk.section,
            }
            for chunk in request.chunks
        ]

        logger.debug(f"Prepared {len(chunk_dicts)} chunks for embedding")

        # Step 5: Embed all passages via OpenAI
        try:
            embedded_passages = await embedding_service.embed_passages(chunk_dicts)
            logger.info(
                f"Successfully embedded {len(embedded_passages)} passages "
                f"(processing time: {time.time() - start_time:.2f}s)"
            )
        except Exception as e:
            logger.error(f"Embedding failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to embed passages: {str(e)}",
            )

        # Step 6: Prepare points for Qdrant upsert
        points_to_upsert = [
            {
                "id": p["id"],  # Hash-based ID from embedding_service
                "vector": p["vector"],  # 1536-dimensional vector
                "payload": {
                    "content": p["content"],
                    "module": p["module"],
                    "chapter": p["chapter"],
                    "section": p["section"],
                },
            }
            for p in embedded_passages
        ]

        logger.debug(f"Prepared {len(points_to_upsert)} points for Qdrant upsert")

        # Step 7: Upsert vectors to Qdrant
        try:
            await qdrant_service.upsert(points_to_upsert)
            logger.info(
                f"Successfully upserted {len(points_to_upsert)} vectors to Qdrant"
            )
        except Exception as e:
            logger.error(f"Qdrant upsert failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to index passages in Qdrant: {str(e)}",
            )

        # Step 8: Build success response
        processing_time = time.time() - start_time
        response = EmbedResponse(
            success=True,
            chunks_embedded=len(request.chunks),
            collection=request.collection_name,
            message=(
                f"Successfully embedded {len(request.chunks)} passages into "
                f"'{request.collection_name}' in {processing_time:.2f}s"
            ),
        )

        logger.info(
            f"Embed endpoint completed successfully - "
            f"chunks: {len(request.chunks)}, "
            f"time: {processing_time:.2f}s"
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.warning(f"Validation error in embed endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            f"Unexpected error in embed endpoint: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding pipeline failed - please check logs",
        )


@router.get(
    "/conversations/{conversation_id}",
    summary="Get conversation history",
    description="Retrieve message history for a conversation.",
    response_model=dict,
)
async def get_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Retrieve conversation history by ID.

    Args:
        conversation_id: UUID of the conversation
        session: Database session

    Returns:
        Conversation metadata and message history

    Raises:
        HTTPException: If conversation not found
    """
    # TODO: Implement conversation retrieval
    # 1. Query conversations table
    # 2. Fetch associated messages
    # 3. Format response

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Conversation retrieval not yet implemented",
    )


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete conversation",
    description="Delete a conversation and all associated messages.",
)
async def delete_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Delete a conversation and cascade delete messages.

    Args:
        conversation_id: UUID of the conversation to delete
        session: Database session

    Raises:
        HTTPException: If conversation not found
    """
    # TODO: Implement conversation deletion
    # 1. Verify conversation exists
    # 2. Delete associated messages
    # 3. Delete conversation record

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Conversation deletion not yet implemented",
    )


@router.post(
    "/simplify",
    response_model=dict,
    summary="Simplify response difficulty",
    description="Request a simplified version of the response for the current query.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized - user_id required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def simplify_response(
    request: ChatRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Request a simplified version of the chatbot response.

    This endpoint triggers adaptive difficulty adjustment:
    - Tracks simplify request
    - Adjusts user's skill level down by 10 points
    - Reduces confidence score

    Args:
        request: ChatRequest (requires user_id)
        http_request: FastAPI request object
        session: Database session

    Returns:
        Dictionary with adjustment details and new difficulty level

    Raises:
        HTTPException: If user_id not provided or processing fails
    """
    try:
        if not request.user_id:
            logger.warning("Simplify request without user_id")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user_id is required for difficulty adjustment"
            )

        # Get adaptive difficulty service
        from src.personalization.services.adaptive_difficulty_service import (
            get_adaptive_difficulty_service
        )
        from uuid import UUID

        try:
            user_uuid = UUID(request.user_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid user_id format: {request.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format"
            )

        adaptive_service = await get_adaptive_difficulty_service(session)
        result = await adaptive_service.track_simplify_request(user_uuid)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to adjust difficulty")
            )

        logger.info(f"Difficulty simplified for user {request.user_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in simplify endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process difficulty adjustment"
        )


@router.post(
    "/advanced",
    response_model=dict,
    summary="Increase response difficulty",
    description="Request a more advanced version of the response for the current query.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized - user_id required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def advanced_response(
    request: ChatRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Request a more advanced version of the chatbot response.

    This endpoint triggers adaptive difficulty adjustment:
    - Tracks advanced request
    - Adjusts user's skill level up by 10 points
    - Increases confidence score

    Args:
        request: ChatRequest (requires user_id)
        http_request: FastAPI request object
        session: Database session

    Returns:
        Dictionary with adjustment details and new difficulty level

    Raises:
        HTTPException: If user_id not provided or processing fails
    """
    try:
        if not request.user_id:
            logger.warning("Advanced request without user_id")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user_id is required for difficulty adjustment"
            )

        # Get adaptive difficulty service
        from src.personalization.services.adaptive_difficulty_service import (
            get_adaptive_difficulty_service
        )
        from uuid import UUID

        try:
            user_uuid = UUID(request.user_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid user_id format: {request.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format"
            )

        adaptive_service = await get_adaptive_difficulty_service(session)
        result = await adaptive_service.track_advanced_request(user_uuid)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to adjust difficulty")
            )

        logger.info(f"Difficulty increased for user {request.user_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in advanced endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process difficulty adjustment"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the chat service is operational.",
    response_model=dict,
)
async def health() -> dict:
    """
    Health check endpoint for the chat service.

    Returns:
        dict: Status information including service name and status
    """
    return {
        "status": "ok",
        "service": "chat",
        "version": "1.0.0"
    }
