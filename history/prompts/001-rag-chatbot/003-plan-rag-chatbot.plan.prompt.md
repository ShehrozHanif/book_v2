---
id: 003
title: Plan RAG Chatbot architecture
stage: plan
date: 2026-01-30
surface: agent
model: haiku
feature: rag-chatbot
branch: 001-rag-chatbot
user: user
command: /sp.plan
labels: [planning, architecture, api-design, data-model, rag-system]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-rag-chatbot/plan.md
tests:
  - Constitution gate check: PASS
  - Technical context validated against spec
  - Project structure aligned with distributed web app pattern
  - Architecture diagram and request flow documented
---

## Prompt

User invoked `/sp.plan` to design the implementation architecture for RAG Chatbot feature.

Execution followed SDD-RI planning workflow:
1. Loaded specification and constitution
2. Performed constitution gate check (Backend API, Database, RAG Chatbot standards)
3. Defined technical context (Python 3.10+, FastAPI, React 18+, OpenAI, Qdrant, Neon Postgres)
4. Designed distributed web application architecture
5. Documented project structure (backend + frontend separation)
6. Created system architecture diagram
7. Defined RAG pipeline flow with decision rationale

## Response snapshot

**Implementation Plan** generated at `specs/001-rag-chatbot/plan.md` containing:

**Technical Context**:
- Backend: Python 3.10+ with FastAPI
- Frontend: React 18+ with TypeScript
- Storage: Neon PostgreSQL + Qdrant Cloud (1536-dim embeddings)
- Testing: pytest, Jest, React Testing Library
- Performance targets: <3s chat response (p95), <1s vector search, 100+ concurrent users

**Constitution Gate Check**: ✅ PASS
- Backend API standards (documentation, validation, performance, security, testing)
- Database standards (schema, vector store, integrity, performance)
- RAG Chatbot standards (retrieval >85%, generation >90%, UX <3s, edge cases)

**Project Structure**: Distributed web application
- Backend: `backend/` with src/ (api/, models/, services/, database/), tests/, Docker support
- Frontend: `frontend/` with src/ (components/, services/, hooks/, types/), tests/, TypeScript config
- Separation enables: independent scaling, API reusability, clear testing boundaries, deployment flexibility

**System Architecture**:
- React widget embedded in Docusaurus captures text selection and sends queries
- FastAPI backend orchestrates RAG pipeline: query embedding → Qdrant search → LLM generation
- OpenAI API for embeddings (text-embedding-3-small) and LLM (GPT-3.5-turbo)
- Neon Postgres stores conversations, messages, users, audit logs
- 7-day retention for authenticated users, clear on close for anonymous

**Request Flow**: 9-step flow from text selection through LLM response to storage and display

**Design Decisions**: 4 key components with rationale and alternatives considered
- OpenAI embeddings (proven quality vs. open-source)
- Qdrant Cloud (managed service vs. Pinecone/Weaviate)
- GPT-3.5-turbo (cost-effective vs. GPT-4)
- Top-3 passages context (balance token efficiency vs. richness)

**Phase 1 Deliverables** (to be generated):
- `data-model.md`: Complete schema design
- `contracts/openapi.yaml`: API specifications
- `quickstart.md`: Setup and deployment guide
- Agent context updates for AI assistance

## Outcome

- ✅ Impact: Established clear, detailed architecture for RAG Chatbot implementation; eliminates ambiguity on system design, technology choices, and component responsibilities
- 🧪 Tests: Constitution gate validation passed; all standards met or explicitly planned
- 📁 Files:
  - specs/001-rag-chatbot/plan.md (342 lines of architecture + design documentation)
  - Ready for Phase 1 artifact generation
- 🔁 Next prompts: Complete Phase 1 (data-model.md, contracts/, quickstart.md), then run `/sp.tasks` for detailed task breakdown
- 🧠 Reflection: Architecture successfully balances complexity and simplicity; distributed design enables independent development of backend and frontend; clear separation of RAG pipeline services enables testability

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generation succeeded without blockers
- Graders run and results (PASS/FAIL): PASS
  - Technical context: Complete and measurable
  - Constitution gate: PASS (all standards addressed)
  - Project structure: Clear and aligned with distributed web app pattern
  - Architecture diagram: Complete with data flows
  - Design decisions: Documented with rationale and alternatives
  - Request flow: 9-step flow fully documented
- Prompt variant (if applicable): null
- Next experiment: Monitor during task phase whether estimated chunk count (100-150 passages) is accurate; may need adjustment during content embedding phase
