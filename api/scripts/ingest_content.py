#!/usr/bin/env python3
"""
Content ingestion script for the Physical AI Book RAG pipeline.

Parses markdown files from the book/docs directory, chunks them,
generates embeddings, and upserts to Qdrant.
"""

import asyncio
import hashlib
import re
import sys
from pathlib import Path

import frontmatter

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.services.embedding import EmbeddingService
from src.services.vector_store import VectorStoreService
from src.utils.chunker import Chunker


def parse_markdown_file(file_path: Path) -> dict:
    """Parse a markdown file and extract content and metadata."""
    with open(file_path, encoding="utf-8") as f:
        post = frontmatter.load(f)

    # Extract metadata from frontmatter
    metadata = dict(post.metadata)

    # Parse the path to get module and week info
    parts = file_path.parts
    if "docs" in parts:
        docs_idx = parts.index("docs")
        relative_parts = parts[docs_idx + 1 :]

        if len(relative_parts) >= 1:
            # e.g., module-1-ros2/week-1-intro.md
            if relative_parts[0].startswith("module-"):
                metadata["module"] = relative_parts[0]
                if len(relative_parts) >= 2:
                    metadata["week"] = relative_parts[1].replace(".md", "")

    # Build the URL
    url_path = "/docs/" + "/".join(str(p) for p in relative_parts).replace(".md", "")
    metadata["url"] = url_path

    # Extract the first heading as the title if not in frontmatter
    if "title" not in metadata:
        heading_match = re.search(r"^#\s+(.+)$", post.content, re.MULTILINE)
        if heading_match:
            metadata["title"] = heading_match.group(1)
        else:
            metadata["title"] = file_path.stem.replace("-", " ").title()

    metadata["heading"] = metadata.get("title", "")

    return {
        "content": post.content,
        "metadata": metadata,
        "file_path": str(file_path),
    }


def generate_chunk_id(content: str, metadata: dict) -> str:
    """Generate a stable ID for a chunk based on content and metadata."""
    key = f"{metadata.get('url', '')}:{metadata.get('chunk_index', 0)}:{content[:100]}"
    return hashlib.md5(key.encode()).hexdigest()


async def ingest_file(
    file_path: Path,
    chunker: Chunker,
    embedding_service: EmbeddingService,
    vector_store: VectorStoreService,
) -> int:
    """Ingest a single markdown file. Returns number of chunks created."""
    print(f"  Processing: {file_path.name}")

    try:
        parsed = parse_markdown_file(file_path)
        content = parsed["content"]
        base_metadata = parsed["metadata"]

        # Skip empty files
        if not content.strip():
            print(f"    Skipped (empty)")
            return 0

        # Chunk the content
        chunks = chunker.chunk_text(content, base_metadata)

        if not chunks:
            print(f"    Skipped (no chunks)")
            return 0

        # Generate embeddings for all chunks
        chunk_texts = [c.content for c in chunks]
        embeddings = await embedding_service.embed_batch(chunk_texts)

        # Upsert to vector store
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = generate_chunk_id(chunk.content, chunk.metadata)

            # Add content to metadata for retrieval
            payload = {
                **chunk.metadata,
                "content": chunk.content,
            }

            await vector_store.upsert(
                id=chunk_id,
                vector=embedding,
                payload=payload,
            )

        print(f"    Created {len(chunks)} chunks")
        return len(chunks)

    except Exception as e:
        print(f"    Error: {e}")
        return 0


async def main(docs_path: str = "../book/docs"):
    """Main ingestion function."""
    settings = get_settings()

    # Initialize services
    embedding_service = EmbeddingService(api_key=settings.openai_api_key)
    vector_store = VectorStoreService(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection,
    )
    chunker = Chunker(chunk_size=500, chunk_overlap=50)

    # Ensure collection exists
    print("Ensuring Qdrant collection exists...")
    await vector_store.ensure_collection(vector_size=1536)

    # Find all markdown files
    docs_dir = Path(docs_path)
    if not docs_dir.exists():
        print(f"Error: Docs directory not found: {docs_dir}")
        return

    md_files = list(docs_dir.glob("**/*.md"))
    print(f"Found {len(md_files)} markdown files")

    # Process each file
    total_chunks = 0
    for file_path in md_files:
        chunks = await ingest_file(
            file_path, chunker, embedding_service, vector_store
        )
        total_chunks += chunks

    print(f"\nIngestion complete!")
    print(f"  Files processed: {len(md_files)}")
    print(f"  Total chunks created: {total_chunks}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest book content to Qdrant")
    parser.add_argument(
        "--docs-path",
        default="../book/docs",
        help="Path to the docs directory",
    )
    args = parser.parse_args()

    asyncio.run(main(args.docs_path))
