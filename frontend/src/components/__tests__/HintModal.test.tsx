/**
 * Unit tests for HintModal component.
 * 
 * Tests cover:
 * - Rendering different hint types
 * - Modal open/close behavior
 * - Keyboard navigation (Escape key)
 * - Click handlers
 * - Accessibility
 * - Letter hint special display
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HintModal } from '../HintModal';

describe('HintModal Component', () => {
  const mockOnClose = vi.fn();

  const defaultProps = {
    isOpen: true,
    hint: 'This is a test hint',
    hintType: 'definition' as const,
    onClose: mockOnClose,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Reset body overflow style
    document.body.style.overflow = '';
  });

  describe('Rendering', () => {
    it('should render when isOpen is true', () => {
      render(<HintModal {...defaultProps} />);

      expect(screen.getByTestId('hint-modal')).toBeInTheDocument();
      expect(screen.getByText('This is a test hint')).toBeInTheDocument();
    });

    it('should not render when isOpen is false', () => {
      render(<HintModal {...defaultProps} isOpen={false} />);

      expect(screen.queryByTestId('hint-modal')).not.toBeInTheDocument();
    });

    it('should render with custom testId', () => {
      render(<HintModal {...defaultProps} testId="custom-modal" />);

      expect(screen.getByTestId('custom-modal')).toBeInTheDocument();
    });
  });

  describe('Hint Types', () => {
    it('should render definition hint with correct icon and title', () => {
      render(<HintModal {...defaultProps} hintType="definition" />);

      expect(screen.getByText('Definition Hint')).toBeInTheDocument();
      expect(screen.getByText('📖')).toBeInTheDocument();
    });

    it('should render synonym hint with correct icon and title', () => {
      render(<HintModal {...defaultProps} hintType="synonym" />);

      expect(screen.getByText('Synonym Hint')).toBeInTheDocument();
      expect(screen.getByText('🔄')).toBeInTheDocument();
    });

    it('should render letter hint with correct icon and title', () => {
      render(<HintModal {...defaultProps} hintType="letter" />);

      expect(screen.getByText('Letter Hint')).toBeInTheDocument();
      expect(screen.getByText('🔤')).toBeInTheDocument();
    });
  });

  describe('Letter Hint Special Display', () => {
    it('should display revealed letter and position for letter hints', () => {
      render(
        <HintModal
          {...defaultProps}
          hintType="letter"
          revealedLetter="D"
          position={0}
          hint="The first letter is D"
        />
      );

      expect(screen.getByText('Revealed Letter:')).toBeInTheDocument();
      expect(screen.getByText('D')).toBeInTheDocument();
      expect(screen.getByText('Position:')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument(); // Position is 1-indexed for display
      expect(screen.getByText('The first letter is D')).toBeInTheDocument();
    });

    it('should handle position 0 correctly (display as 1)', () => {
      render(
        <HintModal
          {...defaultProps}
          hintType="letter"
          revealedLetter="A"
          position={0}
        />
      );

      expect(screen.getByText('1')).toBeInTheDocument();
    });

    it('should display regular hint text for letter hint without revealed letter', () => {
      render(
        <HintModal
          {...defaultProps}
          hintType="letter"
          hint="Try thinking about the clue differently"
        />
      );

      expect(screen.getByText('Try thinking about the clue differently')).toBeInTheDocument();
      expect(screen.queryByText('Revealed Letter:')).not.toBeInTheDocument();
    });
  });

  describe('Clue Context', () => {
    it('should display clue information when provided', () => {
      render(
        <HintModal
          {...defaultProps}
          clueInfo={{
            number: 5,
            direction: 'down',
            text: 'Capital of France',
          }}
        />
      );

      expect(screen.getByTestId('hint-modal-clue-context')).toBeInTheDocument();
      expect(screen.getByText('5 down')).toBeInTheDocument();
      expect(screen.getByText('Capital of France')).toBeInTheDocument();
    });

    it('should not display clue context when not provided', () => {
      render(<HintModal {...defaultProps} />);

      expect(screen.queryByTestId('hint-modal-clue-context')).not.toBeInTheDocument();
    });
  });

  describe('Close Functionality', () => {
    it('should call onClose when close button is clicked', () => {
      render(<HintModal {...defaultProps} />);

      const closeButton = screen.getByTestId('hint-modal-close');
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when Got it button is clicked', () => {
      render(<HintModal {...defaultProps} />);

      const gotItButton = screen.getByTestId('hint-modal-got-it');
      fireEvent.click(gotItButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when overlay is clicked', () => {
      render(<HintModal {...defaultProps} />);

      const overlay = screen.getByTestId('hint-modal-overlay');
      fireEvent.click(overlay);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should not call onClose when modal content is clicked', () => {
      render(<HintModal {...defaultProps} />);

      const modal = screen.getByTestId('hint-modal');
      fireEvent.click(modal);

      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it('should call onClose when Escape key is pressed', async () => {
      const user = userEvent.setup();
      render(<HintModal {...defaultProps} />);

      await user.keyboard('{Escape}');

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Body Scroll Prevention', () => {
    it('should prevent body scroll when modal is open', () => {
      render(<HintModal {...defaultProps} />);

      expect(document.body.style.overflow).toBe('hidden');
    });

    it('should restore body scroll when modal is closed', () => {
      const { rerender } = render(<HintModal {...defaultProps} />);

      expect(document.body.style.overflow).toBe('hidden');

      rerender(<HintModal {...defaultProps} isOpen={false} />);

      expect(document.body.style.overflow).toBe('');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<HintModal {...defaultProps} />);

      const overlay = screen.getByTestId('hint-modal-overlay');
      expect(overlay).toHaveAttribute('role', 'dialog');
      expect(overlay).toHaveAttribute('aria-modal', 'true');
      expect(overlay).toHaveAttribute('aria-labelledby', 'hint-modal-title');
      expect(overlay).toHaveAttribute('aria-describedby', 'hint-modal-content');
    });

    it('should have accessible title', () => {
      render(<HintModal {...defaultProps} />);

      const title = screen.getByText('Definition Hint');
      expect(title).toHaveAttribute('id', 'hint-modal-title');
    });

    it('should have accessible content', () => {
      render(<HintModal {...defaultProps} />);

      const content = screen.getByTestId('hint-modal-content');
      expect(content).toHaveAttribute('id', 'hint-modal-content');
    });

    it('should have accessible close button', () => {
      render(<HintModal {...defaultProps} />);

      const closeButton = screen.getByTestId('hint-modal-close');
      expect(closeButton).toHaveAttribute('aria-label', 'Close hint modal');
    });
  });

  describe('Content Display', () => {
    it('should display hint text correctly', () => {
      render(<HintModal {...defaultProps} hint="A four-legged animal" />);

      expect(screen.getByText('A four-legged animal')).toBeInTheDocument();
    });

    it('should display empty hint text', () => {
      render(<HintModal {...defaultProps} hint="" />);

      const content = screen.getByTestId('hint-modal-content');
      expect(content).toBeInTheDocument();
    });
  });

  describe('Multiple Hint Types', () => {
    it('should handle switching between hint types', () => {
      const { rerender } = render(<HintModal {...defaultProps} hintType="definition" />);

      expect(screen.getByText('Definition Hint')).toBeInTheDocument();

      rerender(<HintModal {...defaultProps} hintType="synonym" />);

      expect(screen.getByText('Synonym Hint')).toBeInTheDocument();
      expect(screen.queryByText('Definition Hint')).not.toBeInTheDocument();
    });
  });
});
