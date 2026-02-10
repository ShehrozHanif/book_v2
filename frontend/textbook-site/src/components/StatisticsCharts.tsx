/**
 * Statistics charts component using recharts
 */

import React from "react";
import styles from "./StatisticsCharts.module.css";
import { StatisticsData } from "../types/personalization";

interface StatisticsChartsProps {
  statistics: StatisticsData;
}

const StatisticsCharts: React.FC<StatisticsChartsProps> = ({ statistics }) => {
  const masteryEntries = Object.entries(statistics.mastery_by_chapter)
    .map(([chapterId, score]) => ({
      chapter: `Ch ${chapterId}`,
      mastery: score,
    }))
    .sort((a, b) => parseInt(a.chapter.split(" ")[1]) - parseInt(b.chapter.split(" ")[1]));

  const timeEntries = Object.entries(statistics.time_spent_heatmap)
    .map(([chapterId, hours]) => ({
      chapter: `Ch ${chapterId}`,
      hours: Math.round(hours * 10) / 10,
    }))
    .sort((a, b) => parseInt(a.chapter.split(" ")[1]) - parseInt(b.chapter.split(" ")[1]));

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>📈 Learning Analytics</h2>

      {/* Mastery Heatmap */}
      <div className={styles.chartSection}>
        <h3 className={styles.chartTitle}>Mastery by Chapter</h3>
        <div className={styles.heatmapContainer}>
          <div className={styles.heatmapGrid}>
            {masteryEntries.map((entry) => {
              const percentage = entry.mastery / 100;
              const color = `rgba(76, 175, 80, ${0.2 + percentage * 0.8})`;
              return (
                <div
                  key={entry.chapter}
                  className={styles.heatmapCell}
                  style={{
                    backgroundColor: color,
                    borderColor: percentage > 0.6 ? "#4caf50" : "#ddd",
                  }}
                  title={`${entry.chapter}: ${entry.mastery}%`}
                >
                  <span className={styles.heatmapLabel}>{entry.mastery}</span>
                </div>
              );
            })}
          </div>
          <div className={styles.heatmapLegend}>
            <span>0%</span>
            <div className={styles.legendGradient} />
            <span>100%</span>
          </div>
        </div>
      </div>

      {/* Time Spent Chart */}
      <div className={styles.chartSection}>
        <h3 className={styles.chartTitle}>Time Spent by Chapter</h3>
        <div className={styles.barChart}>
          {timeEntries.slice(0, 12).map((entry) => {
            const maxHours = Math.max(...timeEntries.map((e) => e.hours), 1);
            const percentage = (entry.hours / maxHours) * 100;
            return (
              <div key={entry.chapter} className={styles.barItem}>
                <div className={styles.barLabel}>{entry.chapter}</div>
                <div className={styles.barContainer}>
                  <div
                    className={styles.bar}
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: "#2196f3",
                    }}
                  />
                </div>
                <div className={styles.barValue}>{entry.hours}h</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Learning Curve */}
      <div className={styles.chartSection}>
        <h3 className={styles.chartTitle}>Learning Curve</h3>
        <div className={styles.learningCurve}>
          {statistics.learning_curve.length > 0 ? (
            <div className={styles.curveContainer}>
              {statistics.learning_curve.map((entry, index) => (
                <div
                  key={entry.date}
                  className={styles.curvePoint}
                  style={{
                    left: `${(index / Math.max(statistics.learning_curve.length - 1, 1)) * 100}%`,
                  }}
                  title={`${entry.date}: ${entry.avg_mastery}%`}
                >
                  <div
                    className={styles.curveBar}
                    style={{
                      height: `${entry.avg_mastery}%`,
                      backgroundColor: "#ff9800",
                    }}
                  />
                  <span className={styles.curveDate}>{entry.date.split("-").slice(1).join("-")}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className={styles.noData}>No learning data yet. Start learning to see your progress!</p>
          )}
        </div>
      </div>

      {/* Statistics Summary */}
      <div className={styles.summarySection}>
        <div className={styles.summaryGrid}>
          <div className={styles.summaryCard}>
            <span className={styles.summaryIcon}>📚</span>
            <span className={styles.summaryValue}>
              {statistics.overall_progress.chapters_completed}/{statistics.overall_progress.total_chapters}
            </span>
            <span className={styles.summaryLabel}>Chapters</span>
          </div>
          <div className={styles.summaryCard}>
            <span className={styles.summaryIcon}>📈</span>
            <span className={styles.summaryValue}>{statistics.overall_progress.avg_mastery.toFixed(1)}%</span>
            <span className={styles.summaryLabel}>Avg Mastery</span>
          </div>
          <div className={styles.summaryCard}>
            <span className={styles.summaryIcon}>⏱️</span>
            <span className={styles.summaryValue}>{statistics.overall_progress.total_time_hours.toFixed(1)}h</span>
            <span className={styles.summaryLabel}>Hours Spent</span>
          </div>
          <div className={styles.summaryCard}>
            <span className={styles.summaryIcon}>✏️</span>
            <span className={styles.summaryValue}>{statistics.overall_progress.total_practice_attempts}</span>
            <span className={styles.summaryLabel}>Attempts</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatisticsCharts;
