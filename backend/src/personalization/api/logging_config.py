"""
Logging configuration for chatbot translation feature.

Provides:
1. Language event logging
2. User preference change tracking
3. Authentication attempt logging
4. Error logging with context
"""

import logging
from typing import Optional
from datetime import datetime
from uuid import UUID
import json


class LanguageEventLogger:
    """Logger for language-related events."""

    def __init__(self, name: str = "chatbot_translation"):
        """Initialize language event logger."""
        self.logger = logging.getLogger(name)

    def log_language_preference_set(
        self,
        user_id: UUID,
        language: str,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Log when user sets language preference.

        Args:
            user_id: User ID
            language: Language set (english, urdu)
            success: Whether operation succeeded
            error: Error message if failed
        """
        if success:
            self.logger.info(
                f"Language preference set",
                extra={
                    "event_type": "language_preference_set",
                    "user_id": str(user_id),
                    "language": language,
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        else:
            self.logger.warning(
                f"Failed to set language preference",
                extra={
                    "event_type": "language_preference_set",
                    "user_id": str(user_id),
                    "language": language,
                    "status": "failed",
                    "error": error,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    def log_language_preference_retrieved(
        self,
        user_id: UUID,
        language: str,
        source: str = "database"  # database, cache, default
    ) -> None:
        """
        Log when user's language preference is retrieved.

        Args:
            user_id: User ID
            language: Language retrieved
            source: Source of preference (database, cache, default)
        """
        self.logger.debug(
            f"Language preference retrieved",
            extra={
                "event_type": "language_preference_retrieved",
                "user_id": str(user_id),
                "language": language,
                "source": source,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_urdu_request(
        self,
        user_id: Optional[str],
        is_authenticated: bool,
        template_key: str,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Log Urdu content requests (authentication gating).

        Args:
            user_id: User ID if authenticated
            is_authenticated: Whether user is authenticated
            template_key: Template requested
            success: Whether request succeeded
            error: Error message if failed
        """
        if success:
            self.logger.info(
                f"Urdu content requested (authenticated: {is_authenticated})",
                extra={
                    "event_type": "urdu_request",
                    "user_id": user_id,
                    "authenticated": is_authenticated,
                    "template_key": template_key,
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        else:
            self.logger.warning(
                f"Urdu request failed",
                extra={
                    "event_type": "urdu_request",
                    "user_id": user_id,
                    "authenticated": is_authenticated,
                    "template_key": template_key,
                    "status": "failed",
                    "error": error,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    def log_translation_fallback(
        self,
        user_id: Optional[str],
        template_key: str,
        requested_language: str,
        fallback_language: str = "english"
    ) -> None:
        """
        Log when translation is not available and fallback is used.

        Args:
            user_id: User ID
            template_key: Template key
            requested_language: Language originally requested
            fallback_language: Language used as fallback
        """
        self.logger.info(
            f"Translation fallback used",
            extra={
                "event_type": "translation_fallback",
                "user_id": user_id,
                "template_key": template_key,
                "requested_language": requested_language,
                "fallback_language": fallback_language,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_authentication_failure(
        self,
        reason: str,
        language: str,
        template_key: Optional[str] = None
    ) -> None:
        """
        Log authentication failures (e.g., guest trying to access Urdu).

        Args:
            reason: Reason for failure
            language: Language requested
            template_key: Template requested if applicable
        """
        self.logger.warning(
            f"Authentication failure: {reason}",
            extra={
                "event_type": "authentication_failure",
                "reason": reason,
                "language": language,
                "template_key": template_key,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_validation_error(
        self,
        error_type: str,
        user_id: Optional[str],
        details: dict
    ) -> None:
        """
        Log validation errors.

        Args:
            error_type: Type of validation error
            user_id: User ID if available
            details: Error details
        """
        self.logger.warning(
            f"Validation error: {error_type}",
            extra={
                "event_type": "validation_error",
                "error_type": error_type,
                "user_id": user_id,
                "details": json.dumps(details, default=str),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_api_error(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        user_id: Optional[str],
        error: str
    ) -> None:
        """
        Log API errors.

        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            user_id: User ID if available
            error: Error message
        """
        log_level = logging.ERROR if status_code >= 500 else logging.WARNING

        self.logger.log(
            log_level,
            f"API error: {method} {endpoint} ({status_code})",
            extra={
                "event_type": "api_error",
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "user_id": user_id,
                "error": error,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_glossary_search(
        self,
        query: str,
        language: str,
        result_count: int,
        search_time_ms: float
    ) -> None:
        """
        Log glossary search events.

        Args:
            query: Search query
            language: Search language
            result_count: Number of results
            search_time_ms: Search duration in milliseconds
        """
        self.logger.debug(
            f"Glossary search",
            extra={
                "event_type": "glossary_search",
                "query": query,
                "language": language,
                "result_count": result_count,
                "search_time_ms": search_time_ms,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_template_access(
        self,
        template_key: str,
        language: str,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log template access for analytics.

        Args:
            template_key: Template accessed
            language: Language requested
            user_id: User ID if available
        """
        self.logger.debug(
            f"Template accessed",
            extra={
                "event_type": "template_access",
                "template_key": template_key,
                "language": language,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


# Global logger instance
language_logger = LanguageEventLogger()


# Convenience functions
def log_urdu_request(
    user_id: Optional[str],
    is_authenticated: bool,
    template_key: str
) -> None:
    """Log Urdu content request."""
    language_logger.log_urdu_request(
        user_id, is_authenticated, template_key
    )


def log_authentication_failure(
    reason: str,
    language: str
) -> None:
    """Log authentication failure."""
    language_logger.log_authentication_failure(reason, language)


def log_language_preference_set(
    user_id: UUID,
    language: str,
    success: bool = True
) -> None:
    """Log language preference change."""
    language_logger.log_language_preference_set(user_id, language, success)


def log_translation_fallback(
    user_id: Optional[str],
    template_key: str,
    requested_language: str
) -> None:
    """Log translation fallback."""
    language_logger.log_translation_fallback(
        user_id, template_key, requested_language
    )


# Additional logging for T065 - Comprehensive Operations Logging

def log_admin_operation(admin_id: str, operation: str, resource: str, resource_id: int, success: bool = True):
    """Log admin operations."""
    logger = logging.getLogger("admin_operations")
    level = logging.INFO if success else logging.WARNING
    logger.log(
        level,
        f"Admin {operation}: {resource} #{resource_id}",
        extra={
            "event_type": "admin_operation",
            "admin_id": admin_id,
            "operation": operation,
            "resource": resource,
            "resource_id": resource_id,
            "status": "success" if success else "failed",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


def log_performance_metric(operation: str, duration_ms: float, user_id: Optional[str] = None):
    """Log performance metrics."""
    logger = logging.getLogger("performance")
    logger.debug(
        f"{operation} completed in {duration_ms:.2f}ms",
        extra={
            "event_type": "performance_metric",
            "operation": operation,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


def log_database_operation(operation: str, table: str, success: bool = True, error: Optional[str] = None):
    """Log database operations."""
    logger = logging.getLogger("database")
    level = logging.DEBUG if success else logging.ERROR
    logger.log(
        level,
        f"Database {operation} on {table}",
        extra={
            "event_type": "database_operation",
            "operation": operation,
            "table": table,
            "status": "success" if success else "failed",
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
