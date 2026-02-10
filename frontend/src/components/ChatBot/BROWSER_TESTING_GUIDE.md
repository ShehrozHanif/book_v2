# Browser Testing Guide for ChatbotMessageRTL (T031)

## Overview

This guide provides comprehensive cross-browser testing procedures for the ChatbotMessageRTL component across Chrome, Firefox, Safari, and mobile browsers.

## Test Environment Setup

### Required Tools
- **Chrome**: Latest version (89+)
- **Firefox**: Latest version (63+)
- **Safari**: Latest version (15.4+)
- **Mobile Testing**:
  - iOS Safari on iPhone/iPad (iOS 14+)
  - Chrome on Android (latest)
  - Playwright or Cypress for automated testing

### Browser Capabilities Matrix

| Feature | Chrome | Firefox | Safari | Mobile |
|---------|--------|---------|--------|--------|
| CSS Direction (`dir`) | ✅ Full Support | ✅ Full Support | ✅ Full Support | ✅ Full Support |
| RTL Text Rendering | ✅ Full Support | ✅ Full Support | ✅ Full Support | ✅ Full Support |
| CSS Logical Properties | ✅ 89+ | ✅ 63+ | ✅ 15.4+ | ✅ Latest |
| unicode-bidi | ✅ Full Support | ✅ Full Support | ✅ Full Support | ✅ Full Support |
| Google Fonts | ✅ Full Support | ✅ Full Support | ✅ Full Support | ✅ Full Support |
| HTML Lang Attribute | ✅ Full Support | ✅ Full Support | ✅ Full Support | ✅ Full Support |

---

## Manual Testing Checklist

### 1. Text Direction & Alignment

#### Chrome
- [ ] Open browser DevTools (F12)
- [ ] Set language to Urdu via UI
- [ ] Verify `dir="rtl"` attribute in DOM
- [ ] Check computed style: `direction: rtl`
- [ ] Verify text aligns to the right
- [ ] Check text flows right-to-left

#### Firefox
- [ ] Repeat Chrome steps with Firefox
- [ ] Verify Inspector shows correct direction
- [ ] Check Computed Styles panel

#### Safari
- [ ] Open Safari Web Inspector (Cmd+Option+I)
- [ ] Repeat alignment checks
- [ ] Verify font rendering quality

#### Mobile
- [ ] Test on iOS Safari
- [ ] Test on Chrome Mobile
- [ ] Verify touch-friendly text sizing
- [ ] Check text wrapping on narrow viewport

### 2. Code Block Rendering

#### All Browsers
- [ ] Insert message with code block in English
- [ ] Switch to Urdu
- [ ] Verify code block remains visible
- [ ] Check code has `dir="ltr"` override
- [ ] Verify code text flows left-to-right
- [ ] Test long lines are horizontally scrollable
- [ ] Verify syntax highlighting still visible

#### Specific Tests
```
English Code:
def hello():
    print("Hello, World!")

Urdu Text with Code:
یہ پائتھن کوڈ ہے:
```python
def salam():
    print("السلام عليكم")
```

Expected Result:
- Code block flows left-to-right
- Urdu text flows right-to-left
- Code is readable with monospace font
- Proper spacing around code block
```

### 3. Font Rendering

#### Visual Inspection
- [ ] Urdu text appears with proper script
- [ ] No boxes or replacement characters
- [ ] Diacritic marks display correctly
- [ ] Font size is readable (16px minimum)

#### Font Cascade Testing
```
Expected Font Stack:
1. Noto Sans Urdu (Google Fonts)
2. Scheherazade (fallback)
3. Arial Unicode MS (fallback)
4. System fonts
```

### 4. Message Alignment

#### Assistant Messages (RTL)
- [ ] Background color applied correctly
- [ ] Border on right side (RTL context)
- [ ] Padding applied symmetrically
- [ ] Timestamp aligned correctly

#### User Messages (RTL)
- [ ] Maximum width constraint applied
- [ ] Alignment to right side
- [ ] Color scheme distinct from assistant
- [ ] Border position correct (right side)

### 5. Mobile Responsiveness

#### Viewport Tests
```
Breakpoints to test:
- 320px (iPhone SE)
- 375px (iPhone 12)
- 414px (iPhone 12 Pro Max)
- 768px (iPad)
- 1024px (iPad Pro)
```

#### Mobile Specific
- [ ] Messages fit viewport width
- [ ] Text wraps properly on narrow screens
- [ ] Code blocks are scrollable
- [ ] Touch targets are 44x44px minimum
- [ ] No horizontal scroll bar at root level
- [ ] Font size adequate for mobile reading

### 6. Dark Mode (if supported)

#### CSS Media Query: prefers-color-scheme
- [ ] Test in dark mode on all browsers
- [ ] Colors have sufficient contrast
- [ ] Text remains readable
- [ ] Code block background adjusted

### 7. Accessibility

#### Keyboard Navigation
- [ ] Can tab through messages
- [ ] Focus states visible
- [ ] Screen reader announces message content
- [ ] Lang attribute present

#### Screen Reader Testing (NVDA, JAWS, VoiceOver)
- [ ] Message role announced as "article"
- [ ] Language announced correctly (English/Urdu)
- [ ] Code blocks announced as code
- [ ] Citations announced as list

---

## Automated Testing

### Run Automated Tests

```bash
# Install dependencies
npm install

# Run cross-browser tests
npm run test:browser

# Run visual regression tests
npm run test:visual

# Run accessibility tests
npm run test:a11y
```

### Test Results Interpretation

#### Expected Results
```
✅ All tests passing on:
- Chrome 89+
- Firefox 63+
- Safari 15.4+
- iOS Safari 14+
- Chrome Mobile (latest)
```

#### Common Issues

**Issue**: Text doesn't align right in RTL
- **Cause**: `dir` attribute not applied
- **Fix**: Check ChatbotMessageRTL passes direction prop

**Issue**: Code block text is reversed
- **Cause**: `unicode-bidi` not applied
- **Fix**: Verify CSS `.code-block { unicode-bidi: bidi-override; }`

**Issue**: Urdu characters appear as boxes
- **Cause**: Font not loaded
- **Fix**: Check Google Fonts Noto Sans Urdu loaded

**Issue**: Mobile text too small
- **Cause**: Font size not responsive
- **Fix**: Check media queries in `chatbot-message-rtl.css`

---

## Performance Testing

### Metrics to Monitor

```
Time to Interactive (TTI): < 3s
Largest Contentful Paint (LCP): < 2.5s
Cumulative Layout Shift (CLS): < 0.1
```

### Test Rendering Performance

```javascript
// Measure render time
const start = performance.now();
// Switch language to Urdu
const end = performance.now();
console.log(`Render took ${end - start}ms`);
// Should be < 100ms
```

---

## Browser-Specific Notes

### Chrome
- Best RTL support
- DevTools excellent for debugging
- No known RTL rendering issues
- Font loading via Google Fonts reliable

### Firefox
- Excellent RTL support
- Inspector very helpful
- Consistent with Chrome behavior
- CSS Logical Properties fully supported

### Safari
- Strong RTL support (15.4+)
- Web Inspector similar to Chrome DevTools
- May require testing on actual macOS/iOS
- Font rendering slightly different (antialiasing)

### Mobile Browsers
- iOS Safari: Use Safari Technology Preview for development
- Chrome Mobile: Use Chrome DevTools Remote Debugging
- Test on real devices, not just emulators
- Touch interactions important to test

---

## Test Execution Plan

### Phase 1: Desktop Testing (Day 1)
- [ ] Chrome on Windows/Mac/Linux
- [ ] Firefox on Windows/Mac/Linux
- [ ] Safari on macOS

### Phase 2: Mobile Testing (Day 2)
- [ ] iOS Safari on iPhone
- [ ] Chrome on Android phone
- [ ] iPad and larger tablets

### Phase 3: Edge Cases (Day 3)
- [ ] Mixed English/Urdu content
- [ ] Very long messages
- [ ] Messages with code blocks
- [ ] Messages with lists
- [ ] Dark mode testing

### Phase 4: Performance Testing (Day 4)
- [ ] Load testing with many messages
- [ ] Memory usage monitoring
- [ ] Font loading timing
- [ ] Re-render performance

---

## Sign-Off Checklist

### Desktop Browsers
- [ ] Chrome: Text direction ✅ | Code blocks ✅ | Spacing ✅ | Fonts ✅
- [ ] Firefox: Text direction ✅ | Code blocks ✅ | Spacing ✅ | Fonts ✅
- [ ] Safari: Text direction ✅ | Code blocks ✅ | Spacing ✅ | Fonts ✅

### Mobile Browsers
- [ ] iOS Safari: Layout ✅ | Touch ✅ | Performance ✅
- [ ] Chrome Mobile: Layout ✅ | Touch ✅ | Performance ✅

### Accessibility
- [ ] Screen reader compatible ✅
- [ ] Keyboard navigation works ✅
- [ ] Color contrast adequate ✅
- [ ] Focus states visible ✅

### Performance
- [ ] TTI < 3s ✅
- [ ] LCP < 2.5s ✅
- [ ] CLS < 0.1 ✅
- [ ] Font loading smooth ✅

---

## Reporting Issues

When you find a browser-specific issue:

1. **Document the Issue**
   - Browser and version
   - Operating system
   - Viewport size
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/video

2. **Create a Test Case**
   - Minimal reproducible example
   - Code snippet
   - Console errors (if any)

3. **Check Workarounds**
   - Browser-specific CSS
   - Polyfills needed
   - Vendor prefixes

---

## References

- [MDN: CSS direction property](https://developer.mozilla.org/en-US/docs/Web/CSS/direction)
- [MDN: HTML lang attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/lang)
- [MDN: CSS Logical Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Logical_Properties)
- [W3C: RTL Structural Markup](https://www.w3.org/International/questions/qa-html-dir)
- [Google Fonts: Noto Sans Urdu](https://fonts.google.com/?query=noto+sans+urdu)

---

## Appendix: Test Data

### Sample Urdu Text
```
السلام عليكم ورحمة الله وبركاته

یہ ایک ٹیسٹ ہے۔
یہاں اردو متن آتا ہے۔
کوڈ بھی شامل ہے۔
```

### Sample Code Blocks
```python
# Python example
def hello_urdu():
    message = "السلام عليكم"
    print(message)

# Mixed content
greeting_urdu = "السلام عليكم"
greeting_english = "Hello"
```

### Sample Mixed Content
```html
<p>
  یہ English word والا Urdu text ہے۔
  This Urdu میں English ہے۔
</p>
```

---

**Last Updated**: 2025-02-10
**Test Coverage**: 25+ test cases
**Expected Pass Rate**: 100% on supported browsers
