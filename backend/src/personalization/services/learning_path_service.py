"""Learning path service for personalized learning journeys."""

from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import LearningPath, Progress


# Learning path configurations
LEARNING_PATH_CONFIGS = {
    "beginner": {
        "name": "Beginner Path - Robotics Foundations",
        "description": "Start with fundamentals and build a strong foundation in robotics concepts",
        "chapters": [1, 2, 3, 4, 5, 6],
        "estimated_hours": 30,
        "prerequisites": [],
        "focus": "Core concepts, basic kinematics, simple simulations"
    },
    "developer": {
        "name": "Developer Path - Practical Implementation",
        "description": "Focus on programming, simulation, and practical robot control",
        "chapters": [1, 2, 6, 7, 8, 9, 12, 14, 15],
        "estimated_hours": 45,
        "prerequisites": ["Basic programming knowledge"],
        "focus": "Python programming, simulation tools, control implementation"
    },
    "researcher": {
        "name": "Researcher Path - Advanced Theory",
        "description": "Deep dive into mathematical foundations and cutting-edge techniques",
        "chapters": [1, 2, 3, 4, 5, 10, 11, 13, 16, 17, 18, 19, 20, 21, 22],
        "estimated_hours": 80,
        "prerequisites": ["Linear algebra", "Calculus", "Programming"],
        "focus": "Mathematical rigor, advanced algorithms, research topics"
    },
    "hardware": {
        "name": "Hardware Integration Path",
        "description": "Learn about physical robot systems and hardware interfaces",
        "chapters": [1, 2, 3, 4, 6, 7, 14, 15, 19],
        "estimated_hours": 40,
        "prerequisites": ["Basic electronics"],
        "focus": "Actuators, sensors, hardware control, physical systems"
    },
    "intermediate": {
        "name": "Intermediate Path - Balanced Learning",
        "description": "Balanced approach covering theory and practice",
        "chapters": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14],
        "estimated_hours": 55,
        "prerequisites": ["Basic math and programming"],
        "focus": "Theory foundations with practical applications"
    }
}


def recommend_learning_paths(skill_score: int, skill_tier: str) -> List[Dict[str, Any]]:
    """
    Recommend learning paths based on skill assessment.

    Args:
        skill_score: Skill score from 0-100
        skill_tier: 'beginner', 'intermediate', or 'advanced'

    Returns:
        List of recommended path configs with match percentages

    Algorithm:
        - Beginner (0-49): Beginner path (100%), Intermediate (70%), Developer (60%)
        - Intermediate (50-74): Intermediate (100%), Developer (90%), Researcher (70%)
        - Advanced (75-100): Researcher (100%), Developer (95%), Intermediate (80%)
    """
    recommendations = []

    if skill_tier == "beginner":
        recommendations = [
            {
                "path_key": "beginner",
                "match_percentage": 100,
                "reason": "Perfect match for building foundational knowledge"
            },
            {
                "path_key": "intermediate",
                "match_percentage": 70,
                "reason": "Can explore intermediate topics with extra support"
            },
            {
                "path_key": "developer",
                "match_percentage": 60,
                "reason": "Good if you prefer hands-on programming focus"
            }
        ]
    elif skill_tier == "intermediate":
        recommendations = [
            {
                "path_key": "intermediate",
                "match_percentage": 100,
                "reason": "Balanced approach matching your current level"
            },
            {
                "path_key": "developer",
                "match_percentage": 90,
                "reason": "Excellent for practical implementation skills"
            },
            {
                "path_key": "researcher",
                "match_percentage": 70,
                "reason": "Challenge yourself with advanced theory"
            },
            {
                "path_key": "hardware",
                "match_percentage": 75,
                "reason": "Great for understanding physical robot systems"
            }
        ]
    else:  # advanced
        recommendations = [
            {
                "path_key": "researcher",
                "match_percentage": 100,
                "reason": "Comprehensive coverage of advanced topics"
            },
            {
                "path_key": "developer",
                "match_percentage": 95,
                "reason": "Apply your knowledge to complex implementations"
            },
            {
                "path_key": "intermediate",
                "match_percentage": 80,
                "reason": "Solid option for reviewing and filling gaps"
            },
            {
                "path_key": "hardware",
                "match_percentage": 85,
                "reason": "Deepen understanding of physical systems"
            }
        ]

    # Sort by match percentage
    recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)

    # Add path details
    for rec in recommendations:
        path_key = rec["path_key"]
        config = LEARNING_PATH_CONFIGS[path_key]
        rec.update({
            "name": config["name"],
            "description": config["description"],
            "chapters": config["chapters"],
            "estimated_hours": config["estimated_hours"],
            "prerequisites": config.get("prerequisites", []),
            "focus": config["focus"]
        })

    return recommendations


async def create_learning_path(
    db: AsyncSession,
    user_id: UUID,
    path_key: str
) -> LearningPath:
    """
    Create a learning path for user.

    Args:
        db: Database session
        user_id: User ID
        path_key: Key of path config to create

    Returns:
        Created LearningPath record

    Raises:
        ValueError: If path_key is invalid
    """
    if path_key not in LEARNING_PATH_CONFIGS:
        raise ValueError(f"Invalid path key: {path_key}")

    config = LEARNING_PATH_CONFIGS[path_key]

    # Check if user already has an active path
    existing = await get_active_learning_path(db, user_id)
    if existing:
        # Mark existing path as abandoned
        existing.status = "abandoned"

    # Create new path
    learning_path = LearningPath(
        user_id=user_id,
        path_name=config["name"],
        chapters_array=config["chapters"],
        completion_percentage=0,
        status="active"
    )

    db.add(learning_path)
    await db.commit()
    await db.refresh(learning_path)

    return learning_path


async def get_active_learning_path(
    db: AsyncSession,
    user_id: UUID
) -> Optional[LearningPath]:
    """
    Get user's active learning path.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Active LearningPath or None
    """
    result = await db.execute(
        select(LearningPath)
        .where(
            and_(
                LearningPath.user_id == user_id,
                LearningPath.status == "active"
            )
        )
        .order_by(LearningPath.created_at.desc())
        .limit(1)
    )

    return result.scalar_one_or_none()


async def get_all_user_paths(
    db: AsyncSession,
    user_id: UUID
) -> List[LearningPath]:
    """
    Get all learning paths for user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of all learning paths (active, completed, abandoned)
    """
    result = await db.execute(
        select(LearningPath)
        .where(LearningPath.user_id == user_id)
        .order_by(LearningPath.created_at.desc())
    )

    return list(result.scalars().all())


async def update_path_progress(
    db: AsyncSession,
    user_id: UUID,
    path_id: UUID
) -> Optional[LearningPath]:
    """
    Update learning path completion percentage based on progress.

    Args:
        db: Database session
        user_id: User ID
        path_id: Learning path ID

    Returns:
        Updated LearningPath or None

    Algorithm:
        - Count completed chapters in path
        - completion_percentage = (completed / total) * 100
        - Mark as 'completed' if 100%
    """
    # Get the path
    result = await db.execute(
        select(LearningPath)
        .where(
            and_(
                LearningPath.path_id == path_id,
                LearningPath.user_id == user_id
            )
        )
    )
    path = result.scalar_one_or_none()

    if not path:
        return None

    # Get user's progress for chapters in this path
    progress_result = await db.execute(
        select(Progress)
        .where(
            and_(
                Progress.user_id == user_id,
                Progress.chapter_id.in_(path.chapters_array),
                Progress.completion_status == "completed"
            )
        )
    )
    completed_progress = list(progress_result.scalars().all())

    # Calculate completion percentage
    total_chapters = len(path.chapters_array)
    completed_chapters = len(completed_progress)

    if total_chapters > 0:
        completion_pct = round((completed_chapters / total_chapters) * 100)
    else:
        completion_pct = 0

    path.completion_percentage = completion_pct

    # Mark as completed if 100%
    if completion_pct == 100:
        path.status = "completed"

    await db.commit()
    await db.refresh(path)

    return path


async def get_next_chapter_in_path(
    db: AsyncSession,
    user_id: UUID,
    path_id: UUID
) -> Optional[int]:
    """
    Get next uncompleted chapter in learning path.

    Args:
        db: Database session
        user_id: User ID
        path_id: Learning path ID

    Returns:
        Next chapter ID or None if all complete
    """
    # Get the path
    result = await db.execute(
        select(LearningPath).where(LearningPath.path_id == path_id)
    )
    path = result.scalar_one_or_none()

    if not path:
        return None

    # Get completed chapters
    progress_result = await db.execute(
        select(Progress.chapter_id)
        .where(
            and_(
                Progress.user_id == user_id,
                Progress.chapter_id.in_(path.chapters_array),
                Progress.completion_status == "completed"
            )
        )
    )
    completed_chapter_ids = {row[0] for row in progress_result.all()}

    # Find first uncompleted chapter in path order
    for chapter_id in path.chapters_array:
        if chapter_id not in completed_chapter_ids:
            return chapter_id

    return None  # All chapters completed


def get_path_config(path_key: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a learning path.

    Args:
        path_key: Path configuration key

    Returns:
        Path configuration dict or None
    """
    return LEARNING_PATH_CONFIGS.get(path_key)


def get_all_path_configs() -> Dict[str, Dict[str, Any]]:
    """
    Get all learning path configurations.

    Returns:
        Dict of all path configs
    """
    return LEARNING_PATH_CONFIGS.copy()
