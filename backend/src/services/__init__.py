"""Services package for external integrations and business logic."""

from src.services.qdrant_client import QdrantService, get_qdrant_service
from src.services.openai_client import OpenAIService, get_openai_service
from src.services.conversation_service import (
    ConversationService,
    get_conversation_service
)

# Lazy-loaded singletons
def get_qdrant():
    """Get Qdrant service instance."""
    return get_qdrant_service()


def get_openai():
    """Get OpenAI service instance."""
    return get_openai_service()


__all__ = [
    "QdrantService",
    "get_qdrant_service",
    "get_qdrant",
    "OpenAIService",
    "get_openai_service",
    "get_openai",
    "ConversationService",
    "get_conversation_service",
]
