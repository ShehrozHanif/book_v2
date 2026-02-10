# Urdu Translation Feature - API Documentation (T069)

## Overview

This document provides comprehensive API documentation for the Urdu translation feature of the RAG Chatbot.

**Base URL**: `http://localhost:8000/api/v1`
**Authentication**: JWT Bearer Token
**Content-Type**: `application/json`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Language Preferences](#language-preferences)
3. [Chatbot Translation](#chatbot-translation)
4. [Glossary](#glossary)
5. [Admin Translation Management](#admin-translation-management)
6. [Notifications](#notifications)
7. [Analytics](#analytics)
8. [Error Responses](#error-responses)
9. [Rate Limiting](#rate-limiting)

---

## Authentication

### JWT Bearer Token

All endpoints (except public ones) require authentication via JWT Bearer token.

**Header**:
```
Authorization: Bearer <token>
```

**Token Structure**:
```json
{
  "sub": "user_id",
  "username": "username",
  "role": "student|instructor|admin"
}
```

---

## Language Preferences

### Get User's Language Preference

**Endpoint**: `GET /users/me/language-preference`

**Authentication**: Required
**Description**: Retrieve the current user's language preference

**Response** (200 OK):
```json
{
  "language": "english",
  "updated_at": "2026-02-10T12:00:00"
}
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `500 Internal Server Error`: Server error

---

### Set User's Language Preference

**Endpoint**: `PUT /users/me/language-preference`

**Authentication**: Required
**Description**: Update user's language preference (English/Urdu)

**Request Body**:
```json
{
  "language": "urdu"
}
```

**Valid Values**: `"english"`, `"urdu"`

**Response** (200 OK):
```json
{
  "language": "urdu",
  "updated_at": "2026-02-10T12:00:01"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid language value
- `401 Unauthorized`: Not authenticated
- `422 Unprocessable Entity`: Missing required field
- `500 Internal Server Error`: Server error

---

## Chatbot Translation

### Get Translated Response

**Endpoint**: `GET /chatbot/response/{template_key}`

**Query Parameters**:
- `language` (optional): `"english"` or `"urdu"` (default: user preference)

**Authentication**: Required for Urdu, optional for English

**Description**: Get chatbot response in selected language

**Response** (200 OK):
```json
{
  "template_key": "greeting",
  "english_content": "Hello, how can I help you?",
  "urdu_translation": "السلام علیکم، میں آپ کی کیا مدد کر سکتا ہوں؟",
  "language": "urdu"
}
```

**Error Responses**:
- `401 Unauthorized`: Guest user requesting Urdu (not authenticated)
- `404 Not Found`: Template not found
- `500 Internal Server Error`: Server error

---

### List Available Languages

**Endpoint**: `GET /chatbot/languages`

**Authentication**: Optional

**Response** (200 OK):
```json
{
  "supported_languages": ["english", "urdu"],
  "default": "english"
}
```

---

## Glossary

### Search Glossary Terms

**Endpoint**: `GET /glossary/search`

**Query Parameters**:
- `q` (required): Search query
- `language` (optional): `"english"` or `"urdu"` (default: both)

**Authentication**: Required for Urdu results

**Response** (200 OK):
```json
{
  "query": "ROS 2",
  "results": [
    {
      "id": 1,
      "english_term": "ROS 2 Node",
      "urdu_translation": "ROS 2 ندوڈ",
      "pronunciation_transliterated": "ROS 2 nod",
      "definitions": {
        "english": "A single executable process...",
        "urdu": "ایک واحد قابل عمل عمل..."
      },
      "category": "robotics"
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Missing search query
- `401 Unauthorized`: Urdu search without authentication
- `500 Internal Server Error`: Server error

**Rate Limit**: 100 requests per minute

---

### Get Glossary Term

**Endpoint**: `GET /glossary/{term_id}`

**Authentication**: Required for Urdu content

**Response** (200 OK):
```json
{
  "id": 1,
  "english_term": "Kinematics",
  "urdu_translation": "کائنیمیٹکس",
  "pronunciation_transliterated": "kaineematix",
  "definitions": {...},
  "examples": {...}
}
```

---

### Submit Glossary Feedback

**Endpoint**: `POST /glossary/feedback`

**Authentication**: Required

**Request Body**:
```json
{
  "term_id": 1,
  "feedback": "Translation could be improved",
  "rating": 3
}
```

**Response** (201 Created):
```json
{
  "id": 123,
  "term_id": 1,
  "user_id": 42,
  "feedback": "Translation could be improved",
  "rating": 3,
  "created_at": "2026-02-10T12:00:00"
}
```

---

## Admin Translation Management

### List Translations

**Endpoint**: `GET /admin/translations`

**Query Parameters**:
- `status` (optional): `"draft"`, `"reviewed"`, or `"published"`
- `limit` (optional): Results per page (default: 10, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Authentication**: Required (admin/instructor only)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "template_id": 1,
    "template_key": "greeting",
    "english_content": "Hello",
    "urdu_translation": "السلام",
    "status": "published",
    "is_stale": false,
    "updated_at": "2026-02-10T12:00:00"
  }
]
```

---

### Update Translation

**Endpoint**: `PUT /admin/translations/{template_id}`

**Authentication**: Required (admin/instructor only)

**Request Body**:
```json
{
  "urdu_translation": "نیا ترجمہ"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "template_id": 1,
  "urdu_translation": "نیا ترجمہ",
  "status": "draft",
  "updated_at": "2026-02-10T12:00:01"
}
```

---

### Mark Translation as Reviewed

**Endpoint**: `POST /admin/translations/{template_id}/review`

**Authentication**: Required (admin/instructor only)

**Request Body**:
```json
{
  "status": "reviewed"
}
```

**Valid Status Values**: `"draft"`, `"reviewed"`, `"published"`

**Response** (200 OK):
```json
{
  "id": 1,
  "template_id": 1,
  "status": "reviewed",
  "updated_at": "2026-02-10T12:00:02"
}
```

---

### Get Stale Translations

**Endpoint**: `GET /admin/translations/stale`

**Query Parameters**:
- `limit` (optional): Results per page (default: 10)
- `offset` (optional): Pagination offset

**Authentication**: Required (admin/instructor only)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "template_id": 5,
    "template_key": "error_message",
    "is_stale": true,
    "stale_since": "2026-02-08T10:00:00",
    "urdu_translation": "پرانا ترجمہ"
  }
]
```

---

### Get Translation Metrics

**Endpoint**: `GET /admin/translations/metrics`

**Authentication**: Required (admin/instructor only)

**Response** (200 OK):
```json
{
  "total_templates": 100,
  "translated": 85,
  "reviewed": 70,
  "published": 65,
  "translation_percent": 85.0,
  "review_percent": 70.0,
  "published_percent": 65.0,
  "stale_count": 5
}
```

---

## Notifications

### Get User Notifications

**Endpoint**: `GET /notifications`

**Query Parameters**:
- `unread_only` (optional): `true` to get only unread (default: false)
- `limit` (optional): Results per page (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Authentication**: Required

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "type": "translation_stale",
    "message": "Translation for 'error_message' is now stale",
    "details": {
      "template_id": 5,
      "action_url": "/admin/translations/5"
    },
    "created_at": "2026-02-10T12:00:00",
    "read": false
  }
]
```

---

### Mark Notification as Read

**Endpoint**: `POST /notifications/{notification_id}/read`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "id": 1,
  "read": true,
  "read_at": "2026-02-10T12:05:00"
}
```

---

## Analytics

### Get Language Adoption Metrics

**Endpoint**: `GET /analytics/language-adoption`

**Authentication**: Required (admin/instructor only)

**Response** (200 OK):
```json
{
  "total_users": 1000,
  "english_users": 850,
  "urdu_users": 150,
  "english_percent": 85.0,
  "urdu_percent": 15.0
}
```

---

### Get Language Demographics

**Endpoint**: `GET /analytics/language-demographics`

**Authentication**: Required (admin/instructor only)

**Response** (200 OK):
```json
{
  "student": {"english": 700, "urdu": 130, "total": 830},
  "instructor": {"english": 150, "urdu": 20, "total": 170}
}
```

---

## Error Responses

### 400 Bad Request
Invalid request parameters or malformed JSON.

```json
{
  "error": "Invalid input",
  "status_code": 400,
  "details": {
    "field": "language",
    "issue": "Must be 'english' or 'urdu'"
  }
}
```

### 401 Unauthorized
Authentication required or invalid token.

```json
{
  "error": "Authentication required",
  "status_code": 401,
  "message": "Urdu access requires authentication"
}
```

### 403 Forbidden
Insufficient permissions.

```json
{
  "error": "Permission denied",
  "status_code": 403,
  "message": "Only administrators can access this endpoint"
}
```

### 404 Not Found
Resource not found.

```json
{
  "error": "Resource not found",
  "status_code": 404,
  "details": {"resource": "template", "identifier": "999"}
}
```

### 422 Unprocessable Entity
Validation failed.

```json
{
  "error": "Validation failed",
  "status_code": 422,
  "errors": [
    {
      "field": "language",
      "message": "Field required"
    }
  ]
}
```

### 429 Too Many Requests
Rate limit exceeded.

```json
{
  "error": "Rate limit exceeded",
  "status_code": 429,
  "message": "100 requests per 60 seconds"
}
```

**Headers**:
- `Retry-After`: Seconds to wait before retrying
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

### 500 Internal Server Error
Server error with graceful fallback.

```json
{
  "error": "Internal server error",
  "status_code": 500,
  "message": "An unexpected error occurred. Please try again."
}
```

---

## Rate Limiting

Rate limits are enforced per user per endpoint:

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/glossary/*` | 100 | 60 seconds |
| `/admin/translations` | 50 | 60 seconds |
| `/analytics/*` | 200 | 3600 seconds |
| `/notifications` | 200 | 3600 seconds |
| `/language-preference` | 30 | 60 seconds |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1644505200
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

## Best Practices

1. **Error Handling**: Always check status codes and handle errors gracefully
2. **Rate Limiting**: Implement exponential backoff for 429 responses
3. **Caching**: Cache translations when possible to reduce API calls
4. **Authentication**: Refresh tokens before expiration
5. **Pagination**: Use limit/offset for large result sets
6. **Monitoring**: Log all API errors for debugging

---

**Last Updated**: February 10, 2026
**Version**: 1.0
