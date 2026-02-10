# Features & Architecture

Comprehensive documentation of the Personalization System's core features.

## 1. Progress Tracking

### What It Does
Monitors your learning journey with detailed progress tracking:

- **Chapter Completion** - Mark chapters as complete with mastery score (0-100%)
- **Time Tracking** - Records total time spent per chapter
- **Practice History** - Tracks all practice attempt scores
- **Highest Score** - Maintains your best mastery score per chapter

### How to Use

**Complete a Chapter:**
```bash
POST /api/v1/progress/{chapter_id}/complete
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "mastery_score": 85,
  "time_spent_seconds": 1800
}
```

**Retry a Chapter:**
```bash
POST /api/v1/progress/{chapter_id}/retry
Authorization: Bearer {access_token}
```

This resets your progress and lets you practice again.

**Get Your Progress:**
```bash
GET /api/v1/dashboard/metrics
Authorization: Bearer {access_token}

Response:
{
  "completion_percentage": 45,
  "chapters_completed": 10,
  "total_xp": 2500,
  "achievements_unlocked": 8,
  "current_streak_days": 3
}
```

### Behind the Scenes
- Progress stored in PostgreSQL with transactions
- Real-time calculation of completion percentage
- Mastery scores computed from practice attempts
- Time tracking via database timestamps

---

## 2. Achievement System

### What It Does
Gamifies your learning with 32 unique achievements to unlock:

| Achievement Type | Trigger | Reward |
|------------------|---------|--------|
| **Chapter Complete** | Finish any chapter | 10 XP |
| **First Chapter** | Complete Chapter 1 | 25 XP + Badge |
| **XP Milestones** | Reach 100/500/1000/5000 XP | 50/100/200/500 XP |
| **Perfect Score** | 100% mastery on chapter | 100 XP |
| **Learning Streak** | 7/30 consecutive days | 50/200 XP |
| **Module Complete** | Finish entire module | 200 XP |

### How Achievements Work

**Automatic Detection**
- System detects achievement triggers automatically
- When you complete a chapter → achievement unlocked immediately
- No manual steps needed

**View Your Achievements:**
```bash
GET /api/v1/progress/{user_id}/achievements
Authorization: Bearer {access_token}

Response:
{
  "achievements": [
    {
      "id": "ch_01_complete",
      "title": "Chapter 1 Complete",
      "description": "Finished Chapter 1: Foundations",
      "icon": "📘",
      "points": 10,
      "rarity": "common",
      "earned_date": "2026-02-07T10:30:00Z"
    },
    {
      "id": "first_chapter",
      "title": "First Steps",
      "description": "Completed your first chapter",
      "icon": "🚀",
      "points": 25,
      "rarity": "rare",
      "earned_date": "2026-02-07T10:35:00Z"
    }
  ],
  "stats": {
    "total_achievements": 8,
    "total_points": 210,
    "by_type": {
      "chapter": 3,
      "xp": 2,
      "streak": 1,
      "mastery": 2
    }
  }
}
```

### Achievement Categories

**Chapter Achievements** (1 per chapter + first bonus)
- Unlock when you complete any chapter
- "Chapter X Complete" badge
- First chapter completion bonus: +15 extra XP

**XP Milestones**
- 100 XP: Bronze milestone
- 500 XP: Silver milestone
- 1000 XP: Gold milestone
- 5000 XP: Platinum milestone

**Mastery Achievements**
- Perfect Score: 100% mastery on chapter
- Can unlock multiple per chapter (cumulative)
- Indicates expert-level understanding

**Streak Achievements**
- 7-day streak: 1 week consecutive learning
- 30-day streak: 1 month consecutive learning
- Resets if you miss a day

**Module Achievements**
- Complete all chapters in a module
- Module 1 Complete: Foundations mastered
- Module 2 Complete: ROS2 & Development mastered

### Behind the Scenes
- Achievement detection triggers on chapter completion
- Duplicate prevention with database unique constraints (user_id, achievement_type)
- Badge rendering using PIL (Python Imaging Library)
- Icons and metadata stored in database

---

## 3. Learning Recommendations

### What It Does
Analyzes your learning and suggests personalized recommendations:

- **Weak Chapter Identification** - Chapters where you scored &lt;60%
- **Related Content** - Chapters that build on each other
- **Practice Suggestions** - Specific areas to focus on
- **Priority Ranking** - Most impactful chapters to improve
- **Time Estimation** - How long improvement will take

### How to Get Recommendations

**Fetch Recommendations:**
```bash
GET /api/v1/users/{user_id}/statistics
Authorization: Bearer {access_token}

Response:
{
  "statistics": {
    "total_time_hours": 12.5,
    "mastery_per_chapter": {
      "1": 95,
      "2": 88,
      "3": 45,
      "4": 72
    }
  },
  "recommended_focus_areas": [
    {
      "chapter_id": 3,
      "title": "Chapter 3: Advanced Kinematics",
      "current_mastery": 45,
      "target_mastery": 85,
      "estimated_hours": 3,
      "priority": 1,
      "reason": "Foundation for Chapter 4 & 5",
      "practice_suggestions": [
        {
          "type": "fundamentals",
          "difficulty": "medium",
          "focus": "Basic kinematics equations"
        }
      ]
    }
  ]
}
```

### Recommendation Engine

**Algorithm:**
1. Identify weak chapters (mastery &lt; 60%)
2. Map chapter prerequisites using module structure
3. Calculate improvement efficiency (time vs. mastery gain)
4. Sort by priority (impact on dependent chapters)
5. Estimate time to reach 85% mastery (5 points/hour average)
6. Suggest specific practice areas

**Module Prerequisites:**
- Module 1 → Module 2 (Foundations required)
- Module 2 → Module 3 (ROS2 knowledge needed)
- Module 3 → Module 4 (Advanced concepts required)
- Module 4 → Module 5 (Control & learning needed)

### Behind the Scenes
- Statistics calculated from progress database
- Learning curve analysis with polynomial fitting
- Recommendation engine written in Python
- Real-time calculation based on latest scores

---

## 4. Learning Statistics & Analysis

### What It Does
Analyzes your learning patterns and trends:

- **Time Per Chapter** - How long you spent on each chapter
- **Mastery Progress** - Your score on each chapter
- **Learning Curve** - How fast you're improving
- **Improvement Trends** - Accelerating or plateauing
- **Focus Areas** - Where you need help most

### Access Your Statistics

**Get Comprehensive Statistics:**
```bash
GET /api/v1/users/{user_id}/statistics
Authorization: Bearer {access_token}

Response:
{
  "time_per_chapter": {
    "1": 90,
    "2": 120,
    "3": 180,
    "4": 150
  },
  "total_time_hours": 12.5,
  "mastery_per_chapter": {
    "1": 95,
    "2": 88,
    "3": 45,
    "4": 72
  },
  "learning_curve": {
    "trend": "improving",
    "improvement_rate_per_week": 2.5,
    "estimated_completion": "2026-03-15"
  },
  "recommended_focus_areas": [...]
}
```

### Learning Curve Analysis

**Trend Detection:**
- **Improving** - Your scores getting consistently better
- **Declining** - Scores dropping (might need review)
- **Plateau** - Scores stuck at same level (practice needed)

**Key Metrics:**
- Improvement rate: points/week
- Plateau detection: when scores don't improve
- Regression detection: when scores decline
- Completion estimate: based on current pace

### Behind the Scenes
- Time tracking via database timestamps
- Mastery scores from practice attempts
- Polynomial curve fitting for trend analysis
- Statistical calculations (mean, median, regression)

---

## 5. Advanced Challenges

### What It Does
Unlocks advanced content when you achieve mastery (&gt;85%):

- **Advanced Practice Questions** - Deeper, harder questions
- **Research Paper Summaries** - Academic papers related to content
- **Key Concepts** - Important ideas you should know
- **Real-World Applications** - How this applies in practice

### Unlock Advanced Challenges

**Check Eligibility:**
```bash
GET /api/v1/users/{user_id}/progress/{chapter_id}/advanced-challenges
Authorization: Bearer {access_token}

Response (if eligible):
{
  "mastery_level": 92,
  "challenge_type": "advanced",
  "metadata": {
    "difficulty": "expert",
    "estimated_time": 45
  },
  "questions": [
    {
      "id": "adv_ch1_q1",
      "title": "Advanced Question 1",
      "difficulty": "expert",
      "topic": "Foundations",
      "content": "...",
      "options": [...]
    }
  ],
  "papers": [
    {
      "id": "paper_1",
      "title": "Advanced Robotics Paper",
      "authors": ["Dr. Smith", "Prof. Johnson"],
      "year": 2023,
      "key_concepts": ["Kinematics", "Dynamics"],
      "summary": "...",
      "relevance": "Directly applies Chapter 1 concepts"
    }
  ]
}
```

### Advanced Content Categories

**Difficulty Levels:**
- **Easy** - Slightly harder than chapter content
- **Medium** - Requires deeper understanding
- **Hard** - Challenges your mastery
- **Expert** - Advanced research-level content

**Focus Areas:**
- **Fundamentals** - Core concepts at deeper level
- **Principles** - Why things work the way they do
- **Applications** - Real-world use cases
- **Advanced** - Cutting-edge research
- **Edge Cases** - Boundary conditions and exceptions

### Behind the Scenes
- Eligibility check: mastery_score > 85%
- Advanced questions stored separately in database
- Research papers with metadata from academic sources
- Relevance calculated based on chapter topics

---

## Feature Integration

All features work together to create a cohesive learning experience:

```
Progress Tracking
    ↓ (triggers)
Achievement Detection
    ↓ (generates XP)
Statistics Calculation
    ↓ (analyzes patterns)
Recommendation Engine
    ↓ (suggests focus)
Advanced Challenges (if mastery > 85%)
    ↓ (deepens learning)
Next Level Understanding
```

---

## Next Steps

- **[Learning Paths](/docs/personalization/learning-paths)** - Structured learning journeys
- **[API Reference](/docs/api/endpoints)** - Use features via API
- **[Examples](/docs/api/examples)** - Real-world usage examples

