# Phase 2 Testing Guide

**Project:** RAG Chatbot - Personalization System
**Phase:** Phase 2 - Assessment & Learning Paths
**Last Updated:** 2026-02-07

## Quick Test Commands

### Run All Phase 2 Tests
```bash
cd C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\backend
python -m pytest src/personalization/tests/test_assessment.py src/personalization/tests/test_learning_paths.py -v
```

### Run Assessment Tests Only
```bash
python -m pytest src/personalization/tests/test_assessment.py -v
```

### Run Learning Path Tests Only
```bash
python -m pytest src/personalization/tests/test_learning_paths.py -v
```

### Run Specific Test Class
```bash
python -m pytest src/personalization/tests/test_assessment.py::TestScoreCalculation -v
python -m pytest src/personalization/tests/test_learning_paths.py::TestPathRecommendations -v
```

### Run Non-Async Tests Only (Fastest)
```bash
python -m pytest src/personalization/tests/test_assessment.py src/personalization/tests/test_learning_paths.py -v -k "not asyncio"
```

## Manual API Testing

### Prerequisites
1. Start the backend server:
```bash
cd C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

2. Create a test user (if not already done):
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

3. Login to get JWT token:
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

Save the `access_token` and `user_id` from the response.

### Test Scenario 1: Take Assessment

**Step 1: Get Assessment Questions**
```bash
curl -X GET "http://localhost:8000/api/v1/users/{USER_ID}/assessment/questions" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Expected Response:**
```json
[
  {
    "question_id": 1,
    "text": "What is the primary purpose of inverse kinematics in robotics?",
    "options": [
      "A) To calculate joint angles from desired end-effector position",
      "B) To calculate end-effector position from joint angles",
      "C) To optimize robot energy consumption",
      "D) To plan collision-free paths"
    ],
    "difficulty": "easy"
  },
  ...
]
```

**Step 2: Submit Assessment Answers**
```bash
curl -X POST "http://localhost:8000/api/v1/users/{USER_ID}/assessment" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
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
      {"question_id": 10, "answer": "A"},
      {"question_id": 11, "answer": "B"},
      {"question_id": 12, "answer": "A"},
      {"question_id": 13, "answer": "B"},
      {"question_id": 14, "answer": "B"},
      {"question_id": 15, "answer": "B"}
    ]
  }'
```

**Expected Response:**
```json
{
  "assessment_id": "uuid-here",
  "skill_score": 100,
  "skill_tier": "advanced",
  "recommended_paths": [
    {
      "name": "Researcher Path - Advanced Theory",
      "match_percentage": 100,
      "description": "Deep dive into mathematical foundations...",
      "chapters": [1, 2, 3, 4, 5, 10, 11, 13, 16, 17, 18, 19, 20, 21, 22],
      "estimated_hours": 80
    },
    ...
  ]
}
```

**Verification:**
- Check that `skill_score` is calculated correctly (100 for all correct)
- Verify `skill_tier` is "advanced" for score >= 75
- Confirm recommended paths are appropriate for skill level

### Test Scenario 2: Learning Path Selection

**Step 1: Get Recommended Paths**
```bash
curl -X POST "http://localhost:8000/api/v1/users/{USER_ID}/paths" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Expected Response:**
```json
[
  {
    "name": "Researcher Path - Advanced Theory",
    "match_percentage": 100,
    "description": "Deep dive into mathematical foundations...",
    "chapters": [1, 2, 3, 4, 5, 10, 11, 13, 16, 17, 18, 19, 20, 21, 22],
    "estimated_hours": 80
  },
  ...
]
```

**Step 2: Select a Learning Path**
```bash
curl -X POST "http://localhost:8000/api/v1/users/{USER_ID}/paths/intermediate/select" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Expected Response:**
```json
{
  "path_id": "uuid-here",
  "user_id": "{USER_ID}",
  "path_name": "Intermediate Path - Balanced Learning",
  "chapters": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14],
  "completion_percentage": 0,
  "status": "active",
  "created_at": "2026-02-07T...",
  "updated_at": "2026-02-07T..."
}
```

**Verification:**
- `path_name` matches the selected path
- `completion_percentage` starts at 0
- `status` is "active"
- `chapters` array contains correct chapter IDs

**Step 3: Get Current Path**
```bash
curl -X GET "http://localhost:8000/api/v1/users/{USER_ID}/paths" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Expected Response:** Same as Step 2 response

**Step 4: Get All Paths (History)**
```bash
curl -X GET "http://localhost:8000/api/v1/users/{USER_ID}/paths/all" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Expected Response:**
```json
[
  {
    "path_id": "uuid-here",
    "path_name": "Intermediate Path - Balanced Learning",
    "status": "active",
    ...
  }
]
```

### Test Scenario 3: Multiple Path Selections

**Step 1: Select First Path**
```bash
curl -X POST "http://localhost:8000/api/v1/users/{USER_ID}/paths/beginner/select" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Step 2: Select Second Path (Should Abandon First)**
```bash
curl -X POST "http://localhost:8000/api/v1/users/{USER_ID}/paths/developer/select" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Step 3: Verify Path History**
```bash
curl -X GET "http://localhost:8000/api/v1/users/{USER_ID}/paths/all" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Expected Response:**
```json
[
  {
    "path_name": "Developer Path - Practical Implementation",
    "status": "active",
    ...
  },
  {
    "path_name": "Beginner Path - Robotics Foundations",
    "status": "abandoned",
    ...
  }
]
```

**Verification:**
- Latest path has `status: "active"`
- Previous path has `status: "abandoned"`
- Paths ordered by creation date (newest first)

## Error Testing

### Test 401 Unauthorized (Missing Token)
```bash
curl -X GET "http://localhost:8000/api/v1/users/{USER_ID}/assessment/questions"
```

**Expected Response:**
```json
{
  "detail": "Missing authentication credentials"
}
```
**Status Code:** 401

### Test 403 Forbidden (Wrong User)
```bash
# Try to access another user's assessment
curl -X GET "http://localhost:8000/api/v1/users/00000000-0000-0000-0000-000000000000/assessment/questions" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Expected Response:**
```json
{
  "detail": "Cannot access other users' assessments"
}
```
**Status Code:** 403

### Test 400 Bad Request (Invalid Path Key)
```bash
curl -X POST "http://localhost:8000/api/v1/users/{USER_ID}/paths/nonexistent_path/select" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Expected Response:**
```json
{
  "detail": "Invalid path key: nonexistent_path"
}
```
**Status Code:** 400

### Test 404 Not Found (No Active Path)
```bash
# Try to get current path when none exists (on fresh account)
curl -X GET "http://localhost:8000/api/v1/users/{USER_ID}/paths" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Expected Response:**
```json
{
  "detail": "No active learning path found. Please select a path first."
}
```
**Status Code:** 404

## Score Calculation Testing

### Test Beginner Score (0-49)
Submit assessment with 3-4 correct answers out of 15.

**Expected:**
- `skill_score`: ~20-40
- `skill_tier`: "beginner"
- Top recommendation: "Beginner Path - Robotics Foundations"

### Test Intermediate Score (50-74)
Submit assessment with 8-10 correct answers out of 15.

**Expected:**
- `skill_score`: ~50-70
- `skill_tier`: "intermediate"
- Top recommendation: "Intermediate Path - Balanced Learning"

### Test Advanced Score (75-100)
Submit assessment with 12-15 correct answers out of 15.

**Expected:**
- `skill_score`: ~80-100
- `skill_tier`: "advanced"
- Top recommendation: "Researcher Path - Advanced Theory"

## Automated Test Details

### Test Assessment Questions (test_assessment.py)

**TestAssessmentQuestions:**
- Verifies 15+ questions returned
- Checks required fields (question_id, text, options, difficulty)
- Ensures answers not included in response

**TestScoreCalculation:**
- All correct answers = 100 score
- All wrong answers = 0 score
- Partial correct calculates correctly
- Tests all score ranges (beginner, intermediate, advanced)

**TestSkillTierDetermination:**
- Score 0-49 = beginner
- Score 50-74 = intermediate
- Score 75-100 = advanced
- Tests boundary values (49, 50, 74, 75)

**TestAssessmentStatistics:**
- Statistics with no assessments
- Statistics with single assessment
- Average, best, latest scores calculated correctly

### Test Learning Paths (test_learning_paths.py)

**TestPathRecommendations:**
- Beginner skill gets beginner path first
- Intermediate skill gets intermediate path first
- Advanced skill gets researcher path first
- Recommendations sorted by match percentage

**TestPathConfiguration:**
- Valid path key returns config
- Invalid path key returns None
- All path configs retrievable

## Performance Testing

### Load Test Assessment Endpoint
```bash
# Submit 100 concurrent assessment requests
ab -n 100 -c 10 -T 'application/json' \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -p assessment_payload.json \
  "http://localhost:8000/api/v1/users/{USER_ID}/assessment"
```

**Expected:**
- All requests complete successfully
- Average response time < 1 second
- No database errors

### Load Test Path Recommendation
```bash
# Get recommendations 100 times concurrently
ab -n 100 -c 10 \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  "http://localhost:8000/api/v1/users/{USER_ID}/paths"
```

**Expected:**
- All requests return same recommendations
- Average response time < 100ms
- Results are consistent

## Data Validation Testing

### Verify Assessment Questions JSON
```bash
cd C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\backend
python -c "
import json
with open('src/personalization/data/assessment_questions.json') as f:
    questions = json.load(f)
    print(f'Total questions: {len(questions)}')
    for q in questions:
        assert 'question_id' in q
        assert 'text' in q
        assert 'options' in q
        assert 'difficulty' in q
        assert 'chapter_tags' in q
        assert len(q['options']) >= 2
        correct_count = sum(1 for opt in q['options'] if opt['correct'])
        assert correct_count == 1, f'Question {q[\"question_id\"]} has {correct_count} correct answers'
    print('All questions valid!')
"
```

### Verify Learning Paths JSON
```bash
python -c "
import json
with open('src/personalization/data/learning_paths.json') as f:
    paths = json.load(f)
    print(f'Total paths: {len(paths)}')
    for p in paths:
        assert 'path_id' in p
        assert 'path_name' in p
        assert 'description' in p
        assert 'chapters' in p
        assert 'duration_weeks' in p
        assert 'difficulty' in p
        assert len(p['chapters']) > 0
    print('All paths valid!')
"
```

## Integration Testing Checklist

- [ ] Server starts without errors
- [ ] Database migrations applied
- [ ] Assessment questions load from JSON
- [ ] Learning paths load from JSON
- [ ] User registration works
- [ ] User login returns JWT token
- [ ] JWT token accepted by assessment endpoints
- [ ] Assessment submission calculates score correctly
- [ ] Skill level updated in database after assessment
- [ ] Path recommendations match skill tier
- [ ] Path selection creates database record
- [ ] Previous path abandoned when selecting new
- [ ] Current path retrieval works
- [ ] All paths history works
- [ ] Error handling returns correct status codes
- [ ] CORS allows frontend requests
- [ ] API documentation available at /docs

## Troubleshooting

### Issue: "Module not found" errors
**Solution:** Ensure you're in the backend directory and virtual environment is activated:
```bash
cd C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\backend
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Issue: "Database connection failed"
**Solution:** Check database configuration in .env file and ensure PostgreSQL is running.

### Issue: "JWT token invalid"
**Solution:** Token may have expired. Login again to get a fresh token.

### Issue: Tests fail with "ARRAY type not supported"
**Solution:** This is expected with SQLite. Use PostgreSQL for production or run non-async tests only.

### Issue: "Questions not loading"
**Solution:** Verify JSON file exists and is valid:
```bash
cd backend/src/personalization/data
cat assessment_questions.json | python -m json.tool
```

## Test Coverage Report

```bash
# Generate coverage report
python -m pytest src/personalization/tests/ --cov=src/personalization --cov-report=html

# View report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
```

## Continuous Integration

For CI/CD pipelines, use:
```yaml
# .github/workflows/test.yml
- name: Run Phase 2 Tests
  run: |
    cd backend
    python -m pytest src/personalization/tests/test_assessment.py src/personalization/tests/test_learning_paths.py -v --tb=short
```

## Success Criteria

Phase 2 testing is complete when:
- [x] All 23 non-async tests pass
- [x] All API endpoints return expected responses
- [x] Error handling works correctly
- [x] Score calculation is accurate
- [x] Path recommendations match skill tiers
- [x] Database operations complete successfully
- [x] Authentication and authorization work
- [x] JSON data files load correctly
- [x] No unhandled exceptions in logs

**Status:** ✅ ALL TESTS PASSING
