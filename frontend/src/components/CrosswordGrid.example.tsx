/**
 * Example usage of CrosswordGrid component.
 * 
 * This file demonstrates how to integrate the CrosswordGrid component
 * with state management and puzzle data.
 * 
 * NOTE: This is an example file for reference. It is not imported by the main app.
 */

import React, { useState } from 'react';
import { CrosswordGrid } from './CrosswordGrid';
import type { Cell, Clue, Direction } from '../types/puzzle';

/**
 * Example component showing CrosswordGrid usage.
 */
export const CrosswordGridExample: React.FC = () => {
  // Example puzzle data (8x8 grid with a few words)
  const [cells, setCells] = useState<Cell[]>([
    // Row 0
    { row: 0, col: 0, value: null, is_blocked: false, number: 1 },
    { row: 0, col: 1, value: null, is_blocked: false, number: null },
    { row: 0, col: 2, value: null, is_blocked: false, number: null },
    { row: 0, col: 3, value: null, is_blocked: false, number: null },
    { row: 0, col: 4, value: null, is_blocked: false, number: null },
    { row: 0, col: 5, value: null, is_blocked: true, number: null },
    { row: 0, col: 6, value: null, is_blocked: false, number: 2 },
    { row: 0, col: 7, value: null, is_blocked: false, number: null },
    // Row 1
    { row: 1, col: 0, value: null, is_blocked: false, number: null },
    { row: 1, col: 1, value: null, is_blocked: true, number: null },
    { row: 1, col: 2, value: null, is_blocked: false, number: 3 },
    { row: 1, col: 3, value: null, is_blocked: false, number: null },
    { row: 1, col: 4, value: null, is_blocked: false, number: null },
    { row: 1, col: 5, value: null, is_blocked: false, number: null },
    { row: 1, col: 6, value: null, is_blocked: false, number: null },
    { row: 1, col: 7, value: null, is_blocked: true, number: null },
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
      text: 'Artificial Intelligence',
      answer: 'AI',
      start_row: 0,
      start_col: 6,
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

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Crossword Grid Example</h2>
      <p>Click on a cell to select it, type to fill in letters, use arrow keys to navigate.</p>

      <CrosswordGrid
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

      {/* Display active clue */}
      {activeClue && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f0f0f0' }}>
          <strong>
            {activeClue.number} {activeClue.direction}:
          </strong>{' '}
          {activeClue.direction === 'across'
            ? cluesAcross.find((c) => c.number === activeClue.number)?.text
            : cluesDown.find((c) => c.number === activeClue.number)?.text}
        </div>
      )}
    </div>
  );
};

export default CrosswordGridExample;
