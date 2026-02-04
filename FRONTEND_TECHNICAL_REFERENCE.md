# Frontend Technical Reference - Chatbot Widget Components

**Version**: 1.0
**Last Updated**: January 30, 2026
**Status**: Production Ready

---

## Component API Reference

### ChatInput Component

**Path**: `frontend/src/components/ChatInput.tsx`

**Props**:
```typescript
interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  selectedText?: SelectedText | null;
}
```

**Usage**:
```typescript
import { ChatInput } from '@hackathon/book-frontend';

<ChatInput
  onSendMessage={(msg) => console.log(msg)}
  isLoading={false}
  selectedText={selectedText}
/>
```

**Behavior**:
- Fires `onSendMessage` with text when:
  - User presses Enter (not Shift+Enter)
  - User clicks Send button
  - Button is disabled if text is empty or loading
- Placeholder changes based on selected text
- Input clears after message sent
- Auto-focuses on mount and after message submission

**CSS Classes**:
- `.chat-input-form` - Form container
- `.chat-input` - Input field
- `.chat-submit-btn` - Send button

---

### ChatMessage Component

**Path**: `frontend/src/components/ChatMessage.tsx`

**Props**:
```typescript
interface ChatMessageProps {
  sender: "user" | "bot";
  content: string;
  timestamp?: string;
  citations?: string[];
  relevanceScores?: number[];
}
```

**Usage**:
```typescript
import { ChatMessage } from '@hackathon/book-frontend';

<ChatMessage
  sender="bot"
  content="The answer is..."
  timestamp={new Date().toISOString()}
  citations={["Chapter 1: Intro", "Chapter 2: Basics"]}
  relevanceScores={[0.95, 0.87]}
/>
```

**Behavior**:
- Right-aligned blue for user messages
- Left-aligned gray for bot messages
- Citations display as numbered list with relevance %
- Timestamps format as HH:MM (local time)
- Fade-in animation on mount

**CSS Classes**:
- `.message` - Container
- `.message-user` - User message
- `.message-bot` - Bot message
- `.message-content` - Content area
- `.citations-section` - Citations container
- `.citation-item` - Individual citation

---

### LoadingIndicator Component

**Path**: `frontend/src/components/LoadingIndicator.tsx`

**Props**:
```typescript
interface LoadingIndicatorProps {
  isVisible: boolean;
  elapsedTime?: number; // milliseconds
}
```

**Usage**:
```typescript
import { LoadingIndicator } from '@hackathon/book-frontend';

<LoadingIndicator isVisible={isLoading} elapsedTime={elapsedTime} />
```

**Behavior**:
- Only renders if `isVisible` is true
- Shows elapsed time in seconds (0.0s format)
- Warning appears if elapsed > 2000ms
- Spinner rotates at 60 RPM
- Background changes to yellow when slow (>2s)

**CSS Classes**:
- `.loading-indicator` - Main container
- `.spinner` - Animated spinner
- `.loading-text` - "Searching textbook..." text
- `.slow-message` - Warning message
- `.timer` - Elapsed time display

---

### useChat Hook

**Path**: `frontend/src/hooks/useChat.ts`

**Signature**:
```typescript
function useChat(initialConversationId?: string): {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  sendMessage: (query: string, selectedText?: string) => Promise<void>;
  clearMessages: () => void;
  loadConversation: (conversationId: string) => Promise<void>;
}
```

**Usage**:
```typescript
import { useChat } from '@hackathon/book-frontend';

const {
  messages,
  isLoading,
  error,
  conversationId,
  sendMessage,
  clearMessages
} = useChat();

// Send a message
await sendMessage("What is AI?", "selected text context");

// Clear conversation
clearMessages();
```

**Message Type**:
```typescript
interface Message {
  id?: string;
  sender: "user" | "bot";
  content: string;
  timestamp: string; // ISO format
  citations?: string[];
  relevanceScores?: number[]; // 0-1 range
}
```

**Behavior**:
- Optimistic UI: user message shows before API response
- Conversation ID persists in sessionStorage
- Messages stored in sessionStorage under `chat-messages-{conversationId}`
- Error messages automatically added to messages array
- `loadConversation` retrieves messages from sessionStorage or API

---

### ChatBot Component

**Path**: `frontend/src/components/ChatBot.tsx`

**Props**:
```typescript
interface ChatBotProps {
  onMessage?: (message: string) => void; // Optional callback
}
```

**Usage**:
```typescript
import { ChatBot } from '@hackathon/book-frontend';

export default function DocPage() {
  return (
    <>
      <article>{/* page content */}</article>
      <ChatBot onMessage={(msg) => console.log(msg)} />
    </>
  );
}
```

**Behavior**:
- Displays toggle button in bottom-right corner
- Chat window slides up on toggle
- Shows welcome message on initial load
- Integrates all sub-components
- Auto-scrolls to latest message
- Tracks and displays elapsed time during loading
- Displays conversation ID in header
- Shows error messages with alert styling

**CSS Classes**:
- `.chatbot-widget` - Main widget container
- `.chatbot-toggle` - Toggle button
- `.chatbot-container` - Chat window
- `.chatbot-header` - Header with title
- `.messages-container` - Messages area
- `.welcome-message` - Welcome text
- `.error-message` - Error display

---

## CSS Styling Guide

### Color Palette

```css
/* Primary Colors */
--primary-blue: #4a90e2;
--dark-blue: #357abd;

/* Neutral Colors */
--light-gray: #f8f9fa;
--medium-gray: #e8e8e8;
--dark-gray: #666666;

/* System Colors */
--error-red: #e74c3c;
--warning-yellow: #fde68a;

/* Backgrounds */
--body-bg: white;
--input-bg: #f9f9f9;
```

### Typography

```css
/* Font Stack */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto",
             "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans",
             "Helvetica Neue", sans-serif;

/* Sizes */
--text-xs: 11px;
--text-sm: 12px;
--text-base: 13px;
--text-lg: 14px;
--text-xl: 16px;
--text-2xl: 24px;
```

### Responsive Breakpoints

```css
/* Mobile First */
@media (max-width: 480px) { /* Mobile devices */ }
@media (max-width: 768px) { /* Tablets */ }
@media (min-width: 1024px) { /* Desktop */ }
```

### Animations

```css
/* Spinner Animation */
@keyframes spin {
  to { transform: rotate(360deg); }
}
animation: spin 1s linear infinite;

/* Fade In Animation */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
animation: fadeIn 0.3s ease-in;

/* Slide Up Animation */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
animation: slideUp 0.3s ease;

/* Pulse Animation */
@keyframes pulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}
animation: pulse 1.5s ease-in-out infinite;
```

---

## API Integration Details

### ChatApi Service

**Location**: `frontend/src/services/chatApi.ts`

**Interface**:
```typescript
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

export const chatApi = {
  chat(request: ChatRequest): Promise<ChatResponse>,
  embed(request: EmbedRequest): Promise<void>,
  getConversation(conversationId: string): Promise<Message[]>,
  healthCheck(): Promise<boolean>
}
```

**Configuration**:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
```

**Error Handling**:
```typescript
class ChatApiError extends Error {
  statusCode: number;
  message: string;
}

// Usage
try {
  const response = await chatApi.chat({...});
} catch (error) {
  if (error instanceof ChatApiError) {
    console.error(`API Error ${error.statusCode}: ${error.message}`);
  }
}
```

---

## State Management

### SessionStorage Keys

```typescript
// Current conversation ID
sessionStorage.getItem("current-conversation-id") // Returns: string | null

// Messages for specific conversation
sessionStorage.getItem("chat-messages-{conversationId}") // Returns: JSON string
```

### State Flow Example

```typescript
// Initial state
messages: []
isLoading: false
error: null
conversationId: null

// After sending first message
messages: [
  { sender: "user", content: "What is AI?", timestamp: "..." }
]
isLoading: true
conversationId: "conv-123" // Set from API response

// After receiving response
messages: [
  { sender: "user", content: "What is AI?", timestamp: "..." },
  { sender: "bot", content: "AI is...", citations: [...], timestamp: "..." }
]
isLoading: false
error: null
conversationId: "conv-123"
```

---

## Environment Variables

### Required
```bash
REACT_APP_API_URL=http://localhost:8000
```

### Optional
```bash
REACT_APP_DEBUG=false  # Enable debug logging
REACT_APP_TIMEOUT=30000  # API timeout in ms
```

---

## TypeScript Types

### Complete Type Definitions

```typescript
// Message from chat
export interface Message {
  id?: string;
  sender: "user" | "bot";
  content: string;
  timestamp: string;
  citations?: string[];
  relevanceScores?: number[];
}

// Selected text from hook
export interface SelectedText {
  text: string;
  context?: string;
  timestamp: number;
}

// Chat request
export interface ChatRequest {
  query: string;
  selected_text?: string;
  conversation_id?: string;
  user_id?: string;
}

// Chat response
export interface ChatResponse {
  response: string;
  conversation_id: string;
  retrieved_passages: string[];
  relevance_scores: number[];
  processing_time_ms: number;
}
```

---

## Performance Optimization Tips

### React Optimization
1. **useCallback**: Memoize callbacks in hooks to prevent re-renders
2. **useRef**: Use refs for DOM access instead of state
3. **Conditional Rendering**: Only render LoadingIndicator when loading
4. **Key Prop**: Use unique keys for message lists

### CSS Optimization
1. **CSS Modules**: Scoped styles prevent name collisions
2. **Animations**: Use GPU-accelerated transforms (translate, rotate)
3. **Scrolling**: Use `overflow-y: auto` with custom scrollbar styling
4. **Media Queries**: Mobile-first approach

### Bundle Size
- No external UI libraries (all custom CSS)
- Minimal React dependencies
- Tree-shakeable exports

---

## Accessibility Implementation

### ARIA Attributes
```typescript
// Toggle button
<button aria-label="Toggle chatbot" aria-expanded={isOpen} />

// Loading indicator
<div role="status" aria-label="Loading" aria-live="polite" />

// Chat messages
<div role="article" aria-label="User message" />

// Error message
<div role="alert" aria-live="assertive" />
```

### Keyboard Navigation
- Tab: Move between focusable elements
- Enter: Submit form/activate buttons
- Escape: Close chat (future enhancement)

### Screen Reader Support
- Semantic HTML (article, form, button)
- Descriptive labels and titles
- ARIA live regions for dynamic content
- Color not the only indicator (text labels used)

---

## Testing Guide

### Unit Testing Example

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from './ChatInput';

test('sends message on enter key', () => {
  const handleSendMessage = jest.fn();
  render(
    <ChatInput
      onSendMessage={handleSendMessage}
      isLoading={false}
    />
  );

  const input = screen.getByLabelText('Chat message input');
  fireEvent.change(input, { target: { value: 'Hello' } });
  fireEvent.keyDown(input, { key: 'Enter' });

  expect(handleSendMessage).toHaveBeenCalledWith('Hello');
});
```

### E2E Testing Example

```typescript
describe('ChatBot Widget', () => {
  it('sends and displays message', () => {
    cy.mount(<ChatBot />);
    cy.get('[aria-label="Toggle chatbot"]').click();
    cy.get('input[aria-label="Chat message input"]').type('Hello');
    cy.get('button[aria-label="Send message"]').click();
    cy.contains('Hello').should('be.visible');
  });
});
```

---

## Debugging Tips

### Browser DevTools

**Console Logging**:
```typescript
// In useChat hook
console.log("Sending message:", { query, selectedText });
console.log("API Response:", response);
console.log("Messages:", messages);
```

**Network Tab**:
- Check API requests to `/chat`
- Verify request/response payloads
- Monitor response times

**React DevTools**:
- Inspect component hierarchy
- Check prop values
- View hook state
- Profiling for performance

### SessionStorage Inspection

```javascript
// In browser console
sessionStorage.getItem("current-conversation-id")
JSON.parse(sessionStorage.getItem("chat-messages-conv-123"))
sessionStorage.clear() // Clear all
```

---

## Deployment Checklist

- [ ] All TypeScript compiles without errors
- [ ] Environment variables configured
- [ ] API URL points to production server
- [ ] CSS Modules scoped (no global styles)
- [ ] No console.logs in production code
- [ ] No hardcoded values
- [ ] Accessibility audit passed (axe-devtools)
- [ ] Mobile responsive verified
- [ ] Error handling tested
- [ ] Performance acceptable (< 50ms render)
- [ ] Bundle size < 100KB (gzipped)
- [ ] Source maps available

---

## Common Issues & Solutions

### Issue: Messages not persisting
**Solution**: Check sessionStorage is not blocked; verify conversation ID is being set

### Issue: API calls failing
**Solution**: Verify REACT_APP_API_URL is correct; check CORS headers on backend

### Issue: Styling not applied
**Solution**: Verify CSS Modules are imported; check class names in HTML

### Issue: Auto-scroll not working
**Solution**: Ensure messagesEndRef element exists; check overflow-y property

### Issue: Loading indicator stuck
**Solution**: Verify isLoading state is being cleared; check API error handling

---

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Android)

**Not Supported**:
- IE 11
- Old Android browsers (< 5.0)

---

## Performance Metrics

- **First Paint**: < 500ms
- **Time to Interactive**: < 1s
- **Message Render**: < 50ms
- **Scroll Performance**: 60 FPS
- **Bundle Size**: ~40KB (uncompressed)

---

## Future Enhancement Ideas

1. **Markdown Support**: Parse markdown in responses
2. **Message Editing**: Edit/delete sent messages
3. **Search**: Search conversation history
4. **Export**: Export conversation as PDF/JSON
5. **Voice Input**: Speech-to-text support
6. **Dark Mode**: Theme toggle
7. **Conversation List**: Multiple conversations
8. **Typing Indicator**: Show bot is typing
9. **Read Receipts**: Message read status
10. **Reactions**: Emoji reactions to messages

---

## Support & Documentation

- **Issues**: Report via GitHub issues
- **Documentation**: See FRONTEND_COMPONENTS_IMPLEMENTATION.md
- **Completion Report**: See PHASE3_COMPLETION_REPORT.md
- **Backend API**: See backend README.md

---

**Version History**:
- 1.0 (Jan 30, 2026): Initial release with 5 components
