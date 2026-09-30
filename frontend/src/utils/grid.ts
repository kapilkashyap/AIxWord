/**
 * Utility functions for grid operations and coordinate conversions.
 */

import type { Cell, Clue, Direction } from '../types/puzzle';

/**
 * Convert 2D grid coordinates to 1D array index.
 * 
 * @param row - Row position (0-indexed)
 * @param col - Column position (0-indexed)
 * @param gridSize - Size of the grid (NxN)
 * @returns Array index
 */
export function coordsToIndex(row: number, col: number, gridSize: number): number {
  return row * gridSize + col;
}

/**
 * Convert 1D array index to 2D grid coordinates.
 * 
 * @param index - Array index
 * @param gridSize - Size of the grid (NxN)
 * @returns Object with row and col properties
 */
export function indexToCoords(index: number, gridSize: number): { row: number; col: number } {
  return {
    row: Math.floor(index / gridSize),
    col: index % gridSize,
  };
}

/**
 * Check if coordinates are within grid bounds.
 * 
 * @param row - Row position
 * @param col - Column position
 * @param gridSize - Size of the grid
 * @returns True if coordinates are valid
 */
export function isValidCoord(row: number, col: number, gridSize: number): boolean {
  return row >= 0 && row < gridSize && col >= 0 && col < gridSize;
}

/**
 * Get the cell at specific coordinates from a cell array.
 * 
 * @param cells - Array of cells
 * @param row - Row position
 * @param col - Column position
 * @returns Cell at the specified position, or null if not found
 */
export function getCellAt(cells: Cell[], row: number, col: number): Cell | null {
  return cells.find((cell) => cell.row === row && cell.col === col) || null;
}

/**
 * Get all cells for a specific word based on clue.
 * 
 * @param cells - Array of cells
 * @param clue - Clue defining the word
 * @returns Array of cells that make up the word
 */
export function getWordCells(cells: Cell[], clue: Clue): Cell[] {
  const wordCells: Cell[] = [];
  const { start_row, start_col, length, direction } = clue;

  for (let i = 0; i < length; i++) {
    const row = direction === 'across' ? start_row : start_row + i;
    const col = direction === 'across' ? start_col + i : start_col;
    const cell = getCellAt(cells, row, col);
    if (cell) {
      wordCells.push(cell);
    }
  }

  return wordCells;
}

/**
 * Get the word text from cells.
 * 
 * @param cells - Array of cells for the word
 * @returns Word text (uppercase), with underscores for empty cells
 */
export function getWordText(cells: Cell[]): string {
  return cells.map((cell) => cell.value || '_').join('');
}

/**
 * Check if a word is complete (all cells filled).
 * 
 * @param cells - Array of cells for the word
 * @returns True if all cells have values
 */
export function isWordComplete(cells: Cell[]): boolean {
  return cells.every((cell) => cell.value !== null && cell.value !== '');
}

/**
 * Get the next cell position based on direction.
 * 
 * @param row - Current row
 * @param col - Current column
 * @param direction - Direction to move
 * @param gridSize - Size of the grid
 * @returns Next cell coordinates, or null if out of bounds
 */
export function getNextCell(
  row: number,
  col: number,
  direction: Direction,
  gridSize: number
): { row: number; col: number } | null {
  const nextRow = direction === 'down' ? row + 1 : row;
  const nextCol = direction === 'across' ? col + 1 : col;

  if (isValidCoord(nextRow, nextCol, gridSize)) {
    return { row: nextRow, col: nextCol };
  }
  return null;
}

/**
 * Get the previous cell position based on direction.
 * 
 * @param row - Current row
 * @param col - Current column
 * @param direction - Direction to move
 * @returns Previous cell coordinates, or null if out of bounds
 */
export function getPreviousCell(
  row: number,
  col: number,
  direction: Direction
): { row: number; col: number } | null {
  const prevRow = direction === 'down' ? row - 1 : row;
  const prevCol = direction === 'across' ? col - 1 : col;

  if (isValidCoord(prevRow, prevCol, 8)) {
    return { row: prevRow, col: prevCol };
  }
  return null;
}

/**
 * Find the clue that contains a specific cell.
 * 
 * @param cells - Array of all cells
 * @param clues - Array of clues to search
 * @param row - Row position
 * @param col - Column position
 * @returns Clue that contains the cell, or null if not found
 */
export function findClueForCell(
  cells: Cell[],
  clues: Clue[],
  row: number,
  col: number
): Clue | null {
  for (const clue of clues) {
    const wordCells = getWordCells(cells, clue);
    if (wordCells.some((cell) => cell.row === row && cell.col === col)) {
      return clue;
    }
  }
  return null;
}

/**
 * Get all clues that intersect at a specific cell.
 * 
 * @param cells - Array of all cells
 * @param cluesAcross - Across clues
 * @param cluesDown - Down clues
 * @param row - Row position
 * @param col - Column position
 * @returns Object with across and down clues at the cell
 */
export function getIntersectingClues(
  cells: Cell[],
  cluesAcross: Clue[],
  cluesDown: Clue[],
  row: number,
  col: number
): { across: Clue | null; down: Clue | null } {
  return {
    across: findClueForCell(cells, cluesAcross, row, col),
    down: findClueForCell(cells, cluesDown, row, col),
  };
}

/**
 * Create an empty grid of cells.
 * 
 * @param gridSize - Size of the grid (NxN)
 * @returns Array of empty cells
 */
export function createEmptyGrid(gridSize: number): Cell[] {
  const cells: Cell[] = [];
  for (let row = 0; row < gridSize; row++) {
    for (let col = 0; col < gridSize; col++) {
      cells.push({
        row,
        col,
        value: null,
        is_blocked: false,
        number: null,
      });
    }
  }
  return cells;
}

/**
 * Clone a cell array (deep copy).
 * 
 * @param cells - Array of cells to clone
 * @returns Cloned array
 */
export function cloneCells(cells: Cell[]): Cell[] {
  return cells.map((cell) => ({ ...cell }));
}

/**
 * Update a specific cell in the array.
 * 
 * @param cells - Array of cells
 * @param row - Row position
 * @param col - Column position
 * @param value - New value for the cell
 * @returns New array with updated cell
 */
export function updateCell(
  cells: Cell[],
  row: number,
  col: number,
  value: string | null
): Cell[] {
  return cells.map((cell) =>
    cell.row === row && cell.col === col ? { ...cell, value } : cell
  );
}
