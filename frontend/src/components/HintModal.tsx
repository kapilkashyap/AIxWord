/**
 * HintModal component - Modal dialog to display AI-generated hints.
 * 
 * This component displays hints in a modal overlay with:
 * - Support for different hint types (letter, definition, synonym)
 * - Close button and overlay click to dismiss
 * - Accessible with keyboard navigation and ARIA labels
 * - Smooth animations
 * - Responsive design
 * 
 * Features:
 * - Letter hints show revealed letter and position
 * - Definition hints show alternative definitions
 * - Synonym hints show related words
 * - Escape key to close
 * - Focus trap within modal
 */

import React, { useEffect, useRef } from 'react';
import type { HintType } from '../types/puzzle';
import styles from './HintModal.module.css';

export interface HintModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** The hint text to display */
  hint: string;
  /** Type of hint */
  hintType: HintType;
  /** Revealed letter (for letter hints) */
  revealedLetter?: string | null;
  /** Position of revealed letter (for letter hints) */
  position?: number | null;
  /** Clue number and direction for context */
  clueInfo?: { number: number; direction: string; text: string };
  /** Callback when modal is closed */
  onClose: () => void;
  /** Optional test ID */
  testId?: string;
}

/**
 * HintModal component displays AI-generated hints in a modal dialog.
 */
export const HintModal: React.FC<HintModalProps> = ({
  isOpen,
  hint,
  hintType,
  revealedLetter,
  position,
  clueInfo,
  onClose,
  testId = 'hint-modal',
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  // Handle escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Focus close button when modal opens
  useEffect(() => {
    if (isOpen && closeButtonRef.current) {
      closeButtonRef.current.focus();
    }
  }, [isOpen]);

  // Prevent body scroll when modal is open
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

  // Get hint type display info
  const hintTypeInfo = {
    letter: {
      icon: '🔤',
      title: 'Letter Hint',
      color: '#667eea',
    },
    definition: {
      icon: '📖',
      title: 'Definition Hint',
      color: '#f59e0b',
    },
    synonym: {
      icon: '🔄',
      title: 'Synonym Hint',
      color: '#10b981',
    },
  };

  const typeInfo = hintTypeInfo[hintType] || hintTypeInfo.definition;

  // Handle overlay click
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className={styles.overlay}
      onClick={handleOverlayClick}
      data-testid={`${testId}-overlay`}
      role="dialog"
      aria-modal="true"
      aria-labelledby={`${testId}-title`}
      aria-describedby={`${testId}-content`}
    >
      <div
        ref={modalRef}
        className={styles.modal}
        data-testid={testId}
      >
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <span
              className={styles.icon}
              style={{ color: typeInfo.color }}
              aria-hidden="true"
            >
              {typeInfo.icon}
            </span>
            <h2
              id={`${testId}-title`}
              className={styles.title}
            >
              {typeInfo.title}
            </h2>
          </div>
          <button
            ref={closeButtonRef}
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close hint modal"
            data-testid={`${testId}-close`}
          >
            ✕
          </button>
        </div>

        {/* Clue Context */}
        {clueInfo && (
          <div className={styles.clueContext} data-testid={`${testId}-clue-context`}>
            <span className={styles.clueNumber}>
              {clueInfo.number} {clueInfo.direction}
            </span>
            <span className={styles.clueText}>{clueInfo.text}</span>
          </div>
        )}

        {/* Hint Content */}
        <div
          id={`${testId}-content`}
          className={styles.content}
          data-testid={`${testId}-content`}
        >
          {/* Letter Hint Special Display */}
          {hintType === 'letter' && revealedLetter && position !== null && position !== undefined ? (
            <div className={styles.letterHint}>
              <div className={styles.letterReveal}>
                <span className={styles.letterLabel}>Revealed Letter:</span>
                <span className={styles.letter}>{revealedLetter}</span>
              </div>
              <div className={styles.positionInfo}>
                <span className={styles.positionLabel}>Position:</span>
                <span className={styles.position}>{position + 1}</span>
              </div>
              {hint && (
                <p className={styles.hintText}>{hint}</p>
              )}
            </div>
          ) : (
            <p className={styles.hintText}>{hint}</p>
          )}
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <button
            className={styles.gotItButton}
            onClick={onClose}
            data-testid={`${testId}-got-it`}
          >
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
};

export default HintModal;
