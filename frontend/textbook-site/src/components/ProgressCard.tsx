/**
 * Progress card showing learning statistics
 */

import React from "react";
import styles from "./ProgressCard.module.css";
import { OverallProgress } from "../types/personalization";

interface ProgressCardProps {
  progress: OverallProgress;
}

const ProgressCard: React.FC<ProgressCardProps> = ({ progress }) => {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>📊 Learning Progress</h3>

      <div className={styles.progressItem}>
        <div className={styles.progressLabel}>
          <span>Chapters Completed</span>
          <span className={styles.value}>
            {progress.chapters_completed}/{progress.total_chapters}
          </span>
        </div>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{
              width: `${progress.completion_percentage}%`,
              backgroundColor: "#4CAF50",
            }}
          />
        </div>
        <span className={styles.percentage}>{progress.completion_percentage}%</span>
      </div>

      <div className={styles.progressItem}>
        <div className={styles.progressLabel}>
          <span>Average Mastery</span>
          <span className={styles.value}>{progress.avg_mastery.toFixed(1)}%</span>
        </div>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{
              width: `${progress.avg_mastery}%`,
              backgroundColor: "#2196F3",
            }}
          />
        </div>
      </div>

      <div className={styles.statsGrid}>
        <div className={styles.stat}>
          <span className={styles.statIcon}>⏱️</span>
          <span className={styles.statValue}>{progress.total_time_hours.toFixed(1)}</span>
          <span className={styles.statLabel}>Hours</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statIcon}>✏️</span>
          <span className={styles.statValue}>{progress.total_practice_attempts}</span>
          <span className={styles.statLabel}>Attempts</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statIcon}>📈</span>
          <span className={styles.statValue}>{progress.avg_practice_score.toFixed(0)}%</span>
          <span className={styles.statLabel}>Avg Score</span>
        </div>
      </div>
    </div>
  );
};

export default ProgressCard;
