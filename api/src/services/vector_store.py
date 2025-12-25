"""Qdrant vector store service for semantic search."""

from typing import Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter


class VectorStoreService:
    """Service for vector storage and retrieval using Qdrant."""

    def __init__(self, url: str, api_key: str, collection_name: str):
        self.client = AsyncQdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name

    async def health_check(self) -> bool:
        """Check if Qdrant is accessible."""
        collections = await self.client.get_collections()
        return True

    async def ensure_collection(self, vector_size: int = 1536) -> None:
        """Create collection if it doesn't exist."""
        collections = await self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)

        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    async def upsert(
        self,
        id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Insert or update a vector with payload."""
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    async def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        filter: Filter | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        results = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=filter,
            with_payload=True,
        )
        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results.points
        ]
