# AI Assistance Integration Guide

## Overview

This guide explains how to integrate the AI Assistance Hook into your application. The hook provides complete AI-powered solving features including word solving, puzzle solving, and hint generation.

## Quick Start

### Option 1: Use PuzzleContainerWithAI (Recommended)

The easiest way to get started is to use the pre-built `PuzzleContainerWithAI` component which has everything integrated:

```typescript
// In your App.tsx or main component
import { PuzzleContainerWithAI } from './components/PuzzleContainerWithAI';

function App() {
  return (
    <div className="App">
      <PuzzleContainerWithAI />
    </div>
  );
}
```

This component includes:
- ✅ Puzzle generation form
- ✅ Interactive grid with clues
- ✅ Manual solving controls
- ✅ AI assistance panel
- ✅ All modals and animations
- ✅ Error handling

### Option 2: Custom Integration

If you need more control, integrate the hook manually:

```typescript
import React from 'react';
import { usePuzzle, useAIAssistance } from './hooks';
import { AIAssistancePanel, HintModal, ConfirmationDialog, SolutionAnimation } from './components';

function MyCustomPuzzle() {
  const { puzzle, activeClue, setCellValue } = usePuzzle();
  
  const aiAssistance = useAIAssistance(
    puzzle?.puzzle_id || null,
    activeClue,
    setCellValue
  );

  return (
    <div>
      {/* Your puzzle UI */}
      
      {/* AI Assistance Panel */}
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

      {/* Modals */}
      {aiAssistance.hintModal && (
        <HintModal
          isOpen={aiAssistance.hintModal.isVisible}
          hint={aiAssistance.hintModal.hint}
          hintType={aiAssistance.hintModal.hintType}
          revealedLetter={aiAssistance.hintModal.revealedLetter}
          position={aiAssistance.hintModal.position}
          clueInfo={aiAssistance.hintModal.clueInfo}
          onClose={aiAssistance.closeHintModal}
        />
      )}

      {aiAssistance.confirmationDialog && (
        <ConfirmationDialog
          isOpen={aiAssistance.confirmationDialog.isVisible}
          title={aiAssistance.confirmationDialog.title}
          message={aiAssistance.confirmationDialog.message}
          onConfirm={aiAssistance.confirmationDialog.onConfirm}
          onCancel={aiAssistance.confirmationDialog.onCancel}
        />
      )}

      {aiAssistance.solutionAnimation && (
        <SolutionAnimation
          isActive={aiAssistance.solutionAnimation.isActive}
          type={aiAssistance.solutionAnimation.type}
          progress={
            (aiAssistance.solutionAnimation.currentStep /
              aiAssistance.solutionAnimation.cells.length) * 100
          }
        />
      )}
    </div>
  );
}
```

## Features

### 1. Solve Word
AI solves the currently selected word with confirmation dialog:

```typescript
// Trigger solve word (shows confirmation first)
aiAssistance.showSolveWordConfirmation();

// Check if solving is in progress
if (aiAssistance.isSolvingWord) {
  // Show loading state
}

// Handle errors
if (aiAssistance.solveWordError) {
  // Display error message
}
```

### 2. Solve Puzzle
AI solves the entire puzzle with confirmation dialog:

```typescript
// Trigger solve puzzle (shows confirmation first)
aiAssistance.showSolvePuzzleConfirmation();

// Check if solving is in progress
if (aiAssistance.isSolvingPuzzle) {
  // Show loading state
}
```

### 3. Get Hint
Get hints with different types:

```typescript
// Get a definition hint
aiAssistance.getHint('definition');

// Get a letter reveal hint
aiAssistance.getHint('letter');

// Get a synonym hint
aiAssistance.getHint('synonym');

// Check if getting hint
if (aiAssistance.isGettingHint) {
  // Show loading state
}
```

## Components

### AIAssistancePanel
Main control panel with three buttons:
- Solve Word (requires active clue)
- Solve Puzzle
- Get Hint (requires active clue)

### HintModal
Displays hints in a modal dialog with:
- Hint text
- Revealed letter (for letter hints)
- Close button

### ConfirmationDialog
Shows before destructive actions:
- Solve word confirmation
- Solve puzzle confirmation

### SolutionAnimation
Overlay showing progress when AI is solving:
- Animated progress bar
- Status message
- Cell-by-cell animation

## Error Handling

The hook provides error states for each operation:

```typescript
// Display errors
{aiAssistance.solveWordError && (
  <div className="error">
    {aiAssistance.solveWordError}
    <button onClick={aiAssistance.clearErrors}>Dismiss</button>
  </div>
)}

{aiAssistance.solvePuzzleError && (
  <div className="error">{aiAssistance.solvePuzzleError}</div>
)}

{aiAssistance.hintError && (
  <div className="error">{aiAssistance.hintError}</div>
)}

// Clear all errors at once
aiAssistance.clearErrors();
```

## Animation Behavior

### Word Solving
- Letters appear one at a time (150ms delay)
- Progress shown in overlay
- Auto-closes when complete

### Puzzle Solving
- Letters appear in batches of 3 (100ms delay)
- Faster than word solving
- Progress percentage shown

## Best Practices

1. **Always check for active clue** before enabling word-specific actions
2. **Disable all actions** when any operation is in progress
3. **Clear errors** when component unmounts or puzzle changes
4. **Provide visual feedback** for loading states
5. **Show confirmation dialogs** for destructive actions

## Backend Requirements

Ensure these API endpoints are available:

- `POST /api/puzzles/{puzzle_id}/solve-word`
- `POST /api/puzzles/{puzzle_id}/solve`
- `POST /api/puzzles/{puzzle_id}/hint`

## Testing

Mock the API client in tests:

```typescript
jest.mock('./services/api', () => ({
  apiClient: {
    solveWord: jest.fn().mockResolvedValue({
      success: true,
      updated_cells: [/* mock cells */],
    }),
    solvePuzzle: jest.fn().mockResolvedValue({
      success: true,
      updated_cells: [/* mock cells */],
    }),
    getHint: jest.fn().mockResolvedValue({
      success: true,
      hint: 'Mock hint',
      hint_type: 'definition',
    }),
  },
}));
```

## Examples

See `frontend/src/hooks/useAIAssistance.example.tsx` for complete working examples.

## Troubleshooting

**Q: Animations not playing?**
A: Ensure `setCellValue` is properly updating the grid state.

**Q: Confirmation dialogs not showing?**
A: Check that modal components are rendered in your component tree.

**Q: Hints not displaying?**
A: Verify `activeClue` is set when requesting hints.

**Q: API errors?**
A: Check browser console and verify backend endpoints are accessible.

## Next Steps

1. Replace `PuzzleContainer` with `PuzzleContainerWithAI` in your App
2. Test all three AI features (solve word, solve puzzle, get hint)
3. Customize styling to match your design
4. Add analytics tracking for AI feature usage
5. Implement undo/redo for AI solutions (future enhancement)
