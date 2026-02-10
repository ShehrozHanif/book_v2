"""Tests for learning path service functionality."""

import pytest
from uuid import uuid4

from src.personalization.services import learning_path_service


class TestPathRecommendations:
    """Test learning path recommendation logic."""

    def test_beginner_recommendations(self):
        """Test recommendations for beginner skill level."""
        recommendations = learning_path_service.recommend_learning_paths(
            skill_score=30,
            skill_tier="beginner"
        )

        assert len(recommendations) >= 2
        # Beginner path should be first with 100% match
        assert recommendations[0]["path_key"] == "beginner"
        assert recommendations[0]["match_percentage"] == 100

        # Verify all recommendations have required fields
        for rec in recommendations:
            assert "path_key" in rec
            assert "name" in rec
            assert "description" in rec
            assert "chapters" in rec
            assert "estimated_hours" in rec
            assert "match_percentage" in rec
            assert isinstance(rec["chapters"], list)

    def test_intermediate_recommendations(self):
        """Test recommendations for intermediate skill level."""
        recommendations = learning_path_service.recommend_learning_paths(
            skill_score=60,
            skill_tier="intermediate"
        )

        assert len(recommendations) >= 2
        # Intermediate path should be first with 100% match
        assert recommendations[0]["path_key"] == "intermediate"
        assert recommendations[0]["match_percentage"] == 100

    def test_advanced_recommendations(self):
        """Test recommendations for advanced skill level."""
        recommendations = learning_path_service.recommend_learning_paths(
            skill_score=85,
            skill_tier="advanced"
        )

        assert len(recommendations) >= 2
        # Researcher path should be first with 100% match
        assert recommendations[0]["path_key"] == "researcher"
        assert recommendations[0]["match_percentage"] == 100

    def test_recommendations_sorted_by_match(self):
        """Test that recommendations are sorted by match percentage."""
        recommendations = learning_path_service.recommend_learning_paths(
            skill_score=60,
            skill_tier="intermediate"
        )

        # Verify descending order
        for i in range(len(recommendations) - 1):
            assert recommendations[i]["match_percentage"] >= recommendations[i + 1]["match_percentage"]


@pytest.mark.asyncio
class TestLearningPathCreation:
    """Test learning path creation and database operations."""

    async def test_create_learning_path(self, db_session, test_user):
        """Test creating a learning path for user."""
        path = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="beginner"
        )

        assert path is not None
        assert path.user_id == test_user.user_id
        assert path.path_name == "Beginner Path - Robotics Foundations"
        assert path.status == "active"
        assert path.completion_percentage == 0
        assert isinstance(path.chapters_array, list)
        assert len(path.chapters_array) > 0

    async def test_create_path_with_invalid_key(self, db_session, test_user):
        """Test creating path with invalid path_key raises error."""
        with pytest.raises(ValueError, match="Invalid path key"):
            await learning_path_service.create_learning_path(
                db=db_session,
                user_id=test_user.user_id,
                path_key="nonexistent_path"
            )

    async def test_create_path_abandons_existing(self, db_session, test_user):
        """Test that creating new path abandons existing active path."""
        # Create first path
        path1 = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="beginner"
        )

        assert path1.status == "active"

        # Create second path
        path2 = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="developer"
        )

        assert path2.status == "active"

        # Refresh first path and check it's abandoned
        await db_session.refresh(path1)
        assert path1.status == "abandoned"


@pytest.mark.asyncio
class TestPathRetrieval:
    """Test learning path retrieval operations."""

    async def test_get_active_learning_path(self, db_session, test_user):
        """Test retrieving user's active learning path."""
        # Create a path
        created_path = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="intermediate"
        )

        # Retrieve active path
        active_path = await learning_path_service.get_active_learning_path(
            db=db_session,
            user_id=test_user.user_id
        )

        assert active_path is not None
        assert active_path.path_id == created_path.path_id
        assert active_path.status == "active"

    async def test_get_active_path_returns_none_when_none_exists(self, db_session, test_user):
        """Test that get_active_learning_path returns None when no active path."""
        active_path = await learning_path_service.get_active_learning_path(
            db=db_session,
            user_id=test_user.user_id
        )

        assert active_path is None

    async def test_get_all_user_paths(self, db_session, test_user):
        """Test retrieving all user paths."""
        # Create multiple paths
        await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="beginner"
        )

        await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="developer"
        )

        # Get all paths
        all_paths = await learning_path_service.get_all_user_paths(
            db=db_session,
            user_id=test_user.user_id
        )

        assert len(all_paths) == 2
        # Should be ordered by creation date (newest first)
        assert all_paths[0].status == "active"
        assert all_paths[1].status == "abandoned"


@pytest.mark.asyncio
class TestProgressCalculation:
    """Test learning path progress calculation."""

    async def test_update_path_progress_no_completion(self, db_session, test_user):
        """Test progress calculation with no chapters completed."""
        # Create a path
        path = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="beginner"
        )

        # Update progress (no completed chapters)
        updated_path = await learning_path_service.update_path_progress(
            db=db_session,
            user_id=test_user.user_id,
            path_id=path.path_id
        )

        assert updated_path is not None
        assert updated_path.completion_percentage == 0
        assert updated_path.status == "active"

    async def test_update_path_progress_partial_completion(self, db_session, test_user):
        """Test progress calculation with some chapters completed."""
        from src.personalization.models.db_models import Progress

        # Create a path
        path = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="beginner"
        )

        # Complete first chapter in path
        first_chapter = path.chapters_array[0]
        progress = Progress(
            user_id=test_user.user_id,
            chapter_id=first_chapter,
            completion_status="completed",
            mastery_score=85
        )
        db_session.add(progress)
        await db_session.commit()

        # Update path progress
        updated_path = await learning_path_service.update_path_progress(
            db=db_session,
            user_id=test_user.user_id,
            path_id=path.path_id
        )

        assert updated_path is not None
        assert updated_path.completion_percentage > 0
        assert updated_path.completion_percentage < 100
        assert updated_path.status == "active"

    async def test_update_path_progress_full_completion(self, db_session, test_user):
        """Test progress calculation with all chapters completed."""
        from src.personalization.models.db_models import Progress

        # Create a path
        path = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="beginner"
        )

        # Complete all chapters in path
        for chapter_id in path.chapters_array:
            progress = Progress(
                user_id=test_user.user_id,
                chapter_id=chapter_id,
                completion_status="completed",
                mastery_score=85
            )
            db_session.add(progress)

        await db_session.commit()

        # Update path progress
        updated_path = await learning_path_service.update_path_progress(
            db=db_session,
            user_id=test_user.user_id,
            path_id=path.path_id
        )

        assert updated_path is not None
        assert updated_path.completion_percentage == 100
        assert updated_path.status == "completed"


@pytest.mark.asyncio
class TestNextChapterRecommendation:
    """Test next chapter recommendation logic."""

    async def test_get_next_chapter_when_none_completed(self, db_session, test_user):
        """Test getting next chapter when no chapters completed."""
        # Create a path
        path = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="beginner"
        )

        # Get next chapter
        next_chapter = await learning_path_service.get_next_chapter_in_path(
            db=db_session,
            user_id=test_user.user_id,
            path_id=path.path_id
        )

        assert next_chapter is not None
        assert next_chapter == path.chapters_array[0]

    async def test_get_next_chapter_after_some_completed(self, db_session, test_user):
        """Test getting next chapter after completing some chapters."""
        from src.personalization.models.db_models import Progress

        # Create a path
        path = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="beginner"
        )

        # Complete first two chapters
        for chapter_id in path.chapters_array[:2]:
            progress = Progress(
                user_id=test_user.user_id,
                chapter_id=chapter_id,
                completion_status="completed",
                mastery_score=85
            )
            db_session.add(progress)

        await db_session.commit()

        # Get next chapter
        next_chapter = await learning_path_service.get_next_chapter_in_path(
            db=db_session,
            user_id=test_user.user_id,
            path_id=path.path_id
        )

        assert next_chapter is not None
        assert next_chapter == path.chapters_array[2]

    async def test_get_next_chapter_when_all_completed(self, db_session, test_user):
        """Test getting next chapter when all chapters completed."""
        from src.personalization.models.db_models import Progress

        # Create a path
        path = await learning_path_service.create_learning_path(
            db=db_session,
            user_id=test_user.user_id,
            path_key="beginner"
        )

        # Complete all chapters
        for chapter_id in path.chapters_array:
            progress = Progress(
                user_id=test_user.user_id,
                chapter_id=chapter_id,
                completion_status="completed",
                mastery_score=85
            )
            db_session.add(progress)

        await db_session.commit()

        # Get next chapter
        next_chapter = await learning_path_service.get_next_chapter_in_path(
            db=db_session,
            user_id=test_user.user_id,
            path_id=path.path_id
        )

        assert next_chapter is None


class TestPathConfiguration:
    """Test path configuration retrieval."""

    def test_get_path_config_valid_key(self):
        """Test retrieving config for valid path key."""
        config = learning_path_service.get_path_config("beginner")

        assert config is not None
        assert "name" in config
        assert "chapters" in config
        assert "estimated_hours" in config

    def test_get_path_config_invalid_key(self):
        """Test retrieving config for invalid path key."""
        config = learning_path_service.get_path_config("nonexistent")

        assert config is None

    def test_get_all_path_configs(self):
        """Test retrieving all path configurations."""
        all_configs = learning_path_service.get_all_path_configs()

        assert len(all_configs) >= 3
        assert "beginner" in all_configs
        assert "intermediate" in all_configs
        assert "researcher" in all_configs
