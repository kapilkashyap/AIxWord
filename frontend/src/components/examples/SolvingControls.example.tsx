/**
 * Example usage of SolvingControls component.
 * 
 * This file demonstrates how to integrate the SolvingControls component
 * with the useSolving hook for manual puzzle solving.
 */

import React from 'react';
import { SolvingControls } from './SolvingControls';
import { useSolving } from '../hooks/useSolving';
import type { Puzzle } from '../types/puzzle';

// Example puzzle data
const examplePuzzle: Puzzle = {
  puzzle_id: 'example-1',
  topic: 'Animals',
  grid_size: 8,
  cells: [
    // Row 0
    { row: 0, col: 0, value: null, is_blocked: false, number: 1 },
    { row: 0, col: 1, value: null, is_blocked: false, number: null },
    { row: 0, col: 2, value: null, is_blocked: false, number: null },
    { row: 0, col: 3, value: null, is_blocked: true, number: null },
    { row: 0, col: 4, value: null, is_blocked: false, number: 2 },
    { row: 0, col: 5, value: null, is_blocked: false, number: null },
    { row: 0, col: 6, value: null, is_blocked: false, number: null },
    { row: 0, col: 7, value: null, is_blocked: true, number: null },
    // Additional rows would be defined here...
  ],
  clues_across: [
    {
      number: 1,
      direction: 'across',
      text: 'Feline pet',
      answer: 'CAT',
      start_row: 0,
      start_col: 0,
      length: 3,
    },
    {
      number: 2,
      direction: 'across',
      text: 'Canine pet',
      answer: 'DOG',
      start_row: 0,
      start_col: 4,
      length: 3,
    },
  ],
  clues_down: [
    {
      number: 1,
      direction: 'down',
      text: 'Automobile',
      answer: 'CAR',
      start_row: 0,
      start_col: 0,
      length: 3,
    },
  ],
  word_count: 3,
  fill_rate: 0.3,
  difficulty: 'easy',
  created_at: '2026-09-28T00:00:00Z',
  metadata: {},
};

/**
 * Example 1: Basic usage with useSolving hook
 */
export function BasicSolvingControlsExample() {
  const solving = useSolving();

  // Load example puzzle on mount
  React.useEffect(() => {
    solving.loadPuzzle(examplePuzzle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleClearAll = () => {
    solving.clearAllInput();
    console.log('Cleared all input');
  };

  const handleClearWord = () => {
    if (solving.activeClue) {
      solving.clearWord(solving.activeClue.number, solving.activeClue.direction);
      console.log(`Cleared word ${solving.activeClue.number} ${solving.activeClue.direction}`);
    }
  };

  const handleCheckSolution = () => {
    console.log('Checking solution...');
    console.log('Solving stats:', solving.solvingStats);
    console.log('Completed words:', solving.completedWords);
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '600px' }}>
      <h2>Basic SolvingControls Example</h2>
      <SolvingControls
        hasPuzzle={!!solving.puzzle}
        stats={solving.solvingStats}
        activeClue={solving.activeClue}
        onClearAll={handleClearAll}
        onClearWord={handleClearWord}
        onCheckSolution={handleCheckSolution}
      />
    </div>
  );
}

/**
 * Example 2: With validation state
 */
export function SolvingControlsWithValidationExample() {
  const solving = useSolving();
  const [isValidating, setIsValidating] = React.useState(false);

  React.useEffect(() => {
    solving.loadPuzzle(examplePuzzle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCheckSolution = async () => {
    setIsValidating(true);
    
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    console.log('Validation complete');
    console.log('Stats:', solving.solvingStats);
    
    setIsValidating(false);
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '600px' }}>
      <h2>SolvingControls with Validation</h2>
      <SolvingControls
        hasPuzzle={!!solving.puzzle}
        stats={solving.solvingStats}
        activeClue={solving.activeClue}
        isValidating={isValidating}
        onClearAll={() => solving.clearAllInput()}
        onClearWord={() => {
          if (solving.activeClue) {
            solving.clearWord(solving.activeClue.number, solving.activeClue.direction);
          }
        }}
        onCheckSolution={handleCheckSolution}
      />
    </div>
  );
}

/**
 * Example 3: Complete integration with grid
 */
export function CompleteSolvingExample() {
  const solving = useSolving();

  React.useEffect(() => {
    solving.loadPuzzle(examplePuzzle);
    // Select first clue
    if (examplePuzzle.clues_across.length > 0) {
      solving.selectClue(examplePuzzle.clues_across[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Simulate filling some cells
  const handleFillExample = () => {
    // Fill "CAT"
    solving.setCellValue(0, 0, 'C');
    solving.setCellValue(0, 1, 'A');
    solving.setCellValue(0, 2, 'T');
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '800px' }}>
      <h2>Complete Solving Example</h2>
      
      {/* Demo controls */}
      <div style={{ marginBottom: '1rem' }}>
        <button onClick={handleFillExample}>Fill Example Word (CAT)</button>
      </div>

      {/* Solving stats display */}
      <div style={{ marginBottom: '1rem', padding: '1rem', background: '#f5f5f5', borderRadius: '4px' }}>
        <h3>Current Stats:</h3>
        <ul>
          <li>Filled Cells: {solving.solvingStats.filledCells} / {solving.solvingStats.totalCells}</li>
          <li>Completed Words: {solving.solvingStats.completedWords} / {solving.solvingStats.totalWords}</li>
          <li>Progress: {Math.round(solving.solvingStats.cellsCompletionPercentage)}%</li>
          <li>Fully Complete: {solving.solvingStats.isFullyComplete ? 'Yes' : 'No'}</li>
        </ul>
      </div>

      {/* Completed words list */}
      {solving.completedWords.length > 0 && (
        <div style={{ marginBottom: '1rem', padding: '1rem', background: '#d4edda', borderRadius: '4px' }}>
          <h3>Completed Words:</h3>
          <ul>
            {solving.completedWords.map((word) => (
              <li key={`${word.clue.number}-${word.clue.direction}`}>
                {word.clue.number} {word.clue.direction}: {word.currentText} ({word.clue.text})
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Solving controls */}
      <SolvingControls
        hasPuzzle={!!solving.puzzle}
        stats={solving.solvingStats}
        activeClue={solving.activeClue}
        onClearAll={() => {
          solving.clearAllInput();
          console.log('Cleared all');
        }}
        onClearWord={() => {
          if (solving.activeClue) {
            solving.clearWord(solving.activeClue.number, solving.activeClue.direction);
            console.log('Cleared word');
          }
        }}
        onCheckSolution={() => {
          console.log('Check solution clicked');
          console.log('Stats:', solving.solvingStats);
        }}
      />
    </div>
  );
}

/**
 * Example 4: Custom styling
 */
export function CustomStyledSolvingControlsExample() {
  const solving = useSolving();

  React.useEffect(() => {
    solving.loadPuzzle(examplePuzzle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div style={{ padding: '2rem', maxWidth: '600px' }}>
      <h2>Custom Styled SolvingControls</h2>
      <SolvingControls
        hasPuzzle={!!solving.puzzle}
        stats={solving.solvingStats}
        activeClue={solving.activeClue}
        className="custom-solving-controls"
        onClearAll={() => solving.clearAllInput()}
        onClearWord={() => {
          if (solving.activeClue) {
            solving.clearWord(solving.activeClue.number, solving.activeClue.direction);
          }
        }}
        onCheckSolution={() => console.log('Check solution')}
      />
    </div>
  );
}

// Export all examples
export default {
  BasicSolvingControlsExample,
  SolvingControlsWithValidationExample,
  CompleteSolvingExample,
  CustomStyledSolvingControlsExample,
};
