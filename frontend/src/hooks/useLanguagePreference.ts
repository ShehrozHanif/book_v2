/**
 * useLanguagePreference Hook
 *
 * Custom React hook for managing user's language preference.
 *
 * Provides:
 * - Get user's current language preference
 * - Set/update language preference
 * - Loading and error states
 * - Automatic persistence to database
 */

import { useState, useCallback, useEffect } from 'react';
import { useAuth } from './useAuth';
import { chatbotTranslationAPI } from '../services/chatbotTranslationAPI';


interface LanguagePreferenceState {
  language: 'english' | 'urdu' | null;
  loading: boolean;
  error: Error | string | null;
}


const useLanguagePreference = () => {
  const { user, isAuthenticated } = useAuth();
  const [state, setState] = useState<LanguagePreferenceState>({
    language: null,
    loading: false,
    error: null,
  });

  /**
   * Load user's language preference from server
   */
  const loadPreference = useCallback(async () => {
    if (!isAuthenticated || !user?.user_id) {
      setState({ language: 'english', loading: false, error: null });
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const preference = await chatbotTranslationAPI.getUserLanguagePreference(
        user.user_id
      );
      setState({
        language: (preference.language as 'english' | 'urdu') || 'english',
        loading: false,
        error: null,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load preference';
      setState({
        language: 'english',
        loading: false,
        error: errorMessage,
      });
    }
  }, [user?.user_id, isAuthenticated]);

  /**
   * Set user's language preference
   */
  const setLanguage = useCallback(
    async (language: 'english' | 'urdu') => {
      if (!isAuthenticated || !user?.user_id) {
        throw new Error('Must be authenticated to set language preference');
      }

      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const response = await chatbotTranslationAPI.setUserLanguagePreference(
          user.user_id,
          language
        );

        setState({
          language: (response.language as 'english' | 'urdu') || language,
          loading: false,
          error: null,
        });

        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to save preference';
        setState(prev => ({
          ...prev,
          loading: false,
          error: errorMessage,
        }));
        throw err;
      }
    },
    [user?.user_id, isAuthenticated]
  );

  /**
   * Reset language preference to default
   */
  const resetLanguage = useCallback(async () => {
    await setLanguage('english');
  }, [setLanguage]);

  /**
   * Clear any error state
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  /**
   * Load preference on mount or when authentication changes
   */
  useEffect(() => {
    loadPreference();
  }, [loadPreference]);

  return {
    language: state.language || 'english',
    setLanguage,
    resetLanguage,
    loading: state.loading,
    error: state.error,
    clearError,
    refetch: loadPreference,
  };
};

export default useLanguagePreference;
export { useLanguagePreference };
