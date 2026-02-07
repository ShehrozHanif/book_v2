# API Reference

Complete REST API documentation for the Hackathon1 Book Personalization System.

## Quick Facts

| Property | Value |
|----------|-------|
| **API Version** | 1.0.0 |
| **Format** | REST with JSON |
| **Base URL** | `http://localhost:8000/api/v1` (dev) |
| **Authentication** | JWT Bearer Token |
| **Response Format** | JSON with status envelope |
| **Rate Limit** | 100 req/min per user |
| **Uptime SLA** | 99.5% |

## Response Format

All API responses follow a consistent format:

### Success Response (2xx)
```json
{
  "status": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com"
  },
  "timestamp": "2026-02-07T10:30:00Z"
}
```

### Error Response (4xx/5xx)
```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "detail": "Email is already registered",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

## HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| **200** | OK | Request succeeded |
| **201** | Created | Resource created successfully |
| **400** | Bad Request | Invalid input or validation error |
| **401** | Unauthorized | Missing or invalid authentication token |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Resource already exists (e.g., duplicate email) |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Unexpected server error |

## Error Codes

| Error Code | HTTP | Meaning | Action |
|-----------|------|---------|--------|
| INVALID_REQUEST | 400 | Request validation failed | Check request format and parameters |
| INVALID_TOKEN | 401 | Token expired or malformed | Refresh token or re-authenticate |
| USER_NOT_FOUND | 404 | User doesn't exist | Check username or user_id |
| EMAIL_ALREADY_EXISTS | 409 | Email already registered | Use different email or login |
| INVALID_CREDENTIALS | 401 | Wrong username/password | Verify credentials |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests | Wait before retrying |
| INTERNAL_ERROR | 500 | Server error | Retry later or contact support |

## Authentication

The API uses JWT (JSON Web Token) authentication. All protected endpoints require an `Authorization` header with a Bearer token.

### Header Format
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Lifecycle

1. **Register or Login** → Receive access_token + refresh_token
2. **Use access_token** → Valid for 30 minutes
3. **Token expires** → Use refresh_token to get new access_token
4. **Get new access_token** → Valid for another 30 minutes
5. **Refresh_token expires** → Valid for 7 days (re-login required)

### Token Types

| Token | Lifetime | Purpose |
|-------|----------|---------|
| **access_token** | 30 minutes | API requests |
| **refresh_token** | 7 days | Get new access tokens |

## Rate Limiting

The API implements rate limiting to ensure fair usage:

| Endpoint Category | Limit | Window |
|------------------|-------|--------|
| Authentication | 5 | per 5 minutes (per IP) |
| Registration | 3 | per 1 hour (per IP) |
| General API | 100 | per 1 minute (per user) |
| Dashboard | 10 | per 1 minute (per user) |

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1644235260
```

### Handling Rate Limits

When rate limited (429 response):
```json
{
  "status": "error",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "detail": "Rate limit exceeded. Retry after 60 seconds",
  "retry_after": 60
}
```

**Recommended retry strategy:**
- Wait for `retry_after` seconds
- Implement exponential backoff
- Never retry more than 3 times

## Content Type

All requests and responses use JSON:
```
Content-Type: application/json
Accept: application/json
```

## Pagination

List endpoints support pagination:

```bash
GET /api/v1/progress/achievements?page=1&limit=20
```

Response includes pagination info:
```json
{
  "status": "success",
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 32,
    "pages": 2
  }
}
```

## Timestamps

All timestamps use ISO 8601 format (UTC):
```
2026-02-07T10:30:00Z
```

## API Sections

- **[Authentication](/docs/api/authentication)** - Register, login, refresh tokens
- **[Endpoints](/docs/api/endpoints)** - All available endpoints
- **[Examples](/docs/api/examples)** - Real-world usage examples
- **[Python SDK](/docs/api/python-sdk)** - Python client library

## Next Steps

1. **[Authenticate](/docs/api/authentication)** - Register your account
2. **[Explore Endpoints](/docs/api/endpoints)** - See available operations
3. **[Try Examples](/docs/api/examples)** - Copy-paste working code
4. **[Use SDK](/docs/api/python-sdk)** - Python client for easier integration

## Support & Resources

- **Status Page**: https://status.personalization.example.com
- **Issues**: https://github.com/personalization/api/issues
- **Email Support**: support@personalization.example.com
- **Documentation**: https://docs.personalization.example.com

---

**Ready to build?** Start with [Authentication](/docs/api/authentication).
