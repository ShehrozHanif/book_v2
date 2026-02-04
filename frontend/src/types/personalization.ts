/**
 * TypeScript types for personalization features
 */

export interface User {
  user_id: string;
  username: string;
  email: string;
  skill_level: number;
  skill_confidence: number;
  profile_picture_url?: string;
  bio?: string;
  preferences: UserPreferences;
  created_at: string;
  last_login_at?: string;
}

export interface UserPreferences {
  explanation_style: "theory_first" | "example_first";
  code_language: "python" | "cpp" | "both";
  learning_pace: "slow" | "medium" | "fast";
  content_focus: "simulation" | "hardware" | "balanced";
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface Achievement {
  type: string;
  title: string;
  description: string;
  icon: string;
  points: number;
  earned_date?: string;
  earned?: boolean;
}

export interface AchievementsResponse {
  earned_count: number;
  total_count: number;
  total_points: number;
  earned: Achievement[];
  locked: Achievement[];
}

export interface PracticeQuestion {
  id: string;
  question: string;
  options: Array<{
    letter: string;
    text: string;
  }>;
  difficulty: "beginner" | "intermediate" | "advanced";
}

export interface PracticeResponse {
  score: number;
  message: string;
  passed: boolean;
}

export interface PracticeHistory {
  attempts: number;
  avg_score: number;
  best_score: number;
  history: Array<{
    attempt_number: number;
    score: number;
    date: string;
    question_count: number;
  }>;
}

export interface OverallProgress {
  total_chapters: number;
  chapters_started: number;
  chapters_in_progress: number;
  chapters_completed: number;
  completion_percentage: number;
  avg_mastery: number;
  total_time_hours: number;
  total_practice_attempts: number;
  avg_practice_score: number;
}

export interface StatisticsData {
  overall_progress: OverallProgress;
  mastery_by_chapter: Record<number, number>;
  time_spent_heatmap: Record<number, number>;
  learning_curve: Array<{
    date: string;
    avg_mastery: number;
    chapters_completed: number;
  }>;
  recommended_focus_areas: Array<{
    chapter_id: number;
    mastery_score: number;
    completion_status: string;
    time_spent_hours: number;
    reason: string;
  }>;
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
  generated_at: string;
}

export interface LearningPath {
  path_id: string;
  user_id: string;
  path_name: string;
  chapters: number[];
  completion_percentage: number;
  status: "active" | "completed" | "abandoned";
  created_at: string;
  updated_at: string;
}

export interface ProgressRecord {
  progress_id: string;
  user_id: string;
  chapter_id: number;
  completion_status: "not_started" | "in_progress" | "completed";
  time_spent_seconds: number;
  mastery_score: number;
  last_accessed_at: string;
  practice_attempts: number;
  highest_practice_score: number;
  created_at: string;
  updated_at: string;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => Promise<void>;
}
