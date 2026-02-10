/**
 * Tests for useGlossary hook (T038)
 *
 * Test coverage:
 * - getTerm() with caching
 * - searchTerms() with validation and caching
 * - listTerms() with pagination
 * - getCategories() with caching
 * - submitFeedback() with cache invalidation
 * - getStats() with caching
 * - Error handling
 * - Cache management
 * - Cleanup on unmount
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useGlossary } from './useGlossary';
import * as glossaryAPI from '../services/glossaryAPI';

// Mock the glossaryAPI module
jest.mock('../services/glossaryAPI');

const mockGlossaryAPI = glossaryAPI as jest.Mocked<typeof glossaryAPI>;

describe('useGlossary hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  /**
   * getTerm() tests
   */
  describe('getTerm()', () => {
    const mockTerm = {
      id: 'term-1',
      english_term: 'ROS Node',
      urdu_translation: 'ROS نوڈ',
      pronunciation_transliterated: 'ros nod',
      definition_english: 'A process in ROS',
      definition_urdu: 'ROS میں ایک عمل',
      category: 'robotics',
      status: 'active',
    };

    it('should fetch term and set state', async () => {
      mockGlossaryAPI.glossaryAPI.getTerm.mockResolvedValueOnce(mockTerm);

      const { result } = renderHook(() => useGlossary());

      expect(result.current.term.data).toBeNull();
      expect(result.current.term.isLoading).toBe(false);

      let termResult;
      await act(async () => {
        termResult = await result.current.getTerm('ROS Node');
      });

      expect(termResult).toEqual(mockTerm);
      expect(result.current.term.data).toEqual(mockTerm);
      expect(result.current.term.error).toBeNull();
    });

    it('should cache term results', async () => {
      mockGlossaryAPI.glossaryAPI.getTerm.mockResolvedValueOnce(mockTerm);

      const { result } = renderHook(() => useGlossary());

      // First call
      await act(async () => {
        await result.current.getTerm('ROS Node');
      });

      expect(mockGlossaryAPI.glossaryAPI.getTerm).toHaveBeenCalledTimes(1);

      // Second call should use cache
      await act(async () => {
        await result.current.getTerm('ROS Node');
      });

      expect(mockGlossaryAPI.glossaryAPI.getTerm).toHaveBeenCalledTimes(1); // Still 1, not 2
    });

    it('should handle getTerm errors', async () => {
      const error = new Error('Term not found');
      mockGlossaryAPI.glossaryAPI.getTerm.mockRejectedValueOnce(error);

      const { result } = renderHook(() => useGlossary());

      let termResult;
      await act(async () => {
        termResult = await result.current.getTerm('Invalid');
      });

      expect(termResult).toBeNull();
      expect(result.current.term.error).toBeTruthy();
      expect(result.current.term.data).toBeNull();
    });
  });

  /**
   * searchTerms() tests
   */
  describe('searchTerms()', () => {
    const mockResults = [
      {
        id: 'term-1',
        english_term: 'Sensor',
        urdu_translation: 'سینسر',
        pronunciation_transliterated: 'sensor',
        definition_english: 'A device',
        definition_urdu: 'ایک آلہ',
        category: 'robotics',
        status: 'active',
      },
    ];

    it('should search terms', async () => {
      mockGlossaryAPI.glossaryAPI.searchTerms.mockResolvedValueOnce(mockResults);

      const { result } = renderHook(() => useGlossary());

      let searchResult;
      await act(async () => {
        searchResult = await result.current.searchTerms('sensor', 'english');
      });

      expect(searchResult).toEqual(mockResults);
      expect(result.current.searchResults.data).toEqual(mockResults);
      expect(result.current.searchResults.error).toBeNull();
    });

    it('should return empty array for empty query', async () => {
      const { result } = renderHook(() => useGlossary());

      let searchResult;
      await act(async () => {
        searchResult = await result.current.searchTerms('');
      });

      expect(searchResult).toEqual([]);
      expect(mockGlossaryAPI.glossaryAPI.searchTerms).not.toHaveBeenCalled();
    });

    it('should return empty array for whitespace query', async () => {
      const { result } = renderHook(() => useGlossary());

      let searchResult;
      await act(async () => {
        searchResult = await result.current.searchTerms('   ');
      });

      expect(searchResult).toEqual([]);
    });

    it('should cache search results', async () => {
      mockGlossaryAPI.glossaryAPI.searchTerms.mockResolvedValueOnce(mockResults);

      const { result } = renderHook(() => useGlossary());

      // First call
      await act(async () => {
        await result.current.searchTerms('sensor', 'english');
      });

      expect(mockGlossaryAPI.glossaryAPI.searchTerms).toHaveBeenCalledTimes(1);

      // Second call with same params should use cache
      await act(async () => {
        await result.current.searchTerms('sensor', 'english');
      });

      expect(mockGlossaryAPI.glossaryAPI.searchTerms).toHaveBeenCalledTimes(1);
    });

    it('should handle different language cache separately', async () => {
      mockGlossaryAPI.glossaryAPI.searchTerms.mockResolvedValueOnce(mockResults);

      const { result } = renderHook(() => useGlossary());

      // Search in English
      await act(async () => {
        await result.current.searchTerms('sensor', 'english');
      });

      expect(mockGlossaryAPI.glossaryAPI.searchTerms).toHaveBeenCalledTimes(1);

      // Search in Urdu (different cache)
      await act(async () => {
        await result.current.searchTerms('sensor', 'urdu');
      });

      expect(mockGlossaryAPI.glossaryAPI.searchTerms).toHaveBeenCalledTimes(2);
    });

    it('should handle search errors', async () => {
      const error = new Error('Search failed');
      mockGlossaryAPI.glossaryAPI.searchTerms.mockRejectedValueOnce(error);

      const { result } = renderHook(() => useGlossary());

      let searchResult;
      await act(async () => {
        searchResult = await result.current.searchTerms('sensor');
      });

      expect(searchResult).toEqual([]);
      expect(result.current.searchResults.error).toBeTruthy();
    });
  });

  /**
   * listTerms() tests
   */
  describe('listTerms()', () => {
    const mockTerms = [
      {
        id: 'term-1',
        english_term: 'Node',
        urdu_translation: 'نوڈ',
        pronunciation_transliterated: 'nod',
        definition_english: 'A ROS process',
        definition_urdu: 'ROS عمل',
        category: 'robotics',
        status: 'active',
      },
    ];

    it('should list terms with default pagination', async () => {
      mockGlossaryAPI.glossaryAPI.listTerms.mockResolvedValueOnce(mockTerms);

      const { result } = renderHook(() => useGlossary());

      let listResult;
      await act(async () => {
        listResult = await result.current.listTerms();
      });

      expect(listResult).toEqual(mockTerms);
      expect(mockGlossaryAPI.glossaryAPI.listTerms).toHaveBeenCalledWith(
        undefined,
        50,
        0
      );
    });

    it('should list terms with custom pagination', async () => {
      mockGlossaryAPI.glossaryAPI.listTerms.mockResolvedValueOnce(mockTerms);

      const { result } = renderHook(() => useGlossary());

      await act(async () => {
        await result.current.listTerms('robotics', 100, 20);
      });

      expect(mockGlossaryAPI.glossaryAPI.listTerms).toHaveBeenCalledWith(
        'robotics',
        100,
        20
      );
    });

    it('should cache list results separately by params', async () => {
      mockGlossaryAPI.glossaryAPI.listTerms.mockResolvedValueOnce(mockTerms);

      const { result } = renderHook(() => useGlossary());

      // First call with limit 50
      await act(async () => {
        await result.current.listTerms(undefined, 50, 0);
      });

      // Second call with limit 100 (different cache)
      await act(async () => {
        await result.current.listTerms(undefined, 100, 0);
      });

      expect(mockGlossaryAPI.glossaryAPI.listTerms).toHaveBeenCalledTimes(2);
    });

    it('should handle list errors', async () => {
      const error = new Error('List failed');
      mockGlossaryAPI.glossaryAPI.listTerms.mockRejectedValueOnce(error);

      const { result } = renderHook(() => useGlossary());

      let listResult;
      await act(async () => {
        listResult = await result.current.listTerms();
      });

      expect(listResult).toEqual([]);
      expect(result.current.terms.error).toBeTruthy();
    });
  });

  /**
   * getCategories() tests
   */
  describe('getCategories()', () => {
    const mockCategories = ['robotics', 'control', 'kinematics'];

    it('should fetch categories', async () => {
      mockGlossaryAPI.glossaryAPI.getCategories.mockResolvedValueOnce(
        mockCategories
      );

      const { result } = renderHook(() => useGlossary());

      let categories;
      await act(async () => {
        categories = await result.current.getCategories();
      });

      expect(categories).toEqual(mockCategories);
      expect(result.current.categories.data).toEqual(mockCategories);
    });

    it('should cache categories', async () => {
      mockGlossaryAPI.glossaryAPI.getCategories.mockResolvedValueOnce(
        mockCategories
      );

      const { result } = renderHook(() => useGlossary());

      await act(async () => {
        await result.current.getCategories();
      });

      expect(mockGlossaryAPI.glossaryAPI.getCategories).toHaveBeenCalledTimes(1);

      // Second call should use cache
      await act(async () => {
        await result.current.getCategories();
      });

      expect(mockGlossaryAPI.glossaryAPI.getCategories).toHaveBeenCalledTimes(1);
    });

    it('should handle category fetch errors', async () => {
      const error = new Error('Failed to fetch categories');
      mockGlossaryAPI.glossaryAPI.getCategories.mockRejectedValueOnce(error);

      const { result } = renderHook(() => useGlossary());

      let categories;
      await act(async () => {
        categories = await result.current.getCategories();
      });

      expect(categories).toEqual([]);
      expect(result.current.categories.error).toBeTruthy();
    });
  });

  /**
   * submitFeedback() tests
   */
  describe('submitFeedback()', () => {
    const mockResponse = {
      status: 'success',
      message: 'Feedback submitted',
      feedback_id: 'feedback-123',
    };

    it('should submit feedback', async () => {
      mockGlossaryAPI.glossaryAPI.submitFeedback.mockResolvedValueOnce(
        mockResponse
      );

      const { result } = renderHook(() => useGlossary());

      let feedbackResult;
      await act(async () => {
        feedbackResult = await result.current.submitFeedback(
          'suggestion',
          'Good content',
          'token-123'
        );
      });

      expect(feedbackResult).toEqual(mockResponse);
      expect(result.current.feedback.data).toEqual(mockResponse);
    });

    it('should invalidate cache after feedback submission', async () => {
      mockGlossaryAPI.glossaryAPI.submitFeedback.mockResolvedValueOnce(
        mockResponse
      );
      mockGlossaryAPI.glossaryAPI.listTerms.mockResolvedValueOnce([]);
      mockGlossaryAPI.glossaryAPI.searchTerms.mockResolvedValueOnce([]);

      const { result } = renderHook(() => useGlossary());

      // Populate list cache
      await act(async () => {
        await result.current.listTerms();
      });

      const initialCallCount = mockGlossaryAPI.glossaryAPI.listTerms.mock
        .calls.length;

      // Submit feedback
      await act(async () => {
        await result.current.submitFeedback(
          'suggestion',
          'Good content',
          'token-123'
        );
      });

      // Cache should be invalidated, so next list call makes new API call
      await act(async () => {
        await result.current.listTerms();
      });

      expect(mockGlossaryAPI.glossaryAPI.listTerms).toHaveBeenCalledTimes(
        initialCallCount + 1
      );
    });

    it('should handle feedback submission errors', async () => {
      const error = new Error('Feedback submission failed');
      mockGlossaryAPI.glossaryAPI.submitFeedback.mockRejectedValueOnce(error);

      const { result } = renderHook(() => useGlossary());

      let feedbackResult;
      await act(async () => {
        feedbackResult = await result.current.submitFeedback(
          'suggestion',
          'Good content',
          'token-123'
        );
      });

      expect(feedbackResult).toBeNull();
      expect(result.current.feedback.error).toBeTruthy();
    });
  });

  /**
   * getStats() tests
   */
  describe('getStats()', () => {
    const mockStats = {
      total_terms: 150,
      total_categories: 5,
      categories: ['robotics', 'control', 'kinematics', 'programming', 'hardware'],
      status: 'active',
    };

    it('should fetch statistics', async () => {
      mockGlossaryAPI.glossaryAPI.getStats.mockResolvedValueOnce(mockStats);

      const { result } = renderHook(() => useGlossary());

      let stats;
      await act(async () => {
        stats = await result.current.getStats();
      });

      expect(stats).toEqual(mockStats);
      expect(result.current.stats.data).toEqual(mockStats);
    });

    it('should cache statistics', async () => {
      mockGlossaryAPI.glossaryAPI.getStats.mockResolvedValueOnce(mockStats);

      const { result } = renderHook(() => useGlossary());

      await act(async () => {
        await result.current.getStats();
      });

      expect(mockGlossaryAPI.glossaryAPI.getStats).toHaveBeenCalledTimes(1);

      // Second call should use cache
      await act(async () => {
        await result.current.getStats();
      });

      expect(mockGlossaryAPI.glossaryAPI.getStats).toHaveBeenCalledTimes(1);
    });

    it('should handle stats fetch errors', async () => {
      const error = new Error('Failed to fetch stats');
      mockGlossaryAPI.glossaryAPI.getStats.mockRejectedValueOnce(error);

      const { result } = renderHook(() => useGlossary());

      let stats;
      await act(async () => {
        stats = await result.current.getStats();
      });

      expect(stats).toBeNull();
      expect(result.current.stats.error).toBeTruthy();
    });
  });

  /**
   * Loading state tests
   */
  describe('isLoading state', () => {
    it('should be true when any operation is loading', async () => {
      mockGlossaryAPI.glossaryAPI.getTerm.mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(() => resolve({}), 100))
      );

      const { result } = renderHook(() => useGlossary());

      expect(result.current.isLoading).toBe(false);

      act(() => {
        result.current.getTerm('test');
      });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });
  });

  /**
   * Error state tests
   */
  describe('error state', () => {
    it('should return first error found', async () => {
      const error = new Error('Test error');
      mockGlossaryAPI.glossaryAPI.getTerm.mockRejectedValueOnce(error);

      const { result } = renderHook(() => useGlossary());

      await act(async () => {
        await result.current.getTerm('test');
      });

      expect(result.current.error).toBeTruthy();
    });

    it('should clear error when operation succeeds', async () => {
      const mockTerm = {
        id: 'test',
        english_term: 'Test',
        urdu_translation: 'ٹیسٹ',
        pronunciation_transliterated: 'test',
        definition_english: 'Test definition',
        definition_urdu: 'ٹیسٹ تعریف',
        category: 'test',
        status: 'active',
      };

      mockGlossaryAPI.glossaryAPI.getTerm.mockRejectedValueOnce(
        new Error('First call fails')
      );

      const { result } = renderHook(() => useGlossary());

      // First call fails
      await act(async () => {
        await result.current.getTerm('test');
      });

      expect(result.current.error).toBeTruthy();

      // Second call succeeds
      mockGlossaryAPI.glossaryAPI.getTerm.mockResolvedValueOnce(mockTerm);

      await act(async () => {
        await result.current.getTerm('test');
      });

      expect(result.current.error).toBeNull();
      expect(result.current.term.data).toEqual(mockTerm);
    });
  });

  /**
   * Cache management tests
   */
  describe('cache management', () => {
    it('should clear cache with clearCache()', async () => {
      const mockTerms = [
        {
          id: 'test',
          english_term: 'Test',
          urdu_translation: 'ٹیسٹ',
          pronunciation_transliterated: 'test',
          definition_english: 'Test',
          definition_urdu: 'ٹیسٹ',
          category: 'test',
          status: 'active',
        },
      ];

      mockGlossaryAPI.glossaryAPI.listTerms.mockResolvedValueOnce(mockTerms);

      const { result } = renderHook(() => useGlossary());

      // First call
      await act(async () => {
        await result.current.listTerms();
      });

      expect(mockGlossaryAPI.glossaryAPI.listTerms).toHaveBeenCalledTimes(1);

      // Clear cache
      act(() => {
        result.current.clearCache();
      });

      // Second call should hit API again
      await act(async () => {
        await result.current.listTerms();
      });

      expect(mockGlossaryAPI.glossaryAPI.listTerms).toHaveBeenCalledTimes(2);
    });

    it('should invalidate specific cache patterns', async () => {
      mockGlossaryAPI.glossaryAPI.listTerms.mockResolvedValueOnce([]);
      mockGlossaryAPI.glossaryAPI.searchTerms.mockResolvedValueOnce([]);

      const { result } = renderHook(() => useGlossary());

      // Cache list terms
      await act(async () => {
        await result.current.listTerms();
      });

      // Cache search results
      await act(async () => {
        await result.current.searchTerms('test');
      });

      expect(mockGlossaryAPI.glossaryAPI.listTerms).toHaveBeenCalledTimes(1);
      expect(mockGlossaryAPI.glossaryAPI.searchTerms).toHaveBeenCalledTimes(1);

      // Invalidate only list cache
      act(() => {
        result.current.invalidateCache('list:');
      });

      // List should call API again
      await act(async () => {
        await result.current.listTerms();
      });

      expect(mockGlossaryAPI.glossaryAPI.listTerms).toHaveBeenCalledTimes(2);

      // Search should still use cache
      await act(async () => {
        await result.current.searchTerms('test');
      });

      expect(mockGlossaryAPI.glossaryAPI.searchTerms).toHaveBeenCalledTimes(1);
    });
  });
});
