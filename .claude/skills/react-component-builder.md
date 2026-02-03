---
name: react-component-builder
description: Build reusable React functional components with proper props, hooks, and documentation
model: sonnet
---

# React Component Builder Skill

## Purpose
Create well-structured, documented React functional components following best practices.

## Key Responsibilities
- Design component architecture
- Build functional components with React Hooks
- Manage component props and PropTypes/TypeScript types
- Handle component state and lifecycle
- Create custom hooks when needed
- Write comprehensive JSDoc documentation
- Ensure component reusability and composability

## Component Structure
```
Component
├── Props definition (PropTypes or types)
├── Custom hooks (if needed)
├── State management (useState, useCallback, etc.)
├── Effects (useEffect, useLayoutEffect)
├── Event handlers
├── Render logic
└── Export statement
```

## When to Use
- Creating new UI components
- Building feature-specific components
- Creating reusable component libraries
- Refactoring existing components
- Building container/presentational component pairs

## Typical Outputs
- Complete React component code
- Props definition with defaults
- JSDoc comments
- Usage examples
- State management code if needed

## Component Types

### Presentational Components
- Pure UI components
- Accept data via props
- Focus on rendering
- Highly reusable

### Container Components
- Data fetching logic
- State management
- Business logic
- Connect to context/Redux

### Custom Hooks
- Shared logic extraction
- Reusable state logic
- API calls wrapping
- Event handlers

## Best Practices
- Keep components small and focused (single responsibility)
- Use meaningful prop names
- Provide default props
- Memoize expensive components (React.memo)
- Use useCallback for stable function references
- Document all props with JSDoc
- Create compound components for complex UIs
- Test components in isolation
- Use composition over inheritance

## Code Example Structure
```jsx
import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';

/**
 * ComponentName - Component description
 *
 * @param {Object} props - Component props
 * @param {string} props.title - Component title
 * @param {Function} props.onClick - Click handler
 * @returns {JSX.Element}
 */
const ComponentName = ({ title, onClick, children }) => {
  const [state, setState] = useState(null);

  const handleClick = useCallback(() => {
    onClick?.();
  }, [onClick]);

  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};

ComponentName.propTypes = {
  title: PropTypes.string.isRequired,
  onClick: PropTypes.func,
  children: PropTypes.node,
};

ComponentName.defaultProps = {
  onClick: null,
  children: null,
};

export default ComponentName;
```
