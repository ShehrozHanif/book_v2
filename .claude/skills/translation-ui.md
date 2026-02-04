---
name: translation-ui
description: Add language toggle, localization support, and RTL text handling for multilingual UI
model: sonnet
---

# Translation UI Skill

## Purpose
Implement language switching, internationalization (i18n), and right-to-left (RTL) text support for global accessibility.

## Key Responsibilities
- Build language switcher component
- Implement i18n/localization framework
- Handle RTL text direction
- Manage language persistence
- Load language-specific resources
- Handle text direction for mixed content
- Manage locale-specific formatting
- Support dynamic language switching
- Ensure translation quality and consistency

## Language Support Strategy

### Supported Languages
- English (en) - LTR (Left-to-Right)
- Urdu (ur) - RTL (Right-to-Left)
- Additional languages as needed

### Implementation Approach
- Use i18next for translation management
- Namespace-based organization
- Lazy loading of language files
- Fallback to English

## i18next Setup

```jsx
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      ur: { translation: urTranslations }
    },
    lng: localStorage.getItem('language') || 'en',
    fallbackLng: 'en',
    interpolation: { escapeValue: false }
  });
```

## Language Switcher Component

```jsx
<LanguageSwitcher
  languages={['en', 'ur']}
  currentLanguage={i18n.language}
  onLanguageChange={(lang) => changeLanguage(lang)}
/>
```

### Switcher Options
- Dropdown menu
- Button group
- Flag icons with labels
- Compact icon-only buttons

## RTL Implementation

### Document-level RTL
```jsx
useEffect(() => {
  const direction = i18n.language === 'ur' ? 'rtl' : 'ltr';
  document.documentElement.dir = direction;
  document.documentElement.lang = i18n.language;
}, [i18n.language]);
```

### Component-level RTL
```jsx
const isRTL = i18n.language === 'ur';

className={isRTL ? 'text-right' : 'text-left'}
style={{
  marginRight: isRTL ? '1rem' : 'auto',
  marginLeft: isRTL ? 'auto' : '1rem'
}}
```

### Flexbox RTL
```jsx
// Instead of flex-row/flex-col, use Tailwind's RTL support
className="flex flex-row-reverse rtl:flex-row"
```

## Translation File Structure

### English (en.json)
```json
{
  "common": {
    "home": "Home",
    "about": "About",
    "contact": "Contact"
  },
  "chatbot": {
    "placeholder": "Ask a question...",
    "send": "Send"
  }
}
```

### Urdu (ur.json)
```json
{
  "common": {
    "home": "ہوم",
    "about": "ہمارے بارے میں",
    "contact": "رابطہ"
  },
  "chatbot": {
    "placeholder": "سوال پوچھیں...",
    "send": "بھیجیں"
  }
}
```

## Translation Hook Usage

```jsx
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t, i18n } = useTranslation();

  return (
    <div dir={i18n.language === 'ur' ? 'rtl' : 'ltr'}>
      <h1>{t('common.home')}</h1>
      <button onClick={() => i18n.changeLanguage('ur')}>
        {t('common.language')}
      </button>
    </div>
  );
};
```

## Text Direction Utilities

```jsx
const useTextDirection = () => {
  const { i18n } = useTranslation();
  const isRTL = i18n.language === 'ur';

  return {
    isRTL,
    direction: isRTL ? 'rtl' : 'ltr',
    marginLeft: isRTL ? 'auto' : undefined,
    marginRight: isRTL ? undefined : 'auto',
    textAlign: isRTL ? 'right' : 'left'
  };
};
```

## Common RTL Patterns

### Flexbox Layout
```jsx
// Reverse flex direction for RTL
className={`flex gap-4 ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}
```

### Spacing
```jsx
// Use logical properties
style={{
  paddingInlineStart: isRTL ? 'auto' : '1rem',
  paddingInlineEnd: isRTL ? '1rem' : 'auto'
}}
```

### Icons
```jsx
// Flip icons for RTL
<Icon style={{ transform: isRTL ? 'scaleX(-1)' : 'none' }} />
```

## Locale-specific Formatting

### Number Formatting
```jsx
const formatNumber = (num, locale) => {
  return new Intl.NumberFormat(locale).format(num);
};
```

### Date Formatting
```jsx
const formatDate = (date, locale) => {
  return new Intl.DateTimeFormat(locale).format(date);
};
```

### Currency Formatting
```jsx
const formatCurrency = (amount, locale) => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
};
```

## Translation Management

### Translation Keys
- Flat or nested structure
- Consistent naming convention
- Grouped by feature/page
- Include context in keys

### Plural Forms
```jsx
t('items', { count: itemCount })
```

### Interpolation
```jsx
t('welcome', { name: 'Ahmed' })
// "Welcome, Ahmed"
```

## Persistence & Caching

```jsx
// Save language preference
const changeLanguage = (lang) => {
  i18n.changeLanguage(lang);
  localStorage.setItem('language', lang);
  localStorage.setItem('direction', lang === 'ur' ? 'rtl' : 'ltr');
};

// Load on app startup
useEffect(() => {
  const savedLang = localStorage.getItem('language') || 'en';
  i18n.changeLanguage(savedLang);
}, []);
```

## Quality Assurance

- Verify text direction consistency
- Check for broken translations
- Test mixed LTR/RTL content
- Validate date/number formatting
- Check component spacing with different text lengths
- Test keyboard navigation in RTL
- Verify icon orientation

## Accessibility

- Set document dir attribute
- Use lang attribute for language
- Proper text alignment per direction
- Icon flipping for directional arrows
- Keyboard navigation RTL support
