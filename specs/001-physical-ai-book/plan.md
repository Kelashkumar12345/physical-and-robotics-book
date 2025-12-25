# Implementation Plan: Physical AI & Humanoid Robotics Book with RAG Chatbot

**Branch**: `001-physical-ai-book` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-physical-ai-book/spec.md`

## Summary

Build a Docusaurus-based educational book covering Physical AI and Humanoid Robotics (4 modules, 13 weeks) with an embedded RAG chatbot. The chatbot uses FastAPI backend, OpenAI Agents SDK for conversational AI, Qdrant Cloud for vector search, and supports anonymous session-based usage with 50 questions/session limit. Deploy to GitHub Pages with chatbot API hosted separately.

## Technical Context

**Language/Version**: Python 3.11+, Node.js 18+, TypeScript 5.x
**Primary Dependencies**: Docusaurus 3.x, FastAPI, OpenAI Agents SDK, Qdrant Client, asyncpg
**Storage**: Qdrant Cloud (vectors), Neon Serverless Postgres (session tracking)
**Testing**: pytest (backend), Jest (frontend), Playwright (E2E)
**Target Platform**: GitHub Pages (static), Cloud Run/Vercel (API)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <3s page load, <5s chatbot response, 99% uptime
**Constraints**: Free tier limits (Qdrant, Neon), 50 questions/session, no auth required
**Scale/Scope**: ~50 content pages, ~100 concurrent users, 13 weeks curriculum

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Simulation-First Development | PASS | Content covers Isaac Sim, Gazebo, Unity simulations |
| II. Modular Architecture | PASS | Separate frontend (Docusaurus), backend (FastAPI), vector store (Qdrant), database (Neon) |
| III. Documentation-as-Code | PASS | Markdown content in Docusaurus, version-controlled |
| IV. RAG-Enabled Content | PASS | OpenAI Agents SDK + Qdrant for semantic search with citations |
| V. Practical Learning Focus | PASS | Code examples for ROS 2, URDF, sensors, VLA |
| VI. Sim-to-Real Methodology | PASS | Content covers Isaac Sim → Gazebo → Jetson deployment |

**Gate Result**: PASS - All 6 principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-physical-ai-book/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
# Frontend: Docusaurus Book
book/
├── docusaurus.config.ts
├── sidebars.ts
├── src/
│   ├── components/
│   │   ├── ChatWidget/       # RAG chatbot React component
│   │   ├── CodeBlock/        # Enhanced code blocks with copy
│   │   └── TextSelector/     # Text selection for contextual queries
│   ├── css/
│   └── pages/
├── docs/
│   ├── intro.md
│   ├── module-1-ros2/
│   │   ├── week-1-intro.md
│   │   ├── week-2-sensors.md
│   │   ├── week-3-nodes.md
│   │   ├── week-4-topics.md
│   │   └── week-5-services.md
│   ├── module-2-gazebo/
│   │   ├── week-6-setup.md
│   │   └── week-7-urdf.md
│   ├── module-3-isaac/
│   │   ├── week-8-isaac-sdk.md
│   │   ├── week-9-perception.md
│   │   └── week-10-nav2.md
│   ├── module-4-vla/
│   │   ├── week-11-humanoid.md
│   │   ├── week-12-locomotion.md
│   │   └── week-13-capstone.md
│   └── hardware/
│       └── requirements.md
├── static/
│   └── img/
└── package.json

# Backend: FastAPI RAG Service
api/
├── src/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Environment configuration
│   ├── models/
│   │   ├── conversation.py  # Session/message models
│   │   └── content.py       # ContentChunk, Citation models
│   ├── services/
│   │   ├── rag_service.py   # RAG orchestration
│   │   ├── embedding.py     # OpenAI embeddings
│   │   ├── vector_store.py  # Qdrant operations
│   │   └── agent.py         # OpenAI Agents SDK integration
│   ├── api/
│   │   ├── chat.py          # Chat endpoints
│   │   ├── health.py        # Health check
│   │   └── deps.py          # Dependencies
│   └── utils/
│       ├── chunker.py       # Content chunking
│       └── rate_limiter.py  # Session rate limiting
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/
│   ├── ingest_content.py    # Index book content to Qdrant
│   └── seed_db.py           # Initialize Neon schema
├── requirements.txt
└── Dockerfile

# Shared
.github/
├── workflows/
│   ├── deploy-book.yml      # Deploy Docusaurus to GitHub Pages
│   └── deploy-api.yml       # Deploy FastAPI to Cloud Run
└── dependabot.yml
```

**Structure Decision**: Web application with separate frontend (Docusaurus static site) and backend (FastAPI API). Frontend deployed to GitHub Pages, backend to Cloud Run or Vercel serverless.

## Complexity Tracking

> No violations - all principles satisfied with standard architecture.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Separate API | Cloud Run | GitHub Pages is static-only; API needs serverless compute |
| No auth | Session cookies | Clarification confirmed anonymous-only usage |
| Rate limiting | In-memory + session ID | 50/session limit, no persistence needed |
