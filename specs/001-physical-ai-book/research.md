# Research: Physical AI & Humanoid Robotics Book with RAG Chatbot

**Date**: 2025-12-25
**Feature**: 001-physical-ai-book

## Technology Decisions

### 1. Static Site Generator: Docusaurus 3.x

**Decision**: Use Docusaurus 3.x for the book platform

**Rationale**:
- Native MDX support for interactive code examples
- Built-in versioning for curriculum updates
- Excellent search integration (Algolia DocSearch or local)
- GitHub Pages deployment out-of-the-box
- Active community with robotics/AI documentation use cases

**Alternatives Considered**:
- **MkDocs**: Simpler but less customizable for React components
- **GitBook**: Commercial, less control over deployment
- **VitePress**: Vue-based, smaller ecosystem for custom components

### 2. RAG Backend: FastAPI + OpenAI Agents SDK

**Decision**: FastAPI with OpenAI Agents SDK for conversational RAG

**Rationale**:
- FastAPI provides async support critical for AI API calls
- OpenAI Agents SDK offers built-in conversation management
- Native Python ecosystem matches robotics tooling (ROS 2, Isaac)
- Pydantic validation for API contracts

**Alternatives Considered**:
- **LangChain**: More abstraction, but heavier dependency
- **LlamaIndex**: Good for RAG, but less mature agent support
- **Direct OpenAI API**: More control, but manual conversation state

### 3. Vector Store: Qdrant Cloud Free Tier

**Decision**: Qdrant Cloud for vector embeddings and semantic search

**Rationale**:
- 1GB free tier sufficient for ~50 pages of book content
- Native Python client with async support
- Payload filtering for module/week metadata
- Good performance for small-scale deployment

**Alternatives Considered**:
- **Pinecone**: More scalable, but overkill for free tier needs
- **Weaviate**: Self-hosted complexity
- **ChromaDB**: Local-first, harder to deploy serverless

### 4. Database: Neon Serverless Postgres

**Decision**: Neon for session tracking (minimal use per clarification)

**Rationale**:
- Per-clarification: No persistent storage needed
- Session data stored in-memory/cookies only
- Neon available if future features need persistence
- Free tier with generous limits

**Alternatives Considered**:
- **Supabase**: Similar offering, Neon simpler for minimal use
- **PlanetScale**: MySQL-based, less Python ecosystem fit
- **No database**: Valid given session-only requirement

### 5. Embedding Model: text-embedding-3-small

**Decision**: OpenAI text-embedding-3-small for content embeddings

**Rationale**:
- 1536 dimensions, good balance of quality/cost
- Consistent with OpenAI Agents SDK ecosystem
- Sufficient for educational content similarity
- $0.00002/1K tokens (affordable for ~50 pages)

**Alternatives Considered**:
- **text-embedding-3-large**: Higher quality, but 3x cost
- **Cohere embed-v3**: Requires additional API key
- **Local models (sentence-transformers)**: Deployment complexity

### 6. API Hosting: Google Cloud Run

**Decision**: Cloud Run for FastAPI deployment

**Rationale**:
- Free tier: 2M requests/month, 360K GB-seconds
- Auto-scaling from zero (cost-efficient)
- Container-based (matches Dockerfile in plan)
- Easy CORS configuration for GitHub Pages frontend

**Alternatives Considered**:
- **Vercel Functions**: Good, but Python cold starts slower
- **Railway**: Simple, but less generous free tier
- **AWS Lambda**: More complex IAM setup

### 7. Content Chunking Strategy

**Decision**: Semantic chunking with 500-token chunks, 50-token overlap

**Rationale**:
- 500 tokens ~= 1-2 paragraphs, good for context
- Overlap prevents information loss at boundaries
- Metadata includes: module, week, topic, heading hierarchy
- Citations link back to exact document sections

**Alternatives Considered**:
- **Fixed character chunking**: Loses semantic boundaries
- **Sentence-level**: Too granular for educational content
- **Page-level**: Too large, reduces retrieval precision

## Best Practices Research

### Docusaurus + Custom React Components

**Pattern**: Create ChatWidget as a theme component

```text
book/src/components/ChatWidget/
├── index.tsx           # Main widget component
├── ChatWindow.tsx      # Expandable chat UI
├── MessageList.tsx     # Conversation display
├── InputBar.tsx        # User input with send button
└── styles.module.css   # Scoped styles
```

**Integration**: Use `@theme/Root` wrapper to inject globally.

### FastAPI + Qdrant Best Practices

**Pattern**: Dependency injection for services

```python
# api/src/api/deps.py
async def get_rag_service() -> RAGService:
    return RAGService(
        vector_store=QdrantVectorStore(),
        agent=OpenAIAgent(),
    )

# api/src/api/chat.py
@router.post("/chat")
async def chat(
    request: ChatRequest,
    rag: RAGService = Depends(get_rag_service),
):
    return await rag.query(request.message, request.context)
```

### Rate Limiting Pattern

**Pattern**: Session-based counter with cookie

```python
# In-memory store (per-instance, resets on restart - acceptable per spec)
session_counts: dict[str, int] = {}

async def check_rate_limit(session_id: str) -> bool:
    count = session_counts.get(session_id, 0)
    if count >= 50:
        raise HTTPException(429, "Session limit reached")
    session_counts[session_id] = count + 1
    return True
```

### Text Selection for Contextual Queries

**Pattern**: Browser Selection API + postMessage to widget

```typescript
// TextSelector component
document.addEventListener('mouseup', () => {
  const selection = window.getSelection()?.toString();
  if (selection && selection.length > 10) {
    // Show "Ask about this" tooltip
    showContextMenu(selection);
  }
});
```

## Integration Patterns

### Frontend-Backend Communication

```text
┌─────────────────┐         ┌─────────────────┐
│  Docusaurus     │  HTTPS  │  FastAPI        │
│  (GitHub Pages) │◄───────►│  (Cloud Run)    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │                           ▼
         │                  ┌─────────────────┐
         │                  │  Qdrant Cloud   │
         │                  │  (Vectors)      │
         │                  └─────────────────┘
         │                           │
         │                           ▼
         │                  ┌─────────────────┐
         │                  │  OpenAI API     │
         │                  │  (Embeddings +  │
         │                  │   Agents SDK)   │
         └──────────────────┴─────────────────┘
```

### Content Ingestion Pipeline

```text
1. Build Docusaurus (generates static HTML/JSON)
2. Parse docs/*.md files
3. Chunk content (500 tokens, 50 overlap)
4. Generate embeddings (text-embedding-3-small)
5. Upsert to Qdrant with metadata:
   - module: "module-1-ros2"
   - week: "week-3-nodes"
   - heading: "Creating ROS 2 Nodes"
   - url: "/docs/module-1-ros2/week-3-nodes#creating-ros-2-nodes"
```

## Resolved Clarifications

| Topic | Resolution | Source |
|-------|------------|--------|
| Authentication | Anonymous only, session-based | Spec clarification |
| Data retention | Session-only, no persistence | Spec clarification |
| Rate limiting | 50 questions/session | Spec clarification |
| Hosting | GitHub Pages + Cloud Run | This research |
| Embedding model | text-embedding-3-small | This research |
| Chunk size | 500 tokens, 50 overlap | This research |
