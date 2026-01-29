"""Conversation management service for handling chat history and context."""

import logging
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.models.database import Conversation, Message, User

logger = logging.getLogger(__name__)

# Approximate tokens per character for token limit estimation
TOKENS_PER_CHAR = 0.25


class ConversationService:
    """Service for managing conversations and message history."""

    def __init__(self, session: AsyncSession):
        """Initialize conversation service with database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create_conversation(self, user_id: Optional[UUID] = None) -> UUID:
        """Create a new conversation.

        Args:
            user_id: Optional UUID of the user creating the conversation

        Returns:
            UUID: ID of the newly created conversation

        Raises:
            Exception: If database operation fails
        """
        try:
            conversation = Conversation(
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            self.session.add(conversation)
            await self.session.flush()
            await self.session.refresh(conversation)

            logger.info(
                f"Created conversation {conversation.conversation_id} "
                f"for user {user_id}"
            )
            return conversation.conversation_id

        except Exception as e:
            logger.error(f"Failed to create conversation: {str(e)}")
            raise

    async def save_message(
        self,
        conversation_id: UUID,
        sender: str,
        content: str
    ) -> UUID:
        """Save a message to the conversation.

        Args:
            conversation_id: UUID of the conversation
            sender: 'user' or 'assistant'
            content: Message text content

        Returns:
            UUID: ID of the saved message

        Raises:
            ValueError: If sender is invalid or content is empty
            Exception: If database operation fails
        """
        if sender not in ["user", "assistant"]:
            raise ValueError("Sender must be 'user' or 'assistant'")

        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        try:
            message = Message(
                conversation_id=conversation_id,
                sender=sender,
                content=content,
                timestamp=datetime.utcnow()
            )
            self.session.add(message)
            await self.session.flush()
            await self.session.refresh(message)

            logger.debug(
                f"Saved {sender} message {message.message_id} "
                f"to conversation {conversation_id}"
            )
            return message.message_id

        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}")
            raise

    async def load_conversation(
        self,
        conversation_id: UUID,
        limit: int = 20
    ) -> List[Dict]:
        """Load recent messages from a conversation.

        Args:
            conversation_id: UUID of the conversation
            limit: Maximum number of messages to retrieve (default: 20)

        Returns:
            List of dicts with message data:
            [
                {
                    "message_id": UUID,
                    "sender": "user" or "assistant",
                    "content": "message text",
                    "timestamp": datetime
                },
                ...
            ]

        Raises:
            Exception: If database operation fails
        """
        try:
            # Query messages, ordered by timestamp descending (newest first)
            stmt = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.timestamp.desc())
                .limit(limit)
            )

            result = await self.session.execute(stmt)
            messages = result.scalars().all()

            # Reverse to get chronological order (oldest first)
            messages = list(reversed(messages))

            formatted_messages = [
                {
                    "message_id": str(msg.message_id),
                    "sender": msg.sender,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in messages
            ]

            logger.debug(
                f"Loaded {len(formatted_messages)} messages "
                f"from conversation {conversation_id}"
            )
            return formatted_messages

        except Exception as e:
            logger.error(f"Failed to load conversation: {str(e)}")
            raise

    async def format_context_for_prompt(
        self,
        messages: List[Dict]
    ) -> List[Dict]:
        """Format messages for LLM chat completions API.

        Converts internal message format to OpenAI chat completions format.

        Args:
            messages: List of message dicts with sender and content

        Returns:
            List of dicts in OpenAI format:
            [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."},
                ...
            ]
        """
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg["sender"],
                "content": msg["content"]
            })
        return formatted

    async def get_context_window(
        self,
        conversation_id: UUID,
        max_tokens: int = 2000,
        max_messages: int = 20
    ) -> List[Dict]:
        """Get recent messages within token and message limits.

        This method loads messages and applies token-based context windowing
        to respect LLM token limits while preserving recent conversation history.

        Args:
            conversation_id: UUID of the conversation
            max_tokens: Maximum tokens allowed in context (default: 2000)
            max_messages: Maximum messages to include (default: 20)

        Returns:
            List of message dicts ordered chronologically (oldest first)

        Raises:
            Exception: If database operation fails
        """
        try:
            # Load messages (latest first, limited by max_messages)
            messages = await self.load_conversation(
                conversation_id,
                limit=max_messages
            )

            if not messages:
                return []

            # Calculate tokens for each message and apply limit
            context_messages = []
            total_tokens = 0

            # Iterate from newest to oldest to build context
            for msg in reversed(messages):
                msg_tokens = int(len(msg["content"]) * TOKENS_PER_CHAR)
                total_tokens += msg_tokens

                if total_tokens > max_tokens:
                    logger.debug(
                        f"Token limit reached ({total_tokens}>{max_tokens}) "
                        f"for conversation {conversation_id}"
                    )
                    break

                context_messages.insert(0, msg)  # Insert at beginning for chronological order

            logger.debug(
                f"Built context window with {len(context_messages)} messages "
                f"({total_tokens} tokens) for conversation {conversation_id}"
            )
            return context_messages

        except Exception as e:
            logger.error(f"Failed to get context window: {str(e)}")
            raise

    async def get_conversation_summary(
        self,
        conversation_id: UUID
    ) -> Dict:
        """Get metadata about a conversation.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Dict with conversation metadata:
            {
                "conversation_id": UUID,
                "user_id": Optional[UUID],
                "created_at": datetime,
                "updated_at": datetime,
                "message_count": int
            }

        Raises:
            Exception: If database operation fails
        """
        try:
            stmt = (
                select(Conversation)
                .where(Conversation.conversation_id == conversation_id)
                .options(selectinload(Conversation.messages))
            )

            result = await self.session.execute(stmt)
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            return {
                "conversation_id": conversation.conversation_id,
                "user_id": conversation.user_id,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "message_count": len(conversation.messages) if conversation.messages else 0
            }

        except Exception as e:
            logger.error(f"Failed to get conversation summary: {str(e)}")
            raise

    async def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete a conversation and all associated messages.

        Args:
            conversation_id: UUID of the conversation to delete

        Returns:
            bool: True if deletion successful

        Raises:
            Exception: If database operation fails
        """
        try:
            stmt = select(Conversation).where(
                Conversation.conversation_id == conversation_id
            )
            result = await self.session.execute(stmt)
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            self.session.delete(conversation)
            await self.session.flush()

            logger.info(f"Deleted conversation {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete conversation: {str(e)}")
            raise

    async def cleanup_expired_conversations(
        self,
        hours: int = 24
    ) -> int:
        """Delete conversations older than specified hours without user association.

        Args:
            hours: Delete conversations created more than N hours ago (default: 24)

        Returns:
            int: Number of conversations deleted

        Raises:
            Exception: If database operation fails
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            stmt = select(Conversation).where(
                (Conversation.user_id.is_(None)) &
                (Conversation.created_at < cutoff_time)
            )

            result = await self.session.execute(stmt)
            expired_conversations = result.scalars().all()

            for conversation in expired_conversations:
                self.session.delete(conversation)

            await self.session.flush()
            count = len(expired_conversations)

            logger.info(f"Cleaned up {count} expired conversations")
            return count

        except Exception as e:
            logger.error(f"Failed to cleanup expired conversations: {str(e)}")
            raise


# Factory for dependency injection
async def get_conversation_service(session: AsyncSession) -> ConversationService:
    """Factory function for creating ConversationService instances.

    Args:
        session: AsyncSession for database operations

    Returns:
        ConversationService: Initialized service instance
    """
    return ConversationService(session)
