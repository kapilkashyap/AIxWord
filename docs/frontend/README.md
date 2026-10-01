# Frontend Documentation

This directory contains comprehensive documentation for the AIxWord frontend application.

## Overview

The AIxWord frontend is a modern React-based single-page application built with TypeScript, Vite, and Tailwind CSS. It provides an interactive crossword puzzle experience with AI-powered generation and solving capabilities.

## Documentation Structure

### Architecture Documentation

**[Frontend Architecture](./architecture/FRONTEND_ARCHITECTURE.md)**
- Technology stack and design decisions
- Component architecture and patterns
- State management strategy
- Data flow and API integration
- Styling approach (Tailwind + CSS Modules)
- Performance optimizations
- Testing strategy
- Accessibility guidelines
- Build and deployment process

### API Documentation

**[Types and API Client](./api/TYPES_AND_API_CLIENT.md)**
- TypeScript type definitions
  - Puzzle domain types (Cell, Clue, Puzzle, etc.)
  - API request/response types
  - UI state types
- API client documentation
  - Available methods and endpoints
  - Request/response schemas
  - Error handling
- Custom hooks reference
  - `useAPI` - API call state management
  - `useMultiAPI` - Multiple API calls
  - `usePuzzle` - Puzzle state management
- Utility functions
  - Grid utilities
  - Validation utilities
  - Keyboard utilities

### User Guides

**[User Guide](./guides/USER_GUIDE.md)**
- Getting started with AIxWord
- Generating puzzles
- Solving puzzles
- AI assistance features
- Keyboard shortcuts
- Tips and tricks for all skill levels
- Troubleshooting common issues
- FAQ

## Quick Links

### For Developers

- **Setup**: See [frontend/README.md](../../frontend/README.md) for installation and setup
- **Architecture**: [Frontend Architecture](./architecture/FRONTEND_ARCHITECTURE.md)
- **API Client**: [Types and API Client](./api/TYPES_AND_API_CLIENT.md)
- **Testing**: [Testing Guide](../guides/TESTING.md)
- **Contributing**: [Contributing Guide](../guides/CONTRIBUTING.md)

### For Users

- **Getting Started**: [User Guide](./guides/USER_GUIDE.md)
- **Quick Start**: [Quick Start Guide](../guides/QUICK_START.md)
- **Deployment**: [Deployment Guide](../guides/DEPLOYMENT.md)

### Related Documentation

- **Backend API**: [API Reference](../api/API_REFERENCE_COMPLETE.md)
- **System Architecture**: [Architecture Overview](../architecture/ARCHITECTURE.md)
- **Multi-Agent System**: [Multi-Agent System](../architecture/MULTI_AGENT_SYSTEM.md)
- **Development Guide**: [Development Guide](../guides/DEVELOPMENT.md)

## Technology Stack

- **Framework**: React 18.2.0
- **Language**: TypeScript 5.3.3
- **Build Tool**: Vite 5.0.8
- **Styling**: Tailwind CSS 3.3.6 + CSS Modules
- **HTTP Client**: Axios 1.6.2
- **Testing**: Vitest 1.0.4 + React Testing Library + Playwright
- **Linting**: ESLint 8.55.0

## Key Features

### Phase 1: Foundation (Completed)
- ✅ Project setup with Vite, React, TypeScript
- ✅ Tailwind CSS configuration
- ✅ TypeScript types for puzzle domain
- ✅ API client service
- ✅ Custom hooks for state management
- ✅ Utility functions for grid operations
- ✅ Test infrastructure setup

### Phase 2: Grid UI (Completed)
- ✅ Interactive 8×8 crossword grid
- ✅ Cell component with keyboard input
- ✅ Grid navigation with arrow keys
- ✅ Visual feedback for selected/active cells

### Phase 3: Clue Display (Completed)
- ✅ Clue panel with across/down sections
- ✅ Clue highlighting and selection
- ✅ Synchronization with grid

### Phase 4: Puzzle Generation (Completed)
- ✅ Topic input form
- ✅ Generate puzzle button
- ✅ Loading states and error handling
- ✅ Integration with backend API

### Phase 5: AI Assistance (Completed)
- ✅ Solve entire puzzle with AI
- ✅ Solve individual words
- ✅ Get hints (letter, definition, synonym)

## Development Workflow

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`

### Running Tests

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

### Code Quality

```bash
# Linting
npm run lint

# Type checking
npx tsc --noEmit
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── __tests__/       # Component unit tests
│   │   ├── Grid.tsx         # Main crossword grid
│   │   ├── GridCell.tsx     # Individual cell component
│   │   ├── CluePanel.tsx    # Clue display panel
│   │   ├── PuzzleGenerator.tsx
│   │   ├── PuzzleContainer.tsx
│   │   └── SolvingControls.tsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useAPI.ts        # API call management
│   │   ├── usePuzzle.ts     # Puzzle state management
│   │   └── useSolving.ts    # Solving state management
│   ├── services/            # External service integrations
│   │   └── api.ts           # Backend API client
│   ├── types/               # TypeScript type definitions
│   │   ├── puzzle.ts        # Puzzle domain types
│   │   └── api.ts           # API request/response types
│   ├── utils/               # Utility functions
│   │   ├── grid.ts          # Grid manipulation utilities
│   │   ├── validation.ts    # Input validation
│   │   └── keyboard.ts      # Keyboard navigation
│   ├── test/                # Test configuration
│   │   └── setup.ts         # Test environment setup
│   ├── App.tsx              # Root application component
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles
├── e2e/                     # End-to-end tests (Playwright)
│   ├── puzzle-generation.spec.ts
│   ├── manual-solving.spec.ts
│   ├── ai-assistance.spec.ts
│   └── complete-workflow.spec.ts
├── public/                  # Static assets
├── index.html               # HTML entry point
├── vite.config.ts           # Vite configuration
├── vitest.config.ts         # Vitest configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── README.md                # Setup and quick start guide
```

## Path Aliases

The project uses TypeScript path aliases for cleaner imports:

```typescript
import { apiClient } from '@services/api';
import { usePuzzle } from '@hooks/usePuzzle';
import { Cell } from '@types/puzzle';
import { getCellAt } from '@utils/grid';
```

Available aliases:
- `@/` → `./src/`
- `@components/` → `./src/components/`
- `@hooks/` → `./src/hooks/`
- `@services/` → `./src/services/`
- `@types/` → `./src/types/`
- `@utils/` → `./src/utils/`

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Contributing

See the [Contributing Guide](../guides/CONTRIBUTING.md) for information on:
- Code style guidelines
- Component structure
- Testing requirements
- Pull request process

## Support

- **Documentation**: Check this guide and related docs
- **Issues**: Report bugs or request features on GitHub
- **Development**: See [Development Guide](../guides/DEVELOPMENT.md)

---

**Last Updated**: 2026-09-30
