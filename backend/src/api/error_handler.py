"""Error handling and exception handlers for API."""

import logging
import traceback
from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from src.models.schemas import ErrorResponse

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: str = None,
    ):
        """
        Initialize API exception.

        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class ValidationException(APIException):
    """Exception for validation errors."""

    def __init__(self, message: str, details: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class NotFoundException(APIException):
    """Exception for not found errors."""

    def __init__(self, message: str, details: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class UnauthorizedException(APIException):
    """Exception for authentication errors."""

    def __init__(self, message: str = "Unauthorized", details: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class ForbiddenException(APIException):
    """Exception for authorization errors."""

    def __init__(self, message: str = "Forbidden", details: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class RateLimitException(APIException):
    """Exception for rate limiting."""

    def __init__(self, message: str = "Rate limit exceeded", details: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handle custom API exceptions.

    Args:
        request: FastAPI request object
        exc: APIException instance

    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"API Exception - Status: {exc.status_code}, Message: {exc.message}, Details: {exc.details}"
    )

    error_response = ErrorResponse(
        error=exc.message,
        details=exc.details,
        status_code=exc.status_code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: Validation error instance

    Returns:
        JSONResponse with validation error details
    """
    logger.warning(f"Validation error: {exc}")

    # Extract field-level errors
    errors = []
    if hasattr(exc, "errors"):
        for error in exc.errors():
            field = ".".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "validation error")
            errors.append(f"{field}: {msg}")

    details = "; ".join(errors) if errors else "Request validation failed"

    error_response = ErrorResponse(
        error="Validation error",
        details=details,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"Unhandled exception - Type: {type(exc).__name__}, Message: {str(exc)}",
        exc_info=exc,
    )

    # In production, don't expose internal error details
    is_development = False  # This would be pulled from settings in production
    details = str(exc) if is_development else "An internal error occurred"

    error_response = ErrorResponse(
        error="Internal server error",
        details=details,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 404 not found errors.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with 404 error
    """
    logger.warning(f"Not found - Path: {request.url.path}")

    error_response = ErrorResponse(
        error="Not found",
        details=f"Endpoint '{request.url.path}' not found",
        status_code=status.HTTP_404_NOT_FOUND,
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_response.model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Exception handlers registered successfully")
