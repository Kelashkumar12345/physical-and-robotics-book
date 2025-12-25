"""Content-related Pydantic models."""

from pydantic import BaseModel, Field


class ContentChunk(BaseModel):
    """A segment of book content indexed for semantic search."""

    id: str
    topic_id: str
    content: str = Field(..., description="Chunk text content (~500 tokens)")
    metadata: dict = Field(default_factory=dict)


class ChunkMetadata(BaseModel):
    """Metadata for a content chunk."""

    module: str = Field(..., description="Module slug, e.g., 'module-1-ros2'")
    week: str = Field(..., description="Week slug, e.g., 'week-3-nodes'")
    topic: str = Field(..., description="Topic slug")
    heading: str = Field(..., description="Section heading for display")
    url: str = Field(..., description="Full URL to the section")
    chunk_index: int = Field(default=0, description="Index within the topic")


class Citation(BaseModel):
    """A reference linking a response to a book section."""

    title: str = Field(..., description="Section title for display")
    url: str = Field(..., description="Link to the referenced section")
    relevanceScore: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score (0-1)",
    )
