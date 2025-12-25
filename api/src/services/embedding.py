"""OpenAI embedding service using text-embedding-3-small."""

from openai import AsyncOpenAI


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    MODEL = "text-embedding-3-small"
    DIMENSIONS = 1536

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        response = await self.client.embeddings.create(
            model=self.MODEL,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        response = await self.client.embeddings.create(
            model=self.MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]
