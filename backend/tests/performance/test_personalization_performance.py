"""Performance tests for personalization feature (T087)."""

import pytest
from uuid import uuid4
from httpx import AsyncClient


class TestProfileRetrieval:
    """Test profile data retrieval performance."""

    @pytest.mark.asyncio
    async def test_get_user_profile_under_500ms(self, test_db_session, sample_test_users, perf_timer, performance_targets):
        """Profile retrieval should complete in < 500ms."""
        from src.personalization.services.user_service import get_user_by_id

        user = sample_test_users[0]

        with perf_timer("get_user_profile") as timer:
            result = await get_user_by_id(test_db_session, user.user_id)

        assert result is not None
        timer.assert_under(performance_targets["profile_retrieval_ms"])

    @pytest.mark.asyncio
    async def test_get_user_by_id_under_500ms(self, test_db_session, sample_test_users, perf_timer, performance_targets):
        """User lookup by ID should complete in < 500ms."""
        from src.personalization.services.user_service import get_user_by_id

        user = sample_test_users[0]

        with perf_timer("get_user_by_id") as timer:
            result = await get_user_by_id(test_db_session, user.user_id)

        assert result is not None
        assert result.user_id == user.user_id
        timer.assert_under(performance_targets["profile_retrieval_ms"])

    @pytest.mark.asyncio
    async def test_bulk_user_retrieval_scaling(self, test_db_session, sample_test_data_large, perf_timer, performance_targets, perf_stats):
        """Verify bulk user retrieval performance scales linearly."""
        from src.personalization.services.user_service import get_user_by_id

        users = sample_test_data_large["users"]

        # Test retrieval for multiple users
        for user in users[:20]:  # Test with 20 users
            with perf_timer(f"get_user_{user.user_id}") as timer:
                result = await get_user_by_id(test_db_session, user.user_id)
            assert result is not None
            perf_stats.add(timer.elapsed_ms)

        # Verify p95 is still under threshold
        assert perf_stats.p95_ms < performance_targets["profile_retrieval_ms"]

    @pytest.mark.asyncio
    async def test_concurrent_profile_requests(self, test_db_session, sample_test_users, perf_timer, performance_targets):
        """Concurrent profile requests should complete in reasonable time."""
        from src.personalization.services.user_service import get_user_by_id
        import asyncio

        users = sample_test_users[:5]

        async def get_profile(user):
            return await get_user_by_id(test_db_session, user.user_id)

        with perf_timer("concurrent_profiles") as timer:
            results = await asyncio.gather(*[get_profile(u) for u in users])

        assert len(results) == len(users)
        assert all(r is not None for r in results)
        # Concurrent should still be relatively fast
        timer.assert_under(performance_targets["profile_retrieval_ms"] * 2)


class TestDashboardPerformance:
    """Test dashboard load performance."""

    @pytest.mark.asyncio
    async def test_progress_summary_under_500ms(self, test_db_session, sample_test_data_large, perf_timer, performance_targets):
        """Progress summary should load in < 500ms."""
        from sqlalchemy import select
        from src.personalization.models.db_models import Progress

        user = sample_test_data_large["users"][0]

        with perf_timer("progress_summary") as timer:
            result = await test_db_session.execute(
                select(Progress).where(Progress.user_id == user.user_id)
            )
            progress_records = result.scalars().all()

        assert len(progress_records) > 0
        timer.assert_under(performance_targets["progress_retrieval_ms"] if hasattr(performance_targets, "progress_retrieval_ms") else 500)

    @pytest.mark.asyncio
    async def test_achievement_list_under_500ms(self, test_db_session, sample_test_data_large, perf_timer):
        """Achievement list should load in < 500ms."""
        from sqlalchemy import select
        from src.personalization.models.db_models import Achievement

        user = sample_test_data_large["users"][0]

        with perf_timer("achievement_list") as timer:
            result = await test_db_session.execute(
                select(Achievement).where(Achievement.user_id == user.user_id)
            )
            achievements = result.scalars().all()

        assert len(achievements) > 0
        timer.assert_under(500)

    @pytest.mark.asyncio
    async def test_dashboard_with_full_history_under_2s(self, test_db_session, sample_test_data_large, perf_timer, performance_targets):
        """Full dashboard load with all data should complete in < 2s."""
        from sqlalchemy import select
        from src.personalization.models.db_models import Progress, Achievement, PracticeAttempt

        user = sample_test_data_large["users"][0]

        with perf_timer("full_dashboard") as timer:
            # Simulate full dashboard data loading
            progress_result = await test_db_session.execute(
                select(Progress).where(Progress.user_id == user.user_id)
            )
            progress = progress_result.scalars().all()

            achievement_result = await test_db_session.execute(
                select(Achievement).where(Achievement.user_id == user.user_id)
            )
            achievements = achievement_result.scalars().all()

            practice_result = await test_db_session.execute(
                select(PracticeAttempt).where(PracticeAttempt.user_id == user.user_id)
            )
            practice_attempts = practice_result.scalars().all()

        assert len(progress) > 0
        assert len(achievements) > 0
        timer.assert_under(performance_targets["dashboard_load_ms"])

    @pytest.mark.asyncio
    async def test_learning_path_data_under_500ms(self, test_db_session, sample_test_data_large, perf_timer):
        """Learning path data should load in < 500ms."""
        from sqlalchemy import select
        from src.personalization.models.db_models import LearningPath

        user = sample_test_data_large["users"][0]

        with perf_timer("learning_path_data") as timer:
            result = await test_db_session.execute(
                select(LearningPath).where(LearningPath.user_id == user.user_id)
            )
            paths = result.scalars().all()

        # Even if no paths exist, query should be fast
        timer.assert_under(500)


class TestChatWithPersonalization:
    """Test chat endpoint with personalization."""

    @pytest.mark.asyncio
    async def test_personalization_applies_quickly(self, test_db_session, sample_test_users, perf_timer):
        """Personalization application should not add significant overhead."""
        from src.personalization.services.chat_integration_service import apply_personalization

        user = sample_test_users[0]
        sample_query = "What is a robot?"

        with perf_timer("apply_personalization") as timer:
            result = await apply_personalization(test_db_session, user.user_id, sample_query)

        assert result is not None
        # Personalization should add < 500ms overhead
        timer.assert_under(500)

    @pytest.mark.asyncio
    async def test_preference_application_fast(self, test_db_session, sample_test_users, perf_timer):
        """User preference application should be fast."""
        from src.personalization.services.user_service import get_user_by_id

        user = sample_test_users[0]

        # Simulate preference loading and application
        with perf_timer("preference_application") as timer:
            user_data = await get_user_by_id(test_db_session, user.user_id)
            # In a real scenario, preferences would be applied to response
            preferences = user_data.preferences_json if user_data else None

        timer.assert_under(200)


class TestDatabaseQueryPerformance:
    """Test raw database query performance."""

    @pytest.mark.asyncio
    async def test_user_query_performance(self, test_db_session, sample_test_data_large, perf_timer):
        """User queries with proper indexing should be fast."""
        from sqlalchemy import select
        from src.personalization.models.db_models import User

        user = sample_test_data_large["users"][0]

        with perf_timer("user_query") as timer:
            result = await test_db_session.execute(
                select(User).where(User.user_id == user.user_id)
            )
            found_user = result.scalar_one_or_none()

        assert found_user is not None
        timer.assert_under(100)

    @pytest.mark.asyncio
    async def test_progress_query_performance(self, test_db_session, sample_test_data_large, perf_timer):
        """Progress queries should be fast with indexes."""
        from sqlalchemy import select
        from src.personalization.models.db_models import Progress

        user = sample_test_data_large["users"][0]

        with perf_timer("progress_query") as timer:
            result = await test_db_session.execute(
                select(Progress).where(Progress.user_id == user.user_id)
            )
            progress_records = result.scalars().all()

        assert len(progress_records) > 0
        timer.assert_under(100)

    @pytest.mark.asyncio
    async def test_achievement_query_performance(self, test_db_session, sample_test_data_large, perf_timer):
        """Achievement queries should be fast."""
        from sqlalchemy import select
        from src.personalization.models.db_models import Achievement

        user = sample_test_data_large["users"][0]

        with perf_timer("achievement_query") as timer:
            result = await test_db_session.execute(
                select(Achievement).where(Achievement.user_id == user.user_id)
            )
            achievements = result.scalars().all()

        timer.assert_under(100)

    @pytest.mark.asyncio
    async def test_learning_path_query_performance(self, test_db_session, sample_test_data_large, perf_timer):
        """Learning path queries should be fast."""
        from sqlalchemy import select
        from src.personalization.models.db_models import LearningPath

        user = sample_test_data_large["users"][0]

        with perf_timer("learning_path_query") as timer:
            result = await test_db_session.execute(
                select(LearningPath).where(LearningPath.user_id == user.user_id)
            )
            paths = result.scalars().all()

        timer.assert_under(100)


class TestPerformanceConsistency:
    """Test that performance remains consistent."""

    @pytest.mark.asyncio
    async def test_repeated_queries_consistent(self, test_db_session, sample_test_users, perf_timer, perf_stats):
        """Repeated queries should have consistent performance."""
        from src.personalization.services.user_service import get_user_by_id

        user = sample_test_users[0]

        # Run same query 10 times
        for i in range(10):
            with perf_timer(f"query_{i}") as timer:
                result = await get_user_by_id(test_db_session, user.user_id)
            assert result is not None
            perf_stats.add(timer.elapsed_ms)

        # All should be under threshold
        for time in perf_stats.times:
            assert time < 500, f"Query took {time}ms, expected < 500ms"

    @pytest.mark.asyncio
    async def test_no_performance_degradation_with_load(self, test_db_session, sample_test_data_large, perf_timer, perf_stats):
        """Performance should not degrade with larger dataset."""
        from sqlalchemy import select
        from src.personalization.models.db_models import Progress

        user = sample_test_data_large["users"][0]

        # Query performance should be same regardless of total data
        for _ in range(5):
            with perf_timer("loaded_query") as timer:
                result = await test_db_session.execute(
                    select(Progress).where(Progress.user_id == user.user_id)
                )
                records = result.scalars().all()
            assert len(records) > 0
            perf_stats.add(timer.elapsed_ms)

        # Average should still be under threshold
        assert perf_stats.avg_ms < 100, f"Average query time {perf_stats.avg_ms}ms > 100ms"
