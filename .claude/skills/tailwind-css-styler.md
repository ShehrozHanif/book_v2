---
name: tailwind-css-styler
description: Style React components with Tailwind CSS, manage design systems, and create responsive layouts
model: sonnet
---

# Tailwind CSS Styler Skill

## Purpose
Apply Tailwind CSS utility classes to create beautiful, responsive, and consistent component styling.

## Key Responsibilities
- Apply Tailwind utility classes effectively
- Create responsive designs with mobile-first approach
- Implement dark mode support
- Build custom Tailwind configurations
- Manage color schemes and design tokens
- Create reusable component classes
- Optimize CSS file size
- Ensure accessibility (color contrast, focus states)

## Tailwind Features

### Responsive Design
- Mobile-first breakpoints (sm, md, lg, xl, 2xl)
- Responsive utilities with prefixes
- Container queries
- Aspect ratio utilities

### Styling Utilities
- Colors and gradients
- Typography (fonts, sizes, weights, line-height)
- Spacing (margin, padding)
- Sizing (width, height)
- Flexbox and Grid
- Backgrounds and borders
- Shadows and effects
- Transforms and transitions

### Advanced Features
- Dark mode support
- Custom color schemes
- CSS-in-JS approach (no separate CSS files)
- Class composition and extraction
- Performance optimization

## Best Practices

### Class Organization
```jsx
<div className={`
  // Layout
  flex items-center justify-between
  // Sizing
  w-full h-auto
  // Spacing
  px-4 py-2 gap-2
  // Colors
  bg-white dark:bg-gray-900
  // Typography
  text-lg font-semibold
  // Borders and effects
  rounded-lg shadow-md
  // Responsive
  md:px-6 md:py-4
  lg:flex-row flex-col
`}>
  Content
</div>
```

### Design System
- Define color palette
- Establish typography scale
- Create spacing scale
- Set responsive breakpoints
- Document component patterns

### Responsive Patterns
- Mobile: 100% width, single column
- Tablet (md): 2-3 columns, optimized touch
- Desktop (lg): Full layout, multiple columns
- Large screens (xl): Sidebar layouts

### Accessibility
- Sufficient color contrast (WCAG AA/AAA)
- Focus states for interactive elements
- Proper spacing for touch targets (min 44px)
- Semantic HTML with Tailwind

## Common Patterns

### Button Styling
```jsx
className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
```

### Card Layout
```jsx
className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
```

### Responsive Grid
```jsx
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
```

### Text with Truncation
```jsx
className="truncate md:line-clamp-2 text-gray-600 dark:text-gray-300"
```

## Tailwind Configuration
- Custom color schemes
- Extended typography
- Custom spacing values
- Plugin integration
- Content paths for scanning
- Theme customization

## Tips
- Prefer utility-first approach
- Use @apply sparingly (only for complex patterns)
- Leverage dark mode with dark: prefix
- Use Tailwind plugins for complex utilities
- Keep responsive breakpoints consistent
- Test on actual devices
- Use CSS custom properties for dynamic values
