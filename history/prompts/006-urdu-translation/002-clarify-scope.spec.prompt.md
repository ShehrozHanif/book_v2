---
id: "002"
title: "Clarify Urdu translation scope for RAG chatbot"
stage: "spec"
feature: "006-urdu-translation"
date_iso: "2026-02-10"
surface: "agent"
model: "claude-haiku-4-5-20251001"
branch: "release/003-personalization-complete"
user: "shehroz"
command: "[continuation - scope clarification]"
labels:
  - "urdu-translation"
  - "bilingual"
  - "scope-clarification"
  - "chatbot"
links:
  spec: "/specs/006-urdu-translation/spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "specs/006-urdu-translation/spec.md"
  - "specs/006-urdu-translation/README.md"
  - "specs/006-urdu-translation/checklists/requirements.md"
  - "SPEC_006_URDU_TRANSLATION_SUMMARY.md"
tests_yaml: []
---

## Prompt

Update the Urdu translation specification (006-urdu-translation) to clarify that:
1. Urdu translation is for RAG Chatbot ONLY (not textbook chapters)
2. Authentication is REQUIRED for accessing Urdu translation features
3. Preference storage is hybrid (database for authenticated users, browser storage for guests)

Complete all specification updates to ensure consistency across:
- User Stories 1-5: Refocus from chapter reading to chatbot conversations
- Functional Requirements FR-001 through FR-013: Change context from chapters to chatbot responses
- Key Entities: Replace chapter-based entities with chatbot-response-template entities
- Success Criteria SC-001 through SC-010: Focus on authenticated user chatbot interactions
- Assumptions: Clarify scope is RAG chatbot responses (50-100 templates Phase 1)
- Constraints & Dependencies: Update to reflect response template scope
- Out of Scope: Explicitly exclude textbook chapter translation
- Clarification Decisions Q1-Q3: Reframe for chatbot context

Then commit these changes with appropriate commit message.

## Response

Successfully completed comprehensive specification scope clarification with the following updates:

### User Stories - Refocused from Chapters to Chatbot

**User Story 1**: Changed from "Bilingual Chapter Reading" → "Bilingual Chatbot Conversations"
- Authenticated users ask questions in Urdu, receive Urdu responses
- Maintains conversation history across language switches

**User Story 2**: Changed from generic RTL → "RTL Layout & Typography in Chatbot"
- RTL formatting applies to chatbot responses specifically
- Chat interface elements adapt to Urdu direction

**User Story 3**: Changed from chapter references → "Technical Terminology Consistency in Chatbot"
- Consistent term usage across all chatbot responses
- Referenced examples: chatbot questions about "Jacobian Matrix", "ROS 2 Node", etc.

**User Story 4**: Changed from chapter translation management → "Chatbot Response Template Translation Management"
- Admins manage Urdu translations of response templates (not chapters)
- Phase 1 focuses on core 50-100 response templates

**User Story 5**: Changed from app-wide → "Chatbot Language Preference Persistence"
- Preference applies specifically to authenticated user chatbot interactions
- Persists across sessions and devices for logged-in users

### Functional Requirements - Updated FR-001 through FR-013

**FR-001** (NEW): Authentication required before Urdu access
**FR-002**: Chatbot responses in both English and Urdu
**FR-003**: RTL layout for chatbot responses
**FR-004**: Glossary accessible to authenticated users
**FR-005**: English terminology preservation in chatbot
**FR-006**: Authenticated user language preference persistence
**FR-007**: Code examples in RTL chatbot context
**FR-008**: Translation updates for response templates
**FR-009**: Admin interface for response template translation status
**FR-010**: Mixed-language handling in chatbot
**FR-011**: Pronunciation guides in chatbot responses
**FR-012**: Chatbot history search in both languages
**FR-013**: Correct rendering of dates/numbers in Urdu responses

### Key Entities - Replaced with Chatbot Focus

- ChatbotResponseTemplate (replaced "Chapter")
- ChatbotTranslation (replaced generic "Translation")
- GlossaryTerm (kept, clarified for authenticated users)
- UserLanguagePreference (focused on chatbot language)
- ChatbotResponseTranslationStatus (replaced "TranslationStatus")

### Success Criteria - Updated SC-001 through SC-010

- SC-001: Toggle chatbot language in <1 second (no history loss)
- SC-002: 95%+ RTL rendering on devices
- SC-003: 100% consistent technical terms in chatbot
- SC-004: 100% preference persistence across sessions/devices (auth users)
- SC-005: 99% correct code rendering in RTL chatbot
- SC-006: 90%+ search accuracy across English/Urdu queries
- SC-007: 0% discrepancy in response template translation status
- SC-008: Authenticated Urdu users can ask multiple questions with complete responses
- SC-009: 4.0+ satisfaction rating on chatbot bilingual functionality
- SC-010: 80% of Urdu-speaking users have chatbot default to Urdu on return visits

### Assumptions - 8 Total, Clarified for Chatbot Scope

1. **Scope**: RAG chatbot ONLY (explicitly not chapters)
2. **Authentication**: Required for Urdu access
3. **Translation Quality**: Human translators with robotics expertise
4. **Font Support**: Modern browsers have Urdu support with fallbacks
5. **Response Templates**: 50-100 core templates in Phase 1
6. **Technical Terms**: English terms with Urdu explanations
7. **RTL Implementation**: CSS direction: rtl approach
8. **User Base**: 5-20% Urdu speakers in target markets

### Constraints & Dependencies - Updated

**Technical Constraints**:
- Mobile optimization for RTL
- Efficient translation storage (no duplication)
- No page reload on language switch
- Auth check before Urdu access

**Data Dependencies**:
- 50-100 chatbot response templates Phase 1 (~10,000-20,000 words)
- 150+ glossary terms
- User preference schema extension
- Response template versioning

**External Dependencies**:
- Human translators with robotics knowledge
- Urdu font resources
- Translation management tool (optional)

### Out of Scope - Explicit Clarifications

**EXPLICITLY OUT OF SCOPE**:
- Textbook chapters (Chapters 1-22) - NOT translated
- Textbook learning paths, assessments, practice questions
- Dashboard/analytics translations
- Guest user access to Urdu (auth required)

### Clarification Decisions Q1-Q3 - Updated with Chatbot Context

**Q1: Chatbot Response Translation Rollout Strategy**
- Phase 1 (Month 1-3): 50-100 core response templates
- Phase 2 (Month 3-6): 100+ additional templates
- MVP launch with authenticated user feedback

**Q2: Technical Glossary Access Model**
- Official admin-maintained glossary for authenticated users
- User feedback mechanism (not public forum)
- Quarterly curation process

**Q3: Chatbot Response Terminology Consistency**
- Hybrid: Manual translation + post-translation automated audits
- Per-batch validation (every 50 response templates)
- Glossary database updates from translator discoveries

### Files Updated

1. **specs/006-urdu-translation/spec.md** (460 lines)
   - All 5 user stories refocused
   - All 13 requirements updated for chatbot context
   - Edge cases updated for chatbot scope
   - Assumptions clarified
   - Constraints updated
   - Out of Scope section expanded
   - Q1-Q3 clarifications reframed

2. **specs/006-urdu-translation/README.md**
   - Status updated: "Scope Clarified"
   - Commits pending notation

3. **specs/006-urdu-translation/checklists/requirements.md**
   - Checklist title updated for clarity
   - Updated notation indicating scope clarification

4. **SPEC_006_URDU_TRANSLATION_SUMMARY.md**
   - Status: "Ready for /sp.plan"
   - Feature scope section completely rewritten
   - Translation scope changed from chapters to response templates
   - Glossary scope clarified as authenticated-user-only

### Git Commit

Commit: 129f759
Message: "docs: clarify 006-urdu-translation scope - RAG chatbot only with auth required"

Changes:
- 4 files changed
- 203 insertions
- 181 deletions

## Quality Assessment

✅ **Specification Quality**: PASS (after clarification)
- No implementation details
- Focused on chatbot user value and business needs
- Written for non-technical stakeholders
- All mandatory sections completed with chatbot context

✅ **Requirements Quality**: PASS (after clarification)
- 13 functional requirements are specific and testable
- 10 success criteria are measurable
- All criteria are technology-agnostic
- Acceptance scenarios follow Given-When-Then format

✅ **Scope Clarity**: PASS (fully clarified)
- RAG Chatbot ONLY (not textbook)
- Authentication required
- Response templates as translation units
- Hybrid preference storage

✅ **Readiness for Planning**: PASS
- Specification is now complete with clarified scope
- Ready for `/sp.plan` to create implementation architecture

## Next Steps

1. **Proceed to Planning**: Run `/sp.plan` to create implementation architecture
   - Design chatbot response translation system
   - Plan authentication integration for language access
   - Design RTL rendering for chat responses
   - Plan glossary access control

2. **Ready for Tasks**: After planning, run `/sp.tasks` to break down into actionable work items

3. **Implementation**: Begin Phase 1 with 50-100 core response template translations

## Artifacts

- ✅ Updated `/specs/006-urdu-translation/spec.md` with chatbot scope
- ✅ Updated `/specs/006-urdu-translation/README.md`
- ✅ Updated `/specs/006-urdu-translation/checklists/requirements.md`
- ✅ Updated `/SPEC_006_URDU_TRANSLATION_SUMMARY.md`
- ✅ Git commit: 129f759

**Status**: Specification clarification complete and committed. Ready for `/sp.plan` phase.

