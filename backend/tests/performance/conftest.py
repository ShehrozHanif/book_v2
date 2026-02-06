"""Performance testing utilities and fixtures for personalization tests."""

import time
import pytest
from contextlib import contextmanager
from typing import Dict, List
from uuid import uuid4


class PerformanceTimer:
    """Context manager for precise performance timing."""

    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.elapsed_ms = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        if self.start_time:
            self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000
            return False
        return False

    def assert_under(self, threshold_ms: float):
        """Assert elapsed time is under threshold."""
        assert self.elapsed_ms < threshold_ms, \
            f"{self.name} took {self.elapsed_ms:.2f}ms, expected < {threshold_ms}ms"

    def assert_between(self, min_ms: float, max_ms: float):
        """Assert elapsed time is within range."""
        assert min_ms < self.elapsed_ms < max_ms, \
            f"{self.name} took {self.elapsed_ms:.2f}ms, expected between {min_ms}-{max_ms}ms"


class PerformanceStats:
    """Track performance statistics across multiple runs."""

    def __init__(self):
        self.times: List[float] = []

    def add(self, elapsed_ms: float):
        """Add timing measurement."""
        self.times.append(elapsed_ms)

    @property
    def count(self) -> int:
        """Number of measurements."""
        return len(self.times)

    @property
    def min_ms(self) -> float:
        """Minimum time."""
        return min(self.times) if self.times else 0

    @property
    def max_ms(self) -> float:
        """Maximum time."""
        return max(self.times) if self.times else 0

    @property
    def avg_ms(self) -> float:
        """Average time."""
        if not self.times:
            return 0
        return sum(self.times) / len(self.times)

    @property
    def p95_ms(self) -> float:
        """95th percentile."""
        if len(self.times) < 2:
            return self.avg_ms
        sorted_times = sorted(self.times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]

    @property
    def p99_ms(self) -> float:
        """99th percentile."""
        if len(self.times) < 2:
            return self.avg_ms
        sorted_times = sorted(self.times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def __str__(self) -> str:
        return (
            f"PerformanceStats(n={self.count}, "
            f"min={self.min_ms:.2f}ms, max={self.max_ms:.2f}ms, "
            f"avg={self.avg_ms:.2f}ms, p95={self.p95_ms:.2f}ms, p99={self.p99_ms:.2f}ms)"
        )


@pytest.fixture
def perf_timer():
    """Fixture providing PerformanceTimer context manager."""
    return PerformanceTimer


@pytest.fixture
def perf_stats():
    """Fixture providing PerformanceStats tracker."""
    return PerformanceStats()


@pytest.fixture
async def sample_test_users(test_db_session):
    """Create sample users for performance testing.

    Creates users with realistic data for performance measurement.
    """
    from src.personalization.models.db_models import User

    users = []
    for i in range(10):
        user = User(
            user_id=uuid4(),
            username=f"perf_test_user_{i}",
            email=f"perf_user_{i}@test.com",
            password_hash="hashed_password",
            skill_level=50 + (i % 50),
            skill_confidence=75,
            bio=f"Test user {i}",
        )
        test_db_session.add(user)
        users.append(user)

    await test_db_session.commit()
    return users


@pytest.fixture
async def sample_test_data_large(test_db_session):
    """Create large dataset for stress testing performance.

    Creates:
    - 100 users with varied profiles
    - Progress data for all chapters
    - Achievements and practice attempts
    """
    from src.personalization.models.db_models import (
        User, Progress, Achievement, PracticeAttempt
    )
    from datetime import datetime, timedelta

    users = []
    progress_records = []
    achievements = []
    practice_attempts = []

    # Create 100 users
    for i in range(100):
        user = User(
            user_id=uuid4(),
            username=f"stress_test_user_{i}",
            email=f"stress_user_{i}@test.com",
            password_hash="hashed_password",
            skill_level=20 + (i % 80),
            skill_confidence=40 + (i % 60),
            bio=f"Stress test user {i}",
        )
        test_db_session.add(user)
        users.append(user)

        # Create progress for each user across chapters
        for chapter_id in range(1, 23):
            progress = Progress(
                progress_id=uuid4(),
                user_id=user.user_id,
                chapter_id=chapter_id,
                mastery_score=30 + (i + chapter_id) % 70,
                completion_status="completed" if (i + chapter_id) % 2 == 0 else "in_progress",
                time_spent_seconds=3600 * ((i + chapter_id) % 20),
                practice_attempts=(i + chapter_id) % 10,
                highest_practice_score=50 + (i + chapter_id) % 50,
                created_at=datetime.utcnow() - timedelta(days=30),
                updated_at=datetime.utcnow()
            )
            test_db_session.add(progress)
            progress_records.append(progress)

        # Create achievements
        for j in range(5):
            achievement = Achievement(
                achievement_id=uuid4(),
                user_id=user.user_id,
                achievement_type=f"ch_{1 + j}_complete",
                earned_date=datetime.utcnow() - timedelta(days=7 * j),
                display_info_json={
                    "title": f"Achievement {j}",
                    "icon": "star",
                    "points": 50,
                    "rarity": "common"
                }
            )
            test_db_session.add(achievement)
            achievements.append(achievement)

        # Create practice attempts
        for j in range(3):
            attempt = PracticeAttempt(
                attempt_id=uuid4(),
                user_id=user.user_id,
                chapter_id=1 + (j % 22),
                score=50 + (i + j) % 50,
                questions_json={"total": 5, "correct": 3 + (i % 2)},
                attempted_at=datetime.utcnow() - timedelta(days=7 * j)
            )
            test_db_session.add(attempt)
            practice_attempts.append(attempt)

    await test_db_session.commit()

    return {
        "users": users,
        "progress": progress_records,
        "achievements": achievements,
        "practice_attempts": practice_attempts
    }


@pytest.fixture
def performance_targets():
    """Define performance targets for assertions."""
    return {
        "profile_retrieval_ms": 500,
        "dashboard_load_ms": 2000,
        "chat_personalization_ms": 3000,
        "database_query_ms": 100,
        "cache_hit_ms": 50,
    }
