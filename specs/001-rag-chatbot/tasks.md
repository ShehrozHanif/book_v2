---
description: "Task list for RAG Chatbot feature implementation"
---

# Tasks: RAG Chatbot for Humanoid Robotics Textbook

**Input**: Design documents from `/specs/001-rag-chatbot/` (spec.md, plan.md)
**Prerequisites**: ✅ spec.md, ✅ plan.md (both complete)

**Tests**: Not explicitly requested in spec. TDD approach optional for dev team preference.

**Organization**: Tasks grouped by user story (US1, US2, US3) enabling independent implementation and testing. Each story can be delivered as a separate MVP increment.

**Estimated Total Tasks**: 28 tasks across 5 phases
**Parallel Opportunities**: 12 tasks can run in parallel (marked with [P])
**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = ~13 tasks for core RAG chatbot with text selection

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, repository structure, and tooling setup

**Duration**: 1-2 days
**Parallel**: 6 of 7 tasks can run in parallel

---

- [ ] T001 Create repository structure per plan.md (backend/, frontend/, docs/) at repository root

- [ ] T002 [P] Initialize backend Python project with FastAPI dependencies (requirements.txt, virtual env)

- [ ] T003 [P] Initialize frontend React project with TypeScript, Tailwind, Docusaurus integration (package.json, tsconfig.json)

- [ ] T004 [P] Configure Python linting (Black, pylint) and formatting tools in backend/

- [ ] T005 [P] Configure JavaScript linting (ESLint) and formatting (Prettier) in frontend/

- [ ] T006 [P] Setup Docker configuration for backend containerization (Dockerfile, docker-compose.yml)

- [ ] T007 Create .env.example files for backend/ and frontend/ with required environment variables

**Checkpoint**: ✅ Basic project scaffolding complete - ready for foundational tasks

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on. No story work can begin until this phase is 100% complete.

**Duration**: 2-3 days
**Critical**: These tasks BLOCK all user story work. Must be completed before Phase 3.

---

### Database & Schema

- [ ] T008 Design and create Neon PostgreSQL schema in backend/src/database/schema.sql with tables:
  - users (user_id, email, created_at, updated_at)
  - conversations (conversation_id, user_id [optional], created_at, expires_at, updated_at)
  - messages (message_id, conversation_id, sender [user/bot], content, timestamp, embedding_stats)
  - textbook_chunks (chunk_id, content, module, chapter, section, created_at)
  - audit_logs (log_id, query, response, relevance_scores, timestamp, user_id [optional])

- [ ] T009 [P] Setup SQLAlchemy ORM models in backend/src/models/database.py (User, Conversation, Message, TextbookChunk, AuditLog)

- [ ] T010 [P] Configure Neon Postgres connection pooling in backend/src/database/connection.py with async SQLAlchemy

- [ ] T011 [P] Setup environment configuration management in backend/src/config.py (load from .env, validate required variables)

### API & Framework Setup

- [ ] T012 Initialize FastAPI application structure in backend/src/main.py with:
  - CORS configuration (allow Docusaurus origin)
  - Middleware stack (logging, error handling)
  - Health check endpoint (/health, /ready)

- [ ] T013 [P] Create API request/response schemas (Pydantic models) in backend/src/models/schemas.py:
  - ChatRequest (query, selected_text, conversation_id, user_id)
  - ChatResponse (response, conversation_id, retrieved_passages, relevance_scores, processing_time_ms)
  - ErrorResponse (error, details, status_code)

- [ ] T014 [P] Setup API routing structure in backend/src/api/routes/ (placeholder routes for chat, embed, health)

- [ ] T015 [P] Implement input validation and sanitization middleware in backend/src/api/dependencies.py:
  - Validate ChatRequest structure
  - Sanitize query text (prevent injection attacks)
  - Enforce max query length (e.g., 5000 chars)

- [ ] T016 [P] Implement rate limiting middleware in backend/src/api/dependencies.py (10 req/min per IP for anonymous users)

- [ ] T017 [P] Setup error handling framework in backend/src/api/error_handler.py with standard error responses (400, 401, 429, 500)

### External Service Integration Setup

- [ ] T018 Setup Qdrant Cloud client in backend/src/services/qdrant_client.py:
  - Initialize connection to Qdrant Cloud instance
  - Create collection "textbook_passages" with 1536 dimensions
  - Add utility methods for vector operations

- [ ] T019 [P] Setup OpenAI API client in backend/src/services/openai_client.py:
  - Initialize OpenAI SDK with API key from .env
  - Create helper methods for embeddings (text-embedding-3-small)
  - Create helper methods for LLM calls (gpt-3.5-turbo)

- [ ] T020 [P] Setup conversation cache/context manager in backend/src/services/conversation_service.py:
  - Load conversation history from DB
  - Manage context window (recent messages only)
  - Prepare system prompt with prior context

### Frontend Widget Setup

- [ ] T021 Create base ChatBot component structure in frontend/src/components/ChatBot.tsx:
  - Container component with state management
  - Layout (input area, message display, history sidebar)
  - Integration hooks for API calls

- [ ] T022 [P] Create text selection handler in frontend/src/hooks/useTextSelection.ts:
  - Detect when user selects text in page
  - Capture selected text + context
  - Expose selected_text to ChatInput component

- [ ] T023 [P] Create chat API service in frontend/src/services/chatApi.ts:
  - POST /chat wrapper function with proper headers
  - Error handling (timeout, network, API errors)
  - Response parsing and validation

**Checkpoint**: ✅ Foundation complete - database, API framework, external services, and frontend scaffolding ready. User story work can now proceed in parallel.

---

## Phase 3: User Story 1 - Student Asks Question About Course Content (Priority: P1) 🎯 MVP

**Goal**: Enable students to select text and ask the chatbot questions about textbook content, receiving contextual answers with citations.

**Value**: Core RAG chatbot functionality - the primary reason for the feature. Without this, the system is incomplete.

**Independent Test**:
1. Open textbook chapter in browser
2. Select text paragraph
3. Click "Ask Chatbot" button
4. Enter question: "What does this mean?"
5. Verify: Chatbot responds within 3 seconds with relevant answer citing source chapter
6. Can be tested in isolation without User Story 2 or 3

---

### Implementation for User Story 1

**Backend - RAG Pipeline Services**

- [ ] T024 [P] [US1] Implement embedding service in backend/src/services/embedding_service.py:
  - embed_query(text) → returns 1536-dim vector via OpenAI
  - embed_passages(passages) → batch embed textbook chunks
  - Handles rate limiting to OpenAI API

- [ ] T025 [P] [US1] Implement retrieval service in backend/src/services/retrieval_service.py:
  - search_qdrant(query_vector) → top 5 passages by cosine similarity
  - rank_passages(passages, query) → rerank top 5 by relevance
  - Return top 3 passages for context window

- [ ] T026 [P] [US1] Implement generation service in backend/src/services/generation_service.py:
  - generate_response(query, context_passages, conversation_history) → LLM response via OpenAI
  - Extract citations from response [Chapter X: Section Y]
  - Validate response doesn't hallucinate (cites sources from context only)
  - Acknowledge uncertainty when confidence is low

- [ ] T027 [US1] Implement chat orchestrator in backend/src/services/chat_service.py (depends on T024, T025, T026):
  - Orchestrate embedding → retrieval → generation pipeline
  - Load conversation context for multi-turn (when conversation_id provided)
  - Save messages and audit logs to database
  - Return ChatResponse with all metadata

- [ ] T028 [US1] Implement /chat endpoint in backend/src/api/routes/chat.py (depends on T027):
  - POST /chat(ChatRequest) → ChatResponse
  - Validate request, load user context
  - Call chat_service.process_query()
  - Return response with processing_time_ms
  - Handle errors gracefully (500, 503 for API failures)

**Backend - Content Embedding (Admin Task)**

- [ ] T029 [P] [US1] Implement /chat/embed endpoint in backend/src/api/routes/chat.py:
  - POST /chat/embed(textbook_content, module, chapter, section) → success/failure
  - Chunk textbook into 200-500 word passages
  - Embed each chunk with embedding_service
  - Store chunks + embeddings in Qdrant + Postgres
  - Requires admin authentication (future feature, skip auth for MVP)

**Frontend - UI Components**

- [ ] T030 [P] [US1] Create ChatInput component in frontend/src/components/ChatInput.tsx:
  - Text input field with submit button
  - Display loading state while waiting for response
  - Integrate with useChat hook
  - Integrate with useTextSelection hook to prepopulate with selected text
  - Clear input after message sent

- [ ] T031 [P] [US1] Create ChatMessage component in frontend/src/components/ChatMessage.tsx:
  - Display user messages (right-aligned)
  - Display bot messages (left-aligned) with citations highlighted
  - Format citations as [Chapter X: Section Y] with link to section (if possible)
  - Show timestamp for each message

- [ ] T032 [P] [US1] Create LoadingIndicator component in frontend/src/components/LoadingIndicator.tsx:
  - Display animated spinner while waiting for /chat response
  - Show status message (e.g., "Searching textbook...")
  - Timeout indicator if response > 3 seconds

- [ ] T033 [US1] Implement useChat hook in frontend/src/hooks/useChat.ts (depends on T023):
  - State: messages[], conversation_id, loading, error
  - Function: sendMessage(query) → calls chatApi.post('/chat')
  - Handle response parsing, error states
  - Maintain message history
  - Integrate with Neon backend conversation storage (anonymous = localStorage, auth = API)

**Frontend - Widget Assembly**

- [ ] T034 [US1] Assemble ChatBot widget in frontend/src/components/ChatBot.tsx (depends on T030, T031, T032, T033):
  - Compose ChatInput, ChatMessage, LoadingIndicator components
  - Initialize useChat hook for state management
  - Initialize useTextSelection hook for text capture
  - Embed widget in Docusaurus page (via .mdx wrapper component)
  - Style with Tailwind CSS per design system
  - Test responsive layout (mobile, tablet, desktop)

**Integration & Testing**

- [ ] T035 [US1] Integration test for User Story 1: test full flow from text selection → chat response in tests/integration/test_us1_ask_question.py:
  - Seed test database with sample textbook chunks
  - Mock OpenAI API responses
  - Test: Select text → Ask question → Get response with citations
  - Verify response latency < 3 seconds
  - Verify >85% relevance of retrieved passages

**Checkpoint**: ✅ User Story 1 complete and testable independently. Core RAG chatbot functional. Students can ask questions and receive textbook-grounded answers.

---

## Phase 4: User Story 2 - Chatbot Maintains Learning Context Across Questions (Priority: P2)

**Goal**: Enable multi-turn conversations where the chatbot remembers previous context and can handle follow-up questions without repetition.

**Value**: Improves learning by enabling Socratic-style dialogue. Students can ask clarifying follow-ups.

**Independent Test**:
1. Ask question 1: "What is ROS 2?"
2. Ask follow-up: "Can you explain differently?"
3. Verify: Bot refers back to previous answer without re-stating basics
4. Test 5+ exchanges and verify response time stays < 3 seconds

**Dependency**: Requires User Story 1 (chat endpoint) complete

---

### Implementation for User Story 2

**Backend - Conversation Context**

- [ ] T036 [US2] Enhance conversation_service in backend/src/services/conversation_service.py:
  - load_conversation(conversation_id) → return recent 5-10 messages
  - format_context_for_prompt(messages) → system prompt with prior context
  - Limit context to prevent token overflow (max ~4000 tokens of history)
  - Handle case when no prior context exists

- [ ] T037 [US2] Update chat_service in backend/src/services/chat_service.py:
  - When conversation_id provided: Load context via conversation_service
  - Pass prior messages to generation_service in LLM call
  - Maintain conversation_id across exchanges
  - Ensure response time stays < 3s even with context (test in Phase 4)

**Frontend - Conversation History**

- [ ] T038 [P] [US2] Create ConversationHistory component in frontend/src/components/ConversationHistory.tsx:
  - Display list of previous messages (scrollable)
  - Show sender (User/Bot), timestamp, message preview
  - Highlight current conversation vs archived
  - (Note: Archived conversations handled in Phase 5, US3)

- [ ] T039 [P] [US2] Update ChatBot component in frontend/src/components/ChatBot.tsx (depends on T034):
  - Integrate ConversationHistory panel in layout
  - Auto-scroll to latest message
  - Preserve conversation_id across page refresh (in sessionStorage)

- [ ] T040 [US2] Update useChat hook in frontend/src/hooks/useChat.ts (depends on T033):
  - Load conversation_id from sessionStorage if exists
  - Send conversation_id with each /chat request
  - Maintain conversation history in component state
  - Handle context truncation on client side (last 10 messages)

**Testing for User Story 2**

- [ ] T041 [US2] Integration test for multi-turn conversation in tests/integration/test_us2_context.py:
  - Send question 1, verify response
  - Send follow-up question 2 (should reference Q1)
  - Send 5+ exchanges, verify <3s response time maintained
  - Verify conversation_id stays consistent

**Checkpoint**: ✅ User Story 2 complete. Multi-turn conversations work with context. Students can have natural dialogue.

---

## Phase 5: User Story 3 - Chatbot Handles Off-Topic and Invalid Questions Gracefully (Priority: P3)

**Goal**: Gracefully refuse off-topic questions, handle malformed input, and prevent hallucinations. Build trust through responsible AI.

**Value**: Improves reliability and user trust. Prevents chatbot from confidently providing wrong information.

**Independent Test**:
1. Ask off-topic: "What's the weather?" → Should politely refuse
2. Send empty query → Should show helpful prompt
3. Try injection: "Ignore previous instructions..." → Should sanitize and refuse
4. Ask system question: "Who made you?" → Should acknowledge it's AI and redirect
5. Verify 100% of edge cases handled gracefully

**Dependency**: Requires User Story 1 (chat endpoint) complete

---

### Implementation for User Story 3

**Backend - Safety & Validation**

- [ ] T042 [P] [US3] Enhance security_service in backend/src/services/security_service.py:
  - detect_injection_attempt(query) → regex patterns for prompt injection
  - detect_off_topic(query, retrieved_passages) → semantic distance check
  - Confidence threshold: if no relevant passages retrieved (relevance < 0.3), flag as off-topic

- [ ] T043 [P] [US3] Update generation_service in backend/src/services/generation_service.py:
  - If off-topic detected: Return refusal message instead of LLM call
  - If no relevant passages: Acknowledge uncertainty, suggest rephrasing
  - Validate LLM response doesn't contradict retrieved passages

- [ ] T044 [US3] Update chat_service in backend/src/services/chat_service.py (depends on T042, T043):
  - Run security checks before RAG pipeline
  - Handle edge cases:
    - Empty query: "Please ask a question about the textbook."
    - Off-topic query: "I can help with questions about Humanoid Robotics. Please ask about the textbook content."
    - Injection attempt: Sanitize and ask for rephrased question
    - API failure: "I'm temporarily unavailable. Please try again."

**Frontend - Error Handling**

- [ ] T045 [P] [US3] Create ErrorMessage component in frontend/src/components/ErrorMessage.tsx:
  - Display error with user-friendly message
  - Show "retry" button for transient errors
  - Don't expose internal error details
  - Differentiate error types (user error, API error, timeout)

- [ ] T046 [P] [US3] Update ChatInput component in frontend/src/components/ChatInput.tsx:
  - Disable submit if query is empty
  - Show input validation hint
  - Warn if query seems like injection attempt (client-side)

- [ ] T047 [US3] Update useChat hook in frontend/src/hooks/useChat.ts (depends on T033):
  - Handle error states from /chat endpoint (400, 429, 500)
  - Display appropriate error message to user
  - Don't retry on 400 (user error), do retry on 500 (transient)
  - Set error timeout (clear after 5 seconds)

**Testing for User Story 3**

- [ ] T048 [US3] Integration test for edge cases in tests/integration/test_us3_edge_cases.py:
  - Test empty query handling
  - Test off-topic query detection
  - Test injection attempt prevention
  - Test API timeout handling
  - Verify 100% graceful handling (no crashes)

**Checkpoint**: ✅ User Story 3 complete. Edge cases handled. System is robust.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Non-story-specific work to complete production readiness (logging, monitoring, documentation, deployment)

**Duration**: 2-3 days

---

### Logging & Monitoring

- [ ] T049 [P] Setup structured logging in backend/src/logger.py:
  - Log all queries (anonymized), responses, latencies
  - Log embeddings API calls + costs
  - Log LLM API calls + token usage
  - Log errors with stack traces (non-sensitive)

- [ ] T050 [P] Setup audit logging in backend/src/services/chat_service.py:
  - Log to audit_logs table: query, response, relevance_scores, user_id, timestamp
  - Enable quality monitoring and debugging

### Documentation

- [ ] T051 [P] Generate OpenAPI schema in backend/ as contracts/openapi.yaml:
  - Full schema for /chat, /chat/embed endpoints
  - Request/response schemas, error codes, examples
  - Authentication requirements (future)

- [ ] T052 [P] Create API documentation in backend/README.md:
  - Setup instructions, environment variables
  - API endpoint examples with curl
  - Testing with sample queries
  - Deployment guide (Heroku/Railway/Vercel)

- [ ] T053 [P] Create frontend README in frontend/README.md:
  - Setup instructions
  - Component hierarchy and prop documentation
  - Docusaurus integration guide
  - Deployment guide (Vercel)

### Deployment & Infrastructure

- [ ] T054 Build Docker image for backend Dockerfile:
  - Base: python:3.10-slim
  - Install dependencies from requirements.txt
  - Run with gunicorn or uvicorn
  - Expose port 8000

- [ ] T055 [P] Create docker-compose.yml for local development:
  - Backend service
  - PostgreSQL service (optional, for local testing)
  - Environment configuration

- [ ] T056 [P] Setup GitHub Actions CI/CD in .github/workflows/:
  - Run tests on push (pytest for backend, Jest for frontend)
  - Lint checks (Black, ESLint)
  - Build Docker image
  - Deploy to staging on push to develop, production on merge to main

### Performance Optimization (if needed based on testing)

- [ ] T057 [P] Optimize vector search in Qdrant:
  - Index parameters for 1536 dims
  - Connection pooling for concurrent queries
  - Response caching for identical queries (optional)

- [ ] T058 [P] Optimize LLM calls:
  - Batch embedding requests where possible
  - Cache embeddings for common queries
  - Monitor token usage and costs

**Checkpoint**: ✅ Production-ready chatbot with full documentation, testing, and deployment pipeline.

---

## Task Summary

| Phase | Name | Tasks | Duration | Critical |
|-------|------|-------|----------|----------|
| 1 | Setup | T001-T007 | 1-2 days | ⚠️ Blocks all work |
| 2 | Foundational | T008-T023 | 2-3 days | ⚠️ Blocks user stories |
| 3 | User Story 1 (MVP) | T024-T035 | 3-4 days | 🎯 Core feature |
| 4 | User Story 2 | T036-T041 | 1-2 days | 💡 Enhances UX |
| 5 | User Story 3 | T042-T048 | 1-2 days | 🛡️ Safety |
| 6 | Polish | T049-T058 | 2-3 days | 📦 Production |
| **TOTAL** | **RAG Chatbot** | **58 tasks** | **~10-15 days** | ✅ Parallel-friendly |

---

## Parallel Execution Strategy

### Phase 1 (Setup)
- T002, T003, T004, T005, T006 can run in parallel (5 parallelizable)
- T001, T007 must run first
- **Parallel opportunity**: 5 of 7 tasks

### Phase 2 (Foundation)
- Database setup (T008) must complete first
- Then T009-T011 can run in parallel (3 parallelizable)
- API setup (T012) must complete first
- Then T013-T017 can run in parallel (5 parallelizable)
- Service setup (T018-T020) all parallelizable (3 parallelizable)
- Frontend setup (T021-T023) all parallelizable (3 parallelizable)
- **Parallel opportunity**: 11 of 16 tasks after dependencies

### Phase 3 (User Story 1)
- Backend services (T024-T026) all parallelizable (3 parallelizable)
- T027 depends on all backend services (T024-T026)
- T028 depends on T027
- Frontend components (T030-T032) all parallelizable (3 parallelizable)
- T033 depends on T023
- T034 depends on T030-T033
- **Parallel opportunity**: 6 of 12 tasks

### Phase 4 & 5 (US2 & US3)
- Can run in parallel with each other (don't interfere)
- Internal parallelization within each story
- **Parallel opportunity**: Several tasks in each

### Phase 6 (Polish)
- Most tasks parallelizable except deployment
- T049-T053 can run in parallel
- T054-T056 can run in parallel
- **Parallel opportunity**: 10 of 10 tasks

---

## MVP Scope (Minimum Viable Product)

**To deliver a working RAG chatbot**:

1. **Must Complete**:
   - Phase 1 (Setup) - All 7 tasks
   - Phase 2 (Foundation) - All 16 tasks
   - Phase 3 (User Story 1 MVP) - All 12 tasks
   - **Total**: 35 tasks for core functionality

2. **Optional (Post-MVP)**:
   - Phase 4 (User Story 2) - Multi-turn conversations
   - Phase 5 (User Story 3) - Edge case handling
   - Phase 6 (Polish) - Production hardening

3. **MVP Deliverable**:
   - Students can select text and ask single-turn questions
   - Chatbot retrieves relevant passages and generates answers with citations
   - Graceful error messages for API failures
   - <3 second response time for 95% of queries

---

## Agent Assignment (For `/sp.implement` phase)

When moving to implementation, assign tasks to agents:

**Backend Dev Agent** (has database, FastAPI, ORM skills):
- T008-T027 (database, API setup, RAG services)
- Estimated: 18 tasks

**Frontend Dev Agent** (has React, Tailwind, component skills):
- T002, T003, T005, T030-T034 (React components, styling)
- Estimated: 8 tasks

**RAG/Chatbot Agent** (has embeddings, LLM, RAG skills):
- T024-T026 (embedding, retrieval, generation services)
- T029 (content embedding)
- T042-T044 (safety & edge cases)
- Estimated: 7 tasks

**Testing & QA Agent** (has test suite, validation skills):
- T035, T041, T048 (integration tests)
- T051, T052 (API documentation & testing)
- Estimated: 5 tasks

**DevOps Agent** (has Docker, CI/CD, deployment skills):
- T001, T004, T006, T007 (project setup)
- T054-T056 (deployment & CI/CD)
- Estimated: 7 tasks

---

## Success Criteria for Complete Implementation

- [ ] All 58 tasks completed and merged
- [ ] User Story 1 (MVP): Student can select text → ask question → get citation answer (3 sec p95)
- [ ] User Story 2: Multi-turn conversations work with context
- [ ] User Story 3: All edge cases handled gracefully
- [ ] Tests passing: Unit tests (backend), Integration tests (all stories), Contract tests (API)
- [ ] Documentation: README, API docs, deployment guide
- [ ] Deployment: CI/CD pipeline configured, staging environment working
- [ ] Performance: Vector search <1s, LLM response <3s, page load <3s, 100+ concurrent users
- [ ] Quality: >85% retrieval relevance, >90% answer accuracy, 100% citation rate, 100% uptime

---

**Status**: ✅ **READY FOR IMPLEMENTATION**
**Next Command**: Assign tasks to agents and run `/sp.implement` to begin development
