/**
 * Custom hook for managing AI assistance features.
 * 
 * This hook provides AI-powered solving assistance including:
 * - Solve entire puzzle with AI
 * - Solve individual words with AI
 * - Get hints for words
 * - Confirmation dialogs for destructive actions
 * - Animation and feedback for AI solutions
 * 
 * It integrates with the puzzle state management and API client
 * to provide a seamless AI assistance experience.
 */

import { useState, useCallback } from 'react';
import { apiClient } from '../services/api';
import type { HintType } from '../types/puzzle';
import type { SolveResponse, HintResponse } from '../types/api';

/**
 * State for hint modal display.
 */
export interface HintModalState {
  /** Whether the hint modal is visible */
  isVisible: boolean;
  /** The hint text to display */
  hint: string;
  /** Type of hint provided */
  hintType: HintType;
  /** Revealed letter (if hint type is 'letter') */
  revealedLetter: string | null;
  /** Position of revealed letter (if applicable) */
  position: number | null;
  /** Clue information for context */
  clueInfo: { number: number; direction: string; text: string };
}

/**
 * State for confirmation dialog.
 */
export interface ConfirmationDialogState {
  /** Whether the dialog is visible */
  isVisible: boolean;
  /** Title of the dialog */
  title: string;
  /** Message to display */
  message: string;
  /** Type of action (affects styling) */
  actionType: 'solve-word' | 'solve-puzzle';
  /** Callback when user confirms */
  onConfirm: () => void;
  /** Callback when user cancels */
  onCancel: () => void;
}

/**
 * State for solution animation.
 */
export interface SolutionAnimationState {
  /** Whether animation is active */
  isActive: boolean;
  /** Type of solution being animated */
  type: 'word' | 'puzzle';
  /** Cells being animated */
  cells: Array<{ row: number; col: number; value: string }>;
  /** Current animation step */
  currentStep: number;
}

/**
 * Hook for managing AI assistance features.
 * 
 * @param puzzleId - Current puzzle ID
 * @param activeClue - Currently active clue
 * @param setCellValue - Function to update cell values
 * @returns Object with AI assistance state and functions
 */
export function useAIAssistance(
  puzzleId: string | null,
  activeClue: { number: number; direction: 'across' | 'down' } | null,
  setCellValue: (row: number, col: number, value: string | null) => void
) {
  // Loading states
  const [isSolvingWord, setIsSolvingWord] = useState(false);
  const [isSolvingPuzzle, setIsSolvingPuzzle] = useState(false);
  const [isGettingHint, setIsGettingHint] = useState(false);

  // Error states
  const [solveWordError, setSolveWordError] = useState<string | null>(null);
  const [solvePuzzleError, setSolvePuzzleError] = useState<string | null>(null);
  const [hintError, setHintError] = useState<string | null>(null);

  // Modal states
  const [hintModal, setHintModal] = useState<HintModalState | null>(null);
  const [confirmationDialog, setConfirmationDialog] = useState<ConfirmationDialogState | null>(null);
  const [solutionAnimation, setSolutionAnimation] = useState<SolutionAnimationState | null>(null);

  /**
   * Show confirmation dialog for solve word action.
   */
  const showSolveWordConfirmation = useCallback(() => {
    if (!activeClue) return;

    setConfirmationDialog({
      isVisible: true,
      title: 'Solve Word with AI',
      message: `Are you sure you want AI to solve ${activeClue.number} ${activeClue.direction}? This will overwrite your current answer for this word.`,
      actionType: 'solve-word',
      onConfirm: () => {
        setConfirmationDialog(null);
        executeSolveWord();
      },
      onCancel: () => {
        setConfirmationDialog(null);
      },
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeClue]);

  /**
   * Show confirmation dialog for solve puzzle action.
   */
  const showSolvePuzzleConfirmation = useCallback(() => {
    setConfirmationDialog({
      isVisible: true,
      title: 'Solve Entire Puzzle with AI',
      message: 'Are you sure you want AI to solve the entire puzzle? This will overwrite all your current answers.',
      actionType: 'solve-puzzle',
      onConfirm: () => {
        setConfirmationDialog(null);
        executeSolvePuzzle();
      },
      onCancel: () => {
        setConfirmationDialog(null);
      },
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Execute solve word API call.
   */
  const executeSolveWord = useCallback(async () => {
    if (!puzzleId || !activeClue) return;

    setIsSolvingWord(true);
    setSolveWordError(null);

    try {
      const response: SolveResponse = await apiClient.solveWord(puzzleId, {
        clue_number: activeClue.number,
        direction: activeClue.direction,
        use_intersections: true,
      });

      if (response.success && response.updated_cells && response.updated_cells.length > 0) {
        // Start animation
        setSolutionAnimation({
          isActive: true,
          type: 'word',
          cells: response.updated_cells.map(cell => ({
            row: cell.row,
            col: cell.col,
            value: cell.value || '',
          })),
          currentStep: 0,
        });

        // Animate cells one by one
        let step = 0;
        const animationInterval = setInterval(() => {
          if (step < response.updated_cells.length) {
            const cell = response.updated_cells[step];
            if (cell.value) {
              setCellValue(cell.row, cell.col, cell.value);
            }
            step++;
            setSolutionAnimation(prev => prev ? { ...prev, currentStep: step } : null);
          } else {
            clearInterval(animationInterval);
            // End animation after a brief delay
            setTimeout(() => {
              setSolutionAnimation(null);
            }, 500);
          }
        }, 150); // 150ms between each letter
      } else {
        setSolveWordError(response.reasoning || 'Failed to solve word');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to solve word';
      setSolveWordError(errorMessage);
    } finally {
      setIsSolvingWord(false);
    }
  }, [puzzleId, activeClue, setCellValue]);

  /**
   * Execute solve puzzle API call.
   */
  const executeSolvePuzzle = useCallback(async () => {
    if (!puzzleId) return;

    setIsSolvingPuzzle(true);
    setSolvePuzzleError(null);

    try {
      const response: SolveResponse = await apiClient.solvePuzzle(puzzleId, {
        use_hints: true,
      });

      if (response.success && response.updated_cells && response.updated_cells.length > 0) {
        // Start animation
        setSolutionAnimation({
          isActive: true,
          type: 'puzzle',
          cells: response.updated_cells.map(cell => ({
            row: cell.row,
            col: cell.col,
            value: cell.value || '',
          })),
          currentStep: 0,
        });

        // Animate cells in batches for faster completion
        let step = 0;
        const batchSize = 3; // Fill 3 cells at a time
        const animationInterval = setInterval(() => {
          const endStep = Math.min(step + batchSize, response.updated_cells.length);
          
          for (let i = step; i < endStep; i++) {
            const cell = response.updated_cells[i];
            if (cell.value) {
              setCellValue(cell.row, cell.col, cell.value);
            }
          }
          
          step = endStep;
          setSolutionAnimation(prev => prev ? { ...prev, currentStep: step } : null);

          if (step >= response.updated_cells.length) {
            clearInterval(animationInterval);
            // End animation after a brief delay
            setTimeout(() => {
              setSolutionAnimation(null);
            }, 1000);
          }
        }, 100); // 100ms between batches
      } else {
        setSolvePuzzleError(response.reasoning || 'Failed to solve puzzle');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to solve puzzle';
      setSolvePuzzleError(errorMessage);
    } finally {
      setIsSolvingPuzzle(false);
    }
  }, [puzzleId, setCellValue]);

  /**
   * Get a hint for the current word.
   */
  const getHint = useCallback(async (hintType: HintType = 'definition', clueText: string = '') => {
    if (!puzzleId || !activeClue) return;

    setIsGettingHint(true);
    setHintError(null);

    try {
      const response: HintResponse = await apiClient.getHint(puzzleId, {
        clue_number: activeClue.number,
        direction: activeClue.direction,
        hint_type: hintType,
      });

      if (response.success) {
        setHintModal({
          isVisible: true,
          hint: response.hint,
          hintType: response.hint_type as HintType,
          revealedLetter: response.revealed_letter,
          position: response.position,
          clueInfo: {
            number: activeClue.number,
            direction: activeClue.direction,
            text: clueText,
          },
        });
      } else {
        setHintError('Failed to generate hint');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get hint';
      setHintError(errorMessage);
    } finally {
      setIsGettingHint(false);
    }
  }, [puzzleId, activeClue]);

  /**
   * Close the hint modal.
   */
  const closeHintModal = useCallback(() => {
    setHintModal(null);
  }, []);

  /**
   * Close the confirmation dialog.
   */
  const closeConfirmationDialog = useCallback(() => {
    setConfirmationDialog(null);
  }, []);

  /**
   * Clear all errors.
   */
  const clearErrors = useCallback(() => {
    setSolveWordError(null);
    setSolvePuzzleError(null);
    setHintError(null);
  }, []);

  /**
   * Check if any AI operation is in progress.
   */
  const isAnyOperationInProgress = isSolvingWord || isSolvingPuzzle || isGettingHint;

  return {
    // Loading states
    isSolvingWord,
    isSolvingPuzzle,
    isGettingHint,
    isAnyOperationInProgress,

    // Error states
    solveWordError,
    solvePuzzleError,
    hintError,

    // Modal states
    hintModal,
    confirmationDialog,
    solutionAnimation,

    // Actions
    showSolveWordConfirmation,
    showSolvePuzzleConfirmation,
    getHint,
    closeHintModal,
    closeConfirmationDialog,
    clearErrors,
  };
}

export default useAIAssistance;
