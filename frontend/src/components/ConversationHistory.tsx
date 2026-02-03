import React from "react";

export interface Message {
  id?: string;
  sender: "user" | "bot";
  content: string;
  timestamp: string;
  citations?: string[];
  relevanceScores?: number[];
}

interface ConversationHistoryProps {
  messages: Message[];
  onSelectMessage?: (messageId: string) => void;
  currentConversationId?: string | null;
}

export const ConversationHistory: React.FC<ConversationHistoryProps> = ({
  messages,
  onSelectMessage,
  currentConversationId,
}) => {
  // Show last 20 messages
  const recentMessages = messages.slice(-20);

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

  const truncateContent = (content: string, maxLength: number = 50) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + "...";
  };

  const handleMessageClick = (messageId?: string) => {
    if (messageId && onSelectMessage) {
      onSelectMessage(messageId);
    }
  };

  return (
    <div className="conversation-history" role="complementary" aria-label="Conversation history">
      <div className="history-header">
        <h3>Conversation History</h3>
        {currentConversationId && (
          <p className="conversation-id-badge" title={currentConversationId}>
            ID: {currentConversationId.substring(0, 8)}
          </p>
        )}
      </div>

      <div className="history-list" role="list">
        {recentMessages.length === 0 ? (
          <div className="empty-state">
            <p>No messages yet</p>
            <p className="empty-hint">Start a conversation to see history</p>
          </div>
        ) : (
          recentMessages.map((message, idx) => {
            const isLatest = idx === recentMessages.length - 1;
            const messageId = message.id || `msg_${idx}`;

            return (
              <div
                key={messageId}
                className={`history-item ${message.sender} ${isLatest ? "latest" : ""}`}
                role="listitem"
                onClick={() => handleMessageClick(message.id)}
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    handleMessageClick(message.id);
                  }
                }}
                aria-label={`${message.sender === "user" ? "User" : "Assistant"} message at ${formatTimestamp(message.timestamp)}`}
              >
                <div className="history-item-header">
                  <span className={`sender-label ${message.sender}`}>
                    {message.sender === "user" ? "You" : "Bot"}
                  </span>
                  <span className="message-time">{formatTimestamp(message.timestamp)}</span>
                </div>
                <p className="message-preview" title={message.content}>
                  {truncateContent(message.content)}
                </p>
                {isLatest && <div className="latest-badge">Latest</div>}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ConversationHistory;
