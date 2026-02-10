/**
 * Glossary API Service
 *
 * Frontend API client for:
 * 1. Getting glossary terms by ID
 * 2. Listing all glossary terms with pagination
 * 3. Searching glossary terms (English or Urdu)
 * 4. Getting glossary categories
 * 5. Submitting glossary feedback
 * 6. Getting glossary statistics
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * Glossary term with bilingual support
 */
export interface GlossaryTerm {
  id: string;
  english_term: string;
  urdu_translation: string;
  pronunciation_transliterated: string;
  definition_english: string;
  definition_urdu: string;
  category: string;
  status: string;
  related_terms?: string[];
  created_at?: string;
  updated_at?: string;
}

/**
 * Glossary statistics
 */
export interface GlossaryStats {
  total_terms: number;
  total_categories: number;
  categories: string[];
  status: string;
}

/**
 * Glossary feedback submission response
 */
export interface GlossaryFeedbackResponse {
  status: string;
  message: string;
  feedback_id: string;
}

/**
 * API error class for glossary operations
 */
export class GlossaryApiError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "GlossaryApiError";
  }
}

/**
 * Glossary API client
 */
export const glossaryAPI = {
  /**
   * Get a specific glossary term by ID
   *
   * @param termId - English term name or ID
   * @returns Glossary term with full details
   * @throws GlossaryApiError if term not found
   */
  async getTerm(termId: string): Promise<GlossaryTerm> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/glossary/${encodeURIComponent(termId)}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new GlossaryApiError(
          response.status,
          errorData.detail || `Failed to fetch glossary term: ${response.statusText}`
        );
      }

      const data = await response.json();
      return data as GlossaryTerm;
    } catch (error) {
      if (error instanceof GlossaryApiError) {
        throw error;
      }
      throw new GlossaryApiError(
        500,
        `Network error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  },

  /**
   * List all glossary terms with pagination
   *
   * @param category - Optional category filter
   * @param limit - Maximum results (default: 50)
   * @param offset - Pagination offset (default: 0)
   * @returns Array of glossary terms
   */
  async listTerms(
    category?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<GlossaryTerm[]> {
    try {
      const params = new URLSearchParams();
      if (category) params.append("category", category);
      params.append("limit", limit.toString());
      params.append("offset", offset.toString());

      const response = await fetch(
        `${API_BASE_URL}/api/v1/glossary?${params.toString()}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new GlossaryApiError(
          response.status,
          errorData.detail || `Failed to fetch glossary terms: ${response.statusText}`
        );
      }

      const data = await response.json();
      return data as GlossaryTerm[];
    } catch (error) {
      if (error instanceof GlossaryApiError) {
        throw error;
      }
      throw new GlossaryApiError(
        500,
        `Network error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  },

  /**
   * Search glossary terms
   *
   * @param query - Search query string
   * @param language - Search language: "english" or "urdu" (default: "english")
   * @param category - Optional category filter
   * @param limit - Maximum results (default: 20)
   * @returns Array of matching glossary terms
   */
  async searchTerms(
    query: string,
    language: "english" | "urdu" = "english",
    category?: string,
    limit: number = 20
  ): Promise<GlossaryTerm[]> {
    try {
      if (!query || query.trim().length === 0) {
        throw new GlossaryApiError(400, "Search query cannot be empty");
      }

      const params = new URLSearchParams();
      params.append("q", query);
      params.append("language", language.toLowerCase());
      if (category) params.append("category", category);
      params.append("limit", Math.min(limit, 100).toString());

      const response = await fetch(
        `${API_BASE_URL}/api/v1/glossary/search?${params.toString()}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new GlossaryApiError(
          response.status,
          errorData.detail || `Failed to search glossary: ${response.statusText}`
        );
      }

      const data = await response.json();
      return data as GlossaryTerm[];
    } catch (error) {
      if (error instanceof GlossaryApiError) {
        throw error;
      }
      throw new GlossaryApiError(
        500,
        `Network error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  },

  /**
   * Get all glossary categories
   *
   * @returns Array of category names
   */
  async getCategories(): Promise<string[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/glossary/categories`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new GlossaryApiError(
          response.status,
          errorData.detail || `Failed to fetch categories: ${response.statusText}`
        );
      }

      const data = await response.json();
      return data as string[];
    } catch (error) {
      if (error instanceof GlossaryApiError) {
        throw error;
      }
      throw new GlossaryApiError(
        500,
        `Network error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  },

  /**
   * Submit feedback about a glossary term
   *
   * Requires authentication. Feedback types:
   * - "suggestion": New idea or improvement
   * - "correction": Fix an error
   * - "new_term": Suggest a new term
   *
   * @param feedbackType - Type of feedback (suggestion, correction, new_term)
   * @param content - Feedback content (10-500 characters)
   * @param glossaryTermId - Related term ID (optional)
   * @param suggestedTerm - New term name (for new_term type)
   * @param authToken - JWT auth token (required)
   * @returns Feedback submission response
   * @throws GlossaryApiError if not authenticated or validation fails
   */
  async submitFeedback(
    feedbackType: "suggestion" | "correction" | "new_term",
    content: string,
    authToken: string,
    glossaryTermId?: string,
    suggestedTerm?: string
  ): Promise<GlossaryFeedbackResponse> {
    try {
      // Validate input
      if (!content || content.trim().length < 10) {
        throw new GlossaryApiError(400, "Feedback content must be at least 10 characters");
      }

      if (content.length > 500) {
        throw new GlossaryApiError(400, "Feedback content must not exceed 500 characters");
      }

      if (!authToken) {
        throw new GlossaryApiError(401, "Authentication required to submit feedback");
      }

      const params = new URLSearchParams();
      params.append("feedback_type", feedbackType);
      params.append("content", content);
      if (glossaryTermId) params.append("glossary_term_id", glossaryTermId);
      if (suggestedTerm) params.append("suggested_term", suggestedTerm);

      const response = await fetch(
        `${API_BASE_URL}/api/v1/glossary/feedback?${params.toString()}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${authToken}`,
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        if (response.status === 401) {
          throw new GlossaryApiError(401, "Authentication failed - please log in again");
        }

        throw new GlossaryApiError(
          response.status,
          errorData.detail || `Failed to submit feedback: ${response.statusText}`
        );
      }

      const data = await response.json();
      return data as GlossaryFeedbackResponse;
    } catch (error) {
      if (error instanceof GlossaryApiError) {
        throw error;
      }
      throw new GlossaryApiError(
        500,
        `Network error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  },

  /**
   * Get glossary statistics
   *
   * @returns Statistics including term count, category count, and categories list
   */
  async getStats(): Promise<GlossaryStats> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/glossary/stats`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new GlossaryApiError(
          response.status,
          errorData.detail || `Failed to fetch statistics: ${response.statusText}`
        );
      }

      const data = await response.json();
      return data as GlossaryStats;
    } catch (error) {
      if (error instanceof GlossaryApiError) {
        throw error;
      }
      throw new GlossaryApiError(
        500,
        `Network error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  },
};

export default glossaryAPI;
