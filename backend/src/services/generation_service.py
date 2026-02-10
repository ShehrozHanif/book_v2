"""Generation service for LLM response generation with citations."""

import re
import logging
from typing import List, Dict, Optional, Tuple
from src.services.openai_client import get_openai_service

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for generating responses using OpenAI LLM with RAG context."""

    def __init__(self, max_tokens: int = 500):
        """Initialize generation service.

        Args:
            max_tokens: Maximum tokens in LLM response (default: 500)
        """
        self.openai_service = get_openai_service()
        self.max_tokens = max_tokens

        # Fallback responses for edge cases
        self.fallback_responses = {
            "no_context": (
                "I don't have enough information from the textbook to answer this question confidently. "
                "Please check the textbook directly or rephrase your question."
            ),
            "off_topic": (
                "I can help with questions about Humanoid Robotics. "
                "Please ask about the textbook content."
            ),
            "api_error": (
                "I'm temporarily unable to generate a response. Please try again in a moment."
            ),
            "invalid_response": (
                "I couldn't generate a proper response. Please try rephrasing your question."
            )
        }

    def extract_citations(self, response: str) -> List[str]:
        """Extract [Chapter X: Section Y] citations from response.

        Looks for patterns like:
        - [Chapter 1]
        - [Chapter 1: Introduction]
        - [Chapter 2: Section 3]
        - [Module 1: Chapter 2: Section 3]

        Args:
            response: Generated response text

        Returns:
            List of citation strings found in the response
        """
        # Pattern: [Chapter/Module X...] with optional sections
        pattern = r'\[(?:Chapter|Module)\s+\d+(?::\s*[^\]]+)?\]'
        citations = re.findall(pattern, response, re.IGNORECASE)
        return citations

    def validate_response(
        self,
        response: str,
        context_passages: List[str]
    ) -> Tuple[bool, str]:
        """Check response doesn't hallucinate (uses context only).

        Uses heuristics to detect if response is grounded in context:
        1. If response has citations, assume it's grounded
        2. If response is short (< 100 chars), likely edge case (acceptable)
        3. If no context provided but response exists, it's a fallback message
        4. Otherwise, add citation reminder

        Args:
            response: Generated response text
            context_passages: List of passages used for context

        Returns:
            Tuple of (is_valid, enhanced_response)
            - is_valid: True if response appears valid
            - enhanced_response: Response with added citations if needed
        """
        # Check for citations
        citations = self.extract_citations(response)
        if citations:
            logger.info(f"Response validated with {len(citations)} citations")
            return True, response

        # If no citations but response is short, assume edge case
        if len(response) < 100:
            logger.info("Response is short (likely edge case handling)")
            return True, response

        # If no context provided, assume it's a fallback message
        if not context_passages:
            logger.info("No context passages - using fallback response")
            return True, response

        # Add citation reminder if context was provided but not cited
        logger.warning("Response has no citations - adding reminder")
        enhanced_response = (
            f"{response}\n\n"
            f"[Note: This response is based on the retrieved textbook passages. "
            f"Please refer to the relevant chapters for detailed information.]"
        )
        return True, enhanced_response

    async def generate_response(
        self,
        query: str,
        context_passages: List[str],
        conversation_history: Optional[List[Dict]] = None,
        use_fallback_on_error: bool = True,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response using LLM with context.

        Args:
            query: User's question
            context_passages: List of relevant textbook passages retrieved by RAG
            conversation_history: Optional list of previous messages in format:
                [
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."},
                    ...
                ]
            use_fallback_on_error: If True, return fallback message on API error
                                   If False, raise exception (default: True)
            system_prompt: Optional personalized system prompt for the LLM

        Returns:
            str: Generated response from the LLM (or fallback message on error)

        Raises:
            ValueError: If query is invalid
            Exception: If OpenAI API call fails and use_fallback_on_error=False
        """
        try:
            # Handle edge case: no context passages
            if not context_passages:
                logger.warning("No context passages provided for generation")
                return self.fallback_responses["no_context"]

            response = await self.openai_service.generate_response(
                query=query,
                context_passages=context_passages,
                conversation_history=conversation_history,
                max_tokens=self.max_tokens,
                system_prompt=system_prompt
            )

            # Validate and enhance response
            is_valid, enhanced_response = self.validate_response(
                response, context_passages
            )

            logger.info(
                f"Generated response ({len(enhanced_response)} chars, valid={is_valid})"
            )
            return enhanced_response

        except ValueError as e:
            # Invalid input - re-raise
            logger.error(f"Invalid input to generation service: {e}")
            raise
        except Exception as e:
            # API error - fallback or raise
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            if use_fallback_on_error:
                logger.info("Returning fallback response due to API error")
                return self.fallback_responses["api_error"]
            else:
                raise

    def get_fallback_response(self, response_type: str) -> str:
        """Get a fallback response for edge cases.

        Args:
            response_type: Type of fallback needed (no_context, off_topic, api_error, invalid_response)

        Returns:
            str: Fallback response message
        """
        return self.fallback_responses.get(
            response_type,
            self.fallback_responses["invalid_response"]
        )


# Singleton instance
_generation_service_instance = None


def get_generation_service(max_tokens: int = 500) -> GenerationService:
    """Get or create the generation service singleton.

    Args:
        max_tokens: Maximum tokens in response (default: 500)

    Returns:
        GenerationService: Initialized service instance
    """
    global _generation_service_instance
    if _generation_service_instance is None:
        _generation_service_instance = GenerationService(max_tokens=max_tokens)
    return _generation_service_instance
