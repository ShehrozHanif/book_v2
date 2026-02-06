"""Retrieval service for vector search and passage ranking."""

import logging
import re
from typing import List, Dict, Optional
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

    async def search(
        self,
        query_vector: List[float],
        filter_chapter: Optional[str] = None
    ) -> List[Dict]:
        """Search Qdrant for top-k similar passages.

        Args:
            query_vector: 1536-dimensional embedding vector
            filter_chapter: Optional chapter to filter results (e.g., "Chapter 4")

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
                top_k=self.top_k,
                filter_chapter=filter_chapter
            )
            logger.info(f"Qdrant search returned {len(results)} results (filter_chapter={filter_chapter})")
            return results
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            raise

    def extract_chapter_number(self, query: str) -> Optional[int]:
        """Extract chapter number from query if present.

        Args:
            query: User query string

        Returns:
            Chapter number (1-22) if found, None otherwise
        """
        # Look for patterns like "Chapter 5", "chapter 5", "Ch 5", "Ch. 5"
        patterns = [
            r'chapter\s+(\d+)',
            r'ch\.?\s+(\d+)',
            r'ch\.?\s*(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                chapter_num = int(match.group(1))
                if 1 <= chapter_num <= 22:
                    logger.info(f"Detected chapter {chapter_num} in query: '{query[:50]}...'")
                    return chapter_num

        return None

    async def rank_passages(
        self,
        passages: List[Dict],
        query: str
    ) -> List[Dict]:
        """Rank passages by relevance and filter low-scoring results.

        Also prioritizes passages from a specific chapter if detected in query.

        Args:
            passages: List of passage dicts from Qdrant search
            query: Original query string (for logging context)

        Returns:
            List of ranked passages filtered by min_relevance threshold,
            sorted by score descending (with chapter-specific results prioritized)
        """
        # Detect if query is asking about a specific chapter
        target_chapter = self.extract_chapter_number(query)

        # Filter by minimum relevance threshold
        filtered = [
            p for p in passages
            if p.get("score", 0) >= self.min_relevance
        ]

        # If a specific chapter was detected, prioritize passages from that chapter
        if target_chapter:
            target_chapter_str = f"Chapter {target_chapter}"

            # Separate passages: from target chapter vs others
            target_passages = [
                p for p in filtered
                if target_chapter_str in p.get("payload", {}).get("chapter", "")
            ]
            other_passages = [
                p for p in filtered
                if target_chapter_str not in p.get("payload", {}).get("chapter", "")
            ]

            # Sort both groups by score descending
            target_passages.sort(key=lambda x: x.get("score", 0), reverse=True)
            other_passages.sort(key=lambda x: x.get("score", 0), reverse=True)

            # Combine: target chapter first, then others
            ranked = target_passages + other_passages

            logger.info(
                f"Chapter-specific filtering: {len(target_passages)} from Chapter {target_chapter}, "
                f"{len(other_passages)} from other chapters"
            )
        else:
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
        1. Detect if query targets a specific chapter
        2. Search for top-k passages using vector similarity (NO filtering - semantic first)
        3. Rank passages by relevance score with chapter prioritization
        4. Extract content and scores for LLM context

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
        # DEBUG: Log retrieve_context call
        logger.info(f"[RETRIEVAL] retrieve_context called with query: {query}")
        logger.info(f"[RETRIEVAL] Service instance ID: {id(self)}")

        # Detect if query targets a specific chapter
        target_chapter = self.extract_chapter_number(query)

        logger.info(f"[RETRIEVAL] Detected chapter number: {target_chapter}")

        # Step 1: Search Qdrant WITHOUT filter - use semantic similarity first
        # For bare "Chapter X" queries, semantic similarity is low, so filtering would return 0 results
        # Instead, we retrieve more results and let rank_passages prioritize by chapter
        try:
            search_top_k = self.top_k * 5  # Get 25 results to have larger pool for chapter prioritization
            results = await self.qdrant_service.search(
                query_vector,
                top_k=search_top_k,
                filter_chapter=None  # NO FILTER - let semantic similarity guide
            )
            logger.info(f"[RETRIEVAL] Qdrant search returned {len(results)} results (no filter - semantic ranking)")
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            raise

        # Step 1b: If target chapter detected but not in results, do targeted search for that chapter
        target_chapter = self.extract_chapter_number(query)
        if target_chapter:
            target_chapter_str = f"Chapter {target_chapter}"
            chapters_in_results = [
                r['payload'].get('chapter', '') for r in results
            ]
            if not any(target_chapter_str in ch for ch in chapters_in_results):
                logger.info(f"[RETRIEVAL] Target Chapter {target_chapter} not in top {search_top_k} results, adding targeted search")
                try:
                    # Get top results specifically for this chapter
                    targeted_results = await self.qdrant_service.search(
                        query_vector,
                        top_k=5,
                        filter_chapter=target_chapter_str
                    )
                    if targeted_results:
                        # Insert the best targeted result at the beginning
                        results.insert(0, targeted_results[0])
                        logger.info(f"[RETRIEVAL] Added targeted result for Chapter {target_chapter}")
                except Exception as e:
                    logger.warning(f"[RETRIEVAL] Targeted search for Chapter {target_chapter} failed: {e}")

        # Step 2: Rank passages with chapter prioritization
        ranked = await self.rank_passages(results, query)

        # Step 3: Extract content and scores (top-k for context window)
        passages = [
            r["payload"]["content"]
            for r in ranked[:top_k]
        ]
        scores = [r["score"] for r in ranked[:top_k]]

        # DEBUG: Log what we're returning
        logger.info(f"[RETRIEVAL] Returning {len(passages)} passages:")
        for i, (p, s) in enumerate(zip(passages, scores), 1):
            ch = p.split('Chapter')[1].strip().split()[0] if 'Chapter' in p else '?'
            logger.info(f"[RETRIEVAL]   [{i}] Chapter {ch} (score: {s:.3f})")

        logger.info(f"[RETRIEVAL] Retrieved {len(passages)} passages for context")
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
