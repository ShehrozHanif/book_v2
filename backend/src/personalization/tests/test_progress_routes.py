"""Tests for progress routes (T038, T039)."""

import pytest
from httpx import AsyncClient


class TestProgressRoutes:
    """Test progress tracking API endpoints."""

    @pytest.mark.asyncio
    async def test_mark_chapter_complete_endpoint(
        self, client: AsyncClient, created_user, auth_headers, test_db
    ):
        """Test POST /api/v1/progress/{chapter_id}/complete endpoint."""
        response = await client.post(
            "/api/v1/progress/1/complete",
            json={
                "mastery_score": 85,
                "time_spent_seconds": 1800
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "progress" in data
        assert "xp_earned" in data
        assert "achievements_unlocked" in data

        # Verify progress data
        progress = data["progress"]
        assert progress["chapter_id"] == 1
        assert progress["completion_status"] == "completed"
        assert progress["mastery_score"] == 85

        # Verify XP earned
        assert data["xp_earned"] == 50

    @pytest.mark.asyncio
    async def test_mark_chapter_complete_without_time(
        self, client: AsyncClient, auth_headers
    ):
        """Test completing chapter without time_spent_seconds."""
        response = await client.post(
            "/api/v1/progress/2/complete",
            json={"mastery_score": 90},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["progress"]["mastery_score"] == 90

    @pytest.mark.asyncio
    async def test_mark_chapter_complete_invalid_chapter(
        self, client: AsyncClient, auth_headers
    ):
        """Test completing invalid chapter ID."""
        response = await client.post(
            "/api/v1/progress/25/complete",
            json={"mastery_score": 85},
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "must be between 1 and 22" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_mark_chapter_complete_unauthorized(
        self, client: AsyncClient
    ):
        """Test completing chapter without authentication."""
        response = await client.post(
            "/api/v1/progress/1/complete",
            json={"mastery_score": 85}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_progress_endpoint(
        self, client: AsyncClient, created_user, auth_headers, test_db
    ):
        """Test GET /api/v1/progress endpoint."""
        from src.personalization.services import progress_service

        user_id = created_user.user_id

        # Complete some chapters
        await progress_service.complete_chapter(test_db, user_id, 1, 85, 1800)
        await progress_service.complete_chapter(test_db, user_id, 2, 90, 1500)
        await progress_service.complete_chapter(test_db, user_id, 3, 80, 2000)

        response = await client.get(
            "/api/v1/progress",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "total_chapters_completed" in data
        assert "completion_percentage" in data
        assert "chapters_completed" in data
        assert "total_time_invested_hours" in data
        assert "total_xp_earned" in data
        assert "average_mastery_score" in data
        assert "chapter_details" in data

        # Verify data
        assert data["total_chapters_completed"] == 3
        assert data["completion_percentage"] > 0
        assert len(data["chapters_completed"]) == 3
        assert 1 in data["chapters_completed"]
        assert 2 in data["chapters_completed"]
        assert 3 in data["chapters_completed"]

        # Verify XP
        expected_xp = 85 + 90 + 80
        assert data["total_xp_earned"] == expected_xp

        # Verify average mastery
        expected_avg = round((85 + 90 + 80) / 3, 1)
        assert data["average_mastery_score"] == expected_avg

    @pytest.mark.asyncio
    async def test_get_progress_empty(
        self, client: AsyncClient, auth_headers
    ):
        """Test getting progress with no completed chapters."""
        response = await client.get(
            "/api/v1/progress",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_chapters_completed"] == 0
        assert data["completion_percentage"] == 0.0
        assert len(data["chapters_completed"]) == 0
        assert data["total_xp_earned"] == 0

    @pytest.mark.asyncio
    async def test_get_progress_with_learning_path(
        self, client: AsyncClient, created_user, auth_headers, test_db
    ):
        """Test getting progress with active learning path."""
        from src.personalization.services import learning_path_service, progress_service

        user_id = created_user.user_id

        # Create learning path
        path = await learning_path_service.create_learning_path(
            test_db, user_id, "Test Path", [1, 2, 3, 4, 5]
        )

        # Complete some chapters
        await progress_service.complete_chapter(test_db, user_id, 1, 85)
        await progress_service.complete_chapter(test_db, user_id, 2, 90)

        response = await client.get(
            "/api/v1/progress",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify path progress
        assert data["current_path_progress"] is not None
        path_progress = data["current_path_progress"]
        assert path_progress["chapters_in_path"] == 5
        assert path_progress["completed"] == 2
        assert path_progress["progress_percentage"] == 40.0
        assert path_progress["next_chapter"] == 3

    @pytest.mark.asyncio
    async def test_get_progress_unauthorized(
        self, client: AsyncClient
    ):
        """Test getting progress without authentication."""
        response = await client.get("/api/v1/progress")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_complete_multiple_chapters_xp_accumulation(
        self, client: AsyncClient, auth_headers
    ):
        """Test XP accumulation across multiple chapter completions."""
        # Complete chapters sequentially
        for chapter_id in range(1, 6):
            response = await client.post(
                f"/api/v1/progress/{chapter_id}/complete",
                json={"mastery_score": 80},
                headers=auth_headers
            )
            assert response.status_code == 200

        # Get progress and verify total XP
        response = await client.get(
            "/api/v1/progress",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # XP = sum of mastery scores
        expected_xp = 80 * 5
        assert data["total_xp_earned"] == expected_xp

    @pytest.mark.asyncio
    async def test_chapter_details_in_progress(
        self, client: AsyncClient, created_user, auth_headers, test_db
    ):
        """Test chapter details structure in progress response."""
        from src.personalization.services import progress_service

        user_id = created_user.user_id

        # Complete a chapter
        await progress_service.complete_chapter(test_db, user_id, 5, 88, 2100)

        response = await client.get(
            "/api/v1/progress",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify chapter details
        chapter_details = data["chapter_details"]
        assert "5" in chapter_details

        ch5 = chapter_details["5"]
        assert ch5["completion_status"] == "completed"
        assert ch5["mastery_score"] == 88
        assert ch5["time_spent"] == 2100
        assert ch5["practice_attempts"] == 0
