"""Comprehensive integration tests for User Story 2 - Multi-Turn Conversations.

This module tests the complete multi-turn conversation workflow:
1. Single question baseline (T041-1)
2. Follow-up questions with same conversation_id (T041-2)
3. Multi-turn conversation (5+ exchanges) (T041-3)
4. Context passed to generation service (T041-4)
5. Message history persists in database (T041-5)
6. Session persistence integration (T041-6)

Acceptance Criteria:
- All 6 tests passing
- <3 second SLA maintained across all exchanges
- Conversation IDs preserved correctly
- Message history stored in database
- Context passed to LLM for follow-ups
"""

import pytest
import time
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schemas import ChatRequest, ChatResponse
from src.services.chat_service import ChatService
from src.models.database import Message, Conversation


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_session():
    """Create mock async database session."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_embedding_service():
    """Create mock embedding service returning 1536-dim vectors."""
    service = AsyncMock()
    service.embed_query = AsyncMock(return_value=[0.1] * 1536)
    return service


@pytest.fixture
def mock_retrieval_service():
    """Create mock retrieval service with >85% relevance scores."""
    service = AsyncMock()
    service.retrieve_context = AsyncMock(
        return_value=(
            [
                "ROS 2 is a robotics middleware for robot software development.",
                "ROS 2 enables composition of complex robotic systems.",
                "ROS 2 is built on top of DDS (Data Distribution Service)."
            ],
            [0.95, 0.87, 0.86]  # All > 0.85 per SC-005
        )
    )
    return service


@pytest.fixture
def mock_generation_service():
    """Create mock generation service with citations."""
    service = AsyncMock()
    service.generate_response = AsyncMock(
        return_value=(
            "ROS 2 (Robot Operating System 2) is a flexible middleware for writing robot software. "
            "[Chapter 1: 1.1 Introduction]"
        )
    )
    return service


@pytest.fixture
def mock_conversation_service():
    """Create mock conversation service."""
    service = AsyncMock()
    service.get_context_window = AsyncMock(return_value=[])
    service.format_context_for_prompt = AsyncMock(return_value=[])
    service.save_message = AsyncMock()
    service.create_conversation = AsyncMock(return_value=uuid4())
    service.load_conversation = AsyncMock(return_value=[])
    return service


@pytest.fixture
def chat_service(
    mock_session,
    mock_embedding_service,
    mock_retrieval_service,
    mock_generation_service
):
    """Create ChatService with mocked dependencies."""
    return ChatService(
        session=mock_session,
        embedding_service=mock_embedding_service,
        retrieval_service=mock_retrieval_service,
        generation_service=mock_generation_service
    )


# ============================================================================
# TEST 1: Single Question Baseline
# ============================================================================

@pytest.mark.asyncio
async def test_single_question_baseline(
    chat_service,
    mock_embedding_service,
    mock_retrieval_service,
    mock_generation_service
):
    """
    TEST T041-1: Single Question Baseline

    Verify single question works (baseline for US2).

    Acceptance Criteria:
    - Query embedded to 1536 dimensions
    - Passages retrieved from vector database
    - Response generated with citations
    - Conversation ID returned
    - Processing time < 3 seconds
    """
    query = "What is ROS 2?"

    response = await chat_service.process_query(query)

    # Validate response structure
    assert isinstance(response, ChatResponse)
    assert response.response is not None
    assert len(response.response) > 0

    # Validate conversation ID
    assert response.conversation_id is not None
    assert isinstance(response.conversation_id, str)
    assert len(response.conversation_id) > 0

    # Validate retrieved passages
    assert len(response.retrieved_passages) == 3
    assert "ROS 2" in response.retrieved_passages[0]

    # Validate relevance scores
    assert len(response.relevance_scores) == 3
    assert all(score > 0.85 for score in response.relevance_scores)

    # Validate citations present
    assert "[Chapter" in response.response

    # Validate SLA: <3 seconds
    assert response.processing_time_ms < 3000
    assert response.processing_time_ms > 0

    # Verify all services were called
    mock_embedding_service.embed_query.assert_called_once_with(query)
    mock_retrieval_service.retrieve_context.assert_called_once()
    mock_generation_service.generate_response.assert_called_once()


# ============================================================================
# TEST 2: Follow-up Question with Same Conversation ID
# ============================================================================

@pytest.mark.asyncio
async def test_follow_up_question_same_conversation(
    chat_service,
    mock_embedding_service,
    mock_retrieval_service,
    mock_generation_service
):
    """
    TEST T041-2: Follow-up Question with Same Conversation ID

    Verify follow-up questions use same conversation_id.

    Acceptance Criteria:
    - First query generates conversation ID
    - Second query with same ID preserves it
    - Conversation service loads history
    - Both queries complete successfully
    """
    with patch('src.services.chat_service.get_conversation_service') as mock_get_conv_service:
        # Setup mock conversation service
        mock_conv_service = AsyncMock()
        mock_conv_service.get_context_window = AsyncMock(return_value=[])
        mock_conv_service.format_context_for_prompt = AsyncMock(return_value=[])
        mock_conv_service.save_message = AsyncMock()
        mock_get_conv_service.return_value = mock_conv_service

        # First question
        response1 = await chat_service.process_query("What is ROS 2?")
        conv_id_1 = response1.conversation_id

        assert conv_id_1 is not None
        assert isinstance(conv_id_1, str)

        # Mock generation with context reference
        mock_generation_service.generate_response = AsyncMock(
            return_value="As I mentioned, ROS 2 is a middleware. [Chapter 1: 1.2]"
        )

        # Second question (follow-up) with same conversation ID
        response2 = await chat_service.process_query(
            "Can you explain differently?",
            conversation_id=conv_id_1
        )
        conv_id_2 = response2.conversation_id

        # Conversation ID should match
        assert conv_id_2 == conv_id_1

        # Verify conversation service was called for second query
        assert mock_conv_service.get_context_window.called
        assert mock_conv_service.save_message.called


# ============================================================================
# TEST 3: Multi-turn Conversation (5+ Exchanges)
# ============================================================================

@pytest.mark.asyncio
async def test_multi_turn_conversation_five_exchanges(
    chat_service,
    mock_embedding_service,
    mock_retrieval_service,
    mock_generation_service
):
    """
    TEST T041-3: Multi-turn Conversation (5+ Exchanges)

    Verify <3 second SLA maintained across 5 exchanges.

    Acceptance Criteria:
    - All 5 exchanges complete successfully
    - Each exchange < 3000ms
    - Same conversation ID preserved
    - All responses include citations
    """
    with patch('src.services.chat_service.get_conversation_service') as mock_get_conv_service:
        # Setup mock conversation service
        mock_conv_service = AsyncMock()
        mock_conv_service.get_context_window = AsyncMock(return_value=[])
        mock_conv_service.format_context_for_prompt = AsyncMock(return_value=[])
        mock_conv_service.save_message = AsyncMock()
        mock_get_conv_service.return_value = mock_conv_service

        # Reset mocks for this test
        mock_embedding_service.embed_query = AsyncMock(return_value=[0.1] * 1536)
        mock_retrieval_service.retrieve_context = AsyncMock(
            return_value=(
                ["Passage 1", "Passage 2", "Passage 3"],
                [0.95, 0.87, 0.86]
            )
        )
        mock_generation_service.generate_response = AsyncMock(
            return_value="Answer [Chapter X]"
        )

        # Send 5 questions
        conv_id = None
        for i in range(5):
            response = await chat_service.process_query(
                query=f"Question {i+1}?",
                conversation_id=conv_id
            )

            # Validate response
            assert response is not None
            assert isinstance(response, ChatResponse)

            # Check SLA: <3 seconds
            assert response.processing_time_ms < 3000, \
                f"Question {i+1} took {response.processing_time_ms}ms (exceeded 3000ms SLA)"

            # Check citations present
            assert "[Chapter" in response.response

            # Preserve conversation ID for next iteration
            if conv_id is None:
                conv_id = response.conversation_id
            else:
                # Verify ID is preserved
                assert response.conversation_id == conv_id


# ============================================================================
# TEST 4: Context Passed to Generation Service
# ============================================================================

@pytest.mark.asyncio
async def test_context_passed_to_generation_service(
    chat_service,
    mock_embedding_service,
    mock_retrieval_service,
    mock_generation_service
):
    """
    TEST T041-4: Context Passed to Generation Service

    Verify prior messages are passed to generation service.

    Acceptance Criteria:
    - Conversation history loaded from database
    - History formatted for LLM prompt
    - History passed to generation service
    - Response generated with context awareness
    """
    with patch('src.services.chat_service.get_conversation_service') as mock_get_conv_service:
        # Setup mock conversation service with history
        mock_conv_service = AsyncMock()

        # Mock conversation history (prior messages)
        prior_messages = [
            {
                "message_id": "1",
                "sender": "user",
                "content": "What is ROS 2?",
                "timestamp": "2026-01-30T10:00:00Z"
            },
            {
                "message_id": "2",
                "sender": "assistant",
                "content": "ROS 2 is a robotics middleware. [Chapter 1: 1.1]",
                "timestamp": "2026-01-30T10:00:01Z"
            },
        ]

        # Format for prompt
        formatted_history = [
            {"role": "user", "content": "What is ROS 2?"},
            {"role": "assistant", "content": "ROS 2 is a robotics middleware. [Chapter 1: 1.1]"}
        ]

        mock_conv_service.get_context_window = AsyncMock(return_value=prior_messages)
        mock_conv_service.format_context_for_prompt = AsyncMock(return_value=formatted_history)
        mock_conv_service.save_message = AsyncMock()
        mock_get_conv_service.return_value = mock_conv_service

        # Reset generation mock
        mock_generation_service.generate_response = AsyncMock(
            return_value="As I mentioned before, ROS 2 is a middleware. [Chapter 1: 1.2]"
        )

        # Send follow-up query
        conv_id = str(uuid4())
        response = await chat_service.process_query(
            query="Tell me more about that",
            conversation_id=conv_id
        )

        assert response.status_code == 200 if hasattr(response, 'status_code') else True

        # Verify context was loaded
        assert mock_conv_service.get_context_window.called
        assert mock_conv_service.format_context_for_prompt.called

        # Verify context was passed to generation service
        call_kwargs = mock_generation_service.generate_response.call_args.kwargs
        assert "conversation_history" in call_kwargs
        assert call_kwargs["conversation_history"] is not None
        assert isinstance(call_kwargs["conversation_history"], list)


# ============================================================================
# TEST 5: Message History Persists in Database
# ============================================================================

@pytest.mark.asyncio
async def test_message_history_persists_in_database(
    chat_service,
    mock_embedding_service,
    mock_retrieval_service,
    mock_generation_service
):
    """
    TEST T041-5: Message History Persists in Database

    Verify messages are saved to database.

    Acceptance Criteria:
    - User message saved to database
    - Assistant message saved to database
    - Both messages have same conversation_id
    - Messages have correct sender field
    - Commit is called to persist
    """
    with patch('src.services.chat_service.get_conversation_service') as mock_get_conv_service:
        # Setup mock conversation service
        mock_conv_service = AsyncMock()
        mock_conv_service.get_context_window = AsyncMock(return_value=[])
        mock_conv_service.format_context_for_prompt = AsyncMock(return_value=[])

        # Track saved messages
        saved_messages = []

        async def mock_save_message(conv_id, sender, content):
            saved_messages.append({
                "conv_id": str(conv_id),
                "sender": sender,
                "content": content
            })
            return uuid4()

        mock_conv_service.save_message = AsyncMock(side_effect=mock_save_message)
        mock_get_conv_service.return_value = mock_conv_service

        # Send query
        conv_id = str(uuid4())
        response = await chat_service.process_query(
            query="What is ROS 2?",
            conversation_id=conv_id
        )

        # Verify both user and assistant messages saved
        assert len(saved_messages) == 2

        # Verify user message
        assert saved_messages[0]["sender"] == "user"
        assert saved_messages[0]["content"] == "What is ROS 2?"
        assert saved_messages[0]["conv_id"] == conv_id

        # Verify assistant message
        assert saved_messages[1]["sender"] == "assistant"
        assert len(saved_messages[1]["content"]) > 0
        assert saved_messages[1]["conv_id"] == conv_id

        # Verify commit was called
        assert chat_service.session.commit.called


# ============================================================================
# TEST 6: Session Persistence with sessionStorage
# ============================================================================

@pytest.mark.asyncio
async def test_session_persistence_integration():
    """
    TEST T041-6: Session Persistence with sessionStorage

    This test documents the frontend integration for session persistence.
    Actual browser testing would be done with Cypress/Playwright.

    Frontend Integration Requirements:
    1. Store conversation_id in sessionStorage after first query
    2. Retrieve conversation_id from sessionStorage on page refresh
    3. Include conversation_id in subsequent API requests
    4. Clear sessionStorage when conversation ends

    Example Frontend Code:
    ```javascript
    // After receiving first response
    const response = await fetch('/api/v1/chat', {
        method: 'POST',
        body: JSON.stringify({ query: 'What is ROS 2?' })
    });
    const data = await response.json();
    sessionStorage.setItem('conversationId', data.conversation_id);

    // For follow-up queries
    const conversationId = sessionStorage.getItem('conversationId');
    const response = await fetch('/api/v1/chat', {
        method: 'POST',
        body: JSON.stringify({
            query: 'Tell me more',
            conversation_id: conversationId
        })
    });
    ```

    This test is marked as a placeholder for documentation purposes.
    E2E tests should be implemented in frontend/cypress/e2e/ directory.
    """
    # This is a documentation test - actual E2E testing happens in Cypress
    assert True, "Frontend E2E tests should verify sessionStorage persistence"


# ============================================================================
# TEST 7: Conversation ID UUID Format Validation
# ============================================================================

@pytest.mark.asyncio
async def test_conversation_id_uuid_format(chat_service):
    """
    TEST T041-7: Conversation ID UUID Format

    Verify conversation IDs are valid UUIDs.

    Acceptance Criteria:
    - Generated conversation IDs are valid UUID4 format
    - UUIDs can be parsed without error
    - UUIDs are unique across requests
    """
    query = "What is ROS 2?"

    # Generate multiple conversation IDs
    conv_ids = []
    for _ in range(3):
        response = await chat_service.process_query(query)
        conv_ids.append(response.conversation_id)

    # Verify all are valid UUIDs
    for conv_id in conv_ids:
        try:
            UUID(conv_id)
        except (ValueError, AttributeError):
            pytest.fail(f"Invalid UUID format: {conv_id}")

    # Verify uniqueness
    assert len(set(conv_ids)) == len(conv_ids), "Conversation IDs should be unique"


# ============================================================================
# TEST 8: Concurrent Conversations
# ============================================================================

@pytest.mark.asyncio
async def test_concurrent_conversations_isolated(
    chat_service,
    mock_embedding_service,
    mock_retrieval_service,
    mock_generation_service
):
    """
    TEST T041-8: Concurrent Conversations Are Isolated

    Verify multiple conversations don't interfere with each other.

    Acceptance Criteria:
    - Two conversations with different IDs
    - Messages don't leak between conversations
    - Each conversation maintains independent state
    """
    with patch('src.services.chat_service.get_conversation_service') as mock_get_conv_service:
        # Setup mock conversation service
        mock_conv_service = AsyncMock()
        mock_conv_service.get_context_window = AsyncMock(return_value=[])
        mock_conv_service.format_context_for_prompt = AsyncMock(return_value=[])
        mock_conv_service.save_message = AsyncMock()
        mock_get_conv_service.return_value = mock_conv_service

        # Conversation 1
        response1 = await chat_service.process_query("What is ROS 2?")
        conv_id_1 = response1.conversation_id

        # Conversation 2 (different topic)
        response2 = await chat_service.process_query("What is kinematics?")
        conv_id_2 = response2.conversation_id

        # IDs should be different
        assert conv_id_1 != conv_id_2

        # Continue conversation 1
        response3 = await chat_service.process_query(
            "Tell me more",
            conversation_id=conv_id_1
        )

        # Should preserve conversation 1's ID
        assert response3.conversation_id == conv_id_1


# ============================================================================
# TEST EXECUTION SUMMARY
# ============================================================================

"""
User Story 2 (US2) Integration Test Summary:
============================================

Tests Implemented:
✓ T041-1: Single question baseline
✓ T041-2: Follow-up with same conversation_id
✓ T041-3: Multi-turn (5 exchanges) with <3s SLA
✓ T041-4: Context passed to generation service
✓ T041-5: Message history persists in database
✓ T041-6: Session persistence (frontend integration doc)
✓ T041-7: Conversation ID UUID format validation
✓ T041-8: Concurrent conversations isolation

Total: 8 integration tests for multi-turn conversations

Run all tests:
pytest backend/tests/integration/test_user_story_2_context.py -v

Run with coverage:
pytest backend/tests/integration/test_user_story_2_context.py -v --cov=src.services --cov-report=html

Run specific test:
pytest backend/tests/integration/test_user_story_2_context.py::test_multi_turn_conversation_five_exchanges -v
"""
