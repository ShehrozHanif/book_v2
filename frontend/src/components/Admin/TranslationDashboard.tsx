/**
 * Admin Translation Dashboard Component (T049)
 *
 * Displays translation management interface for instructors/admins:
 * - List all chatbot response templates
 * - Show translation status (draft, reviewed, published)
 * - Display completion percentage
 * - Indicate stale translations
 * - Allow bulk status updates
 */

import React, { useState, useEffect } from "react";
import { adminTranslationAPI } from "../../services/adminTranslationAPI";

export interface Translation {
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

export interface Metrics {
  total_templates: number;
  translated: number;
  reviewed: number;
  published: number;
  translation_percent: number;
  review_percent: number;
  published_percent: number;
  stale_count: number;
}

interface TranslationDashboardProps {
  onTranslationUpdate?: (template_id: number) => void;
}

export const TranslationDashboard: React.FC<TranslationDashboardProps> = ({
  onTranslationUpdate,
}) => {
  const [translations, setTranslations] = useState<Translation[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [selectedTranslations, setSelectedTranslations] = useState<number[]>([]);
  const [page, setPage] = useState(0);
  const [pageSize] = useState(10);

  useEffect(() => {
    loadData();
  }, [statusFilter, page]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [translationsData, metricsData] = await Promise.all([
        adminTranslationAPI.listTranslations({
          status: statusFilter,
          limit: pageSize,
          offset: page * pageSize,
        }),
        adminTranslationAPI.getMetrics(),
      ]);

      setTranslations(translationsData);
      setMetrics(metricsData);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load translations";
      setError(errorMessage);
      console.error("Error loading translations:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusFilterChange = (status: string | null) => {
    setStatusFilter(status);
    setPage(0);
    setSelectedTranslations([]);
  };

  const handleSelectTranslation = (template_id: number) => {
    setSelectedTranslations((prev) =>
      prev.includes(template_id)
        ? prev.filter((id) => id !== template_id)
        : [...prev, template_id]
    );
  };

  const handleSelectAll = () => {
    if (selectedTranslations.length === translations.length) {
      setSelectedTranslations([]);
    } else {
      setSelectedTranslations(translations.map((t) => t.template_id));
    }
  };

  const handleBulkPublish = async () => {
    if (selectedTranslations.length === 0) {
      setError("Please select translations to publish");
      return;
    }

    try {
      await adminTranslationAPI.bulkPublish(selectedTranslations);
      setSelectedTranslations([]);
      await loadData();
      if (onTranslationUpdate) {
        selectedTranslations.forEach(onTranslationUpdate);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to publish translations";
      setError(errorMessage);
    }
  };

  const handleBulkReview = async () => {
    if (selectedTranslations.length === 0) {
      setError("Please select translations to review");
      return;
    }

    try {
      await adminTranslationAPI.bulkReview(selectedTranslations, "reviewed");
      setSelectedTranslations([]);
      await loadData();
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to review translations";
      setError(errorMessage);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case "published":
        return "bg-green-100 text-green-800";
      case "reviewed":
        return "bg-blue-100 text-blue-800";
      case "draft":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading && !metrics) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading translation dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-3xl font-bold mb-6">Translation Dashboard</h1>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-800 rounded">
          {error}
        </div>
      )}

      {/* Metrics Section */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-gray-50 rounded">
            <div className="text-sm text-gray-600">Total Templates</div>
            <div className="text-2xl font-bold">{metrics.total_templates}</div>
          </div>

          <div className="p-4 bg-blue-50 rounded">
            <div className="text-sm text-gray-600">Translated</div>
            <div className="text-2xl font-bold text-blue-600">
              {metrics.translation_percent}%
            </div>
            <div className="text-xs text-gray-500">
              {metrics.translated}/{metrics.total_templates}
            </div>
          </div>

          <div className="p-4 bg-green-50 rounded">
            <div className="text-sm text-gray-600">Published</div>
            <div className="text-2xl font-bold text-green-600">
              {metrics.published_percent}%
            </div>
            <div className="text-xs text-gray-500">
              {metrics.published}/{metrics.total_templates}
            </div>
          </div>

          <div className="p-4 bg-red-50 rounded">
            <div className="text-sm text-gray-600">Stale</div>
            <div className="text-2xl font-bold text-red-600">
              {metrics.stale_count}
            </div>
          </div>
        </div>
      )}

      {/* Filter and Action Bar */}
      <div className="mb-6 flex flex-wrap gap-4 items-center">
        <div>
          <label className="text-sm font-medium text-gray-700 mr-2">
            Filter by Status:
          </label>
          <select
            value={statusFilter || ""}
            onChange={(e) =>
              handleStatusFilterChange(e.target.value || null)
            }
            className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring"
          >
            <option value="">All</option>
            <option value="draft">Draft</option>
            <option value="reviewed">Reviewed</option>
            <option value="published">Published</option>
          </select>
        </div>

        {selectedTranslations.length > 0 && (
          <div className="flex gap-2">
            <button
              onClick={handleBulkReview}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Mark as Reviewed ({selectedTranslations.length})
            </button>
            <button
              onClick={handleBulkPublish}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Publish ({selectedTranslations.length})
            </button>
          </div>
        )}
      </div>

      {/* Translations Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 border-b">
              <th className="p-3 text-left">
                <input
                  type="checkbox"
                  checked={
                    translations.length > 0 &&
                    selectedTranslations.length === translations.length
                  }
                  onChange={handleSelectAll}
                />
              </th>
              <th className="p-3 text-left">Template Key</th>
              <th className="p-3 text-left">English Content</th>
              <th className="p-3 text-left">Urdu Translation</th>
              <th className="p-3 text-left">Status</th>
              <th className="p-3 text-left">Stale</th>
              <th className="p-3 text-left">Last Updated</th>
            </tr>
          </thead>
          <tbody>
            {translations.map((translation) => (
              <tr
                key={translation.template_id}
                className="border-b hover:bg-gray-50"
              >
                <td className="p-3">
                  <input
                    type="checkbox"
                    checked={selectedTranslations.includes(
                      translation.template_id
                    )}
                    onChange={() =>
                      handleSelectTranslation(translation.template_id)
                    }
                  />
                </td>
                <td className="p-3 font-medium text-sm">
                  {translation.template_key}
                </td>
                <td className="p-3 text-sm max-w-xs truncate">
                  {translation.english_content}
                </td>
                <td className="p-3 text-sm max-w-xs truncate" dir="rtl">
                  {translation.urdu_translation || "—"}
                </td>
                <td className="p-3">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(translation.status)}`}
                  >
                    {translation.status}
                  </span>
                </td>
                <td className="p-3">
                  {translation.is_stale ? (
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                      ⚠️ Stale
                    </span>
                  ) : (
                    <span className="text-xs text-gray-500">—</span>
                  )}
                </td>
                <td className="p-3 text-sm text-gray-500">
                  {translation.updated_at
                    ? new Date(translation.updated_at).toLocaleDateString()
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {translations.length === 0 && !loading && (
        <div className="p-4 text-center text-gray-500">
          No translations found
        </div>
      )}

      {/* Pagination */}
      {metrics && metrics.total_templates > pageSize && (
        <div className="mt-6 flex justify-between items-center">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {page + 1} of{" "}
            {Math.ceil(metrics.total_templates / pageSize)}
          </span>
          <button
            onClick={() =>
              setPage(
                Math.min(
                  page + 1,
                  Math.ceil(metrics.total_templates / pageSize) - 1
                )
              )
            }
            disabled={
              page >= Math.ceil(metrics.total_templates / pageSize) - 1
            }
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default TranslationDashboard;
