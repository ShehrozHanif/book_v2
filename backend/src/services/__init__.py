"""Services package for external integrations and business logic."""

from src.services.qdrant_client import QdrantService, get_qdrant_service
from src.services.openai_client import OpenAIService, get_openai_service
from src.services.conversation_service import (
    ConversationService,
    get_conversation_service
)
from src.services.embedding_service import (
    EmbeddingService,
    get_embedding_service
)
from src.services.retrieval_service import (
    RetrievalService,
    get_retrieval_service
)
from src.services.generation_service import (
    GenerationService,
    get_generation_service
)
from src.services.security_service import (
    SecurityService,
    get_security_service
)
from src.services.chat_service import (
    ChatService,
    get_chat_service
)

# Lazy-loaded singletons
def get_qdrant():
    """Get Qdrant service instance."""
    return get_qdrant_service()


def get_openai():
    """Get OpenAI service instance."""
    return get_openai_service()


__all__ = [
    # Qdrant Vector Database
    "QdrantService",
    "get_qdrant_service",
    "get_qdrant",
    # OpenAI API
    "OpenAIService",
    "get_openai_service",
    "get_openai",
    # Conversation Management
    "ConversationService",
    "get_conversation_service",
    # RAG Pipeline Services
    "EmbeddingService",
    "get_embedding_service",
    "RetrievalService",
    "get_retrieval_service",
    "GenerationService",
    "get_generation_service",
    "SecurityService",
    "get_security_service",
    "ChatService",
    "get_chat_service",
]
