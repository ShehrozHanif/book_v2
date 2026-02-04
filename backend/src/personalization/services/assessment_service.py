"""Assessment service for knowledge evaluation and skill scoring."""

from typing import List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import KnowledgeAssessment, User


# Assessment question bank with 10 questions across difficulty levels
ASSESSMENT_QUESTIONS = [
    {
        "question_id": 1,
        "text": "What is the primary purpose of inverse kinematics in robotics?",
        "options": [
            "A) To calculate joint angles from desired end-effector position",
            "B) To calculate end-effector position from joint angles",
            "C) To optimize robot energy consumption",
            "D) To plan collision-free paths"
        ],
        "correct_answer": "A",
        "difficulty": "beginner",
        "points": 10
    },
    {
        "question_id": 2,
        "text": "Which of the following is NOT a common coordinate frame representation in robotics?",
        "options": [
            "A) Euler angles",
            "B) Quaternions",
            "C) Rotation matrices",
            "D) Fibonacci sequences"
        ],
        "correct_answer": "D",
        "difficulty": "beginner",
        "points": 10
    },
    {
        "question_id": 3,
        "text": "What does ZMP (Zero Moment Point) represent in bipedal robotics?",
        "options": [
            "A) The center of mass of the robot",
            "B) The point where net ground reaction moment is zero",
            "C) The highest point on the robot",
            "D) The midpoint between two feet"
        ],
        "correct_answer": "B",
        "difficulty": "intermediate",
        "points": 15
    },
    {
        "question_id": 4,
        "text": "In the Denavit-Hartenberg (DH) convention, how many parameters are used to describe each link?",
        "options": [
            "A) 2",
            "B) 3",
            "C) 4",
            "D") 6"
        ],
        "correct_answer": "C",
        "difficulty": "intermediate",
        "points": 15
    },
    {
        "question_id": 5,
        "text": "What is the main advantage of using Model Predictive Control (MPC) for robot locomotion?",
        "options": [
            "A) It requires no computation",
            "B) It can incorporate constraints and optimize over a time horizon",
            "C) It works without sensor feedback",
            "D) It only uses historical data"
        ],
        "correct_answer": "B",
        "difficulty": "advanced",
        "points": 20
    },
    {
        "question_id": 6,
        "text": "Which Python library is commonly used for numerical computation in robotics?",
        "options": [
            "A) pandas",
            "B) NumPy",
            "C) Flask",
            "D) Django"
        ],
        "correct_answer": "B",
        "difficulty": "beginner",
        "points": 10
    },
    {
        "question_id": 7,
        "text": "What is the purpose of a Jacobian matrix in robotics?",
        "options": [
            "A) To store robot configuration",
            "B) To relate joint velocities to end-effector velocities",
            "C) To represent sensor data",
            "D) To calculate robot weight"
        ],
        "correct_answer": "B",
        "difficulty": "intermediate",
        "points": 15
    },
    {
        "question_id": 8,
        "text": "In humanoid robotics, what is 'gait generation'?",
        "options": [
            "A) The process of designing robot appearance",
            "B) The creation of walking patterns and trajectories",
            "C) The manufacturing of robot joints",
            "D) The programming of speech synthesis"
        ],
        "correct_answer": "B",
        "difficulty": "beginner",
        "points": 10
    },
    {
        "question_id": 9,
        "text": "What challenge does the 'curse of dimensionality' present in robot motion planning?",
        "options": [
            "A) Robots become physically larger",
            "B) Computational complexity grows exponentially with degrees of freedom",
            "C) Robots move too slowly",
            "D) Sensors become less accurate"
        ],
        "correct_answer": "B",
        "difficulty": "advanced",
        "points": 20
    },
    {
        "question_id": 10,
        "text": "Which of the following is a key consideration for stable bipedal walking?",
        "options": [
            "A) Keeping the center of pressure within the support polygon",
            "B) Maximizing robot height",
            "C) Using only open-loop control",
            "D) Minimizing number of sensors"
        ],
        "correct_answer": "A",
        "difficulty": "intermediate",
        "points": 15
    }
]


def get_assessment_questions() -> List[Dict[str, Any]]:
    """
    Get assessment questions (without correct answers for client).

    Returns:
        List of assessment questions without correct answers
    """
    return [
        {
            "question_id": q["question_id"],
            "text": q["text"],
            "options": q["options"],
            "difficulty": q["difficulty"]
        }
        for q in ASSESSMENT_QUESTIONS
    ]


def calculate_skill_score(answers: List[Dict[str, Any]]) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Calculate skill score based on assessment answers.

    Args:
        answers: List of dicts with 'question_id' and 'answer' keys

    Returns:
        Tuple of (skill_score: int 0-100, graded_questions: List)

    Algorithm:
        - Each question has points based on difficulty
        - Score = (total_earned_points / total_possible_points) * 100
        - Rounds to nearest integer
    """
    # Create answer lookup
    answer_lookup = {ans["question_id"]: ans["answer"] for ans in answers}

    total_points = sum(q["points"] for q in ASSESSMENT_QUESTIONS)
    earned_points = 0
    graded_questions = []

    for question in ASSESSMENT_QUESTIONS:
        q_id = question["question_id"]
        user_answer = answer_lookup.get(q_id, "")
        correct_answer = question["correct_answer"]
        is_correct = (user_answer == correct_answer)

        if is_correct:
            earned_points += question["points"]

        graded_questions.append({
            "question_id": q_id,
            "text": question["text"],
            "options": question["options"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "correct": is_correct,
            "difficulty": question["difficulty"],
            "points_earned": question["points"] if is_correct else 0,
            "points_possible": question["points"]
        })

    # Calculate percentage score
    skill_score = round((earned_points / total_points) * 100)

    return skill_score, graded_questions


def determine_skill_tier(skill_score: int) -> str:
    """
    Determine skill tier based on score.

    Args:
        skill_score: Score from 0-100

    Returns:
        Skill tier: 'beginner', 'intermediate', or 'advanced'

    Tiers:
        - 0-49: beginner
        - 50-74: intermediate
        - 75-100: advanced
    """
    if skill_score < 50:
        return "beginner"
    elif skill_score < 75:
        return "intermediate"
    else:
        return "advanced"


async def create_assessment(
    db: AsyncSession,
    user_id: UUID,
    answers: List[Dict[str, Any]]
) -> Tuple[KnowledgeAssessment, int, str]:
    """
    Create knowledge assessment record and calculate skill score.

    Args:
        db: Database session
        user_id: User ID
        answers: List of user answers

    Returns:
        Tuple of (assessment_record, skill_score, skill_tier)
    """
    # Calculate score
    skill_score, graded_questions = calculate_skill_score(answers)
    skill_tier = determine_skill_tier(skill_score)

    # Create assessment record
    assessment = KnowledgeAssessment(
        user_id=user_id,
        questions_json={"questions": graded_questions},
        calculated_skill_score=skill_score
    )

    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    return assessment, skill_score, skill_tier


async def get_user_assessments(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 10
) -> List[KnowledgeAssessment]:
    """
    Get user's assessment history.

    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of assessments to return

    Returns:
        List of assessment records, newest first
    """
    result = await db.execute(
        select(KnowledgeAssessment)
        .where(KnowledgeAssessment.user_id == user_id)
        .order_by(KnowledgeAssessment.created_at.desc())
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_latest_assessment(
    db: AsyncSession,
    user_id: UUID
) -> KnowledgeAssessment:
    """
    Get user's most recent assessment.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Latest assessment record or None
    """
    result = await db.execute(
        select(KnowledgeAssessment)
        .where(KnowledgeAssessment.user_id == user_id)
        .order_by(KnowledgeAssessment.created_at.desc())
        .limit(1)
    )

    return result.scalar_one_or_none()


def calculate_assessment_statistics(assessments: List[KnowledgeAssessment]) -> Dict[str, Any]:
    """
    Calculate statistics from assessment history.

    Args:
        assessments: List of assessment records

    Returns:
        Dict with statistics (avg_score, improvement, etc.)
    """
    if not assessments:
        return {
            "total_assessments": 0,
            "average_score": 0,
            "best_score": 0,
            "latest_score": 0,
            "improvement": 0
        }

    scores = [a.calculated_skill_score for a in assessments]

    return {
        "total_assessments": len(assessments),
        "average_score": round(sum(scores) / len(scores), 1),
        "best_score": max(scores),
        "latest_score": scores[0] if scores else 0,
        "improvement": scores[0] - scores[-1] if len(scores) > 1 else 0
    }
