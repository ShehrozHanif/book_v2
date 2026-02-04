/**
 * Shared type definitions for the RAG Chatbot frontend
 */

export interface Message {
  id?: string;
  sender: "user" | "assistant";
  content: string;
  timestamp?: number;
  metadata?: MessageMetadata;
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
