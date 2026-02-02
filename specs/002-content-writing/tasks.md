# Tasks: Content Writing & Book Modules

**Input**: Design documents from `/specs/002-content-writing/`
**Prerequisites**: spec.md (5 user stories with priorities), plan.md (writer workflow, timeline), research.md (unknowns resolved), data-model.md (entities), quickstart.md (onboarding), contracts/ (schemas)

**Tests**: No automated tests requested in spec; all tasks focus on content writing, code example verification, expert review, and RAG indexing validation.

**Organization**: Tasks are grouped by user story (5 user stories) to enable independent implementation and testing. Foundational tasks (infrastructure setup, tooling) must complete before any writing begins. User stories proceed in priority order (P1 → P2 → P2 → P1) with parallel opportunities within each module.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different chapters, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, writer environment, and tooling

**Timeline**: Day 0 (before Week 1 writing begins)

- [x] T001 Create textbook directory structure in `textbook/` with subdirectories: `chapters/`, `code-examples/`, `metadata/`, `contracts/`

- [ ] T002 Create chapter template file at `textbook/chapters/_chapter-template.md` with learning objectives, sections, code examples, references structure (from plan.md §Phase 1)

- [ ] T003 [P] Create code examples README at `textbook/code-examples/README.md` with setup instructions, dependencies, how to run, expected output, troubleshooting

- [ ] T004 [P] Create centralized references database at `textbook/metadata/references.json` with empty structure for 50-100 APA-formatted references (from data-model.md)

- [ ] T005 [P] Create module metadata index at `textbook/metadata/module-index.json` with 4 module definitions (Module 1-4) including chapter counts, word count targets, status fields

- [ ] T006 Create code examples manifest at `textbook/metadata/code-examples-manifest.json` with mapping of 66 code examples to chapters (from spec.md §Code Examples Strategy)

- [ ] T007 Setup local development VM (Ubuntu 22.04 + ROS 2 Humble LTS + Gazebo 11) per quickstart.md §Prerequisites or document access to shared lab VM; create setup verification script

- [ ] T008 [P] Create CI/CD pipeline configuration for code example verification (GitHub Actions or equivalent) that tests all code examples against Ubuntu 22.04 + ROS 2 Humble environment

- [ ] T009 [P] Create peer-review checklist template at `textbook/metadata/peer-review-checklist.md` with sections: Fact Accuracy, Clarity, Completeness, Issues Log (from plan.md §Research Task 3)

- [ ] T010 [P] Create expert review template at `textbook/metadata/expert-review-template.json` schema matching Review entity from data-model.md (accuracy_score, clarity_score, completeness_score, flagged_issues)

**Checkpoint**: Textbook infrastructure ready; writer environment prepared; no write tasks blocked

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tools and processes that enable writing and verification

**⚠️ CRITICAL**: Writer onboarding and workflow automation must be complete before any chapter writing begins

- [ ] T011 Create chapter writing workflow automation script at `scripts/create-chapter.sh` that auto-generates chapter file from template, fills metadata headers (chapter_id, module, title), initializes code examples array

- [ ] T012 [P] Create code example testing harness at `scripts/test-code-examples.sh` that runs all Python examples via pytest, C++ examples via CMake/compiler, validates URDF/YAML syntax, outputs pass/fail per example

- [ ] T013 Create chapter word count verification script at `scripts/verify-word-count.sh` that counts words in each chapter markdown file, validates within ±10% of target (2300-2400 words), generates report

- [ ] T014 [P] Create RAG indexing metadata generator at `scripts/generate-rag-metadata.sh` that reads chapter files, extracts learning objectives, keywords, section headings, generates chapter-level metadata for Qdrant indexing (from plan.md §Phase 1)

- [ ] T015 Create expert review submission workflow documentation at `textbook/REVIEW_PROCESS.md` with steps: chapter submitted → expert assigned → review checklist completed → issues logged → approved for indexing (from plan.md §Risk Mitigation)

- [ ] T016 [P] Create reference validation script at `scripts/validate-references.sh` that checks all cited references exist in `references.json`, validates APA format, optionally validates URLs return 200 OK

- [ ] T017 Create writer onboarding checklist at `textbook/WRITER_ONBOARDING.md` based on quickstart.md, confirming: environment setup, ROS 2 installed, local testing successful, chapter template reviewed, workflow understood

**Checkpoint**: All infrastructure, scripts, and processes ready; writers can now begin content creation

---

## Phase 3: User Story 1 - Module 1 Fundamentals (Priority: P1) 🎯 MVP

**Goal**: Write 5 foundational chapters (12,000 words, 15 code examples) covering humanoid robotics basics. Module 1 serves as pilot for RAG indexing validation; completion by end of Week 1.

**Independent Test**: Module 1 can be indexed into RAG independently. Chatbot successfully answers 90%+ of queries about humanoid robotics basics using only Module 1 content.

**Acceptance Scenarios**:
- All 5 chapters complete (12,000 words) with 2-3 code examples each
- All 15 code examples tested locally on Ubuntu 22.04 + ROS 2 Humble, pass CI/CD pipeline
- Expert review completed; 95%+ accuracy audit score
- All chapters indexed into Qdrant; chatbot retrieval validated

### Implementation for User Story 1

- [ ] T018 [P] [US1] Write Chapter 1 "What is a Humanoid Robot?" (2,300 words) in `textbook/chapters/01-what-is-humanoid-robotics.md` with: history overview, design paradigms, applications, biomimetics principles; include 2-3 code examples references (URDF example, platform overview script)

- [ ] T019 [P] [US1] Write Chapter 2 "Kinematics Basics" (2,300 words) in `textbook/chapters/02-kinematics-basics.md` with: forward kinematics explanation, inverse kinematics algorithms, joint systems, link frames, worked examples with matrices

- [ ] T020 [P] [US1] Write Chapter 3 "Dynamics & Motion" (2,400 words) in `textbook/chapters/03-dynamics-motion.md` with: forces and torque concepts, balance mechanics, center of mass, walking motion basics

- [ ] T021 [P] [US1] Write Chapter 4 "Sensors & Perception" (2,400 words) in `textbook/chapters/04-sensors-perception.md` with: IMU sensor explanation, vision systems overview, tactile sensors, odometry concepts

- [ ] T022 [P] [US1] Write Chapter 5 "Hardware Overview" (2,300 words) in `textbook/chapters/05-hardware-overview.md` with: motor types, actuator systems, power distribution, mechanical design principles

- [ ] T023 [P] [US1] Create Chapter 1 code examples: `textbook/code-examples/chapter_01_example_01.urdf` (URDF file defining simple robot), `chapter_01_example_02.py` (Python script displaying platform specifications); test locally

- [ ] T024 [P] [US1] Create Chapter 2 code examples: `textbook/code-examples/chapter_02_example_01.py` (forward kinematics solver), `chapter_02_example_02.py` (inverse kinematics demo); test locally

- [ ] T025 [P] [US1] Create Chapter 3 code examples: `textbook/code-examples/chapter_03_example_01.py` (Gazebo dynamics simulation demo), `chapter_03_example_02.py` (balance calculation example); test locally

- [ ] T026 [P] [US1] Create Chapter 4 code examples: `textbook/code-examples/chapter_04_example_01.py` (ROS 2 IMU sensor subscriber), `chapter_04_example_02.py` (sensor data visualization); test locally

- [ ] T027 [P] [US1] Create Chapter 5 code examples: `textbook/code-examples/chapter_05_example_01.cpp` (motor control in C++), `chapter_05_example_02.py` (power system monitoring); test locally

- [ ] T028 [US1] Run all 15 Chapter 1-5 code examples through local test harness (`scripts/test-code-examples.sh`); confirm 100% pass rate on Ubuntu 22.04 + ROS 2 Humble; document any environment-specific setup

- [ ] T029 [US1] Add all references cited in Chapters 1-5 to `textbook/metadata/references.json` in APA format (expected: 15-20 references); validate with `scripts/validate-references.sh`

- [ ] T030 [US1] Run word count verification for Chapters 1-5 with `scripts/verify-word-count.sh`; confirm each chapter 2,300-2,400 words; total 12,000 words ±200

- [ ] T031 [US1] Submit Module 1 (5 chapters + 15 code examples) for expert review; create pull request to branch `002-content-writing` with title "Module 1: Fundamentals - Ready for Expert Review" and detailed summary

- [ ] T032 [US1] Incorporate expert review feedback on Module 1 (chapters and code examples); address all flagged issues; re-test any modified code examples; update references if accuracy audit requires clarification

- [ ] T033 [US1] Generate RAG indexing metadata for Module 1 using `scripts/generate-rag-metadata.sh`; create metadata records in `textbook/metadata/module-index.json` for each of 5 chapters with learning objectives, keywords, section headings

- [ ] T034 [US1] Submit Module 1 for RAG indexing into Qdrant; coordinate with Spec 001 team to confirm indexing complete and embeddings generated (by end of Week 1)

- [ ] T035 [US1] Validate Module 1 RAG retrieval: run 10 sample queries on RAG chatbot (e.g., "What is forward kinematics?", "How do sensors work?"); confirm >80% relevance of retrieved sections with citations to correct chapters; document retrieval validation results

**Checkpoint**: Module 1 complete, approved, indexed, and RAG-validated by end of Week 1; chatbot can answer fundamental questions

---

## Phase 4: User Story 2 - Module 2 ROS 2 & Architecture (Priority: P1)

**Goal**: Write 6 chapters on ROS 2 and software architecture (13,000 words, 18 code examples). Can begin Week 1 Day 3 in parallel with Module 1 review; target completion Week 2. Proceeds with confidence after Module 1 RAG pilot validates pipeline.

**Independent Test**: Module 2 can be indexed independently. Chatbot successfully answers 90%+ of queries about ROS 2 concepts, motion planning, and software architecture using only Module 2 content.

**Acceptance Scenarios**:
- All 6 chapters complete (13,000 words) with 3 code examples each
- All 18 code examples tested; 100% pass rate on Ubuntu 22.04 + ROS 2 Humble
- Expert review completed; 95%+ accuracy audit
- All chapters indexed into RAG

### Implementation for User Story 2

- [ ] T036 [P] [US2] Write Chapter 6 "ROS 2 Fundamentals" (2,300 words) in `textbook/chapters/06-ros2-fundamentals.md` with: nodes, topics, services, actions, parameter server; include code examples of publisher/subscriber patterns

- [ ] T037 [P] [US2] Write Chapter 7 "Robot Description & URDF" (2,300 words) in `textbook/chapters/07-urdf-robot-description.md` with: URDF structure, link definitions, joint types, visual/collision meshes, Gazebo plugins

- [ ] T038 [P] [US2] Write Chapter 8 "Simulation Environments" (2,300 words) in `textbook/chapters/08-simulation-gazebo-isaac.md` with: Gazebo 11 setup, Isaac Sim basics, launch files, physics simulation configuration

- [ ] T039 [P] [US2] Write Chapter 9 "Motion Planning" (2,300 words) in `textbook/chapters/09-motion-planning.md` with: path planning algorithms, RRT*, collision checking, MoveIt! framework overview

- [ ] T040 [P] [US2] Write Chapter 10 "Control Systems" (2,300 words) in `textbook/chapters/10-control-systems.md` with: PID control theory, trajectory following, joint-level commands, feedback loops

- [ ] T041 [P] [US2] Write Chapter 11 "Real-time Considerations" (2,300 words) in `textbook/chapters/11-realtime-performance.md` with: timing constraints, synchronization, performance tuning, profiling strategies

- [ ] T042 [P] [US2] Create Chapter 6 code examples: `textbook/code-examples/chapter_06_example_01.py` (ROS 2 publisher), `chapter_06_example_02.py` (ROS 2 subscriber), `chapter_06_example_03.py` (service client/server); test locally

- [ ] T043 [P] [US2] Create Chapter 7 code examples: `textbook/code-examples/chapter_07_example_01.urdf` (complete URDF example), `chapter_07_example_02.py` (URDF parser), `chapter_07_example_03.py` (mesh loading demo); test locally

- [ ] T044 [P] [US2] Create Chapter 8 code examples: `textbook/code-examples/chapter_08_example_01.yaml` (Gazebo launch config), `chapter_08_example_02.py` (Gazebo client API), `chapter_08_example_03.yaml` (Isaac Sim setup); test locally

- [ ] T045 [P] [US2] Create Chapter 9 code examples: `textbook/code-examples/chapter_09_example_01.py` (motion planning with MoveIt), `chapter_09_example_02.py` (collision checking), `chapter_09_example_03.py` (RRT path planner demo); test locally

- [ ] T046 [P] [US2] Create Chapter 10 code examples: `textbook/code-examples/chapter_10_example_01.py` (PID controller implementation), `chapter_10_example_02.cpp` (real-time control loop), `chapter_10_example_03.py` (trajectory generator); test locally

- [ ] T047 [P] [US2] Create Chapter 11 code examples: `textbook/code-examples/chapter_11_example_01.py` (timing profiler), `chapter_11_example_02.cpp` (real-time thread example), `chapter_11_example_03.py` (performance analysis); test locally

- [ ] T048 [US2] Run all 18 Chapter 6-11 code examples through CI/CD pipeline; confirm 100% pass rate on Ubuntu 22.04 + ROS 2 Humble (depends on T042-T047 completion)

- [ ] T049 [US2] Add all references cited in Chapters 6-11 to `textbook/metadata/references.json` in APA format (expected: 20-25 new references); validate with `scripts/validate-references.sh`

- [ ] T050 [US2] Run word count verification for Chapters 6-11 with `scripts/verify-word-count.sh`; confirm total 13,000 words ±200 (depends on T036-T041 completion)

- [ ] T051 [US2] Submit Module 2 for expert review; create pull request with title "Module 2: ROS 2 & Architecture - Ready for Expert Review"; expert review timeline: 24-48 hours

- [ ] T052 [US2] Incorporate expert review feedback on Module 2; address flagged issues; re-test modified code examples; confirm 95%+ accuracy audit

- [ ] T053 [US2] Generate RAG indexing metadata for Module 2; update `textbook/metadata/module-index.json` with all 6 chapter records

- [ ] T054 [US2] Submit Module 2 for RAG indexing (by end of Week 2); validate retrieval with 10 sample queries about ROS 2, motion planning, control

**Checkpoint**: Module 2 complete, approved, and indexed; RAG chatbot now covers both fundamentals and software architecture

---

## Phase 5: User Story 3 - Module 3 Control & Kinematics (Priority: P2)

**Goal**: Write 6 chapters on advanced control and kinematics (14,000 words, 18 code examples). Target Week 2-3. More technically advanced; assumes Modules 1-2 complete.

**Independent Test**: Module 3 querying via chatbot answers questions about kinematics algorithms, control hierarchies, locomotion with >90% relevance.

**Acceptance Scenarios**:
- All 6 chapters complete (14,000 words) with 3 code examples each
- All 18 code examples tested; 100% pass rate
- Expert review completed; 95%+ accuracy; math formulas verified against Siciliano et al.
- All chapters indexed into RAG

### Implementation for User Story 3

- [ ] T055 [P] [US3] Write Chapter 12 "Advanced Kinematics" (2,400 words) in `textbook/chapters/12-advanced-kinematics.md` with: DH parameters, Jacobian matrix, singularities, redundancy handling; include mathematical derivations

- [ ] T056 [P] [US3] Write Chapter 13 "Walking & Locomotion" (2,400 words) in `textbook/chapters/13-walking-locomotion.md` with: gait generation, stability margin, center of pressure, balance control algorithms

- [ ] T057 [P] [US3] Write Chapter 14 "Manipulation & Grasping" (2,400 words) in `textbook/chapters/14-manipulation-grasping.md` with: arm kinematics, end-effector frames, grasp planning, force control

- [ ] T058 [P] [US3] Write Chapter 15 "Whole-Body Control" (2,400 words) in `textbook/chapters/15-wholebody-control.md` with: multi-objective control, hierarchies, constraint handling, prioritized tasks

- [ ] T059 [P] [US3] Write Chapter 16 "Learning-Based Control" (2,400 words) in `textbook/chapters/16-learning-based-control.md` with: reinforcement learning basics, neural networks for control, imitation learning

- [ ] T060 [P] [US3] Write Chapter 17 "Debugging & Troubleshooting" (2,400 words) in `textbook/chapters/17-debugging-troubleshooting.md` with: common issues, diagnostics, logging strategies, performance profiling

- [ ] T061 [P] [US3] Create Chapter 12 code examples: `textbook/code-examples/chapter_12_example_01.py` (Jacobian computation), `chapter_12_example_02.py` (DH parameter transformation), `chapter_12_example_03.cpp` (kinematics solver); test locally

- [ ] T062 [P] [US3] Create Chapter 13 code examples: `textbook/code-examples/chapter_13_example_01.py` (gait pattern generator), `chapter_13_example_02.py` (balance controller), `chapter_13_example_03.py` (walking simulator); test locally

- [ ] T063 [P] [US3] Create Chapter 14 code examples: `textbook/code-examples/chapter_14_example_01.py` (grasp quality metrics), `chapter_14_example_02.py` (end-effector trajectory), `chapter_14_example_03.cpp` (force control); test locally

- [ ] T064 [P] [US3] Create Chapter 15 code examples: `textbook/code-examples/chapter_15_example_01.py` (hierarchical control architecture), `chapter_15_example_02.py` (constraint solver), `chapter_15_example_03.cpp` (QP solver integration); test locally

- [ ] T065 [P] [US3] Create Chapter 16 code examples: `textbook/code-examples/chapter_16_example_01.py` (RL agent for joint control), `chapter_16_example_02.py` (neural network inference), `chapter_16_example_03.py` (imitation learning); test locally

- [ ] T066 [P] [US3] Create Chapter 17 code examples: `textbook/code-examples/chapter_17_example_01.py` (logging utilities), `chapter_17_example_02.py` (performance profiler), `chapter_17_example_03.py` (common bug examples); test locally

- [ ] T067 [US3] Run all 18 Chapter 12-17 code examples through CI/CD pipeline; confirm 100% pass rate (depends on T061-T066)

- [ ] T068 [US3] Add all references (expected: 25-30 new) to `textbook/metadata/references.json`; validate with `scripts/validate-references.sh`

- [ ] T069 [US3] Verify word count for Chapters 12-17: total 14,000 words ±200 (depends on T055-T060)

- [ ] T070 [US3] Submit Module 3 for expert review; expert review timeline: 24-48 hours

- [ ] T071 [US3] Incorporate expert review feedback on Module 3; verify mathematical formulas against Siciliano et al. "Robotics: Modelling, Planning and Control"; confirm 95%+ accuracy

- [ ] T072 [US3] Generate RAG indexing metadata for Module 3; update module-index.json

- [ ] T073 [US3] Submit Module 3 for RAG indexing (by end of Week 3); validate retrieval with 10 sample queries about kinematics, control, locomotion

**Checkpoint**: Module 3 complete, indexed; RAG chatbot now covers fundamentals, software architecture, and advanced control

---

## Phase 6: User Story 4 - Module 4 Applications & Advanced Topics (Priority: P2)

**Goal**: Write 5 chapters on real-world applications (13,000 words, 15 code examples). Target Week 3-4. **DEFERRABLE**: If timeline slips, defer to post-hackathon; Modules 1-3 deliver base 100 points alone.

**Independent Test**: Module 4 can be indexed independently. Chatbot answers questions about applications, ethics, emerging tech, benchmarks using Module 4 content. Chapter 22 (Getting Started) is standalone beginner guide.

**Acceptance Scenarios**:
- All 5 chapters complete (13,000 words)
- External sources cross-checked (case studies, manufacturer specs)
- Chapter 22 (Getting Started) enables new users to build a simple humanoid system
- All chapters indexed into RAG (if timeline permits)

### Implementation for User Story 4

- [ ] T074 [P] [US4] Write Chapter 18 "Real-World Applications" (2,600 words) in `textbook/chapters/18-applications.md` with: manufacturing, service robotics, research platforms, real case studies from industry

- [ ] T075 [P] [US4] Write Chapter 19 "Ethical Considerations" (2,600 words) in `textbook/chapters/19-ethics.md` with: safety standards, human-robot interaction principles, legal/regulatory landscape

- [ ] T076 [P] [US4] Write Chapter 20 "Emerging Technologies" (2,600 words) in `textbook/chapters/20-emerging-technologies.md` with: AI integration, digital twins, edge computing, 5G for robotics

- [ ] T077 [P] [US4] Write Chapter 21 "Competition & Benchmarks" (2,600 words) in `textbook/chapters/21-benchmarks.md` with: RoboCup, industrial standards, performance metrics, competition strategies

- [ ] T078 [P] [US4] Write Chapter 22 "Getting Started: Your First Project" (2,600 words) in `textbook/chapters/22-getting-started.md` with: step-by-step beginner guide, building simple humanoid system, links to examples, simulation walkthrough

- [ ] T079 [P] [US4] Create Chapter 18 code examples: `textbook/code-examples/chapter_18_example_01.py` (application-specific config), `chapter_18_example_02.yaml` (industry standards), `chapter_18_example_03.py` (case study demo); test locally

- [ ] T080 [P] [US4] Create Chapter 19 code examples: `textbook/code-examples/chapter_19_example_01.py` (safety monitoring), `chapter_19_example_02.py` (HRI protocol implementation), `chapter_19_example_03.yaml` (safety config); test locally

- [ ] T081 [P] [US4] Create Chapter 20 code examples: `textbook/code-examples/chapter_20_example_01.py` (digital twin integration), `chapter_20_example_02.py` (edge device communication), `chapter_20_example_03.py` (cloud coordination); test locally

- [ ] T082 [P] [US4] Create Chapter 21 code examples: `textbook/code-examples/chapter_21_example_01.py` (RoboCup example), `chapter_21_example_02.py` (benchmark execution), `chapter_21_example_03.py` (performance evaluation); test locally

- [ ] T083 [P] [US4] Create Chapter 22 code examples: `textbook/code-examples/chapter_22_example_01.urdf` (simple beginner robot), `chapter_22_example_02.py` (getting started script), `chapter_22_example_03.launch.py` (complete launch file); test locally

- [ ] T084 [US4] Run all 15 Chapter 18-22 code examples through CI/CD pipeline; confirm 100% pass rate (depends on T079-T083)

- [ ] T085 [US4] Cross-check all external sources in Chapters 18-22 against published case studies, manufacturer specs, published benchmarks; add 20-25 new references to `references.json`

- [ ] T086 [US4] Verify word count for Chapters 18-22: total 13,000 words ±200 (depends on T074-T078)

- [ ] T087 [US4] Submit Module 4 for expert review; expert review timeline: 24-48 hours (or defer if timeline slips)

- [ ] T088 [US4] Incorporate expert review feedback on Module 4; verify all application claims cite published sources; confirm 95%+ accuracy

- [ ] T089 [US4] Generate RAG indexing metadata for Module 4; update module-index.json with all 5 chapter records

- [ ] T090 [US4] Submit Module 4 for RAG indexing (by end of Week 4, or defer if needed); validate retrieval with sample queries about applications, ethics, emerging tech

**Checkpoint**: Module 4 complete (or deferred); if complete, full 52,000-word textbook indexed and RAG-validated. If deferred, Modules 1-3 (39,000 words) deliver base 100 points.

---

## Phase 7: User Story 5 - Technical Review & Accuracy Validation (Priority: P1)

**Goal**: Domain expert reviews each module for technical accuracy before RAG indexing. Flexible pool of 2-3 reviewers; fallback structured peer-review if expert unavailable. Module-by-module staggered reviews as modules complete.

**Independent Test**: Each module review completed independently; module marked "approved for indexing" only after 95%+ accuracy audit.

**Acceptance Scenarios**:
- Modules 1-4 each reviewed by domain expert or peer checklist
- All technical claims traceable to official docs with version info
- All code examples tested and produce expected outputs
- Modules approved with 0 blocker-level errors; minor issues resolved
- Module marked "approved for indexing" before submission to RAG

### Implementation for User Story 5

- [ ] T091 [US5] Identify and confirm availability of expert reviewer for Module 1 (humanoid robotics fundamentals expert); document reviewer name, expertise area, email, expected availability

- [ ] T092 [US5] Assign Module 1 (5 chapters, 15 examples) to expert reviewer; provide review template, checklist, reference materials, deadline (24-48 hours from submission)

- [ ] T093 [US5] Track Module 1 expert review progress; if expert unavailable >12 hours, trigger peer-review fallback: second writer + engineer review Module 1 using structured peer-review checklist from `textbook/metadata/peer-review-checklist.md`

- [ ] T094 [US5] Consolidate Module 1 review feedback: log all flagged issues (critical/high/medium/low severity) in Review entity format; create issues list for author to resolve

- [ ] T095 [US5] Verify Module 1 factual accuracy: spot-check 5-10 key claims against official ROS 2 docs, Gazebo docs, and Siciliano et al. textbook; confirm all code examples execute correctly on test hardware

- [ ] T096 [US5] Compute Module 1 accuracy score: if all flagged issues resolved and spot-check passes, assign accuracy_score ≥95; mark module "approved for indexing" (depends on T091-T095)

- [ ] T097 [US5] Identify and confirm expert reviewer for Module 2 (ROS 2 / software architecture expert); document reviewer details, availability

- [ ] T098 [US5] Assign Module 2 (6 chapters, 18 examples) to expert reviewer; provide review materials, 24-48 hour deadline

- [ ] T099 [US5] Track Module 2 review; trigger peer-review fallback if needed (>12 hours expert unavailability)

- [ ] T100 [US5] Consolidate Module 2 review feedback; log flagged issues; cross-check code examples and architecture claims against official ROS 2 documentation

- [ ] T101 [US5] Compute Module 2 accuracy score; verify ≥95%; mark "approved for indexing" (depends on T097-T100)

- [ ] T102 [US5] Identify and confirm expert reviewer for Module 3 (control systems / kinematics expert); document reviewer

- [ ] T103 [US5] Assign Module 3 (6 chapters, 18 examples) to expert reviewer; deadline 24-48 hours

- [ ] T104 [US5] Track Module 3 review; trigger fallback if needed

- [ ] T105 [US5] Consolidate Module 3 review feedback; verify all mathematical formulas match Siciliano et al. and peer-reviewed robotics publications; test control algorithms on local simulator

- [ ] T106 [US5] Compute Module 3 accuracy score; verify ≥95%; mark "approved for indexing" (depends on T102-T105)

- [ ] T107 [US5] Identify and confirm expert reviewer for Module 4 (applications / industry expert, or reuse Module 1 expert if available); document reviewer

- [ ] T108 [US5] Assign Module 4 (5 chapters, 15 examples) to expert reviewer; deadline 24-48 hours (or defer if Module 4 deferred)

- [ ] T109 [US5] Track Module 4 review; trigger fallback if needed

- [ ] T110 [US5] Consolidate Module 4 review feedback; verify all real-world application claims cite published case studies or manufacturer specs; check benchmark descriptions

- [ ] T111 [US5] Compute Module 4 accuracy score; verify ≥95%; mark "approved for indexing" (or mark "deferred" if timeline slips)

- [ ] T112 [US5] Generate final accuracy audit report: tabulate accuracy scores for all 22 chapters, confirm 95%+ median score across all modules; document any remaining open issues and remediation status

- [ ] T113 [US5] Create final review summary at `textbook/REVIEW_SUMMARY.md` documenting: modules reviewed, reviewers assigned, accuracy scores, any deferred issues, approval dates

**Checkpoint**: All completed modules (1-3 minimum, 4 if time permits) marked "approved for indexing" with 95%+ accuracy audit; ready for RAG submission

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and preparation for deployment

**Timeline**: End of Week 4

- [ ] T114 [P] Create final textbook index at `textbook/INDEX.md` listing all 22 chapters (or 17 if Module 4 deferred) with links, word counts, code example counts, approval status

- [ ] T115 [P] Create textbook style guide at `textbook/STYLE_GUIDE.md` documenting: terminology consistency, formatting conventions, code comment style, reference format, learned best practices from writing process

- [ ] T116 [P] Generate combined references bibliography at `textbook/REFERENCES.md` with all 75-100+ APA-formatted citations from `references.json`, organized by chapter

- [ ] T117 [P] Validate all markdown files for formatting errors: check headers, code blocks, links, image references; fix any broken links or formatting issues

- [ ] T118 Run final code example verification: execute `scripts/test-code-examples.sh` on all code examples from completed modules; confirm 100% pass rate; document any environment-specific notes

- [ ] T119 Verify all chapters follow consistent template structure: check each chapter has learning objectives, sections, code examples, references; no orphaned content

- [ ] T120 Create final deployment checklist at `textbook/DEPLOYMENT_CHECKLIST.md` confirming: all chapters written ✓, code examples tested ✓, expert reviews complete ✓, accuracy audit passed ✓, RAG metadata generated ✓, ready for indexing ✓

- [ ] T121 [P] Create contribution guidelines at `textbook/CONTRIBUTING.md` for post-hackathon maintenance (how to add chapters, update code examples, refresh references)

- [ ] T122 Generate final statistics report: total word count (target: 52,000 or 39,000 if Module 4 deferred), chapter count (22 or 17), code example count (66 or 51), reference count, completion percentage

- [ ] T123 Conduct final readability review: sample 5 chapters, check Flesch-Kincaid Grade 10-12 level; verify active voice >75%; confirm technical terminology is defined

- [ ] T124 Validate RAG metadata generation: confirm all completed chapters have metadata records in `module-index.json` with learning objectives, keywords, sections; ready for vector embedding generation

**Checkpoint**: Textbook documentation complete, all validation passed, ready for public deployment and RAG chatbot integration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (Day 0)
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all writing tasks (Days 0-1)
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (Module 1): Can start immediately after Phase 2 (Week 1 Day 1)
  - US2 (Module 2): Can start Week 1 Day 3 in parallel with US1 review (does not block)
  - US3 (Module 3): Can start Week 2 Day 1 after US1 indexed (not strictly required but recommended)
  - US4 (Module 4): Can start Week 3 Day 1; can be deferred if timeline slips
  - US5 (Reviews): Runs in parallel with writing; each module reviewed as submitted
- **Polish (Phase 8)**: Depends on all desired modules being complete and approved (Week 4)

### User Story Dependencies

- **US1 (Module 1, P1)**: No dependencies on other US; can start after Phase 2
- **US2 (Module 2, P1)**: Can start immediately after Phase 2; no dependency on US1 (independent story)
- **US3 (Module 3, P2)**: Can start after Phase 2; recommended after US1 indexed (not mandatory)
- **US4 (Module 4, P2)**: Can start after Phase 2; can be deferred without blocking US1-US3
- **US5 (Reviews, P1)**: Runs parallel to writing; each module reviewed on submission; no blocking dependencies

### Within Each User Story

- Chapter writing tasks [P] can run in parallel (different files)
- Code example creation tasks [P] can run in parallel (different files)
- All chapter writing for a module should complete before code verification
- All code verification should complete before expert review submission
- Expert review must complete before RAG indexing

### Parallel Opportunities

**Phase 1 (Setup)**:
- All tasks marked [P] can run in parallel: T003-T010

**Phase 2 (Foundational)**:
- All tasks marked [P] can run in parallel: T012, T014, T016
- Remaining tasks (T011, T013, T015, T017) are sequential but quick

**Phase 3 (Module 1, US1)**:
- All chapter writing tasks [P] can run in parallel: T018-T022 (different chapters)
- All code example creation tasks [P] can run in parallel: T023-T027 (different chapters)
- Sequential: code testing (T028), references (T029), word count (T030), submission (T031), review (T032), indexing (T033-T034), validation (T035)

**Phase 4 (Module 2, US2)**:
- All chapter writing tasks [P] can run in parallel: T036-T041
- All code example creation tasks [P] can run in parallel: T042-T047
- Can START in parallel with Module 1 review (T032); does not wait for Module 1 completion

**Phase 5 (Module 3, US3)**:
- All chapter writing tasks [P] can run in parallel: T055-T060
- All code example creation tasks [P] can run in parallel: T061-T066
- Can START after Module 1 indexed (T034) for confidence; or immediately after Phase 2

**Phase 6 (Module 4, US4)**:
- All chapter writing tasks [P] can run in parallel: T074-T078
- All code example creation tasks [P] can run in parallel: T079-T083
- Can be deferred or run in parallel with US3

**Phase 7 (Reviews, US5)**:
- Module 1 review (T091-T096) runs parallel to Module 2 writing
- Module 2 review (T097-T101) runs parallel to Module 3 writing
- Module 3 review (T102-T106) runs parallel to Module 4 writing
- Module 4 review (T107-T111) can be deferred
- All reviews can leverage fallback peer-review if expert unavailable (no blocking)

---

## Parallel Example: Weeks 1-4 Timeline

### Week 1
- **Setup + Foundational** (Days 1-1): All Phase 1 + Phase 2 tasks completed in parallel where possible
- **Module 1 Writing** (Days 2-6): Chapters T018-T022 written in parallel; examples T023-T027 created in parallel
- **Module 1 Code Testing** (Day 6): T028 runs all examples through pipeline
- **Module 1 Review** (Days 6-7): T091-T096 expert review or fallback peer-review; author addresses feedback
- **Module 1 Indexing** (Day 7): T033-T035 generate metadata, submit for RAG, validate retrieval
- **Module 2 Writing Start** (Day 3, parallel with US1 review): T036-T041 write chapters in parallel

### Week 2
- **Module 2 Code Testing & Review** (Days 1-4): T042-T047 create examples; T048 test pipeline; T097-T101 expert review
- **Module 2 Indexing** (Days 4-5): T053-T054 metadata generation, RAG submission, validation
- **Module 3 Writing Start** (Day 3, after Module 1 indexed): T055-T060 write chapters in parallel

### Week 3
- **Module 3 Code Testing & Review** (Days 1-4): T061-T066 create examples; T067 test pipeline; T102-T106 expert review
- **Module 3 Indexing** (Days 4-5): T072-T073 metadata, RAG submission, validation
- **Module 4 Writing Start** (Day 3): T074-T078 write chapters in parallel (if timeline permits)

### Week 4
- **Module 4 Code Testing & Review** (Days 1-3, or defer): T079-T084 examples, testing, review
- **Module 4 Indexing** (Days 3-4, or defer): T089-T090 metadata, submission
- **Final Validation & Polish** (Days 5-7): Phase 8 tasks T114-T124 finalize documentation, run final checks, deployment checklist

---

## Implementation Strategy

### MVP First (Modules 1-3, 39,000 words)

1. **Complete Phase 1 & 2** (Days 0-1): Setup + Foundational infrastructure
2. **Complete Module 1 (US1)** (Week 1): Write, verify, review, index
3. **Validate Module 1 RAG Pilot** (Week 1, end): Confirm RAG pipeline works before proceeding
4. **Complete Modules 2-3 (US2-US3)** (Weeks 2-3): Parallel writing, testing, review, indexing
5. **Modules 1-3 Indexed & Validated** (Week 3, end): Full 39,000-word base textbook live in RAG = 100 base points
6. **Module 4 (US4, optional)** (Week 4): If timeline permits, write, verify, review, index 5th module
7. **Final Polish & Deployment** (Week 4, end): Documentation, statistics, deployment checklist

### Incremental Delivery

- **Checkpoint 1 (Week 1, end)**: Module 1 indexed, RAG chatbot can answer fundamental questions
- **Checkpoint 2 (Week 2, end)**: Modules 1-2 indexed, chatbot covers fundamentals + software architecture
- **Checkpoint 3 (Week 3, end)**: Modules 1-3 indexed, chatbot covers fundamentals + architecture + control
- **Checkpoint 4 (Week 4, end)**: Modules 1-4 indexed (if completed), full textbook live

### Risk Mitigations

- **Expert Reviewer Unavailable**: Triggered fallback peer-review checklist (tasks T093, T099, T104, T109); 12-hour SLA before fallback
- **Code Example Fails in CI/CD**: Test examples locally first (T028, T048, T067, T084); CI/CD validates; re-test if failure
- **Timeline Slip, Week 3-4**: Module 4 explicitly deferrable (tasks marked [US4]); Modules 1-3 alone deliver base 100 points
- **RAG Pipeline Broken Week 1**: Module 1 pilot (T034-T035) validates pipeline; if issues detected, remediate before Module 2 indexing (Week 2)
- **Accuracy Audit Fails**: Expert review with structured checklist (tasks T092-T106); spot-check claims against references before marking approved; fallback peer-review ensures quality gate

---

## Notes

- **[P] = Parallelizable**: Different files/chapters, no inter-task dependencies
- **[US1-US5] = Story labels**: Map tasks to specific user story for traceability
- Each module (US1-US4) is independently completable and testable
- Each module can be indexed independently into RAG
- Module 4 is explicitly deferrable; base 100 points achieved with Modules 1-3 (39,000 words)
- All code examples must be tested locally + pass CI/CD before chapter approval
- All chapters must be reviewed (expert or fallback peer) + 95%+ accuracy before RAG indexing
- Commit work after each phase or logical group (e.g., after T035 Module 1 checkpoint)
- Stop at any checkpoint (T035 Module 1, T054 Module 2, T073 Module 3) to validate story independently before moving to next

---

## Task Summary

- **Total Tasks**: 124
- **Phase 1 (Setup)**: 10 tasks
- **Phase 2 (Foundational)**: 7 tasks
- **Phase 3 (Module 1, US1)**: 18 tasks
- **Phase 4 (Module 2, US2)**: 19 tasks
- **Phase 5 (Module 3, US3)**: 19 tasks
- **Phase 6 (Module 4, US4)**: 17 tasks
- **Phase 7 (Reviews, US5)**: 23 tasks
- **Phase 8 (Polish)**: 11 tasks

**Critical Path**: T001-T010 (Setup) → T011-T017 (Foundational) → T018-T035 (Module 1 MVP) → T036-T054 (Module 2) → T055-T073 (Module 3) → [Optional: T074-T090 Module 4] → T114-T124 (Polish)

**Parallel Opportunities**:
- Phase 1: 8 parallelizable tasks (T003-T010)
- Phase 2: 3 parallelizable tasks (T012, T014, T016)
- Module 1: 5 chapter writing [P], 5 code examples [P], parallel review (T091-T096 async)
- Module 2: 6 chapter writing [P], 6 code examples [P], parallel review (T097-T101 async)
- Module 3: 6 chapter writing [P], 6 code examples [P], parallel review (T102-T106 async)
- Module 4: 5 chapter writing [P], 5 code examples [P], parallel review (T107-T111 async)

---

**Status**: Task Generation COMPLETE | Ready for Implementation (`/sp.implement`) | Branch: `002-content-writing`

