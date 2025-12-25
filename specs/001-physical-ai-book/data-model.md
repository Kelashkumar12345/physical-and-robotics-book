# Data Model: Physical AI & Humanoid Robotics Book with RAG Chatbot

**Date**: 2025-12-25
**Feature**: 001-physical-ai-book

## Entity Overview

```text
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Module    │──1:N──│    Week     │──1:N──│    Topic    │
└─────────────┘       └─────────────┘       └─────────────┘
                                                   │
                                                   │ 1:N
                                                   ▼
                                            ┌─────────────┐
                                            │ContentChunk │
                                            └──────┬──────┘
                                                   │
                      ┌────────────────────────────┤
                      │                            │
                      ▼                            ▼
               ┌─────────────┐              ┌─────────────┐
               │ Conversation│──1:N────────│   Message   │
               │  (Session)  │              └──────┬──────┘
               └─────────────┘                     │
                                                   │ N:M
                                                   ▼
                                            ┌─────────────┐
                                            │  Citation   │
                                            └─────────────┘
```

## Entities

### Module

Represents a major course section (1-4).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | string | PK, format: "module-{n}" | Unique identifier |
| number | int | 1-4 | Module sequence number |
| title | string | required, max 100 | Display title |
| slug | string | unique, lowercase | URL-safe identifier |
| description | string | max 500 | Brief module overview |
| weeks | Week[] | 1:N relationship | Weeks in this module |

**Example**:
```json
{
  "id": "module-1",
  "number": 1,
  "title": "The Robotic Nervous System (ROS 2)",
  "slug": "module-1-ros2",
  "description": "Middleware for robot control..."
}
```

### Week

Represents a time-based content unit (1-13).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | string | PK, format: "week-{n}" | Unique identifier |
| number | int | 1-13 | Week sequence number |
| title | string | required, max 100 | Display title |
| slug | string | unique, lowercase | URL-safe identifier |
| moduleId | string | FK → Module.id | Parent module |
| topics | Topic[] | 1:N relationship | Topics covered this week |

**Example**:
```json
{
  "id": "week-3",
  "number": 3,
  "title": "ROS 2 Nodes and Topics",
  "slug": "week-3-nodes",
  "moduleId": "module-1"
}
```

### Topic

An individual learning concept with content.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | string | PK, UUID | Unique identifier |
| title | string | required, max 200 | Topic heading |
| slug | string | unique within week | URL-safe identifier |
| weekId | string | FK → Week.id | Parent week |
| content | string | required | Markdown content |
| codeExamples | CodeExample[] | optional | Associated code blocks |
| order | int | >= 0 | Display order within week |

### ContentChunk

A segment of book content indexed for semantic search.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | string | PK, UUID | Unique identifier |
| topicId | string | FK → Topic.id | Source topic |
| content | string | required, ~500 tokens | Chunk text content |
| embedding | float[1536] | required | Vector embedding |
| metadata | object | required | Search metadata |

**Metadata Structure**:
```json
{
  "module": "module-1-ros2",
  "week": "week-3-nodes",
  "topic": "creating-ros2-nodes",
  "heading": "Creating ROS 2 Nodes",
  "url": "/docs/module-1-ros2/week-3-nodes#creating-ros-2-nodes",
  "chunkIndex": 0
}
```

### Conversation (Session-only)

A user's chat session with the chatbot. **In-memory only per clarification**.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sessionId | string | PK, UUID | Browser session identifier |
| messages | Message[] | 1:N, max 100 | Conversation messages |
| questionCount | int | 0-50 | Rate limit counter |
| createdAt | datetime | auto | Session start time |
| context | string | optional | Selected text context |

**Lifecycle**: Created on first message, cleared when browser session ends.

### Message

A single user query or chatbot response.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | string | PK, UUID | Unique identifier |
| sessionId | string | FK → Conversation | Parent session |
| role | enum | "user" \| "assistant" | Message author |
| content | string | required, max 4000 | Message text |
| citations | Citation[] | optional | Source references |
| timestamp | datetime | auto | Message time |

### Citation

A reference linking a response to a book section.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | string | PK, UUID | Unique identifier |
| messageId | string | FK → Message.id | Parent message |
| chunkId | string | FK → ContentChunk.id | Source chunk |
| title | string | required | Display text |
| url | string | required, valid URL | Link to section |
| relevanceScore | float | 0.0-1.0 | Similarity score |

## Validation Rules

### Content Validation

| Rule | Applies To | Constraint |
|------|------------|------------|
| Module count | Module | Exactly 4 modules |
| Week count | Week | Exactly 13 weeks total |
| Week distribution | Week | Weeks 1-5 in Module 1, 6-7 in Module 2, 8-10 in Module 3, 11-13 in Module 4 |
| Slug format | All slugs | lowercase, alphanumeric + hyphens |
| Chunk size | ContentChunk | 400-600 tokens |
| Embedding dimension | ContentChunk | Exactly 1536 floats |

### Session Validation

| Rule | Applies To | Constraint |
|------|------------|------------|
| Rate limit | Conversation | questionCount <= 50 |
| Message length | Message.content | <= 4000 characters |
| Context length | Conversation.context | <= 2000 characters (per edge case) |
| Session timeout | Conversation | Cleared on browser session end |

## State Transitions

### Conversation Lifecycle

```text
[New Session] ──► [Active] ──► [Rate Limited] ──► [Session End]
     │              │  ▲              │
     │              │  │              │
     │              ▼  │              │
     │         [Question Asked]       │
     │         (count < 50)           │
     │                                │
     └────────────────────────────────┘
              (browser closes)
```

### States

| State | questionCount | Behavior |
|-------|---------------|----------|
| New Session | 0 | Created on first widget open |
| Active | 1-49 | Questions accepted |
| Rate Limited | 50 | New questions rejected, browsing continues |
| Session End | - | All data cleared |

## Indexes

### Qdrant Collection: `book_content`

```json
{
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "module": "keyword",
    "week": "keyword",
    "topic": "keyword",
    "heading": "text",
    "url": "keyword"
  }
}
```

**Index Usage**:
- Semantic search: Vector similarity on `embedding`
- Filter by module: `payload.module == "module-1-ros2"`
- Filter by week: `payload.week == "week-3-nodes"`
