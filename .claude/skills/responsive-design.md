---
name: responsive-design
description: Make React components mobile-responsive with adaptive layouts and breakpoint-based design
model: sonnet
---

# Responsive Design Skill

## Purpose
Create responsive, adaptive designs that work seamlessly across all device sizes from mobile to desktop.

## Key Responsibilities
- Implement mobile-first approach
- Design adaptive layouts for different breakpoints
- Create flexible grids and flexbox layouts
- Handle touch interactions
- Optimize images for different devices
- Implement viewport optimization
- Test across device sizes
- Manage responsive typography
- Create responsive navigation patterns

## Responsive Breakpoints

### Tailwind Breakpoints (Mobile-First)
```
xs: 0px (default)
sm: 640px (small phones)
md: 768px (tablets)
lg: 1024px (smaller desktops)
xl: 1280px (standard desktops)
2xl: 1536px (large displays)
```

## Mobile-First Approach

```jsx
// Default (mobile) styles
<div className="
  flex flex-col gap-2
  // Tablet and up
  md:flex-row md:gap-4
  // Desktop and up
  lg:gap-6
">
  Content
</div>
```

## Common Responsive Patterns

### Navigation
```jsx
// Mobile: Hamburger menu
// Tablet+: Horizontal navbar
<nav className={`
  flex items-center justify-between
  md:flex-row flex-col
  ${mobileMenuOpen ? 'block' : 'hidden'} md:flex
`}>
  <Logo />
  <Menu />
</nav>
```

### Grid Layout
```jsx
// Mobile: Single column
// Tablet: 2 columns
// Desktop: 3-4 columns
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => (
    <Card key={item.id} {...item} />
  ))}
</div>
```

### Sidebar Layout
```jsx
// Mobile: Stacked (sidebar below content)
// Desktop: Side-by-side
<div className="flex flex-col lg:flex-row gap-6">
  <main className="flex-1">
    Content
  </main>
  <aside className="w-full lg:w-64">
    Sidebar
  </aside>
</div>
```

### Card Layout
```jsx
<div className={`
  p-4 md:p-6 lg:p-8
  text-sm md:text-base lg:text-lg
  grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6
`}>
  {/* Cards */}
</div>
```

## Responsive Typography

```jsx
// Responsive font sizes
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
  Title
</h1>

// Responsive line height and spacing
<p className="text-base md:text-lg lg:text-xl leading-relaxed md:leading-loose">
  Content
</p>
```

## Responsive Images

### Image Container
```jsx
<div className="aspect-video w-full overflow-hidden rounded-lg">
  <img
    src={imageSrc}
    alt="Description"
    className="w-full h-full object-cover"
  />
</div>
```

### Responsive Image Sizes
```jsx
<img
  srcSet={`
    ${img320} 320w,
    ${img640} 640w,
    ${img1024} 1024w
  `}
  sizes="(max-width: 640px) 320px, (max-width: 1024px) 640px, 1024px"
  src={img1024}
  alt="Description"
/>
```

## Responsive Spacing

```jsx
// Padding that scales
<div className="px-4 md:px-6 lg:px-8 py-4 md:py-6 lg:py-8">
  {/* Content */}
</div>

// Gap that scales
<div className="grid gap-2 md:gap-4 lg:gap-6">
  {/* Items */}
</div>
```

## Touch Interactions

```jsx
// Increase touch target size
<button className="p-3 md:p-2 min-h-12 md:min-h-10">
  Click me
</button>

// Touch-optimized spacing
<div className="space-y-4 md:space-y-2">
  {/* Items */}
</div>

// Hover effects for desktop only
<a className="
  transition-colors
  hover:text-blue-600 md:hover:text-blue-600
  active:text-blue-800 md:active:text-blue-800
">
  Link
</a>
```

## Responsive Flex Layout

```jsx
// Adjust flex direction and wrapping
<div className="flex flex-col md:flex-row gap-4 flex-wrap">
  <div className="flex-1 min-w-0">Item 1</div>
  <div className="flex-1 min-w-0">Item 2</div>
  <div className="flex-1 min-w-0">Item 3</div>
</div>
```

## Display Utilities

```jsx
// Show/hide based on screen size
<div className="hidden md:block">
  Desktop content
</div>

<div className="md:hidden">
  Mobile content
</div>

// Responsive display
<div className="
  grid grid-cols-2 md:grid-cols-4
  flex md:grid
">
  Items
</div>
```

## Responsive Container

```jsx
// Max-width container that centers content
<div className="max-w-7xl mx-auto px-4">
  {/* Content automatically centered and padded */}
</div>
```

## Testing Responsive Design

### Browser DevTools
- Toggle device toolbar
- Test common device sizes
- Throttle network (mobile speeds)
- Test touch interactions

### Device Sizes to Test
```
Mobile:
- 320px (small phone)
- 375px (iPhone)
- 430px (large phone)

Tablet:
- 768px (iPad)
- 1024px (iPad Pro)

Desktop:
- 1280px (standard)
- 1920px (full HD)
- 2560px (4K)
```

### Responsive Checklist
- All text readable on mobile
- Touch targets at least 44x44px
- Images scale properly
- Navigation functional on mobile
- No horizontal scrolling
- Proper spacing at all sizes
- Forms usable on mobile
- Media queries working
- Font sizes readable
- Colors visible (contrast)

## Viewport Meta Tag
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

## CSS Media Queries

```jsx
// Max-width (mobile-first)
@media (max-width: 768px) {
  // Mobile styles
}

// Min-width (desktop-first - not recommended)
@media (min-width: 768px) {
  // Desktop styles
}
```

## Performance Considerations
- Minimize DOM elements for mobile
- Lazy load off-screen content
- Optimize images for screen size
- Use CSS Grid for complex layouts
- Avoid fixed widths
- Test performance on real devices
- Monitor bundle size
