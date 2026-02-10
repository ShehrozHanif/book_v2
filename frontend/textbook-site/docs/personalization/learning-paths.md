# Learning Paths

Structured learning journeys personalized to your goals and pace.

## What is a Learning Path?

A Learning Path is a curated sequence of chapters designed to guide you through the curriculum effectively:

- **Personalized** - Adapted to your current level and progress
- **Goal-Oriented** - Aligned with your learning objectives
- **Scaffolded** - Prerequisites built before advanced content
- **Flexible** - Can be adapted as you learn
- **Trackable** - Monitor progress within the path

## Built-in Learning Paths

### 1. Foundations First (Beginner)
**Goal**: Master fundamental concepts

**Sequence**:
1. Chapter 1 - Foundations Basics
2. Chapter 2 - Core Concepts
3. Chapter 3 - Intermediate Applications
4. Chapter 4 - First Principles Deep Dive
5. Chapter 5 - Capstone Project

**Duration**: 4-6 weeks
**Effort**: 8-10 hours/week
**Difficulty**: ★☆☆

**Best for**: Students new to the subject

---

### 2. Fast Track (Intermediate)
**Goal**: Reach proficiency quickly

**Sequence**:
1. Chapter 1 - Foundations (Review)
2. Chapter 3 - Advanced Kinematics
3. Chapter 6 - ROS2 Development
4. Chapter 9 - Control Systems
5. Chapter 12 - Advanced Concepts

**Duration**: 2-3 weeks
**Effort**: 12-15 hours/week
**Difficulty**: ★★☆

**Best for**: Intermediate learners seeking depth

---

### 3. Mastery Track (Advanced)
**Goal**: Achieve expert-level understanding

**Sequence**:
1. Chapters 1-5 - Complete Module 1
2. Chapters 6-10 - Complete Module 2
3. Chapters 11-15 - Complete Module 3
4. Chapters 16+ - Advanced Applications
5. Research Papers & Advanced Challenges

**Duration**: 8-12 weeks
**Effort**: 15-20 hours/week
**Difficulty**: ★★★

**Best for**: Advanced learners seeking mastery

---

### 4. Project-Based (Practical)
**Goal**: Build real projects while learning

**Sequence**:
1. Chapters 1-2 - Foundations
2. Chapter 6-8 - ROS2 Development
3. Project: Build Simple Robot Simulator
4. Chapters 9-10 - Control & Motion
5. Project: Implement Advanced Controller
6. Chapters 11-15 - Advanced Topics
7. Project: Full Application Development

**Duration**: 10-14 weeks
**Effort**: 12-18 hours/week
**Difficulty**: ★★★

**Best for**: Hands-on learners who learn by doing

---

## How Learning Paths Work

### Selection Process

1. **Take Assessment** - Answer questions about your background
2. **System Recommends** - Path matches your level and goals
3. **View Path Details** - See recommended chapters and timeline
4. **Select Path** - Commit to the learning journey
5. **Get Personalized Progress** - Track completion and recommendations

### Progress Tracking

For each chapter in your path:
- **Target Mastery**: 85% for pathway completion
- **Estimated Time**: Time recommendation per chapter
- **Prerequisites**: What to complete first
- **Related Resources**: Links to additional material
- **Practice Focus**: Areas to emphasize

### Recommendations During Path

The system provides ongoing recommendations:
- **Weak Areas**: Chapters to review or retry
- **Next Steps**: Recommended next chapters
- **Skip Suggestions**: If you master content early
- **Time Estimates**: How long to reach goals
- **Focus Areas**: What needs attention

## Creating Custom Paths

### Path Customization

While using a built-in path, you can:

- **Swap Chapters** - Rearrange order based on interests
- **Skip Ahead** - If prerequisites already mastered
- **Combine Paths** - Mix elements from multiple paths
- **Add Resources** - Include external materials
- **Adjust Pace** - Slower or faster based on progress

### API for Custom Paths

**Get Available Paths:**
```bash
GET /api/v1/learning-paths
Authorization: Bearer {token}

Response:
{
  "paths": [
    {
      "id": "foundations_first",
      "name": "Foundations First",
      "description": "Master fundamental concepts",
      "difficulty": "beginner",
      "duration_weeks": 6,
      "hours_per_week": 10,
      "chapters": [1, 2, 3, 4, 5]
    },
    {
      "id": "fast_track",
      "name": "Fast Track",
      "description": "Reach proficiency quickly",
      "difficulty": "intermediate",
      "duration_weeks": 3,
      "hours_per_week": 15,
      "chapters": [1, 3, 6, 9, 12]
    }
  ]
}
```

**Select a Path:**
```bash
POST /api/v1/learning-paths/select
Authorization: Bearer {token}
Content-Type: application/json

{
  "path_id": "foundations_first"
}

Response:
{
  "status": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "selected_path": "foundations_first",
    "started_at": "2026-02-07T10:30:00Z",
    "estimated_completion": "2026-03-20T23:59:00Z",
    "current_chapter": 1,
    "progress_percentage": 0
  }
}
```

## Path Recommendations

The system recommends paths based on:

### Initial Assessment
- **Background Knowledge** - What you already know
- **Learning Goals** - What you want to achieve
- **Available Time** - How much time you can dedicate
- **Learning Style** - How you learn best

### Dynamic Adaptation
- **Actual Progress** - Based on mastery scores
- **Learning Pace** - How fast you're progressing
- **Struggle Areas** - Where you need help
- **Performance Trends** - Improvement trajectory

### Recommendation Changes
If data suggests better path:
- System notifies you
- Recommends switch with justification
- Easy to adopt new path
- Keeps progress from previous chapters

## Path Statistics

### Track Your Progress

**View Path Progress:**
```bash
GET /api/v1/users/{user_id}/statistics
Authorization: Bearer {token}

Response includes:
{
  "selected_path": {
    "id": "foundations_first",
    "name": "Foundations First",
    "progress_percentage": 45,
    "chapters_completed": 2,
    "total_chapters": 5,
    "estimated_completion_date": "2026-03-20",
    "is_on_track": true,
    "pace_adjustment": "normal"
  }
}
```

### Key Metrics

| Metric | Meaning |
|--------|---------|
| **Progress** | % of path chapters completed |
| **Mastery Score** | Average across all chapters |
| **Time Invested** | Total hours in this path |
| **Pace** | Fast, Normal, or Slow |
| **On Track?** | Will complete on estimated date |

## Switching Paths

### Can I Change Paths?

**Yes!** You can switch paths at any time:

1. **View Available Paths** - See all options
2. **Compare Paths** - See differences
3. **Select New Path** - Switch with one click
4. **Keep Progress** - All completed chapters count
5. **Resume Progress** - Continue where you left off

**Example:**
```bash
POST /api/v1/learning-paths/select
Authorization: Bearer {token}

{
  "path_id": "fast_track",
  "keep_progress": true
}
```

## Accelerated Paths

### Skip Ahead

If you already know material:

1. **Take Pre-Assessment** - Demonstrate knowledge
2. **Prove Mastery** - Score 90%+ on assessment
3. **Skip Chapters** - Approved chapters skipped
4. **Keep Credits** - Completion still counts
5. **Accelerate Progress** - Move faster through path

---

## Tips for Success

1. **Choose Right Path** - Match your level and goals
2. **Follow Sequentially** - Respect prerequisites
3. **Hit Target Mastery** - Aim for 85%+ before moving on
4. **Use Recommendations** - Follow suggested focus areas
5. **Track Progress** - Monitor time and performance
6. **Stay Consistent** - Regular learning beats cramming
7. **Ask Questions** - Don't get stuck on hard topics
8. **Celebrate Wins** - Acknowledge achievements

---

## Next Steps

- **[Get Started](/docs/deployment/quick-start)** - Begin learning
- **[View Features](/docs/personalization/features)** - Understand system
- **[API Reference](/docs/api)** - Access paths programmatically

---

**Ready to select your path?** Start with [Quick Start](/docs/deployment/quick-start).
