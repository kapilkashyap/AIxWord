/**
 * Grid component - Main grid component for the crossword puzzle.
 * 
 * This is a simplified, modular version of CrosswordGrid that uses CSS modules
 * for styling. It provides the same functionality with a cleaner API.
 * 
 * Features:
 * - Renders the complete crossword grid with all cells
 * - Manages cell selection and navigation
 * - Handles keyboard input and navigation (arrow keys, tab, backspace)
 * - Supports both across and down word directions
 * - Provides visual feedback for active words and completed cells
 * - Integrates with parent state management for puzzle solving
 * - Uses CSS modules for scoped styling
 */

import React, { useCallback, useEffect, useRef } from 'react';
import type { Cell as CellType, CellState, Clue, Direction } from '../types/puzzle';
import { Cell } from './Cell';
import {
  getCellAt,
  updateCell,
  findClueForCell,
} from '../utils/grid';
import {
  getNextCellFromArrow,
  getNextCellInWord,
  getPreviousCellInWord,
  toggleDirection,
  isCellInWord,
} from '../utils/keyboard';
import styles from './Grid.module.css';

export interface GridProps {
  /** Array of all cells in the grid */
  cells: CellType[];
  /** Grid size (NxN) */
  gridSize: number;
  /** Across clues */
  cluesAcross: Clue[];
  /** Down clues */
  cluesDown: Clue[];
  /** Currently selected cell position */
  selectedCell: { row: number; col: number } | null;
  /** Current word direction */
  currentDirection: Direction;
  /** Currently active clue */
  activeClue: { number: number; direction: Direction } | null;
  /** Callback when a cell is selected */
  onCellSelect: (row: number, col: number) => void;
  /** Callback when cell value changes */
  onCellChange: (cells: CellType[]) => void;
  /** Callback when direction changes */
  onDirectionChange: (direction: Direction) => void;
  /** Callback when active clue changes */
  onActiveClueChange: (clue: { number: number; direction: Direction } | null) => void;
  /** Optional cell size in pixels */
  cellSize?: number;
  /** Whether the grid is read-only */
  readOnly?: boolean;
  /** Optional CSS class name */
  className?: string;
}

/**
 * Grid component renders the interactive crossword puzzle grid.
 */
export const Grid: React.FC<GridProps> = ({
  cells,
  gridSize,
  cluesAcross,
  cluesDown,
  selectedCell,
  currentDirection,
  activeClue,
  onCellSelect,
  onCellChange,
  onDirectionChange,
  onActiveClueChange,
  cellSize = 50,
  readOnly = false,
  className,
}) => {
  const gridRef = useRef<HTMLDivElement>(null);

  // Create a set of blocked cell coordinates for efficient lookup
  const blockedCells = React.useMemo(() => {
    const blocked = new Set<string>();
    cells.forEach((cell) => {
      if (cell.is_blocked) {
        blocked.add(`${cell.row},${cell.col}`);
      }
    });
    return blocked;
  }, [cells]);

  // Convert cells to CellState with visual state information
  const cellStates: CellState[] = React.useMemo(() => {
    return cells.map((cell) => {
      const isSelected =
        selectedCell !== null &&
        cell.row === selectedCell.row &&
        cell.col === selectedCell.col;

      // Check if cell is part of the active word
      let isActiveWord = false;
      if (activeClue) {
        const clue =
          activeClue.direction === 'across'
            ? cluesAcross.find((c) => c.number === activeClue.number)
            : cluesDown.find((c) => c.number === activeClue.number);

        if (clue) {
          isActiveWord = isCellInWord(
            cell.row,
            cell.col,
            clue.start_row,
            clue.start_col,
            clue.length,
            clue.direction
          );
        }
      }

      return {
        ...cell,
        is_selected: isSelected,
        is_active_word: isActiveWord,
        is_completed: false, // Will be set by validation logic
        has_error: false, // Will be set by validation logic
      };
    });
  }, [cells, selectedCell, activeClue, cluesAcross, cluesDown]);

  // Handle cell click
  const handleCellClick = useCallback(
    (row: number, col: number) => {
      if (readOnly) return;

      // If clicking the same cell, toggle direction
      if (selectedCell && selectedCell.row === row && selectedCell.col === col) {
        onDirectionChange(toggleDirection(currentDirection));
      } else {
        onCellSelect(row, col);
      }

      // Update active clue based on current direction
      const clues = currentDirection === 'across' ? cluesAcross : cluesDown;
      const clue = findClueForCell(cells, clues, row, col);
      if (clue) {
        onActiveClueChange({ number: clue.number, direction: currentDirection });
      }
    },
    [
      readOnly,
      selectedCell,
      currentDirection,
      cells,
      cluesAcross,
      cluesDown,
      onCellSelect,
      onDirectionChange,
      onActiveClueChange,
    ]
  );

  // Handle cell input
  const handleCellInput = useCallback(
    (row: number, col: number, value: string) => {
      if (readOnly) return;

      // Update the cell value
      const updatedCells = updateCell(cells, row, col, value || null);
      onCellChange(updatedCells);

      // Move to next cell if a letter was entered
      if (value && selectedCell) {
        const nextCell = getNextCellInWord(
          row,
          col,
          currentDirection,
          gridSize,
          blockedCells
        );
        if (nextCell) {
          onCellSelect(nextCell.row, nextCell.col);
        }
      }
    },
    [
      readOnly,
      cells,
      selectedCell,
      currentDirection,
      gridSize,
      blockedCells,
      onCellChange,
      onCellSelect,
    ]
  );

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (readOnly || !selectedCell) return;

      const { row, col } = selectedCell;

      // Arrow key navigation
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        e.preventDefault();
        const nextCell = getNextCellFromArrow(row, col, e.key, gridSize, blockedCells);
        if (nextCell) {
          onCellSelect(nextCell.row, nextCell.col);

          // Update direction based on arrow key
          if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            if (currentDirection !== 'across') {
              onDirectionChange('across');
            }
          } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            if (currentDirection !== 'down') {
              onDirectionChange('down');
            }
          }
        }
      }

      // Backspace - clear current cell and move to previous
      else if (e.key === 'Backspace') {
        e.preventDefault();
        const currentCell = getCellAt(cells, row, col);
        
        if (currentCell?.value) {
          // Clear current cell
          const updatedCells = updateCell(cells, row, col, null);
          onCellChange(updatedCells);
        } else {
          // Move to previous cell
          const prevCell = getPreviousCellInWord(
            row,
            col,
            currentDirection,
            gridSize,
            blockedCells
          );
          if (prevCell) {
            onCellSelect(prevCell.row, prevCell.col);
            // Clear the previous cell
            const updatedCells = updateCell(cells, prevCell.row, prevCell.col, null);
            onCellChange(updatedCells);
          }
        }
      }

      // Delete - clear current cell
      else if (e.key === 'Delete') {
        e.preventDefault();
        const updatedCells = updateCell(cells, row, col, null);
        onCellChange(updatedCells);
      }

      // Space - toggle direction
      else if (e.key === ' ') {
        e.preventDefault();
        onDirectionChange(toggleDirection(currentDirection));
      }

      // Tab - move to next word
      else if (e.key === 'Tab') {
        e.preventDefault();
        // Find next clue
        const clues = currentDirection === 'across' ? cluesAcross : cluesDown;
        const currentClueIndex = activeClue
          ? clues.findIndex((c) => c.number === activeClue.number)
          : -1;
        
        const nextClueIndex = e.shiftKey
          ? (currentClueIndex - 1 + clues.length) % clues.length
          : (currentClueIndex + 1) % clues.length;
        
        const nextClue = clues[nextClueIndex];
        if (nextClue) {
          onCellSelect(nextClue.start_row, nextClue.start_col);
          onActiveClueChange({ number: nextClue.number, direction: currentDirection });
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    readOnly,
    selectedCell,
    currentDirection,
    gridSize,
    cells,
    blockedCells,
    cluesAcross,
    cluesDown,
    activeClue,
    onCellSelect,
    onCellChange,
    onDirectionChange,
    onActiveClueChange,
  ]);

  // Calculate grid dimensions
  const gridWidth = gridSize * cellSize;
  const gridHeight = gridSize * cellSize;

  return (
    <div className={`${styles.container} ${className || ''}`} data-testid="grid-container">
      <div
        ref={gridRef}
        className={styles.grid}
        style={{
          width: `${gridWidth}px`,
          height: `${gridHeight}px`,
          gridTemplateColumns: `repeat(${gridSize}, ${cellSize}px)`,
          gridTemplateRows: `repeat(${gridSize}, ${cellSize}px)`,
        }}
        data-testid="grid"
        data-grid-size={gridSize}
      >
        {cellStates.map((cell) => {
          const shouldFocus =
            selectedCell !== null &&
            cell.row === selectedCell.row &&
            cell.col === selectedCell.col;

          return (
            <Cell
              key={`${cell.row}-${cell.col}`}
              cell={cell}
              onClick={handleCellClick}
              onInput={handleCellInput}
              shouldFocus={shouldFocus}
              cellSize={cellSize}
              readOnly={readOnly}
            />
          );
        })}
      </div>

      {/* Direction indicator */}
      {!readOnly && (
        <div className={styles.directionIndicator} data-testid="direction-indicator">
          <span className={styles.directionLabel}>Direction:</span>
          <span className={styles.directionValue}>
            {currentDirection === 'across' ? '→ Across' : '↓ Down'}
          </span>
          <span className={styles.directionHint}>(Space to toggle)</span>
        </div>
      )}
    </div>
  );
};

export default Grid;
