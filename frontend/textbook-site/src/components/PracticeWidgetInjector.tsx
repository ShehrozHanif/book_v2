/**
 * PracticeWidgetInjector - Injects practice questions widget into chapter pages
 * Runs after hydration to add interactive practice section at bottom of chapters
 */

import React, { useEffect, useRef, useState } from 'react';
import { PersonalizationProvider } from './PersonalizationProvider';
import PracticeQuestionsWidget from './PracticeQuestionsWidget';
import { createRoot, Root } from 'react-dom/client';

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
  const article = document.querySelector('article');
  if (article) return article;

  const main = document.querySelector('main');
  if (main) return main;

  const docsContent = document.querySelector('.docs-content');
  if (docsContent) return docsContent as HTMLElement;

  return null;
}

export const PracticeWidgetInjector: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const rootRef = useRef<Root | null>(null);
  const [pathname, setPathname] = useState('');

  // Set initial pathname on mount and listen for URL changes (Docusaurus SPA navigation)
  useEffect(() => {
    setPathname(window.location.pathname);

    const observer = new MutationObserver(() => {
      if (window.location.pathname !== pathname) {
        setPathname(window.location.pathname);
      }
    });

    observer.observe(document.querySelector('title') || document.head, {
      childList: true,
      subtree: true,
      characterData: true,
    });

    const handlePopState = () => setPathname(window.location.pathname);
    window.addEventListener('popstate', handlePopState);

    return () => {
      observer.disconnect();
      window.removeEventListener('popstate', handlePopState);
    };
  }, [pathname]);

  // Inject widget when pathname changes
  useEffect(() => {
    // Cleanup previous injection
    if (rootRef.current) {
      try { rootRef.current.unmount(); } catch (e) { /* ignore */ }
      rootRef.current = null;
    }
    if (containerRef.current && containerRef.current.parentElement) {
      try { containerRef.current.parentElement.removeChild(containerRef.current); } catch (e) { /* ignore */ }
      containerRef.current = null;
    }

    const chapterId = extractChapterIdFromUrl();
    if (!chapterId) {
      return;
    }

    const injectWidget = () => {
      const article = getInsertionPoint();
      if (!article) {
        setTimeout(injectWidget, 500);
        return;
      }

      // Skip if widget already injected
      if (article.querySelector('[data-practice-widget]')) {
        return;
      }

      const container = document.createElement('div');
      container.setAttribute('data-practice-widget', String(chapterId));
      container.className = 'practice-widget-container';

      article.appendChild(container);
      containerRef.current = container;

      const root = createRoot(container);
      root.render(
        <PersonalizationProvider>
          <PracticeQuestionsWidget chapterId={chapterId} />
        </PersonalizationProvider>
      );
      rootRef.current = root;
    };

    // Wait for DOM to be ready after navigation
    setTimeout(injectWidget, 300);

    return () => {
      if (rootRef.current) {
        try { rootRef.current.unmount(); } catch (e) { /* ignore */ }
        rootRef.current = null;
      }
      if (containerRef.current && containerRef.current.parentElement) {
        try { containerRef.current.parentElement.removeChild(containerRef.current); } catch (e) { /* ignore */ }
        containerRef.current = null;
      }
    };
  }, [pathname]);

  return null;
};

export default PracticeWidgetInjector;
