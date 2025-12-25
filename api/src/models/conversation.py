"""Conversation-related Pydantic models."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from src.models.content import Citation


class MessageRole(str, Enum):
    """Message author role."""

    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """A single user query or chatbot response."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    role: MessageRole
    content: str = Field(..., max_length=4000)
    citations: list[Citation] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Conversation(BaseModel):
    """A user's chat session with the chatbot (in-memory only)."""

    session_id: str
    messages: list[Message] = Field(default_factory=list)
    question_count: int = Field(default=0, ge=0, le=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    context: str | None = Field(default=None, max_length=2000)


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's question or message",
    )
    context: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional selected text context for contextual queries",
    )


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""

    id: str = Field(..., description="Unique message identifier")
    message: str = Field(..., description="AI assistant's response")
    citations: list[Citation] = Field(
        default_factory=list,
        description="Source citations from the book",
    )
    isOutOfScope: bool = Field(
        default=False,
        description="True if the question is outside the book's scope",
    )
    questionsRemaining: int = Field(
        default=50,
        ge=0,
        le=50,
        description="Questions remaining in session",
    )


class SessionStatus(BaseModel):
    """Session status response."""

    sessionId: str
    questionCount: int = Field(ge=0, le=50)
    questionsRemaining: int = Field(ge=0, le=50)
    hasContext: bool = Field(default=False)
