"""Unit tests for conversation management service."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.conversation_service import ConversationService, get_conversation_service
from src.models.database import Conversation, Message


@pytest.fixture
def mock_session():
    """Fixture for mocked AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest_asyncio.fixture
async def conversation_service(mock_session):
    """Fixture for ConversationService with mocked session."""
    return ConversationService(mock_session)


class TestConversationServiceCreateConversation:
    """Tests for create_conversation method."""

    @pytest.mark.asyncio
    async def test_create_conversation_success(self, conversation_service, mock_session):
        """Test successful conversation creation."""
        test_id = uuid4()

        # Create a side effect for refresh that sets the ID
        async def refresh_side_effect(obj):
            obj.conversation_id = test_id

        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(side_effect=refresh_side_effect)
        mock_session.add = MagicMock()

        conversation_service.session = mock_session

        conv_id = await conversation_service.create_conversation()

        assert conv_id == test_id
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_conversation_with_user_id(self, conversation_service, mock_session):
        """Test conversation creation with user ID."""
        user_id = uuid4()
        test_id = uuid4()

        # Create a side effect for refresh that sets the ID
        async def refresh_side_effect(obj):
            obj.conversation_id = test_id

        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(side_effect=refresh_side_effect)
        mock_session.add = MagicMock()

        conversation_service.session = mock_session

        conv_id = await conversation_service.create_conversation(user_id)

        assert conv_id == test_id
        # Verify add was called with a Conversation object
        call_args = mock_session.add.call_args
        conversation_obj = call_args[0][0]
        assert conversation_obj.user_id == user_id


class TestConversationServiceSaveMessage:
    """Tests for save_message method."""

    @pytest.mark.asyncio
    async def test_save_message_success(self, conversation_service, mock_session):
        """Test successful message saving."""
        conversation_id = uuid4()
        test_id = uuid4()

        # Create a side effect for refresh that sets the ID
        async def refresh_side_effect(obj):
            obj.message_id = test_id

        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(side_effect=refresh_side_effect)
        mock_session.add = MagicMock()
        conversation_service.session = mock_session

        msg_id = await conversation_service.save_message(
            conversation_id,
            "user",
            "Test question"
        )

        assert msg_id == test_id
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_message_invalid_sender(self, conversation_service):
        """Test that invalid sender raises ValueError."""
        with pytest.raises(ValueError, match="must be 'user' or 'assistant'"):
            await conversation_service.save_message(
                uuid4(),
                "invalid",
                "content"
            )

    @pytest.mark.asyncio
    async def test_save_message_empty_content(self, conversation_service):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await conversation_service.save_message(
                uuid4(),
                "user",
                ""
            )

    @pytest.mark.asyncio
    async def test_save_message_whitespace_only(self, conversation_service):
        """Test that whitespace-only content raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await conversation_service.save_message(
                uuid4(),
                "user",
                "   "
            )

    @pytest.mark.asyncio
    async def test_save_message_assistant(self, conversation_service, mock_session):
        """Test saving assistant message."""
        conversation_id = uuid4()
        test_id = uuid4()

        # Create a side effect for refresh that sets the ID
        async def refresh_side_effect(obj):
            obj.message_id = test_id

        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(side_effect=refresh_side_effect)
        mock_session.add = MagicMock()
        conversation_service.session = mock_session

        msg_id = await conversation_service.save_message(
            conversation_id,
            "assistant",
            "Generated response"
        )

        assert msg_id == test_id
        call_args = mock_session.add.call_args
        msg_obj = call_args[0][0]
        assert msg_obj.sender == "assistant"


class TestConversationServiceLoadConversation:
    """Tests for load_conversation method."""

    @pytest.mark.asyncio
    async def test_load_conversation_success(self, conversation_service, mock_session):
        """Test successful conversation loading."""
        conversation_id = uuid4()

        # Create mock messages
        mock_msg1 = MagicMock(spec=Message)
        mock_msg1.message_id = uuid4()
        mock_msg1.sender = "user"
        mock_msg1.content = "First question"
        mock_msg1.timestamp = datetime.utcnow()

        mock_msg2 = MagicMock(spec=Message)
        mock_msg2.message_id = uuid4()
        mock_msg2.sender = "assistant"
        mock_msg2.content = "First answer"
        mock_msg2.timestamp = datetime.utcnow()

        # Mock execute to return messages
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_msg2, mock_msg1]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        conversation_service.session = mock_session

        messages = await conversation_service.load_conversation(conversation_id)

        assert len(messages) == 2
        assert messages[0]["sender"] == "user"
        assert messages[1]["sender"] == "assistant"

    @pytest.mark.asyncio
    async def test_load_conversation_empty(self, conversation_service, mock_session):
        """Test loading empty conversation."""
        conversation_id = uuid4()

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        conversation_service.session = mock_session

        messages = await conversation_service.load_conversation(conversation_id)

        assert messages == []


class TestConversationServiceFormatContextForPrompt:
    """Tests for format_context_for_prompt method."""

    @pytest.mark.asyncio
    async def test_format_context_success(self, conversation_service):
        """Test successful message formatting."""
        messages = [
            {"message_id": "1", "sender": "user", "content": "Question?", "timestamp": None},
            {"message_id": "2", "sender": "assistant", "content": "Answer.", "timestamp": None}
        ]

        formatted = await conversation_service.format_context_for_prompt(messages)

        assert len(formatted) == 2
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "assistant"
        assert formatted[0]["content"] == "Question?"
        assert formatted[1]["content"] == "Answer."

    @pytest.mark.asyncio
    async def test_format_context_empty(self, conversation_service):
        """Test formatting empty message list."""
        formatted = await conversation_service.format_context_for_prompt([])
        assert formatted == []


class TestConversationServiceGetContextWindow:
    """Tests for get_context_window method."""

    @pytest.mark.asyncio
    async def test_get_context_window_success(self, conversation_service, mock_session):
        """Test successful context window retrieval."""
        conversation_id = uuid4()

        # Create mock messages (5 messages, ~100 chars each = ~25 tokens)
        mock_messages = []
        for i in range(5):
            mock_msg = MagicMock(spec=Message)
            mock_msg.message_id = uuid4()
            mock_msg.sender = "user" if i % 2 == 0 else "assistant"
            mock_msg.content = "x" * 100
            mock_msg.timestamp = datetime.utcnow()
            mock_messages.append({
                "message_id": str(mock_msg.message_id),
                "sender": mock_msg.sender,
                "content": mock_msg.content,
                "timestamp": mock_msg.timestamp
            })

        # Mock load_conversation
        with patch.object(conversation_service, "load_conversation", new_callable=AsyncMock) as mock_load:
            mock_load.return_value = mock_messages

            context = await conversation_service.get_context_window(
                conversation_id,
                max_tokens=2000
            )

            assert len(context) == 5
            assert context[0]["sender"] in ["user", "assistant"]

    @pytest.mark.asyncio
    async def test_get_context_window_respects_token_limit(self, conversation_service):
        """Test that context window respects token limit."""
        conversation_id = uuid4()

        # Create messages that exceed token limit
        messages = [
            {
                "message_id": str(uuid4()),
                "sender": "user",
                "content": "x" * 5000,  # ~1250 tokens
                "timestamp": datetime.utcnow()
            },
            {
                "message_id": str(uuid4()),
                "sender": "assistant",
                "content": "y" * 5000,  # ~1250 tokens
                "timestamp": datetime.utcnow()
            }
        ]

        with patch.object(conversation_service, "load_conversation", new_callable=AsyncMock) as mock_load:
            mock_load.return_value = messages

            context = await conversation_service.get_context_window(
                conversation_id,
                max_tokens=500  # Low limit
            )

            # Should return fewer messages due to token limit
            total_tokens = sum(int(len(m["content"]) * 0.25) for m in context)
            assert total_tokens <= 500

    @pytest.mark.asyncio
    async def test_get_context_window_empty(self, conversation_service):
        """Test context window with empty conversation."""
        with patch.object(conversation_service, "load_conversation", new_callable=AsyncMock) as mock_load:
            mock_load.return_value = []

            context = await conversation_service.get_context_window(uuid4())

            assert context == []


class TestConversationServiceGetConversationSummary:
    """Tests for get_conversation_summary method."""

    @pytest.mark.asyncio
    async def test_get_conversation_summary_success(self, conversation_service, mock_session):
        """Test successful conversation summary retrieval."""
        conversation_id = uuid4()
        user_id = uuid4()

        mock_conv = MagicMock(spec=Conversation)
        mock_conv.conversation_id = conversation_id
        mock_conv.user_id = user_id
        mock_conv.created_at = datetime.utcnow()
        mock_conv.updated_at = datetime.utcnow()
        mock_conv.messages = [MagicMock(), MagicMock()]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_conv
        mock_session.execute = AsyncMock(return_value=mock_result)

        conversation_service.session = mock_session

        summary = await conversation_service.get_conversation_summary(conversation_id)

        assert summary["conversation_id"] == conversation_id
        assert summary["user_id"] == user_id
        assert summary["message_count"] == 2

    @pytest.mark.asyncio
    async def test_get_conversation_summary_not_found(self, conversation_service, mock_session):
        """Test summary retrieval for non-existent conversation."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        conversation_service.session = mock_session

        with pytest.raises(ValueError, match="not found"):
            await conversation_service.get_conversation_summary(uuid4())


class TestConversationServiceDeleteConversation:
    """Tests for delete_conversation method."""

    @pytest.mark.asyncio
    async def test_delete_conversation_success(self, conversation_service, mock_session):
        """Test successful conversation deletion."""
        conversation_id = uuid4()

        mock_conv = MagicMock(spec=Conversation)
        mock_conv.conversation_id = conversation_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_conv
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = MagicMock()
        mock_session.flush = AsyncMock()

        conversation_service.session = mock_session

        result = await conversation_service.delete_conversation(conversation_id)

        assert result is True
        # Verify delete was called (with any argument, as it's the conversation object)
        assert mock_session.delete.called

    @pytest.mark.asyncio
    async def test_delete_conversation_not_found(self, conversation_service, mock_session):
        """Test deletion of non-existent conversation."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        conversation_service.session = mock_session

        with pytest.raises(ValueError, match="not found"):
            await conversation_service.delete_conversation(uuid4())


class TestConversationServiceCleanupExpired:
    """Tests for cleanup_expired_conversations method."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_conversations(self, conversation_service, mock_session):
        """Test cleanup of expired conversations."""
        mock_conv1 = MagicMock(spec=Conversation)
        mock_conv1.conversation_id = uuid4()
        mock_conv2 = MagicMock(spec=Conversation)
        mock_conv2.conversation_id = uuid4()

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_conv1, mock_conv2]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = MagicMock()
        mock_session.flush = AsyncMock()

        conversation_service.session = mock_session

        count = await conversation_service.cleanup_expired_conversations(hours=24)

        assert count == 2
        assert mock_session.delete.call_count == 2


class TestGetConversationServiceFactory:
    """Tests for get_conversation_service factory function."""

    @pytest.mark.asyncio
    async def test_get_conversation_service_factory(self):
        """Test factory function returns ConversationService."""
        mock_session = AsyncMock(spec=AsyncSession)

        service = await get_conversation_service(mock_session)

        assert isinstance(service, ConversationService)
        assert service.session == mock_session
