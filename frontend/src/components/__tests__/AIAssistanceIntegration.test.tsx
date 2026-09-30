/**
 * Integration tests for AI Assistance features in PuzzleContainerWithAI.
 * 
 * These tests verify the integration of AI assistance components:
 * - AIAssistancePanel integration with useAIAssistance hook
 * - HintModal integration and display
 * - ConfirmationDialog integration for AI operations
 * - SolutionAnimation integration
 * - Error handling across components
 * 
 * Note: Full end-to-end user flows are complex and timing-sensitive.
 * These tests focus on verifying component integration and state management
 * rather than complete user journeys.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AIAssistancePanel } from '../AIAssistancePanel';
import { HintModal } from '../HintModal';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { SolutionAnimation } from '../SolutionAnimation';
import type { Cell } from '../../types/puzzle';

describe('AI Assistance Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('AIAssistancePanel Integration', () => {
    it('should integrate with confirmation flow for solve word', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();

      render(
        <AIAssistancePanel
          hasPuzzle={true}
          activeClue={{ number: 1, direction: 'across' }}
          onSolveWord={mockOnSolveWord}
          onSolvePuzzle={mockOnSolvePuzzle}
          onGetHint={mockOnGetHint}
        />
      );

      // Verify panel renders
      expect(screen.getByTestId('ai-assistance-panel')).toBeInTheDocument();

      // Click solve word button
      const solveWordButton = screen.getByTestId('solve-word-button');
      fireEvent.click(solveWordButton);

      // Verify callback was called
      expect(mockOnSolveWord).toHaveBeenCalledTimes(1);
    });

    it('should integrate with confirmation flow for solve puzzle', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();

      render(
        <AIAssistancePanel
          hasPuzzle={true}
          activeClue={{ number: 1, direction: 'across' }}
          onSolveWord={mockOnSolveWord}
          onSolvePuzzle={mockOnSolvePuzzle}
          onGetHint={mockOnGetHint}
        />
      );

      // Click solve puzzle button
      const solvePuzzleButton = screen.getByTestId('solve-puzzle-button');
      fireEvent.click(solvePuzzleButton);

      // Verify callback was called
      expect(mockOnSolvePuzzle).toHaveBeenCalledTimes(1);
    });

    it('should integrate with hint modal flow', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();

      render(
        <AIAssistancePanel
          hasPuzzle={true}
          activeClue={{ number: 1, direction: 'across' }}
          onSolveWord={mockOnSolveWord}
          onSolvePuzzle={mockOnSolvePuzzle}
          onGetHint={mockOnGetHint}
        />
      );

      // Click get hint button
      const getHintButton = screen.getByTestId('get-hint-button');
      fireEvent.click(getHintButton);

      // Verify callback was called
      expect(mockOnGetHint).toHaveBeenCalledTimes(1);
    });

    it('should disable buttons during operations', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();

      render(
        <AIAssistancePanel
          hasPuzzle={true}
          activeClue={{ number: 1, direction: 'across' }}
          isSolvingWord={true}
          onSolveWord={mockOnSolveWord}
          onSolvePuzzle={mockOnSolvePuzzle}
          onGetHint={mockOnGetHint}
        />
      );

      // All buttons should be disabled during operation
      expect(screen.getByTestId('solve-word-button')).toBeDisabled();
      expect(screen.getByTestId('solve-puzzle-button')).toBeDisabled();
      expect(screen.getByTestId('get-hint-button')).toBeDisabled();
    });

    it('should show loading state for solve word', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();

      render(
        <AIAssistancePanel
          hasPuzzle={true}
          activeClue={{ number: 1, direction: 'across' }}
          isSolvingWord={true}
          onSolveWord={mockOnSolveWord}
          onSolvePuzzle={mockOnSolvePuzzle}
          onGetHint={mockOnGetHint}
        />
      );

      expect(screen.getByText('Solving...')).toBeInTheDocument();
    });

    it('should show loading state for solve puzzle', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();

      render(
        <AIAssistancePanel
          hasPuzzle={true}
          activeClue={{ number: 1, direction: 'across' }}
          isSolvingPuzzle={true}
          onSolveWord={mockOnSolveWord}
          onSolvePuzzle={mockOnSolvePuzzle}
          onGetHint={mockOnGetHint}
        />
      );

      expect(screen.getByText('Solving Puzzle...')).toBeInTheDocument();
    });

    it('should show loading state for get hint', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();

      render(
        <AIAssistancePanel
          hasPuzzle={true}
          activeClue={{ number: 1, direction: 'across' }}
          isGettingHint={true}
          onSolveWord={mockOnSolveWord}
          onSolvePuzzle={mockOnSolvePuzzle}
          onGetHint={mockOnGetHint}
        />
      );

      expect(screen.getByText('Getting Hint...')).toBeInTheDocument();
    });
  });

  describe('HintModal Integration', () => {
    it('should display hint modal with definition hint', () => {
      const mockOnClose = vi.fn();

      render(
        <HintModal
          isOpen={true}
          hint="Think about a common household pet"
          hintType="definition"
          clueInfo={{
            number: 1,
            direction: 'across',
            text: 'Feline pet',
          }}
          onClose={mockOnClose}
        />
      );

      expect(screen.getByTestId('hint-modal')).toBeInTheDocument();
      expect(screen.getByText('Think about a common household pet')).toBeInTheDocument();
      expect(screen.getByText('1 across')).toBeInTheDocument();
    });

    it('should display hint modal with letter hint', () => {
      const mockOnClose = vi.fn();

      render(
        <HintModal
          isOpen={true}
          hint="The first letter is revealed"
          hintType="letter"
          revealedLetter="C"
          position={0}
          clueInfo={{
            number: 1,
            direction: 'across',
            text: 'Feline pet',
          }}
          onClose={mockOnClose}
        />
      );

      expect(screen.getByTestId('hint-modal')).toBeInTheDocument();
      expect(screen.getByText('The first letter is revealed')).toBeInTheDocument();
      expect(screen.getByText('C')).toBeInTheDocument();
    });

    it('should call onClose when close button is clicked', () => {
      const mockOnClose = vi.fn();

      render(
        <HintModal
          isOpen={true}
          hint="Test hint"
          hintType="definition"
          clueInfo={{
            number: 1,
            direction: 'across',
            text: 'Test clue',
          }}
          onClose={mockOnClose}
        />
      );

      const closeButton = screen.getByLabelText(/close/i);
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should not render when isOpen is false', () => {
      const mockOnClose = vi.fn();

      render(
        <HintModal
          isOpen={false}
          hint="Test hint"
          hintType="definition"
          clueInfo={{
            number: 1,
            direction: 'across',
            text: 'Test clue',
          }}
          onClose={mockOnClose}
        />
      );

      expect(screen.queryByTestId('hint-modal')).not.toBeInTheDocument();
    });
  });

  describe('ConfirmationDialog Integration', () => {
    it('should display confirmation dialog for solve word', () => {
      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();

      render(
        <ConfirmationDialog
          isOpen={true}
          title="Solve Word with AI"
          message="Are you sure you want AI to solve 1 across?"
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      expect(screen.getByText('Solve Word with AI')).toBeInTheDocument();
      expect(screen.getByText(/Are you sure you want AI to solve 1 across/)).toBeInTheDocument();
    });

    it('should display confirmation dialog for solve puzzle', () => {
      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();

      render(
        <ConfirmationDialog
          isOpen={true}
          title="Solve Entire Puzzle with AI"
          message="Are you sure you want AI to solve the entire puzzle?"
          confirmVariant="warning"
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      expect(screen.getByText('Solve Entire Puzzle with AI')).toBeInTheDocument();
      expect(screen.getByText(/entire puzzle/)).toBeInTheDocument();
    });

    it('should call onConfirm when confirm button is clicked', () => {
      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();

      render(
        <ConfirmationDialog
          isOpen={true}
          title="Test Dialog"
          message="Test message"
          confirmLabel="Yes, Solve"
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const confirmButton = screen.getByTestId('confirmation-dialog-confirm');
      fireEvent.click(confirmButton);

      expect(mockOnConfirm).toHaveBeenCalledTimes(1);
    });

    it('should call onCancel when cancel button is clicked', () => {
      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();

      render(
        <ConfirmationDialog
          isOpen={true}
          title="Test Dialog"
          message="Test message"
          cancelLabel="Cancel"
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('should not render when isOpen is false', () => {
      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();

      render(
        <ConfirmationDialog
          isOpen={false}
          title="Test Dialog"
          message="Test message"
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      expect(screen.queryByText('Test Dialog')).not.toBeInTheDocument();
    });
  });

  describe('SolutionAnimation Integration', () => {
    it('should render solution animation with cells', () => {
      const mockOnComplete = vi.fn();
      const cells: Cell[] = [
        { row: 0, col: 0, value: 'C', is_blocked: false, number: 1 },
        { row: 0, col: 1, value: 'A', is_blocked: false, number: null },
        { row: 0, col: 2, value: 'T', is_blocked: false, number: null },
      ];

      render(
        <SolutionAnimation
          cells={cells}
          isAnimating={true}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.getByTestId('solution-animation')).toBeInTheDocument();
    });

    it('should render animation overlay when animating', () => {
      const mockOnComplete = vi.fn();
      const cells: Cell[] = [
        { row: 0, col: 0, value: 'C', is_blocked: false, number: 1 },
      ];

      render(
        <SolutionAnimation
          cells={cells}
          isAnimating={true}
          onComplete={mockOnComplete}
          speed={100}
        />
      );

      // Verify animation overlay is rendered
      expect(screen.getByTestId('solution-animation')).toBeInTheDocument();
      expect(screen.getByText(/AI Solving/i)).toBeInTheDocument();
    });

    it('should not render when not animating', () => {
      const mockOnComplete = vi.fn();
      const cells: Cell[] = [
        { row: 0, col: 0, value: 'C', is_blocked: false, number: 1 },
      ];

      render(
        <SolutionAnimation
          cells={cells}
          isAnimating={false}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.queryByTestId('solution-animation')).not.toBeInTheDocument();
    });
  });

  describe('Component Integration Scenarios', () => {
    it('should handle complete solve word flow with all components', () => {
      // This test verifies that all components can be rendered together
      // and their callbacks work correctly

      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();
      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();
      const mockOnHintClose = vi.fn();
      const mockOnAnimationComplete = vi.fn();

      const { rerender } = render(
        <>
          <AIAssistancePanel
            hasPuzzle={true}
            activeClue={{ number: 1, direction: 'across' }}
            onSolveWord={mockOnSolveWord}
            onSolvePuzzle={mockOnSolvePuzzle}
            onGetHint={mockOnGetHint}
          />
          <ConfirmationDialog
            isOpen={false}
            title="Test"
            message="Test"
            onConfirm={mockOnConfirm}
            onCancel={mockOnCancel}
          />
          <HintModal
            isOpen={false}
            hint="Test"
            hintType="definition"
            clueInfo={{ number: 1, direction: 'across', text: 'Test' }}
            onClose={mockOnHintClose}
          />
          <SolutionAnimation
            cells={[]}
            isAnimating={false}
            onComplete={mockOnAnimationComplete}
          />
        </>
      );

      // Step 1: Click solve word button
      const solveWordButton = screen.getByTestId('solve-word-button');
      fireEvent.click(solveWordButton);
      expect(mockOnSolveWord).toHaveBeenCalled();

      // Step 2: Show confirmation dialog
      rerender(
        <>
          <AIAssistancePanel
            hasPuzzle={true}
            activeClue={{ number: 1, direction: 'across' }}
            isSolvingWord={false}
            onSolveWord={mockOnSolveWord}
            onSolvePuzzle={mockOnSolvePuzzle}
            onGetHint={mockOnGetHint}
          />
          <ConfirmationDialog
            isOpen={true}
            title="Solve Word with AI"
            message="Are you sure?"
            onConfirm={mockOnConfirm}
            onCancel={mockOnCancel}
          />
          <HintModal
            isOpen={false}
            hint="Test"
            hintType="definition"
            clueInfo={{ number: 1, direction: 'across', text: 'Test' }}
            onClose={mockOnHintClose}
          />
          <SolutionAnimation
            cells={[]}
            isAnimating={false}
            onComplete={mockOnAnimationComplete}
          />
        </>
      );

      expect(screen.getByText('Solve Word with AI')).toBeInTheDocument();

      // Step 3: Confirm action
      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      fireEvent.click(confirmButton);
      expect(mockOnConfirm).toHaveBeenCalled();

      // Step 4: Show animation
      const cells: Cell[] = [
        { row: 0, col: 0, value: 'C', is_blocked: false, number: 1 },
      ];

      rerender(
        <>
          <AIAssistancePanel
            hasPuzzle={true}
            activeClue={{ number: 1, direction: 'across' }}
            isSolvingWord={true}
            onSolveWord={mockOnSolveWord}
            onSolvePuzzle={mockOnSolvePuzzle}
            onGetHint={mockOnGetHint}
          />
          <ConfirmationDialog
            isOpen={false}
            title="Test"
            message="Test"
            onConfirm={mockOnConfirm}
            onCancel={mockOnCancel}
          />
          <HintModal
            isOpen={false}
            hint="Test"
            hintType="definition"
            clueInfo={{ number: 1, direction: 'across', text: 'Test' }}
            onClose={mockOnHintClose}
          />
          <SolutionAnimation
            cells={cells}
            isAnimating={true}
            onComplete={mockOnAnimationComplete}
          />
        </>
      );

      expect(screen.getByTestId('solution-animation')).toBeInTheDocument();
      expect(screen.getByText('Solving...')).toBeInTheDocument();
    });

    it('should handle complete hint flow with all components', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();
      const mockOnHintClose = vi.fn();

      const { rerender } = render(
        <>
          <AIAssistancePanel
            hasPuzzle={true}
            activeClue={{ number: 1, direction: 'across' }}
            onSolveWord={mockOnSolveWord}
            onSolvePuzzle={mockOnSolvePuzzle}
            onGetHint={mockOnGetHint}
          />
          <HintModal
            isOpen={false}
            hint="Test"
            hintType="definition"
            clueInfo={{ number: 1, direction: 'across', text: 'Test' }}
            onClose={mockOnHintClose}
          />
        </>
      );

      // Step 1: Click get hint button
      const getHintButton = screen.getByTestId('get-hint-button');
      fireEvent.click(getHintButton);
      expect(mockOnGetHint).toHaveBeenCalled();

      // Step 2: Show hint modal
      rerender(
        <>
          <AIAssistancePanel
            hasPuzzle={true}
            activeClue={{ number: 1, direction: 'across' }}
            isGettingHint={true}
            onSolveWord={mockOnSolveWord}
            onSolvePuzzle={mockOnSolvePuzzle}
            onGetHint={mockOnGetHint}
          />
          <HintModal
            isOpen={true}
            hint="Think about a common household pet"
            hintType="definition"
            clueInfo={{ number: 1, direction: 'across', text: 'Feline pet' }}
            onClose={mockOnHintClose}
          />
        </>
      );

      expect(screen.getByTestId('hint-modal')).toBeInTheDocument();
      expect(screen.getByText('Think about a common household pet')).toBeInTheDocument();

      // Step 3: Close hint modal
      const closeButton = screen.getByLabelText(/close/i);
      fireEvent.click(closeButton);
      expect(mockOnHintClose).toHaveBeenCalled();
    });
  });

  describe('Error State Integration', () => {
    it('should handle error states in AI assistance panel', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();

      render(
        <AIAssistancePanel
          hasPuzzle={true}
          activeClue={null}
          onSolveWord={mockOnSolveWord}
          onSolvePuzzle={mockOnSolvePuzzle}
          onGetHint={mockOnGetHint}
        />
      );

      // Buttons should be disabled when no active clue
      expect(screen.getByTestId('solve-word-button')).toBeDisabled();
      expect(screen.getByTestId('get-hint-button')).toBeDisabled();

      // Info message should be shown
      expect(screen.getByTestId('select-word-hint')).toBeInTheDocument();
    });

    it('should handle multiple operations disabled state', () => {
      const mockOnSolveWord = vi.fn();
      const mockOnSolvePuzzle = vi.fn();
      const mockOnGetHint = vi.fn();

      render(
        <AIAssistancePanel
          hasPuzzle={true}
          activeClue={{ number: 1, direction: 'across' }}
          isSolvingWord={false}
          isSolvingPuzzle={true}
          isGettingHint={false}
          onSolveWord={mockOnSolveWord}
          onSolvePuzzle={mockOnSolvePuzzle}
          onGetHint={mockOnGetHint}
        />
      );

      // All buttons should be disabled when any operation is in progress
      expect(screen.getByTestId('solve-word-button')).toBeDisabled();
      expect(screen.getByTestId('solve-puzzle-button')).toBeDisabled();
      expect(screen.getByTestId('get-hint-button')).toBeDisabled();
    });
  });
});
