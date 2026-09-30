# AIxWord Frontend Architecture

## Overview

The AIxWord frontend is a React-based single-page application (SPA) built with TypeScript, Vite, and Tailwind CSS. It provides an interactive crossword puzzle experience with AI-powered generation and solving capabilities.

## Technology Stack

- **Framework**: React 18.2.0
- **Language**: TypeScript 5.3.3
- **Build Tool**: Vite 5.0.8
- **Styling**: Tailwind CSS 3.3.6 + CSS Modules
- **HTTP Client**: Axios 1.6.2
- **Testing**: Vitest 1.0.4 + React Testing Library + Playwright
- **Linting**: ESLint 8.55.0 with TypeScript support

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
│   │   ├── SolvingControls.tsx
│   │   └── *.module.css     # Component-scoped styles
│   ├── hooks/               # Custom React hooks
│   │   ├── __tests__/       # Hook tests
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
│   └── manual-solving.spec.ts
├── public/                  # Static assets
├── index.html               # HTML entry point
├── vite.config.ts           # Vite configuration
├── vitest.config.ts         # Vitest configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## Architecture Patterns

### 1. Component Architecture

#### Container/Presentational Pattern

- **Container Components**: Manage state and business logic
  - `PuzzleContainer`: Orchestrates the entire puzzle flow
  - `PuzzleGenerator`: Manages puzzle generation workflow
  
- **Presentational Components**: Focus on UI rendering
  - `Grid`, `GridCell`: Display the crossword grid
  - `CluePanel`, `ClueList`: Display clues
  - `SolvingControls`, `PuzzleActions`: Action buttons

#### Component Composition

Components are designed to be composable and reusable:

```
PuzzleContainer
├── PuzzleGeneratorForm
│   └── GenerationProgress
├── Grid
│   └── GridCell (multiple)
├── CluePanel
│   ├── ClueList (Across)
│   └── ClueList (Down)
├── SolvingControls
└── PuzzleActions
```

### 2. State Management

#### Local State with Hooks

The application uses React hooks for state management:

- **usePuzzle**: Central puzzle state (grid, clues, metadata)
- **useAPI**: API call state (loading, data, error)
- **useSolving**: Solving-specific state (progress, validation)

#### State Flow

```
User Action → Component Event Handler → Hook State Update → Component Re-render
```

Example:
```typescript
// User clicks cell
onCellSelect(row, col)
  ↓
usePuzzle.selectCell(row, col)
  ↓
setSelectedCell({ row, col })
  ↓
Grid re-renders with new selection
```

#### State Immutability

All state updates follow immutability principles:

```typescript
// ✅ Correct: Create new array
const updatedCells = cells.map(cell => 
  cell.row === row && cell.col === col 
    ? { ...cell, value: newValue }
    : cell
);

// ❌ Wrong: Mutate existing array
cells[index].value = newValue;
```

### 3. Data Flow

#### Unidirectional Data Flow

```
Backend API
    ↓
API Client (services/api.ts)
    ↓
useAPI Hook
    ↓
Container Component
    ↓
Presentational Components
    ↓
User Interaction
    ↓
Event Handlers
    ↓
State Update (back to top)
```

#### API Integration

The `apiClient` service provides a clean interface to the backend:

```typescript
// services/api.ts
export const apiClient = {
  generatePuzzle: (request: PuzzleGenerateRequest) => 
    axios.post('/api/puzzles/generate', request),
  
  solvePuzzle: (puzzleId: string, request: SolvePuzzleRequest) =>
    axios.post(`/api/puzzles/${puzzleId}/solve`, request),
  
  // ... other methods
};
```

The `useAPI` hook wraps API calls with loading/error state:

```typescript
const { data, loading, error, execute } = useAPI<PuzzleGenerateResponse>();

// Execute API call
const response = await execute(() => apiClient.generatePuzzle(request));
```

### 4. Type Safety

#### Strict TypeScript Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

#### Type Definitions

All data structures are strongly typed:

- **Domain Types** (`types/puzzle.ts`): Core puzzle entities
- **API Types** (`types/api.ts`): Request/response schemas
- **Component Props**: Explicit prop interfaces

```typescript
export interface GridProps {
  cells: Cell[];
  gridSize: number;
  selectedCell: { row: number; col: number } | null;
  onCellSelect: (row: number, col: number) => void;
  // ... other props
}
```

### 5. Styling Strategy

#### Hybrid Approach: Tailwind + CSS Modules

- **Tailwind CSS**: Utility classes for rapid development
  - Layout (flexbox, grid)
  - Spacing (margin, padding)
  - Colors and typography
  
- **CSS Modules**: Component-scoped styles for complex UI
  - Grid cell positioning
  - Animations and transitions
  - Component-specific layouts

```tsx
// Using Tailwind
<div className="flex items-center gap-4 p-4 bg-white rounded-lg shadow">

// Using CSS Modules
<div className={styles.gridContainer}>
  <div className={styles.cell} />
</div>
```

### 6. Error Handling

#### Layered Error Handling

1. **API Layer**: Axios interceptors catch network errors
2. **Hook Layer**: `useAPI` captures and exposes errors
3. **Component Layer**: Display user-friendly error messages
4. **Global Layer**: Error boundaries catch React errors

```typescript
// API error handling
try {
  const response = await apiClient.generatePuzzle(request);
  return response.data;
} catch (error) {
  if (axios.isAxiosError(error)) {
    return { error: error.response?.data?.message || 'Network error' };
  }
  return { error: 'Unexpected error occurred' };
}
```

#### Graceful Degradation

- Failed API calls don't crash the app
- Partial data is displayed when available
- Retry mechanisms for transient failures
- Clear error messages guide user recovery

### 7. Performance Optimizations

#### React Optimizations

- **useMemo**: Memoize expensive computations
  ```typescript
  const completionPercentage = useMemo(() => 
    calculateCompletion(userCells), 
    [userCells]
  );
  ```

- **useCallback**: Prevent unnecessary re-renders
  ```typescript
  const handleCellSelect = useCallback((row: number, col: number) => {
    selectCell(row, col);
  }, [selectCell]);
  ```

- **React.memo**: Memoize components
  ```typescript
  export const GridCell = React.memo<GridCellProps>(({ ... }) => {
    // Component implementation
  });
  ```

#### Code Splitting

Vite automatically code-splits the application:
- Lazy loading for route-based components (future)
- Dynamic imports for heavy dependencies
- Optimized bundle sizes

#### Asset Optimization

- SVG icons for scalability
- Optimized images in public folder
- CSS purging via Tailwind (production builds)

### 8. Testing Strategy

#### Three-Layer Testing Pyramid

1. **Unit Tests** (Vitest + React Testing Library)
   - Component rendering and behavior
   - Hook logic and state updates
   - Utility function correctness
   - Coverage target: 80%+

2. **Integration Tests** (Vitest + React Testing Library)
   - Component interactions
   - API integration with mocked backend
   - State management across components
   - User workflows

3. **End-to-End Tests** (Playwright)
   - Complete user journeys
   - Real browser interactions
   - Backend integration (requires running server)
   - Critical paths only

#### Test Organization

```
src/
├── components/
│   ├── Grid.tsx
│   └── __tests__/
│       ├── Grid.test.tsx          # Unit tests
│       └── integration.test.tsx   # Integration tests
e2e/
├── puzzle-generation.spec.ts      # E2E tests
└── manual-solving.spec.ts         # E2E tests
```

#### Testing Best Practices

- **Arrange-Act-Assert** pattern
- Test user behavior, not implementation details
- Use semantic queries (`getByRole`, `getByLabelText`)
- Mock external dependencies (API calls)
- Test error states and edge cases

### 9. Accessibility (a11y)

#### WCAG 2.1 AA Compliance

- **Keyboard Navigation**: Full keyboard support
  - Arrow keys for grid navigation
  - Tab for focus management
  - Space/Enter for actions
  
- **Screen Reader Support**:
  - Semantic HTML (`<button>`, `<input>`, `<label>`)
  - ARIA attributes where needed
  - Descriptive labels and alt text
  
- **Visual Accessibility**:
  - High contrast colors
  - Focus indicators
  - Sufficient text size (16px minimum)
  - Color is not the only indicator

```tsx
// Accessible button example
<button
  aria-label="Generate puzzle"
  aria-busy={loading}
  disabled={loading}
>
  {loading ? 'Generating...' : 'Generate Puzzle'}
</button>
```

### 10. Build and Deployment

#### Development Build

```bash
npm run dev
# Starts Vite dev server on http://localhost:5173
# Hot Module Replacement (HMR) enabled
# Source maps for debugging
```

#### Production Build

```bash
npm run build
# 1. TypeScript compilation (tsc)
# 2. Vite build (bundling, minification)
# 3. Output to dist/ folder
```

#### Build Optimizations

- Tree shaking (removes unused code)
- Minification (Terser)
- CSS purging (Tailwind)
- Asset hashing for cache busting
- Gzip compression

## Key Design Decisions

### 1. Why React?

- **Component-based**: Natural fit for crossword grid (cells, clues)
- **Ecosystem**: Rich library ecosystem (testing, routing, state)
- **Performance**: Virtual DOM for efficient updates
- **Developer Experience**: Excellent tooling and documentation

### 2. Why TypeScript?

- **Type Safety**: Catch errors at compile time
- **IntelliSense**: Better IDE support and autocomplete
- **Refactoring**: Safer code changes
- **Documentation**: Types serve as inline documentation

### 3. Why Vite?

- **Fast**: Lightning-fast HMR and build times
- **Modern**: Native ES modules, no bundling in dev
- **Simple**: Minimal configuration
- **Optimized**: Production builds are highly optimized

### 4. Why Tailwind CSS?

- **Rapid Development**: Utility-first approach speeds up styling
- **Consistency**: Design system built-in
- **Performance**: Purges unused CSS in production
- **Responsive**: Mobile-first responsive design

### 5. Why CSS Modules for Components?

- **Scoping**: Avoid global CSS conflicts
- **Maintainability**: Styles co-located with components
- **Flexibility**: Complex layouts easier than pure Tailwind
- **Performance**: Only load styles for rendered components

### 6. Why Axios over Fetch?

- **Interceptors**: Global request/response handling
- **Automatic JSON**: Parses JSON responses automatically
- **Error Handling**: Better error handling out of the box
- **Timeout Support**: Built-in request timeouts
- **TypeScript Support**: Excellent type definitions

### 7. Why Custom Hooks over Context API?

- **Simplicity**: Easier to understand and test
- **Performance**: No unnecessary re-renders
- **Flexibility**: Compose hooks as needed
- **Testability**: Hooks can be tested in isolation

## Future Enhancements

### Planned Improvements

1. **State Management**: Consider Zustand/Redux for complex state
2. **Routing**: Add React Router for multi-page navigation
3. **PWA**: Progressive Web App capabilities (offline support)
4. **Internationalization**: Multi-language support (i18n)
5. **Themes**: Dark mode and custom themes
6. **Animations**: Framer Motion for smooth transitions
7. **Persistence**: LocalStorage for saving progress
8. **Social Features**: Share puzzles, leaderboards

### Scalability Considerations

- **Code Splitting**: Route-based lazy loading
- **Virtual Scrolling**: For large grids (15x15+)
- **Web Workers**: Offload heavy computations
- **Service Workers**: Caching and offline support
- **CDN**: Static asset delivery
- **Monitoring**: Error tracking (Sentry) and analytics

## Development Guidelines

### Code Style

- Follow ESLint rules (enforced in CI)
- Use Prettier for formatting (future)
- Meaningful variable and function names
- JSDoc comments for complex functions
- Keep components under 300 lines

### Component Guidelines

- One component per file
- Props interface at the top
- Destructure props in function signature
- Use TypeScript for all props
- Export component as default

### Hook Guidelines

- Prefix with `use` (e.g., `usePuzzle`)
- Return object with named properties
- Document return values with JSDoc
- Keep hooks focused (single responsibility)

### Testing Guidelines

- Test file next to source file or in `__tests__`
- Name: `ComponentName.test.tsx`
- Mock external dependencies
- Test user interactions, not implementation
- Aim for 80%+ coverage

## Troubleshooting

### Common Issues

1. **Port 5173 already in use**
   ```bash
   # Kill process on port 5173
   lsof -ti:5173 | xargs kill -9
   ```

2. **TypeScript errors after npm install**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Tests failing with "document is not defined"**
   - Ensure `vitest.config.ts` has `environment: 'jsdom'`
   - Check `src/test/setup.ts` is configured

4. **Styles not applying**
   - Verify Tailwind is configured in `postcss.config.js`
   - Check `index.css` imports Tailwind directives
   - Restart dev server after config changes

### Debug Tools

- **React DevTools**: Browser extension for component inspection
- **Vite Inspector**: Built-in dev server inspector
- **TypeScript Compiler**: `tsc --noEmit` for type checking
- **ESLint**: `npm run lint` for code quality

## Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Vitest Documentation](https://vitest.dev)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev)

## Contributing

See the main project README for contribution guidelines.

## License

See the main project LICENSE file.
