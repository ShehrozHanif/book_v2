# Browser Testing Guide - Complete Instructions

**Date**: 2026-02-07
**Purpose**: Complete step-by-step guide to test Hackathon1 Book in your web browser

---

## 🚀 Quick Start (Choose Your OS)

### Windows Users
```bash
# Double-click this file:
START_LOCAL.bat

# This will automatically:
# 1. Start Docker services
# 2. Start Docusaurus
# 3. Open browsers to http://localhost:3000 and http://localhost:8000/docs
```

### Mac/Linux Users
```bash
# In terminal:
chmod +x START_LOCAL.sh
./START_LOCAL.sh

# This will automatically:
# 1. Start Docker services
# 2. Start Docusaurus
# 3. Open browsers to http://localhost:3000 and http://localhost:8000/docs
```

---

## 📋 Manual Setup (If Scripts Don't Work)

### Terminal 1: Start Backend Services

```bash
cd /path/to/book
docker-compose up -d
sleep 15
docker-compose ps
```

**Expected output:**
```
NAME                    COMMAND                   STATUS
personalization-postgres   "docker-entrypoint..."  Up (healthy)
personalization-redis      "redis-server..."       Up (healthy)
personalization-api        "uvicorn main:app..."   Up (healthy)
```

### Terminal 2: Start Docusaurus

```bash
cd frontend/textbook-site
npm install
npm run start
```

**Expected output:**
```
[INFO] Docusaurus website is running at: http://localhost:3000/
```

### Browser Windows

Open 3 browser windows:

1. **http://localhost:3000** - Docusaurus Book
2. **http://localhost:8000/docs** - API Documentation
3. **http://localhost:8000/redoc** - Alternative API Docs

---

## 🧪 What to Test in Each Browser Window

---

## 1️⃣ Docusaurus Book (http://localhost:3000)

### Section: Textbook Content

**Navigate the sidebar:**
- [ ] Click "📚 Textbook Content" to expand/collapse
- [ ] See Modules 1-5 listed
- [ ] Click on Module 1 → Chapter 1
- [ ] Should see chapter content with markdown formatting

**Features to test:**
- [ ] Table of contents generates correctly
- [ ] Links between pages work
- [ ] Search functionality works (search icon at top)
- [ ] Mobile view (F12 DevTools → Toggle device toolbar)

### Section: Personalization System

**Navigate to:**
- [ ] System Overview (read about features)
- [ ] Features & Architecture (see detailed documentation)
- [ ] Learning Paths (view 4 predefined paths)

**Things to verify:**
- [ ] Images/diagrams load
- [ ] Tables display correctly
- [ ] Code examples are syntax highlighted
- [ ] Links to other sections work

### Section: API Reference

**Navigate to:**
- [ ] API Overview (response format, status codes)
- [ ] Authentication Guide (JWT flows, token lifecycle)
- [ ] Endpoints Reference (all 15+ endpoints)

**Verify:**
- [ ] Endpoint tables display properly
- [ ] Code examples are formatted
- [ ] Links to authentication section work
- [ ] All endpoint groups are listed

### Section: Deployment & Operations

**Check:**
- [ ] Deployment Overview page loads
- [ ] Quick Start Guide displays correctly
- [ ] All steps are numbered and clear
- [ ] Code blocks are readable

### Section: Development Guide

**Verify:**
- [ ] System Architecture page loads
- [ ] Diagrams are visible
- [ ] Tables with tech stack show all info
- [ ] All links are working

### Search Functionality

**Test the search:**
1. Click search icon at top
2. Type: "achievements"
3. Should show matching pages
4. Click result to navigate
5. Search term should be highlighted

### Mobile Responsiveness

**Test on mobile (F12 DevTools):**
1. Press F12 to open DevTools
2. Click "Toggle device toolbar" (or Ctrl+Shift+M)
3. Select iPhone 12 or iPad
4. Verify:
   - [ ] Sidebar becomes hamburger menu
   - [ ] Text is readable
   - [ ] Navigation works
   - [ ] No horizontal scrolling

---

## 2️⃣ Swagger API Docs (http://localhost:8000/docs)

### Explore API Endpoints

**See all endpoints:**
- [ ] Page loads with complete API schema
- [ ] Endpoints grouped by category:
  - Authentication (3 endpoints)
  - User Profile (2 endpoints)
  - Progress (4 endpoints)
  - Achievements (1 endpoint)
  - Statistics (1 endpoint)
  - Learning Paths (2 endpoints)
  - Preferences (2 endpoints)
  - Advanced Challenges (1 endpoint)
  - Health (3 endpoints)

### Test User Registration

**Steps:**
1. Find "POST /users/register"
2. Click to expand
3. Click "Try it out" button
4. Enter test data:
   ```json
   {
     "username": "testuser123",
     "email": "test@example.com",
     "password": "TestPass123!"
   }
   ```
5. Click "Execute"
6. Check response:
   - [ ] Status 201 Created
   - [ ] Response has access_token
   - [ ] Response has refresh_token
   - [ ] Response has user_id

**Expected response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user_id": "550e8400-...",
    "username": "testuser123"
  },
  "timestamp": "2026-02-07T..."
}
```

### Save Your Access Token

After successful registration, you'll need the access token for other tests:
1. Copy the `access_token` value
2. Keep it for next tests

### Test User Login

**Steps:**
1. Find "POST /users/login"
2. Click "Try it out"
3. Enter credentials:
   ```json
   {
     "username": "testuser123",
     "password": "TestPass123!"
   }
   ```
4. Click "Execute"
5. Check response: should get new tokens

### Test Authenticated Endpoint (Get Profile)

**Steps:**
1. Find "GET /users/profile"
2. Click "Try it out"
3. You need to authorize first:
   - Scroll to top
   - Click "Authorize" button
   - Paste your access_token (without "Bearer " prefix)
   - Click "Authorize"
4. Now try the endpoint again
5. Click "Execute"
6. Check response:
   - [ ] Status 200 OK
   - [ ] Response has user profile data

### Test Other Endpoints

**Try these endpoints with your token:**
1. "GET /dashboard/metrics" - Dashboard data
2. "POST /progress/{chapter_id}/complete" - Mark chapter complete
3. "GET /progress/achievements" - Get achievements
4. "GET /users/{user_id}/statistics" - Learning statistics

---

## 3️⃣ ReDoc API Docs (http://localhost:8000/redoc)

**Alternative view:**
- [ ] ReDoc page loads
- [ ] Shows same endpoints as Swagger
- [ ] Better organization and documentation
- [ ] Click endpoints to see details

---

## 🔌 Additional Testing

### Test Health Endpoints

**In new browser tabs:**

1. **http://localhost:8000/health**
   - Should show: `{"status":"ok",...}`

2. **http://localhost:8000/ready**
   - Should show: `{"status":"ready","components":{"database":"ok","cache":"ok"}}`

3. **http://localhost:8000/health/cache**
   - Should show cache status information

### Test with cURL (in Terminal 3)

```bash
# Health check
curl http://localhost:8000/health

# Test registration (same as Swagger)
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "curluser",
    "email": "curl@example.com",
    "password": "CurlPass123!"
  }'

# Get response
# Copy the access_token from response

# Login
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "curluser",
    "password": "CurlPass123!"
  }'

# Get profile (use your token)
curl -X GET http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## ✅ Testing Checklist

### Docusaurus (http://localhost:3000)
- [ ] Page loads without errors
- [ ] Sidebar navigation works
- [ ] Can click on different sections
- [ ] Textbook modules expand/collapse
- [ ] Search works (try searching "API")
- [ ] Mobile view works (use DevTools)
- [ ] All pages load (no 404 errors)
- [ ] Code blocks display properly
- [ ] Tables render correctly
- [ ] Images/diagrams display
- [ ] Links between pages work

### API Documentation (http://localhost:8000/docs)
- [ ] Swagger UI loads
- [ ] All endpoint groups visible
- [ ] Can expand endpoints
- [ ] Can see request/response schemas
- [ ] Register endpoint works
- [ ] Can save authentication token
- [ ] Can authenticate with token
- [ ] Get profile endpoint works with token
- [ ] Errors display properly (try invalid password)

### API Functionality
- [ ] Health check responds
- [ ] Register creates user
- [ ] Login returns tokens
- [ ] Token can authenticate requests
- [ ] API accepts JSON correctly
- [ ] Error messages are helpful

### Backend Services
- [ ] Docker containers running
- [ ] PostgreSQL responding
- [ ] Redis responding
- [ ] FastAPI responding
- [ ] No error messages in logs

### Database
- [ ] User data saved to database
- [ ] Achievements can be stored
- [ ] Progress tracking works
- [ ] Statistics can be calculated

---

## 🐛 Troubleshooting

### Issue: "Connection refused" on localhost:3000

**Solution:**
```bash
# Check if Docusaurus is running
npm list docusaurus

# Try restarting
cd frontend/textbook-site
npm run start
```

### Issue: "Connection refused" on localhost:8000

**Solution:**
```bash
# Check if Docker containers are running
docker-compose ps

# If not running, start them
docker-compose up -d

# Check logs
docker-compose logs api
```

### Issue: npm install fails

**Solution:**
```bash
# Clear cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules

# Reinstall
npm install
```

### Issue: Docker services not becoming healthy

**Solution:**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
sleep 20
docker-compose ps
```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port 3000
# On Windows: netstat -ano | findstr :3000
# On Mac/Linux: lsof -i :3000

# Kill the process or use different port
npm run start -- --port 3001
```

---

## 📊 Expected Results

### Docusaurus Should Show:
- ✅ 5 main sections in sidebar
- ✅ 39 total documentation pages
- ✅ Professional formatting
- ✅ No broken links
- ✅ All content readable
- ✅ Search functionality works

### API Should Support:
- ✅ User registration
- ✅ User login
- ✅ Token authentication
- ✅ Profile retrieval
- ✅ Progress tracking
- ✅ Achievement tracking
- ✅ Statistics calculation
- ✅ Health monitoring

### Database Should Have:
- ✅ Users table with registered users
- ✅ Progress table (if you complete chapters)
- ✅ Achievements table
- ✅ Preferences table
- ✅ All data persisted

---

## 🎉 Success Indicators

**System is working if:**
1. ✅ http://localhost:3000 loads documentation
2. ✅ http://localhost:8000/docs shows API endpoints
3. ✅ Can register a user via API
4. ✅ Can login with credentials
5. ✅ Can call authenticated endpoints
6. ✅ Docker containers are healthy
7. ✅ No error messages in logs
8. ✅ Database stores user data
9. ✅ All API endpoints return proper responses
10. ✅ Frontend and backend communicate correctly

---

## 🎯 Testing Scenarios

### Scenario 1: Complete User Journey

1. **Register user** via Swagger:
   - Username: student1
   - Email: student1@example.com
   - Password: Student123!

2. **Login** with credentials

3. **Save token** from response

4. **Get profile** using token

5. **Complete a chapter** using API

6. **View achievements** (should have some)

7. **View dashboard metrics** (should show progress)

8. **Check statistics** (should show learning data)

### Scenario 2: Documentation Review

1. Read "Personalization System Overview"
2. Understand "5 Core Features"
3. Review "Learning Paths"
4. Read "API Reference"
5. Follow "Quick Start Guide"
6. Review "System Architecture"

### Scenario 3: API Exploration

1. View all endpoints in Swagger
2. Try at least 5 different endpoints
3. Test authentication flow
4. Test error handling (invalid password)
5. Check rate limiting (if implemented)

---

## 📞 Need Help?

**If something doesn't work:**

1. Check LOCAL_TESTING_GUIDE.md
2. Read BROWSER_TESTING_GUIDE.md (this file)
3. Check logs:
   ```bash
   docker-compose logs
   ```
4. Restart services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

## 🎬 Next Steps After Testing

After successful testing in browser:

1. ✅ Verify all 10 success indicators above
2. ✅ Test all 3 scenarios
3. ✅ Take screenshots if needed
4. ✅ Document any issues
5. ✅ Prepare for production deployment

---

**Happy Testing!** 🚀

Let me know what you find in your browser testing!
