/**
 * Progress Dashboard Component (T044)
 * Displays overall progress metrics and chapter completion status
 */

import React, { useState, useEffect } from "react";
import "./ProgressDashboard.css";

interface ProgressData {
  total_chapters_completed: number;
  completion_percentage: number;
  chapters_completed: number[];
  current_path_progress: {
    path_id: string;
    chapters_in_path: number;
    completed: number;
    progress_percentage: number;
    next_chapter: number | null;
  } | null;
  total_time_invested_hours: number;
  total_xp_earned: number;
  average_mastery_score: number;
  chapter_details: {
    [key: string]: {
      completion_status: string;
      mastery_score: number;
      time_spent: number;
      practice_attempts: number;
    };
  };
}

interface ProgressDashboardProps {
  userId: string;
  apiBaseUrl?: string;
}

const ProgressDashboard: React.FC<ProgressDashboardProps> = ({
  userId,
  apiBaseUrl = "/api/v1"
}) => {
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("access_token");

        const response = await fetch(`${apiBaseUrl}/progress`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error("Failed to fetch progress data");
        }

        const data = await response.json();
        setProgressData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, [userId, apiBaseUrl]);

  if (loading) {
    return <div className="progress-dashboard loading">Loading progress...</div>;
  }

  if (error) {
    return <div className="progress-dashboard error">Error: {error}</div>;
  }

  if (!progressData) {
    return <div className="progress-dashboard">No progress data available</div>;
  }

  const getMasteryColor = (score: number): string => {
    if (score >= 80) return "mastery-high";
    if (score >= 60) return "mastery-medium";
    return "mastery-low";
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="progress-dashboard">
      <h2>Your Learning Progress</h2>

      {/* Overall Progress Bar */}
      <div className="overall-progress-section">
        <div className="progress-header">
          <h3>Overall Completion</h3>
          <span className="progress-percentage">
            {progressData.completion_percentage}%
          </span>
        </div>
        <div className="progress-bar-container">
          <div
            className="progress-bar-fill"
            style={{ width: `${progressData.completion_percentage}%` }}
          />
        </div>
        <p className="progress-stats">
          {progressData.total_chapters_completed} of 22 chapters completed
        </p>
      </div>

      {/* Current Learning Path Status */}
      {progressData.current_path_progress && (
        <div className="learning-path-section">
          <h3>Current Learning Path: {progressData.current_path_progress.path_id}</h3>
          <div className="path-progress">
            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{ width: `${progressData.current_path_progress.progress_percentage}%` }}
              />
            </div>
            <p>
              {progressData.current_path_progress.completed} of{" "}
              {progressData.current_path_progress.chapters_in_path} chapters completed
            </p>
            {progressData.current_path_progress.next_chapter && (
              <p className="next-chapter">
                Next: Chapter {progressData.current_path_progress.next_chapter}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <h4>Time Invested</h4>
            <p className="stat-value">{progressData.total_time_invested_hours}h</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h4>XP Earned</h4>
            <p className="stat-value">{progressData.total_xp_earned}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <h4>Avg. Mastery</h4>
            <p className="stat-value">{progressData.average_mastery_score}%</p>
          </div>
        </div>
      </div>

      {/* Chapters Completed List */}
      <div className="chapters-section">
        <h3>Chapter Progress</h3>
        <div className="chapters-grid">
          {Object.entries(progressData.chapter_details)
            .sort(([a], [b]) => parseInt(a) - parseInt(b))
            .map(([chapterId, details]) => (
              <div
                key={chapterId}
                className={`chapter-card ${details.completion_status}`}
                title={`Chapter ${chapterId}: ${details.completion_status}`}
              >
                <div className="chapter-number">Ch {chapterId}</div>
                <div className={`mastery-score ${getMasteryColor(details.mastery_score)}`}>
                  {details.mastery_score}%
                </div>
                <div className="chapter-stats">
                  <div className="time-spent" title="Time spent">
                    ⏱️ {formatTime(details.time_spent)}
                  </div>
                  <div className="practice-attempts" title="Practice attempts">
                    📝 {details.practice_attempts}
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Recent Activity Log */}
      <div className="activity-log">
        <h3>Recent Activity</h3>
        <ul>
          {progressData.chapters_completed
            .slice(-5)
            .reverse()
            .map((chapterId) => (
              <li key={chapterId}>
                ✅ Completed Chapter {chapterId}
                {progressData.chapter_details[chapterId.toString()] && (
                  <span className="mastery-tag">
                    {" "}
                    - Mastery:{" "}
                    {progressData.chapter_details[chapterId.toString()].mastery_score}%
                  </span>
                )}
              </li>
            ))}
        </ul>
      </div>
    </div>
  );
};

export default ProgressDashboard;
