# Feature Specification: Urdu Language Translation & Bilingual Support

**Feature Branch**: `006-urdu-translation`
**Created**: 2026-02-10
**Status**: Draft
**Input**: User description: "Add Urdu translation support for the textbook with bilingual reading experience, RTL layout support, and technical terminology handling"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bilingual Chapter Reading (Priority: P1)

A user learning robotics in Urdu can read the same chapter content in both English and Urdu side-by-side or toggle between languages without losing their place or progress.

**Why this priority**: This is the core value proposition. Without bilingual reading, the feature provides no value. It enables non-English speakers to learn while gradually building English proficiency.

**Independent Test**: Can be fully tested by loading a chapter, toggling language, and verifying that content switches while maintaining scroll position and progress tracking. Delivers complete bilingual learning experience.

**Acceptance Scenarios**:

1. **Given** a user is on Chapter 1 in English, **When** they click language toggle, **Then** the entire chapter content switches to Urdu with maintained scroll position
2. **Given** a user is halfway through reading in Urdu, **When** they switch to English, **Then** they return to the same scroll position
3. **Given** a user switches languages, **When** they navigate to dashboard, **Then** their language preference is remembered
4. **Given** a user reads a chapter in Urdu, **When** they take a practice test, **Then** practice questions are also in Urdu

---

### User Story 2 - RTL Layout & Typography (Priority: P1)

The interface automatically adapts to Right-to-Left (RTL) text direction when viewing Urdu content, with proper text alignment, spacing, and line breaking for Urdu script (Nastaliq/Naskh).

**Why this priority**: RTL support is critical for Urdu usability. Without it, Urdu text displays incorrectly and is unreadable, defeating the entire feature.

**Independent Test**: Can be fully tested by switching to Urdu and verifying that all UI elements (paragraphs, lists, headings, code blocks) display correctly with RTL direction. Urdu text should be readable without manual adjustments.

**Acceptance Scenarios**:

1. **Given** Urdu is selected, **When** displaying a chapter with headings, lists, and paragraphs, **Then** all text aligns right-to-left
2. **Given** Urdu content with code examples, **When** code is displayed, **Then** code blocks remain LTR while surrounding text is RTL
3. **Given** Urdu text with numbers and dates, **When** displayed, **Then** numbers appear in correct position without text reflow
4. **Given** a mobile device viewing Urdu content, **When** text wraps to next line, **Then** word breaks occur correctly for Urdu

---

### User Story 3 - Technical Terminology Consistency (Priority: P1)

Technical terms (API, algorithm, node, kinematics, etc.) in English remain standardized across all Urdu translations so learners can recognize terms in original technical literature and documentation.

**Why this priority**: Robotics is a domain where English technical terms are standard globally. Translating these terms inconsistently confuses learners. Maintaining English terms with Urdu explanations bridges language gap while preserving technical accuracy.

**Independent Test**: Can be fully tested by verifying that all glossary terms appear consistently in both languages and that a terminology reference page exists in both languages.

**Acceptance Scenarios**:

1. **Given** a technical term "Jacobian Matrix" appears in Chapter 12, **When** viewing in Urdu, **Then** the term displays as "Jacobian Matrix" with Urdu explanation nearby
2. **Given** the term "ROS 2 Node" appears 15 times in Chapter 6, **When** viewing in Urdu, **Then** all 15 instances display identically
3. **Given** a user opens the technical glossary, **When** they filter by Urdu, **Then** they see English term with Urdu definition and pronunciation
4. **Given** a code variable named "joint_angle", **When** code examples are shown in Urdu context, **Then** the variable name remains unchanged

---

### User Story 4 - Translation Management & Updates (Priority: P2)

Instructors and translators can view which chapters are translated, update translations when content changes, and track translation completeness without breaking existing user progress.

**Why this priority**: As textbook content evolves, translations must stay synchronized. This ensures accuracy but is secondary to having working bilingual reading.

**Independent Test**: Can be fully tested by having an admin update a translation and verifying that existing users see the update while maintaining their progress records.

**Acceptance Scenarios**:

1. **Given** a translator updates Chapter 8 Urdu content, **When** the update is published, **Then** new users see the updated version while existing progress is preserved
2. **Given** 18 chapters translated and 4 pending, **When** admin views translation dashboard, **Then** they see clear completion status and can filter by language
3. **Given** Chapter 15 English content updated, **When** instructor reviews, **Then** they see notification that Urdu translation needs refresh
4. **Given** a chapter marked as translated, **When** translator flags it as incomplete due to quality issues, **Then** status updates and users are notified

---

### User Story 5 - Language Preference Persistence (Priority: P2)

Users can set their preferred language once, and the app remembers it across sessions, chapters, and features (dashboard, practice, achievements).

**Why this priority**: Improves user experience by reducing friction, but works only if core bilingual reading works first.

**Independent Test**: Can be fully tested by setting language preference, logging out, logging back in, and verifying that all pages load in the selected language.

**Acceptance Scenarios**:

1. **Given** a user sets Urdu as preferred language, **When** they log out and back in, **Then** all content loads in Urdu
2. **Given** a user set English as preferred in session 1, **When** they open the app 24 hours later, **Then** English is still selected
3. **Given** a user viewing dashboard in Urdu, **When** they navigate to practice section, **Then** practice questions are also in Urdu
4. **Given** multiple devices, **When** user sets language on Device A to Urdu, **Then** Device B also reflects Urdu preference

---

### Edge Cases

- What happens when a chapter is partially translated (some sections in English, some in Urdu)?
- How does the system handle Urdu text mixed with mathematical equations or special symbols?
- What happens if a user's device doesn't have Urdu font support?
- How are RTL numbers (dates, phone numbers) handled in mixed-language contexts?
- What happens when code examples contain English variables but are displayed in RTL context?
- How does search work across both English and Urdu content?
- What happens if translation contains errors or inconsistencies?

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support displaying chapter content in both English and Urdu with a language toggle mechanism accessible from every page
- **FR-002**: System MUST automatically apply Right-to-Left (RTL) layout direction when Urdu is selected, including proper text alignment, spacing, and element ordering
- **FR-003**: System MUST maintain a technical glossary with 150+ key robotics terms, each with English term, Urdu translation, pronunciation guide, and contextual definition
- **FR-004**: System MUST preserve English technical terminology in all Urdu translations to maintain consistency with international documentation
- **FR-005**: System MUST persist user's language preference in database and apply it across all features (chapters, dashboard, practice, achievements, profile)
- **FR-006**: System MUST ensure code examples display correctly in RTL context with proper syntax highlighting and without line reflow distortion
- **FR-007**: System MUST support real-time translation updates where changing English source content triggers notification that Urdu translation needs refresh
- **FR-008**: System MUST provide admin interface to track translation completion status per chapter and identify chapters needing translation
- **FR-009**: System MUST handle mixed-language content (English headings with Urdu explanations) without breaking layout or readability
- **FR-010**: System MUST include pronunciation guides (in Latin characters: transliteration) for Urdu technical terms to aid pronunciation
- **FR-011**: System MUST ensure search functionality works across both English and Urdu content, finding results in both languages
- **FR-012**: System MUST maintain all user progress and achievement records regardless of language selection, with no data loss on language switch
- **FR-013**: System MUST display dates, numbers, and special characters correctly in Urdu context without reversed or corrupted rendering

### Key Entities

- **Chapter**: Document containing learning content, maintainedfor both English and Urdu versions with versioning to track translation status
- **Translation**: Mapping between English source content and Urdu translation, including metadata (translator, completion date, quality status)
- **GlossaryTerm**: Technical robotics term with English definition, Urdu translation, pronunciation guide, and usage examples in both languages
- **UserLanguagePreference**: User's selected language persisted with session and device information
- **TranslationStatus**: Tracks which chapters are translated, which are pending, and identifies stale translations (English updated but Urdu not)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can toggle between English and Urdu content on any chapter in under 1 second with no data loss or scroll position disruption
- **SC-002**: Urdu text displays correctly formatted (RTL direction) on 95%+ of tested devices and browsers with proper font rendering
- **SC-003**: 100% of robotics technical terms (150+ identified terms) appear consistently spelled and positioned across all Urdu translations
- **SC-004**: Users can set language preference and have it persist across 100% of navigation paths (chapters, dashboard, practice, settings, logout/login)
- **SC-005**: Code examples in Urdu chapters render correctly without text reflow or alignment issues in 99% of tested scenarios
- **SC-006**: Search functionality returns relevant results in both English and Urdu with 90%+ relevance accuracy when user searches in their preferred language
- **SC-007**: Translation dashboard shows completion status with 0% discrepancy between reported status and actual content availability
- **SC-008**: New users starting in Urdu can complete Chapters 1-5 practice sections with no language-related barriers or missing content
- **SC-009**: Urdu speaking users report 4.0+ satisfaction rating (out of 5) on bilingual readability and language preference functionality
- **SC-010**: 80% of Urdu learners complete their first chapter compared to overall user completion rate

---

## Assumptions

1. **Translation Quality**: We assume Urdu translations will be provided by human translators with subject matter expertise in robotics terminology
2. **Font Support**: We assume modern browsers and devices have Urdu font support; for legacy devices, we'll provide fallback fonts
3. **Scope of Translation**: Modules 2-4 (Chapters 6-22) will be translated initially; Module 1 can be added in Phase 2
4. **Technical Terminology**: We assume technical terms should remain in English with Urdu explanations rather than coined Urdu equivalents
5. **RTL Implementation**: We assume CSS `direction: rtl` and logical properties will be used for RTL support rather than flipping
6. **User Base**: We assume a significant portion of learners are Urdu speakers (5-20% based on target markets: Pakistan, Urdu diaspora)

---

## Constraints & Dependencies

### Technical Constraints
- Must work on mobile devices (where RTL layout is particularly important)
- Translations must be stored efficiently without duplicating entire chapter data
- Language switching must not require page reload
- RTL support must be compatible with existing code highlighting library

### Data Dependencies
- Requires translation of 17 chapters (Chapters 6-22) - estimated 100,000+ words
- Requires glossary creation with 150+ technical terms and definitions
- Requires user preference schema extension (minimal database change)

### External Dependencies
- Urdu translator(s) with robotics domain knowledge
- Urdu font resources (may use Google Fonts Noto Sans Urdu or similar)
- Possibly translation management tool (e.g., Crowdin) for collaborative translation workflow

---

## Out of Scope

- Voice/audio versions of Urdu content (can be future phase)
- Real-time collaborative translation interface (use external tools)
- Automatic machine translation (using OpenAI/Google Translate) - will use human translation for quality
- Translate user-generated content (forum posts, comments, etc.)
- Support for other languages besides English and Urdu
- Urdu keyboard layout assistance or IME integration
- Cultural adaptation beyond language (e.g., changing examples for Urdu context)

---

## Open Questions

[NEEDS CLARIFICATION: Should chapters be translated all at once before launch, or can we launch with partial translation (e.g., first 5 chapters) and add others incrementally? This affects MVP scope and launch timeline.]

[NEEDS CLARIFICATION: Should the glossary support user-contributed terms and translations, or should it be admin-only? This affects community engagement but adds moderation complexity.]

[NEEDS CLARIFICATION: What is the acceptable level of Urdu text inconsistency (e.g., different transliterations of the same term)? Should we use automated terminology checks or rely on translator consistency?]

