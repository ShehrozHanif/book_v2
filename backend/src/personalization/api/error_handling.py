"""
Comprehensive Error Handling (T064)

Centralized error handling for all endpoints:
- 401 Unauthorized for unauthenticated Urdu access
- 403 Forbidden for unauthorized admin actions
- 404 Not Found for missing resources
- 422 Unprocessable Entity for invalid inputs
- 500 Internal Server Error with graceful fallback to English
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict = None,
    ):
        """
        Initialize exception.

        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class UnauthorizedError(AppException):
    """User is not authenticated."""

    def __init__(self, message: str = "Authentication required", details: dict = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class ForbiddenError(AppException):
    """User lacks required permissions."""

    def __init__(self, message: str = "Permission denied", details: dict = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ValidationError(AppException):
    """Invalid input data."""

    def __init__(self, message: str = "Invalid input", details: dict = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class AuthenticationGateError(AppException):
    """User not authenticated for Urdu access."""

    def __init__(self, message: str = "Urdu access requires authentication"):
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED,
            {"language": "urdu", "fallback": "english"},
        )


class DatabaseError(AppException):
    """Database operation failed."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


def setup_error_handlers(app: FastAPI):
    """Set up error handlers for FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle application exceptions."""
        logger.error(
            f"Application error: {exc.message}",
            extra={"status_code": exc.status_code, "details": exc.details},
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "status_code": exc.status_code,
                "details": exc.details,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")

        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(x) for x in error["loc"][1:]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation failed",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "errors": errors,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors."""
        logger.error(f"Database error: {str(exc)}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database operation failed",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred. Please try again.",
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.error(
            f"Unexpected error: {type(exc).__name__}: {str(exc)}", exc_info=True
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred. Please try again.",
                "path": str(request.url.path),
            },
        )

    logger.info("Error handlers configured")


# Convenience functions for common errors

def raise_unauthorized_urdu():
    """Raise error for unauthenticated Urdu access."""
    raise AuthenticationGateError(
        "Guests cannot access Urdu content. Please login to continue."
    )


def raise_forbidden_admin(resource: str = "resource"):
    """Raise error for forbidden admin action."""
    raise ForbiddenError(
        f"You do not have permission to access {resource}. "
        "Contact an administrator if you need access."
    )


def raise_not_found(resource: str, identifier: str = None):
    """Raise error for missing resource."""
    message = f"{resource} not found"
    if identifier:
        message += f": {identifier}"
    raise NotFoundError(message, {"resource": resource, "identifier": identifier})


def raise_validation_error(field: str, message: str):
    """Raise validation error."""
    raise ValidationError(
        f"Invalid {field}: {message}", {"field": field, "issue": message}
    )


def raise_database_error(operation: str = None):
    """Raise database error."""
    message = "Database operation failed"
    if operation:
        message += f" ({operation})"
    raise DatabaseError(message)
