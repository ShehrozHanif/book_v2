# Physical AI & Humanoid Robotics - AI-Native Textbook

## Live Deployment

| Service | URL | Status |
|---------|-----|--------|
| **Textbook (Frontend)** | [shehrozhanif.github.io/book_v2](https://shehrozhanif.github.io/book_v2/docs/intro) | Deployed on GitHub Pages |
| **Backend API** | [book-backend-yart.onrender.com](https://book-backend-yart.onrender.com) | Deployed on Render |
| **Database** | Neon PostgreSQL (cloud) | Connected |
| **Vector Store** | Qdrant Cloud | 179 indexed passages |

---

## Project Overview

An AI-native textbook for teaching **Physical AI & Humanoid Robotics**, built entirely using **Spec-Driven Development (SDD)** with **Claude Code** as the AI development partner. The project features:

- **22-chapter textbook** across 5 modules (80,000+ words)
- **RAG-powered chatbot** for interactive Q&A over textbook content
- **User authentication** with JWT-based login/registration
- **Personalized learning** with adaptive difficulty, progress tracking, achievements, and statistics
- **Urdu translation** for bilingual chatbot responses with RTL support
- **9 specialized Claude Code sub-agents** for automated development

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Docusaurus 3 + React 18 + TypeScript |
| **Backend** | FastAPI + Python 3.10 + Uvicorn |
| **Database** | Neon PostgreSQL (async SQLAlchemy ORM) |
| **Vector DB** | Qdrant Cloud (1536-dim OpenAI embeddings) |
| **AI/LLM** | OpenAI GPT-4o-mini + text-embedding-3-small |
| **Auth** | JWT (PyJWT) + bcrypt password hashing |
| **Deployment** | GitHub Pages (frontend) + Render (backend) |
| **Dev Tools** | Claude Code + Spec-Kit Plus + GitHub Actions |

---

## Project Structure

```
book/
├── frontend/textbook-site/     # Docusaurus frontend
│   ├── docs/                   # 22 chapters in 5 modules
│   ├── src/                    # React components & services
│   └── docusaurus.config.js    # Site configuration
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/                # Chat routes, rate limiter, error handling
│   │   ├── services/           # RAG pipeline (embedding, retrieval, generation)
│   │   ├── models/             # Database & Pydantic schemas
│   │   ├── database/           # Connection pooling, session management
│   │   └── personalization/    # User system (auth, progress, achievements, translation)
│   ├── Dockerfile              # Production container
│   └── requirements.txt        # Python dependencies
├── specs/                      # 6 feature specifications (SDD)
│   ├── 001-rag-chatbot/
│   ├── 002-content-writing/
│   ├── 003-personalization/
│   ├── 004-deployment/
│   ├── 005-textbook-frontend/
│   └── 006-urdu-translation/
├── .claude/agents/             # 9 specialized sub-agents
├── .specify/                   # Spec-Kit Plus templates & constitution
├── render.yaml                 # Render deployment blueprint
└── .github/workflows/          # GitHub Actions CI/CD
```

---

## Features

### RAG Chatbot
- Embeds user questions using OpenAI `text-embedding-3-small`
- Retrieves relevant passages from Qdrant vector database (179 indexed chunks)
- Generates contextual answers using GPT-4o-mini with retrieved context
- Multi-turn conversation support with history
- Security: injection detection, off-topic filtering, query sanitization

### User Authentication & Profiles
- JWT-based registration and login
- User profile with background assessment
- Protected routes requiring authentication

### Personalized Learning
- 3 adaptive difficulty levels (Beginner / Intermediate / Advanced)
- Progress tracking per chapter with mastery scoring
- 32 unlockable achievements with badge rendering
- Practice questions with retry functionality
- Learning statistics with trend analysis and recommendations
- Advanced challenges for high-mastery users (>85%)

### Urdu Translation (Bilingual Support)
- Toggle between English and Urdu chatbot responses
- RTL rendering for Urdu text
- 150+ technical term glossary
- Language preference persistence across sessions
- Admin translation management dashboard
- Rate-limited glossary API (100 req/min)

### Textbook Content
- 5 modules, 22 chapters, 80,000+ words
- 48 validated code examples
- 92 APA-formatted citations
- Expert-reviewed (avg. 96/100 score)
- RAG-validated (92.25% avg. relevance across 30 test queries)

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or Neon cloud database)
- OpenAI API key
- Qdrant Cloud account

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt

# Create .env file with:
# DATABASE_URL=postgresql://...
# OPENAI_API_KEY=sk-...
# QDRANT_URL=https://...
# QDRANT_API_KEY=...
# JWT_SECRET_KEY=...

uvicorn src.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend/textbook-site
npm install
npm run start
# Opens at http://localhost:3000/book
```

---

## API Endpoints

### Core
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| POST | `/api/v1/chat` | RAG chatbot query |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/register` | Register new user |
| POST | `/api/v1/users/login` | User login (returns JWT) |
| GET | `/api/v1/users/me` | Get current user profile |

### Personalization
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/{id}/progress` | Learning progress |
| POST | `/api/v1/users/{id}/progress/{ch}/complete` | Mark chapter complete |
| GET | `/api/v1/users/{id}/achievements` | User achievements |
| POST | `/api/v1/users/{id}/progress/{ch}/practice` | Submit practice attempt |
| GET | `/api/v1/users/{id}/statistics` | Learning statistics |

### Translation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chatbot/translate` | Translate chatbot response |
| GET | `/api/v1/glossary/search` | Search technical glossary |
| GET/PUT | `/api/v1/language-preferences/{id}` | Language preferences |

Full API documentation available at `/docs` (Swagger UI) when running the backend.

---

## Testing

- **614 automated tests** (100% pass rate)
- **53 manual QA test cases** across 5 browsers
- **15 performance benchmarks** (response <3s, toggle <1s, search <500ms)
- **12 end-to-end test flows**

```bash
cd backend
python -m pytest                          # Run all tests
python -m pytest src/personalization/tests/  # Personalization tests only
```

---

## Development Methodology

This project was built using **Spec-Driven Development (SDD)** with **Spec-Kit Plus**:

1. **Constitution** - Project principles and quality standards
2. **Specification** - Feature requirements (6 specs)
3. **Planning** - Architecture decisions and design
4. **Tasks** - Testable implementation tasks
5. **Implementation** - Code with test coverage
6. **Documentation** - API docs, guides, deployment playbooks

**9 Claude Code Sub-Agents** provided specialized capabilities:
- Backend Dev, Frontend Dev, RAG Chatbot, Content Writing
- Code Generation, Testing/QA, DevOps/Deployment
- Documentation, Translation

See [complete_flow.md](./complete_flow.md) for the full project journey.

---

## Project Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 175 (98 + 77) |
| Completion | 100% |
| Automated Tests | 614 |
| QA Test Cases | 53 |
| Code Lines (backend) | 33,000+ |
| Frontend Files | 57 TypeScript files |
| Documentation | 7,300+ lines |
| Textbook Words | 80,000+ |
| Chapters | 22 |
| Code Examples | 48 |
| Achievements | 32 |
| Prompt History Records | 47 |
| Sub-Agents | 9 |
| Feature Specs | 6 |

---

## Repository

- **GitHub**: [github.com/ShehrozHanif/book_v2](https://github.com/ShehrozHanif/book_v2)
- **Branch**: `001-rag-chatbot`
