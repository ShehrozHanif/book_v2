"""Unit tests for generation service."""

import pytest
from unittest.mock import AsyncMock
from src.services.generation_service import GenerationService, get_generation_service


@pytest.fixture
def mock_openai_service():
    """Create mock OpenAI service."""
    service = AsyncMock()
    service.generate_response = AsyncMock(
        return_value="ROS 2 is a middleware framework for robotics. [Chapter 1: Fundamentals]"
    )
    return service


@pytest.fixture
def generation_service(mock_openai_service):
    """Create generation service with mocked OpenAI."""
    service = GenerationService(max_tokens=500)
    service.openai_service = mock_openai_service
    return service


@pytest.mark.asyncio
async def test_generate_response(generation_service, mock_openai_service):
    """Test response generation."""
    query = "What is ROS 2?"
    context = ["ROS 2 is a robotics framework"]

    response = await generation_service.generate_response(
        query=query,
        context_passages=context
    )

    assert isinstance(response, str)
    assert len(response) > 0
    mock_openai_service.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_generate_response_with_conversation_history(generation_service, mock_openai_service):
    """Test response generation with conversation history."""
    query = "What about its architecture?"
    context = ["ROS 2 uses client-server architecture"]
    history = [
        {"role": "user", "content": "What is ROS 2?"},
        {"role": "assistant", "content": "ROS 2 is a robotics framework"}
    ]

    response = await generation_service.generate_response(
        query=query,
        context_passages=context,
        conversation_history=history
    )

    assert isinstance(response, str)
    # Verify history was passed to OpenAI service
    call_args = mock_openai_service.generate_response.call_args
    assert call_args.kwargs["conversation_history"] == history


def test_extract_citations():
    """Test citation extraction from response."""
    generation_service = GenerationService()

    response = """
    ROS 2 is a middleware framework. [Chapter 1: Fundamentals]
    It supports various communication patterns. [Chapter 2: Architecture]
    """

    citations = generation_service.extract_citations(response)

    assert len(citations) == 2
    assert "[Chapter 1: Fundamentals]" in citations
    assert "[Chapter 2: Architecture]" in citations


def test_extract_citations_various_formats():
    """Test citation extraction with different formats."""
    generation_service = GenerationService()

    response = """
    [Chapter 1]
    [Chapter 2: Introduction]
    [Module 1: Chapter 3: Advanced Topics]
    """

    citations = generation_service.extract_citations(response)

    assert len(citations) == 3


def test_extract_citations_no_citations():
    """Test extraction when no citations present."""
    generation_service = GenerationService()

    response = "This is a response without any citations."

    citations = generation_service.extract_citations(response)

    assert len(citations) == 0


def test_validate_response_with_citations():
    """Test validation of response with citations."""
    generation_service = GenerationService()

    response = "ROS 2 is a framework. [Chapter 1: Fundamentals]"
    context = ["ROS 2 is a robotics framework"]

    is_valid = generation_service.validate_response(response, context)

    assert is_valid is True


def test_validate_response_short_response():
    """Test validation of short response (edge case)."""
    generation_service = GenerationService()

    response = "I don't know."
    context = ["ROS 2 is a robotics framework"]

    is_valid = generation_service.validate_response(response, context)

    assert is_valid is True


def test_validate_response_no_citations_logs_warning():
    """Test that ungrounded response is logged."""
    generation_service = GenerationService()

    response = "This is a long response without citations. " * 10
    context = ["Some context"]

    is_valid = generation_service.validate_response(response, context)

    # Should still be valid but logs warning
    assert is_valid is True


@pytest.mark.asyncio
async def test_generate_response_error_handling(generation_service, mock_openai_service):
    """Test error handling in response generation."""
    mock_openai_service.generate_response.side_effect = Exception("API error")

    with pytest.raises(Exception):
        await generation_service.generate_response(
            query="Test",
            context_passages=["Test passage"]
        )


def test_get_generation_service_singleton():
    """Test that generation service returns singleton."""
    service1 = get_generation_service()
    service2 = get_generation_service()

    assert service1 is service2


def test_generation_service_config():
    """Test generation service initialization with custom config."""
    service = GenerationService(max_tokens=1000)

    assert service.max_tokens == 1000
