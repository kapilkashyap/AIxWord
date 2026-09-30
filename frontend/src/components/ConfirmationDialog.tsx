/**
 * ConfirmationDialog component - Reusable confirmation dialog for destructive actions.
 * 
 * This component displays a modal confirmation dialog with:
 * - Customizable title, message, and button labels
 * - Confirm and cancel actions
 * - Keyboard navigation (Enter to confirm, Escape to cancel)
 * - Accessible with ARIA labels
 * - Focus trap within dialog
 * - Overlay click to cancel
 * 
 * Features:
 * - Used before solving entire puzzle (overwrites user input)
 * - Prevents accidental destructive actions
 * - Smooth animations
 * - Responsive design
 */

import React, { useEffect, useRef } from 'react';
import styles from './ConfirmationDialog.module.css';

export interface ConfirmationDialogProps {
  /** Whether the dialog is open */
  isOpen: boolean;
  /** Dialog title */
  title: string;
  /** Dialog message/description */
  message: string;
  /** Confirm button label */
  confirmLabel?: string;
  /** Cancel button label */
  cancelLabel?: string;
  /** Confirm button variant */
  confirmVariant?: 'primary' | 'danger' | 'warning';
  /** Whether confirm action is in progress */
  isConfirming?: boolean;
  /** Callback when confirmed */
  onConfirm: () => void;
  /** Callback when cancelled */
  onCancel: () => void;
  /** Optional icon */
  icon?: string;
  /** Optional test ID */
  testId?: string;
}

/**
 * ConfirmationDialog component displays a confirmation dialog.
 */
export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  confirmVariant = 'primary',
  isConfirming = false,
  onConfirm,
  onCancel,
  icon = '⚠️',
  testId = 'confirmation-dialog',
}) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const confirmButtonRef = useRef<HTMLButtonElement>(null);
  const cancelButtonRef = useRef<HTMLButtonElement>(null);

  // Handle keyboard events
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onCancel();
      } else if (e.key === 'Enter' && !isConfirming) {
        onConfirm();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isConfirming, onConfirm, onCancel]);

  // Focus cancel button when dialog opens
  useEffect(() => {
    if (isOpen && cancelButtonRef.current) {
      cancelButtonRef.current.focus();
    }
  }, [isOpen]);

  // Prevent body scroll when dialog is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  // Handle overlay click
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onCancel();
    }
  };

  // Get confirm button class based on variant
  const confirmButtonClass = `${styles.button} ${styles.confirmButton} ${
    confirmVariant === 'danger'
      ? styles.dangerButton
      : confirmVariant === 'warning'
      ? styles.warningButton
      : styles.primaryButton
  }`;

  return (
    <div
      className={styles.overlay}
      onClick={handleOverlayClick}
      data-testid={`${testId}-overlay`}
      role="dialog"
      aria-modal="true"
      aria-labelledby={`${testId}-title`}
      aria-describedby={`${testId}-message`}
    >
      <div
        ref={dialogRef}
        className={styles.dialog}
        data-testid={testId}
      >
        {/* Icon */}
        <div className={styles.iconContainer}>
          <span className={styles.icon} aria-hidden="true">
            {icon}
          </span>
        </div>

        {/* Content */}
        <div className={styles.content}>
          <h2
            id={`${testId}-title`}
            className={styles.title}
          >
            {title}
          </h2>
          <p
            id={`${testId}-message`}
            className={styles.message}
          >
            {message}
          </p>
        </div>

        {/* Actions */}
        <div className={styles.actions}>
          <button
            ref={cancelButtonRef}
            className={`${styles.button} ${styles.cancelButton}`}
            onClick={onCancel}
            disabled={isConfirming}
            data-testid={`${testId}-cancel`}
            aria-label="Cancel action"
          >
            {cancelLabel}
          </button>
          <button
            ref={confirmButtonRef}
            className={confirmButtonClass}
            onClick={onConfirm}
            disabled={isConfirming}
            data-testid={`${testId}-confirm`}
            aria-label="Confirm action"
          >
            {isConfirming ? (
              <>
                <span className={styles.spinner}></span>
                <span>Processing...</span>
              </>
            ) : (
              confirmLabel
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationDialog;
