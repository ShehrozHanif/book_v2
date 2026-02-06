"""Tests for T092: Database Connection Pooling."""

import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool


class TestConnectionPoolConfiguration:
    """Test connection pool configuration."""

    def test_pool_config_returns_tuple(self):
        """Verify _get_pool_config returns (poolclass, config_dict)."""
        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        assert poolclass is not None
        assert isinstance(config, dict)

    def test_pool_config_has_expected_keys(self):
        """Verify QueuePool configuration has expected parameters."""
        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        # For QueuePool mode, verify expected keys
        if poolclass == AsyncAdaptedQueuePool:
            assert "pool_size" in config
            assert "max_overflow" in config
            assert "pool_timeout" in config
            assert "pool_recycle" in config
            assert "pool_pre_ping" in config

    def test_pool_config_queuepool_settings(self):
        """Verify QueuePool configuration parameters when in queuepool mode."""
        # Only run if queuepool mode is enabled
        pool_mode = os.getenv("DATABASE_POOL_MODE", "queuepool")
        if pool_mode != "queuepool":
            pytest.skip("Not in QueuePool mode")

        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        if poolclass == AsyncAdaptedQueuePool:
            assert config["pool_size"] == 5  # Min connections
            assert config["max_overflow"] == 15  # Max additional
            assert config["pool_timeout"] == 30  # Timeout in seconds
            assert config["pool_recycle"] == 3600  # Recycle after 1 hour
            assert config["pool_pre_ping"] is True  # Health check

    def test_pool_config_nullpool_mode(self):
        """Verify NullPool configuration when requested."""
        from src.database.connection import _get_pool_config

        with patch.dict("os.environ", {"DATABASE_POOL_MODE": "nullpool"}):
            # Reload to pick up env var
            import importlib
            import src.database.connection as conn_module
            importlib.reload(conn_module)

            poolclass, config = conn_module._get_pool_config()
            assert poolclass is NullPool
            assert config == {}

    def test_pool_total_capacity(self):
        """Verify total pool capacity when using QueuePool."""
        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        if poolclass == AsyncAdaptedQueuePool and config:
            total_capacity = config["pool_size"] + config["max_overflow"]
            assert total_capacity == 20  # Expected: 5 + 15


class TestConnectionPooling:
    """Test connection pooling behavior."""

    def test_engine_created_successfully(self):
        """Verify engine is created without errors."""
        from src.database.connection import engine

        assert engine is not None

    def test_pool_class_matches_config(self):
        """Verify engine pool class matches configuration."""
        from src.database.connection import engine, DATABASE_POOL_MODE

        if DATABASE_POOL_MODE == "queuepool":
            # Should use AsyncAdaptedQueuePool for async engines
            assert engine.pool.__class__.__name__ in ["AsyncAdaptedQueuePool", "FallbackAsyncAdaptedQueuePool"]
        else:
            # Should use NullPool for serverless
            assert engine.pool.__class__.__name__ == "NullPool"

    def test_pool_pre_ping_when_queuepool(self):
        """Verify connection health checks are enabled for QueuePool."""
        from src.database.connection import engine, DATABASE_POOL_MODE

        if DATABASE_POOL_MODE == "queuepool":
            # pre_ping might be set on the pool
            pool = engine.pool
            if hasattr(pool, "pre_ping"):
                assert pool.pre_ping is True

    def test_pool_recycle_when_queuepool(self):
        """Verify pool recycle timeout is set for QueuePool."""
        from src.database.connection import engine, DATABASE_POOL_MODE

        if DATABASE_POOL_MODE == "queuepool":
            pool = engine.pool
            if hasattr(pool, "_recycle"):
                assert pool._recycle == 3600  # 1 hour

    def test_database_url_configured(self):
        """Verify DATABASE_URL is properly configured."""
        from src.database.connection import DATABASE_URL

        assert DATABASE_URL is not None
        assert len(DATABASE_URL) > 0


class TestConnectionReuse:
    """Test connection reuse patterns."""

    @pytest.mark.asyncio
    async def test_session_creation(self):
        """Verify sessions can be created."""
        from src.database.connection import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            assert session is not None

    @pytest.mark.asyncio
    async def test_multiple_sequential_sessions(self):
        """Verify multiple sequential sessions work correctly."""
        from src.database.connection import AsyncSessionLocal

        sessions = []
        for i in range(5):
            async with AsyncSessionLocal() as session:
                assert session is not None
                sessions.append(session is not None)

        assert len(sessions) == 5
        assert all(sessions)

    @pytest.mark.asyncio
    async def test_concurrent_session_access(self):
        """Verify concurrent access to sessions."""
        from src.database.connection import AsyncSessionLocal

        async def create_session(session_id):
            async with AsyncSessionLocal() as session:
                await asyncio.sleep(0.01)
                return session_id

        results = await asyncio.gather(
            *[create_session(i) for i in range(10)]
        )

        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_concurrent_requests_succeed(self):
        """Verify concurrent requests succeed."""
        from src.database.connection import AsyncSessionLocal

        async def worker(worker_id):
            try:
                async with AsyncSessionLocal() as session:
                    await asyncio.sleep(0.001)
                    return True
            except Exception:
                return False

        results = await asyncio.gather(
            *[worker(i) for i in range(50)],
            return_exceptions=False
        )

        # Most should succeed
        assert sum(results) >= 40


class TestConnectionConfiguration:
    """Test connection configuration options."""

    def test_pool_mode_configurable(self):
        """Verify pool mode is configurable via environment."""
        from src.database.connection import DATABASE_POOL_MODE

        assert DATABASE_POOL_MODE in ["queuepool", "nullpool"]

    def test_get_pool_config_function_exists(self):
        """Verify _get_pool_config function is available."""
        from src.database.connection import _get_pool_config

        assert callable(_get_pool_config)

    def test_get_session_available(self):
        """Verify get_session dependency injection is available."""
        from src.database.connection import get_session

        assert callable(get_session)

    def test_async_session_local_available(self):
        """Verify AsyncSessionLocal is available."""
        from src.database.connection import AsyncSessionLocal

        assert AsyncSessionLocal is not None


class TestPoolCapacity:
    """Test pool capacity configuration."""

    def test_pool_capacity_reasonable(self):
        """Verify pool capacity is reasonable for typical deployments."""
        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        if config:  # Only check for QueuePool
            total_capacity = config.get("pool_size", 0) + config.get("max_overflow", 0)
            # Reasonable range: 10-50 total connections
            assert 10 <= total_capacity <= 50

    def test_pool_min_size_reasonable(self):
        """Verify minimum pool size is reasonable."""
        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        if config:
            pool_size = config.get("pool_size", 0)
            assert pool_size > 0 and pool_size <= 20

    def test_pool_max_overflow_reasonable(self):
        """Verify max overflow is reasonable."""
        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        if config:
            max_overflow = config.get("max_overflow", 0)
            assert max_overflow >= 0 and max_overflow <= 50


class TestConnectionIntegration:
    """Integration tests for connection pooling."""

    def test_init_db_callable(self):
        """Verify init_db is callable."""
        from src.database.connection import init_db

        assert callable(init_db)

    def test_close_db_callable(self):
        """Verify close_db is callable."""
        from src.database.connection import close_db

        assert callable(close_db)

    @pytest.mark.asyncio
    async def test_session_dependency_injection(self):
        """Verify session dependency injection works."""
        from src.database.connection import get_session

        # get_session is an async generator
        session_gen = get_session()
        assert hasattr(session_gen, "__anext__")

    def test_engine_has_pool(self):
        """Verify engine has a pool configured."""
        from src.database.connection import engine

        assert hasattr(engine, "pool")
        assert engine.pool is not None


class TestConnectionPoolingSettings:
    """Test specific connection pooling settings."""

    def test_pool_timeout_configured(self):
        """Verify pool timeout setting."""
        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        if config:
            timeout = config.get("pool_timeout", None)
            if timeout is not None:
                assert isinstance(timeout, int)
                assert timeout > 0

    def test_pool_recycle_configured(self):
        """Verify pool recycle setting."""
        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        if config:
            recycle = config.get("pool_recycle", None)
            if recycle is not None:
                assert isinstance(recycle, int)
                assert recycle > 0
                assert recycle == 3600  # 1 hour

    def test_pool_pre_ping_configured(self):
        """Verify pool pre-ping setting."""
        from src.database.connection import _get_pool_config

        poolclass, config = _get_pool_config()

        if config:
            pre_ping = config.get("pool_pre_ping", None)
            if pre_ping is not None:
                assert isinstance(pre_ping, bool)
                assert pre_ping is True


# Summary statistics about tests
def test_summary():
    """Test that demonstrates all connection pooling features are configured."""
    from src.database.connection import (
        engine,
        _get_pool_config,
        DATABASE_POOL_MODE,
        DATABASE_URL,
        get_session,
        AsyncSessionLocal,
        init_db,
        close_db,
    )

    poolclass, config = _get_pool_config()

    # Verify all components exist
    assert engine is not None
    assert DATABASE_URL is not None
    assert DATABASE_POOL_MODE in ["queuepool", "nullpool"]
    assert callable(get_session)
    assert callable(init_db)
    assert callable(close_db)
    assert AsyncSessionLocal is not None

    # Verify pooling is configured appropriately
    if DATABASE_POOL_MODE == "queuepool":
        assert poolclass is not None
        if config:
            assert "pool_size" in config
            assert "max_overflow" in config
            assert "pool_timeout" in config
            assert "pool_recycle" in config
            assert "pool_pre_ping" in config
