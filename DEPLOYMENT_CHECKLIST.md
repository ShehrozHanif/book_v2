# 🚀 Production Deployment Checklist

**Status**: Ready to Deploy ✅
**Created**: 2026-02-04 22:40 UTC

All preparation is complete. Follow these steps in order.

---

## Phase 1: Account Setup (10 minutes)

### Neon PostgreSQL

- [ ] Go to https://neon.tech
- [ ] Sign up with GitHub (recommended)
- [ ] Create project: `robotics-textbook-rag`
- [ ] Copy connection string (format: `postgresql://user:password@ep-xxxx.us-west-2.aws.neon.tech/neondb?sslmode=require`)
- [ ] Initialize schema using Neon SQL Editor (paste `backend/src/database/schema.sql`)
- [ ] Verify with `\dt` command (list tables)

### Render

- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Authorize repository access
- [ ] **Do NOT create service yet** (Phase 4)

### GitHub Pages

- [ ] Repository Settings → Pages
- [ ] Source: Deploy from a branch
- [ ] Branch: `gh-pages`
- [ ] Folder: `/ (root)`

---

## Phase 2: Collect Secrets (5 minutes)

Write down these values:

- [ ] Neon Connection String: `postgresql://...`
- [ ] OpenAI API Key: `sk-proj-...`
- [ ] Qdrant API Key: `...`
- [ ] GitHub Username: `...`
- [ ] JWT Secret (run: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

---

## Phase 3: Update Configuration Files (5 minutes)

### Update `backend/.env.production`

Replace ALL placeholders with actual values:
- `[USER]:[PASSWORD]` → actual Neon credentials
- `[OPENAI_API_KEY]` → your OpenAI key
- `[YOUR_GITHUB_USERNAME]` → your GitHub username
- `[GENERATE_NEW_SECRET_KEY_MIN_32_CHARS]` → output from secrets command

### Update `frontend/package.json`

Find line with `"homepage"` and replace:
```json
"homepage": "https://[YOUR_GITHUB_USERNAME].github.io/book",
```
becomes:
```json
"homepage": "https://your-username.github.io/book",
```

---

## Phase 4: Deploy Backend to Render (15 minutes)

1. Go to https://render.com → Dashboard
2. Click **New +** → **Web Service**
3. Select your GitHub repository
4. Configure:
   - Service Name: `robotics-rag-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - Plan: `Free`

5. Go to **Environment** tab
6. Add all variables from `backend/.env.production`
7. Click **Create Web Service**
8. Wait for build (5-10 minutes)
9. Test: `curl https://robotics-rag-backend.onrender.com/health`

---

## Phase 5: Deploy Frontend to GitHub Pages (10 minutes)

```bash
cd frontend
npm install
npm run build
npm run deploy
```

Wait 2-3 minutes, then test: `https://[your-username].github.io/book`

---

## Phase 6: Test Everything (15 minutes)

### Backend Health
```bash
curl https://robotics-rag-backend.onrender.com/health
# Should return: {"status": "ok", "environment": "production"}
```

### Frontend Load
- [ ] Site loads in browser (no 404)
- [ ] Chat widget visible
- [ ] No console errors (F12 → Console)

### Chat Functionality
1. Open chat widget
2. Send: "What is forward kinematics?"
3. Check:
   - [ ] Response received
   - [ ] Response cites Chapter 2
   - [ ] Response time < 3 seconds
   - [ ] No CORS errors in console

Test additional queries:
- [ ] "Explain the Zero Moment Point"
- [ ] "How do I set up ROS 2 nodes?"
- [ ] "Ethical considerations in humanoid robots"
- [ ] "Motion planning code examples"

### Performance
- [ ] Page load time: < 2 seconds
- [ ] Chat response time: < 3 seconds
- [ ] No network errors

---

## Phase 7: Monitor Logs (5 minutes)

### Backend Logs (Render)
1. Go to Render dashboard
2. Select service
3. Click **Logs**
4. Check for errors (should be clean)

### Database (Neon)
1. Go to Neon dashboard
2. Check "Monitoring" tab
3. Verify queries are working

---

## Troubleshooting Quick Reference

### Frontend 404
- Check GitHub Pages is enabled (Settings → Pages)
- Verify branch is `gh-pages`
- Try `npm run deploy` again
- Wait 5 minutes, refresh

### Chat Not Responding
- Open DevTools (F12)
- Check Console for CORS errors
- If CORS error: Update `ALLOWED_ORIGINS` in Render, wait 1-2 min

### Backend Error
- Check Render logs (Render Dashboard → Logs)
- Verify all env vars are set
- Check database connection string format

### Database Error
- Verify connection string has `?sslmode=require`
- Test: `psql "your-connection-string"`
- Check Neon dashboard for project status

---

## Files Modified

Created for deployment:
- `backend/.env.production` ✅
- `frontend/.env.production` ✅
- `DEPLOYMENT_STATUS.md` ✅
- `DEPLOYMENT_CHECKLIST.md` ✅
- `frontend/package.json` (updated) ✅

---

## Success Criteria (All Must Pass)

- [ ] Backend health check returns 200
- [ ] Frontend loads at GitHub Pages URL
- [ ] Chat widget opens
- [ ] Chat sends and receives messages
- [ ] Response cites correct chapters
- [ ] Page load < 2 seconds
- [ ] Chat response < 3 seconds
- [ ] No CORS errors in console
- [ ] No errors in Render logs

---

## Next Action

1. Create Neon account: https://neon.tech
2. Create Render account: https://render.com
3. Follow steps above in order

**Estimated Total Time**: ~50 minutes

For detailed troubleshooting, see `DEPLOYMENT_GUIDE.md`
