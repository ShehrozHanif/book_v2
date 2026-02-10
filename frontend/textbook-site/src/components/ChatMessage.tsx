import React from "react";
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
  const formatCitations = (citations: string[]) => {
    return citations.map((citation, idx) => {
      const relevancePercent = (
        (relevanceScores[idx] || 0) * 100
      ).toFixed(1);
      return (
        <span
          key={idx}
          className="citation"
          title={`Relevance: ${relevancePercent}%`}
          role="doc-note"
        >
          [{idx + 1}]
        </span>
      );
    });
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
