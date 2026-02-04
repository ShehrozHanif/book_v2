---
description: "Task list for User Personalization & Adaptive Learning feature implementation"
---

# Tasks: User Personalization & Adaptive Learning

**Input**: Design documents from `/specs/003-personalization/` (spec.md, plan.md)
**Prerequisites**: ✅ spec.md, ✅ plan.md (both complete)

**Tests**: Comprehensive testing required - unit tests for authentication, integration tests for user flows, E2E tests for complete personalization journey.

**Organization**: Tasks grouped by user story (US1-US6) enabling independent implementation and testing. Each story can be delivered as a separate increment. Tasks progress through 7 phases: Setup → Authentication → Assessment & Paths → Progress Tracking → Personalization → Gamification → Frontend → Privacy & Deployment.

**Estimated Total Tasks**: 98 tasks across 7 phases
**Parallel Opportunities**: 42 tasks can run in parallel (marked with [P])
**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1-US2) = ~35 tasks for core personalization with profiles, assessment, and learning paths

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- **Complexity**: S (Small: 2-4h), M (Medium: 4-6h), L (Large: 6-8h)

---

## Phase 0: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, database schema design
**Duration**: 1-2 days
**Parallel**: 7 of 8 tasks can run in parallel

---

- [ ] T001 Create backend directory structure for personalization in `backend/src/personalization/` with subdirectories: `models/`, `services/`, `api/`, `utils/`
  - **Complexity**: S
  - **Dependencies**: None
  - **Deliverable**: Directory structure created with empty `__init__.py` files

- [ ] T002 [P] Design PostgreSQL schema for user personalization in `backend/src/personalization/schema.sql` with tables:
  - users (user_id, username, email, password_hash, skill_level, preferences_json, created_at, last_login_at, deleted_at)
  - knowledge_assessments (assessment_id, user_id, questions_json, calculated_skill_score, created_at)
  - learning_paths (path_id, user_id, path_name, chapters_array, completion_percentage, status, created_at, updated_at)
  - progress (progress_id, user_id, chapter_id, completion_status, time_spent_seconds, mastery_score, last_accessed_at, practice_attempts, highest_practice_score)
  - conversations (extends Spec 001 with user_id FK, difficulty_level fields)
  - achievements (achievement_id, user_id, achievement_type, earned_date, display_info_json)
  - **Complexity**: M
  - **Dependencies**: None
  - **Acceptance**: Schema includes all entities from plan.md, foreign key constraints, indexes on user_id

- [ ] T003 [P] Create Alembic migration for personalization schema in `backend/alembic/versions/001_add_personalization.py`
  - **Complexity**: M
  - **Dependencies**: T002
  - **Acceptance**: Migration creates all tables, can be applied/reverted cleanly

- [ ] T004 [P] Setup SQLAlchemy ORM models in `backend/src/personalization/models/db_models.py` for User, KnowledgeAssessment, LearningPath, Progress, Achievement
  - **Complexity**: M
  - **Dependencies**: T002
  - **Acceptance**: Models map to schema, include relationships, validation rules

- [ ] T005 [P] Create Pydantic schemas in `backend/src/personalization/models/schemas.py` for:
  - UserCreate, UserLogin, UserResponse, UserProfile
  - AssessmentRequest, AssessmentResponse
  - LearningPathResponse, ProgressResponse
  - PreferencesUpdate, AchievementResponse
  - **Complexity**: M
  - **Dependencies**: None
  - **Acceptance**: Schemas match API contracts from plan.md

- [ ] T006 [P] Setup JWT authentication utilities in `backend/src/personalization/utils/auth.py`:
  - Token generation/validation
  - Password hashing (bcrypt)
  - Refresh token logic
  - **Complexity**: M
  - **Dependencies**: None
  - **Acceptance**: Can generate/validate JWT tokens, hash passwords securely

- [ ] T007 [P] Create authentication middleware in `backend/src/personalization/api/dependencies.py`:
  - get_current_user dependency
  - optional_user dependency (for anonymous access)
  - Permission checks
  - **Complexity**: M
  - **Dependencies**: T006
  - **Acceptance**: Middleware extracts user from JWT, handles missing/invalid tokens

- [ ] T008 [P] Add personalization configuration to `backend/src/config.py`:
  - JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
  - REFRESH_TOKEN_EXPIRE_DAYS
  - PASSWORD_MIN_LENGTH
  - **Complexity**: S
  - **Dependencies**: None
  - **Acceptance**: Config loaded from .env, includes validation

**Checkpoint**: ✅ Infrastructure ready - database schema, models, auth utilities prepared

---

## Phase 1: Authentication & User Management (Week 1)

**Purpose**: Core user authentication enabling profile creation, login/logout, session management
**Duration**: 2-3 days
**User Stories**: US1 (New User Creates Profile)

---

### User Story 1 - New User Creates Profile and Starts Learning (Priority: P1)

**Goal**: Enable users to create profiles, authenticate, and be recognized across sessions

**Independent Test**: User can register, log in, receive JWT token, make authenticated requests, log out, and log back in with credentials retained

---

- [ ] T009 [US1] Implement user registration endpoint POST `/api/v1/users/register` in `backend/src/personalization/api/routes/users.py`:
  - Validate username/email uniqueness
  - Hash password with bcrypt
  - Create user record in database
  - Return user_id and success message
  - **Complexity**: M
  - **Dependencies**: T004, T005, T006
  - **Acceptance**: Can register new user, duplicate username/email rejected, password hashed

- [ ] T010 [P] [US1] Implement user login endpoint POST `/api/v1/users/login` in `backend/src/personalization/api/routes/users.py`:
  - Validate credentials
  - Generate JWT access token + refresh token
  - Update last_login_at timestamp
  - Return tokens and user profile
  - **Complexity**: M
  - **Dependencies**: T004, T006, T007
  - **Acceptance**: Valid credentials return JWT token, invalid credentials return 401

- [ ] T011 [P] [US1] Implement token refresh endpoint POST `/api/v1/users/refresh` in `backend/src/personalization/api/routes/users.py`:
  - Validate refresh token
  - Issue new access token
  - **Complexity**: S
  - **Dependencies**: T006, T007
  - **Acceptance**: Valid refresh token returns new access token

- [ ] T012 [P] [US1] Implement logout endpoint POST `/api/v1/users/logout` in `backend/src/personalization/api/routes/users.py`:
  - Invalidate refresh token
  - Clear session
  - **Complexity**: S
  - **Dependencies**: T007
  - **Acceptance**: Logout clears tokens, subsequent requests with old token fail

- [ ] T013 [US1] Implement get user profile endpoint GET `/api/v1/users/me` in `backend/src/personalization/api/routes/users.py`:
  - Return current user's profile data
  - Include skill_level, preferences, created_date, last_login
  - **Complexity**: S
  - **Dependencies**: T007
  - **Acceptance**: Authenticated user can retrieve their profile

- [ ] T014 [P] [US1] Implement update user profile endpoint PATCH `/api/v1/users/me` in `backend/src/personalization/api/routes/users.py`:
  - Update username, email, bio, profile_picture
  - Validate new data
  - **Complexity**: M
  - **Dependencies**: T007
  - **Acceptance**: User can update profile fields, validation errors handled

- [ ] T015 [P] [US1] Create user service layer in `backend/src/personalization/services/user_service.py`:
  - create_user(username, email, password)
  - authenticate_user(email, password)
  - get_user_by_id(user_id)
  - update_user_profile(user_id, updates)
  - **Complexity**: M
  - **Dependencies**: T004
  - **Acceptance**: Service handles DB operations, returns structured data

- [ ] T016 [P] [US1] Write unit tests for authentication in `backend/tests/personalization/test_auth.py`:
  - Test registration (success, duplicate email)
  - Test login (valid/invalid credentials)
  - Test token generation/validation
  - Test password hashing
  - **Complexity**: M
  - **Dependencies**: T009, T010, T006
  - **Acceptance**: All auth edge cases covered, 90%+ code coverage

- [ ] T017 [P] [US1] Write integration tests for user endpoints in `backend/tests/personalization/test_users_api.py`:
  - Test full registration → login → profile retrieval flow
  - Test logout and token invalidation
  - **Complexity**: M
  - **Dependencies**: T009-T013
  - **Acceptance**: E2E user authentication flow passes

**Checkpoint**: ✅ User authentication complete - users can register, log in, access profile

---

## Phase 2: Assessment & Learning Paths (Week 1-2)

**Purpose**: Knowledge assessment to establish baseline skill level, generate personalized learning paths
**Duration**: 3-4 days
**User Stories**: US1 (Assessment), US2 (Learning Paths)

---

### User Story 1 (continued) - Knowledge Assessment

- [ ] T018 [US1] Create knowledge assessment question bank in `backend/src/personalization/data/assessment_questions.json`:
  - 10 multiple-choice questions covering Module 1 & 2 concepts
  - Questions span beginner → advanced difficulty
  - Include correct answers and difficulty ratings
  - **Complexity**: M
  - **Dependencies**: None (requires content expertise)
  - **Acceptance**: 10 questions with 4 options each, correct answers marked

- [ ] T019 [US1] Implement get assessment endpoint GET `/api/v1/users/assessment/questions` in `backend/src/personalization/api/routes/assessment.py`:
  - Return 5-10 random questions from question bank
  - Exclude correct answers from response
  - **Complexity**: S
  - **Dependencies**: T018
  - **Acceptance**: Returns question set without revealing answers

- [ ] T020 [US1] Implement submit assessment endpoint POST `/api/v1/users/{user_id}/assessment` in `backend/src/personalization/api/routes/assessment.py`:
  - Receive user's answers
  - Calculate skill score (0-100) based on correctness and difficulty
  - Store assessment record in database
  - Update user's skill_level in profile
  - Return skill score and recommended paths
  - **Complexity**: L
  - **Dependencies**: T018, T019, T004
  - **Acceptance**: Scores calculated accurately, skill level updated, paths recommended

- [ ] T021 [P] [US1] Create assessment scoring algorithm in `backend/src/personalization/services/assessment_service.py`:
  - Weighted scoring (harder questions worth more)
  - Normalize to 0-100 scale
  - Map score to skill tier (0-30: beginner, 31-70: intermediate, 71-100: advanced)
  - **Complexity**: M
  - **Dependencies**: T018
  - **Acceptance**: Scoring is consistent, reproducible, maps to skill tiers

- [ ] T022 [P] [US1] Write unit tests for assessment scoring in `backend/tests/personalization/test_assessment.py`:
  - Test scoring algorithm with known answer sets
  - Test skill tier mapping
  - Test edge cases (all correct, all wrong, partial)
  - **Complexity**: M
  - **Dependencies**: T021
  - **Acceptance**: Scoring algorithm validated with test cases

### User Story 2 - Personalized Learning Paths

- [ ] T023 [US2] Define learning path configurations in `backend/src/personalization/data/learning_paths.json`:
  - Beginner Path: chapters [1, 2, 3, 4, 5, 6, 7, 9, 10, 13, 14, 17, 18, 20]
  - Developer Path: chapters [1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 21]
  - Researcher Path: chapters [2, 3, 4, 8, 11, 12, 15, 16, 19, 20, 21, 22]
  - Include path metadata (name, description, target_skill_level, estimated_hours)
  - **Complexity**: M
  - **Dependencies**: None (requires curriculum design)
  - **Acceptance**: 3-5 paths defined with chapter sequences

- [ ] T024 [US2] Implement learning path recommendation algorithm in `backend/src/personalization/services/path_service.py`:
  - Map skill level to recommended paths
  - Calculate match percentage for each path
  - Return top 3 paths ranked by match
  - **Complexity**: M
  - **Dependencies**: T023, T021
  - **Acceptance**: Skill level 0-30 recommends Beginner Path first, 71-100 recommends Researcher Path first

- [ ] T025 [US2] Implement create learning path endpoint POST `/api/v1/users/{user_id}/learning-paths` in `backend/src/personalization/api/routes/paths.py`:
  - Accept path_id (from recommended paths)
  - Create learning path record for user
  - Set status to "active"
  - Initialize progress tracking for all chapters in path
  - **Complexity**: M
  - **Dependencies**: T023, T024, T004
  - **Acceptance**: User can select a path, path created with all chapters, progress initialized

- [ ] T026 [P] [US2] Implement get learning path endpoint GET `/api/v1/users/{user_id}/learning-paths` in `backend/src/personalization/api/routes/paths.py`:
  - Return user's active learning path
  - Include chapters in order, completion status per chapter, overall progress %
  - **Complexity**: M
  - **Dependencies**: T025
  - **Acceptance**: Returns complete path data with progress tracking

- [ ] T027 [P] [US2] Implement update learning path endpoint PATCH `/api/v1/users/{user_id}/learning-paths/{path_id}` in `backend/src/personalization/api/routes/paths.py`:
  - Allow user to switch paths
  - Mark old path as "abandoned"
  - Preserve progress data from old path
  - **Complexity**: M
  - **Dependencies**: T025
  - **Acceptance**: User can switch paths, old progress preserved

- [ ] T028 [P] [US2] Write unit tests for path recommendation in `backend/tests/personalization/test_paths.py`:
  - Test recommendation for beginner (0-30), intermediate (31-70), advanced (71-100)
  - Test path switching logic
  - **Complexity**: M
  - **Dependencies**: T024
  - **Acceptance**: Path recommendations match skill levels, switching works correctly

**Checkpoint**: ✅ Assessment and paths complete - users can take quiz, receive skill score, select learning path

---

## Phase 3: Progress Tracking (Week 2)

**Purpose**: Track user learning progress across chapters, time spent, mastery scoring
**Duration**: 3-4 days
**User Stories**: US3 (Progress Tracking)

---

### User Story 3 - System Tracks Progress and Celebrates Milestones

- [ ] T029 [US3] Implement track progress endpoint POST `/api/v1/users/{user_id}/progress/{chapter_id}/track` in `backend/src/personalization/api/routes/progress.py`:
  - Accept time_spent_seconds increment
  - Update progress record for chapter
  - Update last_accessed_at timestamp
  - **Complexity**: M
  - **Dependencies**: T004
  - **Acceptance**: Time tracking accumulates correctly, timestamps updated

- [ ] T030 [US3] Implement mark chapter complete endpoint POST `/api/v1/users/{user_id}/progress/{chapter_id}/complete` in `backend/src/personalization/api/routes/progress.py`:
  - Accept mastery_score (0-100)
  - Mark completion_status as "completed"
  - Update learning path completion percentage
  - Check for achievement unlocks (chapter complete, module complete)
  - Return achievement data if unlocked
  - **Complexity**: L
  - **Dependencies**: T029, T004
  - **Acceptance**: Chapter marked complete, path progress updated, achievements awarded

- [ ] T031 [P] [US3] Implement get progress dashboard endpoint GET `/api/v1/users/{user_id}/progress` in `backend/src/personalization/api/routes/progress.py`:
  - Return chapters completed count + percentage
  - Return modules completed count
  - Return total learning time (hours)
  - Return current skill level
  - Return current path with next chapter recommendation
  - Return achievements earned
  - Return learning statistics (time per chapter, mastery per chapter)
  - **Complexity**: L
  - **Dependencies**: T029, T030
  - **Acceptance**: Dashboard returns all metrics from spec.md SC-015

- [ ] T032 [P] [US3] Create progress calculation service in `backend/src/personalization/services/progress_service.py`:
  - calculate_chapter_completion_percentage(user_id)
  - calculate_total_learning_time(user_id)
  - get_next_recommended_chapter(user_id, path_id)
  - get_learning_statistics(user_id)
  - **Complexity**: M
  - **Dependencies**: T004
  - **Acceptance**: Calculations accurate, handle edge cases (no progress, empty path)

- [ ] T033 [P] [US3] Implement chapter completion detection heuristic in `backend/src/personalization/services/progress_service.py`:
  - Detect completion when conversation includes 5+ questions from chapter
  - Detect completion when user asks for next topic
  - Optional: explicit "Mark Complete" button click
  - **Complexity**: M
  - **Dependencies**: T032
  - **Acceptance**: Heuristic triggers on conversation depth, doesn't false-positive

- [ ] T034 [P] [US3] Create progress timeline endpoint GET `/api/v1/users/{user_id}/progress/timeline` in `backend/src/personalization/api/routes/progress.py`:
  - Return chronological list of chapters learned with dates
  - Include key concepts summary per chapter
  - **Complexity**: M
  - **Dependencies**: T031
  - **Acceptance**: Timeline shows learning journey, sortable by date

- [ ] T035 [P] [US3] Write unit tests for progress tracking in `backend/tests/personalization/test_progress.py`:
  - Test time accumulation
  - Test completion marking
  - Test dashboard calculations
  - Test next chapter recommendation logic
  - **Complexity**: M
  - **Dependencies**: T029-T032
  - **Acceptance**: Progress calculations validated, edge cases covered

**Checkpoint**: ✅ Progress tracking complete - users can track time, mark chapters complete, view dashboard

---

## Phase 4: Personalization & Adaptation (Week 2-3)

**Purpose**: Adapt chatbot responses based on user skill level, preferences, performance
**Duration**: 4-5 days
**User Stories**: US1 (Personalized Responses), US4 (Adaptive Difficulty), US5 (Preferences)

---

### User Story 1 (continued) - Personalized Responses

- [ ] T036 [US1] Extend Spec 001 chat endpoint POST `/api/v1/chat` in `backend/src/api/routes/chat.py`:
  - Add optional user_id field to ChatRequest schema
  - Load user profile and skill level if user_id provided
  - Pass skill level to response generation
  - **Complexity**: M
  - **Dependencies**: T007 (auth middleware), Spec 001 chat endpoint
  - **Acceptance**: Chat endpoint accepts user_id, retrieves user data

- [ ] T037 [US1] Implement difficulty-aware prompt generation in `backend/src/personalization/services/personalization_service.py`:
  - generate_personalized_prompt(query, skill_level, preferences)
  - Beginner (0-30): Simple language, analogies, step-by-step, avoid jargon
  - Intermediate (31-70): Balanced technical depth, code examples, some math
  - Advanced (71-100): Mathematical rigor, research citations, edge cases
  - **Complexity**: L
  - **Dependencies**: T036
  - **Acceptance**: Prompts demonstrably different for beginner vs advanced users

- [ ] T038 [P] [US1] Add user context to conversation history in `backend/src/personalization/services/personalization_service.py`:
  - Include username in system prompt
  - Include skill level context
  - Include current learning path chapter
  - **Complexity**: S
  - **Dependencies**: T036
  - **Acceptance**: Conversation context includes user personalization data

- [ ] T039 [P] [US1] Write integration tests for personalized responses in `backend/tests/personalization/test_personalized_chat.py`:
  - Test same question with beginner vs advanced user
  - Verify response complexity differs measurably
  - Test conversation history includes user context
  - **Complexity**: M
  - **Dependencies**: T037
  - **Acceptance**: Responses adapt to skill level, testable difference in complexity

### User Story 4 - Adaptive Difficulty Based on Performance

- [ ] T040 [US4] Implement performance tracking in conversation in `backend/src/personalization/services/personalization_service.py`:
  - Track user answer correctness (implicit from follow-up questions)
  - Track "Simplify" button clicks
  - Track "More Detail" requests
  - Update estimated skill level based on performance
  - **Complexity**: L
  - **Dependencies**: T037
  - **Acceptance**: System detects struggle/mastery patterns, adjusts skill level

- [ ] T041 [P] [US4] Implement difficulty override endpoints in `backend/src/personalization/api/routes/chat.py`:
  - POST `/api/v1/chat/simplify` - force simpler response
  - POST `/api/v1/chat/advanced` - force advanced response
  - Store preference for current session
  - **Complexity**: M
  - **Dependencies**: T037
  - **Acceptance**: User can override difficulty, preference applied to next responses

- [ ] T042 [P] [US4] Create dynamic difficulty adjustment algorithm in `backend/src/personalization/services/personalization_service.py`:
  - Decrease skill level by 10 points after 3 "Simplify" requests
  - Increase skill level by 10 points after 5 correct advanced answers
  - Cap at 0-100 range
  - **Complexity**: M
  - **Dependencies**: T040
  - **Acceptance**: Skill level adapts based on performance, caps enforced

- [ ] T043 [P] [US4] Add skill level confidence score in `backend/src/personalization/models/db_models.py`:
  - Add skill_confidence field to User model (0-100)
  - Update confidence based on performance consistency
  - Use confidence to weight difficulty adjustments
  - **Complexity**: M
  - **Dependencies**: T004
  - **Acceptance**: Confidence score tracks, low confidence = more sensitive adjustments

- [ ] T044 [P] [US4] Write unit tests for adaptive difficulty in `backend/tests/personalization/test_adaptive_difficulty.py`:
  - Test skill level decrease on struggle pattern
  - Test skill level increase on mastery pattern
  - Test difficulty override
  - **Complexity**: M
  - **Dependencies**: T040-T042
  - **Acceptance**: Adaptation logic validated with test scenarios

### User Story 5 - User Customizes Learning Preferences

- [ ] T045 [US5] Implement preferences data model extension in `backend/src/personalization/models/db_models.py`:
  - Add preferences_json field to User model (explanation_style, code_language, learning_pace, content_focus)
  - Default values: example_first, python, medium, balanced
  - **Complexity**: S
  - **Dependencies**: T004
  - **Acceptance**: Preferences stored in JSON, defaults applied on registration

- [ ] T046 [US5] Implement update preferences endpoint PATCH `/api/v1/users/{user_id}/preferences` in `backend/src/personalization/api/routes/users.py`:
  - Accept preferences_json update
  - Validate enum values
  - Update user record
  - **Complexity**: M
  - **Dependencies**: T045
  - **Acceptance**: User can update preferences, invalid values rejected

- [ ] T047 [US5] Implement preference-aware response generation in `backend/src/personalization/services/personalization_service.py`:
  - Explanation style: theory_first vs example_first (reorder response structure)
  - Code language: prioritize Python vs C++ examples
  - Learning pace: slow (verbose), medium (balanced), fast (concise)
  - Content focus: simulation vs hardware (filter retrieved content)
  - **Complexity**: L
  - **Dependencies**: T037, T046
  - **Acceptance**: Responses adapt to preferences, example_first leads with code

- [ ] T048 [P] [US5] Create preferences validation schema in `backend/src/personalization/models/schemas.py`:
  - PreferencesUpdate schema with enum validation
  - explanation_style: Literal["theory_first", "example_first"]
  - code_language: Literal["python", "cpp", "both"]
  - learning_pace: Literal["slow", "medium", "fast"]
  - content_focus: Literal["simulation", "hardware", "balanced"]
  - **Complexity**: S
  - **Dependencies**: T005
  - **Acceptance**: Schema validates preference values, rejects invalid

- [ ] T049 [P] [US5] Write integration tests for preferences in `backend/tests/personalization/test_preferences.py`:
  - Test preference update
  - Test response adaptation to example_first vs theory_first
  - Test code language prioritization
  - **Complexity**: M
  - **Dependencies**: T047
  - **Acceptance**: Preferences applied to responses, testable differences

**Checkpoint**: ✅ Personalization complete - responses adapt to skill level, performance, preferences

---

## Phase 5: Gamification & Stats (Week 3)

**Purpose**: Badge/achievement system, practice/retry functionality, learning statistics
**Duration**: 3-4 days
**User Stories**: US3 (Milestones), US6 (Retry & Stats)

---

### User Story 3 (continued) - Achievements & Milestones

- [ ] T050 [US3] Define achievement types in `backend/src/personalization/data/achievements.json`:
  - Chapter complete achievements (22 total)
  - Module complete achievements (4 total)
  - XP milestones (100, 500, 1000, 5000 points)
  - Streak achievements (7-day, 30-day)
  - Include achievement metadata (title, description, icon_url, points)
  - **Complexity**: M
  - **Dependencies**: None (requires design)
  - **Acceptance**: 30+ achievements defined with metadata

- [ ] T051 [US3] Implement achievement detection service in `backend/src/personalization/services/achievement_service.py`:
  - check_achievements(user_id, event_type, event_data)
  - Detect chapter/module completion
  - Detect XP thresholds
  - Detect learning streaks
  - Award achievements, store in database
  - **Complexity**: L
  - **Dependencies**: T050, T004
  - **Acceptance**: Achievements awarded on trigger events, no duplicates

- [ ] T052 [P] [US3] Integrate achievement detection into progress endpoints in `backend/src/personalization/api/routes/progress.py`:
  - Call check_achievements after chapter completion
  - Return unlocked achievements in response
  - **Complexity**: M
  - **Dependencies**: T051, T030
  - **Acceptance**: Achievements unlock on chapter complete, returned to user

- [ ] T053 [P] [US3] Implement get achievements endpoint GET `/api/v1/users/{user_id}/achievements` in `backend/src/personalization/api/routes/achievements.py`:
  - Return all earned achievements
  - Include earned_date, display_info
  - Sort by earned_date descending
  - **Complexity**: S
  - **Dependencies**: T051
  - **Acceptance**: Returns user's achievements, includes metadata

- [ ] T054 [P] [US3] Create achievement badge renderer service in `backend/src/personalization/services/badge_service.py`:
  - generate_badge_image(achievement_id) → PNG
  - Badge design with icon, title, date
  - Return as downloadable PNG or base64
  - **Complexity**: M
  - **Dependencies**: T050
  - **Acceptance**: Badges rendered as PNG, visually distinct

- [ ] T055 [P] [US3] Write unit tests for achievements in `backend/tests/personalization/test_achievements.py`:
  - Test achievement detection logic
  - Test duplicate prevention
  - Test XP threshold achievements
  - **Complexity**: M
  - **Dependencies**: T051
  - **Acceptance**: Achievement logic validated, no duplicate awards

### User Story 6 - Retry Concepts and Learning Statistics

- [ ] T056 [US6] Implement practice question generation in `backend/src/personalization/services/practice_service.py`:
  - generate_practice_questions(chapter_id, count=5)
  - Draw from assessment question bank for that chapter
  - Return questions without answers
  - **Complexity**: M
  - **Dependencies**: T018
  - **Acceptance**: Returns 3-5 practice questions per chapter

- [ ] T057 [US6] Implement practice attempt submission endpoint POST `/api/v1/users/{user_id}/progress/{chapter_id}/practice` in `backend/src/personalization/api/routes/progress.py`:
  - Accept user's practice answers
  - Calculate mastery score (0-100)
  - Store practice attempt record
  - Update highest_practice_score if improved
  - **Complexity**: M
  - **Dependencies**: T056, T004
  - **Acceptance**: Practice scored, attempts tracked, high score updated

- [ ] T058 [P] [US6] Implement retry functionality in `backend/src/personalization/api/routes/progress.py`:
  - POST `/api/v1/users/{user_id}/progress/{chapter_id}/retry`
  - Generate practice questions
  - Mark chapter as "in_progress" again
  - Track retry count
  - **Complexity**: M
  - **Dependencies**: T056, T057
  - **Acceptance**: User can retry chapters, questions generated, progress updated

- [ ] T059 [P] [US6] Implement learning statistics endpoint GET `/api/v1/users/{user_id}/statistics` in `backend/src/personalization/api/routes/statistics.py`:
  - Return time_per_chapter heatmap (chapter_id → hours)
  - Return mastery_per_chapter (chapter_id → score)
  - Calculate learning curve (skill level over time)
  - Identify recommended focus areas (low mastery chapters)
  - **Complexity**: L
  - **Dependencies**: T032
  - **Acceptance**: Statistics accurate, includes all metrics from spec.md US6

- [ ] T060 [P] [US6] Create learning curve calculation in `backend/src/personalization/services/statistics_service.py`:
  - Track skill level snapshots over time
  - Calculate improvement rate (points/week)
  - Detect plateaus or regressions
  - **Complexity**: M
  - **Dependencies**: T059
  - **Acceptance**: Learning curve shows progression, detects trends

- [ ] T061 [P] [US6] Implement recommended focus areas algorithm in `backend/src/personalization/services/statistics_service.py`:
  - Identify chapters with mastery_score < 60%
  - Suggest related chapters to revisit
  - Suggest practice attempts for weak areas
  - **Complexity**: M
  - **Dependencies**: T059
  - **Acceptance**: Recommendations target weak areas, relevant suggestions

- [ ] T062 [P] [US6] Implement advanced challenges for high mastery in `backend/src/personalization/services/practice_service.py`:
  - Detect mastery_score > 85%
  - Offer research paper summaries for that chapter
  - Offer advanced practice questions
  - **Complexity**: M
  - **Dependencies**: T057
  - **Acceptance**: High performers receive advanced content

- [ ] T063 [P] [US6] Write unit tests for practice and stats in `backend/tests/personalization/test_practice_stats.py`:
  - Test practice question generation
  - Test retry logic
  - Test statistics calculations
  - Test focus area recommendations
  - **Complexity**: M
  - **Dependencies**: T056-T061
  - **Acceptance**: Practice/stats logic validated

**Checkpoint**: ✅ Gamification complete - achievements unlock, practice available, stats displayed

---

## Phase 6: Frontend Dashboard (Week 3-4)

**Purpose**: React-based progress dashboard, learning path browser, settings UI
**Duration**: 4-5 days
**User Stories**: US2 (Path Browser), US3 (Dashboard), US5 (Preferences UI), US6 (Stats Visualization)

---

- [ ] T064 Create frontend directory structure in `frontend/src/personalization/` with subdirectories: `components/`, `pages/`, `hooks/`, `services/`, `types/`
  - **Complexity**: S
  - **Dependencies**: None
  - **Deliverable**: Directory structure with index files

- [ ] T065 [P] Create TypeScript types in `frontend/src/personalization/types/index.ts`:
  - User, UserProfile, Preferences
  - LearningPath, Progress, Achievement
  - AssessmentQuestion, PracticeAttempt
  - **Complexity**: M
  - **Dependencies**: T005 (match backend schemas)
  - **Acceptance**: Types match backend Pydantic models

- [ ] T066 [P] Create personalization API service in `frontend/src/personalization/services/api.ts`:
  - register(username, email, password)
  - login(email, password)
  - getProfile()
  - updatePreferences(preferences)
  - getProgress()
  - getLearningPath()
  - getAchievements()
  - getStatistics()
  - **Complexity**: M
  - **Dependencies**: T065
  - **Acceptance**: API methods handle errors, return typed data

- [ ] T067 [US3] Create progress dashboard page in `frontend/src/personalization/pages/Dashboard.tsx`:
  - Display chapters completed (% and count)
  - Display total learning time
  - Display current skill level
  - Display current learning path progress
  - Display recent achievements
  - **Complexity**: L
  - **Dependencies**: T066
  - **Acceptance**: Dashboard loads data from API, displays all metrics

- [ ] T068 [P] [US3] Create progress visualization components in `frontend/src/personalization/components/ProgressVisuals.tsx`:
  - ProgressRing (circular progress indicator)
  - ChapterList (chapters with completion status)
  - TimeHeatmap (time per chapter visualization)
  - **Complexity**: M
  - **Dependencies**: T067
  - **Acceptance**: Visualizations render correctly, responsive

- [ ] T069 [P] [US3] Create achievement gallery component in `frontend/src/personalization/components/AchievementGallery.tsx`:
  - Grid of earned achievements
  - Badge images with titles/descriptions
  - Unlock dates
  - **Complexity**: M
  - **Dependencies**: T066
  - **Acceptance**: Achievements displayed, visually appealing

- [ ] T070 [US2] Create learning path browser page in `frontend/src/personalization/pages/LearningPaths.tsx`:
  - Display recommended paths
  - Show path details (chapters, estimated time)
  - Allow path selection
  - Show current path progress
  - **Complexity**: L
  - **Dependencies**: T066
  - **Acceptance**: User can browse and select paths

- [ ] T071 [P] [US2] Create path progress tracker component in `frontend/src/personalization/components/PathProgress.tsx`:
  - Chapter list in path order
  - Completion checkmarks
  - Next recommended chapter highlighted
  - **Complexity**: M
  - **Dependencies**: T070
  - **Acceptance**: Path progress clear, next chapter obvious

- [ ] T072 [US5] Create preferences settings page in `frontend/src/personalization/pages/Settings.tsx`:
  - Form for explanation style
  - Form for code language
  - Form for learning pace
  - Form for content focus
  - Save button
  - **Complexity**: M
  - **Dependencies**: T066
  - **Acceptance**: Preferences editable, saved to backend

- [ ] T073 [P] [US5] Create preference toggle components in `frontend/src/personalization/components/PreferenceToggles.tsx`:
  - ExplanationStyleToggle (theory-first / example-first)
  - CodeLanguageSelector (Python / C++ / Both)
  - LearningPaceSlider (Slow → Medium → Fast)
  - ContentFocusToggle (Simulation / Hardware / Balanced)
  - **Complexity**: M
  - **Dependencies**: T072
  - **Acceptance**: Toggles intuitive, update on change

- [ ] T074 [US6] Create statistics page in `frontend/src/personalization/pages/Statistics.tsx`:
  - Time-on-topic heatmap
  - Mastery scores per chapter (bar chart)
  - Learning curve line chart
  - Recommended focus areas list
  - **Complexity**: L
  - **Dependencies**: T066
  - **Acceptance**: Statistics visualized clearly, interactive

- [ ] T075 [P] [US6] Create chart components in `frontend/src/personalization/components/Charts.tsx`:
  - TimeHeatmap (time per chapter)
  - MasteryBarChart (scores per chapter)
  - LearningCurve (skill level over time)
  - Use Chart.js or Recharts library
  - **Complexity**: M
  - **Dependencies**: T074
  - **Acceptance**: Charts render with real data, responsive

- [ ] T076 [US1] Create user profile page in `frontend/src/personalization/pages/Profile.tsx`:
  - Display username, email, bio
  - Display profile picture
  - Edit profile button
  - View achievements button
  - **Complexity**: M
  - **Dependencies**: T066
  - **Acceptance**: Profile displays user data, editable

- [ ] T077 [P] [US1] Create authentication components in `frontend/src/personalization/components/Auth.tsx`:
  - LoginForm
  - RegisterForm
  - LogoutButton
  - Handle JWT token storage (localStorage)
  - **Complexity**: M
  - **Dependencies**: T066
  - **Acceptance**: Auth forms functional, tokens managed

- [ ] T078 [P] Create navigation integration in `frontend/src/personalization/components/Navigation.tsx`:
  - Add Dashboard link to main nav
  - Add Profile link
  - Add Settings link
  - Add Statistics link
  - **Complexity**: S
  - **Dependencies**: T067-T074
  - **Acceptance**: Navigation links work, pages accessible

- [ ] T079 [P] Create useAuth hook in `frontend/src/personalization/hooks/useAuth.ts`:
  - Manage authentication state
  - Provide login/logout methods
  - Check token validity
  - Redirect to login if unauthenticated
  - **Complexity**: M
  - **Dependencies**: T077
  - **Acceptance**: Auth state managed, protected routes work

- [ ] T080 [P] Create useProgress hook in `frontend/src/personalization/hooks/useProgress.ts`:
  - Fetch and cache progress data
  - Provide refresh method
  - Handle loading/error states
  - **Complexity**: M
  - **Dependencies**: T066
  - **Acceptance**: Progress data fetched efficiently, cached

- [ ] T081 [P] Write frontend component tests in `frontend/tests/personalization/`:
  - Test Dashboard component renders
  - Test LearningPaths component
  - Test Settings component
  - Test auth forms
  - **Complexity**: M
  - **Dependencies**: T067-T077
  - **Acceptance**: Component tests pass, 80%+ coverage

**Checkpoint**: ✅ Frontend complete - dashboard, paths, settings, stats all accessible

---

## Phase 7: Privacy, Testing, Deployment (Week 4)

**Purpose**: GDPR compliance, comprehensive testing, performance optimization, documentation
**Duration**: 3-4 days
**User Stories**: All (Testing), GDPR Compliance

---

### GDPR Compliance & Data Privacy

- [ ] T082 Implement data export endpoint GET `/api/v1/users/{user_id}/export` in `backend/src/personalization/api/routes/users.py`:
  - Return all user data (profile, progress, conversations, achievements) as JSON
  - Include timestamps, metadata
  - Deliver as downloadable file
  - **Complexity**: M
  - **Dependencies**: T004
  - **Acceptance**: User receives complete data export, GDPR-compliant format

- [ ] T083 [P] Implement account deletion endpoint DELETE `/api/v1/users/{user_id}` in `backend/src/personalization/api/routes/users.py`:
  - Soft delete user (set deleted_at timestamp)
  - Anonymize personal data (replace with placeholders)
  - Preserve non-personal aggregate stats
  - Schedule hard delete after 90 days
  - **Complexity**: M
  - **Dependencies**: T004
  - **Acceptance**: User data anonymized, hard delete scheduled

- [ ] T084 [P] Create privacy policy document at `docs/PRIVACY_POLICY.md`:
  - Data collection practices
  - Data retention policy (90-day deletion)
  - User rights (export, deletion)
  - Encryption practices
  - **Complexity**: S
  - **Dependencies**: None (requires legal review)
  - **Acceptance**: Privacy policy comprehensive, GDPR-compliant

- [ ] T085 [P] Implement conversation data archival in `backend/src/personalization/services/archival_service.py`:
  - Archive conversations older than 6 months to cold storage
  - Keep recent conversations in hot database
  - Implement pagination for conversation history
  - **Complexity**: M
  - **Dependencies**: T004
  - **Acceptance**: Old conversations archived, performance maintained

### Comprehensive Testing

- [ ] T086 Write E2E test for complete user journey in `backend/tests/e2e/test_personalization_flow.py`:
  - Register → Login → Assessment → Path Selection → Ask Question → Track Progress → View Dashboard → Logout
  - **Complexity**: L
  - **Dependencies**: All backend endpoints
  - **Acceptance**: Full flow passes, no errors

- [ ] T087 [P] Write performance tests in `backend/tests/performance/test_personalization_performance.py`:
  - Profile retrieval < 500ms
  - Dashboard load < 2s
  - Chat with personalization < 3s
  - **Complexity**: M
  - **Dependencies**: T086
  - **Acceptance**: Performance targets met (SC-007, SC-015)

- [ ] T088 [P] Write security tests in `backend/tests/security/test_personalization_security.py`:
  - Test password hashing strength
  - Test JWT token expiration
  - Test SQL injection prevention
  - Test authentication bypass attempts
  - **Complexity**: M
  - **Dependencies**: T009-T012
  - **Acceptance**: Security vulnerabilities tested, none exploitable

- [ ] T089 [P] Write edge case tests in `backend/tests/personalization/test_edge_cases.py`:
  - User abandons learning path mid-way
  - User switches paths
  - Inaccurate skill assessment
  - Inconsistent performance (advanced questions correct, basic wrong)
  - User refuses assessment
  - **Complexity**: M
  - **Dependencies**: All personalization services
  - **Acceptance**: Edge cases from spec.md handled gracefully

### Performance Optimization & Deployment

- [ ] T090 Add database indexes in migration `backend/alembic/versions/002_add_indexes.py`:
  - Index on users.user_id, users.email
  - Index on progress.user_id, progress.chapter_id
  - Index on conversations.user_id
  - Index on achievements.user_id
  - **Complexity**: S
  - **Dependencies**: T003
  - **Acceptance**: Queries <500ms with indexes

- [ ] T091 [P] Implement API response caching in `backend/src/personalization/api/middleware.py`:
  - Cache progress dashboard for 60s
  - Cache learning path data for 300s
  - Cache achievements for 600s
  - Use Redis or in-memory cache
  - **Complexity**: M
  - **Dependencies**: T031, T026, T053
  - **Acceptance**: Cached responses faster, cache invalidated on updates

- [ ] T092 [P] Setup database connection pooling optimization in `backend/src/database/connection.py`:
  - Configure pool size (min 5, max 20)
  - Configure connection timeout
  - Configure connection recycling
  - **Complexity**: S
  - **Dependencies**: T003
  - **Acceptance**: Connection pool stable under load

- [ ] T093 [P] Create deployment configuration for personalization in `backend/deployment/personalization.yaml`:
  - Database migration steps
  - Environment variables required
  - Service dependencies
  - Health check endpoints
  - **Complexity**: M
  - **Dependencies**: None
  - **Acceptance**: Deployment reproducible, automated

### Documentation

- [ ] T094 Create API documentation for personalization in `docs/api/PERSONALIZATION_API.md`:
  - Document all endpoints (auth, profiles, paths, progress, achievements)
  - Include request/response examples
  - Include authentication requirements
  - **Complexity**: M
  - **Dependencies**: All API endpoints
  - **Acceptance**: Documentation complete, examples accurate

- [ ] T095 [P] Create user guide for personalization in `docs/USER_GUIDE.md`:
  - How to create profile
  - How to take assessment
  - How to select learning path
  - How to track progress
  - How to customize preferences
  - **Complexity**: M
  - **Dependencies**: Frontend pages
  - **Acceptance**: User guide clear, covers all features

- [ ] T096 [P] Create developer setup guide in `docs/DEVELOPER_SETUP.md`:
  - Local development environment setup
  - Database setup
  - Running tests
  - Debugging tips
  - **Complexity**: S
  - **Dependencies**: All setup tasks
  - **Acceptance**: New developer can set up environment from guide

- [ ] T097 [P] Create architecture documentation in `docs/ARCHITECTURE.md`:
  - Database schema diagram
  - API architecture
  - Authentication flow
  - Personalization algorithm overview
  - **Complexity**: M
  - **Dependencies**: All implementation
  - **Acceptance**: Architecture clear, diagrams helpful

- [ ] T098 [P] Update main README with personalization features in `README.md`:
  - Add personalization feature overview
  - Link to user guide
  - Link to API docs
  - **Complexity**: S
  - **Dependencies**: T094, T095
  - **Acceptance**: README updated, links work

**Checkpoint**: ✅ Testing, privacy, deployment complete - feature production-ready

---

## Task Summary by User Story

| User Story | Task Count | Key Deliverables |
|------------|-----------|------------------|
| **US1** - New User Creates Profile | 18 tasks | Registration, login, assessment, personalized responses |
| **US2** - Personalized Learning Paths | 12 tasks | Path recommendation, selection, progress tracking |
| **US3** - Progress Tracking & Milestones | 15 tasks | Dashboard, achievements, time tracking, celebrations |
| **US4** - Adaptive Difficulty | 10 tasks | Performance tracking, difficulty adjustment, overrides |
| **US5** - Learning Preferences | 8 tasks | Preference settings, response adaptation |
| **US6** - Retry & Statistics | 12 tasks | Practice questions, retry logic, statistics visualization |
| **Infrastructure** | 15 tasks | Setup, auth utilities, database schema, testing |
| **Frontend** | 18 tasks | Dashboard, settings, visualization components |
| **Privacy & Deployment** | 10 tasks | GDPR compliance, testing, docs, deployment |
| **Total** | **98 tasks** | Full personalization system |

---

## Dependency Map

### Critical Path (Must Complete in Order)
1. **Phase 0 Setup** (T001-T008) → Enables all subsequent work
2. **Phase 1 Authentication** (T009-T017) → Required for user identity
3. **Phase 2 Assessment** (T018-T022) → Required for skill level
4. **Phase 2 Learning Paths** (T023-T028) → Required for personalized journey
5. **Phase 3 Progress Tracking** (T029-T035) → Required for dashboard
6. **Phase 4 Personalization** (T036-T049) → Core value delivery
7. **Phase 5 Gamification** (T050-T063) → Engagement features
8. **Phase 6 Frontend** (T064-T081) → User interface
9. **Phase 7 Testing & Deployment** (T082-T098) → Production readiness

### Parallel Opportunities
- **Within Phase 1**: T010-T017 can run in parallel after T009
- **Within Phase 2**: T023-T028 can run in parallel with T018-T022
- **Within Phase 3**: T031-T035 can run in parallel after T030
- **Within Phase 4**: Multiple preference and adaptation tasks (T038-T049)
- **Within Phase 5**: Achievement and practice tasks (T050-T063)
- **Within Phase 6**: All component tasks (T065-T081) once API service ready
- **Within Phase 7**: Documentation tasks (T094-T098) can run in parallel

---

## Complexity Distribution

- **Small (2-4h)**: 25 tasks
- **Medium (4-6h)**: 52 tasks
- **Large (6-8h)**: 21 tasks

**Total Estimated Effort**: ~440 hours (~11 weeks for 1 developer, ~4 weeks for 3 developers)

---

## Testing Coverage by Phase

| Phase | Unit Tests | Integration Tests | E2E Tests |
|-------|-----------|-------------------|-----------|
| Phase 1 - Auth | T016 | T017 | - |
| Phase 2 - Assessment & Paths | T022, T028 | - | - |
| Phase 3 - Progress | T035 | - | - |
| Phase 4 - Personalization | T044, T049 | T039 | - |
| Phase 5 - Gamification | T055, T063 | - | - |
| Phase 6 - Frontend | T081 | - | - |
| Phase 7 - Complete Flow | T088, T089 | T087 | T086 |

---

## Next Steps

1. **Immediate (Week 1)**: Execute Phase 0 + Phase 1 (T001-T017) to establish authentication foundation
2. **Week 2**: Execute Phase 2 + Phase 3 (T018-T035) for assessment and progress tracking
3. **Week 3**: Execute Phase 4 + Phase 5 (T036-T063) for personalization and gamification
4. **Week 4**: Execute Phase 6 + Phase 7 (T064-T098) for frontend and deployment

**Status**: Task breakdown complete | Ready for implementation | Total: 98 tasks
