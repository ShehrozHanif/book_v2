/**
 * PracticeWidgetInjector - Injects practice questions widget into chapter pages
 * Runs after hydration to add interactive practice section at bottom of chapters
 */

import React, { useEffect, useRef } from 'react';
import { usePersonalization } from './PersonalizationProvider';
import PracticeQuestionsWidget from './PracticeQuestionsWidget';
import ReactDOM from 'react-dom';

/**
 * Extract chapter ID from current page URL
 */
function extractChapterIdFromUrl(): number | null {
  const path = window.location.pathname;
  const match = path.match(/chapter-(\d+)/i);
  if (match) {
    return parseInt(match[1], 10);
  }
  return null;
}

/**
 * Find the main content area and inject the widget
 */
function getInsertionPoint(): HTMLElement | null {
  // Try to find the main article element that contains chapter content
  const article = document.querySelector('article');
  if (article) {
    return article;
  }

  // Fallback to main element
  const main = document.querySelector('main');
  if (main) {
    return main;
  }

  // Final fallback to any docs-content container
  const docsContent = document.querySelector('.docs-content');
  if (docsContent) {
    return docsContent as HTMLElement;
  }

  return null;
}

export const PracticeWidgetInjector: React.FC = () => {
  const { isAuthenticated } = usePersonalization();
  const injectionPointRef = useRef<HTMLElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const chapterId = extractChapterIdFromUrl();

    // Only inject on chapter pages (not on module index or other pages)
    if (!chapterId) {
      return;
    }

    // Wait for DOM to be fully ready
    const injectWidget = () => {
      // Find insertion point
      const article = getInsertionPoint();
      if (!article) {
        // Retry after a delay
        setTimeout(injectWidget, 500);
        return;
      }

      // Skip if widget already injected on this page
      if (article.querySelector('[data-practice-widget]')) {
        return;
      }

      injectionPointRef.current = article;

      // Create a container for the widget
      const container = document.createElement('div');
      container.setAttribute('data-practice-widget', String(chapterId));
      container.className = 'practice-widget-container';

      // Append to end of article
      article.appendChild(container);
      containerRef.current = container;

      // Render the widget into the container
      ReactDOM.render(
        <PracticeQuestionsWidget chapterId={chapterId} />,
        container
      );
    };

    // Use requestIdleCallback if available, otherwise setTimeout
    if ('requestIdleCallback' in window) {
      requestIdleCallback(injectWidget, { timeout: 2000 });
    } else {
      setTimeout(injectWidget, 100);
    }

    // Cleanup on unmount
    return () => {
      if (containerRef.current) {
        try {
          ReactDOM.unmountComponentAtNode(containerRef.current);
        } catch (e) {
          console.error('Error unmounting practice widget:', e);
        }
      }
    };
  }, [isAuthenticated]);

  return null;
};

export default PracticeWidgetInjector;
