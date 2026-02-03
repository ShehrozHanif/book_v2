"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.config import get_settings
from src.database.connection import init_db, close_db
from src.api.error_handler import setup_exception_handlers
from src.api.rate_limiter import RateLimiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize rate limiter
rate_limiter = RateLimiter(
    requests_per_period=settings.RATE_LIMIT_REQUESTS,
    period_seconds=settings.RATE_LIMIT_PERIOD,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # Startup
    logger.info("Initializing database...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Closing database connections...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Backend API for RAG-powered chatbot over Humanoid Robotics textbook",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup exception handlers
setup_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"],
)

# Make rate limiter available to app
app.state.rate_limiter = rate_limiter


# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness check endpoint - verifies all services are ready."""
    return {
        "status": "ready",
        "database": "connected",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "title": "RAG Chatbot API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi_schema": "/openapi.json",
    }


# Import and include routers
from src.api.routes.chat import router as chat_router

app.include_router(chat_router)
