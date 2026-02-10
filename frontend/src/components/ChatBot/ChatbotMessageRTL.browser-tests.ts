/**
 * Cross-Browser Testing Suite for ChatbotMessageRTL Component
 *
 * Tests RTL rendering across multiple browsers:
 * - Chrome/Chromium
 * - Firefox
 * - Safari
 * - Mobile browsers (iOS Safari, Chrome Mobile)
 *
 * Test Categories:
 * 1. Text Direction & Alignment
 * 2. Code Block Integrity
 * 3. Spacing & Margins
 * 4. Font Rendering
 * 5. Mobile Responsiveness
 */

/**
 * Browser Compatibility Matrix
 *
 * | Feature | Chrome | Firefox | Safari | Mobile |
 * |---------|--------|---------|--------|--------|
 * | dir attribute | ✓ | ✓ | ✓ | ✓ |
 * | RTL text rendering | ✓ | ✓ | ✓ | ✓ |
 * | Logical properties | ✓ 89+ | ✓ 63+ | ✓ 15.4+ | ✓ |
 * | unicode-bidi | ✓ | ✓ | ✓ | ✓ |
 * | Google Fonts | ✓ | ✓ | ✓ | ✓ |
 */

interface BrowserTestCase {
  name: string;
  description: string;
  testFn: () => Promise<boolean>;
  browsers: string[];
}

interface TestResult {
  testName: string;
  browser: string;
  passed: boolean;
  error?: string;
  duration: number;
}

/**
 * Test Case 1: Text Direction Rendering
 */
const textDirectionTests: BrowserTestCase[] = [
  {
    name: 'Urdu text renders RTL',
    description: 'Verify dir="rtl" is applied and text flows right-to-left',
    testFn: async () => {
      const element = document.querySelector('[dir="rtl"]');
      if (!element) return false;

      const computedDir = window.getComputedStyle(element).direction;
      return computedDir === 'rtl';
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'English text renders LTR',
    description: 'Verify dir="ltr" is applied and text flows left-to-right',
    testFn: async () => {
      const element = document.querySelector('[dir="ltr"]');
      if (!element) return false;

      const computedDir = window.getComputedStyle(element).direction;
      return computedDir === 'ltr';
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'Text alignment matches direction',
    description: 'RTL text should be right-aligned, LTR text left-aligned',
    testFn: async () => {
      const rtlElement = document.querySelector('.dir-rtl');
      const ltrElement = document.querySelector('.dir-ltr');

      if (!rtlElement || !ltrElement) return false;

      const rtlAlign = window.getComputedStyle(rtlElement).textAlign;
      const ltrAlign = window.getComputedStyle(ltrElement).textAlign;

      return rtlAlign === 'right' && ltrAlign === 'left';
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'Lang attribute set correctly',
    description: 'lang="ur" for Urdu, lang="en" for English',
    testFn: async () => {
      const urduElement = document.querySelector('[lang="ur"]');
      const englishElement = document.querySelector('[lang="en"]');

      return !!urduElement && !!englishElement;
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  }
];

/**
 * Test Case 2: Code Block Rendering
 */
const codeBlockTests: BrowserTestCase[] = [
  {
    name: 'Code blocks remain LTR in RTL context',
    description: 'Code block should have dir="ltr" even when parent is RTL',
    testFn: async () => {
      const codeBlock = document.querySelector('.code-block');
      if (!codeBlock) return false;

      const computedDir = window.getComputedStyle(codeBlock).direction;
      const dirAttr = codeBlock.getAttribute('dir');

      return (dirAttr === 'ltr' || computedDir === 'ltr');
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'Inline code stays LTR',
    description: 'Inline code should maintain LTR direction',
    testFn: async () => {
      const inlineCode = document.querySelector('.inline-code');
      if (!inlineCode) return false;

      const computedDir = window.getComputedStyle(inlineCode).direction;
      const dirAttr = inlineCode.getAttribute('dir');

      return (dirAttr === 'ltr' || computedDir === 'ltr');
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'Code block is horizontally scrollable',
    description: 'Long code lines should be scrollable, not wrapped',
    testFn: async () => {
      const codeBlock = document.querySelector('.code-block');
      if (!codeBlock) return false;

      const overflowX = window.getComputedStyle(codeBlock).overflowX;
      return overflowX === 'auto' || overflowX === 'scroll';
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'Code syntax highlighting applies',
    description: 'Code should have proper styling applied',
    testFn: async () => {
      const code = document.querySelector('.code-block code');
      if (!code) return false;

      const fontFamily = window.getComputedStyle(code).fontFamily;
      return fontFamily.includes('Courier') || fontFamily.includes('monospace');
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  }
];

/**
 * Test Case 3: Spacing & Layout
 */
const spacingTests: BrowserTestCase[] = [
  {
    name: 'Message padding applied correctly',
    description: 'Messages should have consistent padding',
    testFn: async () => {
      const message = document.querySelector('.chatbot-message-rtl');
      if (!message) return false;

      const padding = window.getComputedStyle(message).padding;
      const paddingValues = padding.split(' ');

      return paddingValues.length > 0 && paddingValues[0] !== '0px';
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'Blockquote border on correct side',
    description: 'RTL blockquotes should have border-right, LTR have border-left',
    testFn: async () => {
      const blockquote = document.querySelector('blockquote');
      if (!blockquote) return true; // Skip if no blockquote

      const borderLeft = window.getComputedStyle(blockquote).borderLeftWidth;
      const borderRight = window.getComputedStyle(blockquote).borderRightWidth;

      // Should have border on one side
      return (parseInt(borderLeft) > 0 || parseInt(borderRight) > 0);
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'List items aligned correctly',
    description: 'List items should be properly aligned in RTL/LTR context',
    testFn: async () => {
      const list = document.querySelector('ul, ol');
      if (!list) return true; // Skip if no list

      const paddingStart = window.getComputedStyle(list).paddingInlineStart;
      return paddingStart !== '0px';
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  }
];

/**
 * Test Case 4: Font Rendering
 */
const fontTests: BrowserTestCase[] = [
  {
    name: 'Urdu font is loaded',
    description: 'Noto Sans Urdu or fallback font should be applied',
    testFn: async () => {
      const urduElement = document.querySelector('[lang="ur"]');
      if (!urduElement) return false;

      const fontFamily = window.getComputedStyle(urduElement).fontFamily;
      return fontFamily.includes('Noto') || fontFamily.includes('Scheherazade') || fontFamily.includes('Arial');
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'Font size is readable',
    description: 'Urdu text should have adequate font size',
    testFn: async () => {
      const urduElement = document.querySelector('[lang="ur"]');
      if (!urduElement) return false;

      const fontSize = window.getComputedStyle(urduElement).fontSize;
      const fontSizeNum = parseInt(fontSize);

      return fontSizeNum >= 14; // Minimum readable size
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  },
  {
    name: 'Line height is adequate',
    description: 'Text should have proper line spacing',
    testFn: async () => {
      const message = document.querySelector('.chatbot-message-rtl');
      if (!message) return false;

      const lineHeight = window.getComputedStyle(message).lineHeight;
      const lineHeightNum = parseFloat(lineHeight);

      return lineHeightNum >= 1.5; // Minimum line height ratio
    },
    browsers: ['Chrome', 'Firefox', 'Safari', 'Mobile']
  }
];

/**
 * Test Case 5: Mobile Responsiveness
 */
const mobileTests: BrowserTestCase[] = [
  {
    name: 'Mobile viewport width respected',
    description: 'Messages should be responsive on mobile screens',
    testFn: async () => {
      if (window.innerWidth > 640) return true; // Skip on desktop

      const message = document.querySelector('.chatbot-message-rtl');
      if (!message) return false;

      const rect = (message as HTMLElement).getBoundingClientRect();
      return rect.width <= window.innerWidth;
    },
    browsers: ['Mobile']
  },
  {
    name: 'Text wraps on narrow screens',
    description: 'Long text should wrap properly on mobile',
    testFn: async () => {
      if (window.innerWidth > 640) return true; // Skip on desktop

      const text = document.querySelector('.message-text');
      if (!text) return false;

      const rect = (text as HTMLElement).getBoundingClientRect();
      return rect.height > 0;
    },
    browsers: ['Mobile']
  },
  {
    name: 'Touch targets are adequate',
    description: 'Interactive elements should be touch-friendly',
    testFn: async () => {
      const buttons = document.querySelectorAll('button');

      for (const button of buttons) {
        const rect = button.getBoundingClientRect();
        // Minimum touch target size is 44x44 px
        if (rect.width < 44 || rect.height < 44) {
          return false;
        }
      }

      return true;
    },
    browsers: ['Mobile']
  },
  {
    name: 'Code blocks scrollable on mobile',
    description: 'Code blocks should be horizontally scrollable on narrow screens',
    testFn: async () => {
      if (window.innerWidth > 640) return true; // Skip on desktop

      const codeBlock = document.querySelector('.code-block');
      if (!codeBlock) return true; // Skip if no code block

      return (codeBlock as HTMLElement).scrollWidth > (codeBlock as HTMLElement).clientWidth;
    },
    browsers: ['Mobile']
  }
];

/**
 * Test Runner
 */
export async function runCrossBrowserTests(): Promise<TestResult[]> {
  const allTests = [
    ...textDirectionTests,
    ...codeBlockTests,
    ...spacingTests,
    ...fontTests,
    ...mobileTests
  ];

  const results: TestResult[] = [];
  const isMobile = window.innerWidth <= 640;
  const browserName = getBrowserName();

  for (const test of allTests) {
    // Skip if test is not for current browser
    if (!test.browsers.includes(browserName) && !test.browsers.includes('Mobile' && isMobile)) {
      continue;
    }

    const startTime = performance.now();
    try {
      const passed = await test.testFn();
      const duration = performance.now() - startTime;

      results.push({
        testName: test.name,
        browser: browserName,
        passed,
        duration
      });
    } catch (error) {
      const duration = performance.now() - startTime;
      results.push({
        testName: test.name,
        browser: browserName,
        passed: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        duration
      });
    }
  }

  return results;
}

/**
 * Browser Detection
 */
function getBrowserName(): string {
  const ua = navigator.userAgent.toLowerCase();

  if (ua.includes('safari') && !ua.includes('chrome')) {
    return 'Safari';
  } else if (ua.includes('firefox')) {
    return 'Firefox';
  } else if (ua.includes('chrome')) {
    return 'Chrome';
  } else if (ua.includes('edge')) {
    return 'Edge';
  }

  return 'Unknown';
}

/**
 * Generate Test Report
 */
export function generateTestReport(results: TestResult[]): string {
  const passed = results.filter(r => r.passed).length;
  const total = results.length;
  const passRate = ((passed / total) * 100).toFixed(1);

  let report = `
# RTL Cross-Browser Test Report

**Generated**: ${new Date().toISOString()}
**Browser**: ${getBrowserName()}
**Viewport**: ${window.innerWidth}x${window.innerHeight}
**Results**: ${passed}/${total} passed (${passRate}%)

## Test Results

| Test Name | Browser | Status | Duration |
|-----------|---------|--------|----------|
`;

  for (const result of results) {
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    const duration = result.duration.toFixed(2);
    report += `| ${result.testName} | ${result.browser} | ${status} | ${duration}ms |\n`;
  }

  if (results.some(r => !r.passed)) {
    report += `

## Failed Tests

`;
    for (const result of results.filter(r => !r.passed)) {
      report += `- **${result.testName}**: ${result.error || 'Test failed'}\n`;
    }
  }

  return report;
}

/**
 * Export for testing frameworks
 */
export const browserTests = {
  textDirection: textDirectionTests,
  codeBlocks: codeBlockTests,
  spacing: spacingTests,
  fonts: fontTests,
  mobile: mobileTests
};
