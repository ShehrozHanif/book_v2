"""Unit tests for structured logger."""

import pytest
from src.logger import StructuredLogger, get_logger


class TestStructuredLogger:
    """Test suite for StructuredLogger."""

    def test_logger_initialization(self):
        """Test logger can be initialized."""
        logger = StructuredLogger("test_logger")
        assert logger is not None
        assert logger.logger.name == "test_logger"

    def test_get_logger_factory(self):
        """Test get_logger factory function."""
        logger = get_logger("test_factory")
        assert isinstance(logger, StructuredLogger)
        assert logger.logger.name == "test_factory"

    def test_log_query(self, caplog):
        """Test query logging."""
        logger = StructuredLogger("test")
        logger.log_query(
            query="What is ROS 2?",
            conversation_id="550e8400-e29b-41d4-a716-446655440000",
            user_id="7c9e6679-7425-40de-944b-e07fc1f90ae7"
        )
        assert "Query received" in caplog.text
        assert "conv_id=550e8400" in caplog.text

    def test_log_query_anonymous(self, caplog):
        """Test anonymous query logging."""
        logger = StructuredLogger("test")
        logger.log_query(
            query="What is ROS 2?",
            conversation_id="550e8400-e29b-41d4-a716-446655440000",
            user_id=None
        )
        assert "Query received" in caplog.text
        assert "user_id=anonymous" in caplog.text

    def test_log_embedding_api_call(self, caplog):
        """Test embedding API call logging."""
        logger = StructuredLogger("test")
        logger.log_embedding_api_call(
            query="What is ROS 2?",
            tokens=50,
            cost=0.000001,
            duration_ms=234.56
        )
        assert "Embedding API" in caplog.text
        assert "tokens=50" in caplog.text
        assert "cost=$0.000001" in caplog.text

    def test_log_retrieval(self, caplog):
        """Test retrieval logging."""
        logger = StructuredLogger("test")
        logger.log_retrieval(
            query="What is ROS 2?",
            num_passages=3,
            relevance_scores=[0.95, 0.87, 0.86],
            duration_ms=456.78
        )
        assert "Retrieval" in caplog.text
        assert "passages=3" in caplog.text
        assert "avg_relevance=0.893" in caplog.text

    def test_log_retrieval_empty_scores(self, caplog):
        """Test retrieval logging with empty scores."""
        logger = StructuredLogger("test")
        logger.log_retrieval(
            query="What is ROS 2?",
            num_passages=0,
            relevance_scores=[],
            duration_ms=100.0
        )
        assert "Retrieval" in caplog.text
        assert "passages=0" in caplog.text

    def test_log_generation_api_call(self, caplog):
        """Test generation API call logging."""
        logger = StructuredLogger("test")
        logger.log_generation_api_call(
            prompt_tokens=1000,
            completion_tokens=200,
            total_tokens=1200,
            cost=0.00027,
            duration_ms=1234.56
        )
        assert "Generation API" in caplog.text
        assert "tokens=1200" in caplog.text
        assert "prompt=1000" in caplog.text
        assert "completion=200" in caplog.text

    def test_log_error(self, caplog):
        """Test error logging."""
        logger = StructuredLogger("test")
        logger.log_error(
            error_type="validation_error",
            message="Invalid query",
            details={"query_length": 0}
        )
        assert "ERROR" in caplog.text
        assert "validation_error" in caplog.text

    def test_log_performance(self, caplog):
        """Test performance logging."""
        logger = StructuredLogger("test")
        logger.log_performance(
            operation="process_query",
            duration_ms=2000.0,
            success=True,
            metadata={"num_passages": 3}
        )
        assert "Performance" in caplog.text
        assert "process_query" in caplog.text
        assert "duration=2000.00ms" in caplog.text
        assert "success" in caplog.text

    def test_log_rate_limit(self, caplog):
        """Test rate limit logging."""
        logger = StructuredLogger("test")
        logger.log_rate_limit(
            identifier="192.168.1.1",
            limit=60,
            window="1m"
        )
        assert "Rate limit exceeded" in caplog.text
        assert "limit=60/1m" in caplog.text

    def test_log_cache_hit(self, caplog):
        """Test cache hit logging."""
        logger = StructuredLogger("test")
        logger.log_cache_hit(
            cache_key="query_hash_12345",
            hit=True
        )
        assert "Cache HIT" in caplog.text

    def test_log_cache_miss(self, caplog):
        """Test cache miss logging."""
        logger = StructuredLogger("test")
        logger.log_cache_hit(
            cache_key="query_hash_67890",
            hit=False
        )
        assert "Cache MISS" in caplog.text
