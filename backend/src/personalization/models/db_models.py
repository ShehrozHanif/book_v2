"""SQLAlchemy ORM models for personalization feature."""

from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import (
    Column, String, Integer, Text, TIMESTAMP, ForeignKey,
    CheckConstraint, UniqueConstraint, Index, ARRAY
)
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base
import uuid
import re

Base = declarative_base()


class User(Base):
    """User model for authentication and profile data."""

    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    skill_level = Column(Integer, default=50, nullable=False)
    skill_confidence = Column(Integer, default=50, nullable=False)
    is_admin = Column(Integer, default=0, nullable=False)
    profile_picture_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    preferences_json = Column(JSON, default={
        "explanation_style": "example_first",
        "code_language": "python",
        "learning_pace": "medium",
        "content_focus": "balanced"
    }, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    assessments = relationship("KnowledgeAssessment", back_populates="user", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    practice_attempts = relationship("PracticeAttempt", back_populates="user", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint('skill_level >= 0 AND skill_level <= 100', name='check_skill_level_range'),
        CheckConstraint('skill_confidence >= 0 AND skill_confidence <= 100', name='check_skill_confidence_range'),
        CheckConstraint('length(username) >= 3 AND length(username) <= 50', name='check_username_length'),
        Index('idx_users_deleted_at', 'deleted_at'),
    )

    @validates('email')
    def validate_email(self, key, email):
        """Validate email format."""
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        if not re.match(pattern, email, re.IGNORECASE):
            raise ValueError(f"Invalid email format: {email}")
        return email.lower()

    @validates('skill_level', 'skill_confidence')
    def validate_score_range(self, key, value):
        """Validate score is in 0-100 range."""
        if not (0 <= value <= 100):
            raise ValueError(f"{key} must be between 0 and 100")
        return value

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "user_id": str(self.user_id),
            "username": self.username,
            "email": self.email,
            "skill_level": self.skill_level,
            "skill_confidence": self.skill_confidence,
            "profile_picture_url": self.profile_picture_url,
            "bio": self.bio,
            "preferences": self.preferences_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, skill_level={self.skill_level})>"


class KnowledgeAssessment(Base):
    """Knowledge assessment model for skill evaluation."""

    __tablename__ = "knowledge_assessments"

    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    questions_json = Column(JSON, nullable=False)
    calculated_skill_score = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="assessments")

    # Constraints
    __table_args__ = (
        CheckConstraint('calculated_skill_score >= 0 AND calculated_skill_score <= 100', name='check_assessment_score_range'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        return {
            "assessment_id": str(self.assessment_id),
            "user_id": str(self.user_id),
            "questions": self.questions_json,
            "calculated_skill_score": self.calculated_skill_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<KnowledgeAssessment(assessment_id={self.assessment_id}, score={self.calculated_skill_score})>"


class LearningPath(Base):
    """Learning path model for personalized learning journeys."""

    __tablename__ = "learning_paths"

    path_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    path_name = Column(String(100), nullable=False)
    chapters_array = Column(ARRAY(Integer), nullable=False)
    completion_percentage = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default='active', nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="learning_paths")

    # Constraints
    __table_args__ = (
        CheckConstraint('completion_percentage >= 0 AND completion_percentage <= 100', name='check_completion_range'),
        CheckConstraint("status IN ('active', 'completed', 'abandoned')", name='check_status_values'),
    )

    @validates('status')
    def validate_status(self, key, status):
        """Validate status is one of allowed values."""
        allowed = ['active', 'completed', 'abandoned']
        if status not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return status

    def to_dict(self) -> Dict[str, Any]:
        """Convert learning path to dictionary."""
        return {
            "path_id": str(self.path_id),
            "user_id": str(self.user_id),
            "path_name": self.path_name,
            "chapters": list(self.chapters_array) if self.chapters_array else [],
            "completion_percentage": self.completion_percentage,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<LearningPath(path_id={self.path_id}, name={self.path_name}, status={self.status})>"


class Progress(Base):
    """Progress tracking model for chapter-level learning progress."""

    __tablename__ = "progress"

    progress_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    chapter_id = Column(Integer, nullable=False)
    completion_status = Column(String(20), default='not_started', nullable=False, index=True)
    time_spent_seconds = Column(Integer, default=0, nullable=False)
    mastery_score = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    practice_attempts = Column(Integer, default=0, nullable=False)
    highest_practice_score = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="progress_records")

    # Constraints
    __table_args__ = (
        CheckConstraint('chapter_id >= 1 AND chapter_id <= 22', name='check_chapter_id_range'),
        CheckConstraint("completion_status IN ('not_started', 'in_progress', 'completed')", name='check_completion_status_values'),
        CheckConstraint('time_spent_seconds >= 0', name='check_time_spent_positive'),
        CheckConstraint('mastery_score >= 0 AND mastery_score <= 100', name='check_mastery_score_range'),
        CheckConstraint('practice_attempts >= 0', name='check_practice_attempts_positive'),
        CheckConstraint('highest_practice_score >= 0 AND highest_practice_score <= 100', name='check_highest_practice_score_range'),
        UniqueConstraint('user_id', 'chapter_id', name='unique_user_chapter'),
        Index('idx_progress_user_chapter', 'user_id', 'chapter_id'),
    )

    @validates('completion_status')
    def validate_completion_status(self, key, status):
        """Validate completion status is one of allowed values."""
        allowed = ['not_started', 'in_progress', 'completed']
        if status not in allowed:
            raise ValueError(f"Completion status must be one of {allowed}")
        return status

    def to_dict(self) -> Dict[str, Any]:
        """Convert progress to dictionary."""
        return {
            "progress_id": str(self.progress_id),
            "user_id": str(self.user_id),
            "chapter_id": self.chapter_id,
            "completion_status": self.completion_status,
            "time_spent_seconds": self.time_spent_seconds,
            "mastery_score": self.mastery_score,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "practice_attempts": self.practice_attempts,
            "highest_practice_score": self.highest_practice_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, chapter={self.chapter_id}, status={self.completion_status})>"


class Achievement(Base):
    """Achievement model for gamification badges and milestones."""

    __tablename__ = "achievements"

    achievement_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    achievement_type = Column(String(100), nullable=False)
    earned_date = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    display_info_json = Column(JSON, nullable=False)

    # Relationships
    user = relationship("User", back_populates="achievements")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_type', name='unique_achievement_per_user'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert achievement to dictionary."""
        return {
            "achievement_id": str(self.achievement_id),
            "user_id": str(self.user_id),
            "achievement_type": self.achievement_type,
            "earned_date": self.earned_date.isoformat() if self.earned_date else None,
            "display_info": self.display_info_json,
        }

    def __repr__(self):
        return f"<Achievement(achievement_id={self.achievement_id}, type={self.achievement_type})>"


class PracticeAttempt(Base):
    """Practice attempt model for tracking user practice sessions."""

    __tablename__ = "practice_attempts"

    attempt_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    chapter_id = Column(Integer, nullable=False, index=True)
    questions_json = Column(JSON, nullable=False)
    score = Column(Integer, nullable=False)
    attempted_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="practice_attempts")

    # Constraints
    __table_args__ = (
        CheckConstraint('chapter_id >= 1 AND chapter_id <= 22', name='check_practice_chapter_id_range'),
        CheckConstraint('score >= 0 AND score <= 100', name='check_practice_score_range'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert practice attempt to dictionary."""
        return {
            "attempt_id": str(self.attempt_id),
            "user_id": str(self.user_id),
            "chapter_id": self.chapter_id,
            "questions": self.questions_json,
            "score": self.score,
            "attempted_at": self.attempted_at.isoformat() if self.attempted_at else None,
        }

    def __repr__(self):
        return f"<PracticeAttempt(attempt_id={self.attempt_id}, chapter={self.chapter_id}, score={self.score})>"


# =====================================================================
# CHATBOT TRANSLATION MODELS (For Urdu Translation Feature - 006)
# =====================================================================


class ChatbotResponseTemplate(Base):
    """Chatbot response template model for translation management."""

    __tablename__ = "chatbot_response_template"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_key = Column(String(255), nullable=False, unique=True, index=True)
    english_content = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default='published', nullable=False)  # published, draft, archived
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    translations = relationship("ChatbotTranslation", back_populates="template", cascade="all, delete-orphan")
    translation_status = relationship("ChatbotResponseTranslationStatus", back_populates="template", uselist=False, cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        Index('idx_chatbot_template_status', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "template_key": self.template_key,
            "english_content": self.english_content,
            "version": self.version,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<ChatbotResponseTemplate(id={self.id}, key={self.template_key}, status={self.status})>"


class ChatbotTranslation(Base):
    """Chatbot translation model for storing Urdu and other language translations."""

    __tablename__ = "chatbot_translation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_template_id = Column(UUID(as_uuid=True), ForeignKey('chatbot_response_template.id', ondelete='CASCADE'), nullable=False, index=True)
    language = Column(String(50), nullable=False)  # urdu, etc.
    translated_content = Column(Text, nullable=True)  # nullable until translated
    translator_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    version = Column(Integer, default=1, nullable=False)  # tracks English version this translation covers
    status = Column(String(50), default='draft', nullable=False)  # draft, in_review, published
    translated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    reviewed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    template = relationship("ChatbotResponseTemplate", back_populates="translations")
    translator = relationship("User", foreign_keys=[translator_id])

    # Constraints
    __table_args__ = (
        UniqueConstraint('response_template_id', 'language', name='uq_translation_template_language'),
        Index('idx_translation_template_status', 'response_template_id', 'status'),
        Index('idx_translation_language_status', 'language', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "template_id": str(self.response_template_id),
            "language": self.language,
            "translated_content": self.translated_content,
            "translator_id": str(self.translator_id) if self.translator_id else None,
            "version": self.version,
            "status": self.status,
            "translated_at": self.translated_at.isoformat() if self.translated_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }

    def __repr__(self):
        return f"<ChatbotTranslation(id={self.id}, language={self.language}, status={self.status})>"


class GlossaryTerm(Base):
    """Glossary term model for technical terminology with translations."""

    __tablename__ = "glossary_term"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    english_term = Column(String(255), nullable=False, unique=True, index=True)
    urdu_translation = Column(String(255), nullable=False)
    pronunciation_transliterated = Column(String(255), nullable=False)  # Latin characters
    definition_english = Column(Text, nullable=False)
    definition_urdu = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)  # robotics, control, kinematics, etc.
    status = Column(String(50), default='published', nullable=False)  # published, under_review
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    feedback = relationship("GlossaryFeedback", back_populates="term", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "english_term": self.english_term,
            "urdu_translation": self.urdu_translation,
            "pronunciation_transliterated": self.pronunciation_transliterated,
            "definition_english": self.definition_english,
            "definition_urdu": self.definition_urdu,
            "category": self.category,
            "status": self.status,
        }

    def __repr__(self):
        return f"<GlossaryTerm(id={self.id}, term={self.english_term})>"


class GlossaryFeedback(Base):
    """Glossary feedback model for user suggestions and corrections."""

    __tablename__ = "glossary_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    glossary_term_id = Column(UUID(as_uuid=True), ForeignKey('glossary_term.id', ondelete='SET NULL'), nullable=True, index=True)
    suggested_term = Column(String(255), nullable=True)  # for new term suggestions
    feedback_type = Column(String(50), nullable=False)  # suggestion, correction, new_term
    content = Column(Text, nullable=False)
    status = Column(String(50), default='pending', nullable=False)  # pending, accepted, rejected
    admin_response = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    reviewed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    term = relationship("GlossaryTerm", back_populates="feedback")

    # Constraints
    __table_args__ = (
        Index('idx_feedback_status', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "glossary_term_id": str(self.glossary_term_id) if self.glossary_term_id else None,
            "suggested_term": self.suggested_term,
            "feedback_type": self.feedback_type,
            "content": self.content,
            "status": self.status,
            "admin_response": self.admin_response,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<GlossaryFeedback(id={self.id}, type={self.feedback_type}, status={self.status})>"


class UserLanguagePreference(Base):
    """User language preference model for chatbot language selection."""

    __tablename__ = "user_language_preference"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    language = Column(String(50), default='english', nullable=False)  # english, urdu
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "language": self.language,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<UserLanguagePreference(user_id={self.user_id}, language={self.language})>"


class ChatbotResponseTranslationStatus(Base):
    """Translation status tracker for chatbot response templates."""

    __tablename__ = "chatbot_response_translation_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_template_id = Column(UUID(as_uuid=True), ForeignKey('chatbot_response_template.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    english_version = Column(Integer, default=1, nullable=False)
    urdu_version = Column(Integer, nullable=True)  # nullable until translated
    status = Column(String(50), default='needs_translation', nullable=False)  # translated, needs_translation, needs_review, stale
    last_updated = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    template = relationship("ChatbotResponseTemplate", back_populates="translation_status")

    # Constraints
    __table_args__ = (
        Index('idx_translation_status', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "template_id": str(self.response_template_id),
            "english_version": self.english_version,
            "urdu_version": self.urdu_version,
            "status": self.status,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    def __repr__(self):
        return f"<ChatbotResponseTranslationStatus(template_id={self.response_template_id}, status={self.status})>"
