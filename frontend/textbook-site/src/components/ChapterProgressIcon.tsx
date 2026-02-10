/**
 * ChapterProgressIcon - Displays completion status for chapters in sidebar
 */

import React, { useState } from 'react';
import styles from './ChapterProgressIcon.module.css';

interface ChapterProgressIconProps {
  chapterId: number;
  status: 'not_started' | 'in_progress' | 'completed';
  masteryScore?: number;
}

/**
 * Returns icon and color based on chapter completion status
 */
const getStatusDisplay = (status: string) => {
  switch (status) {
    case 'completed':
      return { icon: '✓', color: '#2e8555', label: 'Completed' };
    case 'in_progress':
      return { icon: '📈', color: '#f39c12', label: 'In Progress' };
    case 'not_started':
      return { icon: '◯', color: '#ccc', label: 'Not Started' };
    default:
      return { icon: '◯', color: '#ccc', label: 'Unknown' };
  }
};

export const ChapterProgressIcon: React.FC<ChapterProgressIconProps> = ({
  chapterId,
  status,
  masteryScore,
}) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const display = getStatusDisplay(status);

  const tooltipText = masteryScore
    ? `Chapter ${chapterId}: ${display.label} (${Math.round(masteryScore)}% mastery)`
    : `Chapter ${chapterId}: ${display.label}`;

  return (
    <span
      className={styles.icon}
      style={{
        color: display.color,
        cursor: 'default',
      }}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      title={tooltipText}
      aria-label={tooltipText}
    >
      {display.icon}
      {showTooltip && <div className={styles.tooltip}>{tooltipText}</div>}
    </span>
  );
};

export default ChapterProgressIcon;
