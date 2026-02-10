/**
 * ChatbotMessageRTL Component
 *
 * Renders chatbot messages with proper RTL (Right-to-Left) support for Urdu
 * and LTR (Left-to-Right) support for English.
 *
 * Features:
 * - Automatic direction detection based on language
 * - Code blocks remain left-to-right even in RTL context
 * - Proper text alignment for both directions
 * - Mobile responsive
 * - Number and date formatting support
 */

import React, { ReactNode } from 'react';
import '../../styles/chatbot-message-rtl.css';

export interface ChatbotMessageRTLProps {
  /** Content to render (can be string or JSX) */
  children: ReactNode;
  /** Language code: 'english' or 'urdu' */
  language: 'english' | 'urdu';
  /** Optional CSS class names */
  className?: string;
  /** Whether this is a user message (affects styling) */
  isUserMessage?: boolean;
  /** Optional message ID for accessibility */
  messageId?: string;
}

/**
 * ChatbotMessageRTL Component
 *
 * Applies proper RTL/LTR styling and handling for chatbot messages
 */
export const ChatbotMessageRTL: React.FC<ChatbotMessageRTLProps> = ({
  children,
  language,
  className = '',
  isUserMessage = false,
  messageId,
}) => {
  const direction = language === 'urdu' ? 'rtl' : 'ltr';
  const directionClass = language === 'urdu' ? 'dir-rtl' : 'dir-ltr';

  const messageClass = [
    'chatbot-message-rtl',
    directionClass,
    isUserMessage ? 'user-message' : 'assistant-message',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div
      className={messageClass}
      dir={direction}
      lang={language === 'urdu' ? 'ur' : 'en'}
      id={messageId}
      role="article"
      aria-label={`${isUserMessage ? 'User' : 'Assistant'} message in ${language}`}
    >
      {children}
    </div>
  );
};

/**
 * ChatbotMessageContent Component
 *
 * Wrapper for actual message content with proper handling of special elements
 * (code blocks, code inline, etc.)
 */
export interface ChatbotMessageContentProps {
  children: ReactNode;
  language: 'english' | 'urdu';
  className?: string;
}

export const ChatbotMessageContent: React.FC<ChatbotMessageContentProps> = ({
  children,
  language,
  className = '',
}) => {
  const directionClass = language === 'urdu' ? 'dir-rtl' : 'dir-ltr';

  return (
    <div className={`chatbot-message-content ${directionClass} ${className}`}>
      {children}
    </div>
  );
};

/**
 * Helper component for code blocks in RTL context
 * Ensures code stays LTR even when parent is RTL
 */
export interface CodeBlockProps {
  children: ReactNode;
  language?: string;
  className?: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  children,
  language,
  className = '',
}) => {
  return (
    <pre className={`code-block ${className}`} dir="ltr">
      <code className={language ? `language-${language}` : ''}>
        {children}
      </code>
    </pre>
  );
};

/**
 * Helper component for inline code in RTL context
 */
export interface InlineCodeProps {
  children: ReactNode;
  className?: string;
}

export const InlineCode: React.FC<InlineCodeProps> = ({
  children,
  className = '',
}) => {
  return (
    <code className={`inline-code ${className}`} dir="ltr">
      {children}
    </code>
  );
};

export default ChatbotMessageRTL;
