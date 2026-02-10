/**
 * API client for personalization endpoints
 */

import {
  User,
  UserPreferences,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  AchievementsResponse,
  PracticeQuestion,
  PracticeResponse,
  PracticeHistory,
  StatisticsData,
} from "../types/personalization";

// Use window location to determine API URL, fallback to localhost:8000
const API_BASE_URL = typeof window !== "undefined" && window.location.hostname !== "localhost"
  ? `${window.location.protocol}//${window.location.hostname}:8000/api/v1`
  : "http://localhost:8000/api/v1";

interface ApiError {
  detail: string;
  status_code?: number;
}

class PersonalizationApi {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem("access_token");
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem("access_token", token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get("content-type");

    if (!response.ok) {
      let errorData: ApiError;

      if (contentType?.includes("application/json")) {
        errorData = await response.json();
      } else {
        errorData = { detail: response.statusText };
      }

      const error = new Error(errorData.detail) as Error & { status?: number };
      error.status = response.status;
      throw error;
    }

    if (contentType?.includes("application/json")) {
      return response.json();
    }

    return {} as T;
  }

  // Authentication endpoints
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/users/login`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(credentials),
    });

    const data = await this.handleResponse<AuthResponse>(response);
    this.setToken(data.access_token);
    return data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/users/register`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    const result = await this.handleResponse<AuthResponse>(response);
    this.setToken(result.access_token);
    return result;
  }

  async logout(): Promise<void> {
    try {
      await fetch(`${API_BASE_URL}/users/logout`, {
        method: "POST",
        headers: this.getHeaders(),
      });
    } finally {
      this.clearToken();
    }
  }

  async getProfile(userId: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/profile`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse<User>(response);
  }

  // Preferences endpoints
  async getPreferences(userId: string): Promise<UserPreferences> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/preferences`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse<UserPreferences>(response);
  }

  async updatePreferences(
    userId: string,
    preferences: Partial<UserPreferences>
  ): Promise<UserPreferences> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/preferences`, {
      method: "PUT",
      headers: this.getHeaders(),
      body: JSON.stringify(preferences),
    });

    return this.handleResponse<UserPreferences>(response);
  }

  async resetPreferences(userId: string): Promise<UserPreferences> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/preferences/reset`, {
      method: "POST",
      headers: this.getHeaders(),
    });

    return this.handleResponse<UserPreferences>(response);
  }

  // Achievement endpoints
  async getAchievements(userId: string): Promise<AchievementsResponse> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/achievements`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse<AchievementsResponse>(response);
  }

  // Practice endpoints
  async getPracticeQuestions(userId: string, chapterId: number): Promise<{
    chapter_id: number;
    question_count: number;
    questions: PracticeQuestion[];
  }> {
    const response = await fetch(
      `${API_BASE_URL}/users/${userId}/chapters/${chapterId}/practice`,
      {
        headers: this.getHeaders(),
      }
    );

    return this.handleResponse(response);
  }

  async submitPracticeAnswers(
    userId: string,
    chapterId: number,
    answers: Record<string, string>
  ): Promise<PracticeResponse> {
    const response = await fetch(
      `${API_BASE_URL}/users/${userId}/chapters/${chapterId}/practice`,
      {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify({ answers }),
      }
    );

    return this.handleResponse<PracticeResponse>(response);
  }

  async getPracticeHistory(
    userId: string,
    chapterId: number
  ): Promise<PracticeHistory> {
    const response = await fetch(
      `${API_BASE_URL}/users/${userId}/chapters/${chapterId}/practice/history`,
      {
        headers: this.getHeaders(),
      }
    );

    return this.handleResponse<PracticeHistory>(response);
  }

  // Statistics endpoints
  async getStatistics(userId: string): Promise<StatisticsData> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/statistics`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse<StatisticsData>(response);
  }

  async getProgressOverview(userId: string): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/users/${userId}/statistics/overview`,
      {
        headers: this.getHeaders(),
      }
    );

    return this.handleResponse(response);
  }

  // Assessment endpoints
  async submitAssessment(userId: string, answers: Record<string, string>): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/assessments`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        user_id: userId,
        answers,
      }),
    });

    return this.handleResponse(response);
  }

  // Learning path endpoints
  async recommendLearningPath(userId: string): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/learning-paths/recommend`,
      {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify({ user_id: userId }),
      }
    );

    return this.handleResponse(response);
  }

  async selectLearningPath(userId: string, pathName: string): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/users/${userId}/learning-paths`,
      {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify({ path_name: pathName }),
      }
    );

    return this.handleResponse(response);
  }

  // Progress endpoints
  async getProgress(userId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/progress`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse(response);
  }

  async updateProgress(userId: string, chapterId: number, data: any): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/users/${userId}/progress/${chapterId}`,
      {
        method: "PUT",
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      }
    );

    return this.handleResponse(response);
  }

  // Privacy endpoints
  async getPrivacyPolicy(userId: string): Promise<{
    title: string;
    last_updated: string;
    content: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/privacy-policy`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse(response);
  }

  async getTermsOfService(userId: string): Promise<{
    title: string;
    last_updated: string;
    content: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/terms-of-service`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse(response);
  }
}

// Export singleton instance
export const personalizationApi = new PersonalizationApi();
