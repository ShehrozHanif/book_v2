/**
 * Custom React Hook for Glossary Operations
 *
 * Provides:
 * - Searching glossary terms
 * - Fetching individual terms
 * - Submitting feedback
 * - Caching for performance
 */

import { useState, useCallback, useEffect } from 'react';
import { glossaryAPI, GlossaryTerm, GlossaryFeedback } from '../services/glossaryAPI';

interface UseGlossaryReturn {
  // State
  terms: GlossaryTerm[];
  loading: boolean;
  error: string | null;
  selectedTerm: GlossaryTerm | null;
  
  // Methods
  searchTerms: (query: string, language?: 'english' | 'urdu') => Promise<void>;
  getTerm: (termId: string) => Promise<void>;
  submitFeedback: (feedback: GlossaryFeedback, token: string) => Promise<void>;
  clearSearch: () => void;
}

export const useGlossary = (): UseGlossaryReturn => {
  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTerm, setSelectedTerm] = useState<GlossaryTerm | null>(null);

  // Cache to avoid repeated requests
  const [cache, setCache] = useState<Map<string, GlossaryTerm>>(new Map());

  /**
   * Search glossary terms
   */
  const searchTerms = useCallback(
    async (query: string, language: 'english' | 'urdu' = 'english') => {
      if (!query.trim()) {
        setError('Search query cannot be empty');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const results = await glossaryAPI.searchTerms(query, language);
        setTerms(results);

        // Cache results
        const newCache = new Map(cache);
        results.forEach((term) => {
          newCache.set(term.english_term, term);
        });
        setCache(newCache);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to search glossary');
        setTerms([]);
      } finally {
        setLoading(false);
      }
    },
    [cache]
  );

  /**
   * Get a specific glossary term
   */
  const getTerm = useCallback(
    async (termId: string) => {
      setLoading(true);
      setError(null);

      try {
        // Check cache first
        if (cache.has(termId)) {
          const cachedTerm = cache.get(termId)!;
          setSelectedTerm(cachedTerm);
          return;
        }

        const term = await glossaryAPI.getTerm(termId);
        if (term) {
          setSelectedTerm(term);
          const newCache = new Map(cache);
          newCache.set(term.english_term, term);
          setCache(newCache);
        } else {
          setError(`Term '${termId}' not found`);
          setSelectedTerm(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch term');
        setSelectedTerm(null);
      } finally {
        setLoading(false);
      }
    },
    [cache]
  );

  /**
   * Submit feedback on a glossary term
   */
  const submitFeedback = useCallback(
    async (feedback: GlossaryFeedback, token: string) => {
      setLoading(true);
      setError(null);

      try {
        await glossaryAPI.submitFeedback(feedback, token);
        // Success message could be shown to user via a toast notification
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to submit feedback');
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /**
   * Clear search results
   */
  const clearSearch = useCallback(() => {
    setTerms([]);
    setSelectedTerm(null);
    setError(null);
  }, []);

  return {
    terms,
    loading,
    error,
    selectedTerm,
    searchTerms,
    getTerm,
    submitFeedback,
    clearSearch,
  };
};
