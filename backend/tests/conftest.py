"""Pytest configuration and shared fixtures for all tests."""

import pytest
import asyncio
import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Set test database URL before importing any modules that use it
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_API_KEY", "test-api-key")
os.environ.setdefault("QDRANT_COLLECTION_NAME", "test_chunks")
os.environ.setdefault("ALLOWED_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("RATE_LIMIT_REQUESTS", "10")
os.environ.setdefault("RATE_LIMIT_PERIOD", "60")

from src.models.database import Base


# Configure asyncio event loop
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db_engine():
    """Create in-memory SQLite database engine for tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        pool_pre_ping=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_factory = async_sessionmaker(
        bind=test_db_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with async_session_factory() as session:
        yield session


@pytest.fixture
def mock_openai_service():
    """Mock OpenAI service for embedding and generation."""
    service = AsyncMock()
    service.embed = AsyncMock(return_value=[0.1] * 1536)
    service.generate = AsyncMock(
        return_value="Generated response [Chapter 1: Introduction]"
    )
    return service


@pytest.fixture
def mock_qdrant_service():
    """Mock Qdrant vector database service."""
    service = AsyncMock()
    service.create_collection = AsyncMock()
    service.upsert = AsyncMock(return_value={"count": 3})
    service.search = AsyncMock(
        return_value=[
            {"payload": {"content": "Passage 1"}, "score": 0.95},
            {"payload": {"content": "Passage 2"}, "score": 0.87},
            {"payload": {"content": "Passage 3"}, "score": 0.82},
        ]
    )
    return service


@pytest.fixture
def mock_conversation_service():
    """Mock conversation service for multi-turn support."""
    service = AsyncMock()
    service.get_context_window = AsyncMock(return_value=[])
    service.format_context_for_prompt = AsyncMock(return_value=[])
    service.save_message = AsyncMock()
    service.create_conversation = AsyncMock()
    return service


# Configure pytest asyncio
pytest_plugins = ('pytest_asyncio',)
