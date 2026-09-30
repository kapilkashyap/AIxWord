/**
 * Custom hook for managing puzzle state.
 * 
 * This hook provides centralized state management for the current puzzle,
 * including grid state, user inputs, and puzzle metadata.
 */

import { useState, useCallback, useMemo } from 'react';
import type { Puzzle, Cell, CellState, GridState, Direction, Clue } from '../types/puzzle';
import { updateCell, getWordCells, isWordComplete } from '../utils/grid';

/**
 * Hook for managing puzzle state and user interactions.
 * 
 * @returns Object with puzzle state and manipulation functions
 */
export function usePuzzle() {
  const [puzzle, setPuzzle] = useState<Puzzle | null>(null);
  const [userCells, setUserCells] = useState<Cell[]>([]);
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number } | null>(null);
  const [currentDirection, setCurrentDirection] = useState<Direction>('across');
  const [activeClue, setActiveClue] = useState<{ number: number; direction: Direction } | null>(
    null
  );

  /**
   * Load a new puzzle and initialize user cells.
   */
  const loadPuzzle = useCallback((newPuzzle: Puzzle) => {
    setPuzzle(newPuzzle);
    // Initialize user cells with empty values
    const emptyCells = newPuzzle.cells.map((cell) => ({
      ...cell,
      value: null, // User starts with empty grid
    }));
    setUserCells(emptyCells);
    setSelectedCell(null);
    setCurrentDirection('across');
    setActiveClue(null);
  }, []);

  /**
   * Clear the current puzzle.
   */
  const clearPuzzle = useCallback(() => {
    setPuzzle(null);
    setUserCells([]);
    setSelectedCell(null);
    setCurrentDirection('across');
    setActiveClue(null);
  }, []);

  /**
   * Update a cell value.
   */
  const setCellValue = useCallback(
    (row: number, col: number, value: string | null) => {
      setUserCells((prev) => updateCell(prev, row, col, value));
    },
    []
  );

  /**
   * Clear a cell value.
   */
  const clearCell = useCallback((row: number, col: number) => {
    setUserCells((prev) => updateCell(prev, row, col, null));
  }, []);

  /**
   * Reset all user cells to empty.
   */
  const resetGrid = useCallback(() => {
    if (puzzle) {
      const emptyCells = puzzle.cells.map((cell) => ({
        ...cell,
        value: null,
      }));
      setUserCells(emptyCells);
    }
  }, [puzzle]);

  /**
   * Select a cell and update active clue.
   */
  const selectCell = useCallback(
    (row: number, col: number, direction?: Direction) => {
      setSelectedCell({ row, col });
      if (direction) {
        setCurrentDirection(direction);
      }
    },
    []
  );

  /**
   * Toggle the current direction.
   */
  const toggleDirection = useCallback(() => {
    setCurrentDirection((prev) => (prev === 'across' ? 'down' : 'across'));
  }, []);

  /**
   * Select a clue and its first cell.
   */
  const selectClue = useCallback(
    (clue: Clue) => {
      setActiveClue({ number: clue.number, direction: clue.direction });
      setCurrentDirection(clue.direction);
      setSelectedCell({ row: clue.start_row, col: clue.start_col });
    },
    []
  );

  /**
   * Get cell states with UI metadata (selected, active word, completed).
   */
  const cellStates = useMemo((): CellState[] => {
    if (!puzzle || userCells.length === 0) return [];

    const states: CellState[] = userCells.map((cell) => ({
      ...cell,
      is_selected: false,
      is_active_word: false,
      is_completed: false,
      has_error: false,
    }));

    // Mark selected cell
    if (selectedCell) {
      const selectedIndex = states.findIndex(
        (cell) => cell.row === selectedCell.row && cell.col === selectedCell.col
      );
      if (selectedIndex !== -1) {
        states[selectedIndex].is_selected = true;
      }
    }

    // Mark ALL completed words (not just active word)
    const allClues = [...puzzle.clues_across, ...puzzle.clues_down];
    allClues.forEach((clue) => {
      const wordCells = getWordCells(userCells, clue);
      const isComplete = isWordComplete(wordCells);

      if (isComplete) {
        wordCells.forEach((wordCell) => {
          const index = states.findIndex(
            (cell) => cell.row === wordCell.row && cell.col === wordCell.col
          );
          if (index !== -1) {
            states[index].is_completed = true;
          }
        });
      }
    });

    // Mark active word cells
    if (activeClue && puzzle) {
      const clues = activeClue.direction === 'across' ? puzzle.clues_across : puzzle.clues_down;
      const clue = clues.find((c) => c.number === activeClue.number);
      if (clue) {
        const wordCells = getWordCells(userCells, clue);

        wordCells.forEach((wordCell) => {
          const index = states.findIndex(
            (cell) => cell.row === wordCell.row && cell.col === wordCell.col
          );
          if (index !== -1) {
            states[index].is_active_word = true;
          }
        });
      }
    }

    return states;
  }, [puzzle, userCells, selectedCell, activeClue]);

  /**
   * Get grid state object.
   */
  const gridState = useMemo(
    (): GridState => ({
      cells: cellStates,
      selected_cell: selectedCell,
      current_direction: currentDirection,
      active_clue: activeClue,
    }),
    [cellStates, selectedCell, currentDirection, activeClue]
  );

  /**
   * Check if puzzle is complete (all non-blocked cells filled).
   */
  const isComplete = useMemo(() => {
    if (!puzzle || userCells.length === 0) return false;

    return userCells.every((cell) => {
      if (cell.is_blocked) return true;
      return cell.value !== null && cell.value !== '';
    });
  }, [puzzle, userCells]);

  /**
   * Get completion percentage.
   */
  const completionPercentage = useMemo(() => {
    if (!puzzle || userCells.length === 0) return 0;

    const fillableCells = userCells.filter((cell) => !cell.is_blocked);
    const filledCells = fillableCells.filter((cell) => cell.value !== null && cell.value !== '');

    return fillableCells.length > 0 ? (filledCells.length / fillableCells.length) * 100 : 0;
  }, [puzzle, userCells]);

  return {
    // State
    puzzle,
    userCells,
    selectedCell,
    currentDirection,
    activeClue,
    cellStates,
    gridState,
    isComplete,
    completionPercentage,

    // Actions
    loadPuzzle,
    clearPuzzle,
    setCellValue,
    clearCell,
    resetGrid,
    selectCell,
    toggleDirection,
    selectClue,
    setActiveClue,
  };
}
