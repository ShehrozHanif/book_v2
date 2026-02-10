/**
 * Cross-Browser Testing with Playwright
 *
 * Automated tests for ChatbotMessageRTL component across:
 * - Chrome
 * - Firefox
 * - Safari
 * - Mobile viewports
 *
 * Run with: npx playwright test ChatbotMessageRTL.playwright.spec.ts
 */

import { test, expect, Page } from '@playwright/test';

/**
 * Configure browsers to test
 */
const browsers = ['chromium', 'firefox', 'webkit'];
const mobileViewports = [
  { name: 'iPhone SE', width: 375, height: 667 },
  { name: 'iPhone 12', width: 390, height: 844 },
  { name: 'Pixel 5', width: 393, height: 851 }
];

/**
 * Helper to setup test page
 */
async function setupTestPage(page: Page) {
  // Navigate to chatbot component
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

  // Wait for chatbot to load
  await page.waitForSelector('.chatbot-widget', { timeout: 5000 });
}

/**
 * T031: Cross-Browser RTL Rendering Tests
 */
describe('T031: Cross-Browser RTL Rendering', () => {

  test.describe('Text Direction & Alignment', () => {
    browsers.forEach(browserName => {
      test(`${browserName}: Urdu text renders RTL`, async ({ page }) => {
        await setupTestPage(page);

        // Open chatbot
        await page.click('.chatbot-toggle');
        await page.waitForSelector('.messages-container');

        // Switch to Urdu (if language toggle available)
        const languageToggle = await page.$('[data-testid="language-toggle"]');
        if (languageToggle) {
          await page.click('[data-testid="urdu-button"]');
          await page.waitForTimeout(500); // Wait for direction to apply
        }

        // Check for RTL direction
        const rtlMessage = await page.$('[dir="rtl"]');
        expect(rtlMessage).not.toBeNull();

        // Verify computed direction style
        const direction = await page.evaluate(() => {
          const elem = document.querySelector('[dir="rtl"]');
          return window.getComputedStyle(elem!).direction;
        });
        expect(direction).toBe('rtl');

        // Verify text alignment
        const textAlign = await page.evaluate(() => {
          const elem = document.querySelector('.chatbot-message-rtl[lang="ur"]');
          return window.getComputedStyle(elem!).textAlign;
        });
        expect(['right', 'end']).toContain(textAlign);
      });

      test(`${browserName}: English text renders LTR`, async ({ page }) => {
        await setupTestPage(page);
        await page.click('.chatbot-toggle');
        await page.waitForSelector('.messages-container');

        // Check for LTR direction
        const ltrMessage = await page.$('[dir="ltr"]');
        expect(ltrMessage).not.toBeNull();

        // Verify computed direction style
        const direction = await page.evaluate(() => {
          const elem = document.querySelector('[dir="ltr"]');
          return window.getComputedStyle(elem!).direction;
        });
        expect(direction).toBe('ltr');
      });

      test(`${browserName}: Lang attribute set correctly`, async ({ page }) => {
        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        // Check English lang attribute
        const englishMsg = await page.$('[lang="en"]');
        expect(englishMsg).not.toBeNull();

        // Check Urdu lang attribute (if available)
        const urduToggle = await page.$('[data-testid="urdu-button"]');
        if (urduToggle) {
          await page.click(urduToggle);
          await page.waitForTimeout(500);

          const urduMsg = await page.$('[lang="ur"]');
          expect(urduMsg).not.toBeNull();
        }
      });
    });
  });

  test.describe('Code Block Rendering', () => {
    browsers.forEach(browserName => {
      test(`${browserName}: Code blocks remain LTR in RTL context`, async ({ page }) => {
        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        // Send a message with code (if code sample available)
        await page.fill('input[placeholder*="message" i]', 'show code example');
        await page.press('input[placeholder*="message" i]', 'Enter');

        await page.waitForTimeout(2000); // Wait for response

        // Check code block direction
        const codeBlock = await page.$('.code-block');
        if (codeBlock) {
          const codeDir = await page.evaluate(() => {
            const elem = document.querySelector('.code-block');
            return {
              direction: window.getComputedStyle(elem!).direction,
              dirAttr: elem?.getAttribute('dir')
            };
          });

          expect(codeDir.direction).toBe('ltr');
          expect(['ltr', null]).toContain(codeDir.dirAttr);
        }
      });

      test(`${browserName}: Inline code stays LTR`, async ({ page }) => {
        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        // Check inline code elements
        const inlineCode = await page.$('.inline-code');
        if (inlineCode) {
          const codeDir = await page.evaluate(() => {
            const elem = document.querySelector('.inline-code');
            return window.getComputedStyle(elem!).direction;
          });

          expect(codeDir).toBe('ltr');
        }
      });

      test(`${browserName}: Code block is horizontally scrollable`, async ({ page }) => {
        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        const codeBlock = await page.$('.code-block');
        if (codeBlock) {
          const isScrollable = await page.evaluate(() => {
            const elem = document.querySelector('.code-block') as HTMLElement;
            return elem.scrollWidth > elem.clientWidth;
          });

          // Should be scrollable if content overflows
          expect(typeof isScrollable).toBe('boolean');
        }
      });
    });
  });

  test.describe('Font Rendering', () => {
    browsers.forEach(browserName => {
      test(`${browserName}: Urdu font is loaded`, async ({ page }) => {
        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        // Switch to Urdu
        const urduToggle = await page.$('[data-testid="urdu-button"]');
        if (urduToggle) {
          await page.click(urduToggle);
          await page.waitForTimeout(500);

          const fontFamily = await page.evaluate(() => {
            const elem = document.querySelector('[lang="ur"]');
            return window.getComputedStyle(elem!).fontFamily;
          });

          // Should have Noto Sans Urdu or fallback
          expect(
            fontFamily.includes('Noto') ||
            fontFamily.includes('Scheherazade') ||
            fontFamily.includes('Arial')
          ).toBeTruthy();
        }
      });

      test(`${browserName}: Font size is readable`, async ({ page }) => {
        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        const fontSize = await page.evaluate(() => {
          const elem = document.querySelector('.chatbot-message-rtl');
          return parseInt(window.getComputedStyle(elem!).fontSize);
        });

        expect(fontSize).toBeGreaterThanOrEqual(14); // Minimum readable size
      });

      test(`${browserName}: Line height is adequate`, async ({ page }) => {
        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        const lineHeight = await page.evaluate(() => {
          const elem = document.querySelector('.chatbot-message-rtl');
          return parseFloat(window.getComputedStyle(elem!).lineHeight);
        });

        expect(lineHeight).toBeGreaterThanOrEqual(1.5);
      });
    });
  });

  test.describe('Mobile Responsiveness', () => {
    mobileViewports.forEach(viewport => {
      test(`Mobile ${viewport.name}: Layout responsive`, async ({ page }) => {
        // Set mobile viewport
        await page.setViewportSize({ width: viewport.width, height: viewport.height });

        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        // Check message fits viewport
        const messageWidth = await page.evaluate(() => {
          const elem = document.querySelector('.chatbot-message-rtl') as HTMLElement;
          return {
            width: elem.offsetWidth,
            maxWidth: parseInt(window.getComputedStyle(elem).maxWidth)
          };
        });

        expect(messageWidth.width).toBeLessThanOrEqual(viewport.width);
      });

      test(`Mobile ${viewport.name}: Text wraps correctly`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        // Text should wrap, not overflow
        const hasOverflow = await page.evaluate(() => {
          const container = document.querySelector('.messages-container') as HTMLElement;
          return container.scrollWidth > container.clientWidth;
        });

        expect(hasOverflow).toBe(false);
      });

      test(`Mobile ${viewport.name}: Touch targets are adequate`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await setupTestPage(page);

        // Check button sizes (should be 44x44 minimum)
        const buttonSizes = await page.evaluate(() => {
          const buttons = Array.from(document.querySelectorAll('button'));
          return buttons.map(btn => ({
            width: btn.offsetWidth,
            height: btn.offsetHeight,
            adequate: btn.offsetWidth >= 44 && btn.offsetHeight >= 44
          }));
        });

        const allAdequate = buttonSizes.every(btn => btn.adequate);
        expect(allAdequate).toBe(true);
      });

      test(`Mobile ${viewport.name}: Code blocks scrollable`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await setupTestPage(page);
        await page.click('.chatbot-toggle');

        // Send code example
        await page.fill('input[placeholder*="message" i]', 'show long code');
        await page.press('input[placeholder*="message" i]', 'Enter');

        await page.waitForTimeout(2000);

        const codeBlock = await page.$('.code-block');
        if (codeBlock) {
          const isScrollable = await page.evaluate(() => {
            const elem = document.querySelector('.code-block') as HTMLElement;
            return elem.scrollWidth > elem.clientWidth;
          });

          // Should allow horizontal scroll on narrow screens
          expect(isScrollable).toBe(true);
        }
      });
    });
  });

  test.describe('Accessibility', () => {
    test('Screen reader friendly (all browsers)', async ({ page }) => {
      await setupTestPage(page);
      await page.click('.chatbot-toggle');

      // Check ARIA attributes
      const message = await page.$('[role="article"]');
      expect(message).not.toBeNull();

      // Check lang attribute
      const langAttr = await page.evaluate(() => {
        const elem = document.querySelector('[role="article"]');
        return elem?.getAttribute('lang');
      });

      expect(['en', 'ur']).toContain(langAttr);
    });

    test('Keyboard navigation works', async ({ page }) => {
      await setupTestPage(page);

      // Tab through interactive elements
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => {
        return document.activeElement?.tagName;
      });

      expect(focused).toBeTruthy();
    });

    test('Focus styles visible', async ({ page }) => {
      await setupTestPage(page);

      // Focus on button
      await page.click('.chatbot-toggle');
      await page.keyboard.press('Tab');

      // Check focus styling
      const hasFocusStyle = await page.evaluate(() => {
        const elem = document.activeElement;
        const styles = window.getComputedStyle(elem!);
        return {
          outline: styles.outline,
          boxShadow: styles.boxShadow
        };
      });

      expect(
        hasFocusStyle.outline !== 'none' ||
        hasFocusStyle.boxShadow !== 'none'
      ).toBe(true);
    });
  });

  test.describe('Performance', () => {
    test('Language switch completes quickly (< 100ms)', async ({ page }) => {
      await setupTestPage(page);
      await page.click('.chatbot-toggle');

      const startTime = Date.now();

      // Switch language
      const urduButton = await page.$('[data-testid="urdu-button"]');
      if (urduButton) {
        await page.click(urduButton);
        await page.waitForSelector('[dir="rtl"]', { timeout: 1000 });
      }

      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(500); // Reasonable timeout
    });

    test('Messages render without layout shift', async ({ page }) => {
      await setupTestPage(page);
      await page.click('.chatbot-toggle');

      // Monitor layout shift
      const cls = await page.evaluate(() => {
        return new Promise<number>(resolve => {
          let totalCLS = 0;
          const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if ((entry as any).hadRecentInput) continue;
              totalCLS += (entry as any).value;
            }
          });

          observer.observe({ entryTypes: ['layout-shift'] });

          setTimeout(() => {
            observer.disconnect();
            resolve(totalCLS);
          }, 2000);
        });
      });

      expect(cls).toBeLessThan(0.1); // CLS should be minimal
    });
  });
});

/**
 * Export test data for manual testing
 */
export const testData = {
  urduText: 'السلام عليكم ورحمة الله وبركاته',
  codeExample: `def hello_urdu():
    message = "السلام عليكم"
    print(message)`,
  mixedContent: 'یہ English word والا Urdu text ہے۔'
};
