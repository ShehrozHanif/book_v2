"""Pydantic schemas for personalization API contracts."""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from uuid import UUID


# User schemas
class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "username": "robotics_learner",
            "email": "user@example.com",
            "password": "SecurePass123!"
        }
    })


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }
    })


class UserPreferences(BaseModel):
    """Schema for user learning preferences."""
    explanation_style: Literal["theory_first", "example_first"] = Field(default="example_first")
    code_language: Literal["python", "cpp", "both"] = Field(default="python")
    learning_pace: Literal["slow", "medium", "fast"] = Field(default="medium")
    content_focus: Literal["simulation", "hardware", "balanced"] = Field(default="balanced")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "explanation_style": "example_first",
            "code_language": "python",
            "learning_pace": "medium",
            "content_focus": "balanced"
        }
    })


class UserProfile(BaseModel):
    """Schema for user profile data."""
    user_id: UUID
    username: str
    email: EmailStr
    skill_level: int = Field(..., ge=0, le=100)
    skill_confidence: int = Field(..., ge=0, le=100)
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: UserPreferences
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Schema for user registration/login response."""
    user_id: UUID
    username: str
    email: EmailStr
    message: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "robotics_learner",
            "email": "user@example.com",
            "message": "Registration successful"
        }
    })


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user_id: UUID
    username: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "robotics_learner"
        }
    })


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    bio: Optional[str] = Field(None, max_length=500)
    profile_picture_url: Optional[str] = None
    preferences: Optional[UserPreferences] = None


# Assessment schemas
class AssessmentQuestion(BaseModel):
    """Schema for a single assessment question."""
    question_id: int
    text: str
    options: List[str]
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    correct: Optional[bool] = None
    difficulty: Literal["beginner", "intermediate", "advanced"] = "intermediate"


class AssessmentRequest(BaseModel):
    """Schema for submitting assessment answers."""
    answers: List[Dict[str, Any]] = Field(..., description="List of question_id and answer pairs")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "answers": [
                {"question_id": 1, "answer": "A"},
                {"question_id": 2, "answer": "C"},
                {"question_id": 3, "answer": "B"}
            ]
        }
    })

    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v):
        """Validate answers list."""
        if not v:
            raise ValueError("Answers list cannot be empty")
        for answer in v:
            if 'question_id' not in answer or 'answer' not in answer:
                raise ValueError("Each answer must have 'question_id' and 'answer' fields")
        return v


class PathRecommendation(BaseModel):
    """Schema for learning path recommendation."""
    path_id: Optional[UUID] = None
    name: str
    match_percentage: int = Field(..., ge=0, le=100)
    description: Optional[str] = None
    chapters: List[int]
    estimated_hours: Optional[int] = None


class AssessmentResponse(BaseModel):
    """Schema for assessment submission response."""
    assessment_id: UUID
    skill_score: int = Field(..., ge=0, le=100)
    skill_tier: Literal["beginner", "intermediate", "advanced"]
    recommended_paths: List[PathRecommendation]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
            "skill_score": 72,
            "skill_tier": "intermediate",
            "recommended_paths": [
                {
                    "name": "Developer Path",
                    "match_percentage": 85,
                    "chapters": [1, 2, 6, 7, 8, 9],
                    "estimated_hours": 40
                }
            ]
        }
    })


# Learning path schemas
class LearningPathCreate(BaseModel):
    """Schema for creating a learning path."""
    path_name: str
    chapters: List[int] = Field(..., min_length=1)

    @field_validator('chapters')
    @classmethod
    def validate_chapters(cls, v):
        """Validate chapter IDs are in valid range."""
        for chapter_id in v:
            if not (1 <= chapter_id <= 22):
                raise ValueError(f"Chapter ID {chapter_id} must be between 1 and 22")
        return v


class LearningPathResponse(BaseModel):
    """Schema for learning path response."""
    path_id: UUID
    user_id: UUID
    path_name: str
    chapters: List[int]
    completion_percentage: int = Field(..., ge=0, le=100)
    status: Literal["active", "completed", "abandoned"]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Progress schemas
class ProgressTrack(BaseModel):
    """Schema for tracking time on a chapter."""
    time_spent_seconds: int = Field(..., ge=0, description="Time increment in seconds")


class ProgressComplete(BaseModel):
    """Schema for marking chapter complete."""
    mastery_score: int = Field(..., ge=0, le=100, description="Mastery score for the chapter")
    time_spent_seconds: Optional[int] = Field(None, ge=0, description="Optional final time spent")


class ProgressResponse(BaseModel):
    """Schema for progress data response."""
    progress_id: UUID
    user_id: UUID
    chapter_id: int
    completion_status: Literal["not_started", "in_progress", "completed"]
    time_spent_seconds: int
    mastery_score: int
    last_accessed_at: datetime
    practice_attempts: int
    highest_practice_score: int

    model_config = ConfigDict(from_attributes=True)


class AchievementInfo(BaseModel):
    """Schema for achievement display info."""
    title: str
    description: str
    icon_url: Optional[str] = None
    points: int = 0


class ChapterCompleteResponse(BaseModel):
    """Schema for chapter completion response."""
    status: str = "completed"
    achievement_unlocked: Optional[AchievementInfo] = None
    next_recommendation: Optional[Dict[str, Any]] = None


# Dashboard schemas
class DashboardResponse(BaseModel):
    """Schema for user progress dashboard."""
    chapters_completed: int
    modules_completed: int
    total_learning_time_hours: float
    current_skill_level: int
    current_path: Optional[LearningPathResponse] = None
    achievements: List[Dict[str, Any]]
    learning_statistics: Dict[str, Any]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "chapters_completed": 5,
            "modules_completed": 1,
            "total_learning_time_hours": 12.5,
            "current_skill_level": 72,
            "current_path": {
                "path_name": "Developer Path",
                "completion_percentage": 32,
                "next_chapter_id": 9
            },
            "achievements": [
                {
                    "title": "Mastered Kinematics",
                    "earned_date": "2026-02-01T10:30:00Z"
                }
            ],
            "learning_statistics": {
                "time_per_chapter": {"1": 120, "2": 150},
                "mastery_per_chapter": {"1": 85, "2": 78}
            }
        }
    })


# Achievement schemas
class AchievementResponse(BaseModel):
    """Schema for achievement response."""
    achievement_id: UUID
    user_id: UUID
    achievement_type: str
    earned_date: datetime
    display_info: AchievementInfo

    model_config = ConfigDict(from_attributes=True)


# Practice schemas
class PracticeQuestion(BaseModel):
    """Schema for practice question."""
    question_id: int
    text: str
    options: List[str]
    chapter_id: int


class PracticeAttemptRequest(BaseModel):
    """Schema for submitting practice attempt."""
    answers: List[Dict[str, Any]] = Field(..., description="List of question_id and answer pairs")

    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v):
        """Validate answers list."""
        if not v:
            raise ValueError("Answers list cannot be empty")
        return v


class PracticeAttemptResponse(BaseModel):
    """Schema for practice attempt response."""
    attempt_id: UUID
    score: int = Field(..., ge=0, le=100)
    questions: List[PracticeQuestion]
    user_answers: List[str]
    correct_answers: List[str]
    feedback: Optional[str] = None


# Statistics schemas
class LearningStatistics(BaseModel):
    """Schema for learning statistics response."""
    time_per_chapter: Dict[str, int]
    mastery_per_chapter: Dict[str, int]
    learning_curve: List[Dict[str, Any]]
    recommended_focus_areas: List[Dict[str, Any]]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "time_per_chapter": {"1": 120, "2": 150, "3": 180},
            "mastery_per_chapter": {"1": 85, "2": 78, "3": 92},
            "learning_curve": [
                {"date": "2026-01-01", "skill_level": 50},
                {"date": "2026-01-15", "skill_level": 65}
            ],
            "recommended_focus_areas": [
                {"chapter_id": 5, "reason": "Low mastery (58%)", "priority": "high"}
            ]
        }
    })


# Chat personalization schemas
class ChatRequest(BaseModel):
    """Schema for chat request with personalization."""
    query: str = Field(..., min_length=1, max_length=2000)
    user_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    difficulty_override: Optional[Literal["beginner", "intermediate", "advanced"]] = None


class ChatResponse(BaseModel):
    """Schema for chat response with personalization."""
    response: str
    conversation_id: UUID
    difficulty_level_used: Literal["beginner", "intermediate", "advanced"]
    retrieved_chapters: List[int]
    processing_time_ms: int
    user_personalization_applied: bool
