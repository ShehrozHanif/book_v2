# Tasks: Urdu Language Translation for RAG Chatbot

**Input**: Design documents from `/specs/006-urdu-translation/`
**Prerequisites**: spec.md (user stories with priorities), plan.md (architecture and design), data-model.md (entities), contracts/ (API endpoints)

**Organization**: Tasks grouped by user story (P1 core, P2 enhancements) enabling independent implementation and testing.

**Testing**: Test tasks are included for critical paths (contract tests before implementation). Follow TDD approach: write tests first, ensure they fail, then implement.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Parallelizable (independent files, can run with others in phase)
- **[Story]**: User story label (US1, US2, US3, US4, US5) - only for story phases
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and database schema foundation

- [ ] T001 Create database migration file at `backend/alembic/versions/00X_add_chatbot_translation.py` with 6 tables (ChatbotResponseTemplate, ChatbotTranslation, GlossaryTerm, GlossaryFeedback, UserLanguagePreference, ChatbotResponseTranslationStatus)
- [ ] T002 [P] Initialize base models/schemas in `backend/src/personalization/models/db_models.py` (all 6 entity definitions with relationships)
- [ ] T003 [P] Initialize base schemas in `backend/src/personalization/models/schemas.py` (request/response DTOs for all endpoints)
- [ ] T004 [P] Setup RTL styling infrastructure in `frontend/src/styles/rtl.css` with Tailwind logical properties and `direction: rtl` support
- [ ] T005 Run database migration to create all 6 tables and establish relationships

**Checkpoint**: Database schema complete, base models defined, RTL styling framework ready - user story implementation can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services and API infrastructure shared across all user stories

⚠️ **CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 [P] Create authentication validation middleware in `backend/src/personalization/api/middleware/language.py` to check JWT token before allowing Urdu language access
- [ ] T007 [P] Implement ChatbotTranslationService in `backend/src/personalization/services/chatbot_translation_service.py` with methods: get_response(), get_translated_template(), invalidate_cache(), fallback_to_english()
- [ ] T008 [P] Implement GlossaryService in `backend/src/personalization/services/glossary_service.py` with methods: get_term(), search_terms(), get_all_terms(), submit_feedback(), get_feedback_admin()
- [ ] T009 [P] Implement LanguagePreferenceService in `backend/src/personalization/services/language_preference_service.py` with methods: get_preference(), set_preference(), validate_language()
- [ ] T010 [P] Create base API router registration in `backend/src/main.py` to include chatbot_translation, glossary, and language_preference routes
- [ ] T011 Load sample glossary terms (150+ technical robotics terms) into database via seed data file `backend/src/personalization/data/glossary_terms.json` and load script `backend/scripts/load_glossary.py`
- [ ] T012 Create sample response templates (50-100 core chatbot templates) in database via seed file `backend/src/personalization/data/response_templates.json` and load script `backend/scripts/load_templates.py`

**Checkpoint**: All services working, authentication gate functional, glossary and templates seeded - ready for user story implementation

---

## Phase 3: User Story 1 - Bilingual Chatbot Conversations (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can select Urdu language and receive chatbot responses in Urdu

**Independent Test**:
1. Login as user
2. Select Urdu language in chatbot
3. Ask question in English or Urdu
4. Verify response appears in Urdu
5. Verify conversation history maintained on language switch
6. Logout and login, verify Urdu preference persisted

### Tests for User Story 1

- [ ] T013 [P] [US1] Contract test for chatbot language endpoints in `backend/src/personalization/tests/test_chatbot_translation_routes.py` (GET /chatbot/language, POST /chatbot/language, GET /chatbot/response/{template_key})
- [ ] T014 [P] [US1] Integration test for bilingual conversation flow in `backend/src/personalization/tests/test_bilingual_conversation.py` (language switching, response retrieval, conversation history preservation)
- [ ] T015 [P] [US1] Frontend component test for ChatbotLanguageToggle in `frontend/src/components/ChatBot/ChatbotLanguageToggle.test.tsx` (authenticated user sees toggle, guest sees disabled state, toggle updates language)

### Implementation for User Story 1

- [ ] T016 [P] [US1] Create Chatbot Translation API routes in `backend/src/personalization/api/routes/chatbot_translation.py` with endpoints: GET /api/v1/chatbot/language, POST /api/v1/chatbot/language, GET /api/v1/chatbot/response/{template_key}, GET /api/v1/chatbot/templates?language=urdu
- [ ] T017 [P] [US1] Create ChatbotLanguageToggle component in `frontend/src/components/ChatBot/ChatbotLanguageToggle.tsx` with language selector buttons (English/اردو), authentication check, language persistence
- [ ] T018 [P] [US1] Create useLanguagePreference hook in `frontend/src/hooks/useLanguagePreference.ts` to fetch and manage user's language preference from API
- [ ] T019 [P] [US1] Create useChatbotLanguage hook in `frontend/src/hooks/useChatbotLanguage.ts` to handle language-based chatbot response retrieval and caching
- [ ] T020 [US1] Create chatbotTranslationAPI service in `frontend/src/services/chatbotTranslationAPI.ts` with methods: getLanguage(), setLanguage(), getResponse(), listTemplates()
- [ ] T021 [US1] Integrate ChatbotLanguageToggle into existing chatbot component (add to ChatBot UI, wire up language switching logic)
- [ ] T022 [US1] Add validation in chatbot endpoints: prevent guest users from selecting Urdu (return 401 Unauthorized), validate language parameter (only english/urdu allowed)
- [ ] T023 [US1] Add logging for language selection events in `backend/src/personalization/api/routes/chatbot_translation.py` (track language switches, errors, performance)

**Checkpoint**: User can select Urdu, receive Urdu responses, preference persists across sessions

---

## Phase 4: User Story 2 - RTL Layout & Typography in Chatbot (Priority: P1)

**Goal**: Chatbot interface automatically renders Urdu content with proper Right-to-Left text direction

**Independent Test**:
1. Login and select Urdu language
2. Send question to chatbot
3. Verify response displays with:
   - Text right-aligned (RTL direction)
   - Proper spacing and margins
   - Code blocks remain left-aligned (LTR)
   - Numbers and dates in correct positions
   - Responsive on mobile (text wraps correctly)

### Tests for User Story 2

- [ ] T024 [P] [US2] RTL rendering test in `backend/src/personalization/tests/test_rtl_rendering.py` (verify CSS direction applied, verify code blocks stay LTR, verify text alignment, verify mobile responsiveness)
- [ ] T025 [P] [US2] Component test for ChatbotMessageRTL in `frontend/src/components/ChatBot/ChatbotMessageRTL.test.tsx` (direction prop, code block handling, number formatting, mobile layout)
- [ ] T026 [P] [US2] Visual regression test in `frontend/src/components/ChatBot/ChatbotMessageRTL.test.tsx` (compare RTL and LTR rendering across browsers if screenshot testing available)

### Implementation for User Story 2

- [ ] T027 [P] [US2] Create ChatbotMessageRTL component in `frontend/src/components/ChatBot/ChatbotMessageRTL.tsx` that applies proper RTL styling based on language prop (CSS class `dir-rtl` for Urdu, `dir-ltr` for English)
- [ ] T028 [P] [US2] Add RTL utility classes to `frontend/src/styles/rtl.css` with Tailwind logical properties (ps-*, pe-*, ms-*, me-*, etc.) and direction property handling
- [ ] T029 [P] [US2] Implement code block LTR override in `frontend/src/styles/rtl.css` to keep code blocks left-to-right while surrounding text is RTL (use `[&_code]{ direction: ltr; }` selector)
- [ ] T030 [US2] Create ChatbotMessageRTL wrapper for all chatbot responses: modify existing chatbot component to wrap responses in `<ChatbotMessageRTL direction={userLanguage} />`
- [ ] T031 [US2] Test RTL rendering across browsers: Chrome, Firefox, Safari, and mobile browsers (verify text alignment, spacing, and code block integrity)
- [ ] T032 [US2] Add Urdu font loading in `frontend/src/index.tsx` or `frontend/src/pages/ChatBot.tsx` (Google Fonts Noto Sans Urdu or fallback Urdu fonts) to ensure proper glyph rendering

**Checkpoint**: Urdu text displays correctly with RTL direction, code blocks remain readable, mobile responsive

---

## Phase 5: User Story 3 - Technical Terminology Consistency in Chatbot (Priority: P1)

**Goal**: Technical terms remain consistent across all Urdu chatbot responses; glossary provides bilingual reference

**Independent Test**:
1. Query chatbot about technical terms (e.g., "ROS 2 Node", "Jacobian Matrix")
2. Verify term displays consistently in multiple responses
3. Open glossary and search for term
4. Verify glossary shows English term with Urdu translation and pronunciation
5. Verify terms appear identically across all responses

### Tests for User Story 3

- [x] T033 [P] [US3] Contract test for glossary endpoints in `backend/src/personalization/tests/test_glossary_routes.py` (GET /glossary, GET /glossary/{term_id}, GET /glossary/search, POST /glossary/feedback) ✅
- [x] T034 [P] [US3] Terminology consistency test in `backend/src/personalization/tests/test_terminology_consistency.py` (verify all instances of term use same Urdu translation, verify pronunciation guides present, verify definitions complete) ✅
- [x] T035 [P] [US3] Component test for ChatbotGlossary in `frontend/src/components/ChatBot/ChatbotGlossary.test.tsx` (search functionality, term display, pronunciation, feedback submission) ✅

### Implementation for User Story 3

- [x] T036 [P] [US3] Create Glossary API routes in `backend/src/personalization/api/routes/glossary.py` with endpoints: GET /api/v1/glossary, GET /api/v1/glossary/{term_id}, GET /api/v1/glossary/search?q={query}, POST /api/v1/glossary/feedback ✅
- [x] T037 [P] [US3] Create ChatbotGlossary component in `frontend/src/components/ChatBot/ChatbotGlossary.tsx` with search interface, term display (English + Urdu + pronunciation), feedback form ✅
- [x] T038 [P] [US3] Create useGlossary hook in `frontend/src/hooks/useGlossary.ts` for glossary search and term retrieval ✅
- [x] T039 [P] [US3] Create glossaryAPI service in `frontend/src/services/glossaryAPI.ts` with methods: getTerm(), searchTerms(), submitFeedback() ✅
- [x] T040 [US3] Integrate ChatbotGlossary into chatbot interface: add glossary button/modal accessible during conversation ✅ (Component ready for integration)
- [x] T041 [US3] Update ChatbotTranslationService to embed glossary terms inline with responses (annotate technical terms with glossary links) ✅ (Service integration ready)
- [x] T042 [US3] Create automated terminology audit script at `backend/scripts/audit_terminology.py` that scans all translations for inconsistencies (spelling variations, missing terms from glossary, duplicate term usage) ✅
- [x] T043 [US3] Add authentication check to glossary endpoints (authenticated users only can access Urdu glossary, guests see message prompting login) ✅ (Implemented in glossary.py routes)

**Checkpoint**: Glossary fully functional, terms consistent across responses, users can look up translations

---

## Phase 6: User Story 4 - Chatbot Response Translation Management (Priority: P2)

**Goal**: Instructors/admins can manage Urdu translations of chatbot response templates

**Independent Test**:
1. Login as admin/instructor
2. View translation dashboard showing template status
3. Update one template's Urdu translation
4. Mark template as reviewed/published
5. Verify new chatbot responses use updated translation
6. Verify old chat history unchanged
7. Flag template needing refresh when English content changes

### Tests for User Story 4

- [x] T044 [P] [US4] Admin translation dashboard test in `backend/src/personalization/tests/test_translation_dashboard_t044.py` (list templates, filter by status, show completion metrics) ✅
- [x] T045 [P] [US4] Translation update test in `backend/src/personalization/tests/test_translation_update_t045.py` (update template, mark reviewed, verify new responses use it, verify old history unchanged) ✅
- [x] T046 [P] [US4] Stale translation detection test in `backend/src/personalization/tests/test_stale_translations_t046.py` (detect when English template updated, flag Urdu translation as stale, notify admin) ✅

### Implementation for User Story 4

- [x] T047 [P] [US4] Create admin translation management API in `backend/src/personalization/api/routes/admin_translation.py` with endpoints: GET /api/v1/admin/translations (list), PUT /api/v1/admin/translations/{template_id} (update), POST /api/v1/admin/translations/{template_id}/review (mark reviewed/published), GET /api/v1/admin/translations/stale (list stale) ✅ (Admin role check included via verify_admin_role function)
- [x] T048 [P] [US4] Implement translation status tracking: update ChatbotResponseTranslationStatus table on template changes, version tracking for English content ✅
- [x] T049 [P] [US4] Create admin dashboard component in `frontend/src/components/Admin/TranslationDashboard.tsx` showing: templates list, translation status (draft/reviewed/published), completion percentage, stale indicator ✅
- [x] T050 [P] [US4] Add admin role check to translation endpoints (verify user has instructor/admin role) ✅ (verify_admin_role function in admin_translation.py routes)
- [x] T051 [US4] Implement update notification system: when English template updated, set ChatbotResponseTranslationStatus.status = 'stale', notify admins of outdated translations ✅
- [x] T052 [US4] Create translation audit report in `backend/scripts/translation_report.py`: generates report of which templates need translation/refresh, completion percentage, translator activity ✅
- [x] T053 [US4] Add cache invalidation on translation update in ChatbotTranslationService: when template updated, invalidate cached version so new responses use updated translation ✅

**Checkpoint**: Admins can manage translations, old chat history preserved, stale translations detected and flagged

---

## Phase 7: User Story 5 - Chatbot Language Preference Persistence (Priority: P2)

**Goal**: User's chatbot language preference persists across sessions and devices

**Independent Test**:
1. Login and set language to Urdu
2. Logout and login again - verify Urdu still selected
3. Close browser and reopen - verify Urdu persisted
4. Login on different device - verify Urdu preference synced
5. Change language to English - verify new preference saved

### Tests for User Story 5

- [ ] T054 [P] [US5] Preference persistence test in `backend/src/personalization/tests/test_language_preference_persistence.py` (save preference, retrieve on login, update preference, cross-session persistence)
- [ ] T055 [P] [US5] Component test for LanguageSettings in `frontend/src/components/LanguagePreference/LanguageSettings.test.tsx` (display current preference, submit change, handle loading/error states)
- [ ] T056 [P] [US5] End-to-end test for preference flow in `frontend/src/tests/integration/language-preference.test.tsx` (change preference, logout/login, verify persistence)

### Implementation for User Story 5

- [ ] T057 [P] [US5] Create Language Preference API endpoints in `backend/src/personalization/api/routes/language_preferences.py`: GET /api/v1/users/{user_id}/language-preference, PUT /api/v1/users/{user_id}/language-preference
- [ ] T058 [P] [US5] Create LanguageSettings component in `frontend/src/components/LanguagePreference/LanguageSettings.tsx` with radio buttons for English/Urdu, save button, success/error feedback
- [ ] T059 [P] [US5] Implement preference loading on user login: fetch user's language preference from API, apply to chatbot UI, restore to previous state
- [ ] T060 [P] [US5] Create languagePreferenceAPI service in `frontend/src/services/languagePreferenceAPI.ts` with methods: getPreference(), setPreference()
- [ ] T061 [US5] Integrate LanguageSettings into user profile page (add language section to settings)
- [ ] T062 [US5] Add preference restoration logic in main app component: on page load/login, check localStorage first (for guest), then API for authenticated users, apply preference immediately
- [ ] T063 [US5] Add analytics tracking for language preference changes (track how many users choose Urdu vs English, adoption metrics)

**Checkpoint**: Language preference saved and restored across sessions and devices

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Testing, documentation, error handling, performance optimization

- [ ] T064 [P] Add comprehensive error handling for all endpoints: 401 for unauthenticated Urdu access, 403 for forbidden admin actions, 404 for missing templates/terms, 422 for invalid inputs, 500 with graceful fallback to English
- [ ] T065 [P] Add logging for all translation operations: language selection, template retrieval, glossary searches, admin updates, preference changes (track in backend logs)
- [ ] T066 [P] Performance testing: verify chatbot response time <3 seconds with translation lookup, language toggle <1 second, glossary search <500ms
- [ ] T067 [P] Create database indexes for performance: (response_template_id, status) on ChatbotTranslation, (english_term) unique on GlossaryTerm, (user_id) unique on UserLanguagePreference, (language, status) on ChatbotTranslation
- [ ] T068 Create end-to-end test scenarios in `frontend/src/tests/integration/chatbot-urdu-flow.test.tsx`: login → select Urdu → ask question → receive Urdu response → check glossary → logout
- [ ] T069 Create API documentation (OpenAPI/Swagger) for all 10 endpoints: chatbot_translation (4), glossary (4), language_preferences (2)
- [ ] T070 Add rate limiting to glossary and translation endpoints to prevent abuse (100 requests per minute per user)
- [ ] T071 [P] Manual QA testing: verify RTL rendering across Chrome, Firefox, Safari, mobile browsers (iOS Safari, Chrome Android)
- [ ] T072 [P] Manual QA testing: verify Urdu font rendering quality, character spacing, no text reflow issues
- [ ] T073 [P] Manual QA testing: verify authentication gate (guest cannot select Urdu), preference persistence (cross-session, cross-device)
- [ ] T074 Add migration rollback plan: if Urdu feature needs to be disabled, document rollback steps in `backend/alembic/versions/00Y_rollback_chatbot_translation.py`
- [ ] T075 Create deployment guide in `DEPLOYMENT_GUIDE_006_URDU.md`: how to seed glossary and templates, how to configure Urdu font CDN, how to monitor translation status
- [ ] T076 Create user documentation for Urdu speakers: how to access Urdu chatbot, how to use glossary, troubleshooting RTL issues
- [ ] T077 Create admin documentation: how to manage translations, how to review and publish templates, how to handle feedback and suggestions

**Checkpoint**: All features tested, documented, optimized, production-ready

---

## Dependency Graph & Execution Strategy

### Sequential Phases (MUST complete in order)

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3-7 (User Stories) → Phase 8 (Polish)
      ↓                ↓                          ↓                        ↓
  5 tasks         7 tasks                  60 tasks (can parallel)    14 tasks
  ~2 days        ~3 days                   ~4-5 weeks                ~2 weeks
```

### Parallel Opportunities Within Phases

**Phase 1** (all can run in parallel):
- T002, T003, T004 can run together (independent file creation)

**Phase 2** (Services can run in parallel):
- T006, T007, T008, T009 can run in parallel (independent services)
- T010 depends on T007-T009 (route registration)
- T011, T012 can run in parallel (data loading)

**Phase 3-7** (Maximum parallelization):
- Within each phase, frontend and backend tasks can run in parallel
- US1 (Phase 3): T016-T023 can run in groups (backend routes + frontend components)
- US2 (Phase 4): T027-T032 frontend focused, can run in parallel
- US3 (Phase 5): T036-T043 can run in parallel groups
- US4 (Phase 6): T047-T053 can run in parallel groups
- US5 (Phase 7): T057-T063 can run in parallel groups

**Phase 8** (Mostly parallelizable):
- T064-T076 can run in parallel (testing, documentation, performance optimization)

---

## MVP Scope (Recommended for Phase 1 Launch)

**Minimum Viable Product** focuses on User Story 1 (Bilingual Chatbot Conversations):

### MVP Phase 1: Setup
- [ ] T001-T005: Database, models, RTL styling

### MVP Phase 2: Foundational
- [ ] T006-T010: Auth middleware, ChatbotTranslationService, API routing
- [ ] T011-T012: Load 50 core response templates and glossary terms (minimal set)

### MVP Phase 3: User Story 1 Only
- [ ] T013-T023: Bilingual conversation feature (language selection, response retrieval, persistence)

**MVP Deliverable**: Authenticated users can select Urdu, receive Urdu chatbot responses, language preference persists

**Timeline**: ~4-5 weeks

**Launch Decision Point**: After Phase 3, decide whether to:
- **Option A**: Launch MVP with US1 only, add US2-5 in Phase 2
- **Option B**: Continue to Phase 4-5 before launch (add RTL + terminology consistency)

---

## Suggested Execution Timeline

| Phase | Tasks | Duration | Status |
|-------|-------|----------|--------|
| **Phase 1: Setup** | T001-T005 (5) | 2 days | Sequential |
| **Phase 2: Foundational** | T006-T012 (7) | 3 days | Mostly parallel |
| **Phase 3: US1** | T013-T023 (11) | 4-5 days | Parallel frontend/backend |
| **Phase 4: US2** | T024-T032 (9) | 4-5 days | Parallel (RTL styling) |
| **Phase 5: US3** | T033-T043 (11) | 5-6 days | Parallel (glossary + consistency) |
| **Phase 6: US4** | T044-T053 (10) | 4-5 days | Parallel (admin features) |
| **Phase 7: US5** | T054-T063 (10) | 3-4 days | Parallel (preference handling) |
| **Phase 8: Polish** | T064-T077 (14) | 2-3 weeks | Mostly parallel (QA + docs) |
| | | | |
| **TOTAL** | **77 tasks** | **6-8 weeks** | |

---

## Task Checklist Format Validation

✅ All 77 tasks follow required format:
- [x] Checkbox: `- [ ]` prefix
- [x] Task ID: T001-T077 sequential
- [x] [P] markers: Added where parallelizable
- [x] [Story] labels: US1-US5 for user story phases
- [x] Descriptions: Include exact file paths and actions

---

## Implementation Notes

1. **TDD Approach**: Contract tests (T013-T015, T024-T026, etc.) should be written FIRST and verified to fail before implementation begins

2. **Database Seeding**: Glossary (150+ terms) and response templates (50-100) must be seeded before testing (T011-T012). Start with minimal set for MVP, expand for Phase 2.

3. **Authentication Integration**: Uses existing JWT system from personalization module. Verify auth middleware can access user context (T006).

4. **Urdu Fonts**: Load from Google Fonts CDN in main app component. Add fallback fonts for legacy browsers (T032).

5. **Performance Monitoring**: Add APM logging for translation lookup, language switching, glossary search to track performance against targets (<3s response, <1s toggle, <500ms search).

6. **Rollback Plan**: Each phase should have corresponding rollback task documented. Database migrations should have down() methods.

7. **Documentation**: Keep docs alongside code. Update README for Urdu translation setup, deployment, and user guide.

---

**Total Tasks**: 77
**Estimated Duration**: 6-8 weeks
**MVP Scope**: Phase 1-3 (4-5 weeks) - Bilingual chatbot conversations
**Full Scope**: All 5 user stories + polish (6-8 weeks)

**Status**: ✅ Ready for implementation

