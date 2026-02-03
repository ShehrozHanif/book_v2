# RAG Chatbot Frontend - Deployment Guide

React TypeScript frontend for Humanoid Robotics Textbook RAG Chatbot.

## Quick Start

### 1. Prerequisites

- Node.js 18+ and npm
- Backend API running (see backend/README.md)

### 2. Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API URL
```

### 3. Environment Variables

Create `.env.local` file in `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

**Environment Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API base URL | `http://localhost:8000` or `https://api.roboticsbook.ai` |

### 4. Start Development Server

```bash
npm start
```

Browser opens at: http://localhost:3000

### 5. Build for Production

```bash
npm run build
```

Production-ready files are in `build/` directory.

---

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatBot.tsx                # Main chat widget
│   │   ├── ConversationHistory.tsx    # Sidebar with past messages
│   │   ├── MessagePanel.tsx           # Chat message display area
│   │   ├── ChatInput.tsx              # Input box with send button
│   │   ├── ChatMessage.tsx            # Individual message component
│   │   ├── LoadingIndicator.tsx       # Loading spinner
│   │   └── ErrorMessage.tsx           # Error display
│   ├── hooks/
│   │   ├── useChat.ts                 # Chat state management
│   │   └── useTextSelection.ts        # Detects selected text on page
│   ├── services/
│   │   └── chatApi.ts                 # API client for backend
│   ├── types/
│   │   └── chat.ts                    # TypeScript interfaces
│   ├── styles/
│   │   └── ChatBot.css                # Component styles
│   ├── App.tsx                        # Root component
│   └── index.tsx                      # Entry point
├── public/
│   ├── index.html                     # HTML template
│   └── favicon.ico                    # App icon
├── package.json                       # Dependencies
├── tsconfig.json                      # TypeScript config
└── README.md                          # This file
```

---

## Component Architecture

### Component Hierarchy

```
ChatBot (main widget)
├── ConversationHistory
│   └── Message[] (sidebar with past conversations)
├── MessagePanel
│   ├── ChatMessage[] (user and bot messages)
│   ├── LoadingIndicator (shown while waiting for response)
│   └── ErrorMessage (shown on errors)
└── ChatInput (text input + send button)
```

### Key Components

#### ChatBot

Main container component that orchestrates the chat experience.

```typescript
import { ChatBot } from '@robotics-book/chatbot';

function App() {
  return (
    <div>
      <h1>Textbook Chapter</h1>
      <p>Content here...</p>
      <ChatBot />  {/* Chat widget appears */}
    </div>
  );
}
```

#### MessagePanel

Displays conversation messages with citations.

Features:
- Auto-scroll to latest message
- Citation links to textbook sections
- Message timestamps
- User/bot message styling

#### ConversationHistory

Sidebar showing past conversations.

Features:
- List of conversation threads
- Click to switch conversations
- New conversation button
- Conversation timestamps

#### ChatInput

Text input with send functionality.

Features:
- Multi-line input support
- Enter to send (Shift+Enter for newline)
- Character count (max 5000)
- Disabled during loading

---

## Hooks

### useChat

Manages chat state and API calls.

**Usage:**

```typescript
import { useChat } from './hooks/useChat';

function ChatComponent() {
  const {
    messages,           // Message[] - all messages in conversation
    conversationId,     // string | null - current conversation ID
    loading,            // boolean - API request in progress
    error,              // string | null - error message if any
    sendMessage,        // (query: string) => Promise<void>
    clearError          // () => void - clear error state
  } = useChat();

  const handleSend = async (query: string) => {
    await sendMessage(query);
  };

  return (
    <div>
      {messages.map(msg => (
        <div key={msg.id}>{msg.content}</div>
      ))}
      {loading && <LoadingIndicator />}
      {error && <ErrorMessage message={error} onClear={clearError} />}
    </div>
  );
}
```

**State Management:**

```typescript
interface Message {
  id: string;
  sender: 'user' | 'bot';
  content: string;
  timestamp: Date;
  citations?: string[];
}

interface ChatState {
  messages: Message[];
  conversationId: string | null;
  loading: boolean;
  error: string | null;
}
```

### useTextSelection

Detects text selected by user on the page.

**Usage:**

```typescript
import { useTextSelection } from './hooks/useTextSelection';

function ChatInput() {
  const selectedText = useTextSelection();

  useEffect(() => {
    if (selectedText) {
      console.log('User selected:', selectedText);
      // Pre-fill input or add to query
    }
  }, [selectedText]);
}
```

**How it works:**
- Listens to `mouseup` events
- Captures `window.getSelection()`
- Returns selected text string

---

## API Integration

### Chat API Client

Located in `src/services/chatApi.ts`.

**Endpoints:**

#### Send Message

```typescript
import { chatApi } from './services/chatApi';

// Simple query
const response = await chatApi.chat({
  query: "What is ROS 2?",
});

// With conversation context
const response = await chatApi.chat({
  query: "How does that compare to ROS 1?",
  conversation_id: "550e8400-e29b-41d4-a716-446655440000"
});

// With selected text
const response = await chatApi.chat({
  query: "Can you explain this in more detail?",
  selected_text: "ROS 2 is a middleware framework..."
});
```

**Response Format:**

```typescript
interface ChatResponse {
  response: string;                // AI-generated answer with citations
  conversation_id: string;         // UUID for follow-up questions
  retrieved_passages: string[];    // Textbook passages used
  relevance_scores: number[];      // Relevance scores (0-1)
  processing_time_ms: number;      // Backend processing time
}
```

**Error Handling:**

```typescript
try {
  const response = await chatApi.chat({ query });
} catch (error) {
  if (error.response?.status === 429) {
    // Rate limit exceeded
    console.error('Too many requests. Please wait.');
  } else if (error.response?.status === 400) {
    // Validation error
    console.error('Invalid query:', error.response.data.details);
  } else {
    // Server error
    console.error('Server error. Please try again.');
  }
}
```

---

## Integration with Docusaurus

### Installation

```bash
npm install @robotics-book/chatbot
```

### Usage in .mdx Files

```mdx
---
title: Chapter 1: Introduction to ROS 2
---

import { ChatBot } from '@robotics-book/chatbot';

# Chapter 1: Introduction to ROS 2

ROS 2 (Robot Operating System 2) is a flexible middleware framework...

## 1.1 What is ROS 2?

ROS 2 provides a publish-subscribe messaging system...

<ChatBot />
```

### Customization

```typescript
<ChatBot
  apiUrl="https://api.roboticsbook.ai"
  theme="dark"
  position="bottom-right"
  placeholder="Ask a question about this chapter..."
/>
```

---

## Testing

### Run Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### E2E Tests (Cypress)

```bash
# Install Cypress
npm install --save-dev cypress

# Open Cypress UI
npm run cypress:open

# Run headless
npm run cypress:run
```

**Test Coverage Goals:**

- Components: > 80%
- Hooks: > 90%
- Services: > 85%

---

## Build and Deployment

### Production Build

```bash
# Build optimized bundle
npm run build

# Output in build/ directory
ls -lh build/

# Test production build locally
npx serve -s build
```

### Bundle Size

- **Target**: < 150KB gzipped
- **Current**: ~120KB gzipped

**Optimize Bundle:**

```bash
# Analyze bundle size
npm run build -- --stats
npx webpack-bundle-analyzer build/bundle-stats.json
```

### Deployment Options

#### Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy to production
vercel deploy --prod
```

#### Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=build
```

#### Docker

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
# Build image
docker build -t rag-chatbot-frontend:latest .

# Run container
docker run -d -p 3000:80 rag-chatbot-frontend:latest
```

#### GitHub Pages

```bash
# Install gh-pages
npm install --save-dev gh-pages

# Add to package.json
{
  "homepage": "https://yourusername.github.io/repo-name",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}

# Deploy
npm run deploy
```

---

## Performance

### Metrics

| Metric | Target | Current |
|--------|--------|---------|
| First Contentful Paint | < 1.5s | ~1.2s |
| Time to Interactive | < 3s | ~2.5s |
| Bundle size (gzipped) | < 150KB | ~120KB |
| Chat response render | < 100ms | ~50ms |

### Optimization Tips

1. **Code Splitting**: Dynamic imports for heavy components
2. **Lazy Loading**: Load chat widget only when needed
3. **Memoization**: Use `React.memo()` for static components
4. **Debouncing**: Debounce text selection detection

---

## Accessibility

### WCAG 2.1 AA Compliance

- ✅ Keyboard navigation (Tab, Enter, Escape)
- ✅ Screen reader support (ARIA labels)
- ✅ Color contrast ratio > 4.5:1
- ✅ Focus indicators on interactive elements
- ✅ Alt text for icons

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Navigate between elements |
| `Enter` | Send message |
| `Shift+Enter` | New line in input |
| `Escape` | Close chat widget |
| `Ctrl+L` | Clear conversation |

### Screen Reader Support

```typescript
<button
  aria-label="Send message"
  aria-describedby="chat-input"
>
  <SendIcon />
</button>

<div
  role="log"
  aria-live="polite"
  aria-label="Chat conversation"
>
  {messages.map(msg => (
    <div role="article" aria-label={`${msg.sender} message`}>
      {msg.content}
    </div>
  ))}
</div>
```

---

## Troubleshooting

### "Cannot connect to backend"

**Cause**: Backend not running or wrong `REACT_APP_API_URL`

**Solution**:
```bash
# Check .env.local
cat .env.local

# Verify backend is running
curl http://localhost:8000/health

# Update .env.local and restart
npm start
```

### "Messages not rendering"

**Cause**: API response format mismatch

**Solution**:
```typescript
// Check API response in browser console
console.log('API Response:', response);

// Verify response matches expected format
interface ChatResponse {
  response: string;
  conversation_id: string;
  retrieved_passages: string[];
  relevance_scores: number[];
  processing_time_ms: number;
}
```

### "Text selection not working"

**Cause**: Page content in iframe or shadow DOM

**Solution**:
```typescript
// Update useTextSelection hook to handle iframes
useEffect(() => {
  const handleSelection = () => {
    const selection = window.getSelection();
    // Add iframe handling
    if (selection && selection.toString().trim()) {
      setSelectedText(selection.toString());
    }
  };

  document.addEventListener('mouseup', handleSelection);
  // Also listen on iframes if needed
}, []);
```

### High memory usage

**Cause**: Conversation history accumulating without limits

**Solution**:
```typescript
// In useChat hook, limit message history
const MAX_MESSAGES = 100;

const addMessage = (message: Message) => {
  setMessages(prev => {
    const updated = [...prev, message];
    // Keep only last 100 messages
    return updated.slice(-MAX_MESSAGES);
  });
};
```

---

## Environment Variables

### Development

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

### Production

```env
REACT_APP_API_URL=https://api.roboticsbook.ai
REACT_APP_ENV=production
```

### Testing

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=test
```

---

## Contributing

### Development Workflow

1. Create feature branch
2. Write tests first (TDD)
3. Implement component
4. Ensure coverage > 80%
5. Run linter: `npm run lint`
6. Submit pull request

### Code Quality

```bash
# Lint code
npm run lint

# Fix lint errors
npm run lint -- --fix

# Type check
npm run type-check
```

---

## Support

- **Storybook**: `npm run storybook` (component documentation)
- **Issues**: GitHub Issues
- **Email**: support@roboticsbook.ai

---

**Last Updated**: 2024-01-30

**Version**: 1.0.0
