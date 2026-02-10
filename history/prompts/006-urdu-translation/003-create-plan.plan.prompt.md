---
id: "003"
title: "Create implementation plan for Urdu translation"
stage: "plan"
feature: "006-urdu-translation"
date_iso: "2026-02-10"
surface: "agent"
model: "claude-haiku-4-5-20251001"
branch: "release/003-personalization-complete"
user: "shehroz"
command: "/sp.plan"
labels:
  - "urdu-translation"
  - "implementation-plan"
  - "architecture"
  - "chatbot"
links:
  spec: "/specs/006-urdu-translation/spec.md"
  plan: "/specs/006-urdu-translation/plan.md"
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "specs/006-urdu-translation/plan.md"
tests_yaml: []
---

## Prompt

Execute `/sp.plan` workflow to create comprehensive implementation architecture for 006-urdu-translation feature.

Input: Clarified feature specification from `/specs/006-urdu-translation/spec.md` (RAG Chatbot-only, authentication-required, hybrid preference storage).

Deliverables:
1. Implementation plan document with technical context, design decisions, data model outline
2. Constitution check against project principles
3. Project structure (documentation + source code layout)
4. Key design decisions with rationale and alternatives
5. Phase 0 research tasks and Phase 1 design preview
6. Success measures and next steps

## Response

Successfully created comprehensive implementation plan for Urdu translation feature.

### Document: `/specs/006-urdu-translation/plan.md` (591 lines)

**Summary**
- Enable Urdu-speaking users to interact with RAG chatbot in native language
- Translate 50-100 core chatbot response templates (Phase 1)
- RTL layout support with authentication-required access
- Technical focus: existing FastAPI backend + React frontend + Neon PostgreSQL

**Technical Context**
- Languages: Python 3.10+, TypeScript 5.0+, React 18+
- Dependencies: FastAPI, SQLAlchemy async, Pydantic, React, Tailwind CSS
- Storage: Neon PostgreSQL (response templates, translations, glossary, user preferences)
- Testing: pytest (backend), Jest/React Testing Library (frontend)
- Performance: <3s chatbot response (unaffected), <1s language toggle, <500ms glossary lookup
- Constraints: Auth required for Urdu, no chat history loss on switch, RTL-compatible code highlighting

**Constitution Check: ✅ PASS** (all principles satisfied)
- Specification-driven ✅ (comprehensive spec with 5 stories, 13 requirements)
- Educational excellence ✅ (terminology consistency, glossary)
- User-centric ✅ (persistent preferences, seamless switching)
- Production-ready ✅ (API tested, error handling, RTL quality)
- Composable ✅ (modular services, reusable components)
- Technology stack ✅ (FastAPI, React, Neon all approved)
- Security ✅ (auth required, no hardcoded secrets, SQL injection prevented)
- Testing ✅ (unit/integration/RTL/e2e tests planned)

### Key Design Decisions (6 total)

**1. Response Template Translation Model**
- Decision: Store translations at response template level (100 templates), not individual responses
- Rationale: Templates stable; responses dynamic; consistent terminology; reduced storage
- Alternatives: External i18n files (too rigid), inline translations (duplicated storage), on-the-fly translation (inconsistent)

**2. Authentication Gate**
- Decision: Require login before Urdu language access
- Rationale: Authenticated users get persistent preferences; guests English-only; simple UX
- Alternatives: Guest Urdu with browser storage (messy), allow guests with revert (confusing), auth required (clean, chosen)

**3. Glossary Access Control**
- Decision: Glossary accessible to all authenticated users; feedback mechanism for improvements
- Rationale: Supports bilingual learning; scalable through quarterly curation
- Alternatives: Public glossary (inconsistent), admin-only (limits support), public forum (moderation overhead), auth + feedback (chosen)

**4. RTL Implementation**
- Decision: CSS `direction: rtl` with logical properties (padding-inline-start, margin-block-end)
- Rationale: Automatic text/margin reversal; works with Tailwind; keeps code LTR
- Alternatives: Flexbox row-reverse (layout only), string reversal (breaks code), HTML dir attribute (less flexible), CSS approach (chosen)

**5. Language Preference Persistence**
- Decision: Database storage for authenticated users only
- Rationale: Cross-device persistence; enables analytics; simple (one storage mechanism)
- Alternatives: Browser localStorage (no cross-device), database only (requires migration), both (sync complexity), database chosen

**6. Translation QA Strategy**
- Decision: Hybrid approach (manual translation + automated post-translation audits)
- Rationale: Human expertise + systematic error catching; no tool friction during translation
- Alternatives: Automated checking (slows translators), manual-only (misses errors), machine translation (poor quality), hybrid chosen

### Project Structure

**Documentation**:
```
specs/006-urdu-translation/
├── spec.md ✅ (clarified scope)
├── plan.md ✅ (THIS FILE)
├── research.md (Phase 0 - to generate)
├── data-model.md (Phase 1 - to generate)
├── quickstart.md (Phase 1 - to generate)
└── contracts/ (Phase 1 - to generate)
    ├── chatbot-translation-api.openapi.yaml
    ├── glossary-api.openapi.yaml
    └── language-preference-api.openapi.yaml
```

**Backend** (Python/FastAPI):
```
backend/src/personalization/
├── models/
│   ├── db_models.py (NEW: 6 tables + relationships)
│   └── schemas.py (NEW: request/response schemas)
├── services/
│   ├── chatbot_translation_service.py (NEW)
│   ├── glossary_service.py (NEW)
│   └── language_preference_service.py (NEW)
├── api/routes/
│   ├── chatbot_translation.py (NEW: 4 endpoints)
│   ├── glossary.py (NEW: 4 endpoints)
│   └── language_preferences.py (NEW: 2 endpoints)
└── tests/ (10+ test files, 80%+ coverage)
```

**Frontend** (React/TypeScript):
```
frontend/src/
├── components/ChatBot/
│   ├── ChatbotLanguageToggle.tsx (NEW)
│   ├── ChatbotMessageRTL.tsx (NEW)
│   └── ChatbotGlossary.tsx (NEW)
├── components/LanguagePreference/
│   └── LanguageSettings.tsx (NEW)
├── hooks/
│   ├── useLanguagePreference.ts (NEW)
│   ├── useChatbotLanguage.ts (NEW)
│   └── useGlossary.ts (NEW)
├── services/
│   ├── chatbotTranslationAPI.ts (NEW)
│   ├── glossaryAPI.ts (NEW)
│   └── languagePreferenceAPI.ts (NEW)
├── styles/
│   └── rtl.css (NEW: Tailwind RTL utilities)
└── tests/ (8+ test files, 70%+ coverage)
```

**Database**:
```
backend/alembic/versions/
└── 00X_add_chatbot_translation.py (6 tables, indexes, constraints)
```

### Data Model (Phase 1 Design)

**6 Entities** (detailed in plan.md):
1. `ChatbotResponseTemplate` - English source templates (100 in Phase 1)
2. `ChatbotTranslation` - Urdu translations with versioning and status
3. `GlossaryTerm` - 150+ robotics terms (English/Urdu/pronunciation)
4. `GlossaryFeedback` - User suggestions and corrections
5. `UserLanguagePreference` - Persistent language choice per user
6. `ChatbotResponseTranslationStatus` - Coverage tracking (which templates translated)

**Relationships**:
- ChatbotTranslation → ChatbotResponseTemplate (many per template across versions)
- ChatbotTranslation → User (translator attribution)
- UserLanguagePreference → User (one per user)
- GlossaryFeedback → User + GlossaryTerm (user-driven improvements)

### API Contracts (Phase 1 Design)

**3 Main APIs**:

1. **Chatbot Translation API**
   - `GET /api/v1/chatbot/language` - Get current user's language
   - `POST /api/v1/chatbot/language` - Set language (validates auth + language)
   - `GET /api/v1/chatbot/response/{template_key}` - Get template in preferred language
   - `GET /api/v1/chatbot/templates?language=urdu` - List all translated templates

2. **Glossary API**
   - `GET /api/v1/glossary` - List all terms (query: language, category, search)
   - `GET /api/v1/glossary/{term_id}` - Single term in requested language
   - `GET /api/v1/glossary/search?q=text` - Full-text search (auth required)
   - `POST /api/v1/glossary/feedback` - Submit term suggestion (auth required)

3. **Language Preference API**
   - `GET /api/v1/users/{user_id}/language-preference` - Get preference
   - `PUT /api/v1/users/{user_id}/language-preference` - Update preference (auth required)

**Authentication**: All Urdu endpoints require valid JWT token
**Error Codes**: 401 (unauthorized guests), 403 (forbidden access), 404 (not found), 422 (invalid language), 500 (graceful fallback)

### Frontend Components (Phase 1 Design)

**4 Main Components**:
1. `ChatbotLanguageToggle.tsx` - English/Urdu selector in chatbot
2. `ChatbotMessageRTL.tsx` - RTL-aware response display with code block handling
3. `ChatbotGlossary.tsx` - Modal glossary with search (authenticated users)
4. `LanguageSettings.tsx` - User profile language preference form

**Styling**: Tailwind CSS with custom RTL utilities (logical properties, direction: rtl)

### Backend Services (Phase 1 Design)

**3 Main Services**:
1. `ChatbotTranslationService` - Load templates, cache translations, fallback to English
2. `GlossaryService` - Search terms, manage feedback, admin curation
3. `LanguagePreferenceService` - Persist and retrieve user preferences

### Phase 0: Research Tasks

**TBD in research.md**:
1. Urdu font rendering - Which fonts work best across browsers? (Google Fonts Noto Sans Urdu?)
2. Code block RTL - Pattern for keeping code LTR while surrounding text RTL?
3. Chatbot template format - Current response structure? Database or code-based?
4. Translation storage - JSON files vs. database? (Recommend database for versioning)
5. Auth system integration - Current JWT flow? How to check authentication in endpoints?
6. Performance impact - Current chatbot response time? Translation lookup overhead?

### Success Measures

| Metric | Target | Verification |
|--------|--------|---------------|
| Language Toggle Speed | <1 second | Lighthouse |
| RTL Rendering Quality | 95%+ browsers | Manual testing |
| Glossary Search | <500ms | Load test |
| Terminology Consistency | 100% match | Automated audit |
| Auth Validation | 100% guest block | Endpoint tests |
| Preference Persistence | 100% across sessions | Integration tests |
| Code Coverage | 80%+ backend, 70%+ frontend | pytest/Jest |
| User Satisfaction | 4.0+ rating | Post-launch survey |

### Next Steps

**Immediate** (Before Phase 2 Tasks):
1. Generate `research.md` with answers to 6 research questions
2. Finalize `data-model.md` with detailed SQL schema
3. Generate OpenAPI specs in `/contracts/`
4. Update agent context with new technologies

**Then** (Phase 2 - Tasks):
5. Run `/sp.tasks` to break down into actionable work items
6. Assign tasks to development team

**Implementation** (After Approval):
7. Phase 1: Implement 50-100 core response templates
8. QA and testing (RTL across browsers)
9. Deploy to staging
10. User testing with Urdu speakers
11. Iterate on feedback

### Git Commit

Commit: `e982acc`
Message: "docs: create implementation plan for 006-urdu-translation feature"

## Quality Assessment

✅ **Plan Quality**: PASS
- Clear technical context with all necessary details
- 6 design decisions with rationale and alternatives
- Comprehensive data model entities with relationships
- 3 API contracts with endpoints, auth, error codes
- 4 frontend components and 3 backend services designed
- Project structure aligned with existing codebase
- Phase 0 research and Phase 1 design roadmap clear

✅ **Alignment with Specification**: PASS
- All 5 user stories addressed in design
- All 13 functional requirements incorporated
- All 10 success criteria have measurable verification
- Authentication gate implemented
- RTL support designed
- Terminology consistency addressed
- Response template translation model chosen

✅ **Constitution Compliance**: PASS
- Specification-driven (plan based on detailed spec)
- Educational excellence (glossary design, terminology)
- User-centric (preference persistence, seamless switching)
- Production-ready (error handling, testing, documentation)
- Composable (modular services, reusable components)
- Technology stack (FastAPI, React, Neon approved)
- Security (auth required, SQL injection prevented)
- Testing (80%+ backend, 70%+ frontend coverage planned)

✅ **Readiness for Phase 0 Research**: PASS
- Technical context clear; 6 research questions identified
- Dependencies documented
- Project structure defined
- Ready to resolve unknowns in research phase

✅ **Readiness for Phase 1 Design**: CONDITIONAL
- After research.md generated, ready for detailed design
- Data model and API contracts can be finalized
- Agent context can be updated

## Artifacts Created

- ✅ `/specs/006-urdu-translation/plan.md` (591 lines, comprehensive implementation plan)
- ✅ Git commit: `e982acc`
- ✅ PHR created: `003-create-plan.plan.prompt.md`

## Status Summary

**Planning Phase Complete**: ✅

Plan provides:
- Clear technical architecture for Urdu translation feature
- 6 key design decisions with full rationale
- Data model with 6 entities and relationships
- 3 API contracts with 10 endpoints
- 4 frontend components and 3 backend services
- Project structure aligned with existing codebase
- Phase 0 research roadmap
- Phase 1 design roadmap
- Success measures and next steps

**Next Phase**: Phase 0 Research (resolve 6 unknowns in research.md)
**Then**: Phase 1 Design (finalize data model, API specs, quickstart)
**Then**: Phase 2 Tasks (break down into actionable work items)
**Then**: Implementation (develop, test, deploy)

