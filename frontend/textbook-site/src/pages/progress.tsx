/**
 * Progress page - Track learning progress across chapters
 */

import React, { useEffect, useState } from 'react';
import { usePersonalization } from '../components/PersonalizationProvider';
import { personalizationApi } from '../services/personalizationApi';
import { siteUrl } from '../utils/paths';
import styles from './progress.module.css';

interface ChapterProgress {
  chapter_id: number;
  chapter_title: string;
  mastery_score: number;
  completion_percentage: number;
  time_spent?: number;
  last_accessed?: string;
}

interface ProgressData {
  total_chapters: number;
  completed_chapters: number;
  overall_mastery: number;
  chapters: ChapterProgress[];
}

export default function ProgressPage(): JSX.Element {
  const { user, isAuthenticated, isLoading: authLoading } = usePersonalization();
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      window.location.href = siteUrl(`/login?redirect=${encodeURIComponent(window.location.pathname)}`);
    }
  }, [isAuthenticated, authLoading]);

  // Fetch progress data
  useEffect(() => {
    if (!user || !isAuthenticated) return;

    const fetchProgress = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await personalizationApi.getProgress(user.user_id);
        setProgress(data);
      } catch (err) {
        const error = err as Error;
        setError(error.message || 'Failed to load progress. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, [user, isAuthenticated]);

  if (authLoading || loading) {
    return <div className={styles.container}><div className={styles.loading}>Loading progress...</div></div>;
  }

  if (error) {
    return <div className={styles.container}><div className={styles.error}>{error}</div></div>;
  }

  if (!progress) {
    return <div className={styles.container}><div className={styles.empty}>No progress data available.</div></div>;
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#4CAF50'; // Green
    if (score >= 60) return '#FFC107'; // Yellow
    if (score >= 40) return '#FF9800'; // Orange
    return '#f44336'; // Red
  };

  return (
    <div className={styles.container}>
      <h1>📈 Learning Progress</h1>

      <div className={styles.overallStats}>
        <div className={styles.progressCircle}>
          <div className={styles.circleContent}>
            <div className={styles.percentage}>{progress.overall_mastery}%</div>
            <div className={styles.label}>Overall Mastery</div>
          </div>
          <svg viewBox="0 0 100 100" className={styles.svg}>
            <circle cx="50" cy="50" r="45" className={styles.bgCircle} />
            <circle
              cx="50"
              cy="50"
              r="45"
              className={styles.progressCirclesvg}
              style={{
                strokeDashoffset: 282.7 - (282.7 * progress.overall_mastery) / 100,
                stroke: getScoreColor(progress.overall_mastery),
              }}
            />
          </svg>
        </div>

        <div className={styles.statsBox}>
          <div className={styles.statItem}>
            <div className={styles.statNumber}>{progress.completed_chapters}</div>
            <div className={styles.statText}>Chapters Completed</div>
          </div>
          <div className={styles.statItem}>
            <div className={styles.statNumber}>{progress.total_chapters}</div>
            <div className={styles.statText}>Total Chapters</div>
          </div>
        </div>
      </div>

      <div className={styles.chaptersSection}>
        <h2>Chapters Progress</h2>
        <div className={styles.chaptersList}>
          {progress.chapters.length === 0 ? (
            <p className={styles.empty}>No chapters started yet. Start learning now!</p>
          ) : (
            progress.chapters.map((chapter) => (
              <div key={chapter.chapter_id} className={styles.chapterItem}>
                <div className={styles.chapterHeader}>
                  <h3 className={styles.chapterTitle}>{chapter.chapter_title}</h3>
                  <span
                    className={styles.masteryBadge}
                    style={{ backgroundColor: getScoreColor(chapter.mastery_score) }}
                  >
                    {chapter.mastery_score}%
                  </span>
                </div>

                <div className={styles.progressBar}>
                  <div
                    className={styles.progressFill}
                    style={{
                      width: `${chapter.completion_percentage}%`,
                      backgroundColor: getScoreColor(chapter.mastery_score),
                    }}
                  />
                </div>

                <div className={styles.chapterStats}>
                  <span>Completion: {chapter.completion_percentage}%</span>
                  {chapter.time_spent && (
                    <span>Time Spent: {Math.round(chapter.time_spent)} mins</span>
                  )}
                  {chapter.last_accessed && (
                    <span>Last Accessed: {new Date(chapter.last_accessed).toLocaleDateString()}</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className={styles.tips}>
        <h2>💡 Learning Tips</h2>
        <ul>
          <li>Regular practice improves your mastery score</li>
          <li>Complete all chapters in a module to unlock advanced challenges</li>
          <li>Review low-mastery chapters to strengthen your knowledge</li>
          <li>Check your dashboard for personalized recommendations</li>
        </ul>
      </div>
    </div>
  );
}
