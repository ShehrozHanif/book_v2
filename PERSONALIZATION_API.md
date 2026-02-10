# Personalization System API Documentation

**Version**: 1.0.0
**Base URL**: `http://localhost:8000/api/v1` (development) | `https://api.personalization.example.com/api/v1` (production)
**API Format**: REST with JSON
**Authentication**: JWT Bearer Token

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [Endpoints](#endpoints)
6. [Examples](#examples)
7. [SDKs](#sdks)

---

## Getting Started

### Prerequisites
- HTTP client (curl, Postman, requests library)
- Valid credentials or registration capability
- Internet connection to API server

### Base URL Structure
```
Protocol: HTTPS (production)
Domain: api.personalization.example.com
Version: v1
Format: /api/v1/{resource}/{id}/{action}
```

### API Response Format
All responses are JSON with the following structure:

**Success Response** (2xx):
```json
{
  "status": "success",
  "data": { /* response data */ },
  "timestamp": "2026-02-07T10:30:00Z"
}
```

**Error Response** (4xx/5xx):
```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "detail": "Human-readable error message",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

---

## Authentication

### Overview
The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid access token.

### Authentication Flow

#### 1. Register New User
```bash
POST /api/v1/users/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}

Response (201):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe"
}
```

#### 2. Login
```bash
POST /api/v1/users/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123!"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 3. Use Token in Requests
```bash
GET /api/v1/users/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Details

**Access Token**:
- Validity: 30 minutes
- Use for: API requests
- Included in: Authorization header

**Refresh Token**:
- Validity: 7 days
- Use for: Obtaining new access token
- Store securely: Never expose to frontend

### Refresh Access Token
```bash
POST /api/v1/users/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*)

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When | Retry |
|------|---------|------|-------|
| 200 | OK | Request succeeded | No |
| 201 | Created | Resource created | No |
| 400 | Bad Request | Invalid input | No |
| 401 | Unauthorized | Missing/invalid token | Refresh token |
| 403 | Forbidden | Insufficient permissions | No |
| 404 | Not Found | Resource not found | No |
| 409 | Conflict | Resource already exists | No |
| 429 | Too Many Requests | Rate limit exceeded | Yes, after delay |
| 500 | Server Error | Internal server error | Yes, exponential backoff |

### Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| INVALID_REQUEST | Request validation failed | Check request format and parameters |
| INVALID_TOKEN | Token expired or invalid | Refresh token or re-authenticate |
| USER_NOT_FOUND | User doesn't exist | Register new user or check email |
| DUPLICATE_USER | Email/username already exists | Use different email/username |
| RATE_LIMIT_EXCEEDED | Too many requests | Wait and retry |
| INTERNAL_ERROR | Server-side error | Contact support |

### Error Response Example
```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "detail": "Email format is invalid",
  "field": "email",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

---

## Rate Limiting

### Limits by Endpoint Category

| Category | Limit | Window | Notes |
|----------|-------|--------|-------|
| Authentication | 5 requests | 5 minutes | Login, register endpoints |
| Registration | 3 requests | 1 hour | /users/register only |
| General API | 100 requests | 1 minute | All other endpoints |
| Dashboard | 10 requests | 1 minute | Heavy computation |

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1644242400
```

### Handling Rate Limits

**When rate limit exceeded** (429 response):
```bash
# Response headers
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1644242460

# Recommended: Exponential backoff
wait = 2^attempt  # 1s, 2s, 4s, 8s...
```

---

## Endpoints

### 1. Authentication Endpoints

#### POST /users/register
Register a new user account.

**Request**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (201):
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe"
}
```

**Errors**:
- 400: Invalid password, duplicate email/username
- 429: Too many registration attempts

---

#### POST /users/login
Authenticate user and get tokens.

**Request**:
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

**Response** (200):
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors**:
- 401: Invalid credentials
- 429: Too many login attempts

---

#### POST /users/refresh
Get new access token using refresh token.

**Request**:
```json
{
  "refresh_token": "..."
}
```

**Response** (200):
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors**:
- 401: Invalid refresh token

---

### 2. User Profile Endpoints

#### GET /users/profile
Get current user profile.

**Headers**: Authorization: Bearer {token}

**Response** (200):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "skill_level": 65,
  "skill_tier": "Intermediate",
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-02-07T10:00:00Z"
}
```

**Errors**:
- 401: Not authenticated
- 404: User not found

---

#### PUT /users/profile
Update user profile.

**Headers**: Authorization: Bearer {token}

**Request**:
```json
{
  "username": "john_doe_updated",
  "bio": "Learning robotics enthusiast",
  "skill_level": 70
}
```

**Response** (200):
```json
{
  "user_id": "...",
  "username": "john_doe_updated",
  "bio": "Learning robotics enthusiast",
  "skill_level": 70,
  "updated_at": "2026-02-07T10:30:00Z"
}
```

**Errors**:
- 401: Not authenticated
- 400: Invalid input
- 409: Username already exists

---

### 3. Progress Endpoints

#### POST /progress/{chapter_id}/complete
Mark a chapter as completed.

**Headers**: Authorization: Bearer {token}

**Path Parameters**:
- chapter_id: 1-22 (integer)

**Request**:
```json
{
  "mastery_score": 95,
  "time_spent_seconds": 1800
}
```

**Response** (200):
```json
{
  "chapter_id": 5,
  "completion_status": 95,
  "xp_earned": 500,
  "achievements_unlocked": [
    {
      "id": "ch_5_complete",
      "title": "Chapter 5 Master",
      "points": 50,
      "rarity": "uncommon"
    }
  ],
  "total_chapters_completed": 10
}
```

**Errors**:
- 401: Not authenticated
- 400: Invalid chapter_id (not 1-22)
- 400: Invalid mastery_score (not 0-100)

---

#### POST /progress/{chapter_id}/retry
Retry a chapter (resets progress).

**Headers**: Authorization: Bearer {token}

**Path Parameters**:
- chapter_id: 1-22 (integer)

**Response** (200):
```json
{
  "chapter_id": 5,
  "status": "reset",
  "practice_questions": [
    {
      "id": "q1",
      "question": "What is a servo motor?",
      "options": ["A", "B", "C", "D"],
      "difficulty": "medium"
    }
  ]
}
```

**Errors**:
- 401: Not authenticated
- 404: Chapter not found

---

#### POST /progress/{chapter_id}/practice
Submit practice answers and get score.

**Headers**: Authorization: Bearer {token}

**Path Parameters**:
- chapter_id: 1-22 (integer)

**Request**:
```json
{
  "answers": [
    {"question_id": "q1", "answer": "A"},
    {"question_id": "q2", "answer": "B"}
  ]
}
```

**Response** (200):
```json
{
  "mastery_score": 85,
  "correct_answers": 17,
  "total_questions": 20,
  "attempt_number": 3,
  "highest_score": 90,
  "feedback": "Great attempt! Review topics X, Y, Z for improvement."
}
```

**Errors**:
- 401: Not authenticated
- 400: Invalid chapter or answers

---

### 4. Dashboard Endpoints

#### GET /dashboard/metrics
Get comprehensive dashboard metrics.

**Headers**: Authorization: Bearer {token}

**Response** (200):
```json
{
  "user": {
    "username": "john_doe",
    "skill_level": 65,
    "skill_tier": "Intermediate"
  },
  "progress": {
    "chapters_completed": 10,
    "total_chapters": 22,
    "completion_percentage": 45.5,
    "total_time_hours": 12.5,
    "total_xp": 2500
  },
  "learning_path": {
    "current_path": "Robotics Fundamentals",
    "chapters_in_path": 7,
    "chapters_completed": 4,
    "progress_percentage": 57.1,
    "estimated_completion_date": "2026-03-01"
  },
  "achievements": {
    "badges_earned": 8,
    "badges": [
      {
        "title": "Chapter 1 Master",
        "earned_date": "2026-01-20T10:00:00Z"
      }
    ]
  },
  "statistics": {
    "average_mastery_score": 78.5,
    "most_mastered_chapter": 3,
    "least_mastered_chapter": 15,
    "learning_streak": 12,
    "last_activity": "2026-02-07T09:45:00Z"
  }
}
```

**Cache**: 60 seconds (with caching middleware)

**Errors**:
- 401: Not authenticated

---

### 5. Achievement Endpoints

#### GET /progress/{user_id}/achievements
Get user's achievements and statistics.

**Headers**: Authorization: Bearer {token}

**Path Parameters**:
- user_id: UUID string

**Response** (200):
```json
{
  "earned": [
    {
      "id": "ch_1_complete",
      "title": "Chapter 1 Complete",
      "description": "Completed the first chapter",
      "icon": "🏆",
      "points": 50,
      "rarity": "common",
      "earned_date": "2026-01-15T10:00:00Z"
    }
  ],
  "stats": {
    "total_achievements": 12,
    "total_points": 450,
    "by_type": {
      "chapter_complete": 8,
      "xp_earned": 3,
      "mastery": 1
    },
    "recent": [...]
  }
}
```

**Errors**:
- 401: Not authenticated
- 403: Cannot view other user's achievements
- 404: User not found

---

### 6. Statistics Endpoints

#### GET /users/{user_id}/statistics
Get comprehensive learning statistics.

**Headers**: Authorization: Bearer {token}

**Path Parameters**:
- user_id: UUID string

**Response** (200):
```json
{
  "time_per_chapter": {
    "1": 45.5,
    "2": 52.3,
    "3": 38.2
  },
  "total_time_hours": 12.5,
  "mastery_per_chapter": {
    "1": 95,
    "2": 88,
    "3": 100
  },
  "learning_curve": {
    "trend": "improving",
    "rate": 2.5,
    "plateaus": [],
    "regressions": []
  },
  "recommended_focus_areas": [
    {
      "chapter_id": 15,
      "current_mastery": 45,
      "recommendation": "Review fundamentals"
    }
  ]
}
```

**Cache**: 300 seconds (with caching middleware)

**Errors**:
- 401: Not authenticated
- 403: Insufficient permissions
- 404: User not found

---

### 7. Learning Path Endpoints

#### GET /learning-paths
Get available learning paths.

**Headers**: Authorization: Bearer {token}

**Response** (200):
```json
[
  {
    "path_id": "path_1",
    "path_name": "Robotics Fundamentals",
    "description": "Basic concepts of robotics",
    "chapters": [1, 2, 3, 4, 5],
    "difficulty": "beginner",
    "estimated_hours": 20
  }
]
```

**Cache**: 300 seconds

**Errors**:
- 401: Not authenticated

---

#### POST /learning-paths/select
Select a learning path.

**Headers**: Authorization: Bearer {token}

**Request**:
```json
{
  "path_id": "path_1"
}
```

**Response** (200):
```json
{
  "status": "selected",
  "path_id": "path_1",
  "path_name": "Robotics Fundamentals",
  "started_at": "2026-02-07T10:30:00Z"
}
```

**Errors**:
- 401: Not authenticated
- 404: Path not found

---

### 8. Preferences Endpoints

#### GET /users/{user_id}/preferences
Get user preferences.

**Headers**: Authorization: Bearer {token}

**Path Parameters**:
- user_id: UUID string

**Response** (200):
```json
{
  "learning_pace": "moderate",
  "theory_first": true,
  "notification_enabled": true,
  "timezone": "UTC",
  "language": "en"
}
```

**Errors**:
- 401: Not authenticated
- 403: Cannot view other user's preferences
- 404: User not found

---

#### PUT /users/{user_id}/preferences
Update user preferences.

**Headers**: Authorization: Bearer {token}

**Path Parameters**:
- user_id: UUID string

**Request**:
```json
{
  "learning_pace": "fast",
  "theory_first": false,
  "notification_enabled": true
}
```

**Response** (200):
```json
{
  "learning_pace": "fast",
  "theory_first": false,
  "notification_enabled": true,
  "updated_at": "2026-02-07T10:30:00Z"
}
```

**Errors**:
- 401: Not authenticated
- 403: Cannot modify other user's preferences
- 400: Invalid preference values

---

### 9. Health & Utility Endpoints

#### GET /health
Check API health status.

**Response** (200):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-07T10:30:00Z",
  "services": {
    "database": "healthy",
    "cache": "healthy"
  }
}
```

---

#### GET /ready
Check if API is ready to accept requests.

**Response** (200):
```json
{
  "status": "ready",
  "ready": true,
  "checks": {
    "database": "connected",
    "cache": "connected",
    "migrations": "applied"
  }
}
```

---

#### GET /api/v1/health/cache
Get cache system status (for T091 caching).

**Response** (200):
```json
{
  "hits": 1234,
  "misses": 156,
  "hit_rate_percent": 88.8,
  "invalidations": 45,
  "expirations": 23,
  "current_size": 87,
  "memory_usage_bytes": 45320
}
```

---

## Examples

### Complete Learning Flow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "robotics_learner",
    "email": "learner@example.com",
    "password": "SecurePass123!"
  }'

# Response: Get access_token and refresh_token

# 2. Get dashboard (with auth)
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
curl -X GET http://localhost:8000/api/v1/dashboard/metrics \
  -H "Authorization: Bearer $TOKEN"

# 3. Select learning path
curl -X POST http://localhost:8000/api/v1/learning-paths/select \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path_id": "path_1"
  }'

# 4. Complete chapter
curl -X POST http://localhost:8000/api/v1/progress/1/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mastery_score": 95,
    "time_spent_seconds": 1800
  }'

# 5. Get achievements
curl -X GET "http://localhost:8000/api/v1/progress/{user_id}/achievements" \
  -H "Authorization: Bearer $TOKEN"

# 6. Get statistics
curl -X GET "http://localhost:8000/api/v1/users/{user_id}/statistics" \
  -H "Authorization: Bearer $TOKEN"
```

---

## SDKs

### Python Client Example

```python
import requests
from datetime import datetime

class PersonalizationAPI:
    def __init__(self, base_url="http://localhost:8000", username=None, password=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

        if username and password:
            self.login(username, password)

    def register(self, username, email, password):
        """Register new user."""
        response = self.session.post(
            f"{self.base_url}/api/v1/users/register",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 201:
            data = response.json()
            self.token = data['access_token']
            self.session.headers['Authorization'] = f"Bearer {self.token}"
            return data
        raise ValueError(f"Registration failed: {response.text}")

    def login(self, username, password):
        """Login user."""
        response = self.session.post(
            f"{self.base_url}/api/v1/users/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            self.session.headers['Authorization'] = f"Bearer {self.token}"
            return data
        raise ValueError(f"Login failed: {response.text}")

    def get_dashboard(self):
        """Get dashboard metrics."""
        response = self.session.get(f"{self.base_url}/api/v1/dashboard/metrics")
        return response.json()

    def complete_chapter(self, chapter_id, mastery_score, time_spent_seconds=0):
        """Complete a chapter."""
        response = self.session.post(
            f"{self.base_url}/api/v1/progress/{chapter_id}/complete",
            json={"mastery_score": mastery_score, "time_spent_seconds": time_spent_seconds}
        )
        return response.json()

    def get_achievements(self, user_id):
        """Get user achievements."""
        response = self.session.get(f"{self.base_url}/api/v1/progress/{user_id}/achievements")
        return response.json()

# Usage
api = PersonalizationAPI()
api.register("learner", "learner@example.com", "SecurePass123!")
dashboard = api.get_dashboard()
print(f"Completion: {dashboard['progress']['completion_percentage']}%")
api.complete_chapter(1, mastery_score=95)
```

---

## Support

- **Documentation**: https://github.com/personalization/docs
- **Issues**: https://github.com/personalization/api/issues
- **Email**: support@personalization.example.com
- **Status Page**: https://status.personalization.example.com

---

## Changelog

### Version 1.0.0 (2026-02-07)
- Initial API release
- Complete endpoint documentation
- Rate limiting and error handling
- Authentication with JWT
- Caching middleware (T091)
- Connection pooling (T092)
- Database indexes (T090)
