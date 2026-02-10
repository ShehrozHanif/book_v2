// Get API URL from environment or fallback to localhost
const API_BASE_URL =
  (typeof process !== 'undefined' && process.env.REACT_APP_API_URL) ||
  (typeof window !== 'undefined' && (window as any).REACT_APP_API_URL) ||
  "http://127.0.0.1:8000";

export interface ChatRequest {
  query: string;
  selected_text?: string;
  conversation_id?: string;
  user_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  retrieved_passages: string[];
  relevance_scores: number[];
  processing_time_ms: number;
}

export interface EmbedRequest {
  content: string;
  metadata?: Record<string, unknown>;
  document_id?: string;
}

export class ChatApiError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "ChatApiError";
  }
}

export class TimeoutError extends ChatApiError {
  constructor(message: string = "Request timed out") {
    super(408, message);
    this.name = "TimeoutError";
  }
}

export class NetworkError extends ChatApiError {
  constructor(message: string = "Network error") {
    super(0, message);
    this.name = "NetworkError";
  }
}

export const chatApi = {
  /**
   * Send a chat message and get a response
   * @param request Chat request with query and optional context
   * @returns Chat response with answer and retrieved passages
   */
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorBody = await response.text();
        throw new ChatApiError(
          response.status,
          `Chat API error: ${response.statusText} - ${errorBody}`
        );
      }

      const data = await response.json();
      return data as ChatResponse;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ChatApiError) {
        throw error;
      }

      // Handle abort/timeout
      if (error instanceof Error && error.name === "AbortError") {
        throw new TimeoutError("Request timed out after 30 seconds");
      }

      // Handle network errors
      if (error instanceof TypeError) {
        throw new NetworkError("Network error - please check your connection");
      }

      throw new ChatApiError(
        500,
        `Unexpected error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  },

  /**
   * Embed new content into the knowledge base
   * @param request Embed request with content and optional metadata
   */
  async embed(request: EmbedRequest): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/embed`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        throw new ChatApiError(
          response.status,
          `Embed API error: ${response.statusText} - ${errorBody}`
        );
      }
    } catch (error) {
      if (error instanceof ChatApiError) {
        throw error;
      }
      throw new ChatApiError(
        500,
        `Network error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  },

  /**
   * Get conversation history
   * @param conversationId ID of the conversation
   * @returns Array of messages in the conversation
   */
  async getConversation(
    conversationId: string
  ): Promise<Array<{ sender: string; content: string }>> {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new ChatApiError(
          response.status,
          `Failed to fetch conversation: ${response.statusText}`
        );
      }

      const data = await response.json();
      return data as Array<{ sender: string; content: string }>;
    } catch (error) {
      if (error instanceof ChatApiError) {
        throw error;
      }
      throw new ChatApiError(
        500,
        `Network error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  },

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
      });
      return response.ok;
    } catch {
      return false;
    }
  },
};
