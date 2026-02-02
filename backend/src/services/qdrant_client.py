"""Qdrant vector database client for semantic search."""

import logging
import os
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for vector search using Qdrant Cloud."""

    def __init__(self):
        """Initialize Qdrant client with environment variables."""
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if not qdrant_url or not qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables must be set")

        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")
        self.vector_size = 1536  # OpenAI embedding dimension (text-embedding-3-small)

    async def create_collection(self) -> bool:
        """Create collection if it doesn't exist.

        Returns:
            bool: True if collection created or already exists, False on error

        Raises:
            Exception: If connection to Qdrant fails
        """
        try:
            # Check if collection exists
            try:
                self.client.get_collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
            except Exception:
                # Collection doesn't exist, create it
                pass

            # Create collection with COSINE distance metric
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection '{self.collection_name}' created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            raise

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """Search for similar passages using vector similarity.

        Args:
            query_vector: 1536-dimensional embedding vector from OpenAI
            top_k: Number of top results to return (default: 5)
            score_threshold: Minimum similarity score (0.0-1.0, optional)

        Returns:
            List of dicts with id, score, and payload fields:
            [
                {
                    "id": "chunk_id",
                    "score": 0.95,
                    "payload": {
                        "content": "...",
                        "module": "...",
                        "chapter": "...",
                        "section": "..."
                    }
                },
                ...
            ]

        Raises:
            ValueError: If query_vector dimension doesn't match
            Exception: If Qdrant search fails
        """
        if len(query_vector) != self.vector_size:
            raise ValueError(
                f"Query vector dimension {len(query_vector)} "
                f"does not match expected {self.vector_size}"
            )

        try:
            # Use query_points method for semantic search in Qdrant
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k,
                score_threshold=score_threshold
            )

            # Transform results to dict format
            passages = []
            for result in results.points:
                passages.append({
                    "id": str(result.id),
                    "score": result.score,
                    "payload": dict(result.payload) if result.payload else {}
                })

            logger.debug(f"Retrieved {len(passages)} passages for query")
            return passages

        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise

    async def upsert(self, points: List[Dict]) -> bool:
        """Upsert passage vectors into Qdrant.

        Each point dict should contain:
        {
            "id": "unique_id",  # Can be numeric or string
            "vector": [1.0, 2.0, ...],  # 1536-dimensional vector
            "payload": {
                "content": "passage text",
                "module": "module name",
                "chapter": "chapter name",
                "section": "section name"
            }
        }

        Args:
            points: List of point dicts with id, vector, and payload

        Returns:
            bool: True if upsert successful

        Raises:
            ValueError: If points format is invalid
            Exception: If Qdrant upsert fails
        """
        if not points:
            logger.warning("Empty points list provided to upsert")
            return True

        try:
            # Validate and convert points to PointStruct format
            point_structs = []
            for i, point in enumerate(points):
                if "id" not in point or "vector" not in point or "payload" not in point:
                    raise ValueError(
                        f"Point {i} missing required fields: id, vector, payload"
                    )

                vector = point["vector"]
                if len(vector) != self.vector_size:
                    raise ValueError(
                        f"Point {i} vector dimension {len(vector)} "
                        f"does not match expected {self.vector_size}"
                    )

                # Convert id to integer if possible, otherwise use as string
                point_id = point["id"]
                if isinstance(point_id, str):
                    try:
                        point_id = int(point_id)
                    except ValueError:
                        # Keep as string if not convertible to int
                        pass

                point_structs.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=point["payload"]
                    )
                )

            # Upsert all points
            self.client.upsert(
                collection_name=self.collection_name,
                points=point_structs
            )

            logger.info(f"Successfully upserted {len(point_structs)} points")
            return True

        except Exception as e:
            logger.error(f"Failed to upsert points: {str(e)}")
            raise

    async def delete_collection(self) -> bool:
        """Delete the collection (use with caution).

        Returns:
            bool: True if collection deleted

        Raises:
            Exception: If deletion fails
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            raise

    async def get_collection_info(self) -> Dict:
        """Get information about the collection.

        Returns:
            Dict with collection metadata (point count, vectors_count, etc.)

        Raises:
            Exception: If collection info retrieval fails
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "points_count": info.points_count,
                "vectors_count": info.vectors_count if hasattr(info, "vectors_count") else None,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            raise


# Lazy singleton instance
_qdrant_service_instance = None


def get_qdrant_service():
    """Get or create the Qdrant service singleton.

    Returns:
        QdrantService: Initialized service instance
    """
    global _qdrant_service_instance
    if _qdrant_service_instance is None:
        _qdrant_service_instance = QdrantService()
    return _qdrant_service_instance
