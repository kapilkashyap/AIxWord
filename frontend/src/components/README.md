# Grid UI Components

This directory contains the interactive crossword grid components for AIxWord.

## Components

### CrosswordGrid

The main grid component that renders the complete crossword puzzle with interactive cells.

**Features:**
- Renders an NxN grid of cells based on puzzle data
- Manages cell selection and keyboard navigation
- Supports both "across" and "down" word directions
- Provides visual feedback for active words, completed cells, and errors
- Handles keyboard input (letters, arrow keys, backspace, delete, space, tab)
- Integrates with parent state management

**Props:**
```typescript
interface CrosswordGridProps {
  cells: Cell[];                    // Array of all cells in the grid
  gridSize: number;                 // Grid size (NxN)
  cluesAcross: Clue[];             // Across clues
  cluesDown: Clue[];               // Down clues
  selectedCell: { row: number; col: number } | null;  // Currently selected cell
  currentDirection: Direction;      // Current word direction ('across' | 'down')
  activeClue: { number: number; direction: Direction } | null;  // Active clue
  onCellSelect: (row: number, col: number) => void;  // Cell selection callback
  onCellChange: (cells: Cell[]) => void;  // Cell value change callback
  onDirectionChange: (direction: Direction) => void;  // Direction change callback
  onActiveClueChange: (clue: { number: number; direction: Direction } | null) => void;
  cellSize?: number;               // Cell size in pixels (default: 50)
  readOnly?: boolean;              // Whether grid is read-only (default: false)
}
```

**Usage:**
```tsx
import { CrosswordGrid } from './components';

<CrosswordGrid
  cells={puzzleCells}
  gridSize={8}
  cluesAcross={acrossClues}
  cluesDown={downClues}
  selectedCell={selectedCell}
  currentDirection={direction}
  activeClue={activeClue}
  onCellSelect={handleCellSelect}
  onCellChange={handleCellChange}
  onDirectionChange={handleDirectionChange}
  onActiveClueChange={handleActiveClueChange}
/>
```

### GridCell

Individual cell component that represents a single square in the crossword grid.

**Features:**
- Displays cell number (if cell starts a word)
- Shows cell value (letter)
- Renders blocked cells (black squares)
- Handles click events
- Manages keyboard input
- Provides visual states (selected, active word, completed, error)
- Auto-focuses when selected

**Props:**
```typescript
interface GridCellProps {
  cell: CellState;                 // Cell state with visual properties
  onClick: (row: number, col: number) => void;  // Click handler
  onInput: (row: number, col: number, value: string) => void;  // Input handler
  shouldFocus: boolean;            // Whether cell should receive focus
  cellSize?: number;               // Cell size in pixels (default: 50)
}
```

**Note:** GridCell is typically used internally by CrosswordGrid and not directly by consumers.

## Keyboard Navigation

The grid supports comprehensive keyboard navigation:

| Key | Action |
|-----|--------|
| **Arrow Keys** | Navigate between cells (changes direction automatically) |
| **Letters (A-Z)** | Enter letter in current cell and advance to next cell |
| **Backspace** | Clear current cell and move to previous cell |
| **Delete** | Clear current cell without moving |
| **Space** | Toggle between across/down directions |
| **Tab** | Move to next word (Shift+Tab for previous word) |

## Visual States

Cells have different visual states to provide feedback:

- **Normal**: White background, gray border
- **Hover**: Light gray background (on non-blocked cells)
- **Selected**: Gold background with orange border
- **Active Word**: Light yellow background (cells in current word)
- **Completed**: Light green background (correct answer)
- **Error**: Light red background with shake animation (incorrect answer)
- **Blocked**: Black background (non-interactive)

## Styling

The components use CSS classes that can be customized:

- `.crossword-grid-container` - Main container
- `.crossword-grid` - Grid layout
- `.grid-cell` - Individual cell
- `.grid-cell--selected` - Selected cell state
- `.grid-cell--active-word` - Active word state
- `.grid-cell--completed` - Completed state
- `.grid-cell--error` - Error state
- `.grid-cell--blocked` - Blocked cell
- `.grid-cell__number` - Cell number label
- `.grid-cell__input` - Input field
- `.direction-indicator` - Direction display

## Accessibility

The components include accessibility features:

- ARIA labels for screen readers
- Keyboard navigation support
- High contrast mode support
- Reduced motion support
- Focus visible indicators
- Semantic HTML structure

## Responsive Design

The grid adapts to different screen sizes:

- Smaller cell sizes on mobile devices
- Adjusted font sizes for readability
- Touch-friendly interaction areas
- Responsive direction indicator

## Example

See `CrosswordGrid.example.tsx` for a complete working example of how to integrate the grid component with state management.

## Integration with State Management

The CrosswordGrid component is designed to work with external state management. It receives state as props and communicates changes through callbacks. This allows it to integrate with:

- React hooks (useState, useReducer)
- Context API
- State management libraries (Redux, Zustand, etc.)
- Custom hooks (like `usePuzzle`)

Example with custom hook:
```tsx
import { usePuzzle } from '../hooks/usePuzzle';
import { CrosswordGrid } from './components';

function PuzzleView() {
  const {
    puzzle,
    selectedCell,
    currentDirection,
    activeClue,
    selectCell,
    updateCells,
    changeDirection,
    setActiveClue,
  } = usePuzzle();

  if (!puzzle) return <div>No puzzle loaded</div>;

  return (
    <CrosswordGrid
      cells={puzzle.cells}
      gridSize={puzzle.grid_size}
      cluesAcross={puzzle.clues_across}
      cluesDown={puzzle.clues_down}
      selectedCell={selectedCell}
      currentDirection={currentDirection}
      activeClue={activeClue}
      onCellSelect={selectCell}
      onCellChange={updateCells}
      onDirectionChange={changeDirection}
      onActiveClueChange={setActiveClue}
    />
  );
}
```

## Testing

The components are designed to be testable:

- Pure functional components
- Props-based state management
- Callback-based event handling
- No direct DOM manipulation
- Isolated business logic in utility functions

Example test structure:
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { CrosswordGrid } from './CrosswordGrid';

describe('CrosswordGrid', () => {
  it('renders grid with correct size', () => {
    // Test implementation
  });

  it('handles cell selection', () => {
    // Test implementation
  });

  it('handles keyboard navigation', () => {
    // Test implementation
  });
});
```

## Performance Considerations

- Uses React.useMemo for expensive computations
- Efficient cell state calculations
- Optimized re-renders with useCallback
- Minimal DOM updates
- CSS transitions for smooth animations

## Future Enhancements

Potential improvements for future versions:

- Touch gesture support (swipe to navigate)
- Undo/redo functionality
- Cell highlighting for intersecting words
- Animation for AI-filled cells
- Customizable color themes
- Grid zoom controls
- Print-optimized layout
- Mobile-specific optimizations
