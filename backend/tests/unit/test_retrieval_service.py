"""Unit tests for retrieval service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.retrieval_service import RetrievalService, get_retrieval_service


@pytest.fixture
def mock_qdrant_service():
    """Create mock Qdrant service."""
    service = AsyncMock()
    service.search = AsyncMock(
        return_value=[
            {
                "id": "1",
                "score": 0.95,
                "payload": {"content": "Passage 1", "chapter": "1"}
            },
            {
                "id": "2",
                "score": 0.87,
                "payload": {"content": "Passage 2", "chapter": "2"}
            },
            {
                "id": "3",
                "score": 0.82,
                "payload": {"content": "Passage 3", "chapter": "3"}
            },
            {
                "id": "4",
                "score": 0.25,
                "payload": {"content": "Passage 4", "chapter": "4"}
            },
        ]
    )
    return service


@pytest.fixture
def retrieval_service(mock_qdrant_service):
    """Create retrieval service with mocked Qdrant."""
    service = RetrievalService(top_k=5, min_relevance=0.3)
    service.qdrant_service = mock_qdrant_service
    return service


@pytest.mark.asyncio
async def test_search(retrieval_service, mock_qdrant_service):
    """Test vector search."""
    query_vector = [0.1] * 1536

    result = await retrieval_service.search(query_vector)

    assert len(result) == 4
    assert result[0]["score"] == 0.95
    mock_qdrant_service.search.assert_called_once_with(query_vector, top_k=5)


@pytest.mark.asyncio
async def test_rank_passages(retrieval_service):
    """Test passage ranking and filtering."""
    passages = [
        {"id": "1", "score": 0.95, "payload": {"content": "Passage 1"}},
        {"id": "2", "score": 0.87, "payload": {"content": "Passage 2"}},
        {"id": "3", "score": 0.82, "payload": {"content": "Passage 3"}},
        {"id": "4", "score": 0.25, "payload": {"content": "Passage 4"}},
    ]

    result = await retrieval_service.rank_passages(passages, "test query")

    # Should filter out passage with score 0.25 (below 0.3 threshold)
    assert len(result) == 3
    # Should be sorted by score descending
    assert result[0]["score"] == 0.95
    assert result[1]["score"] == 0.87
    assert result[2]["score"] == 0.82


@pytest.mark.asyncio
async def test_retrieve_context(retrieval_service):
    """Test full retrieval pipeline."""
    query_vector = [0.1] * 1536
    query = "What is kinematics?"

    passages, scores = await retrieval_service.retrieve_context(
        query_vector, query, top_k=3
    )

    assert len(passages) == 3
    assert len(scores) == 3
    assert all(isinstance(p, str) for p in passages)
    assert all(isinstance(s, float) for s in scores)
    assert scores[0] >= scores[1] >= scores[2]
    # Scores should be in descending order
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_retrieve_context_fewer_results_than_top_k(retrieval_service):
    """Test when fewer passages exist than requested top_k."""
    # Mock search to return fewer results
    retrieval_service.qdrant_service.search = AsyncMock(
        return_value=[
            {"id": "1", "score": 0.95, "payload": {"content": "Passage 1"}},
            {"id": "2", "score": 0.87, "payload": {"content": "Passage 2"}},
        ]
    )

    query_vector = [0.1] * 1536
    passages, scores = await retrieval_service.retrieve_context(
        query_vector, "query", top_k=3
    )

    # Should return only 2 passages (all available above threshold)
    assert len(passages) == 2
    assert len(scores) == 2


@pytest.mark.asyncio
async def test_retrieve_context_filters_low_relevance(retrieval_service):
    """Test that low relevance passages are filtered."""
    # Mock search to return passages with varying relevance
    retrieval_service.qdrant_service.search = AsyncMock(
        return_value=[
            {"id": "1", "score": 0.95, "payload": {"content": "Passage 1"}},
            {"id": "2", "score": 0.2, "payload": {"content": "Passage 2"}},  # Below threshold
            {"id": "3", "score": 0.5, "payload": {"content": "Passage 3"}},
        ]
    )

    query_vector = [0.1] * 1536
    passages, scores = await retrieval_service.retrieve_context(
        query_vector, "query", top_k=3
    )

    # Should only return passages above 0.3 threshold
    assert len(passages) == 2
    assert all(score >= 0.3 for score in scores)


def test_get_retrieval_service_singleton():
    """Test that retrieval service returns singleton."""
    service1 = get_retrieval_service()
    service2 = get_retrieval_service()

    assert service1 is service2


def test_retrieval_service_config():
    """Test retrieval service initialization with custom config."""
    service = RetrievalService(top_k=10, min_relevance=0.5)

    assert service.top_k == 10
    assert service.min_relevance == 0.5
