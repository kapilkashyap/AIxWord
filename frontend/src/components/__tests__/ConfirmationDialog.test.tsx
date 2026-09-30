/**
 * Unit tests for ConfirmationDialog component.
 * 
 * Tests cover:
 * - Rendering with different states
 * - Confirm and cancel actions
 * - Keyboard navigation (Enter, Escape)
 * - Button variants
 * - Loading states
 * - Accessibility
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ConfirmationDialog } from '../ConfirmationDialog';

describe('ConfirmationDialog Component', () => {
  const mockOnConfirm = vi.fn();
  const mockOnCancel = vi.fn();

  const defaultProps = {
    isOpen: true,
    title: 'Confirm Action',
    message: 'Are you sure you want to proceed?',
    onConfirm: mockOnConfirm,
    onCancel: mockOnCancel,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    document.body.style.overflow = '';
  });

  describe('Rendering', () => {
    it('should render when isOpen is true', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      expect(screen.getByTestId('confirmation-dialog')).toBeInTheDocument();
      expect(screen.getByText('Confirm Action')).toBeInTheDocument();
      expect(screen.getByText('Are you sure you want to proceed?')).toBeInTheDocument();
    });

    it('should not render when isOpen is false', () => {
      render(<ConfirmationDialog {...defaultProps} isOpen={false} />);

      expect(screen.queryByTestId('confirmation-dialog')).not.toBeInTheDocument();
    });

    it('should render with custom testId', () => {
      render(<ConfirmationDialog {...defaultProps} testId="custom-dialog" />);

      expect(screen.getByTestId('custom-dialog')).toBeInTheDocument();
    });

    it('should render default icon', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      expect(screen.getByText('⚠️')).toBeInTheDocument();
    });

    it('should render custom icon', () => {
      render(<ConfirmationDialog {...defaultProps} icon="🚀" />);

      expect(screen.getByText('🚀')).toBeInTheDocument();
    });
  });

  describe('Button Labels', () => {
    it('should render default button labels', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      expect(screen.getByText('Confirm')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    it('should render custom button labels', () => {
      render(
        <ConfirmationDialog
          {...defaultProps}
          confirmLabel="Yes, proceed"
          cancelLabel="No, go back"
        />
      );

      expect(screen.getByText('Yes, proceed')).toBeInTheDocument();
      expect(screen.getByText('No, go back')).toBeInTheDocument();
    });
  });

  describe('Button Variants', () => {
    it('should apply primary variant by default', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      const confirmButton = screen.getByTestId('confirmation-dialog-confirm');
      expect(confirmButton.className).toContain('primaryButton');
    });

    it('should apply danger variant', () => {
      render(<ConfirmationDialog {...defaultProps} confirmVariant="danger" />);

      const confirmButton = screen.getByTestId('confirmation-dialog-confirm');
      expect(confirmButton.className).toContain('dangerButton');
    });

    it('should apply warning variant', () => {
      render(<ConfirmationDialog {...defaultProps} confirmVariant="warning" />);

      const confirmButton = screen.getByTestId('confirmation-dialog-confirm');
      expect(confirmButton.className).toContain('warningButton');
    });
  });

  describe('Confirm Action', () => {
    it('should call onConfirm when confirm button is clicked', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      const confirmButton = screen.getByTestId('confirmation-dialog-confirm');
      fireEvent.click(confirmButton);

      expect(mockOnConfirm).toHaveBeenCalledTimes(1);
    });

    it('should call onConfirm when Enter key is pressed', async () => {
      const user = userEvent.setup();
      render(<ConfirmationDialog {...defaultProps} />);

      await user.keyboard('{Enter}');

      expect(mockOnConfirm).toHaveBeenCalledTimes(1);
    });

    it('should not call onConfirm when Enter is pressed during confirmation', async () => {
      const user = userEvent.setup();
      render(<ConfirmationDialog {...defaultProps} isConfirming={true} />);

      await user.keyboard('{Enter}');

      expect(mockOnConfirm).not.toHaveBeenCalled();
    });
  });

  describe('Cancel Action', () => {
    it('should call onCancel when cancel button is clicked', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      const cancelButton = screen.getByTestId('confirmation-dialog-cancel');
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('should call onCancel when Escape key is pressed', async () => {
      const user = userEvent.setup();
      render(<ConfirmationDialog {...defaultProps} />);

      await user.keyboard('{Escape}');

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('should call onCancel when overlay is clicked', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      const overlay = screen.getByTestId('confirmation-dialog-overlay');
      fireEvent.click(overlay);

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('should not call onCancel when dialog content is clicked', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      const dialog = screen.getByTestId('confirmation-dialog');
      fireEvent.click(dialog);

      expect(mockOnCancel).not.toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    it('should show loading state when isConfirming is true', () => {
      render(<ConfirmationDialog {...defaultProps} isConfirming={true} />);

      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });

    it('should disable both buttons when isConfirming is true', () => {
      render(<ConfirmationDialog {...defaultProps} isConfirming={true} />);

      const confirmButton = screen.getByTestId('confirmation-dialog-confirm');
      const cancelButton = screen.getByTestId('confirmation-dialog-cancel');

      expect(confirmButton).toBeDisabled();
      expect(cancelButton).toBeDisabled();
    });

    it('should not show loading state by default', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      expect(screen.queryByText('Processing...')).not.toBeInTheDocument();
    });
  });

  describe('Body Scroll Prevention', () => {
    it('should prevent body scroll when dialog is open', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      expect(document.body.style.overflow).toBe('hidden');
    });

    it('should restore body scroll when dialog is closed', () => {
      const { rerender } = render(<ConfirmationDialog {...defaultProps} />);

      expect(document.body.style.overflow).toBe('hidden');

      rerender(<ConfirmationDialog {...defaultProps} isOpen={false} />);

      expect(document.body.style.overflow).toBe('');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      const overlay = screen.getByTestId('confirmation-dialog-overlay');
      expect(overlay).toHaveAttribute('role', 'dialog');
      expect(overlay).toHaveAttribute('aria-modal', 'true');
      expect(overlay).toHaveAttribute('aria-labelledby', 'confirmation-dialog-title');
      expect(overlay).toHaveAttribute('aria-describedby', 'confirmation-dialog-message');
    });

    it('should have accessible title', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      const title = screen.getByText('Confirm Action');
      expect(title).toHaveAttribute('id', 'confirmation-dialog-title');
    });

    it('should have accessible message', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      const message = screen.getByText('Are you sure you want to proceed?');
      expect(message).toHaveAttribute('id', 'confirmation-dialog-message');
    });

    it('should have accessible button labels', () => {
      render(<ConfirmationDialog {...defaultProps} />);

      const confirmButton = screen.getByTestId('confirmation-dialog-confirm');
      const cancelButton = screen.getByTestId('confirmation-dialog-cancel');

      expect(confirmButton).toHaveAttribute('aria-label', 'Confirm action');
      expect(cancelButton).toHaveAttribute('aria-label', 'Cancel action');
    });
  });

  describe('Content Display', () => {
    it('should display title and message correctly', () => {
      render(
        <ConfirmationDialog
          {...defaultProps}
          title="Delete Item"
          message="This action cannot be undone."
        />
      );

      expect(screen.getByText('Delete Item')).toBeInTheDocument();
      expect(screen.getByText('This action cannot be undone.')).toBeInTheDocument();
    });

    it('should handle long messages', () => {
      const longMessage = 'This is a very long message that should still be displayed correctly in the dialog. '.repeat(5).trim();
      render(<ConfirmationDialog {...defaultProps} message={longMessage} />);

      const messageElement = screen.getByTestId('confirmation-dialog').querySelector('p');
      expect(messageElement).toHaveTextContent(longMessage);
    });
  });

  describe('Button Interaction', () => {
    it('should not trigger actions when buttons are disabled', () => {
      render(<ConfirmationDialog {...defaultProps} isConfirming={true} />);

      const confirmButton = screen.getByTestId('confirmation-dialog-confirm');
      const cancelButton = screen.getByTestId('confirmation-dialog-cancel');

      fireEvent.click(confirmButton);
      fireEvent.click(cancelButton);

      expect(mockOnConfirm).not.toHaveBeenCalled();
      expect(mockOnCancel).not.toHaveBeenCalled();
    });
  });
});
