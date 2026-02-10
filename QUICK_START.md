# 🚀 Quick Start: Production Deployment

**Status**: Configuration Complete ✅
**Next Step**: Deploy to Neon + Render + GitHub Pages

---

## Overview

Your RAG chatbot is ready to deploy. All code is prepared. You just need to:

1. **Create 2 accounts** (15 min, free tier)
2. **Update 2 config files** with your credentials (5 min)
3. **Run deployment commands** (5 min for frontend, 10 min for backend)
4. **Test everything** (15 min)

**Total Time**: ~50 minutes

---

## The 3-Step Deployment

### Step 1: Create Accounts & Get Credentials (15 min)

**Neon PostgreSQL:**
```
1. Go to https://neon.tech
2. Sign up with GitHub
3. Create project: robotics-textbook-rag
4. Copy connection string: postgresql://...@ep-xxxx.us-west-2.aws.neon.tech/...
```

**Render:**
```
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize repo access
4. (Don't create service yet - we'll do that after config)
```

**GitHub Pages:**
```
Already enabled. Just ensure it's set to deploy from gh-pages branch.
```

**Secrets to Collect:**
- [ ] Neon connection string
- [ ] OpenAI API key (from https://platform.openai.com/api-keys)
- [ ] Qdrant API key (from your Qdrant Cloud account)
- [ ] Your GitHub username

---

### Step 2: Update Configuration Files (5 min)

**File 1: `backend/.env.production`**

Open the file and replace these placeholders:

```diff
- DATABASE_URL=postgresql+asyncpg://[USER]:[PASSWORD]@[NEON_HOST]/[DBNAME]?sslmode=require
+ DATABASE_URL=postgresql+asyncpg://postgres:mypassword@ep-abc123.us-west-2.aws.neon.tech/neondb?sslmode=require

- OPENAI_API_KEY=[YOUR_OPENAI_API_KEY]
+ OPENAI_API_KEY=sk-proj-ABC123def456...

- QDRANT_API_KEY=[YOUR_QDRANT_API_KEY]  
+ QDRANT_API_KEY=myqdrantkey123...

- ALLOWED_ORIGINS=["https://[YOUR_GITHUB_USERNAME].github.io", "https://[YOUR_GITHUB_USERNAME].github.io/book"]
+ ALLOWED_ORIGINS=["https://john-doe.github.io", "https://john-doe.github.io/book"]

- JWT_SECRET_KEY=[GENERATE_NEW_SECRET_KEY_MIN_32_CHARS]
+ JWT_SECRET_KEY=aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456
```

**To generate JWT_SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**File 2: `frontend/package.json`**

Find this line:
```json
"homepage": "https://[YOUR_GITHUB_USERNAME].github.io/book",
```

Replace `[YOUR_GITHUB_USERNAME]` with your actual GitHub username:
```json
"homepage": "https://john-doe.github.io/book",
```

---

### Step 3: Deploy (15 min)

**Deploy Backend to Render:**

1. Go to https://render.com → Dashboard
2. Click **New +** → **Web Service**
3. Select your repository (book)
4. Configure:
   - Service Name: `robotics-rag-backend`
   - Environment: `Python 3`
   - Build: `pip install -r backend/requirements.txt`
   - Start: `cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Go to **Environment** tab
6. Add all variables from your updated `backend/.env.production`
7. Click **Create Web Service**
8. Wait for build (5-10 minutes)

**Deploy Frontend to GitHub Pages:**

```bash
cd frontend
npm install
npm run build
npm run deploy
```

Wait 2-3 minutes. Then test: `https://your-username.github.io/book`

---

## Verify It Works

### Test 1: Backend Health
```bash
curl https://robotics-rag-backend.onrender.com/health
# Should return: {"status": "ok", "environment": "production"}
```

### Test 2: Frontend Loads
- Open: `https://your-username.github.io/book`
- Should load without 404 error
- Chat widget should be visible

### Test 3: Chat Works
1. Open chat widget
2. Send: "What is forward kinematics?"
3. Should get response in < 3 seconds
4. Response should cite Chapter 2 of textbook

---

## If Something Goes Wrong

**Frontend 404 error?**
- Wait 5 minutes (GitHub Pages is slow)
- Re-run: `npm run deploy`

**Chat not responding?**
- Open DevTools (F12) → Console
- Look for red CORS errors
- If CORS error: Update `ALLOWED_ORIGINS` in Render, wait 1-2 min

**Backend error?**
- Check Render Logs: Render Dashboard → Your service → Logs
- Look for database connection errors
- Verify all env vars are set (no missing values)

**Database connection error?**
- Verify connection string has `?sslmode=require` at end
- Test locally: `psql "your-connection-string"`
- Check Neon dashboard

---

## Full Documentation

- **DEPLOYMENT_CHECKLIST.md** - Detailed phase-by-phase checklist
- **DEPLOYMENT_GUIDE.md** - Complete step-by-step with troubleshooting
- **DEPLOYMENT_STATUS.md** - Architecture, file list, env vars

---

## Quick Commands

```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Test backend
curl https://robotics-rag-backend.onrender.com/health

# Deploy frontend
cd frontend && npm install && npm run build && npm run deploy

# Connect to database
psql "postgresql://user:pass@ep-xxxx.us-west-2.aws.neon.tech/neondb?sslmode=require"
```

---

## Expected Costs

**First Month (Free Tier):**
- Neon: $0
- Render: $0
- GitHub Pages: $0
- OpenAI: ~$5-20 (usage-based)
- **Total: $5-20**

**Upgrade to Always-On (Optional):**
- Render paid: +$7/month

---

## Timeline

| Task | Duration | Status |
|------|----------|--------|
| Create accounts | 15 min | Manual |
| Update config files | 5 min | Manual |
| Deploy backend | 15 min | Auto |
| Deploy frontend | 5 min | Auto |
| Test | 15 min | Manual |
| **Total** | **~55 min** | ✅ Ready |

---

## Success Checklist

- [ ] Created Neon and Render accounts
- [ ] Collected all secrets
- [ ] Updated `backend/.env.production`
- [ ] Updated `frontend/package.json` homepage
- [ ] Deployed backend to Render
- [ ] Deployed frontend to GitHub Pages
- [ ] Backend /health endpoint responds
- [ ] Frontend loads without 404
- [ ] Chat widget works
- [ ] Test query returns response
- [ ] No CORS errors in console

---

**You're Ready!** 🚀

Start here: Create Neon account at https://neon.tech
