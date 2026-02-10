import React from 'react';
import '../styles/chatbot-message-rtl.css';


interface ChatbotMessageRTLProps {
  content: string;
  language: 'english' | 'urdu';
  timestamp?: Date;
  isLoading?: boolean;
}


const ChatbotMessageRTL: React.FC<ChatbotMessageRTLProps> = ({
  content,
  language,
  timestamp,
  isLoading = false,
}) => {
  /**
   * Detect if text contains code blocks
   */
  const hasCodeBlock = /```[\s\S]*?```|`[^`]*`/g.test(content);

  /**
   * Format content, preserving code blocks as LTR
   */
  const renderContent = () => {
    if (!hasCodeBlock) {
      return <p className="message-text">{content}</p>;
    }

    // Split content by code blocks
    const parts = content.split(/(`[^`]*`|```[\s\S]*?```)/);

    return (
      <div className="message-text">
        {parts.map((part, idx) => {
          if (part.match(/`/)) {
            // This is a code block - keep it LTR
            return (
              <code
                key={idx}
                className="message-code"
                dir="ltr"
              >
                {part.replace(/`/g, '')}
              </code>
            );
          }
          // Regular text
          return <span key={idx}>{part}</span>;
        })}
      </div>
    );
  };

  return (
    <div
      className={`chatbot-message-rtl ${language} ${isLoading ? 'loading' : ''}`}
      dir={language === 'urdu' ? 'rtl' : 'ltr'}
    >
      {/* Message Content */}
      <div className="message-content">
        {renderContent()}
      </div>

      {/* Timestamp */}
      {timestamp && (
        <span className="message-timestamp">
          {timestamp.toLocaleTimeString(
            language === 'urdu' ? 'ur-PK' : 'en-US',
            {
              hour: '2-digit',
              minute: '2-digit',
            }
          )}
        </span>
      )}

      {/* Language Badge */}
      <span className="language-badge">
        {language === 'urdu' ? 'اردو' : 'English'}
      </span>
    </div>
  );
};

export default ChatbotMessageRTL;
