"""Dependency injection setup for API services."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request

from src.config import Settings, get_settings
from src.services.embedding import EmbeddingService
from src.services.vector_store import VectorStoreService
from src.services.agent import AgentService
from src.services.rag_service import RAGService
from src.utils.rate_limiter import RateLimiter


# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    settings = get_settings()
    return EmbeddingService(api_key=settings.openai_api_key)


@lru_cache
def get_vector_store() -> VectorStoreService:
    """Get cached vector store service instance."""
    settings = get_settings()
    return VectorStoreService(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection,
    )


@lru_cache
def get_agent_service() -> AgentService:
    """Get cached agent service instance."""
    settings = get_settings()
    return AgentService(api_key=settings.openai_api_key)


@lru_cache
def get_rate_limiter() -> RateLimiter:
    """Get cached rate limiter instance."""
    settings = get_settings()
    return RateLimiter(max_requests=settings.rate_limit_per_session)


def get_rag_service(
    embedding: EmbeddingService = Depends(get_embedding_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
    agent: AgentService = Depends(get_agent_service),
) -> RAGService:
    """Get RAG service with all dependencies injected."""
    return RAGService(
        embedding_service=embedding,
        vector_store=vector_store,
        agent_service=agent,
    )


def get_session_id(request: Request) -> str:
    """Extract or generate session ID from request."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
    return session_id


# Type aliases for dependency injection
EmbeddingDep = Annotated[EmbeddingService, Depends(get_embedding_service)]
VectorStoreDep = Annotated[VectorStoreService, Depends(get_vector_store)]
AgentDep = Annotated[AgentService, Depends(get_agent_service)]
RAGServiceDep = Annotated[RAGService, Depends(get_rag_service)]
RateLimiterDep = Annotated[RateLimiter, Depends(get_rate_limiter)]
SessionIdDep = Annotated[str, Depends(get_session_id)]
