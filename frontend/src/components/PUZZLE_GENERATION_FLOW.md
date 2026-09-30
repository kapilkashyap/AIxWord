# Puzzle Generation UI Flow

This document describes the puzzle generation and solving UI flow components implemented for AIxWord.

## Overview

The puzzle generation UI flow provides a complete user experience for:
1. Generating AI-powered crossword puzzles
2. Displaying generation progress and status
3. Interacting with the puzzle grid
4. Getting AI assistance (solve, hints)
5. Validating solutions

## Components

### 1. PuzzleGeneratorForm

**Purpose**: Form component for configuring and generating new puzzles.

**Features**:
- Topic input (required)
- Grid size selection (4×4 to 20×20, default 8×8)
- Difficulty level (easy, medium, hard)
- Advanced options (min/max words, max iterations)
- Form validation with error messages
- Loading state during generation
- Responsive design

**Props**:
```typescript
interface PuzzleGeneratorFormProps {
  onSubmit: (request: PuzzleGenerateRequest) => void;
  isLoading?: boolean;
  error?: string | null;
  showAdvanced?: boolean;
  className?: string;
}
```

**Usage**:
```tsx
<PuzzleGeneratorForm
  onSubmit={handleGeneratePuzzle}
  isLoading={isGenerating}
  error={generationError}
/>
```

### 2. GenerationProgress

**Purpose**: Displays puzzle generation progress and status.

**Features**:
- Animated loading state with progress steps
- Success state with puzzle statistics
- Error state with helpful suggestions
- Smooth animations and transitions

**Props**:
```typescript
interface GenerationProgressProps {
  isGenerating: boolean;
  response: PuzzleGenerateResponse | null;
  error?: string | null;
  className?: string;
}
```

**Usage**:
```tsx
<GenerationProgress
  isGenerating={isGenerating}
  response={generationResponse}
  error={generationError}
/>
```

### 3. PuzzleActions

**Purpose**: Action buttons for puzzle solving assistance.

**Features**:
- Solve entire puzzle with AI
- Solve current word with AI
- Get hint for current word
- Validate solution
- Reset puzzle
- Loading states for each action
- Disabled states based on puzzle state
- Helpful tooltips

**Props**:
```typescript
interface PuzzleActionsProps {
  hasPuzzle: boolean;
  isComplete: boolean;
  activeClue: { number: number; direction: Direction } | null;
  isSolvingPuzzle?: boolean;
  isSolvingWord?: boolean;
  isGettingHint?: boolean;
  isValidating?: boolean;
  onSolvePuzzle: () => void;
  onSolveWord: () => void;
  onGetHint: () => void;
  onValidate: () => void;
  onReset: () => void;
  className?: string;
}
```

**Usage**:
```tsx
<PuzzleActions
  hasPuzzle={!!puzzle}
  isComplete={isComplete}
  activeClue={activeClue}
  isSolvingPuzzle={isSolvingPuzzle}
  onSolvePuzzle={handleSolvePuzzle}
  onSolveWord={handleSolveWord}
  onGetHint={handleGetHint}
  onValidate={handleValidate}
  onReset={handleReset}
/>
```

### 4. PuzzleContainer

**Purpose**: Main container orchestrating the complete puzzle flow.

**Features**:
- Manages puzzle lifecycle (generation, solving, validation)
- Integrates all puzzle components
- Handles API calls for all operations
- Provides responsive layout
- Shows notifications for hints and validation
- Progress tracking

**Props**:
```typescript
interface PuzzleContainerProps {
  className?: string;
}
```

**Usage**:
```tsx
<PuzzleContainer />
```

## User Flow

### 1. Puzzle Generation

1. User enters a topic (e.g., "Space Exploration")
2. User optionally configures grid size and difficulty
3. User clicks "Generate Puzzle"
4. GenerationProgress shows animated loading state
5. On success, puzzle is displayed with grid and clues
6. On error, helpful suggestions are shown

### 2. Puzzle Solving

1. User clicks on a cell or clue to select it
2. User types letters to fill in answers
3. User can navigate with arrow keys, tab, backspace
4. Active word is highlighted in the grid
5. Progress percentage is shown in the info bar

### 3. AI Assistance

**Solve Entire Puzzle**:
- Click "Solve Puzzle" button
- AI fills in all answers
- Loading state shown during solving

**Solve Current Word**:
- Select a word by clicking a clue or cell
- Click "Solve Word" button
- AI fills in just that word

**Get Hint**:
- Select a word
- Click "Get Hint" button
- Hint notification appears with additional clue
- Auto-dismisses after 10 seconds

### 4. Validation

1. User clicks "Validate" button
2. Solution is checked against correct answers
3. Validation notification shows:
   - Success: "Perfect! All answers are correct! 🎉"
   - Partial: "X of Y correct (Z%)"
4. Auto-dismisses after 10 seconds

### 5. Reset

1. User clicks "Reset" button
2. All user-entered letters are cleared
3. Grid returns to empty state
4. Clues and structure remain

### 6. New Puzzle

1. User clicks "New Puzzle" button
2. Returns to generation form
3. Previous puzzle is cleared

## Responsive Design

All components are fully responsive:

- **Desktop (>1024px)**: Side-by-side grid and clues
- **Tablet (768-1024px)**: Stacked layout
- **Mobile (<768px)**: Compact layout with collapsible clues
- **Small Mobile (<480px)**: Icon-only action buttons

## Styling

All components use CSS Modules for scoped styling:
- `PuzzleGeneratorForm.module.css`
- `GenerationProgress.module.css`
- `PuzzleActions.module.css`
- `PuzzleContainer.module.css`

Each module includes:
- Light mode styles (default)
- Dark mode support (`@media (prefers-color-scheme: dark)`)
- Responsive breakpoints
- Smooth animations and transitions

## State Management

The puzzle flow uses React hooks for state management:

**usePuzzle Hook**:
- Manages puzzle data and user cells
- Handles cell selection and navigation
- Tracks completion status

**useAPI Hook**:
- Manages API call state (loading, error, data)
- Provides execute function for API calls
- Handles error messages

**useMultiAPI Hook**:
- Manages multiple concurrent API calls
- Tracks state for each call separately
- Used for solving multiple words

## API Integration

All components integrate with the FastAPI backend:

**Endpoints Used**:
- `POST /api/puzzles/generate` - Generate puzzle
- `POST /api/puzzles/{id}/solve` - Solve entire puzzle
- `POST /api/puzzles/{id}/solve-word` - Solve specific word
- `POST /api/puzzles/{id}/hint` - Get hint
- `POST /api/puzzles/{id}/validate` - Validate solution

## Error Handling

Comprehensive error handling throughout:
- Form validation errors
- API error messages
- Network error handling
- User-friendly error messages
- Retry suggestions

## Accessibility

All components follow accessibility best practices:
- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader friendly
- High contrast support

## Testing

Components include test IDs for testing:
- `data-testid="puzzle-generator-form"`
- `data-testid="generation-progress"`
- `data-testid="puzzle-actions"`
- `data-testid="puzzle-container"`

## Future Enhancements

Potential improvements:
1. Document upload for RAG-based generation
2. Save/load puzzle progress
3. Puzzle history and favorites
4. Multiplayer solving
5. Timed challenges
6. Difficulty-based scoring
7. Social sharing
8. Print-friendly view
9. Puzzle templates
10. Custom grid patterns

## Files Created

### Components
- `PuzzleGeneratorForm.tsx` - Puzzle generation form
- `GenerationProgress.tsx` - Generation status display
- `PuzzleActions.tsx` - Action buttons
- `PuzzleContainer.tsx` - Main orchestrator

### Styles
- `PuzzleGeneratorForm.module.css`
- `PuzzleGeneratorForm.module.css.d.ts`
- `GenerationProgress.module.css`
- `GenerationProgress.module.css.d.ts`
- `PuzzleActions.module.css`
- `PuzzleActions.module.css.d.ts`
- `PuzzleContainer.module.css`
- `PuzzleContainer.module.css.d.ts`

### Updated Files
- `components/index.ts` - Added exports
- `App.tsx` - Uses PuzzleContainer
- `App.css` - Simplified global styles

## Integration

To use the complete puzzle flow in your app:

```tsx
import { PuzzleContainer } from './components';

function App() {
  return <PuzzleContainer />;
}
```

That's it! The PuzzleContainer handles everything else.
