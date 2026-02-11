import React, { useState } from "react";
import { chatApi } from "../services/chatApi";
import "../styles/chat-message.css";

interface ChatMessageProps {
  sender: "user" | "bot";
  content: string;
  timestamp?: string;
  citations?: string[];
  relevanceScores?: number[];
  isHighlighted?: boolean;
  messageId?: string;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  sender,
  content,
  timestamp,
  citations = [],
  relevanceScores = [],
  isHighlighted = false,
  messageId,
}) => {
  const [urduText, setUrduText] = useState<string | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [showUrdu, setShowUrdu] = useState(false);
  const [translateError, setTranslateError] = useState<string | null>(null);

  const handleTranslate = async () => {
    if (urduText) {
      setShowUrdu(!showUrdu);
      return;
    }

    setIsTranslating(true);
    setTranslateError(null);
    try {
      const response = await chatApi.translate({ text: content });
      setUrduText(response.translated_text);
      setShowUrdu(true);
    } catch (err) {
      setTranslateError("Translation failed. Please try again.");
      console.error("Translation error:", err);
    } finally {
      setIsTranslating(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return timestamp;
    }
  };

  return (
    <div
      className={`message message-${sender} ${isHighlighted ? 'message-highlighted' : ''}`}
      data-message-id={messageId}
      role="article"
      aria-label={`${sender === "user" ? "Your message" : "Assistant message"}`}
    >
      <div className="message-content">
        <p className="message-text">{content}</p>

        {/* Urdu Translation - directly under English text */}
        {sender === "bot" && showUrdu && urduText && (
          <div className="urdu-translation" dir="rtl" lang="ur">
            <p className="urdu-text">{urduText}</p>
          </div>
        )}

        {/* Translate Button - before citations, right-aligned */}
        {sender === "bot" && (
          <div className="translate-actions">
            <button
              className={`translate-btn ${showUrdu ? 'translate-btn-active' : ''} ${isTranslating ? 'translate-btn-loading' : ''}`}
              onClick={handleTranslate}
              disabled={isTranslating}
              title={showUrdu ? "Hide Urdu translation" : "Translate to Urdu"}
            >
              {isTranslating ? (
                <span className="translate-spinner">⟳</span>
              ) : showUrdu ? (
                '✓ اردو'
              ) : (
                '🌐 اردو'
              )}
            </button>
            {translateError && (
              <span className="translate-error">{translateError}</span>
            )}
          </div>
        )}

        {citations.length > 0 && (
          <div className="citations-section" aria-label="Citations">
            <div className="citations-label">Sources:</div>
            <ul className="citations-list">
              {citations.map((citation, idx) => (
                <li key={idx} className="citation-item">
                  <span className="citation-badge">[{idx + 1}]</span>
                  <span className="citation-text" title={citation}>
                    {citation.substring(0, 60)}
                    {citation.length > 60 ? "..." : ""}
                  </span>
                  <span className="relevance-score">
                    {((relevanceScores[idx] || 0) * 100).toFixed(0)}%
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {timestamp && (
        <div className="message-time" aria-label="Timestamp">
          {formatTimestamp(timestamp)}
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
