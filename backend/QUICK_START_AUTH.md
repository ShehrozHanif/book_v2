# Quick Start: Testing Authentication API

Fast guide to test the authentication endpoints.

## Prerequisites

1. Backend server running on `http://localhost:8000`
2. Database configured and migrated
3. Environment variables set (.env file)

## 1. Quick Test with curl

### Register a New User
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

**Expected Response** (201 Created):
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "testuser"
}
```

Save the `access_token` for next steps.

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### Get Profile
```bash
# Replace <TOKEN> with your access_token
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <TOKEN>"
```

### Update Profile
```bash
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Robotics enthusiast",
    "preferences": {
      "explanation_style": "theory_first",
      "code_language": "cpp"
    }
  }'
```

### Logout
```bash
curl -X POST "http://localhost:8000/api/v1/users/logout" \
  -H "Authorization: Bearer <TOKEN>"
```

## 2. Python Script Test

Create a file `test_auth.py`:

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/users"

# Register
print("1. Registering user...")
response = requests.post(f"{BASE_URL}/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
})
print(f"Status: {response.status_code}")
tokens = response.json()
access_token = tokens["access_token"]
print(f"Token: {access_token[:50]}...\n")

# Get profile
print("2. Getting profile...")
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/me", headers=headers)
print(f"Status: {response.status_code}")
profile = response.json()
print(f"Username: {profile['username']}")
print(f"Skill Level: {profile['skill_level']}\n")

# Update profile
print("3. Updating profile...")
response = requests.put(f"{BASE_URL}/me", headers=headers, json={
    "bio": "Testing the API",
    "preferences": {
        "explanation_style": "example_first",
        "code_language": "python"
    }
})
print(f"Status: {response.status_code}")
updated = response.json()
print(f"Bio: {updated['bio']}")
print(f"Preferences: {updated['preferences']}\n")

# Logout
print("4. Logging out...")
response = requests.post(f"{BASE_URL}/logout", headers=headers)
print(f"Status: {response.status_code}")
print("Done!")
```

Run it:
```bash
python test_auth.py
```

## 3. Frontend Test

### Start Frontend (if available)
```bash
cd frontend
npm start
```

### Test Flow
1. Navigate to `http://localhost:3000/login`
2. Click "Register here"
3. Fill form:
   - Username: testuser
   - Email: test@example.com
   - Password: TestPass123!
4. Click "Create account"
5. Should redirect to dashboard
6. Check localStorage for tokens

### Browser Console Check
```javascript
// Check if tokens are stored
console.log('Access Token:', localStorage.getItem('access_token'));
console.log('User ID:', localStorage.getItem('user_id'));
console.log('Username:', localStorage.getItem('username'));
```

## 4. Run Tests

### Run All Auth Tests
```bash
cd backend
python -m pytest src/personalization/tests/test_auth_utils.py -v
```

### Run Specific Test File
```bash
# JWT tests
python -m pytest src/personalization/tests/test_jwt.py -v

# Registration tests
python -m pytest src/personalization/tests/test_register.py -v

# Login tests
python -m pytest src/personalization/tests/test_login.py -v

# Profile tests
python -m pytest src/personalization/tests/test_profile.py -v
```

### Run with Coverage
```bash
python -m pytest src/personalization/tests/ --cov=src/personalization --cov-report=html
```

View coverage report:
```bash
# Open htmlcov/index.html in browser
```

## 5. Postman Collection

### Import Collection
1. Open Postman
2. Create new collection "Robotics Auth"
3. Add environment with:
   - `base_url`: `http://localhost:8000`
   - `access_token`: (auto-populated)

### Add Requests

#### 1. Register
- Method: POST
- URL: `{{base_url}}/api/v1/users/register`
- Body (JSON):
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "TestPass123!"
}
```
- Tests (JavaScript):
```javascript
pm.test("Registration successful", function() {
    pm.response.to.have.status(201);
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access_token);
});
```

#### 2. Get Profile
- Method: GET
- URL: `{{base_url}}/api/v1/users/me`
- Headers:
  - `Authorization`: `Bearer {{access_token}}`

#### 3. Update Profile
- Method: PUT
- URL: `{{base_url}}/api/v1/users/me`
- Headers:
  - `Authorization`: `Bearer {{access_token}}`
- Body (JSON):
```json
{
  "bio": "Updated from Postman",
  "preferences": {
    "explanation_style": "theory_first"
  }
}
```

#### 4. Logout
- Method: POST
- URL: `{{base_url}}/api/v1/users/logout`
- Headers:
  - `Authorization`: `Bearer {{access_token}}`

## 6. Common Issues & Solutions

### Issue: 401 Unauthorized
**Solution**: Check if token is valid and included in header
```bash
# Verify token format
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" -v
```

### Issue: 400 Username Already Exists
**Solution**: Use a different username or login instead
```bash
# Login with existing credentials
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'
```

### Issue: 422 Validation Error
**Solution**: Check request body format
```bash
# Correct format example
{
  "username": "testuser",     # 3-50 characters
  "email": "test@example.com",  # Valid email
  "password": "TestPass123!"  # 8+ chars, uppercase, lowercase, digit
}
```

### Issue: Connection Refused
**Solution**: Ensure backend is running
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend if not running
cd backend
uvicorn src.main:app --reload
```

### Issue: Database Error
**Solution**: Check database connection
```bash
# Verify .env file has correct DATABASE_URL
# Run migrations
alembic upgrade head
```

## 7. Environment Setup

### Minimal .env File
```env
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (use your actual database URL)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/robotics_db

# CORS (for frontend)
ALLOWED_ORIGINS=http://localhost:3000
```

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 8. Testing Checklist

- [ ] User can register with valid credentials
- [ ] Registration rejects duplicate username
- [ ] Registration rejects duplicate email
- [ ] Registration validates password strength
- [ ] User can login with correct credentials
- [ ] Login rejects incorrect password
- [ ] Access token works for protected endpoints
- [ ] Token refresh works when access token expires
- [ ] User can get their profile
- [ ] User can update profile fields
- [ ] User can update preferences
- [ ] User can logout
- [ ] Deleted users cannot access endpoints
- [ ] Password reset flow works
- [ ] Rate limiting prevents brute force

## 9. Quick Troubleshooting

```bash
# Check backend logs
tail -f backend/logs/app.log

# Check if endpoints are registered
curl http://localhost:8000/openapi.json | jq '.paths'

# Test database connection
psql $DATABASE_URL -c "SELECT version();"

# Verify JWT secret is loaded
python -c "from src.config import get_settings; print(get_settings().JWT_SECRET_KEY[:10])"
```

## 10. Next Steps

After verifying authentication works:

1. **Integrate with Frontend**:
   - Test login page in browser
   - Verify token storage
   - Test protected routes

2. **Load Test**:
   - Use `locust` or `ab` to test rate limiting
   - Verify performance under load

3. **Security Audit**:
   - Test for SQL injection
   - Test for XSS
   - Verify CORS settings

4. **Production Prep**:
   - Setup email service
   - Configure Redis for token blacklist
   - Enable HTTPS
   - Setup monitoring

## Resources

- **Full API Docs**: See `backend/README_AUTH.md`
- **OpenAPI Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Test Files**: `backend/src/personalization/tests/`

## Support

For issues:
1. Check backend logs
2. Verify environment variables
3. Run test suite
4. Review API documentation
