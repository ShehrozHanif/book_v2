# Implementation Plan: Urdu Language Translation for RAG Chatbot

**Branch**: `006-urdu-translation` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-urdu-translation/spec.md`

---

## Summary

Enable Urdu-speaking users to interact with the RAG chatbot in their native language by implementing bilingual chatbot response translation with authentication-required access. The system will translate 50-100 core chatbot response templates to Urdu in Phase 1, featuring Right-to-Left (RTL) layout support, technical terminology consistency, and persistent language preferences for authenticated users. The implementation leverages the existing FastAPI backend, Neon PostgreSQL, and React frontend while adding translation management infrastructure.

---

## Technical Context

**Language/Version**: Python 3.10+, TypeScript 5.0+, React 18+

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy (async), Pydantic
- Frontend: React, Tailwind CSS, RTL libraries (e.g., `rtl-detect` or `postcss-rtl`)
- Infrastructure: Neon PostgreSQL, Qdrant (for vector embeddings)
- Translation Management: (TBD - may use translation files or database)

**Storage**:
- Neon PostgreSQL for chatbot response templates, translations, glossary, user preferences
- Response templates stored in database with versioning
- Urdu translations stored as separate field with version tracking

**Testing**:
- pytest for backend (unit, integration, RTL rendering tests)
- Jest/React Testing Library for frontend (RTL layout tests, language switching)
- Manual QA for RTL text rendering across browsers

**Target Platform**: Web (FastAPI backend + React frontend), Mobile-optimized

**Project Type**: Web application (existing backend + frontend enhancement)

**Performance Goals**:
- Chatbot response time < 3 seconds (unaffected by language translation)
- Language toggle < 1 second (no page reload)
- Glossary lookup < 500ms for authenticated users

**Constraints**:
- Authentication required before Urdu access (no guest Urdu)
- Language switching must not lose chat history
- RTL support must work with existing code highlighting library
- Urdu fonts must load without breaking chat layout
- Translation storage must not duplicate entire response content

**Scale/Scope**:
- Phase 1: 50-100 core chatbot response templates
- Phase 2: 100+ additional templates
- 150+ technical glossary terms
- Estimated user base: 5-20% Urdu speakers

---

## Constitution Check

**GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.**

| Principle | Check | Status |
|-----------|-------|--------|
| **Specification-Driven Development** | Feature has comprehensive spec with 5 user stories, 13 requirements, 10 success criteria | ✅ PASS |
| **Educational Excellence** | Technical terminology consistency maintained; glossary with translations/pronunciations | ✅ PASS |
| **User-Centric Design** | Language preference persists; seamless switching; accessible to authenticated users | ✅ PASS |
| **Production Readiness** | All API endpoints tested; error handling; RTL rendering quality; no hardcoded translations | ✅ PASS |
| **Composability & Reusability** | Translation service modular; glossary service reusable; language preference extensible | ✅ PASS |
| **Technology Stack** | Uses FastAPI (backend), React (frontend), Neon (database) - all approved | ✅ PASS |
| **Security** | Authentication required; no hardcoded secrets; SQL injection prevented by SQLAlchemy | ✅ PASS |
| **Testing** | Plan includes unit/integration/RTL tests; backend 80%+ coverage; critical paths 100% | ✅ PASS |

**Gate Result**: ✅ PASS - Feature complies with all constitution principles.

---

## Project Structure

### Documentation (this feature)

```text
specs/006-urdu-translation/
├── spec.md                    # Feature specification ✅
├── plan.md                    # This file (Phase 1 output)
├── research.md                # Phase 0 output (to be generated)
├── data-model.md              # Phase 1 output (to be generated)
├── quickstart.md              # Phase 1 output (to be generated)
├── contracts/                 # Phase 1 output (to be generated)
│   ├── chatbot-translation-api.openapi.yaml
│   ├── glossary-api.openapi.yaml
│   └── language-preference-api.openapi.yaml
├── checklists/
│   └── requirements.md         # Quality checklist ✅
└── README.md                  # Navigation guide ✅
```

### Source Code (repository root)

```text
# Backend: Python/FastAPI
backend/src/personalization/
├── models/
│   ├── db_models.py           # New: ChatbotResponseTemplate, ChatbotTranslation, GlossaryTerm, etc.
│   └── schemas.py             # New: request/response schemas for chatbot translation endpoints
├── services/
│   ├── chatbot_translation_service.py  # New: Translation management, caching
│   ├── glossary_service.py             # New: Glossary retrieval for authenticated users
│   └── language_preference_service.py   # New: Preference persistence
├── api/
│   ├── routes/
│   │   ├── chatbot_translation.py      # New: Endpoints for language selection, translation toggle
│   │   ├── glossary.py                 # New: Glossary endpoints (authenticated)
│   │   └── language_preferences.py     # New: User preference endpoints
│   └── middleware/
│       └── language.py                 # New: Language detection/routing middleware
└── tests/
    ├── test_chatbot_translation_service.py   # Unit tests
    ├── test_glossary_service.py              # Unit tests
    ├── test_language_preference_service.py   # Unit tests
    ├── test_chatbot_translation_routes.py    # Integration tests
    ├── test_glossary_routes.py               # Integration tests
    ├── test_rtl_rendering.py                 # RTL layout validation tests
    └── test_language_switching.py            # End-to-end tests

# Frontend: React/TypeScript
frontend/src/
├── components/
│   ├── ChatBot/
│   │   ├── ChatbotLanguageToggle.tsx    # New: Language selector in chatbot
│   │   ├── ChatbotMessageRTL.tsx        # New: RTL-aware message display
│   │   └── ChatbotGlossary.tsx          # New: Glossary modal for authenticated users
│   └── LanguagePreference/
│       └── LanguageSettings.tsx         # New: Language preference form
├── hooks/
│   ├── useLanguagePreference.ts         # New: Hook for language preference
│   ├── useChatbotLanguage.ts            # New: Hook for chatbot language switching
│   └── useGlossary.ts                   # New: Hook for glossary lookup
├── styles/
│   └── rtl.css                          # New: RTL-specific styling
├── services/
│   ├── chatbotTranslationAPI.ts         # New: API calls for translations
│   ├── glossaryAPI.ts                   # New: API calls for glossary
│   └── languagePreferenceAPI.ts         # New: API calls for preferences
└── tests/
    ├── ChatbotLanguageToggle.test.tsx    # Component tests
    ├── ChatbotMessageRTL.test.tsx        # RTL rendering tests
    ├── useLanguagePreference.test.ts     # Hook tests
    └── integration/
        └── chatbot-urdu-flow.test.tsx    # End-to-end Urdu chatbot flow

# Shared
backend/alembic/versions/
└── 00X_add_chatbot_translation.py      # Database migration for new tables
```

**Structure Decision**: Web application with backend (FastAPI) and frontend (React) separation. Backend handles translation logic, authentication checks, and glossary management. Frontend handles language switching UI, RTL rendering, and preference management. Database (Neon PostgreSQL) stores all translation data with versioning.

---

## Key Design Decisions

### 1. Response Template Translation Model

**Decision**: Store translations at the response template level, not at individual response level.

**Rationale**:
- Chatbot generates responses dynamically from templates + context
- Templates are stable; individual responses are unique
- Translating templates enables consistent terminology across all responses
- Reduces storage overhead (translate 100 templates, not 10,000 responses)

**Alternatives Considered**:
- A) Store translations in external file (i18n approach) → Too rigid for dynamic chatbot
- B) Store translations inline with responses → Duplicates storage
- C) Use machine translation on-the-fly → Inconsistent terminology, slower

**Implementation**: Database table `chatbot_response_template` with fields:
- `id`, `template_key` (unique identifier)
- `english_content` (source template)
- `urdu_content` (translated template, nullable until translated)
- `version`, `translator`, `status` (draft/published/reviewed)

### 2. Authentication Gate for Urdu

**Decision**: Require authentication before user can select Urdu language.

**Rationale**:
- Authenticated users get language preference persistence
- Guest users see English-only interface
- Simplifies preference storage (database vs browser)
- Meets specification requirement: "authentication required for Urdu features"

**Alternatives Considered**:
- A) Allow guests to use Urdu with browser storage → Messy, inconsistent experience
- B) Allow guests but revert to English on logout → Confusing UX
- C) Require auth → Clear, simple, aligns with feature design

**Implementation**:
- Add authentication check in chatbot language selection endpoint
- Return 401 Unauthorized if guest requests Urdu
- Frontend redirects to login flow
- After login, restore previous language preference

### 3. Glossary Access Control

**Decision**: Glossary accessible to all authenticated users, read-only. Suggestions via feedback mechanism.

**Rationale**:
- Glossary supports learning in both languages
- Authenticated users benefit from curriculum-wide glossary
- Feedback channel enables improvement without moderation burden
- Admins curate suggestions quarterly

**Alternatives Considered**:
- A) Glossary public to all → Inconsistent with auth requirement
- B) Glossary admin-only → Limits learner support
- C) Public glossary + forum → Moderation overhead
- D) Authenticated access + feedback → Clean, scalable

**Implementation**:
- Table `glossary_term` with `id`, `english_term`, `urdu_translation`, `pronunciation`
- Endpoint `GET /glossary?language=urdu` (requires auth)
- Endpoint `POST /glossary/feedback` (authenticated user suggestions)
- Admin endpoint to review and promote suggestions

### 4. RTL Implementation Strategy

**Decision**: Use CSS `direction: rtl` with logical properties; avoid bidirectional string reversal.

**Rationale**:
- CSS `direction: rtl` handles text alignment, margin/padding reversal automatically
- Logical properties (`inline-start`, `block-end`) work across LTR/RTL contexts
- Avoids hacky string reversal that breaks code blocks
- Compatible with existing Tailwind CSS setup

**Alternatives Considered**:
- A) CSS Flexbox with `flex-direction: row-reverse` → Only works for layout, not text
- B) String reversal → Breaks code, numbers, punctuation
- C) HTML `dir="rtl"` attribute → Works but less flexible than CSS
- D) CSS `direction: rtl` + logical properties → Clean, maintainable

**Implementation**:
- Conditional CSS class based on language: `dir-ltr` vs `dir-rtl`
- Use Tailwind logical properties: `ps-4` (padding-inline-start), `me-2` (margin-inline-end)
- Override code block styles: `[&_code]{ direction: ltr; }` to keep code LTR

### 5. Language Preference Persistence

**Decision**: Store in database for authenticated users; browser localStorage for guests (English-only).

**Rationale**:
- Authenticated users get persistent preferences across devices
- Guests can't access Urdu anyway (auth required), so no need for guest storage
- Database storage enables admin analytics (which users prefer Urdu)
- Reduces complexity (one storage mechanism instead of two)

**Alternatives Considered**:
- A) Browser localStorage only → No cross-device persistence
- B) Database only → Requires migration from localStorage
- C) Both databases + localStorage → Sync complexity
- D) Database for auth users, localStorage for guests → Needed but guests can't use Urdu

**Implementation**:
- Table `user_language_preference` with `user_id`, `language`, `updated_at`
- Endpoint `POST /users/{user_id}/language-preference` (authenticated)
- Fetch preference on login, apply to chatbot UI
- Update on language toggle

### 6. Translation Quality Assurance

**Decision**: Hybrid approach (manual translation + automated post-translation audits).

**Rationale**:
- Human translators understand context and domain expertise
- Automated audits catch systematic errors (spelling, missing terms)
- No tool friction during translation phase (faster delivery)
- Validation phase before publication (ensures quality)

**Alternatives Considered**:
- A) Automated terminology checking during translation → Slows translators down
- B) Manual review only → Misses systematic errors
- C) Machine translation → Poor quality, inconsistent
- D) Hybrid (manual + audits) → Best balance

**Implementation**:
- Pre-translation: Provide style guide + glossary database
- Translation: Translators work without tools
- Post-translation audit: Automated scan for inconsistencies
  - Flagged terms run through glossary validator
  - Report generated for human review
- Quality review: Human resolves flags, approves for publication
- Timeline: 1-2 days audit per 50 templates, 3-5 days review per 50 templates

---

## Phase 0: Research (TBD in research.md)

Research tasks to resolve before Phase 1 design:

1. **RTL Font Rendering**: Which Urdu fonts work best across browsers? (Google Fonts Noto Sans Urdu vs. others)
2. **Code Block RTL**: How to keep code blocks LTR while surrounding text is RTL?
3. **ChatBot Template Format**: Current chatbot response structure? Are templates stored in code or database?
4. **Translation Storage**: Should translations be in JSON files or database? (Recommend database for versioning)
5. **Existing Auth System**: How does current JWT/authentication work? What user context is available?
6. **Performance**: Current chatbot response time? Will translation lookup add measurable overhead?

---

## Phase 1: Design & Contracts

### 1.1 Data Model (data-model.md)

**Entities to define**:

#### ChatbotResponseTemplate
```
id: UUID
template_key: str (unique, e.g., "greeting", "ros2_intro")
english_content: str (Jinja2 template or markdown)
version: int
created_at: datetime
updated_at: datetime
status: enum (published, draft, archived)
```

#### ChatbotTranslation
```
id: UUID
response_template_id: UUID (FK)
language: enum (urdu)
translated_content: str (nullable until translation complete)
translator_id: UUID (FK to User)
translated_at: datetime
reviewed_at: datetime
status: enum (draft, in_review, published)
version: int (tracks English version this translation covers)
```

#### GlossaryTerm
```
id: UUID
english_term: str (unique)
urdu_translation: str
pronunciation_transliterated: str (Latin characters)
definition_english: str
definition_urdu: str
category: str (e.g., "robotics", "control", "kinematics")
created_at: datetime
updated_at: datetime
status: enum (published, under_review)
```

#### GlossaryFeedback
```
id: UUID
user_id: UUID (FK)
glossary_term_id: UUID (nullable - for existing terms)
suggested_term: str (nullable - for new terms)
feedback_type: enum (suggestion, correction, new_term)
content: str
created_at: datetime
reviewed_at: datetime
admin_response: str (nullable)
status: enum (pending, accepted, rejected)
```

#### UserLanguagePreference
```
id: UUID
user_id: UUID (FK, unique)
language: enum (english, urdu)
updated_at: datetime
```

#### ChatbotResponseTranslationStatus
```
id: UUID
response_template_id: UUID (FK, unique)
english_version: int
urdu_version: int (nullable - not yet translated)
status: enum (translated, needs_translation, needs_review, stale)
last_updated: datetime
```

**Relationships**:
- `ChatbotTranslation` → `ChatbotResponseTemplate` (many translations per template across versions)
- `ChatbotTranslation` → `User` (translator) (many translations per translator)
- `UserLanguagePreference` → `User` (one preference per user)
- `GlossaryFeedback` → `User` (feedback from user)
- `GlossaryFeedback` → `GlossaryTerm` (feedback on term)

### 1.2 API Contracts (contracts/)

**Three main APIs**:

1. **Chatbot Translation API** (for selecting/switching language in chatbot)
   - `GET /api/v1/chatbot/language` - Get current user's preferred chatbot language
   - `POST /api/v1/chatbot/language` - Set chatbot language (requires auth, validates Urdu)
   - `GET /api/v1/chatbot/response/{template_key}` - Get response template in preferred language
   - `GET /api/v1/chatbot/templates?language=urdu` - List all translated templates

2. **Glossary API** (for term lookups in chat)
   - `GET /api/v1/glossary` - List all terms (query params: language, category, search)
   - `GET /api/v1/glossary/{term_id}` - Get single term in requested language
   - `GET /api/v1/glossary/search?q=urdu_text` - Search glossary (requires auth)
   - `POST /api/v1/glossary/feedback` - Submit term suggestion/feedback (requires auth)

3. **Language Preference API** (for profile settings)
   - `GET /api/v1/users/{user_id}/language-preference` - Get user's language preference
   - `PUT /api/v1/users/{user_id}/language-preference` - Update language preference (requires auth)

**Authentication**: All Urdu endpoints require valid JWT token (Bearer token in header)

**Error Codes**:
- `401 Unauthorized` - Guest attempting Urdu language
- `403 Forbidden` - User accessing another user's preferences
- `404 Not Found` - Template or term doesn't exist
- `422 Unprocessable Entity` - Invalid language selection (only urdu/english supported)
- `500 Internal Server Error` - Translation service error (graceful fallback to English)

See `/contracts/` for OpenAPI specifications.

### 1.3 Frontend Components (quickstart.md)

**Key components to implement**:

1. **ChatbotLanguageToggle.tsx**
   - Displays language buttons (English / اردو)
   - Shows only to authenticated users
   - On click: Validates auth, updates preference, re-fetches chatbot context
   - Visual indicator of current language

2. **ChatbotMessageRTL.tsx**
   - Wraps chatbot responses
   - Applies `dir="rtl"` for Urdu, `dir="ltr"` for English
   - Handles code block LTR-ing
   - Responsive for mobile (font size, padding)

3. **ChatbotGlossary.tsx**
   - Modal/side panel for glossary lookup
   - Search box with live results
   - Term detail view: English → Urdu + pronunciation
   - Only visible to authenticated users

4. **LanguageSettings.tsx**
   - User profile page language preference
   - Radio buttons: English / Urdu
   - Save button with success confirmation
   - Loading state while updating

**Styling**: Tailwind CSS with custom RTL utilities
- Create `rtl.css` with:
  - `@supports (direction: rtl)` blocks for RTL-specific rules
  - Logical properties (padding-inline-start, margin-block-end, etc.)
  - Code block LTR override

### 1.4 Backend Services (services/)

**Three main services**:

1. **ChatbotTranslationService**
   - Load response templates from database
   - Cache translations (in-memory with TTL)
   - Fallback to English if translation missing
   - Methods:
     - `get_response(template_key: str, language: str) → str`
     - `get_translated_template(template_key: str) → ChatbotTranslation`
     - `invalidate_cache(template_key: str = None)`

2. **GlossaryService**
   - Load glossary terms from database
   - Search functionality (full-text search on terms)
   - Methods:
     - `get_term(term_id: UUID) → GlossaryTerm`
     - `search_terms(query: str, language: str) → List[GlossaryTerm]`
     - `get_all_terms(language: str = "urdu") → List[GlossaryTerm]`
     - `submit_feedback(user_id: UUID, feedback_data) → GlossaryFeedback`

3. **LanguagePreferenceService**
   - Persist user language choice
   - Retrieve on login
   - Methods:
     - `get_preference(user_id: UUID) → UserLanguagePreference`
     - `set_preference(user_id: UUID, language: str) → UserLanguagePreference`
     - `validate_language(language: str) → bool`

### 1.5 Database Migrations (alembic/)

Create migration `00X_add_chatbot_translation.py`:
- Create all 6 tables (ResponseTemplate, Translation, GlossaryTerm, Feedback, Preference, Status)
- Create indexes on common queries:
  - `(response_template_id, status)` on ChatbotTranslation
  - `(english_term)` on GlossaryTerm (unique)
  - `(user_id)` on UserLanguagePreference (unique)
  - `(language, status)` on ChatbotTranslation for filtering
- Add foreign key constraints with CASCADE delete where appropriate

---

## Phase 1 Continuation: Agent Context Update

**Action**: After data model and contracts finalized:
- Run `.specify/scripts/bash/update-agent-context.sh` (or PowerShell equivalent)
- Agent-specific context files updated with:
  - New database tables and schemas
  - New API endpoints
  - New services and their responsibilities
  - New frontend components
  - Testing requirements

---

## Complexity Tracking

**No Constitution violations detected.** Feature aligns with all principles:
- ✅ Specification-driven (comprehensive spec completed)
- ✅ Educational excellence (terminology consistency)
- ✅ User-centric (authenticated preference persistence)
- ✅ Production-ready (tested, documented, error-handled)
- ✅ Composable (modular services and components)

**Inherent Complexity**: Low-to-Medium
- RTL rendering: Moderate (CSS-based, not hacky string reversal)
- Translation management: Low (CRUD operations)
- Authentication integration: Low (uses existing JWT system)
- Database design: Low-to-Moderate (straightforward schema)

---

## Next Steps

### Immediate (Before Phase 2 - Tasks)

1. **Generate research.md** (Phase 0):
   - Research Urdu font options and performance
   - Research current chatbot template storage
   - Research code block RTL handling patterns
   - Research existing auth system integration points

2. **Finalize data-model.md** with detailed SQL schema

3. **Generate OpenAPI contracts** in `/contracts/`

4. **Update agent context** with new technologies/patterns

### Then (Phase 2 - Tasks)

5. Run `/sp.tasks` to break down into actionable work items:
   - Backend database migration
   - Backend API endpoints (3 main routes)
   - Backend services (3 main services)
   - Frontend components (4 main components)
   - Tests (unit, integration, RTL rendering, end-to-end)

### Implementation Phase (After Approval)

6. Implement Phase 1: 50-100 core response template translations
7. QA and testing (RTL rendering across browsers)
8. Deploy to staging environment
9. User testing with Urdu-speaking users
10. Iterate on feedback
11. Plan Phase 2: Additional 100+ templates

---

## Success Measures

| Metric | Target | Verification |
|--------|--------|---------------|
| **Language Toggle Speed** | <1 second | Lighthouse performance audit |
| **RTL Rendering Quality** | 95%+ browsers correct | Manual testing on Chrome, Firefox, Safari, mobile browsers |
| **Glossary Search Performance** | <500ms | Backend load test |
| **Translation Consistency** | 100% terminology match | Automated audit script |
| **Authentication Validation** | 100% Urdu blocked for guests | Automated endpoint tests |
| **Preference Persistence** | 100% across sessions | Integration tests (logout/login cycle) |
| **Code Test Coverage** | 80%+ backend, 70%+ frontend | pytest/Jest coverage reports |
| **User Satisfaction** | 4.0+ rating | Post-launch survey |

---

## References

- **Specification**: [spec.md](./spec.md)
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- **Existing Stack**: FastAPI, SQLAlchemy, React, Tailwind CSS
- **Similar Features**: Language preference system (already in personalization module)

**Plan Status**: ✅ READY FOR RESEARCH PHASE (Phase 0)

Next: Run research tasks, then Phase 1 design, then `/sp.tasks` for implementation.

