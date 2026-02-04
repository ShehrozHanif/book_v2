"""Embedding service for query and passage vectorization."""

import logging
from typing import List
from src.services.openai_client import get_openai_service
from src.services.qdrant_client import get_qdrant_service

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for embedding queries and passages using OpenAI."""

    def __init__(self):
        """Initialize embedding service with OpenAI client."""
        self.openai_service = get_openai_service()

    async def embed_query(self, query: str) -> List[float]:
        """Embed a single query for vector search.

        Args:
            query: User query string to embed

        Returns:
            List of 1536 floats representing the embedding vector

        Raises:
            ValueError: If query is empty
            Exception: If OpenAI API call fails
        """
        try:
            embedding = await self.openai_service.embed_text(query)
            logger.info(f"Embedded query: {len(query)} chars → 1536 dims")
            return embedding
        except Exception as e:
            logger.error(f"Failed to embed query: {e}")
            raise

    async def embed_passages(self, passages: List[dict]) -> List[dict]:
        """Batch embed passages for indexing.

        Args:
            passages: List of dicts with 'content' and optional metadata fields
                [
                    {"content": "passage text", "module": "...", "chapter": "...", ...},
                    ...
                ]

        Returns:
            List of passage dicts with added 'vector' field and unique 'id'
                [
                    {
                        "content": "passage text",
                        "vector": [1.0, 2.0, ...],  # 1536-dim vector
                        "id": 12345678,
                        "module": "...",
                        ...
                    },
                    ...
                ]

        Raises:
            ValueError: If passages list is empty or contains empty content
            Exception: If OpenAI API call fails
        """
        if not passages:
            raise ValueError("Passages list cannot be empty")

        texts = [p["content"] for p in passages]

        try:
            embeddings = await self.openai_service.embed_batch(texts)
            logger.info(f"Embedded {len(passages)} passages")

            # Combine embeddings with metadata
            embedded_passages = [
                {
                    **passages[i],
                    "vector": embeddings[i],
                    "id": hash(passages[i]["content"]) % (10 ** 8),  # Simple ID
                }
                for i in range(len(passages))
            ]
            return embedded_passages
        except Exception as e:
            logger.error(f"Failed to embed passages: {e}")
            raise

    async def index_textbook(self, chunks: List[dict]) -> int:
        """Convenience method to embed and index textbook chunks in one call.

        This is a helper method that combines embedding and Qdrant indexing
        for the content ingestion pipeline.

        Args:
            chunks: List of chunk dicts with 'content' and metadata fields
                [
                    {"content": "...", "module": "...", "chapter": "...", ...},
                    ...
                ]

        Returns:
            int: Number of chunks successfully embedded and indexed

        Raises:
            ValueError: If chunks list is empty
            Exception: If embedding or indexing fails
        """
        if not chunks:
            raise ValueError("Chunks list cannot be empty")

        try:
            # Embed passages
            embedded = await self.embed_passages(chunks)
            logger.info(f"Embedded {len(embedded)} chunks for indexing")

            # Prepare points for Qdrant
            points = [
                {
                    "id": p["id"],
                    "vector": p["vector"],
                    "payload": {
                        "content": p["content"],
                        "module": p.get("module", ""),
                        "chapter": p.get("chapter", ""),
                        "section": p.get("section", ""),
                    },
                }
                for p in embedded
            ]

            # Upsert to Qdrant
            qdrant_service = get_qdrant_service()
            await qdrant_service.upsert(points)
            logger.info(f"Indexed {len(points)} chunks in Qdrant")

            return len(embedded)

        except Exception as e:
            logger.error(f"Failed to index textbook chunks: {e}")
            raise


# Singleton instance
_embedding_service_instance = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton.

    Returns:
        EmbeddingService: Initialized service instance
    """
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance
