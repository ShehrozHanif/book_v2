"""Practice service for generating and tracking practice questions."""

import logging
import random
from typing import Dict, List, Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personalization.models.db_models import PracticeAttempt, Progress
from src.personalization.services.user_service import get_user_by_id

logger = logging.getLogger(__name__)


# Sample practice questions by chapter (would be generated from Qdrant in production)
PRACTICE_QUESTIONS_BY_CHAPTER = {
    1: [
        {
            "id": "q1_1",
            "question": "What is robotics?",
            "options": [
                {"letter": "A", "text": "The study of robots and automation", "correct": True},
                {"letter": "B", "text": "Only manufacturing robots", "correct": False},
                {"letter": "C", "text": "Computer programming", "correct": False},
                {"letter": "D", "text": "Mechanical engineering only", "correct": False}
            ],
            "difficulty": "beginner"
        },
        {
            "id": "q1_2",
            "question": "Which of the following is NOT a component of a robot?",
            "options": [
                {"letter": "A", "text": "Actuators", "correct": False},
                {"letter": "B", "text": "Sensors", "correct": False},
                {"letter": "C", "text": "Controller", "correct": False},
                {"letter": "D", "text": "Wheel alignment", "correct": True}
            ],
            "difficulty": "beginner"
        }
    ],
    2: [
        {
            "id": "q2_1",
            "question": "What is forward kinematics?",
            "options": [
                {"letter": "A", "text": "Computing joint positions from end-effector", "correct": False},
                {"letter": "B", "text": "Computing end-effector position from joint angles", "correct": True},
                {"letter": "C", "text": "Computing robot dynamics", "correct": False},
                {"letter": "D", "text": "Computing torques from velocities", "correct": False}
            ],
            "difficulty": "intermediate"
        }
    ]
}


class PracticeService:
    """Service for managing practice questions and attempts."""

    def __init__(self, db: AsyncSession):
        """
        Initialize practice service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_practice_questions(self,
                                    chapter_id: int,
                                    limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get practice questions for a chapter.

        Args:
            chapter_id: Chapter ID
            limit: Maximum number of questions to return

        Returns:
            List of practice questions
        """
        # In production, would retrieve from Qdrant or database
        questions = PRACTICE_QUESTIONS_BY_CHAPTER.get(chapter_id, [])

        if not questions:
            logger.warning(f"No practice questions found for chapter {chapter_id}")
            # Return placeholder questions
            questions = [
                {
                    "id": f"q{chapter_id}_{i}",
                    "question": f"Sample question {i+1} for Chapter {chapter_id}",
                    "options": [
                        {"letter": "A", "text": "Option 1", "correct": True},
                        {"letter": "B", "text": "Option 2", "correct": False},
                        {"letter": "C", "text": "Option 3", "correct": False},
                        {"letter": "D", "text": "Option 4", "correct": False}
                    ],
                    "difficulty": "beginner"
                }
                for i in range(min(limit, 5))
            ]

        return questions[:limit]

    def calculate_score(self,
                       questions: List[Dict[str, Any]],
                       answers: Dict[str, str]) -> int:
        """
        Calculate practice attempt score.

        Args:
            questions: List of questions asked
            answers: Dictionary mapping question IDs to selected answers

        Returns:
            Score 0-100
        """
        if not questions:
            return 0

        correct_count = 0
        for question in questions:
            question_id = question.get("id")
            if question_id not in answers:
                continue

            selected_answer = answers[question_id]

            # Find correct answer
            correct_option = next(
                (opt for opt in question.get("options", []) if opt.get("correct")),
                None
            )

            if correct_option and correct_option.get("letter") == selected_answer:
                correct_count += 1

        score = int((correct_count / len(questions)) * 100) if questions else 0
        return max(0, min(100, score))  # Clamp to 0-100

    async def save_practice_attempt(self,
                                   user_id: UUID,
                                   chapter_id: int,
                                   questions: List[Dict[str, Any]],
                                   answers: Dict[str, str]) -> Optional[PracticeAttempt]:
        """
        Save a practice attempt.

        Args:
            user_id: User ID
            chapter_id: Chapter ID
            questions: Questions that were asked
            answers: User's answers

        Returns:
            PracticeAttempt record if successful
        """
        score = self.calculate_score(questions, answers)

        attempt = PracticeAttempt(
            user_id=user_id,
            chapter_id=chapter_id,
            questions_json={
                "questions": [
                    {
                        "id": q.get("id"),
                        "question": q.get("question"),
                        "difficulty": q.get("difficulty")
                    }
                    for q in questions
                ],
                "total": len(questions)
            },
            score=score
        )

        self.db.add(attempt)

        # Update progress record with highest practice score
        progress = await self.db.execute(
            select(Progress).where(
                (Progress.user_id == user_id) & (Progress.chapter_id == chapter_id)
            )
        )
        record = progress.scalar_one_or_none()

        if record:
            record.practice_attempts += 1
            if score > record.highest_practice_score:
                record.highest_practice_score = score
                # Update mastery score based on practice score
                record.mastery_score = int((record.mastery_score + score) / 2)

        await self.db.commit()
        await self.db.refresh(attempt)

        logger.info(f"Practice attempt saved: user={user_id}, chapter={chapter_id}, score={score}")

        return attempt

    async def get_chapter_practice_history(self,
                                          user_id: UUID,
                                          chapter_id: int) -> Dict[str, Any]:
        """
        Get practice history for a user's chapter.

        Args:
            user_id: User ID
            chapter_id: Chapter ID

        Returns:
            Dictionary with practice statistics
        """
        attempts = await self.db.execute(
            select(PracticeAttempt).where(
                (PracticeAttempt.user_id == user_id) &
                (PracticeAttempt.chapter_id == chapter_id)
            )
        )
        records = attempts.scalars().all()

        if not records:
            return {
                "attempts": 0,
                "avg_score": 0,
                "best_score": 0,
                "history": []
            }

        scores = [r.score for r in records]

        return {
            "attempts": len(records),
            "avg_score": int(sum(scores) / len(scores)),
            "best_score": max(scores),
            "history": [
                {
                    "attempt_number": i + 1,
                    "score": r.score,
                    "date": r.attempted_at.isoformat() if r.attempted_at else None,
                    "question_count": r.questions_json.get("total", 0)
                }
                for i, r in enumerate(records)
            ]
        }

    async def recommend_practice(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get practice recommendation for user.

        Args:
            user_id: User ID

        Returns:
            Recommended chapter for practice or None
        """
        # Find chapters with lowest mastery or not completed
        progress_records = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        records = progress_records.scalars().all()

        if not records:
            return None

        # Sort by mastery score (ascending) and completion status
        sorted_chapters = sorted(
            records,
            key=lambda p: (p.mastery_score, p.completion_status != "in_progress")
        )

        if sorted_chapters and sorted_chapters[0].mastery_score < 80:
            chapter = sorted_chapters[0]
            return {
                "chapter_id": chapter.chapter_id,
                "reason": f"Low mastery score ({chapter.mastery_score}%)",
                "suggested_difficulty": (
                    "beginner" if chapter.mastery_score < 40 else
                    "intermediate" if chapter.mastery_score < 60 else
                    "advanced"
                )
            }

        return None


async def get_practice_service(db: AsyncSession) -> PracticeService:
    """
    Get practice service instance.

    Args:
        db: Database session

    Returns:
        PracticeService instance
    """
    return PracticeService(db)
