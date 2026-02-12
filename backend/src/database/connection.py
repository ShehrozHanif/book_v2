"""Database connection and session management with production connection pooling."""

import os
import ssl as ssl_module
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DATABASE_POOL_MODE = os.getenv("DATABASE_POOL_MODE", "queuepool")  # queuepool or nullpool

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Ensure the URL uses asyncio driver for PostgreSQL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Detect if SSL is needed (Neon, Render, etc.) and strip unsupported params
NEEDS_SSL = "sslmode=" in DATABASE_URL or "ssl=" in DATABASE_URL or "neon.tech" in DATABASE_URL
# Remove query params not supported by asyncpg
for param in ["sslmode=require", "channel_binding=require", "ssl=require"]:
    DATABASE_URL = DATABASE_URL.replace("&" + param, "").replace("?" + param + "&", "?").replace("?" + param, "")
# Clean up trailing ? or &
DATABASE_URL = DATABASE_URL.rstrip("&").rstrip("?")


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

# Build connect_args for SSL if needed (Neon requires SSL)
connect_args = {}
if NEEDS_SSL:
    ssl_context = ssl_module.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl_module.CERT_NONE
    connect_args["ssl"] = ssl_context

# Create async engine with production-grade connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=poolclass,
    future=True,
    connect_args=connect_args,
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
    from sqlalchemy import text

    async with engine.begin() as conn:
        # Create personalization tables (uses PostgreSQL-specific types)
        await conn.run_sync(PersonalizationBase.metadata.create_all)

        # Create conversations table if it doesn't exist
        # (uses UUID to match personalization users table)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id VARCHAR(36) PRIMARY KEY,
                user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                expires_at TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """))

        # Create messages table if it doesn't exist
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id VARCHAR(36) PRIMARY KEY,
                conversation_id VARCHAR(36) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """))

        # Create audit_logs table if it doesn't exist
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                query TEXT,
                response TEXT,
                relevance_scores JSON,
                user_id VARCHAR(36),
                conversation_id VARCHAR(36),
                processing_time_ms FLOAT,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """))


async def close_db():
    """Close database connections."""
    await engine.dispose()
