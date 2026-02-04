"""Personalization API routes."""

from src.personalization.api.routes.users import router as users_router
from src.personalization.api.routes.assessment import router as assessment_router
from src.personalization.api.routes.progress import router as progress_router

__all__ = ["users_router", "assessment_router", "progress_router"]
