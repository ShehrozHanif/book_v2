"""
Component tests for ChatbotLanguageToggle component.

Tests the bilingual language selection UI component:
1. Display toggle for English/Urdu
2. Handle language selection
3. Show authentication requirement for Urdu
4. Update preference on selection
5. Persist selection
"""

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ChatbotLanguageToggle from './ChatbotLanguageToggle';


describe('ChatbotLanguageToggle Component', () => {
  const mockOnLanguageChange = jest.fn();
  const mockSetLanguagePreference = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockOnLanguageChange.mockResolvedValue(true);
    mockSetLanguagePreference.mockResolvedValue(true);
  });

  describe('Rendering', () => {
    test('renders language toggle buttons', () => {
      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      expect(screen.getByRole('button', { name: /english/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /urdu/i })).toBeInTheDocument();
    });

    test('highlights current language selection', () => {
      render(
        <ChatbotLanguageToggle
          currentLanguage="urdu"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      expect(urduButton).toHaveClass('selected');
    });

    test('shows both language options', () => {
      const { container } = render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      expect(screen.getByText('English')).toBeInTheDocument();
      expect(screen.getByText('اردو')).toBeInTheDocument(); // Urdu script
    });
  });

  describe('Language Selection', () => {
    test('calls onLanguageChange when language is selected', async () => {
      const user = userEvent.setup();
      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      await user.click(urduButton);

      expect(mockOnLanguageChange).toHaveBeenCalledWith('urdu');
    });

    test('changes highlight when language is selected', async () => {
      const user = userEvent.setup();
      const { rerender } = render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      await user.click(urduButton);

      // Simulate language change in parent component
      rerender(
        <ChatbotLanguageToggle
          currentLanguage="urdu"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      expect(urduButton).toHaveClass('selected');
    });

    test('handles switching between languages', async () => {
      const user = userEvent.setup();
      const { rerender } = render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      // Switch to Urdu
      await user.click(screen.getByRole('button', { name: /urdu/i }));
      expect(mockOnLanguageChange).toHaveBeenCalledWith('urdu');

      rerender(
        <ChatbotLanguageToggle
          currentLanguage="urdu"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      // Switch back to English
      await user.click(screen.getByRole('button', { name: /english/i }));
      expect(mockOnLanguageChange).toHaveBeenCalledWith('english');
    });
  });

  describe('Authentication Requirement for Urdu', () => {
    test('disables Urdu option for unauthenticated users', () => {
      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={false}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      expect(urduButton).toBeDisabled();
    });

    test('shows login prompt when unauthenticated user clicks Urdu', async () => {
      const user = userEvent.setup();
      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={false}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      await user.click(urduButton);

      // Should show login message or tooltip
      await waitFor(() => {
        expect(
          screen.getByText(/sign in|login|authenticate/i)
        ).toBeInTheDocument();
      });
    });

    test('tooltip indicates Urdu requires login', () => {
      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={false}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      expect(urduButton).toHaveAttribute('aria-label', expect.stringMatching(/login|sign in/i));
    });

    test('enables Urdu for authenticated users', () => {
      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      expect(urduButton).not.toBeDisabled();
    });
  });

  describe('Visual States', () => {
    test('applies active state to selected language', () => {
      render(
        <ChatbotLanguageToggle
          currentLanguage="urdu"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      const englishButton = screen.getByRole('button', { name: /english/i });

      expect(urduButton).toHaveClass('active');
      expect(englishButton).not.toHaveClass('active');
    });

    test('shows loading state while changing language', async () => {
      const user = userEvent.setup();
      mockOnLanguageChange.mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      const { container } = render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      await user.click(urduButton);

      // Should show loading indicator
      expect(container.querySelector('.loading')).toBeInTheDocument();
    });

    test('shows RTL attribute for Urdu text', () => {
      const { container } = render(
        <ChatbotLanguageToggle
          currentLanguage="urdu"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      // Component should have RTL attributes when Urdu selected
      const urduElements = container.querySelectorAll('[dir="rtl"]');
      expect(urduElements.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    test('buttons have proper ARIA labels', () => {
      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      const englishButton = screen.getByRole('button', { name: /english/i });
      const urduButton = screen.getByRole('button', { name: /urdu/i });

      expect(englishButton).toHaveAttribute('aria-label');
      expect(urduButton).toHaveAttribute('aria-label');
    });

    test('indicates current selection with aria-pressed', () => {
      render(
        <ChatbotLanguageToggle
          currentLanguage="urdu"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      const urduButton = screen.getByRole('button', { name: /urdu/i });
      const englishButton = screen.getByRole('button', { name: /english/i });

      expect(urduButton).toHaveAttribute('aria-pressed', 'true');
      expect(englishButton).toHaveAttribute('aria-pressed', 'false');
    });

    test('keyboard navigation works', async () => {
      const user = userEvent.setup();
      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      const englishButton = screen.getByRole('button', { name: /english/i });
      englishButton.focus();

      // Tab to next button
      await user.tab();
      expect(screen.getByRole('button', { name: /urdu/i })).toHaveFocus();

      // Activate with Enter
      await user.keyboard('{Enter}');
      expect(mockOnLanguageChange).toHaveBeenCalledWith('urdu');
    });
  });

  describe('Error Handling', () => {
    test('handles language change error gracefully', async () => {
      const user = userEvent.setup();
      mockOnLanguageChange.mockRejectedValue(new Error('Network error'));

      const { container } = render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      await user.click(screen.getByRole('button', { name: /urdu/i }));

      await waitFor(() => {
        expect(container.querySelector('.error-message')).toBeInTheDocument();
      });
    });

    test('shows error message on failed preference update', async () => {
      const user = userEvent.setup();
      mockOnLanguageChange.mockRejectedValue(
        new Error('Failed to save preference')
      );

      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      await user.click(screen.getByRole('button', { name: /urdu/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/failed|error/i)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Props and Integration', () => {
    test('accepts currentLanguage prop', () => {
      const { rerender } = render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      expect(
        screen.getByRole('button', { name: /english/i })
      ).toHaveClass('active');

      rerender(
        <ChatbotLanguageToggle
          currentLanguage="urdu"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      expect(
        screen.getByRole('button', { name: /urdu/i })
      ).toHaveClass('active');
    });

    test('respects isAuthenticated prop', () => {
      const { rerender } = render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={false}
        />
      );

      expect(screen.getByRole('button', { name: /urdu/i })).toBeDisabled();

      rerender(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      expect(screen.getByRole('button', { name: /urdu/i })).not.toBeDisabled();
    });

    test('calls callback with correct language value', async () => {
      const user = userEvent.setup();
      render(
        <ChatbotLanguageToggle
          currentLanguage="english"
          onLanguageChange={mockOnLanguageChange}
          isAuthenticated={true}
        />
      );

      await user.click(screen.getByRole('button', { name: /urdu/i }));
      expect(mockOnLanguageChange).toHaveBeenCalledWith('urdu');

      await user.click(screen.getByRole('button', { name: /english/i }));
      expect(mockOnLanguageChange).toHaveBeenCalledWith('english');
    });
  });
});
