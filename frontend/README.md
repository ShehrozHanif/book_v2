# RAG Chatbot Frontend

React-based widget for the RAG Chatbot application.

## Project Structure

```
src/
├── components/       # React components
├── services/         # API and utility services
├── hooks/            # Custom React hooks
├── types/            # TypeScript type definitions
├── styles/           # CSS and styling
└── index.tsx         # Application entry point

tests/
├── unit/             # Unit tests
├── integration/      # Integration tests
└── setupTests.ts     # Test configuration
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

3. Start the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

## Development

### Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Runs the test suite

### Code Style

The project uses TypeScript for type safety and follows React best practices.

## Testing

Run tests with:
```bash
npm test
```

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.
