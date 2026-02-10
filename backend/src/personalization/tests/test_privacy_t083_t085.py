"""Tests for GDPR and Privacy Compliance (T083-T085)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.personalization.models.db_models import (
    User,
    Progress,
    Achievement,
    PracticeAttempt,
    LearningPath,
)
from src.personalization.services.privacy_service import PrivacyService


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_user():
    """Create mock user."""
    user = MagicMock(spec=User)
    user.user_id = uuid4()
    user.username = "testuser"
    user.email = "test@example.com"
    user.skill_level = "intermediate"
    user.skill_confidence = 75
    user.bio = "Test bio"
    user.is_deleted = False
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    user.last_login_at = datetime.utcnow()
    user.deleted_at = None
    return user


class TestCollectUserData:
    """Tests for T084: Data export functionality."""

    @pytest.mark.asyncio
    async def test_collect_user_data_success(self, mock_db, mock_user):
        """Test successful data collection."""
        user_id = mock_user.user_id

        # Mock user fetch
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = mock_user

        # Mock progress
        progress_mock = MagicMock(
            chapter_id=1,
            mastery_score=75,
            completion_status="completed",
            time_spent_seconds=3600,
            practice_attempts=2,
            highest_practice_score=75,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        progress_result = MagicMock()
        progress_result.scalars().all.return_value = [progress_mock]

        # Mock achievements
        achievement_mock = MagicMock(
            achievement_id=uuid4(),
            achievement_type="ch_1_complete",
            display_info_json={"title": "Achievement 1"},
            earned_date=datetime.utcnow(),
        )
        achievement_result = MagicMock()
        achievement_result.scalars().all.return_value = [achievement_mock]

        # Mock practice attempts
        practice_mock = MagicMock(
            attempt_id=uuid4(),
            chapter_id=1,
            score=75,
            questions_json={"total": 5},
            attempted_at=datetime.utcnow(),
        )
        practice_result = MagicMock()
        practice_result.scalars().all.return_value = [practice_mock]

        # Mock learning paths
        paths_result = MagicMock()
        paths_result.scalars().all.return_value = []

        # Mock user preferences
        prefs_result = MagicMock()
        prefs_result.scalar_one_or_none.return_value = None

        # Setup mock_db.execute to return correct results
        call_count = [0]
        def side_effect_fn(*args, **kwargs):
            if call_count[0] == 0:  # User fetch
                call_count[0] += 1
                return user_result
            elif call_count[0] == 1:  # Progress fetch
                call_count[0] += 1
                return progress_result
            elif call_count[0] == 2:  # Achievements fetch
                call_count[0] += 1
                return achievement_result
            elif call_count[0] == 3:  # Practice attempts fetch
                call_count[0] += 1
                return practice_result
            elif call_count[0] == 4:  # Learning paths fetch
                call_count[0] += 1
                return paths_result
            elif call_count[0] == 5:  # User preferences fetch
                call_count[0] += 1
                return prefs_result
            return MagicMock()

        mock_db.execute.side_effect = side_effect_fn

        service = PrivacyService(mock_db)
        data = await service.collect_user_data(user_id)

        # Verify data structure
        assert "export_date" in data
        assert "user" in data
        assert "progress" in data
        assert "achievements" in data
        assert "practice_attempts" in data
        assert "summary" in data

        assert data["user"]["username"] == "testuser"
        assert len(data["progress"]) == 1
        assert len(data["achievements"]) == 1
        assert data["summary"]["total_chapters_attempted"] == 1

    @pytest.mark.asyncio
    async def test_collect_user_data_not_found(self, mock_db):
        """Test data collection for non-existent user."""
        user_id = uuid4()

        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = user_result

        service = PrivacyService(mock_db)

        with pytest.raises(ValueError) as exc_info:
            await service.collect_user_data(user_id)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_collect_user_data_with_all_entities(self, mock_db, mock_user):
        """Test data collection includes all entity types."""
        user_id = mock_user.user_id

        # Setup mocks to return various data types
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = mock_user

        # Multiple progress records
        progress_records = [
            MagicMock(
                chapter_id=i,
                mastery_score=50 + (i * 5),
                completion_status="completed" if i < 5 else "in_progress",
                time_spent_seconds=3600 * i,
                practice_attempts=i + 1,
                highest_practice_score=50 + (i * 5),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            for i in range(1, 6)
        ]
        progress_result = MagicMock()
        progress_result.scalars().all.return_value = progress_records

        # Multiple achievements
        achievements = [
            MagicMock(
                achievement_id=uuid4(),
                achievement_type=f"ch_{i}_complete",
                display_info_json={"title": f"Achievement {i}"},
                earned_date=datetime.utcnow(),
            )
            for i in range(1, 4)
        ]
        achievement_result = MagicMock()
        achievement_result.scalars().all.return_value = achievements

        # Multiple practice attempts
        practice_attempts = [
            MagicMock(
                attempt_id=uuid4(),
                chapter_id=1,
                score=50 + (i * 10),
                questions_json={"total": 5},
                attempted_at=datetime.utcnow(),
            )
            for i in range(1, 4)
        ]
        practice_result = MagicMock()
        practice_result.scalars().all.return_value = practice_attempts

        # Learning paths
        paths_result = MagicMock()
        paths_result.scalars().all.return_value = []

        # User preferences
        prefs_result = MagicMock()
        prefs_result.scalar_one_or_none.return_value = None

        call_count = [0]
        def side_effect(*args, **kwargs):
            if call_count[0] == 0:
                call_count[0] += 1
                return user_result
            elif call_count[0] == 1:
                call_count[0] += 1
                return progress_result
            elif call_count[0] == 2:
                call_count[0] += 1
                return achievement_result
            elif call_count[0] == 3:
                call_count[0] += 1
                return practice_result
            elif call_count[0] == 4:
                call_count[0] += 1
                return paths_result
            elif call_count[0] == 5:
                call_count[0] += 1
                return prefs_result
            return MagicMock()

        mock_db.execute.side_effect = side_effect

        service = PrivacyService(mock_db)
        data = await service.collect_user_data(user_id)

        # Verify all entities collected
        assert len(data["progress"]) == 5
        assert len(data["achievements"]) == 3
        assert len(data["practice_attempts"]) == 3
        assert data["summary"]["total_chapters_attempted"] == 5
        assert data["summary"]["total_achievements"] == 3
        assert data["summary"]["total_practice_attempts"] == 3


class TestDeleteUserAccountCascading:
    """Tests for T085: Account deletion with cascading deletes."""

    @pytest.mark.asyncio
    async def test_delete_account_success(self, mock_db, mock_user):
        """Test successful account deletion with cascading."""
        user_id = mock_user.user_id

        # Mock user fetch
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = mock_user

        # Mock related records
        progress_records = [MagicMock() for _ in range(3)]
        progress_result = MagicMock()
        progress_result.scalars().all.return_value = progress_records

        achievements = [MagicMock() for _ in range(2)]
        achievement_result = MagicMock()
        achievement_result.scalars().all.return_value = achievements

        practice_attempts = [MagicMock() for _ in range(1)]
        practice_result = MagicMock()
        practice_result.scalars().all.return_value = practice_attempts

        paths = []
        paths_result = MagicMock()
        paths_result.scalars().all.return_value = paths

        prefs = None
        prefs_result = MagicMock()
        prefs_result.scalar_one_or_none.return_value = prefs

        call_count = [0]
        def side_effect(*args, **kwargs):
            if call_count[0] == 0:  # User fetch
                call_count[0] += 1
                return user_result
            elif call_count[0] == 1:  # Progress fetch
                call_count[0] += 1
                return progress_result
            elif call_count[0] == 2:  # Achievement fetch
                call_count[0] += 1
                return achievement_result
            elif call_count[0] == 3:  # Practice attempt fetch
                call_count[0] += 1
                return practice_result
            elif call_count[0] == 4:  # Learning paths fetch
                call_count[0] += 1
                return paths_result
            elif call_count[0] == 5:  # User preferences fetch
                call_count[0] += 1
                return prefs_result
            return MagicMock()

        mock_db.execute.side_effect = side_effect

        service = PrivacyService(mock_db)
        success = await service.delete_user_account_cascading(user_id)

        assert success is True
        assert mock_user.is_deleted is True
        assert mock_user.deleted_at is not None
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_account_user_not_found(self, mock_db):
        """Test deletion fails gracefully for non-existent user."""
        user_id = uuid4()

        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = user_result

        service = PrivacyService(mock_db)
        success = await service.delete_user_account_cascading(user_id)

        assert success is False
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_account_handles_errors(self, mock_db, mock_user):
        """Test deletion handles errors gracefully."""
        user_id = mock_user.user_id

        # Mock database error
        mock_db.execute.side_effect = Exception("Database error")

        service = PrivacyService(mock_db)
        success = await service.delete_user_account_cascading(user_id)

        assert success is False
        mock_db.rollback.assert_called_once()


class TestAnonymizeDeletedUserData:
    """Tests for T085: Data anonymization for deleted users."""

    @pytest.mark.asyncio
    async def test_anonymize_user_data_success(self, mock_db, mock_user):
        """Test successful user data anonymization."""
        user_id = mock_user.user_id

        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = user_result

        service = PrivacyService(mock_db)
        success = await service.anonymize_deleted_user_data(user_id)

        assert success is True
        # Verify anonymization
        assert "deleted_user_" in mock_user.username
        assert "@deleted.invalid" in mock_user.email
        assert mock_user.password_hash is None
        assert mock_user.bio is None
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_anonymize_user_not_found(self, mock_db):
        """Test anonymization fails for non-existent user."""
        user_id = uuid4()

        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = user_result

        service = PrivacyService(mock_db)
        success = await service.anonymize_deleted_user_data(user_id)

        assert success is False
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_anonymize_preserves_user_id(self, mock_db, mock_user):
        """Test that anonymization preserves user ID for referential integrity."""
        user_id = mock_user.user_id
        original_id = mock_user.user_id

        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = user_result

        service = PrivacyService(mock_db)
        await service.anonymize_deleted_user_data(user_id)

        # User ID should remain unchanged
        assert mock_user.user_id == original_id


class TestPrivacyServiceIntegration:
    """Integration tests for privacy service operations."""

    @pytest.mark.asyncio
    async def test_export_then_delete_workflow(self, mock_db, mock_user):
        """Test complete workflow: export then delete."""
        user_id = mock_user.user_id

        # Mock for export
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = mock_user

        progress_result = MagicMock()
        progress_result.scalars().all.return_value = [
            MagicMock(
                chapter_id=1,
                mastery_score=80,
                completion_status="completed",
                time_spent_seconds=3600,
                practice_attempts=1,
                highest_practice_score=80,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        ]

        achievement_result = MagicMock()
        achievement_result.scalars().all.return_value = []

        practice_result = MagicMock()
        practice_result.scalars().all.return_value = []

        paths_result = MagicMock()
        paths_result.scalars().all.return_value = []

        prefs_result = MagicMock()
        prefs_result.scalar_one_or_none.return_value = None

        call_count = [0]
        def side_effect(*args, **kwargs):
            if call_count[0] == 0:
                call_count[0] += 1
                return user_result
            elif call_count[0] == 1:
                call_count[0] += 1
                return progress_result
            elif call_count[0] == 2:
                call_count[0] += 1
                return achievement_result
            elif call_count[0] == 3:
                call_count[0] += 1
                return practice_result
            elif call_count[0] == 4:
                call_count[0] += 1
                return paths_result
            elif call_count[0] == 5:
                call_count[0] += 1
                return prefs_result
            return MagicMock()

        mock_db.execute.side_effect = side_effect

        service = PrivacyService(mock_db)

        # Step 1: Export
        export_data = await service.collect_user_data(user_id)
        assert "user" in export_data
        assert export_data["summary"]["total_chapters_attempted"] == 1

        # Step 2: Delete (setup new service instance since db.execute was exhausted)
        call_count = [0]
        def side_effect_delete(*args, **kwargs):
            if call_count[0] == 0:  # User fetch for delete
                call_count[0] += 1
                return user_result
            elif call_count[0] == 1:  # Progress fetch for delete
                call_count[0] += 1
                return progress_result
            elif call_count[0] == 2:  # Achievement fetch for delete
                call_count[0] += 1
                return achievement_result
            elif call_count[0] == 3:  # Practice attempt fetch for delete
                call_count[0] += 1
                return practice_result
            elif call_count[0] == 4:  # Learning paths fetch for delete
                call_count[0] += 1
                return paths_result
            return MagicMock()

        mock_db.execute.side_effect = side_effect_delete
        success = await service.delete_user_account_cascading(user_id)
        assert success is True
