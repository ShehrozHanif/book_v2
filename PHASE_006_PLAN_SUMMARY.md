# Phase 006: Urdu Translation - Planning Complete ✅

**Date**: 2026-02-10
**Feature**: 006-urdu-translation (Urdu Language Translation for RAG Chatbot)
**Branch**: release/003-personalization-complete
**Status**: ✅ Planning Phase COMPLETE - Ready for Phase 0 Research

---

## Executive Summary

Comprehensive implementation plan created for enabling Urdu-speaking users to interact with the RAG chatbot in their native language. The plan defines a phased approach:
- **Phase 1 (MVP)**: Translate 50-100 core chatbot response templates with RTL support and authentication-required access
- **Phase 2**: Expand to 100+ additional templates
- **Scope**: RAG Chatbot ONLY (not textbook chapters), authentication required, persistent language preferences

---

## Artifacts Delivered

### 1. Implementation Plan
**File**: `specs/006-urdu-translation/plan.md` (591 lines, 24 KB)

**Contains**:
- ✅ Technical context (Python 3.10+, FastAPI, React 18+, Neon PostgreSQL)
- ✅ Constitution check (PASS - all 8 principles satisfied)
- ✅ 6 key design decisions with rationale and alternatives
- ✅ Project structure (documentation + source code)
- ✅ Data model with 6 entities (ChatbotResponseTemplate, Translation, GlossaryTerm, Feedback, Preference, Status)
- ✅ API contracts (10 endpoints across 3 main APIs)
- ✅ Frontend component design (4 components)
- ✅ Backend service design (3 services)
- ✅ Database migration strategy
- ✅ Phase 0 research roadmap (6 unknowns to resolve)
- ✅ Phase 1 design roadmap
- ✅ 8 success measures with verification methods

### 2. Previous Artifacts (Specification Phase)
- ✅ `specs/006-urdu-translation/spec.md` (460 lines, 21 KB)
  - 5 user stories with prioritization
  - 13 functional requirements
  - 10 success criteria
  - 8 assumptions
  - Clarified scope and out-of-scope items

- ✅ `specs/006-urdu-translation/README.md` (navigation guide)
- ✅ `specs/006-urdu-translation/checklists/requirements.md` (quality checklist)
- ✅ `SPEC_006_URDU_TRANSLATION_SUMMARY.md` (executive summary)

### 3. Prompt History Records
- ✅ `001-create-spec.spec.prompt.md` (specification creation)
- ✅ `002-clarify-scope.spec.prompt.md` (scope clarification)
- ✅ `003-create-plan.plan.prompt.md` (implementation planning)

---

## Key Design Decisions

| # | Decision | Rationale | Alternatives Considered |
|---|----------|-----------|------------------------|
| 1 | **Response Template Translation Model** | Translate 100 templates, not responses; consistent terminology; reduced storage | i18n files (rigid), inline translations (duplicated), on-the-fly (inconsistent) |
| 2 | **Authentication Gate** | Require login for Urdu; persistent preferences; simple UX | Guest Urdu (messy), allow guests with revert (confusing) |
| 3 | **Glossary Access Control** | Authenticated users read-only + feedback mechanism | Public (inconsistent), admin-only (limited), forum (moderation burden) |
| 4 | **RTL Implementation** | CSS `direction: rtl` + logical properties | Flexbox reverse (layout only), string reversal (breaks code), HTML dir (less flexible) |
| 5 | **Language Preference Persistence** | Database for authenticated users | localStorage (no cross-device), both (sync complexity) |
| 6 | **Translation QA Strategy** | Manual translation + automated post-translation audits | Automated checks (slows translators), manual-only (misses errors), machine translation (poor quality) |

---

## Technical Architecture

### Data Model (6 Entities)

```
ChatbotResponseTemplate
├── id: UUID
├── template_key: str (unique)
├── english_content: str
├── version: int
├── status: enum (published, draft, archived)
└── [relationships to ChatbotTranslation, TranslationStatus]

ChatbotTranslation
├── id: UUID
├── response_template_id: UUID (FK)
├── language: enum (urdu)
├── translated_content: str (nullable)
├── translator_id: UUID (FK)
├── version: int
├── status: enum (draft, in_review, published)
└── timestamps: translated_at, reviewed_at

GlossaryTerm
├── id: UUID
├── english_term: str (unique)
├── urdu_translation: str
├── pronunciation_transliterated: str
├── definition_english: str
├── definition_urdu: str
├── category: str
└── status: enum (published, under_review)

GlossaryFeedback
├── id: UUID
├── user_id: UUID (FK)
├── glossary_term_id: UUID (nullable, FK)
├── feedback_type: enum (suggestion, correction, new_term)
├── content: str
├── status: enum (pending, accepted, rejected)
└── admin_response: str (nullable)

UserLanguagePreference
├── id: UUID
├── user_id: UUID (FK, unique)
├── language: enum (english, urdu)
└── updated_at: datetime

ChatbotResponseTranslationStatus
├── id: UUID
├── response_template_id: UUID (FK, unique)
├── english_version: int
├── urdu_version: int (nullable)
├── status: enum (translated, needs_translation, needs_review, stale)
└── last_updated: datetime
```

### API Contracts (10 Endpoints)

**Chatbot Translation API** (4 endpoints)
```
GET    /api/v1/chatbot/language
POST   /api/v1/chatbot/language
GET    /api/v1/chatbot/response/{template_key}
GET    /api/v1/chatbot/templates?language=urdu
```

**Glossary API** (4 endpoints)
```
GET    /api/v1/glossary
GET    /api/v1/glossary/{term_id}
GET    /api/v1/glossary/search?q=text
POST   /api/v1/glossary/feedback
```

**Language Preference API** (2 endpoints)
```
GET    /api/v1/users/{user_id}/language-preference
PUT    /api/v1/users/{user_id}/language-preference
```

All Urdu endpoints require JWT authentication (Bearer token).

### Frontend Components (4 Components)

1. **ChatbotLanguageToggle.tsx** - Language selector in chatbot (English/اردو)
2. **ChatbotMessageRTL.tsx** - RTL-aware message display with code block handling
3. **ChatbotGlossary.tsx** - Glossary modal with search (authenticated users)
4. **LanguageSettings.tsx** - User profile language preference form

### Backend Services (3 Services)

1. **ChatbotTranslationService** - Load templates, cache translations, fallback to English
2. **GlossaryService** - Search terms, manage feedback, admin curation
3. **LanguagePreferenceService** - Persist and retrieve user preferences

### Project Structure

```
Backend:
  backend/src/personalization/
  ├── models/db_models.py (6 tables)
  ├── models/schemas.py (request/response)
  ├── services/chatbot_translation_service.py
  ├── services/glossary_service.py
  ├── services/language_preference_service.py
  ├── api/routes/chatbot_translation.py
  ├── api/routes/glossary.py
  ├── api/routes/language_preferences.py
  └── tests/ (10+ test files, 80%+ coverage)

Frontend:
  frontend/src/
  ├── components/ChatBot/ (3 components)
  ├── components/LanguagePreference/ (1 component)
  ├── hooks/ (3 custom hooks)
  ├── services/ (3 API services)
  ├── styles/rtl.css (Tailwind RTL utilities)
  └── tests/ (8+ test files, 70%+ coverage)

Database:
  backend/alembic/versions/00X_add_chatbot_translation.py
  (6 tables with indexes and constraints)
```

---

## Constitution Check

**Result**: ✅ **PASS** - All 8 principles satisfied

| Principle | Status | Evidence |
|-----------|--------|----------|
| Specification-Driven | ✅ | Comprehensive spec with 5 stories, 13 requirements, 10 criteria |
| Educational Excellence | ✅ | Terminology consistency, glossary with pronunciations |
| User-Centric | ✅ | Persistent preferences, seamless switching, auth-gated access |
| Production-Ready | ✅ | Error handling, RTL quality, no hardcoded translations |
| Composable | ✅ | Modular services, reusable components, extensible schema |
| Tech Stack | ✅ | FastAPI, React, Neon (all approved) |
| Security | ✅ | Auth required, no secrets in code, SQL injection prevented |
| Testing | ✅ | 80%+ backend, 70%+ frontend coverage planned |

---

## Phase 0: Research Tasks (6 Unknowns)

**Status**: Identified, ready for research phase

1. **Urdu Font Rendering** - Which fonts work best across browsers? (Google Fonts Noto Sans Urdu vs. others)
2. **Code Block RTL** - Pattern for keeping code LTR while surrounding text RTL?
3. **Chatbot Template Format** - Current response structure? Database or code-based?
4. **Translation Storage** - JSON files or database? (Recommend database for versioning)
5. **Auth System Integration** - Current JWT flow? How to check authentication in endpoints?
6. **Performance Baseline** - Current chatbot response time? What translation lookup overhead?

---

## Phase 1: Design Roadmap (After Research)

**Deliverables**:
1. `research.md` - Answers to 6 research questions with findings
2. `data-model.md` - Detailed SQL schema and migrations
3. `contracts/` - OpenAPI specifications for all 3 APIs
4. `quickstart.md` - Setup and development guide
5. Updated agent context with new technologies

**Timeline**: 1-2 weeks

---

## Success Measures (8 Metrics)

| Metric | Target | Verification Method |
|--------|--------|---------------------|
| **Language Toggle Speed** | <1 second | Lighthouse performance audit |
| **RTL Rendering Quality** | 95%+ browsers correct | Manual testing across Chrome, Firefox, Safari, mobile |
| **Glossary Search Performance** | <500ms | Backend load test |
| **Terminology Consistency** | 100% match | Automated audit script comparing all instances |
| **Authentication Validation** | 100% guest block | Automated endpoint tests (401 Unauthorized) |
| **Preference Persistence** | 100% across sessions | Integration tests (logout/login cycle) |
| **Code Test Coverage** | 80%+ backend, 70%+ frontend | pytest/Jest coverage reports |
| **User Satisfaction** | 4.0+ rating (out of 5) | Post-launch survey of Urdu users |

---

## Git Commits (This Phase)

```
e982acc docs: create implementation plan for 006-urdu-translation feature
129f759 docs: clarify 006-urdu-translation scope - RAG chatbot only with auth required
29eec08 spec: answer 3 clarification questions for 006-urdu-translation
9a20640 docs: add README for 006-urdu-translation specification
ce7e1ba docs: add Urdu translation specification summary
abe4a39 spec: create 006-urdu-translation feature specification
```

---

## Current Status

| Phase | Status | Deliverables |
|-------|--------|--------------|
| **Specification** | ✅ COMPLETE | spec.md (460 lines), clarity checked, 3 questions answered |
| **Planning** | ✅ COMPLETE | plan.md (591 lines), 6 decisions, data model, API contracts |
| **Research** | ⏳ PENDING | 6 unknowns identified, ready for investigation |
| **Design** | ⏳ PENDING | After research: data-model.md, contracts, quickstart |
| **Tasks** | ⏳ PENDING | After design: `/sp.tasks` to generate work items |
| **Implementation** | ⏳ PENDING | After tasks: Phase 1 MVP development |

---

## Next Steps

### Immediate (Before Implementation)
1. ✅ **Specification** - COMPLETE
2. ✅ **Planning** - COMPLETE
3. ⏳ **Research** (Phase 0) - Resolve 6 unknowns
4. ⏳ **Design** (Phase 1) - Finalize schemas and contracts
5. ⏳ **Task Generation** (Phase 2) - Run `/sp.tasks`

### Then (Implementation Phase)
6. Implement Phase 1: 50-100 core response templates
7. Comprehensive testing (unit, integration, RTL, e2e)
8. Staging deployment
9. User testing with Urdu-speaking users
10. Iterate on feedback
11. Plan Phase 2: Additional 100+ templates

---

## Recommended Next Command

After reviewing this plan:

```bash
# Phase 0: Research (manually or using agents to resolve 6 unknowns)
# Then:
/sp.tasks
# To generate actionable work items for Phase 1 implementation
```

---

## Summary

The implementation plan for Urdu translation provides:

✅ **Clear Architecture** - 6 design decisions with full rationale
✅ **Complete Data Model** - 6 entities with relationships
✅ **API Design** - 10 endpoints across 3 main APIs
✅ **Component Design** - 4 frontend + 3 backend services
✅ **Project Structure** - Clear file organization and responsibilities
✅ **Quality Assurance** - Phase 0 research + Phase 1 design roadmap
✅ **Success Criteria** - 8 measurable metrics with verification
✅ **Constitution Alignment** - All 8 project principles satisfied

**Status**: Ready for Phase 0 Research and subsequent implementation phases.

---

**Created**: 2026-02-10
**Branch**: release/003-personalization-complete
**Next Review**: After Phase 0 research completion

