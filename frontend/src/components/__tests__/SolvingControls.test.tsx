/**
 * Tests for SolvingControls component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SolvingControls } from '../SolvingControls';
import type { SolvingStats } from '../../hooks/useSolving';

describe('SolvingControls', () => {
  const mockStats: SolvingStats = {
    totalWords: 10,
    completedWords: 3,
    wordsCompletionPercentage: 30,
    totalCells: 50,
    filledCells: 20,
    cellsCompletionPercentage: 40,
    isFullyComplete: false,
  };

  const mockHandlers = {
    onClearAll: vi.fn(),
    onClearWord: vi.fn(),
    onCheckSolution: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should not render when no puzzle is loaded', () => {
      const { container } = render(
        <SolvingControls
          hasPuzzle={false}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      expect(container.firstChild).toBeNull();
    });

    it('should render when puzzle is loaded', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      expect(screen.getByTestId('solving-controls')).toBeInTheDocument();
    });

    it('should display progress percentage', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      expect(screen.getByText('40%')).toBeInTheDocument();
    });

    it('should display filled cells count', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      expect(screen.getByText('20')).toBeInTheDocument();
      expect(screen.getByText('/ 50 cells')).toBeInTheDocument();
    });

    it('should display completed words count', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('/ 10 words')).toBeInTheDocument();
    });

    it('should render progress bar with correct width', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      const progressFill = screen.getByTestId('progress-fill');
      expect(progressFill).toHaveStyle({ width: '40%' });
    });
  });

  describe('Completion Message', () => {
    it('should not show completion message when puzzle is incomplete', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      expect(screen.queryByTestId('completion-message')).not.toBeInTheDocument();
    });

    it('should show completion message when puzzle is fully complete', () => {
      const completeStats: SolvingStats = {
        ...mockStats,
        completedWords: 10,
        wordsCompletionPercentage: 100,
        filledCells: 50,
        cellsCompletionPercentage: 100,
        isFullyComplete: true,
      };

      render(
        <SolvingControls
          hasPuzzle={true}
          stats={completeStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      expect(screen.getByTestId('completion-message')).toBeInTheDocument();
      expect(screen.getByText(/All words complete/i)).toBeInTheDocument();
    });
  });

  describe('Clear Word Button', () => {
    it('should be disabled when no active clue', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('clear-word-button');
      expect(button).toBeDisabled();
    });

    it('should be enabled when active clue exists', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={{ number: 1, direction: 'across' }}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('clear-word-button');
      expect(button).not.toBeDisabled();
    });

    it('should call onClearWord when clicked', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={{ number: 1, direction: 'across' }}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('clear-word-button');
      fireEvent.click(button);

      expect(mockHandlers.onClearWord).toHaveBeenCalledTimes(1);
    });

    it('should be disabled when validating', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={{ number: 1, direction: 'across' }}
          isValidating={true}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('clear-word-button');
      expect(button).toBeDisabled();
    });
  });

  describe('Clear All Button', () => {
    it('should be disabled when no cells are filled', () => {
      const emptyStats: SolvingStats = {
        ...mockStats,
        filledCells: 0,
        cellsCompletionPercentage: 0,
      };

      render(
        <SolvingControls
          hasPuzzle={true}
          stats={emptyStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('clear-all-button');
      expect(button).toBeDisabled();
    });

    it('should be enabled when cells are filled', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('clear-all-button');
      expect(button).not.toBeDisabled();
    });

    it('should call onClearAll when clicked', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('clear-all-button');
      fireEvent.click(button);

      expect(mockHandlers.onClearAll).toHaveBeenCalledTimes(1);
    });

    it('should be disabled when validating', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          isValidating={true}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('clear-all-button');
      expect(button).toBeDisabled();
    });
  });

  describe('Check Solution Button', () => {
    it('should be disabled when no cells are filled', () => {
      const emptyStats: SolvingStats = {
        ...mockStats,
        filledCells: 0,
        cellsCompletionPercentage: 0,
      };

      render(
        <SolvingControls
          hasPuzzle={true}
          stats={emptyStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('check-solution-button');
      expect(button).toBeDisabled();
    });

    it('should be enabled when cells are filled', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('check-solution-button');
      expect(button).not.toBeDisabled();
    });

    it('should call onCheckSolution when clicked', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('check-solution-button');
      fireEvent.click(button);

      expect(mockHandlers.onCheckSolution).toHaveBeenCalledTimes(1);
    });

    it('should show loading state when validating', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          isValidating={true}
          {...mockHandlers}
        />
      );

      expect(screen.getByText('Checking...')).toBeInTheDocument();
    });

    it('should be disabled when validating', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          isValidating={true}
          {...mockHandlers}
        />
      );

      const button = screen.getByTestId('check-solution-button');
      expect(button).toBeDisabled();
    });
  });

  describe('Keyboard Shortcuts Hint', () => {
    it('should display keyboard shortcuts', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          {...mockHandlers}
        />
      );

      expect(screen.getByTestId('shortcuts-hint')).toBeInTheDocument();
      expect(screen.getByText('Navigate')).toBeInTheDocument();
      expect(screen.getByText('Toggle direction')).toBeInTheDocument();
      expect(screen.getByText('Clear')).toBeInTheDocument();
      expect(screen.getByText('Next word')).toBeInTheDocument();
    });
  });

  describe('Custom Class Name', () => {
    it('should apply custom class name', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={null}
          className="custom-class"
          {...mockHandlers}
        />
      );

      const container = screen.getByTestId('solving-controls');
      expect(container).toHaveClass('custom-class');
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria labels', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={{ number: 1, direction: 'across' }}
          {...mockHandlers}
        />
      );

      expect(screen.getByLabelText('Clear current word')).toBeInTheDocument();
      expect(screen.getByLabelText('Clear all answers')).toBeInTheDocument();
      expect(screen.getByLabelText('Check solution')).toBeInTheDocument();
    });

    it('should have proper titles for tooltips', () => {
      render(
        <SolvingControls
          hasPuzzle={true}
          stats={mockStats}
          activeClue={{ number: 1, direction: 'across' }}
          {...mockHandlers}
        />
      );

      const clearWordButton = screen.getByTestId('clear-word-button');
      expect(clearWordButton).toHaveAttribute('title', 'Clear 1 across');

      const clearAllButton = screen.getByTestId('clear-all-button');
      expect(clearAllButton).toHaveAttribute('title', 'Clear all your answers');

      const checkButton = screen.getByTestId('check-solution-button');
      expect(checkButton).toHaveAttribute('title', 'Check your solution');
    });
  });
});
