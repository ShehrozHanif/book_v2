/**
 * Glossary API Service for chatbot glossary feature
 */

import { API_BASE_URL } from './config';

export interface GlossaryTerm {
  id: string;
  english_term: string;
  urdu_translation: string;
  pronunciation_transliterated: string;
  definition_english: string;
  definition_urdu: string;
  category?: string;
  status: string;
}

export interface GlossaryFeedback {
  feedback_type: 'suggestion' | 'correction' | 'new_term';
  content: string;
  glossary_term_id?: string;
  suggested_term?: string;
}

class GlossaryAPIService {
  private baseURL: string = `${API_BASE_URL}/api/v1`;

  async getTerm(termId: string): Promise<GlossaryTerm | null> {
    try {
      const response = await fetch(`${this.baseURL}/glossary/${encodeURIComponent(termId)}`);
      if (response.status === 404) return null;
      if (!response.ok) throw new Error(`Failed to fetch term: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching glossary term:', error);
      throw error;
    }
  }

  async searchTerms(
    query: string,
    language: 'english' | 'urdu' = 'english',
    category?: string,
    limit: number = 20
  ): Promise<GlossaryTerm[]> {
    try {
      const params = new URLSearchParams({
        q: query,
        language,
        limit: String(limit),
      });
      if (category) params.append('category', category);
      
      const response = await fetch(`${this.baseURL}/glossary/search?${params}`);
      if (!response.ok) throw new Error(`Failed to search glossary: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error('Error searching glossary:', error);
      throw error;
    }
  }

  async listTerms(
    category?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<GlossaryTerm[]> {
    try {
      const params = new URLSearchParams({
        limit: String(limit),
        offset: String(offset),
      });
      if (category) params.append('category', category);
      
      const response = await fetch(`${this.baseURL}/glossary?${params}`);
      if (!response.ok) throw new Error(`Failed to list glossary terms: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error('Error listing glossary terms:', error);
      throw error;
    }
  }

  async submitFeedback(
    feedback: GlossaryFeedback,
    token: string
  ): Promise<{ status: string; message: string; feedback_id: string }> {
    try {
      const params = new URLSearchParams({
        feedback_type: feedback.feedback_type,
        content: feedback.content,
      });
      if (feedback.glossary_term_id) params.append('glossary_term_id', feedback.glossary_term_id);
      if (feedback.suggested_term) params.append('suggested_term', feedback.suggested_term);
      
      const response = await fetch(`${this.baseURL}/glossary/feedback?${params}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.status === 401) throw new Error('Authentication required');
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit feedback');
      }
      return await response.json();
    } catch (error) {
      console.error('Error submitting glossary feedback:', error);
      throw error;
    }
  }
}

export const glossaryAPI = new GlossaryAPIService();
