"""SQLAlchemy ORM models for database entities."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model for authenticated users."""

    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"


class Conversation(Base):
    """Conversation model for storing chat sessions."""

    __tablename__ = "conversations"

    conversation_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(conversation_id={self.conversation_id}, user_id={self.user_id})>"


class Message(Base):
    """Message model for storing chat messages."""

    __tablename__ = "messages"

    message_id = Column(String(36), primary_key=True)
    conversation_id = Column(String(36), ForeignKey("conversations.conversation_id"), nullable=False)
    sender = Column(String(10), nullable=False)  # 'user' or 'bot'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(message_id={self.message_id}, sender={self.sender})>"


class TextbookChunk(Base):
    """TextbookChunk model for storing embedded textbook passages."""

    __tablename__ = "textbook_chunks"

    chunk_id = Column(String(36), primary_key=True)
    content = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    chapter = Column(String(100), nullable=True)
    section = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<TextbookChunk(chunk_id={self.chunk_id}, module={self.module}, chapter={self.chapter})>"


class AuditLog(Base):
    """AuditLog model for storing RAG pipeline audit information."""

    __tablename__ = "audit_logs"

    log_id = Column(String(36), primary_key=True)
    query = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    relevance_scores = Column(JSON, nullable=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    conversation_id = Column(String(36), ForeignKey("conversations.conversation_id"), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(log_id={self.log_id}, user_id={self.user_id}, conversation_id={self.conversation_id})>"
