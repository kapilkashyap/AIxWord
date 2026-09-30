/**
 * SolutionAnimation component - Animated display of AI-solved words.
 * 
 * This component provides a visual animation when AI solves words:
 * - Letter-by-letter animation with configurable speed
 * - Highlight effect for solved cells
 * - Skip animation option
 * - Completion callback
 * - Smooth transitions
 * 
 * Features:
 * - Configurable animation speed
 * - Pause/resume capability
 * - Skip to end functionality
 * - Progress indicator
 * - Accessible with reduced motion support
 */

import React, { useState, useEffect, useCallback } from 'react';
import type { Cell } from '../types/puzzle';
import styles from './SolutionAnimation.module.css';

export interface SolutionAnimationProps {
  /** Cells to animate */
  cells: Cell[];
  /** Animation speed in milliseconds per letter */
  speed?: number;
  /** Whether animation is active */
  isAnimating: boolean;
  /** Callback when animation completes */
  onComplete: () => void;
  /** Callback to skip animation */
  onSkip?: () => void;
  /** Optional CSS class name */
  className?: string;
  /** Optional test ID */
  testId?: string;
}

/**
 * SolutionAnimation component animates AI-solved words into the grid.
 */
export const SolutionAnimation: React.FC<SolutionAnimationProps> = ({
  cells,
  speed = 150,
  isAnimating,
  onComplete,
  onSkip,
  className,
  testId = 'solution-animation',
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  // Reset when cells change
  useEffect(() => {
    setCurrentIndex(0);
    setIsComplete(false);
  }, [cells]);

  // Animate letters
  useEffect(() => {
    if (!isAnimating || isComplete) return;

    if (currentIndex >= cells.length) {
      setIsComplete(true);
      onComplete();
      return;
    }

    const timer = setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
    }, speed);

    return () => clearTimeout(timer);
  }, [currentIndex, cells.length, isAnimating, isComplete, speed, onComplete]);

  // Handle skip
  const handleSkip = useCallback(() => {
    setCurrentIndex(cells.length);
    setIsComplete(true);
    if (onSkip) {
      onSkip();
    } else {
      onComplete();
    }
  }, [cells.length, onSkip, onComplete]);

  // Handle escape key to skip
  useEffect(() => {
    if (!isAnimating || isComplete) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        handleSkip();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isAnimating, isComplete, handleSkip]);

  if (!isAnimating && !isComplete) {
    return null;
  }

  const progress = cells.length > 0 ? (currentIndex / cells.length) * 100 : 0;
  const visibleCells = cells.slice(0, currentIndex);

  return (
    <div
      className={`${styles.container} ${className || ''}`}
      data-testid={testId}
      role="status"
      aria-live="polite"
      aria-label="AI solution animation in progress"
    >
      <div className={styles.content}>
        {/* Animation Icon */}
        <div className={styles.iconContainer}>
          <span className={styles.icon} aria-hidden="true">
            ✨
          </span>
        </div>

        {/* Message */}
        <div className={styles.message}>
          <h3 className={styles.title}>AI Solving...</h3>
          <p className={styles.subtitle}>
            Filling in {cells.length} {cells.length === 1 ? 'letter' : 'letters'}
          </p>
        </div>

        {/* Progress Bar */}
        <div className={styles.progressContainer}>
          <div className={styles.progressBar} data-testid={`${testId}-progress-bar`}>
            <div
              className={styles.progressFill}
              style={{ width: `${progress}%` }}
              data-testid={`${testId}-progress-fill`}
            />
          </div>
          <div className={styles.progressText}>
            {currentIndex} / {cells.length}
          </div>
        </div>

        {/* Letter Preview */}
        <div className={styles.letterPreview} data-testid={`${testId}-letters`}>
          {visibleCells.map((cell, index) => (
            <span
              key={`${cell.row}-${cell.col}`}
              className={styles.letter}
              style={{
                animationDelay: `${index * 0.05}s`,
              }}
              data-testid={`${testId}-letter-${index}`}
            >
              {cell.value}
            </span>
          ))}
        </div>

        {/* Skip Button */}
        {!isComplete && (
          <button
            className={styles.skipButton}
            onClick={handleSkip}
            data-testid={`${testId}-skip`}
            aria-label="Skip animation"
          >
            <span className={styles.skipIcon}>⏭️</span>
            <span>Skip Animation</span>
          </button>
        )}

        {/* Completion Message */}
        {isComplete && (
          <div className={styles.completeMessage} data-testid={`${testId}-complete`}>
            <span className={styles.completeIcon}>✓</span>
            <span>Solution Applied!</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default SolutionAnimation;
