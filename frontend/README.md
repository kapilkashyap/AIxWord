# AIxWord Frontend

React-based frontend application for the AI-powered interactive crossword puzzle game.

## Overview

This is a modern React application built with:
- **React 18+** - UI framework
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API communication
- **Vitest** - Unit testing framework

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API client and services
│   ├── types/          # TypeScript type definitions
│   ├── utils/          # Utility functions
│   ├── test/           # Test setup and utilities
│   ├── App.tsx         # Root application component
│   ├── App.css         # Application styles
│   ├── main.tsx        # Application entry point
│   └── index.css       # Global styles
├── index.html          # HTML template
├── package.json        # Dependencies and scripts
├── tsconfig.json       # TypeScript configuration
├── vite.config.ts      # Vite configuration
├── tailwind.config.js  # Tailwind CSS configuration
└── vitest.config.ts    # Vitest configuration
```

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file in the frontend directory:

```bash
cp .env.example .env
```

Edit `.env` if needed:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEV_MODE=true
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Available Scripts

### Development

```bash
# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Code Quality

```bash
# Run ESLint
npm run lint

# Run type checking
npx tsc --noEmit
```

### Testing

```bash
# Run tests
npm run test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Features

### Phase 1: Foundation (Current)
- ✅ Project setup with Vite, React, TypeScript
- ✅ Tailwind CSS configuration
- ✅ TypeScript types for puzzle domain
- ✅ API client service
- ✅ Custom hooks for state management
- ✅ Utility functions for grid operations
- ✅ Test infrastructure setup

### Phase 2: Grid UI (Upcoming)
- Interactive 8×8 crossword grid
- Cell component with keyboard input
- Grid navigation with arrow keys
- Visual feedback for selected/active cells

### Phase 3: Clue Display (Upcoming)
- Clue panel with across/down sections
- Clue highlighting and selection
- Synchronization with grid

### Phase 4: Puzzle Generation (Upcoming)
- Topic input form
- Generate puzzle button
- Loading states and error handling
- Integration with backend API

### Phase 5: AI Assistance (Upcoming)
- Solve entire puzzle with AI
- Solve individual words
- Get hints (letter, definition, synonym)

## Architecture

### State Management

The application uses React hooks for state management:

- **`usePuzzle`** - Manages puzzle state, user inputs, and grid state
- **`useAPI`** - Handles API calls with loading/error states

### API Communication

The `apiClient` service provides a typed interface to the backend:

```typescript
import { apiClient } from '@services/api';

// Generate puzzle
const response = await apiClient.generatePuzzle({
  topic: 'Science',
  grid_size: 8,
  difficulty: 'medium'
});

// Solve word
const solution = await apiClient.solveWord(puzzleId, {
  clue_number: 1,
  direction: 'across'
});
```

### Type Safety

All API requests and responses are fully typed:

```typescript
import type { Puzzle, Cell, Clue } from '@types/puzzle';
import type { PuzzleGenerateRequest, PuzzleGenerateResponse } from '@types/api';
```

### Utility Functions

Helper functions for common operations:

```typescript
import { getCellAt, getWordCells, isWordComplete } from '@utils/grid';
import { validateTopic, sanitizeLetter } from '@utils/validation';
import { getNextCellFromArrow, toggleDirection } from '@utils/keyboard';
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

## Styling

The application uses Tailwind CSS with custom theme extensions:

### Custom Colors

```css
cell-empty: #ffffff
cell-blocked: #000000
cell-selected: #ffeb3b
cell-active-word: #fff9c4
cell-completed: #c8e6c9
cell-error: #ffcdd2
clue-active: #1976d2
clue-hover: #e3f2fd
```

### Custom Spacing

```css
cell: 3rem (48px) - Standard cell size
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Development Guidelines

### Code Style

- Use TypeScript strict mode
- Follow React hooks best practices
- Use functional components
- Prefer composition over inheritance
- Write self-documenting code with JSDoc comments

### Component Structure

```typescript
/**
 * Component description.
 * 
 * @param props - Component props
 * @returns JSX element
 */
function MyComponent({ prop1, prop2 }: MyComponentProps) {
  // Hooks
  const [state, setState] = useState();
  
  // Callbacks
  const handleClick = useCallback(() => {
    // ...
  }, []);
  
  // Render
  return (
    <div>
      {/* ... */}
    </div>
  );
}
```

### Testing

- Write tests alongside implementation
- Test user interactions, not implementation details
- Use React Testing Library best practices
- Aim for 90%+ coverage

## Troubleshooting

### Port Already in Use

If port 5173 is already in use:

```bash
# Kill the process using the port
lsof -ti:5173 | xargs kill -9

# Or change the port in vite.config.ts
```

### API Connection Issues

1. Ensure backend is running on `http://localhost:8000`
2. Check CORS configuration in backend
3. Verify `VITE_API_BASE_URL` in `.env`

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

## Documentation

For detailed documentation, see the [Frontend Documentation](../docs/frontend/README.md):

- **[Frontend Architecture](../docs/frontend/architecture/FRONTEND_ARCHITECTURE.md)** - Architecture patterns, design decisions, and technical details
- **[Types and API Client](../docs/frontend/api/TYPES_AND_API_CLIENT.md)** - TypeScript types, API client, hooks, and utilities
- **[User Guide](../docs/frontend/guides/USER_GUIDE.md)** - Complete user guide for solving puzzles

### Related Documentation

- **[Quick Start Guide](../docs/guides/QUICK_START.md)** - Get started quickly
- **[Development Guide](../docs/guides/DEVELOPMENT.md)** - Development workflow and best practices
- **[Testing Guide](../docs/guides/TESTING.md)** - Testing strategy and guidelines
- **[API Reference](../docs/api/API_REFERENCE_COMPLETE.md)** - Backend API documentation

## Contributing

1. Follow the existing code style
2. Write tests for new features
3. Update documentation
4. Run linter before committing
5. See [Contributing Guide](../docs/guides/CONTRIBUTING.md) for details

## License

MIT License - See LICENSE file for details
