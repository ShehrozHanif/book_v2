# Authentication API Documentation

Complete documentation for the personalization authentication and user management endpoints.

## Table of Contents

- [Overview](#overview)
- [Authentication Flow](#authentication-flow)
- [Endpoints](#endpoints)
  - [User Registration](#user-registration)
  - [User Login](#user-login)
  - [Token Refresh](#token-refresh)
  - [User Logout](#user-logout)
  - [Get Profile](#get-profile)
  - [Update Profile](#update-profile)
  - [Delete Account](#delete-account)
  - [Password Reset](#password-reset)
  - [Email Verification](#email-verification)
- [Error Codes](#error-codes)
- [Testing](#testing)

## Overview

The authentication system uses JWT (JSON Web Tokens) for stateless authentication. All protected endpoints require a valid Bearer token in the Authorization header.

**Base URL**: `/api/v1/users`

**Authentication**: Bearer token (JWT)

## Authentication Flow

```
┌─────────┐                                          ┌─────────┐
│ Client  │                                          │ Server  │
└────┬────┘                                          └────┬────┘
     │                                                    │
     │  1. POST /register (username, email, password)    │
     │───────────────────────────────────────────────────>│
     │                                                    │
     │  2. Return access_token + refresh_token           │
     │<───────────────────────────────────────────────────│
     │                                                    │
     │  3. Store tokens in localStorage/secure storage   │
     │                                                    │
     │  4. Include Bearer token in subsequent requests   │
     │  GET /me (Authorization: Bearer <access_token>)   │
     │───────────────────────────────────────────────────>│
     │                                                    │
     │  5. Return user data                              │
     │<───────────────────────────────────────────────────│
     │                                                    │
     │  6. When access_token expires:                    │
     │  POST /refresh (refresh_token)                    │
     │───────────────────────────────────────────────────>│
     │                                                    │
     │  7. Return new access_token + refresh_token       │
     │<───────────────────────────────────────────────────│
     │                                                    │
```

## Endpoints

### User Registration

Register a new user account.

**Endpoint**: `POST /api/v1/users/register`

**Authentication**: None

**Request Body**:
```json
{
  "username": "robotics_learner",
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Password Requirements**:
- Minimum 8 characters
- Maximum 100 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

**Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "robotics_learner"
}
```

**Error Responses**:
- `400 Bad Request`: Username/email already exists or password too weak
- `422 Unprocessable Entity`: Invalid request format
- `429 Too Many Requests`: Rate limit exceeded (3 attempts per hour)

**curl Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "robotics_learner",
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

---

### User Login

Authenticate and receive access tokens.

**Endpoint**: `POST /api/v1/users/login`

**Authentication**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "robotics_learner"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Invalid request format
- `429 Too Many Requests`: Rate limit exceeded (5 attempts per 5 minutes)

**curl Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

---

### Token Refresh

Refresh an expired access token using a refresh token.

**Endpoint**: `POST /api/v1/users/refresh`

**Authentication**: None (but requires valid refresh token)

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "robotics_learner"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token

**curl Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

### User Logout

Logout user (client-side token removal with server acknowledgment).

**Endpoint**: `POST /api/v1/users/logout`

**Authentication**: Bearer token required

**Request Body**: None

**Response** (204 No Content): Empty response

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token

**curl Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Note**: In a JWT-based system, logout is primarily handled client-side by removing tokens. This endpoint serves as a logout event hook for logging/analytics. For production, implement token blacklist/revocation.

---

### Get Profile

Get current authenticated user's profile.

**Endpoint**: `GET /api/v1/users/me`

**Authentication**: Bearer token required

**Request Body**: None

**Response** (200 OK):
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "robotics_learner",
  "email": "user@example.com",
  "skill_level": 72,
  "skill_confidence": 68,
  "profile_picture_url": "https://example.com/avatar.jpg",
  "bio": "Passionate about robotics and automation",
  "preferences": {
    "explanation_style": "example_first",
    "code_language": "python",
    "learning_pace": "medium",
    "content_focus": "balanced"
  },
  "created_at": "2026-02-01T10:30:00Z",
  "last_login_at": "2026-02-07T15:45:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token

**curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Update Profile

Update current user's profile information.

**Endpoint**: `PUT /api/v1/users/me`

**Authentication**: Bearer token required

**Request Body** (all fields optional):
```json
{
  "username": "new_username",
  "email": "newemail@example.com",
  "bio": "Updated bio text",
  "profile_picture_url": "https://example.com/newavatar.jpg",
  "preferences": {
    "explanation_style": "theory_first",
    "code_language": "cpp",
    "learning_pace": "fast",
    "content_focus": "simulation"
  }
}
```

**Preference Options**:
- `explanation_style`: "theory_first" | "example_first"
- `code_language`: "python" | "cpp" | "both"
- `learning_pace`: "slow" | "medium" | "fast"
- `content_focus`: "simulation" | "hardware" | "balanced"

**Response** (200 OK):
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "new_username",
  "email": "newemail@example.com",
  "skill_level": 72,
  "skill_confidence": 68,
  "profile_picture_url": "https://example.com/newavatar.jpg",
  "bio": "Updated bio text",
  "preferences": {
    "explanation_style": "theory_first",
    "code_language": "cpp",
    "learning_pace": "fast",
    "content_focus": "simulation"
  },
  "created_at": "2026-02-01T10:30:00Z",
  "last_login_at": "2026-02-07T15:45:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Username/email already exists
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: User not found

**curl Example**:
```bash
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Updated bio text",
    "preferences": {
      "explanation_style": "theory_first",
      "code_language": "cpp"
    }
  }'
```

---

### Delete Account

Delete current user's account (soft delete).

**Endpoint**: `DELETE /api/v1/users/me`

**Authentication**: Bearer token required

**Request Body**:
```json
{
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "message": "Account successfully deleted"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid password or token
- `404 Not Found`: User not found

**curl Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "password": "SecurePass123!"
  }'
```

**Note**: This performs a soft delete (sets `deleted_at` timestamp). For GDPR compliance, implement data anonymization or hard delete.

---

### Password Reset

Request and complete password reset.

#### Request Password Reset

**Endpoint**: `POST /api/v1/users/forgot-password`

**Authentication**: None

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

**curl Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

**Note**: Always returns success to prevent email enumeration attacks. In production, integrate with email service (SendGrid, AWS SES, etc.).

#### Complete Password Reset

**Endpoint**: `POST /api/v1/users/reset-password`

**Authentication**: None (requires reset token)

**Request Body**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "NewSecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "message": "Password successfully reset"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid/expired token or weak password
- `404 Not Found`: User not found

**curl Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "new_password": "NewSecurePass123!"
  }'
```

**Note**: Reset tokens expire in 1 hour.

---

### Email Verification

Optional email verification feature (placeholder implementation).

#### Request Verification Email

**Endpoint**: `POST /api/v1/users/verify-email`

**Authentication**: Bearer token required

**Request Body**: None

**Response** (200 OK):
```json
{
  "message": "Verification email sent"
}
```

**curl Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/verify-email" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Verify Email

**Endpoint**: `GET /api/v1/users/verify-email/{token}`

**Authentication**: None

**Response** (200 OK):
```json
{
  "message": "Email successfully verified"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid or expired token
- `404 Not Found`: User not found

**curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/users/verify-email/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Note**: This is a placeholder. In production, add `email_verified` field to User model and implement actual email service integration.

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request successful, no response body |
| 400 | Bad Request - Invalid input or validation error |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Valid authentication but insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Request format invalid |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Common Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Testing

### Using curl

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Save the access_token from response
export TOKEN="<access_token_from_response>"

# 2. Get user profile
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer $TOKEN"

# 3. Update profile
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Test user bio"
  }'

# 4. Logout
curl -X POST "http://localhost:8000/api/v1/users/logout" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Postman

1. **Import Collection**:
   - Create a new collection named "Robotics Auth API"
   - Add requests for each endpoint

2. **Setup Environment Variables**:
   - `base_url`: `http://localhost:8000`
   - `access_token`: (auto-populated from login response)

3. **Test Flow**:
   1. POST Register → Save `access_token` to environment
   2. POST Login → Verify tokens returned
   3. GET Profile → Use saved token
   4. PUT Update Profile → Test field updates
   5. POST Logout → Clear token

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/users"

# Register
response = requests.post(f"{BASE_URL}/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
})
tokens = response.json()
access_token = tokens["access_token"]

# Get profile
headers = {"Authorization": f"Bearer {access_token}"}
profile = requests.get(f"{BASE_URL}/me", headers=headers)
print(profile.json())

# Update profile
update = requests.put(f"{BASE_URL}/me", headers=headers, json={
    "bio": "Updated via Python"
})
print(update.json())
```

---

## Security Best Practices

1. **Store Tokens Securely**:
   - Never store tokens in localStorage on production
   - Use httpOnly cookies or secure storage mechanisms
   - Implement CSRF protection for cookie-based auth

2. **Token Expiration**:
   - Access tokens expire in 30 minutes
   - Refresh tokens expire in 7 days
   - Implement automatic token refresh on client

3. **Rate Limiting**:
   - Login: 5 attempts per 5 minutes
   - Registration: 3 attempts per hour
   - Implement exponential backoff on client

4. **Password Security**:
   - Passwords hashed with bcrypt
   - Minimum strength requirements enforced
   - Never log or expose passwords

5. **HTTPS Required**:
   - Always use HTTPS in production
   - Never send tokens over unencrypted connections

---

## Environment Variables

Required environment variables:

```env
JWT_SECRET_KEY=<your-secret-key-here>
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Support

For issues or questions, contact the development team or refer to the main project documentation.
