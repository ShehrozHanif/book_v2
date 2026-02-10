# Authentication

Complete guide to authenticating with the Hackathon1 Book API using JWT tokens.

## Overview

The API uses JWT (JSON Web Token) authentication for secure, stateless authentication. Each user receives tokens upon registration or login that grant access to protected endpoints.

## Authentication Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Register or Login                                     │
│ └─────────────────────────────────────────────────────┘
│                         ↓
│ 2. Receive access_token (30 min) + refresh_token (7 days)
│                         ↓
│ 3. Use access_token in Authorization header
│                         ↓
│ 4. Make API requests with token
│                         ↓
│ 5. Token expires after 30 minutes
│                         ↓
│ 6. Use refresh_token to get new access_token
│                         ↓
│ 7. Repeat from step 3
```

## Step 1: Register

Create a new account:

**Request:**
```bash
POST /api/v1/users/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*)

**Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com"
  },
  "timestamp": "2026-02-07T10:30:00Z"
}
```

**Error Cases:**

Email already registered:
```json
{
  "status": "error",
  "error_code": "EMAIL_ALREADY_EXISTS",
  "detail": "Email is already registered",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

Invalid password:
```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "detail": "Password must contain uppercase, lowercase, number, and special character",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

## Step 2: Login

Access existing account:

**Request:**
```bash
POST /api/v1/users/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe"
  },
  "timestamp": "2026-02-07T10:30:00Z"
}
```

**Error Cases:**

Invalid credentials:
```json
{
  "status": "error",
  "error_code": "INVALID_CREDENTIALS",
  "detail": "Invalid username or password",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

## Step 3: Make Authenticated Requests

Use the access token in the `Authorization` header:

```bash
GET /api/v1/users/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2026-02-07T10:00:00Z",
    "last_login": "2026-02-07T10:30:00Z"
  },
  "timestamp": "2026-02-07T10:30:00Z"
}
```

## Step 4: Refresh Expired Token

When access token expires (401 Unauthorized):

**Request:**
```bash
POST /api/v1/users/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "timestamp": "2026-02-07T10:30:00Z"
}
```

**Error Cases:**

Refresh token expired:
```json
{
  "status": "error",
  "error_code": "INVALID_TOKEN",
  "detail": "Refresh token expired. Please login again.",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

## Token Information

### Access Token
- **Lifetime**: 30 minutes
- **Purpose**: API requests
- **Format**: JWT with header, payload, signature
- **Usage**: Include in `Authorization: Bearer` header

### Refresh Token
- **Lifetime**: 7 days
- **Purpose**: Get new access tokens
- **Storage**: Secure HTTP-only cookie or localStorage
- **Usage**: POST to `/users/refresh` when access token expires

### JWT Structure

A typical JWT looks like:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ1c2VybmFtZSI6ImpvaG5fZG9lIiwiZXhwIjoxNjQ0MjM1MjAwfQ.signature
```

Decoded payload:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "exp": 1644235200
}
```

## Security Best Practices

### DO ✅

- **Store refresh token securely** - Use HTTP-only cookies or secure storage
- **Include access token in requests** - Add to every authenticated request
- **Refresh tokens before expiry** - Check expiration time
- **Handle 401 responses** - Automatically refresh and retry
- **HTTPS only** - Always use HTTPS in production
- **Validate token expiry** - Check `exp` claim before use

### DON'T ❌

- **Don't log tokens** - Never include tokens in logs
- **Don't commit tokens** - Never add tokens to version control
- **Don't share tokens** - Each user has unique tokens
- **Don't store in localStorage** - Vulnerable to XSS
- **Don't use HTTP** - Always use HTTPS for authentication
- **Don't hardcode credentials** - Use environment variables

## Common Scenarios

### Automatic Token Refresh

```python
import requests
from datetime import datetime, timedelta

class APIClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

    def login(self):
        response = requests.post(
            f"{self.base_url}/users/login",
            json={"username": self.username, "password": self.password}
        )
        data = response.json()["data"]
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_expiry = datetime.now() + timedelta(seconds=data["expires_in"])

    def ensure_token_valid(self):
        if datetime.now() >= self.token_expiry:
            self.refresh_access_token()

    def refresh_access_token(self):
        response = requests.post(
            f"{self.base_url}/users/refresh",
            json={"refresh_token": self.refresh_token}
        )
        data = response.json()["data"]
        self.access_token = data["access_token"]
        self.token_expiry = datetime.now() + timedelta(seconds=data["expires_in"])

    def get(self, endpoint):
        self.ensure_token_valid()
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        return response.json()
```

### Handling 401 Responses

```python
def make_request_with_retry(client, method, endpoint, **kwargs):
    response = requests.request(
        method,
        f"{client.base_url}{endpoint}",
        headers={"Authorization": f"Bearer {client.access_token}"},
        **kwargs
    )

    if response.status_code == 401:
        # Token expired, refresh and retry
        client.refresh_access_token()
        response = requests.request(
            method,
            f"{client.base_url}{endpoint}",
            headers={"Authorization": f"Bearer {client.access_token}"},
            **kwargs
        )

    return response.json()
```

## Error Handling

### 401 Unauthorized

Triggered when:
- No Authorization header provided
- Token is invalid or malformed
- Token has expired

**Action**: Refresh token or re-authenticate

```json
{
  "status": "error",
  "error_code": "INVALID_TOKEN",
  "detail": "Token has expired",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

### 403 Forbidden

Triggered when:
- User doesn't have permission for endpoint
- Accessing other user's data

**Action**: Verify user permissions or use correct user_id

```json
{
  "status": "error",
  "error_code": "FORBIDDEN",
  "detail": "You don't have permission to access this resource",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

## Next Steps

- **[Endpoints](/docs/api/endpoints)** - Available API operations
- **[Examples](/docs/api/examples)** - Real-world code samples
- **[Python SDK](/docs/api/python-sdk)** - Client library

