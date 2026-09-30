/**
 * Custom hook for managing manual puzzle solving state and logic.
 * 
 * This hook extends usePuzzle with solving-specific functionality:
 * - Word completion detection
 * - Progress tracking
 * - Validation helpers
 * - Solving statistics
 * 
 * It provides a clean API for components that need solving-specific features
 * without cluttering the base usePuzzle hook.
 */

import { useMemo, useCallback } from 'react';
import { usePuzzle } from './usePuzzle';
import type { Clue, Direction } from '../types/puzzle';
import { getWordCells, isWordComplete, getWordText } from '../utils/grid';

/**
 * Statistics about the current solving session.
 */
export interface SolvingStats {
  /** Total number of words in puzzle */
  totalWords: number;
  /** Number of completed words */
  completedWords: number;
  /** Percentage of words completed (0-100) */
  wordsCompletionPercentage: number;
  /** Total number of fillable cells */
  totalCells: number;
  /** Number of filled cells */
  filledCells: number;
  /** Percentage of cells filled (0-100) */
  cellsCompletionPercentage: number;
  /** Whether all words are complete */
  isFullyComplete: boolean;
}

/**
 * Information about a word's completion status.
 */
export interface WordCompletionInfo {
  /** The clue for this word */
  clue: Clue;
  /** Whether all cells in the word are filled */
  isComplete: boolean;
  /** Current text in the word (with underscores for empty cells) */
  currentText: string;
  /** Number of filled cells */
  filledCount: number;
  /** Total length of the word */
  totalLength: number;
}

/**
 * Hook for managing puzzle solving state and logic.
 * 
 * @returns Object with solving state and manipulation functions
 */
export function useSolving() {
  // Get base puzzle state from usePuzzle
  const puzzleState = usePuzzle();
  const { puzzle, userCells } = puzzleState;

  /**
   * Get completion info for a specific word.
   */
  const getWordCompletionInfo = useCallback(
    (clue: Clue): WordCompletionInfo => {
      const wordCells = getWordCells(userCells, clue);
      const isComplete = isWordComplete(wordCells);
      const currentText = getWordText(wordCells);
      const filledCount = wordCells.filter(
        (cell) => cell.value !== null && cell.value !== ''
      ).length;

      return {
        clue,
        isComplete,
        currentText,
        filledCount,
        totalLength: clue.length,
      };
    },
    [userCells]
  );

  /**
   * Get completion info for all words.
   */
  const allWordsCompletionInfo = useMemo((): WordCompletionInfo[] => {
    if (!puzzle) return [];

    const allClues = [...puzzle.clues_across, ...puzzle.clues_down];
    return allClues.map((clue) => getWordCompletionInfo(clue));
  }, [puzzle, getWordCompletionInfo]);

  /**
   * Get list of completed words.
   */
  const completedWords = useMemo((): WordCompletionInfo[] => {
    return allWordsCompletionInfo.filter((info) => info.isComplete);
  }, [allWordsCompletionInfo]);

  /**
   * Get list of incomplete words.
   */
  const incompleteWords = useMemo((): WordCompletionInfo[] => {
    return allWordsCompletionInfo.filter((info) => !info.isComplete);
  }, [allWordsCompletionInfo]);

  /**
   * Check if a specific word is complete.
   */
  const isWordCompleteByClue = useCallback(
    (clueNumber: number, direction: Direction): boolean => {
      if (!puzzle) return false;

      const clues = direction === 'across' ? puzzle.clues_across : puzzle.clues_down;
      const clue = clues.find((c) => c.number === clueNumber);

      if (!clue) return false;

      const wordCells = getWordCells(userCells, clue);
      return isWordComplete(wordCells);
    },
    [puzzle, userCells]
  );

  /**
   * Get solving statistics.
   */
  const solvingStats = useMemo((): SolvingStats => {
    if (!puzzle || userCells.length === 0) {
      return {
        totalWords: 0,
        completedWords: 0,
        wordsCompletionPercentage: 0,
        totalCells: 0,
        filledCells: 0,
        cellsCompletionPercentage: 0,
        isFullyComplete: false,
      };
    }

    const totalWords = puzzle.clues_across.length + puzzle.clues_down.length;
    const completedWordsCount = completedWords.length;
    const wordsCompletionPercentage =
      totalWords > 0 ? (completedWordsCount / totalWords) * 100 : 0;

    const fillableCells = userCells.filter((cell) => !cell.is_blocked);
    const totalCells = fillableCells.length;
    const filledCells = fillableCells.filter(
      (cell) => cell.value !== null && cell.value !== ''
    ).length;
    const cellsCompletionPercentage = totalCells > 0 ? (filledCells / totalCells) * 100 : 0;

    const isFullyComplete = completedWordsCount === totalWords && totalWords > 0;

    return {
      totalWords,
      completedWords: completedWordsCount,
      wordsCompletionPercentage,
      totalCells,
      filledCells,
      cellsCompletionPercentage,
      isFullyComplete,
    };
  }, [puzzle, userCells, completedWords]);

  /**
   * Get cells that belong to completed words.
   */
  const completedWordCells = useMemo((): Set<string> => {
    const cellSet = new Set<string>();

    completedWords.forEach((wordInfo) => {
      const wordCells = getWordCells(userCells, wordInfo.clue);
      wordCells.forEach((cell) => {
        cellSet.add(`${cell.row},${cell.col}`);
      });
    });

    return cellSet;
  }, [completedWords, userCells]);

  /**
   * Check if a specific cell is part of a completed word.
   */
  const isCellInCompletedWord = useCallback(
    (row: number, col: number): boolean => {
      return completedWordCells.has(`${row},${col}`);
    },
    [completedWordCells]
  );

  /**
   * Get the next incomplete word (for auto-navigation).
   */
  const getNextIncompleteWord = useCallback((): WordCompletionInfo | null => {
    if (incompleteWords.length === 0) return null;

    // Find the first incomplete word with at least one filled cell
    const partiallyFilled = incompleteWords.find((info) => info.filledCount > 0);
    if (partiallyFilled) return partiallyFilled;

    // Otherwise return the first incomplete word
    return incompleteWords[0];
  }, [incompleteWords]);

  /**
   * Clear all user input (reset to empty grid).
   */
  const clearAllInput = useCallback(() => {
    puzzleState.resetGrid();
  }, [puzzleState]);

  /**
   * Clear a specific word.
   */
  const clearWord = useCallback(
    (clueNumber: number, direction: Direction) => {
      if (!puzzle) return;

      const clues = direction === 'across' ? puzzle.clues_across : puzzle.clues_down;
      const clue = clues.find((c) => c.number === clueNumber);

      if (!clue) return;

      const wordCells = getWordCells(userCells, clue);
      wordCells.forEach((cell) => {
        puzzleState.clearCell(cell.row, cell.col);
      });
    },
    [puzzle, userCells, puzzleState]
  );

  /**
   * Fill a word with specific text.
   */
  const fillWord = useCallback(
    (clueNumber: number, direction: Direction, text: string) => {
      if (!puzzle) return;

      const clues = direction === 'across' ? puzzle.clues_across : puzzle.clues_down;
      const clue = clues.find((c) => c.number === clueNumber);

      if (!clue) return;

      const wordCells = getWordCells(userCells, clue);
      const letters = text.toUpperCase().split('');

      wordCells.forEach((cell, index) => {
        if (index < letters.length) {
          puzzleState.setCellValue(cell.row, cell.col, letters[index]);
        }
      });
    },
    [puzzle, userCells, puzzleState]
  );

  return {
    // Re-export all base puzzle state
    ...puzzleState,

    // Solving-specific state
    solvingStats,
    completedWords,
    incompleteWords,
    allWordsCompletionInfo,
    completedWordCells,

    // Solving-specific functions
    getWordCompletionInfo,
    isWordCompleteByClue,
    isCellInCompletedWord,
    getNextIncompleteWord,
    clearAllInput,
    clearWord,
    fillWord,
  };
}

export default useSolving;
