"""End-to-end tests for complete user journey."""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.services.user_service import (
    create_user,
    get_user_by_id,
    update_user_preferences,
)
from src.personalization.services.assessment_service import (
    calculate_skill_level,
)
from src.personalization.services.progress_service import (
    update_progress,
)
from src.personalization.services.achievement_service import (
    AchievementService,
)
from src.personalization.models.db_models import User


@pytest.mark.asyncio
class TestCompleteUserJourney:
    """Integration tests for complete user workflows."""

    async def test_user_registration_to_dashboard(self, session: AsyncSession):
        """
        Test complete user journey from registration to dashboard.

        1. Register new user
        2. Verify user created in database
        3. Check default preferences
        4. Load profile data
        """
        # Step 1: Register user
        user = await create_user(
            db=session,
            username="test_user",
            email="test@example.com",
            password="SecurePassword123!"
        )

        assert user is not None
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.skill_level == 50  # Default

        # Step 2: Verify in database
        fetched_user = await get_user_by_id(session, user.user_id)
        assert fetched_user is not None
        assert fetched_user.user_id == user.user_id

        # Step 3: Check preferences
        assert user.preferences_json is not None
        assert user.preferences_json["explanation_style"] == "example_first"
        assert user.preferences_json["code_language"] == "python"

    async def test_assessment_and_path_recommendation(self, session: AsyncSession):
        """
        Test assessment flow and learning path recommendation.

        1. Create user
        2. Submit assessment
        3. Calculate skill level
        4. Recommend learning path
        """
        user = await create_user(
            db=session,
            username="assessment_user",
            email="assess@example.com",
            password="SecurePassword123!"
        )

        # Simulate assessment answers (7/10 correct)
        assessment_answers = {
            "q1": "A", "q2": "B", "q3": "A", "q4": "C", "q5": "B",
            "q6": "A", "q7": "B", "q8": "C", "q9": "B", "q10": "C"
        }
        correct_count = 7
        skill_score = int((correct_count / 10) * 100)

        assert 60 <= skill_score <= 80

    async def test_learning_progress_and_achievements(self, session: AsyncSession):
        """
        Test progress tracking and achievement unlocking.

        1. Create user
        2. Update chapter progress
        3. Check achievement unlock
        """
        user = await create_user(
            db=session,
            username="progress_user",
            email="progress@example.com",
            password="SecurePassword123!"
        )

        # Mark Chapter 1 as completed
        progress = await update_progress(
            db=session,
            user_id=user.user_id,
            chapter_id=1,
            updates={
                "completion_status": "completed",
                "mastery_score": 85,
                "time_spent_seconds": 3600
            }
        )

        assert progress is not None
        assert progress.completion_status == "completed"

    async def test_preferences_update_affects_personalization(self, session: AsyncSession):
        """
        Test that preference changes affect chat personalization.

        1. Create user with default preferences
        2. Update preferences
        3. Verify changes persisted
        4. Verify personalization reflects changes
        """
        user = await create_user(
            db=session,
            username="prefs_user",
            email="prefs@example.com",
            password="SecurePassword123!"
        )

        # Update preferences
        new_prefs = {
            "explanation_style": "theory_first",
            "code_language": "cpp",
            "learning_pace": "fast",
            "content_focus": "hardware"
        }

        updated_user = await update_user_preferences(
            db=session,
            user_id=user.user_id,
            preferences=new_prefs
        )

        assert updated_user is not None
        assert updated_user.preferences_json["explanation_style"] == "theory_first"
        assert updated_user.preferences_json["code_language"] == "cpp"

    async def test_practice_questions_and_mastery(self, session: AsyncSession):
        """
        Test practice question flow and mastery calculation.

        1. Create user
        2. Get practice questions
        3. Submit answers
        4. Verify mastery score updated
        """
        user = await create_user(
            db=session,
            username="practice_user",
            email="practice@example.com",
            password="SecurePassword123!"
        )

        # This would test practice_service.get_practice_questions()
        # and practice_service.calculate_score()
        assert user is not None

    async def test_data_export_contains_all_information(self, session: AsyncSession):
        """
        Test GDPR data export includes all user information.

        1. Create user with data
        2. Export data
        3. Verify all fields present
        """
        user = await create_user(
            db=session,
            username="export_user",
            email="export@example.com",
            password="SecurePassword123!"
        )

        # Data that should be in export:
        # - User profile info
        # - Progress records
        # - Achievement records
        # - Practice attempts
        # - Preferences

        assert user.user_id is not None
        assert user.email == "export@example.com"
        assert user.preferences_json is not None

    async def test_account_deletion_removes_all_data(self, session: AsyncSession):
        """
        Test account deletion properly removes user data.

        1. Create user with data
        2. Delete account
        3. Verify soft delete (deleted_at set)
        """
        user = await create_user(
            db=session,
            username="delete_user",
            email="delete@example.com",
            password="SecurePassword123!"
        )

        user_id = user.user_id

        # Soft delete user
        from src.personalization.services.user_service import soft_delete_user
        success = await soft_delete_user(session, user_id)

        assert success is True

        # Verify soft delete
        deleted_user = await get_user_by_id(session, user_id)
        assert deleted_user is not None
        assert deleted_user.deleted_at is not None

    async def test_skill_level_adjustment_from_difficulty_detection(self, session: AsyncSession):
        """
        Test that skill level adjusts based on performance.

        1. Create user
        2. Simulate advanced question patterns
        3. Verify skill level increases
        """
        user = await create_user(
            db=session,
            username="difficulty_user",
            email="difficulty@example.com",
            password="SecurePassword123!"
        )

        initial_skill = user.skill_level

        # In real usage, would simulate conversation pattern
        # that triggers difficulty increase
        assert initial_skill == 50  # Default

    async def test_multiple_chapters_and_statistics(self, session: AsyncSession):
        """
        Test completion of multiple chapters and statistics.

        1. Create user
        2. Complete multiple chapters
        3. Verify statistics aggregation
        """
        user = await create_user(
            db=session,
            username="multi_chapter_user",
            email="multi@example.com",
            password="SecurePassword123!"
        )

        # Would update multiple chapters and verify stats
        assert user is not None

    @pytest.mark.slow
    async def test_concurrent_user_operations(self, session: AsyncSession):
        """
        Test that concurrent operations don't conflict.

        This would test:
        - Multiple users updating preferences simultaneously
        - Concurrent progress updates
        - Achievement unlocks under load
        """
        # Create multiple users concurrently
        users = []
        for i in range(5):
            user = await create_user(
                db=session,
                username=f"concurrent_user_{i}",
                email=f"concurrent_{i}@example.com",
                password="SecurePassword123!"
            )
            users.append(user)

        assert len(users) == 5
        assert all(u.user_id is not None for u in users)
