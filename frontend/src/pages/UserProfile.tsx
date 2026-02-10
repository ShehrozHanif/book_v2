/**
 * User Profile Page (T061)
 *
 * User settings and profile management including:
 * - User information display
 * - Language preference settings
 * - Profile picture management
 * - Account settings
 */

import React, { useState, useEffect } from "react";
import LanguageSettings from "../components/LanguagePreference/LanguageSettings";

interface UserProfileProps {
  userId?: number;
  onLanguageChange?: (language: string) => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({
  userId,
  onLanguageChange,
}) => {
  const [activeTab, setActiveTab] = useState<"profile" | "settings" | "privacy">(
    "profile"
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <h1 className="text-3xl font-bold text-gray-900">User Profile</h1>
          <p className="mt-2 text-gray-600">
            Manage your account settings and preferences
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: "profile", label: "Profile" },
              { id: "settings", label: "Settings" },
              { id: "privacy", label: "Privacy" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        {activeTab === "profile" && (
          <div className="space-y-8">
            {/* Profile Picture Section */}
            <section className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-xl font-semibold mb-6">Profile Picture</h2>
              <div className="flex items-center space-x-6">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
                  <span className="text-4xl text-white">👤</span>
                </div>
                <div>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    Upload New Picture
                  </button>
                  <p className="mt-2 text-sm text-gray-600">
                    JPG, PNG or GIF (max 5MB)
                  </p>
                </div>
              </div>
            </section>

            {/* User Information Section */}
            <section className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-xl font-semibold mb-6">User Information</h2>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value="user_name"
                    disabled
                    className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded text-gray-600 cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value="user@example.com"
                    disabled
                    className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded text-gray-600 cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Name
                  </label>
                  <input
                    type="text"
                    defaultValue="User Name"
                    className="w-full px-4 py-2 border border-gray-300 rounded hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Role
                  </label>
                  <input
                    type="text"
                    value="Student"
                    disabled
                    className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded text-gray-600 cursor-not-allowed"
                  />
                </div>
              </div>
            </section>
          </div>
        )}

        {activeTab === "settings" && (
          <div className="space-y-8">
            {/* Language Preference - T061 Integration */}
            <section className="bg-white rounded-lg shadow-md p-8">
              <LanguageSettings
                onPreferenceChange={onLanguageChange}
                showLabel={true}
              />
            </section>

            {/* Notification Settings */}
            <section className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-xl font-semibold mb-6">Notifications</h2>
              <div className="space-y-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-gray-700">
                    Email notifications for new messages
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-gray-700">
                    Weekly learning summary email
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-gray-700">
                    Push notifications on mobile
                  </span>
                </label>
              </div>
            </section>

            {/* Theme Settings */}
            <section className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-xl font-semibold mb-6">Appearance</h2>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Theme
                </label>
                <select className="w-full px-4 py-2 border border-gray-300 rounded hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Light</option>
                  <option>Dark</option>
                  <option>System</option>
                </select>
              </div>
            </section>
          </div>
        )}

        {activeTab === "privacy" && (
          <div className="space-y-8">
            <section className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-xl font-semibold mb-6">Privacy Settings</h2>
              <div className="space-y-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-gray-700">
                    Profile visible to other users
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-gray-700">
                    Allow others to see my learning activity
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-gray-700">
                    Allow personalized recommendations
                  </span>
                </label>
              </div>
            </section>

            <section className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-xl font-semibold mb-6">Data Management</h2>
              <div className="space-y-4">
                <button className="w-full px-4 py-3 border border-blue-600 text-blue-600 rounded hover:bg-blue-50 font-medium transition">
                  Download My Data
                </button>
                <button className="w-full px-4 py-3 border border-red-600 text-red-600 rounded hover:bg-red-50 font-medium transition">
                  Delete My Account
                </button>
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile;
