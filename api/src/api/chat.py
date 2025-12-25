"""Chat API endpoints."""

from fastapi import APIRouter, Response

from src.models.conversation import ChatRequest, ChatResponse, SessionStatus
from src.api.deps import RAGServiceDep, RateLimiterDep, SessionIdDep

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "Successful response"},
        400: {"description": "Invalid request"},
        429: {"description": "Rate limit exceeded (50 questions/session)"},
        503: {"description": "Service unavailable (AI service down)"},
    },
)
async def send_message(
    request: ChatRequest,
    response: Response,
    rag_service: RAGServiceDep,
    rate_limiter: RateLimiterDep,
    session_id: SessionIdDep,
) -> ChatResponse:
    """
    Send a message to the chatbot.

    Rate limited to 50 questions per session.
    """
    # Check and increment rate limit
    questions_remaining = rate_limiter.check_and_increment(session_id)

    # Process through RAG pipeline
    chat_response = await rag_service.query(
        message=request.message,
        context=request.context,
        questions_remaining=questions_remaining,
    )

    # Set session cookie if not present
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=86400,  # 24 hours
    )

    # Add header with remaining questions
    response.headers["X-Questions-Remaining"] = str(questions_remaining)

    return chat_response


@router.get(
    "/chat/session",
    response_model=SessionStatus,
)
async def get_session(
    rate_limiter: RateLimiterDep,
    session_id: SessionIdDep,
) -> SessionStatus:
    """Get current session status."""
    question_count = rate_limiter.get_count(session_id)
    questions_remaining = rate_limiter.get_remaining(session_id)

    return SessionStatus(
        sessionId=session_id,
        questionCount=question_count,
        questionsRemaining=questions_remaining,
        hasContext=False,  # Context tracking would need conversation state
    )


@router.delete(
    "/chat/session",
)
async def reset_session(
    response: Response,
    rate_limiter: RateLimiterDep,
    session_id: SessionIdDep,
) -> dict:
    """Reset chat session, clearing conversation history and rate limit."""
    rate_limiter.reset_session(session_id)

    # Clear the session cookie
    response.delete_cookie(key="session_id")

    return {"message": "Session reset successfully"}
