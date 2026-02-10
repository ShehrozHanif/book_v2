# Local Testing Guide - Complete Setup

**Date**: 2026-02-07
**Status**: Step-by-step instructions for testing Hackathon1 Book locally

---

## 🚀 Quick Start (5 Steps)

### Step 1: Start Backend Services with Docker Compose
```bash
cd /path/to/book
docker-compose up -d
sleep 15  # Wait for services to start
```

### Step 2: Verify Services
```bash
docker-compose ps
# All 3 services should show "Up (healthy)"
```

### Step 3: Start Docusaurus Documentation Site
```bash
cd frontend/textbook-site
npm install
npm run start
# Opens http://localhost:3000
```

### Step 4: Start Backend Development Server (Optional)
```bash
# In another terminal
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### Step 5: Open in Browser

**Visit these URLs:**
1. 📚 **Docusaurus Book**: http://localhost:3000
2. 🔌 **API Docs**: http://localhost:8000/docs
3. 📊 **API ReDoc**: http://localhost:8000/redoc
4. ✅ **Health Check**: http://localhost:8000/health

---

## 📋 Detailed Setup Instructions

### Prerequisites

Verify you have installed:
```bash
docker --version      # Should be 20.10.0+
docker-compose --version  # Should be 1.29.0+
npm --version         # Should be 14+
python --version      # Should be 3.10+
```

If not installed, see [Prerequisites](#prerequisites-setup) section below.

---

## 🔧 Full Setup Process

### 1. Backend Setup with Docker

**Start all services:**
```bash
cd /path/to/book

# Start services
docker-compose up -d

# Wait for health checks to pass
sleep 15

# Verify all services are healthy
docker-compose ps
```

**Expected output:**
```
NAME                   STATUS
personalization-postgres   Up (healthy)
personalization-redis      Up (healthy)
personalization-api        Up (healthy)
```

**If services don't start:**
```bash
# Check logs
docker-compose logs

# Restart
docker-compose down
docker-compose up -d
```

---

### 2. Database Verification

**Check database connection:**
```bash
docker-compose exec postgres psql -U personalization -d personalization_db -c "SELECT 1;"
# Should return: 1
```

**Check Redis:**
```bash
docker-compose exec redis redis-cli ping
# Should return: PONG
```

**Check API:**
```bash
curl http://localhost:8000/health
# Should return JSON with status "ok"
```

---

### 3. Frontend - Docusaurus Setup

**Navigate to textbook-site:**
```bash
cd frontend/textbook-site
```

**Install dependencies:**
```bash
npm install
```

**Start development server:**
```bash
npm run start
```

**Expected output:**
```
[INFO] Docusaurus website is running at: http://localhost:3000/
```

**Browser opens automatically** to http://localhost:3000

---

### 4. Backend Development Server (Optional)

If you want to run backend separately from Docker:

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.docker .env

# Run backend
uvicorn src.main:app --reload --port 8000
```

**Expected output:**
```
Uvicorn running on http://127.0.0.1:8000
```

---

## 🌐 Browser Access Guide

### Main URLs to Test

| URL | Purpose | Status |
|-----|---------|--------|
| http://localhost:3000 | 📚 Docusaurus Book | Main UI |
| http://localhost:8000/docs | 🔌 Swagger API Docs | Interactive API |
| http://localhost:8000/redoc | 📊 ReDoc API | Alternative docs |
| http://localhost:8000/health | ✅ Health Check | Service status |
| http://localhost:8000/ready | ⚡ Readiness Check | Ready to serve |

---

## 🧪 Testing Checklist

### 1. Docusaurus Book (http://localhost:3000)

**Navigation:**
- [ ] Open http://localhost:3000
- [ ] Sidebar loads with all sections
- [ ] Can navigate between chapters
- [ ] Search bar works
- [ ] Mobile responsive (test on DevTools)

**Sections to Check:**
- [ ] 📚 Textbook Content (collapsed by default)
- [ ] 🎓 Personalization System (3 pages)
- [ ] 🔌 API Reference (3 pages)
- [ ] 🚀 Deployment & Operations (2 pages)
- [ ] 💻 Development Guide (1 page)

### 2. API Documentation (http://localhost:8000/docs)

**Swagger UI:**
- [ ] Page loads with API schema
- [ ] All endpoint groups visible
- [ ] Can expand endpoints to see details
- [ ] Try-it-out functionality works

**Test an endpoint:**
```
1. Find "POST /users/register"
2. Click "Try it out"
3. Enter test data:
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "TestPass123!"
   }
4. Click "Execute"
5. Should see 201 Created response
```

### 3. Health Checks

**Test health endpoints:**
```bash
# In terminal
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/api/v1/health/cache
```

**Expected responses:**
```json
// /health
{"status":"ok","timestamp":"2026-02-07T..."}

// /ready
{"status":"ready","components":{"database":"ok","cache":"ok"}}
```

### 4. Test API Endpoints

**Register a user:**
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Expected response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "user_id": "550e8400-...",
    "username": "john_doe"
  }
}
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

**Get profile (use access_token from login):**
```bash
curl -X GET http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🐛 Troubleshooting

### Port Already in Use

**If port 3000 is taken:**
```bash
# Use different port
cd frontend/textbook-site
npm run start -- --port 3001
```

**If port 8000 is taken:**
```bash
# Use different port
uvicorn src.main:app --port 8001
```

### Docker Services Won't Start

**Check logs:**
```bash
docker-compose logs
docker-compose logs api
docker-compose logs postgres
docker-compose logs redis
```

**Restart services:**
```bash
docker-compose down
docker-compose up -d
sleep 20
```

### npm Start Hangs

**Clear cache:**
```bash
cd frontend/textbook-site
rm -rf node_modules
npm install
npm run start
```

### Database Connection Error

**Verify database:**
```bash
docker-compose exec postgres psql -U personalization -c "SELECT 1;"
```

**If fails, restart:**
```bash
docker-compose down -v
docker-compose up -d
sleep 20
```

### API Not Responding

**Check if running:**
```bash
curl http://localhost:8000/health
```

**If fails, restart backend:**
```bash
# If using Docker
docker-compose restart api

# If using local backend
# Ctrl+C to stop, then:
uvicorn src.main:app --reload --port 8000
```

---

## 🎯 Full Testing Workflow

### Phase 1: Verify Services (5 minutes)

```bash
# Terminal 1: Start services
docker-compose up -d
sleep 15
docker-compose ps

# Terminal 2: Check health
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

### Phase 2: Start Documentation (5 minutes)

```bash
# Terminal 2: Start Docusaurus
cd frontend/textbook-site
npm run start
# Browser opens to http://localhost:3000
```

### Phase 3: Test Documentation (10 minutes)

In browser (http://localhost:3000):
- [ ] Navigate sidebar
- [ ] Read about Personalization System
- [ ] Check API Reference section
- [ ] View Deployment guide
- [ ] Read Architecture docs
- [ ] Test responsive design

### Phase 4: Test API (10 minutes)

In browser (http://localhost:8000/docs):
- [ ] Register user
- [ ] Login with credentials
- [ ] Get profile (using token)
- [ ] View available endpoints
- [ ] Try different endpoint groups

### Phase 5: Database Testing (5 minutes)

```bash
# Check data was created
docker-compose exec postgres psql -U personalization -d personalization_db \
  -c "SELECT * FROM users LIMIT 1;"

docker-compose exec postgres psql -U personalization -d personalization_db \
  -c "SELECT COUNT(*) FROM users;"
```

---

## 📚 What to Test in Each Section

### Personalization System (http://localhost:3000/docs/personalization/)

**System Overview** - Check:
- [ ] System architecture diagram visible
- [ ] Key features listed
- [ ] Learning journey flowchart displayed

**Features & Architecture** - Check:
- [ ] All 5 features documented
- [ ] Code examples present
- [ ] Tables and diagrams load

**Learning Paths** - Check:
- [ ] 4 learning paths described
- [ ] Path differences clear
- [ ] API examples shown

### API Reference (http://localhost:3000/docs/api/)

**API Overview** - Check:
- [ ] Response format explained
- [ ] Status codes listed
- [ ] Error codes documented

**Authentication Guide** - Check:
- [ ] JWT flow explained
- [ ] Token lifecycle documented
- [ ] Code examples present

**Endpoints Reference** - Check:
- [ ] All 15+ endpoints listed
- [ ] Request/response examples shown
- [ ] Tables with endpoint details

### Deployment (http://localhost:3000/docs/deployment/)

**Deployment Overview** - Check:
- [ ] Architecture diagram visible
- [ ] System requirements listed
- [ ] Services described

**Quick Start** - Check:
- [ ] 5-step setup clear
- [ ] Commands executable
- [ ] Expected outputs documented

### Development (http://localhost:3000/docs/development/)

**Architecture** - Check:
- [ ] 5-layer architecture visible
- [ ] Technology stack listed
- [ ] Performance metrics shown

---

## 🔍 API Testing with curl

### Complete User Journey

```bash
# 1. Register
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
  }')

echo "Register Response:"
echo $REGISTER_RESPONSE | jq

# 2. Extract token
ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.data.access_token')
echo "Access Token: $ACCESS_TOKEN"

# 3. Get profile
curl -s -X GET http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | jq

# 4. Get dashboard metrics
curl -s -X GET http://localhost:8000/api/v1/dashboard/metrics \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | jq

# 5. Complete a chapter
curl -s -X POST http://localhost:8000/api/v1/progress/1/complete \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mastery_score": 85,
    "time_spent_seconds": 1800
  }' | jq

# 6. Get achievements
curl -s -X GET http://localhost:8000/api/v1/progress/achievements \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | jq
```

---

## ✅ Verification Checklist

Before Deployment:
- [ ] Docker services running (3/3 healthy)
- [ ] Docusaurus loads (http://localhost:3000)
- [ ] API docs accessible (http://localhost:8000/docs)
- [ ] Health checks pass
- [ ] User registration works
- [ ] Token-based auth works
- [ ] API endpoints respond correctly
- [ ] Database queries execute
- [ ] All documentation pages render
- [ ] Mobile responsive works
- [ ] Search functionality works
- [ ] No console errors

---

## 🎉 Success Indicators

**Backend Working:**
- ✅ All 3 Docker services healthy
- ✅ API responds to requests
- ✅ Health check returns "ok"
- ✅ Users can register/login
- ✅ Database queries work

**Frontend Working:**
- ✅ Docusaurus loads
- ✅ Sidebar navigation works
- ✅ All pages render
- ✅ Search works
- ✅ Responsive on mobile

**System Working:**
- ✅ Can access documentation
- ✅ Can interact with API
- ✅ Can create users
- ✅ Can authenticate
- ✅ Can perform operations

---

## 📞 Quick Help Commands

```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs api
docker-compose logs postgres
docker-compose logs redis

# Restart all services
docker-compose restart

# Stop all services
docker-compose down

# Stop and remove data
docker-compose down -v

# View database
docker-compose exec postgres psql -U personalization

# View Redis
docker-compose exec redis redis-cli

# Rebuild images
docker-compose build

# Run tests
cd backend && pytest tests/ -v
```

---

## 🚀 Ready to Test?

**Start with:**
```bash
# Terminal 1
docker-compose up -d
sleep 15

# Terminal 2
cd frontend/textbook-site
npm run start
```

**Then visit:**
- http://localhost:3000 - Docusaurus Book
- http://localhost:8000/docs - API Documentation

**Enjoy testing!** 🎉

