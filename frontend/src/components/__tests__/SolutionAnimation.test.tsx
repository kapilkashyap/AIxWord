/**
 * Unit tests for SolutionAnimation component.
 * 
 * Tests cover:
 * - Rendering with different states
 * - Skip functionality
 * - Accessibility
 * - Content display
 * 
 * Note: Animation timing tests are covered by integration tests
 * due to complexity of testing React state updates with fake timers
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SolutionAnimation } from '../SolutionAnimation';
import type { Cell } from '../../types/puzzle';

describe('SolutionAnimation Component', () => {
  const mockOnComplete = vi.fn();
  const mockOnSkip = vi.fn();

  const mockCells: Cell[] = [
    { row: 0, col: 0, value: 'T', is_blocked: false, number: 1 },
    { row: 0, col: 1, value: 'E', is_blocked: false, number: null },
    { row: 0, col: 2, value: 'S', is_blocked: false, number: null },
    { row: 0, col: 3, value: 'T', is_blocked: false, number: null },
  ];

  const defaultProps = {
    cells: mockCells,
    isAnimating: true,
    onComplete: mockOnComplete,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render when isAnimating is true', () => {
      render(<SolutionAnimation {...defaultProps} />);

      expect(screen.getByTestId('solution-animation')).toBeInTheDocument();
      expect(screen.getByText('AI Solving...')).toBeInTheDocument();
    });

    it('should not render when isAnimating is false', () => {
      render(<SolutionAnimation {...defaultProps} isAnimating={false} />);

      expect(screen.queryByTestId('solution-animation')).not.toBeInTheDocument();
    });

    it('should render with custom testId', () => {
      render(<SolutionAnimation {...defaultProps} testId="custom-animation" />);

      expect(screen.getByTestId('custom-animation')).toBeInTheDocument();
    });

    it('should display correct letter count', () => {
      render(<SolutionAnimation {...defaultProps} />);

      expect(screen.getByText('Filling in 4 letters')).toBeInTheDocument();
    });

    it('should display singular letter for single cell', () => {
      render(<SolutionAnimation {...defaultProps} cells={[mockCells[0]]} />);

      expect(screen.getByText('Filling in 1 letter')).toBeInTheDocument();
    });
  });

  describe('Progress Display', () => {
    it('should show initial progress', () => {
      render(<SolutionAnimation {...defaultProps} />);

      expect(screen.getByText('0 / 4')).toBeInTheDocument();
    });

    it('should show progress bar', () => {
      render(<SolutionAnimation {...defaultProps} />);

      const progressBar = screen.getByTestId('solution-animation-progress-bar');
      expect(progressBar).toBeInTheDocument();

      const progressFill = screen.getByTestId('solution-animation-progress-fill');
      expect(progressFill).toBeInTheDocument();
    });
  });

  describe('Letter Preview', () => {
    it('should display letters container', () => {
      render(<SolutionAnimation {...defaultProps} />);

      expect(screen.getByTestId('solution-animation-letters')).toBeInTheDocument();
    });
  });

  describe('Skip Functionality', () => {
    it('should show skip button during animation', () => {
      render(<SolutionAnimation {...defaultProps} />);

      expect(screen.getByTestId('solution-animation-skip')).toBeInTheDocument();
      expect(screen.getByText('Skip Animation')).toBeInTheDocument();
    });

    it('should call onSkip when skip button is clicked', () => {
      render(<SolutionAnimation {...defaultProps} onSkip={mockOnSkip} />);

      const skipButton = screen.getByTestId('solution-animation-skip');
      fireEvent.click(skipButton);

      expect(mockOnSkip).toHaveBeenCalledTimes(1);
    });

    it('should call onComplete when skip button is clicked without onSkip', () => {
      render(<SolutionAnimation {...defaultProps} />);

      const skipButton = screen.getByTestId('solution-animation-skip');
      fireEvent.click(skipButton);

      expect(mockOnComplete).toHaveBeenCalledTimes(1);
    });

    it('should call onSkip when Escape key is pressed', async () => {
      const user = userEvent.setup({ delay: null });
      render(<SolutionAnimation {...defaultProps} onSkip={mockOnSkip} />);

      await user.keyboard('{Escape}');

      expect(mockOnSkip).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<SolutionAnimation {...defaultProps} />);

      const container = screen.getByTestId('solution-animation');
      expect(container).toHaveAttribute('role', 'status');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-label', 'AI solution animation in progress');
    });

    it('should have accessible skip button', () => {
      render(<SolutionAnimation {...defaultProps} />);

      const skipButton = screen.getByTestId('solution-animation-skip');
      expect(skipButton).toHaveAttribute('aria-label', 'Skip animation');
    });
  });

  describe('Custom Class Name', () => {
    it('should apply custom className', () => {
      render(<SolutionAnimation {...defaultProps} className="custom-class" />);

      const container = screen.getByTestId('solution-animation');
      expect(container).toHaveClass('custom-class');
    });
  });

  describe('Empty Cells', () => {
    it('should handle empty cells array', () => {
      render(<SolutionAnimation {...defaultProps} cells={[]} />);

      expect(screen.getByText('Filling in 0 letters')).toBeInTheDocument();
      expect(screen.getByText('0 / 0')).toBeInTheDocument();
    });
  });

  describe('Content Display', () => {
    it('should display animation icon', () => {
      render(<SolutionAnimation {...defaultProps} />);

      expect(screen.getByText('✨')).toBeInTheDocument();
    });

    it('should display subtitle message', () => {
      render(<SolutionAnimation {...defaultProps} />);

      expect(screen.getByText(/Filling in \d+ letter/)).toBeInTheDocument();
    });
  });
});
