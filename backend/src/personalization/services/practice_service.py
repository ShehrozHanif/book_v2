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
        },
        {
            "id": "q1_adv_1",
            "question": "How do biomimetic robotics principles compare to traditional industrial robotics in terms of adaptability?",
            "options": [
                {"letter": "A", "text": "Biomimetic systems provide superior adaptability to unstructured environments", "correct": True},
                {"letter": "B", "text": "Traditional robotics are always more adaptable", "correct": False},
                {"letter": "C", "text": "Adaptability is independent of design philosophy", "correct": False},
                {"letter": "D", "text": "This comparison is not relevant to modern robotics", "correct": False}
            ],
            "difficulty": "advanced"
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
        },
        {
            "id": "q2_adv_1",
            "question": "What are the computational complexity implications of solving inverse kinematics using numerical methods versus analytical solutions?",
            "options": [
                {"letter": "A", "text": "Numerical methods are always faster", "correct": False},
                {"letter": "B", "text": "Analytical solutions have deterministic complexity but limited solvability", "correct": True},
                {"letter": "C", "text": "There is no meaningful difference in complexity", "correct": False},
                {"letter": "D", "text": "Complexity depends only on the number of DOF", "correct": False}
            ],
            "difficulty": "advanced"
        }
    ]
}

# Research paper summaries for advanced learners (high mastery chapters)
RESEARCH_PAPERS_BY_CHAPTER = {
    1: [
        {
            "id": "paper1_1",
            "title": "A Survey of Robotics Research and Applications",
            "authors": "IEEE Robotics and Automation Society",
            "year": 2022,
            "key_concepts": ["Robotics history", "Current applications", "Future trends"],
            "summary": "Comprehensive overview of robotics field covering historical development, current state-of-the-art applications, and emerging research directions",
            "difficulty": "advanced",
            "relevance_to_chapter": 0.95
        }
    ],
    2: [
        {
            "id": "paper2_1",
            "title": "Analytical and Numerical Methods in Robot Kinematics",
            "authors": "International Journal of Robotics Research",
            "year": 2023,
            "key_concepts": ["Kinematics solutions", "Computational efficiency", "Real-time computation"],
            "summary": "Detailed analysis of forward and inverse kinematics solution methods with performance benchmarks",
            "difficulty": "advanced",
            "relevance_to_chapter": 0.98
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

    async def check_advanced_challenges_eligibility(self,
                                                   user_id: UUID,
                                                   chapter_id: int) -> bool:
        """
        Check if user is eligible for advanced challenges (mastery > 85%).

        Args:
            user_id: User ID
            chapter_id: Chapter ID

        Returns:
            True if user mastery is > 85%, False otherwise
        """
        progress = await self.db.execute(
            select(Progress).where(
                (Progress.user_id == user_id) & (Progress.chapter_id == chapter_id)
            )
        )
        record = progress.scalar_one_or_none()

        if not record:
            return False

        return record.mastery_score > 85

    async def get_advanced_challenges(self,
                                     user_id: UUID,
                                     chapter_id: int) -> Optional[Dict[str, Any]]:
        """
        Get advanced challenges for high mastery chapters (>85% mastery).

        Advanced challenges include research paper summaries and advanced practice questions.

        Args:
            user_id: User ID
            chapter_id: Chapter ID (1-22)

        Returns:
            Dictionary with advanced challenges or None if not eligible
        """
        # Check eligibility
        eligible = await self.check_advanced_challenges_eligibility(user_id, chapter_id)
        if not eligible:
            return None

        # Get research papers for the chapter
        papers = RESEARCH_PAPERS_BY_CHAPTER.get(chapter_id, [])

        # Get advanced practice questions
        all_questions = PRACTICE_QUESTIONS_BY_CHAPTER.get(chapter_id, [])
        advanced_questions = [q for q in all_questions if q.get("difficulty") == "advanced"]

        # If no advanced questions, generate placeholders
        if not advanced_questions:
            advanced_questions = [
                {
                    "id": f"q{chapter_id}_adv_{i}",
                    "question": f"Advanced question {i+1}: Analyze the research implications of concepts in Chapter {chapter_id}",
                    "options": [
                        {"letter": "A", "text": "Complex scenario 1", "correct": True},
                        {"letter": "B", "text": "Complex scenario 2", "correct": False},
                        {"letter": "C", "text": "Complex scenario 3", "correct": False},
                        {"letter": "D", "text": "Complex scenario 4", "correct": False}
                    ],
                    "difficulty": "advanced"
                }
                for i in range(1, 4)
            ]

        # Generate placeholder papers if none exist
        if not papers:
            papers = [
                {
                    "id": f"paper{chapter_id}_{i}",
                    "title": f"Advanced Research in Chapter {chapter_id}",
                    "authors": "Research Team",
                    "year": 2024,
                    "key_concepts": ["Advanced topic 1", "Advanced topic 2", "Advanced topic 3"],
                    "summary": f"Research summary for Chapter {chapter_id}",
                    "difficulty": "advanced",
                    "relevance_to_chapter": 0.9
                }
                for i in range(1, 2)
            ]

        logger.info(f"Advanced challenges retrieved: user={user_id}, chapter={chapter_id}, questions={len(advanced_questions)}, papers={len(papers)}")

        return {
            "chapter_id": chapter_id,
            "user_mastery": (await self.db.execute(
                select(Progress).where(
                    (Progress.user_id == user_id) & (Progress.chapter_id == chapter_id)
                )
            )).scalar_one_or_none().mastery_score,
            "advanced_questions": advanced_questions,
            "research_papers": papers,
            "challenge_type": "advanced_mastery",
            "total_questions": len(advanced_questions),
            "total_papers": len(papers)
        }


async def get_practice_service(db: AsyncSession) -> PracticeService:
    """
    Get practice service instance.

    Args:
        db: Database session

    Returns:
        PracticeService instance
    """
    return PracticeService(db)
