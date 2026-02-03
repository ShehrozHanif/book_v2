"""Retrieval service for vector search and passage ranking."""

import logging
from typing import List, Dict
from src.services.qdrant_client import get_qdrant_service

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving and ranking relevant passages from Qdrant."""

    def __init__(self, top_k: int = 5, min_relevance: float = 0.3):
        """Initialize retrieval service.

        Args:
            top_k: Number of top results to retrieve from Qdrant (default: 5)
            min_relevance: Minimum relevance score threshold (0-1, default: 0.3)
        """
        self.qdrant_service = get_qdrant_service()
        self.top_k = top_k
        self.min_relevance = min_relevance

    async def search(self, query_vector: List[float]) -> List[Dict]:
        """Search Qdrant for top-k similar passages.

        Args:
            query_vector: 1536-dimensional embedding vector

        Returns:
            List of dicts with passage data:
            [
                {
                    "id": "chunk_id",
                    "score": 0.95,
                    "payload": {
                        "content": "passage text",
                        "module": "...",
                        "chapter": "...",
                        "section": "..."
                    }
                },
                ...
            ]

        Raises:
            ValueError: If query_vector dimension is invalid
            Exception: If Qdrant search fails
        """
        try:
            results = await self.qdrant_service.search(
                query_vector,
                top_k=self.top_k
            )
            logger.info(f"Qdrant search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            raise

    async def rank_passages(
        self,
        passages: List[Dict],
        query: str
    ) -> List[Dict]:
        """Rank passages by relevance and filter low-scoring results.

        Args:
            passages: List of passage dicts from Qdrant search
            query: Original query string (for logging context)

        Returns:
            List of ranked passages filtered by min_relevance threshold,
            sorted by score descending
        """
        # Filter by minimum relevance threshold
        filtered = [
            p for p in passages
            if p.get("score", 0) >= self.min_relevance
        ]

        # Sort by score descending
        ranked = sorted(
            filtered,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        logger.info(
            f"Ranked {len(passages)} passages → {len(ranked)} relevant "
            f"(threshold: {self.min_relevance})"
        )
        return ranked

    async def retrieve_context(
        self,
        query_vector: List[float],
        query: str,
        top_k: int = 3
    ) -> tuple[List[str], List[float]]:
        """Retrieve and rank passages for LLM context.

        This method performs the full retrieval pipeline:
        1. Search for top-k passages using vector similarity
        2. Rank passages by relevance score
        3. Extract content and scores for LLM context

        Args:
            query_vector: 1536-dimensional embedding vector
            query: Original query string (for logging)
            top_k: Number of passages to return for context (default: 3)

        Returns:
            Tuple of:
            - passages (List[str]): List of passage content strings
            - scores (List[float]): Corresponding relevance scores (0-1)

        Raises:
            Exception: If search or ranking fails
        """
        # Step 1: Search Qdrant
        results = await self.search(query_vector)

        # Step 2: Rank passages
        ranked = await self.rank_passages(results, query)

        # Step 3: Extract content and scores (top-k for context window)
        passages = [
            r["payload"]["content"]
            for r in ranked[:top_k]
        ]
        scores = [r["score"] for r in ranked[:top_k]]

        logger.info(f"Retrieved {len(passages)} passages for context")
        return passages, scores


# Singleton instance
_retrieval_service_instance = None


def get_retrieval_service(
    top_k: int = 5,
    min_relevance: float = 0.3
) -> RetrievalService:
    """Get or create the retrieval service singleton.

    Args:
        top_k: Number of top results to retrieve (default: 5)
        min_relevance: Minimum relevance threshold (default: 0.3)

    Returns:
        RetrievalService: Initialized service instance
    """
    global _retrieval_service_instance
    if _retrieval_service_instance is None:
        _retrieval_service_instance = RetrievalService(
            top_k=top_k,
            min_relevance=min_relevance
        )
    return _retrieval_service_instance
