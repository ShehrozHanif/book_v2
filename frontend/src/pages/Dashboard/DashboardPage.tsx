/**
 * Main dashboard page for personalization features
 */

import React, { useState, useEffect } from "react";
import styles from "./DashboardPage.module.css";
import { useAuth } from "../../hooks/useAuth";
import { personalizationApi } from "../../services/personalizationApi";
import { StatisticsData } from "../../types/personalization";
import Header from "../../components/personalization/Header";
import ProfileCard from "../../components/personalization/ProfileCard";
import ProgressCard from "../../components/personalization/ProgressCard";
import LearningPathsCard from "../../components/personalization/LearningPathsCard";
import AchievementsGallery from "../../components/personalization/AchievementsGallery";
import PreferencesForm from "../../components/personalization/PreferencesForm";
import StatisticsCharts from "../../components/personalization/StatisticsCharts";
import LoadingSpinner from "../../components/LoadingSpinner";

type TabType = "overview" | "achievements" | "practice" | "settings";

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [statistics, setStatistics] = useState<StatisticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadStatistics = async () => {
      if (!user) return;

      setIsLoading(true);
      setError(null);

      try {
        const data = await personalizationApi.getStatistics(user.user_id);
        setStatistics(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load statistics";
        setError(message);
        console.error("Error loading statistics:", err);
      } finally {
        setIsLoading(false);
      }
    };

    loadStatistics();
  }, [user]);

  if (!user) {
    return (
      <div className={styles.container}>
        <p className={styles.error}>Please log in to access your dashboard</p>
      </div>
    );
  }

  return (
    <div className={styles.dashboardContainer}>
      <Header userName={user.username} />

      <div className={styles.tabNavigation}>
        <button
          className={`${styles.tabButton} ${activeTab === "overview" ? styles.active : ""}`}
          onClick={() => setActiveTab("overview")}
        >
          📊 Overview
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === "achievements" ? styles.active : ""}`}
          onClick={() => setActiveTab("achievements")}
        >
          🏆 Achievements
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === "practice" ? styles.active : ""}`}
          onClick={() => setActiveTab("practice")}
        >
          📝 Practice
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === "settings" ? styles.active : ""}`}
          onClick={() => setActiveTab("settings")}
        >
          ⚙️ Settings
        </button>
      </div>

      <div className={styles.content}>
        {isLoading && (
          <div className={styles.loadingContainer}>
            <LoadingSpinner />
            <p>Loading dashboard...</p>
          </div>
        )}

        {error && (
          <div className={styles.errorContainer}>
            <p className={styles.errorMessage}>⚠️ {error}</p>
          </div>
        )}

        {!isLoading && !error && (
          <>
            {activeTab === "overview" && (
              <div className={styles.tabContent}>
                <div className={styles.topRow}>
                  <ProfileCard user={user} />
                  {statistics && <ProgressCard progress={statistics.overall_progress} />}
                  {statistics && <LearningPathsCard skillLevel={user.skill_level} />}
                </div>

                {statistics && (
                  <div className={styles.statisticsSection}>
                    <StatisticsCharts statistics={statistics} />
                  </div>
                )}
              </div>
            )}

            {activeTab === "achievements" && (
              <div className={styles.tabContent}>
                {statistics && (
                  <AchievementsGallery achievements={statistics.achievements} />
                )}
              </div>
            )}

            {activeTab === "practice" && (
              <div className={styles.tabContent}>
                <div className={styles.practiceSection}>
                  <h2>📝 Practice & Mastery</h2>
                  {statistics && (
                    <div className={styles.recommendedChapters}>
                      <h3>Recommended Focus Areas</h3>
                      {statistics.recommended_focus_areas.length > 0 ? (
                        <ul>
                          {statistics.recommended_focus_areas.slice(0, 5).map((area) => (
                            <li key={area.chapter_id}>
                              <span className={styles.chapterName}>
                                Chapter {area.chapter_id}
                              </span>
                              <span className={styles.masteryScore}>
                                Mastery: {area.mastery_score}%
                              </span>
                              <span className={styles.reason}>{area.reason}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p>Great work! You're doing well in all chapters.</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === "settings" && (
              <div className={styles.tabContent}>
                <PreferencesForm user={user} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
