/**
 * PuzzleActions component - Action buttons for puzzle solving assistance.
 * 
 * Features:
 * - Solve entire puzzle button
 * - Solve current word button
 * - Get hint button
 * - Validate solution button
 * - Reset puzzle button
 * - Loading states for each action
 * - Disabled states based on puzzle state
 * - Tooltips and keyboard shortcuts
 * - Responsive design
 */

import React from 'react';
import type { Direction } from '../types/puzzle';
import styles from './PuzzleActions.module.css';

export interface PuzzleActionsProps {
  /** Whether a puzzle is loaded */
  hasPuzzle: boolean;
  /** Whether puzzle is complete */
  isComplete: boolean;
  /** Currently active clue */
  activeClue: { number: number; direction: Direction } | null;
  /** Whether solve puzzle is in progress */
  isSolvingPuzzle?: boolean;
  /** Whether solve word is in progress */
  isSolvingWord?: boolean;
  /** Whether getting hint is in progress */
  isGettingHint?: boolean;
  /** Whether validating is in progress */
  isValidating?: boolean;
  /** Callback when solve puzzle is clicked */
  onSolvePuzzle: () => void;
  /** Callback when solve word is clicked */
  onSolveWord: () => void;
  /** Callback when get hint is clicked */
  onGetHint: () => void;
  /** Callback when validate is clicked */
  onValidate: () => void;
  /** Callback when reset is clicked */
  onReset: () => void;
  /** Optional CSS class name */
  className?: string;
}

/**
 * PuzzleActions component provides action buttons for puzzle solving.
 */
export const PuzzleActions: React.FC<PuzzleActionsProps> = ({
  hasPuzzle,
  isComplete,
  activeClue,
  isSolvingPuzzle = false,
  isSolvingWord = false,
  isGettingHint = false,
  isValidating = false,
  onSolvePuzzle,
  onSolveWord,
  onGetHint,
  onValidate,
  onReset,
  className,
}) => {
  const isAnyActionInProgress =
    isSolvingPuzzle || isSolvingWord || isGettingHint || isValidating;

  return (
    <div
      className={`${styles.container} ${className || ''}`}
      data-testid="puzzle-actions"
    >
      {/* Primary Actions */}
      <div className={styles.primaryActions}>
        {/* Solve Puzzle Button */}
        <button
          className={`${styles.button} ${styles.primaryButton}`}
          onClick={onSolvePuzzle}
          disabled={!hasPuzzle || isComplete || isAnyActionInProgress}
          title="Let AI solve the entire puzzle"
          aria-label="Solve entire puzzle with AI"
          data-testid="solve-puzzle-button"
        >
          {isSolvingPuzzle ? (
            <>
              <span className={styles.spinner}></span>
              <span>Solving...</span>
            </>
          ) : (
            <>
              <span className={styles.icon}>🤖</span>
              <span>Solve Puzzle</span>
            </>
          )}
        </button>

        {/* Validate Button */}
        <button
          className={`${styles.button} ${styles.secondaryButton}`}
          onClick={onValidate}
          disabled={!hasPuzzle || isAnyActionInProgress}
          title="Check your solution"
          aria-label="Validate solution"
          data-testid="validate-button"
        >
          {isValidating ? (
            <>
              <span className={styles.spinner}></span>
              <span>Checking...</span>
            </>
          ) : (
            <>
              <span className={styles.icon}>✓</span>
              <span>Validate</span>
            </>
          )}
        </button>
      </div>

      {/* Secondary Actions */}
      <div className={styles.secondaryActions}>
        {/* Solve Word Button */}
        <button
          className={`${styles.button} ${styles.tertiaryButton}`}
          onClick={onSolveWord}
          disabled={!hasPuzzle || !activeClue || isComplete || isAnyActionInProgress}
          title={
            activeClue
              ? `Solve ${activeClue.number} ${activeClue.direction}`
              : 'Select a word to solve'
          }
          aria-label="Solve current word with AI"
          data-testid="solve-word-button"
        >
          {isSolvingWord ? (
            <>
              <span className={styles.spinner}></span>
              <span>Solving...</span>
            </>
          ) : (
            <>
              <span className={styles.icon}>💡</span>
              <span>Solve Word</span>
            </>
          )}
        </button>

        {/* Get Hint Button */}
        <button
          className={`${styles.button} ${styles.tertiaryButton}`}
          onClick={onGetHint}
          disabled={!hasPuzzle || !activeClue || isComplete || isAnyActionInProgress}
          title={
            activeClue
              ? `Get hint for ${activeClue.number} ${activeClue.direction}`
              : 'Select a word to get a hint'
          }
          aria-label="Get hint for current word"
          data-testid="get-hint-button"
        >
          {isGettingHint ? (
            <>
              <span className={styles.spinner}></span>
              <span>Getting...</span>
            </>
          ) : (
            <>
              <span className={styles.icon}>💭</span>
              <span>Get Hint</span>
            </>
          )}
        </button>

        {/* Reset Button */}
        <button
          className={`${styles.button} ${styles.dangerButton}`}
          onClick={onReset}
          disabled={!hasPuzzle || isAnyActionInProgress}
          title="Clear all answers and start over"
          aria-label="Reset puzzle"
          data-testid="reset-button"
        >
          <span className={styles.icon}>🔄</span>
          <span>Reset</span>
        </button>
      </div>

      {/* Help Text */}
      {!hasPuzzle && (
        <div className={styles.helpText} data-testid="help-text">
          Generate a puzzle to enable actions
        </div>
      )}

      {hasPuzzle && !activeClue && (
        <div className={styles.helpText} data-testid="help-text">
          Click on a clue or cell to enable word-specific actions
        </div>
      )}

      {isComplete && (
        <div className={styles.completeText} data-testid="complete-text">
          🎉 Puzzle complete! Validate to check your solution.
        </div>
      )}
    </div>
  );
};

export default PuzzleActions;
