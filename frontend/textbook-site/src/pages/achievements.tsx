/**
 * Achievements page - Display user achievements and badges
 */

import React, { useEffect, useState } from 'react';
import { usePersonalization } from '../components/PersonalizationProvider';
import { personalizationApi } from '../services/personalizationApi';
import { siteUrl } from '../utils/paths';
import styles from './achievements.module.css';

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  earned_date?: string;
  points?: number;
  rarity?: string;
}

interface AchievementsData {
  achievements: Achievement[];
  stats: {
    total_achievements: number;
    total_points: number;
  };
}

export default function AchievementsPage(): JSX.Element {
  const { user, isAuthenticated, isLoading: authLoading } = usePersonalization();
  const [achievements, setAchievements] = useState<AchievementsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      window.location.href = siteUrl(`/login?redirect=${encodeURIComponent(window.location.pathname)}`);
    }
  }, [isAuthenticated, authLoading]);

  // Fetch achievements
  useEffect(() => {
    if (!user || !isAuthenticated) return;

    const fetchAchievements = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await personalizationApi.getAchievements(user.user_id);
        setAchievements(data);
      } catch (err) {
        const error = err as Error;
        setError(error.message || 'Failed to load achievements. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchAchievements();
  }, [user, isAuthenticated]);

  if (authLoading || loading) {
    return <div className={styles.container}><div className={styles.loading}>Loading achievements...</div></div>;
  }

  if (error) {
    return <div className={styles.container}><div className={styles.error}>{error}</div></div>;
  }

  if (!achievements) {
    return <div className={styles.container}><div className={styles.empty}>No achievements yet. Start learning!</div></div>;
  }

  const rarityColor = (rarity?: string) => {
    switch (rarity) {
      case 'legendary': return '#FFD700';
      case 'epic': return '#9C27B0';
      case 'rare': return '#2196F3';
      case 'uncommon': return '#4CAF50';
      default: return '#9E9E9E';
    }
  };

  return (
    <div className={styles.container}>
      <h1>🏆 My Achievements</h1>

      <div className={styles.stats}>
        <div className={styles.stat}>
          <div className={styles.statValue}>{achievements.stats.total_achievements}</div>
          <div className={styles.statLabel}>Achievements Unlocked</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{achievements.stats.total_points}</div>
          <div className={styles.statLabel}>Points Earned</div>
        </div>
      </div>

      <div className={styles.achievementsGrid}>
        {achievements.achievements.length === 0 ? (
          <p className={styles.empty}>No achievements yet. Complete chapters to earn badges!</p>
        ) : (
          achievements.achievements.map((achievement) => (
            <div
              key={achievement.id}
              className={styles.achievementCard}
              style={{ borderColor: rarityColor(achievement.rarity) }}
            >
              <div className={styles.icon}>{achievement.icon}</div>
              <h3 className={styles.title}>{achievement.title}</h3>
              <p className={styles.description}>{achievement.description}</p>
              {achievement.points && (
                <div className={styles.points}>+{achievement.points} points</div>
              )}
              {achievement.rarity && (
                <div className={styles.rarity} style={{ color: rarityColor(achievement.rarity) }}>
                  {achievement.rarity.toUpperCase()}
                </div>
              )}
              {achievement.earned_date && (
                <div className={styles.earned}>
                  Earned: {new Date(achievement.earned_date).toLocaleDateString()}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
