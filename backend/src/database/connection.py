"""Database connection and session management with production connection pooling."""

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_POOL_MODE = os.getenv("DATABASE_POOL_MODE", "queuepool")  # queuepool or nullpool

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Ensure the URL uses asyncio driver for PostgreSQL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


def _get_pool_config():
    """
    Get appropriate pool configuration based on environment.

    Returns:
        Tuple of (poolclass, pool_config_dict)
    """
    if DATABASE_POOL_MODE == "nullpool":
        # For serverless/Neon - no connection pooling
        return NullPool, {}

    # Production AsyncAdaptedQueuePool configuration
    # Balanced for VPS/cloud environments with async support
    pool_config = {
        "pool_size": 5,              # Min connections to maintain
        "max_overflow": 15,          # Additional temporary connections (20 total max)
        "pool_timeout": 30,          # Wait 30s for available connection
        "pool_recycle": 3600,        # Recycle connections after 1 hour
        "pool_pre_ping": True,       # Test connection before use
    }
    return AsyncAdaptedQueuePool, pool_config


# Determine pool configuration
poolclass, pool_config = _get_pool_config()

# Create async engine with production-grade connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=poolclass,
    future=True,
    **pool_config  # Unpack pool configuration parameters
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
    from src.personalization.models.db_models import Base as PersonalizationBase

    async with engine.begin() as conn:
        # Create personalization tables only (uses PostgreSQL-specific types)
        await conn.run_sync(PersonalizationBase.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()
