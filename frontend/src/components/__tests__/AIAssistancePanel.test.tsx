/**
 * Unit tests for AIAssistancePanel component.
 * 
 * Tests cover:
 * - Rendering with different states
 * - Button states (enabled/disabled)
 * - Loading states
 * - Click handlers
 * - Accessibility
 * - Conditional rendering based on puzzle state
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AIAssistancePanel } from '../AIAssistancePanel';

describe('AIAssistancePanel Component', () => {
  const mockOnSolveWord = vi.fn();
  const mockOnSolvePuzzle = vi.fn();
  const mockOnGetHint = vi.fn();

  const defaultProps = {
    hasPuzzle: true,
    activeClue: { number: 1, direction: 'across' as const },
    onSolveWord: mockOnSolveWord,
    onSolvePuzzle: mockOnSolvePuzzle,
    onGetHint: mockOnGetHint,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render when puzzle is loaded', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      expect(screen.getByTestId('ai-assistance-panel')).toBeInTheDocument();
      expect(screen.getByText('AI Assistance')).toBeInTheDocument();
      expect(screen.getByText('Get help solving the puzzle with AI')).toBeInTheDocument();
    });

    it('should not render when no puzzle is loaded', () => {
      render(<AIAssistancePanel {...defaultProps} hasPuzzle={false} />);

      expect(screen.queryByTestId('ai-assistance-panel')).not.toBeInTheDocument();
    });

    it('should render all three action buttons', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      expect(screen.getByTestId('solve-word-button')).toBeInTheDocument();
      expect(screen.getByTestId('get-hint-button')).toBeInTheDocument();
      expect(screen.getByTestId('solve-puzzle-button')).toBeInTheDocument();
    });

    it('should render warning message', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      expect(screen.getByTestId('ai-warning')).toBeInTheDocument();
      expect(screen.getByText(/AI assistance will overwrite your current answers/)).toBeInTheDocument();
    });
  });

  describe('Button States - With Active Clue', () => {
    it('should enable solve word button when active clue exists', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      const solveWordButton = screen.getByTestId('solve-word-button');
      expect(solveWordButton).not.toBeDisabled();
    });

    it('should enable get hint button when active clue exists', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      const getHintButton = screen.getByTestId('get-hint-button');
      expect(getHintButton).not.toBeDisabled();
    });

    it('should always enable solve puzzle button', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      const solvePuzzleButton = screen.getByTestId('solve-puzzle-button');
      expect(solvePuzzleButton).not.toBeDisabled();
    });

    it('should not show select word hint when active clue exists', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      expect(screen.queryByTestId('select-word-hint')).not.toBeInTheDocument();
    });
  });

  describe('Button States - Without Active Clue', () => {
    it('should disable solve word button when no active clue', () => {
      render(<AIAssistancePanel {...defaultProps} activeClue={null} />);

      const solveWordButton = screen.getByTestId('solve-word-button');
      expect(solveWordButton).toBeDisabled();
    });

    it('should disable get hint button when no active clue', () => {
      render(<AIAssistancePanel {...defaultProps} activeClue={null} />);

      const getHintButton = screen.getByTestId('get-hint-button');
      expect(getHintButton).toBeDisabled();
    });

    it('should keep solve puzzle button enabled when no active clue', () => {
      render(<AIAssistancePanel {...defaultProps} activeClue={null} />);

      const solvePuzzleButton = screen.getByTestId('solve-puzzle-button');
      expect(solvePuzzleButton).not.toBeDisabled();
    });

    it('should show select word hint when no active clue', () => {
      render(<AIAssistancePanel {...defaultProps} activeClue={null} />);

      expect(screen.getByTestId('select-word-hint')).toBeInTheDocument();
      expect(screen.getByText(/Select a word to use Solve Word or Get Hint/)).toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should show loading state for solve word button', () => {
      render(<AIAssistancePanel {...defaultProps} isSolvingWord={true} />);

      const solveWordButton = screen.getByTestId('solve-word-button');
      expect(solveWordButton).toHaveTextContent('Solving...');
      expect(solveWordButton).toBeDisabled();
    });

    it('should show loading state for get hint button', () => {
      render(<AIAssistancePanel {...defaultProps} isGettingHint={true} />);

      const getHintButton = screen.getByTestId('get-hint-button');
      expect(getHintButton).toHaveTextContent('Getting Hint...');
      expect(getHintButton).toBeDisabled();
    });

    it('should show loading state for solve puzzle button', () => {
      render(<AIAssistancePanel {...defaultProps} isSolvingPuzzle={true} />);

      const solvePuzzleButton = screen.getByTestId('solve-puzzle-button');
      expect(solvePuzzleButton).toHaveTextContent('Solving Puzzle...');
      expect(solvePuzzleButton).toBeDisabled();
    });

    it('should disable all buttons when any operation is in progress', () => {
      render(<AIAssistancePanel {...defaultProps} isSolvingWord={true} />);

      expect(screen.getByTestId('solve-word-button')).toBeDisabled();
      expect(screen.getByTestId('get-hint-button')).toBeDisabled();
      expect(screen.getByTestId('solve-puzzle-button')).toBeDisabled();
    });
  });

  describe('Click Handlers', () => {
    it('should call onSolveWord when solve word button is clicked', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      const solveWordButton = screen.getByTestId('solve-word-button');
      fireEvent.click(solveWordButton);

      expect(mockOnSolveWord).toHaveBeenCalledTimes(1);
    });

    it('should call onGetHint when get hint button is clicked', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      const getHintButton = screen.getByTestId('get-hint-button');
      fireEvent.click(getHintButton);

      expect(mockOnGetHint).toHaveBeenCalledTimes(1);
    });

    it('should call onSolvePuzzle when solve puzzle button is clicked', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      const solvePuzzleButton = screen.getByTestId('solve-puzzle-button');
      fireEvent.click(solvePuzzleButton);

      expect(mockOnSolvePuzzle).toHaveBeenCalledTimes(1);
    });

    it('should not call handlers when buttons are disabled', () => {
      render(<AIAssistancePanel {...defaultProps} activeClue={null} />);

      const solveWordButton = screen.getByTestId('solve-word-button');
      const getHintButton = screen.getByTestId('get-hint-button');

      fireEvent.click(solveWordButton);
      fireEvent.click(getHintButton);

      expect(mockOnSolveWord).not.toHaveBeenCalled();
      expect(mockOnGetHint).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for buttons', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      expect(screen.getByLabelText('Solve current word with AI')).toBeInTheDocument();
      expect(screen.getByLabelText('Get hint for current word')).toBeInTheDocument();
      expect(screen.getByLabelText('Solve entire puzzle with AI')).toBeInTheDocument();
    });

    it('should have descriptive titles for buttons with active clue', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      const solveWordButton = screen.getByTestId('solve-word-button');
      expect(solveWordButton).toHaveAttribute('title', 'Solve 1 across with AI');

      const getHintButton = screen.getByTestId('get-hint-button');
      expect(getHintButton).toHaveAttribute('title', 'Get a hint for 1 across');
    });

    it('should have descriptive titles for buttons without active clue', () => {
      render(<AIAssistancePanel {...defaultProps} activeClue={null} />);

      const solveWordButton = screen.getByTestId('solve-word-button');
      expect(solveWordButton).toHaveAttribute('title', 'Select a word to solve');

      const getHintButton = screen.getByTestId('get-hint-button');
      expect(getHintButton).toHaveAttribute('title', 'Select a word to get a hint');
    });
  });

  describe('Custom Class Name', () => {
    it('should apply custom className', () => {
      render(<AIAssistancePanel {...defaultProps} className="custom-class" />);

      const panel = screen.getByTestId('ai-assistance-panel');
      expect(panel).toHaveClass('custom-class');
    });
  });

  describe('Button Content', () => {
    it('should show correct text for solve word button', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      expect(screen.getByText('Solve Word')).toBeInTheDocument();
    });

    it('should show correct text for get hint button', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      expect(screen.getByText('Get Hint')).toBeInTheDocument();
    });

    it('should show correct text for solve puzzle button', () => {
      render(<AIAssistancePanel {...defaultProps} />);

      expect(screen.getByText('Solve Puzzle')).toBeInTheDocument();
    });
  });
});
