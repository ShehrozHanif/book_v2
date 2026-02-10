"""Pytest configuration and fixtures for personalization tests."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.personalization.models.db_models import Base
from src.personalization.utils.auth import init_auth_config


# Test database URL (use in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Monkey patch JSONB and ARRAY to JSON for SQLite compatibility
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy import JSON, Text
from sqlalchemy.types import TypeDecorator
import json as json_lib

class SQLiteARRAY(TypeDecorator):
    """Array type for SQLite (stored as JSON string)."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json_lib.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json_lib.loads(value)
        return value

# Override JSONB and ARRAY compilation for SQLite
def _jsonb_to_json_sqlite():
    """Convert JSONB and ARRAY columns to JSON/Text for SQLite testing."""
    from src.personalization.models import db_models
    import inspect

    for name, obj in inspect.getmembers(db_models):
        if inspect.isclass(obj) and hasattr(obj, '__table__'):
            for column in obj.__table__.columns:
                if hasattr(column.type, '__class__'):
                    if column.type.__class__.__name__ == 'JSONB':
                        column.type = JSON()
                    elif column.type.__class__.__name__ == 'ARRAY':
                        column.type = SQLiteARRAY()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    # Patch JSONB and ARRAY for SQLite BEFORE creating tables
    _jsonb_to_json_sqlite()

    # Force reload of Base metadata to apply changes
    from src.personalization.models.db_models import Base
    Base.metadata.clear()

    # Re-import models to regenerate tables with patched types
    from src.personalization.models import db_models
    import importlib
    importlib.reload(db_models)

    # Get the updated Base
    from src.personalization.models.db_models import Base

    # Patch again after reload
    _jsonb_to_json_sqlite()

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def client(test_db) -> Generator[TestClient, None, None]:
    """Create a test HTTP client."""
    from src.main import app
    from src.database.connection import get_session

    # Override the database dependency
    async def override_get_session():
        yield test_db

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as tc:
        yield tc

    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
def init_test_auth():
    """Initialize auth configuration for tests."""
    init_auth_config(
        secret_key="test_secret_key_for_testing_only",
        access_expire=30,
        refresh_expire=7
    )


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!"
    }


@pytest.fixture
def sample_user_data_2():
    """Second sample user data for testing."""
    return {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "TestPass456!"
    }


@pytest.fixture
async def created_user(test_db, sample_user_data):
    """Create a test user in the database."""
    from src.personalization.services import user_service

    user = await user_service.create_user(
        db=test_db,
        username=sample_user_data["username"],
        email=sample_user_data["email"],
        password=sample_user_data["password"]
    )

    return user


@pytest.fixture
async def auth_headers(created_user):
    """Get authentication headers for test user."""
    from src.personalization.utils.auth import create_access_token

    token = create_access_token({"sub": str(created_user.user_id), "username": created_user.username})

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_user(test_db):
    """Create a test user for database operations."""
    from src.personalization.services import user_service

    user = await user_service.create_user(
        db=test_db,
        username="testuser_db",
        email="testdb@example.com",
        password="TestPass123!"
    )

    return user


@pytest.fixture
async def db_session(test_db):
    """Alias for test_db to match test naming convention."""
    return test_db
