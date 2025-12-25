# Quickstart: Physical AI & Humanoid Robotics Book

## Prerequisites

- Node.js 18+ (for Docusaurus)
- Python 3.11+ (for FastAPI backend)
- Git
- OpenAI API key
- Qdrant Cloud account (free tier)
- Neon Postgres account (free tier, optional)

## 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/physical-ai-book.git
cd physical-ai-book

# Install frontend dependencies
cd book
npm install

# Install backend dependencies
cd ../api
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Environment Configuration

### Backend (.env)

Create `api/.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=book_content

# Optional: Neon Postgres (if persistent storage needed)
# DATABASE_URL=postgresql://user:pass@host/db

# App Config
CORS_ORIGINS=http://localhost:3000,https://your-github-pages-url
SESSION_SECRET=your-random-secret-key
RATE_LIMIT_PER_SESSION=50
```

### Frontend

Create `book/.env`:

```env
REACT_APP_API_URL=http://localhost:8000
```

## 3. Initialize Vector Store

```bash
cd api

# Create Qdrant collection
python scripts/init_qdrant.py

# Ingest book content (after writing content)
python scripts/ingest_content.py --docs-path ../book/docs
```

## 4. Run Development Servers

### Terminal 1: Backend API

```bash
cd api
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

### Terminal 2: Frontend Book

```bash
cd book
npm start
```

Visit:
- Book: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 5. Verify Setup

### Test API Health

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "dependencies": {
    "qdrant": "up",
    "openai": "up"
  }
}
```

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is ROS 2?"}'
```

Expected response:
```json
{
  "id": "uuid-here",
  "message": "ROS 2 (Robot Operating System 2) is...",
  "citations": [
    {
      "title": "Module 1: ROS 2 Fundamentals",
      "url": "/docs/module-1-ros2/week-3-nodes"
    }
  ],
  "questionsRemaining": 49
}
```

## 6. Content Development

### Add New Content

1. Create markdown file in `book/docs/module-X/`:

```markdown
---
sidebar_position: 1
---

# Week X: Topic Title

Introduction paragraph...

## Section Heading

Content with code examples:

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
```

2. Update sidebar in `book/sidebars.ts`

3. Re-ingest content:

```bash
cd api
python scripts/ingest_content.py --docs-path ../book/docs
```

## 7. Deployment

### Deploy Book to GitHub Pages

```bash
cd book
npm run build
npm run deploy
```

### Deploy API to Cloud Run

```bash
cd api

# Build container
docker build -t physical-ai-api .

# Push to Container Registry
docker tag physical-ai-api gcr.io/your-project/physical-ai-api
docker push gcr.io/your-project/physical-ai-api

# Deploy to Cloud Run
gcloud run deploy physical-ai-api \
  --image gcr.io/your-project/physical-ai-api \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=...,QDRANT_URL=..."
```

## Common Issues

### "Qdrant connection failed"

- Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Check Qdrant Cloud dashboard for cluster status

### "OpenAI rate limit exceeded"

- Check OpenAI dashboard for usage limits
- Consider implementing request queuing

### "CORS error in browser"

- Verify `CORS_ORIGINS` includes your frontend URL
- Ensure no trailing slashes in URLs

## Project Structure Reference

```text
physical-ai-book/
├── book/                    # Docusaurus frontend
│   ├── docs/               # Course content (Markdown)
│   ├── src/components/     # React components (ChatWidget)
│   └── docusaurus.config.ts
├── api/                     # FastAPI backend
│   ├── src/
│   │   ├── main.py
│   │   ├── services/       # RAG, embeddings, vector store
│   │   └── api/            # Endpoints
│   ├── scripts/            # Ingestion scripts
│   └── tests/
└── specs/                   # Feature specifications
```
