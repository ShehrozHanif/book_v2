# Implementation Plan: User Personalization & Adaptive Learning

**Branch**: `003-personalization` | **Date**: 2026-02-04 | **Spec**: [specs/003-personalization/spec.md](./spec.md)

---

## Summary

Implement a comprehensive user personalization system that extends the RAG chatbot to remember individual users, track their learning progress across 22 textbook chapters, generate personalized learning paths, and adapt chatbot response difficulty based on user skill level and performance. The system includes user authentication, knowledge assessment, progress tracking, learning path recommendations, adaptive responses, and gamification (badges/achievements).

**Timeline**: 2-3 weeks (P1 core features) + 1 week (P2 engagement features) = ~4 weeks total

**Scope**: 20 functional requirements, 6 user stories (P1 & P2), progression from authentication through adaptive difficulty

---

## Technical Context

**Language/Version**: Python 3.10+, TypeScript/React (frontend), PostgreSQL (database)

**Primary Dependencies**:
- FastAPI (extend from Spec 001)
- PostgreSQL with SQLAlchemy ORM
- JWT authentication for session management
- Qdrant (existing from Spec 002) for chapter/knowledge data
- OpenAI API (existing integration)

**Storage**:
- User profiles in PostgreSQL (users table)
- Progress tracking in PostgreSQL (progress table)
- Conversations in PostgreSQL (conversations table with user_id foreign key)
- Badges/achievements in PostgreSQL (achievements table)

**Testing**:
- Unit tests: Authentication, profile CRUD, progress calculation
- Integration tests: Full user flow (registration → assessment → learning path → response personalization)
- End-to-end tests: New user creates profile, completes assessment, follows learning path, receives personalized responses

**Target Platform**:
- Backend: FastAPI (extends Spec 001)
- Frontend: React dashboard for progress tracking (new)
- Database: PostgreSQL (extends Spec 001)

---

## Architecture Decisions

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| **Authentication Method** | JWT tokens with refresh mechanism for scalability; session stored in PostgreSQL for invalidation | Simple session cookies (less scalable, harder to handle multi-device) |
| **Learning Paths** | Pre-configured paths (expert-curated) initially; not AI-generated | AI path generation (too complex, requires ML pipeline) |
| **Difficulty Adaptation** | User skill level from profile + assessed via response correctness; can override with "Simplify"/"Advanced" buttons | Fully automatic difficulty detection (unreliable, frustrating) |
| **Progress Detection** | Explicit "Mark Complete" + heuristic (conversation depth/topics covered); not auto-detection | Fully automatic detection (misses genuine learning) |
| **Data Storage** | Single PostgreSQL database with user_id foreign keys across tables | Separate NoSQL for conversations (over-engineering) |
| **Badge System** | Store badge metadata in database, render as visual PNG | Blockchain/NFT (unnecessary complexity) |

---

## Phase 0: Research & Unknowns Resolution

### Unknowns Identified

**Q1: User Authentication Approach**
- How to integrate with existing Spec 001 authentication (if any)?
- Spec 001 uses no user authentication (stateless API)
- **Resolution**: Implement new authentication layer as separate service; chat endpoint extended to accept optional user_id

**Q2: Learning Path Configuration**
- How are learning paths defined? (hardcoded, admin UI, database?)
- **Resolution**: Define 3-5 learning paths in database; admin UI for management is out-of-scope (manual DB updates initially)

**Q3: Progress Tracking Heuristics**
- How to detect chapter completion without explicit user action?
- **Resolution**: Use heuristics: conversation includes 5+ questions from a chapter, user asks for confirmation = chapter complete

**Q4: Chatbot Response Adaptation**
- How to modify Spec 001 responses based on user skill level?
- **Resolution**: Add user_id and skill_level to chat endpoint request; generate different prompts for difficulty adaptation

---

## Phase 1: Design & Contracts

### 1. Data Model: User & Progress Entities

**User Entity**
```json
{
  "user_id": "uuid",
  "username": "string (unique)",
  "email": "string (unique)",
  "password_hash": "bcrypt_hash",
  "skill_level": 0-100,
  "created_date": "ISO8601",
  "last_login_date": "ISO8601",
  "profile_picture_url": "optional_url",
  "bio": "optional_string",
  "preferences": {
    "explanation_style": "theory_first | example_first",
    "code_language": "python | cpp | both",
    "learning_pace": "slow | medium | fast",
    "content_focus": "simulation | hardware | balanced"
  },
  "deleted_at": "optional_ISO8601 (soft delete for GDPR)"
}
```

**KnowledgeAssessment Entity**
```json
{
  "assessment_id": "uuid",
  "user_id": "uuid (FK)",
  "questions": [
    {
      "question_id": 1,
      "text": "What is ROS 2?",
      "options": ["A", "B", "C", "D"],
      "user_answer": "A",
      "correct_answer": "A",
      "correct": true
    }
  ],
  "calculated_skill_score": 0-100,
  "created_date": "ISO8601",
  "updated_date": "ISO8601"
}
```

**LearningPath Entity**
```json
{
  "path_id": "uuid",
  "user_id": "uuid (FK)",
  "path_name": "Beginner Path | Developer Path | Researcher Path",
  "chapters_in_order": [1, 2, 3, 5, 6, 7, ...],
  "completed_chapter_count": 5,
  "total_chapter_count": 17,
  "completion_percentage": 29,
  "status": "active | completed | abandoned",
  "created_date": "ISO8601",
  "last_updated_date": "ISO8601"
}
```

**Progress Entity**
```json
{
  "progress_id": "uuid",
  "user_id": "uuid (FK)",
  "chapter_id": "integer (1-22)",
  "completion_status": "not_started | in_progress | completed",
  "time_spent_seconds": 3600,
  "mastery_score": 0-100,
  "last_accessed_date": "ISO8601",
  "practice_attempts": 2,
  "highest_practice_score": 85,
  "created_date": "ISO8601",
  "updated_date": "ISO8601"
}
```

**Conversation Entity** (extends Spec 001)
```json
{
  "conversation_id": "uuid",
  "user_id": "uuid (FK) - NEW FIELD",
  "messages": [
    {
      "role": "user",
      "content": "What is kinematics?",
      "timestamp": "ISO8601"
    },
    {
      "role": "assistant",
      "content": "Kinematics is...",
      "timestamp": "ISO8601",
      "difficulty_level": "beginner"
    }
  ],
  "associated_chapter": "optional_integer (detected or user-specified)",
  "difficulty_level_detected": "beginner | intermediate | advanced",
  "created_date": "ISO8601",
  "updated_date": "ISO8601"
}
```

**Achievement Entity**
```json
{
  "achievement_id": "uuid",
  "user_id": "uuid (FK)",
  "achievement_type": "chapter_complete_1 | module_complete_1 | xp_100 | streak_7",
  "earned_date": "ISO8601",
  "display_info": {
    "title": "Mastered Kinematics",
    "description": "Completed Chapter 2 with 80%+ mastery",
    "icon_url": "url_to_badge_png",
    "points": 50
  }
}
```

---

### 2. API Contracts

**Contract 1: Register User**
```
POST /api/v1/users/register
Body: {
  "username": "robotics_learner",
  "email": "user@example.com",
  "password": "secure_password"
}
Response: {
  "user_id": "uuid",
  "username": "robotics_learner",
  "message": "Registration successful. Please log in."
}
```

**Contract 2: Login User**
```
POST /api/v1/users/login
Body: {
  "email": "user@example.com",
  "password": "secure_password"
}
Response: {
  "access_token": "jwt_token",
  "user_id": "uuid",
  "username": "robotics_learner"
}
```

**Contract 3: Take Knowledge Assessment**
```
POST /api/v1/users/{user_id}/assessment
Body: {
  "answers": [
    {"question_id": 1, "answer": "A"},
    {"question_id": 2, "answer": "C"},
    ...
  ]
}
Response: {
  "skill_score": 72,
  "recommended_paths": [
    {"path_id": "uuid", "name": "Developer Path", "match_percentage": 85},
    {"path_id": "uuid", "name": "Beginner Path", "match_percentage": 60}
  ]
}
```

**Contract 4: Get User Progress Dashboard**
```
GET /api/v1/users/{user_id}/progress
Response: {
  "chapters_completed": 5,
  "modules_completed": 1,
  "total_learning_time_hours": 12.5,
  "current_skill_level": 72,
  "current_path": {
    "path_name": "Developer Path",
    "completion_percentage": 32,
    "next_chapter_id": 9
  },
  "achievements": [
    {"title": "Mastered Kinematics", "earned_date": "2026-02-01", "icon_url": "..."},
    ...
  ],
  "learning_statistics": {
    "time_per_chapter": {"1": 120, "2": 150, ...},
    "mastery_per_chapter": {"1": 85, "2": 78, ...}
  }
}
```

**Contract 5: Chat with Personalization (Extended from Spec 001)**
```
POST /api/v1/chat
Body: {
  "query": "Explain forward kinematics",
  "user_id": "uuid (NEW - optional, enables personalization)",
  "conversation_id": "uuid (optional, for continuation)"
}
Response: {
  "response": "Forward kinematics is...",
  "conversation_id": "uuid",
  "difficulty_level_used": "intermediate",
  "retrieved_chapters": [2, 12],
  "processing_time_ms": 1200,
  "user_personalization_applied": true
}
```

**Contract 6: Mark Chapter Complete**
```
POST /api/v1/users/{user_id}/progress/{chapter_id}/complete
Body: {
  "mastery_score": 82,
  "time_spent_seconds": 3600
}
Response: {
  "status": "completed",
  "achievement_unlocked": {
    "title": "Mastered Kinematics",
    "points": 50
  },
  "next_recommendation": {
    "chapter_id": 3,
    "title": "Dynamics & Motion"
  }
}
```

---

### 3. Implementation Phases

**Phase 1 (Week 1): Core Authentication & User Management**
- User registration/login with JWT
- Profile CRUD operations
- Session management
- Database schema creation

**Phase 2 (Week 1-2): Assessment & Learning Paths**
- Knowledge assessment quiz (5-10 questions)
- Learning path generation based on skill level
- Path storage and recommendation logic

**Phase 3 (Week 2): Progress Tracking**
- Chapter completion tracking
- Time-on-topic tracking
- Mastery scoring
- Progress dashboard API

**Phase 4 (Week 2-3): Personalization & Adaptation**
- Response difficulty adjustment in chat endpoint
- Preference settings (explanation style, language, pace)
- Apply preferences to responses
- Dynamic difficulty detection from user responses

**Phase 5 (Week 3): Gamification & Stats**
- Badge/achievement system
- Learning statistics (time heatmap, mastery scores, curves)
- Retry/practice functionality
- Milestones and celebrations

**Phase 6 (Week 3-4): Frontend Dashboard**
- Progress visualization
- Learning path browser
- Achievement gallery
- Settings/preferences UI

**Phase 7 (Week 4): Data Privacy & Polish**
- GDPR compliance (data export, deletion)
- Testing (unit, integration, E2E)
- Performance optimization
- Documentation

---

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **JWT Tokens** | Stateless, scalable; refresh tokens for long sessions |
| **PostgreSQL for All User Data** | Simplicity; single database consistent with Spec 001 |
| **Skill Level 0-100 Scale** | Interpretable; compatible with percentage-based metrics |
| **Heuristic-based Progress Detection** | Pragmatic; avoids ML complexity while capturing real learning |
| **Pre-configured Learning Paths** | Expert curation ensures quality; simpler than AI generation |
| **Difficulty as Response Customization** | Reuse existing RAG pipeline; modify prompts based on skill level |

---

## Risks & Mitigations

| Risk | Blast Radius | Mitigation |
|------|--------------|-----------|
| **User Data Privacy** | High - GDPR violation | Clear privacy policy, encryption at rest, easy deletion, external audit |
| **Password Hashing** | High - security breach | Use bcrypt with salt; password reset flow with email verification |
| **Database Scalability** | High - user data slowdown | Indexed user_id columns, archival of old conversations, read replicas if needed |
| **Assessment Accuracy** | Medium - wrong skill assessment | Allow reassessment anytime; heuristic adjustment based on conversation performance |
| **Path Recommendation Quality** | Medium - user frustration | Expert review of paths; user can switch paths anytime |
| **API Breaking Changes** | Medium - client incompatibility | Spec 001 chat endpoint extended with optional fields; backward compatible |

---

## Outputs from Phase 1

- ✅ **spec.md**: Complete feature specification with 6 user stories, 20 FRs, 15 SCs
- ✅ **plan.md** (this file): Architecture, data model, API contracts, phases
- 📋 **data-model.md** (Phase 2): Detailed schema with migrations
- 📋 **contracts/** (Phase 2): Full API contract definitions
- 📋 **tasks.md** (Phase 2): Task breakdown with dependencies

---

## Next Steps

1. **Phase 2 (Next)**: Run `/sp.tasks` to break implementation into atomic tasks
   - Database schema tasks (8-10 tasks)
   - Authentication tasks (6-8 tasks)
   - Progress tracking tasks (8-10 tasks)
   - Personalization tasks (6-8 tasks)
   - Frontend dashboard tasks (6-8 tasks)
   - Testing tasks (8-10 tasks)
2. **Phase 3 (After tasks)**: Run `/sp.implement` to execute tasks in dependency order
3. **Phase 4**: Browser testing and deployment

---

**Status**: Plan Phase 1 Complete | Ready for `/sp.tasks` | Branch: `003-personalization`
