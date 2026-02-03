# Complete Spec-Kit Plus Workflow Guide
## Building the Physical AI Textbook Hackathon with Spec-Driven Development

---

## 📚 Table of Contents

1. [Understanding Spec-Kit Plus](#understanding-spec-kit-plus)
2. [Pre-Setup Requirements](#pre-setup-requirements)
3. [Step-by-Step Implementation Guide](#step-by-step-implementation-guide)
4. [Spec-Kit Plus File Structure](#spec-kit-plus-file-structure)
5. [Commands & Tools Reference](#commands--tools-reference)
6. [Subagent & Skill Creation Process](#subagent--skill-creation-process)
7. [Full Workflow Timeline](#full-workflow-timeline)

---

## 🎯 Understanding Spec-Kit Plus

### What is Spec-Kit Plus?

**Spec-Kit Plus** is a framework for **Spec-Driven Development (SDD)** that ensures:
- Clear, documented requirements (SPEC)
- Well-architected design (PLAN)
- Actionable, testable tasks (TASKS)
- Systematic implementation (IMPLEMENTATION)
- Intelligent agents doing the work (SUBAGENTS)

### The SDD Flow

```
Requirements → Specification → Architecture Plan → Tasks → Implementation
                     ↓              ↓              ↓
              (What?)        (How?)        (Who does what?)
```

### Key Principles

1. **Clarity First** - Write what you need before how to build it
2. **Architecture Matters** - Plan before coding
3. **Testability** - Every task has acceptance criteria
4. **Traceability** - Track decisions with ADRs (Architecture Decision Records)
5. **Automation** - Use agents to execute plans

---

## 📋 Pre-Setup Requirements

### Before You Start:

1. **GitHub Repository Setup**
   ```bash
   git clone <your-repo>
   cd book
   git branch -b feature/spec-kit-setup
   ```

2. **Install Spec-Kit Plus Tools**
   ```bash
   # Check if spec-kit-plus is initialized
   ls -la .specify/

   # If not, clone the template
   git clone https://github.com/panaversity/spec-kit-plus .specify
   ```

3. **Project Directory Structure**
   ```
   book/
   ├── .specify/                    # Spec-Kit Plus folder
   │   ├── templates/              # Templates for specs, plans, tasks
   │   ├── scripts/                # Helper scripts
   │   ├── memory/
   │   │   └── constitution.md     # Project principles
   │   └── commands/               # Available commands
   ├── specs/
   │   └── textbook/              # Feature folder for textbook
   │       ├── spec.md            # Feature specification
   │       ├── plan.md            # Architecture plan
   │       ├── tasks.md           # Actionable tasks
   │       └── agents.md          # Subagents & skills
   ├── history/
   │   ├── prompts/               # Prompt History Records (PHR)
   │   │   ├── constitution/
   │   │   ├── textbook/
   │   │   └── general/
   │   └── adr/                   # Architecture Decision Records
   ├── README.md
   ├── AGENTS_AND_SKILLS_ANALYSIS.md
   └── SPEC_KIT_PLUS_WORKFLOW.md
   ```

---

## 🔧 Step-by-Step Implementation Guide

## **PHASE 0: Constitution & Project Setup** ⚙️

### **Step 1: Create/Review Project Constitution**

**What is Constitution?**
- Core principles governing your project
- Code standards, testing requirements, architecture patterns
- Team agreements on quality and process

**Action:**
```bash
# Create or update constitution
# File: .specify/memory/constitution.md

# Contents should include:
# 1. Project Vision
# 2. Code Quality Standards
# 3. Testing Requirements
# 4. Architecture Principles
# 5. Team Agreements
```

**Example Constitution Sections:**

```markdown
# Physical AI & Humanoid Robotics Textbook - Constitution

## Project Vision
Create an AI-native, interactive textbook with:
- 4 comprehensive modules (ROS 2, Gazebo, Isaac, VLA)
- RAG-powered chatbot for Q&A
- Multilingual support (English + Urdu)
- Personalized learning paths

## Code Standards
- Python 3.10+ with type hints
- FastAPI for backend
- React/TypeScript for frontend
- Docusaurus for documentation site
- PEP 8 compliance

## Testing Requirements
- Minimum 90% code coverage
- Unit, integration, and E2E tests
- All endpoints must have tests
- RAG pipeline must be testable

## Architecture Principles
- Microservices-ready (separate frontend, backend, chatbot)
- Database-agnostic ORM (SQLAlchemy)
- Vector embeddings for RAG
- Modular code with clear interfaces
- Configuration via environment variables

## Team Agreements
- All decisions documented in ADRs
- Code reviewed before merge
- Tests pass before deployment
- Documentation updated with code
```

---

## **PHASE 1: Write the SPECIFICATION** 📝

### **Step 2: Create Feature Specification**

**What is a Specification?**
- Clear statement of WHAT needs to be built
- Requirements, acceptance criteria, constraints
- No architectural decisions yet
- User stories and use cases

**File Location:** `specs/textbook/spec.md`

**Use Claude Code Skill:**
```bash
/sp.specify
# OR manually create specs/textbook/spec.md
```

**Specification Structure:**

```markdown
# Physical AI & Humanoid Robotics Textbook - Specification

## 1. Feature Overview
### What is this?
Interactive AI-native textbook for teaching Physical AI and Humanoid Robotics

### Why build it?
- Support Panaversity's mission to teach cutting-edge AI
- Create first AI-native technical textbook
- Launch portal for AI-native book creation
- Provide foundation for O/A Level, Science, Engineering, Medical books

### Success Metrics
- Base: 100 points (book + RAG chatbot)
- Bonus: Up to 200 points (authentication, personalization, translation, agents)

## 2. Requirements (Must Have)
### Functional Requirements
- **FR1:** Create textbook with 4 modules covering Physical AI concepts
- **FR2:** Deploy book to GitHub Pages or Vercel
- **FR3:** Build RAG chatbot that answers questions about book content
- **FR4:** Chatbot must support text selection-based queries
- **FR5:** Use Docusaurus as book framework
- **FR6:** Use OpenAI API for LLM responses
- **FR7:** Use Qdrant Cloud for vector embeddings
- **FR8:** Use Neon Postgres for data storage

### Non-Functional Requirements
- **NF1:** Book loads in < 2 seconds
- **NF2:** Chat response in < 3 seconds
- **NF3:** Support mobile and desktop browsers
- **NF4:** 99% uptime for deployment
- **NF5:** HTTPS/SSL enabled

## 3. Bonus Requirements (Nice to Have)
- **BR1:** User authentication with better-auth.com
- **BR2:** User profiling (software/hardware background)
- **BR3:** Content personalization by chapter
- **BR4:** Urdu translation support
- **BR5:** Claude Code subagents for content generation

## 4. Constraints
- Deadline: November 30, 2025 at 6:00 PM
- Maximum 90-second demo video
- Must be publicly available GitHub repo
- Must work without local setup complications

## 5. Out of Scope
- Hardware for robots (not required)
- Real robot deployment
- Mobile app (web only)
- Video hosting infrastructure

## 6. Acceptance Criteria
- [ ] All 4 modules written with 50+ pages
- [ ] Chatbot answers 95%+ of test queries correctly
- [ ] Book renders correctly on mobile
- [ ] All links and code examples work
- [ ] Zero security vulnerabilities (OWASP)
- [ ] Deployment URL is publicly accessible
```

**Key Point:** Specification should answer "WHAT" not "HOW"

---

## **PHASE 2: Create Architecture PLAN** 🏗️

### **Step 3: Design Architecture & Create Plan**

**What is a Plan?**
- HOW you will build it
- Technology choices with rationale
- Architecture decisions
- System design and data flow
- Risk mitigation

**File Location:** `specs/textbook/plan.md`

**Use Claude Code Skill:**
```bash
/sp.plan
# OR manually create specs/textbook/plan.md
```

**Plan Structure:**

```markdown
# Physical AI & Humanoid Robotics Textbook - Architecture Plan

## 1. Architecture Overview

### System Components
```
┌─────────────────────────────────────────────┐
│         FRONTEND (Docusaurus + React)       │
│  - Book content (4 modules)                 │
│  - Chatbot widget                           │
│  - Auth UI (Login/Signup)                   │
│  - Personalization panel                    │
│  - Language toggle (English/Urdu)           │
└────────────┬────────────────────────────────┘
             │ (API calls)
             ↓
┌─────────────────────────────────────────────┐
│     BACKEND (FastAPI + Python)              │
│  - /chat - Send questions                   │
│  - /auth/signup - User registration         │
│  - /auth/signin - User login                │
│  - /personalize - Get personalized content  │
│  - /translate - Get Urdu translation        │
└────────────┬────────────────────────────────┘
             │ (Database queries)
    ┌────────┴──────────────┐
    ↓                       ↓
┌──────────────┐      ┌──────────────┐
│ Neon Postgres│      │ Qdrant Cloud │
│  - Users     │      │  - Embeddings│
│  - Chapters  │      │  - Metadata  │
│  - Chat hist │      │  - Vectors   │
└──────────────┘      └──────────────┘
```

## 2. Technology Stack Rationale

### Frontend
**Choice:** Docusaurus 3 + React + Tailwind CSS
**Why:**
- Docusaurus specializes in technical documentation
- Built-in search and versioning
- GitHub Pages integration
- React for interactive chatbot widget
- Tailwind for responsive design

### Backend
**Choice:** FastAPI + Python
**Why:**
- Fast performance (async/await)
- Built-in OpenAPI documentation
- Easy integration with AI libraries (OpenAI, LangChain)
- Type hints for safety
- Excellent error handling

### Databases
**Choice:** Neon Postgres + Qdrant Cloud
**Why:**
- Neon: Serverless, scales automatically, free tier available
- Qdrant: Vector database optimized for RAG, free tier sufficient
- pgvector: Native vector support in Postgres
- Both support modern AI/ML workflows

### AI/ML
**Choice:** OpenAI API + LangChain
**Why:**
- GPT-4 best in class for reasoning
- OpenAI Whisper for voice (future)
- LangChain handles RAG orchestration
- Well-documented and reliable

## 3. Data Flow

### Chat Query Flow
```
User types question
    ↓
Frontend sends to /chat endpoint
    ↓
Backend receives query
    ↓
Query embedding generated (OpenAI)
    ↓
Vector search in Qdrant (semantic match)
    ↓
Retrieved chunks stored in Postgres
    ↓
Prompt built with context
    ↓
OpenAI API called with prompt
    ↓
Response streamed to frontend
    ↓
Chat saved to chat_history table
    ↓
Response displayed to user
```

### Authentication Flow
```
User clicks Signup
    ↓
Form with background questions (better-auth)
    ↓
User profile created in Postgres
    ↓
JWT token generated
    ↓
Token stored in browser (httpOnly cookie)
    ↓
Subsequent requests include token
    ↓
Backend validates token
    ↓
User data retrieved for personalization
```

## 4. Database Schema

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  name VARCHAR(255),
  software_background VARCHAR(255),
  hardware_background VARCHAR(255),
  learning_goals TEXT,
  preferred_difficulty VARCHAR(50) DEFAULT 'intermediate',
  preferred_language VARCHAR(10) DEFAULT 'en',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Chapters table
CREATE TABLE chapters (
  id SERIAL PRIMARY KEY,
  module_id INTEGER,
  chapter_number INTEGER,
  title VARCHAR(255),
  content_md TEXT,
  excerpt VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Chat history
CREATE TABLE chat_history (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  query TEXT NOT NULL,
  response TEXT,
  retrieved_chapters INTEGER[],
  created_at TIMESTAMP DEFAULT NOW()
);

-- Translations cache
CREATE TABLE translations (
  id SERIAL PRIMARY KEY,
  source_lang VARCHAR(10),
  target_lang VARCHAR(10),
  source_text TEXT,
  translated_text TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 5. API Endpoints Design

```
AUTH
POST   /auth/signup          - Register user with background questions
POST   /auth/signin          - Login user
POST   /auth/logout          - Logout user
GET    /auth/profile         - Get user profile
PUT    /auth/profile         - Update user profile

CHAT
POST   /chat                 - Send query, get response
GET    /chat/history         - Get user's chat history
POST   /chat/select          - Query from text selection
DELETE /chat/{id}            - Delete chat message

CONTENT
GET    /chapters/:moduleId   - Get chapters by module
GET    /chapter/:id          - Get chapter content
POST   /search               - Search book content

PERSONALIZATION
GET    /personalize/:chapterId - Get personalized content
PUT    /personalize/:chapterId - Save personalization preference

TRANSLATION
POST   /translate            - Get Urdu translation
GET    /translate/status     - Check translation progress

ADMIN
POST   /embed-content        - Embed book chapters to Qdrant
GET    /health               - Health check endpoint
```

## 6. Key Architectural Decisions

### Decision 1: Monolithic Backend vs Microservices
**Decision:** Monolithic FastAPI app
**Rationale:** Hackathon timeline, simpler deployment, single database
**Trade-off:** Less scalable but faster to build

### Decision 2: Client-side vs Server-side Rendering
**Decision:** Server-side rendering for personalization
**Rationale:** User profile needed before rendering, consistent experience
**Trade-off:** Slightly higher server load

### Decision 3: Embedding Strategy
**Decision:** Chunk-based embedding (not document-based)
**Rationale:** More granular search results, better Q&A accuracy
**Trade-off:** More vectors to store

### Decision 4: Authentication Method
**Decision:** JWT tokens in httpOnly cookies
**Rationale:** Secure, stateless, works with SPA
**Trade-off:** No revocation without blacklist

## 7. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| OpenAI API rate limits | Chat unavailable | Implement caching, queue system |
| Qdrant vector search fails | No relevant results | Fallback to keyword search |
| User authentication bugs | Security risk | Thorough testing, third-party audit |
| Translation quality poor | Bad UX | Use GPT-4 for translation, manual review |
| Database downtime | Complete outage | Neon backup, Postgres replication |

## 8. Deployment Strategy

### Frontend Deployment
- Build Docusaurus to static HTML/CSS/JS
- Deploy to GitHub Pages (free, automatic)
- Custom domain via DNS (optional)
- CDN provided by GitHub

### Backend Deployment
- Containerize FastAPI with Docker
- Deploy to Vercel Functions OR Railway OR Heroku
- Environment variables: OPENAI_API_KEY, DATABASE_URL, etc.
- Automatic CI/CD via GitHub Actions

### Database Deployment
- Neon: Create serverless Postgres instance
- Qdrant: Create cloud collection (free tier)
- Backups: Automatic (Neon), manual exports (Qdrant)

## 9. Monitoring & Operations

- FastAPI logs to stdout (Vercel/Railway captures)
- Database slow query logging
- Chat latency monitoring
- Error tracking with Sentry (free tier)
- Uptime monitoring with UptimeRobot

## 10. Future Scalability

- Separate chatbot service (if needed)
- Caching layer (Redis) for performance
- CDN for static assets
- Database replication for HA
- Queue system (Celery) for async tasks
```

**Key Point:** Plan should answer "HOW" with detailed technical decisions

---

## **PHASE 3: Generate TASKS** ✅

### **Step 4: Break Down Into Actionable Tasks**

**What are Tasks?**
- Granular, actionable items
- Assigned to specific agents/people
- Have acceptance criteria
- Have dependencies
- Testable and completable

**File Location:** `specs/textbook/tasks.md`

**Use Claude Code Skill:**
```bash
/sp.tasks
# OR manually create specs/textbook/tasks.md
```

**Tasks Structure Example:**

```markdown
# Physical AI & Humanoid Robotics Textbook - Tasks

## Task Categories

### 1. SETUP & INFRASTRUCTURE (Week 1)

#### Task 1.1: Initialize Project Structure
**Assigned to:** Frontend Dev Agent
**Depends on:** None
**Acceptance Criteria:**
- [ ] GitHub repo created and public
- [ ] Docusaurus installed and configured
- [ ] Sidebar navigation set up
- [ ] README.md created with setup instructions
- [ ] `.specify/` folder initialized
- [ ] specs/ folder structure created

**Testing:**
```bash
# Verify structure
ls -la .specify/
ls -la specs/textbook/
npm run start  # Should run without errors
```

---

#### Task 1.2: Set Up Neon Postgres Database
**Assigned to:** Backend Dev Agent
**Depends on:** None
**Acceptance Criteria:**
- [ ] Neon account created (free tier)
- [ ] Database instance created
- [ ] Connection string obtained
- [ ] pgvector extension enabled
- [ ] `.env` file created with DATABASE_URL
- [ ] Test connection from local machine

**Testing:**
```bash
psql $DATABASE_URL -c "SELECT version();"
psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

#### Task 1.3: Set Up Qdrant Cloud
**Assigned to:** RAG/Chatbot Agent
**Depends on:** None
**Acceptance Criteria:**
- [ ] Qdrant Cloud account created (free tier)
- [ ] Collection created with dimension 1536
- [ ] API key generated
- [ ] `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- [ ] Test connection from Python

**Testing:**
```python
from qdrant_client import QdrantClient
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
print(client.get_collections())
```

---

#### Task 1.4: Initialize FastAPI Backend
**Assigned to:** Backend Dev Agent
**Depends on:** None
**Acceptance Criteria:**
- [ ] FastAPI app created with proper structure
- [ ] CORS configured for localhost:3000
- [ ] `/health` endpoint returns 200
- [ ] Error handling middleware added
- [ ] Logging configured
- [ ] Requirements.txt created

**Testing:**
```bash
cd backend
uvicorn main:app --reload
curl http://localhost:8000/health  # Returns {"status": "ok"}
```

---

### 2. CONTENT CREATION (Week 2-3)

#### Task 2.1: Write Module 1 - ROS 2 Fundamentals
**Assigned to:** Content Writing Agent
**Depends on:** Task 1.1 (Docusaurus setup)
**Acceptance Criteria:**
- [ ] 5 chapters written (2000+ words each)
- [ ] Each chapter has learning objectives
- [ ] Practical code examples included
- [ ] End-of-chapter exercises (3-5 each)
- [ ] Assessment questions (5-10 each)
- [ ] All chapters in Markdown format
- [ ] No broken links or references

**Chapters:**
1. What is Physical AI?
2. ROS 2 Architecture
3. Nodes, Topics, and Services
4. Building ROS 2 Packages
5. Integration with Python Agents

**Testing:**
```bash
npm run build  # Should complete without errors
# Manual review: All content renders correctly
```

---

#### Task 2.2: Generate Code Examples for Module 1
**Assigned to:** Code Generation Agent
**Depends on:** Task 2.1
**Acceptance Criteria:**
- [ ] 10+ code examples generated
- [ ] All examples tested and working
- [ ] Examples have inline documentation
- [ ] Code follows Python/ROS 2 best practices
- [ ] Examples downloadable as `.py` files

**Examples:**
- ROS 2 node creation
- Topic publisher/subscriber
- Service server/client
- Launch file example
- Parameter configuration

**Testing:**
```bash
# Each example should run without errors
python example_node_creation.py &
python example_subscriber.py
# Should successfully communicate
```

---

#### Task 2.3: Write Module 2 - Gazebo & Simulation
**Assigned to:** Content Writing Agent
**Depends on:** Task 1.1
**Status:** Similar structure to Task 2.1
...

#### Task 2.4: Write Module 3 - NVIDIA Isaac
**Assigned to:** Content Writing Agent
**Depends on:** Task 1.1
**Status:** Similar structure to Task 2.1
...

#### Task 2.5: Write Module 4 - Vision-Language-Action
**Assigned to:** Content Writing Agent
**Depends on:** Task 1.1
**Status:** Similar structure to Task 2.1
...

---

### 3. BACKEND API DEVELOPMENT (Week 4)

#### Task 3.1: Create Database Schema
**Assigned to:** Backend Dev Agent
**Depends on:** Task 1.2
**Acceptance Criteria:**
- [ ] All tables created (users, chapters, chat_history, etc.)
- [ ] Indexes created for performance
- [ ] Constraints defined (FK, unique, etc.)
- [ ] Sample data inserted
- [ ] Migration script created

**Testing:**
```bash
python scripts/create_schema.py
psql $DATABASE_URL -c "\dt"  # List all tables
```

---

#### Task 3.2: Implement Authentication Endpoints
**Assigned to:** Backend Dev Agent
**Depends on:** Task 3.1
**Acceptance Criteria:**
- [ ] POST /auth/signup - creates user
- [ ] POST /auth/signin - returns JWT token
- [ ] POST /auth/logout - invalidates token
- [ ] GET /auth/profile - returns user data
- [ ] PUT /auth/profile - updates profile
- [ ] Password hashing with bcrypt
- [ ] JWT validation on protected routes

**Testing:**
```bash
# Signup test
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Should return user ID and JWT token
```

---

#### Task 3.3: Implement Chat Endpoints
**Assigned to:** Backend Dev Agent
**Depends on:** Task 3.1, Task 1.3
**Acceptance Criteria:**
- [ ] POST /chat - accepts query, returns response
- [ ] GET /chat/history - returns user's chat history
- [ ] POST /chat/select - handles text selection queries
- [ ] Chat history stored in database
- [ ] Response includes source chapters

**Testing:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is ROS 2?"}'
```

...

### 4. RAG CHATBOT DEVELOPMENT (Week 5)

#### Task 4.1: Create Content Embedding Pipeline
**Assigned to:** RAG/Chatbot Agent
**Depends on:** Task 2.1-2.5 (chapters), Task 1.3 (Qdrant)
**Acceptance Criteria:**
- [ ] All chapters extracted from Markdown
- [ ] Content chunked into 500-word segments
- [ ] Embeddings generated using OpenAI API
- [ ] Vectors stored in Qdrant with metadata
- [ ] Metadata includes chapter_id, section, title
- [ ] Script runs in < 30 minutes for all chapters

**Testing:**
```python
# Query test
from qdrant_client import QdrantClient
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
query_vector = embed_text("What is ROS 2?")
results = client.search(collection_name="book_embeddings", query_vector=query_vector, limit=5)
print(results)  # Should return 5 relevant chunks
```

---

#### Task 4.2: Implement Retrieval-Augmented Generation Logic
**Assigned to:** RAG/Chatbot Agent
**Depends on:** Task 4.1
**Acceptance Criteria:**
- [ ] Query embedding generated
- [ ] Top 5 chunks retrieved from Qdrant
- [ ] Chunks ranked by relevance
- [ ] Prompt built with context
- [ ] OpenAI API called
- [ ] Response includes citations

**Testing:**
```bash
# RAG pipeline test
python -m pytest tests/test_rag_pipeline.py
# Should achieve 90%+ accuracy on test questions
```

---

#### Task 4.3: Build Frontend Chatbot Widget
**Assigned to:** Frontend Dev Agent
**Depends on:** Task 1.1, Task 3.3
**Acceptance Criteria:**
- [ ] React component created
- [ ] Chat message display working
- [ ] Text input and send button functional
- [ ] Loading states shown
- [ ] Error messages displayed
- [ ] Text selection detection working
- [ ] Mobile responsive
- [ ] Styled with Tailwind CSS

**Testing:**
```bash
npm run test -- ChatWidget.test.tsx
# Should have > 90% coverage
```

---

### 5. AUTHENTICATION & PERSONALIZATION (Week 6)

#### Task 5.1: Implement better-auth.com Integration
**Assigned to:** Backend Dev Agent
**Depends on:** Task 3.2
**Acceptance Criteria:**
- [ ] better-auth.com account created
- [ ] OAuth configured (Google, GitHub)
- [ ] User signup form with background questions
- [ ] Profile data stored in database
- [ ] User dashboard created
- [ ] Profile update functionality

**Questions on Signup:**
- Software background (beginner/intermediate/advanced)
- Hardware experience (None/ARM/GPU/Edge devices)
- Learning goals (List of interests)

...

### 6. TRANSLATION FEATURE (Week 7)

#### Task 6.1: Implement Urdu Translation
**Assigned to:** Translation Agent
**Depends on:** Task 2.1-2.5
**Acceptance Criteria:**
- [ ] All chapters translated to Urdu
- [ ] Technical terms properly translated
- [ ] Code examples kept in English
- [ ] Translations cached in database
- [ ] Translation toggle in UI
- [ ] RTL layout support added

...

### 7. TESTING & VALIDATION (Weeks 4-9)

#### Task 7.1: Create API Endpoint Tests
**Assigned to:** Testing & QA Agent
**Depends on:** Task 3.x (all endpoints)
**Acceptance Criteria:**
- [ ] Unit tests for all endpoints
- [ ] Integration tests for full flows
- [ ] Test coverage > 90%
- [ ] All tests pass before deployment

...

### 8. DEPLOYMENT (Week 9)

#### Task 8.1: Deploy Frontend to GitHub Pages
**Assigned to:** DevOps Agent
**Depends on:** Task 2.x (all content)
**Acceptance Criteria:**
- [ ] Docusaurus builds successfully
- [ ] GitHub Actions workflow created
- [ ] Deployed to GitHub Pages
- [ ] Custom domain configured (optional)
- [ ] SSL/HTTPS working

...

#### Task 8.2: Deploy Backend to Vercel
**Assigned to:** DevOps Agent
**Depends on:** Task 3.x (all endpoints)
**Acceptance Criteria:**
- [ ] FastAPI containerized with Docker
- [ ] Deployed to Vercel Functions OR Railway
- [ ] Environment variables configured
- [ ] Database connection working
- [ ] Monitoring set up

...

### 9. DOCUMENTATION (Week 10)

#### Task 9.1: Create Complete Project Documentation
**Assigned to:** Documentation Agent
**Depends on:** All previous tasks
**Acceptance Criteria:**
- [ ] Setup guide written (20+ pages)
- [ ] API documentation completed
- [ ] Architecture diagrams created
- [ ] Deployment guide written
- [ ] Troubleshooting guide created
- [ ] All code examples documented

...

### 10. DEMO & SUBMISSION (Week 10)

#### Task 10.1: Create Demo Video (< 90 seconds)
**Assigned to:** Documentation Agent
**Depends on:** All tasks completed
**Acceptance Criteria:**
- [ ] Show book navigation (20s)
- [ ] Demonstrate chatbot (30s)
- [ ] Show authentication (15s)
- [ ] Demo personalization (15s)
- [ ] Show Urdu translation (10s)
- [ ] Video < 90 seconds
- [ ] Clear audio and video quality

...

#### Task 10.2: Submit Hackathon
**Assigned to:** Documentation Agent
**Depends on:** Task 10.1
**Acceptance Criteria:**
- [ ] GitHub repo link submitted
- [ ] Live book URL submitted
- [ ] Demo video link submitted
- [ ] WhatsApp number provided
- [ ] All forms filled correctly
- [ ] Submitted before deadline

---

## TASK DEPENDENCIES MAP

```
Task 1.1 ──┬──> Task 2.1 ──┬──> Task 4.1 ──> Task 4.2
           │               │                  │
           │               └──────────────────┘
           │
Task 1.2 ──┼──> Task 3.1 ──> Task 3.2 ──────┐
           │                                 │
Task 1.3 ──┼──────────────────────────────────> Task 4.1
           │
Task 1.4 ──┴──> Task 3.1 ──> Task 3.3 ──────> Task 4.2 ──> Task 4.3

Task 4.3 ──> Task 5.1 ──> Task 5.2 ──> Task 5.3
                                       │
Task 2.1 ──────────────────────────────> Task 6.1

All Tasks ──> Task 7.x (Testing)
All Tasks ──> Task 8.x (Deployment)
All Tasks ──> Task 9.x (Documentation)
All Tasks ──> Task 10.x (Demo & Submission)
```

---

## AGENT ASSIGNMENT SUMMARY

| Agent | Tasks | Weeks |
|-------|-------|-------|
| Content Writing Agent | 2.1, 2.3, 2.4, 2.5 | 2-3 |
| Code Generation Agent | 2.2, 2.6, 2.8, 2.10 | 2-4 |
| Backend Dev Agent | 1.2, 1.4, 3.1-3.5 | 1, 4-6 |
| RAG/Chatbot Agent | 1.3, 4.1-4.2 | 1, 5 |
| Frontend Dev Agent | 1.1, 4.3, 5.2, 5.3 | 1, 5-7 |
| Translation Agent | 6.1 | 7 |
| Testing & QA Agent | 7.1-7.7 | 4-9 |
| DevOps Agent | 8.1-8.4 | 9 |
| Documentation Agent | 9.1-9.4, 10.1-10.2 | 10 |

---

## Acceptance Criteria Checklist

Use this template for every task:

```markdown
### Acceptance Criteria
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Testing Plan
- [ ] Unit tests: [coverage %]
- [ ] Integration tests: [what's tested]
- [ ] Manual testing: [steps]

### Definition of Done
- [ ] Code reviewed
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Deployed (if applicable)
```
```

**Key Point:** Tasks should be granular, testable, and have clear dependencies

---

## **PHASE 4: Create Subagents & Skills** 🤖

### **Step 5: Define Subagents & Their Skills**

**File Location:** `specs/textbook/agents.md`

**Subagent Definition Template:**

```markdown
# Subagents & Skills Definition

## Agent 1: Content Writing Agent

### Purpose
Generate and write book chapters, exercises, and assessment questions

### Skills Registry

#### Skill: Chapter Writer
- **Input:** Topic, module number, learning level, target word count
- **Process:** Generate comprehensive chapter with learning objectives, explanations, examples
- **Output:** Markdown file with formatted chapter
- **Acceptance Criteria:**
  - [ ] 2000+ words
  - [ ] Learning objectives (3-5)
  - [ ] Examples (5+)
  - [ ] No grammatical errors

#### Skill: Exercise Generator
- **Input:** Chapter topic, difficulty level, count (default 5)
- **Process:** Create hands-on exercises relevant to chapter
- **Output:** Markdown with exercise descriptions and solutions
- **Acceptance Criteria:**
  - [ ] Exercises are progressively difficult
  - [ ] All have clear solutions
  - [ ] Code examples included

#### Skill: Assessment Question Generator
- **Input:** Chapter content, question count, question type (MCQ/short-answer)
- **Process:** Generate assessment questions to test understanding
- **Output:** Questions with answers and explanations
- **Acceptance Criteria:**
  - [ ] Questions cover key concepts
  - [ ] Multiple difficulty levels
  - [ ] Clear answer keys

### Skills Dependency Chain
```
Chapter Writer
    ↓ (generates content)
Exercise Generator (uses chapter content)
    ↓
Assessment Question Generator (uses chapter content)
    ↓
Chapter Summarizer (creates summary from chapter)
```

---

## Agent 2: Code Generation Agent

### Purpose
Generate, test, and validate code examples and snippets

### Skills Registry

#### Skill: ROS 2 Code Generator
- **Input:** Feature description, complexity level, node count
- **Process:** Generate ROS 2 Python code following best practices
- **Output:** Complete working .py files with docstrings
- **Acceptance Criteria:**
  - [ ] Code follows ROS 2 conventions
  - [ ] Type hints included
  - [ ] Docstrings for all functions
  - [ ] Tested successfully

#### Skill: Code Testing Skill
- **Input:** Python code file
- **Process:** Create pytest test cases
- **Output:** Comprehensive test suite
- **Acceptance Criteria:**
  - [ ] > 90% code coverage
  - [ ] Tests for happy path and edge cases
  - [ ] All tests pass

#### Skill: Code Review Skill
- **Input:** Source code
- **Process:** Review for quality, security, best practices
- **Output:** Review feedback with corrections
- **Acceptance Criteria:**
  - [ ] No security vulnerabilities (OWASP)
  - [ ] Follows project standards
  - [ ] Suggestions for improvement

### Skills Dependency Chain
```
ROS 2 Code Generator
    ↓
Code Testing Skill (tests the generated code)
    ↓
Code Review Skill (reviews for quality)
    ↓
Code Documentation Skill (adds comments)
```

... (continue for all 9 agents)
```

---

## **PHASE 5: Creating Prompt History Records (PHRs)** 📜

### **Step 6: Record All Decisions**

**What is a PHR?**
- Record of every important prompt and response
- Tracks reasoning behind decisions
- Creates audit trail for the project
- Stored in `history/prompts/`

**Structure:**

```
history/prompts/
├── constitution/
│   └── 001-project-constitution.constitution.prompt.md
├── textbook/
│   ├── 001-create-specification.spec.prompt.md
│   ├── 002-architecture-planning.plan.prompt.md
│   ├── 003-task-generation.tasks.prompt.md
│   └── 004-agent-definition.misc.prompt.md
└── general/
    └── 001-setup-workflow.general.prompt.md
```

**PHR Template Location:** `.specify/templates/phr-template.prompt.md`

**Create PHR Command:**
```bash
# After completing each phase
/sp.phr --title "Create Project Constitution" --stage constitution
/sp.phr --title "Write Feature Specification" --stage spec --feature textbook
/sp.phr --title "Design Architecture Plan" --stage plan --feature textbook
/sp.phr --title "Generate Actionable Tasks" --stage tasks --feature textbook
```

---

## **PHASE 6: Architecture Decision Records (ADRs)** 📋

### **Step 7: Document Major Decisions**

**What is an ADR?**
- Documents significant architectural decisions
- Records options considered and rationale
- Stored in `history/adr/`

**When to Create ADR:**
- Technology choices (FastAPI vs Flask, Neon vs AWS RDS)
- Architecture patterns (monolithic vs microservices)
- Data storage decisions (vector database choice)
- Integration choices

**Create ADR Command:**
```bash
/sp.adr "Use FastAPI for Backend API Server"
/sp.adr "Choose Qdrant Cloud for Vector Embeddings"
/sp.adr "Implement Monolithic Architecture for MVP"
```

**ADR Template:**

```markdown
# ADR-001: Use FastAPI for Backend API Server

## Status
ACCEPTED

## Context
Need to choose Python web framework for RAG chatbot API with fast performance, good AI library integration, and easy deployment.

## Decision
Use FastAPI with Python 3.10+

## Rationale
- Async/await for high concurrency
- Built-in OpenAPI documentation
- Excellent AI library ecosystem
- Type hints for safety
- Easy Vercel/Railway deployment

## Alternatives Considered
1. Django - Too heavyweight
2. Flask - Slower, no async
3. Quart - Less community support

## Consequences
- Positive: Fast development, good performance
- Negative: Smaller community than Django
- Mitigated by: Good documentation, active development

## Status: ACCEPTED (Date: 2024-01-15)
```

---

## 🔧 Commands & Tools Reference

### Spec-Kit Plus Commands

```bash
# 1. SPECIFICATION
/sp.specify
# Launches CLI to create specs/textbook/spec.md

# 2. PLANNING
/sp.plan
# Launches CLI to create specs/textbook/plan.md

# 3. TASK GENERATION
/sp.tasks
# Launches CLI to create specs/textbook/tasks.md

# 4. IMPLEMENTATION
/sp.implement
# Launches task execution (runs agents)

# 5. ADR CREATION
/sp.adr "Decision Title"
# Creates architecture decision record

# 6. PHR RECORDING
/sp.phr --title "Title" --stage spec --feature textbook
# Records prompt history

# 7. ANALYSIS
/sp.analyze
# Cross-artifact consistency check

# 8. CHECKLIST
/sp.checklist
# Generates custom checklist for feature

# 9. REVERSE ENGINEER
/sp.reverse-engineer
# Creates spec from existing code

# 10. CONSTITUTION
/sp.constitution
# Create/update project constitution
```

---

## 📊 Full Workflow Timeline

```
WEEK 1: SETUP & SPEC
├─ Day 1-2: Constitutional Foundations
│  ├─ Create .specify/memory/constitution.md
│  └─ /sp.phr "Create Constitution"
├─ Day 3: Feature Specification
│  ├─ Run /sp.specify OR manually create specs/textbook/spec.md
│  └─ Define WHAT needs to be built
└─ Day 4-5: Project Infrastructure
   ├─ Initialize GitHub repo
   ├─ Set up Docusaurus
   ├─ Create Neon database account
   ├─ Create Qdrant Cloud account

WEEK 2: ARCHITECTURE & TASKS
├─ Day 1-2: Architecture Planning
│  ├─ Run /sp.plan OR manually create specs/textbook/plan.md
│  ├─ Design system architecture
│  └─ Document technology choices
├─ Day 3: Task Generation
│  ├─ Run /sp.tasks OR manually create specs/textbook/tasks.md
│  └─ Break into granular, testable tasks
├─ Day 4: Subagent Definition
│  ├─ Create specs/textbook/agents.md
│  ├─ Define 9 subagents with skills
│  └─ Map tasks to agents
└─ Day 5: Decision Recording
   ├─ Create ADRs for major decisions
   ├─ Record PHRs for all phases

WEEKS 3-9: IMPLEMENTATION (AGENTS EXECUTE)
├─ Week 3:
│  ├─ Content Writing Agent: Starts modules
│  └─ Frontend Dev Agent: Sets up Docusaurus
├─ Week 4:
│  ├─ Backend Dev Agent: API endpoints
│  ├─ Code Generation Agent: Code examples
│  └─ DevOps Agent: Database setup
├─ Week 5:
│  ├─ RAG/Chatbot Agent: Embedding pipeline
│  ├─ Frontend Dev Agent: Chatbot widget
│  └─ Testing & QA Agent: Initial tests
├─ Week 6:
│  ├─ Backend Dev Agent: Authentication
│  └─ Frontend Dev Agent: Auth UI
├─ Week 7:
│  ├─ Translation Agent: Urdu translation
│  ├─ Frontend Dev Agent: Language toggle
│  └─ Testing & QA Agent: Translation tests
├─ Week 8:
│  ├─ All Agents: Demonstrate skills
│  └─ Documentation Agent: Technical docs
├─ Week 9:
│  ├─ DevOps Agent: Full deployment
│  ├─ Testing & QA Agent: Final validation
│  └─ Backend Dev Agent: Monitoring

WEEK 10: FINAL SUBMISSION
├─ Day 1-2: Documentation
│  ├─ Documentation Agent: Complete all docs
│  ├─ Setup guides
│  └─ API documentation
├─ Day 3-4: Demo Video
│  ├─ Record < 90 second demo
│  ├─ Show all features
│  └─ Upload to YouTube
└─ Day 5: SUBMISSION
   ├─ Fill submission form
   ├─ Submit GitHub link
   ├─ Submit book URL
   ├─ Submit demo video
   └─ Provide WhatsApp number
```

---

## 🎯 Execution Checklist

### Before Starting Implementation:
- [ ] Constitution created and reviewed
- [ ] Specification completed and approved
- [ ] Architecture plan documented
- [ ] All tasks defined with acceptance criteria
- [ ] Subagents and skills defined
- [ ] Team assignments confirmed
- [ ] GitHub repo set up
- [ ] All databases created
- [ ] Environment variables configured

### During Implementation:
- [ ] Daily status updates
- [ ] PHRs recorded for major decisions
- [ ] ADRs created for architectural decisions
- [ ] Tests written alongside code
- [ ] Documentation kept updated
- [ ] Dependencies respected (task ordering)

### Before Submission:
- [ ] All tasks completed and tested
- [ ] Code reviewed and merged
- [ ] Deployment successful and verified
- [ ] Documentation complete
- [ ] Demo video recorded (< 90s)
- [ ] All submission fields filled
- [ ] Submission deadline: Nov 30, 2025 at 6:00 PM

---

## 📞 Command Summary Sheet

```bash
# INITIALIZATION
git clone <repo>
cd book
.specify/scripts/init.sh  # Initialize Spec-Kit Plus

# SPEC DEVELOPMENT
/sp.specify               # Create specification
/sp.plan                 # Create architecture plan
/sp.tasks                # Generate tasks
/sp.agents               # Define subagents & skills

# DOCUMENTATION
/sp.adr "Decision Title"  # Create ADR
/sp.phr --title "Title"   # Record prompt history
/sp.analyze              # Check consistency

# IMPLEMENTATION
/sp.implement            # Execute tasks
npm run start            # Dev server (frontend)
uvicorn main:app --reload  # Dev server (backend)

# TESTING & DEPLOYMENT
npm run build            # Build Docusaurus
npm run deploy           # Deploy to GitHub Pages
vercel deploy           # Deploy backend

# SUBMISSION
# Fill form: https://forms.gle/CQsSEGM3GeCrL43c8
```

---

## 🚀 Next Steps to Start

### 1. **TODAY: Set Up Project**
```bash
git clone <your-repo> && cd book
mkdir -p .specify specs/textbook history/prompts history/adr
git branch -b feature/spec-kit-setup
```

### 2. **TOMORROW: Create Constitution**
```bash
# Edit .specify/memory/constitution.md
# Then record with /sp.phr
```

### 3. **DAY 3: Write Specification**
```bash
# Run /sp.specify OR
# Edit specs/textbook/spec.md manually
```

### 4. **DAY 4: Plan Architecture**
```bash
# Run /sp.plan OR
# Edit specs/textbook/plan.md manually
```

### 5. **DAY 5: Generate Tasks**
```bash
# Run /sp.tasks OR
# Edit specs/textbook/tasks.md manually
```

### 6. **WEEK 2: Define Agents & Skills**
```bash
# Create specs/textbook/agents.md
# Define 9 subagents with skills
```

### 7. **WEEK 3+: Start Implementation**
```bash
# Agents begin execution
# Daily status updates
# Record decisions with ADRs/PHRs
```

---

**You're now ready to build this hackathon using Spec-Kit Plus! Start with the Constitution and work through each phase.** 🎯

