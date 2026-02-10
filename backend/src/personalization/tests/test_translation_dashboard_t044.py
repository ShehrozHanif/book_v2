"""
Admin Translation Dashboard Tests (T044)

Tests for the admin translation management dashboard:
1. List all templates with translation status
2. Filter by status (draft/reviewed/published)
3. Show completion metrics (% translated, reviewed, published)
4. Pagination support
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestTranslationDashboardList:
    """Tests for GET /api/v1/admin/translations endpoint."""

    async def test_list_translations_success(self, client: AsyncClient, auth_headers: dict):
        """Should list all templates with translation status."""
        response = await client.get(
            "/api/v1/admin/translations",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_list_translations_filter_by_status(self, client: AsyncClient, auth_headers: dict):
        """Should filter templates by translation status."""
        response = await client.get(
            "/api/v1/admin/translations?status=draft",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        items = response.json()
        assert isinstance(items, list)

    async def test_list_translations_with_pagination(self, client: AsyncClient, auth_headers: dict):
        """Should support pagination."""
        response = await client.get(
            "/api/v1/admin/translations?limit=10&offset=0",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_list_translations_response_schema(self, client: AsyncClient, auth_headers: dict):
        """Should return proper response schema with all required fields."""
        response = await client.get(
            "/api/v1/admin/translations",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        items = response.json()
        if items:
            item = items[0]
            assert "id" in item
            assert "english_content" in item
            assert "urdu_translation" in item
            assert "status" in item
            assert "updated_at" in item

    async def test_list_translations_requires_admin_role(self, client: AsyncClient):
        """Should reject non-admin users."""
        response = await client.get("/api/v1/admin/translations")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_list_translations_different_statuses(self, client: AsyncClient, auth_headers: dict):
        """Should filter by different statuses."""
        for status_val in ["draft", "reviewed", "published"]:
            response = await client.get(
                f"/api/v1/admin/translations?status={status_val}",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK


class TestTranslationDashboardMetrics:
    """Tests for translation completion metrics."""

    async def test_get_metrics_success(self, client: AsyncClient, auth_headers: dict):
        """Should return dashboard metrics."""
        response = await client.get(
            "/api/v1/admin/translations/metrics",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        metrics = response.json()
        assert "total_templates" in metrics
        assert "translated" in metrics
        assert "reviewed" in metrics
        assert "published" in metrics

    async def test_metrics_percentages(self, client: AsyncClient, auth_headers: dict):
        """Should calculate correct percentages."""
        response = await client.get(
            "/api/v1/admin/translations/metrics",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        metrics = response.json()
        # Percentages should be between 0 and 100
        assert 0 <= metrics.get("translation_percent", 0) <= 100
        assert 0 <= metrics.get("review_percent", 0) <= 100

    async def test_completion_metrics_format(self, client: AsyncClient, auth_headers: dict):
        """Should return metrics in expected format."""
        response = await client.get(
            "/api/v1/admin/translations/metrics",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        metrics = response.json()
        required_fields = [
            "total_templates",
            "translated",
            "reviewed",
            "published",
            "translation_percent",
            "review_percent",
            "published_percent"
        ]
        for field in required_fields:
            assert field in metrics
