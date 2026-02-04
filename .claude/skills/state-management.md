---
name: state-management
description: Implement efficient React state management with Hooks, Context API, and custom patterns
model: sonnet
---

# State Management Skill

## Purpose
Design and implement scalable, efficient state management for React applications using modern patterns and best practices.

## Key Responsibilities
- Design state architecture
- Create custom hooks for shared logic
- Implement Context API for global state
- Manage local component state
- Handle side effects with useEffect
- Optimize re-renders
- Implement state persistence
- Handle async operations
- Manage form state
- Create reusable state patterns

## State Types

### Local Component State
```jsx
const [count, setCount] = useState(0);
const [formData, setFormData] = useState({});
const [loading, setLoading] = useState(false);
```

### Global Application State
- User authentication
- Theme preferences
- Language/locale
- Sidebar visibility
- User settings

### Server State
- API data
- Cache
- Synchronization status

## React Hooks

### useState Hook
```jsx
const [state, setState] = useState(initialValue);

// Object state
const [form, setForm] = useState({
  name: '',
  email: ''
});

const updateForm = (field, value) => {
  setForm(prev => ({
    ...prev,
    [field]: value
  }));
};
```

### useEffect Hook
```jsx
// Fetch data on mount
useEffect(() => {
  fetchData();
}, []); // Empty dependency array = run once

// Update on prop change
useEffect(() => {
  handlePropChange();
}, [prop]); // Run when prop changes

// Cleanup
useEffect(() => {
  const unsubscribe = subscribe();
  return () => unsubscribe();
}, []);
```

### useCallback Hook
```jsx
// Prevent unnecessary re-renders of child components
const handleClick = useCallback(() => {
  doSomething(value);
}, [value]); // Only recreate if value changes
```

### useMemo Hook
```jsx
// Expensive computation caching
const expensiveValue = useMemo(() => {
  return calculateExpensiveValue(input);
}, [input]); // Only recalculate if input changes
```

### useContext Hook
```jsx
const theme = useContext(ThemeContext);
const user = useContext(UserContext);
```

### useReducer Hook
```jsx
const [state, dispatch] = useReducer(reducer, initialState);

const reducer = (state, action) => {
  switch (action.type) {
    case 'INCREMENT':
      return { ...state, count: state.count + 1 };
    case 'SET_USER':
      return { ...state, user: action.payload };
    default:
      return state;
  }
};
```

## Context API Pattern

### Create Context
```jsx
const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

### Use Context
```jsx
const MyComponent = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div style={{ background: theme === 'light' ? '#fff' : '#000' }}>
      Current theme: {theme}
      <button onClick={toggleTheme}>Toggle</button>
    </div>
  );
};
```

## Custom Hooks

### useFetch Hook
```jsx
const useFetch = (url) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url);
        const json = await response.json();
        setData(json);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
};
```

### useLocalStorage Hook
```jsx
const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
};
```

### useForm Hook
```jsx
const useForm = (initialValues, onSubmit) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleBlur = (e) => {
    const { name } = e.target;
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch (error) {
      setErrors({ submit: error.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    setValues,
    setErrors
  };
};
```

### useAsync Hook
```jsx
const useAsync = (asyncFunction, immediate = true) => {
  const [status, setStatus] = useState('idle');
  const [value, setValue] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(async () => {
    setStatus('pending');
    setValue(null);
    setError(null);
    try {
      const response = await asyncFunction();
      setValue(response);
      setStatus('success');
      return response;
    } catch (error) {
      setError(error);
      setStatus('error');
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { execute, status, value, error };
};
```

## State Pattern Best Practices

### Lift State Up
```jsx
// Don't duplicate state in multiple children
// Instead, lift state to parent
const Parent = () => {
  const [sharedValue, setSharedValue] = useState('');

  return (
    <>
      <Child1 value={sharedValue} onChange={setSharedValue} />
      <Child2 value={sharedValue} />
    </>
  );
};
```

### Single Responsibility
```jsx
// ❌ Bad: Too much state
const [user, setUser] = useState(complexObject);

// ✅ Good: Separate concerns
const [userId, setUserId] = useState('');
const [userName, setUserName] = useState('');
const [userEmail, setUserEmail] = useState('');
```

### Prevent Prop Drilling
```jsx
// Use Context for deeply nested components
const AuthContext = createContext();

// In parent
<AuthContext.Provider value={user}>
  <DeepComponent />
</AuthContext.Provider>

// In deep component
const user = useContext(AuthContext);
```

## Performance Optimization

### useMemo for Expensive Computations
```jsx
const sortedList = useMemo(() => {
  return data.sort((a, b) => a.name.localeCompare(b.name));
}, [data]);
```

### React.memo for Components
```jsx
const MemoizedComponent = React.memo(({ data }) => {
  return <div>{data}</div>;
});
```

### useCallback for Event Handlers
```jsx
const handleDelete = useCallback((id) => {
  dispatch({ type: 'DELETE', payload: id });
}, []);
```

## State Persistence

```jsx
// Persist to localStorage
useEffect(() => {
  localStorage.setItem('appState', JSON.stringify(state));
}, [state]);

// Restore on load
useEffect(() => {
  const saved = localStorage.getItem('appState');
  if (saved) {
    setState(JSON.parse(saved));
  }
}, []);
```

## State Debugging

```jsx
// Log state changes
useEffect(() => {
  console.log('State updated:', state);
}, [state]);

// Use React DevTools
// Component -> Profiler -> Track render
```

## Common Patterns

### Loading States
```jsx
if (loading) return <Loading />;
if (error) return <Error error={error} />;
return <Content data={data} />;
```

### Undo/Redo
```jsx
const [past, setPast] = useState([]);
const [present, setPresent] = useState(initialState);
const [future, setFuture] = useState([]);

const undo = () => {
  if (past.length === 0) return;
  setFuture([present, ...future]);
  setPresent(past[past.length - 1]);
  setPast(past.slice(0, -1));
};
```
