/**
 * Progress Visualization Charts Component (T045)
 * Uses Recharts for interactive data visualization
 */

import React from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from "recharts";
import "./ProgressCharts.css";

interface ChapterDetail {
  completion_status: string;
  mastery_score: number;
  time_spent: number;
  practice_attempts: number;
}

interface ProgressChartsProps {
  chapterDetails: {
    [key: string]: ChapterDetail;
  };
  chaptersCompleted: number[];
}

const ProgressCharts: React.FC<ProgressChartsProps> = ({
  chapterDetails,
  chaptersCompleted
}) => {
  // Chart 1: Mastery Scores by Chapter (Bar Chart)
  const masteryData = Object.entries(chapterDetails)
    .filter(([_, details]) => details.mastery_score > 0)
    .map(([chapterId, details]) => ({
      chapter: `Ch ${chapterId}`,
      mastery: details.mastery_score,
      chapterId: parseInt(chapterId)
    }))
    .sort((a, b) => a.chapterId - b.chapterId);

  // Chart 2: Time Spent by Chapter (Pie Chart)
  const timeData = Object.entries(chapterDetails)
    .filter(([_, details]) => details.time_spent > 0)
    .map(([chapterId, details]) => ({
      name: `Chapter ${chapterId}`,
      value: Math.round(details.time_spent / 60), // Convert to minutes
      chapterId: parseInt(chapterId)
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8); // Top 8 chapters by time

  // Chart 3: Progress Over Time (Line Chart)
  // Simulate progress over time based on completed chapters
  const progressOverTime = chaptersCompleted
    .sort((a, b) => a - b)
    .map((chapterId, index) => ({
      chapter: index + 1,
      completed: index + 1,
      percentage: ((index + 1) / 22) * 100
    }));

  // Chart 4: Skill Level Trend (Area Chart)
  // Calculate cumulative average mastery
  const skillTrendData = masteryData.map((item, index) => {
    const cumulativeAvg = masteryData
      .slice(0, index + 1)
      .reduce((sum, d) => sum + d.mastery, 0) / (index + 1);
    return {
      chapter: item.chapter,
      skillLevel: Math.round(cumulativeAvg),
      chapterId: item.chapterId
    };
  });

  // Colors for charts
  const COLORS = [
    "#4CAF50",
    "#2196F3",
    "#FFC107",
    "#f44336",
    "#9C27B0",
    "#00BCD4",
    "#FF9800",
    "#E91E63"
  ];

  const getMasteryColor = (mastery: number): string => {
    if (mastery >= 80) return "#4CAF50";
    if (mastery >= 60) return "#FFC107";
    return "#f44336";
  };

  return (
    <div className="progress-charts">
      <h2>Learning Analytics</h2>

      {/* Chart 1: Mastery Scores by Chapter */}
      <div className="chart-container">
        <h3>Mastery Scores by Chapter</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={masteryData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="chapter" />
            <YAxis domain={[0, 100]} />
            <Tooltip
              formatter={(value: number) => [`${value}%`, "Mastery"]}
              contentStyle={{
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                border: "1px solid #ccc",
                borderRadius: "8px"
              }}
            />
            <Legend />
            <Bar dataKey="mastery" name="Mastery Score">
              {masteryData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getMasteryColor(entry.mastery)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <p className="chart-description">
          Your mastery scores across completed chapters. Higher is better!
        </p>
      </div>

      {/* Chart 2: Time Spent by Chapter */}
      <div className="chart-container">
        <h3>Time Spent by Chapter (Top 8)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={timeData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) =>
                `${name}: ${(percent * 100).toFixed(0)}%`
              }
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {timeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number) => [`${value} min`, "Time Spent"]}
              contentStyle={{
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                border: "1px solid #ccc",
                borderRadius: "8px"
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <p className="chart-description">
          Distribution of time invested across chapters (in minutes).
        </p>
      </div>

      {/* Chart 3: Progress Over Time */}
      <div className="chart-container">
        <h3>Progress Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={progressOverTime}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="chapter"
              label={{ value: "Chapters Completed", position: "insideBottom", offset: -5 }}
            />
            <YAxis
              label={{ value: "Progress %", angle: -90, position: "insideLeft" }}
              domain={[0, 100]}
            />
            <Tooltip
              formatter={(value: number, name: string) => {
                if (name === "completed") return [value, "Chapters Completed"];
                return [`${value.toFixed(1)}%`, "Completion"];
              }}
              contentStyle={{
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                border: "1px solid #ccc",
                borderRadius: "8px"
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="percentage"
              name="Completion %"
              stroke="#2196F3"
              strokeWidth={2}
              dot={{ fill: "#2196F3", r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
        <p className="chart-description">
          Your learning journey progression over completed chapters.
        </p>
      </div>

      {/* Chart 4: Skill Level Trend */}
      <div className="chart-container">
        <h3>Skill Level Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={skillTrendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="chapter" />
            <YAxis domain={[0, 100]} />
            <Tooltip
              formatter={(value: number) => [`${value}`, "Skill Level"]}
              contentStyle={{
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                border: "1px solid #ccc",
                borderRadius: "8px"
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="skillLevel"
              name="Skill Level"
              stroke="#4CAF50"
              fill="#4CAF50"
              fillOpacity={0.6}
            />
          </AreaChart>
        </ResponsiveContainer>
        <p className="chart-description">
          Your cumulative skill level based on average mastery scores.
        </p>
      </div>

      {/* Summary Stats */}
      <div className="chart-summary">
        <h3>Key Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon">🎯</div>
            <div className="insight-content">
              <h4>Average Mastery</h4>
              <p className="insight-value">
                {masteryData.length > 0
                  ? Math.round(
                      masteryData.reduce((sum, d) => sum + d.mastery, 0) / masteryData.length
                    )
                  : 0}
                %
              </p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">⏱️</div>
            <div className="insight-content">
              <h4>Total Time</h4>
              <p className="insight-value">
                {Math.round(
                  Object.values(chapterDetails).reduce((sum, d) => sum + d.time_spent, 0) / 3600
                )}
                h
              </p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">📈</div>
            <div className="insight-content">
              <h4>Chapters Completed</h4>
              <p className="insight-value">{chaptersCompleted.length}</p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">🔥</div>
            <div className="insight-content">
              <h4>Highest Mastery</h4>
              <p className="insight-value">
                {masteryData.length > 0
                  ? Math.max(...masteryData.map((d) => d.mastery))
                  : 0}
                %
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressCharts;
