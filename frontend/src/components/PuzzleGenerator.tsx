/**
 * PuzzleGenerator component - Orchestrates puzzle generation flow.
 * 
 * This component combines the PuzzleGeneratorForm and GenerationProgress
 * components to provide a complete puzzle generation experience.
 * 
 * Features:
 * - Puzzle generation form with validation
 * - Real-time generation progress display
 * - Success/error state handling
 * - Callback when puzzle is successfully generated
 * - Responsive layout
 * - Loading states
 * - Error recovery
 */

import React, { useState, useCallback } from 'react';
import { apiClient } from '../services/api';
import { useAPI } from '../hooks/useAPI';
import type { PuzzleGenerateRequest, PuzzleGenerateResponse } from '../types/api';
import type { Puzzle } from '../types/puzzle';
import { PuzzleGeneratorForm } from './PuzzleGeneratorForm';
import { GenerationProgress } from './GenerationProgress';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import styles from './PuzzleGenerator.module.css';

export interface PuzzleGeneratorProps {
  /** Callback when puzzle is successfully generated */
  onPuzzleGenerated?: (puzzle: Puzzle) => void;
  /** Callback when generation is cancelled */
  onCancel?: () => void;
  /** Whether to show the cancel button */
  showCancel?: boolean;
  /** Initial form values */
  initialValues?: Partial<PuzzleGenerateRequest>;
  /** Whether to show advanced options by default */
  showAdvancedOptions?: boolean;
  /** Optional CSS class name */
  className?: string;
  /** Optional test ID */
  testId?: string;
}

/**
 * PuzzleGenerator component provides a complete puzzle generation interface.
 */
export const PuzzleGenerator: React.FC<PuzzleGeneratorProps> = ({
  onPuzzleGenerated,
  onCancel,
  showCancel = false,
  // initialValues, // Reserved for future use to pre-populate form
  showAdvancedOptions = false,
  className = '',
  testId = 'puzzle-generator',
}) => {
  // API state for puzzle generation
  const { data, loading, error, execute, reset } = useAPI<PuzzleGenerateResponse>();

  // Local state
  const [generationAttempts, setGenerationAttempts] = useState(0);

  /**
   * Handle form submission to generate puzzle
   */
  const handleSubmit = useCallback(
    async (request: PuzzleGenerateRequest) => {
      setGenerationAttempts((prev) => prev + 1);

      const response = await execute(() => apiClient.generatePuzzle(request));

      // If successful and puzzle was generated, notify parent
      if (response?.success && response.puzzle && onPuzzleGenerated) {
        onPuzzleGenerated(response.puzzle);
      }
    },
    [execute, onPuzzleGenerated]
  );

  /**
   * Handle retry after error
   */
  const handleRetry = useCallback(() => {
    reset();
    setGenerationAttempts(0);
  }, [reset]);

  /**
   * Handle cancel
   */
  const handleCancel = useCallback(() => {
    reset();
    setGenerationAttempts(0);
    if (onCancel) {
      onCancel();
    }
  }, [reset, onCancel]);

  // Determine if we should show the success state
  const showSuccess = !loading && data?.success && data.puzzle;

  // Determine if we should show the error state
  const showError = !loading && (error || (data && !data.success));

  return (
    <div className={`${styles.container} ${className}`} data-testid={testId}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h2 className={styles.title}>Create Your Crossword Puzzle</h2>
          <p className={styles.subtitle}>
            Generate an AI-powered crossword puzzle on any topic in seconds
          </p>
        </div>
        {showCancel && onCancel && (
          <button
            className={styles.cancelButton}
            onClick={handleCancel}
            disabled={loading}
            aria-label="Cancel generation"
            data-testid={`${testId}-cancel`}
          >
            ✕
          </button>
        )}
      </div>

      {/* Main Content */}
      <div className={styles.content}>
        {/* Generation Form */}
        <div className={styles.formSection}>
          <PuzzleGeneratorForm
            onSubmit={handleSubmit}
            isLoading={loading}
            error={error}
            showAdvanced={showAdvancedOptions}
          />
        </div>

        {/* Generation Progress */}
        {(loading || data || error) && (
          <div className={styles.progressSection}>
            <GenerationProgress
              isGenerating={loading}
              response={data}
              error={error}
            />
          </div>
        )}

        {/* Additional Error Display with Retry */}
        {showError && (
          <div className={styles.errorSection}>
            <ErrorMessage
              message={
                error ||
                data?.error_message ||
                'Failed to generate puzzle. Please try again.'
              }
              severity="error"
              title="Generation Failed"
              dismissible={true}
              onDismiss={handleRetry}
              onRetry={handleRetry}
              retryLabel="Try Again"
              testId={`${testId}-error`}
            />
            {generationAttempts > 1 && (
              <div className={styles.attemptInfo}>
                <p className={styles.attemptText}>
                  Attempt {generationAttempts} - Don't give up! Try adjusting your settings.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Success Actions */}
        {showSuccess && data?.puzzle && (
          <div className={styles.successActions}>
            <button
              className={styles.primaryButton}
              onClick={() => onPuzzleGenerated && onPuzzleGenerated(data.puzzle!)}
              data-testid={`${testId}-start-solving`}
            >
              <span>🎯</span>
              <span>Start Solving</span>
            </button>
            <button
              className={styles.secondaryButton}
              onClick={handleRetry}
              data-testid={`${testId}-generate-another`}
            >
              <span>🔄</span>
              <span>Generate Another</span>
            </button>
          </div>
        )}

        {/* Help Text */}
        {!loading && !data && !error && (
          <div className={styles.helpSection}>
            <div className={styles.helpCard}>
              <h3 className={styles.helpTitle}>💡 Tips for Great Puzzles</h3>
              <ul className={styles.helpList}>
                <li>
                  <strong>Choose specific topics:</strong> "Ancient Rome" works better than just
                  "History"
                </li>
                <li>
                  <strong>Start with 8×8:</strong> Perfect size for beginners, generates faster
                </li>
                <li>
                  <strong>Try different difficulties:</strong> Easy for casual fun, Hard for a
                  challenge
                </li>
                <li>
                  <strong>Be patient:</strong> Generation can take 30-60 seconds for quality
                  puzzles
                </li>
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Loading Overlay (for full-screen loading) */}
      {loading && (
        <div className={styles.loadingOverlay} data-testid={`${testId}-loading-overlay`}>
          <LoadingSpinner
            size="large"
            message="Generating your puzzle... This may take up to 60 seconds."
            centered={true}
          />
        </div>
      )}
    </div>
  );
};

export default PuzzleGenerator;
