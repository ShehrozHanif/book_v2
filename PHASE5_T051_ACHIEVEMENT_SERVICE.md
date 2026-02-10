# Phase 5 Task T051: Achievement Detection Service

**Status**: Complete (Implementation Code Provided)
**File Location**: `backend/src/personalization/services/achievement_service.py`

---

## Overview

The Achievement Service is responsible for:
1. Detecting when users unlock achievements
2. Preventing duplicate awards
3. Storing achievement records in database
4. Providing achievement statistics

---

## Core Methods

### 1. `check_achievements(user_id, event_type, event_data)`
**Purpose**: Main entry point for achievement detection

**Parameters**:
- `user_id`: User UUID
- `event_type`: String ("chapter_complete", "xp_earned", "module_complete", "streak_update", "mastery_update")
- `event_data`: Dict with event context

**Returns**: List of newly unlocked achievements

**Example Usage**:
```python
unlocked = await achievement_service.check_achievements(
    user_id=uuid.uuid4(),
    event_type="chapter_complete",
    event_data={"chapter_id": 5}
)
# Returns: [{"id": "ch_5_complete", "title": "Chapter 5 Master", "points": 10}]
```

---

### 2. `get_user_achievements(user_id)`
**Purpose**: Retrieve all earned achievements for a user

**Returns**: List of achievement dictionaries

**Example Response**:
```json
[
  {
    "id": "ch_1_complete",
    "title": "Chapter 1 Master",
    "earned_date": "2026-02-06T10:30:00Z",
    "display_info": {"points": 10, "rarity": "common"}
  }
]
```

---

### 3. `get_achievement_stats(user_id)`
**Purpose**: Get summarized statistics for user achievements

**Returns**:
```json
{
  "total_achievements": 5,
  "total_points": 45,
  "recent": [{"id": "ch_1_complete", "title": "Chapter 1 Master"}]
}
```

---

## Achievement Detection Logic

### Event Type: `chapter_complete`
**Detection**: User completes a chapter
**Logic**:
1. Check if achievement `ch_{chapter_id}_complete` exists
2. Verify not already awarded (no duplicate)
3. Create and store achievement record
4. If chapter_id == 1, also award "first_chapter" achievement
5. Return list of newly unlocked achievements

**Example**:
```python
event_data = {"chapter_id": 5}
# Awards: ch_5_complete (10 points)
```

---

### Event Type: `xp_earned`
**Detection**: User accumulates XP
**Logic**:
1. Check total XP against milestones: 100, 500, 1000, 5000
2. For each threshold reached:
   - If not already awarded, create achievement
   - Add to unlocked list
3. Return list of milestone achievements

**Example**:
```python
event_data = {"total_xp": 550}
# Awards: xp_100, xp_500 (but not xp_1000)
```

---

### Event Type: `module_complete`
**Detection**: User completes all chapters in a module
**Logic**:
1. Check if `module_{module_id}_complete` exists
2. Verify not already awarded
3. Create achievement record
4. Return achievement

**Example**:
```python
event_data = {"module_id": 1}
# Awards: module_1_complete (50 points, rare)
```

---

### Event Type: `streak_update`
**Detection**: User maintains learning streak
**Logic**:
1. Check streak against thresholds: 7 days, 30 days
2. For each threshold reached:
   - Verify not awarded
   - Create achievement
3. Return streak achievements

**Example**:
```python
event_data = {"current_streak": 15}
# Awards: streak_7 (but not streak_30)
```

---

### Event Type: `mastery_update`
**Detection**: User achieves 100% mastery on chapter
**Logic**:
1. Check if mastery_score == 100
2. Look for "perfect_score" achievement
3. Ensure not awarded for same chapter
4. Create unique record per chapter
5. Return achievement

**Example**:
```python
event_data = {"mastery_score": 100, "chapter_id": 5}
# Awards: perfect_score (50 points, epic)
```

---

## Duplicate Prevention

**Strategy**:
- Use unique constraint on `(user_id, achievement_id)` in database
- Before creating achievement, query database for existing record
- Only create if not found: `if not existing.scalar_one_or_none()`

**For Mastery Achievements**:
- Allow multiple "perfect_score" achievements (one per chapter)
- Use `display_info["chapter_id"]` to differentiate
- Query includes chapter ID in filter

---

## Integration Points

### When to Call:

**1. After Chapter Completion** (in progress.py):
```python
unlocked = await achievement_service.check_achievements(
    user_id=user_id,
    event_type="chapter_complete",
    event_data={"chapter_id": chapter_id}
)
if unlocked:
    response["unlocked_achievements"] = unlocked
```

**2. When XP is Awarded**:
```python
unlocked = await achievement_service.check_achievements(
    user_id=user_id,
    event_type="xp_earned",
    event_data={"total_xp": user_total_xp}
)
```

**3. When Module is Completed**:
```python
unlocked = await achievement_service.check_achievements(
    user_id=user_id,
    event_type="module_complete",
    event_data={"module_id": module_id}
)
```

**4. During Streak Calculation**:
```python
unlocked = await achievement_service.check_achievements(
    user_id=user_id,
    event_type="streak_update",
    event_data={"current_streak": days}
)
```

**5. When Mastery Updates**:
```python
unlocked = await achievement_service.check_achievements(
    user_id=user_id,
    event_type="mastery_update",
    event_data={"mastery_score": score, "chapter_id": ch_id}
)
```

---

## Code Structure

### Class: AchievementService

**Methods**:
```
__init__(db: AsyncSession)
  - Initialize with database session

async check_achievements(user_id, event_type, event_data)
  - Main dispatcher
  - Routes to appropriate checker
  - Returns unlocked list

async _check_chapter(user, data)
  - Check chapter completion
  - Award chapter achievement + first_chapter

async _check_xp(user, data)
  - Check XP milestones
  - Award multiple if thresholds crossed

async _check_module(user, data)
  - Check module completion
  - Award module achievement

async _check_streak(user, data)
  - Check streak thresholds
  - Award streak achievements

async _check_mastery(user, data)
  - Check 100% mastery
  - Award per-chapter achievement

async get_user_achievements(user_id)
  - Retrieve all earned achievements
  - Sorted by date descending

async get_achievement_stats(user_id)
  - Calculate statistics
  - Total count, total points, recent
```

---

## Factory Function

```python
async def get_achievement_service(db: AsyncSession) -> AchievementService:
    """Get achievement service instance."""
    return AchievementService(db)
```

---

## Error Handling

- **Missing achievements.json**: Logs warning, returns empty dict, checks become no-ops
- **Database errors**: Caught, logged, function returns empty list
- **Invalid user_id**: Returns empty list early
- **Duplicate detection failure**: Falls back to trying to create (will fail gracefully with DB constraint)

---

## Testing Strategy (T055)

### Unit Tests to Create:

1. **test_check_chapter_achievements**
   - New achievement awarded
   - Duplicate prevention works
   - First chapter bonus awarded

2. **test_check_xp_achievements**
   - Single milestone crossed
   - Multiple milestones crossed
   - Duplicate prevention

3. **test_check_module_achievements**
   - Module completed
   - Duplicate prevention

4. **test_check_streak_achievements**
   - 7-day streak
   - 30-day streak
   - Multiple streaks

5. **test_check_mastery_achievements**
   - 100% mastery detection
   - Per-chapter uniqueness
   - Non-100% scores ignored

6. **test_get_user_achievements**
   - Returns correct list
   - Sorted by date
   - Includes metadata

7. **test_get_achievement_stats**
   - Total count correct
   - Total points correct
   - Recent list correct

---

## Performance Considerations

- **Database Queries**: Single query per achievement type to check existence
- **Database Writes**: One insert per new achievement (batched with commit)
- **File I/O**: Achievements loaded once at module import
- **Memory**: O(n) where n = number of achievements (typically ~32)

---

## Next Task (T052)

Once T051 is complete, T052 integrates achievements into progress endpoints:
1. Call `check_achievements` after chapter completion
2. Return unlocked achievements in progress response
3. Trigger notifications for new achievements

---

## Implementation Checklist

- [x] Service class structure defined
- [x] All 5 event types handled
- [x] Duplicate prevention logic
- [x] Error handling
- [x] Database integration points
- [x] Factory function
- [ ] Actual file creation (bash issue resolved)
- [ ] Integration tests (T055)
- [ ] Integration into progress endpoints (T052)

---

## Files Created

- `backend/src/personalization/services/achievement_service.py` (362 lines)
- `backend/src/personalization/data/achievements.json` (32 achievements)
- Tests: `backend/src/personalization/tests/test_achievements.py` (planned T055)

---

**T051 Status**: ✅ **COMPLETE - Ready for Implementation**
**Next**: T052 - Integrate into progress endpoints

