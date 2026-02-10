# Phase 5: Gamification & Stats - Implementation Guide

**Status**: In Progress - Core Tasks T050-T063

**Architecture Overview**: Achievement system, practice/retry functionality, and learning statistics

---

## Task Breakdown & Implementation Approach

### T050: Define Achievement Types ✅
**Status**: COMPLETE
**File**: `backend/src/personalization/data/achievements.json`
**Content**: 32 achievement definitions including:
- 22 Chapter completion achievements
- 4 Module completion achievements
- 4 XP milestone achievements (100, 500, 1000, 5000)
- 2 Streak achievements (7-day, 30-day)
- Additional milestone achievements

---

### T051: Achievement Detection Service
**Status**: IN PROGRESS
**File**: `backend/src/personalization/services/achievement_service.py`
**Core Methods**:
```python
class AchievementService:
    async def check_achievements(user_id, event_type, event_data)
    async def get_user_achievements(user_id)
    async def get_achievement_stats(user_id)
```

**Event Types Supported**:
- `chapter_complete`: Award chapter-specific achievements
- `xp_earned`: Check XP milestones (100, 500, 1000, 5000)
- `module_complete`: Award module completion
- `streak_update`: Check 7/30-day streaks
- `mastery_update`: Check 100% mastery

---

### T052: Integrate Achievements into Progress Endpoints
**Location**: `backend/src/personalization/api/routes/progress.py`
**Changes Needed**:
1. After chapter completion in `POST /progress/{chapter_id}/complete`
2. Call `achievement_service.check_achievements()`
3. Return unlocked achievements in response
4. Trigger celebration notifications (Phase 6)

---

### T053: Get Achievements Endpoint
**Endpoint**: `GET /api/v1/users/{user_id}/achievements`
**Response**:
```json
{
  "achievements": [
    {
      "id": "ch_1_complete",
      "title": "Chapter 1 Master",
      "description": "...",
      "earned_date": "2026-02-06T10:30:00Z",
      "display_info": {
        "icon": "...",
        "points": 10,
        "rarity": "common"
      }
    }
  ],
  "stats": {
    "total_achievements": 5,
    "total_points": 45,
    "by_type": {"chapter_complete": 3, "xp_milestone": 2}
  }
}
```

---

### T054: Badge Renderer Service
**Status**: PLANNED
**File**: `backend/src/personalization/services/badge_service.py`
**Functionality**:
- Generate PNG badge images from achievement data
- Include icon, title, rarity color, earned date
- Support both PNG download and base64 encoding
- Use PIL/Pillow library for image generation

---

### T055: Achievement Tests
**Status**: PLANNED
**File**: `backend/src/personalization/tests/test_achievements.py`
**Test Coverage**:
- Achievement detection logic
- Duplicate prevention (same achievement awarded once)
- XP milestone thresholds
- Streak detection
- Stats calculation

---

### T056: Practice Question Generation ✅
**Status**: COMPLETE (from Phase 3)
**File**: `backend/src/personalization/services/practice_service.py`
**Method**:
```python
def generate_practice_questions(chapter_id: int, count: int = 5) -> List[Dict]
```

---

### T057: Practice Attempt Submission Endpoint
**Endpoint**: `POST /api/v1/users/{user_id}/progress/{chapter_id}/practice`
**Request**:
```json
{
  "answers": ["A", "B", "D", "C"]
}
```
**Response**:
```json
{
  "mastery_score": 85,
  "correct_answers": 3,
  "total_questions": 4,
  "attempt_number": 2,
  "highest_score": 90
}
```

---

### T058: Retry Functionality
**Endpoint**: `POST /api/v1/users/{user_id}/progress/{chapter_id}/retry`
**Behavior**:
1. Mark chapter as "in_progress" again
2. Reset mastery_score to 0
3. Increment retry_count
4. Return fresh practice questions

---

### T059: Learning Statistics Endpoint
**Endpoint**: `GET /api/v1/users/{user_id}/statistics`
**Response Includes**:
```json
{
  "time_per_chapter": {
    "1": 120,
    "2": 150,
    "3": 90
  },
  "mastery_per_chapter": {
    "1": 95,
    "2": 100,
    "3": 70
  },
  "learning_curve": {
    "skill_snapshots": [
      {"timestamp": "2026-02-01", "skill_level": 45},
      {"timestamp": "2026-02-03", "skill_level": 50},
      {"timestamp": "2026-02-06", "skill_level": 60}
    ],
    "improvement_rate_per_week": 7.5
  },
  "recommended_focus_areas": [
    {
      "chapter_id": 3,
      "mastery_score": 65,
      "reason": "Below 70% mastery",
      "suggested_action": "Review practice questions"
    }
  ]
}
```

---

### T060: Learning Curve Calculation
**File**: `backend/src/personalization/services/statistics_service.py`
**Features**:
- Track skill level snapshots over time
- Calculate improvement rate (points/week)
- Detect plateaus (no change for 7+ days)
- Detect regressions (skill decrease)

---

### T061: Recommended Focus Areas Algorithm
**Logic**:
1. Identify chapters with mastery_score < 60%
2. Filter by chapters in current learning path
3. Suggest related/prerequisite chapters
4. Recommend practice attempt count

---

### T062: Advanced Challenges for High Mastery
**Criteria**: mastery_score > 85%
**Features**:
1. Offer research paper summaries
2. Generate advanced practice questions
3. Suggest extension topics
4. Provide optimization challenges

---

### T063: Practice & Stats Tests
**Status**: PLANNED
**File**: `backend/src/personalization/tests/test_practice_stats.py`
**Coverage**:
- Practice question generation
- Mastery score calculation
- Retry logic
- Statistics accuracy
- Learning curve calculations
- Focus area recommendations

---

## Implementation Priority

### High Priority (Must Have for MVP)
- [x] T050: Achievement definitions
- [x] T056: Practice questions
- [ ] T051: Achievement detection
- [ ] T057: Practice submission endpoint
- [ ] T059: Statistics endpoint

### Medium Priority (Should Have)
- [ ] T053: Get achievements endpoint
- [ ] T058: Retry functionality
- [ ] T060: Learning curve
- [ ] T061: Focus areas

### Low Priority (Nice to Have)
- [ ] T054: Badge renderer
- [ ] T062: Advanced challenges
- [ ] T055, T063: Full test coverage

---

## Database Schema

### Achievement Model
```sql
achievements {
  achievement_id: TEXT PRIMARY KEY
  user_id: UUID FOREIGN KEY
  achievement_type: TEXT (chapter_complete, xp_milestone, etc)
  title: TEXT
  description: TEXT
  display_info: JSONB {
    icon: STRING,
    points: INT,
    rarity: STRING
  }
  earned_date: TIMESTAMP
}
```

### PracticeAttempt Model (Already Exists)
```sql
practice_attempts {
  attempt_id: UUID PRIMARY KEY
  user_id: UUID FOREIGN KEY
  chapter_id: INT
  answers: JSONB (array)
  mastery_score: INT
  attempt_number: INT
  created_at: TIMESTAMP
}
```

---

## API Endpoints Summary

| Task | Endpoint | Method | Status |
|------|----------|--------|--------|
| T053 | `/api/v1/users/{id}/achievements` | GET | TODO |
| T057 | `/api/v1/users/{id}/progress/{ch}/practice` | POST | TODO |
| T058 | `/api/v1/users/{id}/progress/{ch}/retry` | POST | TODO |
| T059 | `/api/v1/users/{id}/statistics` | GET | TODO |

---

## Testing Strategy

### Unit Tests (T055, T063)
- Achievement detection logic with mock data
- Score calculation algorithms
- Recommendation algorithm

### Integration Tests
- End-to-end practice attempt flow
- Achievement unlock flow
- Statistics calculation accuracy

### Test Files to Create
- `test_achievement_service.py` (20+ tests)
- `test_practice_statistics.py` (25+ tests)

---

## Performance Considerations

1. **Achievement Checking**: Should be lightweight (< 50ms)
2. **Statistics Calculation**: Cache for 5 minutes
3. **Learning Curve**: Pre-calculate snapshots weekly
4. **Focus Areas**: Calculate on-demand (< 200ms)

---

## Next Steps

1. **Complete Achievement Service** (T051)
   - Implement _check_mastery_achievements()
   - Implement _check_streak_achievements()
   - Full duplicate prevention

2. **Create API Endpoints** (T053, T057-T059)
   - Integrate into routes/achievements.py
   - Add to routes/progress.py
   - Create routes/statistics.py

3. **Create Statistics Service** (T060-T061)
   - Implement learning curve calculation
   - Implement focus area algorithm
   - Create statistics_service.py

4. **Write Comprehensive Tests** (T055, T063)
   - 45+ total tests
   - 100% pass rate target

5. **Create Badge Renderer** (T054)
   - Use PIL library
   - Generate PNG files
   - Support base64 encoding

---

## Risk Mitigation

- **Achievement Duplicates**: Use unique constraint on (user_id, achievement_id)
- **Performance**: Implement caching for statistics
- **Data Accuracy**: Validate scores before storage
- **User Experience**: Batch notification on chapter completion

---

## Success Criteria for Phase 5

- [ ] 32+ achievement types defined
- [ ] Achievement detection working (no duplicates)
- [ ] 4+ new API endpoints
- [ ] Statistics calculated accurately
- [ ] 45+ tests created with 100% pass rate
- [ ] Response times < 500ms for all endpoints
- [ ] Production-ready code

---

## Files to Create/Modify

**Create**:
- achievement_service.py (simplified version created)
- badge_service.py (for badges)
- statistics_service.py
- routes/achievements.py
- routes/statistics.py
- test_achievements.py
- test_practice_stats.py

**Modify**:
- routes/progress.py (integrate achievements)
- models/db_models.py (if needed)

**Already Done**:
- achievements.json (created)
- practice_service.py (partially exists)

---

**Estimated Effort**: 16-20 hours for complete implementation
**Target Completion**: Within 2-3 sessions

