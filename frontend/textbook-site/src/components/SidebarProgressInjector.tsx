/**
 * SidebarProgressInjector - Injects progress icons into sidebar chapter links
 * Runs after hydration to add visual progress indicators to the sidebar
 */

import React, { useEffect } from 'react';
import { usePersonalization } from './PersonalizationProvider';
import ChapterProgressIcon from './ChapterProgressIcon';

/**
 * Extract chapter ID from URL path
 * Matches patterns like "/chapter-01", "/chapter-1", or "chapter-01.md"
 */
function extractChapterIdFromHref(href: string): number | null {
  const match = href.match(/chapter-(\d+)/i);
  if (match) {
    return parseInt(match[1], 10);
  }
  return null;
}

export const SidebarProgressInjector: React.FC = () => {
  const { progress, isAuthenticated } = usePersonalization();

  useEffect(() => {
    if (!isAuthenticated || !progress) {
      return;
    }

    // Find all sidebar links that match chapter pattern
    const sidebarItems = document.querySelectorAll(
      'a[href*="chapter-"], a[href*="/docs/module-"]'
    );

    sidebarItems.forEach((link) => {
      const href = link.getAttribute('href');
      if (!href) return;

      const chapterId = extractChapterIdFromHref(href);
      if (!chapterId) return;

      // Skip if already has progress icon
      if (link.querySelector('[data-chapter-progress]')) {
        return;
      }

      // Find the chapter progress record
      const chapterProgress = progress.find(
        (p) => p.chapter_id === chapterId
      );

      const status = chapterProgress?.completion_status || 'not_started';
      const masteryScore = chapterProgress?.mastery_score;

      // Create a wrapper span for the icon
      const iconSpan = document.createElement('span');
      iconSpan.setAttribute('data-chapter-progress', String(chapterId));
      iconSpan.className = 'chapter-progress-icon-wrapper';
      iconSpan.style.marginRight = '6px';
      iconSpan.style.display = 'inline-flex';
      iconSpan.style.alignItems = 'center';

      // Get icon and color based on status
      let icon = '◯';
      let color = '#ccc';
      let label = 'Not Started';

      switch (status) {
        case 'completed':
          icon = '✓';
          color = '#2e8555';
          label = 'Completed';
          break;
        case 'in_progress':
          icon = '📈';
          color = '#f39c12';
          label = 'In Progress';
          break;
      }

      const tooltip = masteryScore
        ? `${label} (${Math.round(masteryScore)}% mastery)`
        : label;

      iconSpan.innerHTML = `<span style="color: ${color}; font-weight: bold; font-size: 16px; cursor: default;" title="${tooltip}">${icon}</span>`;

      // Insert icon at the beginning of the link text
      const textNode = link.childNodes[0];
      if (textNode) {
        link.insertBefore(iconSpan, textNode);
      } else {
        link.insertBefore(iconSpan, link.firstChild);
      }
    });
  }, [progress, isAuthenticated]);

  return null;
};

export default SidebarProgressInjector;
