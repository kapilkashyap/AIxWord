# Clue Display Components

This document provides comprehensive documentation for the Clue Display components in the AIxWord application.

## Overview

The Clue Display components provide an interactive interface for displaying crossword puzzle clues with features like:
- Organized display of across and down clues
- Visual feedback for active and completed clues
- Progress tracking for partially filled words
- Click-to-select functionality to jump to grid positions
- Multiple layout options (tabs or split view)
- Overall puzzle progress tracking

## Components

### ClueList

The main container component that displays all clues for the crossword puzzle.

#### Props

```typescript
interface ClueListProps {
  cluesAcross: Clue[];           // Across clues
  cluesDown: Clue[];             // Down clues
  cells: Cell[];                 // All cells in the grid (for progress tracking)
  activeClue: {                  // Currently active clue
    number: number;
    direction: Direction;
  } | null;
  onClueClick: (clue: Clue) => void;  // Callback when a clue is clicked
  showAnswers?: boolean;         // Whether to show answers (solution mode)
  layout?: 'tabs' | 'split';     // Layout mode
  className?: string;            // Optional CSS class name
}
```

#### Features

- **Overall Progress Bar**: Shows completion percentage across all clues
- **Two Layout Modes**:
  - `tabs`: Tabbed interface switching between across and down clues
  - `split`: Side-by-side display of both directions
- **Auto-scroll**: Automatically scrolls to the active clue
- **Progress Tracking**: Shows completed vs. total clues for each direction
- **Empty State**: Graceful handling when no clues are available

#### Usage Example

```tsx
import { ClueList } from './components';

function MyPuzzle() {
  const [activeClue, setActiveClue] = useState(null);
  
  const handleClueClick = (clue: Clue) => {
    // Jump to the clue's starting position in the grid
    setSelectedCell({ row: clue.start_row, col: clue.start_col });
    setCurrentDirection(clue.direction);
    setActiveClue({ number: clue.number, direction: clue.direction });
  };

  return (
    <ClueList
      cluesAcross={cluesAcross}
      cluesDown={cluesDown}
      cells={cells}
      activeClue={activeClue}
      onClueClick={handleClueClick}
      layout="tabs"
    />
  );
}
```

### ClueItem

Individual clue component that displays a single clue with interactive features.

#### Props

```typescript
interface ClueItemProps {
  clue: Clue;                    // The clue data
  isActive: boolean;             // Whether this clue is currently active
  isCompleted: boolean;          // Whether this clue is completed
  currentAnswer?: string;        // Current filled letters for progress display
  onClick: (clue: Clue) => void; // Callback when clue is clicked
  showAnswer?: boolean;          // Whether to show the answer
  className?: string;            // Optional CSS class name
}
```

#### Features

- **Visual States**:
  - Default: Normal appearance
  - Active: Highlighted with blue background and indicator
  - Completed: Green background with checkmark
- **Progress Display**: Shows partially filled letters (e.g., "P_TH__")
- **Answer Display**: Shows full answer when completed or in solution mode
- **Keyboard Accessible**: Supports Enter and Space key activation
- **ARIA Labels**: Proper accessibility attributes

#### Usage Example

```tsx
import { ClueItem } from './components';

function MyClueList() {
  const isCompleted = currentAnswer === clue.answer;
  
  return (
    <ClueItem
      clue={clue}
      isActive={activeClue?.number === clue.number}
      isCompleted={isCompleted}
      currentAnswer={currentAnswer}
      onClick={handleClueClick}
    />
  );
}
```

## Integration with Grid Component

The Clue Display components are designed to work seamlessly with the Grid component:

```tsx
import { Grid, ClueList } from './components';

function CrosswordPuzzle() {
  const [cells, setCells] = useState<Cell[]>([...]);
  const [selectedCell, setSelectedCell] = useState(null);
  const [currentDirection, setCurrentDirection] = useState<Direction>('across');
  const [activeClue, setActiveClue] = useState(null);

  const handleClueClick = (clue: Clue) => {
    // Jump to clue position in grid
    setSelectedCell({ row: clue.start_row, col: clue.start_col });
    setCurrentDirection(clue.direction);
    setActiveClue({ number: clue.number, direction: clue.direction });
  };

  return (
    <div style={{ display: 'flex', gap: '2rem' }}>
      {/* Grid on the left */}
      <Grid
        cells={cells}
        gridSize={8}
        cluesAcross={cluesAcross}
        cluesDown={cluesDown}
        selectedCell={selectedCell}
        currentDirection={currentDirection}
        activeClue={activeClue}
        onCellSelect={setSelectedCell}
        onCellChange={setCells}
        onDirectionChange={setCurrentDirection}
        onActiveClueChange={setActiveClue}
      />

      {/* Clues on the right */}
      <ClueList
        cluesAcross={cluesAcross}
        cluesDown={cluesDown}
        cells={cells}
        activeClue={activeClue}
        onClueClick={handleClueClick}
      />
    </div>
  );
}
```

## Styling

Both components use CSS Modules for scoped styling:

- `ClueItem.module.css`: Styles for individual clue items
- `ClueList.module.css`: Styles for the clue list container

### Customization

You can customize the appearance by:

1. **Using className prop**: Pass custom CSS classes
2. **CSS Variables**: Override CSS custom properties
3. **Modifying CSS Modules**: Edit the module files directly

### Responsive Design

Both components are fully responsive:
- **Desktop**: Full-featured layout with all visual elements
- **Tablet**: Adjusted spacing and font sizes
- **Mobile**: Compact layout optimized for small screens

### Accessibility

The components follow WCAG 2.1 AA guidelines:
- **Keyboard Navigation**: Full keyboard support
- **ARIA Labels**: Proper semantic markup
- **Focus Management**: Clear focus indicators
- **Color Contrast**: Meets contrast requirements
- **Screen Reader Support**: Descriptive labels and roles
- **High Contrast Mode**: Adapts to user preferences
- **Reduced Motion**: Respects prefers-reduced-motion

## Progress Tracking

The ClueList component automatically tracks progress by:

1. Comparing current cell values with clue answers
2. Calculating completion percentage
3. Displaying progress indicators for each direction
4. Showing overall puzzle completion

### Progress Display

- **Overall Progress Bar**: Visual bar showing total completion
- **Section Progress**: Completed/total count for each direction
- **Individual Progress**: Partially filled letters for each clue
- **Completion Indicators**: Checkmarks for completed clues

## Layout Modes

### Tabs Layout (Default)

- Tabbed interface with "Across" and "Down" tabs
- Only one direction visible at a time
- Automatically switches to active clue's tab
- Better for smaller screens

### Split Layout

- Both directions visible simultaneously
- Scrollable sections for each direction
- Better for larger screens
- Easier comparison between clues

## State Management

The components are designed to be controlled:

```tsx
// Parent component manages state
const [activeClue, setActiveClue] = useState(null);

// ClueList receives state and callbacks
<ClueList
  activeClue={activeClue}
  onClueClick={(clue) => {
    // Update parent state
    setActiveClue({ number: clue.number, direction: clue.direction });
  }}
/>
```

## Performance Considerations

- **Memoization**: Uses React.useMemo for expensive computations
- **Auto-scroll**: Smooth scrolling with behavior: 'smooth'
- **Efficient Updates**: Only re-renders when necessary
- **Virtual Scrolling**: Consider for puzzles with 100+ clues

## Testing

Example test cases:

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ClueList } from './ClueList';

test('displays all clues', () => {
  render(<ClueList cluesAcross={clues} cluesDown={[]} ... />);
  expect(screen.getByText('First clue')).toBeInTheDocument();
});

test('highlights active clue', () => {
  render(<ClueList activeClue={{ number: 1, direction: 'across' }} ... />);
  const clue = screen.getByTestId('clue-1-across');
  expect(clue).toHaveAttribute('data-active', 'true');
});

test('calls onClueClick when clue is clicked', () => {
  const handleClick = jest.fn();
  render(<ClueList onClueClick={handleClick} ... />);
  fireEvent.click(screen.getByTestId('clue-1-across'));
  expect(handleClick).toHaveBeenCalledWith(expect.objectContaining({ number: 1 }));
});
```

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Full support

## Future Enhancements

Potential improvements:
- Search/filter functionality
- Clue hints and definitions
- Difficulty indicators
- Time tracking per clue
- Clue history/undo
- Clue bookmarking
- Export clues to PDF

## Related Components

- **Grid**: Main crossword grid component
- **Cell**: Individual grid cell component
- **GridCell**: Alternative cell component

## See Also

- [Grid Component README](./README.md)
- [Type Definitions](../types/puzzle.ts)
- [Example Usage](./ClueList.example.tsx)
