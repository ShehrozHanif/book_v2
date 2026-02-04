"""Pydantic request and response schemas for API endpoints."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class MessageSchema(BaseModel):
    """Schema for individual chat messages."""

    sender: str = Field(..., description="Sender of the message: 'user' or 'bot'")
    content: str = Field(..., description="Content of the message")
    timestamp: str = Field(..., description="ISO format timestamp of the message")

    @field_validator("sender")
    @classmethod
    def validate_sender(cls, v: str) -> str:
        """Validate sender is either 'user' or 'bot'."""
        if v not in ["user", "bot"]:
            raise ValueError("sender must be either 'user' or 'bot'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "sender": "user",
                "content": "What is humanoid robotics?",
                "timestamp": "2024-01-30T10:30:00Z",
            }
        }


class ChatRequest(BaseModel):
    """Schema for incoming chat requests."""

    query: str = Field(
        ...,
        description="The user's query/question",
        min_length=1,
        max_length=5000,
    )
    selected_text: Optional[str] = Field(
        None,
        description="Optional highlighted text from the textbook",
        max_length=2000,
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID to continue existing conversation",
    )
    user_id: Optional[str] = Field(
        None,
        description="Optional authenticated user ID",
    )
    difficulty_override: Optional[str] = Field(
        None,
        description="Optional difficulty override: 'simplify' or 'advanced'",
        enum=["simplify", "advanced"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the definition of kinematics?",
                "selected_text": None,
                "conversation_id": None,
                "user_id": None,
            }
        }


class ChatResponse(BaseModel):
    """Schema for chat response."""

    response: str = Field(..., description="The bot's response to the user query")
    conversation_id: str = Field(..., description="The conversation ID for tracking context")
    retrieved_passages: List[str] = Field(
        default_factory=list,
        description="List of textbook passages used for context",
    )
    relevance_scores: List[float] = Field(
        default_factory=list,
        description="Relevance scores for each retrieved passage (0-1 scale)",
    )
    processing_time_ms: float = Field(
        ...,
        description="Time taken to generate response in milliseconds",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Kinematics is the branch of mechanics...",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "retrieved_passages": [
                    "Kinematics is the study of motion...",
                    "The kinematic equations describe...",
                ],
                "relevance_scores": [0.92, 0.87],
                "processing_time_ms": 245.5,
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(
        None,
        description="Additional error details or suggestions",
    )
    status_code: int = Field(
        ...,
        description="HTTP status code",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation error",
                "details": "Query must be between 1 and 5000 characters",
                "status_code": 400,
            }
        }


class ConversationSchema(BaseModel):
    """Schema for conversation metadata."""

    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: Optional[str] = Field(None, description="Associated user ID if authenticated")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    message_count: int = Field(default=0, description="Number of messages in conversation")

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    """Schema for user information."""

    user_id: str = Field(..., description="Unique user identifier")
    email: Optional[str] = Field(None, description="User email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
