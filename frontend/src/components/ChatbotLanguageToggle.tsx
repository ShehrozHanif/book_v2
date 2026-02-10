"""
ChatbotLanguageToggle Component

A bilingual language selector for the chatbot interface.
- Shows English/Urdu toggle buttons
- Requires authentication for Urdu
- Updates user preference on selection
- Shows RTL text direction for Urdu
"""

import React, { useState, useCallback } from 'react';
import { useLanguagePreference } from '../hooks/useLanguagePreference';
import { useAuth } from '../hooks/useAuth';
import '../styles/chatbot-language-toggle.css';


interface ChatbotLanguageToggleProps {
  currentLanguage?: 'english' | 'urdu';
  onLanguageChange?: (language: 'english' | 'urdu') => Promise<void>;
  isAuthenticated?: boolean;
}


const ChatbotLanguageToggle: React.FC<ChatbotLanguageToggleProps> = ({
  currentLanguage = 'english',
  onLanguageChange,
  isAuthenticated: authProp,
}) => {
  const { isAuthenticated: authHook } = useAuth();
  const { setLanguage, loading, error } = useLanguagePreference();
  const [selectedLanguage, setSelectedLanguage] = useState<'english' | 'urdu'>(
    currentLanguage
  );
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);

  // Use auth from prop or hook
  const isAuthenticated = authProp !== undefined ? authProp : authHook;

  const handleLanguageSelect = useCallback(
    async (language: 'english' | 'urdu') => {
      // Check if trying to access Urdu without authentication
      if (language === 'urdu' && !isAuthenticated) {
        setShowLoginPrompt(true);
        setTimeout(() => setShowLoginPrompt(false), 3000);
        return;
      }

      try {
        setSelectedLanguage(language);

        // Call parent callback if provided
        if (onLanguageChange) {
          await onLanguageChange(language);
        }

        // Save preference to database
        await setLanguage(language);
      } catch (err) {
        console.error('Failed to change language:', err);
        // Revert selection on error
        setSelectedLanguage(currentLanguage);
      }
    },
    [isAuthenticated, currentLanguage, onLanguageChange, setLanguage]
  );

  return (
    <div className="chatbot-language-toggle">
      <div className="language-buttons">
        {/* English Button */}
        <button
          className={`language-button ${selectedLanguage === 'english' ? 'active' : ''}`}
          onClick={() => handleLanguageSelect('english')}
          disabled={loading}
          aria-label="Switch to English"
          aria-pressed={selectedLanguage === 'english'}
          title="English"
        >
          <span className="language-label">English</span>
        </button>

        {/* Urdu Button */}
        <button
          className={`language-button urdu-button ${selectedLanguage === 'urdu' ? 'active' : ''} ${
            !isAuthenticated ? 'disabled' : ''
          }`}
          onClick={() => handleLanguageSelect('urdu')}
          disabled={loading || !isAuthenticated}
          aria-label={
            isAuthenticated
              ? 'Switch to Urdu'
              : 'Sign in to use Urdu'
          }
          aria-pressed={selectedLanguage === 'urdu'}
          title={
            isAuthenticated
              ? 'اردو (Urdu)'
              : 'Sign in to use Urdu'
          }
          dir="rtl"
        >
          <span className="language-label">اردو</span>
        </button>
      </div>

      {/* Loading Indicator */}
      {loading && (
        <div className="loading-indicator">
          <span className="spinner"></span>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message" role="alert">
          {typeof error === 'string' ? error : 'Failed to change language'}
        </div>
      )}

      {/* Login Prompt for Urdu */}
      {showLoginPrompt && !isAuthenticated && (
        <div className="login-prompt" role="alert">
          <span>Sign in to use Urdu</span>
        </div>
      )}
    </div>
  );
};

export default ChatbotLanguageToggle;
