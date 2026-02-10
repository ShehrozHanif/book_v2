# Implementation Plan: Textbook Frontend with Docusaurus Documentation Site

**Feature**: 005-textbook-frontend
**Created**: 2026-02-04
**Status**: Active Planning
**Specification**: [spec.md](./spec.md)

---

## Executive Summary

Build a professional Docusaurus-based documentation site for the 20-chapter Physical AI & Humanoid Robotics textbook. The site will provide chapter navigation, full-text search, syntax-highlighted code examples, and embedded RAG chatbot integration for interactive learning.

**MVP Delivery**: 2-3 weeks
**Full Feature Set**: 3-4 weeks

---

## Technical Context

### Technology Stack

**Framework & Hosting**:
- ✅ **Docusaurus 3.x** - Static site generator for documentation (industry standard, built-in search, React-based)
- ✅ **GitHub Pages** - Free hosting with automatic deploys via GitHub Actions
- ✅ **Node.js 18+** - Runtime for Docusaurus build and development
- ✅ **GitHub Actions** - CI/CD automation for builds and deployments

**Frontend Technologies**:
- ✅ **React 18+** - Docusaurus is built on React; chatbot widget integration via React
- ✅ **Markdown** - All 20 chapters in markdown format (existing from Phase 002)
- ✅ **Docusaurus CLI** - Build tools, local development server, optimization

**Integration Points**:
- ✅ **RAG Chatbot API** - Backend from Phase 004 at production URL (Render)
- ✅ **Qdrant Vector DB** - Already indexed with textbook chapters (Phase 004)
- ✅ **OpenAI API** - Chatbot uses this; no new integration needed

**Development Environment**:
- ✅ **VS Code** - Recommended IDE
- ✅ **npm/yarn** - Package management
- ✅ **Git/GitHub** - Version control and CI/CD

### Architecture Pattern

```
User Browser (Client)
    ↓
Static Site (GitHub Pages) ← Built by Docusaurus
    ├─ HTML/CSS/JS
    ├─ 20 Chapters (markdown → HTML)
    ├─ Search Index (embedded)
    └─ Chat Widget Component
         ↓
    ChatBot Backend API (Render, Phase 004)
         ↓
    Qdrant Vector DB (production)
         ↓
    OpenAI API
```

**Key Decision**: Search index is built once during site generation and embedded in static files. No backend search service needed. When chapters are updated, GitHub Actions rebuilds the entire site, including the search index.

### Constitution Check

**Status**: ✅ PASSED (All standards applicable and met)

✅ **E. Frontend Standards**:
- Docusaurus provides responsive design (mobile, tablet, desktop)
- Built-in accessibility support (WCAG 2.1 AA compliance via defaults)
- Optimized performance with static site generation (<3 sec page load)
- Cross-browser support (Chrome, Firefox, Safari)

✅ **Specification-Driven Development**:
- This plan follows SDD methodology
- Specification provides testable criteria
- All requirements are measurable

✅ **Technology Stack Compliance**:
- Docusaurus 3+ (✅ specified in constitution)
- React 18+ (✅ Docusaurus uses React)
- No forbidden technologies used (✅ no Next.js, no SQLite)

✅ **Code Quality Standards**:
- All JavaScript code follows ESLint
- Prettier formatting applied
- Error handling for chatbot unavailability
- No hardcoded secrets (API keys in .env)

✅ **Testing Requirements**:
- Manual testing of all features
- Acceptance criteria from spec provide test cases
- Performance testing of search (<500ms)
- Chatbot integration testing

---

## Key Decisions & Rationale

### Decision 1: Docusaurus for Static Site Generation

**Choice**: Docusaurus 3.x (vs. Hugo, Sphinx, Next.js)

**Rationale**:
- ✅ React-based: Seamless integration with chatbot widget component
- ✅ Built-in search: Full-text search works out-of-the-box without backend
- ✅ Markdown-native: Supports 20 existing markdown chapters
- ✅ Zero-config deployment: Direct GitHub Pages support with Actions
- ✅ Industry standard: Used by Meta, Facebook, React docs, FastAPI

**Alternatives Considered**:
- Hugo: Faster builds, but no React/widget integration
- Sphinx: Great for Python projects, but markdown support weaker
- Next.js: Overkill for static content; adds complexity and cost

### Decision 2: Search Index as Build-Time Artifact

**Choice**: Search index built during `npm run build`, embedded in site (Clarification Q1 resolved)

**Rationale**:
- ✅ No backend needed (no extra infrastructure cost)
- ✅ Sub-100ms search queries (client-side, no network latency)
- ✅ Automatic updates via GitHub Actions when chapters change
- ✅ Meets <500ms success criterion
- ✅ Docusaurus standard pattern

**Alternatives Considered**:
- Backend search API: Adds complexity, requires server maintenance
- Browser-downloaded index: Works but larger initial download
- Algolia/Meilisearch: Great but adds cost

### Decision 3: Chatbot Widget as React Component

**Choice**: Embed chatbot as React component that calls backend API (existing from Phase 004)

**Rationale**:
- ✅ Reuses existing chatbot backend (no new API needed)
- ✅ React integration with Docusaurus is native
- ✅ Graceful error handling when API unavailable (Clarification Q2)
- ✅ Can be toggled on/off via component state

**Alternatives Considered**:
- iFrame embed: Would work but less integrated UX
- Custom HTML widget: Not React-native; harder to maintain

### Decision 4: Homepage with Hybrid Navigation

**Choice**: Homepage with both "Start Here" button AND search box (Clarification Q3 resolved)

**Rationale**:
- ✅ Serves sequential learners (click "Start Here" → Module 1)
- ✅ Serves self-directed learners (search for topics)
- ✅ Industry standard (Django docs, FastAPI, React docs all use this)
- ✅ Maximizes engagement

**Alternatives Considered**:
- Sequential only: Restricts self-directed learners
- Search-first: Confuses sequential learners
- Separate landing page: Adds complexity

---

## Non-Functional Requirements & Design

### Performance

**Success Criteria**:
- SC-002: Search returns results in <500ms ✅
- SC-003: Pages load in <2s (broadband) or <4s (mobile) ✅

**Design Approach**:
- Static HTML/CSS/JS (no backend latency)
- Lazy-load images in chapters
- Minify and gzip all assets
- CDN via GitHub Pages (free)
- Service worker for offline support (stretch goal)

### Accessibility

**Success Criteria**:
- SC-008: WCAG 2.1 AA compliance ✅
- SC-009: Lighthouse accessibility score 90+ ✅

**Design Approach**:
- Use Docusaurus semantic HTML (heading hierarchy H1-H6)
- Color contrast ≥4.5:1 (Docusaurus defaults meet this)
- Keyboard navigation fully supported
- Alt text for all images
- ARIA labels for interactive components (chatbot button)

### Scalability

**Design Approach**:
- Static site can scale infinitely (GitHub Pages CDN)
- Search index scales with number of chapters (embedded)
- Chatbot API scaling handled by Phase 004 (Render backend)
- No database scaling needed (static files only)

### Reliability

**Success Criteria**:
- SC-007: Chatbot 99% available ✅

**Design Approach**:
- Site always works (static files)
- Graceful degradation if chatbot API down (show error message)
- Automatic backups (GitHub stores source)
- Automated redeploys via GitHub Actions on chapter changes

### Security

**Design Approach**:
- No user data stored (static site, read-only)
- HTTPS enforced (GitHub Pages default)
- No authentication required (public content)
- Chatbot API handles auth (already secured in Phase 004)
- No hardcoded secrets (.env for API keys during build)

---

## Interfaces & API Contracts

### External Dependencies

**1. Textbook Chapters (Input)**
- **Source**: `textbook/chapters/` (existing markdown files)
- **Format**: Markdown with YAML frontmatter
- **Schema**:
  ```yaml
  ---
  id: chapter-001
  title: Introduction to Robotics
  module: 1
  order: 1
  ---
  # Chapter Content (Markdown)
  ```
- **Validation**: Docusaurus will process and validate during build
- **Update Frequency**: Build triggered on GitHub commit

**2. Chatbot Backend API**
- **URL**: Production Render URL (from Phase 004)
- **Method**: POST `/api/v1/chat` (existing from Phase 001)
- **Request**: `{ "query": "What is forward kinematics?", "conversation_id": "..." }`
- **Response**: `{ "response": "...", "sources": [...], "metadata": {...} }`
- **Error Handling**: Show "Chat currently unavailable" if API returns 5xx or timeout >3s
- **Rate Limit**: 10 requests/min per user (from Phase 004)

**3. Search Index (Built-in)**
- **Type**: Lunr.js or Docusaurus built-in search
- **Format**: Embedded in static files
- **Update**: Regenerated during `npm run build`
- **Performance**: Sub-100ms queries (client-side)

### Browser APIs Used

- **Fetch API**: Call chatbot backend
- **LocalStorage**: Store search history (optional, stretch goal)
- **Copy to Clipboard API**: Copy button in code blocks
- **IntersectionObserver**: Lazy-load images, detect scroll position

---

## Data Model

### Entities (Logical, No Database)

**Chapter**
```
- id: string (slug)
- title: string
- module: integer (1-5)
- order: integer (1-4 within module)
- content: markdown string
- sections: array of {heading, level, anchor}
- codeExamples: array of {language, code, lineNumbers}
- metadata: {createdAt, updatedAt, author}
```

**Module**
```
- id: integer (1-5)
- title: string
- description: string
- chapters: array of Chapter references
```

**SearchIndex**
```
- Built at build-time from all chapters
- Indexed fields: title, sections, content, code examples
- Output: JavaScript object embedded in HTML
- Updated: Every `npm run build` (triggered by GitHub commit)
```

**ChatSession** (Client-side, optional)
```
- userId: optional (from Phase 003 personalization)
- conversation: array of {role, message, timestamp}
- currentChapterId: string (context for chatbot)
- preferences: {darkMode, fontSize}
- Stored: Browser LocalStorage
```

---

## Implementation Phases

### Phase 1: Setup & Foundation (3-5 days)

**Goals**:
- Initialize Docusaurus project
- Set up GitHub Pages deployment
- Configure CI/CD pipeline
- Prepare for chapter import

**Tasks**:
1. Create Docusaurus project with `npx create-docusaurus@latest`
2. Configure `docusaurus.config.js` for GitHub Pages
3. Set up GitHub Actions workflow for build & deploy
4. Create directory structure for chapters (`docs/chapters/`)
5. Add base styling and Tailwind CSS (if customization needed)
6. Set up local development environment
7. Test build process locally

**Deliverables**:
- ✅ Working Docusaurus project locally
- ✅ GitHub Actions CI/CD configured
- ✅ Test deploy to GitHub Pages
- ✅ Development guide documented

**Success Criteria**:
- Site deploys to GitHub Pages successfully
- Pages load without errors
- Site is accessible at `https://[username].github.io/book`

---

### Phase 2: Chapter Import & Navigation (3-5 days)

**Goals**:
- Import all 20 chapters from `textbook/chapters/`
- Set up module organization
- Implement chapter navigation
- Create homepage with dual navigation

**Tasks**:
1. Copy 20 chapters to `docs/chapters/`
2. Add YAML frontmatter to each chapter (module, order)
3. Create `docs/sidebars.js` configuration
4. Configure Docusaurus sidebar with modules and chapters
5. Implement "Previous/Next" navigation buttons
6. Add breadcrumb navigation component
7. Create homepage with "Start Here" button + search prompt
8. Implement "Table of Contents" sidebar auto-generation from headings

**Deliverables**:
- ✅ All 20 chapters visible and navigable
- ✅ Module-based organization working
- ✅ Homepage with dual navigation
- ✅ Breadcrumbs showing current location

**Success Criteria**:
- Navigate to any chapter in <2 clicks (SC-001)
- All 20 chapters display correctly
- Sidebar highlights current chapter
- Next/Previous buttons work on all chapters
- Homepage clearly shows both learning paths

---

### Phase 3: Search Functionality (2-3 days)

**Goals**:
- Enable and configure full-text search
- Test search performance
- Optimize index size

**Tasks**:
1. Enable Docusaurus search plugin (built-in)
2. Configure search index fields (title, content, sections)
3. Test search performance with sample queries
4. Implement search result ranking by relevance
5. Add search result snippets (context around match)
6. Test search with special characters and Unicode

**Deliverables**:
- ✅ Search box visible on all pages
- ✅ Search returns relevant results
- ✅ Results ranked by relevance
- ✅ Context snippets displayed

**Success Criteria**:
- Search returns results in <500ms (SC-002)
- Results include context snippets
- Special characters handled correctly
- Search index updated on chapter changes (via CI/CD rebuild)

---

### Phase 4: Code Examples & Syntax Highlighting (2-3 days)

**Goals**:
- Add syntax highlighting for 4 languages (Python, ROS2, URDF, YAML)
- Implement copy-to-clipboard functionality
- Test all code examples display correctly

**Tasks**:
1. Configure code block highlighting (Docusaurus uses Prism.js by default)
2. Add syntax highlighting for Python, XML (URDF), YAML, Bash
3. Implement copy button on code blocks (Docusaurus has built-in support)
4. Add line numbers to code blocks where needed
5. Test that 100% of code examples are highlighted
6. Verify code formatting is correct in all chapters

**Deliverables**:
- ✅ All code examples highlighted
- ✅ Copy buttons on all code blocks
- ✅ Line numbers where appropriate
- ✅ No unformatted code blocks

**Success Criteria**:
- 100% of code examples have syntax highlighting (SC-004)
- Copy button works and shows confirmation
- Code remains readable and properly indented
- All 4 languages supported

---

### Phase 5: Chatbot Integration (3-5 days)

**Goals**:
- Embed chatbot widget on all pages
- Connect to Phase 004 backend API
- Implement graceful error handling
- Test chatbot functionality

**Tasks**:
1. Create React component for chatbot widget
2. Configure API endpoint for chatbot backend (from Phase 004)
3. Implement chat message input and display
4. Add "open/close" toggle button (bottom-right corner)
5. Implement graceful error handling:
   - Show "Chat currently unavailable" if API returns 5xx
   - Show error if timeout >3s
   - Keep chapters readable if chatbot fails
6. Add loading indicator while waiting for response
7. Test chatbot with sample queries about chapters
8. Implement context passing (current chapter to chatbot)

**Deliverables**:
- ✅ Chat widget visible on all chapter pages
- ✅ Chat can be toggled open/close
- ✅ Messages sent and responses received
- ✅ Error handling working
- ✅ Context passed to chatbot

**Success Criteria**:
- Chatbot accessible from any chapter (SC-007 requirement)
- Responses arrive within 3 seconds
- Error messages clear if API unavailable
- Chat widget doesn't break chapter reading
- 99% availability of chat feature

---

### Phase 6: Responsive Design & Accessibility (2-3 days)

**Goals**:
- Ensure responsive design on all breakpoints
- Verify WCAG 2.1 AA compliance
- Optimize for mobile and tablet

**Tasks**:
1. Test responsive design on mobile (375px), tablet (768px), desktop (1920px)
2. Verify sidebar collapses on mobile
3. Test touch interactions on mobile/tablet
4. Verify color contrast ≥4.5:1 (Docusaurus defaults usually comply)
5. Test keyboard navigation (Tab, Enter, Escape)
6. Run Lighthouse audit on all pages
7. Add alt text to all images
8. Verify ARIA labels on interactive elements (chat button)

**Deliverables**:
- ✅ Responsive on all breakpoints
- ✅ Lighthouse score 90+ (SC-009)
- ✅ WCAG 2.1 AA compliance (SC-008)
- ✅ Keyboard navigation tested

**Success Criteria**:
- Responsive design passes on 3 breakpoints (SC-005)
- Lighthouse accessibility score ≥90 (SC-009)
- Full keyboard navigation works
- No console errors on any browser
- Mobile text readable without zoom

---

### Phase 7: Performance Optimization (1-2 days)

**Goals**:
- Optimize page load time
- Minimize bundle size
- Test on slow networks

**Tasks**:
1. Minify and gzip all assets
2. Lazy-load images in chapters
3. Use responsive images (srcset)
4. Minimize CSS and JavaScript bundle
5. Remove unused dependencies
6. Test page load speed on broadband (>5Mbps) and mobile (3G)
7. Test from slow network (DevTools throttling)

**Deliverables**:
- ✅ Pages load in <2s (broadband) or <4s (mobile)
- ✅ All assets minified
- ✅ No unused dependencies
- ✅ Performance optimized

**Success Criteria**:
- Pages load in <2s on broadband (SC-003)
- Pages load in <4s on mobile (SC-003)
- Lighthouse performance score ≥90

---

### Phase 8: Testing & Quality Assurance (2-3 days)

**Goals**:
- Comprehensive testing of all features
- Performance testing
- Cross-browser testing

**Tasks**:
1. Manual testing of all acceptance scenarios (20 scenarios from spec)
2. Performance testing: search <500ms, pages <2s load
3. Test on Chrome, Firefox, Safari (latest versions)
4. Test on Windows, macOS, iOS, Android
5. Test edge cases:
   - 404 page for missing chapters
   - Special characters in search
   - JavaScript disabled (content still readable)
   - Chatbot API down (error message shown)
6. Load testing with Lighthouse
7. Security testing: no hardcoded secrets, no XSS vulnerabilities

**Deliverables**:
- ✅ All acceptance scenarios passing
- ✅ Cross-browser tested
- ✅ Performance verified
- ✅ Edge cases handled

**Success Criteria**:
- 100% of acceptance scenarios passing
- All pages accessible and readable
- No console errors
- Lighthouse reports >90 on all pages

---

### Phase 9: Documentation & Deployment (1-2 days)

**Goals**:
- Document setup and deployment
- Finalize for production release
- Create quick-start guide

**Tasks**:
1. Update README.md with setup instructions
2. Document chapter format and structure
3. Create deployment guide (how to redeploy after chapter changes)
4. Create contributing guide (how to add new chapters)
5. Document chatbot integration and API
6. Create quick-start guide for users
7. Add CHANGELOG.md with release notes
8. Final review and QA

**Deliverables**:
- ✅ README with setup instructions
- ✅ Contributing guide for new chapters
- ✅ Deployment documentation
- ✅ User quick-start guide
- ✅ CHANGELOG

**Success Criteria**:
- New team members can set up locally in <10 minutes
- Process for adding chapters is clear
- All documentation is current and accurate

---

## Constraints & Trade-offs

### Constraints

1. **Static Site Only**: No server-side processing. Search index must be built-time artifact.
2. **GitHub Pages Limitations**: 1GB repo size limit (easily accommodates 20 chapters + assets)
3. **Chatbot API Dependency**: Site can't do real-time chat if backend is down (graceful degradation)
4. **No User Data Persistence**: Site is read-only; no user accounts or progress tracking (handled by Phase 003)
5. **Search Language**: Limited to languages supported by Lunr.js (English primary)

### Trade-offs

| Trade-off | Choice | Rationale |
|-----------|--------|-----------|
| Backend Search API vs Build-time Index | Build-time | Simpler, cheaper, meets performance requirement |
| Docusaurus vs Custom Frontend | Docusaurus | Faster development, built-in features, maintenance |
| Single vs Multi-language | English only | Urdu translation is Phase 005 separate feature |
| Database vs Static Files | Static | Aligns with GitHub Pages, scales infinitely |
| Complex Theming vs Docusaurus Default | Docusaurus default | Faster, meets requirements, professional look |

---

## Risk Analysis

### Top 3 Risks

**Risk 1: Chapter Format Inconsistency**
- **Severity**: Medium
- **Probability**: Medium
- **Mitigation**: Audit all 20 chapters before import; establish markdown format guide
- **Fallback**: Script to auto-format chapters if issues found

**Risk 2: Chatbot API Unavailability**
- **Severity**: Low
- **Probability**: Low
- **Mitigation**: Graceful error handling implemented (show error message)
- **Fallback**: Site still fully functional for reading; chat degrades gracefully

**Risk 3: Search Performance with 20 Chapters**
- **Severity**: Low
- **Probability**: Low
- **Mitigation**: Test with full index; optimize index size if needed
- **Fallback**: Implement server-side search (Phase 004 extension)

---

## Dependencies

**Internal Dependencies**:
1. ✅ **Phase 002 (Content Writing)**: 20 chapters in markdown format - COMPLETE
2. ✅ **Phase 004 (Deployment)**: Chatbot API available at production URL - COMPLETE
3. ✅ **GitHub Repository**: Public repo with Pages enabled - AVAILABLE

**External Dependencies**:
1. **Docusaurus 3.x**: npm package (maintained by Meta)
2. **Node.js 18+**: Runtime (freely available)
3. **GitHub Pages**: Free hosting (GitHub feature)
4. **GitHub Actions**: Free CI/CD (GitHub feature)

---

## Success Metrics

| Metric | Target | Acceptance |
|--------|--------|-----------|
| **Chapter Navigation** | <2 clicks to any chapter | SC-001 ✅ |
| **Search Performance** | <500ms for queries | SC-002 ✅ |
| **Page Load Time** | <2s broadband / <4s mobile | SC-003 ✅ |
| **Code Highlighting** | 100% of examples | SC-004 ✅ |
| **Responsive Design** | 3+ breakpoints passing | SC-005 ✅ |
| **Search Index Updates** | Same-day deployment | SC-006 ✅ |
| **Chatbot Availability** | 99% of page loads | SC-007 ✅ |
| **Keyboard Accessibility** | Full navigation | SC-008 ✅ |
| **Lighthouse Score** | 90+ on all pages | SC-009 ✅ |
| **Chapter Maintenance** | Drop markdown file | SC-010 ✅ |

---

## Rollout Strategy

### MVP Release (Weeks 1-2)
**Scope**: Core textbook reading experience
- All 20 chapters navigable
- Search functional
- Code examples displayed
- Homepage with navigation options
- **Timeline**: Deploy to GitHub Pages end of Week 2

### Full Release (Week 3)
- Add chatbot integration (if API ready)
- Comprehensive testing
- Performance optimization
- Documentation complete
- **Timeline**: Full release end of Week 3

### Maintenance Plan
- Monitor Lighthouse scores (weekly)
- Update chapters as needed (trigger automatic rebuild)
- Monitor chatbot API connectivity
- Collect user feedback (optional tracking via analytics)

---

## Team & Responsibilities

**Frontend Developer**:
- Docusaurus configuration and customization
- React component development (chat widget)
- Responsive design and accessibility
- Performance optimization

**DevOps**:
- GitHub Actions CI/CD setup
- GitHub Pages deployment
- Monitoring and uptime tracking

**QA**:
- Manual testing on all browsers
- Performance testing (page load, search)
- Accessibility testing (WCAG 2.1 AA)
- User acceptance testing

---

## Next Steps

1. ✅ **Approval**: Review and approve this plan
2. 📝 **Task Generation**: Run `/sp.tasks 005-textbook-frontend` to generate detailed tasks
3. ⚙️ **Implementation**: Execute tasks in priority order
4. 🧪 **Testing**: Run comprehensive QA against acceptance criteria
5. 🚀 **Deployment**: Deploy to GitHub Pages
6. 📊 **Monitoring**: Track metrics and user feedback

---

## Appendix: Key Files & Configurations

### Docusaurus Configuration
**File**: `docusaurus.config.js`
```javascript
module.exports = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  url: 'https://[username].github.io/book',
  baseUrl: '/book/',
  projectName: 'book',
  organizationName: '[username]',
  trailingSlash: false,

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: 'sidebars.js',
          editUrl: 'https://github.com/[username]/book/edit/main/docs/',
        },
        theme: {
          customCss: 'src/css/custom.css',
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Robotics Textbook',
      logo: { src: 'img/logo.svg' },
    },
    footer: {
      copyright: 'Copyright © 2026',
    },
  },
};
```

### GitHub Actions Workflow
**File**: `.github/workflows/deploy.yml`
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```

---

**Status**: ✅ PLAN READY FOR TASK GENERATION

Next: Run `/sp.tasks 005-textbook-frontend` to generate detailed implementation tasks.
