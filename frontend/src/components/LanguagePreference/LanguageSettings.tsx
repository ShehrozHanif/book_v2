/**
 * Language Settings Component (T058)
 *
 * Allows users to select and save their language preference:
 * - English or Urdu language selection
 * - Save button with loading state
 * - Success/error feedback
 * - RTL support for Urdu
 */

import React, { useState, useEffect } from "react";
import { languagePreferenceAPI } from "../../services/languagePreferenceAPI";

interface LanguageSettingsProps {
  onPreferenceChange?: (language: string) => void;
  showLabel?: boolean;
}

export const LanguageSettings: React.FC<LanguageSettingsProps> = ({
  onPreferenceChange,
  showLabel = true,
}) => {
  const [language, setLanguage] = useState<string>("english");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    loadPreference();
  }, []);

  const loadPreference = async () => {
    setLoading(true);
    setError(null);

    try {
      const preference = await languagePreferenceAPI.getPreference();
      setLanguage(preference.language || "english");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load preference";
      setError(errorMessage);
      console.error("Error loading preference:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const result = await languagePreferenceAPI.setPreference(language);
      setSuccess(true);

      if (onPreferenceChange) {
        onPreferenceChange(language);
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to save preference";
      setError(errorMessage);
      console.error("Error saving preference:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleLanguageChange = (newLanguage: string) => {
    setLanguage(newLanguage);
    setSuccess(false);
  };

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex items-center justify-center h-32">
          <div className="text-gray-600">Loading language settings...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      {showLabel && (
        <h3 className="text-lg font-semibold mb-6">Language Preference</h3>
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-800 rounded flex justify-between items-center">
          <span>{error}</span>
          <button
            onClick={loadPreference}
            className="ml-2 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
          >
            Retry
          </button>
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-green-100 text-green-800 rounded">
          ✓ Language preference saved successfully!
        </div>
      )}

      {/* Language Options */}
      <div className="space-y-4 mb-6">
        {/* English Option */}
        <label className="flex items-center p-4 border-2 border-gray-200 rounded cursor-pointer hover:border-blue-400 transition">
          <input
            type="radio"
            name="language"
            value="english"
            checked={language === "english"}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="w-4 h-4 text-blue-600"
            disabled={saving}
          />
          <div className="ml-4">
            <div className="font-medium text-gray-900">English</div>
            <div className="text-sm text-gray-600">
              Chat in English language
            </div>
          </div>
        </label>

        {/* Urdu Option */}
        <label
          className="flex items-center p-4 border-2 border-gray-200 rounded cursor-pointer hover:border-blue-400 transition"
          dir="rtl"
        >
          <input
            type="radio"
            name="language"
            value="urdu"
            checked={language === "urdu"}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="w-4 h-4 text-blue-600"
            disabled={saving}
          />
          <div className="mr-4 text-right">
            <div className="font-medium text-gray-900">اردو</div>
            <div className="text-sm text-gray-600">اردو میں چیٹ کریں</div>
          </div>
        </label>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        disabled={saving || language === (language || "english")}
        className={`w-full py-3 px-4 rounded font-medium transition ${
          saving
            ? "bg-gray-400 text-gray-600 cursor-not-allowed"
            : "bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800"
        }`}
      >
        {saving ? "Saving..." : "Save Language Preference"}
      </button>

      {/* Info Text */}
      <p className="mt-4 text-sm text-gray-600">
        Your language preference will be saved to your account and applied
        across all devices.
      </p>
    </div>
  );
};

export default LanguageSettings;
