"""Security service for prompt injection detection and off-topic query filtering."""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class SecurityService:
    """Detects injection attempts and off-topic queries."""

    def __init__(self):
        """Initialize security service with injection patterns."""
        # Common prompt injection patterns
        self.injection_patterns = [
            r"ignore\s+previous",
            r"forget\s+about",
            r"disregard\s+previous",
            r"system\s+prompt",
            r"jailbreak",
            r"bypass.*filter",
            r"disregard.*instruction",
            r"ignore\s+the\s+above",
            r"forget\s+your\s+role",
            r"act\s+as\s+(?!a\s+helpful)",  # "act as" anything other than helpful
            r"new\s+instructions?:",
            r"override\s+your",
            r"you\s+are\s+now",
            r"from\s+now\s+on",
        ]

        # SQL injection patterns (defensive layer)
        self.sql_injection_patterns = [
            r"(?i)\b(DROP|DELETE|TRUNCATE|EXEC|EXECUTE)\s+(TABLE|DATABASE|FROM)",
            r"(?i);?\s*DROP\s+TABLE",
            r"(?i)UNION\s+SELECT",
            r"(?i)--\s*$",  # SQL comments at end of line
            r"(?i)/\*.*\*/",  # SQL block comments
            r"(?i)'\s*OR\s*'",  # OR injection pattern
            r"(?i)'\s*=\s*'",  # Equality injection pattern
            r"(?i)WHERE\s+\d\s*=\s*\d",  # WHERE 1=1 pattern
        ]

    def detect_injection_attempt(self, query: str) -> Tuple[bool, str]:
        """Detect prompt injection attempts.

        Args:
            query: User query to analyze

        Returns:
            Tuple of (is_injection, pattern_matched)
            - is_injection: True if injection detected, False otherwise
            - pattern_matched: The pattern that matched (empty string if no match)
        """
        if not query:
            return False, ""

        query_lower = query.lower()

        # Check prompt injection patterns
        for pattern in self.injection_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                logger.warning(
                    f"Potential prompt injection detected: pattern='{pattern}', "
                    f"query_snippet='{query[:50]}...'"
                )
                return True, pattern

        # Check SQL injection patterns (defensive)
        for pattern in self.sql_injection_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                logger.warning(
                    f"Potential SQL injection detected: pattern='{pattern}', "
                    f"query_snippet='{query[:50]}...'"
                )
                return True, pattern

        return False, ""

    def detect_off_topic(
        self,
        query: str,
        retrieved_passages: List[str],
        relevance_scores: List[float],
        threshold: float = 0.3
    ) -> Tuple[bool, float]:
        """Detect if query is off-topic based on retrieved passages.

        Uses relevance scores from vector similarity search to determine
        if the query is related to textbook content.

        Args:
            query: User query
            retrieved_passages: Passages retrieved from vector DB
            relevance_scores: Relevance scores for passages (higher = more relevant)
            threshold: Minimum relevance threshold (default: 0.3)

        Returns:
            Tuple of (is_off_topic, best_score)
            - is_off_topic: True if off-topic (no relevant passages), False if on-topic
            - best_score: Best relevance score found (0.0 if none)
        """
        # If no passages or scores, assume off-topic
        if not relevance_scores:
            logger.info(f"No relevance scores for query: '{query[:50]}...'")
            return True, 0.0

        best_score = max(relevance_scores)

        # If best score is below threshold, it's off-topic
        is_off_topic = best_score < threshold

        if is_off_topic:
            logger.info(
                f"Off-topic query detected: best_score={best_score:.3f}, "
                f"threshold={threshold}, query='{query[:50]}...'"
            )
        else:
            logger.debug(
                f"On-topic query: best_score={best_score:.3f}, "
                f"query='{query[:50]}...'"
            )

        return is_off_topic, best_score

    def sanitize_query(self, query: str) -> str:
        """Remove potentially harmful content from query.

        Applies basic sanitization to prevent:
        - SQL injection attempts
        - Excessive length
        - Null bytes and control characters

        Args:
            query: Raw user query

        Returns:
            Sanitized query string
        """
        if not query:
            return ""

        # Remove null bytes
        sanitized = query.replace('\x00', '')

        # Remove other control characters (except newlines and tabs)
        sanitized = ''.join(
            char for char in sanitized
            if char.isprintable() or char in ['\n', '\t', ' ']
        )

        # Remove SQL injection keywords (defensive layer)
        # Only remove when followed by SQL syntax patterns
        sql_patterns = [
            (r"\bDROP\s+TABLE\b", ""),
            (r"\bDELETE\s+FROM\b", ""),
            (r"\bTRUNCATE\s+TABLE\b", ""),
            (r"\bUNION\s+SELECT\b", ""),
            (r";", " "),  # Remove semicolons (statement terminators)
        ]
        for pattern, replacement in sql_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # Limit to maximum length (prevent DoS)
        max_length = 5000
        if len(sanitized) > max_length:
            logger.warning(
                f"Query truncated from {len(sanitized)} to {max_length} chars"
            )
            sanitized = sanitized[:max_length]

        # Strip whitespace
        sanitized = sanitized.strip()

        return sanitized

    def validate_query(self, query: str) -> Tuple[bool, str]:
        """Comprehensive query validation.

        Performs all security checks in one method for convenience.

        Args:
            query: User query to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if query passes all checks, False otherwise
            - error_message: Descriptive error message (empty if valid)
        """
        # Check empty
        if not query or not query.strip():
            return False, "Query cannot be empty"

        # Check length
        if len(query) > 5000:
            return False, "Query exceeds maximum length of 5000 characters"

        # Check for injection attempts
        is_injection, pattern = self.detect_injection_attempt(query)
        if is_injection:
            return False, "Query contains potentially malicious patterns"

        return True, ""


# Singleton instance
_security_service_instance = None


def get_security_service() -> SecurityService:
    """Get or create the security service singleton.

    Returns:
        SecurityService: Initialized service instance
    """
    global _security_service_instance
    if _security_service_instance is None:
        _security_service_instance = SecurityService()
    return _security_service_instance
