/**
 * Notification API Service
 *
 * Handles HTTP communication for notifications:
 * - Get user notifications
 * - Mark as read
 * - Get statistics
 */

import axios, { AxiosInstance } from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export interface NotificationDetails {
  [key: string]: any;
}

export interface Notification {
  id: number;
  type: "translation_stale" | "translation_updated" | "translation_published" | "template_changed";
  channel: "in_app" | "email" | "webhook";
  message: string;
  details: NotificationDetails;
  created_at: string;
  read: boolean;
  read_at?: string;
  status: "pending" | "sent" | "failed";
}

export interface NotificationStats {
  total: number;
  unread: number;
  by_type: Record<string, number>;
}

class NotificationAPI {
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
  }

  /**
   * Get notifications for current user
   */
  async getNotifications(
    unreadOnly: boolean = false,
    limit: number = 20,
    offset: number = 0
  ): Promise<Notification[]> {
    try {
      const response = await this.client.get<Notification[]>(
        `/api/v1/notifications`,
        {
          params: {
            unread_only: unreadOnly,
            limit,
            offset,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching notifications:", error);
      throw error;
    }
  }

  /**
   * Get unread notifications
   */
  async getUnreadNotifications(limit: number = 20): Promise<Notification[]> {
    return this.getNotifications(true, limit, 0);
  }

  /**
   * Mark a notification as read
   */
  async markAsRead(notificationId: number): Promise<Notification> {
    try {
      const response = await this.client.post<Notification>(
        `/api/v1/notifications/${notificationId}/read`
      );
      return response.data;
    } catch (error) {
      console.error(`Error marking notification ${notificationId} as read:`, error);
      throw error;
    }
  }

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<{ marked_read: number }> {
    try {
      const response = await this.client.post<{ marked_read: number }>(
        `/api/v1/notifications/read-all`
      );
      return response.data;
    } catch (error) {
      console.error("Error marking all notifications as read:", error);
      throw error;
    }
  }

  /**
   * Get notification statistics
   */
  async getStats(): Promise<NotificationStats> {
    try {
      const response = await this.client.get<NotificationStats>(
        `/api/v1/notifications/stats`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching notification stats:", error);
      throw error;
    }
  }
}

export const notificationAPI = new NotificationAPI();
