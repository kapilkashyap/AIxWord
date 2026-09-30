/**
 * SolvingControls component - Manual solving control buttons.
 * 
 * This component provides a simplified set of controls specifically for
 * manual puzzle solving, separate from AI assistance features.
 * 
 * Features:
 * - Clear all input button
 * - Clear current word button
 * - Check solution button
 * - Progress display
 * - Keyboard shortcuts
 * - Responsive design
 */

import React from 'react';
import type { Direction } from '../types/puzzle';
import type { SolvingStats } from '../hooks/useSolving';
import styles from './SolvingControls.module.css';

export interface SolvingControlsProps {
  /** Whether a puzzle is loaded */
  hasPuzzle: boolean;
  /** Solving statistics */
  stats: SolvingStats;
  /** Currently active clue */
  activeClue: { number: number; direction: Direction } | null;
  /** Whether validation is in progress */
  isValidating?: boolean;
  /** Callback when clear all is clicked */
  onClearAll: () => void;
  /** Callback when clear word is clicked */
  onClearWord: () => void;
  /** Callback when check solution is clicked */
  onCheckSolution: () => void;
  /** Optional CSS class name */
  className?: string;
}

/**
 * SolvingControls component provides manual solving controls.
 */
export const SolvingControls: React.FC<SolvingControlsProps> = ({
  hasPuzzle,
  stats,
  activeClue,
  isValidating = false,
  onClearAll,
  onClearWord,
  onCheckSolution,
  className,
}) => {
  if (!hasPuzzle) {
    return null;
  }

  return (
    <div
      className={`${styles.container} ${className || ''}`}
      data-testid="solving-controls"
    >
      {/* Progress Section */}
      <div className={styles.progressSection}>
        <div className={styles.progressHeader}>
          <span className={styles.progressLabel}>Your Progress</span>
          <span className={styles.progressPercentage}>
            {Math.round(stats.cellsCompletionPercentage)}%
          </span>
        </div>

        {/* Progress Bar */}
        <div className={styles.progressBar} data-testid="progress-bar">
          <div
            className={styles.progressFill}
            style={{ width: `${stats.cellsCompletionPercentage}%` }}
            data-testid="progress-fill"
          />
        </div>

        {/* Stats */}
        <div className={styles.stats}>
          <div className={styles.statItem}>
            <span className={styles.statValue}>{stats.filledCells}</span>
            <span className={styles.statLabel}>/ {stats.totalCells} cells</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statValue}>{stats.completedWords}</span>
            <span className={styles.statLabel}>/ {stats.totalWords} words</span>
          </div>
        </div>

        {/* Completion Message */}
        {stats.isFullyComplete && (
          <div className={styles.completionMessage} data-testid="completion-message">
            🎉 All words complete! Check your solution to verify.
          </div>
        )}
      </div>

      {/* Control Buttons */}
      <div className={styles.controls}>
        {/* Clear Word Button */}
        <button
          className={`${styles.button} ${styles.clearWordButton}`}
          onClick={onClearWord}
          disabled={!activeClue || isValidating}
          title={
            activeClue
              ? `Clear ${activeClue.number} ${activeClue.direction}`
              : 'Select a word to clear'
          }
          aria-label="Clear current word"
          data-testid="clear-word-button"
        >
          <span className={styles.icon}>🗑️</span>
          <span>Clear Word</span>
        </button>

        {/* Clear All Button */}
        <button
          className={`${styles.button} ${styles.clearAllButton}`}
          onClick={onClearAll}
          disabled={stats.filledCells === 0 || isValidating}
          title="Clear all your answers"
          aria-label="Clear all answers"
          data-testid="clear-all-button"
        >
          <span className={styles.icon}>🔄</span>
          <span>Clear All</span>
        </button>

        {/* Check Solution Button */}
        <button
          className={`${styles.button} ${styles.checkButton}`}
          onClick={onCheckSolution}
          disabled={stats.filledCells === 0 || isValidating}
          title="Check your solution"
          aria-label="Check solution"
          data-testid="check-solution-button"
        >
          {isValidating ? (
            <>
              <span className={styles.spinner}></span>
              <span>Checking...</span>
            </>
          ) : (
            <>
              <span className={styles.icon}>✓</span>
              <span>Check Solution</span>
            </>
          )}
        </button>
      </div>

      {/* Keyboard Shortcuts Hint */}
      <div className={styles.shortcuts} data-testid="shortcuts-hint">
        <span className={styles.shortcutsLabel}>Keyboard:</span>
        <span className={styles.shortcutItem}>
          <kbd>←↑→↓</kbd> Navigate
        </span>
        <span className={styles.shortcutItem}>
          <kbd>Space</kbd> Toggle direction
        </span>
        <span className={styles.shortcutItem}>
          <kbd>Backspace</kbd> Clear
        </span>
        <span className={styles.shortcutItem}>
          <kbd>Tab</kbd> Next word
        </span>
      </div>
    </div>
  );
};

export default SolvingControls;
