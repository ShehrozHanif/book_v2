# Local Development Setup Guide

**Goal**: Run the complete RAG chatbot application locally before deploying to production

**Current Status**: All code complete, ready for local testing

---

## Prerequisites

✅ Python 3.14.2 (installed)
✅ Node v24.12.0 (installed)
✅ npm 11.6.2 (installed)
✅ Git (installed)
✅ PostgreSQL (if running Neon locally) OR SQLite (simpler)

**Choose**: SQLite (easier for local) OR PostgreSQL (same as production)

---

## Option 1: Local Setup with SQLite (Recommended for Quick Testing)

SQLite requires no additional installation. Database file stored locally.

### Step 1: Backend Setup (5 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "FastAPI|SQLAlchemy"
```

### Step 2: Configure Backend for Local Development

The `.env` file already exists. Verify it has:

```bash
# Check existing .env
cat backend/.env
```

Should contain:
```
DATABASE_URL=sqlite:///./test.db
OPENAI_API_KEY=sk-... (your key)
QDRANT_URL=http://localhost:6333 (or production URL)
QDRANT_API_KEY=... (your key)
OPENAI_MODEL=gpt-3.5-turbo
ENVIRONMENT=development
DEBUG=true
HOST=127.0.0.1
PORT=8000
```

**If DATABASE_URL is missing or wrong:**

```bash
# Edit .env and add/update:
DATABASE_URL=sqlite:///./test.db
```

### Step 3: Initialize Database

The database will auto-create on first run, but verify schema with:

```bash
cd backend

# Start Python and test connection
python -c "
from src.database.connection import engine, AsyncSessionLocal
from src.models.database import Base
import asyncio

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Database initialized')

asyncio.run(init())
"
```

### Step 4: Run Backend

```bash
cd backend

# Start FastAPI server
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

**Verify backend is working:**

```bash
# In another terminal:
curl http://127.0.0.1:8000/health
# Should return: {"status": "ok", "environment": "development"}

curl http://127.0.0.1:8000/docs
# Open in browser to see API documentation
```

### Step 5: Frontend Setup (5 minutes)

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list react

# Set API URL for local development
# Create/update .env.local
echo "REACT_APP_API_URL=http://127.0.0.1:8000" > .env.local
```

### Step 6: Run Frontend

```bash
cd frontend

# Start React development server
npm start

# You should see:
# Compiled successfully!
# On Your Network: http://192.168.x.x:3000
# Local: http://localhost:3000
```

Browser will auto-open at `http://localhost:3000`

### Step 7: Test Locally

Open browser to `http://localhost:3000`

**Test these flows**:

1. **Chat Widget Test**:
   - [ ] Chat widget opens
   - [ ] Click "Send message"
   - [ ] Type: "What is forward kinematics?"
   - [ ] Should receive response within 3 seconds
   - [ ] Response cites Chapter 2

2. **Authentication Test** (if available):
   - [ ] Sign up new user
   - [ ] Verify user created
   - [ ] Log in with credentials
   - [ ] Verify dashboard loads

3. **Network Test** (DevTools):
   - [ ] Open DevTools (F12)
   - [ ] Go to Network tab
   - [ ] Send chat message
   - [ ] Verify API request to `http://127.0.0.1:8000/api/v1/chat`
   - [ ] Response status should be 200
   - [ ] Response time displayed

4. **Performance Test**:
   - [ ] Chat response time: target <3 sec
   - [ ] Frontend load time: target <2 sec
   - [ ] Check DevTools → Performance tab

---

## Option 2: Local Setup with PostgreSQL (Production-Like)

If you want to test with actual PostgreSQL (closer to production):

### Step 1: Install PostgreSQL Locally

**Windows**:
- Download: https://www.postgresql.org/download/windows/
- Run installer, note the password you set for `postgres` user
- Default port: 5432

**macOS**:
```bash
brew install postgresql
brew services start postgresql
```

**Linux**:
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

### Step 2: Create Local Database

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql prompt:
CREATE DATABASE rag_chatbot;
\connect rag_chatbot
```

### Step 3: Update Backend .env

```bash
# Edit backend/.env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/rag_chatbot
```

### Step 4: Follow Backend Setup from Option 1

- Same venv creation
- Same dependency installation
- Database will auto-create schema on first run

### Step 5: Run Backend & Frontend

Same as Option 1, Steps 4-7

---

## Running Both Backend & Frontend Together

**Terminal 1** (Backend):
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2** (Frontend):
```bash
cd frontend
npm start
```

**Terminal 3** (Optional - Monitor logs):
```bash
# Watch backend logs
tail -f backend/backend.log

# Or watch test runs
cd backend && pytest -v
```

---

## Testing Checklist

### Backend Health

- [ ] `curl http://127.0.0.1:8000/health` → 200 OK with {"status": "ok"}
- [ ] `curl http://127.0.0.1:8000/ready` → 200 OK with database connected
- [ ] `curl http://127.0.0.1:8000/docs` → API docs page loads

### Frontend Health

- [ ] `http://localhost:3000` loads without errors
- [ ] Browser console (F12 → Console) has no red errors
- [ ] Network tab shows API calls succeeding

### Chat Functionality

- [ ] Type message in chat widget
- [ ] Response received within 3 seconds
- [ ] Response contains textbook content (chapters cited)
- [ ] No CORS errors in console
- [ ] No 404 errors in network tab

### Performance Metrics

- [ ] Page load time: <2 seconds (DevTools → Performance)
- [ ] Chat response time: <3 seconds (measure in DevTools → Network)
- [ ] CPU usage: <50% during operation (DevTools → Performance)
- [ ] Memory usage: <100MB for React (DevTools → Memory)

---

## Stopping the Servers

**Stop Backend**:
```bash
# Ctrl+C in Terminal 1
```

**Stop Frontend**:
```bash
# Ctrl+C in Terminal 2
```

**Deactivate Python venv**:
```bash
deactivate
```

---

## Troubleshooting

### Error: "Port 8000 already in use"

```bash
# Find what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # macOS/Linux

# Kill the process (Windows):
taskkill /PID <PID> /F

# Or use different port:
uvicorn src.main:app --port 8001
```

### Error: "DATABASE_URL not set"

```bash
# Verify .env exists in backend/
ls -la backend/.env

# Add to .env if missing:
echo "DATABASE_URL=sqlite:///./test.db" >> backend/.env
```

### Error: "OPENAI_API_KEY not set"

```bash
# Add your OpenAI key to backend/.env:
echo "OPENAI_API_KEY=sk-your-key-here" >> backend/.env

# Or set as environment variable:
# Windows:
set OPENAI_API_KEY=sk-your-key-here

# macOS/Linux:
export OPENAI_API_KEY=sk-your-key-here
```

### Error: "CORS error in browser console"

The backend should have CORS configured, but verify in `backend/src/main.py:60`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    ...
)
```

### Error: "Chat query returns error"

Check backend logs for:
- OpenAI API key invalid
- Qdrant connection failed
- Database query failed

Fix in `backend/.env` and restart backend.

### React won't start: "npm ERR!"

```bash
cd frontend

# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Try again
npm start
```

---

## Next Steps After Local Testing

### ✅ If Everything Works Locally:

1. **Commit your changes**:
   ```bash
   git add backend/.env frontend/.env
   git commit -m "Local development setup verified"
   ```

2. **Prepare for production**:
   - Update `backend/.env.production` with Neon credentials
   - Update `frontend/.env.production` with Render URL
   - Follow tasks.md Phase 1 for production setup

3. **Deploy to Render**:
   - Follow tasks.md Phase 3 (Deploy US1)

### ❌ If Something Doesn't Work:

1. **Check logs**:
   - Backend: `uvicorn` output in Terminal 1
   - Frontend: `npm` output in Terminal 2
   - Database: Check `.db` file exists in `backend/`

2. **Run tests**:
   ```bash
   cd backend
   pytest tests/ -v
   ```

3. **Check configuration**:
   - Verify all keys in `backend/.env`
   - Verify frontend API URL in `frontend/.env.local`
   - Verify ports (8000 backend, 3000 frontend)

4. **Clear cache & restart**:
   ```bash
   # Backend: Ctrl+C and restart
   # Frontend: Ctrl+C, then npm start
   ```

---

## Development Tips

### Hot Reload

Both FastAPI (`--reload`) and React (`npm start`) auto-reload on file changes. Just save and refresh/wait for auto-refresh.

### Debug Output

Add logging to backend:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")
```

Or use breakpoints in VS Code:
```python
import pdb; pdb.set_trace()  # Debugger will pause here
```

### Test Individual Endpoints

```bash
# Test chat endpoint
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is a humanoid robot?"}'

# Test with longer timeout if needed
curl --max-time 10 -X POST ...
```

### Monitor Database

If using SQLite:
```bash
# Check database file
ls -la backend/test.db

# View with sqlite3 CLI
sqlite3 backend/test.db
sqlite> SELECT * FROM users;
sqlite> .quit
```

---

## Files Modified for Local Testing

```
backend/
├── .env                         (local env vars)
├── test.db                      (auto-created SQLite, in .gitignore)
└── venv/                        (virtual env, in .gitignore)

frontend/
├── .env.local                   (local env vars, in .gitignore)
└── node_modules/               (npm packages, in .gitignore)
```

---

## Success Criteria (Local)

✅ Backend runs on http://127.0.0.1:8000
✅ Frontend runs on http://localhost:3000
✅ API health check returns 200 OK
✅ Chat widget loads
✅ Chat query returns response <3 sec
✅ No console errors
✅ No CORS errors
✅ No database errors

---

## Ready for Production?

Once all tests pass locally:

1. ✅ Backend works locally
2. ✅ Frontend connects to backend
3. ✅ Chat functionality verified
4. ✅ Performance targets met

**Then proceed to**: `specs/004-deployment/tasks.md` Phase 1 (Setup) for production deployment

---

**Document Created**: 2026-02-04
**Setup Time**: ~15 minutes (SQLite option)
**Test Time**: ~10 minutes
**Total**: ~25 minutes before production deployment
