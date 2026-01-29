"""Unit tests for OpenAI API client service."""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock


@pytest.fixture
def mock_openai_client():
    """Fixture for mocked OpenAI client."""
    with patch("src.services.openai_client.AsyncOpenAI") as mock:
        yield mock


@pytest_asyncio.fixture
async def openai_service(mock_openai_client):
    """Fixture for OpenAIService with mocked client."""
    with patch.dict("os.environ", {
        "OPENAI_API_KEY": "test_key",
        "OPENAI_MODEL": "gpt-3.5-turbo"
    }):
        from src.services.openai_client import OpenAIService
        service = OpenAIService()
        service.client = mock_openai_client.return_value
        yield service


class TestOpenAIServiceInit:
    """Tests for OpenAIService initialization."""

    def test_init_requires_api_key(self):
        """Test that init raises ValueError if API key is missing."""
        from src.services.openai_client import OpenAIService
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                OpenAIService()

    def test_init_with_valid_env_vars(self):
        """Test successful initialization with environment variables."""
        from src.services.openai_client import OpenAIService
        with patch("src.services.openai_client.AsyncOpenAI") as mock_client:
            with patch.dict("os.environ", {
                "OPENAI_API_KEY": "test_key",
                "OPENAI_MODEL": "gpt-4"
            }):
                service = OpenAIService()
                assert service.embedding_model == "text-embedding-3-small"
                assert service.chat_model == "gpt-4"
                mock_client.assert_called_once()

    def test_init_default_model(self):
        """Test default model when not specified."""
        from src.services.openai_client import OpenAIService
        with patch("src.services.openai_client.AsyncOpenAI"):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}, clear=True):
                service = OpenAIService()
                assert service.chat_model == "gpt-3.5-turbo"


class TestOpenAIServiceEmbedText:
    """Tests for embed_text method."""

    @pytest.mark.asyncio
    async def test_embed_text_success(self, openai_service):
        """Test successful text embedding."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        openai_service.client.embeddings.create = AsyncMock(return_value=mock_response)

        embedding = await openai_service.embed_text("test passage")

        assert len(embedding) == 1536
        openai_service.client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_text_empty_raises_error(self, openai_service):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await openai_service.embed_text("")

    @pytest.mark.asyncio
    async def test_embed_text_whitespace_only_raises_error(self, openai_service):
        """Test that whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await openai_service.embed_text("   ")

    @pytest.mark.asyncio
    async def test_embed_text_api_failure(self, openai_service):
        """Test embedding with API error."""
        openai_service.client.embeddings.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        with pytest.raises(Exception, match="API Error"):
            await openai_service.embed_text("test")


class TestOpenAIServiceEmbedBatch:
    """Tests for embed_batch method."""

    @pytest.mark.asyncio
    async def test_embed_batch_success(self, openai_service):
        """Test successful batch embedding."""
        texts = ["passage 1", "passage 2", "passage 3"]
        mock_embeddings = [
            MagicMock(embedding=[0.1 * i] * 1536, index=i)
            for i in range(3)
        ]
        mock_response = MagicMock()
        mock_response.data = mock_embeddings

        openai_service.client.embeddings.create = AsyncMock(return_value=mock_response)

        embeddings = await openai_service.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)
        openai_service.client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_batch_empty_list_raises_error(self, openai_service):
        """Test that empty texts list raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await openai_service.embed_batch([])

    @pytest.mark.asyncio
    async def test_embed_batch_contains_empty_text(self, openai_service):
        """Test that empty text in list raises ValueError."""
        texts = ["passage 1", "", "passage 3"]
        with pytest.raises(ValueError, match="is empty"):
            await openai_service.embed_batch(texts)

    @pytest.mark.asyncio
    async def test_embed_batch_api_failure(self, openai_service):
        """Test batch embedding with API error."""
        openai_service.client.embeddings.create = AsyncMock(
            side_effect=Exception("Rate limit")
        )
        with pytest.raises(Exception, match="Rate limit"):
            await openai_service.embed_batch(["test1", "test2"])

    @pytest.mark.asyncio
    async def test_embed_batch_maintains_order(self, openai_service):
        """Test that embeddings are returned in order of input."""
        texts = ["first", "second", "third"]
        mock_embeddings = [
            MagicMock(embedding=[float(i)] * 1536, index=i)
            for i in range(3)
        ]
        mock_response = MagicMock()
        # Shuffle to test sorting
        mock_response.data = [mock_embeddings[2], mock_embeddings[0], mock_embeddings[1]]

        openai_service.client.embeddings.create = AsyncMock(return_value=mock_response)

        embeddings = await openai_service.embed_batch(texts)

        # Should be sorted by index
        assert embeddings[0][0] == 0.0  # First
        assert embeddings[1][0] == 1.0  # Second
        assert embeddings[2][0] == 2.0  # Third


class TestOpenAIServiceGenerateResponse:
    """Tests for generate_response method."""

    @pytest.mark.asyncio
    async def test_generate_response_success(self, openai_service):
        """Test successful response generation."""
        query = "What is robotics?"
        context = ["Robotics is the study of robots..."]

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Generated answer"))]
        openai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        response = await openai_service.generate_response(query, context)

        assert response == "Generated answer"
        openai_service.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_response_empty_query_raises_error(self, openai_service):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await openai_service.generate_response("", ["context"])

    @pytest.mark.asyncio
    async def test_generate_response_with_conversation_history(self, openai_service):
        """Test response generation with conversation history."""
        query = "Follow-up question?"
        context = ["Relevant passage"]
        history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"}
        ]

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Follow-up answer"))]
        openai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        response = await openai_service.generate_response(query, context, history)

        assert response == "Follow-up answer"

        # Verify history was included in messages
        call_args = openai_service.client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert len(messages) >= 4  # system + 2 history + user

    @pytest.mark.asyncio
    async def test_generate_response_no_context(self, openai_service):
        """Test response generation with no context passages."""
        query = "What is a question?"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Answer"))]
        openai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        response = await openai_service.generate_response(query, [])

        assert response == "Answer"
        # Should still call the API
        openai_service.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_response_custom_temperature(self, openai_service):
        """Test response generation with custom temperature."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        openai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        await openai_service.generate_response(
            "query",
            ["context"],
            temperature=0.3,
            max_tokens=100
        )

        call_args = openai_service.client.chat.completions.create.call_args
        assert call_args.kwargs["temperature"] == 0.3
        assert call_args.kwargs["max_tokens"] == 100

    @pytest.mark.asyncio
    async def test_generate_response_api_failure(self, openai_service):
        """Test response generation with API error."""
        openai_service.client.chat.completions.create = AsyncMock(
            side_effect=Exception("Connection timeout")
        )
        with pytest.raises(Exception, match="Connection timeout"):
            await openai_service.generate_response("query", ["context"])


class TestOpenAIServiceGetModelInfo:
    """Tests for get_model_info method."""

    @pytest.mark.asyncio
    async def test_get_model_info(self, openai_service):
        """Test retrieving model information."""
        info = await openai_service.get_model_info()

        assert info["embedding_model"] == "text-embedding-3-small"
        assert info["chat_model"] == "gpt-3.5-turbo"
        assert info["embedding_dimension"] == 1536
