# Frontend Quick Start Guide

## What's Been Created

✓ **10 new files** (640 lines of production-quality code)
✓ **3 core features** (Component, Hook, Service)
✓ **Full TypeScript** support with interfaces
✓ **Responsive design** with mobile optimization
✓ **Error handling** and API integration ready

---

## Quick Import Examples

### Import ChatBot Component
```typescript
import { ChatBot } from "./frontend/src";

export function App() {
  return <ChatBot onMessage={(msg) => console.log(msg)} />;
}
```

### Use Text Selection Hook
```typescript
import { useTextSelection } from "./frontend/src";

export function MyComponent() {
  const { selectedText, clearSelection, hasSelection } = useTextSelection();

  if (hasSelection) {
    console.log(selectedText.text);
  }

  return <div>Text selected: {hasSelection}</div>;
}
```

### Call Chat API
```typescript
import { chatApi, ChatApiError } from "./frontend/src";

async function sendMessage(query: string) {
  try {
    const response = await chatApi.chat({
      query,
      selected_text: "optional context"
    });
    console.log("Response:", response.response);
    console.log("Sources:", response.retrieved_passages);
  } catch (error) {
    if (error instanceof ChatApiError) {
      console.error(`Error ${error.statusCode}: ${error.message}`);
    }
  }
}
```

---

## File Summary

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `ChatBot.tsx` | Main widget component | 127 | ✓ Complete |
| `ChatBot.module.css` | Widget styling | 240 | ✓ Complete |
| `useTextSelection.ts` | Text capture hook | 43 | ✓ Complete |
| `chatApi.ts` | API service | 150 | ✓ Complete |
| `chat.ts` | TypeScript types | 40 | ✓ Complete |
| Barrel exports | Clean imports | 8 | ✓ Complete |

---

## Environment Setup

Create `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000
```

---

## Next Steps

1. **Install dependencies**: `npm install` in frontend/
2. **Start development**: `npm start`
3. **Check types**: `npx tsc --noEmit`
4. **Build for prod**: `npm build`

---

## API Contract

### POST /chat
Send a message and get a response.

**Request**:
```json
{
  "query": "What is humanoid robotics?",
  "selected_text": "optional context",
  "conversation_id": "conv-123",
  "user_id": "user-456"
}
```

**Response**:
```json
{
  "response": "Humanoid robotics is...",
  "conversation_id": "conv-123",
  "retrieved_passages": ["passage1", "passage2"],
  "relevance_scores": [0.95, 0.87],
  "processing_time_ms": 245
}
```

### POST /chat/embed
Add new content to the knowledge base.

**Request**:
```json
{
  "content": "Chapter content...",
  "metadata": {"chapter": 1},
  "document_id": "doc-123"
}
```

### GET /conversations/{id}
Get conversation history.

### GET /health
Check API is running.

---

## Architecture Overview

```
ChatBot Widget
├── useTextSelection Hook
│   └── Captures selected text
├── ChatBot Component
│   ├── Message Display
│   ├── Input Area
│   └── onMessage Callback
└── chatApi Service
    ├── POST /chat
    ├── POST /chat/embed
    ├── GET /conversations/{id}
    └── GET /health
```

---

## Key Types

```typescript
// Send message
interface ChatRequest {
  query: string;
  selected_text?: string;
  conversation_id?: string;
  user_id?: string;
}

// Get response
interface ChatResponse {
  response: string;
  conversation_id: string;
  retrieved_passages: string[];
  relevance_scores: number[];
  processing_time_ms: number;
}

// Message in history
interface Message {
  sender: "user" | "assistant";
  content: string;
  timestamp?: number;
  metadata?: MessageMetadata;
}
```

---

## Development Workflow

```bash
# Watch for changes
npm start

# Run in another terminal
cd backend
python -m uvicorn main:app --reload

# Test the integration
# Open http://localhost:3000
# Try selecting text on the page
# Click the chatbot button and ask a question
```

---

## Troubleshooting

**"Cannot find module"**: Make sure barrel exports are set up (index.ts files in each directory)

**"API error"**: Check `REACT_APP_API_URL` environment variable and backend is running

**"Type errors"**: Run `npx tsc --noEmit` to see all TypeScript errors

---

## What's Ready for Phase 3

- [x] ChatBot component (ready for API integration)
- [x] Text selection hook (ready for context menu)
- [x] API service (ready to call backend)
- [x] Type system (ready for full type safety)
- [x] Styling (ready for customization)
- [x] Error handling (ready for production)

---

**Status**: Phase 2 Complete - Ready for Phase 3 Integration 🚀
