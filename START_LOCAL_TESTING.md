# Local Testing - Quick Start Guide

## 🚀 Start Both Servers Locally

Follow these steps to run the personalization integration locally on your machine.

---

## Step 1: Open Terminal 1 - Start Backend API

```bash
cd "C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\backend"
python -m uvicorn src.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ **Backend is ready when you see:** `Application startup complete`

**URL:** http://localhost:8000/api/v1

---

## Step 2: Open Terminal 2 - Start Frontend (Textbook)

```bash
cd "C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site"
npm run start
```

**Expected Output:**
```
Docusaurus is running at http://localhost:3000/book/
```

✅ **Frontend is ready when you see the browser open automatically**

**URL:** http://localhost:3000/book/

---

## 🧪 Testing the Features

### 1. Test Login Page
1. Go to: http://localhost:3000/book/login
2. Click "Don't have an account? Sign up"
3. Fill in:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `password123`
4. Click "Create Account"
5. Should redirect to home page (logged in)

### 2. Test Progress Icons in Sidebar
1. After login, go to any chapter: http://localhost:3000/book/docs/module-01/chapter-01
2. **Look at sidebar** - you should see **icons next to chapter names**:
   - ✓ (green) = Completed
   - 📈 (orange) = In Progress
   - ◯ (gray) = Not Started
3. **Hover over icons** to see mastery percentage

### 3. Test Practice Questions Widget
1. Scroll to **bottom of any chapter page**
2. Look for **"📝 Test Your Knowledge"** section
3. Click to expand
4. Answer all questions
5. Click **"Submit Answers"**
6. See your score
7. **Check sidebar** - progress icon should update!

### 4. Test Dashboard
1. Go to: http://localhost:3000/book/dashboard
2. You should see:
   - Progress overview card
   - Mastery heatmap (by chapter)
   - Time spent chart
   - Learning curve
   - Focus area recommendations
3. Click **🔄 Refresh** button to update data

### 5. Test Logout
1. Click **Login button** in navbar (top right)
2. Should show user menu with logout
3. Click logout
4. Sidebar icons disappear
5. Practice widget shows "Login to track progress"
6. Dashboard redirects to login

---

## 🔍 Debugging Tips

### Check Backend is Running
```bash
curl http://localhost:8000/api/v1/health
```

Should return status 200 or similar.

### Check Frontend is Running
```bash
curl http://localhost:3000/book/
```

Should return HTML of the page.

### View Browser Console
1. Press **F12** to open DevTools
2. Go to **Console** tab
3. Look for any red errors
4. Check **Network** tab to see API calls

### Check localStorage
1. Press **F12** to open DevTools
2. Go to **Application** tab
3. Click **localStorage** → http://localhost:3000
4. You should see:
   - `access_token` (JWT)
   - `user` (user data)
   - `progress_cache` (cached progress)

---

## 📋 Checklist: All Features Working

- [ ] Backend starts without errors
- [ ] Frontend starts and opens browser
- [ ] Can create account at /login
- [ ] Can log in with valid credentials
- [ ] Can log out
- [ ] Progress icons visible in sidebar
- [ ] Practice widget appears at chapter bottom
- [ ] Can submit practice questions
- [ ] Sidebar icons update after submission
- [ ] Dashboard shows statistics
- [ ] No red errors in browser console
- [ ] localStorage contains tokens

---

## 🛑 Stopping Servers

### To Stop Backend
Press **Ctrl+C** in Terminal 1

### To Stop Frontend
Press **Ctrl+C** in Terminal 2

---

## ⚠️ Common Issues & Solutions

### "Module not found" Error in Backend
```
ERROR: Could not import module "main"
```
**Solution:** Make sure you're in the `backend` directory and running:
```bash
python -m uvicorn src.main:app --reload --port 8000
```

### Frontend port 3000 already in use
```
Error: listen EADDRINUSE :::3000
```
**Solution:** Kill the existing process:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9
```

### Backend won't start on port 8000
```
Error: Address already in use
```
**Solution:** Use a different port:
```bash
python -m uvicorn src.main:app --reload --port 8001
```

Then update `.env` in textbook-site:
```
REACT_APP_API_URL=http://localhost:8001/api/v1
```

### "Cannot GET /login" Error
**Solution:** Make sure you're using `/book/login` not just `/login`:
```
✓ http://localhost:3000/book/login
✗ http://localhost:3000/login
```

### Practice questions not loading
**Solution:**
1. Check backend is running (terminal 1)
2. Check browser console (F12) for errors
3. Verify you're logged in (check localStorage)
4. Verify chapter URL contains `/chapter-`

### Sidebar icons not showing
**Solution:**
1. Log in first
2. Refresh the page
3. Check body tag has `data-auth="true"` (F12 → Inspector)
4. Check CSS is loaded (F12 → Elements → .chapter-progress-icon-wrapper)

---

## 📊 Testing Scenarios

### Scenario 1: New User Flow
1. Go to `/login`
2. Click "Sign up"
3. Register with email: `newuser@test.com`
4. Check localStorage has tokens
5. Sidebar should show all ◯ (not started)

### Scenario 2: Complete Practice Questions
1. Log in
2. Go to Chapter 1
3. Answer all questions
4. Submit
5. See score
6. Check sidebar - Ch 1 icon should change to ✓ or 📈

### Scenario 3: View Dashboard
1. Complete practice in 2-3 chapters
2. Go to `/dashboard`
3. Should show:
   - Progress: X/22 chapters
   - Mastery heatmap with your scores
   - Time spent chart
   - Learning curve (if available)

### Scenario 4: Mobile Testing
1. Open browser DevTools (F12)
2. Click device toggle (top left)
3. Select iPhone SE (375px width)
4. Test:
   - Sidebar on mobile
   - Practice widget scrolls properly
   - Dashboard is readable
   - Buttons are clickable (44px+)

---

## 🎯 What to Test

✅ **Authentication**
- [ ] Register account
- [ ] Login with email/password
- [ ] Logout functionality
- [ ] Token persists on refresh
- [ ] Invalid credentials rejected

✅ **Progress Tracking**
- [ ] Icons appear in sidebar
- [ ] Correct status displayed
- [ ] Mastery % on hover
- [ ] Icons update after practice

✅ **Practice Widget**
- [ ] Questions load dynamically
- [ ] All questions are required
- [ ] Score calculated correctly
- [ ] Feedback displays
- [ ] Progress saves

✅ **Dashboard**
- [ ] Requires authentication
- [ ] Shows all statistics
- [ ] Charts display correctly
- [ ] Refresh button works
- [ ] Responsive on mobile

✅ **User Experience**
- [ ] No console errors
- [ ] Smooth animations
- [ ] Mobile responsive
- [ ] Keyboard accessible
- [ ] Fast loading

---

## 📞 If Something Doesn't Work

1. **Check browser console** (F12 → Console)
   - Look for red error messages
   - Check network errors

2. **Check backend is running**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

3. **Check network requests**
   - F12 → Network tab
   - Perform an action (login, submit practice)
   - Look for the API request
   - Check response status (200 = OK)

4. **Clear browser data**
   - Clear localStorage: `localStorage.clear()`
   - Clear cache: Ctrl+Shift+Delete
   - Close and reopen browser

5. **Restart servers**
   - Stop backend (Ctrl+C)
   - Stop frontend (Ctrl+C)
   - Start both again

---

## 📈 Performance Tips

**Frontend feels slow?**
- Check Network tab for slow API calls
- Verify backend is running
- Try closing other browser tabs
- Rebuild frontend: `npm run build`

**Dashboard takes long to load?**
- First load fetches from API
- Subsequent loads use cache
- Try refresh button
- Check Network tab for request time

---

## 📚 Quick Reference

| URL | Purpose |
|-----|---------|
| http://localhost:3000/book/ | Home page |
| http://localhost:3000/book/login | Login/Register |
| http://localhost:3000/book/docs/module-01/chapter-01 | Chapter 1 with practice |
| http://localhost:3000/book/dashboard | Statistics dashboard |
| http://localhost:8000/api/v1 | Backend API root |

---

## 🎓 Next Steps After Testing

1. ✅ Verify all features work
2. ✅ Test on mobile (DevTools responsive mode)
3. ✅ Check console for no errors
4. ✅ Review documentation:
   - `PERSONALIZATION_SETUP.md`
   - `PERSONALIZATION_INTEGRATION_SUMMARY.md`
5. ✅ Customize as needed (colors, API URL, etc.)
6. ✅ Deploy to production when ready

---

**Happy Testing! 🚀**

For issues or questions, refer to:
- `PERSONALIZATION_SETUP.md` - Troubleshooting section
- Browser DevTools Console - Error messages
- Backend logs - API errors
