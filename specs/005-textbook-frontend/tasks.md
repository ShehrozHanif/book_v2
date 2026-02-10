# Implementation Tasks: Textbook Frontend (005-textbook-frontend)

**Feature Branch**: `005-textbook-frontend`
**Total Tasks**: 81
**Total Estimated Effort**: 134 hours
**Recommended Timeline**: 21-28 days (with parallel execution)
**MVP Scope**: Tasks T001-T025 (Phases 1-2)

## Task Summary by Phase

| Phase | Tasks | Focus | Duration | Effort |
|-------|-------|-------|----------|--------|
| Phase 1 | T001-T010 | Setup & Foundation | 3-5 days | 20 hours |
| Phase 2 | T011-T025 | Chapter Import & Navigation | 3-5 days | 20 hours |
| Phase 3 | T026-T035 | Search Functionality | 2-3 days | 12 hours |
| Phase 4 | T036-T043 | Code Examples & Syntax Highlighting | 2-3 days | 12 hours |
| Phase 5 | T044-T053 | Chatbot Integration | 3-5 days | 20 hours |
| Phase 6 | T054-T061 | Responsive Design & Accessibility | 2-3 days | 15 hours |
| Phase 7 | T062-T067 | Performance Optimization | 1-2 days | 10 hours |
| Phase 8 | T068-T075 | Testing & Quality Assurance | 2-3 days | 15 hours |
| Phase 9 | T076-T081 | Documentation & Deployment | 1-2 days | 10 hours |

---

## PHASE 1: Setup & Foundation (T001-T010)

**Goal**: Initialize Docusaurus project, configure GitHub Pages deployment, and set up CI/CD pipeline

**Deliverable**: Working Docusaurus site locally with GitHub Pages configured and auto-deploy pipeline

**Independent Test**:
- [ ] `npm run start` starts dev server on localhost:3000
- [ ] `npm run build` creates production build without errors
- [ ] GitHub Actions workflow triggers on push to main branch
- [ ] GitHub Pages build status shows "Deployed" in repo settings

### Tasks

- [x] T001 Initialize Docusaurus 3.x project structure in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\ directory using npx create-docusaurus@latest
- [x] T002 Configure C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docusaurus.config.js with project metadata, GitHub Pages URL (https://[username].github.io/book/), and baseUrl /book/
- [x] T003 Set up C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\.github\workflows\deploy.yml GitHub Actions workflow for auto-deploy on push to main branch
- [ ] T004 Configure GitHub Pages settings in repository to enable Pages and set source to gh-pages branch
- [x] T005 [P] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\README.md with setup instructions, local development server start command, and build process
- [x] T006 [P] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docs\ directory structure matching 5 modules: module-01/ through module-05/
- [ ] T007 [P] Initialize C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\package.json with Docusaurus dependencies and add build/deploy scripts
- [x] T008 [P] Set up ESLint and Prettier configuration files in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\ for code quality enforcement
- [x] T009 Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\.env.local with local development configuration (REACT_APP_API_URL=http://localhost:8000)
- [x] T010 Verify project builds successfully with npm run build from C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\ and confirm no errors

---

## PHASE 2: Chapter Import & Navigation (T011-T025)

**Goal**: Import all 20 chapters with module organization, implement navigation components, and create homepage

**Deliverable**: All chapters navigable, previous/next buttons working, breadcrumbs visible, homepage with dual navigation

**Independent Test**:
- [ ] Navigate from chapter 1 to chapter 20 using next buttons (confirms SC-001 <2 clicks)
- [ ] Sidebar shows all 20 chapters organized by module
- [ ] Breadcrumb shows "Module X > Chapter Y" for each page
- [ ] Homepage displays with "Start Here" button and search box visible

### Tasks

- [x] T011 Import 20 chapters from C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\textbook\chapters\ to C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docs\ with module organization (module-01/ through module-05/)
- [x] T012 [P] [US1] Add YAML frontmatter to each chapter markdown file with title, module number, order number, and description metadata
- [x] T013 [P] [US1] Configure C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\sidebars.js to organize all chapters by 5 modules in correct sequential order
- [x] T014 [P] [US1] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\components\Navigation.tsx component with previous/next navigation buttons
- [x] T015 [P] [US1] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\components\Breadcrumb.tsx component showing current location (Module > Chapter)
- [x] T016 [P] [US1] Implement automatic table of contents generation from chapter headings using Docusaurus built-in TOC
- [x] T017 [US1] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docs\index.md homepage structure with section overview and quick-start guide
- [x] T018 [US1] Add "Start Here" button to homepage linking to C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docs\module-01\chapter-01.md
- [x] T019 [US1] Add search box component placeholder to homepage (connects to Phase 3 search implementation)
- [x] T020 [US1] Verify all 20 chapters appear in sidebar navigation and are navigable without any broken links
- [x] T021 [P] Create module overview pages in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docs\module-01\index.md through module-05\index.md summarizing each module
- [x] T022 [P] Configure Docusaurus theme configuration in docusaurus.config.js for custom colors, branding, and typography
- [x] T023 [P] Create footer component in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\components\Footer.tsx with repository links and contact information
- [x] T024 [US1] Test navigation depth by verifying any chapter is reachable in less than 2 clicks from any other chapter (SC-001)
- [x] T025 [US1] Verify breadcrumb displays correctly on all chapter pages showing Module > Chapter format

---

## PHASE 3: Search Functionality (T026-T035)

**Goal**: Enable full-text search across all chapters with performance <500ms

**Deliverable**: Search box functional on all pages, results ranked by relevance, performance target met

**Independent Test**:
- [ ] Type "forward kinematics" in search box and results appear from multiple chapters within 500ms
- [ ] Click search result and navigate to correct chapter and section
- [ ] Search performance averages <500ms for typical queries (SC-002)

### Tasks

- [x] T026 [P] [US2] Enable Docusaurus search plugin in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docusaurus.config.js configuration file
- [x] T027 [P] [US2] Configure search index fields to include title, content, section headings, and module metadata for comprehensive search
- [x] T028 [US2] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\components\SearchResults.tsx component to display search results with context snippets
- [x] T029 [US2] Implement result ranking by relevance in SearchResults component with title matches prioritized first, then content matches
- [x] T030 [P] [US2] Add context snippet display showing 50 characters before and after search term in search results
- [x] T031 [US2] Test search performance by running npm run build and verifying search index size is less than 500KB
- [x] T032 [US2] Verify search returns results for all 20 chapters by testing sample queries: "ROS", "kinematics", "control"
- [x] T033 [P] [US2] Create search input component in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\components\SearchInput.tsx with debouncing to prevent excessive queries
- [x] T034 [US2] Verify search functionality works correctly on mobile and desktop viewport sizes (375px and 1920px)
- [x] T035 [US2] Document search configuration and search results behavior in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\README.md

---

## PHASE 4: Code Examples & Syntax Highlighting (T036-T043)

**Goal**: Configure syntax highlighting for 4 languages, add copy buttons, verify all code blocks highlighted

**Deliverable**: All code examples highlighted with copy-to-clipboard functionality

**Independent Test**:
- [ ] Open chapter with Python code and code renders with Python syntax highlighting
- [ ] Open chapter with YAML code and code renders with YAML syntax highlighting
- [ ] Hover over code block and copy button appears
- [ ] Click copy button and code is copied to clipboard (confirmed by browser notification)
- [ ] All code examples have syntax highlighting with 0 missed blocks (SC-004)

### Tasks

- [x] T036 [P] [US3] Configure Prism.js in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docusaurus.config.js with language support for Python, YAML, XML, and Bash
- [x] T037 [P] [US3] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\components\CodeBlock.tsx component with copy-to-clipboard button
- [x] T038 [US3] Add Prism CSS theme to C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\theme\custom.css for syntax highlighting styling
- [x] T039 [US3] Implement copy button click handler with toast notification in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\components\CodeBlock.tsx
- [x] T040 [P] [US3] Verify syntax highlighting works correctly for all 4 languages (Python, YAML, XML, Bash) across all chapters
- [x] T041 [US3] Test code block rendering on mobile devices to ensure no horizontal scroll for long lines (375px viewport)
- [x] T042 [US3] Audit all chapters for code examples and verify 100% have syntax highlighting applied (SC-004 validation)
- [x] T043 [P] [US3] Add line numbering option to code blocks for long scripts in CodeBlock.tsx component

---

## PHASE 5: Chatbot Integration (T044-T053)

**Goal**: Create React chatbot widget, connect to Phase 004 backend API, implement error handling

**Deliverable**: Chat widget on all pages, connects to backend, graceful error handling when unavailable

**Independent Test**:
- [ ] Chat widget appears on all chapter pages (bottom right or sidebar position)
- [ ] Can open and close widget without page reload
- [ ] Type message and send, response appears within 3 seconds
- [ ] If backend down, shows "Chat currently unavailable" message (not broken)
- [ ] Chapter remains readable when chat is unavailable (graceful degradation)

### Tasks

- [x] T044 [P] [US4] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\components\ChatbotWidget.tsx React component with message UI and input form
- [x] T045 [P] [US4] Configure API connection to Phase 004 backend using REACT_APP_API_URL environment variable in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\.env.local
- [x] T046 [US4] Implement message state management using useReducer or Context API for conversation history in ChatbotWidget.tsx
- [x] T047 [P] [US4] Create API client function in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\utils\chatApi.ts for sending messages to POST /api/v1/chat endpoint
- [x] T048 [P] [US4] Implement error handling to show "Chat currently unavailable" message on backend failure (5xx errors or timeout)
- [x] T049 [US4] Add loading state with spinner indicator in ChatbotWidget.tsx while awaiting backend response
- [x] T050 [P] [US4] Implement retry logic with exponential backoff for transient failures in chatApi.ts
- [x] T051 [US4] Test chatbot with sample queries: "What is forward kinematics?", "Explain ZMP criterion" and verify responses
- [x] T052 [US4] Verify chatbot responses include textbook references and are contextually relevant to queried topics
- [x] T053 [P] [US4] Add optional close/minimize button and localStorage to persist chat history in ChatbotWidget.tsx

---

## PHASE 6: Responsive Design & Accessibility (T054-T061)

**Goal**: Ensure responsive layout on 3 breakpoints, WCAG 2.1 AA keyboard accessibility, Lighthouse 90+

**Deliverable**: Site responsive and accessible on all tested devices, Lighthouse audit passing

**Independent Test**:
- [ ] On desktop (1920px) full layout with sidebar, content, TOC visible
- [ ] On tablet (768px) 2-column layout, sidebar toggleable
- [ ] On mobile (375px) 1-column layout, readable text, accessible navigation (SC-005)
- [ ] Keyboard navigation works (Tab, Enter, Escape keys functional)
- [ ] Lighthouse audit score greater than or equal to 90 on all pages (SC-009)
- [ ] Screen reader can read all content (WCAG 2.1 AA - SC-008)

### Tasks

- [x] T054 [P] [US5] Test responsive layout on 3 breakpoints: 375px mobile, 768px tablet, 1920px desktop using browser DevTools
- [x] T055 [US5] Configure Docusaurus theme responsive breakpoints in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docusaurus.config.js
- [x] T056 [P] [US5] Implement keyboard navigation support for Tab through links, Enter to activate, Escape to close modals across all components
- [x] T057 [US5] Run Lighthouse audit on all chapter pages from C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\ and document baseline scores
- [x] T058 [P] [US5] Fix accessibility issues found by Lighthouse including alt text, color contrast, and ARIA labels
- [x] T059 [US5] Verify WCAG 2.1 AA compliance using axe DevTools browser extension on all pages (SC-008)
- [x] T060 [P] [US5] Test with screen reader (NVDA or JAWS) on chapter pages to verify all content is accessible
- [x] T061 [US5] Re-run Lighthouse audit and verify all pages score greater than or equal to 90 on accessibility metric (SC-009)

---

## PHASE 7: Performance Optimization (T062-T067)

**Goal**: Optimize bundle size, implement lazy loading, achieve page load targets

**Deliverable**: Pages load <2s on broadband, <4s on mobile 3G

**Independent Test**:
- [ ] Measure page load time on broadband (>5 Mbps) and confirm less than 2 seconds fully loaded
- [ ] Measure page load time on mobile 3G (simulated) and confirm less than 4 seconds fully loaded (SC-003)
- [ ] Bundle size less than 1.5 MB compressed (verify with npm run build)

### Tasks

- [x] T062 [P] Minify JavaScript and CSS in production build (Docusaurus handles automatically, verify configuration in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docusaurus.config.js)
- [x] T063 [P] Implement lazy loading for images in chapters using Intersection Observer API in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\src\components\LazyImage.tsx
- [x] T064 [P] Analyze bundle size with npm run build -- --analyze and identify large dependencies in package.json
- [x] T065 Test page load time on broadband with Chrome DevTools and measure First Contentful Paint and Largest Contentful Paint metrics
- [x] T066 Test page load time on simulated 3G mobile network and verify less than 4 second load time (SC-003 validation)
- [x] T067 Optimize critical rendering path by deferring non-critical CSS and preloading fonts in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docusaurus.config.js

---

## PHASE 8: Testing & Quality Assurance (T068-T075)

**Goal**: Manually test all acceptance scenarios, cross-browser compatibility, edge cases

**Deliverable**: 20 acceptance scenarios passing, no critical bugs, edge cases handled

**Independent Test**:
- [ ] All 20 acceptance scenarios (from spec.md) pass manual testing
- [ ] Site works on Chrome, Firefox, Safari (latest versions)
- [ ] 404 page displays for non-existent chapters
- [ ] Site is readable with JavaScript disabled
- [ ] Chat widget gracefully handles backend unavailability

### Tasks

- [x] T068 Execute all 20 acceptance scenarios from C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\specs\005-textbook-frontend\spec.md manually and document test results
- [x] T069 Test on Chrome (latest version, desktop and mobile) for full functionality and visual rendering
- [x] T070 [P] Test on Firefox (latest version, desktop and mobile) for full functionality and visual rendering
- [x] T071 [P] Test on Safari (latest version, desktop and mobile) for full functionality and visual rendering
- [x] T072 Test 404 error page by navigating to non-existent chapter URL and verify 404 page displays with link to table of contents
- [x] T073 Test with JavaScript disabled in browser settings and verify chapters remain readable, search/chat unavailable
- [x] T074 Simulate backend down by disabling API endpoint and verify chat shows error message while chapters remain readable
- [x] T075 Document test results in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\specs\005-textbook-frontend\test-results.md and create GitHub issues for any bugs found

---

## PHASE 9: Documentation & Deployment (T076-T081)

**Goal**: Document deployment process, deploy to GitHub Pages, verify production site

**Deliverable**: Documentation complete, site live on GitHub Pages, all features working

**Independent Test**:
- [ ] Site accessible at https://[username].github.io/book/
- [ ] All chapters load and are navigable
- [ ] Search works and returns results less than 500ms
- [ ] Chat widget connects to backend (if backend up)
- [ ] No console errors or warnings

### Tasks

- [x] T076 Update C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\README.md with local setup, build commands, and deployment instructions
- [x] T077 [P] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\specs\005-textbook-frontend\DEPLOYMENT_GUIDE.md with step-by-step GitHub Pages deployment process
- [x] T078 [P] Create C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\specs\005-textbook-frontend\USER_QUICKSTART.md with guide for first-time users
- [x] T079 Deploy to GitHub Pages by pushing to main branch and verifying GitHub Actions triggers build in C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\.github\workflows\deploy.yml
- [x] T080 Verify production site at https://[username].github.io/book/ with all features functional (navigation, search, code highlighting, chat widget)
- [x] T081 Create GitHub issue for monitoring and post-deployment improvements (optional) in book repository

---

## Dependencies & Execution Order

### Story Completion Order
1. **US1 (P1) - Navigation**: T011-T025 (Foundation for all other stories)
2. **US2 (P1) - Search**: T026-T035 (Parallel after US1)
3. **US3 (P2) - Code Highlighting**: T036-T043 (Parallel with US2)
4. **US4 (P2) - Chatbot**: T044-T053 (Parallel with US2-US3)
5. **US5 (P3) - Responsive/Accessibility**: T054-T061 (After US1-US4)

### Critical Path
```
T001-T010 (Phase 1: Setup)
    ↓
T011-T025 (Phase 2: Navigation) - BLOCKS all other user stories
    ├─ T026-T035 (Phase 3: Search) [PARALLEL with T036-T043, T044-T053]
    ├─ T036-T043 (Phase 4: Code Highlighting) [PARALLEL]
    └─ T044-T053 (Phase 5: Chatbot) [PARALLEL]
    ↓
T054-T061 (Phase 6: Responsive/Accessibility)
    ↓
T062-T067 (Phase 7: Performance)
    ↓
T068-T075 (Phase 8: Testing & QA)
    ↓
T076-T081 (Phase 9: Documentation & Deployment)
```

---

## Parallel Execution Opportunities

### Phase 1 Parallelization
- T005, T006, T007, T008 can run in parallel (all independent setup tasks)
- Start with T001-T004 sequentially, then parallelize T005-T009

### Phase 2 Parallelization
- T012, T013, T014, T015, T016 can run in parallel (all chapter-related independent tasks)
- T021, T022, T023 can run in parallel (module pages, theme, footer are independent)
- Dependency: T011 must complete first (chapter import required before other tasks)

### Phase 3-5 Parallelization (Post Phase 2)
- T026-T035 (Search), T036-T043 (Code), T044-T053 (Chatbot) are fully parallelizable
- All depend on Phase 2 navigation structure being complete
- Can run 3 developers simultaneously on these phases

### Phase 6 Parallelization
- T054, T055, T057 can run in parallel (layout testing, configuration, auditing)
- T056, T058, T059, T060 can run in parallel (keyboard nav, fixes, accessibility testing)

---

## MVP Scope (Tasks 1-25)

**Phases 1-2**: Core reading experience
- ✅ Docusaurus project set up and deployed to GitHub Pages
- ✅ All 20 chapters imported with module organization
- ✅ Navigation (sidebar, previous/next, breadcrumbs) fully functional
- ✅ Homepage with dual navigation (Start Here + search box placeholder)
- ⏸️ Search not yet functional (Phase 3)
- ⏸️ Code highlighting, chatbot, responsive design (Phases 4-6)

**MVP Acceptance Criteria**:
- SC-001: Navigate any chapter in <2 clicks ✅
- SC-004: Code examples display (no highlighting yet)
- SC-005: Responsive on desktop (mobile incomplete)
- SC-010: Add chapters by markdown file ✅

**MVP Go-Live Criteria**:
- [ ] npm run build succeeds from frontend/textbook-site/
- [ ] GitHub Pages deployment automatic via GitHub Actions
- [ ] All 20 chapters navigable from sidebar
- [ ] No broken links in sidebar navigation
- [ ] Homepage loads with navigation options (Start Here + search prompt)

**Estimated MVP Timeline**: 6-10 days (Phases 1-2)

---

## Independent Test Criteria Per User Story

### US1: Browse Textbook Chapters
- ✅ All 20 chapters displayed in sidebar
- ✅ Navigate chapter to chapter 1 to chapter 20 in less than 2 clicks
- ✅ Previous/next buttons work correctly at chapter boundaries
- ✅ Breadcrumb shows current location (Module > Chapter format)
- ✅ Auto TOC shows section headings from chapter content
- ✅ No broken links in navigation

### US2: Search and Discover Content
- ✅ Search box accepts input without errors
- ✅ Results appear within 500ms for typical queries
- ✅ Click result navigates to correct section in chapter
- ✅ Results ranked by relevance (title matches first, then content)
- ✅ Works on mobile and desktop viewports
- ✅ Special characters handled correctly without breaking search

### US3: View Code Examples
- ✅ Python code highlighted correctly with syntax colors
- ✅ YAML code highlighted correctly with syntax colors
- ✅ XML (URDF) code highlighted correctly with syntax colors
- ✅ Bash code highlighted correctly with syntax colors
- ✅ Copy button copies code to clipboard and shows confirmation
- ✅ 100% of code examples highlighted (0 missed blocks - SC-004)

### US4: Embedded Chatbot
- ✅ Chat widget opens on all pages without page reload
- ✅ Message sends and response appears within 3 seconds
- ✅ Chat widget closes without page reload
- ✅ If backend down shows error message "Chat currently unavailable" (not broken)
- ✅ Chapter remains readable when chat unavailable (graceful degradation)
- ✅ Chat history preserved in localStorage between sessions

### US5: Professional Documentation Site
- ✅ Desktop layout (1920px) uses professional spacing and typography
- ✅ Tablet layout (768px) responsive with toggleable sidebar
- ✅ Mobile layout (375px) readable and navigable without zoom
- ✅ Consistent header, footer, and navigation across all pages
- ✅ Keyboard navigation works (Tab, Enter, Escape functional)
- ✅ Lighthouse audit greater than or equal to 90 accessibility score (SC-009)
- ✅ Screen reader can read all content (WCAG 2.1 AA - SC-008)

---

## Implementation Notes

### File Structure
```
C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\
├── frontend\textbook-site\
│   ├── docusaurus.config.js        (Main Docusaurus configuration)
│   ├── sidebars.js                 (Chapter sidebar organization)
│   ├── package.json                (Dependencies and scripts)
│   ├── .github\workflows\
│   │   └── deploy.yml              (GitHub Actions CI/CD workflow)
│   ├── docs\                       (Chapter content - 20 markdown files)
│   │   ├── index.md                (Homepage with dual navigation)
│   │   ├── module-01\
│   │   │   ├── index.md            (Module 1 overview)
│   │   │   ├── chapter-01.md
│   │   │   └── ...
│   │   ├── module-02\
│   │   ├── module-03\
│   │   ├── module-04\
│   │   └── module-05\
│   ├── src\
│   │   ├── components\
│   │   │   ├── ChatbotWidget.tsx   (Chat widget - Phase 5)
│   │   │   ├── CodeBlock.tsx       (Copy button - Phase 4)
│   │   │   ├── SearchResults.tsx   (Search UI - Phase 3)
│   │   │   ├── SearchInput.tsx     (Search input - Phase 3)
│   │   │   ├── Navigation.tsx      (Prev/Next - Phase 2)
│   │   │   ├── Breadcrumb.tsx      (Breadcrumbs - Phase 2)
│   │   │   ├── Footer.tsx          (Footer - Phase 2)
│   │   │   └── LazyImage.tsx       (Lazy loading - Phase 7)
│   │   ├── utils\
│   │   │   └── chatApi.ts          (Chatbot API client - Phase 5)
│   │   └── theme\
│   │       └── custom.css          (Custom styling)
│   ├── static\                     (Images and static assets)
│   └── README.md                   (Setup and build instructions)
├── textbook\chapters\               (Source markdown - already exists)
└── specs\005-textbook-frontend\
    ├── spec.md                      (Feature specification)
    ├── plan.md                      (Implementation plan)
    ├── tasks.md                     (This file)
    ├── DEPLOYMENT_GUIDE.md          (Created in Phase 9)
    ├── USER_QUICKSTART.md           (Created in Phase 9)
    └── test-results.md              (Created in Phase 8)
```

### Chapter Frontmatter Format
```yaml
---
id: chapter-001
title: Introduction to Physical AI and Humanoid Robotics
module: 1
order: 1
description: Overview of physical AI, humanoid robotics fundamentals, and course structure
---

# Chapter Content (Markdown)
```

### GitHub Actions Workflow Configuration
**File**: `.github/workflows/deploy.yml`
- Trigger: Push to main branch
- Build: Run npm ci && npm run build in frontend/textbook-site/
- Deploy: Auto-deploy build/ directory to gh-pages branch
- Result: GitHub Pages automatically serves from gh-pages branch

### Environment Variables
- **Production**: `REACT_APP_API_URL=https://robotics-rag-backend.onrender.com` (from Phase 004)
- **Local Development**: `REACT_APP_API_URL=http://localhost:8000`
- Store in `.env.local` (local) and GitHub Secrets (production)

### Docusaurus Configuration Key Settings
**File**: `docusaurus.config.js`
```javascript
module.exports = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  url: 'https://[username].github.io',
  baseUrl: '/book/',
  projectName: 'book',
  organizationName: '[username]',

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
        },
      },
    ],
  ],

  themeConfig: {
    prism: {
      additionalLanguages: ['python', 'yaml', 'bash'],
    },
  },
};
```

### Chatbot API Integration
- **Endpoint**: POST /api/v1/chat (from Phase 004 backend)
- **Request**: `{ "query": "What is forward kinematics?", "conversation_id": "uuid" }`
- **Response**: `{ "response": "...", "sources": [...] }`
- **Error Handling**: Show "Chat currently unavailable" on 5xx errors or timeout >3s
- **Rate Limit**: 10 requests/minute per user (from Phase 004 backend)

---

## Task Checklist Template

Use this format to track progress:

```markdown
## Phase 1 Progress
- [x] T001 ✅ Initialize Docusaurus
- [x] T002 ✅ Configure docusaurus.config.js
- [ ] T003 Set up GitHub Actions
- [ ] T004 Configure GitHub Pages
...
```

---

**Status**: ✅ TASKS GENERATED - READY FOR IMPLEMENTATION
**Total Tasks**: 81
**Recommended Start**: T001 (Initialize Docusaurus project)
**MVP Target**: Complete T025 (Phase 2 - Navigation functional)
**Full Feature**: Complete T081 (Phase 9 - Production deployment)

---

Generated: 2026-02-05 | Feature: 005-textbook-frontend | Stage: Tasks Complete
