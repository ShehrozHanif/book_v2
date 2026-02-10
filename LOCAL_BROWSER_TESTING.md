# 🧪 LOCAL BROWSER TESTING - Test Your Docusaurus Book NOW

**Date**: 2026-02-09
**Goal**: Run your book locally and test in browser before deployment

---

## ⚡ QUICK START (2 MINUTES)

### Copy & Paste This Command:

```bash
cd C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site && npm install && npm start
```

**Then:**
1. Wait 2-3 minutes for npm to install packages
2. Browser opens automatically at `http://localhost:3000`
3. Click around and explore your book!
4. When done testing, press `Ctrl+C` to stop

---

## 📖 WHAT YOU'LL SEE

When it's working, you'll see:

```
✓ ready in 2.3s
[SUCCESS] Docusaurus server is running on: http://localhost:3000
```

And your browser opens with your textbook showing:
- Homepage with "Start Here" button
- All 22 chapters organized in 5 modules
- Full navigation sidebar
- Search functionality

---

## ✅ QUICK TESTS (5 MINUTES)

### Test 1: Click around sidebar
1. Look at left sidebar
2. Click on "Chapter 6: ROS 2 Fundamentals"
3. Content should load instantly
4. Click another chapter
5. Verify it changes

### Test 2: Use search
1. Click search icon (🔍 top right)
2. Type: "kinematics"
3. See results appear
4. Click a result
5. Should navigate to that chapter

### Test 3: Try next/previous
1. Scroll down to bottom of chapter
2. Click "Next →" button
3. Should load next chapter
4. Click "← Previous" button
5. Should load previous chapter

### Test 4: Mobile view
1. Press `F12` (opens Developer Tools)
2. Click phone icon (top left of developer tools)
3. Select "iPhone 12"
4. Verify page is readable
5. Click menu icon to see sidebar
6. Should work on phone

### Test 5: Check for errors
1. Still in Developer Tools (F12)
2. Go to "Console" tab
3. Reload page (`Ctrl+R`)
4. Look for red error messages
5. Green/yellow are OK, red is bad
6. Fix red errors if any

---

## 🛠️ STEP-BY-STEP GUIDE

### Step 1: Prerequisites Check

Open a terminal and verify you have Node.js:

```bash
node --version
```

Should show: `v20.x` or higher

If not: Download from https://nodejs.org/

---

### Step 2: Navigate to Project

```bash
cd C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site
```

Verify you're there:
```bash
ls
```

You should see: `docs`, `src`, `package.json`, `docusaurus.config.js`, etc.

---

### Step 3: Install Dependencies (First Time Only)

```bash
npm install
```

This takes 2-3 minutes. Wait for it to finish.

You'll see at the end:
```
up to date, audited XX packages
```

---

### Step 4: Start Development Server

```bash
npm start
```

Wait for this message:
```
[SUCCESS] Docusaurus server is running on: http://localhost:3000
```

Browser should automatically open. If not:
- Manually go to: `http://localhost:3000`

---

### Step 5: Test Your Book!

Click around:
- Homepage
- Modules
- Chapters
- Navigation
- Search

---

## 📊 COMPREHENSIVE CHECKLIST

Print this and check boxes as you test:

### Navigation
- [ ] Sidebar shows all chapters
- [ ] Clicking sidebar items changes page
- [ ] Breadcrumbs at top (e.g., "Home > Module 1 > Chapter 1")
- [ ] Breadcrumb links work
- [ ] Previous/Next buttons appear at bottom
- [ ] Previous/Next buttons navigate correctly
- [ ] Home link works

### Content
- [ ] Chapter title displays
- [ ] Chapter text readable
- [ ] Code blocks show with dark background
- [ ] Code formatting looks right
- [ ] Images display (if any)
- [ ] Tables display correctly
- [ ] Lists display correctly
- [ ] Internal links work

### Search
- [ ] Search box visible (top right)
- [ ] Can type in search
- [ ] Results appear as dropdown
- [ ] Results are relevant
- [ ] Click result navigates to chapter

### Mobile
- [ ] F12 Developer Tools open
- [ ] Phone icon works
- [ ] iPhone 12 selected
- [ ] Text readable without horizontal scroll
- [ ] Menu icon appears
- [ ] Menu icon opens/closes sidebar
- [ ] Touch-friendly buttons

### Performance
- [ ] Homepage loads <2 seconds
- [ ] Chapter loads <1 second
- [ ] No lag when scrolling
- [ ] Clicking works instantly
- [ ] Search responds quickly

### Quality
- [ ] No red errors in Console (F12)
- [ ] No broken layout
- [ ] Colors look good
- [ ] Font sizes readable
- [ ] No missing content

---

## 🐛 FIXES FOR COMMON ISSUES

### Issue: "npm command not found"
```
Fix:
1. Download Node.js 20+ from nodejs.org
2. Install it
3. Restart terminal
```

### Issue: Port 3000 in use
```
Fix: Use different port
npm start -- --port 3001

Then access: http://localhost:3001
```

### Issue: "Cannot find module" error
```
Fix:
npm install
npm start
```

### Issue: Blank page / content missing
```
Fix:
npm run clear
npm start
```

### Issue: Styles look broken
```
Fix:
npm run clear && npm start
```

### Issue: Browser doesn't open automatically
```
Fix: Manually go to http://localhost:3000
```

---

## 📱 TESTING ON REAL PHONE/TABLET

1. Find your computer's IP address:
```bash
ipconfig
```
Look for IPv4 address (e.g., 192.168.1.5)

2. On your phone, go to:
```
http://192.168.1.5:3000
```

3. Test on your actual device

---

## 📊 PERFORMANCE CHECK

### Check page load time:
1. Press `F12` (Developer Tools)
2. Go to "Network" tab
3. Reload page (`Ctrl+R`)
4. Bottom left shows total time
5. Should be <2 seconds

### Check for errors:
1. Press `F12` (Developer Tools)
2. Go to "Console" tab
3. Look for red messages
4. Green/yellow are OK
5. Red errors need fixing

---

## 🎯 SUCCESS CRITERIA

Your book is ready when ALL these pass:

- ✅ All 22 chapters accessible
- ✅ Navigation works
- ✅ Search finds chapters
- ✅ Mobile view works
- ✅ No red console errors
- ✅ Pages load quickly
- ✅ Content displays correctly

---

## 🎓 TESTING SCENARIOS

### Scenario: First-Time User (5 min)
```
1. Open http://localhost:3000
2. See homepage
3. Click "Start Here"
4. Browse modules
5. Read a chapter
6. Use next/previous
7. Try search
✅ Everything works smoothly
```

### Scenario: Mobile Learner (3 min)
```
1. F12 → phone icon
2. Select iPhone 12
3. Navigate chapters
4. Use search
5. Verify readable
✅ Mobile works great
```

### Scenario: Keyboard User (3 min)
```
1. Tab through page
2. Navigate only with keyboard
3. Search with Ctrl+K
4. No mouse needed
✅ Accessible
```

---

## 🧪 WHAT TO LOOK FOR

### Good Signs ✅
- Chapters load instantly
- Text is readable
- Code looks formatted
- Navigation works
- Search finds things
- Mobile view works
- No console errors

### Bad Signs ❌
- Blank page
- Content cut off
- Text unreadable
- Links don't work
- Search broken
- Mobile broken
- Red console errors

---

## 🚀 AFTER TESTING

### If Everything Works ✅
```bash
# Stop server
Ctrl+C

# Build for deployment
npm run build

# Ready to deploy!
```

### If Issues Found ❌
```bash
# Note the issue
# Fix the code in docs/ folder
# Save the file
# Browser auto-reloads
# Test again
# Repeat until fixed
```

---

## 📞 COMMANDS CHEAT SHEET

```bash
# Navigate to project
cd C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site

# Install (first time)
npm install

# Start dev server
npm start

# Stop server
Ctrl+C

# Clear cache
npm run clear

# Build for production
npm run build

# Test production build
npm run serve

# Browser access
http://localhost:3000
```

---

## 💡 PRO TIPS

1. **Keep Developer Tools Open** while testing
   - Spot errors in real-time
   - Monitor performance

2. **Test Different Browsers**
   - Chrome, Firefox, Safari, Edge

3. **Test on Real Device**
   - Find IP address with ipconfig
   - Access from phone/tablet

4. **Use Hot Reload**
   - Make changes to docs/
   - Browser auto-reloads
   - No need to restart

5. **Share Link While Testing**
   - Get friends to test
   - Gather feedback
   - Real-world validation

---

## ✅ FINAL CHECKLIST

Before deployment:
- [ ] All chapters load
- [ ] Navigation works
- [ ] Search works
- [ ] Mobile works
- [ ] No console errors
- [ ] Performance is good
- [ ] Content looks great

---

## 🎉 YOU'RE READY!

**Execute this NOW:**

```bash
cd C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site && npm install && npm start
```

**Then tell me:**
1. Did it start successfully?
2. Does the homepage load?
3. Can you click chapters?
4. What do you see?

**Let's go! 🚀**
