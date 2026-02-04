/**
 * Achievement gallery component for displaying earned and locked badges
 */

import React from "react";
import styles from "./AchievementsGallery.module.css";

interface Achievement {
  type: string;
  title: string;
  description: string;
  icon: string;
  points: number;
  earned_date?: string;
  earned?: boolean;
}

interface AchievementsGalleryProps {
  achievements: {
    total_earned: number;
    total_points: number;
    achievements_by_category: Record<string, number>;
    recent_achievements: Array<{
      type: string;
      title: string;
      earned_date: string;
    }>;
  };
}

// Mock full achievements list for display
const allAchievements: Achievement[] = [
  {
    type: "chapter_1_mastered",
    title: "Fundamentals Started",
    description: "Completed Chapter 1: Fundamentals",
    icon: "🚀",
    points: 10,
  },
  {
    type: "xp_100",
    title: "Century Club",
    description: "Earned 100 XP points",
    icon: "💯",
    points: 100,
  },
  {
    type: "streak_7_days",
    title: "Week Warrior",
    description: "7 consecutive days of learning",
    icon: "🔥",
    points: 50,
  },
  {
    type: "perfect_practice",
    title: "Perfect Practice",
    description: "Scored 100% on a practice attempt",
    icon: "✨",
    points: 30,
  },
  {
    type: "question_master",
    title: "Question Master",
    description: "Asked 50 questions in chat",
    icon: "❓",
    points: 35,
  },
  {
    type: "early_adopter",
    title: "Early Adopter",
    description: "Started learning in the first week",
    icon: "🎖️",
    points: 20,
  },
];

const AchievementsGallery: React.FC<AchievementsGalleryProps> = ({ achievements }) => {
  const earnedSet = new Set(
    achievements.recent_achievements.map((a) => a.type)
  );

  const enrichedAchievements = allAchievements.map((ach) => ({
    ...ach,
    earned: earnedSet.has(ach.type),
  }));

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>🏆 Achievements</h2>
        <div className={styles.stats}>
          <div className={styles.stat}>
            <span className={styles.statValue}>{achievements.total_earned}</span>
            <span className={styles.statLabel}>Earned</span>
          </div>
          <div className={styles.divider} />
          <div className={styles.stat}>
            <span className={styles.statValue}>{achievements.total_points}</span>
            <span className={styles.statLabel}>Points</span>
          </div>
        </div>
      </div>

      {achievements.recent_achievements.length > 0 && (
        <div className={styles.recentSection}>
          <h3 className={styles.sectionTitle}>Recently Earned</h3>
          <div className={styles.recentList}>
            {achievements.recent_achievements.slice(0, 5).map((ach) => (
              <div key={ach.type} className={styles.recentItem}>
                <span className={styles.recentIcon}>⭐</span>
                <div className={styles.recentInfo}>
                  <p className={styles.recentTitle}>{ach.title}</p>
                  <p className={styles.recentDate}>
                    {new Date(ach.earned_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className={styles.gallerySection}>
        <h3 className={styles.sectionTitle}>All Achievements</h3>
        <div className={styles.gallery}>
          {enrichedAchievements.map((ach) => (
            <div
              key={ach.type}
              className={`${styles.badge} ${ach.earned ? styles.earned : styles.locked}`}
              title={ach.description}
            >
              <div className={styles.badgeContent}>
                <span className={styles.badgeIcon}>{ach.icon}</span>
                {!ach.earned && <span className={styles.lockOverlay}>🔒</span>}
              </div>
              <span className={styles.badgeTitle}>{ach.title}</span>
              <span className={styles.badgePoints}>+{ach.points} pts</span>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.categoriesSection}>
        <h3 className={styles.sectionTitle}>By Category</h3>
        <div className={styles.categories}>
          {Object.entries(achievements.achievements_by_category).map(([category, count]) => (
            <div key={category} className={styles.categoryItem}>
              <span className={styles.categoryName}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </span>
              <span className={styles.categoryCount}>{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AchievementsGallery;
