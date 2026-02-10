/**
 * Tests for ChatbotGlossary component (T037)
 *
 * Test coverage:
 * - Component rendering
 * - Search functionality
 * - Category filtering
 * - Loading and error states
 * - Bilingual content display
 * - RTL/LTR support
 * - Accessibility features
 * - User interactions
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatbotGlossary } from './ChatbotGlossary';
import * as useGlossaryModule from '../../hooks/useGlossary';
import * as useLanguagePreferenceModule from '../../hooks/useLanguagePreference';

// Mock the hooks
jest.mock('../../hooks/useGlossary');
jest.mock('../../hooks/useLanguagePreference');

const mockUseGlossary = useGlossaryModule.useGlossary as jest.MockedFunction<
  typeof useGlossaryModule.useGlossary
>;
const mockUseLanguagePreference = useLanguagePreferenceModule.useLanguagePreference as jest.MockedFunction<
  typeof useLanguagePreferenceModule.useLanguagePreference
>;

// Mock glossary data
const mockGlossaryTerms = [
  {
    id: 'term-1',
    english_term: 'Sensor',
    urdu_translation: 'سینسر',
    pronunciation_transliterated: 'sensor',
    definition_english: 'A device that detects changes',
    definition_urdu: 'ایک آلہ جو تبدیلی کا پتہ لگاتا ہے',
    category: 'robotics',
    status: 'active',
    related_terms: ['Actuator', 'Feedback'],
  },
  {
    id: 'term-2',
    english_term: 'Actuator',
    urdu_translation: 'ایکچوایٹر',
    pronunciation_transliterated: 'actuator',
    definition_english: 'A device that produces motion',
    definition_urdu: 'ایک آلہ جو حرکت پیدا کرتا ہے',
    category: 'robotics',
    status: 'active',
  },
];

const mockCategories = ['robotics', 'control', 'kinematics'];

const defaultUseGlossaryReturn = {
  searchTerms: jest.fn(),
  getCategories: jest.fn(),
  getTerm: jest.fn(),
  searchResults: { data: [], isLoading: false, error: null },
  categories: { data: mockCategories, isLoading: false, error: null },
  isLoading: false,
  error: null,
  clearCache: jest.fn(),
  invalidateCache: jest.fn(),
};

const defaultUseLanguagePreferenceReturn = {
  language: 'english' as const,
  setLanguage: jest.fn(),
};

describe('ChatbotGlossary Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseGlossary.mockReturnValue(defaultUseGlossaryReturn);
    mockUseLanguagePreference.mockReturnValue(defaultUseLanguagePreferenceReturn);
  });

  /**
   * Rendering tests
   */
  describe('rendering', () => {
    it('should render glossary component', () => {
      render(<ChatbotGlossary />);

      expect(screen.getByRole('region')).toBeInTheDocument();
      expect(screen.getByText('Glossary')).toBeInTheDocument();
    });

    it('should display title and subtitle', () => {
      render(<ChatbotGlossary />);

      expect(screen.getByText('Glossary')).toBeInTheDocument();
      expect(screen.getByText('Search technical terminology')).toBeInTheDocument();
    });

    it('should render search input', () => {
      render(<ChatbotGlossary />);

      const searchInput = screen.getByPlaceholderText('Search terms...');
      expect(searchInput).toBeInTheDocument();
    });

    it('should render category filter', () => {
      render(<ChatbotGlossary />);

      const categorySelect = screen.getByLabelText('Select category');
      expect(categorySelect).toBeInTheDocument();
      expect(categorySelect).toHaveValue('');
    });

    it('should apply expanded class when expanded prop is true', () => {
      const { container } = render(<ChatbotGlossary expanded={true} />);

      expect(container.querySelector('.chatbot-glossary.expanded')).toBeInTheDocument();
    });

    it('should apply compact class when expanded prop is false', () => {
      const { container } = render(<ChatbotGlossary expanded={false} />);

      expect(container.querySelector('.chatbot-glossary.compact')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(<ChatbotGlossary className="custom-class" />);

      expect(container.querySelector('.chatbot-glossary.custom-class')).toBeInTheDocument();
    });
  });

  /**
   * Search functionality tests
   */
  describe('search functionality', () => {
    it('should update search input on user input', async () => {
      render(<ChatbotGlossary />);

      const searchInput = screen.getByPlaceholderText('Search terms...') as HTMLInputElement;
      await userEvent.type(searchInput, 'sensor');

      expect(searchInput.value).toBe('sensor');
    });

    it('should call searchTerms when user types', async () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchTerms: jest.fn().mockResolvedValue([]),
      });

      render(<ChatbotGlossary />);

      const searchInput = screen.getByPlaceholderText('Search terms...');
      await userEvent.type(searchInput, 'sensor');

      await waitFor(() => {
        expect(mockUseGlossary().searchTerms).toHaveBeenCalled();
      });
    });

    it('should display search results', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary />);

      // Should render term names
      expect(screen.getByText('Sensor')).toBeInTheDocument();
      expect(screen.getByText('Actuator')).toBeInTheDocument();
    });

    it('should display empty state when no search query', () => {
      render(<ChatbotGlossary />);

      expect(screen.getByText(/Type above to search for terms/i)).toBeInTheDocument();
    });

    it('should display no results message when search returns empty', async () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: [], isLoading: false, error: null },
      });

      render(<ChatbotGlossary initialQuery="nonexistent" />);

      await waitFor(() => {
        expect(screen.getByText(/No results found for "nonexistent"/i)).toBeInTheDocument();
      });
    });

    it('should clear search when clear button clicked', async () => {
      render(<ChatbotGlossary initialQuery="sensor" />);

      const clearButton = screen.getByLabelText('Clear');
      await userEvent.click(clearButton);

      expect(screen.getByPlaceholderText('Search terms...')).toHaveValue('');
    });

    it('should show clear button when search has value', () => {
      render(<ChatbotGlossary initialQuery="sensor" />);

      expect(screen.getByLabelText('Clear')).toBeInTheDocument();
    });
  });

  /**
   * Category filtering tests
   */
  describe('category filtering', () => {
    it('should populate category filter with available categories', () => {
      render(<ChatbotGlossary />);

      const categorySelect = screen.getByLabelText('Select category') as HTMLSelectElement;
      const options = Array.from(categorySelect.options);

      expect(options).toHaveLength(mockCategories.length + 1); // +1 for "All Categories"
    });

    it('should call searchTerms with category when selected', async () => {
      const searchTermsMock = jest.fn();
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchTerms: searchTermsMock,
      });

      render(<ChatbotGlossary initialQuery="sensor" />);

      const categorySelect = screen.getByLabelText('Select category');
      await userEvent.selectOptions(categorySelect, 'robotics');

      await waitFor(() => {
        expect(searchTermsMock).toHaveBeenCalledWith(
          'sensor',
          'english',
          'robotics',
          20
        );
      });
    });

    it('should reset category when "All Categories" selected', async () => {
      const searchTermsMock = jest.fn();
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchTerms: searchTermsMock,
      });

      render(<ChatbotGlossary initialQuery="sensor" />);

      const categorySelect = screen.getByLabelText('Select category');

      // Select category
      await userEvent.selectOptions(categorySelect, 'robotics');

      // Reset to all
      await userEvent.selectOptions(categorySelect, '');

      await waitFor(() => {
        expect(searchTermsMock).toHaveBeenCalledWith(
          'sensor',
          'english',
          undefined,
          20
        );
      });
    });
  });

  /**
   * Bilingual support tests
   */
  describe('bilingual support', () => {
    it('should display Urdu content when language is Urdu', () => {
      mockUseLanguagePreference.mockReturnValue({
        language: 'urdu',
        setLanguage: jest.fn(),
      });

      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary />);

      // Should display Urdu title
      expect(screen.getByText('اصطلاحات کی فہرست')).toBeInTheDocument();

      // Should display Urdu translations
      expect(screen.getByText('سینسر')).toBeInTheDocument();
    });

    it('should display English content when language is English', () => {
      mockUseLanguagePreference.mockReturnValue({
        language: 'english',
        setLanguage: jest.fn(),
      });

      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary />);

      expect(screen.getByText('Glossary')).toBeInTheDocument();
      expect(screen.getByText('Sensor')).toBeInTheDocument();
    });

    it('should display term definitions in correct language', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary />);

      expect(screen.getByText('A device that detects changes')).toBeInTheDocument();
      expect(screen.getByText('ایک آلہ جو تبدیلی کا پتہ لگاتا ہے')).toBeInTheDocument();
    });

    it('should display related terms', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary />);

      expect(screen.getByText(/Actuator, Feedback/)).toBeInTheDocument();
    });

    it('should display pronunciation guides', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary />);

      expect(screen.getByText('sensor')).toBeInTheDocument();
    });
  });

  /**
   * Loading state tests
   */
  describe('loading state', () => {
    it('should display loading state when isLoading is true', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        isLoading: true,
        searchResults: { data: null, isLoading: true, error: null },
      });

      render(<ChatbotGlossary initialQuery="sensor" />);

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should display loading text in Urdu when language is Urdu', () => {
      mockUseLanguagePreference.mockReturnValue({
        language: 'urdu',
        setLanguage: jest.fn(),
      });

      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        isLoading: true,
        searchResults: { data: null, isLoading: true, error: null },
      });

      render(<ChatbotGlossary initialQuery="sensor" />);

      expect(screen.getByText('لوڈ ہو رہا ہے...')).toBeInTheDocument();
    });

    it('should not show loading when search query is empty', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        isLoading: true,
      });

      render(<ChatbotGlossary />);

      expect(screen.queryByRole('status')).not.toBeInTheDocument();
    });
  });

  /**
   * Error state tests
   */
  describe('error handling', () => {
    it('should display error message when error occurs', () => {
      const error = new Error('Search failed');
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        error,
      });

      render(<ChatbotGlossary initialQuery="sensor" />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/Search failed/)).toBeInTheDocument();
    });

    it('should display retry button on error', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        error: new Error('Search failed'),
      });

      render(<ChatbotGlossary initialQuery="sensor" />);

      expect(screen.getByText('Retry')).toBeInTheDocument();
    });

    it('should call clearCache when retry button clicked', async () => {
      const clearCacheMock = jest.fn();
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        error: new Error('Search failed'),
        clearCache: clearCacheMock,
      });

      render(<ChatbotGlossary initialQuery="sensor" />);

      const retryButton = screen.getByText('Retry');
      await userEvent.click(retryButton);

      expect(clearCacheMock).toHaveBeenCalled();
    });
  });

  /**
   * RTL/LTR support tests
   */
  describe('RTL/LTR support', () => {
    it('should set dir="ltr" for English content', () => {
      mockUseLanguagePreference.mockReturnValue({
        language: 'english',
        setLanguage: jest.fn(),
      });

      const { container } = render(<ChatbotGlossary />);

      expect(container.querySelector('[dir="ltr"]')).toBeInTheDocument();
    });

    it('should set dir="rtl" for Urdu content', () => {
      mockUseLanguagePreference.mockReturnValue({
        language: 'urdu',
        setLanguage: jest.fn(),
      });

      const { container } = render(<ChatbotGlossary />);

      expect(container.querySelector('[dir="rtl"]')).toBeInTheDocument();
    });

    it('should set lang attribute correctly', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      const { container } = render(<ChatbotGlossary />);

      const termCards = container.querySelectorAll('.glossary-term-card');
      expect(termCards[0]).toHaveAttribute('lang', 'en');
    });
  });

  /**
   * Accessibility tests
   */
  describe('accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<ChatbotGlossary />);

      expect(screen.getByLabelText('Search terms')).toBeInTheDocument();
      expect(screen.getByLabelText('Select category')).toBeInTheDocument();
    });

    it('should have region role', () => {
      render(<ChatbotGlossary />);

      expect(screen.getByRole('region')).toBeInTheDocument();
    });

    it('should have status role for loading state', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        isLoading: true,
        searchResults: { data: null, isLoading: true, error: null },
      });

      render(<ChatbotGlossary initialQuery="sensor" />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should have alert role for errors', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        error: new Error('Search failed'),
      });

      render(<ChatbotGlossary initialQuery="sensor" />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      const { container } = render(<ChatbotGlossary />);

      const termCard = container.querySelector('.glossary-term-card') as HTMLElement;

      // Should be focusable
      termCard?.focus();
      expect(document.activeElement).toBe(termCard);

      // Should trigger on Enter
      fireEvent.keyDown(termCard, { key: 'Enter' });

      // Should trigger on Space
      fireEvent.keyDown(termCard, { key: ' ' });
    });
  });

  /**
   * Callback tests
   */
  describe('callbacks', () => {
    it('should call onTermSelect when term is clicked', async () => {
      const onTermSelect = jest.fn();
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary onTermSelect={onTermSelect} />);

      const termCard = screen.getByText('Sensor').closest('.glossary-term-card') as HTMLElement;
      await userEvent.click(termCard);

      expect(onTermSelect).toHaveBeenCalledWith('term-1', 'Sensor');
    });

    it('should pass initialQuery prop', () => {
      render(<ChatbotGlossary initialQuery="sensor" />);

      expect(screen.getByDisplayValue('sensor')).toBeInTheDocument();
    });

    it('should respect maxResults prop', async () => {
      const searchTermsMock = jest.fn();
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchTerms: searchTermsMock,
      });

      render(<ChatbotGlossary initialQuery="test" maxResults={50} />);

      await waitFor(() => {
        expect(searchTermsMock).toHaveBeenCalledWith(
          'test',
          'english',
          undefined,
          50
        );
      });
    });
  });

  /**
   * Category display tests
   */
  describe('category display', () => {
    it('should display category badges', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary />);

      const categoryBadges = screen.getAllByText('robotics');
      expect(categoryBadges.length).toBeGreaterThan(0);
    });
  });

  /**
   * Result count display tests
   */
  describe('result count', () => {
    it('should display result count when results exist', () => {
      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary initialQuery="test" />);

      expect(screen.getByText('2 results found')).toBeInTheDocument();
    });

    it('should display result count in Urdu', () => {
      mockUseLanguagePreference.mockReturnValue({
        language: 'urdu',
        setLanguage: jest.fn(),
      });

      mockUseGlossary.mockReturnValue({
        ...defaultUseGlossaryReturn,
        searchResults: { data: mockGlossaryTerms, isLoading: false, error: null },
      });

      render(<ChatbotGlossary initialQuery="test" />);

      expect(screen.getByText('2 نتیجے ملے')).toBeInTheDocument();
    });
  });
});
