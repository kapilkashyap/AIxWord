/**
 * Unit tests for useAIAssistance hook.
 * 
 * Tests cover:
 * - Initial state
 * - Solve word confirmation and execution
 * - Solve puzzle confirmation and execution
 * - Get hint functionality
 * - Error handling for all operations
 * - Modal state management
 * - Animation state management
 * - Loading states
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAIAssistance } from '../useAIAssistance';
import { apiClient } from '../../services/api';
import type { SolveResponse, HintResponse } from '../../types/api';

// Mock the API client
vi.mock('../../services/api', () => ({
  apiClient: {
    solveWord: vi.fn(),
    solvePuzzle: vi.fn(),
    getHint: vi.fn(),
  },
}));

describe('useAIAssistance Hook', () => {
  const mockPuzzleId = 'test-puzzle-123';
  const mockActiveClue = { number: 1, direction: 'across' as const };
  const mockSetCellValue = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  describe('Initial State', () => {
    it('should initialize with correct default state', () => {
      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      expect(result.current.isSolvingWord).toBe(false);
      expect(result.current.isSolvingPuzzle).toBe(false);
      expect(result.current.isGettingHint).toBe(false);
      expect(result.current.isAnyOperationInProgress).toBe(false);
      expect(result.current.solveWordError).toBeNull();
      expect(result.current.solvePuzzleError).toBeNull();
      expect(result.current.hintError).toBeNull();
      expect(result.current.hintModal).toBeNull();
      expect(result.current.confirmationDialog).toBeNull();
      expect(result.current.solutionAnimation).toBeNull();
    });
  });

  describe('Solve Word Confirmation', () => {
    it('should show confirmation dialog when showSolveWordConfirmation is called', () => {
      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      act(() => {
        result.current.showSolveWordConfirmation();
      });

      expect(result.current.confirmationDialog).not.toBeNull();
      expect(result.current.confirmationDialog?.isVisible).toBe(true);
      expect(result.current.confirmationDialog?.title).toBe('Solve Word with AI');
      expect(result.current.confirmationDialog?.message).toContain('1 across');
      expect(result.current.confirmationDialog?.actionType).toBe('solve-word');
    });

    it('should not show confirmation dialog if no active clue', () => {
      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, null, mockSetCellValue)
      );

      act(() => {
        result.current.showSolveWordConfirmation();
      });

      expect(result.current.confirmationDialog).toBeNull();
    });

    it('should close confirmation dialog when onCancel is called', () => {
      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      act(() => {
        result.current.showSolveWordConfirmation();
      });

      expect(result.current.confirmationDialog).not.toBeNull();

      act(() => {
        result.current.confirmationDialog?.onCancel();
      });

      expect(result.current.confirmationDialog).toBeNull();
    });
  });

  describe('Solve Word Execution', () => {
    // Note: The successful solve tests are covered by integration tests
    // The hook's internal callback dependencies make unit testing the success path complex

    it('should handle solve word API error', async () => {
      const errorMessage = 'Failed to solve word';
      vi.mocked(apiClient.solveWord).mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      act(() => {
        result.current.showSolveWordConfirmation();
      });

      const onConfirm = result.current.confirmationDialog?.onConfirm;

      await act(async () => {
        onConfirm!();
        await vi.runAllTimersAsync();
      });

      expect(result.current.solveWordError).toBe(errorMessage);
      expect(mockSetCellValue).not.toHaveBeenCalled();
    }, 10000);

    it('should handle unsuccessful solve response', async () => {
      const mockResponse: SolveResponse = {
        success: false,
        answer: null,
        confidence: 0,
        reasoning: 'Could not find suitable answer',
        updated_cells: [],
      };

      vi.mocked(apiClient.solveWord).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      act(() => {
        result.current.showSolveWordConfirmation();
      });

      const onConfirm = result.current.confirmationDialog?.onConfirm;

      await act(async () => {
        onConfirm!();
        await vi.runAllTimersAsync();
      });

      expect(result.current.solveWordError).toBe('Could not find suitable answer');
      expect(mockSetCellValue).not.toHaveBeenCalled();
    }, 10000);

    it('should not execute if no puzzle ID', async () => {
      const { result } = renderHook(() =>
        useAIAssistance(null, mockActiveClue, mockSetCellValue)
      );

      act(() => {
        result.current.showSolveWordConfirmation();
      });

      const onConfirm = result.current.confirmationDialog?.onConfirm;

      await act(async () => {
        onConfirm!();
        await vi.runAllTimersAsync();
      });

      expect(apiClient.solveWord).not.toHaveBeenCalled();
    }, 10000);
  });

  describe('Solve Puzzle Confirmation', () => {
    it('should show confirmation dialog when showSolvePuzzleConfirmation is called', () => {
      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      act(() => {
        result.current.showSolvePuzzleConfirmation();
      });

      expect(result.current.confirmationDialog).not.toBeNull();
      expect(result.current.confirmationDialog?.isVisible).toBe(true);
      expect(result.current.confirmationDialog?.title).toBe('Solve Entire Puzzle with AI');
      expect(result.current.confirmationDialog?.message).toContain('entire puzzle');
      expect(result.current.confirmationDialog?.actionType).toBe('solve-puzzle');
    });
  });

  describe('Solve Puzzle Execution', () => {
    // Note: The successful solve tests are covered by integration tests
    // The hook's internal callback dependencies make unit testing the success path complex

    it('should handle solve puzzle API error', async () => {
      const errorMessage = 'Failed to solve puzzle';
      vi.mocked(apiClient.solvePuzzle).mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      act(() => {
        result.current.showSolvePuzzleConfirmation();
      });

      const onConfirm = result.current.confirmationDialog?.onConfirm;

      await act(async () => {
        onConfirm!();
        await vi.runAllTimersAsync();
      });

      expect(result.current.solvePuzzleError).toBe(errorMessage);
      expect(mockSetCellValue).not.toHaveBeenCalled();
    }, 10000);
  });

  describe('Get Hint', () => {
    it('should successfully get a definition hint', async () => {
      const mockResponse: HintResponse = {
        success: true,
        hint: 'A four-legged animal that barks',
        hint_type: 'definition',
        revealed_letter: null,
        position: null,
      };

      vi.mocked(apiClient.getHint).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      await act(async () => {
        await result.current.getHint('definition', 'Pet animal');
      });

      expect(result.current.isGettingHint).toBe(false);
      expect(result.current.hintModal).not.toBeNull();
      expect(result.current.hintModal?.isVisible).toBe(true);
      expect(result.current.hintModal?.hint).toBe('A four-legged animal that barks');
      expect(result.current.hintModal?.hintType).toBe('definition');
      expect(result.current.hintModal?.clueInfo.number).toBe(1);
      expect(result.current.hintModal?.clueInfo.direction).toBe('across');

      expect(apiClient.getHint).toHaveBeenCalledWith(mockPuzzleId, {
        clue_number: 1,
        direction: 'across',
        hint_type: 'definition',
      });
    });

    it('should successfully get a letter hint', async () => {
      const mockResponse: HintResponse = {
        success: true,
        hint: 'The first letter is revealed',
        hint_type: 'letter',
        revealed_letter: 'D',
        position: 0,
      };

      vi.mocked(apiClient.getHint).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      await act(async () => {
        await result.current.getHint('letter', 'Pet animal');
      });

      expect(result.current.hintModal).not.toBeNull();
      expect(result.current.hintModal?.hintType).toBe('letter');
      expect(result.current.hintModal?.revealedLetter).toBe('D');
      expect(result.current.hintModal?.position).toBe(0);
    });

    it('should handle get hint API error', async () => {
      const errorMessage = 'Failed to generate hint';
      vi.mocked(apiClient.getHint).mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      await act(async () => {
        await result.current.getHint('definition');
      });

      expect(result.current.hintError).toBe(errorMessage);
      expect(result.current.hintModal).toBeNull();
    });

    it('should handle unsuccessful hint response', async () => {
      const mockResponse: HintResponse = {
        success: false,
        hint: '',
        hint_type: 'definition',
        revealed_letter: null,
        position: null,
      };

      vi.mocked(apiClient.getHint).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      await act(async () => {
        await result.current.getHint();
      });

      expect(result.current.hintError).toBe('Failed to generate hint');
      expect(result.current.hintModal).toBeNull();
    });

    it('should not execute if no puzzle ID', async () => {
      const { result } = renderHook(() =>
        useAIAssistance(null, mockActiveClue, mockSetCellValue)
      );

      await act(async () => {
        await result.current.getHint();
      });

      expect(apiClient.getHint).not.toHaveBeenCalled();
    });

    it('should not execute if no active clue', async () => {
      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, null, mockSetCellValue)
      );

      await act(async () => {
        await result.current.getHint();
      });

      expect(apiClient.getHint).not.toHaveBeenCalled();
    });
  });

  describe('Modal Management', () => {
    it('should close hint modal when closeHintModal is called', async () => {
      const mockResponse: HintResponse = {
        success: true,
        hint: 'Test hint',
        hint_type: 'definition',
        revealed_letter: null,
        position: null,
      };

      vi.mocked(apiClient.getHint).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      await act(async () => {
        await result.current.getHint();
      });

      expect(result.current.hintModal).not.toBeNull();

      act(() => {
        result.current.closeHintModal();
      });

      expect(result.current.hintModal).toBeNull();
    });

    it('should close confirmation dialog when closeConfirmationDialog is called', () => {
      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      act(() => {
        result.current.showSolveWordConfirmation();
      });

      expect(result.current.confirmationDialog).not.toBeNull();

      act(() => {
        result.current.closeConfirmationDialog();
      });

      expect(result.current.confirmationDialog).toBeNull();
    });
  });

  describe('Error Management', () => {
    it('should clear all errors when clearErrors is called', async () => {
      vi.mocked(apiClient.solveWord).mockRejectedValue(new Error('Solve word error'));
      vi.mocked(apiClient.getHint).mockRejectedValue(new Error('Hint error'));

      const { result } = renderHook(() =>
        useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
      );

      // Trigger solve word error
      act(() => {
        result.current.showSolveWordConfirmation();
      });
      const onConfirm = result.current.confirmationDialog?.onConfirm;
      await act(async () => {
        onConfirm!();
        await vi.runAllTimersAsync();
      });

      // Trigger hint error
      await act(async () => {
        await result.current.getHint();
      });

      expect(result.current.solveWordError).toBe('Solve word error');
      expect(result.current.hintError).toBe('Hint error');

      // Clear all errors
      act(() => {
        result.current.clearErrors();
      });

      expect(result.current.solveWordError).toBeNull();
      expect(result.current.solvePuzzleError).toBeNull();
      expect(result.current.hintError).toBeNull();
    }, 10000);
  });
});
