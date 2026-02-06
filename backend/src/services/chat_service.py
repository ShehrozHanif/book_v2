"""Chat service for orchestrating the full RAG pipeline."""

import time
import logging
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.services.embedding_service import get_embedding_service
from src.services.retrieval_service import get_retrieval_service
from src.services.generation_service import get_generation_service
from src.services.conversation_service import get_conversation_service
from src.services.security_service import get_security_service
from src.models.schemas import ChatResponse
from src.models.database import AuditLog
from src.logger import get_logger

logger = logging.getLogger(__name__)
structured_logger = get_logger(__name__)


class ChatService:
    """Service for orchestrating the full RAG chat pipeline."""

    def __init__(
        self,
        session: AsyncSession,
        embedding_service=None,
        retrieval_service=None,
        generation_service=None,
        security_service=None
    ):
        """Initialize chat service with dependencies.

        Args:
            session: AsyncSession for database operations
            embedding_service: Optional EmbeddingService instance
            retrieval_service: Optional RetrievalService instance
            generation_service: Optional GenerationService instance
            security_service: Optional SecurityService instance
        """
        self.session = session
        self.embedding_service = (
            embedding_service or get_embedding_service()
        )
        self.retrieval_service = (
            retrieval_service or get_retrieval_service()
        )
        self.generation_service = (
            generation_service or get_generation_service()
        )
        self.security_service = (
            security_service or get_security_service()
        )

    async def process_query(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        difficulty_override: Optional[str] = None,
    ) -> ChatResponse:
        """Process user query through full RAG pipeline with safety checks.

        Pipeline steps:
        0. Validate and sanitize query (security checks)
        1. Embed query using OpenAI embeddings
        2. Retrieve relevant passages from Qdrant vector database
        3. Check if query is off-topic
        4. Load conversation history for multi-turn support
        5. Generate response using LLM with context and history
        6. Save messages to database for conversation tracking
        7. Return response with citations, retrieved passages, and metadata

        Args:
            query: User's question/query
            conversation_id: Optional UUID string for multi-turn conversations
            user_id: Optional UUID string for user tracking
            difficulty_override: Optional difficulty override ('simplify' or 'advanced')

        Returns:
            ChatResponse with response text, retrieved passages, scores, and timing

        Raises:
            ValueError: If query is invalid
            Exception: If any pipeline step fails
        """
        start_time = time.time()

        try:
            # Generate conversation ID early for consistency
            final_conversation_id = conversation_id or str(uuid4())
            conversation_uuid = None
            if conversation_id:
                try:
                    conversation_uuid = UUID(conversation_id)
                except (ValueError, AttributeError):
                    conversation_uuid = None

            # Step 0: Validate and sanitize query
            # Check for empty query
            if not query or not query.strip():
                logger.info("Empty query received")
                return ChatResponse(
                    response="Please ask a question about the Humanoid Robotics textbook. For example: 'What is ROS 2?' or 'Explain inverse kinematics.'",
                    conversation_id=final_conversation_id,
                    retrieved_passages=[],
                    relevance_scores=[],
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )

            # Sanitize query
            original_query = query
            query = self.security_service.sanitize_query(query)

            if not query:
                logger.warning("Query became empty after sanitization")
                return ChatResponse(
                    response="I couldn't process your query. Please rephrase your question.",
                    conversation_id=final_conversation_id,
                    retrieved_passages=[],
                    relevance_scores=[],
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )

            # Check for injection attempts
            is_injection, pattern = self.security_service.detect_injection_attempt(query)
            if is_injection:
                logger.warning(f"Potential injection detected: pattern={pattern}")
                return ChatResponse(
                    response="I detected an unusual pattern in your query. Could you rephrase your question about the textbook?",
                    conversation_id=final_conversation_id,
                    retrieved_passages=[],
                    relevance_scores=[],
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )

            logger.info(f"Processing query: {query[:50]}...")

            # Log incoming query (anonymized)
            structured_logger.log_query(
                query=query,
                conversation_id=final_conversation_id,
                user_id=user_id
            )

            # Step 1: Embed query
            query_vector = await self.embedding_service.embed_query(query)
            logger.debug("Query embedding complete")

            # Step 2: Retrieve relevant passages
            logger.info(f"[CHAT] About to call retrieve_context with query: {query}")
            context_passages, relevance_scores = (
                await self.retrieval_service.retrieve_context(
                    query_vector=query_vector,
                    query=query
                )
            )
            logger.info(f"[CHAT] retrieve_context returned {len(context_passages)} passages")
            for i, (p, s) in enumerate(zip(context_passages, relevance_scores), 1):
                ch = p.split('Chapter')[1].strip().split()[0] if 'Chapter' in p else '?'
                logger.info(f"[CHAT]   [{i}] Chapter {ch} (score: {s:.3f})")
            logger.debug(
                f"Retrieved {len(context_passages)} passages "
                f"with avg score {sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0:.3f}"
            )

            # Step 3: Check if query is off-topic
            is_off_topic, best_score = self.security_service.detect_off_topic(
                query=query,
                retrieved_passages=context_passages,
                relevance_scores=relevance_scores,
                threshold=0.3
            )

            if is_off_topic:
                logger.info(f"Off-topic query detected (best score: {best_score:.3f})")
                return ChatResponse(
                    response="I can help with questions about Humanoid Robotics. Please ask about the textbook content, such as kinematics, dynamics, ROS 2, or robot control systems.",
                    conversation_id=final_conversation_id,
                    retrieved_passages=context_passages,
                    relevance_scores=relevance_scores,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )

            # Step 4: Load conversation history (if multi-turn)
            conversation_history = []
            if conversation_uuid:
                conversation_service = await get_conversation_service(self.session)
                try:
                    messages = await conversation_service.get_context_window(
                        conversation_uuid,
                        max_tokens=2000,
                        max_messages=20
                    )
                    conversation_history = (
                        await conversation_service.format_context_for_prompt(messages)
                    )
                    logger.debug(
                        f"Loaded {len(messages)} messages from conversation history"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to load conversation history: {e}. "
                        f"Proceeding without history."
                    )

            # Step 5: Generate response with personalization if user is authenticated
            try:
                # Import personalization service
                from src.personalization.services.personalization_service import get_personalization_service
                personalization_service = await get_personalization_service(self.session)

                # Build personalized prompt with user context
                user_uuid = None
                difficulty_override = None
                if user_id:
                    try:
                        from uuid import UUID
                        user_uuid = UUID(user_id)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid user_id format: {user_id}")

                # Build context text from passages
                context_text = "\n\n".join([f"[PASSAGE]\n{p}\n[/PASSAGE]" for p in context_passages])

                # Generate personalized prompt
                personalization_result = await personalization_service.build_personalized_prompt(
                    query=query,
                    retrieved_context=context_text,
                    user_id=user_uuid,
                    difficulty_override=difficulty_override if user_uuid else None
                )

                # Extract personalized system prompt
                personalized_system_prompt = personalization_result.get("system_prompt")

                # Generate response with personalized prompt
                response_text = await self.generation_service.generate_response(
                    query=query,
                    context_passages=context_passages,
                    conversation_history=conversation_history if conversation_history else None,
                    use_fallback_on_error=True,
                    system_prompt=personalized_system_prompt if user_uuid else None
                )
                logger.debug(f"Response generation complete ({len(response_text)} chars)")
            except Exception as gen_error:
                logger.error(f"Generation failed, using fallback: {gen_error}")
                response_text = self.generation_service.get_fallback_response("api_error")

            # Step 6: Save to database (if conversation_id provided)
            if conversation_uuid:
                conversation_service = await get_conversation_service(self.session)
                try:
                    await conversation_service.save_message(
                        conversation_uuid,
                        sender="user",
                        content=query
                    )
                    await conversation_service.save_message(
                        conversation_uuid,
                        sender="assistant",
                        content=response_text
                    )
                    await self.session.commit()
                    logger.debug("Messages saved to database")
                except Exception as e:
                    logger.error(f"Failed to save messages: {e}")
                    await self.session.rollback()
                    # Don't fail the entire request if message saving fails
                    pass

            processing_time = (time.time() - start_time) * 1000

            logger.info(
                f"Query processed in {processing_time:.0f}ms "
                f"(validation, embedding, retrieval, off-topic check, generation, storage)"
            )

            # Save audit log
            try:
                await self.save_audit_log(
                    query=query,
                    response=response_text,
                    relevance_scores=relevance_scores,
                    user_id=user_id,
                    conversation_id=final_conversation_id,
                    processing_time_ms=int(processing_time)
                )
            except Exception as audit_error:
                logger.warning(f"Failed to save audit log: {audit_error}")
                # Don't fail the request if audit logging fails

            # Log performance metrics
            structured_logger.log_performance(
                operation="process_query",
                duration_ms=processing_time,
                success=True,
                metadata={
                    "num_passages": len(context_passages),
                    "avg_relevance": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
                }
            )

            return ChatResponse(
                response=response_text,
                conversation_id=final_conversation_id,
                retrieved_passages=context_passages,
                relevance_scores=relevance_scores,
                processing_time_ms=processing_time
            )

        except TimeoutError as e:
            # Handle timeout gracefully
            logger.error(f"Request timeout: {e}")
            processing_time = (time.time() - start_time) * 1000

            structured_logger.log_error(
                error_type="timeout_error",
                message="Request processing timed out",
                details={"processing_time_ms": processing_time}
            )

            return ChatResponse(
                response="I'm temporarily unavailable. Please try again in a moment.",
                conversation_id=final_conversation_id if 'final_conversation_id' in locals() else str(uuid4()),
                retrieved_passages=[],
                relevance_scores=[],
                processing_time_ms=processing_time
            )

        except ValueError as e:
            # Handle validation errors
            logger.warning(f"Validation error: {e}")
            processing_time = (time.time() - start_time) * 1000

            structured_logger.log_error(
                error_type="validation_error",
                message=str(e),
                details={"query_length": len(query) if 'query' in locals() else 0}
            )

            return ChatResponse(
                response="I couldn't process your query. Please check your input and try again.",
                conversation_id=final_conversation_id if 'final_conversation_id' in locals() else str(uuid4()),
                retrieved_passages=[],
                relevance_scores=[],
                processing_time_ms=processing_time
            )

        except Exception as e:
            # Handle unexpected errors gracefully
            logger.error(f"Chat processing failed: {e}", exc_info=True)
            processing_time = (time.time() - start_time) * 1000

            # Log error
            structured_logger.log_error(
                error_type="query_processing_error",
                message=str(e),
                details={
                    "query_length": len(query) if 'query' in locals() else 0,
                    "conversation_id": conversation_id
                }
            )

            # Log performance (failure)
            structured_logger.log_performance(
                operation="process_query",
                duration_ms=processing_time,
                success=False
            )

            # Return graceful error response instead of raising
            return ChatResponse(
                response="An error occurred while processing your query. Please try again.",
                conversation_id=final_conversation_id if 'final_conversation_id' in locals() else str(uuid4()),
                retrieved_passages=[],
                relevance_scores=[],
                processing_time_ms=processing_time
            )

    async def save_audit_log(
        self,
        query: str,
        response: str,
        relevance_scores: list,
        user_id: Optional[str],
        conversation_id: str,
        processing_time_ms: int
    ):
        """Save query/response to audit_logs table.

        Args:
            query: User query
            response: Generated response
            relevance_scores: List of relevance scores
            user_id: Optional user UUID
            conversation_id: Conversation UUID
            processing_time_ms: Processing time in milliseconds
        """
        try:
            # Convert IDs to UUIDs
            user_uuid = UUID(user_id) if user_id else None
            conversation_uuid = UUID(conversation_id) if conversation_id else None

            audit_log = AuditLog(
                query=query,
                response=response,
                relevance_scores=relevance_scores,
                user_id=user_uuid,
                conversation_id=conversation_uuid,
                processing_time_ms=float(processing_time_ms),
                timestamp=datetime.utcnow()
            )

            self.session.add(audit_log)
            await self.session.commit()

            logger.debug(f"Audit log saved: {audit_log.log_id}")

        except Exception as e:
            logger.error(f"Failed to save audit log: {e}")
            await self.session.rollback()
            # Don't raise - audit logging should not break the main flow


async def get_chat_service(
    session: AsyncSession,
    embedding_service=None,
    retrieval_service=None,
    generation_service=None,
    security_service=None
) -> ChatService:
    """Factory for creating ChatService instances.

    Args:
        session: AsyncSession for database operations
        embedding_service: Optional EmbeddingService instance
        retrieval_service: Optional RetrievalService instance
        generation_service: Optional GenerationService instance
        security_service: Optional SecurityService instance

    Returns:
        ChatService: Initialized service instance
    """
    return ChatService(
        session,
        embedding_service=embedding_service,
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        security_service=security_service
    )
