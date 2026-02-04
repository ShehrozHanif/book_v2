"""Integration tests for /chat/embed endpoint."""

import pytest
import json
from httpx import AsyncClient
from src.main import app
from tests.fixtures.sample_textbook import SAMPLE_CHUNKS, MINIMAL_CHUNKS


class TestEmbedEndpoint:
    """Test suite for the /api/v1/chat/embed endpoint."""

    @pytest.mark.asyncio
    async def test_embed_single_chunk(self):
        """Test embedding a single textbook chunk."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "chunks": [
                    {
                        "content": "ROS 2 is a robotics middleware that enables flexible robot software.",
                        "module": "Module 1",
                        "chapter": "Chapter 1",
                        "section": "1.1 Introduction",
                    }
                ]
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["chunks_embedded"] == 1
            assert data["collection"] == "textbook_chunks"
            assert "Successfully embedded" in data["message"]

    @pytest.mark.asyncio
    async def test_embed_multiple_chunks(self):
        """Test embedding multiple textbook chunks at once."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "chunks": MINIMAL_CHUNKS
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["chunks_embedded"] == len(MINIMAL_CHUNKS)
            assert data["collection"] == "textbook_chunks"

    @pytest.mark.asyncio
    async def test_embed_with_custom_collection(self):
        """Test embedding with a custom collection name."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "chunks": [
                    {
                        "content": "Test content for custom collection.",
                        "module": "Module 1",
                        "chapter": "Chapter 1",
                        "section": "1.0 Test",
                    }
                ],
                "collection_name": "custom_textbook"
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            # Note: collection_name in request doesn't change the actual Qdrant collection
            # used (still defaults to environment variable), but is returned in response
            assert response.status_code == 200
            data = response.json()
            assert data["collection"] == "custom_textbook"

    @pytest.mark.asyncio
    async def test_embed_empty_chunks_returns_400(self):
        """Test that empty chunks list returns 400 Bad Request."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {"chunks": []}

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 400
            data = response.json()
            assert "error" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_embed_missing_required_field_returns_422(self):
        """Test that missing required fields returns 422 Unprocessable Entity."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Missing 'content' field
            payload = {
                "chunks": [
                    {
                        "module": "Module 1",
                        "chapter": "Chapter 1",
                        "section": "1.1",
                    }
                ]
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_embed_invalid_chunk_format_returns_422(self):
        """Test that invalid chunk format returns 422."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Content is too short (min_length=10)
            payload = {
                "chunks": [
                    {
                        "content": "short",  # Less than 10 chars
                        "module": "Module 1",
                        "chapter": "Chapter 1",
                        "section": "1.1",
                    }
                ]
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_embed_content_too_long_returns_422(self):
        """Test that content exceeding max_length returns 422."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Content exceeds max_length=5000
            long_content = "x" * 5001

            payload = {
                "chunks": [
                    {
                        "content": long_content,
                        "module": "Module 1",
                        "chapter": "Chapter 1",
                        "section": "1.1",
                    }
                ]
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_embed_response_format(self):
        """Test that response conforms to EmbedResponse schema."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "chunks": [
                    {
                        "content": "ROS 2 enables flexible robot software development across platforms.",
                        "module": "Module 1",
                        "chapter": "Chapter 1: Fundamentals",
                        "section": "1.1 Introduction",
                    }
                ]
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 200
            data = response.json()

            # Verify response has all required fields
            assert "success" in data
            assert "chunks_embedded" in data
            assert "collection" in data
            assert "message" in data

            # Verify field types
            assert isinstance(data["success"], bool)
            assert isinstance(data["chunks_embedded"], int)
            assert isinstance(data["collection"], str)
            assert isinstance(data["message"], str)

    @pytest.mark.asyncio
    async def test_embed_metadata_preserved(self):
        """Test that chunk metadata (module, chapter, section) is preserved."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "chunks": [
                    {
                        "content": "Test content about humanoid robotics and kinematics.",
                        "module": "Module 2: Advanced Topics",
                        "chapter": "Chapter 5: Kinematics",
                        "section": "5.1 Forward Kinematics",
                    }
                ]
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            # Note: Response doesn't return the vectors/metadata, but it should be
            # stored in Qdrant with the payload. This is verified in Qdrant retrieval tests.

    @pytest.mark.asyncio
    async def test_embed_handles_special_characters(self):
        """Test that content with special characters is handled correctly."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "chunks": [
                    {
                        "content": "ROS 2 uses pub-sub pattern! It's flexible & robust for robotics (e.g., humanoids).",
                        "module": "Module 1",
                        "chapter": "Chapter 1",
                        "section": "1.1 Intro",
                    }
                ]
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_embed_large_batch(self):
        """Test embedding a large batch of chunks."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Use the full sample chunks
            payload = {
                "chunks": SAMPLE_CHUNKS
            }

            response = await client.post("/api/v1/chat/embed", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["chunks_embedded"] == len(SAMPLE_CHUNKS)
