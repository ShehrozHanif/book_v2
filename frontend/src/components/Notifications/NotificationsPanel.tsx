/**
 * Notifications Panel Component (T051)
 *
 * Displays user notifications for translation updates and stale translations:
 * - List of notifications with details
 * - Mark as read functionality
 * - Filter by type
 * - Notification statistics
 */

import React, { useState, useEffect } from "react";
import { notificationAPI, Notification, NotificationStats } from "../../services/notificationAPI";

interface NotificationsPanelProps {
  onNotificationClick?: (notification: Notification) => void;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const NotificationsPanel: React.FC<NotificationsPanelProps> = ({
  onNotificationClick,
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "unread">("all");

  useEffect(() => {
    loadNotifications();

    if (autoRefresh) {
      const interval = setInterval(loadNotifications, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, filter]);

  const loadNotifications = async () => {
    setLoading(true);
    setError(null);

    try {
      const [notificationsData, statsData] = await Promise.all([
        filter === "unread"
          ? notificationAPI.getUnreadNotifications()
          : notificationAPI.getNotifications(),
        notificationAPI.getStats(),
      ]);

      setNotifications(notificationsData);
      setStats(statsData);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load notifications";
      setError(errorMessage);
      console.error("Error loading notifications:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId: number, e: React.MouseEvent) => {
    e.stopPropagation();

    try {
      await notificationAPI.markAsRead(notificationId);
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === notificationId ? { ...n, read: true } : n
        )
      );
      await loadNotifications();
    } catch (err) {
      console.error("Error marking notification as read:", err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationAPI.markAllAsRead();
      await loadNotifications();
    } catch (err) {
      console.error("Error marking all as read:", err);
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (onNotificationClick) {
      onNotificationClick(notification);
    }
    if (!notification.read) {
      handleMarkAsRead(notification.id, {} as React.MouseEvent);
    }
  };

  const getNotificationIcon = (type: string): string => {
    switch (type) {
      case "translation_stale":
        return "⚠️";
      case "translation_updated":
        return "✏️";
      case "translation_published":
        return "✅";
      case "template_changed":
        return "🔄";
      default:
        return "📢";
    }
  };

  const getNotificationColor = (type: string): string => {
    switch (type) {
      case "translation_stale":
        return "bg-red-50 border-red-200";
      case "translation_updated":
        return "bg-blue-50 border-blue-200";
      case "translation_published":
        return "bg-green-50 border-green-200";
      case "template_changed":
        return "bg-yellow-50 border-yellow-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  if (loading && !notifications.length) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading notifications...</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Notifications</h2>
        {stats && (
          <div className="text-sm text-gray-600">
            {stats.unread} of {stats.total} unread
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-800 rounded">
          {error}
        </div>
      )}

      {/* Filter and Actions */}
      <div className="mb-6 flex gap-4 items-center">
        <div>
          <label className="text-sm font-medium text-gray-700 mr-2">
            Filter:
          </label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as "all" | "unread")}
            className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring"
          >
            <option value="all">All</option>
            <option value="unread">Unread</option>
          </select>
        </div>

        {stats && stats.unread > 0 && (
          <button
            onClick={handleMarkAllRead}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
          >
            Mark All as Read
          </button>
        )}
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {notifications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {filter === "unread" ? "No unread notifications" : "No notifications"}
          </div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification.id}
              onClick={() => handleNotificationClick(notification)}
              className={`p-4 border-l-4 rounded cursor-pointer transition ${
                getNotificationColor(notification.type)
              } ${!notification.read ? "border-l-blue-600 bg-opacity-100" : "border-l-gray-300 opacity-75"}`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">
                      {getNotificationIcon(notification.type)}
                    </span>
                    <p className="font-medium text-gray-900">
                      {notification.message}
                    </p>
                  </div>

                  {notification.details && (
                    <div className="mt-2 text-sm text-gray-600">
                      {notification.details.english_content_preview && (
                        <p className="truncate">
                          "{notification.details.english_content_preview}"
                        </p>
                      )}
                      {notification.details.action_url && (
                        <a
                          href={notification.details.action_url}
                          className="text-blue-600 hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          View Details →
                        </a>
                      )}
                    </div>
                  )}

                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(notification.created_at).toLocaleDateString()}{" "}
                    {new Date(notification.created_at).toLocaleTimeString()}
                  </p>
                </div>

                {!notification.read && (
                  <button
                    onClick={(e) => handleMarkAsRead(notification.id, e)}
                    className="ml-2 px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Mark Read
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Statistics */}
      {stats && (
        <div className="mt-6 pt-6 border-t grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {stats.total}
            </div>
            <div className="text-sm text-gray-600">Total</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {stats.unread}
            </div>
            <div className="text-sm text-gray-600">Unread</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {stats.by_type.translation_stale || 0}
            </div>
            <div className="text-sm text-gray-600">Stale</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationsPanel;
