"""Unit tests for embedding service."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.embedding_service import EmbeddingService, get_embedding_service


@pytest.fixture
def mock_openai_service():
    """Create mock OpenAI service."""
    service = AsyncMock()
    service.embed_text = AsyncMock(return_value=[0.1] * 1536)
    service.embed_batch = AsyncMock(
        return_value=[[0.1] * 1536, [0.2] * 1536]
    )
    return service


@pytest.fixture
def embedding_service(mock_openai_service):
    """Create embedding service with mocked OpenAI."""
    service = EmbeddingService()
    service.openai_service = mock_openai_service
    return service


@pytest.mark.asyncio
async def test_embed_query(embedding_service, mock_openai_service):
    """Test single query embedding."""
    query = "What is ROS 2?"

    result = await embedding_service.embed_query(query)

    assert isinstance(result, list)
    assert len(result) == 1536
    mock_openai_service.embed_text.assert_called_once_with(query)


@pytest.mark.asyncio
async def test_embed_query_empty_raises_error(embedding_service, mock_openai_service):
    """Test embedding empty query raises error."""
    mock_openai_service.embed_text.side_effect = ValueError("Text cannot be empty")

    with pytest.raises(ValueError):
        await embedding_service.embed_query("")


@pytest.mark.asyncio
async def test_embed_passages(embedding_service, mock_openai_service):
    """Test batch passage embedding."""
    passages = [
        {"content": "ROS 2 is a robotics framework", "chapter": "1"},
        {"content": "Kinematics deals with motion", "chapter": "2"},
    ]

    result = await embedding_service.embed_passages(passages)

    assert len(result) == 2
    assert all("vector" in p for p in result)
    assert all("id" in p for p in result)
    assert all(len(p["vector"]) == 1536 for p in result)
    assert result[0]["content"] == passages[0]["content"]
    mock_openai_service.embed_batch.assert_called_once()


@pytest.mark.asyncio
async def test_embed_passages_empty_raises_error(embedding_service):
    """Test embedding empty passages list raises error."""
    with pytest.raises(ValueError):
        await embedding_service.embed_passages([])


@pytest.mark.asyncio
async def test_embed_passages_preserves_metadata(embedding_service):
    """Test that embedding preserves passage metadata."""
    passages = [
        {
            "content": "Test passage",
            "chapter": "Chapter 1",
            "section": "Introduction",
            "module": "Basics"
        }
    ]

    result = await embedding_service.embed_passages(passages)

    assert result[0]["chapter"] == "Chapter 1"
    assert result[0]["section"] == "Introduction"
    assert result[0]["module"] == "Basics"
    assert result[0]["content"] == "Test passage"


def test_get_embedding_service_singleton():
    """Test that embedding service returns singleton."""
    service1 = get_embedding_service()
    service2 = get_embedding_service()

    assert service1 is service2
