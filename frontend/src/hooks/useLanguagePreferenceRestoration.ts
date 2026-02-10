/**
 * useLanguagePreferenceRestoration Hook (T062)
 *
 * Restores user's language preference on app load:
 * 1. Check localStorage first (for guests)
 * 2. Fetch from API if authenticated
 * 3. Apply preference immediately to document
 * 4. Sync across tabs
 */

import { useEffect, useState } from "react";
import { languagePreferenceAPI } from "../services/languagePreferenceAPI";

interface UseLanguagePreferenceRestorationReturn {
  language: "english" | "urdu";
  loading: boolean;
  error: string | null;
  updateLanguage: (language: "english" | "urdu") => Promise<void>;
}

export const useLanguagePreferenceRestoration =
  (): UseLanguagePreferenceRestorationReturn => {
    const [language, setLanguage] = useState<"english" | "urdu">("english");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
      initializeLanguagePreference();

      // Listen for storage changes (cross-tab sync)
      window.addEventListener("storage", handleStorageChange);
      return () => {
        window.removeEventListener("storage", handleStorageChange);
      };
    }, []);

    /**
     * Initialize language preference on app load
     */
    const initializeLanguagePreference = async () => {
      setLoading(true);
      setError(null);

      let storedLanguage: "english" | "urdu" | null = null;

      try {
        // Step 1: Check localStorage first (faster, for guests)
        storedLanguage = languagePreferenceAPI.getStoredLanguage();
        if (storedLanguage) {
          setLanguage(storedLanguage);
          languagePreferenceAPI.applyLanguagePreference(storedLanguage);
          setLoading(false);

          // Step 2: If authenticated, fetch from API to sync
          await syncWithServerPreference();
          return;
        }

        // Step 2: Try to fetch from API (for authenticated users)
        await fetchAndApplyPreference();
      } catch (err) {
        // Fall back to localStorage or default if API fails
        const fallbackLanguage = storedLanguage || "english";
        setLanguage(fallbackLanguage);
        languagePreferenceAPI.applyLanguagePreference(fallbackLanguage);
        console.warn("Could not fetch preference from API, using fallback:", err);
      } finally {
        setLoading(false);
      }
    };

    /**
     * Fetch preference from API and apply
     */
    const fetchAndApplyPreference = async () => {
      try {
        const preference = await languagePreferenceAPI.getPreference();
        setLanguage(preference.language);
        languagePreferenceAPI.applyLanguagePreference(preference.language);
      } catch (err) {
        // API call failed, use default or stored
        const defaultLanguage: "english" | "urdu" = "english";
        setLanguage(defaultLanguage);
        languagePreferenceAPI.applyLanguagePreference(defaultLanguage);
        throw err;
      }
    };

    /**
     * Sync with server preference if authenticated
     */
    const syncWithServerPreference = async () => {
      try {
        const preference = await languagePreferenceAPI.getPreference();
        if (preference.language !== language) {
          setLanguage(preference.language);
          languagePreferenceAPI.applyLanguagePreference(preference.language);
        }
      } catch (err) {
        // Silent fail - user's stored preference is still valid
        console.debug("Could not sync preference with server:", err);
      }
    };

    /**
     * Update language preference (locally and on server)
     */
    const updateLanguage = async (newLanguage: "english" | "urdu") => {
      try {
        setError(null);

        // Update immediately on client
        setLanguage(newLanguage);
        languagePreferenceAPI.applyLanguagePreference(newLanguage);

        // Sync with server
        await languagePreferenceAPI.setPreference(newLanguage);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to update language";
        setError(errorMessage);
        setLanguage(language); // Revert on error
        throw err;
      }
    };

    /**
     * Handle storage changes (cross-tab sync)
     */
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "language_preference" && e.newValue) {
        const newLanguage = e.newValue as "english" | "urdu";
        if (["english", "urdu"].includes(newLanguage)) {
          setLanguage(newLanguage);
          languagePreferenceAPI.applyLanguagePreference(newLanguage);
        }
      }
    };

    return {
      language,
      loading,
      error,
      updateLanguage,
    };
  };

export default useLanguagePreferenceRestoration;
