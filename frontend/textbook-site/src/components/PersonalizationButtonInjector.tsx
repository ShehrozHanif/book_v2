/**
 * PersonalizationButtonInjector - Injects personalization button after Learning Objectives
 * Runs after hydration to add interactive personalization section to chapter pages
 */

import React, { useEffect, useRef, useState } from 'react';
import { PersonalizationProvider } from './PersonalizationProvider';
import PersonalizationButton from './PersonalizationButton';
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
 * Find the Learning Objectives H2 element
 */
function getLearningObjectivesHeading(): HTMLHeadingElement | null {
  const headingById = document.querySelector('h2#learning-objectives') as HTMLHeadingElement;
  if (headingById) {
    return headingById;
  }

  const allH2s = document.querySelectorAll('h2');
  for (const h2 of allH2s) {
    if (h2.textContent?.includes('Learning Objectives')) {
      return h2;
    }
  }

  return null;
}

export const PersonalizationButtonInjector: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const rootRef = useRef<Root | null>(null);
  const [pathname, setPathname] = useState(typeof window !== 'undefined' ? window.location.pathname : '');

  // Listen for URL changes (Docusaurus SPA navigation)
  useEffect(() => {
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

    // Also listen for popstate (back/forward navigation)
    const handlePopState = () => setPathname(window.location.pathname);
    window.addEventListener('popstate', handlePopState);

    return () => {
      observer.disconnect();
      window.removeEventListener('popstate', handlePopState);
    };
  }, [pathname]);

  // Inject button when pathname changes
  useEffect(() => {
    // Cleanup previous injection
    if (rootRef.current) {
      try {
        rootRef.current.unmount();
      } catch (e) {
        // ignore
      }
      rootRef.current = null;
    }
    if (containerRef.current && containerRef.current.parentElement) {
      try {
        containerRef.current.parentElement.removeChild(containerRef.current);
      } catch (e) {
        // ignore
      }
      containerRef.current = null;
    }

    const chapterId = extractChapterIdFromUrl();
    if (!chapterId) {
      return;
    }

    const injectButton = () => {
      const heading = getLearningObjectivesHeading();
      if (!heading) {
        setTimeout(injectButton, 500);
        return;
      }

      const parent = heading.parentElement;
      if (!parent) return;

      // Skip if already injected
      if (parent.querySelector('[data-personalization-button]')) {
        return;
      }

      const container = document.createElement('div');
      container.setAttribute('data-personalization-button', String(chapterId));
      container.className = 'personalization-button-container';

      if (heading.nextSibling) {
        parent.insertBefore(container, heading.nextSibling);
      } else {
        parent.appendChild(container);
      }

      containerRef.current = container;

      const root = createRoot(container);
      root.render(
        <PersonalizationProvider>
          <PersonalizationButton chapterId={chapterId} />
        </PersonalizationProvider>
      );
      rootRef.current = root;
    };

    // Wait for DOM to be ready after navigation
    setTimeout(injectButton, 300);

    return () => {
      if (rootRef.current) {
        try {
          rootRef.current.unmount();
        } catch (e) {
          // ignore
        }
        rootRef.current = null;
      }
      if (containerRef.current && containerRef.current.parentElement) {
        try {
          containerRef.current.parentElement.removeChild(containerRef.current);
        } catch (e) {
          // ignore
        }
        containerRef.current = null;
      }
    };
  }, [pathname]);

  return null;
};

export default PersonalizationButtonInjector;
