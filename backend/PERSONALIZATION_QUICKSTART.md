# Personalization Feature Quick Start Guide

## What's Been Built (Phases 0-3)

We've completed **35 out of 94 tasks** implementing:

### ✅ Authentication System
- User registration and login with JWT tokens
- Profile management
- Password security (bcrypt hashing)
- Token refresh mechanism

### ✅ Knowledge Assessment
- 10-question robotics quiz
- Skill scoring (0-100) and tier assignment
- Assessment history tracking

### ✅ Learning Paths
- 5 predefined learning paths
- Smart path recommendations based on skill
- Path selection and progress tracking

### ✅ Progress Tracking
- Chapter-level progress (22 chapters, 4 modules)
- Time tracking and mastery scoring
- Comprehensive dashboard with metrics

---

## Setup Instructions

### 1. Prerequisites
```bash
# Python 3.11+
python --version

# PostgreSQL database (Neon recommended)
# Ensure you have DATABASE_URL in .env
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `backend/.env` file:
```env
# Database
DATABASE_URL=postgresql://user:pass@host/dbname

# JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-min-32-characters-long

# Environment
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### 4. Initialize Database
```bash
# Create tables
python -c "
from src.database.connection import init_db
import asyncio
asyncio.run(init_db())
"
```

### 5. Run the API
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

---

## Testing the API

### Using the Interactive Docs (Swagger UI)

1. Open `http://localhost:8000/docs` in your browser
2. You'll see all available endpoints organized by tags

### Complete User Journey

#### Step 1: Register a New User
```bash
POST /api/v1/users/register

Request Body:
{
  "username": "robotics_student",
  "email": "student@example.com",
  "password": "SecurePass123!"
}

Response:
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "robotics_student"
}
```

**Save the `access_token` for subsequent requests!**

#### Step 2: Get Assessment Questions
```bash
GET /api/v1/users/{user_id}/assessment/questions
Authorization: Bearer <your_access_token>

Response:
[
  {
    "question_id": 1,
    "text": "What is the primary purpose of inverse kinematics?",
    "options": ["A) To calculate joint angles...", "B) ...", "C) ...", "D) ..."],
    "difficulty": "beginner"
  },
  // ... 9 more questions
]
```

#### Step 3: Submit Assessment
```bash
POST /api/v1/users/{user_id}/assessment
Authorization: Bearer <your_access_token>

Request Body:
{
  "answers": [
    {"question_id": 1, "answer": "A"},
    {"question_id": 2, "answer": "D"},
    {"question_id": 3, "answer": "B"},
    {"question_id": 4, "answer": "C"},
    {"question_id": 5, "answer": "B"},
    {"question_id": 6, "answer": "B"},
    {"question_id": 7, "answer": "B"},
    {"question_id": 8, "answer": "B"},
    {"question_id": 9, "answer": "B"},
    {"question_id": 10, "answer": "A"}
  ]
}

Response:
{
  "assessment_id": "...",
  "skill_score": 72,
  "skill_tier": "intermediate",
  "recommended_paths": [
    {
      "name": "Intermediate Path - Balanced Learning",
      "match_percentage": 100,
      "description": "Balanced approach covering theory and practice",
      "chapters": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14],
      "estimated_hours": 55
    },
    // ... more recommendations
  ]
}
```

#### Step 4: Select a Learning Path
```bash
POST /api/v1/users/{user_id}/paths/intermediate/select
Authorization: Bearer <your_access_token>

Response:
{
  "path_id": "...",
  "user_id": "...",
  "path_name": "Intermediate Path - Balanced Learning",
  "chapters": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14],
  "completion_percentage": 0,
  "status": "active",
  "created_at": "2026-02-04T10:30:00Z",
  "updated_at": "2026-02-04T10:30:00Z"
}
```

#### Step 5: Start Learning a Chapter
```bash
POST /api/v1/users/{user_id}/progress/1/start
Authorization: Bearer <your_access_token>

Response:
{
  "progress_id": "...",
  "user_id": "...",
  "chapter_id": 1,
  "completion_status": "in_progress",
  "time_spent_seconds": 0,
  "mastery_score": 0,
  "last_accessed_at": "2026-02-04T10:35:00Z",
  "practice_attempts": 0,
  "highest_practice_score": 0
}
```

#### Step 6: Track Time Spent
```bash
POST /api/v1/users/{user_id}/progress/1/time
Authorization: Bearer <your_access_token>

Request Body:
{
  "time_spent_seconds": 1800
}

Response: (updated progress with new time)
```

#### Step 7: Complete Chapter
```bash
POST /api/v1/users/{user_id}/progress/1/complete
Authorization: Bearer <your_access_token>

Request Body:
{
  "mastery_score": 85,
  "time_spent_seconds": 300
}

Response:
{
  "status": "completed",
  "achievement_unlocked": {
    "title": "First Steps",
    "description": "Completed your first chapter!",
    "icon_url": "/badges/first_chapter.svg",
    "points": 10
  },
  "next_recommendation": {
    "chapter_id": 2,
    "reason": "Next chapter in Intermediate Path - Balanced Learning",
    "from_path": true
  }
}
```

#### Step 8: View Progress Dashboard
```bash
GET /api/v1/users/{user_id}/progress
Authorization: Bearer <your_access_token>

Response:
{
  "chapters_completed": 1,
  "modules_completed": 0,
  "total_learning_time_hours": 0.58,
  "current_skill_level": 72,
  "current_path": {
    "path_id": "...",
    "path_name": "Intermediate Path - Balanced Learning",
    "chapters": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14],
    "completion_percentage": 8,
    "status": "active"
  },
  "achievements": [],
  "learning_statistics": {
    "1": {
      "completion_status": "completed",
      "mastery_score": 85,
      "time_spent_hours": 0.58,
      "practice_attempts": 0,
      "highest_practice_score": 0,
      "last_accessed": "2026-02-04T10:40:00Z"
    }
  }
}
```

---

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### Get Profile (with token)
```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Running Tests

### Unit Tests
```bash
cd backend
pytest tests/unit/personalization/test_auth.py -v
```

Expected output:
```
test_auth.py::TestPasswordHashing::test_hash_password_creates_different_hashes PASSED
test_auth.py::TestPasswordHashing::test_verify_password_success PASSED
test_auth.py::TestPasswordValidation::test_validate_strong_password PASSED
test_auth.py::TestTokenCreation::test_create_access_token PASSED
test_auth.py::TestTokenVerification::test_verify_access_token_valid PASSED
...
30+ tests PASSED
```

### Integration Tests
```bash
cd backend
pytest tests/integration/personalization/test_user_endpoints.py -v
```

Expected output:
```
test_user_endpoints.py::TestUserRegistration::test_register_user_success PASSED
test_user_endpoints.py::TestUserLogin::test_login_success PASSED
test_user_endpoints.py::TestGetCurrentUser::test_get_current_user_success PASSED
...
25+ tests PASSED
```

### Run All Tests
```bash
cd backend
pytest tests/unit/personalization/ tests/integration/personalization/ -v
```

---

## API Endpoints Reference

### Authentication Endpoints
```
POST   /api/v1/users/register       - Register new user
POST   /api/v1/users/login          - Login and get tokens
POST   /api/v1/users/refresh        - Refresh access token
POST   /api/v1/users/logout         - Logout (client-side token removal)
GET    /api/v1/users/me             - Get current user profile
PUT    /api/v1/users/me             - Update profile
GET    /api/v1/users/{user_id}      - Get user by ID
```

### Assessment & Learning Paths
```
GET    /api/v1/users/{user_id}/assessment/questions       - Get questions
POST   /api/v1/users/{user_id}/assessment                 - Submit assessment
POST   /api/v1/users/{user_id}/paths                      - Get recommendations
POST   /api/v1/users/{user_id}/paths/{path_key}/select    - Select path
GET    /api/v1/users/{user_id}/paths                      - Get active path
GET    /api/v1/users/{user_id}/paths/all                  - Get all paths
```

### Progress Tracking
```
POST   /api/v1/users/{user_id}/progress/{chapter_id}/start      - Start chapter
POST   /api/v1/users/{user_id}/progress/{chapter_id}/complete   - Complete chapter
POST   /api/v1/users/{user_id}/progress/{chapter_id}/time       - Track time
GET    /api/v1/users/{user_id}/progress                         - Get dashboard
GET    /api/v1/users/{user_id}/progress/{chapter_id}            - Get chapter progress
```

---

## Database Schema

### Users Table
```sql
users (
  user_id UUID PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  skill_level INTEGER DEFAULT 50 CHECK (skill_level BETWEEN 0 AND 100),
  skill_confidence INTEGER DEFAULT 50 CHECK (skill_confidence BETWEEN 0 AND 100),
  profile_picture_url TEXT,
  bio TEXT,
  preferences_json JSONB DEFAULT '{"explanation_style":"example_first",...}',
  created_at TIMESTAMP DEFAULT NOW(),
  last_login_at TIMESTAMP,
  deleted_at TIMESTAMP
)
```

### Knowledge Assessments Table
```sql
knowledge_assessments (
  assessment_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
  questions_json JSONB NOT NULL,
  calculated_skill_score INTEGER NOT NULL CHECK (0-100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

### Learning Paths Table
```sql
learning_paths (
  path_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
  path_name VARCHAR(100) NOT NULL,
  chapters_array INTEGER[] NOT NULL,
  completion_percentage INTEGER DEFAULT 0 CHECK (0-100),
  status VARCHAR(20) DEFAULT 'active' CHECK IN ('active','completed','abandoned'),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

### Progress Table
```sql
progress (
  progress_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
  chapter_id INTEGER NOT NULL CHECK (1-22),
  completion_status VARCHAR(20) DEFAULT 'not_started' CHECK IN ('not_started','in_progress','completed'),
  time_spent_seconds INTEGER DEFAULT 0,
  mastery_score INTEGER DEFAULT 0 CHECK (0-100),
  last_accessed_at TIMESTAMP DEFAULT NOW(),
  practice_attempts INTEGER DEFAULT 0,
  highest_practice_score INTEGER DEFAULT 0 CHECK (0-100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE (user_id, chapter_id)
)
```

---

## Common Issues & Solutions

### Issue: Database connection error
**Solution**: Ensure `DATABASE_URL` is set correctly in `.env` and database is accessible.

### Issue: JWT token errors
**Solution**: Ensure `SECRET_KEY` is set in `.env` (minimum 32 characters).

### Issue: "User already exists" on registration
**Solution**: Use a different username/email or check the database for existing users.

### Issue: Tests failing
**Solution**:
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check database is accessible
- Initialize auth config in tests

### Issue: 401 Unauthorized errors
**Solution**:
- Ensure you're including the `Authorization: Bearer <token>` header
- Check if token has expired (access tokens expire in 30 minutes)
- Use refresh token to get new access token

---

## Next Steps (Phases 4-7)

### Phase 4: Chat Personalization
- Extend chat endpoint to use user skill level
- Generate personalized responses based on preferences
- Add difficulty adjustment based on user performance

### Phase 5: Gamification
- Implement 30+ achievements
- Add practice questions for each chapter
- Create statistics and learning curve analysis

### Phase 6: Frontend Dashboard
- Build React dashboard with TypeScript
- Create charts for progress visualization
- Implement responsive design

### Phase 7: Production Readiness
- Add GDPR compliance (data export, account deletion)
- Comprehensive testing (E2E, performance, security)
- API documentation and deployment guide

---

## Development Workflow

### Adding a New Endpoint

1. **Define Pydantic Schema** (if needed)
```python
# backend/src/personalization/models/schemas.py
class NewFeatureRequest(BaseModel):
    field1: str
    field2: int
```

2. **Create Service Function**
```python
# backend/src/personalization/services/new_service.py
async def process_feature(db: AsyncSession, data: dict) -> Result:
    # Business logic here
    pass
```

3. **Create API Route**
```python
# backend/src/personalization/api/routes/new_route.py
@router.post("/api/v1/feature")
async def create_feature(
    data: NewFeatureRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await process_feature(db, data.model_dump())
    return result
```

4. **Add Tests**
```python
# backend/tests/unit/personalization/test_new_service.py
def test_process_feature():
    # Test service logic
    pass

# backend/tests/integration/personalization/test_new_endpoint.py
async def test_create_feature_endpoint(client):
    # Test API endpoint
    pass
```

5. **Update Documentation**
- Add endpoint to API docs
- Update IMPLEMENTATION_STATUS.md
- Add example to QUICKSTART.md

---

## File Locations

### Backend Files
```
backend/src/personalization/
├── models/
│   ├── db_models.py           - SQLAlchemy ORM models
│   └── schemas.py             - Pydantic request/response schemas
├── services/
│   ├── user_service.py        - User management logic
│   ├── assessment_service.py  - Assessment and scoring
│   ├── learning_path_service.py - Path recommendations
│   └── progress_service.py    - Progress tracking
├── api/
│   ├── dependencies.py        - Auth dependencies
│   └── routes/
│       ├── users.py           - Auth endpoints
│       ├── assessment.py      - Assessment/path endpoints
│       └── progress.py        - Progress endpoints
└── utils/
    └── auth.py                - JWT utilities

backend/tests/
├── unit/personalization/
│   └── test_auth.py
└── integration/personalization/
    └── test_user_endpoints.py
```

---

## Support & Resources

- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Implementation Status**: `backend/IMPLEMENTATION_STATUS.md`
- **Database Schema**: Defined in `backend/src/personalization/models/db_models.py`

---

## Quick Reference

### User Skill Tiers
- **Beginner**: 0-49 points
- **Intermediate**: 50-74 points
- **Advanced**: 75-100 points

### Learning Paths
- **Beginner**: 6 chapters, 30 hours
- **Intermediate**: 12 chapters, 55 hours
- **Developer**: 9 chapters, 45 hours
- **Researcher**: 15 chapters, 80 hours
- **Hardware**: 9 chapters, 40 hours

### Module Structure (22 chapters)
- **Module 1**: Chapters 1-6 (Introduction & Fundamentals)
- **Module 2**: Chapters 7-12 (Kinematics & Control)
- **Module 3**: Chapters 13-18 (Advanced Topics)
- **Module 4**: Chapters 19-22 (Applications & Future)

---

**Happy Learning! 🤖**
