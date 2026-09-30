/**
 * GenerationProgress component - Displays puzzle generation progress and status.
 * 
 * Features:
 * - Shows generation status (generating, success, error)
 * - Displays progress information (iterations, word count)
 * - Animated loading state
 * - Success/error messages
 * - Responsive design
 */

import React from 'react';
import type { PuzzleGenerateResponse } from '../types/api';
import styles from './GenerationProgress.module.css';

export interface GenerationProgressProps {
  /** Whether generation is in progress */
  isGenerating: boolean;
  /** Generation response data */
  response: PuzzleGenerateResponse | null;
  /** Error message if generation failed */
  error?: string | null;
  /** Optional CSS class name */
  className?: string;
}

/**
 * GenerationProgress component displays the status of puzzle generation.
 */
export const GenerationProgress: React.FC<GenerationProgressProps> = ({
  isGenerating,
  response,
  error,
  className,
}) => {
  // Don't render if not generating and no response/error
  if (!isGenerating && !response && !error) {
    return null;
  }

  // Determine status
  const hasError = !!error || (response && !response.success);
  const hasSuccess = response?.success && response.puzzle;

  return (
    <div
      className={`${styles.container} ${className || ''}`}
      data-testid="generation-progress"
    >
      {/* Generating State */}
      {isGenerating && (
        <div className={styles.generatingState} data-testid="generating-state">
          <div className={styles.spinnerContainer}>
            <div className={styles.spinner}></div>
          </div>
          <div className={styles.statusContent}>
            <h3 className={styles.statusTitle}>Generating Puzzle...</h3>
            <p className={styles.statusMessage}>
              Our AI agents are working together to create your crossword puzzle.
              This may take 30-60 seconds.
            </p>
            <div className={styles.progressSteps}>
              <div className={styles.step}>
                <span className={styles.stepIcon}>🤖</span>
                <span className={styles.stepLabel}>Planning grid layout</span>
              </div>
              <div className={styles.step}>
                <span className={styles.stepIcon}>📝</span>
                <span className={styles.stepLabel}>Generating words and clues</span>
              </div>
              <div className={styles.step}>
                <span className={styles.stepIcon}>🔍</span>
                <span className={styles.stepLabel}>Validating puzzle</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success State */}
      {!isGenerating && hasSuccess && response && response.puzzle && (
        <div className={styles.successState} data-testid="success-state">
          <div className={styles.successIcon}>✅</div>
          <div className={styles.statusContent}>
            <h3 className={styles.statusTitle}>Puzzle Generated Successfully!</h3>
            <p className={styles.statusMessage}>
              Your crossword puzzle is ready to solve.
            </p>
            <div className={styles.statsGrid}>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Grid Size</span>
                <span className={styles.statValue}>
                  {response.puzzle.grid_size}×{response.puzzle.grid_size}
                </span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Words</span>
                <span className={styles.statValue}>{response.puzzle.word_count}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Difficulty</span>
                <span className={styles.statValue}>
                  {response.puzzle.difficulty.charAt(0).toUpperCase() +
                    response.puzzle.difficulty.slice(1)}
                </span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Fill Rate</span>
                <span className={styles.statValue}>
                  {Math.round(response.puzzle.fill_rate * 100)}%
                </span>
              </div>
            </div>
            {response.iterations > 0 && (
              <p className={styles.iterationInfo}>
                Generated in {response.iterations} iteration{response.iterations !== 1 ? 's' : ''}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Error State */}
      {!isGenerating && hasError && (
        <div className={styles.errorState} data-testid="error-state">
          <div className={styles.errorIcon}>❌</div>
          <div className={styles.statusContent}>
            <h3 className={styles.statusTitle}>Generation Failed</h3>
            <p className={styles.statusMessage}>
              {error || response?.error_message || 'An unexpected error occurred'}
            </p>
            {response && response.iterations > 0 && (
              <p className={styles.iterationInfo}>
                Attempted {response.iterations} iteration{response.iterations !== 1 ? 's' : ''}
              </p>
            )}
            <div className={styles.errorHints}>
              <p className={styles.hintTitle}>Suggestions:</p>
              <ul className={styles.hintList}>
                <li>Try a different topic</li>
                <li>Reduce the grid size</li>
                <li>Increase max iterations in advanced options</li>
                <li>Check your internet connection</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerationProgress;
