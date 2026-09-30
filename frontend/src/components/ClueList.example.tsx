/**
 * Example usage of ClueList component.
 * 
 * This file demonstrates how to integrate the ClueList component
 * with the Grid component for a complete crossword puzzle experience.
 * 
 * NOTE: This is an example file for reference. It is not imported by the main app.
 */

import React, { useState } from 'react';
import { Grid } from './Grid';
import { ClueList } from './ClueList';
import type { Cell, Clue, Direction } from '../types/puzzle';

/**
 * Example component showing ClueList and Grid integration.
 */
export const ClueListExample: React.FC = () => {
  // Example puzzle data (8x8 grid with a few words)
  const [cells, setCells] = useState<Cell[]>([
    // Row 0
    { row: 0, col: 0, value: null, is_blocked: false, number: 1 },
    { row: 0, col: 1, value: null, is_blocked: false, number: null },
    { row: 0, col: 2, value: null, is_blocked: false, number: null },
    { row: 0, col: 3, value: null, is_blocked: false, number: null },
    { row: 0, col: 4, value: null, is_blocked: false, number: null },
    { row: 0, col: 5, value: null, is_blocked: false, number: null },
    { row: 0, col: 6, value: null, is_blocked: true, number: null },
    { row: 0, col: 7, value: null, is_blocked: false, number: 2 },
    // Row 1
    { row: 1, col: 0, value: null, is_blocked: false, number: null },
    { row: 1, col: 1, value: null, is_blocked: true, number: null },
    { row: 1, col: 2, value: null, is_blocked: false, number: 3 },
    { row: 1, col: 3, value: null, is_blocked: false, number: null },
    { row: 1, col: 4, value: null, is_blocked: false, number: null },
    { row: 1, col: 5, value: null, is_blocked: false, number: null },
    { row: 1, col: 6, value: null, is_blocked: false, number: null },
    { row: 1, col: 7, value: null, is_blocked: false, number: null },
    // Row 2
    { row: 2, col: 0, value: null, is_blocked: false, number: null },
    { row: 2, col: 1, value: null, is_blocked: false, number: 4 },
    { row: 2, col: 2, value: null, is_blocked: false, number: null },
    { row: 2, col: 3, value: null, is_blocked: true, number: null },
    { row: 2, col: 4, value: null, is_blocked: false, number: 5 },
    { row: 2, col: 5, value: null, is_blocked: false, number: null },
    { row: 2, col: 6, value: null, is_blocked: false, number: null },
    { row: 2, col: 7, value: null, is_blocked: false, number: null },
    // ... (remaining cells would be defined similarly)
    // For brevity, this example only shows partial data
  ]);

  const cluesAcross: Clue[] = [
    {
      number: 1,
      direction: 'across',
      text: 'Programming language created by Guido van Rossum',
      answer: 'PYTHON',
      start_row: 0,
      start_col: 0,
      length: 6,
    },
    {
      number: 2,
      direction: 'across',
      text: 'Artificial Intelligence (abbr.)',
      answer: 'AI',
      start_row: 0,
      start_col: 7,
      length: 2,
    },
    {
      number: 3,
      direction: 'across',
      text: 'JavaScript library for building user interfaces',
      answer: 'REACT',
      start_row: 1,
      start_col: 2,
      length: 5,
    },
    {
      number: 4,
      direction: 'across',
      text: 'Web framework for Python',
      answer: 'DJANGO',
      start_row: 2,
      start_col: 1,
      length: 6,
    },
    {
      number: 5,
      direction: 'across',
      text: 'Query language for APIs',
      answer: 'GRAPHQL',
      start_row: 2,
      start_col: 4,
      length: 7,
    },
  ];

  const cluesDown: Clue[] = [
    {
      number: 1,
      direction: 'down',
      text: 'A collection of data',
      answer: 'ARRAY',
      start_row: 0,
      start_col: 0,
      length: 5,
    },
    {
      number: 2,
      direction: 'down',
      text: 'Application Programming Interface (abbr.)',
      answer: 'API',
      start_row: 0,
      start_col: 7,
      length: 3,
    },
    {
      number: 3,
      direction: 'down',
      text: 'Representational State Transfer (abbr.)',
      answer: 'REST',
      start_row: 1,
      start_col: 2,
      length: 4,
    },
  ];

  // State for grid interaction
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number } | null>(
    null
  );
  const [currentDirection, setCurrentDirection] = useState<Direction>('across');
  const [activeClue, setActiveClue] = useState<{
    number: number;
    direction: Direction;
  } | null>(null);

  // Handlers
  const handleCellSelect = (row: number, col: number) => {
    setSelectedCell({ row, col });
  };

  const handleCellChange = (updatedCells: Cell[]) => {
    setCells(updatedCells);
  };

  const handleDirectionChange = (direction: Direction) => {
    setCurrentDirection(direction);
  };

  const handleActiveClueChange = (clue: { number: number; direction: Direction } | null) => {
    setActiveClue(clue);
  };

  const handleClueClick = (clue: Clue) => {
    // Select the first cell of the clue
    setSelectedCell({ row: clue.start_row, col: clue.start_col });
    setCurrentDirection(clue.direction);
    setActiveClue({ number: clue.number, direction: clue.direction });
  };

  return (
    <div style={{ padding: '2rem', display: 'flex', gap: '2rem', height: '100vh' }}>
      {/* Left side: Grid */}
      <div style={{ flex: '0 0 auto' }}>
        <h2>Crossword Puzzle</h2>
        <Grid
          cells={cells}
          gridSize={8}
          cluesAcross={cluesAcross}
          cluesDown={cluesDown}
          selectedCell={selectedCell}
          currentDirection={currentDirection}
          activeClue={activeClue}
          onCellSelect={handleCellSelect}
          onCellChange={handleCellChange}
          onDirectionChange={handleDirectionChange}
          onActiveClueChange={handleActiveClueChange}
          cellSize={50}
          readOnly={false}
        />
      </div>

      {/* Right side: Clues */}
      <div style={{ flex: '1 1 auto', minWidth: '300px', maxWidth: '500px' }}>
        <h2>Clues</h2>
        <div style={{ height: 'calc(100vh - 150px)' }}>
          <ClueList
            cluesAcross={cluesAcross}
            cluesDown={cluesDown}
            cells={cells}
            activeClue={activeClue}
            onClueClick={handleClueClick}
            showAnswers={false}
            layout="tabs"
          />
        </div>
      </div>
    </div>
  );
};

export default ClueListExample;
