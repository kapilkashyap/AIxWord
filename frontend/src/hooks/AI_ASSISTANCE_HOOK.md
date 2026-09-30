# AI Assistance Hook (`useAIAssistance`)

## Overview

The `useAIAssistance` hook provides a complete solution for integrating AI-powered solving assistance into the crossword puzzle application. It manages state, API calls, animations, and user interactions for three core AI features:

1. **Solve Word** - AI solves the currently selected word
2. **Solve Puzzle** - AI solves the entire puzzle
3. **Get Hint** - AI provides hints for the selected word

## Features

### Core Functionality
- ✅ AI-powered word solving with intersection awareness
- ✅ Full puzzle solving with animated cell filling
- ✅ Multiple hint types (letter reveal, definition, synonym)
- ✅ Confirmation dialogs for destructive actions
- ✅ Animated solution display
- ✅ Comprehensive error handling
- ✅ Loading states for all operations

### User Experience
- ✅ Smooth animations when filling cells
- ✅ Confirmation before overwriting user input
- ✅ Modal display for hints with options
- ✅ Progress indicators during AI operations
- ✅ Clear error messages with dismiss actions

## Installation

The hook is already integrated into the project. Import it from the hooks module:

```typescript
import { useAIAssistance } from '../hooks/useAIAssistance';
```

## Basic Usage

```typescript
import React from 'react';
import { useAIAssistance } from '../hooks/useAIAssistance';
import { usePuzzle } from '../hooks/usePuzzle';

function MyPuzzleComponent() {
  const { puzzle, activeClue, setCellValue } = usePuzzle();
  
  const aiAssistance = useAIAssistance(
    puzzle?.puzzle_id || null,
    activeClue,
    setCellValue
  );

  return (
    <div>
      <button 
        onClick={aiAssistance.showSolveWordConfirmation}
        disabled={!activeClue || aiAssistance.isSolvingWord}
      >
        Solve Word
      </button>
      
      <button 
        onClick={aiAssistance.showSolvePuzzleConfirmation}
        disabled={aiAssistance.isSolvingPuzzle}
      >
        Solve Puzzle
      </button>
      
      <button 
        onClick={() => aiAssistance.getHint('definition')}
        disabled={!activeClue || aiAssistance.isGettingHint}
      >
        Get Hint
      </button>
    </div>
  );
}
```

## API Reference

### Hook Signature

```typescript
function useAIAssistance(
  puzzleId: string | null,
  activeClue: { number: number; direction: 'across' | 'down' } | null,
  setCellValue: (row: number, col: number, value: string | null) => void
): AIAssistanceReturn
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `puzzleId` | `string \| null` | Current puzzle ID (required for API calls) |
| `activeClue` | `{ number: number; direction: 'across' \| 'down' } \| null` | Currently selected clue |
| `setCellValue` | `(row, col, value) => void` | Function to update cell values in the grid |

### Return Value

The hook returns an object with the following properties:

#### Loading States

| Property | Type | Description |
|----------|------|-------------|
| `isSolvingWord` | `boolean` | True when solving a word is in progress |
| `isSolvingPuzzle` | `boolean` | True when solving the puzzle is in progress |
| `isGettingHint` | `boolean` | True when getting a hint is in progress |
| `isAnyOperationInProgress` | `boolean` | True if any AI operation is active |

#### Error States

| Property | Type | Description |
|----------|------|-------------|
| `solveWordError` | `string \| null` | Error message from solve word operation |
| `solvePuzzleError` | `string \| null` | Error message from solve puzzle operation |
| `hintError` | `string \| null` | Error message from hint generation |

#### Modal States

| Property | Type | Description |
|----------|------|-------------|
| `hintModal` | `HintModalState \| null` | State for hint modal display |
| `confirmationDialog` | `ConfirmationDialogState \| null` | State for confirmation dialog |
| `solutionAnimation` | `SolutionAnimationState \| null` | State for solution animation |

#### Actions

| Method | Signature | Description |
|--------|-----------|-------------|
| `showSolveWordConfirmation` | `() => void` | Show confirmation dialog for solving word |
| `showSolvePuzzleConfirmation` | `() => void` | Show confirmation dialog for solving puzzle |
| `getHint` | `(hintType?: HintType) => Promise<void>` | Get a hint for the active word |
| `closeHintModal` | `() => void` | Close the hint modal |
| `closeConfirmationDialog` | `() => void` | Close the confirmation dialog |
| `clearErrors` | `() => void` | Clear all error messages |

## State Types

### HintModalState

```typescript
interface HintModalState {
  isVisible: boolean;
  hintText: string;
  hintType: HintType;
  revealedLetter: string | null;
  position: number | null;
  clueNumber: number;
  direction: 'across' | 'down';
}
```

### ConfirmationDialogState

```typescript
interface ConfirmationDialogState {
  isVisible: boolean;
  title: string;
  message: string;
  actionType: 'solve-word' | 'solve-puzzle';
  onConfirm: () => void;
  onCancel: () => void;
}
```

### SolutionAnimationState

```typescript
interface SolutionAnimationState {
  isActive: boolean;
  type: 'word' | 'puzzle';
  cells: Array<{ row: number; col: number; value: string }>;
  currentStep: number;
}
```

## Integration with UI Components

The hook is designed to work seamlessly with the AI assistance UI components:

### AIAssistancePanel

```typescript
<AIAssistancePanel
  hasPuzzle={!!puzzle}
  activeClue={activeClue}
  isSolvingWord={aiAssistance.isSolvingWord}
  isSolvingPuzzle={aiAssistance.isSolvingPuzzle}
  isGettingHint={aiAssistance.isGettingHint}
  onSolveWord={aiAssistance.showSolveWordConfirmation}
  onSolvePuzzle={aiAssistance.showSolvePuzzleConfirmation}
  onGetHint={() => aiAssistance.getHint('definition')}
/>
```

### HintModal

```typescript
{aiAssistance.hintModal && (
  <HintModal
    isOpen={aiAssistance.hintModal.isVisible}
    hintText={aiAssistance.hintModal.hintText}
    hintType={aiAssistance.hintModal.hintType}
    revealedLetter={aiAssistance.hintModal.revealedLetter}
    position={aiAssistance.hintModal.position}
    clueNumber={aiAssistance.hintModal.clueNumber}
    direction={aiAssistance.hintModal.direction}
    onClose={() => aiAssistance.closeHintModal()}
    onRequestAnotherHint={(type) => aiAssistance.getHint(type)}
  />
)}
```

### ConfirmationDialog

```typescript
{aiAssistance.confirmationDialog && (
  <ConfirmationDialog
    isOpen={aiAssistance.confirmationDialog.isVisible}
    title={aiAssistance.confirmationDialog.title}
    message={aiAssistance.confirmationDialog.message}
    confirmLabel="Yes, Solve"
    cancelLabel="Cancel"
    variant={
      aiAssistance.confirmationDialog.actionType === 'solve-puzzle'
        ? 'warning'
        : 'info'
    }
    onConfirm={aiAssistance.confirmationDialog.onConfirm}
    onCancel={aiAssistance.confirmationDialog.onCancel}
  />
)}
```

### SolutionAnimation

```typescript
{aiAssistance.solutionAnimation && (
  <SolutionAnimation
    isActive={aiAssistance.solutionAnimation.isActive}
    type={aiAssistance.solutionAnimation.type}
    progress={
      aiAssistance.solutionAnimation.cells.length > 0
        ? (aiAssistance.solutionAnimation.currentStep /
            aiAssistance.solutionAnimation.cells.length) * 100
        : 0
    }
    message={
      aiAssistance.solutionAnimation.type === 'word'
        ? 'AI is solving the word...'
        : 'AI is solving the puzzle...'
    }
  />
)}
```

## Hint Types

The hook supports three types of hints:

### 1. Letter Reveal (`'letter'`)
Reveals a single letter from the answer at a random position (preferring middle letters).

```typescript
aiAssistance.getHint('letter');
```

### 2. Alternative Definition (`'definition'`)
Provides an alternative definition or explanation of the answer using AI.

```typescript
aiAssistance.getHint('definition');
```

### 3. Synonym (`'synonym'`)
Provides a synonym or related word to help guess the answer.

```typescript
aiAssistance.getHint('synonym');
```

## Animation Behavior

### Word Solving Animation
- Fills letters one at a time with 150ms delay between each
- Shows progress in the solution animation overlay
- Automatically closes after completion

### Puzzle Solving Animation
- Fills letters in batches of 3 for faster completion
- 100ms delay between batches
- Shows overall progress percentage
- Automatically closes after completion

## Error Handling

The hook provides comprehensive error handling:

```typescript
// Display errors
{aiAssistance.solveWordError && (
  <ErrorMessage
    message={aiAssistance.solveWordError}
    type="error"
    onClose={aiAssistance.clearErrors}
  />
)}

// Errors are automatically set when API calls fail
// Clear all errors at once
aiAssistance.clearErrors();
```

## Best Practices

### 1. Always Check for Active Clue
```typescript
<button
  onClick={aiAssistance.showSolveWordConfirmation}
  disabled={!activeClue || aiAssistance.isSolvingWord}
>
  Solve Word
</button>
```

### 2. Disable Actions During Operations
```typescript
const isDisabled = aiAssistance.isAnyOperationInProgress;
```

### 3. Handle Hint Modal Letter Reveal
```typescript
const handleHintModalClose = (revealLetter: boolean = false) => {
  if (revealLetter && aiAssistance.hintModal) {
    // Update the cell with the revealed letter
    const { revealedLetter, position, clueNumber, direction } = aiAssistance.hintModal;
    // ... update logic
  }
  aiAssistance.closeHintModal();
};
```

### 4. Clear Errors on Component Unmount
```typescript
useEffect(() => {
  return () => {
    aiAssistance.clearErrors();
  };
}, [aiAssistance]);
```

## Complete Example

See `useAIAssistance.example.tsx` for complete working examples including:
- Full integration with all UI components
- Simple integration with minimal UI
- Custom hint type selection
- Programmatic AI assistance

## Dependencies

The hook depends on:
- `apiClient` from `../services/api`
- Type definitions from `../types/puzzle` and `../types/api`
- React hooks (`useState`, `useCallback`)

## Backend API Endpoints

The hook makes calls to the following backend endpoints:

- `POST /api/puzzles/{puzzle_id}/solve-word` - Solve a specific word
- `POST /api/puzzles/{puzzle_id}/solve` - Solve entire puzzle
- `POST /api/puzzles/{puzzle_id}/hint` - Get a hint

Ensure these endpoints are available and properly configured in your backend.

## Testing

When testing components that use this hook, mock the API client:

```typescript
jest.mock('../services/api', () => ({
  apiClient: {
    solveWord: jest.fn(),
    solvePuzzle: jest.fn(),
    getHint: jest.fn(),
  },
}));
```

## Troubleshooting

### Issue: Animations not playing
**Solution**: Ensure `setCellValue` function is properly passed and updates the grid state.

### Issue: Confirmation dialogs not showing
**Solution**: Check that the modal components are rendered in your component tree.

### Issue: Hints not displaying
**Solution**: Verify that `activeClue` is set when requesting hints.

### Issue: API errors
**Solution**: Check browser console for network errors and verify backend endpoints are accessible.

## Future Enhancements

Potential improvements for future versions:
- Configurable animation speeds
- Undo/redo for AI solutions
- Hint history tracking
- AI confidence display
- Progressive hint system (easier hints first)
- Batch hint requests for multiple words

## Related Documentation

- [AI Assistance UI Components](../components/AI_ASSISTANCE_COMPONENTS.md)
- [Puzzle State Management](./usePuzzle.ts)
- [Solving Hook](./useSolving.ts)
- [API Client](../services/api.ts)
