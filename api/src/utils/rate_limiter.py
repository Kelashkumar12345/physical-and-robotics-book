"""Session-based rate limiting for chatbot queries."""

from fastapi import HTTPException, status


class RateLimiter:
    """In-memory rate limiter with 50 questions per session."""

    def __init__(self, max_requests: int = 50):
        self.max_requests = max_requests
        self._session_counts: dict[str, int] = {}

    def get_count(self, session_id: str) -> int:
        """Get current question count for a session."""
        return self._session_counts.get(session_id, 0)

    def get_remaining(self, session_id: str) -> int:
        """Get remaining questions for a session."""
        return self.max_requests - self.get_count(session_id)

    def check_and_increment(self, session_id: str) -> int:
        """
        Check rate limit and increment counter.

        Returns:
            Number of questions remaining after this request.

        Raises:
            HTTPException: If rate limit exceeded.
        """
        current_count = self._session_counts.get(session_id, 0)

        if current_count >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": (
                        f"You've reached the {self.max_requests} question limit for this session. "
                        "Please start a new session to continue."
                    ),
                },
            )

        self._session_counts[session_id] = current_count + 1
        return self.max_requests - current_count - 1

    def reset_session(self, session_id: str) -> None:
        """Reset question count for a session."""
        self._session_counts.pop(session_id, None)
