/**
 * useChapterProgress - Hook to get progress data for a specific chapter
 */

import { useMemo } from 'react';
import { usePersonalization } from '../components/PersonalizationProvider';
import { ProgressRecord } from '../types/personalization';

interface ChapterProgressData {
  status: 'not_started' | 'in_progress' | 'completed';
  masteryScore?: number;
  timeSpentSeconds?: number;
  practiceAttempts?: number;
}

/**
 * Returns progress data for a specific chapter
 * Returns default (not_started) if user not authenticated
 */
export const useChapterProgress = (chapterId: number): ChapterProgressData => {
  const { progress, isAuthenticated } = usePersonalization();

  return useMemo(() => {
    if (!isAuthenticated || !progress) {
      return { status: 'not_started' };
    }

    const chapterProgress = progress.find(
      (p: ProgressRecord) => p.chapter_id === chapterId
    );

    if (!chapterProgress) {
      return { status: 'not_started' };
    }

    return {
      status: (chapterProgress.completion_status as 'not_started' | 'in_progress' | 'completed'),
      masteryScore: chapterProgress.mastery_score,
      timeSpentSeconds: chapterProgress.time_spent_seconds,
      practiceAttempts: chapterProgress.practice_attempts,
    };
  }, [progress, chapterId, isAuthenticated]);
};
