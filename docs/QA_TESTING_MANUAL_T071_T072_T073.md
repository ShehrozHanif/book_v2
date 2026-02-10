# Manual QA Testing Guide - Urdu Translation Feature (T071-T073)

## Overview

This document contains comprehensive manual QA testing procedures for the Urdu translation feature covering:
- **T071**: RTL rendering across browsers
- **T072**: Urdu font rendering quality
- **T073**: Authentication gate and preference persistence

---

## T071: RTL Rendering Across Browsers

### Objective
Verify that Urdu content displays correctly with Right-to-Left (RTL) text direction across all major browsers and devices.

### Test Environment Setup

**Browser Versions to Test**:
- Chrome/Chromium: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions (macOS)
- Mobile Chrome (Android): Latest version
- Mobile Safari (iOS): Latest version

**Test Data**:
- Short text: "السلام علیکم"
- Medium text: "مرحبا بك في تطبيق الدردشة الآلية"
- Long text: "السلام علیکم، میں آپ کی کیا مدد کر سکتا ہوں؟ یہ ایک مثال ہے جو بتاتا ہے کہ اردو متن کیسے صحیح طریقے سے دکھایا جائے۔"

### Test Cases

#### T071.1: Basic RTL Direction on Desktop

**Steps**:
1. Login to the application as authenticated user
2. Select Urdu language from language toggle
3. Send a message in Urdu to chatbot
4. Observe response text direction

**Expected Results**:
- [ ] Text is right-aligned (starts from right side)
- [ ] Text flows from right to left naturally
- [ ] No horizontal scrollbars appear
- [ ] Text doesn't overflow container

**Browsers to Test**:
- [ ] Chrome (Windows)
- [ ] Chrome (macOS)
- [ ] Firefox (Windows)
- [ ] Firefox (macOS)
- [ ] Safari (macOS)

**Status**: ______

#### T071.2: RTL with Code Blocks

**Steps**:
1. In Urdu mode, trigger a response containing code blocks
2. Example code block:
   ```
   print("Hello")
   ```
3. Observe code block formatting

**Expected Results**:
- [ ] Urdu text remains right-aligned
- [ ] Code block remains left-aligned (LTR)
- [ ] Clear visual distinction between Urdu and code
- [ ] Code is syntax-highlighted properly
- [ ] No misalignment between RTL and LTR content

**Browsers to Test**:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari

**Status**: ______

#### T071.3: RTL with Numbers and Dates

**Steps**:
1. Select Urdu language
2. Ask for dates/numbers: "اج کی تاریخ کیا ہے؟" (What's today's date?)
3. Observe response with mixed Urdu text and English numbers/dates

**Expected Results**:
- [ ] Urdu text is right-aligned
- [ ] Numbers appear in correct position (2024 not 4202)
- [ ] Dates are readable and in correct order
- [ ] Mixed RTL/LTR content is properly separated
- [ ] No overlapping between text and numbers

**Browsers to Test**:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari

**Status**: ______

#### T071.4: Mobile RTL Rendering (iOS)

**Steps**:
1. Open application on iPad/iPhone (Safari)
2. Login and select Urdu
3. Send Urdu message and observe response
4. Test at different viewport sizes (portrait and landscape)

**Expected Results**:
- [ ] Text is right-aligned on mobile
- [ ] Content doesn't exceed screen width
- [ ] No horizontal scrolling required
- [ ] Touch interactions work properly
- [ ] Text remains readable at all sizes

**Devices to Test**:
- [ ] iPhone 12/13 (Safari)
- [ ] iPhone 14/15 (Safari)
- [ ] iPad (Safari)

**Status**: ______

#### T071.5: Mobile RTL Rendering (Android)

**Steps**:
1. Open application on Android device (Chrome)
2. Login and select Urdu
3. Send Urdu message and observe response
4. Test at different viewport sizes

**Expected Results**:
- [ ] Text is right-aligned on mobile
- [ ] Content fits within screen
- [ ] No horizontal scrolling required
- [ ] All controls are properly aligned
- [ ] Gestures work correctly

**Devices to Test**:
- [ ] Samsung Galaxy S22+ (Chrome)
- [ ] Google Pixel 7 (Chrome)
- [ ] OnePlus 11 (Chrome)

**Status**: ______

#### T071.6: RTL in Glossary Modal

**Steps**:
1. Select Urdu language
2. Open glossary
3. Search for term (e.g., "ROS")
4. View term details with Urdu content

**Expected Results**:
- [ ] Glossary modal uses RTL layout
- [ ] Urdu terms are right-aligned
- [ ] Definition text is right-aligned
- [ ] Examples are properly formatted
- [ ] Close button position is appropriate

**Browsers to Test**:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari

**Status**: ______

#### T071.7: RTL in Notifications

**Steps**:
1. Select Urdu language
2. Trigger notifications (e.g., admin notification)
3. Observe notification display

**Expected Results**:
- [ ] Notification text is right-aligned
- [ ] Close button is on left side
- [ ] Notification fits within viewport
- [ ] Multiple notifications stack properly
- [ ] RTL direction doesn't affect close functionality

**Status**: ______

#### T071.8: RTL Direction Switching

**Steps**:
1. Start with English language selected
2. Send message and observe direction
3. Switch to Urdu
4. Send message and observe direction
5. Switch back to English

**Expected Results**:
- [ ] Direction changes correctly: English (LTR) → Urdu (RTL)
- [ ] Old messages maintain their original direction
- [ ] New messages use current language direction
- [ ] No layout breaking occurs
- [ ] Conversation history is properly maintained

**Browsers to Test**:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari

**Status**: ______

---

## T072: Urdu Font Rendering Quality

### Objective
Verify that Urdu fonts render correctly with proper character spacing, shaping, and no text reflow issues.

### Font Configuration

**Expected Fonts**:
- Primary: Noto Naskh Arabic (from Google Fonts)
- Fallback 1: Droid Arabic Naskh
- Fallback 2: Arial Unicode MS
- System Fallback: Device Urdu fonts

### Test Cases

#### T072.1: Basic Character Rendering

**Test Strings**:
- Simple: "آبجد"
- Word: "السلام"
- Sentence: "السلام علیکم، میں آپ کی کیا مدد کر سکتا ہوں؟"

**Steps**:
1. Select Urdu language
2. Ask chatbot a question that returns above text
3. Inspect character rendering closely

**Expected Results**:
- [ ] All characters display correctly (no boxes or ??)
- [ ] Characters are not cut off
- [ ] Diacritical marks display above/below letters correctly
- [ ] No character corruption visible
- [ ] Text is crisp and readable (not blurry)

**Browsers to Test**:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari

**Status**: ______

#### T072.2: Character Spacing and Shaping

**Test Strings**:
- "ن و ں" (different n forms)
- "ی ے" (different y forms)
- "ا آ ؤ" (different alif forms)

**Steps**:
1. Trigger responses containing these character variations
2. Inspect spacing between characters
3. Verify connected vs standalone characters display properly

**Expected Results**:
- [ ] Connected characters are properly joined (no gaps)
- [ ] Standalone characters are not incorrectly joined
- [ ] Character width is consistent
- [ ] No overlapping between adjacent characters
- [ ] Proper spacing around diacritical marks

**Browsers to Test**:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari

**Status**: ______

#### T072.3: Ligatures and Complex Shapes

**Test Strings**:
- "لا" (lam-alif ligature)
- "لله" (lam-lam-ha complex)
- "السلام" (complex word with multiple shapes)

**Steps**:
1. Select Urdu and view text with ligatures
2. Compare character shaping across browsers
3. Verify ligatures are properly formed

**Expected Results**:
- [ ] Ligatures render correctly where needed
- [ ] Complex shapes are properly connected
- [ ] No breaking of connected forms
- [ ] Consistent rendering across browsers
- [ ] Special forms (initial, medial, final) display correctly

**Browsers to Test**:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari

**Status**: ______

#### T072.4: Responsive Text Sizing

**Steps**:
1. Select Urdu language
2. Set browser zoom to 75%
3. Observe text rendering quality
4. Set zoom to 100% (normal)
5. Set zoom to 150%
6. Set zoom to 200%

**Expected Results**:
- [ ] Text remains readable at all zoom levels
- [ ] No font degradation at any size
- [ ] Character shaping is maintained
- [ ] No unexpected text reflow
- [ ] Line height is appropriate at all sizes

**Status**: ______

#### T072.5: Font Loading Performance

**Steps**:
1. Open DevTools Network tab
2. Select Urdu language (forces font download)
3. Monitor font file loading
4. Clear cache and repeat

**Expected Results**:
- [ ] Fonts load from CDN within 2 seconds
- [ ] Text appears before fonts fully load (graceful fallback)
- [ ] No FOUT (Flash of Unstyled Text)
- [ ] No FOIT (Flash of Invisible Text) longer than 3 seconds
- [ ] Fallback fonts are readable

**Browsers to Test**:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari

**Status**: ______

#### T072.6: Mobile Font Rendering

**Steps**:
1. Open app on iPhone (Safari)
2. Select Urdu language
3. View different text sizes
4. Pinch-to-zoom and observe

**Expected Results**:
- [ ] Fonts render clearly on small screen
- [ ] Characters remain connected properly
- [ ] No pixelation or blurriness
- [ ] Zoom doesn't break text shaping
- [ ] Readable at all mobile zoom levels

**Devices to Test**:
- [ ] iPhone (Safari)
- [ ] Android (Chrome)

**Status**: ______

#### T072.7: Text Reflow on Content Change

**Steps**:
1. Select Urdu language
2. Send short message: "سلام"
3. Send longer message: "یہ ایک طویل پیغام ہے جو متعدد لائنوں پر پھیلے گا"
4. Send message with numbers: "میری عمر 25 سال ہے"
5. Observe layout changes

**Expected Results**:
- [ ] Text wraps correctly (no overflow)
- [ ] No sudden layout jumps
- [ ] Line heights are consistent
- [ ] No text gets cut off
- [ ] Numbers don't cause reflow issues

**Browsers to Test**:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari

**Status**: ______

#### T072.8: Special Characters and Symbols

**Test Strings**:
- Quotation marks: "قالوا"
- Punctuation: "کیا؟ ہاں!"
- Numbers in Urdu: "١٢٣٤٥"
- Currency: "روپے ۔ $"

**Steps**:
1. View responses containing these characters
2. Verify each renders correctly
3. Check spacing around special characters

**Expected Results**:
- [ ] Arabic/Urdu quotation marks render correctly
- [ ] Punctuation is positioned properly
- [ ] Urdu numerals display when appropriate
- [ ] Currency symbols don't cause misalignment
- [ ] Special spacing rules are applied

**Status**: ______

---

## T073: Authentication Gate and Preference Persistence

### Objective
Verify that authentication gate prevents unauthorized Urdu access and language preferences persist across sessions and devices.

### Test Cases

#### T073.1: Guest Cannot Select Urdu

**Steps**:
1. Open application WITHOUT logging in
2. Locate language selector
3. Attempt to click Urdu button
4. Try to send message and request Urdu response

**Expected Results**:
- [ ] Urdu button is disabled or hidden for guests
- [ ] Tooltip/message indicates "Sign in to use Urdu"
- [ ] Clicking disabled button has no effect
- [ ] No Urdu content is served to unauthenticated users
- [ ] Guest receives English response only

**Status**: ______

#### T073.2: Guest Redirects to Login on Urdu Request

**Steps**:
1. Open application as guest
2. Try to directly request Urdu via query parameter: `?language=urdu`
3. Observe application behavior

**Expected Results**:
- [ ] Application redirects to login page
- [ ] OR shows login modal
- [ ] OR displays 401 error with login prompt
- [ ] User must authenticate to proceed with Urdu
- [ ] No Urdu content is exposed

**Status**: ______

#### T073.3: Authenticated User Can Select Urdu

**Steps**:
1. Login with valid credentials
2. Locate language selector
3. Click Urdu button

**Expected Results**:
- [ ] Urdu button is enabled and clickable
- [ ] Language immediately switches to Urdu
- [ ] UI elements change to RTL direction
- [ ] API call is made to set preference
- [ ] No errors occur

**Status**: ______

#### T073.4: Preference Persists Within Session

**Steps**:
1. Login and select Urdu
2. Navigate to different pages (Glossary, Profile, Settings)
3. Return to chatbot
4. Send message

**Expected Results**:
- [ ] Language remains Urdu throughout session
- [ ] All pages use Urdu when available
- [ ] No re-authentication required
- [ ] Preference is consistent across app

**Status**: ______

#### T073.5: Preference Persists Across Sessions

**Steps**:
1. Login and select Urdu
2. Send a message (verify Urdu response)
3. Logout
4. Login again with same account
5. Return to chatbot

**Expected Results**:
- [ ] Language is still set to Urdu
- [ ] No need to re-select language
- [ ] Preference was saved to server
- [ ] API retrieves preference correctly on login

**Status**: ______

#### T073.6: Preference Persists in Incognito/Private Mode

**Steps**:
1. Open incognito/private browser window
2. Login to application
3. Select Urdu language
4. Refresh page
5. Logout and close incognito window
6. Open new incognito window, login again

**Expected Results**:
- [ ] Preference is fetched from server (not localStorage if cleared)
- [ ] OR preference is stored in server session
- [ ] Language is still Urdu on new incognito session
- [ ] No data persists from previous incognito session except server preference

**Status**: ______

#### T073.7: Cross-Device Preference Persistence

**Steps**:
1. On Desktop: Login and select Urdu
2. On Mobile: Login with same account
3. Check language setting on mobile

**Expected Results**:
- [ ] Mobile shows Urdu as selected language
- [ ] Preference synced across devices
- [ ] Both devices show consistent language
- [ ] API returns correct preference for all devices

**Status**: ______

#### T073.8: Preference Overrides Default on Login

**Steps**:
1. Set browser language to Arabic
2. Application default is English
3. Login (user previously selected Urdu)
4. Observe initial language

**Expected Results**:
- [ ] Language is Urdu (user preference)
- [ ] NOT browser language (Arabic)
- [ ] NOT application default (English)
- [ ] User preference takes highest priority

**Status**: ______

#### T073.9: Role-Based Access Control

**Steps**:
1. Login as Student and select Urdu
2. Access all available features (should work)
3. Logout and login as Admin
4. Select Urdu and access admin features

**Expected Results**:
- [ ] Both student and admin can use Urdu
- [ ] Preference is stored per user, not per role
- [ ] All roles can authenticate for Urdu
- [ ] No role-based Urdu restrictions (only auth required)

**Status**: ______

#### T073.10: Preference Reset Functionality

**Steps**:
1. Select Urdu language
2. Click "Reset to Default" or similar option (if available)
3. Observe language change

**Expected Results**:
- [ ] Language resets to English (default)
- [ ] Preference is updated in database
- [ ] On next login, English is selected
- [ ] Reset persists across sessions

**Status**: ______

---

## Summary and Sign-Off

### Testing Checklist

**T071 - RTL Rendering** (8 test cases):
- [ ] Basic RTL direction (all browsers)
- [ ] RTL with code blocks
- [ ] RTL with numbers/dates
- [ ] Mobile RTL (iOS)
- [ ] Mobile RTL (Android)
- [ ] RTL in glossary
- [ ] RTL in notifications
- [ ] RTL direction switching

**T072 - Font Rendering** (8 test cases):
- [ ] Basic character rendering
- [ ] Character spacing and shaping
- [ ] Ligatures and complex shapes
- [ ] Responsive text sizing
- [ ] Font loading performance
- [ ] Mobile font rendering
- [ ] Text reflow on content change
- [ ] Special characters and symbols

**T073 - Auth Gate & Persistence** (10 test cases):
- [ ] Guest cannot select Urdu
- [ ] Guest redirects to login on Urdu request
- [ ] Authenticated user can select Urdu
- [ ] Preference persists within session
- [ ] Preference persists across sessions
- [ ] Preference persists in incognito/private
- [ ] Cross-device preference persistence
- [ ] Preference overrides default on login
- [ ] Role-based access control
- [ ] Preference reset functionality

**Total Test Cases**: 26
**Pass Rate**: ______ %

### Issues Found

| ID | Description | Severity | Browser/Device | Resolution |
|----|-------------|----------|---|---|
| | | | | |

### Sign-Off

**QA Tester**: _________________ **Date**: __________

**Sign-Off**: ☐ All tests passed, feature ready for production
        ☐ Some tests failed, see issues above
        ☐ Critical issues found, feature NOT ready

**Comments**: _________________________________________________________________
