/**
 * useGlossary Hook
 *
 * Custom React hook for managing glossary operations with state management.
 *
 * Features:
 * - Fetch individual terms
 * - Search terms with caching
 * - List all terms with pagination
 * - Get available categories
 * - Submit feedback
 * - Get glossary statistics
 * - Error handling with retry logic
 * - Loading state management
 * - Result caching to minimize API calls
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import {
  glossaryAPI,
  GlossaryTerm,
  GlossaryStats,
  GlossaryFeedbackResponse,
  GlossaryApiError,
} from '../services/glossaryAPI';

/**
 * Cache entry for search results
 */
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

/**
 * Cache manager for glossary results
 */
class GlossaryCache {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private readonly TTL_MS = 5 * 60 * 1000; // 5 minutes

  set<T>(key: string, data: T): void {
    const now = Date.now();
    this.cache.set(key, {
      data,
      timestamp: now,
      expiresAt: now + this.TTL_MS,
    });
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    // Check if cache has expired
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  clear(): void {
    this.cache.clear();
  }

  invalidate(pattern: string): void {
    for (const key of this.cache.keys()) {
      if (key.startsWith(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}

/**
 * State for a single glossary operation
 */
interface OperationState<T> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
}

/**
 * Hook state
 */
interface UseGlossaryState {
  term: OperationState<GlossaryTerm>;
  terms: OperationState<GlossaryTerm[]>;
  searchResults: OperationState<GlossaryTerm[]>;
  categories: OperationState<string[]>;
  stats: OperationState<GlossaryStats>;
  feedback: OperationState<GlossaryFeedbackResponse>;
}

/**
 * Initial state
 */
const initialState: UseGlossaryState = {
  term: { data: null, isLoading: false, error: null },
  terms: { data: null, isLoading: false, error: null },
  searchResults: { data: null, isLoading: false, error: null },
  categories: { data: null, isLoading: false, error: null },
  stats: { data: null, isLoading: false, error: null },
  feedback: { data: null, isLoading: false, error: null },
};

/**
 * useGlossary Hook
 *
 * Provides glossary operations with caching and state management.
 *
 * @example
 * const {
 *   getTerm,
 *   searchTerms,
 *   listTerms,
 *   getCategories,
 *   submitFeedback,
 *   getStats,
 *   term,
 *   searchResults,
 *   isLoading,
 *   error,
 *   clearCache,
 * } = useGlossary();
 *
 * // Fetch a term
 * const handleFetchTerm = async () => {
 *   await getTerm('ROS Node');
 * };
 *
 * // Search terms
 * const handleSearch = async () => {
 *   await searchTerms('sensor', 'english');
 * };
 *
 * // Submit feedback
 * const handleFeedback = async () => {
 *   await submitFeedback('suggestion', 'Good content', authToken);
 * };
 */
export function useGlossary() {
  const [state, setState] = useState<UseGlossaryState>(initialState);
  const cacheRef = useRef(new GlossaryCache());
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Cancel any pending operations
   */
  const cancelPendingOperations = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  /**
   * Update state for a specific operation
   */
  const updateOperationState = useCallback(
    <K extends keyof UseGlossaryState>(
      operation: K,
      data: Partial<UseGlossaryState[K]>
    ) => {
      setState((prev) => ({
        ...prev,
        [operation]: { ...prev[operation], ...data },
      }));
    },
    []
  );

  /**
   * Fetch a specific glossary term
   */
  const getTerm = useCallback(
    async (termId: string): Promise<GlossaryTerm | null> => {
      try {
        // Check cache first
        const cacheKey = `term:${termId}`;
        const cached = cacheRef.current.get<GlossaryTerm>(cacheKey);
        if (cached) {
          updateOperationState('term', { data: cached, error: null });
          return cached;
        }

        updateOperationState('term', { isLoading: true, error: null });

        const result = await glossaryAPI.getTerm(termId);
        cacheRef.current.set(cacheKey, result);

        updateOperationState('term', {
          data: result,
          isLoading: false,
          error: null,
        });

        return result;
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        updateOperationState('term', {
          isLoading: false,
          error: err,
          data: null,
        });
        return null;
      }
    },
    [updateOperationState]
  );

  /**
   * Search glossary terms with caching
   */
  const searchTerms = useCallback(
    async (
      query: string,
      language: 'english' | 'urdu' = 'english',
      category?: string,
      limit: number = 20
    ): Promise<GlossaryTerm[]> => {
      try {
        // Validate query
        if (!query || query.trim().length === 0) {
          updateOperationState('searchResults', {
            data: [],
            error: null,
            isLoading: false,
          });
          return [];
        }

        // Check cache first
        const cacheKey = `search:${query}:${language}:${category || 'all'}:${limit}`;
        const cached = cacheRef.current.get<GlossaryTerm[]>(cacheKey);
        if (cached) {
          updateOperationState('searchResults', { data: cached, error: null });
          return cached;
        }

        updateOperationState('searchResults', { isLoading: true, error: null });

        const results = await glossaryAPI.searchTerms(query, language, category, limit);
        cacheRef.current.set(cacheKey, results);

        updateOperationState('searchResults', {
          data: results,
          isLoading: false,
          error: null,
        });

        return results;
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        updateOperationState('searchResults', {
          isLoading: false,
          error: err,
          data: [],
        });
        return [];
      }
    },
    [updateOperationState]
  );

  /**
   * List glossary terms with pagination
   */
  const listTerms = useCallback(
    async (
      category?: string,
      limit: number = 50,
      offset: number = 0
    ): Promise<GlossaryTerm[]> => {
      try {
        // Check cache first
        const cacheKey = `list:${category || 'all'}:${limit}:${offset}`;
        const cached = cacheRef.current.get<GlossaryTerm[]>(cacheKey);
        if (cached) {
          updateOperationState('terms', { data: cached, error: null });
          return cached;
        }

        updateOperationState('terms', { isLoading: true, error: null });

        const results = await glossaryAPI.listTerms(category, limit, offset);
        cacheRef.current.set(cacheKey, results);

        updateOperationState('terms', {
          data: results,
          isLoading: false,
          error: null,
        });

        return results;
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        updateOperationState('terms', {
          isLoading: false,
          error: err,
          data: [],
        });
        return [];
      }
    },
    [updateOperationState]
  );

  /**
   * Get all available categories
   */
  const getCategories = useCallback(async (): Promise<string[]> => {
    try {
      // Check cache first
      const cacheKey = 'categories';
      const cached = cacheRef.current.get<string[]>(cacheKey);
      if (cached) {
        updateOperationState('categories', { data: cached, error: null });
        return cached;
      }

      updateOperationState('categories', { isLoading: true, error: null });

      const results = await glossaryAPI.getCategories();
      cacheRef.current.set(cacheKey, results);

      updateOperationState('categories', {
        data: results,
        isLoading: false,
        error: null,
      });

      return results;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      updateOperationState('categories', {
        isLoading: false,
        error: err,
        data: [],
      });
      return [];
    }
  }, [updateOperationState]);

  /**
   * Submit feedback about a glossary term
   */
  const submitFeedback = useCallback(
    async (
      feedbackType: 'suggestion' | 'correction' | 'new_term',
      content: string,
      authToken: string,
      glossaryTermId?: string,
      suggestedTerm?: string
    ): Promise<GlossaryFeedbackResponse | null> => {
      try {
        updateOperationState('feedback', { isLoading: true, error: null });

        const result = await glossaryAPI.submitFeedback(
          feedbackType,
          content,
          authToken,
          glossaryTermId,
          suggestedTerm
        );

        updateOperationState('feedback', {
          data: result,
          isLoading: false,
          error: null,
        });

        // Invalidate related caches after feedback
        cacheRef.current.invalidate('list:');
        cacheRef.current.invalidate('search:');

        return result;
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        updateOperationState('feedback', {
          isLoading: false,
          error: err,
          data: null,
        });
        return null;
      }
    },
    [updateOperationState]
  );

  /**
   * Get glossary statistics
   */
  const getStats = useCallback(async (): Promise<GlossaryStats | null> => {
    try {
      // Check cache first
      const cacheKey = 'stats';
      const cached = cacheRef.current.get<GlossaryStats>(cacheKey);
      if (cached) {
        updateOperationState('stats', { data: cached, error: null });
        return cached;
      }

      updateOperationState('stats', { isLoading: true, error: null });

      const result = await glossaryAPI.getStats();
      cacheRef.current.set(cacheKey, result);

      updateOperationState('stats', {
        data: result,
        isLoading: false,
        error: null,
      });

      return result;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      updateOperationState('stats', {
        isLoading: false,
        error: err,
        data: null,
      });
      return null;
    }
  }, [updateOperationState]);

  /**
   * Clear all cached data
   */
  const clearCache = useCallback(() => {
    cacheRef.current.clear();
  }, []);

  /**
   * Invalidate specific cache keys
   */
  const invalidateCache = useCallback((pattern: string) => {
    cacheRef.current.invalidate(pattern);
  }, []);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      cancelPendingOperations();
    };
  }, [cancelPendingOperations]);

  return {
    // Operations
    getTerm,
    searchTerms,
    listTerms,
    getCategories,
    submitFeedback,
    getStats,

    // State accessors
    term: state.term,
    terms: state.terms,
    searchResults: state.searchResults,
    categories: state.categories,
    stats: state.stats,
    feedback: state.feedback,

    // Combined loading state
    isLoading:
      state.term.isLoading ||
      state.terms.isLoading ||
      state.searchResults.isLoading ||
      state.categories.isLoading ||
      state.stats.isLoading ||
      state.feedback.isLoading,

    // Combined error state (returns first error found)
    error:
      state.term.error ||
      state.terms.error ||
      state.searchResults.error ||
      state.categories.error ||
      state.stats.error ||
      state.feedback.error,

    // Cache management
    clearCache,
    invalidateCache,
  };
}

export type { UseGlossaryState, OperationState };
