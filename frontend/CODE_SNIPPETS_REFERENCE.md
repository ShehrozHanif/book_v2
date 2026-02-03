# Code Snippets Reference - Phase 2 Frontend Setup

## Quick Copy-Paste Examples

### ChatBot Component

#### Basic Usage
```typescript
import { ChatBot } from "./src";

export function App() {
  return <ChatBot />;
}
```

#### With Message Callback
```typescript
import { ChatBot } from "./src";

export function App() {
  const handleMessage = (message: string) => {
    console.log("User said:", message);
  };

  return <ChatBot onMessage={handleMessage} />;
}
```

#### Integration with API
```typescript
import { ChatBot, chatApi } from "./src";

export function App() {
  const handleMessage = async (message: string) => {
    try {
      const response = await chatApi.chat({ query: message });
      // Response now available in component state
      console.log("Assistant:", response.response);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return <ChatBot onMessage={handleMessage} />;
}
```

---

### Text Selection Hook

#### Basic Usage
```typescript
import { useTextSelection } from "./src";

export function MyComponent() {
  const { selectedText, hasSelection } = useTextSelection();

  return (
    <div>
      {hasSelection && (
        <p>You selected: {selectedText?.text}</p>
      )}
    </div>
  );
}
```

#### With Context Length Configuration
```typescript
import { useTextSelection } from "./src";

export function MyComponent() {
  // Capture up to 500 characters of context
  const { selectedText, clearSelection } = useTextSelection(500);

  if (selectedText) {
    return (
      <div>
        <p>Selected: {selectedText.text}</p>
        <p>Context: {selectedText.context}</p>
        <p>Time: {new Date(selectedText.timestamp).toLocaleString()}</p>
        <button onClick={clearSelection}>Clear</button>
      </div>
    );
  }

  return <p>Select some text...</p>;
}
```

#### Integration with Chat Context
```typescript
import { ChatBot, useTextSelection, chatApi } from "./src";

export function AppWithContext() {
  const { selectedText } = useTextSelection();

  const handleMessage = async (query: string) => {
    const response = await chatApi.chat({
      query,
      selected_text: selectedText?.text // Include selected context
    });
    console.log(response);
  };

  return <ChatBot onMessage={handleMessage} />;
}
```

---

### Chat API Service

#### Send a Message
```typescript
import { chatApi } from "./src";

async function askQuestion() {
  const response = await chatApi.chat({
    query: "What is humanoid robotics?"
  });

  console.log("Answer:", response.response);
  console.log("Sources:", response.retrieved_passages);
  console.log("Scores:", response.relevance_scores);
  console.log("Time:", response.processing_time_ms);
}
```

#### With Selected Text Context
```typescript
import { chatApi } from "./src";

async function askWithContext() {
  const response = await chatApi.chat({
    query: "Explain this in more detail",
    selected_text: "The humanoid robot can walk on two legs..."
  });

  console.log(response.response);
}
```

#### With Conversation Tracking
```typescript
import { chatApi } from "./src";

let conversationId: string;

async function startConversation() {
  const response = await chatApi.chat({
    query: "What is humanoid robotics?"
  });

  conversationId = response.conversation_id;
  console.log("Response:", response.response);
}

async function continueConversation() {
  const response = await chatApi.chat({
    query: "Tell me more about that",
    conversation_id: conversationId
  });

  console.log("Follow-up response:", response.response);
}
```

#### With User ID (Multi-user)
```typescript
import { chatApi } from "./src";

async function chatAsUser(userId: string) {
  const response = await chatApi.chat({
    query: "My question here",
    user_id: userId
  });

  return response.response;
}
```

#### Add Content to Knowledge Base
```typescript
import { chatApi } from "./src";

async function embedDocument() {
  await chatApi.embed({
    content: "Chapter 1: Introduction to Humanoid Robotics...",
    metadata: {
      chapter: 1,
      title: "Introduction",
      section: "basics"
    },
    document_id: "doc-chapter-1"
  });

  console.log("Document embedded successfully");
}
```

#### Get Conversation History
```typescript
import { chatApi } from "./src";

async function getHistory(conversationId: string) {
  const messages = await chatApi.getConversation(conversationId);

  messages.forEach((msg) => {
    console.log(`${msg.sender}: ${msg.content}`);
  });
}
```

#### Check API Health
```typescript
import { chatApi } from "./src";

async function checkBackend() {
  const isHealthy = await chatApi.healthCheck();

  if (isHealthy) {
    console.log("Backend is running!");
  } else {
    console.error("Backend is down");
  }
}
```

#### Error Handling
```typescript
import { chatApi, ChatApiError } from "./src";

async function safeChat() {
  try {
    const response = await chatApi.chat({
      query: "What is AI?"
    });
    return response.response;
  } catch (error) {
    if (error instanceof ChatApiError) {
      console.error(`HTTP ${error.statusCode}: ${error.message}`);

      if (error.statusCode === 500) {
        console.error("Server error - try again later");
      } else if (error.statusCode === 404) {
        console.error("Endpoint not found");
      }
    } else {
      console.error("Network error:", error);
    }
  }
}
```

---

### Type Definitions

#### Message Type
```typescript
import { Message } from "./src/types";

const myMessage: Message = {
  id: "msg-1",
  sender: "user",
  content: "Hello",
  timestamp: Date.now(),
  metadata: {
    selectedText: "some text",
    conversationId: "conv-123"
  }
};
```

#### Conversation Type
```typescript
import { Conversation } from "./src/types";

const conversation: Conversation = {
  id: "conv-123",
  messages: [
    { sender: "user", content: "Hello" },
    { sender: "assistant", content: "Hi there!" }
  ],
  createdAt: Date.now(),
  updatedAt: Date.now(),
  title: "My Chat"
};
```

---

### Complete Integration Example

#### Full App with All Features
```typescript
import React, { useState, useCallback } from "react";
import { ChatBot, useTextSelection, chatApi, ChatApiError } from "./src";

export function CompleteApp() {
  const { selectedText, clearSelection } = useTextSelection();
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [responses, setResponses] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleMessage = useCallback(
    async (query: string) => {
      setError(null);

      try {
        // First message - start new conversation
        const response = await chatApi.chat({
          query,
          selected_text: selectedText?.text,
          conversation_id: conversationId || undefined,
          user_id: "user-123"
        });

        // Track conversation for follow-ups
        if (!conversationId) {
          setConversationId(response.conversation_id);
        }

        // Store response
        setResponses((prev) => [
          ...prev,
          `Assistant: ${response.response}`
        ]);

        // Log sources
        console.log("Sources:", response.retrieved_passages);
        console.log("Scores:", response.relevance_scores);

        // Clear selected text after using it
        if (selectedText) {
          clearSelection();
        }
      } catch (err) {
        if (err instanceof ChatApiError) {
          setError(`Error ${err.statusCode}: ${err.message}`);
        } else {
          setError("Network error - please try again");
        }
      }
    },
    [selectedText, conversationId, clearSelection]
  );

  return (
    <div>
      <ChatBot onMessage={handleMessage} />

      {error && <div className="error">{error}</div>}

      {selectedText && (
        <div className="selection">
          Selected: {selectedText.text.substring(0, 100)}...
        </div>
      )}

      <div className="responses">
        {responses.map((resp, idx) => (
          <div key={idx}>{resp}</div>
        ))}
      </div>
    </div>
  );
}
```

---

### Environment Configuration

#### .env File
```bash
# Backend API endpoint
REACT_APP_API_URL=http://localhost:8000

# Optional: API timeout (ms)
REACT_APP_API_TIMEOUT=30000

# Optional: Environment indicator
REACT_APP_ENV=development
```

#### Usage in Code
```typescript
const apiUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";
const isDev = process.env.REACT_APP_ENV === "development";
```

---

### State Management Pattern

#### Using with React Context
```typescript
import { createContext, useState } from "react";
import { chatApi, ChatResponse } from "./src";

export const ChatContext = createContext<{
  messages: string[];
  sendMessage: (query: string) => Promise<void>;
} | null>(null);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<string[]>([]);

  const sendMessage = async (query: string) => {
    try {
      const response = await chatApi.chat({ query });
      setMessages((prev) => [...prev, response.response]);
    } catch (error) {
      setMessages((prev) => [...prev, "Error: Request failed"]);
    }
  };

  return (
    <ChatContext.Provider value={{ messages, sendMessage }}>
      {children}
    </ChatContext.Provider>
  );
}
```

#### Using Context in Components
```typescript
import { useContext } from "react";
import { ChatContext } from "./ChatContext";

export function ChatDisplay() {
  const context = useContext(ChatContext);

  if (!context) {
    return <div>Chat provider not found</div>;
  }

  return (
    <div>
      {context.messages.map((msg, idx) => (
        <div key={idx}>{msg}</div>
      ))}
      <button onClick={() => context.sendMessage("Hello")}>
        Send Message
      </button>
    </div>
  );
}
```

---

## All Available Exports

```typescript
// Components
import { ChatBot } from "./src/components";

// Hooks
import { useTextSelection } from "./src/hooks";

// Services
import { chatApi, ChatApiError } from "./src/services";

// Types
import type {
  Message,
  MessageMetadata,
  Conversation,
  SelectedTextContext,
  ApiError,
} from "./src/types";

// API Types
import type {
  ChatRequest,
  ChatResponse,
  EmbedRequest,
} from "./src/services";
```

---

## Barrel Import Pattern

```typescript
// Instead of:
import { ChatBot } from "./src/components/ChatBot";
import { useTextSelection } from "./src/hooks/useTextSelection";
import { chatApi } from "./src/services/chatApi";

// Use:
import { ChatBot, useTextSelection, chatApi } from "./src";
```

---

## Testing Examples

### Mock chatApi for Tests
```typescript
import { chatApi } from "./src";

jest.mock("./src/services/chatApi", () => ({
  chatApi: {
    chat: jest.fn().mockResolvedValue({
      response: "Test response",
      conversation_id: "test-123",
      retrieved_passages: ["passage1"],
      relevance_scores: [0.95],
      processing_time_ms: 100
    })
  }
}));

test("sends message and gets response", async () => {
  const response = await chatApi.chat({ query: "test" });
  expect(response.response).toBe("Test response");
});
```

### Mock useTextSelection Hook
```typescript
import { useTextSelection } from "./src";

jest.mock("./src/hooks/useTextSelection", () => ({
  useTextSelection: jest.fn(() => ({
    selectedText: {
      text: "test text",
      context: "test text",
      timestamp: Date.now()
    },
    clearSelection: jest.fn(),
    hasSelection: true
  }))
}));
```

---

This file provides copy-paste ready code snippets for all Phase 2 components!
