"""Database connection and session management."""

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Ensure the URL uses asyncio driver for PostgreSQL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with NullPool for serverless environments
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,  # For serverless/Neon
    future=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    """Dependency injection function for database sessions."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    from src.models.database import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()
