import { useState, useCallback, useEffect, useRef } from 'react';
import { useLanguagePreference } from './useLanguagePreference';
import { useAuth } from './useAuth';
import { chatbotTranslationAPI } from '../services/chatbotTranslationAPI';


interface ChatbotResponse {
  content: string;
  template_key: string;
  language: 'english' | 'urdu';
  version: number;
  note?: string;
}

interface ResponseCache {
  [key: string]: ChatbotResponse;
}

interface UseChatbotLanguageState {
  response: ChatbotResponse | null;
  loading: boolean;
  error: Error | string | null;
}


const useChatbotLanguage = () => {
  const { language } = useLanguagePreference();
  const { isAuthenticated } = useAuth();
  const [state, setState] = useState<UseChatbotLanguageState>({
    response: null,
    loading: false,
    error: null,
  });

  // Response cache to avoid redundant API calls
  const cacheRef = useRef<ResponseCache>({});

  /**
   * Get translated response for a template
   */
  const getResponse = useCallback(
    async (
      templateKey: string,
      targetLanguage?: 'english' | 'urdu'
    ): Promise<ChatbotResponse> => {
      const lang = targetLanguage || language;
      const cacheKey = `${templateKey}_${lang}`;

      // Check cache first
      if (cacheRef.current[cacheKey]) {
        setState(prev => ({
          ...prev,
          response: cacheRef.current[cacheKey],
        }));
        return cacheRef.current[cacheKey];
      }

      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const response = await chatbotTranslationAPI.getChatbotResponse(
          templateKey,
          lang,
          isAuthenticated
        );

        // Cache the response
        cacheRef.current[cacheKey] = response;

        setState({
          response,
          loading: false,
          error: null,
        });

        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch response';
        setState({
          response: null,
          loading: false,
          error: errorMessage,
        });

        // Try fallback to English
        if (lang === 'urdu') {
          try {
            const englishResponse = await chatbotTranslationAPI.getChatbotResponse(
              templateKey,
              'english',
              true
            );
            cacheRef.current[cacheKey] = englishResponse;
            setState({
              response: englishResponse,
              loading: false,
              error: null,
            });
            return englishResponse;
          } catch (_) {
            // Fallback also failed
            throw err;
          }
        }

        throw err;
      }
    },
    [language, isAuthenticated]
  );

  /**
   * Handle language change - fetch new response in selected language
   */
  const handleLanguageChange = useCallback(
    async (
      newLanguage: 'english' | 'urdu',
      templateKey?: string
    ) => {
      if (templateKey) {
        await getResponse(templateKey, newLanguage);
      }
    },
    [getResponse]
  );

  /**
   * Clear cache
   */
  const clearCache = useCallback(() => {
    cacheRef.current = {};
  }, []);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  /**
   * Get cache statistics (for debugging/optimization)
   */
  const getCacheStats = useCallback(() => {
    return {
      size: Object.keys(cacheRef.current).length,
      keys: Object.keys(cacheRef.current),
    };
  }, []);

  return {
    response: state.response,
    language,
    getResponse,
    handleLanguageChange,
    loading: state.loading,
    error: state.error,
    clearError,
    clearCache,
    getCacheStats,
    isAuthenticated,
  };
};

export default useChatbotLanguage;
export { useChatbotLanguage };
