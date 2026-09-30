/**
 * GridCell component - Represents a single cell in the crossword grid.
 * 
 * Features:
 * - Displays cell number, value, and blocked state
 * - Handles click and keyboard input
 * - Visual feedback for selection, active word, completion, and errors
 * - Supports both user input and AI-filled values
 */

import React, { useEffect, useRef } from 'react';
import type { CellState } from '../types/puzzle';

export interface GridCellProps {
  /** Cell state including position, value, and visual states */
  cell: CellState;
  /** Callback when cell is clicked */
  onClick: (row: number, col: number) => void;
  /** Callback when a letter is entered */
  onInput: (row: number, col: number, value: string) => void;
  /** Whether this cell should receive focus */
  shouldFocus: boolean;
  /** Size of the cell in pixels */
  cellSize?: number;
}

/**
 * GridCell component renders a single cell in the crossword puzzle.
 */
export const GridCell: React.FC<GridCellProps> = ({
  cell,
  onClick,
  onInput,
  shouldFocus,
  cellSize = 50,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus the input when shouldFocus changes to true
  useEffect(() => {
    if (shouldFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [shouldFocus]);

  // Handle click on the cell
  const handleClick = () => {
    if (!cell.is_blocked) {
      onClick(cell.row, cell.col);
    }
  };

  // Handle keyboard input
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Prevent default for navigation keys to let parent handle them
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Tab', 'Backspace', 'Delete'].includes(e.key)) {
      e.preventDefault();
    }
  };

  // Handle input change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase();
    
    // Only allow single letters A-Z
    if (value === '' || /^[A-Z]$/.test(value)) {
      onInput(cell.row, cell.col, value);
    }
  };

  // Build CSS classes based on cell state
  const cellClasses = [
    'grid-cell',
    cell.is_blocked && 'grid-cell--blocked',
    cell.is_selected && 'grid-cell--selected',
    cell.is_active_word && !cell.is_selected && 'grid-cell--active-word',
    cell.is_completed && 'grid-cell--completed',
    cell.has_error && 'grid-cell--error',
  ]
    .filter(Boolean)
    .join(' ');

  // Render blocked cell
  if (cell.is_blocked) {
    return (
      <div
        className={cellClasses}
        style={{
          width: `${cellSize}px`,
          height: `${cellSize}px`,
        }}
      />
    );
  }

  // Render interactive cell
  return (
    <div
      className={cellClasses}
      style={{
        width: `${cellSize}px`,
        height: `${cellSize}px`,
      }}
      onClick={handleClick}
    >
      {/* Cell number (if this cell starts a word) */}
      {cell.number !== null && (
        <span className="grid-cell__number">{cell.number}</span>
      )}

      {/* Input field for letter entry */}
      <input
        ref={inputRef}
        type="text"
        className="grid-cell__input"
        value={cell.value || ''}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        maxLength={1}
        autoComplete="off"
        autoCorrect="off"
        autoCapitalize="characters"
        spellCheck={false}
        aria-label={`Cell ${cell.row}, ${cell.col}${cell.number ? `, clue ${cell.number}` : ''}`}
        tabIndex={-1} // Prevent tab navigation, use arrow keys instead
      />
    </div>
  );
};

export default GridCell;
