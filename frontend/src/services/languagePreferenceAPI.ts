/**
 * Language Preference API Service (T060)
 *
 * Handles HTTP communication for language preference management:
 * - Get user's language preference
 * - Set/save language preference
 */

import axios, { AxiosInstance } from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export interface LanguagePreference {
  language: "english" | "urdu";
  updated_at?: string;
}

class LanguagePreferenceAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle response errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Clear token if unauthorized
          localStorage.removeItem("access_token");
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get user's current language preference
   */
  async getPreference(): Promise<LanguagePreference> {
    try {
      const response = await this.client.get<LanguagePreference>(
        `/api/v1/users/me/language-preference`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching language preference:", error);
      throw error;
    }
  }

  /**
   * Set/save user's language preference
   */
  async setPreference(language: "english" | "urdu"): Promise<LanguagePreference> {
    // Validate language
    if (!["english", "urdu"].includes(language)) {
      throw new Error("Invalid language. Must be 'english' or 'urdu'");
    }

    try {
      const response = await this.client.put<LanguagePreference>(
        `/api/v1/users/me/language-preference`,
        {
          language,
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error setting language preference:", error);
      throw error;
    }
  }

  /**
   * Get language preference for a specific user (admin only)
   */
  async getUserPreference(userId: number): Promise<LanguagePreference> {
    try {
      const response = await this.client.get<LanguagePreference>(
        `/api/v1/users/${userId}/language-preference`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching preference for user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Get default language preference (for guests)
   */
  getDefaultPreference(): LanguagePreference {
    return {
      language: "english",
      updated_at: undefined,
    };
  }

  /**
   * Apply language preference to document
   */
  applyLanguagePreference(language: "english" | "urdu"): void {
    const htmlElement = document.documentElement;

    if (language === "urdu") {
      htmlElement.setAttribute("dir", "rtl");
      htmlElement.setAttribute("lang", "ur");
      document.body.classList.add("rtl");
    } else {
      htmlElement.setAttribute("dir", "ltr");
      htmlElement.setAttribute("lang", "en");
      document.body.classList.remove("rtl");
    }

    // Store in localStorage for persistence
    localStorage.setItem("language_preference", language);
  }

  /**
   * Get language from localStorage (for initial page load)
   */
  getStoredLanguage(): "english" | "urdu" | null {
    const stored = localStorage.getItem("language_preference");
    if (stored === "english" || stored === "urdu") {
      return stored;
    }
    return null;
  }

  /**
   * Clear stored language preference
   */
  clearStoredLanguage(): void {
    localStorage.removeItem("language_preference");
  }
}

export const languagePreferenceAPI = new LanguagePreferenceAPI();
