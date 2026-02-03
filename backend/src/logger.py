"""Structured logging for production monitoring and observability."""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
import os


class StructuredLogger:
    """Structured JSON logging for production environments.

    Features:
    - Query logging (anonymized for privacy)
    - API call tracking (tokens, cost, duration)
    - Performance monitoring
    - Error tracking with context
    """

    def __init__(self, name: str):
        """Initialize structured logger.

        Args:
            name: Logger name (typically module name)
        """
        self.logger = logging.getLogger(name)
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Prevent duplicate handlers
        if not self.logger.handlers:
            # JSON formatter for structured logs
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_query(
        self,
        query: str,
        conversation_id: str,
        user_id: Optional[str] = None
    ):
        """Log incoming query with anonymization.

        Args:
            query: User question (anonymized in logs)
            conversation_id: Conversation UUID
            user_id: Optional user UUID
        """
        self.logger.info(
            f"Query received: conv_id={conversation_id[:8]}..., "
            f"query_len={len(query)}, user_id={user_id[:8] + '...' if user_id else 'anonymous'}"
        )

    def log_embedding_api_call(
        self,
        query: str,
        tokens: int,
        cost: float,
        duration_ms: float
    ):
        """Log OpenAI embedding API call.

        Args:
            query: Query text (for length tracking)
            tokens: Number of tokens used
            cost: API cost in USD
            duration_ms: Request duration in milliseconds
        """
        self.logger.info(
            f"Embedding API: tokens={tokens}, "
            f"cost=${cost:.6f}, duration={duration_ms:.2f}ms, "
            f"query_len={len(query)}"
        )

    def log_retrieval(
        self,
        query: str,
        num_passages: int,
        relevance_scores: list,
        duration_ms: float
    ):
        """Log retrieval operation.

        Args:
            query: Search query (for length tracking)
            num_passages: Number of passages retrieved
            relevance_scores: List of relevance scores
            duration_ms: Retrieval duration in milliseconds
        """
        avg_relevance = sum(relevance_scores) / len(relevance_scores) \
            if relevance_scores else 0
        min_relevance = min(relevance_scores) if relevance_scores else 0
        max_relevance = max(relevance_scores) if relevance_scores else 0

        self.logger.info(
            f"Retrieval: passages={num_passages}, "
            f"avg_relevance={avg_relevance:.3f}, "
            f"min={min_relevance:.3f}, max={max_relevance:.3f}, "
            f"duration={duration_ms:.2f}ms"
        )

    def log_generation_api_call(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost: float,
        duration_ms: float
    ):
        """Log OpenAI LLM API call.

        Args:
            prompt_tokens: Tokens in prompt
            completion_tokens: Tokens in completion
            total_tokens: Total tokens used
            cost: API cost in USD
            duration_ms: Generation duration in milliseconds
        """
        self.logger.info(
            f"Generation API: tokens={total_tokens} "
            f"(prompt={prompt_tokens}, completion={completion_tokens}), "
            f"cost=${cost:.6f}, duration={duration_ms:.2f}ms"
        )

    def log_error(
        self,
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log error with structured context.

        Args:
            error_type: Error category (e.g., 'validation_error', 'api_error')
            message: Error message
            details: Additional context (sanitized)
        """
        log_entry = {
            "error_type": error_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        self.logger.error(json.dumps(log_entry))

    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log operation performance metrics.

        Args:
            operation: Operation name (e.g., 'process_query', 'embed_document')
            duration_ms: Operation duration in milliseconds
            success: Whether operation succeeded
            metadata: Additional metrics
        """
        status = "success" if success else "failure"
        meta_str = f", {json.dumps(metadata)}" if metadata else ""

        self.logger.info(
            f"Performance: {operation}, "
            f"duration={duration_ms:.2f}ms, status={status}{meta_str}"
        )

    def log_rate_limit(
        self,
        identifier: str,
        limit: int,
        window: str
    ):
        """Log rate limit hit.

        Args:
            identifier: User/IP identifier (anonymized)
            limit: Request limit
            window: Time window (e.g., '1m', '1h')
        """
        self.logger.warning(
            f"Rate limit exceeded: identifier={identifier[:8]}..., "
            f"limit={limit}/{window}"
        )

    def log_cache_hit(
        self,
        cache_key: str,
        hit: bool
    ):
        """Log cache hit/miss.

        Args:
            cache_key: Cache key (hashed)
            hit: Whether cache hit occurred
        """
        status = "HIT" if hit else "MISS"
        self.logger.debug(f"Cache {status}: key={cache_key[:16]}...")


# Global logger instance
logger = StructuredLogger(__name__)


def get_logger(name: str) -> StructuredLogger:
    """Factory for creating logger instances.

    Args:
        name: Logger name (typically __name__)

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)
