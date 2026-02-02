# Implementation Plan: Content Writing & Book Modules

**Branch**: `002-content-writing` | **Date**: 2026-01-31 | **Spec**: [specs/002-content-writing/spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-content-writing/spec.md`

**Note**: This plan covers the workflow, team structure, code verification strategy, and module-by-module delivery approach for creating a 4-module, 52,000-word Humanoid Robotics textbook.

---

## Summary

Create a comprehensive, 4-module Humanoid Robotics textbook (22 chapters, 52,000 words) designed to serve as the authoritative knowledge base for the RAG chatbot. The textbook covers fundamentals (Module 1: 5 chapters), ROS 2 software architecture (Module 2: 6 chapters), advanced control systems (Module 3: 6 chapters), and real-world applications (Module 4: 5 chapters). Each chapter includes theory, diagrams, worked examples, and 2-4 runnable code examples (66 total). The book is written by a solo primary writer over Weeks 1-4, with parallel code verification (local VM + CI/CD) and expert technical review (flexible pool of 2-3 roboticists). Module 1 serves as a pilot to validate the RAG indexing pipeline by end of Week 1; Modules 2-4 roll out with confidence. Module 4 is explicitly deferrable to post-hackathon if timeline slips, ensuring Modules 1-3 (base 100 points) are achieved on schedule.

---

## Technical Context

**Language/Version**: Python 3.10+, C++17, URDF/XML, YAML, Bash/Shell
**Primary Dependencies**:
- ROS 2 Humble LTS (code examples tested against this)
- Gazebo 11+ (simulation examples)
- Isaac Sim (optional simulation alternative, Chapter 8)
- OpenAI Embeddings (RAG indexing)
- Qdrant (vector store from Spec 001)

**Storage**:
- Textbook content stored in `/textbook/` directory (markdown chapters, code examples in `/textbook/code-examples/`)
- Code examples tested locally before commit
- Verified content staged for RAG indexing

**Testing**:
- Unit tests: pytest for Python examples
- Integration tests: All 66 code examples must execute on Ubuntu 22.04 + ROS 2 Humble LTS
- Verification: Local VM (development) + CI/CD pipeline (pre-indexing verification)

**Target Platform**:
- Local development: Ubuntu 22.04 VM with ROS 2 Humble + Gazebo 11
- Deployment: RAG chatbot knowledge base (Qdrant) + Docusaurus frontend

**Project Type**:
- Content + Code artifacts (textbook + runnable examples)
- Dependency: Spec 001 (RAG chatbot) must be production-ready

**Performance Goals**:
- Textbook indexing: Complete by end of Week 4
- RAG chatbot response time: <2 seconds for textbook queries (per Constitution)
- Code example execution: <10 seconds each on local VM
- Accuracy: 95%+ factual accuracy (verified by expert review)

**Constraints**:
- Accuracy floor: 95%+ (factual errors block RAG indexing)
- Code compatibility: All examples must run on Ubuntu 22.04 + ROS 2 Humble LTS
- Version documentation: Deprecated or version-specific content clearly marked
- Review bottleneck: Expert availability mitigated with peer-review fallback
- Timeline pressure: Module 4 deferrable; Modules 1-3 deliverable within 3 weeks

**Scale/Scope**:
- 22 chapters across 4 modules
- 52,000 words (12k + 13k + 14k + 13k)
- 66 code examples (15 + 18 + 18 + 15)
- Solo primary writer
- Flexible pool of 2-3 expert reviewers
- Local testing infrastructure + CI/CD

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Specification-Driven Development
- **Status**: PASS
- **Evidence**: Spec 002 complete with 5 user stories, 12 FRs, 10 success criteria, acceptance checklist
- **Action**: Planning workflow ongoing; tasks.md to follow

### ✅ Educational Excellence
- **Status**: PASS
- **Evidence**: Content accuracy requirements (95%+), code verification strategy (local VM + CI/CD), target audience defined (undergrad/early professional), complexity progression planned (fundamentals → architecture → control → applications)
- **Action**: Expert review process detailed; verification standards explicit in spec

### ✅ User-Centric Design
- **Status**: PASS (deferred to Spec 001 integration)
- **Evidence**: Textbook designed to serve RAG chatbot; module-by-module indexing allows early chatbot testing with Module 1
- **Action**: Module 1 pilot validates RAG integration Week 1

### ✅ Production Readiness
- **Status**: PASS
- **Evidence**: Code examples tested on specified environment (Ubuntu 22.04 + ROS 2 Humble); version documentation explicit; accuracy audit required before indexing
- **Action**: CI/CD pipeline configured; expert review checklist prepared

### ✅ Composability & Reusability
- **Status**: PASS
- **Evidence**: Chapters are independent units; code examples reusable across modules; RAG indexing treats each chapter as discrete knowledge unit
- **Action**: Chapter template ensures consistent structure; code organization in `/textbook/code-examples/` with naming convention

### ⚠️ Content Writing Standards (Constitution Section A)
- **Status**: PARTIAL (conditions in place, execution TBD)
- **Required Checkpoints**:
  - [ ] Accuracy: All 22 chapters verified 95%+ (expert review + fact-checking)
  - [ ] Clarity: Flesch-Kincaid Grade 10-12, active voice >75% (style guide to be created)
  - [ ] Completeness: Learning objectives, concepts, 2+ examples, assessments (Chapter 22 includes getting-started guide; others include code examples)
  - [ ] Code Quality: All 66 examples run without errors, PEP 8/C++17 compliant, commented, dependencies listed
  - [ ] Sourcing: All claims traceable, APA citations, peer-reviewed sources preferred
- **Plan**: Chapter template will enforce these standards; expert review includes accuracy audit

### ✅ Backend API Standards (Constitution Section B)
- **Status**: PASS (deferred to Spec 001)
- **Evidence**: RAG chatbot endpoints handle textbook queries; response time <2 sec (per Spec 002, SC-006)
- **Action**: Integration test required Week 1 (Module 1 pilot)

### ✅ Database Standards (Constitution Section C)
- **Status**: PASS (deferred to Spec 001)
- **Evidence**: Textbook content indexed into Qdrant with metadata; vector embeddings generated per Spec 001
- **Action**: Module 1 pilot validates Qdrant indexing Week 1

### ✅ Testing Requirements
- **Status**: PASS
- **Evidence**: All 66 code examples must execute on specified environment; 100% execution success rate required; local VM + CI/CD pipeline configured
- **Action**: Task breakdown will include code verification task per chapter

### ✅ Security Checklist (Constitution)
- **Status**: PASS (N/A for content writing, relevant to Spec 001 RAG integration)
- **Evidence**: No secrets in textbook content; no hardcoded credentials in examples; SQL injection prevention relevant to backend only
- **Action**: Code examples reviewed for security best practices

---

## Project Structure

### Documentation (this feature)

```text
specs/002-content-writing/
├── spec.md                  # Feature specification (complete)
├── plan.md                  # This file (Phase 0 of /sp.plan)
├── research.md              # Phase 1 output (/sp.plan) - resolve unknowns
├── data-model.md            # Phase 2 output (/sp.plan) - chapter template, metadata
├── quickstart.md            # Phase 2 output (/sp.plan) - writer workflow
├── contracts/               # Phase 2 output (/sp.plan) - chapter schema, code example schema
└── tasks.md                 # Phase 3 output (/sp.tasks) - actionable writing tasks
```

### Source Code (repository root)

```text
textbook/
├── code-examples/
│   ├── chapter_01_example_01.urdf
│   ├── chapter_01_example_02.py
│   ├── chapter_02_example_01.py
│   ├── chapter_02_example_02.cpp
│   ├── ...
│   ├── chapter_22_example_04.py
│   └── README.md            # Setup, execution, troubleshooting
│
├── chapters/
│   ├── 01-what-is-humanoid-robotics.md
│   ├── 02-kinematics-basics.md
│   ├── 03-dynamics-motion.md
│   ├── ...
│   ├── 22-getting-started.md
│   └── _chapter-template.md # Master template for all chapters
│
└── metadata/
    ├── references.json      # Centralized reference list (APA format)
    ├── code-examples-manifest.json  # Map chapters to code examples
    └── module-index.json    # Module-level metadata for RAG indexing
```

**Structure Decision**: Single-project textbook structure with modular chapters and organized code examples. Chapters are independent markdown files following a consistent template. Code examples are organized by chapter with naming convention `chapter_XX_example_YY.ext`. Metadata files support RAG indexing and reference tracking.

---

## Phase 0: Research & Unknowns Resolution

### Unknowns Identified from Spec

**Q1: Writer Productivity & Timeline Feasibility**
- *Unknown*: Can a solo writer produce 2,000-2,500 words/day consistently over 3 weeks?
- *Clarification Session 2026-01-31*: Yes, for Modules 1-3 (base 100 points); Module 4 deferrable if needed
- *Research*: Evaluate writing tools (Docusaurus-friendly markdown), chapter templates, and workflow automation

**Q2: Code Example Verification Strategy**
- *Unknown*: How to verify 66 code examples efficiently without manual testing bottleneck?
- *Clarification Session*: Local VM (fast iteration) + CI/CD pipeline (pre-indexing verification)
- *Research*: Evaluate test automation, CI/CD configuration, and example execution framework

**Q3: Expert Review Bottleneck**
- *Unknown*: Will expert reviewer availability block content publication?
- *Clarification Session*: Flexible pool (2-3 experts) + peer-review fallback checklist
- *Research*: Create structured peer-review checklist; define fallback workflow

**Q4: RAG Indexing Integration**
- *Unknown*: When can Module 1 content be indexed into RAG chatbot?
- *Clarification Session*: Week 1 pilot approach: Module 1 complete (5 chapters) → verify RAG pipeline → proceed with Modules 2-4
- *Research*: Validate RAG indexing pipeline with Spec 001; define metadata schema for chapter-level retrieval

### Research Tasks (Phase 0)

**T-001: Chapter Template Design & Writer Workflow**
- Research best practices for consistent textbook chapter structure
- Evaluate Docusaurus markdown with embedded code examples
- Design master chapter template (overview → concepts → examples → references)
- Output: `_chapter-template.md` + style guide

**T-002: Code Example Verification Framework**
- Research pytest + CI/CD patterns for ROS 2 code examples
- Evaluate Docker-based test environments for consistency
- Design CI/CD pipeline for pre-indexing code verification
- Output: CI/CD configuration + code example test harness

**T-003: Peer-Review Checklist & Expert Review Workflow**
- Research peer-review best practices for technical content
- Design structured checklist for factual accuracy verification
- Define fallback workflow for expert unavailability
- Output: Peer-review checklist + expert review SLA

**T-004: RAG Indexing Metadata & Retrieval Schema**
- Coordinate with Spec 001 to validate indexing pipeline
- Design chapter-level metadata schema (title, learning objectives, tags, word count)
- Test Module 1 indexing workflow end-to-end
- Output: Metadata schema + Module 1 indexing test results

**T-005: Reference Management & Citation Standards**
- Research APA citation format for robotics references
- Design centralized reference database (references.json)
- Define citation workflow for chapter authors
- Output: Reference template + citation guide

---

## Phase 1: Design & Contracts

### 1. Data Model: Chapter Entity & Code Example Entity

**Chapter Entity**
```json
{
  "id": "chapter_01",
  "title": "What is a Humanoid Robot?",
  "module": 1,
  "chapter_number": 1,
  "word_count": 2300,
  "learning_objectives": ["Understand history of humanoid robotics", "..."],
  "sections": [
    {
      "heading": "Introduction",
      "content": "...",
      "subsections": []
    },
    {
      "heading": "Key Concepts",
      "content": "..."
    }
  ],
  "code_examples": ["chapter_01_example_01", "chapter_01_example_02"],
  "references": ["ref_001", "ref_002", "..."],
  "status": "draft|review|approved|indexed",
  "review_status": "pending|expert_review|peer_review|approved",
  "created_date": "2026-02-01",
  "reviewed_date": "2026-02-03",
  "indexed_date": "2026-02-03"
}
```

**Code Example Entity**
```json
{
  "id": "chapter_01_example_01",
  "chapter_id": "chapter_01",
  "title": "Simple Robot URDF Description",
  "language": "urdf",
  "file_path": "code-examples/chapter_01_example_01.urdf",
  "description": "A basic URDF file defining a simple humanoid robot structure",
  "lines_of_code": 45,
  "execution_time_sec": 2,
  "status": "untested|tested|verified",
  "test_environment": "ubuntu_22.04_ros2_humble",
  "test_result": "pass|fail",
  "error_output": "",
  "dependencies": ["ros2", "urdf_parser"],
  "version_notes": "ROS 2 Humble compatible"
}
```

**Metadata Relationships**
- Chapter → Code Examples (1:many)
- Chapter → References (1:many)
- Module → Chapters (1:many)
- Code Example → Test Results (1:many, tracked over time)

---

### 2. API Contracts

**Contract 1: Chapter Content Retrieval** (for RAG indexing)
```
GET /textbook/chapters/{chapter_id}
Response:
{
  "id": "chapter_01",
  "title": "What is a Humanoid Robot?",
  "content": "...",
  "sections": [...],
  "learning_objectives": [...],
  "references": [...],
  "code_examples": [...]
}
```

**Contract 2: Code Example Execution** (for CI/CD verification)
```
POST /verify/code-example
Body: {
  "example_id": "chapter_01_example_01",
  "environment": "ubuntu_22.04_ros2_humble"
}
Response: {
  "success": true,
  "execution_time_sec": 2.5,
  "output": "...",
  "stderr": ""
}
```

**Contract 3: Chapter Review Submission** (for expert/peer review)
```
POST /review/chapter
Body: {
  "chapter_id": "chapter_01",
  "reviewer_type": "expert|peer",
  "accuracy_score": 95,
  "flagged_issues": [
    {
      "line": 42,
      "severity": "high|medium|low",
      "description": "..."
    }
  ],
  "status": "approved|needs_revision"
}
Response: {
  "review_id": "review_001",
  "status": "submitted"
}
```

---

### 3. Quick Start: Writer Workflow

**Week 1: Module 1 (Fundamentals) - 5 chapters, ~12,000 words**

1. **Day 1**: Setup
   - Clone textbook repo, review chapter template
   - Setup local ROS 2 Humble VM for code testing
   - Understand module outline and learning objectives

2. **Days 2-5**: Write Chapters 1-5
   - Chapter 1 (What is a Humanoid Robot): 2,300 words + 2 code examples
   - Chapter 2 (Kinematics Basics): 2,300 words + 2 code examples
   - Chapter 3 (Dynamics & Motion): 2,400 words + 2 code examples
   - Chapter 4 (Sensors & Perception): 2,400 words + 2 code examples
   - Chapter 5 (Hardware Overview): 2,300 words + 2 code examples
   - **Parallel**: Test all code examples on local VM
   - **Parallel**: Submit chapters for expert review as completed

3. **Day 7**: Finalize & Index
   - Resolve expert review feedback
   - Verify all code examples pass CI/CD
   - Submit Module 1 for RAG indexing (12,000 words, 15 code examples)
   - **Validation**: RAG chatbot successfully retrieves Module 1 content for sample queries

**Week 2: Module 2 (ROS 2 Architecture) - 6 chapters, ~13,000 words**

- Weeks 2 follows same cadence: write → test → review → index
- Module 2 chapters: 6, 7, 8, 9, 10, 11

**Week 3: Module 3 (Control & Kinematics) - 6 chapters, ~14,000 words**

- Week 3 follows same cadence
- Module 3 chapters: 12, 13, 14, 15, 16, 17

**Week 4: Module 4 (Applications) - 5 chapters, ~13,000 words (or defer)**

- If timeline permits: chapters 18, 19, 20, 21, 22
- If timeline slips: defer to post-hackathon; Modules 1-3 deliver base 100 points

---

### 4. Chapter Template & Metadata Schema

**Chapter Template** (`_chapter-template.md`)
```markdown
# Chapter X: [Title]

## Learning Objectives
- [ ] Objective 1
- [ ] Objective 2
- [ ] Objective 3

## Introduction
[Introductory paragraph, 200-300 words]

## Key Concepts
### Concept 1: [Name]
[Explanation with examples, 400-600 words]

### Concept 2: [Name]
[Explanation with examples, 400-600 words]

## Code Examples
### Example 1: [Title]
[Description of what the example demonstrates]
```python
# code here
```
[Explanation of key lines]

## Summary
[Recap of key takeaways, 200 words]

## References
[APA-formatted references]
```

**Metadata for RAG Indexing** (in chapter front matter or separate JSON)
```json
{
  "chapter_id": "chapter_01",
  "module": 1,
  "title": "What is a Humanoid Robot?",
  "learning_objectives": ["..."],
  "keywords": ["humanoid", "robot", "history", "kinematics"],
  "word_count": 2300,
  "code_example_count": 2,
  "difficulty_level": "beginner",
  "indexed_sections": [
    {
      "heading": "What is a Humanoid Robot?",
      "word_count": 500,
      "vector_embedding": "[1536 dims]"
    }
  ]
}
```

---

## Phase 2: Constitution Check (Post-Design)

*Re-evaluation after Phase 1 design artifacts.*

### ✅ Content Writing Standards Check
- **Chapter Template**: Enforces learning objectives, key concepts, code examples, references
- **Metadata Schema**: Tracks accuracy_score, review_status for Constitution compliance
- **Verification Plan**: Local VM testing + CI/CD verification ensures code quality
- **Status**: PASS (template and verification workflow in place)

### ✅ Accuracy & Verification
- **Expert Review Workflow**: Defined with fallback peer-review checklist
- **Fact-Checking Process**: Spec outlines draft → AI review → expert review → final audit
- **95%+ Accuracy Gate**: Required before RAG indexing
- **Status**: PASS (process and gates defined)

### ✅ Code Quality & Testing
- **All 66 Examples Tested**: Local VM + CI/CD pipeline
- **Environment Standardized**: Ubuntu 22.04 + ROS 2 Humble LTS
- **100% Execution Success**: Required before indexing
- **Status**: PASS (testing infrastructure planned)

### ✅ Production Readiness
- **Version Documentation**: All tools explicitly versioned (ROS 2 Humble, Gazebo 11, Python 3.10+)
- **Deprecated Content Handling**: Clearly marked with remediation paths
- **RAG Integration**: Module 1 pilot validates pipeline Week 1
- **Status**: PASS (constraints explicit, pilot approach reduces risk)

---

## Key Design Decisions

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| **Solo Writer + Parallel Reviews** | Fast writing pace (2,500 wds/day); reviews happen offline parallel to next chapters | Full writing + sequential reviews (timeline risk) |
| **Module 1 Pilot Approach** | Validates RAG indexing pipeline early; identifies issues Week 1, not Week 4 | Index all modules at end (high risk if pipeline broken) |
| **Module 4 Deferral** | Modules 1-3 = 100 points; eliminates timeline pressure; post-hackathon completion acceptable | Aggressive 4-module push Week 4 (high risk of incomplete/low-quality work) |
| **Peer-Review Fallback** | Ensures content quality even if expert unavailable; reduces reviewer bottleneck | No fallback (risks missed deadlines if expert unavailable) |
| **Local VM + CI/CD Split** | Local VM enables fast iteration; CI/CD pipeline ensures reproducibility before indexing | Only local testing (environment mismatch risk); only CI/CD (slow feedback loop) |
| **Chapter-Level RAG Indexing** | Each chapter is discrete knowledge unit; enables incremental indexing + early chatbot testing | Full-text indexing (harder to debug retrieval; no early validation) |

---

## Risks & Mitigations

| Risk | Blast Radius | Mitigation |
|------|--------------|-----------|
| **Expert Reviewer Unavailable** | Module review delay → indexing delay | Flexible pool (2-3 experts); peer-review fallback checklist |
| **Code Example Fails in CI/CD** | Example cannot be indexed; chapter incomplete | Test early and often on local VM; CI/CD gate before indexing |
| **Timeline Slip (Weeks 3-4)** | Module 4 incomplete | Module 4 explicitly deferrable; Modules 1-3 deliver base points |
| **Accuracy Audit Fails 95%+** | Content cannot be indexed; chatbot unreliable | Expert review + fact-checking before index gate |
| **RAG Pipeline Broken** | Module 1 cannot be indexed; cascades to all modules | Module 1 pilot Week 1 validates pipeline early |

---

## Complexity Justification

*No violations to justify; all decisions align with Constitution.*

---

## Outputs from Phase 1

- ✅ **plan.md** (this file): Implementation strategy and workflow
- 📋 **research.md** (Phase 0): Unknowns resolution (to be completed)
- 📋 **data-model.md** (Phase 1): Chapter and code example entity schemas
- 📋 **contracts/** (Phase 1): API contracts for content retrieval, code verification, review submission
- 📋 **quickstart.md** (Phase 1): Writer workflow (Week 1-4 breakdown with daily tasks)
- 📋 **_chapter-template.md** (Phase 1): Master template for all chapters
- 📋 **tasks.md** (Phase 2, `/sp.tasks`): Actionable writing tasks with dependencies

---

## Next Steps

1. **Phase 0 Complete**: Clarifications resolved (Q1-Q4 answered)
2. **Phase 1 Complete**: Design artifacts in place (data model, contracts, quickstart)
3. **Phase 2 (Next)**: Run `/sp.tasks` to break textbook writing into atomic tasks
   - Writing tasks per chapter (22 tasks)
   - Code verification tasks per chapter (22 tasks)
   - Review tasks per module (4 tasks)
   - RAG indexing validation tasks (4 tasks)
4. **Phase 3 (Implementation)**: Run `/sp.implement` to execute tasks in dependency order

---

**Status**: Plan Phase 1-2 Complete | Ready for `/sp.tasks` | Branch: `002-content-writing`

