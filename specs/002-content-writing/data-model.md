# Data Model: Content Writing & Book Modules

**Date**: 2026-01-31 | **Branch**: `002-content-writing` | **Phase**: 1

---

## Overview

This document defines the core entities, relationships, and validation rules for the textbook content system. The data model supports writing, verification, review, and RAG indexing workflows.

---

## Core Entities

### 1. Module

Represents a major thematic collection of chapters.

```json
{
  "id": "module_01",
  "number": 1,
  "title": "Fundamentals of Humanoid Robotics",
  "description": "Core concepts: what is humanoid, kinematics, dynamics, sensors, hardware",
  "chapter_count": 5,
  "target_word_count": 12000,
  "chapters": ["chapter_01", "chapter_02", "chapter_03", "chapter_04", "chapter_05"],
  "status": "draft|in_progress|review|approved|indexed",
  "created_date": "2026-01-31",
  "target_publication_date": "2026-02-07",
  "expert_reviewer_id": "reviewer_001",
  "metadata": {
    "difficulty_level": "beginner",
    "target_audience": "undergraduate/early professional",
    "prerequisites": "basic calculus, linear algebra, physics, programming"
  }
}
```

**Fields**:
- `id`: Unique identifier (module_01-04)
- `number`: Sequential module number (1-4)
- `title`: Human-readable title
- `description`: 1-2 sentence overview
- `chapter_count`: Number of chapters in module
- `target_word_count`: Expected total word count
- `chapters`: Array of chapter IDs in order
- `status`: Workflow state (see validation rules below)
- `created_date`: ISO 8601 date
- `target_publication_date`: Expected completion date
- `expert_reviewer_id`: Assigned reviewer ID
- `metadata`: Additional attributes (difficulty, audience, prerequisites)

**Relationships**:
- Module → Chapters (1:many)
- Module → Expert Reviewer (1:1)

**Validation Rules**:
- `chapter_count` must match length of `chapters` array
- `target_word_count` must equal sum of chapter `target_word_count` values
- `status` transitions: draft → in_progress → review → approved → indexed (unidirectional)
- `target_publication_date` must be ≥ `created_date`

---

### 2. Chapter

Represents a single topic/lesson within a module.

```json
{
  "id": "chapter_01",
  "number": 1,
  "module_id": "module_01",
  "title": "What is a Humanoid Robot?",
  "file_path": "textbook/chapters/01-what-is-humanoid-robotics.md",
  "word_count": 2300,
  "target_word_count": 2300,
  "learning_objectives": [
    "Understand the history of humanoid robotics",
    "Identify key design paradigms",
    "Recognize real-world applications"
  ],
  "sections": [
    {
      "heading": "Introduction",
      "subsections": [],
      "word_count": 400
    },
    {
      "heading": "History of Humanoid Robots",
      "subsections": [
        "Early Research Era (1960s-2000s)",
        "Modern Platforms (2000s-Present)"
      ],
      "word_count": 800
    },
    {
      "heading": "Design Paradigms & Biomimetics",
      "subsections": [],
      "word_count": 600
    },
    {
      "heading": "Real-World Applications",
      "subsections": [],
      "word_count": 500
    }
  ],
  "code_examples": [
    "chapter_01_example_01",
    "chapter_01_example_02"
  ],
  "references": [
    "ref_001",
    "ref_002",
    "ref_003"
  ],
  "status": "draft|written|review|approved|indexed",
  "accuracy_score": null,
  "review_status": "pending|expert_review|peer_review|approved|flagged",
  "created_date": "2026-01-31",
  "reviewed_date": null,
  "indexed_date": null,
  "reviewer_notes": ""
}
```

**Fields**:
- `id`: Unique identifier (chapter_01-22)
- `number`: Sequential chapter number (1-22)
- `module_id`: Parent module ID
- `title`: Chapter title
- `file_path`: Markdown file location
- `word_count`: Actual word count (filled during writing)
- `target_word_count`: Target word count from spec
- `learning_objectives`: Array of LO strings (3-5 per chapter)
- `sections`: Hierarchical outline with subsection metadata
- `code_examples`: Array of code example IDs referenced in chapter
- `references`: Array of reference IDs (citations)
- `status`: Writing workflow state
- `accuracy_score`: Numeric score 0-100 from expert review (null until reviewed)
- `review_status`: Review workflow state
- `created_date`: ISO 8601 creation date
- `reviewed_date`: ISO 8601 review completion date
- `indexed_date`: ISO 8601 RAG indexing date
- `reviewer_notes`: Feedback from expert/peer reviewer

**Relationships**:
- Chapter → Module (N:1)
- Chapter → Code Examples (1:many)
- Chapter → References (1:many)

**Validation Rules**:
- `number` must match position in module's `chapters` array
- `module_id` must reference valid module
- `word_count` must be within ±10% of `target_word_count` (after final edit)
- `status` transitions: draft → written → review → approved → indexed (unidirectional)
- `review_status` transitions: pending → (expert_review OR peer_review) → approved OR flagged
- If `review_status` is "approved", `accuracy_score` must be ≥ 95
- All `code_examples` must reference valid code example IDs
- All `references` must reference valid reference IDs

---

### 3. CodeExample

Represents a runnable code snippet or file.

```json
{
  "id": "chapter_01_example_01",
  "chapter_id": "chapter_01",
  "number": 1,
  "title": "Simple Robot URDF Description",
  "description": "A basic URDF file defining a simple humanoid robot structure with links and joints",
  "language": "urdf",
  "file_path": "textbook/code-examples/chapter_01_example_01.urdf",
  "content_hash": "abc123def456",
  "lines_of_code": 45,
  "execution_time_sec": 0,
  "status": "draft|written|tested|verified",
  "test_status": "untested|passed|failed",
  "test_environment": "ubuntu_22.04_ros2_humble",
  "test_result": {
    "passed": true,
    "execution_time_sec": 1.5,
    "stdout": "URDF parsing successful...",
    "stderr": "",
    "exit_code": 0
  },
  "dependencies": [
    "ros2",
    "urdf_parser",
    "python3.10"
  ],
  "version_notes": "ROS 2 Humble compatible; requires URDF parser >= 2.0",
  "created_date": "2026-01-31",
  "tested_date": null
}
```

**Fields**:
- `id`: Unique identifier (chapter_XX_example_YY format)
- `chapter_id`: Parent chapter ID
- `number`: Sequential example number within chapter
- `title`: Short descriptive title
- `description`: 1-2 sentence explanation of what the example demonstrates
- `language`: Code language (python, cpp, urdf, yaml, bash, etc.)
- `file_path`: File location in repository
- `content_hash`: SHA256 of file content (for change detection)
- `lines_of_code`: Number of lines (excluding comments/blanks)
- `execution_time_sec`: Time to run (0 if non-executable, e.g., URDF)
- `status`: Writing/testing workflow state
- `test_status`: Result of most recent test (passed/failed/untested)
- `test_environment`: Environment string (ubuntu_22.04_ros2_humble, etc.)
- `test_result`: Object with detailed test output (passed, time, stdout, stderr, exit_code)
- `dependencies`: Array of runtime dependencies (language, libraries, tools)
- `version_notes`: Version constraints and compatibility info
- `created_date`: ISO 8601 creation date
- `tested_date`: ISO 8601 last test date

**Relationships**:
- CodeExample → Chapter (N:1)
- CodeExample → Test Results (1:many, historical)

**Validation Rules**:
- `id` must follow naming convention: chapter_XX_example_YY
- `language` must be one of: python, cpp, urdf, yaml, bash, latex
- `file_path` must start with textbook/code-examples/
- If `language` is executable (python, cpp, bash), `test_status` must be "passed" before chapter can be approved
- If `language` is non-executable (urdf, yaml, latex), `test_status` can be "untested" (not run)
- All `dependencies` must be explicitly listed

---

### 4. Reference

Represents a source citation used in chapters.

```json
{
  "id": "ref_001",
  "type": "official_docs|textbook|paper|datasheet|website|software",
  "title": "ROS 2 Humble Documentation",
  "url": "https://docs.ros.org/en/humble/",
  "version": "Humble LTS",
  "accessed_date": "2026-01-31",
  "authors": null,
  "year": null,
  "publisher": null,
  "edition": null,
  "doi": null,
  "apa_format": "ROS 2 Documentation. (2024). ROS 2 Humble. Retrieved from https://docs.ros.org/en/humble/",
  "usage_count": 5,
  "chapters_cited": [
    "chapter_01",
    "chapter_02",
    "chapter_06",
    "chapter_08"
  ]
}
```

**Fields**:
- `id`: Unique identifier (ref_001-NNN)
- `type`: Reference category
- `title`: Source title
- `url`: Web URL (if applicable)
- `version`: Version/edition info
- `accessed_date`: ISO 8601 access date
- `authors`: Array of author names (if textbook/paper)
- `year`: Publication year
- `publisher`: Publisher name
- `edition`: Edition number
- `doi`: Digital Object Identifier
- `apa_format`: Pre-formatted APA citation string
- `usage_count`: How many chapters reference this
- `chapters_cited`: Array of chapter IDs that cite this reference

**Relationships**:
- Reference → Chapters (1:many)

**Validation Rules**:
- `type` must be one of the enumerated values
- `apa_format` must be valid APA citation
- `chapters_cited` must reference valid chapter IDs
- If `type` is "official_docs" or "website", `url` is required
- If `type` is "textbook" or "paper", `authors`, `year`, `publisher` are required
- `usage_count` must equal length of `chapters_cited`

---

### 5. Review

Represents an expert or peer review of a chapter.

```json
{
  "id": "review_001",
  "chapter_id": "chapter_01",
  "reviewer_id": "reviewer_001",
  "review_type": "expert|peer",
  "submitted_date": "2026-02-02",
  "completed_date": "2026-02-03",
  "accuracy_score": 96,
  "clarity_score": 94,
  "completeness_score": 98,
  "overall_score": 96,
  "status": "approved|needs_revision|flagged",
  "flagged_issues": [
    {
      "id": "issue_001",
      "line": 42,
      "severity": "minor",
      "category": "typo|clarity|accuracy|code_example|reference",
      "description": "Missing space in 'kinematics' spelling",
      "suggested_fix": "Change 'kinmatics' to 'kinematics'"
    }
  ],
  "comment": "Chapter is well-structured with clear explanations. Code examples are correct. One minor typo found and noted above."
}
```

**Fields**:
- `id`: Unique review identifier (review_001-NNN)
- `chapter_id`: Chapter being reviewed
- `reviewer_id`: Reviewer identifier
- `review_type`: expert or peer
- `submitted_date`: ISO 8601 submission date
- `completed_date`: ISO 8601 completion date
- `accuracy_score`: 0-100 numeric score
- `clarity_score`: 0-100 numeric score
- `completeness_score`: 0-100 numeric score
- `overall_score`: Weighted average of three scores
- `status`: Outcome of review (approved, needs_revision, flagged)
- `flagged_issues`: Array of issue objects
- `comment`: Free-form reviewer feedback

**Issue Object Fields**:
- `id`: Unique issue identifier within review
- `line`: Line number in markdown file (if applicable)
- `severity`: critical|high|medium|low
- `category`: typo, clarity, accuracy, code_example, reference
- `description`: Detailed issue description
- `suggested_fix`: Proposed resolution (optional)

**Relationships**:
- Review → Chapter (N:1)
- Review → Reviewer (N:1)

**Validation Rules**:
- `review_type` must be "expert" or "peer"
- If `review_type` is "expert", `accuracy_score` minimum must be ≥ 90 to approve
- If `review_type` is "peer", `accuracy_score` minimum must be ≥ 85 to approve
- All scores must be 0-100
- `overall_score` = (accuracy_score + clarity_score + completeness_score) / 3
- If any `flagged_issues` have severity "critical" or "high", `status` must be "flagged" or "needs_revision"
- `completed_date` must be ≥ `submitted_date`

---

## Relationships & Workflows

### Writing Workflow

```
Module (draft)
  → Chapter 1 (draft) → written → review
    → Review submitted (expert)
      → Review approved (accuracy_score ≥ 95)
        → Chapter status = approved
        → Proceed to indexing
      → Review flagged (accuracy_score < 95)
        → Author revises chapter
        → Re-submit for review
```

### Testing Workflow

```
CodeExample (draft)
  → written
    → tested (local VM)
      → passed → verified
        → Can be included in chapter for indexing
      → failed
        → Author debugs and re-tests
        → Repeat until passed
```

### Indexing Workflow

```
Module (approved)
  → All chapters approved
    → All code examples verified
      → Module status = ready_for_indexing
        → Index to Qdrant
          → Generate vector embeddings
            → Module status = indexed
            → Chatbot can retrieve content
```

---

## Entity Constraints

| Entity | Uniqueness | Cardinality | Ordering |
|--------|-----------|-------------|----------|
| Module | id, number | 4 | Sequential (1-4) |
| Chapter | id, number within module | 22 total, 5-6 per module | Sequential per module |
| CodeExample | id (chapter_XX_example_YY) | 66 total, 2-4 per chapter | Sequential per chapter |
| Reference | id | 50-100 expected | Unordered (cited as needed) |
| Review | id | Multiple per chapter (expert + peer) | Chronological per chapter |

---

## State Machines

### Chapter Status State Machine

```
draft → written → review → approved → indexed
  ↓       ↓        ↓         ↓
[creation] [authoring] [expert review] [RAG indexing]
```

**Transitions**:
- draft → written: Author completes initial draft
- written → review: Author submits for expert review
- review → approved: Expert review passes (accuracy_score ≥ 95)
- review → written: Expert review flags issues; author revises
- approved → indexed: Module ready; index to RAG
- approved → indexed: RAG ingestion and embedding generation complete

### CodeExample Test Status State Machine

```
untested → passed → (included in chapter)
    ↓         ↓
  failed → (debug & retry) → passed
```

**Transitions**:
- untested → passed: Initial test run succeeds
- untested → failed: Initial test run fails
- failed → untested: Author revises code, re-tests
- passed → (end state): Example approved for publication

---

## Derived Fields & Rollups

### Module Metrics

- `total_word_count`: Sum of all chapter word counts
- `total_code_examples`: Count of code examples across chapters
- `completion_percentage`: (sum of approved chapters / total chapters) * 100
- `average_accuracy_score`: Mean of chapter accuracy scores (null if no reviews yet)
- `ready_for_indexing`: true if all chapters approved AND all code examples verified

### Chapter Metrics

- `code_example_count`: Length of `code_examples` array
- `reference_count`: Length of `references` array
- `days_since_created`: Days between created_date and today
- `reviewer_assigned`: true if reviewer_id is non-null
- `can_be_indexed`: review_status == "approved" AND all code examples test_status == "passed"

---

## Validation Rules Summary

| Entity | Rule | Severity |
|--------|------|----------|
| Chapter | word_count within ±10% of target | Error |
| Chapter | accuracy_score ≥ 95 before indexing | Error |
| CodeExample | Executable examples must pass tests | Error |
| CodeExample | All dependencies listed | Error |
| Reference | APA format valid | Error |
| Reference | URL returns 200 OK (if web) | Warning |
| Module | total_word_count matches sum | Error |
| Review | scores 0-100 range | Error |

---

## Next Steps

1. Implement chapter template enforcing this schema (via YAML front matter)
2. Create code example test harness validating CodeExample entity fields
3. Implement review submission form enforcing Review entity structure
4. Build rollup queries for Module metrics dashboards

---

**Status**: Phase 1 Data Model Complete | Ready for Contracts and Quickstart

