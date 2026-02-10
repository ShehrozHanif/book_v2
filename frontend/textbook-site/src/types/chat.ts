/**
 * Shared type definitions for the RAG Chatbot frontend
 */

export interface Message {
  id?: string;
  sender: "user" | "bot";
  content: string;
  timestamp?: string;
  citations?: string[];
  relevanceScores?: number[];
}

export interface MessageMetadata {
  selectedText?: string;
  conversationId?: string;
  relevanceScores?: number[];
  retrievedPassages?: string[];
}

export interface Conversation {
  id: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
  title?: string;
}

export interface SelectedTextContext {
  text: string;
  context?: string;
  timestamp: number;
}

export interface ApiError {
  statusCode: number;
  message: string;
  details?: unknown;
}
