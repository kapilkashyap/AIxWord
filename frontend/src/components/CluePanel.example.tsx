/**
 * Example usage of the CluePanel component.
 * 
 * This file demonstrates how to integrate CluePanel into your application
 * with various configuration options.
 */

import React, { useState } from 'react';
import { CluePanel } from './CluePanel';
import type { Clue, Cell } from '../types/puzzle';

/**
 * Basic CluePanel Example
 * 
 * Shows the simplest usage with minimal props.
 */
export const BasicCluePanelExample: React.FC = () => {
  const [activeClue, setActiveClue] = useState<{ number: number; direction: 'across' | 'down' } | null>(null);

  // Sample clues
  const cluesAcross: Clue[] = [
    {
      number: 1,
      direction: 'across',
      text: 'Capital of France',
      answer: 'PARIS',
      start_row: 0,
      start_col: 0,
      length: 5,
    },
    {
      number: 3,
      direction: 'across',
      text: 'Opposite of hot',
      answer: 'COLD',
      start_row: 2,
      start_col: 0,
      length: 4,
    },
  ];

  const cluesDown: Clue[] = [
    {
      number: 1,
      direction: 'down',
      text: 'Color of the sky',
      answer: 'BLUE',
      start_row: 0,
      start_col: 0,
      length: 4,
    },
    {
      number: 2,
      direction: 'down',
      text: 'Man\'s best friend',
      answer: 'DOG',
      start_row: 0,
      start_col: 1,
      length: 3,
    },
  ];

  // Sample cells (8x8 grid)
  const cells: Cell[] = Array.from({ length: 64 }, (_, i) => ({
    row: Math.floor(i / 8),
    col: i % 8,
    value: null,
    is_blocked: false,
    number: null,
  }));

  const handleClueClick = (clue: Clue) => {
    setActiveClue({ number: clue.number, direction: clue.direction });
    console.log('Clue clicked:', clue);
  };

  return (
    <div style={{ height: '600px', width: '400px' }}>
      <CluePanel
        cluesAcross={cluesAcross}
        cluesDown={cluesDown}
        cells={cells}
        activeClue={activeClue}
        onClueClick={handleClueClick}
      />
    </div>
  );
};

/**
 * Advanced CluePanel Example
 * 
 * Shows all available features and configuration options.
 */
export const AdvancedCluePanelExample: React.FC = () => {
  const [activeClue, setActiveClue] = useState<{ number: number; direction: 'across' | 'down' } | null>(null);
  const [showAnswers, setShowAnswers] = useState(false);

  // Sample clues (same as above)
  const cluesAcross: Clue[] = [
    {
      number: 1,
      direction: 'across',
      text: 'Capital of France',
      answer: 'PARIS',
      start_row: 0,
      start_col: 0,
      length: 5,
    },
    {
      number: 3,
      direction: 'across',
      text: 'Opposite of hot',
      answer: 'COLD',
      start_row: 2,
      start_col: 0,
      length: 4,
    },
    {
      number: 5,
      direction: 'across',
      text: 'Large body of water',
      answer: 'OCEAN',
      start_row: 4,
      start_col: 0,
      length: 5,
    },
  ];

  const cluesDown: Clue[] = [
    {
      number: 1,
      direction: 'down',
      text: 'Color of the sky',
      answer: 'BLUE',
      start_row: 0,
      start_col: 0,
      length: 4,
    },
    {
      number: 2,
      direction: 'down',
      text: 'Man\'s best friend',
      answer: 'DOG',
      start_row: 0,
      start_col: 1,
      length: 3,
    },
  ];

  // Sample cells with some filled values
  const cells: Cell[] = Array.from({ length: 64 }, (_, i) => ({
    row: Math.floor(i / 8),
    col: i % 8,
    value: i === 0 ? 'P' : i === 1 ? 'A' : null,
    is_blocked: false,
    number: i === 0 ? 1 : i === 8 ? 2 : null,
  }));

  const handleClueClick = (clue: Clue) => {
    setActiveClue({ number: clue.number, direction: clue.direction });
    console.log('Clue clicked:', clue);
  };

  return (
    <div style={{ height: '600px', width: '400px' }}>
      <CluePanel
        cluesAcross={cluesAcross}
        cluesDown={cluesDown}
        cells={cells}
        activeClue={activeClue}
        onClueClick={handleClueClick}
        showAnswers={showAnswers}
        initialLayout="split"
        collapsible={true}
        showSearch={true}
        showLayoutToggle={true}
        showAnswerToggle={true}
      />
      
      {/* External controls */}
      <div style={{ marginTop: '1rem' }}>
        <button onClick={() => setShowAnswers(!showAnswers)}>
          {showAnswers ? 'Hide' : 'Show'} Answers
        </button>
      </div>
    </div>
  );
};

/**
 * Mobile-Optimized CluePanel Example
 * 
 * Shows configuration optimized for mobile devices.
 */
export const MobileCluePanelExample: React.FC = () => {
  const [activeClue, setActiveClue] = useState<{ number: number; direction: 'across' | 'down' } | null>(null);

  const cluesAcross: Clue[] = [
    {
      number: 1,
      direction: 'across',
      text: 'Capital of France',
      answer: 'PARIS',
      start_row: 0,
      start_col: 0,
      length: 5,
    },
  ];

  const cluesDown: Clue[] = [
    {
      number: 1,
      direction: 'down',
      text: 'Color of the sky',
      answer: 'BLUE',
      start_row: 0,
      start_col: 0,
      length: 4,
    },
  ];

  const cells: Cell[] = Array.from({ length: 64 }, (_, i) => ({
    row: Math.floor(i / 8),
    col: i % 8,
    value: null,
    is_blocked: false,
    number: null,
  }));

  const handleClueClick = (clue: Clue) => {
    setActiveClue({ number: clue.number, direction: clue.direction });
  };

  return (
    <div style={{ height: '100vh', width: '100%' }}>
      <CluePanel
        cluesAcross={cluesAcross}
        cluesDown={cluesDown}
        cells={cells}
        activeClue={activeClue}
        onClueClick={handleClueClick}
        initialLayout="tabs"
        collapsible={true}
        initialCollapsed={false}
        showSearch={false}
        showLayoutToggle={false}
        showAnswerToggle={false}
      />
    </div>
  );
};

/**
 * Integration Example with Grid
 * 
 * Shows how CluePanel works together with the Grid component.
 */
export const IntegratedExample: React.FC = () => {
  const [activeClue, setActiveClue] = useState<{ number: number; direction: 'across' | 'down' } | null>(null);
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number } | null>(null);

  const cluesAcross: Clue[] = [
    {
      number: 1,
      direction: 'across',
      text: 'Capital of France',
      answer: 'PARIS',
      start_row: 0,
      start_col: 0,
      length: 5,
    },
  ];

  const cluesDown: Clue[] = [
    {
      number: 1,
      direction: 'down',
      text: 'Color of the sky',
      answer: 'BLUE',
      start_row: 0,
      start_col: 0,
      length: 4,
    },
  ];

  const cells: Cell[] = Array.from({ length: 64 }, (_, i) => ({
    row: Math.floor(i / 8),
    col: i % 8,
    value: null,
    is_blocked: false,
    number: i === 0 ? 1 : null,
  }));

  const handleClueClick = (clue: Clue) => {
    // Jump to the clue's starting position in the grid
    setSelectedCell({ row: clue.start_row, col: clue.start_col });
    setActiveClue({ number: clue.number, direction: clue.direction });
  };

  return (
    <div style={{ display: 'flex', gap: '2rem', height: '600px' }}>
      {/* Grid would go here */}
      <div style={{ flex: 1 }}>
        <div style={{ 
          border: '2px solid #ccc', 
          borderRadius: '8px', 
          padding: '1rem',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f8f9fa'
        }}>
          Grid Component
          {selectedCell && (
            <div style={{ marginTop: '1rem', fontSize: '0.875rem' }}>
              Selected: Row {selectedCell.row}, Col {selectedCell.col}
            </div>
          )}
        </div>
      </div>

      {/* CluePanel */}
      <div style={{ width: '400px' }}>
        <CluePanel
          cluesAcross={cluesAcross}
          cluesDown={cluesDown}
          cells={cells}
          activeClue={activeClue}
          onClueClick={handleClueClick}
          showSearch={true}
        />
      </div>
    </div>
  );
};

export default {
  BasicCluePanelExample,
  AdvancedCluePanelExample,
  MobileCluePanelExample,
  IntegratedExample,
};
