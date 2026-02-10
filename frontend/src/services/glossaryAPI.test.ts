/**
 * Tests for glossaryAPI service (T039)
 *
 * Test coverage:
 * - getTerm() - fetch, 404, network error
 * - listTerms() - pagination, filtering
 * - searchTerms() - empty query, language filter
 * - getCategories() - list categories
 * - submitFeedback() - auth, validation, submission
 * - getStats() - statistics retrieval
 * - Error handling for all endpoints
 */

import {
  glossaryAPI,
  GlossaryApiError,
  GlossaryTerm,
  GlossaryStats,
  GlossaryFeedbackResponse,
} from './glossaryAPI';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch as jest.Mock;

describe('glossaryAPI service', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  /**
   * getTerm() tests
   */
  describe('getTerm()', () => {
    const mockTerm: GlossaryTerm = {
      id: 'term-1',
      english_term: 'ROS Node',
      urdu_translation: 'ROS نوڈ',
      pronunciation_transliterated: 'ros nod',
      definition_english: 'A process in ROS',
      definition_urdu: 'ROS میں ایک عمل',
      category: 'robotics',
      status: 'active',
      related_terms: ['ROS 2', 'Subscriber'],
    };

    it('should fetch term successfully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTerm,
      });

      const result = await glossaryAPI.getTerm('ROS Node');

      expect(result).toEqual(mockTerm);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/glossary/ROS%20Node'),
        expect.objectContaining({
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });

    it('should throw 404 error for non-existent term', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Term not found' }),
      });

      await expect(glossaryAPI.getTerm('NonExistent')).rejects.toThrow(
        GlossaryApiError
      );
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new TypeError('Network error'));

      await expect(glossaryAPI.getTerm('ROS Node')).rejects.toThrow(
        GlossaryApiError
      );
    });

    it('should encode term ID in URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTerm,
      });

      await glossaryAPI.getTerm('ROS 2 Node');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('ROS%202%20Node'),
        expect.anything()
      );
    });
  });

  /**
   * listTerms() tests
   */
  describe('listTerms()', () => {
    const mockTerms: GlossaryTerm[] = [
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
      {
        id: 'term-2',
        english_term: 'Topic',
        urdu_translation: 'موضوع',
        pronunciation_transliterated: 'mawzu',
        definition_english: 'A communication channel',
        definition_urdu: 'ابلاغ چینل',
        category: 'robotics',
        status: 'active',
      },
    ];

    it('should list terms with default pagination', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTerms,
      });

      const result = await glossaryAPI.listTerms();

      expect(result).toEqual(mockTerms);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('limit=50&offset=0'),
        expect.anything()
      );
    });

    it('should list terms with custom limit and offset', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTerms,
      });

      await glossaryAPI.listTerms(undefined, 100, 20);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('limit=100&offset=20'),
        expect.anything()
      );
    });

    it('should filter terms by category', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTerms,
      });

      await glossaryAPI.listTerms('robotics', 50, 0);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('category=robotics'),
        expect.anything()
      );
    });

    it('should handle empty list', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      const result = await glossaryAPI.listTerms();

      expect(result).toEqual([]);
    });

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Server error' }),
      });

      await expect(glossaryAPI.listTerms()).rejects.toThrow(GlossaryApiError);
    });
  });

  /**
   * searchTerms() tests
   */
  describe('searchTerms()', () => {
    const mockResults: GlossaryTerm[] = [
      {
        id: 'term-1',
        english_term: 'Sensor',
        urdu_translation: 'سینسر',
        pronunciation_transliterated: 'sensor',
        definition_english: 'A device that detects changes',
        definition_urdu: 'ایک آلہ جو تبدیلی کا پتہ لگاتا ہے',
        category: 'robotics',
        status: 'active',
      },
    ];

    it('should search terms in English', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults,
      });

      const result = await glossaryAPI.searchTerms('sensor', 'english');

      expect(result).toEqual(mockResults);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('q=sensor&language=english'),
        expect.anything()
      );
    });

    it('should search terms in Urdu', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults,
      });

      await glossaryAPI.searchTerms('سینسر', 'urdu');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('language=urdu'),
        expect.anything()
      );
    });

    it('should apply category filter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults,
      });

      await glossaryAPI.searchTerms('sensor', 'english', 'robotics');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('category=robotics'),
        expect.anything()
      );
    });

    it('should throw error for empty query', async () => {
      await expect(glossaryAPI.searchTerms('', 'english')).rejects.toThrow(
        'Search query cannot be empty'
      );
    });

    it('should throw error for whitespace-only query', async () => {
      await expect(glossaryAPI.searchTerms('   ', 'english')).rejects.toThrow(
        'Search query cannot be empty'
      );
    });

    it('should cap limit at 100', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults,
      });

      await glossaryAPI.searchTerms('sensor', 'english', undefined, 200);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('limit=100'),
        expect.anything()
      );
    });

    it('should handle search with no results', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      const result = await glossaryAPI.searchTerms('nonexistentterm');

      expect(result).toEqual([]);
    });

    it('should handle search API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Invalid query' }),
      });

      await expect(glossaryAPI.searchTerms('!@#$')).rejects.toThrow(
        GlossaryApiError
      );
    });
  });

  /**
   * getCategories() tests
   */
  describe('getCategories()', () => {
    const mockCategories = [
      'robotics',
      'control-systems',
      'kinematics',
      'programming',
      'hardware',
    ];

    it('should fetch all categories', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCategories,
      });

      const result = await glossaryAPI.getCategories();

      expect(result).toEqual(mockCategories);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/glossary/categories'),
        expect.anything()
      );
    });

    it('should handle empty category list', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      const result = await glossaryAPI.getCategories();

      expect(result).toEqual([]);
    });

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Server error' }),
      });

      await expect(glossaryAPI.getCategories()).rejects.toThrow(
        GlossaryApiError
      );
    });
  });

  /**
   * submitFeedback() tests
   */
  describe('submitFeedback()', () => {
    const mockResponse: GlossaryFeedbackResponse = {
      status: 'success',
      message: 'Feedback submitted successfully',
      feedback_id: 'feedback-123',
    };

    it('should submit suggestion feedback', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await glossaryAPI.submitFeedback(
        'suggestion',
        'Please add an example usage',
        'token-123'
      );

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('feedback_type=suggestion'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer token-123',
          }),
        })
      );
    });

    it('should submit correction feedback', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await glossaryAPI.submitFeedback(
        'correction',
        'The definition has a typo in the English version',
        'token-123',
        'term-1'
      );

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('feedback_type=correction'),
        expect.anything()
      );
    });

    it('should submit new term feedback', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await glossaryAPI.submitFeedback(
        'new_term',
        'Please add a term for quadrupedal locomotion',
        'token-123',
        undefined,
        'Quadrupedal Gait'
      );

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('suggested_term=Quadrupedal%20Gait'),
        expect.anything()
      );
    });

    it('should throw error for missing auth token', async () => {
      await expect(
        glossaryAPI.submitFeedback('suggestion', 'Good content', '')
      ).rejects.toThrow('Authentication required');
    });

    it('should throw error for content too short', async () => {
      await expect(
        glossaryAPI.submitFeedback('suggestion', 'Short', 'token-123')
      ).rejects.toThrow('at least 10 characters');
    });

    it('should throw error for content too long', async () => {
      const longContent = 'a'.repeat(501);
      await expect(
        glossaryAPI.submitFeedback('suggestion', longContent, 'token-123')
      ).rejects.toThrow('not exceed 500 characters');
    });

    it('should handle 401 auth failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(
        glossaryAPI.submitFeedback('suggestion', 'Good content', 'bad-token')
      ).rejects.toThrow('Authentication failed');
    });

    it('should include Authorization header in request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await glossaryAPI.submitFeedback(
        'suggestion',
        'This is a good suggestion',
        'auth-token-xyz'
      );

      expect(mockFetch).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer auth-token-xyz',
          }),
        })
      );
    });
  });

  /**
   * getStats() tests
   */
  describe('getStats()', () => {
    const mockStats: GlossaryStats = {
      total_terms: 150,
      total_categories: 5,
      categories: ['robotics', 'control', 'kinematics', 'programming', 'hardware'],
      status: 'active',
    };

    it('should fetch glossary statistics', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats,
      });

      const result = await glossaryAPI.getStats();

      expect(result).toEqual(mockStats);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/glossary/stats'),
        expect.anything()
      );
    });

    it('should include category list in stats', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats,
      });

      const result = await glossaryAPI.getStats();

      expect(result.categories).toEqual([
        'robotics',
        'control',
        'kinematics',
        'programming',
        'hardware',
      ]);
    });

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Server error' }),
      });

      await expect(glossaryAPI.getStats()).rejects.toThrow(GlossaryApiError);
    });
  });

  /**
   * Error handling tests
   */
  describe('error handling', () => {
    it('should catch non-GlossaryApiError exceptions', async () => {
      mockFetch.mockRejectedValueOnce(new TypeError('Network timeout'));

      await expect(glossaryAPI.getTerm('test')).rejects.toThrow(GlossaryApiError);
    });

    it('should preserve HTTP status code in error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: async () => ({ detail: 'Rate limited' }),
      });

      try {
        await glossaryAPI.getTerm('test');
      } catch (error) {
        if (error instanceof GlossaryApiError) {
          expect(error.statusCode).toBe(429);
        }
      }
    });

    it('should handle JSON parse errors in responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      await expect(glossaryAPI.getTerm('test')).rejects.toThrow();
    });
  });

  /**
   * URL encoding tests
   */
  describe('URL encoding', () => {
    it('should properly encode special characters in search query', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await glossaryAPI.searchTerms('test & special=chars');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('test%20%26%20special%3Dchars'),
        expect.anything()
      );
    });

    it('should properly encode Urdu text in search', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await glossaryAPI.searchTerms('اردو', 'urdu');

      expect(mockFetch).toHaveBeenCalled();
    });
  });
});
