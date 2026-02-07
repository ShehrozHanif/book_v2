# Run Hackathon1 Book Locally - Step by Step

**Date**: 2026-02-07
**Status**: Ready to Run

---

## 🚀 Method 1: Automatic (Easiest)

### Windows Users - Double Click:
```
C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\START_LOCAL.bat
```

**This will automatically:**
1. ✅ Start Docker services (PostgreSQL, Redis, FastAPI)
2. ✅ Wait for services to become healthy
3. ✅ Start Docusaurus (npm run start)
4. ✅ Open 2 browser windows:
   - http://localhost:3000 (Docusaurus Book)
   - http://localhost:8000/docs (API Docs)

---

## 🔧 Method 2: Manual (If Script Doesn't Work)

### Step 1: Open Terminal/PowerShell

**Press:**
```
Windows Key + R
```

**Type:**
```
powershell
```

**Press Enter**

---

### Step 2: Navigate to Project

**Type this command:**
```powershell
cd "C:\Users\Shehroz Hanif\Desktop\Hackathon1\book"
```

**Press Enter**

---

### Step 3: Start Docker Services

**Type:**
```powershell
docker-compose up -d
```

**Press Enter**

**Expected output:**
```
[+] Running 3/3
  ✓ Network personalization-network  Created
  ✓ Container personalization-postgres  Started
  ✓ Container personalization-redis  Started
  ✓ Container personalization-api  Started
```

---

### Step 4: Wait & Verify Services

**Type:**
```powershell
sleep 15
docker-compose ps
```

**Press Enter**

**Expected output - all should show "Up (healthy)":**
```
NAME                         COMMAND                  STATUS
personalization-postgres     docker-entrypoint...     Up (healthy)
personalization-redis        redis-server...          Up (healthy)
personalization-api          uvicorn main:app...      Up (healthy)
```

---

### Step 5: Open New Terminal for Docusaurus

**Press:**
```
Windows Key + R
```

**Type:**
```
powershell
```

**Press Enter**

---

### Step 6: Start Docusaurus

**Type:**
```powershell
cd "C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site"
npm install
npm run start
```

**Press Enter**

**This will take 2-3 minutes. Expected output when done:**
```
[INFO] Docusaurus website is running at: http://localhost:3000/
```

**When you see this message, Docusaurus is ready!**

---

### Step 7: Open Browsers

**Open 2 new browser windows:**

1. **First browser:** http://localhost:3000
   - This is the Docusaurus book

2. **Second browser:** http://localhost:8000/docs
   - This is the Swagger API documentation

---

## ✅ What You Should See

### Browser 1: http://localhost:3000

**Docusaurus Book:**
```
Left Sidebar:
├── Home
├── Getting Started
├── 📚 Textbook Content
│   ├── Module 1: Foundations
│   ├── Module 2: ROS2
│   ├── Module 3: Advanced Kinematics
│   ├── Module 4: Learning & Control
│   └── Module 5: Applications
├── 🎓 Personalization System
│   ├── System Overview
│   ├── Features & Architecture
│   └── Learning Paths
├── 🔌 API Reference
│   ├── API Overview
│   ├── Authentication
│   └── Endpoints
├── 🚀 Deployment & Operations
│   ├── Overview
│   └── Quick Start
└── 💻 Development Guide
    └── System Architecture

Top Right:
├── 🔍 Search box
└── 🌙 Dark mode toggle
```

### Browser 2: http://localhost:8000/docs

**Swagger API:**
```
Left Sidebar - Endpoints:
├── Authentication
│   ├── POST /users/register
│   ├── POST /users/login
│   └── POST /users/refresh
├── User Profile
│   ├── GET /users/profile
│   └── PUT /users/profile
├── Progress
│   ├── POST /progress/{chapter_id}/complete
│   ├── POST /progress/{chapter_id}/practice
│   ├── POST /progress/{chapter_id}/retry
│   └── GET /dashboard/metrics
├── Achievements
│   └── GET /progress/{user_id}/achievements
├── Statistics
│   └── GET /users/{user_id}/statistics
├── Learning Paths
│   ├── GET /learning-paths
│   └── POST /learning-paths/select
├── Preferences
│   ├── GET /users/{user_id}/preferences
│   └── PUT /users/{user_id}/preferences
├── Advanced Challenges
│   └── GET /progress/{chapter_id}/advanced-challenges
└── Health
    ├── GET /health
    ├── GET /ready
    └── GET /health/cache

Top:
├── Authorize button (for JWT token)
└── API schema information
```

---

## 🧪 Quick Test (5 Minutes)

### In Browser 2 (http://localhost:8000/docs):

**Step 1: Register User**
1. Find "POST /users/register"
2. Click it to expand
3. Click "Try it out" button
4. Enter this JSON:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "TestPass123!"
}
```
5. Click "Execute" button
6. Look for green "200" or "201" response code
7. Copy the `access_token` from response

**Step 2: Get Profile**
1. Click "Authorize" button at top
2. Paste your access_token
3. Click "Authorize"
4. Find "GET /users/profile"
5. Click "Try it out"
6. Click "Execute"
7. Should see your user profile data

**Step 3: View Documentation**
1. Go to Browser 1: http://localhost:3000
2. Click on sections:
   - Read "Personalization System Overview"
   - Check "API Reference"
   - View "Deployment Guide"
3. Use search (magnifying glass) to find topics
4. Test mobile view (F12 → toggle device toolbar)

---

## 🔍 Verify Everything Works

### Terminal 1 - Check Docker (Original Terminal)

```powershell
docker-compose ps
```

Should show all 3 services as "Up (healthy)"

---

### Terminal 2 - Docusaurus Running

Should show:
```
[INFO] Docusaurus website is running at: http://localhost:3000/
```

---

### Browser Tests

✅ **http://localhost:3000**
- [ ] Page loads
- [ ] Sidebar visible
- [ ] Can click sections
- [ ] Content displays

✅ **http://localhost:8000/docs**
- [ ] Swagger UI loads
- [ ] Can see all endpoints
- [ ] Can try endpoints
- [ ] Get successful responses

✅ **http://localhost:8000/redoc**
- [ ] Alternative API docs view
- [ ] Shows same endpoints

✅ **http://localhost:8000/health**
- [ ] Returns: `{"status":"ok"}`

---

## 🛑 Stop Services When Done

### Option 1: Stop via Terminal

```powershell
docker-compose down
```

### Option 2: Stop via Docker Desktop

1. Open Docker Desktop
2. Click the stop button next to services

---

## ❌ If Something Goes Wrong

### Services Won't Start

```powershell
# Check what's happening
docker-compose logs

# Restart everything
docker-compose down
docker-compose up -d
sleep 15
docker-compose ps
```

### Docusaurus Won't Start

```powershell
cd frontend/textbook-site
# Clear cache
rm -r node_modules
npm cache clean --force
npm install
npm run start
```

### Port Already in Use

```powershell
# Use different port for Docusaurus
npm run start -- --port 3001
# Then visit http://localhost:3001
```

### Can't Find Docker

```powershell
# Check if Docker is installed
docker --version

# If not installed, download from:
# https://www.docker.com/products/docker-desktop
```

---

## 📊 What Each Service Does

| Service | Port | Purpose |
|---------|------|---------|
| **PostgreSQL** | 5432 | Database (user data) |
| **Redis** | 6379 | Cache (fast responses) |
| **FastAPI** | 8000 | Backend API |
| **Docusaurus** | 3000 | Frontend documentation |

---

## 🎯 Success Checklist

After running everything, you should have:

- ✅ Docker showing 3 healthy services
- ✅ http://localhost:3000 showing Docusaurus book
- ✅ http://localhost:8000/docs showing Swagger API
- ✅ Can register a user via API
- ✅ Can login and get token
- ✅ Can call authenticated endpoints
- ✅ No error messages in browsers
- ✅ No error messages in terminals

---

## 🎉 Ready?

**Pick one:**

**Option 1 (Easiest):**
```
Double-click START_LOCAL.bat
```

**Option 2 (Manual):**
Follow steps above in PowerShell

**Then visit in browser:**
- http://localhost:3000 (Book)
- http://localhost:8000/docs (API)

---

## 📞 Troubleshooting

**Issue: Docker not found**
- Solution: Install Docker Desktop from https://www.docker.com/products/docker-desktop

**Issue: npm not found**
- Solution: Install Node.js from https://nodejs.org/

**Issue: Port 3000 or 8000 in use**
- Solution: Change port in npm run start or stop other services

**Issue: Services hang**
- Solution: Stop (docker-compose down) and start fresh

---

## ⏱️ Timing

| Step | Time |
|------|------|
| Docker services start | 15-20 sec |
| npm install (first time) | 2-3 min |
| npm run start | 1-2 min |
| **Total** | **5-6 minutes** |

---

**Everything is ready! Start the services and enjoy testing!** 🚀

