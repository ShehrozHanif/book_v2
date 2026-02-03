# Phase 3: User Story 1 - Module 1 Fundamentals - Quick Start

**Timeline**: Week 1 (7 days)
**Goal**: Write 5 foundational chapters (12,000 words, 15 code examples)
**Status**: Ready to begin ✅

---

## 📋 Phase 3 Overview

### Deliverables
- 5 chapters (2,300-2,400 words each)
- 15 code examples (Python, C++, URDF)
- Expert review completed (95%+ accuracy)
- RAG indexing validated

### Tasks (18 total)
- **T018-T022**: Write 5 chapters (can run in parallel [P])
- **T023-T027**: Create 15 code examples (can run in parallel [P])
- **T028-T030**: Test and validate code/word count
- **T031-T035**: Review, metadata generation, RAG indexing

### Success Criteria
- ✅ All 5 chapters complete (12,000 words ±200)
- ✅ All 15 code examples tested on Ubuntu 22.04 + ROS 2 Humble
- ✅ Expert review passed (95%+ accuracy)
- ✅ RAG retrieval validated (>80% relevance)

---

## 🚀 Getting Started

### Prerequisites
Before starting Phase 3, confirm:

```bash
# 1. Environment setup (from WRITER_ONBOARDING.md)
cd textbook
cat WRITER_ONBOARDING.md
# ✅ Complete all 5 phases

# 2. Verify scripts are executable
cd ../scripts
ls -la *.sh
chmod +x *.sh

# 3. Create test chapter (practice run)
./create-chapter.sh --id 99 --module "Test" --title "Test Chapter"
```

### Verify Scripts Work
```bash
# Test the automation
cd scripts

# List chapters
ls ../textbook/chapters/

# Test word count script
./verify-word-count.sh --all

# Test code example harness (should pass/skip gracefully with empty dir)
./test-code-examples.sh --all
```

---

## 📝 Chapter Writing Workflow

### Step 1: Create Chapter File
```bash
cd scripts
./create-chapter.sh --id 01 --module "Module 1" --title "What is a Humanoid Robot?"
# Creates: ../textbook/chapters/01-what-is-humanoid-robotics.md
```

### Step 2: Write Chapter Content
Edit `textbook/chapters/01-what-is-humanoid-robotics.md`:
- Add learning objectives
- Write sections (history, paradigms, applications, principles)
- Reference code examples
- Add citations

**Template Structure** (from phase 1):
```markdown
# Chapter 1: What is a Humanoid Robot?

## Learning Objectives
- Understand humanoid robot definition
- Identify key design paradigms
- Recognize applications in industry
- Grasp biomimetic principles

## Introduction
[Content...]

## Section 1: History & Evolution
[Content...]

## Section 2: Design Paradigms
[Content...]

## Code Examples
Refer to:
- `chapter_01_example_01.urdf`: Simple URDF robot definition
- `chapter_01_example_02.py`: Platform specifications script

## References
See [references.json](../metadata/references.json) for full citations
- [1] Author (Year)
- [2] Author (Year)
```

### Step 3: Create Code Examples
```bash
cd textbook/code-examples

# Example 1: URDF file (chapter_01_example_01.urdf)
# - Define a simple humanoid robot structure
# - Document each link and joint
# - Test with URDF parser

# Example 2: Python script (chapter_01_example_02.py)
# - Display platform specifications
# - Import ROS 2 libraries
# - Include docstring with expected output
# - Test locally with: python3 chapter_01_example_02.py
```

### Step 4: Verify Word Count
```bash
cd scripts
./verify-word-count.sh --file ../textbook/chapters/01-what-is-humanoid-robotics.md

# Output should show:
# Word count: 2,345 words
# Target: 2,300-2,400 words
# Status: ✅ PASS
```

### Step 5: Test Code Examples
```bash
cd scripts
./test-code-examples.sh --chapter 01

# Runs:
# - Python examples via pytest
# - URDF validation
# - Any C++ examples via CMake

# Should output:
# ✅ chapter_01_example_01.urdf PASS
# ✅ chapter_01_example_02.py PASS
```

### Step 6: Add References
```bash
# Edit textbook/metadata/references.json
# Add APA-formatted citations:
{
  "references": [
    {
      "id": "ref_001",
      "author": "Siciliano, B.",
      "year": 2016,
      "title": "Robotics: Modelling, Planning and Control",
      "source": "Springer",
      "url": "https://example.com"
    }
  ]
}

# Validate references
cd scripts
./validate-references.sh --chapter ../textbook/chapters/01-what-is-humanoid-robotics.md
```

---

## 📊 Phase 3 Task Breakdown

### Writing Tasks (T018-T022) [P = Parallel]
```
T018 [P] Chapter 1: What is a Humanoid Robot? (2,300 words)
         Topics: History, paradigms, applications, biomimetics
         Code: URDF example, platform specs script

T019 [P] Chapter 2: Kinematics Basics (2,300 words)
         Topics: Forward/inverse kinematics, joint frames, matrices
         Code: Kinematics solver, IK demo

T020 [P] Chapter 3: Dynamics & Motion (2,400 words)
         Topics: Forces, torque, balance, walking basics
         Code: Gazebo simulation, balance calculator

T021 [P] Chapter 4: Sensors & Perception (2,400 words)
         Topics: IMU, vision, tactile sensors, odometry
         Code: IMU subscriber, sensor visualization

T022 [P] Chapter 5: Hardware Overview (2,300 words)
         Topics: Motors, actuators, power distribution
         Code: Motor control (C++), power monitoring
```

**Timeline**: Days 1-4 (parallel execution)

### Code Example Tasks (T023-T027) [P = Parallel]
```
T023 [P] Chapter 1: URDF + Python script (2 examples)
T024 [P] Chapter 2: Forward/inverse kinematics (2 examples)
T025 [P] Chapter 3: Gazebo + balance solver (2 examples)
T026 [P] Chapter 4: ROS 2 IMU + visualization (2 examples)
T027 [P] Chapter 5: C++ motor control + power monitor (2 examples)
```

**Timeline**: Days 2-5 (parallel with writing)

### Testing & Validation (T028-T030)
```
T028 Test all 15 code examples
     - Command: ./test-code-examples.sh --all
     - Target: 100% pass rate

T029 Add 15-20 references to references.json
     - Validate APA format
     - Command: ./validate-references.sh --all

T030 Verify word count for all 5 chapters
     - Command: ./verify-word-count.sh --all
     - Target: 12,000 ±200 words total
```

**Timeline**: Day 6 (validation day)

### Review & Indexing (T031-T035)
```
T031 Submit Module 1 for expert review
     - Create PR with title: "Module 1: Fundamentals - Ready for Expert Review"
     - Include: chapters, code examples, reference list

T032 Incorporate expert review feedback
     - Address flagged issues
     - Re-test modified code
     - Update references

T033 Generate RAG metadata
     - Command: ./generate-rag-metadata.sh --all
     - Creates: metadata records for 5 chapters

T034 Submit for RAG indexing (to Spec 001 team)
     - Coordinate with: Spec 001 (RAG chatbot)
     - Confirm: embeddings generated

T035 Validate RAG retrieval
     - Run 10 sample queries
     - Confirm: >80% relevance
     - Document: retrieval results
```

**Timeline**: Days 6-7 (review, metadata, handoff)

---

## 🛠️ Useful Commands

### Create a Chapter
```bash
cd scripts
./create-chapter.sh --id 01 --module "Module 1" --title "What is a Humanoid Robot?"
```

### Test Code Examples
```bash
cd scripts
./test-code-examples.sh --chapter 01       # Test chapter 1 only
./test-code-examples.sh --all              # Test all chapters
./test-code-examples.sh --lang python      # Test Python only
```

### Verify Word Count
```bash
cd scripts
./verify-word-count.sh --file ../textbook/chapters/01-what-is-humanoid-robotics.md
./verify-word-count.sh --all                # All chapters
```

### Generate RAG Metadata
```bash
cd scripts
./generate-rag-metadata.sh --chapter ../textbook/chapters/01-what-is-humanoid-robotics.md
./generate-rag-metadata.sh --all            # All chapters
```

### Validate References
```bash
cd scripts
./validate-references.sh --chapter ../textbook/chapters/01-what-is-humanoid-robotics.md
./validate-references.sh --all              # All chapters
./validate-references.sh --all --check-urls # Also check URLs (slower)
```

---

## 📁 File Locations

```
textbook/
├── chapters/
│   ├── 01-what-is-humanoid-robotics.md     (T018)
│   ├── 02-kinematics-basics.md              (T019)
│   ├── 03-dynamics-motion.md                (T020)
│   ├── 04-sensors-perception.md             (T021)
│   └── 05-hardware-overview.md              (T022)
├── code-examples/
│   ├── chapter_01_example_01.urdf           (T023)
│   ├── chapter_01_example_02.py
│   ├── chapter_02_example_01.py             (T024)
│   ├── chapter_02_example_02.py
│   ├── chapter_03_example_01.py             (T025)
│   ├── chapter_03_example_02.py
│   ├── chapter_04_example_01.py             (T026)
│   ├── chapter_04_example_02.py
│   ├── chapter_05_example_01.cpp            (T027)
│   └── chapter_05_example_02.py
├── metadata/
│   ├── references.json                      (T029)
│   └── module-index.json                    (T033)
└── REVIEW_PROCESS.md                        (T031 reference)

scripts/
├── create-chapter.sh                        (Setup)
├── test-code-examples.sh                    (T028)
├── verify-word-count.sh                     (T030)
├── generate-rag-metadata.sh                 (T033)
└── validate-references.sh                   (T029)
```

---

## ⚠️ Common Issues & Troubleshooting

### Issue: Chapter file not created
```bash
# Check script is executable
chmod +x scripts/create-chapter.sh

# Check arguments
./scripts/create-chapter.sh --help

# Try again
./scripts/create-chapter.sh --id 01 --module "Module 1" --title "What is a Humanoid Robot?"
```

### Issue: Code example tests failing
```bash
# Check environment
python3 --version              # Should be 3.10+
which ros2                      # Should exist
which cmake                     # For C++ examples

# Run individual test
cd textbook/code-examples
python3 chapter_01_example_02.py

# Check for errors
cat chapter_01_example_02.py    # Review code
```

### Issue: Word count not validating
```bash
# Check file exists
ls -la textbook/chapters/01-what-is-humanoid-robotics.md

# Manually count words
wc -w textbook/chapters/01-what-is-humanoid-robotics.md

# Check markdown syntax (no broken code blocks)
head -50 textbook/chapters/01-what-is-humanoid-robotics.md
```

### Issue: References not found
```bash
# Check references.json exists
ls -la textbook/metadata/references.json

# Check format (valid JSON)
cat textbook/metadata/references.json | python3 -m json.tool

# Add missing references
# See textbook/STYLE_GUIDE.md for APA format
```

---

## ✅ Phase 3 Checklist

### Before Starting
- [ ] Phase 2 complete (all scripts/docs exist)
- [ ] Environment setup verified (WRITER_ONBOARDING.md)
- [ ] Scripts executable (chmod +x *.sh)
- [ ] Test chapter created and validated

### Writing Phase (Days 1-4)
- [ ] T018: Chapter 1 written (2,300 words)
- [ ] T019: Chapter 2 written (2,300 words)
- [ ] T020: Chapter 3 written (2,400 words)
- [ ] T021: Chapter 4 written (2,400 words)
- [ ] T022: Chapter 5 written (2,300 words)

### Code Examples Phase (Days 2-5)
- [ ] T023: Chapter 1 code examples created (2 examples)
- [ ] T024: Chapter 2 code examples created (2 examples)
- [ ] T025: Chapter 3 code examples created (2 examples)
- [ ] T026: Chapter 4 code examples created (2 examples)
- [ ] T027: Chapter 5 code examples created (2 examples)

### Testing Phase (Day 6)
- [ ] T028: All 15 code examples pass tests
- [ ] T029: All 15-20 references added and validated
- [ ] T030: Word count verified (12,000 ±200 words total)

### Review & Indexing Phase (Days 6-7)
- [ ] T031: Module 1 submitted for expert review (PR created)
- [ ] T032: Expert review feedback incorporated
- [ ] T033: RAG metadata generated
- [ ] T034: Module 1 submitted for RAG indexing
- [ ] T035: RAG retrieval validated (10 sample queries)

---

## 🎯 Success Criteria

**Acceptance Scenarios**:
- ✅ All 5 chapters complete (12,000 words ±200)
- ✅ All 15 code examples tested locally on Ubuntu 22.04 + ROS 2 Humble, pass CI/CD pipeline
- ✅ Expert review completed; 95%+ accuracy audit score
- ✅ All chapters indexed into Qdrant; chatbot retrieval validated (>80% relevance)

**Checkpoint**: Module 1 complete, approved, indexed, and RAG-validated by end of Week 1; chatbot can answer fundamental questions

---

## 📞 Questions or Issues?

- Review process: See `textbook/REVIEW_PROCESS.md`
- Writer onboarding: See `textbook/WRITER_ONBOARDING.md`
- Spec details: See `specs/002-content-writing/spec.md`
- Implementation plan: See `specs/002-content-writing/plan.md`
- All tasks: See `specs/002-content-writing/tasks.md`

---

**Ready to begin? Start with:**
```bash
cd scripts
./create-chapter.sh --id 01 --module "Module 1" --title "What is a Humanoid Robot?"
```

Good luck! 🚀
