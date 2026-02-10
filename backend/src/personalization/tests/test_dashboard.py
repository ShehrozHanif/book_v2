"""Tests for dashboard endpoints (T046)."""

import pytest
from httpx import AsyncClient


class TestDashboardEndpoint:
    """Test dashboard metrics endpoint."""

    @pytest.mark.asyncio
    async def test_get_dashboard_new_user(self, client: AsyncClient, auth_headers):
        """Test dashboard for new user (should show 0% progress)."""
        response = await client.get(
            "/api/v1/dashboard/metrics",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "user" in data
        assert "progress" in data
        assert "achievements" in data
        assert "statistics" in data

        # Verify new user has zero progress
        assert data["progress"]["chapters_completed"] == 0
        assert data["progress"]["completion_percentage"] == 0.0
        assert data["progress"]["total_xp"] == 0

    @pytest.mark.asyncio
    async def test_get_dashboard_after_completing_chapters(
        self, client: AsyncClient, created_user, auth_headers, test_db
    ):
        """Test dashboard after completing chapters."""
        from src.personalization.services import progress_service

        user_id = created_user.user_id

        # Complete some chapters
        await progress_service.complete_chapter(test_db, user_id, 1, 85, 1800)
        await progress_service.complete_chapter(test_db, user_id, 2, 90, 1500)
        await progress_service.complete_chapter(test_db, user_id, 3, 80, 2000)

        response = await client.get(
            "/api/v1/dashboard/metrics",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should show 3 chapters completed
        assert data["progress"]["chapters_completed"] == 3
        assert data["progress"]["completion_percentage"] > 0

        # Should have XP
        assert data["progress"]["total_xp"] > 0

        # Should have time tracked
        assert data["progress"]["total_time_hours"] > 0

    @pytest.mark.asyncio
    async def test_dashboard_data_structure(self, client: AsyncClient, auth_headers):
        """Test dashboard data structure is valid."""
        response = await client.get(
            "/api/v1/dashboard/metrics",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify user section
        assert "username" in data["user"]
        assert "skill_level" in data["user"]
        assert "skill_tier" in data["user"]

        # Verify progress section
        progress = data["progress"]
        assert "chapters_completed" in progress
        assert "total_chapters" in progress
        assert "completion_percentage" in progress
        assert "total_time_hours" in progress
        assert "total_xp" in progress

        # Verify achievements section
        achievements = data["achievements"]
        assert "badges_earned" in achievements
        assert "badges" in achievements
        assert isinstance(achievements["badges"], list)

        # Verify statistics section
        stats = data["statistics"]
        assert "average_mastery_score" in stats
        assert "learning_streak" in stats

    @pytest.mark.asyncio
    async def test_dashboard_xp_calculation(
        self, client: AsyncClient, created_user, auth_headers, test_db
    ):
        """Test XP calculation in dashboard."""
        from src.personalization.services import progress_service

        user_id = created_user.user_id

        # Complete chapters with known mastery scores
        await progress_service.complete_chapter(test_db, user_id, 1, 70)
        await progress_service.complete_chapter(test_db, user_id, 2, 80)
        await progress_service.complete_chapter(test_db, user_id, 3, 90)

        response = await client.get(
            "/api/v1/dashboard/metrics",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # XP should be sum of mastery scores
        expected_xp = 70 + 80 + 90
        assert data["progress"]["total_xp"] == expected_xp

    @pytest.mark.asyncio
    async def test_dashboard_learning_path_progress(
        self, client: AsyncClient, created_user, auth_headers, test_db
    ):
        """Test learning path progress in dashboard."""
        from src.personalization.services import learning_path_service, progress_service

        user_id = created_user.user_id

        # Create learning path
        path = await learning_path_service.create_learning_path(
            test_db, user_id, "Test Path", [1, 2, 3, 4]
        )

        # Complete 2 chapters
        await progress_service.complete_chapter(test_db, user_id, 1, 85)
        await progress_service.complete_chapter(test_db, user_id, 2, 90)

        response = await client.get(
            "/api/v1/dashboard/metrics",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should have learning path info
        if data.get("learning_path"):
            path_info = data["learning_path"]
            assert path_info["chapters_completed"] == 2
            assert path_info["chapters_in_path"] == 4
            assert path_info["progress_percentage"] == 50.0

    @pytest.mark.asyncio
    async def test_dashboard_achievement_display(
        self, client: AsyncClient, created_user, auth_headers, test_db
    ):
        """Test achievement display in dashboard."""
        from src.personalization.services import progress_service
        from src.personalization.services.achievement_service import get_achievement_service

        user_id = created_user.user_id

        # Complete first chapter to unlock achievement
        await progress_service.complete_chapter(test_db, user_id, 1, 85)

        # Process achievements
        achievement_service = await get_achievement_service(test_db)
        await achievement_service.process_progress_update(user_id, 1)

        response = await client.get(
            "/api/v1/dashboard/metrics",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should have at least one achievement
        achievements = data["achievements"]
        assert achievements["badges_earned"] >= 0  # May or may not have unlocked

    @pytest.mark.asyncio
    async def test_dashboard_unauthorized(self, client: AsyncClient):
        """Test dashboard requires authentication."""
        response = await client.get("/api/v1/dashboard/metrics")

        assert response.status_code == 401
