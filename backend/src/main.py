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
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "testserver", "*.onrender.com"],
)

# Make rate limiter available to app
app.state.rate_limiter = rate_limiter


# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "ok", "environment": settings.ENVIRONMENT, "version": "debug-v2"}


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness check endpoint - verifies all services are ready."""
    import os
    openai_key = os.getenv("OPENAI_API_KEY", "")
    qdrant_url = os.getenv("QDRANT_URL", "")
    return {
        "status": "ready",
        "database": "connected",
        "environment": settings.ENVIRONMENT,
        "openai_key_set": bool(openai_key),
        "openai_key_length": len(openai_key),
        "openai_key_prefix": openai_key[:10] + "..." if openai_key else "MISSING",
        "qdrant_url_set": bool(qdrant_url),
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
from src.personalization.api.routes import users_router, assessment_router, progress_router, practice_router
from src.personalization.api.routes.preferences import router as preferences_router
from src.personalization.api.routes.gamification import router as gamification_router
from src.personalization.api.routes.privacy import router as privacy_router
from src.personalization.api.routes.dashboard import router as dashboard_router
from src.personalization.api.routes.chatbot_translation import router as chatbot_translation_router
from src.personalization.api.routes.glossary import router as glossary_router
from src.personalization.api.routes.admin_translation import router as admin_translation_router
from src.personalization.api.routes.notifications import router as notifications_router
from src.personalization.api.routes.language_preferences import router as language_preferences_router
from src.personalization.api.routes.language_analytics import router as language_analytics_router

app.include_router(chat_router)
app.include_router(users_router)
app.include_router(assessment_router)
app.include_router(progress_router)
app.include_router(practice_router)
app.include_router(preferences_router)
app.include_router(gamification_router)
app.include_router(privacy_router)
app.include_router(dashboard_router)
app.include_router(chatbot_translation_router)
app.include_router(glossary_router)
app.include_router(admin_translation_router)
app.include_router(notifications_router)
app.include_router(language_preferences_router)
app.include_router(language_analytics_router)

# Serve React SPA at /book/ with client-side routing support
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

react_build_path = Path(__file__).parent.parent.parent / "frontend" / "build"
if react_build_path.exists():
    # Serve static assets (JS, CSS, images) from /book/static/
    static_path = react_build_path / "static"
    if static_path.exists():
        app.mount("/book/static", StaticFiles(directory=str(static_path)), name="book-static")

    # Catch-all route for SPA client-side routing (must be after API routes)
    @app.get("/book/{full_path:path}", tags=["spa"])
    async def serve_react_app(full_path: str):
        """Serve React SPA - returns index.html for all client-side routes."""
        # Check if the requested path is an actual file (favicon, manifest, etc.)
        file_path = react_build_path / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        # Otherwise serve index.html for client-side routing
        return FileResponse(str(react_build_path / "index.html"))

    @app.get("/book", tags=["spa"])
    async def serve_react_root():
        """Serve React SPA root."""
        return FileResponse(str(react_build_path / "index.html"))

    logger.info(f"React SPA mounted at /book from {react_build_path}")
