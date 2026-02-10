/**
 * Admin Translation API Service
 *
 * Handles HTTP communication for translation management:
 * - List translations with filtering
 * - Get metrics
 * - Update translation status
 * - Bulk operations
 */

import axios, { AxiosInstance } from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

interface ListTranslationsParams {
  status?: string | null;
  limit?: number;
  offset?: number;
}

interface Metrics {
  total_templates: number;
  translated: number;
  reviewed: number;
  published: number;
  translation_percent: number;
  review_percent: number;
  published_percent: number;
  stale_count: number;
}

interface Translation {
  id: number;
  template_id: number;
  template_key: string;
  english_content: string;
  urdu_translation: string;
  status: "draft" | "reviewed" | "published";
  is_stale: boolean;
  updated_at: string;
  stale_since?: string;
}

class AdminTranslationAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add auth token to requests if available
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  /**
   * List all translations with optional filtering
   */
  async listTranslations(
    params?: ListTranslationsParams
  ): Promise<Translation[]> {
    const queryParams = new URLSearchParams();

    if (params?.status) {
      queryParams.append("status", params.status);
    }
    if (params?.limit !== undefined) {
      queryParams.append("limit", params.limit.toString());
    }
    if (params?.offset !== undefined) {
      queryParams.append("offset", params.offset.toString());
    }

    const url = `/api/v1/admin/translations${queryParams.toString() ? `?${queryParams}` : ""}`;

    try {
      const response = await this.client.get<Translation[]>(url);
      return response.data;
    } catch (error) {
      console.error("Error listing translations:", error);
      throw error;
    }
  }

  /**
   * Get translation metrics
   */
  async getMetrics(): Promise<Metrics> {
    try {
      const response = await this.client.get<Metrics>(
        "/api/v1/admin/translations/metrics"
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching metrics:", error);
      throw error;
    }
  }

  /**
   * Get stale translations list
   */
  async listStaleTranslations(
    limit: number = 10,
    offset: number = 0
  ): Promise<Translation[]> {
    try {
      const response = await this.client.get<Translation[]>(
        `/api/v1/admin/translations/stale?limit=${limit}&offset=${offset}`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching stale translations:", error);
      throw error;
    }
  }

  /**
   * Get single translation details
   */
  async getTranslation(templateId: number): Promise<Translation> {
    try {
      const response = await this.client.get<Translation>(
        `/api/v1/admin/translations/${templateId}`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching translation ${templateId}:`, error);
      throw error;
    }
  }

  /**
   * Update translation content
   */
  async updateTranslation(
    templateId: number,
    urduTranslation: string
  ): Promise<Translation> {
    try {
      const response = await this.client.put<Translation>(
        `/api/v1/admin/translations/${templateId}`,
        {
          urdu_translation: urduTranslation,
        }
      );
      return response.data;
    } catch (error) {
      console.error(`Error updating translation ${templateId}:`, error);
      throw error;
    }
  }

  /**
   * Update translation status
   */
  async updateTranslationStatus(
    templateId: number,
    status: "draft" | "reviewed" | "published"
  ): Promise<Translation> {
    try {
      const response = await this.client.post<Translation>(
        `/api/v1/admin/translations/${templateId}/review`,
        { status }
      );
      return response.data;
    } catch (error) {
      console.error(
        `Error updating translation status for ${templateId}:`,
        error
      );
      throw error;
    }
  }

  /**
   * Bulk update translations to reviewed status
   */
  async bulkReview(
    templateIds: number[],
    status: "reviewed" | "published" = "reviewed"
  ): Promise<{
    updated: number;
    translations: Translation[];
  }> {
    try {
      const response = await this.client.post<{
        updated: number;
        translations: Translation[];
      }>("/api/v1/admin/translations/bulk-review", {
        template_ids: templateIds,
        status,
      });
      return response.data;
    } catch (error) {
      console.error("Error bulk reviewing translations:", error);
      throw error;
    }
  }

  /**
   * Bulk publish translations
   */
  async bulkPublish(templateIds: number[]): Promise<{
    published: number;
    translations: Translation[];
  }> {
    try {
      const response = await this.client.post<{
        published: number;
        translations: Translation[];
      }>("/api/v1/admin/translations/bulk-publish", {
        template_ids: templateIds,
      });
      return response.data;
    } catch (error) {
      console.error("Error bulk publishing translations:", error);
      throw error;
    }
  }
}

export const adminTranslationAPI = new AdminTranslationAPI();
