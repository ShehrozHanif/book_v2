# Feature Specification: Urdu Language Translation for RAG Chatbot

**Feature Branch**: `006-urdu-translation`
**Created**: 2026-02-10
**Status**: Draft → Updated with Scope Clarifications (2026-02-10)
**Input**: User description: "Add Urdu translation support for RAG chatbot with login requirement for authenticated users"

**CRITICAL SCOPE CLARIFICATION** (2026-02-10):
- ✅ **Where**: RAG Chatbot ONLY (NOT textbook chapters)
- ✅ **Authentication**: Required login for Urdu translation features
- ✅ **Preference Storage**: Hybrid (database for authenticated users, browser storage for guests)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bilingual Chatbot Conversations (Priority: P1)

An authenticated Urdu-speaking user can ask questions to the RAG chatbot in Urdu and receive responses in Urdu, enabling learning in their native language.

**Why this priority**: Core value - enables Urdu speakers to use the chatbot for learning. Without this, non-English speakers have no way to interact with the system.

**Independent Test**: Can be fully tested by authenticating as a user, selecting Urdu, asking a question, and verifying response is in Urdu with proper RTL formatting. Delivers complete bilingual chat experience.

**Acceptance Scenarios**:

1. **Given** a logged-in user with language set to Urdu, **When** they ask "ROS 2 nay کیا کیا?" (What is ROS 2?), **Then** chatbot responds in Urdu
2. **Given** a user switches from English to Urdu mid-conversation, **When** they ask next question, **Then** response is in Urdu while maintaining conversation history
3. **Given** a user asks a question in Urdu, **When** response includes code examples, **Then** code blocks remain in English with Urdu explanation before/after
4. **Given** a user with Urdu preference logs out, **When** they log back in, **Then** chatbot is still in Urdu

---

### User Story 2 - RTL Layout & Typography in Chatbot (Priority: P1)

The RAG chatbot interface automatically adapts to Right-to-Left (RTL) text direction when displaying Urdu responses, with proper text alignment, spacing, and line breaking for Urdu script (Nastaliq/Naskh).

**Why this priority**: RTL support is critical for Urdu usability in chat. Without it, chatbot responses display incorrectly and are unreadable, defeating the entire feature.

**Independent Test**: Can be fully tested by logging in, selecting Urdu language, asking the chatbot a question, and verifying that the response displays correctly with proper RTL direction. Urdu text should be readable without manual adjustments.

**Acceptance Scenarios**:

1. **Given** Urdu is selected in chatbot, **When** chatbot displays a response with headings, lists, and paragraphs, **Then** all text aligns right-to-left
2. **Given** Urdu chatbot response includes code examples, **When** response is displayed, **Then** code blocks remain LTR while surrounding explanations are RTL
3. **Given** Urdu chatbot text with numbers and dates, **When** displayed, **Then** numbers appear in correct position without text reflow
4. **Given** a mobile device viewing Urdu chatbot responses, **When** text wraps to next line, **Then** word breaks occur correctly for Urdu script

---

### User Story 3 - Technical Terminology Consistency in Chatbot (Priority: P1)

Technical terms (API, algorithm, node, kinematics, ROS 2, etc.) in English remain standardized across all chatbot Urdu responses so learners can recognize terms in original technical literature and documentation.

**Why this priority**: Robotics is a domain where English technical terms are standard globally. Translating these terms inconsistently in chatbot responses confuses learners. Maintaining English terms with Urdu explanations bridges language gap while preserving technical accuracy.

**Independent Test**: Can be fully tested by verifying that when the chatbot responds in Urdu, all technical terms appear consistently and that a technical glossary accessible to authenticated users shows terms in both languages.

**Acceptance Scenarios**:

1. **Given** a user asks chatbot about "Jacobian Matrix" in Urdu, **When** chatbot responds, **Then** the term displays as "Jacobian Matrix" with Urdu explanation nearby
2. **Given** the term "ROS 2 Node" appears in multiple chatbot responses, **When** viewing in Urdu, **Then** all instances display identically
3. **Given** an authenticated user opens the technical glossary, **When** they filter by Urdu, **Then** they see English term with Urdu definition and pronunciation
4. **Given** chatbot explains code with variable named "joint_angle", **When** response is shown in Urdu context, **Then** the variable name remains unchanged

---

### User Story 4 - Chatbot Response Translation Management (Priority: P2)

Instructors can view and manage Urdu translations of RAG chatbot response templates, update translations when content changes, and track translation completeness without disrupting user chat history.

**Why this priority**: As chatbot response templates evolve, their Urdu translations must stay synchronized. This ensures accuracy and consistency but is secondary to having working bilingual chat.

**Independent Test**: Can be fully tested by having an admin update a chatbot response template's Urdu translation and verifying that new responses use the updated translation while existing chat history remains unchanged.

**Acceptance Scenarios**:

1. **Given** a translator updates Urdu translation of a chatbot response template, **When** the update is published, **Then** new chatbot responses use the updated translation
2. **Given** multiple chatbot response templates with Urdu translations, **When** admin views translation dashboard, **Then** they see completion status and can identify templates needing translation
3. **Given** a chatbot response template in English is modified, **When** instructor reviews, **Then** they see notification that Urdu translation may need refresh
4. **Given** a response template marked as translated, **When** translator flags quality issues, **Then** status updates and template is reviewed

---

### User Story 5 - Chatbot Language Preference Persistence (Priority: P2)

Authenticated users can set their preferred language for chatbot interactions once, and the app remembers it across sessions and devices.

**Why this priority**: Improves user experience by reducing friction in chat interactions, but works only if core bilingual chatbot responses work first.

**Independent Test**: Can be fully tested by setting language preference in chatbot settings, logging out, logging back in, and verifying that chatbot uses the selected language.

**Acceptance Scenarios**:

1. **Given** a user sets Urdu as preferred chatbot language, **When** they log out and back in, **Then** chatbot defaults to Urdu
2. **Given** a user set English as preferred chatbot language in session 1, **When** they return 24 hours later, **Then** English is still selected
3. **Given** a user viewing chatbot in Urdu on their first session, **When** they switch to English mid-conversation, **Then** new responses appear in English while chat history remains unchanged
4. **Given** multiple devices, **When** user sets chatbot language to Urdu on Device A, **Then** Device B also defaults to Urdu (requires login on both devices)

---

### Edge Cases

- What happens when a chatbot response is partially translated (some sections in English, some in Urdu)?
- How does the system handle Urdu text mixed with mathematical equations or special symbols in chatbot responses?
- What happens if a user's device doesn't have Urdu font support when chatbot responds in Urdu?
- How are RTL numbers (dates, phone numbers) handled in mixed-language chatbot contexts?
- What happens when chatbot code examples contain English variables but are displayed in RTL context?
- How does chatbot search history work across both English and Urdu queries and responses?
- What happens if chatbot response translation contains errors or inconsistencies?
- How should the system handle guest users (non-authenticated) who want Urdu chatbot responses?
- What happens when user switches language mid-conversation - should previous bot messages retranslate or remain in original language?

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST require user authentication before allowing Urdu language selection in RAG chatbot
- **FR-002**: System MUST support displaying RAG chatbot responses in both English and Urdu with a language toggle mechanism in the chatbot interface
- **FR-003**: System MUST automatically apply Right-to-Left (RTL) layout direction to chatbot responses when Urdu is selected, including proper text alignment, spacing, and element ordering
- **FR-004**: System MUST maintain a technical glossary with 150+ key robotics terms accessible to authenticated users, each with English term, Urdu translation, pronunciation guide, and contextual definition
- **FR-005**: System MUST preserve English technical terminology in all Urdu chatbot responses to maintain consistency with international documentation
- **FR-006**: System MUST persist authenticated user's language preference in database for RAG chatbot and apply it consistently across sessions and devices
- **FR-007**: System MUST ensure code examples in chatbot responses display correctly in RTL context with proper syntax highlighting and without line reflow distortion
- **FR-008**: System MUST support real-time translation updates where changing English source response template triggers notification that Urdu translation needs refresh
- **FR-009**: System MUST provide admin interface to track translation completion status of chatbot response templates and identify templates needing Urdu translation
- **FR-010**: System MUST handle mixed-language content in chatbot responses (English headings with Urdu explanations) without breaking layout or readability
- **FR-011**: System MUST include pronunciation guides (in Latin characters: transliteration) for Urdu technical terms used in chatbot responses
- **FR-012**: System MUST ensure chatbot search/history functionality works across both English and Urdu queries and responses for authenticated users
- **FR-013**: System MUST display dates, numbers, and special characters correctly in Urdu chatbot responses without reversed or corrupted rendering

### Key Entities

- **ChatbotResponseTemplate**: Predefined response template in RAG chatbot with English content, maintained with Urdu version and versioning to track translation status
- **ChatbotTranslation**: Mapping between English chatbot response template and Urdu translation, including metadata (translator, completion date, quality status, version)
- **GlossaryTerm**: Technical robotics term with English definition, Urdu translation, pronunciation guide, and usage examples in both languages (accessible to authenticated users)
- **UserLanguagePreference**: Authenticated user's selected chatbot language (English or Urdu), persisted in database across sessions and devices
- **ChatbotResponseTranslationStatus**: Tracks which response templates are translated to Urdu, which are pending, and identifies stale translations (English updated but Urdu not)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authenticated users can toggle between English and Urdu in chatbot in under 1 second with no conversation history loss
- **SC-002**: Urdu text in chatbot responses displays correctly formatted (RTL direction) on 95%+ of tested devices and browsers with proper font rendering
- **SC-003**: 100% of robotics technical terms (150+ identified terms) appear consistently spelled across all Urdu chatbot responses
- **SC-004**: Authenticated users can set language preference and have it persist across 100% of sessions, including logout/login and device switching
- **SC-005**: Code examples in Urdu chatbot responses render correctly without text reflow or alignment issues in 99% of tested scenarios
- **SC-006**: Chatbot search/history functionality returns results in both English and Urdu with 90%+ relevance accuracy when user searches in their preferred language
- **SC-007**: Translation dashboard shows completion status of chatbot response templates with 0% discrepancy between reported status and actual content availability
- **SC-008**: Authenticated Urdu-speaking users can successfully ask multiple questions to chatbot and receive complete Urdu responses with no language-related barriers
- **SC-009**: Urdu-speaking users report 4.0+ satisfaction rating (out of 5) on chatbot bilingual functionality and language preference persistence
- **SC-010**: 80% of authenticated Urdu speakers who access the chatbot have it default to Urdu language on return visits

---

## Assumptions

1. **Scope**: Urdu translation ONLY applies to RAG chatbot responses, NOT to textbook chapters or other static content
2. **Authentication Required**: Only authenticated (logged-in) users can access Urdu language option in chatbot; non-authenticated guests see English only
3. **Translation Quality**: We assume Urdu translations will be provided by human translators with subject matter expertise in robotics terminology
4. **Font Support**: We assume modern browsers and devices have Urdu font support; for legacy devices, we'll provide fallback fonts
5. **Response Templates**: Chatbot will have predefined response templates (initial scope: 50-100 templates) that will be translated to Urdu
6. **Technical Terminology**: We assume technical terms should remain in English with Urdu explanations rather than coined Urdu equivalents
7. **RTL Implementation**: We assume CSS `direction: rtl` and logical properties will be used for RTL support rather than flipping
8. **User Base**: We assume a significant portion of chatbot users are Urdu speakers (5-20% based on target markets: Pakistan, Urdu diaspora)

---

## Constraints & Dependencies

### Technical Constraints
- Must work on mobile devices (where RTL layout is particularly important)
- Chatbot translations must be stored efficiently without duplicating entire response template data
- Language switching must not require page reload or lose chat history
- RTL support must be compatible with existing code highlighting library in chatbot responses
- Authentication system must be checked before allowing Urdu language selection

### Data Dependencies
- Requires translation of initial 50-100 chatbot response templates - estimated 10,000-20,000 words
- Requires glossary creation with 150+ technical terms and definitions (accessible to authenticated users)
- Requires user preference schema extension (minimal database change to user profile)
- Requires chatbot response template versioning to track English/Urdu translation status

### External Dependencies
- Urdu translator(s) with robotics domain knowledge
- Urdu font resources (may use Google Fonts Noto Sans Urdu or similar)
- Possibly translation management tool (e.g., Crowdin) for collaborative translation workflow

---

## Out of Scope

- **EXPLICITLY OUT OF SCOPE**: Urdu translation of textbook chapters (Chapters 1-22) - this feature applies ONLY to RAG chatbot responses
- **EXPLICITLY OUT OF SCOPE**: Urdu translation of textbook learning paths, assessments, practice questions, or dashboard content
- Voice/audio versions of Urdu chatbot responses (can be future phase)
- Real-time collaborative translation interface (use external tools)
- Automatic machine translation (using OpenAI/Google Translate) - will use human translation for quality
- Translate user-generated content (forum posts, comments, etc.)
- Support for other languages besides English and Urdu in chatbot
- Urdu keyboard layout assistance or IME integration
- Cultural adaptation beyond language (e.g., changing examples for Urdu context)
- Guest user access to Urdu language option (authentication required)

---

## Clarification Decisions

### Q1: Chatbot Response Translation Rollout Strategy - DECIDED ✅

**Decision: Launch MVP with initial 50-100 chatbot response templates, expand to 200+ templates incrementally**

**Rationale**:
- **Faster Time to Market**: Urdu-speaking users get access to core chatbot responses within 2-3 months instead of waiting for all templates
- **User Feedback Loop**: Real users provide feedback on RTL layout, terminology, and translation quality on live templates before translating all responses
- **Focused Scope**: Focus on most-used response templates (general questions, common robotics topics, navigation help)
- **Resource Efficiency**: Translators can work on additional templates while Phase 1 is live and feedback is collected
- **Better UX**: Clear scope (50-100 templates available, more coming) is better than "Coming Soon" placeholders

**Implementation Timeline**:
- Phase 1 (Month 1-3): Translate 50-100 core chatbot response templates (~10,000-20,000 words)
- Launch Phase 1 with core chatbot responses in Urdu for authenticated users
- Phase 2 (Month 3-6): Translate additional 100+ response templates in parallel with user feedback
- Launch Phase 2 with comprehensive chatbot response coverage

---

### Q2: Technical Glossary Access Model - DECIDED ✅

**Decision: Official admin-maintained glossary accessible to authenticated Urdu-speaking users**

**Rationale**:
- **Quality First**: Official glossary maintained by instructors and expert translators ensures consistency and accuracy
- **Authenticated Users Only**: Glossary accessible to logged-in users, supporting their Urdu chatbot experience
- **Community Engagement**: Authenticated users can suggest glossary additions through feedback mechanism (not public forum)
- **Scalability**: Users can request new terms or suggest improvements via authenticated feedback channel
- **Curation Process**: Admins review suggestions and update official glossary quarterly
- **Knowledge Crowd-Sourcing**: Leverage community expertise from authenticated user base
- **Low Moderation Burden**: Feedback mechanism is non-destructive; only curated items affect official glossary

**Implementation**:
- **Official Glossary** (admin-maintained):
  - 150+ core robotics terms
  - Maintained by instructors and translators
  - Versioned and tested before updates
  - Single source of truth
  - Accessible to all authenticated users in both English and Urdu

- **User Feedback Mechanism** (optional authenticated user contributions):
  - Authenticated users can suggest new glossary terms
  - Users can request terminology clarifications
  - Users can suggest alternative translations
  - Admins review quarterly and update official glossary
  - Feedback helps improve terminology coverage

---

### Q3: Chatbot Response Terminology Consistency - DECIDED ✅

**Decision: Hybrid approach (Manual translation with post-translation automated audits)**

**Rationale**:
- **Translator Expertise**: Initial translation by human experts with style guide ensures nuance and context-awareness
- **Automated Quality Checks**: Post-translation scans flag terminology inconsistencies automatically before publication
- **Error Prevention**: Catches mistakes like spelling variations, inconsistent transliterations, missed terms across all response templates
- **Training & Improvement**: Feedback helps translators improve consistency for Phase 2 templates
- **Efficiency Balance**: Manual translation isn't slowed down by tool setup; validation happens in review phase

**Implementation Process**:
1. **Pre-Translation**: Provide translators with:
   - Style guide (transliteration rules, formatting standards for chatbot context)
   - Glossary database (150+ terms with preferred translations)
   - Context examples for technical terms as they appear in chatbot responses

2. **Translation Phase**: Translators work efficiently without tool friction
   - Can reference glossary as needed
   - Follow style guide for consistency
   - Focus on quality and chatbot context

3. **Post-Translation Audits** (before publication):
   - Automated scan for terminology inconsistencies across all response templates
   - Flag spelling variations (e.g., "Jakobian" vs "Jacobian" transliterations)
   - Identify missed glossary terms
   - Report similar-meaning terms used differently in different responses

4. **Quality Review**: Human review of automated findings
   - Resolve flagged inconsistencies
   - Approve automated suggestions
   - Update glossary database with new terms discovered during translation

5. **Publication**: Publish only after audit clearance

**Tools & Timeline**:
- Use glossary database (built into CMS or translation management tool)
- Automated scanning: 1-2 days per batch of 50 response templates after translation completes
- Quality review: 3-5 days per batch of 50 response templates
- Total validation: ~4-7 days per batch before publication

