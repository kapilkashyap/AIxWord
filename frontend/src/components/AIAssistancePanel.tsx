/**
 * AIAssistancePanel component - AI-powered solving assistance controls.
 * 
 * This component provides three AI assistance features:
 * - Solve Word: AI solves the currently selected word
 * - Solve Puzzle: AI solves the entire puzzle
 * - Get Hint: AI provides a hint for the selected word
 * 
 * Features:
 * - Loading states for each action
 * - Error handling and display
 * - Disabled states when no word is selected
 * - Responsive design matching existing components
 * - Accessible with ARIA labels
 */

import React from 'react';
import type { Direction } from '../types/puzzle';
import styles from './AIAssistancePanel.module.css';

export interface AIAssistancePanelProps {
  /** Whether a puzzle is loaded */
  hasPuzzle: boolean;
  /** Currently active clue */
  activeClue: { number: number; direction: Direction } | null;
  /** Whether solve word operation is in progress */
  isSolvingWord?: boolean;
  /** Whether solve puzzle operation is in progress */
  isSolvingPuzzle?: boolean;
  /** Whether hint generation is in progress */
  isGettingHint?: boolean;
  /** Callback when solve word is clicked */
  onSolveWord: () => void;
  /** Callback when solve puzzle is clicked */
  onSolvePuzzle: () => void;
  /** Callback when get hint is clicked */
  onGetHint: () => void;
  /** Optional CSS class name */
  className?: string;
}

/**
 * AIAssistancePanel component provides AI-powered solving assistance.
 */
export const AIAssistancePanel: React.FC<AIAssistancePanelProps> = ({
  hasPuzzle,
  activeClue,
  isSolvingWord = false,
  isSolvingPuzzle = false,
  isGettingHint = false,
  onSolveWord,
  onSolvePuzzle,
  onGetHint,
  className,
}) => {
  if (!hasPuzzle) {
    return null;
  }

  const hasActiveClue = activeClue !== null;
  const isAnyOperationInProgress = isSolvingWord || isSolvingPuzzle || isGettingHint;

  return (
    <div
      className={`${styles.container} ${className || ''}`}
      data-testid="ai-assistance-panel"
    >
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerIcon}>🤖</div>
        <div className={styles.headerContent}>
          <h3 className={styles.title}>AI Assistance</h3>
          <p className={styles.subtitle}>
            Get help solving the puzzle with AI
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className={styles.actions}>
        {/* Solve Word Button */}
        <button
          className={`${styles.button} ${styles.solveWordButton}`}
          onClick={onSolveWord}
          disabled={!hasActiveClue || isAnyOperationInProgress}
          title={
            hasActiveClue
              ? `Solve ${activeClue.number} ${activeClue.direction} with AI`
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
              <span className={styles.icon}>✨</span>
              <span>Solve Word</span>
            </>
          )}
        </button>

        {/* Get Hint Button */}
        <button
          className={`${styles.button} ${styles.hintButton}`}
          onClick={onGetHint}
          disabled={!hasActiveClue || isAnyOperationInProgress}
          title={
            hasActiveClue
              ? `Get a hint for ${activeClue.number} ${activeClue.direction}`
              : 'Select a word to get a hint'
          }
          aria-label="Get hint for current word"
          data-testid="get-hint-button"
        >
          {isGettingHint ? (
            <>
              <span className={styles.spinner}></span>
              <span>Getting Hint...</span>
            </>
          ) : (
            <>
              <span className={styles.icon}>💡</span>
              <span>Get Hint</span>
            </>
          )}
        </button>

        {/* Solve Puzzle Button */}
        <button
          className={`${styles.button} ${styles.solvePuzzleButton}`}
          onClick={onSolvePuzzle}
          disabled={isAnyOperationInProgress}
          title="Solve the entire puzzle with AI"
          aria-label="Solve entire puzzle with AI"
          data-testid="solve-puzzle-button"
        >
          {isSolvingPuzzle ? (
            <>
              <span className={styles.spinner}></span>
              <span>Solving Puzzle...</span>
            </>
          ) : (
            <>
              <span className={styles.icon}>🎯</span>
              <span>Solve Puzzle</span>
            </>
          )}
        </button>
      </div>

      {/* Info Message */}
      {!hasActiveClue && (
        <div className={styles.infoMessage} data-testid="select-word-hint">
          <span className={styles.infoIcon}>ℹ️</span>
          <span>Select a word to use Solve Word or Get Hint</span>
        </div>
      )}

      {/* Warning Message */}
      <div className={styles.warningMessage} data-testid="ai-warning">
        <span className={styles.warningIcon}>⚠️</span>
        <span>
          AI assistance will overwrite your current answers for the selected word or puzzle.
        </span>
      </div>
    </div>
  );
};

export default AIAssistancePanel;
