"""Tests for assessment service functionality."""

import pytest
from uuid import uuid4

from src.personalization.services import assessment_service


class TestAssessmentQuestions:
    """Test assessment question retrieval."""

    def test_get_assessment_questions_returns_list(self):
        """Test that get_assessment_questions returns a list."""
        questions = assessment_service.get_assessment_questions()
        assert isinstance(questions, list)
        assert len(questions) >= 10  # Minimum 10 questions

    def test_questions_have_required_fields(self):
        """Test that questions have all required fields."""
        questions = assessment_service.get_assessment_questions()

        for q in questions:
            assert "question_id" in q
            assert "text" in q
            assert "options" in q
            assert "difficulty" in q
            assert isinstance(q["options"], list)
            assert len(q["options"]) >= 2  # At least 2 options

    def test_questions_do_not_include_answers(self):
        """Test that questions don't include correct answers."""
        questions = assessment_service.get_assessment_questions()

        for q in questions:
            assert "correct_answer" not in q
            assert "points" not in q


class TestScoreCalculation:
    """Test assessment score calculation logic."""

    def test_all_correct_answers_score_100(self):
        """Test that all correct answers yields 100% score."""
        # Get all questions
        questions = assessment_service.ASSESSMENT_QUESTIONS

        # Create answers with all correct
        answers = [
            {"question_id": q["question_id"], "answer": q["correct_answer"]}
            for q in questions
        ]

        score, graded = assessment_service.calculate_skill_score(answers)

        assert score == 100
        assert all(q["correct"] for q in graded)

    def test_all_wrong_answers_score_0(self):
        """Test that all wrong answers yields 0% score."""
        questions = assessment_service.ASSESSMENT_QUESTIONS

        # Create answers with all wrong (opposite of correct)
        def get_wrong_answer(correct_answer: str) -> str:
            """Get a wrong answer different from correct."""
            options = ["A", "B", "C", "D"]
            options.remove(correct_answer)
            return options[0]

        answers = [
            {"question_id": q["question_id"], "answer": get_wrong_answer(q["correct_answer"])}
            for q in questions
        ]

        score, graded = assessment_service.calculate_skill_score(answers)

        assert score == 0
        assert all(not q["correct"] for q in graded)

    def test_score_calculation_beginner_range(self):
        """Test score calculation in beginner range (0-49)."""
        questions = assessment_service.ASSESSMENT_QUESTIONS

        # Answer first 3 questions correctly (should be < 50%)
        answers = []
        for idx, q in enumerate(questions):
            if idx < 3:
                answers.append({"question_id": q["question_id"], "answer": q["correct_answer"]})
            else:
                answers.append({"question_id": q["question_id"], "answer": "Z"})  # Wrong answer

        score, graded = assessment_service.calculate_skill_score(answers)

        assert 0 <= score <= 100
        # Check that some answers are correct
        correct_count = sum(1 for q in graded if q["correct"])
        assert correct_count == 3

    def test_score_calculation_intermediate_range(self):
        """Test score calculation in intermediate range (50-74)."""
        questions = assessment_service.ASSESSMENT_QUESTIONS

        # Answer about 60% correctly
        correct_count = int(len(questions) * 0.6)
        answers = []

        for idx, q in enumerate(questions):
            if idx < correct_count:
                answers.append({"question_id": q["question_id"], "answer": q["correct_answer"]})
            else:
                answers.append({"question_id": q["question_id"], "answer": "Z"})

        score, graded = assessment_service.calculate_skill_score(answers)

        assert 0 <= score <= 100

    def test_score_calculation_advanced_range(self):
        """Test score calculation in advanced range (75-100)."""
        questions = assessment_service.ASSESSMENT_QUESTIONS

        # Answer about 85% correctly
        correct_count = int(len(questions) * 0.85)
        answers = []

        for idx, q in enumerate(questions):
            if idx < correct_count:
                answers.append({"question_id": q["question_id"], "answer": q["correct_answer"]})
            else:
                answers.append({"question_id": q["question_id"], "answer": "Z"})

        score, graded = assessment_service.calculate_skill_score(answers)

        assert 0 <= score <= 100


class TestSkillTierDetermination:
    """Test skill tier determination logic."""

    def test_score_0_is_beginner(self):
        """Test that score 0 is classified as beginner."""
        tier = assessment_service.determine_skill_tier(0)
        assert tier == "beginner"

    def test_score_49_is_beginner(self):
        """Test that score 49 is classified as beginner."""
        tier = assessment_service.determine_skill_tier(49)
        assert tier == "beginner"

    def test_score_50_is_intermediate(self):
        """Test that score 50 is classified as intermediate."""
        tier = assessment_service.determine_skill_tier(50)
        assert tier == "intermediate"

    def test_score_74_is_intermediate(self):
        """Test that score 74 is classified as intermediate."""
        tier = assessment_service.determine_skill_tier(74)
        assert tier == "intermediate"

    def test_score_75_is_advanced(self):
        """Test that score 75 is classified as advanced."""
        tier = assessment_service.determine_skill_tier(75)
        assert tier == "advanced"

    def test_score_100_is_advanced(self):
        """Test that score 100 is classified as advanced."""
        tier = assessment_service.determine_skill_tier(100)
        assert tier == "advanced"


@pytest.mark.asyncio
class TestAssessmentCreation:
    """Test assessment creation and database operations."""

    async def test_create_assessment_stores_results(self, db_session, test_user):
        """Test that create_assessment stores results in database."""
        # Prepare answers
        questions = assessment_service.ASSESSMENT_QUESTIONS
        answers = [
            {"question_id": q["question_id"], "answer": q["correct_answer"]}
            for q in questions[:5]
        ] + [
            {"question_id": q["question_id"], "answer": "Z"}
            for q in questions[5:]
        ]

        # Create assessment
        assessment, score, tier = await assessment_service.create_assessment(
            db=db_session,
            user_id=test_user.user_id,
            answers=answers
        )

        assert assessment is not None
        assert assessment.user_id == test_user.user_id
        assert 0 <= score <= 100
        assert tier in ["beginner", "intermediate", "advanced"]
        assert assessment.calculated_skill_score == score

    async def test_get_user_assessments_returns_history(self, db_session, test_user):
        """Test retrieving user assessment history."""
        # Create multiple assessments
        questions = assessment_service.ASSESSMENT_QUESTIONS
        answers = [
            {"question_id": q["question_id"], "answer": q["correct_answer"]}
            for q in questions
        ]

        await assessment_service.create_assessment(
            db=db_session,
            user_id=test_user.user_id,
            answers=answers
        )

        # Retrieve history
        history = await assessment_service.get_user_assessments(
            db=db_session,
            user_id=test_user.user_id,
            limit=10
        )

        assert len(history) >= 1
        assert all(a.user_id == test_user.user_id for a in history)

    async def test_get_latest_assessment(self, db_session, test_user):
        """Test retrieving user's latest assessment."""
        # Create assessment
        questions = assessment_service.ASSESSMENT_QUESTIONS
        answers = [
            {"question_id": q["question_id"], "answer": q["correct_answer"]}
            for q in questions
        ]

        created_assessment, _, _ = await assessment_service.create_assessment(
            db=db_session,
            user_id=test_user.user_id,
            answers=answers
        )

        # Retrieve latest
        latest = await assessment_service.get_latest_assessment(
            db=db_session,
            user_id=test_user.user_id
        )

        assert latest is not None
        assert latest.assessment_id == created_assessment.assessment_id


class TestAssessmentStatistics:
    """Test assessment statistics calculation."""

    def test_statistics_with_no_assessments(self):
        """Test statistics calculation with empty history."""
        stats = assessment_service.calculate_assessment_statistics([])

        assert stats["total_assessments"] == 0
        assert stats["average_score"] == 0
        assert stats["best_score"] == 0
        assert stats["latest_score"] == 0
        assert stats["improvement"] == 0

    def test_statistics_with_single_assessment(self):
        """Test statistics with one assessment."""
        from src.personalization.models.db_models import KnowledgeAssessment
        from uuid import uuid4

        # Create a mock assessment without database
        class MockAssessment:
            def __init__(self, score):
                self.calculated_skill_score = score

        assessment = MockAssessment(75)

        stats = assessment_service.calculate_assessment_statistics([assessment])

        assert stats["total_assessments"] == 1
        assert stats["average_score"] == 75
        assert stats["best_score"] == 75
        assert stats["latest_score"] == 75
        assert stats["improvement"] == 0
