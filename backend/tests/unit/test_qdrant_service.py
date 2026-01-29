"""Unit tests for Qdrant vector database service."""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from qdrant_client.models import Distance, VectorParams, PointStruct


@pytest.fixture
def mock_qdrant_client():
    """Fixture for mocked Qdrant client."""
    with patch("src.services.qdrant_client.QdrantClient") as mock:
        yield mock


@pytest_asyncio.fixture
async def qdrant_service(mock_qdrant_client):
    """Fixture for QdrantService with mocked client."""
    with patch.dict("os.environ", {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_API_KEY": "test_key",
        "QDRANT_COLLECTION_NAME": "test_collection"
    }):
        # Re-import to get the mocked version
        from src.services.qdrant_client import QdrantService
        service = QdrantService()
        service.client = mock_qdrant_client.return_value
        yield service


class TestQdrantServiceInit:
    """Tests for QdrantService initialization."""

    def test_init_requires_env_vars(self):
        """Test that init raises ValueError if env vars are missing."""
        from src.services.qdrant_client import QdrantService
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="QDRANT_URL and QDRANT_API_KEY"):
                QdrantService()

    def test_init_with_valid_env_vars(self):
        """Test successful initialization with environment variables."""
        from src.services.qdrant_client import QdrantService
        with patch("src.services.qdrant_client.QdrantClient") as mock_client:
            with patch.dict("os.environ", {
                "QDRANT_URL": "http://localhost:6333",
                "QDRANT_API_KEY": "test_key"
            }):
                service = QdrantService()
                assert service.collection_name == "textbook_chunks"
                assert service.vector_size == 1536
                mock_client.assert_called_once()


class TestQdrantServiceCreateCollection:
    """Tests for create_collection method."""

    @pytest.mark.asyncio
    async def test_create_collection_success(self, qdrant_service):
        """Test successful collection creation."""
        qdrant_service.client.get_collection.side_effect = Exception("Not found")
        result = await qdrant_service.create_collection()
        assert result is True
        qdrant_service.client.create_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_collection_already_exists(self, qdrant_service):
        """Test creation when collection already exists."""
        qdrant_service.client.get_collection.return_value = {"points_count": 100}
        result = await qdrant_service.create_collection()
        assert result is True
        qdrant_service.client.create_collection.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_collection_failure(self, qdrant_service):
        """Test collection creation with error."""
        qdrant_service.client.create_collection.side_effect = Exception("API Error")
        qdrant_service.client.get_collection.side_effect = Exception("Not found")
        with pytest.raises(Exception, match="API Error"):
            await qdrant_service.create_collection()


class TestQdrantServiceSearch:
    """Tests for search method."""

    @pytest.mark.asyncio
    async def test_search_success(self, qdrant_service):
        """Test successful vector search."""
        query_vector = [0.1] * 1536
        mock_results = [
            MagicMock(id=1, score=0.95, payload={"content": "test"}),
            MagicMock(id=2, score=0.87, payload={"content": "passage"})
        ]
        qdrant_service.client.search.return_value = mock_results

        results = await qdrant_service.search(query_vector, top_k=2)

        assert len(results) == 2
        assert results[0]["score"] == 0.95
        assert results[1]["score"] == 0.87
        qdrant_service.client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_invalid_vector_dimension(self, qdrant_service):
        """Test search with invalid vector dimension."""
        query_vector = [0.1] * 512  # Wrong dimension
        with pytest.raises(ValueError, match="does not match expected"):
            await qdrant_service.search(query_vector)

    @pytest.mark.asyncio
    async def test_search_with_threshold(self, qdrant_service):
        """Test search with relevance threshold."""
        query_vector = [0.1] * 1536
        mock_results = [MagicMock(id=1, score=0.95, payload={"content": "test"})]
        qdrant_service.client.search.return_value = mock_results

        results = await qdrant_service.search(
            query_vector,
            top_k=5,
            score_threshold=0.5
        )

        assert len(results) == 1
        # Verify threshold was passed
        call_args = qdrant_service.client.search.call_args
        assert call_args.kwargs["score_threshold"] == 0.5


class TestQdrantServiceUpsert:
    """Tests for upsert method."""

    @pytest.mark.asyncio
    async def test_upsert_success(self, qdrant_service):
        """Test successful upsert of points."""
        points = [
            {
                "id": "1",
                "vector": [0.1] * 1536,
                "payload": {"content": "passage1", "chapter": "1"}
            },
            {
                "id": "2",
                "vector": [0.2] * 1536,
                "payload": {"content": "passage2", "chapter": "2"}
            }
        ]

        result = await qdrant_service.upsert(points)
        assert result is True
        qdrant_service.client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_empty_list(self, qdrant_service):
        """Test upsert with empty points list."""
        result = await qdrant_service.upsert([])
        assert result is True
        qdrant_service.client.upsert.assert_not_called()

    @pytest.mark.asyncio
    async def test_upsert_missing_fields(self, qdrant_service):
        """Test upsert with missing required fields."""
        points = [
            {
                "id": "1",
                "vector": [0.1] * 1536
                # Missing payload
            }
        ]

        with pytest.raises(ValueError, match="missing required fields"):
            await qdrant_service.upsert(points)

    @pytest.mark.asyncio
    async def test_upsert_invalid_vector_dimension(self, qdrant_service):
        """Test upsert with invalid vector dimension."""
        points = [
            {
                "id": "1",
                "vector": [0.1] * 512,  # Wrong dimension
                "payload": {"content": "passage"}
            }
        ]

        with pytest.raises(ValueError, match="vector dimension"):
            await qdrant_service.upsert(points)

    @pytest.mark.asyncio
    async def test_upsert_converts_string_ids_to_int(self, qdrant_service):
        """Test that string IDs are converted to integers when possible."""
        points = [
            {
                "id": "123",
                "vector": [0.1] * 1536,
                "payload": {"content": "passage"}
            }
        ]

        result = await qdrant_service.upsert(points)
        assert result is True

        # Verify that point ID was converted to int
        call_args = qdrant_service.client.upsert.call_args
        point_structs = call_args.kwargs["points"]
        assert isinstance(point_structs[0].id, int)
        assert point_structs[0].id == 123


class TestQdrantServiceDeleteCollection:
    """Tests for delete_collection method."""

    @pytest.mark.asyncio
    async def test_delete_collection_success(self, qdrant_service):
        """Test successful collection deletion."""
        result = await qdrant_service.delete_collection()
        assert result is True
        qdrant_service.client.delete_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_collection_failure(self, qdrant_service):
        """Test collection deletion with error."""
        qdrant_service.client.delete_collection.side_effect = Exception("Not found")
        with pytest.raises(Exception, match="Not found"):
            await qdrant_service.delete_collection()


class TestQdrantServiceGetCollectionInfo:
    """Tests for get_collection_info method."""

    @pytest.mark.asyncio
    async def test_get_collection_info_success(self, qdrant_service):
        """Test successful collection info retrieval."""
        mock_collection = MagicMock(
            points_count=1000,
            vectors_count=1000,
            status="green"
        )
        qdrant_service.client.get_collection.return_value = mock_collection

        info = await qdrant_service.get_collection_info()

        assert info["points_count"] == 1000
        assert info["vectors_count"] == 1000
        assert info["status"] == "green"

    @pytest.mark.asyncio
    async def test_get_collection_info_failure(self, qdrant_service):
        """Test collection info retrieval with error."""
        qdrant_service.client.get_collection.side_effect = Exception("Connection error")
        with pytest.raises(Exception, match="Connection error"):
            await qdrant_service.get_collection_info()
