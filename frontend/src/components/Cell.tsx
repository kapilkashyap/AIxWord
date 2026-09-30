/**
 * Cell component - Represents a single cell in the crossword grid.
 * 
 * This is a simplified, modular version of GridCell that uses CSS modules
 * for styling. It provides the same functionality with a cleaner API.
 * 
 * Features:
 * - Displays cell number, value, and blocked state
 * - Handles click and keyboard input
 * - Visual feedback for selection, active word, completion, and errors
 * - Supports both user input and AI-filled values
 * - Uses CSS modules for scoped styling
 */

import React, { useEffect, useRef } from 'react';
import type { CellState } from '../types/puzzle';
import styles from './Cell.module.css';

export interface CellProps {
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
  /** Whether the cell is read-only */
  readOnly?: boolean;
}

/**
 * Cell component renders a single cell in the crossword puzzle.
 */
export const Cell: React.FC<CellProps> = ({
  cell,
  onClick,
  onInput,
  shouldFocus,
  cellSize = 50,
  readOnly = false,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus the input when shouldFocus changes to true
  useEffect(() => {
    if (shouldFocus && inputRef.current && !readOnly) {
      inputRef.current.focus();
    }
  }, [shouldFocus, readOnly]);

  // Handle click on the cell
  const handleClick = () => {
    if (!cell.is_blocked && !readOnly) {
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
    if (readOnly) return;
    
    const value = e.target.value.toUpperCase();
    
    // Only allow single letters A-Z
    if (value === '' || /^[A-Z]$/.test(value)) {
      onInput(cell.row, cell.col, value);
    }
  };

  // Build CSS classes based on cell state
  const cellClasses = [
    styles.cell,
    cell.is_blocked && styles.blocked,
    cell.is_selected && styles.selected,
    cell.is_active_word && !cell.is_selected && styles.activeWord,
    cell.is_completed && styles.completed,
    cell.has_error && styles.error,
    readOnly && styles.readOnly,
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
        data-testid={`cell-${cell.row}-${cell.col}`}
        data-blocked="true"
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
      data-testid={`cell-${cell.row}-${cell.col}`}
      data-row={cell.row}
      data-col={cell.col}
      data-selected={cell.is_selected}
      data-active-word={cell.is_active_word}
    >
      {/* Cell number (if this cell starts a word) */}
      {cell.number !== null && (
        <span className={styles.number} data-testid={`cell-number-${cell.number}`}>
          {cell.number}
        </span>
      )}

      {/* Input field for letter entry */}
      <input
        ref={inputRef}
        type="text"
        className={styles.input}
        value={cell.value || ''}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        maxLength={1}
        autoComplete="off"
        autoCorrect="off"
        autoCapitalize="characters"
        spellCheck={false}
        readOnly={readOnly}
        disabled={readOnly}
        aria-label={`Cell ${cell.row}, ${cell.col}${cell.number ? `, clue ${cell.number}` : ''}`}
        tabIndex={-1} // Prevent tab navigation, use arrow keys instead
        data-testid={`cell-input-${cell.row}-${cell.col}`}
      />
    </div>
  );
};

export default Cell;
