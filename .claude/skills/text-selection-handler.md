---
name: text-selection-handler
description: Detect and process text selection events for copying, highlighting, and interaction
model: sonnet
---

# Text Selection Handler Skill

## Purpose
Implement text selection detection and handling for features like copy-to-clipboard, highlighting, and contextual interactions.

## Key Responsibilities
- Detect text selection events
- Handle copy-to-clipboard functionality
- Show context menus for selections
- Highlight selected text
- Track selection position and content
- Handle multi-line selections
- Manage selection feedback (visual/audio)
- Prevent default selection behavior when needed
- Support keyboard shortcuts for selection
- Handle programmatic selection

## Text Selection Events

### Selection Detection
```jsx
const handleMouseUp = () => {
  const selection = window.getSelection();
  const selectedText = selection.toString();

  if (selectedText.length > 0) {
    // Selection made
    handleTextSelection(selectedText, selection);
  }
};

useEffect(() => {
  document.addEventListener('mouseup', handleMouseUp);
  return () => {
    document.removeEventListener('mouseup', handleMouseUp);
  };
}, []);
```

### Selection Object Properties
```jsx
const selection = window.getSelection();
{
  rangeCount: number,      // Number of selected ranges
  toString(): string,       // Selected text
  getRangeAt(index),       // Get specific range
  addRange(range),         // Add selection range
  removeAllRanges(),       // Clear selection
  collapsed: boolean       // Is selection empty?
}
```

## Copy to Clipboard

### Modern Clipboard API
```jsx
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    showCopyNotification('Copied to clipboard');
    return true;
  } catch (error) {
    console.error('Failed to copy:', error);
    showCopyNotification('Copy failed', 'error');
    return false;
  }
};
```

### Fallback for Older Browsers
```jsx
const copyToClipboardFallback = (text) => {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();

  try {
    document.execCommand('copy');
    showCopyNotification('Copied to clipboard');
  } catch (error) {
    showCopyNotification('Copy failed', 'error');
  }

  document.body.removeChild(textarea);
};
```

## Selection Context Menu

```jsx
const [selection, setSelection] = useState(null);
const [menuPosition, setMenuPosition] = useState(null);

const handleSelection = (e) => {
  const selectedText = window.getSelection().toString();

  if (selectedText.length > 0) {
    setSelection(selectedText);
    setMenuPosition({ x: e.pageX, y: e.pageY });
  }
};

return (
  <>
    <div onMouseUp={handleSelection}>
      {/* Content */}
    </div>

    {menuPosition && (
      <SelectionMenu
        position={menuPosition}
        text={selection}
        actions={['copy', 'highlight', 'quote']}
      />
    )}
  </>
);
```

## Selection Menu Component

```jsx
const SelectionMenu = ({ position, text, actions, onAction }) => {
  const handleAction = (action) => {
    switch (action) {
      case 'copy':
        navigator.clipboard.writeText(text);
        break;
      case 'highlight':
        highlightSelection(text);
        break;
      case 'quote':
        insertQuote(text);
        break;
    }
    onAction?.(action);
  };

  return (
    <div
      className="absolute bg-white shadow-lg rounded p-2 z-50"
      style={{
        top: `${position.y}px`,
        left: `${position.x}px`
      }}
    >
      {actions.map(action => (
        <button
          key={action}
          onClick={() => handleAction(action)}
          className="block w-full text-left px-3 py-2 hover:bg-gray-100"
        >
          {action.charAt(0).toUpperCase() + action.slice(1)}
        </button>
      ))}
    </div>
  );
};
```

## Highlighting Selected Text

```jsx
const highlightSelection = (text, className = 'highlight') => {
  const selection = window.getSelection();

  if (selection.rangeCount > 0) {
    const range = selection.getRangeAt(0);
    const span = document.createElement('span');
    span.className = className;
    span.style.backgroundColor = 'yellow';

    try {
      range.surroundContents(span);
    } catch (error) {
      // Fallback for complex selections
      const contents = range.extractContents();
      span.appendChild(contents);
      range.insertNode(span);
    }
  }
};
```

## Keyboard Shortcuts

```jsx
const handleKeyDown = (e) => {
  // Copy selection (Ctrl/Cmd + C)
  if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
    const selection = window.getSelection().toString();
    if (selection) {
      navigator.clipboard.writeText(selection);
    }
  }

  // Select all (Ctrl/Cmd + A)
  if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
    selectAllText();
  }
};

const selectAllText = () => {
  const selection = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(document.body);
  selection.removeAllRanges();
  selection.addRange(range);
};
```

## Selection Range Utilities

```jsx
const getSelectionRange = () => {
  const selection = window.getSelection();
  if (selection.rangeCount === 0) return null;

  const range = selection.getRangeAt(0);
  return {
    startOffset: range.startOffset,
    endOffset: range.endOffset,
    startContainer: range.startContainer,
    endContainer: range.endContainer,
    collapsed: range.collapsed,
    text: selection.toString()
  };
};

const createRangeFromPositions = (startContainer, startOffset, endContainer, endOffset) => {
  const range = document.createRange();
  range.setStart(startContainer, startOffset);
  range.setEnd(endContainer, endOffset);
  return range;
};
```

## Selection Position Detection

```jsx
const getSelectionCoordinates = () => {
  const selection = window.getSelection();
  if (selection.rangeCount === 0) return null;

  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();

  return {
    x: rect.left + window.scrollX,
    y: rect.top + window.scrollY,
    width: rect.width,
    height: rect.height,
    bottom: rect.bottom + window.scrollY
  };
};
```

## Selection Cleanup

```jsx
const clearSelection = () => {
  window.getSelection().removeAllRanges();
};

const preventSelection = (element) => {
  element.style.userSelect = 'none';
  element.style.webkitUserSelect = 'none';
  element.style.msUserSelect = 'none';
};

const allowSelection = (element) => {
  element.style.userSelect = 'auto';
};
```

## Performance Considerations

```jsx
// Debounce selection handling
const [selection, setSelection] = useState('');

const handleSelection = useCallback(
  debounce(() => {
    setSelection(window.getSelection().toString());
  }, 100),
  []
);
```

## Accessibility

- Announce copy success to screen readers
- Support keyboard selection shortcuts
- Maintain focus management
- Provide visual feedback
- Use semantic HTML for selection

## Browser Compatibility

- Modern browsers support:
  - getSelection() API
  - Clipboard API
- Fallback for older browsers:
  - execCommand('copy')
  - Manual textarea approach
