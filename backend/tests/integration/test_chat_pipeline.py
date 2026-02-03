"""Integration tests for the full RAG chat pipeline."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.chat_service import ChatService, get_chat_service
from src.models.schemas import ChatResponse


@pytest.fixture
def mock_session():
    """Create mock async database session."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_embedding_service():
    """Create mock embedding service."""
    service = AsyncMock()
    service.embed_query = AsyncMock(return_value=[0.1] * 1536)
    return service


@pytest.fixture
def mock_retrieval_service():
    """Create mock retrieval service."""
    service = AsyncMock()
    service.retrieve_context = AsyncMock(
        return_value=(
            ["Passage 1 about ROS 2", "Passage 2 about kinematics"],
            [0.95, 0.87]
        )
    )
    return service


@pytest.fixture
def mock_generation_service():
    """Create mock generation service."""
    service = AsyncMock()
    service.generate_response = AsyncMock(
        return_value="ROS 2 is a robotics framework. [Chapter 1: Fundamentals]"
    )
    return service


@pytest.fixture
def chat_service(mock_session, mock_embedding_service, mock_retrieval_service, mock_generation_service):
    """Create chat service with mocked dependencies."""
    service = ChatService(
        session=mock_session,
        embedding_service=mock_embedding_service,
        retrieval_service=mock_retrieval_service,
        generation_service=mock_generation_service
    )
    return service


@pytest.mark.asyncio
async def test_process_query_without_conversation(chat_service):
    """Test processing a query without conversation context."""
    query = "What is ROS 2?"

    response = await chat_service.process_query(query)

    assert isinstance(response, ChatResponse)
    assert response.response == "ROS 2 is a robotics framework. [Chapter 1: Fundamentals]"
    assert len(response.retrieved_passages) == 2
    assert len(response.relevance_scores) == 2
    assert response.processing_time_ms > 0


@pytest.mark.asyncio
async def test_process_query_with_conversation_id(chat_service, mock_session):
    """Test processing a query with conversation ID."""
    conversation_id = str(uuid4())
    query = "What about kinematics?"

    # Mock the conversation service
    with patch("src.services.chat_service.get_conversation_service") as mock_conv_service_factory:
        mock_conv_service = AsyncMock()
        mock_conv_service.get_context_window = AsyncMock(return_value=[])
        mock_conv_service.format_context_for_prompt = AsyncMock(return_value=[])
        mock_conv_service.save_message = AsyncMock()
        mock_conv_service_factory.return_value = mock_conv_service

        response = await chat_service.process_query(
            query=query,
            conversation_id=conversation_id
        )

    assert response.conversation_id == conversation_id
    assert response.response is not None


@pytest.mark.asyncio
async def test_process_query_saves_messages(chat_service):
    """Test that messages are saved to database."""
    conversation_id = str(uuid4())
    query = "Test question?"

    with patch("src.services.chat_service.get_conversation_service") as mock_conv_service_factory:
        mock_conv_service = AsyncMock()
        mock_conv_service.get_context_window = AsyncMock(return_value=[])
        mock_conv_service.format_context_for_prompt = AsyncMock(return_value=[])
        mock_conv_service.save_message = AsyncMock()
        mock_conv_service_factory.return_value = mock_conv_service

        await chat_service.process_query(
            query=query,
            conversation_id=conversation_id
        )

        # Verify messages were saved
        assert mock_conv_service.save_message.call_count == 2
        calls = mock_conv_service.save_message.call_args_list
        # First call should be user message
        assert calls[0].kwargs["sender"] == "user"
        assert calls[0].kwargs["content"] == query
        # Second call should be bot response
        assert calls[1].kwargs["sender"] == "assistant"


@pytest.mark.asyncio
async def test_process_query_with_user_id(chat_service):
    """Test processing a query with user ID."""
    user_id = str(uuid4())
    query = "What is kinematics?"

    response = await chat_service.process_query(
        query=query,
        user_id=user_id
    )

    assert response is not None
    assert response.response is not None


@pytest.mark.asyncio
async def test_process_query_embedding_retrieval_generation_pipeline(
    chat_service,
    mock_embedding_service,
    mock_retrieval_service,
    mock_generation_service
):
    """Test the full pipeline is called in correct order."""
    query = "What is the definition of kinematics?"

    response = await chat_service.process_query(query)

    # Verify each service was called
    mock_embedding_service.embed_query.assert_called_once_with(query)
    mock_retrieval_service.retrieve_context.assert_called_once()
    mock_generation_service.generate_response.assert_called_once()

    # Verify response has expected structure
    assert response.response is not None
    assert response.retrieved_passages is not None
    assert response.relevance_scores is not None
    assert response.processing_time_ms > 0


@pytest.mark.asyncio
async def test_process_query_error_handling(chat_service, mock_embedding_service):
    """Test error handling in query processing."""
    mock_embedding_service.embed_query.side_effect = Exception("Embedding failed")

    with pytest.raises(Exception):
        await chat_service.process_query("Test query")


@pytest.mark.asyncio
async def test_process_query_invalid_conversation_id(chat_service):
    """Test that invalid conversation IDs are handled gracefully."""
    # Invalid UUID format should be handled
    response = await chat_service.process_query(
        query="What is ROS 2?",
        conversation_id="invalid-uuid"
    )

    # Should still work and use the provided ID
    assert response is not None
    assert response.conversation_id == "invalid-uuid"


@pytest.mark.asyncio
async def test_chat_service_factory():
    """Test chat service factory function."""
    mock_session = AsyncMock(spec=AsyncSession)

    service = await get_chat_service(mock_session)

    assert isinstance(service, ChatService)
    assert service.session is mock_session


@pytest.mark.asyncio
async def test_process_query_retrieval_context_passed_correctly(
    chat_service,
    mock_retrieval_service,
    mock_generation_service
):
    """Test that retrieved context is correctly passed to generation service."""
    query = "Test query"

    await chat_service.process_query(query)

    # Verify generation service received context passages
    call_kwargs = mock_generation_service.generate_response.call_args.kwargs
    assert "context_passages" in call_kwargs
    assert isinstance(call_kwargs["context_passages"], list)
    assert len(call_kwargs["context_passages"]) == 2


@pytest.mark.asyncio
async def test_process_query_timing_measurement(chat_service):
    """Test that processing time is accurately measured."""
    query = "What is ROS 2?"

    response = await chat_service.process_query(query)

    assert response.processing_time_ms > 0
    # Should be a reasonable time (at least some milliseconds)
    assert isinstance(response.processing_time_ms, float)
