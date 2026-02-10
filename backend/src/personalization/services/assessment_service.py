"""Assessment service for knowledge evaluation and skill scoring."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import KnowledgeAssessment, User


# Load assessment questions from JSON file
def _load_assessment_questions() -> List[Dict[str, Any]]:
    """Load assessment questions from JSON file."""
    current_dir = Path(__file__).parent.parent
    json_path = current_dir / "data" / "assessment_questions.json"

    if not json_path.exists():
        raise FileNotFoundError(f"Assessment questions file not found: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # Transform to internal format for backward compatibility
    transformed_questions = []
    for q in questions:
        # Find the correct option
        correct_option_idx = None
        option_texts = []
        points = 0

        for idx, opt in enumerate(q["options"]):
            option_texts.append(opt["text"])
            if opt["correct"]:
                correct_option_idx = idx
                points = opt["points"]

        # Convert to letter answer (A, B, C, D)
        answer_letters = ["A", "B", "C", "D", "E", "F"]
        correct_answer = answer_letters[correct_option_idx] if correct_option_idx is not None else "A"

        transformed_questions.append({
            "question_id": q["question_id"],
            "text": q["text"],
            "options": [f"{answer_letters[i]}) {opt}" for i, opt in enumerate(option_texts)],
            "correct_answer": correct_answer,
            "difficulty": q["difficulty"],
            "points": points
        })

    return transformed_questions


# Load questions at module initialization
ASSESSMENT_QUESTIONS = _load_assessment_questions()


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
