/**
 * Utility functions for keyboard navigation in the crossword grid.
 */

import type { Direction } from '../types/puzzle';
import { isValidCoord } from './grid';

/**
 * Direction vectors for arrow key navigation.
 */
const DIRECTION_VECTORS: Record<string, { row: number; col: number }> = {
  ArrowUp: { row: -1, col: 0 },
  ArrowDown: { row: 1, col: 0 },
  ArrowLeft: { row: 0, col: -1 },
  ArrowRight: { row: 0, col: 1 },
};

/**
 * Get the next cell position based on arrow key.
 * 
 * @param currentRow - Current row position
 * @param currentCol - Current column position
 * @param key - Arrow key pressed
 * @param gridSize - Size of the grid
 * @param blockedCells - Set of blocked cell coordinates (as "row,col" strings)
 * @returns Next valid cell position, or null if no valid move
 */
export function getNextCellFromArrow(
  currentRow: number,
  currentCol: number,
  key: string,
  gridSize: number,
  blockedCells: Set<string> = new Set()
): { row: number; col: number } | null {
  const vector = DIRECTION_VECTORS[key];
  if (!vector) return null;

  let nextRow = currentRow + vector.row;
  let nextCol = currentCol + vector.col;

  // Keep moving in the direction until we find a valid cell or hit boundary
  while (isValidCoord(nextRow, nextCol, gridSize)) {
    const cellKey = `${nextRow},${nextCol}`;
    if (!blockedCells.has(cellKey)) {
      return { row: nextRow, col: nextCol };
    }
    nextRow += vector.row;
    nextCol += vector.col;
  }

  return null;
}

/**
 * Get the next cell in the current word direction.
 * 
 * @param currentRow - Current row position
 * @param currentCol - Current column position
 * @param direction - Current word direction
 * @param gridSize - Size of the grid
 * @param blockedCells - Set of blocked cell coordinates
 * @returns Next cell in word direction, or null if at end
 */
export function getNextCellInWord(
  currentRow: number,
  currentCol: number,
  direction: Direction,
  gridSize: number,
  blockedCells: Set<string> = new Set()
): { row: number; col: number } | null {
  const key = direction === 'across' ? 'ArrowRight' : 'ArrowDown';
  return getNextCellFromArrow(currentRow, currentCol, key, gridSize, blockedCells);
}

/**
 * Get the previous cell in the current word direction.
 * 
 * @param currentRow - Current row position
 * @param currentCol - Current column position
 * @param direction - Current word direction
 * @param gridSize - Size of the grid
 * @param blockedCells - Set of blocked cell coordinates
 * @returns Previous cell in word direction, or null if at start
 */
export function getPreviousCellInWord(
  currentRow: number,
  currentCol: number,
  direction: Direction,
  gridSize: number,
  blockedCells: Set<string> = new Set()
): { row: number; col: number } | null {
  const key = direction === 'across' ? 'ArrowLeft' : 'ArrowUp';
  return getNextCellFromArrow(currentRow, currentCol, key, gridSize, blockedCells);
}

/**
 * Toggle between across and down directions.
 * 
 * @param currentDirection - Current direction
 * @returns Opposite direction
 */
export function toggleDirection(currentDirection: Direction): Direction {
  return currentDirection === 'across' ? 'down' : 'across';
}

/**
 * Get the first cell of a word based on clue.
 * 
 * @param startRow - Starting row of the word
 * @param startCol - Starting column of the word
 * @returns Cell coordinates
 */
export function getWordStartCell(
  startRow: number,
  startCol: number
): { row: number; col: number } {
  return { row: startRow, col: startCol };
}

/**
 * Get the last cell of a word based on clue.
 * 
 * @param startRow - Starting row of the word
 * @param startCol - Starting column of the word
 * @param length - Length of the word
 * @param direction - Direction of the word
 * @returns Cell coordinates
 */
export function getWordEndCell(
  startRow: number,
  startCol: number,
  length: number,
  direction: Direction
): { row: number; col: number } {
  if (direction === 'across') {
    return { row: startRow, col: startCol + length - 1 };
  } else {
    return { row: startRow + length - 1, col: startCol };
  }
}

/**
 * Check if a cell is within a word's bounds.
 * 
 * @param row - Cell row
 * @param col - Cell column
 * @param startRow - Word start row
 * @param startCol - Word start column
 * @param length - Word length
 * @param direction - Word direction
 * @returns True if cell is within word bounds
 */
export function isCellInWord(
  row: number,
  col: number,
  startRow: number,
  startCol: number,
  length: number,
  direction: Direction
): boolean {
  if (direction === 'across') {
    return row === startRow && col >= startCol && col < startCol + length;
  } else {
    return col === startCol && row >= startRow && row < startRow + length;
  }
}

/**
 * Get all cell positions for a word.
 * 
 * @param startRow - Word start row
 * @param startCol - Word start column
 * @param length - Word length
 * @param direction - Word direction
 * @returns Array of cell positions
 */
export function getWordCellPositions(
  startRow: number,
  startCol: number,
  length: number,
  direction: Direction
): Array<{ row: number; col: number }> {
  const positions: Array<{ row: number; col: number }> = [];

  for (let i = 0; i < length; i++) {
    if (direction === 'across') {
      positions.push({ row: startRow, col: startCol + i });
    } else {
      positions.push({ row: startRow + i, col: startCol });
    }
  }

  return positions;
}

/**
 * Find the next empty cell in a word.
 * 
 * @param startRow - Word start row
 * @param startCol - Word start column
 * @param length - Word length
 * @param direction - Word direction
 * @param filledCells - Set of filled cell coordinates (as "row,col" strings)
 * @returns Next empty cell position, or null if word is complete
 */
export function findNextEmptyCell(
  startRow: number,
  startCol: number,
  length: number,
  direction: Direction,
  filledCells: Set<string>
): { row: number; col: number } | null {
  const positions = getWordCellPositions(startRow, startCol, length, direction);

  for (const pos of positions) {
    const cellKey = `${pos.row},${pos.col}`;
    if (!filledCells.has(cellKey)) {
      return pos;
    }
  }

  return null;
}
