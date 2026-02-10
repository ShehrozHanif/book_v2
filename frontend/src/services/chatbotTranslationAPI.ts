/**
 * Chatbot Translation API Service
 *
 * Frontend API client for:
 * 1. Getting translated chatbot responses
 * 2. Managing user language preferences
 * 3. Searching glossary terms
 * 4. Listing response templates
 */

import axios, { AxiosInstance } from 'axios';
import { apiClient } from './apiClient';


interface ChatbotResponse {
  content: string;
  template_key: string;
  language: 'english' | 'urdu';
  version: number;
  note?: string;
}

interface LanguagePreference {
  user_id: string;
  language: 'english' | 'urdu';
  updated_at?: string;
}

interface GlossaryTerm {
  id: string;
  english_term: string;
  urdu_translation: string;
  pronunciation_transliterated: string;
  definition_english: string;
  definition_urdu: string;
  category?: string;
  status: string;
}

interface ResponseTemplate {
  id: string;
  template_key: string;
  english_content: string;
  version: number;
  status: string;
}


class ChatbotTranslationAPI {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = '/api/v1') {
    this.baseURL = baseURL;
    this.client = apiClient;
  }

  /**
   * Get translated chatbot response
   *
   * @param templateKey - Unique template identifier
   * @param language - Target language (english, urdu)
   * @param isAuthenticated - Whether user is authenticated
   * @returns ChatbotResponse with translated content
   */
  async getChatbotResponse(
    templateKey: string,
    language: 'english' | 'urdu' = 'english',
    isAuthenticated: boolean = false
  ): Promise<ChatbotResponse> {
    try {
      const response = await this.client.get<ChatbotResponse>(
        `${this.baseURL}/chatbot/response/${templateKey}`,
        {
          params: {
            language: language.toLowerCase(),
          },
          timeout: 5000,
        }
      );

      return response.data;
    } catch (error) {
      this.handleError(error, 'Failed to fetch chatbot response');
      throw error;
    }
  }

  /**
   * List all response templates
   *
   * @param statusFilter - Filter by status (published, draft, archived)
   * @param limit - Maximum results
   * @returns Array of response templates
   */
  async listTemplates(
    statusFilter: 'published' | 'draft' | 'archived' = 'published',
    limit: number = 100
  ): Promise<ResponseTemplate[]> {
    try {
      const response = await this.client.get<ResponseTemplate[]>(
        `${this.baseURL}/chatbot/templates`,
        {
          params: {
            status_filter: statusFilter,
            limit,
          },
          timeout: 5000,
        }
      );

      return response.data;
    } catch (error) {
      this.handleError(error, 'Failed to fetch templates');
      throw error;
    }
  }

  /**
   * Search glossary terms
   *
   * @param query - Search query
   * @param language - Search language (english, urdu)
   * @param category - Filter by category
   * @param limit - Maximum results
   * @returns Array of matching glossary terms
   */
  async searchGlossary(
    query: string,
    language: 'english' | 'urdu' = 'english',
    category?: string,
    limit: number = 20
  ): Promise<GlossaryTerm[]> {
    try {
      const response = await this.client.get<GlossaryTerm[]>(
        `${this.baseURL}/glossary/search`,
        {
          params: {
            q: query,
            language: language.toLowerCase(),
            category,
            limit,
          },
          timeout: 5000,
        }
      );

      return response.data;
    } catch (error) {
      this.handleError(error, 'Failed to search glossary');
      throw error;
    }
  }

  /**
   * List glossary terms
   *
   * @param category - Filter by category
   * @param limit - Maximum results
   * @param offset - Pagination offset
   * @returns Array of glossary terms
   */
  async listGlossaryTerms(
    category?: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<GlossaryTerm[]> {
    try {
      const response = await this.client.get<GlossaryTerm[]>(
        `${this.baseURL}/glossary/terms`,
        {
          params: {
            category,
            limit,
            offset,
          },
          timeout: 5000,
        }
      );

      return response.data;
    } catch (error) {
      this.handleError(error, 'Failed to fetch glossary terms');
      throw error;
    }
  }

  /**
   * Get user's language preference
   *
   * @param userId - User ID
   * @returns User's current language preference
   */
  async getUserLanguagePreference(userId: string): Promise<LanguagePreference> {
    try {
      const response = await this.client.get<LanguagePreference>(
        `${this.baseURL}/users/${userId}/language`,
        {
          timeout: 5000,
        }
      );

      return response.data;
    } catch (error) {
      // Return default preference on 404 (new user)
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return {
          user_id: userId,
          language: 'english',
        };
      }

      this.handleError(error, 'Failed to fetch language preference');
      throw error;
    }
  }

  /**
   * Set user's language preference
   *
   * @param userId - User ID
   * @param language - Language to set (english, urdu)
   * @returns Updated preference
   */
  async setUserLanguagePreference(
    userId: string,
    language: 'english' | 'urdu'
  ): Promise<LanguagePreference> {
    try {
      const response = await this.client.post<LanguagePreference>(
        `${this.baseURL}/users/${userId}/language`,
        {
          language: language.toLowerCase(),
        },
        {
          timeout: 5000,
        }
      );

      return response.data;
    } catch (error) {
      this.handleError(error, 'Failed to save language preference');
      throw error;
    }
  }

  /**
   * Handle API errors
   */
  private handleError(error: unknown, defaultMessage: string): void {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const message = error.response?.data?.detail || error.message;

      switch (status) {
        case 401:
          console.error('Authentication required:', message);
          break;
        case 403:
          console.error('Access forbidden:', message);
          break;
        case 404:
          console.error('Not found:', message);
          break;
        case 400:
          console.error('Bad request:', message);
          break;
        case 500:
          console.error('Server error:', message);
          break;
        default:
          console.error(defaultMessage, message);
      }
    } else if (error instanceof Error) {
      console.error(defaultMessage, error.message);
    } else {
      console.error(defaultMessage);
    }
  }
}

// Export singleton instance
export const chatbotTranslationAPI = new ChatbotTranslationAPI();

export default chatbotTranslationAPI;
export type {
  ChatbotResponse,
  LanguagePreference,
  GlossaryTerm,
  ResponseTemplate,
};
