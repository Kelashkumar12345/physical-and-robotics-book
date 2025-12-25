# Physical AI & Humanoid Robotics Constitution

## Core Principles

### I. Simulation-First Development
All robotics algorithms and behaviors MUST be developed and validated in simulation (Isaac Sim, Gazebo, Unity) before deployment to physical hardware. This ensures safety, rapid iteration, and reproducibility.

### II. Modular Architecture
System components MUST be loosely coupled and independently deployable:
- Frontend (Docusaurus static site)
- Backend (FastAPI API service)
- Vector Store (Qdrant Cloud)
- Database (Neon Postgres for session tracking)

Each module has clear interfaces and can be updated without affecting others.

### III. Documentation-as-Code
All course content MUST be stored as Markdown files under version control. Documentation is treated as a first-class artifact:
- Content lives in `book/docs/`
- Changes tracked via Git
- Deployable through CI/CD pipeline

### IV. RAG-Enabled Content
The embedded chatbot MUST use Retrieval-Augmented Generation to provide accurate, book-grounded responses:
- Content indexed in vector store (Qdrant)
- Semantic search for relevant chunks
- Citations link back to source sections
- Out-of-scope detection for non-book topics

### V. Practical Learning Focus
Every concept MUST include hands-on examples:
- Code snippets with syntax highlighting
- Step-by-step tutorials
- Real-world ROS 2, URDF, sensor integration examples
- Executable demonstrations where possible

### VI. Sim-to-Real Methodology
The curriculum follows a progressive sim-to-real pipeline:
1. Isaac Sim (high-fidelity NVIDIA simulation)
2. Gazebo (ROS 2 integration testing)
3. Jetson/Edge deployment (hardware validation)

This ensures learners understand the full development lifecycle from simulation to physical robot deployment.

## Technology Constraints

- **Frontend**: Docusaurus 3.x, TypeScript, React 18
- **Backend**: Python 3.11+, FastAPI, Pydantic
- **AI/ML**: OpenAI Agents SDK, text-embedding-3-small
- **Storage**: Qdrant Cloud (vectors), Neon Postgres (sessions)
- **Deployment**: GitHub Pages (static), Cloud Run (API)

## Quality Standards

- Page load time: <3 seconds
- Chatbot response time: <5 seconds
- Uptime target: 99%
- Mobile-responsive design required
- Code examples must include syntax highlighting

## Governance

This constitution supersedes all other development practices. Any deviation requires:
1. Documentation of the exception
2. Justification of why the principle cannot be followed
3. Approval via ADR (Architecture Decision Record)

**Version**: 1.0.0 | **Ratified**: 2025-12-25 | **Last Amended**: 2025-12-25
