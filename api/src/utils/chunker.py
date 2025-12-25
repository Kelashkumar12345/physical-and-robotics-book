"""Content chunking utility for RAG pipeline."""

import re
from dataclasses import dataclass

import tiktoken


@dataclass
class ContentChunk:
    """A chunk of content with metadata."""

    content: str
    token_count: int
    chunk_index: int
    metadata: dict


class Chunker:
    """Splits content into overlapping chunks for embedding."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base",
    ):
        """
        Initialize the chunker.

        Args:
            chunk_size: Target size in tokens for each chunk (default 500)
            chunk_overlap: Number of overlapping tokens between chunks (default 50)
            encoding_name: Tiktoken encoding to use
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))

    def chunk_text(self, text: str, metadata: dict | None = None) -> list[ContentChunk]:
        """
        Split text into overlapping chunks.

        Args:
            text: The text to chunk
            metadata: Base metadata to include with each chunk

        Returns:
            List of ContentChunk objects
        """
        if not text.strip():
            return []

        base_metadata = metadata or {}
        chunks = []

        # Split into paragraphs first (preserve semantic boundaries)
        paragraphs = self._split_into_paragraphs(text)

        current_chunk = []
        current_tokens = 0
        chunk_index = 0

        for para in paragraphs:
            para_tokens = self.count_tokens(para)

            # If single paragraph exceeds chunk size, split it
            if para_tokens > self.chunk_size:
                # Flush current chunk first
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append(
                        ContentChunk(
                            content=chunk_text,
                            token_count=current_tokens,
                            chunk_index=chunk_index,
                            metadata={**base_metadata, "chunk_index": chunk_index},
                        )
                    )
                    chunk_index += 1
                    current_chunk = []
                    current_tokens = 0

                # Split large paragraph by sentences
                sentence_chunks = self._split_large_paragraph(para)
                for sent_chunk in sentence_chunks:
                    chunks.append(
                        ContentChunk(
                            content=sent_chunk,
                            token_count=self.count_tokens(sent_chunk),
                            chunk_index=chunk_index,
                            metadata={**base_metadata, "chunk_index": chunk_index},
                        )
                    )
                    chunk_index += 1
                continue

            # Check if adding this paragraph would exceed chunk size
            if current_tokens + para_tokens > self.chunk_size:
                # Save current chunk
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append(
                        ContentChunk(
                            content=chunk_text,
                            token_count=current_tokens,
                            chunk_index=chunk_index,
                            metadata={**base_metadata, "chunk_index": chunk_index},
                        )
                    )
                    chunk_index += 1

                    # Keep overlap from end of current chunk
                    overlap_paras = self._get_overlap_paragraphs(
                        current_chunk, self.chunk_overlap
                    )
                    current_chunk = overlap_paras
                    current_tokens = sum(self.count_tokens(p) for p in overlap_paras)

            # Add paragraph to current chunk
            current_chunk.append(para)
            current_tokens += para_tokens

        # Don't forget the last chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append(
                ContentChunk(
                    content=chunk_text,
                    token_count=current_tokens,
                    chunk_index=chunk_index,
                    metadata={**base_metadata, "chunk_index": chunk_index},
                )
            )

        return chunks

    def _split_into_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_large_paragraph(self, para: str) -> list[str]:
        """Split a large paragraph by sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", para)
        chunks = []
        current = []
        current_tokens = 0

        for sent in sentences:
            sent_tokens = self.count_tokens(sent)
            if current_tokens + sent_tokens > self.chunk_size:
                if current:
                    chunks.append(" ".join(current))
                current = [sent]
                current_tokens = sent_tokens
            else:
                current.append(sent)
                current_tokens += sent_tokens

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _get_overlap_paragraphs(
        self, paragraphs: list[str], target_tokens: int
    ) -> list[str]:
        """Get paragraphs from the end that sum to approximately target_tokens."""
        overlap = []
        tokens = 0

        for para in reversed(paragraphs):
            para_tokens = self.count_tokens(para)
            if tokens + para_tokens <= target_tokens:
                overlap.insert(0, para)
                tokens += para_tokens
            else:
                break

        return overlap
