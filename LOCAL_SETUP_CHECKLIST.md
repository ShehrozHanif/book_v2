# Local Setup & Testing Checklist

**Goal**: Get the app running locally → Test it → Then deploy to Render (backend) + Vercel (frontend)

---

## Phase 1: Backend Local Setup

### Step 1: Create Python Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```
- [ ] Virtual environment created and activated

### Step 2: Install Backend Dependencies
```bash
pip install -r requirements.txt
```
- [ ] All packages installed (check with: pip list | grep fastapi)

### Step 3: Setup Environment Variables
```bash
# Copy the example to .env
cp .env.example .env

# Edit .env with your values:
# - OPENAI_API_KEY=sk-...
# - DATABASE_URL=postgresql://...
# - QDRANT_URL=https://...
# - QDRANT_API_KEY=...
```
- [ ] .env file created with all required variables
- [ ] OpenAI API key added
- [ ] Database connection string added
- [ ] Qdrant credentials added

### Step 4: Initialize Database
```bash
# Run migrations (if using Alembic, otherwise skip)
# For now, SQLAlchemy will create tables on first connection
python -c "import asyncio; from src.database.connection import init_db; asyncio.run(init_db())"
```
- [ ] Database connection verified

### Step 5: Start Backend Server
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```
- [ ] Backend running at http://localhost:8000
- [ ] API docs available at http://localhost:8000/docs

### Step 6: Test Backend Endpoints
```bash
# In a new terminal, test:
curl http://localhost:8000/health

# Expected: {"status": "healthy"}
```
- [ ] Health check endpoint responds (GET /health)
- [ ] Chat endpoint accessible (POST /chat)
- [ ] API documentation loads (http://localhost:8000/docs)

---

## Phase 2: Frontend Local Setup

### Step 1: Install Frontend Dependencies
```bash
cd frontend
npm install
```
- [ ] All npm packages installed

### Step 2: Create Frontend .env
```bash
# Create .env.local file:
REACT_APP_API_URL=http://localhost:8000
```
- [ ] Frontend .env configured with backend URL

### Step 3: Start Frontend Development Server
```bash
npm start
```
Expected output:
```
webpack compiled with... warnings
You can now view the app in the browser at http://localhost:3000
```
- [ ] Frontend running at http://localhost:3000

### Step 4: Test Frontend in Browser
- [ ] Docusaurus site loads
- [ ] Navigation works
- [ ] Chatbot widget appears
- [ ] Can type in chat input
- [ ] No console errors

---

## Phase 3: End-to-End Local Testing

### Test 1: Chat Functionality
```
1. Go to http://localhost:3000
2. Open the chatbot widget
3. Type a question: "What is ROS 2?"
4. Wait for response
```
Acceptance:
- [ ] Question submitted successfully
- [ ] Chatbot responds with answer
- [ ] Response appears in conversation history
- [ ] No errors in browser console
- [ ] Response time < 5 seconds (local)

### Test 2: Text Selection Query
```
1. Select text from a book chapter
2. Should trigger chat query automatically
3. Chatbot should answer about selected text
```
Acceptance:
- [ ] Text selection triggers chat
- [ ] Context preserved
- [ ] No JavaScript errors

### Test 3: Chat History
```
1. Send multiple messages
2. Refresh the page
3. Check if conversation persists
```
Acceptance:
- [ ] Messages persist across refresh
- [ ] User session maintained

### Test 4: Error Handling
```
1. Send very long query (>5000 chars)
2. Send empty message
3. Simulate backend disconnection
```
Acceptance:
- [ ] Long queries rejected gracefully
- [ ] Empty messages not sent
- [ ] Disconnection shows error message

---

## Phase 4: Pre-Deployment Verification

### Backend Verification
```bash
# From backend directory:
cd backend

# Check Python version
python --version
# Expected: Python 3.10 or higher

# Verify all imports work
python -c "from src.main import app; print('✅ App imports successfully')"

# Check all environment variables loaded
python -c "from src.config import get_settings; print(get_settings())"
```
- [ ] Python version >= 3.10
- [ ] All imports work
- [ ] Settings load correctly

### Frontend Verification
```bash
# From frontend directory:
cd frontend

# Check Node version
node --version
# Expected: v16 or higher

# Build for production
npm run build

# Expected: Build folder created with optimized code
```
- [ ] Node version >= 16
- [ ] Production build succeeds
- [ ] No build errors or warnings

---

## ✅ Deployment Readiness Checklist

Before deploying, confirm ALL of these:

**Backend Ready?**
- [ ] Uvicorn server runs without errors
- [ ] Health check returns 200
- [ ] Chat endpoint accepts requests
- [ ] Database connection works
- [ ] All env vars configured
- [ ] requirements.txt includes all dependencies
- [ ] No console errors

**Frontend Ready?**
- [ ] npm install completes
- [ ] npm start runs without errors
- [ ] Chatbot widget loads
- [ ] Can connect to backend
- [ ] Production build succeeds
- [ ] No console errors
- [ ] package.json has all scripts

**Integration Ready?**
- [ ] E2E test successful
- [ ] Chat requests return responses
- [ ] No CORS errors
- [ ] Error handling works
- [ ] Performance acceptable

---

## 🚀 Next Steps (After Checklist Complete)

When ALL items above are checked:

1. **Commit to git** (mark tasks complete)
   ```bash
   git add .
   git commit -m "Complete local setup and testing - ready for deployment"
   ```

2. **Deploy Backend to Render**
   - Connect GitHub repo to Render
   - Set environment variables
   - Deploy

3. **Deploy Frontend to Vercel**
   - Connect GitHub repo to Vercel
   - Update API_URL to Render backend URL
   - Deploy

4. **Test Production** (live URLs)

5. **Create Demo Video**

6. **Submit**

---

## 📝 Troubleshooting

### Backend won't start
```
Error: ModuleNotFoundError: No module named 'fastapi'
→ Solution: Run `pip install -r requirements.txt`

Error: ERROR: could not open database
→ Solution: Check DATABASE_URL in .env

Error: OpenAI API error
→ Solution: Verify OPENAI_API_KEY in .env
```

### Frontend won't load
```
Error: npm ERR! code ERESOLVE
→ Solution: Run `npm install --legacy-peer-deps`

Error: Cannot find module 'react'
→ Solution: Run `npm install`

Error: API connection refused
→ Solution: Check REACT_APP_API_URL, backend must be running
```

### Chat not working
```
Error: CORS error in console
→ Solution: Check CORS config in backend/src/main.py

Error: 404 on /chat
→ Solution: Verify chat.py route is registered in main.py

Error: No response from chatbot
→ Solution: Check Qdrant and OpenAI credentials in .env
```

---

**Status**: ⏳ READY TO START
**Start with**: Phase 1, Step 1 (Create virtual environment)
