/**
 * ClueItem component - Represents a single clue in the crossword puzzle.
 * 
 * Features:
 * - Displays clue number, direction, and text
 * - Shows answer length in parentheses
 * - Highlights when the clue is active (currently being solved)
 * - Shows completion status with visual feedback
 * - Clickable to select the corresponding word in the grid
 * - Displays filled letters as user progresses
 * - Supports AI assistance indicators
 */

import React from 'react';
import type { Clue } from '../types/puzzle';
import styles from './ClueItem.module.css';

export interface ClueItemProps {
  /** The clue data */
  clue: Clue;
  /** Whether this clue is currently active */
  isActive: boolean;
  /** Whether this clue is completed */
  isCompleted: boolean;
  /** Current filled letters for this word (for progress display) */
  currentAnswer?: string;
  /** Callback when clue is clicked */
  onClick: (clue: Clue) => void;
  /** Whether to show the answer (for solution mode) */
  showAnswer?: boolean;
  /** Optional CSS class name */
  className?: string;
}

/**
 * ClueItem component renders a single clue with interactive features.
 */
export const ClueItem: React.FC<ClueItemProps> = ({
  clue,
  isActive,
  isCompleted,
  currentAnswer,
  onClick,
  showAnswer = false,
  className,
}) => {
  // Handle click on clue
  const handleClick = () => {
    onClick(clue);
  };

  // Build CSS classes based on state
  const clueClasses = [
    styles.clueItem,
    isActive && styles.active,
    isCompleted && styles.completed,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  // Format the current answer to show progress (e.g., "P_TH__")
  const formatProgress = (): string => {
    if (!currentAnswer) return '';
    return currentAnswer
      .split('')
      .map((char) => (char ? char : '_'))
      .join('');
  };

  const progress = formatProgress();
  const hasProgress = progress && progress.includes('_') && progress.replace(/_/g, '').length > 0;

  return (
    <div
      className={clueClasses}
      onClick={handleClick}
      data-testid={`clue-${clue.number}-${clue.direction}`}
      data-clue-number={clue.number}
      data-direction={clue.direction}
      data-active={isActive}
      data-completed={isCompleted}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
      aria-label={`Clue ${clue.number} ${clue.direction}: ${clue.text}`}
    >
      {/* Clue number */}
      <div className={styles.clueNumber}>
        {clue.number}
      </div>

      {/* Clue content */}
      <div className={styles.clueContent}>
        {/* Clue text */}
        <div className={styles.clueText}>
          {clue.text}
          {' '}
          <span className={styles.clueLength}>({clue.length})</span>
        </div>

        {/* Progress indicator */}
        {hasProgress && !showAnswer && !isCompleted && (
          <div className={styles.clueProgress} data-testid="clue-progress">
            {progress}
          </div>
        )}

        {/* Answer display (for solution mode or completed clues) */}
        {(showAnswer || isCompleted) && clue.answer && (
          <div className={styles.clueAnswer} data-testid="clue-answer">
            {clue.answer}
          </div>
        )}
      </div>

      {/* Completion indicator */}
      {isCompleted && (
        <div className={styles.completionIndicator} data-testid="completion-indicator">
          ✓
        </div>
      )}

      {/* Active indicator */}
      {isActive && !isCompleted && (
        <div className={styles.activeIndicator} data-testid="active-indicator">
          ▶
        </div>
      )}
    </div>
  );
};

export default ClueItem;
