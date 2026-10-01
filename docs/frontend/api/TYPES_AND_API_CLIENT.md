# TypeScript Types and API Client Documentation

This document provides comprehensive documentation for the TypeScript type definitions, API client, custom hooks, and utility functions in the AIxWord frontend application.

## Table of Contents

1. [Type Definitions](#type-definitions)
2. [API Client](#api-client)
3. [Custom Hooks](#custom-hooks)
4. [Utility Functions](#utility-functions)
5. [Usage Examples](#usage-examples)

---

## Type Definitions

### Puzzle Domain Types (`src/types/puzzle.ts`)

#### Core Types

**`Direction`**
```typescript
type Direction = 'across' | 'down';
```
Represents the direction of a word in the crossword grid.

**`Difficulty`**
```typescript
type Difficulty = 'easy' | 'medium' | 'hard';
```
Represents the difficulty level of a puzzle.

**`HintType`**
```typescript
type HintType = 'letter' | 'definition' | 'synonym';
```
Represents the type of hint that can be requested.

#### Data Structures

**`Cell`**
```typescript
interface Cell {
  row: number;              // Row position (0-indexed)
  col: number;              // Column position (0-indexed)
  value: string | null;     // Letter value (uppercase), null if empty
  is_blocked: boolean;      // Whether this cell is blocked (black square)
  number: number | null;    // Clue number if this cell starts a word
}
```

**`Clue`**
```typescript
interface Clue {
  number: number;           // Clue number
  direction: Direction;     // Direction of the word
  text: string;             // Clue text
  answer: string | null;    // Answer word (may be null for unsolved)
  start_row: number;        // Starting row position
  start_col: number;        // Starting column position
  length: number;           // Length of the answer
}
```

**`Puzzle`**
```typescript
interface Puzzle {
  puzzle_id: string;                    // Unique puzzle identifier
  topic: string;                        // Topic of the puzzle
  grid_size: number;                    // Size of the grid (NxN)
  cells: Cell[];                        // All cells in the grid
  clues_across: Clue[];                 // Across clues
  clues_down: Clue[];                   // Down clues
  word_count: number;                   // Number of words in the puzzle
  fill_rate: number;                    // Grid fill rate (0.0 to 1.0)
  difficulty: Difficulty;               // Difficulty level
  created_at: string;                   // Creation timestamp
  metadata: Record<string, unknown>;    // Additional metadata
}
```

**`WordPlacement`**
```typescript
interface WordPlacement {
  word: string;             // Word text
  clue: string;             // Clue for the word
  start_row: number;        // Starting row
  start_col: number;        // Starting column
  direction: Direction;     // Direction
  number: number;           // Clue number
}
```

#### UI State Types

**`CellState`**
```typescript
interface CellState extends Cell {
  is_selected: boolean;     // Whether this cell is currently selected
  is_active_word: boolean;  // Whether this cell is part of the active word
  is_completed: boolean;    // Whether this cell is part of a completed word
  has_error: boolean;       // Whether this cell has an error
}
```

**`GridState`**
```typescript
interface GridState {
  cells: CellState[];                                   // Current cell states
  selected_cell: { row: number; col: number } | null;   // Currently selected cell
  current_direction: Direction;                         // Current word direction
  active_clue: { number: number; direction: Direction } | null;  // Currently active clue
}
```

**`ValidationError`**
```typescript
interface ValidationError {
  row: number;              // Row position
  col: number;              // Column position
  expected: string;         // Expected value
  actual: string | null;    // Actual value provided
  message: string;          // Error message
}
```

### API Types (`src/types/api.ts`)

#### Request Types

**`PuzzleGenerateRequest`**
```typescript
interface PuzzleGenerateRequest {
  topic: string;            // Topic for puzzle generation
  grid_size?: number;       // Grid size (NxN), default 8
  min_words?: number;       // Minimum number of words, default 8
  max_words?: number;       // Maximum number of words, default 15
  difficulty?: Difficulty;  // Difficulty level, default 'medium'
  max_iterations?: number;  // Maximum iterations allowed, default 50
}
```

**`SolvePuzzleRequest`**
```typescript
interface SolvePuzzleRequest {
  use_hints?: boolean;      // Whether to use existing clues as hints
}
```

**`SolveWordRequest`**
```typescript
interface SolveWordRequest {
  clue_number: number;          // Clue number to solve
  direction: Direction;         // Direction of the word
  use_intersections?: boolean;  // Whether to use intersecting letters
}
```

**`HintRequest`**
```typescript
interface HintRequest {
  clue_number: number;      // Clue number for hint
  direction: Direction;     // Direction of the word
  hint_type?: HintType;     // Type of hint to provide
}
```

**`ValidateRequest`**
```typescript
interface ValidateRequest {
  cells: Cell[];            // User's cell values
}
```

#### Response Types

**`PuzzleGenerateResponse`**
```typescript
interface PuzzleGenerateResponse {
  success: boolean;             // Whether generation was successful
  puzzle: Puzzle | null;        // Generated puzzle (if successful)
  status: string;               // Generation status
  iterations: number;           // Number of iterations executed
  error_message: string | null; // Error message (if failed)
}
```

**`SolveResponse`**
```typescript
interface SolveResponse {
  success: boolean;         // Whether solve was successful
  answer: string | null;    // The answer word or full solution
  confidence: number;       // Confidence score (0.0 to 1.0)
  reasoning: string | null; // Explanation of the solution
  updated_cells: Cell[];    // Cells that were updated
}
```

**`HintResponse`**
```typescript
interface HintResponse {
  success: boolean;             // Whether hint generation was successful
  hint: string;                 // The hint text
  hint_type: string;            // Type of hint provided
  revealed_letter: string | null;   // Revealed letter (if hint_type is 'letter')
  position: number | null;      // Position of revealed letter (if applicable)
}
```

**`ValidateResponse`**
```typescript
interface ValidateResponse {
  is_valid: boolean;        // Whether the solution is valid
  is_complete: boolean;     // Whether the puzzle is completely filled
  errors: ValidationError[]; // List of validation errors
  correct_count: number;    // Number of correct cells
  total_count: number;      // Total number of cells to fill
  accuracy: number;         // Accuracy percentage (0.0 to 1.0)
}
```

**`ErrorResponse`**
```typescript
interface ErrorResponse {
  error: string;                        // Error type or code
  message: string;                      // Human-readable error message
  details?: Record<string, unknown>;    // Additional error details
}
```

#### State Management Types

**`ApiState<T>`**
```typescript
interface ApiState<T> {
  data: T | null;           // Response data
  loading: boolean;         // Whether the request is in progress
  error: string | null;     // Error message if request failed
}
```

**`ApiConfig`**
```typescript
interface ApiConfig {
  baseUrl: string;                      // Base URL for API requests
  timeout?: number;                     // Request timeout in milliseconds
  headers?: Record<string, string>;     // Additional headers
}
```

---

## API Client

### Overview

The API client (`src/services/api.ts`) provides a centralized interface for all backend communication with proper error handling, type safety, and response validation.

### Configuration

The API client uses environment variables for configuration:

```typescript
const DEFAULT_CONFIG: ApiConfig = {
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 120000, // 2 minutes for puzzle generation
  headers: {
    'Content-Type': 'application/json',
  },
};
```

### Available Methods

#### Puzzle Generation

**`generatePuzzle(request: PuzzleGenerateRequest): Promise<PuzzleGenerateResponse>`**

Generate a new crossword puzzle based on a topic.

```typescript
const response = await apiClient.generatePuzzle({
  topic: 'Science',
  grid_size: 8,
  min_words: 8,
  max_words: 15,
  difficulty: 'medium',
});
```

#### Puzzle Retrieval

**`getPuzzle(puzzleId: string): Promise<Puzzle>`**

Retrieve a specific puzzle by ID.

```typescript
const puzzle = await apiClient.getPuzzle('puzzle-123');
```

**`listPuzzles(): Promise<Puzzle[]>`**

List all available puzzles.

```typescript
const puzzles = await apiClient.listPuzzles();
```

#### Solving Operations

**`solvePuzzle(puzzleId: string, request?: SolvePuzzleRequest): Promise<SolveResponse>`**

Solve the entire puzzle using AI.

```typescript
const solution = await apiClient.solvePuzzle('puzzle-123', {
  use_hints: true,
});
```

**`solveWord(puzzleId: string, request: SolveWordRequest): Promise<SolveResponse>`**

Solve a specific word using AI.

```typescript
const wordSolution = await apiClient.solveWord('puzzle-123', {
  clue_number: 1,
  direction: 'across',
  use_intersections: true,
});
```

#### Hints

**`getHint(puzzleId: string, request: HintRequest): Promise<HintResponse>`**

Get a hint for a specific word.

```typescript
const hint = await apiClient.getHint('puzzle-123', {
  clue_number: 1,
  direction: 'across',
  hint_type: 'letter',
});
```

#### Validation

**`validateSolution(puzzleId: string, request: ValidateRequest): Promise<ValidateResponse>`**

Validate the user's solution.

```typescript
const validation = await apiClient.validateSolution('puzzle-123', {
  cells: userCells,
});
```

#### Puzzle Management

**`deletePuzzle(puzzleId: string): Promise<void>`**

Delete a puzzle.

```typescript
await apiClient.deletePuzzle('puzzle-123');
```

### Error Handling

The API client automatically handles errors and converts them to user-friendly messages:

- **Network errors**: "Network Error: Unable to reach the server. Please check your connection."
- **Server errors**: Extracts error message from response
- **Other errors**: Generic error message with details

---

## Custom Hooks

### `useAPI<T>()`

A hook for managing API call state with loading and error handling.

**Returns:**
```typescript
{
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (apiCall: () => Promise<T>) => Promise<T | null>;
  reset: () => void;
  clearError: () => void;
}
```

**Example:**
```typescript
const { data, loading, error, execute } = useAPI<PuzzleGenerateResponse>();

const handleGenerate = async () => {
  await execute(() => apiClient.generatePuzzle({ topic: 'Science' }));
};
```

### `useMultiAPI<T>()`

A hook for managing multiple API calls with individual state tracking.

**Returns:**
```typescript
{
  states: Record<string, ApiState<T>>;
  execute: (key: string, apiCall: () => Promise<T>) => Promise<T | null>;
  getState: (key: string) => ApiState<T>;
  reset: (key: string) => void;
  resetAll: () => void;
}
```

**Example:**
```typescript
const { execute, getState } = useMultiAPI<SolveResponse>();

await execute('word-1-across', () => 
  apiClient.solveWord(puzzleId, { clue_number: 1, direction: 'across' })
);

const wordState = getState('word-1-across');
```

### `usePuzzle()`

A hook for managing puzzle state and user interactions.

**Returns:**
```typescript
{
  // State
  puzzle: Puzzle | null;
  userCells: Cell[];
  selectedCell: { row: number; col: number } | null;
  currentDirection: Direction;
  activeClue: { number: number; direction: Direction } | null;
  cellStates: CellState[];
  gridState: GridState;
  isComplete: boolean;
  completionPercentage: number;

  // Actions
  loadPuzzle: (puzzle: Puzzle) => void;
  clearPuzzle: () => void;
  setCellValue: (row: number, col: number, value: string | null) => void;
  clearCell: (row: number, col: number) => void;
  resetGrid: () => void;
  selectCell: (row: number, col: number, direction?: Direction) => void;
  toggleDirection: () => void;
  selectClue: (clue: Clue) => void;
  setActiveClue: (clue: { number: number; direction: Direction } | null) => void;
}
```

**Example:**
```typescript
const {
  puzzle,
  userCells,
  selectedCell,
  loadPuzzle,
  setCellValue,
  selectCell,
} = usePuzzle();

// Load a puzzle
loadPuzzle(puzzleData);

// Select a cell
selectCell(0, 0, 'across');

// Set a cell value
setCellValue(0, 0, 'A');
```

---

## Utility Functions

### Grid Utilities (`src/utils/grid.ts`)

**Coordinate Conversion:**
- `coordsToIndex(row, col, gridSize)`: Convert 2D coordinates to 1D index
- `indexToCoords(index, gridSize)`: Convert 1D index to 2D coordinates
- `isValidCoord(row, col, gridSize)`: Check if coordinates are within bounds

**Cell Operations:**
- `getCellAt(cells, row, col)`: Get cell at specific coordinates
- `getWordCells(cells, clue)`: Get all cells for a word
- `getWordText(cells)`: Get word text from cells
- `isWordComplete(cells)`: Check if word is complete

**Navigation:**
- `getNextCell(row, col, direction, gridSize)`: Get next cell in direction
- `getPreviousCell(row, col, direction)`: Get previous cell in direction
- `findClueForCell(cells, clues, row, col)`: Find clue containing a cell
- `getIntersectingClues(cells, cluesAcross, cluesDown, row, col)`: Get intersecting clues

**Grid Management:**
- `createEmptyGrid(gridSize)`: Create empty grid
- `cloneCells(cells)`: Clone cell array
- `updateCell(cells, row, col, value)`: Update specific cell

### Validation Utilities (`src/utils/validation.ts`)

**Input Validation:**
- `isValidLetter(input)`: Check if input is a single uppercase letter
- `sanitizeLetter(input)`: Sanitize input to uppercase letter or null
- `isLetterKey(key)`: Check if key is a letter
- `isNavigationKey(key)`: Check if key is a navigation key
- `isDeletionKey(key)`: Check if key is a deletion key

**Form Validation:**
- `validateTopic(topic)`: Validate topic string
- `validateGridSize(size)`: Validate grid size
- `validateWordCount(minWords, maxWords)`: Validate word count range
- `validatePuzzleRequest(topic, gridSize, minWords, maxWords)`: Validate complete puzzle request

### Keyboard Utilities (`src/utils/keyboard.ts`)

**Navigation:**
- `getNextCellFromArrow(row, col, key, gridSize, blockedCells)`: Get next cell from arrow key
- `getNextCellInWord(row, col, direction, gridSize, blockedCells)`: Get next cell in word
- `getPreviousCellInWord(row, col, direction, gridSize, blockedCells)`: Get previous cell in word
- `toggleDirection(currentDirection)`: Toggle between across and down

**Word Operations:**
- `getWordStartCell(startRow, startCol)`: Get first cell of word
- `getWordEndCell(startRow, startCol, length, direction)`: Get last cell of word
- `isCellInWord(row, col, startRow, startCol, length, direction)`: Check if cell is in word
- `getWordCellPositions(startRow, startCol, length, direction)`: Get all cell positions for word
- `findNextEmptyCell(startRow, startCol, length, direction, filledCells)`: Find next empty cell in word

---

## Usage Examples

### Complete Puzzle Generation Flow

```typescript
import { apiClient } from '@services/api';
import { useAPI } from '@hooks/useAPI';
import { usePuzzle } from '@hooks/usePuzzle';

function PuzzleGenerator() {
  const { data, loading, error, execute } = useAPI<PuzzleGenerateResponse>();
  const { loadPuzzle } = usePuzzle();

  const handleGenerate = async () => {
    const response = await execute(() =>
      apiClient.generatePuzzle({
        topic: 'Science',
        grid_size: 8,
        difficulty: 'medium',
      })
    );

    if (response?.success && response.puzzle) {
      loadPuzzle(response.puzzle);
    }
  };

  return (
    <button onClick={handleGenerate} disabled={loading}>
      {loading ? 'Generating...' : 'Generate Puzzle'}
    </button>
  );
}
```

### Cell Input Handling

```typescript
import { usePuzzle } from '@hooks/usePuzzle';
import { sanitizeLetter } from '@utils/validation';
import { getNextCellInWord } from '@utils/keyboard';

function GridCell({ row, col }: { row: number; col: number }) {
  const { setCellValue, selectCell, currentDirection } = usePuzzle();

  const handleKeyDown = (e: React.KeyboardEvent) => {
    const letter = sanitizeLetter(e.key);
    if (letter) {
      setCellValue(row, col, letter);
      
      // Move to next cell
      const next = getNextCellInWord(row, col, currentDirection, 8, new Set());
      if (next) {
        selectCell(next.row, next.col);
      }
    }
  };

  return <input onKeyDown={handleKeyDown} />;
}
```

### Validation Flow

```typescript
import { apiClient } from '@services/api';
import { usePuzzle } from '@hooks/usePuzzle';

function ValidateButton({ puzzleId }: { puzzleId: string }) {
  const { userCells } = usePuzzle();

  const handleValidate = async () => {
    const result = await apiClient.validateSolution(puzzleId, {
      cells: userCells,
    });

    if (result.is_valid) {
      alert('Congratulations! Puzzle solved correctly!');
    } else {
      alert(`${result.correct_count}/${result.total_count} correct (${Math.round(result.accuracy * 100)}%)`);
    }
  };

  return <button onClick={handleValidate}>Validate Solution</button>;
}
```

---

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## TypeScript Configuration

The project uses strict TypeScript configuration with path aliases:

```json
{
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@services/*": ["./src/services/*"],
      "@models/*": ["./src/types/*"],
      "@utils/*": ["./src/utils/*"]
    }
  }
}
```

---

## Best Practices

1. **Always use type imports**: Use `import type` for type-only imports to improve build performance
2. **Handle errors gracefully**: Always wrap API calls in try-catch blocks
3. **Use custom hooks**: Leverage `useAPI` and `usePuzzle` for consistent state management
4. **Validate user input**: Use validation utilities before sending data to the API
5. **Sanitize cell values**: Always use `sanitizeLetter` for user input
6. **Check coordinates**: Use `isValidCoord` before accessing cells
7. **Clone state**: Use `cloneCells` when modifying cell arrays to maintain immutability

---

## Testing

To verify the types and API client:

```bash
# Run TypeScript compilation check
npm run build

# Run verification script
node verify_types_and_api.js
```

---

## Next Steps

With the TypeScript types and API client in place, you can now:

1. Build UI components (Grid, Cell, ClueList)
2. Implement keyboard navigation
3. Add puzzle generation interface
4. Implement AI-assisted solving features
5. Add validation and feedback UI

---

## Support

For issues or questions about the types and API client, refer to:
- Backend API documentation: `backend/api/README.md`
- Backend schemas: `backend/api/schemas.py`
- Frontend README: `frontend/README.md`
