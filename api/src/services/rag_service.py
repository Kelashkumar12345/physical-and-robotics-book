"""RAG service orchestrating embedding, vector search, and agent response."""

from uuid import uuid4

from src.models.content import Citation
from src.models.conversation import ChatResponse
from src.services.embedding import EmbeddingService
from src.services.vector_store import VectorStoreService
from src.services.agent import AgentService


class RAGService:
    """Orchestrates RAG pipeline for chatbot responses."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
        agent_service: AgentService,
    ):
        self.embedding = embedding_service
        self.vector_store = vector_store
        self.agent = agent_service

    async def query(
        self,
        message: str,
        context: str | None = None,
        conversation_history: list[dict] | None = None,
        questions_remaining: int = 50,
    ) -> ChatResponse:
        """
        Process a user query through the RAG pipeline.

        1. Embed the query
        2. Retrieve relevant chunks from vector store
        3. Generate response using agent
        4. Extract citations from retrieved chunks
        """
        # Step 1: Embed the query
        query_embedding = await self.embedding.embed(message)

        # Step 2: Retrieve relevant chunks
        retrieved_chunks = await self.vector_store.search(
            query_vector=query_embedding,
            limit=5,
        )

        # Step 3: Generate response
        response_text, is_out_of_scope = await self.agent.chat(
            message=message,
            context=context,
            retrieved_chunks=retrieved_chunks,
            conversation_history=conversation_history,
        )

        # Step 4: Build citations from retrieved chunks
        citations = []
        for chunk in retrieved_chunks[:3]:  # Top 3 sources
            payload = chunk.get("payload", {})
            citations.append(
                Citation(
                    title=payload.get("heading", "Book Section"),
                    url=payload.get("url", "/docs/intro"),
                    relevanceScore=chunk.get("score", 0.0),
                )
            )

        return ChatResponse(
            id=str(uuid4()),
            message=response_text,
            citations=citations,
            isOutOfScope=is_out_of_scope,
            questionsRemaining=questions_remaining,
        )
