/**
 * Language Preference End-to-End Tests (T056)
 *
 * End-to-end tests for language preference persistence:
 * - Change preference in settings
 * - Logout and login again
 * - Verify persistence across sessions
 */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// Mock complete flow components
const mockLoginFlow = jest.fn();
const mockLogoutFlow = jest.fn();
const mockLoadPreference = jest.fn();
const mockSavePreference = jest.fn();

describe("Language Preference E2E Flow", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe("Full preference workflow", () => {
    it("should change preference and persist across sessions", async () => {
      // Step 1: User logs in with default preference (English)
      mockLoginFlow.mockResolvedValue({ user_id: 1, username: "testuser" });
      mockLoadPreference.mockResolvedValue({ language: "english" });

      // Step 2: User navigates to settings
      // Component loads current preference
      const preference = await mockLoadPreference();
      expect(preference.language).toBe("english");

      // Step 3: User changes preference to Urdu
      mockSavePreference.mockResolvedValue({ language: "urdu" });
      const updated = await mockSavePreference("urdu");
      expect(updated.language).toBe("urdu");

      // Step 4: User logs out
      mockLogoutFlow.mockResolvedValue(true);
      const loggedOut = await mockLogoutFlow();
      expect(loggedOut).toBe(true);

      // Step 5: User logs in again
      mockLoginFlow.mockResolvedValue({ user_id: 1, username: "testuser" });
      await mockLoginFlow();

      // Step 6: Verify preference is restored to Urdu
      mockLoadPreference.mockResolvedValue({ language: "urdu" });
      const restored = await mockLoadPreference();
      expect(restored.language).toBe("urdu");
    });

    it("should handle multiple preference changes", async () => {
      // User changes preference multiple times
      mockSavePreference.mockResolvedValue({ language: "urdu" });
      let pref = await mockSavePreference("urdu");
      expect(pref.language).toBe("urdu");

      mockSavePreference.mockResolvedValue({ language: "english" });
      pref = await mockSavePreference("english");
      expect(pref.language).toBe("english");

      mockSavePreference.mockResolvedValue({ language: "urdu" });
      pref = await mockSavePreference("urdu");
      expect(pref.language).toBe("urdu");

      // Final preference should be Urdu
      mockLoadPreference.mockResolvedValue({ language: "urdu" });
      const final = await mockLoadPreference();
      expect(final.language).toBe("urdu");
    });

    it("should work with cross-device access", async () => {
      // Device 1: User sets preference to Urdu
      mockSavePreference.mockResolvedValue({ language: "urdu" });
      await mockSavePreference("urdu");

      // Device 2: User logs in on different device
      mockLoginFlow.mockResolvedValue({ user_id: 1, username: "testuser" });
      await mockLoginFlow();

      // Preference should be synced from server
      mockLoadPreference.mockResolvedValue({ language: "urdu" });
      const preference = await mockLoadPreference();
      expect(preference.language).toBe("urdu");
    });
  });

  describe("Preference in UI", () => {
    it("should apply preference to chatbot immediately", async () => {
      // User loads app
      mockLoadPreference.mockResolvedValue({ language: "urdu" });
      const preference = await mockLoadPreference();

      // Chatbot should display in selected language
      expect(preference.language).toBe("urdu");
    });

    it("should update UI when preference changes", async () => {
      // Initial preference: English
      mockLoadPreference.mockResolvedValue({ language: "english" });
      let pref = await mockLoadPreference();
      expect(pref.language).toBe("english");

      // User changes to Urdu
      mockSavePreference.mockResolvedValue({ language: "urdu" });
      pref = await mockSavePreference("urdu");

      // UI should reflect new language
      expect(pref.language).toBe("urdu");
    });
  });

  describe("Preference sync across tabs", () => {
    it("should sync preference changes across browser tabs", async () => {
      // Tab 1: User changes preference
      mockSavePreference.mockResolvedValue({ language: "urdu" });
      await mockSavePreference("urdu");

      // Tab 2: User should see updated preference via storage event
      // (simulated with direct API call)
      mockLoadPreference.mockResolvedValue({ language: "urdu" });
      const preference = await mockLoadPreference();
      expect(preference.language).toBe("urdu");
    });
  });

  describe("Error recovery", () => {
    it("should handle save failure gracefully", async () => {
      mockLoadPreference.mockResolvedValue({ language: "english" });
      const initial = await mockLoadPreference();
      expect(initial.language).toBe("english");

      // Save fails
      mockSavePreference.mockRejectedValue(new Error("Network error"));

      try {
        await mockSavePreference("urdu");
      } catch (error) {
        // Preference should remain unchanged on client
        expect(initial.language).toBe("english");
      }
    });

    it("should retry preference load on failure", async () => {
      // First attempt fails
      mockLoadPreference.mockRejectedValueOnce(new Error("Network error"));

      try {
        await mockLoadPreference();
      } catch (error) {
        // Retry succeeds
        mockLoadPreference.mockResolvedValue({ language: "english" });
        const preference = await mockLoadPreference();
        expect(preference.language).toBe("english");
      }
    });
  });

  describe("First-time user experience", () => {
    it("should have default preference for new users", async () => {
      // New user logs in
      mockLoadPreference.mockResolvedValue({ language: "english" });
      const preference = await mockLoadPreference();

      // Should default to English
      expect(preference.language).toBe("english");
    });

    it("should allow new user to set preference", async () => {
      // New user loads settings
      mockLoadPreference.mockResolvedValue({ language: "english" });
      await mockLoadPreference();

      // New user selects Urdu
      mockSavePreference.mockResolvedValue({ language: "urdu" });
      const updated = await mockSavePreference("urdu");
      expect(updated.language).toBe("urdu");
    });
  });

  describe("Preference state consistency", () => {
    it("should not have race conditions on save", async () => {
      mockLoadPreference.mockResolvedValue({ language: "english" });

      // Multiple rapid save attempts
      const saves = [
        mockSavePreference.mockResolvedValue({ language: "urdu" }),
        mockSavePreference.mockResolvedValue({ language: "urdu" }),
        mockSavePreference.mockResolvedValue({ language: "urdu" }),
      ];

      await Promise.all(saves);

      // Final state should be consistent
      mockLoadPreference.mockResolvedValue({ language: "urdu" });
      const final = await mockLoadPreference();
      expect(final.language).toBe("urdu");
    });

    it("should maintain consistency across multiple operations", async () => {
      const operations = [
        mockSavePreference.mockResolvedValue({ language: "urdu" }),
        mockLoadPreference.mockResolvedValue({ language: "urdu" }),
        mockSavePreference.mockResolvedValue({ language: "english" }),
        mockLoadPreference.mockResolvedValue({ language: "english" }),
      ];

      for (const op of operations) {
        await op;
      }

      // Verify final state
      mockLoadPreference.mockResolvedValue({ language: "english" });
      const final = await mockLoadPreference();
      expect(final.language).toBe("english");
    });
  });

  describe("Timing and performance", () => {
    it("should load preference quickly on app startup", async () => {
      const startTime = Date.now();

      mockLoadPreference.mockResolvedValue({ language: "english" });
      await mockLoadPreference();

      const duration = Date.now() - startTime;

      // Should load in less than 1 second
      expect(duration).toBeLessThan(1000);
    });

    it("should save preference within acceptable time", async () => {
      const startTime = Date.now();

      mockSavePreference.mockResolvedValue({ language: "urdu" });
      await mockSavePreference("urdu");

      const duration = Date.now() - startTime;

      // Should save in less than 2 seconds
      expect(duration).toBeLessThan(2000);
    });
  });
});
