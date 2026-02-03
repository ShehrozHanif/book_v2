import { useState, useCallback, useRef, useEffect } from "react";
import { chatApi, ChatResponse, ChatApiError, TimeoutError, NetworkError } from "../services/chatApi";

export interface Message {
  id?: string;
  sender: "user" | "bot";
  content: string;
  timestamp: string;
  citations?: string[];
  relevanceScores?: number[];
}

export type ErrorType = "user" | "api" | "timeout" | "network";

export const useChat = (initialConversationId?: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<ErrorType>("api");
  const [currentConversationId, setCurrentConversationId] = useState<
    string | null
  >(initialConversationId || null);
  const [lastQuery, setLastQuery] = useState<string | null>(null);
  const [lastSelectedText, setLastSelectedText] = useState<string | undefined>(undefined);
  const loadingStartTime = useRef<number | null>(null);
  const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Load conversation_id from sessionStorage on mount
  useEffect(() => {
    const savedConversationId = sessionStorage.getItem("current-conversation-id");
    if (savedConversationId && !currentConversationId) {
      setCurrentConversationId(savedConversationId);
      loadConversation(savedConversationId);
    }
  }, []);

  // Cleanup error timeout on unmount
  useEffect(() => {
    return () => {
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current);
      }
    };
  }, []);

  const sendMessage = useCallback(
    async (query: string, selectedText?: string) => {
      // Validate input
      if (!query.trim()) {
        setError("Please enter a message");
        setErrorType("user");
        return;
      }

      setIsLoading(true);
      setError(null);
      setLastQuery(query);
      setLastSelectedText(selectedText);
      loadingStartTime.current = Date.now();

      // Clear any existing error timeout
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current);
      }

      // Add user message to UI immediately (optimistic UI)
      const userMessage: Message = {
        id: `user_${Date.now()}`,
        sender: "user",
        content: query,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        // Call backend API
        const response: ChatResponse = await chatApi.chat({
          query,
          selected_text: selectedText,
          conversation_id: currentConversationId || undefined,
        });

        // Update conversation ID if new or changed
        if (response.conversation_id !== currentConversationId) {
          setCurrentConversationId(response.conversation_id);
          sessionStorage.setItem(
            "current-conversation-id",
            response.conversation_id
          );
        }

        // Add bot message with citations
        const botMessage: Message = {
          id: `${response.conversation_id}_${Date.now()}`,
          sender: "bot",
          content: response.response,
          citations: response.retrieved_passages,
          relevanceScores: response.relevance_scores,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, botMessage]);

        // Save to sessionStorage (last 10 messages for persistence)
        const allMessages = [...messages, userMessage, botMessage];
        const lastTenMessages = allMessages.slice(-10);
        sessionStorage.setItem(
          `chat-messages-${response.conversation_id}`,
          JSON.stringify(lastTenMessages)
        );
      } catch (err) {
        // Enhanced error handling with type detection
        let errorMessage = "Failed to get response";
        let detectedErrorType: ErrorType = "api";

        if (err instanceof ChatApiError) {
          errorMessage = err.message;

          // Determine error type based on status code
          if (err.statusCode === 400) {
            detectedErrorType = "user";
          } else if (err.statusCode === 429) {
            detectedErrorType = "api";
            errorMessage = "Too many requests. Please wait a moment.";
          } else if (err.statusCode === 408 || err.statusCode === 504) {
            detectedErrorType = "timeout";
          } else if (err.statusCode >= 500) {
            detectedErrorType = "api";
          }
        } else if (err instanceof Error) {
          errorMessage = err.message;

          // Check for network errors
          if (errorMessage.toLowerCase().includes("network") ||
              errorMessage.toLowerCase().includes("fetch")) {
            detectedErrorType = "network";
          } else if (errorMessage.toLowerCase().includes("timeout")) {
            detectedErrorType = "timeout";
          }
        }

        setError(errorMessage);
        setErrorType(detectedErrorType);

        // Remove the optimistic user message on error
        setMessages((prev) => prev.slice(0, -1));

        console.error("Chat error:", err);

        // Auto-clear error after 5 seconds
        errorTimeoutRef.current = setTimeout(() => {
          setError(null);
        }, 5000);
      } finally {
        setIsLoading(false);
        loadingStartTime.current = null;
      }
    },
    [currentConversationId, messages]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    // Clear sessionStorage
    if (currentConversationId) {
      sessionStorage.removeItem(`chat-messages-${currentConversationId}`);
    }
  }, [currentConversationId]);

  const clearError = useCallback(() => {
    setError(null);
    if (errorTimeoutRef.current) {
      clearTimeout(errorTimeoutRef.current);
    }
  }, []);

  const retryLastMessage = useCallback(async () => {
    if (lastQuery) {
      await sendMessage(lastQuery, lastSelectedText);
    }
  }, [lastQuery, lastSelectedText, sendMessage]);

  const loadConversation = useCallback(
    async (conversationId: string) => {
      try {
        setIsLoading(true);
        setError(null);

        // Load messages from sessionStorage first
        const cachedMessages = sessionStorage.getItem(
          `chat-messages-${conversationId}`
        );
        if (cachedMessages) {
          setMessages(JSON.parse(cachedMessages));
        } else {
          // Fetch from API if not in sessionStorage
          const history = await chatApi.getConversation(conversationId);
          const loadedMessages: Message[] = history.map((msg) => ({
            sender: msg.sender as "user" | "bot",
            content: msg.content,
            timestamp: new Date().toISOString(),
          }));
          setMessages(loadedMessages);
          sessionStorage.setItem(
            `chat-messages-${conversationId}`,
            JSON.stringify(loadedMessages)
          );
        }

        setCurrentConversationId(conversationId);
        sessionStorage.setItem("current-conversation-id", conversationId);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load conversation";
        setError(errorMessage);
        console.error("Load conversation error:", err);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return {
    messages,
    isLoading,
    error,
    errorType,
    conversationId: currentConversationId,
    sendMessage,
    clearMessages,
    clearError,
    retryLastMessage,
    loadConversation,
  };
};
