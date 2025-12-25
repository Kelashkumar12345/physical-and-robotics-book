# Tasks: Physical AI & Humanoid Robotics Book with RAG Chatbot

**Input**: Design documents from `/specs/001-physical-ai-book/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create monorepo structure with book/ and api/ directories at repository root
- [ ] T002 [P] Initialize Docusaurus 3.x project in book/ with TypeScript configuration
- [ ] T003 [P] Initialize FastAPI project in api/ with Python 3.11+ and requirements.txt
- [ ] T004 [P] Create api/.env.example with OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, CORS_ORIGINS placeholders
- [ ] T005 [P] Create book/.env.example with REACT_APP_API_URL placeholder
- [ ] T006 [P] Configure ESLint and Prettier for book/ in book/.eslintrc.js and book/.prettierrc
- [ ] T007 [P] Configure Ruff linter for api/ in api/pyproject.toml
- [ ] T008 Create .github/workflows/deploy-book.yml for GitHub Pages deployment
- [ ] T009 [P] Create .github/workflows/deploy-api.yml for Cloud Run deployment
- [ ] T010 [P] Create .github/dependabot.yml for dependency updates

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T011 Create api/src/config.py with environment variable loading using pydantic-settings
- [ ] T012 [P] Create api/src/main.py with FastAPI app initialization, CORS middleware, and router includes
- [ ] T013 [P] Create api/src/api/deps.py with dependency injection setup for services
- [ ] T014 Create api/src/api/health.py with GET /api/v1/health endpoint per OpenAPI spec
- [ ] T015 Create book/docusaurus.config.ts with site metadata, theme, and GitHub Pages config
- [ ] T016 [P] Create book/sidebars.ts with 4-module sidebar structure matching content hierarchy
- [ ] T017 [P] Create book/src/css/custom.css with base theme customizations

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Browse Course Content (Priority: P1)

**Goal**: Readers can browse 13-week Physical AI course content organized by 4 modules

**Independent Test**: Navigate to deployed site, browse all 4 modules, verify all 13 weeks accessible

### Content Structure

- [ ] T018 [P] [US1] Create book/docs/intro.md with course overview and learning outcomes
- [ ] T019 [P] [US1] Create book/docs/hardware/requirements.md with workstation and edge kit specifications

### Module 1: ROS 2 (Weeks 1-5)

- [ ] T020 [P] [US1] Create book/docs/module-1-ros2/week-1-intro.md covering Physical AI foundations
- [ ] T021 [P] [US1] Create book/docs/module-1-ros2/week-2-sensors.md covering sensor systems (LiDAR, cameras, IMUs)
- [ ] T022 [P] [US1] Create book/docs/module-1-ros2/week-3-nodes.md covering ROS 2 architecture and nodes
- [ ] T023 [P] [US1] Create book/docs/module-1-ros2/week-4-topics.md covering topics, services, and actions
- [ ] T024 [P] [US1] Create book/docs/module-1-ros2/week-5-services.md covering launch files and parameter management

### Module 2: Gazebo & Unity (Weeks 6-7)

- [ ] T025 [P] [US1] Create book/docs/module-2-gazebo/week-6-setup.md covering Gazebo simulation setup
- [ ] T026 [P] [US1] Create book/docs/module-2-gazebo/week-7-urdf.md covering URDF/SDF and Unity visualization

### Module 3: NVIDIA Isaac (Weeks 8-10)

- [ ] T027 [P] [US1] Create book/docs/module-3-isaac/week-8-isaac-sdk.md covering Isaac SDK and Isaac Sim
- [ ] T028 [P] [US1] Create book/docs/module-3-isaac/week-9-perception.md covering AI perception and manipulation
- [ ] T029 [P] [US1] Create book/docs/module-3-isaac/week-10-nav2.md covering VSLAM and Nav2 path planning

### Module 4: VLA (Weeks 11-13)

- [ ] T030 [P] [US1] Create book/docs/module-4-vla/week-11-humanoid.md covering humanoid kinematics
- [ ] T031 [P] [US1] Create book/docs/module-4-vla/week-12-locomotion.md covering bipedal locomotion
- [ ] T032 [P] [US1] Create book/docs/module-4-vla/week-13-capstone.md covering capstone project with conversational AI

### Navigation

- [ ] T033 [US1] Update book/sidebars.ts to include all 13 weeks organized by module
- [ ] T034 [US1] Verify mobile responsiveness by testing navigation on different viewport sizes

**Checkpoint**: User Story 1 complete - book content browsable, all 13 weeks accessible within 2 clicks

---

## Phase 4: User Story 2 - Ask Chatbot Questions (Priority: P2)

**Goal**: Readers can ask chatbot questions about any book topic and receive RAG-powered answers

**Independent Test**: Open chatbot widget, ask "What is ROS 2?", verify response references book content

### Backend Models

- [ ] T035 [P] [US2] Create api/src/models/content.py with ContentChunk and Citation Pydantic models
- [ ] T036 [P] [US2] Create api/src/models/conversation.py with Conversation, Message, ChatRequest, ChatResponse models

### Backend Services

- [ ] T037 [US2] Create api/src/services/embedding.py with OpenAI text-embedding-3-small integration
- [ ] T038 [US2] Create api/src/services/vector_store.py with Qdrant client for upsert and search operations
- [ ] T039 [US2] Create api/src/services/agent.py with OpenAI Agents SDK integration for chat completion
- [ ] T040 [US2] Create api/src/services/rag_service.py orchestrating embedding, vector search, and agent response

### Backend API

- [ ] T041 [US2] Create api/src/api/chat.py with POST /api/v1/chat endpoint per OpenAPI spec
- [ ] T042 [US2] Add GET /api/v1/chat/session endpoint to api/src/api/chat.py for session status
- [ ] T043 [US2] Add DELETE /api/v1/chat/session endpoint to api/src/api/chat.py for session reset

### Backend Utilities

- [ ] T044 [P] [US2] Create api/src/utils/chunker.py with 500-token chunking and 50-token overlap logic
- [ ] T045 [US2] Create api/src/utils/rate_limiter.py with 50 questions/session in-memory tracking

### Content Ingestion

- [ ] T046 [US2] Create api/scripts/ingest_content.py to parse book/docs/*.md and upsert to Qdrant

### Frontend ChatWidget

- [ ] T047 [US2] Create book/src/components/ChatWidget/index.tsx as main widget component
- [ ] T048 [P] [US2] Create book/src/components/ChatWidget/ChatWindow.tsx with expandable chat UI
- [ ] T049 [P] [US2] Create book/src/components/ChatWidget/MessageList.tsx for conversation display
- [ ] T050 [P] [US2] Create book/src/components/ChatWidget/InputBar.tsx with send button and character counter
- [ ] T051 [P] [US2] Create book/src/components/ChatWidget/styles.module.css with widget styling
- [ ] T052 [US2] Inject ChatWidget globally via book/src/theme/Root.tsx wrapper

### Integration

- [ ] T053 [US2] Create book/src/services/chatApi.ts with fetch wrapper for chat endpoints
- [ ] T054 [US2] Add error handling in ChatWidget for API unavailability (show friendly message)
- [ ] T055 [US2] Add out-of-scope detection display when isOutOfScope=true in response

**Checkpoint**: User Story 2 complete - chatbot answers questions using book content

---

## Phase 5: User Story 3 - Contextual Text Selection (Priority: P3)

**Goal**: Readers can select text and ask chatbot about that specific content

**Independent Test**: Select paragraph about Isaac Sim, click "Ask about this", verify contextual response

### Frontend TextSelector

- [ ] T056 [P] [US3] Create book/src/components/TextSelector/index.tsx with Selection API listener
- [ ] T057 [P] [US3] Create book/src/components/TextSelector/ContextMenu.tsx with "Ask about this" tooltip
- [ ] T058 [P] [US3] Create book/src/components/TextSelector/styles.module.css for tooltip styling
- [ ] T059 [US3] Inject TextSelector globally via book/src/theme/Root.tsx (alongside ChatWidget)

### Integration

- [ ] T060 [US3] Connect TextSelector to ChatWidget via React context or custom event
- [ ] T061 [US3] Update ChatWidget to display selected text context above input field
- [ ] T062 [US3] Update api/src/api/chat.py to handle context parameter in ChatRequest
- [ ] T063 [US3] Add text length validation (>2000 chars shows truncation notice) in TextSelector

**Checkpoint**: User Story 3 complete - selected text queries receive contextual responses

---

## Phase 6: User Story 4 - View Code Examples (Priority: P4)

**Goal**: Readers can view code examples with syntax highlighting and copy functionality

**Independent Test**: Navigate to ROS 2 tutorial, verify Python code has highlighting and copy button works

### Frontend CodeBlock

- [ ] T064 [P] [US4] Create book/src/components/CodeBlock/index.tsx wrapping Docusaurus CodeBlock
- [ ] T065 [P] [US4] Create book/src/components/CodeBlock/CopyButton.tsx with clipboard copy functionality
- [ ] T066 [P] [US4] Create book/src/components/CodeBlock/styles.module.css with enhanced styling
- [ ] T067 [US4] Configure book/src/theme/CodeBlock/index.tsx to use custom CodeBlock component

### Content Enhancement

- [ ] T068 [US4] Review and enhance code examples in book/docs/module-1-ros2/*.md with proper language tags
- [ ] T069 [P] [US4] Review and enhance code examples in book/docs/module-2-gazebo/*.md
- [ ] T070 [P] [US4] Review and enhance code examples in book/docs/module-3-isaac/*.md
- [ ] T071 [P] [US4] Review and enhance code examples in book/docs/module-4-vla/*.md

**Checkpoint**: User Story 4 complete - all code examples display with syntax highlighting and are copyable

---

## Phase 7: User Story 5 - Chatbot Source Citations (Priority: P5)

**Goal**: Chatbot responses include clickable source citations linking to book sections

**Independent Test**: Ask about Nav2, verify response includes "Source: Module 3" with working link

### Backend Enhancement

- [ ] T072 [US5] Update api/src/services/rag_service.py to include citation URLs from chunk metadata
- [ ] T073 [US5] Ensure api/src/models/content.py Citation model includes relevanceScore

### Frontend Citation Display

- [ ] T074 [P] [US5] Create book/src/components/ChatWidget/CitationList.tsx for displaying source links
- [ ] T075 [US5] Update book/src/components/ChatWidget/MessageList.tsx to render citations below responses
- [ ] T076 [US5] Add click handler to navigate to cited section via React Router or window.location

### Content Metadata

- [ ] T077 [US5] Update api/scripts/ingest_content.py to extract heading anchors for precise URL fragments

**Checkpoint**: User Story 5 complete - 80% of responses include valid source citations

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T078 [P] Create book/static/img/logo.svg with Physical AI book logo
- [ ] T079 [P] Create book/static/img/favicon.ico for browser tab
- [ ] T080 Add loading states to ChatWidget during API calls
- [ ] T081 Add rate limit display (X questions remaining) to ChatWidget header
- [ ] T082 [P] Create api/Dockerfile for Cloud Run deployment
- [ ] T083 Run Lighthouse audit on book/ and address performance issues
- [ ] T084 Verify CORS configuration works between GitHub Pages and Cloud Run
- [ ] T085 Run ingest_content.py to populate Qdrant with all book content
- [ ] T086 Execute quickstart.md validation to confirm setup instructions work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 - Content creation, no backend needed
- **Phase 4 (US2)**: Depends on Phase 2 + Phase 3 (needs content to ingest)
- **Phase 5 (US3)**: Depends on Phase 4 (needs chatbot working)
- **Phase 6 (US4)**: Depends on Phase 2 only (independent of chatbot)
- **Phase 7 (US5)**: Depends on Phase 4 (needs chatbot working)
- **Phase 8 (Polish)**: Depends on all user stories

### User Story Dependencies

```text
US1 (Content) ──┬──► US2 (Chatbot) ──┬──► US3 (Text Selection)
                │                    │
                │                    └──► US5 (Citations)
                │
                └──► US4 (Code Examples) [Independent]
```

### Parallel Opportunities by Phase

**Phase 1**: T002-T010 can run in parallel (8 tasks)
**Phase 2**: T012-T017 can run in parallel after T011 (6 tasks)
**Phase 3**: T018-T032 can run in parallel (15 content files)
**Phase 4**: T035-T036 models parallel, T047-T051 components parallel
**Phase 5**: T056-T058 parallel
**Phase 6**: T064-T066 parallel, T068-T071 parallel
**Phase 7**: T074 parallel with backend work

---

## Parallel Example: Phase 3 (User Story 1 Content)

```bash
# Launch all Module 1 content in parallel:
Task: "Create book/docs/module-1-ros2/week-1-intro.md" [T020]
Task: "Create book/docs/module-1-ros2/week-2-sensors.md" [T021]
Task: "Create book/docs/module-1-ros2/week-3-nodes.md" [T022]
Task: "Create book/docs/module-1-ros2/week-4-topics.md" [T023]
Task: "Create book/docs/module-1-ros2/week-5-services.md" [T024]

# Then Module 2, 3, 4 content (all parallel with each other)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Browse Content)
4. **STOP and VALIDATE**: Deploy book to GitHub Pages, verify navigation
5. **MVP ACHIEVED**: Readers can browse all 13 weeks of content

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Content) → Deploy → MVP! (Static book)
3. Add US2 (Chatbot) → Deploy → Interactive Q&A
4. Add US4 (Code Examples) → Deploy → Enhanced code display
5. Add US3 (Text Selection) → Deploy → Contextual queries
6. Add US5 (Citations) → Deploy → Full trust features
7. Polish → Final deployment

---

## Summary

| Phase | User Story | Task Count | Parallel Tasks |
|-------|------------|------------|----------------|
| 1 | Setup | 10 | 8 |
| 2 | Foundational | 7 | 6 |
| 3 | US1 - Browse Content | 17 | 15 |
| 4 | US2 - Chatbot Q&A | 21 | 8 |
| 5 | US3 - Text Selection | 8 | 4 |
| 6 | US4 - Code Examples | 8 | 7 |
| 7 | US5 - Citations | 6 | 1 |
| 8 | Polish | 9 | 4 |
| **Total** | | **86** | **53** |

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 = 34 tasks
