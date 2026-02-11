import React, { useState, useRef, useEffect } from "react";
import { ChatInput } from "./ChatInput";
import { ChatMessage } from "./ChatMessage";
import { LoadingIndicator } from "./LoadingIndicator";
import { ConversationHistory } from "./ConversationHistory";
import { ErrorMessage } from "./ErrorMessage";
import { useChat } from "../hooks/useChat";
import { useTextSelection } from "../hooks/useTextSelection";
import { useLanguagePreference } from "../hooks/useLanguagePreference";
import { useAuth } from "../hooks/useAuth";
import "../styles/chatbot.css";

interface ChatBotProps {
  onMessage?: (message: string) => void;
}

export const ChatBot: React.FC<ChatBotProps> = ({ onMessage }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showHistory, setShowHistory] = useState(window.innerWidth > 768);
  const [highlightedMessageId, setHighlightedMessageId] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();
  const {
    messages,
    isLoading,
    error,
    errorType,
    sendMessage,
    conversationId,
    clearError,
    retryLastMessage
  } = useChat();
  const { selectedText, clearSelection, hasSelection } = useTextSelection();
  const { language } = useLanguagePreference();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Track elapsed time while loading
  useEffect(() => {
    if (!isLoading) {
      setElapsedTime(0);
      return;
    }

    const interval = setInterval(() => {
      setElapsedTime((prev) => prev + 100);
    }, 100);

    return () => clearInterval(interval);
  }, [isLoading]);

  // Update showHistory based on window resize
  useEffect(() => {
    const handleResize = () => {
      setShowHistory(window.innerWidth > 768);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleSendMessage = (message: string) => {
    // Call optional callback if provided
    if (onMessage) {
      onMessage(message);
    }
    // Send through the useChat hook
    sendMessage(message, selectedText?.text);
  };

  const handleSelectMessage = React.useCallback((messageId: string) => {
    setHighlightedMessageId(messageId);

    const messageElement = messagesContainerRef.current?.querySelector(
      `[data-message-id="${messageId}"]`
    );

    if (messageElement) {
      messageElement.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });

      setTimeout(() => setHighlightedMessageId(null), 3000);
    }
  }, []);

  return (
    <div className={`chatbot-widget ${isOpen ? "open" : "closed"}`}>
      {/* Toggle Button */}
      <button
        className="chatbot-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle chatbot"
        aria-expanded={isOpen}
        title="Open chatbot"
      >
        💬
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="chatbot-container">
          {/* Header */}
          <div className="chatbot-header">
            <div className="header-content">
              <h3>Humanoid Robotics Assistant</h3>
              {conversationId && (
                <p className="conversation-id">
                  Conversation: {conversationId.substring(0, 8)}
                </p>
              )}
            </div>
            <div className="header-actions">
              <button
                onClick={() => setIsOpen(false)}
                className="close-btn"
                aria-label="Close chatbot"
                title="Close chatbot"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="chatbot-main">
            {!isAuthenticated ? (
              /* Auth Gate - Login Required */
              <div className="chatbot-auth-gate">
                <div className="auth-gate-content">
                  <div className="auth-gate-icon">🔒</div>
                  <h4 className="auth-gate-title">Sign in to start chatting</h4>
                  <p className="auth-gate-subtitle">
                    Log in to access the AI-powered textbook assistant
                  </p>
                  <button
                    className="auth-gate-login-btn"
                    onClick={() => { window.location.href = "/book/login"; }}
                  >
                    Login
                  </button>
                </div>
              </div>
            ) : (
              <>
                {/* Conversation History Sidebar (Desktop Only) */}
                {showHistory && window.innerWidth > 768 && (
                  <ConversationHistory
                    messages={messages}
                    currentConversationId={conversationId}
                    onSelectMessage={handleSelectMessage}
                  />
                )}

                {/* Messages Panel */}
                <div className="messages-panel">
                  {/* Messages Container */}
                  <div className="messages-container" ref={messagesContainerRef}>
                    {messages.length === 0 && (
                      <div className="welcome-message">
                        <p>👋 Hello! I'm here to help you understand the textbook.</p>
                        <p>
                          {selectedText
                            ? `I noticed you selected: "${selectedText.text.substring(0, 40)}..."`
                            : "Select any text and ask me a question about it!"}
                        </p>
                      </div>
                    )}

                    {messages.map((msg, idx) => (
                      <ChatMessage
                        key={msg.id || idx}
                        sender={msg.sender}
                        content={msg.content}
                        timestamp={msg.timestamp}
                        citations={msg.citations}
                        relevanceScores={msg.relevanceScores}
                        isHighlighted={highlightedMessageId === msg.id}
                        messageId={msg.id}
                        language={language as "english" | "urdu"}
                      />
                    ))}

                    <LoadingIndicator isVisible={isLoading} elapsedTime={elapsedTime} />

                    {error && (
                      <ErrorMessage
                        error={error}
                        errorType={errorType}
                        onRetry={errorType !== "user" ? retryLastMessage : undefined}
                        onDismiss={clearError}
                      />
                    )}

                    <div
                      ref={messagesEndRef}
                      aria-label="Messages end"
                      style={{ height: 0 }}
                    />
                  </div>

                  {/* Input Form */}
                  <ChatInput
                    onSendMessage={handleSendMessage}
                    isLoading={isLoading}
                    selectedText={selectedText}
                    error={error}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBot;
