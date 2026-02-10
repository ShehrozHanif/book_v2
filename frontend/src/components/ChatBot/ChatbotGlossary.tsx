/**
 * ChatbotGlossary Component (T037)
 *
 * Provides a searchable glossary UI for technical terminology support.
 *
 * Features:
 * - Bilingual term display (English + Urdu)
 * - Full-text search across terms
 * - Category filtering
 * - RTL support for Urdu content
 * - Loading and error states
 * - Mobile responsive design
 * - Pronunciation guides
 * - Related terms linking
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useGlossary } from '../../hooks/useGlossary';
import { useLanguagePreference } from '../../hooks/useLanguagePreference';
import './styles/chatbot-glossary.css';

/**
 * Props for ChatbotGlossary component
 */
export interface ChatbotGlossaryProps {
  /** Optional CSS class name */
  className?: string;
  /** Optional callback when term is selected */
  onTermSelect?: (termId: string, term: string) => void;
  /** Optional initial search query */
  initialQuery?: string;
  /** Show as expanded view (full screen) or compact view */
  expanded?: boolean;
  /** Maximum number of results to display */
  maxResults?: number;
}

/**
 * ChatbotGlossary Component
 *
 * Renders a glossary interface with search and filtering capabilities.
 *
 * @example
 * <ChatbotGlossary
 *   onTermSelect={(id, term) => console.log(id, term)}
 *   initialQuery="sensor"
 *   maxResults={10}
 * />
 */
export const ChatbotGlossary: React.FC<ChatbotGlossaryProps> = ({
  className = '',
  onTermSelect,
  initialQuery = '',
  expanded = false,
  maxResults = 20,
}) => {
  const { language } = useLanguagePreference();
  const {
    searchTerms,
    getCategories,
    getTerm,
    searchResults,
    categories,
    isLoading,
    error,
    clearCache,
  } = useGlossary();

  // State management
  const [query, setQuery] = useState(initialQuery);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const [selectedTerm, setSelectedTerm] = useState<string | undefined>();
  const [showTermDetail, setShowTermDetail] = useState(false);
  const [categoriesLoaded, setCategoriesLoaded] = useState(false);

  // Load categories on mount
  useEffect(() => {
    const loadCategories = async () => {
      await getCategories();
      setCategoriesLoaded(true);
    };

    loadCategories();
  }, [getCategories]);

  // Search terms when query or category changes
  useEffect(() => {
    const performSearch = async () => {
      if (query.trim().length > 0) {
        await searchTerms(
          query,
          language === 'urdu' ? 'urdu' : 'english',
          selectedCategory,
          maxResults
        );
      }
    };

    performSearch();
  }, [query, selectedCategory, language, searchTerms, maxResults]);

  /**
   * Handle search input change
   */
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setShowTermDetail(false);
  }, []);

  /**
   * Handle category filter change
   */
  const handleCategoryChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const value = e.target.value;
      setSelectedCategory(value === '' ? undefined : value);
    },
    []
  );

  /**
   * Handle term selection
   */
  const handleTermSelect = useCallback(
    async (termId: string, termName: string) => {
      setSelectedTerm(termId);
      setShowTermDetail(true);

      if (onTermSelect) {
        onTermSelect(termId, termName);
      }
    },
    [onTermSelect]
  );

  /**
   * Handle clear search
   */
  const handleClearSearch = useCallback(() => {
    setQuery('');
    setSelectedCategory(undefined);
    setShowTermDetail(false);
  }, []);

  /**
   * Get RTL direction for content
   */
  const getDirection = (lang: 'english' | 'urdu' = language): 'rtl' | 'ltr' => {
    return lang === 'urdu' ? 'rtl' : 'ltr';
  };

  /**
   * Render loading state
   */
  const renderLoading = () => (
    <div
      className="glossary-loading"
      dir={getDirection()}
      role="status"
      aria-live="polite"
    >
      <div className="spinner"></div>
      <p className="loading-text">
        {language === 'urdu' ? 'لوڈ ہو رہا ہے...' : 'Loading...'}
      </p>
    </div>
  );

  /**
   * Render error state
   */
  const renderError = () => (
    <div className="glossary-error" role="alert">
      <span className="error-icon">⚠️</span>
      <p className="error-message">
        {language === 'urdu'
          ? `خرابی: ${error?.message || 'کچھ غلط ہو گیا'}`
          : `Error: ${error?.message || 'Something went wrong'}`}
      </p>
      <button
        className="error-retry-btn"
        onClick={() => clearCache()}
        aria-label={language === 'urdu' ? 'دوبارہ کوشش کریں' : 'Retry'}
      >
        {language === 'urdu' ? 'دوبارہ کوشش کریں' : 'Retry'}
      </button>
    </div>
  );

  /**
   * Render glossary term card
   */
  const renderTermCard = (term: any, isUrdu: boolean = false) => (
    <div
      key={term.id}
      className={`glossary-term-card ${isUrdu ? 'urdu' : 'english'}`}
      dir={isUrdu ? 'rtl' : 'ltr'}
      lang={isUrdu ? 'ur' : 'en'}
      onClick={() => handleTermSelect(term.id, term.english_term)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleTermSelect(term.id, term.english_term);
        }
      }}
    >
      <div className="term-header">
        <h3 className="term-name">
          {isUrdu ? term.urdu_translation : term.english_term}
        </h3>
        <span className="term-category">{term.category}</span>
      </div>

      {term.pronunciation_transliterated && (
        <p className="term-pronunciation">
          {language === 'urdu' ? 'تلفظ: ' : 'Pronunciation: '}
          <em>{term.pronunciation_transliterated}</em>
        </p>
      )}

      <p className="term-definition">
        {isUrdu ? term.definition_urdu : term.definition_english}
      </p>

      {term.related_terms && term.related_terms.length > 0 && (
        <div className="related-terms">
          <small>
            {language === 'urdu' ? 'متعلقہ شرائط: ' : 'Related terms: '}
            {term.related_terms.join(', ')}
          </small>
        </div>
      )}
    </div>
  );

  /**
   * Render search results
   */
  const renderResults = () => {
    if (query.trim().length === 0) {
      return (
        <div className="glossary-empty" dir={getDirection()}>
          <p>
            {language === 'urdu'
              ? 'اصطلاحات تلاش کرنے کے لیے اوپر ٹائپ کریں'
              : 'Type above to search for terms'}
          </p>
        </div>
      );
    }

    if (!searchResults.data || searchResults.data.length === 0) {
      return (
        <div className="glossary-no-results" dir={getDirection()}>
          <p>
            {language === 'urdu'
              ? `"${query}" کے لیے کوئی نتائج نہیں ملے`
              : `No results found for "${query}"`}
          </p>
        </div>
      );
    }

    return (
      <div className="glossary-results" role="listbox">
        {searchResults.data.map((term) => (
          <div key={term.id} className="result-item">
            {renderTermCard(term, false)}
            {language === 'urdu' && (
              <div className="urdu-translation">
                {renderTermCard(term, true)}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  /**
   * Render glossary interface
   */
  return (
    <div
      className={`chatbot-glossary ${expanded ? 'expanded' : 'compact'} ${className}`}
      dir={getDirection()}
      role="region"
      aria-label={
        language === 'urdu' ? 'اصطلاحات کی فہرست' : 'Glossary search'
      }
    >
      {/* Header */}
      <div className="glossary-header">
        <h2 className="glossary-title">
          {language === 'urdu' ? 'اصطلاحات کی فہرست' : 'Glossary'}
        </h2>
        <p className="glossary-subtitle">
          {language === 'urdu'
            ? 'تکنیکی اصطلاحات تلاش کریں'
            : 'Search technical terminology'}
        </p>
      </div>

      {/* Search Bar */}
      <div className="glossary-search-bar">
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder={
              language === 'urdu'
                ? 'اصطلاح تلاش کریں...'
                : 'Search terms...'
            }
            value={query}
            onChange={handleSearchChange}
            aria-label={
              language === 'urdu' ? 'اصطلاح تلاش کریں' : 'Search terms'
            }
            dir={getDirection()}
          />
          {query && (
            <button
              className="clear-search-btn"
              onClick={handleClearSearch}
              aria-label={language === 'urdu' ? 'صاف کریں' : 'Clear'}
              title={language === 'urdu' ? 'صاف کریں' : 'Clear search'}
            >
              ✕
            </button>
          )}
        </div>

        {/* Category Filter */}
        {categoriesLoaded && categories.data && categories.data.length > 0 && (
          <select
            className="category-filter"
            value={selectedCategory || ''}
            onChange={handleCategoryChange}
            aria-label={
              language === 'urdu' ? 'زمرہ منتخب کریں' : 'Select category'
            }
            dir={getDirection()}
          >
            <option value="">
              {language === 'urdu' ? 'تمام زمرہ جات' : 'All Categories'}
            </option>
            {categories.data.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Content */}
      <div className="glossary-content">
        {error && renderError()}
        {isLoading && query.trim().length > 0 && renderLoading()}
        {!isLoading && !error && renderResults()}
      </div>

      {/* Footer Stats */}
      {searchResults.data && searchResults.data.length > 0 && (
        <div className="glossary-footer" dir={getDirection()}>
          <small className="result-count">
            {language === 'urdu'
              ? `${searchResults.data.length} نتیجے ملے`
              : `${searchResults.data.length} results found`}
          </small>
        </div>
      )}
    </div>
  );
};

export default ChatbotGlossary;
