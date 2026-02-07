# API Endpoints

Complete reference of all available Hackathon1 Book API endpoints.

## Endpoint Groups

### 1. Authentication (3 endpoints)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/users/register` | Create new account | None |
| POST | `/users/login` | Authenticate user | None |
| POST | `/users/refresh` | Get new access token | None |

**Example:**
```bash
# Register
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","email":"john@example.com","password":"SecurePass123!"}'

# Login
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"SecurePass123!"}'

# Refresh token
curl -X POST http://localhost:8000/api/v1/users/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"eyJhbGc..."}'
```

---

### 2. User Profile (2 endpoints)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/users/profile` | Get user profile | JWT |
| PUT | `/users/profile` | Update profile | JWT |

**Example:**
```bash
# Get profile
curl -X GET http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer eyJhbGc..."

# Update profile
curl -X PUT http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe","bio":"Learning robotics"}'
```

---

### 3. Progress Tracking (4 endpoints)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/progress/{chapter_id}/complete` | Mark chapter complete | JWT |
| POST | `/progress/{chapter_id}/practice` | Submit practice answers | JWT |
| POST | `/progress/{chapter_id}/retry` | Reset and retry chapter | JWT |
| GET | `/dashboard/metrics` | Get learning metrics | JWT |

**Example:**
```bash
# Complete chapter
curl -X POST http://localhost:8000/api/v1/progress/1/complete \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"mastery_score":85,"time_spent_seconds":1800}'

# Submit practice answers
curl -X POST http://localhost:8000/api/v1/progress/1/practice \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"answers":[{"question_id":"q1","answer":"A"},{"question_id":"q2","answer":"B"}]}'

# Retry chapter
curl -X POST http://localhost:8000/api/v1/progress/1/retry \
  -H "Authorization: Bearer eyJhbGc..."

# Get dashboard metrics
curl -X GET http://localhost:8000/api/v1/dashboard/metrics \
  -H "Authorization: Bearer eyJhbGc..."
```

---

### 4. Achievements (1 endpoint)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/progress/{user_id}/achievements` | Get user achievements | JWT |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/progress/550e8400/achievements" \
  -H "Authorization: Bearer eyJhbGc..."
```

---

### 5. Statistics (1 endpoint)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/users/{user_id}/statistics` | Get learning statistics | JWT |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/550e8400/statistics" \
  -H "Authorization: Bearer eyJhbGc..."
```

---

### 6. Learning Paths (2 endpoints)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/learning-paths` | List available paths | JWT |
| POST | `/learning-paths/select` | Select learning path | JWT |

**Example:**
```bash
# List paths
curl -X GET http://localhost:8000/api/v1/learning-paths \
  -H "Authorization: Bearer eyJhbGc..."

# Select path
curl -X POST http://localhost:8000/api/v1/learning-paths/select \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"path_id":"fast_track"}'
```

---

### 7. Preferences (2 endpoints)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/users/{user_id}/preferences` | Get user preferences | JWT |
| PUT | `/users/{user_id}/preferences` | Update preferences | JWT |

**Example:**
```bash
# Get preferences
curl -X GET "http://localhost:8000/api/v1/users/550e8400/preferences" \
  -H "Authorization: Bearer eyJhbGc..."

# Update preferences
curl -X PUT "http://localhost:8000/api/v1/users/550e8400/preferences" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"notification_email":true,"dark_mode":true}'
```

---

### 8. Advanced Challenges (1 endpoint)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/progress/{chapter_id}/advanced-challenges` | Get advanced content | JWT |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/progress/1/advanced-challenges" \
  -H "Authorization: Bearer eyJhbGc..."
```

---

### 9. Health Monitoring (3 endpoints)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/health` | Basic health check | None |
| GET | `/ready` | Readiness check | None |
| GET | `/health/cache` | Cache status | None |

**Example:**
```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# Cache status
curl http://localhost:8000/health/cache
```

---

## Request/Response Examples

### Success Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": "123",
    "name": "value"
  },
  "timestamp": "2026-02-07T10:30:00Z"
}
```

### Error Response (400+ errors)
```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "detail": "Detailed error message",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

---

## Rate Limiting

| Endpoint Category | Limit | Window |
|------------------|-------|--------|
| Authentication | 5 | 5 minutes |
| General API | 100 | 1 minute |
| Dashboard | 10 | 1 minute |

---

## Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | UUID | User's unique identifier |
| `chapter_id` | Integer | Chapter number (1-22) |
| `question_id` | String | Practice question ID |
| `path_id` | String | Learning path identifier |

---

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | Integer | 1 | Pagination page number |
| `limit` | Integer | 20 | Items per page |
| `sort` | String | date | Sort order |

---

## Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Success |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - No/invalid token |
| 403 | Forbidden - No permission |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limited |
| 500 | Server Error - Unexpected error |

---

## Next Steps

- **[Authentication Guide](/docs/api/authentication)** - How to authenticate
- **[Code Examples](/docs/api/examples)** - Real-world usage
- **[Python SDK](/docs/api/python-sdk)** - Easy-to-use client library
