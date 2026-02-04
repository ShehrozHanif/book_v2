---
name: chatbot-widget
description: Build interactive chat UI components with message display, user input, and conversation management
model: sonnet
---

# Chatbot Widget Skill

## Purpose
Create fully functional chatbot UI components with real-time messaging, user interaction, and state management.

## Key Responsibilities
- Design chatbot UI layout and structure
- Implement message display system
- Build user input interface
- Handle message sending and receiving
- Manage conversation state and history
- Add loading states and animations
- Implement typing indicators
- Handle error states gracefully
- Add accessibility features

## Component Structure

### Main Components
- **ChatContainer**: Overall wrapper with layout
- **MessageList**: Scrollable message history
- **MessageBubble**: Individual message rendering
- **InputArea**: User message input
- **LoadingIndicator**: Typing/loading animation

## Features to Implement

### Message Display
- User messages (right-aligned)
- Bot messages (left-aligned)
- Timestamps
- Message status (sent, delivered, read)
- Code block syntax highlighting
- Markdown rendering
- Image/media support

### User Input
- Text input with multi-line support
- Send button
- Character count/limit display
- Submit on Enter (with Shift+Enter for new line)
- Clear input after send

### Conversation Management
- Scroll to bottom on new message
- Virtual scrolling for long chats
- Message pagination
- Clear conversation option
- Export chat history

### Loading States
- Typing indicator
- Loading skeleton
- Message animation
- Disabled input during processing

## UI Elements

### Chat Header
```jsx
- Title/Icon
- User/Bot info
- Settings/menu button
- Close button
```

### Message Styles
```jsx
User Message:
- Background: primary color
- Text: white
- Alignment: right
- Rounded bottom-left

Bot Message:
- Background: gray/light
- Text: dark
- Alignment: left
- Rounded bottom-right
```

### Responsive Design
- Mobile: Full width, bottom input
- Tablet: Sidebar + main chat
- Desktop: Full layout options

## Key Hooks & State

```jsx
- useRef (message list scroll)
- useState (messages, input, loading)
- useEffect (auto-scroll, data fetching)
- useCallback (message handling)
- useContext (user/theme context)
```

## Message Object Structure
```jsx
{
  id: string,
  content: string,
  sender: 'user' | 'bot',
  timestamp: Date,
  status: 'sending' | 'sent' | 'error',
  metadata?: {
    source?: string,
    citations?: array
  }
}
```

## Integration Points
- Connect to backend chat API
- Handle streaming responses
- Support WebSocket for real-time updates
- Store conversation history
- Implement retry logic for failed messages

## Accessibility Features
- ARIA labels and roles
- Keyboard navigation
- Screen reader support
- Focus management
- High contrast mode support

## Best Practices
- Optimize re-renders with memo
- Lazy load older messages
- Implement message debouncing
- Handle network errors gracefully
- Provide clear feedback for all actions
- Use optimistic UI updates
- Implement rate limiting
- Monitor message queue
