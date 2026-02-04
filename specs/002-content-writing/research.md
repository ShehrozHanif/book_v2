# Research: Content Writing & Book Modules

**Date**: 2026-01-31 | **Branch**: `002-content-writing` | **Status**: Phase 0 Complete

---

## Overview

Phase 0 research resolves 4 critical unknowns identified in the specification via clarification session (Jan 31, 2026). Each research task validates assumptions and informs design decisions in `plan.md`.

---

## Research Task 1: Writer Productivity & Timeline Feasibility

**Question**: Can a solo writer produce 2,000-2,500 words/day consistently over 3 weeks?

**Decision** (from Clarifications, Q4): Yes, for Modules 1-3 (base 100 points); Module 4 deferrable if needed

**Rationale**:
- Professional technical writers typically produce 1,500-2,500 words/day including research and code examples
- Spec 002 clarifies that Modules 1-3 alone = 39,000 words (12k+13k+14k) = 39 days of work ÷ 21 days (3 weeks) = ~1,900 wds/day avg
- With chapter templates and parallel expert reviews, writer can focus on drafting vs. administrative overhead
- Module 4 (13,000 words, 5 chapters, week 4) is optional; deferral provides schedule buffer

**Alternatives Considered**:
- **Team writing (A)**: 2-3 writers covering different modules → higher coordination overhead, higher consistency risk. Rejected: solo effort simpler for content coherence.
- **Sequential writing + review**: Write all chapters, then review all → expert review becomes bottleneck. Rejected: parallel reviews (expert reviews while writer works on next chapter) more efficient.

**Implementation**:
- Chapter template standardizes structure → faster drafting
- Co-location of theory + code examples → reduces context switching
- Week 1-3 focus on Modules 1-3 (base 100 points)
- Module 4 deferrable to post-hackathon

**Risk**:
- Writer illness or personal emergency Week 2-3 → Module 4 slips even with deferral
- Mitigation: Modular structure allows another writer to continue from outline if needed

---

## Research Task 2: Code Example Verification Strategy

**Question**: How to verify 66 code examples efficiently without manual testing bottleneck?

**Decision** (from Clarifications, Q2): Local VM (fast iteration) + CI/CD pipeline (pre-indexing verification)

**Rationale**:
- **Local VM** (Ubuntu 22.04 + ROS 2 Humble): Enables rapid test-fix-commit cycle during writing (feedback <10 min)
- **CI/CD Pipeline** (GitHub Actions): Automated verification before RAG indexing; catches environment-specific issues
- Two-tier approach balances fast iteration (local) with reproducibility (CI/CD)
- All 66 examples tested on same environment → no "works on my machine" surprises

**Alternatives Considered**:
- **Manual testing only**: Writer tests locally, no CI/CD → environment mismatch risk during deployment. Rejected: inconsistent verification.
- **CI/CD only**: No local testing, slow feedback loop → writer waits 5-10 min for CI results. Rejected: slow iteration.
- **Docker-based testing**: Full containerization → precise reproducibility, but high setup overhead. Rejected: local VM sufficient for hackathon; Docker added post-project.

**Implementation**:
- Local VM setup documented in quickstart.md with exact Ubuntu 22.04 + ROS 2 Humble versions
- Each code example includes minimal setup script to verify runtime dependencies
- CI/CD pipeline (GitHub Actions) runs same examples post-commit
- Test harness: pytest for Python examples, CMake for C++ examples
- Pass criteria: Zero runtime errors, expected output matching, <10 sec execution time

**Test Environment**:
```
Host: Local development machine or shared lab VM
OS: Ubuntu 22.04 LTS
ROS 2: Humble LTS
Gazebo: 11+
Python: 3.10+
C++: 17 (g++ 9.4+)
```

**Risk**:
- CI/CD environment drift from local VM → examples pass locally, fail in CI
- Mitigation: Version lock all dependencies; document exact versions; test CI/CD config early (Week 1)

---

## Research Task 3: Peer-Review Checklist & Expert Review Workflow

**Question**: Will expert reviewer availability block content publication?

**Decision** (from Clarifications, Q1): Flexible pool (2-3 experts) + peer-review fallback checklist

**Rationale**:
- Expert review is critical gate (95%+ accuracy required before RAG indexing)
- Single expert reviewer = bottleneck if unavailable
- Flexible pool of 2-3 roboticists (different expertise areas) enables load balancing
- Peer-review fallback: structured checklist allows another writer/engineer to review if expert unavailable (e.g., during weekends or time-zone delays)
- Staggered module reviews (Expert reviews Module 1 while writer works on Module 2) reduces blocking

**Alternatives Considered**:
- **Single expert, sequential review**: High risk of blocking. Rejected.
- **Automated accuracy check only**: LLMs can miss domain-specific errors. Rejected: human expert essential.
- **No fallback**: Relies entirely on expert availability. Rejected: unreliable.

**Implementation**:
- **Expert Pool**: Identify 2-3 roboticists (each with deep knowledge in 1-2 modules)
  - Module 1: Humanoid robotics fundamentals expert
  - Module 2: ROS 2 / software architecture expert
  - Module 3: Control systems / kinematics expert
  - Module 4: Applications / industry expert (can overlap with Module 1 expert)
- **Expert Review Checklist** (primary):
  ```
  Fact Accuracy:
  - [ ] All technical claims traceable to official docs (ROS 2, Gazebo, Isaac Sim)
  - [ ] Mathematical formulas verified against standard textbooks (Siciliano et al.)
  - [ ] Hardware specs match official manufacturer datasheets
  - [ ] Code examples execute without errors on specified platform

  Clarity:
  - [ ] Terminology consistent throughout module
  - [ ] Explanations appropriate for target audience (undergrad/early pro)
  - [ ] No jargon without definition

  Completeness:
  - [ ] All code examples present and working
  - [ ] References complete and accessible
  - [ ] Learning objectives addresses in chapter content

  Issues Log:
  - [ ] Critical (blocker): factual error or broken code
  - [ ] Major: significant clarity issue, incomplete example
  - [ ] Minor: typo, formatting, minor accuracy adjustment
  ```
- **Peer-Review Checklist** (fallback, if expert unavailable):
  ```
  Checklist from above (Fact Accuracy, Clarity, Completeness), evaluated by writer + engineer
  SLA: If expert unavailable >24 hrs, peer review can proceed
  Result: "Approved with peer review (expert review pending)" or "Flagged for expert review"
  ```
- **Review SLA**: Expert review completed within 24-48 hours of submission
- **Fallback SLA**: If expert unavailable, peer review completed within 12-24 hours

**Risk**:
- Expert review delays → indexing delay
- Mitigation: Flexible pool reduces single-point-of-failure; fallback checklist provides safety net

---

## Research Task 4: RAG Indexing Integration & Metadata Schema

**Question**: When can Module 1 content be indexed into RAG chatbot?

**Decision** (from Clarifications, Q3): Module 1 pilot Week 1; verify pipeline works end-to-end before rolling out Modules 2-4

**Rationale**:
- RAG chatbot is external dependency (Spec 001)
- Unknown: Is RAG indexing pipeline production-ready? Can it handle textbook-scale content (52,000 words)?
- Module 1 pilot approach:
  - Complete Module 1 (5 chapters, 12,000 words, 15 code examples) by end of Week 1
  - Index into Qdrant (vector store)
  - Test RAG chatbot retrieval: Can it answer questions about Module 1? Are citations correct?
  - If successful: Modules 2-4 proceed with confidence
  - If issues detected: Remediate RAG pipeline before indexing Module 2

**Alternatives Considered**:
- **Index all modules end of Week 4**: Simplifies indexing logistics but creates risk—if RAG pipeline broken Week 4, no time to fix. Rejected.
- **Index no modules**: Skip RAG integration until post-hackathon. Rejected: misses chatbot validation goal.

**Implementation**:
- **Module 1 Indexing Timeline**:
  - Chapters 1-5 complete and reviewed: end of Week 1 (day 7)
  - All 15 code examples verified in CI/CD: day 7
  - Submit Module 1 for RAG indexing: day 8-9
  - RAG pipeline ingests, generates embeddings, stores in Qdrant: day 9-10
  - Validation: Run 10 sample queries on chatbot (e.g., "What is forward kinematics?") → expect >80% relevance
  - Status: "Module 1 indexing complete & validated" or "Issues detected, awaiting pipeline fixes"

- **Metadata Schema for RAG**:
  ```json
  {
    "chapter_id": "chapter_01",
    "module": 1,
    "chapter_number": 1,
    "title": "What is a Humanoid Robot?",
    "section": "Introduction",  // optional, for sub-chapter indexing
    "content": "...",
    "word_count": 2300,
    "learning_objectives": ["...", "..."],
    "keywords": ["humanoid", "robot", "history"],
    "code_examples": ["chapter_01_example_01", "chapter_01_example_02"],
    "references": ["ref_001", "ref_002"],
    "difficulty_level": "beginner",
    "source": "textbook/chapters/01-what-is-humanoid-robotics.md",
    "indexed_date": "2026-02-09",
    "version": "1.0"
  }
  ```

- **Retrieval Validation**:
  Sample query set for Module 1:
  1. "What is a humanoid robot?"
  2. "Explain forward kinematics"
  3. "What are the main sensors used in humanoid robots?"
  4. "How does a robot balance?"
  5. "What is an IMU?"
  (Expect >80% of answers cite Module 1 content)

**Risk**:
- RAG pipeline not ready by Week 1 → Module 1 cannot be indexed on schedule
- Mitigation: Coordinate with Spec 001 team early; verify indexing readiness before Week 1; fallback: defer Module 1 indexing to Week 2 (minor delay, no content impact)

---

## Research Task 5: Reference Management & Citation Standards

**Question**: How to maintain accurate, consistent citations across 22 chapters?

**Decision**: Centralized reference database (references.json) + APA citation standard

**Rationale**:
- Specification requires "all claims traceable to official docs with version info"
- Centralized reference database → single source of truth for citations
- APA format → standard in academic/professional settings; easy to convert to HTML/PDF later
- Each chapter includes references section linking to database → avoids duplication

**Alternatives Considered**:
- **Inline citations (BibTeX)**: Allows per-file bibliography but harder to deduplicate. Rejected.
- **Manual references per chapter**: High duplication risk, harder to audit accuracy. Rejected.

**Implementation**:
- **references.json** (centralized):
  ```json
  {
    "ref_001": {
      "type": "official_docs",
      "title": "ROS 2 Humble Documentation",
      "url": "https://docs.ros.org/en/humble/",
      "accessed_date": "2026-01-31",
      "version": "Humble"
    },
    "ref_002": {
      "type": "textbook",
      "title": "Robotics: Modelling, Planning and Control",
      "authors": "Siciliano, B., Sciavicco, L., Villani, L., Oriolo, G.",
      "year": 2010,
      "publisher": "Springer",
      "edition": 1
    },
    "ref_003": {
      "type": "datasheet",
      "title": "Sensor XYZ Technical Specs",
      "manufacturer": "Company Inc.",
      "part_number": "ABC-123",
      "url": "https://example.com/datasheet.pdf",
      "accessed_date": "2026-01-31"
    }
  }
  ```

- **Citation Format in Chapters** (APA):
  - Inline: (Siciliano et al., 2010)
  - Chapter references section: Full APA format with URL + access date

- **Verification**:
  - Expert review includes spot-check: are cited sources actually referenced?
  - CI/CD can validate URLs (200 status code) + parse APA format

**Risk**:
- URLs rot over time → references become outdated post-hackathon
- Mitigation: Capture access dates; prioritize official docs (stable URLs); use archived links where possible

---

## Summary: Research Outputs

| Unknown | Clarification | Research Output |
|---------|---------------|-----------------|
| **Writer Productivity** | Solo 2,000-2,500 wds/day for Modules 1-3; Module 4 deferrable | Timeline validated; chapter template design specified in plan.md |
| **Code Verification** | Local VM + CI/CD split | Test environment spec + CI/CD config framework defined in plan.md |
| **Expert Review Bottleneck** | Flexible pool (2-3 experts) + peer-review fallback | Checklist templates created; review SLA defined; fallback workflow documented |
| **RAG Integration Timing** | Module 1 pilot Week 1 validation | Metadata schema defined; retrieval validation checklist created; risk mitigation documented |
| **Citation Management** | Centralized references.json + APA format | Reference schema designed; inline citation format specified; validation approach documented |

---

## Gates: Ready for Phase 1 Design

✅ **All 5 research tasks complete**
✅ **No NEEDS CLARIFICATION items remaining**
✅ **Unknowns resolved; assumptions validated**
✅ **Proceed to Phase 1: Design & Contracts** (data-model.md, contracts/, quickstart.md)

---

**Status**: Phase 0 Research Complete | Ready for Phase 1 Design

