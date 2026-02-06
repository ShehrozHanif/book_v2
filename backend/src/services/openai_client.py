"""OpenAI API client for embeddings and chat completions."""

import logging
import os
from typing import List, Dict, Optional
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI embeddings and LLM interactions."""

    def __init__(self):
        """Initialize OpenAI client with environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")

        self.client = AsyncOpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text string using OpenAI embeddings.

        Args:
            text: Text to embed

        Returns:
            List of 1536 floats representing the embedding vector

        Raises:
            ValueError: If text is empty
            Exception: If OpenAI API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response.data[0].embedding
            logger.debug(f"Embedded text of length {len(text)}")
            return embedding

        except Exception as e:
            logger.error(f"Failed to embed text: {str(e)}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embed multiple texts using OpenAI embeddings.

        Args:
            texts: List of texts to embed (max 50 per request for rate limiting)

        Returns:
            List of embedding vectors, one per input text

        Raises:
            ValueError: If texts list is empty or contains empty strings
            Exception: If OpenAI API call fails
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        # Validate all texts are non-empty
        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise ValueError(f"Text at index {i} is empty or whitespace-only")

        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )

            # Sort by index to ensure correct ordering
            embeddings = sorted(response.data, key=lambda x: x.index)
            embedding_vectors = [item.embedding for item in embeddings]

            logger.debug(f"Batch embedded {len(texts)} texts")
            return embedding_vectors

        except Exception as e:
            logger.error(f"Failed to batch embed texts: {str(e)}")
            raise

    async def generate_response(
        self,
        query: str,
        context_passages: List[str],
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate a response using GPT with RAG context and conversation history.

        Args:
            query: User's question
            context_passages: List of relevant textbook passages retrieved by RAG
            conversation_history: Optional list of previous messages in format:
                [
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."},
                    ...
                ]
            temperature: Sampling temperature (0.0-2.0, default: 0.7)
            max_tokens: Maximum response length (default: 500)

        Returns:
            str: Generated response from the LLM

        Raises:
            ValueError: If query or context_passages are invalid
            Exception: If OpenAI API call fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not context_passages:
            logger.warning("No context passages provided for generation")

        try:
            # CRITICAL FIX #3: Check context strength and adapt prompt
            strong_context = any(
                len(passage) > 200 and 'not available' not in passage.lower()
                for passage in context_passages
            ) if context_passages else False

            # CRITICAL FIX #4: Check if passages contain chapter-specific headers
            # Even if content is mostly code, if it says "Chapter X -" it's valid content for that chapter
            has_chapter_header = any(
                f"Chapter {i} -" in passage or f"Chapter {i}:" in passage
                for passage in context_passages
                for i in range(1, 23)
            ) if context_passages else False

            if has_chapter_header or strong_context:
                # Chapter-specific content or strong context - use comprehensive prompt
                system_prompt = (
                    "You are a helpful educational assistant for a Humanoid Robotics textbook. "
                    "Use the provided passages to answer the user's question comprehensively. "
                    "Include information from all content types in the passages: text, code examples, diagrams, and technical sections. "
                    "Always cite your sources by chapter/module/section from the passages. "
                    "Synthesize the information to provide a complete answer about the topic."
                )
            else:
                # Weak context - USE the passages but acknowledge they may be limited
                # CRITICAL FIX #6: Make weak context prompts more directive about using passages
                system_prompt = (
                    "You are a helpful educational assistant for a Humanoid Robotics textbook. "
                    "Use the provided passages to answer the user's question. "
                    "The passages may be limited or incomplete, but extract and synthesize all available information. "
                    "Always cite the source (chapter/module) from the passages. "
                    "Provide a helpful answer based on whatever information is available in the passages."
                )

            # Format context passages
            context_text = ""
            if context_passages:
                formatted_passages = [
                    f"[PASSAGE]\n{passage}\n[/PASSAGE]"
                    for passage in context_passages
                ]
                context_text = "\n\n".join(formatted_passages)

            # Build messages list
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Build user message with context
            user_message = f"Question: {query}"
            if context_text:
                # CRITICAL FIX #5: Add explicit instruction that passages should be treated as valid content
                # This helps LLM recognize code-heavy passages from target chapters
                user_message = f"Provided passages:\n{context_text}\n\nPlease answer based on the passages above. If the passages are from the requested chapter or topic, use their content (including code examples and technical sections) as valid information for your answer.\n\n{user_message}"

            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            generated_text = response.choices[0].message.content
            logger.debug(f"Generated response of length {len(generated_text)}")
            return generated_text

        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise

    async def get_model_info(self) -> Dict:
        """Get information about configured models.

        Returns:
            Dict with embedding_model and chat_model names

        Raises:
            Exception: If model retrieval fails
        """
        try:
            return {
                "embedding_model": self.embedding_model,
                "chat_model": self.chat_model,
                "embedding_dimension": 1536
            }
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            raise


# Lazy singleton instance
_openai_service_instance = None


def get_openai_service():
    """Get or create the OpenAI service singleton.

    Returns:
        OpenAIService: Initialized service instance
    """
    global _openai_service_instance
    if _openai_service_instance is None:
        _openai_service_instance = OpenAIService()
    return _openai_service_instance
