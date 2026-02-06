"""Integration tests for Badge endpoints (T054)."""

import pytest
import base64
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from src.personalization.models.db_models import User
from src.personalization.api.routes.progress import (
    get_achievement_badge,
    get_achievement_badge_with_points
)
from uuid import uuid4


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock()


@pytest.fixture
def test_user():
    """Create test user."""
    return User(
        user_id=uuid4(),
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        skill_level=50
    )


class TestBadgeEndpoints:
    """Integration tests for badge endpoints."""

    @pytest.mark.asyncio
    async def test_get_achievement_badge_png(self, mock_db, test_user):
        """Test getting achievement badge as PNG."""
        with patch("src.personalization.api.routes.progress.get_badge_service") as mock_service:
            mock_badge = AsyncMock()
            mock_badge.generate_badge = MagicMock(return_value=b'\x89PNG\r\n\x1a\n' + b'fake_png_data')
            mock_service.return_value = mock_badge

            result = await get_achievement_badge(
                user_id=test_user.user_id,
                achievement_id="ch_1_complete",
                current_user=test_user,
                db=mock_db,
                format="png"
            )

            # Verify PNG response
            assert result.media_type == "image/png"
            assert b'PNG' in result.body

    @pytest.mark.asyncio
    async def test_get_achievement_badge_base64(self, mock_db, test_user):
        """Test getting achievement badge as base64."""
        with patch("src.personalization.api.routes.progress.get_badge_service") as mock_service:
            mock_badge = AsyncMock()
            png_bytes = b'\x89PNG\r\n\x1a\n' + b'fake_png_data'
            mock_badge.generate_badge = MagicMock(return_value=png_bytes)
            mock_service.return_value = mock_badge

            result = await get_achievement_badge(
                user_id=test_user.user_id,
                achievement_id="ch_1_complete",
                current_user=test_user,
                db=mock_db,
                format="base64"
            )

            # Verify base64 response
            assert "badge" in result
            base64_str = result["badge"]
            # Decode and verify it's valid
            decoded = base64.b64decode(base64_str)
            assert decoded == png_bytes

    @pytest.mark.asyncio
    async def test_get_achievement_badge_forbidden(self, mock_db, test_user):
        """Test that users cannot access other users' badges."""
        other_user = User(
            user_id=uuid4(),
            username="otheruser",
            email="other@example.com",
            password_hash="hashed_password",
            skill_level=50
        )

        try:
            await get_achievement_badge(
                user_id=other_user.user_id,
                achievement_id="ch_1_complete",
                current_user=test_user,
                db=mock_db,
                format="png"
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 403

    @pytest.mark.asyncio
    async def test_get_achievement_badge_not_found(self, mock_db, test_user):
        """Test getting badge for non-existent achievement."""
        try:
            await get_achievement_badge(
                user_id=test_user.user_id,
                achievement_id="invalid_achievement",
                current_user=test_user,
                db=mock_db,
                format="png"
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 404

    @pytest.mark.asyncio
    async def test_get_achievement_badge_with_points_png(self, mock_db, test_user):
        """Test getting achievement badge with points as PNG."""
        with patch("src.personalization.api.routes.progress.get_badge_service") as mock_service:
            mock_badge = AsyncMock()
            mock_badge.generate_badge_with_points = MagicMock(return_value=b'\x89PNG\r\n\x1a\n' + b'fake_png_data')
            mock_service.return_value = mock_badge

            result = await get_achievement_badge_with_points(
                user_id=test_user.user_id,
                achievement_id="ch_1_complete",
                current_user=test_user,
                db=mock_db,
                format="png"
            )

            # Verify PNG response
            assert result.media_type == "image/png"
            assert b'PNG' in result.body

    @pytest.mark.asyncio
    async def test_get_achievement_badge_with_points_base64(self, mock_db, test_user):
        """Test getting achievement badge with points as base64."""
        with patch("src.personalization.api.routes.progress.get_badge_service") as mock_service:
            mock_badge = AsyncMock()
            png_bytes = b'\x89PNG\r\n\x1a\n' + b'fake_png_data'
            mock_badge.generate_badge_with_points = MagicMock(return_value=png_bytes)
            mock_service.return_value = mock_badge

            result = await get_achievement_badge_with_points(
                user_id=test_user.user_id,
                achievement_id="ch_1_complete",
                current_user=test_user,
                db=mock_db,
                format="base64"
            )

            # Verify base64 response
            assert "badge" in result
            base64_str = result["badge"]
            # Decode and verify it's valid
            decoded = base64.b64decode(base64_str)
            assert decoded == png_bytes

    @pytest.mark.asyncio
    async def test_get_achievement_badge_various_achievement_ids(self, mock_db, test_user):
        """Test badge generation for various achievement types."""
        achievement_ids = [
            "ch_1_complete",
            "ch_5_complete",
            "xp_100",
            "xp_500",
            "module_1_complete",
            "streak_7",
            "perfect_score"
        ]

        with patch("src.personalization.api.routes.progress.get_badge_service") as mock_service:
            mock_badge = AsyncMock()
            mock_badge.generate_badge = MagicMock(return_value=b'\x89PNG\r\n\x1a\n' + b'fake_png_data')
            mock_service.return_value = mock_badge

            for ach_id in achievement_ids:
                result = await get_achievement_badge(
                    user_id=test_user.user_id,
                    achievement_id=ach_id,
                    current_user=test_user,
                    db=mock_db,
                    format="png"
                )

                assert result.media_type == "image/png"

    @pytest.mark.asyncio
    async def test_get_achievement_badge_default_format(self, mock_db, test_user):
        """Test that default format is PNG."""
        with patch("src.personalization.api.routes.progress.get_badge_service") as mock_service:
            mock_badge = AsyncMock()
            mock_badge.generate_badge = MagicMock(return_value=b'\x89PNG\r\n\x1a\n' + b'fake_png_data')
            mock_service.return_value = mock_badge

            # Call without specifying format (should default to png)
            result = await get_achievement_badge(
                user_id=test_user.user_id,
                achievement_id="ch_1_complete",
                current_user=test_user,
                db=mock_db
            )

            assert result.media_type == "image/png"

    @pytest.mark.asyncio
    async def test_get_achievement_badge_generation_failure(self, mock_db, test_user):
        """Test handling of badge generation failure."""
        with patch("src.personalization.api.routes.progress.get_badge_service") as mock_service:
            mock_badge = AsyncMock()
            mock_badge.generate_badge = MagicMock(return_value=None)
            mock_service.return_value = mock_badge

            try:
                await get_achievement_badge(
                    user_id=test_user.user_id,
                    achievement_id="ch_1_complete",
                    current_user=test_user,
                    db=mock_db,
                    format="png"
                )
                assert False, "Should have raised HTTPException"
            except HTTPException as e:
                assert e.status_code == 500

    @pytest.mark.asyncio
    async def test_badge_filename_includes_achievement_id(self, mock_db, test_user):
        """Test that badge download includes achievement ID in filename."""
        with patch("src.personalization.api.routes.progress.get_badge_service") as mock_service:
            mock_badge = AsyncMock()
            mock_badge.generate_badge = MagicMock(return_value=b'\x89PNG\r\n\x1a\n' + b'fake_png_data')
            mock_service.return_value = mock_badge

            result = await get_achievement_badge(
                user_id=test_user.user_id,
                achievement_id="ch_5_complete",
                current_user=test_user,
                db=mock_db,
                format="png"
            )

            # Verify filename in headers
            assert "ch_5_complete.png" in result.headers["Content-Disposition"]

    @pytest.mark.asyncio
    async def test_badge_with_points_filename(self, mock_db, test_user):
        """Test that points badge download includes special filename."""
        with patch("src.personalization.api.routes.progress.get_badge_service") as mock_service:
            mock_badge = AsyncMock()
            mock_badge.generate_badge_with_points = MagicMock(return_value=b'\x89PNG\r\n\x1a\n' + b'fake_png_data')
            mock_service.return_value = mock_badge

            result = await get_achievement_badge_with_points(
                user_id=test_user.user_id,
                achievement_id="module_1_complete",
                current_user=test_user,
                db=mock_db,
                format="png"
            )

            # Verify filename in headers includes "with_points"
            assert "module_1_complete_with_points.png" in result.headers["Content-Disposition"]
