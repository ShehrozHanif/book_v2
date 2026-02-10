# Personalization Integration Setup Guide

## Overview

This Docusaurus textbook site now includes full personalization features:
- 🔐 User authentication (login/registration)
- 📊 Progress tracking with sidebar checkmarks
- 📝 Interactive practice questions at chapter end
- 📈 Comprehensive statistics dashboard
- 💾 Automatic progress caching

## Prerequisites

- Node.js >= 20.0
- Backend API running at `http://localhost:8000/api/v1`
- npm or yarn package manager

## Installation

### 1. Install Dependencies

```bash
cd frontend/textbook-site
npm install
# or
yarn install
```

This will install required dependencies including:
- `react-router-dom` - for client-side routing (login page, dashboard)
- `recharts` - for charting (optional, we use CSS-based charts)

### 2. Environment Configuration

Create a `.env` file in `frontend/textbook-site/`:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1

# Optional: for production builds
NODE_ENV=development
```

The app will default to `http://localhost:8000/api/v1` if not specified.

## Running the Application

### Development Mode

```bash
cd frontend/textbook-site
npm run start
```

The site will run at `http://localhost:3000/book/`

### Production Build

```bash
npm run build
npm run serve
```

## Features

### 1. Authentication

**Login Page**: `/login`
- Email and password login
- Account registration
- Automatic redirect after login
- Tokens stored in localStorage (access_token, refresh_token)

**Authentication Gate**:
- Personalization features require login
- Non-authenticated users see "Login to track progress" prompts
- Dashboard redirects to login if not authenticated

### 2. Sidebar Progress Indicators

Displays progress icons next to chapters in sidebar:
- ✓ (green) = Completed
- 📈 (orange) = In Progress
- ◯ (gray) = Not Started

**Hover** to see mastery percentage.

Only visible to authenticated users.

### 3. Practice Questions Widget

Appears at bottom of each chapter page:
- Dynamically loads questions from backend
- Multiple choice format
- Collapsible interface
- Shows score after submission
- Automatically updates sidebar progress

**For non-authenticated users**: Shows login prompt

### 4. Dashboard

**URL**: `/dashboard`

Comprehensive statistics page showing:
- Overall progress overview
- Mastery heatmap by chapter
- Time spent distribution
- Learning curve over time
- Recommended focus areas
- Achievement statistics

**Requires authentication**: Redirects to login if not authenticated

### 5. Progress Caching

Progress data is cached in localStorage:
- 5-minute automatic refresh
- Instant load on return visits
- Automatic cache invalidation after practice submission

## Architecture

### Components

**Frontend Structure**:
```
src/
├── components/
│   ├── PersonalizationProvider.tsx      # Auth context & state
│   ├── SidebarProgressInjector.tsx      # Injects progress icons
│   ├── PracticeWidgetInjector.tsx       # Injects practice widget
│   ├── PracticeQuestionsWidget.tsx      # Practice questions UI
│   ├── ProgressCard.tsx                 # Progress overview
│   └── StatisticsCharts.tsx             # Statistics visualizations
├── pages/
│   ├── login.tsx                        # Login/Register page
│   └── dashboard.tsx                    # Statistics dashboard
├── services/
│   └── personalizationApi.ts            # API client (20+ methods)
├── types/
│   └── personalization.ts               # TypeScript interfaces
├── hooks/
│   ├── usePersonalization.ts            # Context hook
│   └── useChapterProgress.ts            # Chapter progress hook
└── theme/
    ├── Root.tsx                         # Wraps app with provider
    └── NavbarItem/                      # (optional navbar customization)
```

### Data Flow

```
┌─────────────────────────────────────────┐
│     Docusaurus Root Component           │
│  (src/theme/Root.tsx)                   │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐  ┌──────────────────────┐
│PersonalizationProvider             │
│ - Auth state                        │
│ - Progress data                     │
│ - API access                        │
└────────┬─────────────────────────────┘
         │
    ┌────┴──────────────┬─────────────┬─────────────┐
    ▼                  ▼              ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐
│ Sidebar     │ │ Practice    │ │ Dashboard   │ │ Navbar  │
│ Injector    │ │ Injector    │ │ Page        │ │ Items   │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────┘
```

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/users/login` | POST | Authenticate user |
| `/users/register` | POST | Create account |
| `/users/{id}/profile` | GET | Get user profile |
| `/users/{id}/progress` | GET | Get all chapter progress |
| `/users/{id}/chapters/{ch}/practice` | GET | Get practice questions |
| `/users/{id}/chapters/{ch}/practice` | POST | Submit practice answers |
| `/users/{id}/statistics` | GET | Get comprehensive statistics |

## localStorage Schema

```javascript
{
  "access_token": "eyJhbGc...",              // JWT token
  "refresh_token": "refresh_xyz...",         // Refresh token
  "user": "{...}",                           // User object
  "progress_cache": "{...}",                 // Cached progress
  "progress_cache_timestamp": "1707..."      // Cache expiry
}
```

## Responsive Design

### Breakpoints

- **Desktop** (>1024px): Full-width layout
- **Tablet** (768px-1024px): Adjusted spacing, stacked sidebar
- **Mobile** (320px-768px): Single column, optimized touch targets
- **Small Mobile** (<320px): Minimal padding, text size reduced

### Key Features

- Touch-friendly buttons (≥44px height)
- Readable text at mobile sizes (≥14px)
- Practice widget scrollable on small screens
- Dashboard cards stack vertically on mobile

## Accessibility

### ARIA Labels

- All buttons have descriptive labels
- Form inputs have associated labels
- Loading states announced with aria-live
- Links include descriptive text

### Keyboard Navigation

- Tab through all interactive elements
- Enter/Space to submit forms
- Escape to close modals (when implemented)
- Arrow keys in radio button groups (practice widget)

### Screen Reader Support

- Semantic HTML (buttons, labels, headings)
- ARIA labels for icons
- Form validation feedback
- Progress status announcements

## Troubleshooting

### Login Issues

**Problem**: "Invalid email or password"
- Verify user exists in backend database
- Check backend API is running
- Confirm API URL in .env is correct

**Problem**: Login successful but no progress appears
- Check browser localStorage permissions
- Verify user_id matches progress records in DB
- Check API authentication headers

### Practice Widget Not Appearing

**Problem**: Widget doesn't show on chapter pages
- Verify chapter URL contains `/chapter-` pattern
- Check browser console for errors
- Ensure React has fully hydrated page
- Verify chapter has practice questions in backend

**Problem**: Questions load but submission fails
- Verify all questions are answered
- Check network tab for API errors
- Verify user authentication token is valid

### Dashboard Not Loading

**Problem**: Blank page or redirect to login
- Verify you're logged in (check localStorage)
- Check browser console for errors
- Verify API statistics endpoint is working
- Clear localStorage and re-authenticate

### Sidebar Icons Not Showing

**Problem**: Progress icons not visible in sidebar
- Verify you're logged in
- Check browser's data-auth attribute on body tag
- Verify CSS is loaded (.chapter-progress-icon-wrapper)
- Open browser DevTools to inspect sidebar items

## Performance Tips

### Caching

- Progress data cached 5 minutes
- Browser caches API responses
- localStorage for instant page loads

### Optimization

- Lazy load ChatBot component
- Debounce sidebar progress updates
- React.lazy() for page components
- CSS-based charts (no recharts overhead)

### Production Build

```bash
npm run build
```

Creates optimized production bundle with:
- Minified JavaScript
- Chunked code splitting
- Optimized CSS
- Source maps for debugging

## Development Workflow

### Adding New Features

1. **Add to PersonalizationProvider** if you need new state/methods
2. **Use usePersonalization hook** to access auth state
3. **Add tests** for new components
4. **Update documentation** with new features

### Testing

```bash
# Run tests (if configured)
npm run test

# Build for production
npm run build

# Check for errors
npm run lint
```

### Debugging

1. **Browser DevTools**:
   - Check Network tab for API calls
   - Inspect localStorage for tokens
   - Use React DevTools for component state

2. **Console Logs**:
   - PersonalizationProvider logs auth initialization
   - API errors logged to console
   - Sidebar injector logs progress icons added

3. **Network Inspection**:
   - Check Authorization headers sent
   - Verify API response format
   - Monitor request/response timing

## Security Notes

### JWT Tokens

- Stored in localStorage (visible to XSS)
- 1-hour expiration (refresh token for renewal)
- Sent as `Bearer` in Authorization header
- Never store sensitive data in tokens

### Best Practices

- Always use HTTPS in production
- Implement token refresh on 401 responses (if not already)
- Validate user input on backend
- Use secure password hashing
- Implement CORS policies

### Future Improvements

- Move tokens to HttpOnly cookies
- Implement refresh token rotation
- Add rate limiting for login attempts
- Add multi-factor authentication
- Implement activity logging

## Maintenance

### Regular Tasks

- Monitor API error rates
- Review user feedback
- Update dependencies monthly
- Backup user progress data
- Monitor localStorage usage

### Common Updates

**Update API URL**:
```bash
# .env
REACT_APP_API_URL=https://api.example.com
```

**Update Default Preferences**:
Edit `frontend/src/types/personalization.ts`

**Disable Feature**:
Remove from `Root.tsx`:
```tsx
// <SidebarProgressInjector /> // Disabled
// <PracticeWidgetInjector />  // Disabled
```

## Support

For issues or questions:
1. Check browser console for errors
2. Verify backend API is responding
3. Review Network tab in DevTools
4. Check localStorage for corrupt data
5. Clear browser cache and try again

## Resources

- [Docusaurus Documentation](https://docusaurus.io)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Fetch API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

**Last Updated**: February 2026
**Version**: 1.0.0
