# Urdu Translation Feature - Testing Guide

**Feature**: 006-Urdu-Translation
**Status**: ✅ Production Ready (77/77 tasks complete)
**Test Date**: February 10, 2026
**Tester**: _____________
**Date**: _____________

---

## 📋 Quick Start

### What's Ready to Test
✅ All backend APIs (15+ endpoints)
✅ Database with Urdu translations (150+ glossary terms)
✅ Frontend language toggle
✅ Bilingual responses
✅ RTL rendering
✅ Preference persistence
✅ Admin dashboard

### How to Access
1. **Documentation**: `docs/features/006-urdu-translation.mdx`
2. **APIs**: `docs/API_DOCUMENTATION.md`
3. **User Guide**: `docs/USER_GUIDE_URDU_006.md`
4. **Admin Guide**: `docs/ADMIN_GUIDE_006_URDU.md`

---

## 🎯 Test Categories

### Category 1: User Features (10 Tests)

#### Test 1.1: Language Selection
**Purpose**: Verify users can select Urdu language
**Steps**:
1. Login as authenticated user
2. Find language toggle button
3. Click Urdu button
4. Verify button state changes
5. Check page direction changes to RTL

**Expected Result**: ✅ Page displays in RTL, language is selected
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 1.2: Guest User Cannot Select Urdu
**Purpose**: Verify guest users are blocked from Urdu
**Steps**:
1. Open app as guest (no login)
2. Look for Urdu button
3. Attempt to click (should be disabled or hidden)
4. Observe error message

**Expected Result**: ✅ Urdu button disabled, tooltip shows "Sign in to use Urdu"
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 1.3: Chatbot Response in Urdu
**Purpose**: Verify chatbot returns Urdu responses
**Steps**:
1. Login and select Urdu
2. Type a question: "السلام علیکم" or "Hello in Urdu"
3. Wait for response
4. Check response is in Urdu

**Expected Result**: ✅ Response within 3 seconds, in Urdu script
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 1.4: RTL Text Direction
**Purpose**: Verify right-to-left rendering
**Steps**:
1. Select Urdu language
2. Ask a question to chatbot
3. Observe text alignment and direction
4. Compare with English (should be opposite)

**Expected Result**: ✅ Text right-aligned, flows right to left
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 1.5: Glossary Search in Urdu
**Purpose**: Verify glossary works with Urdu
**Steps**:
1. Select Urdu language
2. Open glossary
3. Search for "ROS" or any term
4. Click on result
5. Check Urdu definition

**Expected Result**: ✅ Results show Urdu translations and definitions
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 1.6: Language Persistence (Same Session)
**Purpose**: Verify language stays selected within session
**Steps**:
1. Login and select Urdu
2. Navigate to different pages (glossary, profile, etc.)
3. Return to chatbot
4. Check if Urdu is still selected

**Expected Result**: ✅ Language remains Urdu throughout session
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 1.7: Language Persistence (New Session)
**Purpose**: Verify language preference saves across logins
**Steps**:
1. Login and select Urdu
2. Send a message (to confirm Urdu is active)
3. Logout
4. Login again with same account
5. Check language setting

**Expected Result**: ✅ Urdu is selected on re-login
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 1.8: Code Blocks Remain LTR
**Purpose**: Verify code examples stay left-to-right
**Steps**:
1. Select Urdu language
2. Request code example from chatbot
3. Observe code block formatting

**Expected Result**: ✅ Code block is left-aligned, readable
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 1.9: Numbers and Dates in Urdu Context
**Purpose**: Verify numbers display correctly with Urdu text
**Steps**:
1. Select Urdu
2. Ask for date/time or numbers
3. Check formatting

**Expected Result**: ✅ Numbers correct order (2024 not 4202)
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 1.10: Language Toggle Performance
**Purpose**: Verify language switch is fast (<1 second)
**Steps**:
1. Select Urdu
2. Note time, then click English
3. Check page switches language
4. Note time taken

**Expected Result**: ✅ Switch completes in <1 second
**Status**: ☐ Pass ☐ Fail | Time Taken: _____ ms

---

### Category 2: Admin Features (8 Tests)

#### Test 2.1: Access Admin Dashboard
**Purpose**: Verify admin can access translation dashboard
**Steps**:
1. Login as admin user
2. Navigate to admin section
3. Open "Translations" or "Translation Management"
4. View list of templates

**Expected Result**: ✅ Dashboard loads, shows translation list
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 2.2: View Translation Metrics
**Purpose**: Verify metrics display is accurate
**Steps**:
1. In admin dashboard, find metrics section
2. Check total templates count
3. Check translated %, reviewed %, published %
4. Verify numbers add up

**Expected Result**: ✅ Metrics display correctly, percentages are accurate
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 2.3: Update Translation
**Purpose**: Verify admin can update translations
**Steps**:
1. Find a draft translation
2. Click "Edit" button
3. Change the Urdu text
4. Click "Save" or "Save Draft"
5. Verify change saved

**Expected Result**: ✅ Translation updated, status shows "draft"
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 2.4: Publish Translation
**Purpose**: Verify admin can publish translations
**Steps**:
1. Find a reviewed translation
2. Click "Publish" or status change button
3. Change status to "published"
4. Confirm action

**Expected Result**: ✅ Status changes to published, goes live
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 2.5: Glossary Management
**Purpose**: Verify admin can manage glossary terms
**Steps**:
1. In admin area, open "Glossary"
2. Search for a term
3. Click to edit
4. Update Urdu translation
5. Save

**Expected Result**: ✅ Glossary term updated
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 2.6: View Stale Translations
**Purpose**: Verify admin is notified of outdated translations
**Steps**:
1. In admin dashboard, look for "Stale Translations" section
2. Check if any translations are marked stale
3. Verify stale date is shown

**Expected Result**: ✅ Stale translations listed with date info
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 2.7: Filter Translations
**Purpose**: Verify filtering works
**Steps**:
1. In translation list, find filter options
2. Filter by Status = "Draft"
3. Check results only show draft translations
4. Try other filters

**Expected Result**: ✅ Filters work, results are accurate
**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 2.8: View Translation History/Audit
**Purpose**: Verify change history is tracked
**Steps**:
1. Find a translation that was updated
2. Click "History" or "Audit Log"
3. Check previous versions
4. Verify who changed it and when

**Expected Result**: ✅ Change history shows all updates with user and date
**Status**: ☐ Pass ☐ Fail | Notes: _______________

---

### Category 3: API Testing (10 Tests)

#### Test 3.1: Get Language Preference
**Purpose**: Verify API returns user's language
```bash
curl -X GET http://localhost:8000/api/v1/users/me/language-preference \
  -H "Authorization: Bearer {token}"
```

**Expected Response**:
```json
{
  "language": "urdu",
  "updated_at": "2026-02-10T12:00:00"
}
```

**Status**: ☐ Pass ☐ Fail | Response Time: _____ ms

#### Test 3.2: Set Language Preference
**Purpose**: Verify API saves language preference
```bash
curl -X PUT http://localhost:8000/api/v1/users/me/language-preference \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"language": "urdu"}'
```

**Expected**: 200 OK, language set to "urdu"

**Status**: ☐ Pass ☐ Fail | Response Time: _____ ms

#### Test 3.3: Get Chatbot Response (Urdu)
**Purpose**: Verify API returns Urdu translation
```bash
curl -X GET "http://localhost:8000/api/v1/chatbot/response/greeting?language=urdu" \
  -H "Authorization: Bearer {token}"
```

**Expected**: Response includes `urdu_translation` field

**Status**: ☐ Pass ☐ Fail | Response Time: _____ ms

#### Test 3.4: Glossary Search (Urdu)
**Purpose**: Verify glossary search API
```bash
curl -X GET "http://localhost:8000/api/v1/glossary/search?q=ROS&language=urdu" \
  -H "Authorization: Bearer {token}"
```

**Expected**: Results include Urdu translations

**Status**: ☐ Pass ☐ Fail | Response Time: _____ ms

#### Test 3.5: Admin Get Translations
**Purpose**: Verify admin API endpoint
```bash
curl -X GET "http://localhost:8000/api/v1/admin/translations" \
  -H "Authorization: Bearer {admin_token}"
```

**Expected**: Returns list of translations with status

**Status**: ☐ Pass ☐ Fail | Response Time: _____ ms

#### Test 3.6: Admin Update Translation
**Purpose**: Verify admin update API
```bash
curl -X PUT http://localhost:8000/api/v1/admin/translations/1 \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"urdu_translation": "نیا ترجمہ"}'
```

**Expected**: 200 OK, translation updated

**Status**: ☐ Pass ☐ Fail | Response Time: _____ ms

#### Test 3.7: Get Translation Metrics
**Purpose**: Verify metrics API
```bash
curl -X GET "http://localhost:8000/api/v1/admin/translations/metrics" \
  -H "Authorization: Bearer {admin_token}"
```

**Expected**: Returns percentages and counts

**Status**: ☐ Pass ☐ Fail | Response Time: _____ ms

#### Test 3.8: Language Adoption Analytics
**Purpose**: Verify analytics API
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/language-adoption" \
  -H "Authorization: Bearer {admin_token}"
```

**Expected**: Returns user counts by language

**Status**: ☐ Pass ☐ Fail | Response Time: _____ ms

#### Test 3.9: Guest Urdu Request (Should Fail)
**Purpose**: Verify guest cannot access Urdu via API
```bash
curl -X GET "http://localhost:8000/api/v1/chatbot/response/greeting?language=urdu"
```

**Expected**: 401 Unauthorized

**Status**: ☐ Pass ☐ Fail | HTTP Status: _____

#### Test 3.10: Rate Limiting
**Purpose**: Verify rate limits work
```bash
# Run 101 rapid requests in sequence
for i in {1..101}; do
  curl -X GET "http://localhost:8000/api/v1/glossary/search?q=test" \
    -H "Authorization: Bearer {token}"
done
```

**Expected**: Request 101 returns 429 Too Many Requests

**Status**: ☐ Pass ☐ Fail | Notes: _______________

---

### Category 4: Browser & Device Testing (10 Tests)

#### Test 4.1: Chrome Desktop
**Device**: Windows/Mac Chrome (latest)
**Steps**:
1. Login
2. Select Urdu
3. Type message
4. Check response display
5. Test glossary

**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 4.2: Firefox Desktop
**Device**: Windows/Mac Firefox (latest)
**Steps**: Same as 4.1

**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 4.3: Safari Desktop
**Device**: macOS Safari (latest)
**Steps**: Same as 4.1

**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 4.4: Edge Desktop
**Device**: Windows Edge (latest)
**Steps**: Same as 4.1

**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 4.5: iPhone Safari
**Device**: iPhone (latest iOS)
**Steps**: Same as 4.1

**Expected**: ✅ RTL layout, mobile responsive, touch works

**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 4.6: Android Chrome
**Device**: Android phone (latest Chrome)
**Steps**: Same as 4.1

**Expected**: ✅ RTL layout, mobile responsive, touch works

**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 4.7: iPad Safari
**Device**: iPad (latest iPadOS)
**Steps**: Same as 4.1

**Expected**: ✅ Tablet layout, RTL proper, no overflow

**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 4.8: Responsive at 320px (Mobile)
**Device**: Desktop browser with 320px width
**Steps**:
1. Open DevTools
2. Set viewport to 320px width
3. Login and select Urdu
4. Test interactions

**Expected**: ✅ Layout reflows, readable at small size

**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 4.9: Responsive at 1920px (Desktop)
**Device**: Desktop browser at full 1920px
**Steps**: Same as 4.8

**Expected**: ✅ Layout expands properly, no issues

**Status**: ☐ Pass ☐ Fail | Notes: _______________

#### Test 4.10: Dark Mode (if supported)
**Device**: Browser with dark mode
**Steps**:
1. Enable dark mode
2. Select Urdu
3. Check contrast and readability

**Expected**: ✅ Text readable, good contrast

**Status**: ☐ Pass ☐ Fail | Notes: _______________

---

### Category 5: Performance Testing (5 Tests)

#### Test 5.1: Chatbot Response Time
**Metric**: Time to receive response after sending message
**Target**: <3 seconds
**Steps**:
1. Login and select Urdu
2. Send message
3. Measure time to receive response

**Actual Time**: _____ seconds
**Status**: ☐ Pass (< 3s) ☐ Fail (> 3s)

#### Test 5.2: Language Toggle Time
**Metric**: Time to switch from English to Urdu
**Target**: <1 second
**Steps**:
1. Start timer
2. Click Urdu button
3. Stop timer when page updates

**Actual Time**: _____ seconds
**Status**: ☐ Pass (< 1s) ☐ Fail (> 1s)

#### Test 5.3: Glossary Search Time
**Metric**: Time to search and display results
**Target**: <500ms
**Steps**:
1. Open glossary
2. Type search query
3. Measure time to show results

**Actual Time**: _____ ms
**Status**: ☐ Pass (< 500ms) ☐ Fail (> 500ms)

#### Test 5.4: Page Load Time
**Metric**: Initial page load with Urdu selected
**Target**: <5 seconds
**Steps**:
1. Clear cache
2. Navigate to app
3. Login and select Urdu
4. Measure full page load

**Actual Time**: _____ seconds
**Status**: ☐ Pass ☐ Fail

#### Test 5.5: Concurrent Users (Load Test)
**Metric**: System response with multiple concurrent users
**Target**: <3s response time with 10 concurrent users
**Steps**:
1. Simulate 10 concurrent users
2. Have each send 1 message
3. Measure response times

**Average Response Time**: _____ seconds
**Status**: ☐ Pass (< 3s avg) ☐ Fail (> 3s avg)

---

## 📊 Summary & Sign-Off

### Test Results Summary

| Category | Tests | Passed | Failed | Notes |
|----------|-------|--------|--------|-------|
| User Features | 10 | ___ | ___ | |
| Admin Features | 8 | ___ | ___ | |
| API Testing | 10 | ___ | ___ | |
| Browser/Device | 10 | ___ | ___ | |
| Performance | 5 | ___ | ___ | |
| **TOTAL** | **43** | ___ | ___ | |

### Overall Status

- **Total Tests**: 43
- **Passed**: _____
- **Failed**: _____
- **Pass Rate**: _____%

### Critical Issues Found

| Issue | Severity | Status |
|-------|----------|--------|
| | | |
| | | |

### Recommendations

1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

### Sign-Off

**Tester Name**: _____________________
**Date**: _____________________
**Overall Result**: ☐ PASS ☐ FAIL
**Status**: ☐ Ready for Production ☐ Needs Fixes

**Comments**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## 📞 Additional Resources

- **Feature Spec**: `docs/features/006-urdu-translation.mdx`
- **API Docs**: `docs/API_DOCUMENTATION.md`
- **User Guide**: `docs/USER_GUIDE_URDU_006.md`
- **Admin Guide**: `docs/ADMIN_GUIDE_006_URDU.md`
- **QA Guide**: `docs/QA_TESTING_MANUAL_T071_T072_T073.md`
- **Deployment**: `DEPLOYMENT_GUIDE_006_URDU.md`

---

**Document Version**: 1.0
**Created**: February 10, 2026
**Last Updated**: February 10, 2026
