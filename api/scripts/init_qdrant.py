#!/usr/bin/env python3
"""
Initialize Qdrant collection for the Physical AI Book RAG pipeline.

Creates the vector collection with proper settings if it doesn't exist.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.services.vector_store import VectorStoreService


async def main():
    """Initialize the Qdrant collection."""
    settings = get_settings()

    print(f"Connecting to Qdrant at {settings.qdrant_url}...")

    vector_store = VectorStoreService(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection,
    )

    print(f"Creating collection '{settings.qdrant_collection}'...")

    try:
        await vector_store.ensure_collection(vector_size=1536)
        print("Collection created successfully!")

        # Verify collection exists
        collections = await vector_store.client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if settings.qdrant_collection in collection_names:
            print(f"Verified: Collection '{settings.qdrant_collection}' exists")
        else:
            print(f"Warning: Collection not found in list: {collection_names}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
