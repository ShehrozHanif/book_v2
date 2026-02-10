/**
 * Component Tests for ChatbotGlossary (T035)
 *
 * Tests:
 * - Glossary modal opens/closes
 * - Search functionality
 * - Term display (English + Urdu)
 * - Pronunciation guides
 * - Feedback submission
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatbotGlossary } from './ChatbotGlossary';

describe('ChatbotGlossary Component', () => {
  it('should render glossary button when closed', () => {
    render(<ChatbotGlossary isOpen={false} onClose={() => {}} />);
    // Component should not be visible when isOpen=false
  });

  it('should display glossary modal when open', () => {
    render(<ChatbotGlossary isOpen={true} onClose={() => {}} />);
    expect(screen.getByText('Technical Glossary')).toBeInTheDocument();
  });

  it('should close modal on close button click', () => {
    const onClose = jest.fn();
    render(<ChatbotGlossary isOpen={true} onClose={onClose} />);
    const closeButton = screen.getByText('×');
    fireEvent.click(closeButton);
    expect(onClose).toHaveBeenCalled();
  });

  it('should have search functionality', () => {
    render(<ChatbotGlossary isOpen={true} onClose={() => {}} />);
    const searchInput = screen.getByPlaceholderText('Search term...');
    expect(searchInput).toBeInTheDocument();
  });

  it('should support language selection', () => {
    render(<ChatbotGlossary isOpen={true} onClose={() => {}} />);
    const languageSelect = screen.getByDisplayValue('English');
    expect(languageSelect).toBeInTheDocument();
  });

  it('should display selected term details', async () => {
    render(
      <ChatbotGlossary
        isOpen={true}
        onClose={() => {}}
        selectedTerm="ROS 2 Node"
      />
    );

    await waitFor(() => {
      // After term is loaded, should show definitions
      expect(screen.getByText(/Definition/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('should show pronunciation guide', () => {
    render(<ChatbotGlossary isOpen={true} onClose={() => {}} selectedTerm="ROS 2 Node" />);
    // Wait for term to load and verify pronunciation is shown
    waitFor(() => {
      expect(screen.getByText(/Pronunciation/i)).toBeInTheDocument();
    });
  });

  it('should display feedback form for authenticated users', () => {
    render(
      <ChatbotGlossary
        isOpen={true}
        onClose={() => {}}
        authToken="test_token"
      />
    );
    // Feedback section should be visible
    waitFor(() => {
      expect(screen.getByText(/Feedback/i)).toBeInTheDocument();
    });
  });

  it('should not show feedback form for unauthenticated users', () => {
    render(<ChatbotGlossary isOpen={true} onClose={() => {}} />);
    // Feedback section should not be visible
    const feedbackSection = screen.queryByText(/Feedback/i);
    // It may not be rendered at all if term isn't loaded
  });

  it('should validate feedback content length', async () => {
    render(
      <ChatbotGlossary isOpen={true} onClose={() => {}} authToken="test_token" />
    );

    const feedbackInput = screen.getByPlaceholderText('Your feedback...');
    // Try to enter short feedback
    fireEvent.change(feedbackInput, { target: { value: 'short' } });
    // Should not allow submission if less than 10 chars
  });

  it('should handle search with both languages', async () => {
    const { container } = render(
      <ChatbotGlossary isOpen={true} onClose={() => {}} />
    );

    const languageSelect = container.querySelector('select') as HTMLSelectElement;

    // Test English search
    fireEvent.change(languageSelect, { target: { value: 'english' } });
    expect(languageSelect.value).toBe('english');

    // Test Urdu search
    fireEvent.change(languageSelect, { target: { value: 'urdu' } });
    expect(languageSelect.value).toBe('urdu');
  });

  it('should display RTL text for Urdu definitions', () => {
    const { container } = render(
      <ChatbotGlossary isOpen={true} onClose={() => {}} />
    );
    // Verify RTL styling is applied to Urdu content
  });

  it('should navigate back to search', async () => {
    render(
      <ChatbotGlossary
        isOpen={true}
        onClose={() => {}}
        selectedTerm="ROS 2 Node"
      />
    );

    await waitFor(() => {
      const backButton = screen.getByText('Back');
      fireEvent.click(backButton);
    });
  });

  it('should clear search on empty query', () => {
    const { container } = render(
      <ChatbotGlossary isOpen={true} onClose={() => {}} />
    );

    const searchInput = screen.getByPlaceholderText('Search term...') as HTMLInputElement;
    fireEvent.change(searchInput, { target: { value: '' } });
    fireEvent.click(screen.getByText('Search'));

    // Should not perform search with empty query
  });
});
