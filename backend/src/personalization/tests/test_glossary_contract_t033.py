"""
Contract Tests for Glossary API Endpoints (T033)

Tests the contract/interface of all glossary endpoints:
1. GET /api/v1/glossary - List terms
2. GET /api/v1/glossary/{term_id} - Get term
3. GET /api/v1/glossary/search - Search terms
4. GET /api/v1/glossary/categories - Get categories
5. POST /api/v1/glossary/feedback - Submit feedback
6. GET /api/v1/glossary/stats - Get statistics

Ensures:
- Correct HTTP methods
- Proper status codes
- Required response fields
- Parameter handling
- Error conditions
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4


class TestGlossaryListEndpoint:
    """Tests for GET /api/v1/glossary endpoint."""

    async def test_list_terms_success(self, client: AsyncClient):
        """Should list glossary terms with default pagination."""
        response = await client.get("/api/v1/glossary")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_list_terms_with_category_filter(self, client: AsyncClient):
        """Should filter terms by category."""
        response = await client.get("/api/v1/glossary?category=robotics")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_list_terms_with_pagination(self, client: AsyncClient):
        """Should support pagination with limit and offset."""
        response = await client.get("/api/v1/glossary?limit=10&offset=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    async def test_list_terms_limit_validation(self, client: AsyncClient):
        """Should validate limit parameter (1-200)."""
        # Invalid limit
        response = await client.get("/api/v1/glossary?limit=500")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGlossaryGetTermEndpoint:
    """Tests for GET /api/v1/glossary/{term_id} endpoint."""

    async def test_get_term_success(self, client: AsyncClient):
        """Should get specific term by ID."""
        term_id = "ROS Node"
        response = await client.get(f"/api/v1/glossary/{term_id}")

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "english_term" in data
            assert "urdu_translation" in data
            assert "category" in data

    async def test_get_term_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent term."""
        response = await client.get("/api/v1/glossary/NonExistentTerm")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data

    async def test_get_term_response_schema(self, client: AsyncClient):
        """Should return complete term schema."""
        term_id = "Sensor"
        response = await client.get(f"/api/v1/glossary/{term_id}")

        if response.status_code == status.HTTP_200_OK:
            data = response.json()

            # Required fields
            required_fields = [
                'id', 'english_term', 'urdu_translation',
                'pronunciation_transliterated', 'definition_english',
                'definition_urdu', 'category', 'status'
            ]

            for field in required_fields:
                assert field in data, f"Missing required field: {field}"


class TestGlossarySearchEndpoint:
    """Tests for GET /api/v1/glossary/search endpoint."""

    async def test_search_terms_english(self, client: AsyncClient):
        """Should search terms in English."""
        response = await client.get("/api/v1/glossary/search?q=sensor&language=english")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_search_terms_urdu(self, client: AsyncClient):
        """Should search terms in Urdu."""
        response = await client.get("/api/v1/glossary/search?q=سینسر&language=urdu")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_search_missing_query(self, client: AsyncClient):
        """Should require search query."""
        response = await client.get("/api/v1/glossary/search")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_search_empty_query(self, client: AsyncClient):
        """Should validate non-empty query."""
        response = await client.get("/api/v1/glossary/search?q=&language=english")

        # Should fail validation or return empty list
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_200_OK
        ]

    async def test_search_with_category_filter(self, client: AsyncClient):
        """Should filter search results by category."""
        response = await client.get(
            "/api/v1/glossary/search?q=sensor&language=english&category=robotics"
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_search_language_validation(self, client: AsyncClient):
        """Should validate language parameter."""
        response = await client.get("/api/v1/glossary/search?q=test&language=invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGlossaryCategoriesEndpoint:
    """Tests for GET /api/v1/glossary/categories endpoint."""

    async def test_get_categories_success(self, client: AsyncClient):
        """Should list all categories."""
        response = await client.get("/api/v1/glossary/categories")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(isinstance(cat, str) for cat in data)

    async def test_categories_response_format(self, client: AsyncClient):
        """Should return simple list of category strings."""
        response = await client.get("/api/v1/glossary/categories")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should be a simple list, not dict
        assert isinstance(data, list)

        # Categories should be strings
        for category in data:
            assert isinstance(category, str)
            assert len(category) > 0


class TestGlossaryFeedbackEndpoint:
    """Tests for POST /api/v1/glossary/feedback endpoint."""

    async def test_feedback_requires_authentication(self, client: AsyncClient):
        """Should require authentication for feedback submission."""
        response = await client.post(
            "/api/v1/glossary/feedback",
            params={
                "feedback_type": "suggestion",
                "content": "This is a good suggestion for improvement"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_feedback_invalid_type(self, client: AsyncClient, auth_headers: dict):
        """Should validate feedback type."""
        response = await client.post(
            "/api/v1/glossary/feedback",
            params={
                "feedback_type": "invalid_type",
                "content": "This is feedback content"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_feedback_short_content(self, client: AsyncClient, auth_headers: dict):
        """Should validate minimum content length."""
        response = await client.post(
            "/api/v1/glossary/feedback",
            params={
                "feedback_type": "suggestion",
                "content": "short"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_feedback_long_content(self, client: AsyncClient, auth_headers: dict):
        """Should validate maximum content length."""
        long_content = "a" * 501

        response = await client.post(
            "/api/v1/glossary/feedback",
            params={
                "feedback_type": "suggestion",
                "content": long_content
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_feedback_suggestion_type(self, client: AsyncClient, auth_headers: dict):
        """Should accept suggestion feedback type."""
        response = await client.post(
            "/api/v1/glossary/feedback",
            params={
                "feedback_type": "suggestion",
                "content": "This is a good suggestion for improvement"
            },
            headers=auth_headers
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED
        ]

        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            data = response.json()
            assert data.get("status") == "success"
            assert "feedback_id" in data

    async def test_feedback_correction_type(self, client: AsyncClient, auth_headers: dict):
        """Should accept correction feedback type."""
        response = await client.post(
            "/api/v1/glossary/feedback",
            params={
                "feedback_type": "correction",
                "content": "The definition contains an error that should be fixed"
            },
            headers=auth_headers
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED
        ]

    async def test_feedback_new_term_type(self, client: AsyncClient, auth_headers: dict):
        """Should accept new_term feedback type."""
        response = await client.post(
            "/api/v1/glossary/feedback",
            params={
                "feedback_type": "new_term",
                "content": "Please add this important robotics term",
                "suggested_term": "Quadrupedal Gait"
            },
            headers=auth_headers
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED
        ]


class TestGlossaryStatsEndpoint:
    """Tests for GET /api/v1/glossary/stats endpoint."""

    async def test_get_stats_success(self, client: AsyncClient):
        """Should get glossary statistics."""
        response = await client.get("/api/v1/glossary/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should have required fields
        assert "total_terms" in data
        assert "total_categories" in data
        assert "categories" in data
        assert "status" in data

        # Types should be correct
        assert isinstance(data["total_terms"], int)
        assert isinstance(data["total_categories"], int)
        assert isinstance(data["categories"], list)
        assert isinstance(data["status"], str)

    async def test_stats_response_format(self, client: AsyncClient):
        """Should return properly formatted statistics."""
        response = await client.get("/api/v1/glossary/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Statistics should be non-negative
        assert data["total_terms"] >= 0
        assert data["total_categories"] >= 0

        # Categories should match count
        assert data["total_categories"] == len(data["categories"])
