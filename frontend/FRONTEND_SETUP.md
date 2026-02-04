# RAG Chatbot Frontend - Phase 2 Foundational Setup

## Overview

This document outlines the Phase 2 foundational frontend architecture for the RAG Chatbot widget. All core components, hooks, services, and type definitions have been implemented to unblock UI development.

## Project Structure

```
frontend/src/
├── components/
│   ├── ChatBot.tsx              # Main chatbot widget component
│   ├── ChatBot.module.css       # Chatbot styling (CSS Modules)
│   └── index.ts                 # Component exports
├── hooks/
│   ├── useTextSelection.ts      # Text selection capture hook
│   └── index.ts                 # Hook exports
├── services/
│   ├── chatApi.ts              # API service layer
│   └── index.ts                # Service exports
├── types/
│   ├── chat.ts                 # Shared TypeScript interfaces
│   └── index.ts                # Type exports
├── styles/                      # Global styles (empty - for future use)
├── index.tsx                   # Main entry point & exports
└── types/                       # Type definitions
```

## Completed Tasks

### Task T021: ChatBot Component Structure

**File**: `frontend/src/components/ChatBot.tsx`

Main widget container with:
- Open/close toggle button (fixed bottom-right)
- Message history display
- User input area with send button
- Loading state indicator
- Callback support for parent integration
- Accessibility features (aria-labels, keyboard support)

**Key Features**:
- State management for messages, input, and loading state
- Enter key handling for quick message sending
- Disabled input during API calls
- Welcome message on first load
- Responsive design (mobile-friendly)

**Props**:
```typescript
interface ChatBotProps {
  onMessage?: (message: string) => void;  // Optional callback when message is sent
}
```

### Task T022: Text Selection Hook

**File**: `frontend/src/hooks/useTextSelection.ts`

Custom React hook for capturing selected text with context preservation:

**Return Value**:
```typescript
{
  selectedText: SelectedText | null,  // Selected text with context and timestamp
  clearSelection: () => void,         // Function to clear selection
  hasSelection: boolean              // Boolean flag for convenience
}
```

**Features**:
- Listens to mouseup and touchend events
- Captures up to 200 characters of context (configurable)
- Includes timestamp for tracking
- Cleanup on component unmount
- Clear selection utility method

**Usage Example**:
```typescript
const { selectedText, clearSelection, hasSelection } = useTextSelection();
```

### Task T023: Chat API Service

**File**: `frontend/src/services/chatApi.ts`

API service layer with type-safe fetch methods:

**Available Methods**:

1. **chat(request)** - Send a chat message
   - Input: `ChatRequest` (query, selected_text, conversation_id, user_id)
   - Output: `ChatResponse` (response, conversation_id, retrieved_passages, relevance_scores, processing_time_ms)
   - Error: `ChatApiError` with status code and message

2. **embed(request)** - Embed new content
   - Input: `EmbedRequest` (content, metadata, document_id)
   - Used for knowledge base updates

3. **getConversation(id)** - Retrieve conversation history
   - Fetches all messages for a conversation

4. **healthCheck()** - Check API availability
   - Simple endpoint verification

**Configuration**:
- Base URL from environment: `process.env.REACT_APP_API_URL`
- Default: `http://localhost:8000`
- Content-Type: `application/json`

**Error Handling**:
- Custom `ChatApiError` class extends Error
- Includes statusCode and message
- Network errors caught and wrapped

### Type Definitions

**File**: `frontend/src/types/chat.ts`

Shared TypeScript interfaces:

```typescript
interface Message {
  id?: string;
  sender: "user" | "assistant";
  content: string;
  timestamp?: number;
  metadata?: MessageMetadata;
}

interface MessageMetadata {
  selectedText?: string;
  conversationId?: string;
  relevanceScores?: number[];
  retrievedPassages?: string[];
}

interface Conversation {
  id: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
  title?: string;
}

interface SelectedTextContext {
  text: string;
  context?: string;
  timestamp: number;
}

interface ApiError {
  statusCode: number;
  message: string;
  details?: unknown;
}
```

## Styling

**CSS Modules Approach**: `ChatBot.module.css`

Visual design includes:
- Fixed position widget (bottom-right corner)
- Smooth animations (slide-up, pulse)
- Responsive design (mobile-optimized)
- Color scheme: Blue (#0066cc) primary, light gray (#f8f9fa) background
- Gradient header with contrast messaging
- Disabled state styling for inputs/buttons

**Key Classes**:
- `.chatbot-container` - Fixed wrapper
- `.chatbot-widget` - Main chat window
- `.chatbot-messages` - Message display area
- `.chatbot-input-area` - Input controls
- `.message-user` / `.message-assistant` - Message styling

## Environment Configuration

Create `.env` in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000
```

**Environment Variables**:
- `REACT_APP_API_URL` - Backend API endpoint (default: localhost:8000)
- All other configuration through environment files

## Export Structure

**Main Entry Point** (`frontend/src/index.tsx`):

```typescript
// Components
export { ChatBot, default } from "./components";

// Hooks
export { useTextSelection } from "./hooks";

// Services
export { chatApi } from "./services";

// Types
export type {
  Message,
  MessageMetadata,
  Conversation,
  SelectedTextContext,
  ApiError,
} from "./types";
```

**Submodule Exports**:
- `components/index.ts` - ChatBot component
- `hooks/index.ts` - useTextSelection hook
- `services/index.ts` - chatApi service
- `types/index.ts` - All TypeScript types

## Integration Checklist

- [x] ChatBot component created with container structure
- [x] useTextSelection hook implemented
- [x] chatApi service with POST/GET methods
- [x] TypeScript interfaces defined
- [x] Error handling structure in place
- [x] CSS styling complete
- [x] Component ready for integration
- [x] Export structure organized

## Next Steps

**Phase 3 - Component Integration**:
1. Integrate ChatBot with useTextSelection hook
2. Wire chatApi service into ChatBot message handler
3. Implement conversation history management
4. Add context menu for selected text
5. Create conversation persistence layer

**Phase 4 - Advanced Features**:
1. Message streaming support
2. Markdown rendering for responses
3. Citation/passage highlighting
4. Search history sidebar
5. User authentication

## Development Commands

```bash
# Start development server
npm start

# Build for production
npm build

# Run tests
npm test

# Type checking
npx tsc --noEmit
```

## File References

- **Components**: `C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\src\components\ChatBot.tsx`
- **Hooks**: `C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\src\hooks\useTextSelection.ts`
- **Services**: `C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\src\services\chatApi.ts`
- **Types**: `C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\src\types\chat.ts`
- **Styling**: `C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\src\components\ChatBot.module.css`

## Acceptance Criteria - All Met ✓

- [x] ChatBot.tsx created with container component
- [x] useTextSelection.ts hook implemented
- [x] chatApi.ts service with POST methods (chat, embed, healthCheck)
- [x] getConversation GET method included
- [x] Proper TypeScript interfaces defined
- [x] Error handling structure in place (ChatApiError)
- [x] Component ready for integration with other parts
- [x] Files created and organized
- [x] Component structure overview documented
- [x] TypeScript interfaces defined
- [x] API endpoint mapping complete
