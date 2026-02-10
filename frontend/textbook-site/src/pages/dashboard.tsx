/**
 * Dashboard page - Comprehensive statistics and learning analytics
 */

import React, { useEffect, useState } from 'react';
import { usePersonalization } from '../components/PersonalizationProvider';
import { personalizationApi } from '../services/personalizationApi';
import { StatisticsData } from '../types/personalization';
import ProgressCard from '../components/ProgressCard';
import StatisticsCharts from '../components/StatisticsCharts';
import styles from './dashboard.module.css';

type DashboardState = 'loading' | 'loaded' | 'error';

export default function DashboardPage(): JSX.Element {
  const { user, isAuthenticated, isLoading: authLoading } = usePersonalization();

  const [statistics, setStatistics] = useState<StatisticsData | null>(null);
  const [state, setState] = useState<DashboardState>('loading');
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      window.location.href = `/book/login?redirect=${encodeURIComponent(window.location.pathname)}`;
    }
  }, [isAuthenticated, authLoading]);

  // Fetch statistics when user is authenticated
  useEffect(() => {
    if (!user || !isAuthenticated) return;

    const fetchStatistics = async () => {
      try {
        setState('loading');
        setError(null);
        const data = await personalizationApi.getStatistics(user.user_id);
        setStatistics(data);
        setState('loaded');
      } catch (err) {
        const error = err as Error;
        setError(
          error.message || 'Failed to load statistics. Please try again later.'
        );
        setState('error');
      }
    };

    fetchStatistics();
  }, [user, isAuthenticated]);

  const handleRefresh = async () => {
    if (!user) return;

    try {
      setState('loading');
      const data = await personalizationApi.getStatistics(user.user_id);
      setStatistics(data);
      setState('loaded');
    } catch (err) {
      const error = err as Error;
      setError(error.message || 'Failed to refresh statistics.');
      setState('error');
    }
  };

  if (authLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <div className={styles.container}>
        <div className={styles.errorState}>
          <p>Please log in to access your dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>📚 Learning Dashboard</h1>
          <p className={styles.subtitle}>
            Welcome back, <strong>{user.username}</strong>! Here's your learning progress.
          </p>
        </div>
        <button
          className={styles.refreshButton}
          onClick={handleRefresh}
          disabled={state === 'loading'}
          title="Refresh dashboard data"
        >
          {state === 'loading' ? '⏳ Refreshing...' : '🔄 Refresh'}
        </button>
      </div>

      {/* Loading State */}
      {state === 'loading' && !statistics && (
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>Loading your statistics...</p>
        </div>
      )}

      {/* Error State */}
      {state === 'error' && !statistics && (
        <div className={styles.errorState}>
          <h2>⚠️ Unable to Load Statistics</h2>
          <p>{error}</p>
          <button
            className={styles.retryButton}
            onClick={handleRefresh}
          >
            Try Again
          </button>
        </div>
      )}

      {/* Content */}
      {state === 'loaded' && statistics && (
        <div className={styles.content}>
          {/* Progress Overview */}
          <section className={styles.section}>
            <ProgressCard progress={statistics.overall_progress} />
          </section>

          {/* Statistics Charts */}
          <section className={styles.section}>
            <StatisticsCharts statistics={statistics} />
          </section>

          {/* Focus Areas Recommendations */}
          {statistics.recommended_focus_areas.length > 0 && (
            <section className={styles.section}>
              <div className={styles.focusCard}>
                <h2 className={styles.focusTitle}>🎯 Recommended Focus Areas</h2>
                <div className={styles.focusItems}>
                  {statistics.recommended_focus_areas.map((area) => (
                    <div key={area.chapter_id} className={styles.focusItem}>
                      <div className={styles.focusHeader}>
                        <h3 className={styles.focusChapter}>
                          Chapter {area.chapter_id}
                        </h3>
                        <span className={styles.focusMastery}>
                          {Math.round(area.mastery_score)}% mastery
                        </span>
                      </div>
                      <p className={styles.focusReason}>{area.reason}</p>
                      <div className={styles.focusStats}>
                        <span>
                          ⏱️ {area.time_spent_hours.toFixed(1)}h spent
                        </span>
                        <span className={styles.focusStatus}>
                          {area.completion_status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* Last Updated */}
          <div className={styles.footer}>
            <p>Last updated: {new Date(statistics.generated_at).toLocaleString()}</p>
          </div>
        </div>
      )}
    </div>
  );
}
