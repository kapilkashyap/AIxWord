/**
 * PuzzleGeneratorForm component - Form for generating new crossword puzzles.
 * 
 * Features:
 * - Topic input for puzzle generation
 * - Grid size selection (4x4 to 20x20, default 8x8)
 * - Difficulty level selection (easy, medium, hard)
 * - Advanced options (min/max words, max iterations)
 * - Form validation
 * - Loading state during generation
 * - Error handling and display
 * - Responsive design
 */

import React, { useState, useCallback } from 'react';
import type { PuzzleGenerateRequest } from '../types/api';
import type { Difficulty } from '../types/puzzle';
import styles from './PuzzleGeneratorForm.module.css';

export interface PuzzleGeneratorFormProps {
  /** Callback when form is submitted */
  onSubmit: (request: PuzzleGenerateRequest) => void;
  /** Whether generation is in progress */
  isLoading?: boolean;
  /** Error message to display */
  error?: string | null;
  /** Whether to show advanced options */
  showAdvanced?: boolean;
  /** Optional CSS class name */
  className?: string;
}

/**
 * Default form values
 */
const DEFAULT_VALUES: PuzzleGenerateRequest = {
  topic: '',
  grid_size: 8,
  min_words: 8,
  max_words: 15,
  difficulty: 'medium',
  max_iterations: 50,
};

/**
 * PuzzleGeneratorForm component provides a form for generating puzzles.
 */
export const PuzzleGeneratorForm: React.FC<PuzzleGeneratorFormProps> = ({
  onSubmit,
  isLoading = false,
  error = null,
  showAdvanced: initialShowAdvanced = false,
  className,
}) => {
  const [formData, setFormData] = useState<PuzzleGenerateRequest>(DEFAULT_VALUES);
  const [showAdvanced, setShowAdvanced] = useState(initialShowAdvanced);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  /**
   * Validate form data
   */
  const validateForm = useCallback((): boolean => {
    const errors: Record<string, string> = {};

    // Validate topic
    if (!formData.topic.trim()) {
      errors.topic = 'Topic is required';
    } else if (formData.topic.length > 100) {
      errors.topic = 'Topic must be 100 characters or less';
    }

    // Validate grid size
    if (formData.grid_size !== undefined && (formData.grid_size < 4 || formData.grid_size > 20)) {
      errors.grid_size = 'Grid size must be between 4 and 20';
    }

    // Validate word counts
    if (formData.min_words !== undefined && formData.min_words < 4) {
      errors.min_words = 'Minimum words must be at least 4';
    }
    if (formData.max_words !== undefined && formData.min_words !== undefined && formData.max_words < formData.min_words) {
      errors.max_words = 'Maximum words must be greater than or equal to minimum words';
    }

    // Validate max iterations
    if (formData.max_iterations !== undefined && (formData.max_iterations < 1 || formData.max_iterations > 100)) {
      errors.max_iterations = 'Max iterations must be between 1 and 100';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  }, [formData]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();

      if (validateForm()) {
        onSubmit(formData);
      }
    },
    [formData, validateForm, onSubmit]
  );

  /**
   * Handle input change
   */
  const handleChange = useCallback(
    (field: keyof PuzzleGenerateRequest, value: string | number) => {
      setFormData((prev) => ({
        ...prev,
        [field]: value,
      }));
      // Clear validation error for this field
      if (validationErrors[field]) {
        setValidationErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[field];
          return newErrors;
        });
      }
    },
    [validationErrors]
  );

  /**
   * Handle topic input change
   */
  const handleTopicChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleChange('topic', e.target.value);
    },
    [handleChange]
  );

  /**
   * Handle grid size change
   */
  const handleGridSizeChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      handleChange('grid_size', parseInt(e.target.value, 10));
    },
    [handleChange]
  );

  /**
   * Handle difficulty change
   */
  const handleDifficultyChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      handleChange('difficulty', e.target.value as Difficulty);
    },
    [handleChange]
  );

  /**
   * Handle min words change
   */
  const handleMinWordsChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleChange('min_words', parseInt(e.target.value, 10));
    },
    [handleChange]
  );

  /**
   * Handle max words change
   */
  const handleMaxWordsChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleChange('max_words', parseInt(e.target.value, 10));
    },
    [handleChange]
  );

  /**
   * Handle max iterations change
   */
  const handleMaxIterationsChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleChange('max_iterations', parseInt(e.target.value, 10));
    },
    [handleChange]
  );

  /**
   * Toggle advanced options
   */
  const handleToggleAdvanced = useCallback(() => {
    setShowAdvanced((prev) => !prev);
  }, []);

  /**
   * Reset form to defaults
   */
  const handleReset = useCallback(() => {
    setFormData(DEFAULT_VALUES);
    setValidationErrors({});
  }, []);

  return (
    <div className={`${styles.formContainer} ${className || ''}`} data-testid="puzzle-generator-form">
      <form onSubmit={handleSubmit} className={styles.form}>
        {/* Header */}
        <div className={styles.formHeader}>
          <h2 className={styles.formTitle}>Generate Puzzle</h2>
          <p className={styles.formDescription}>
            Create an AI-powered crossword puzzle on any topic
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className={styles.errorAlert} role="alert" data-testid="form-error">
            <span className={styles.errorIcon}>⚠️</span>
            <span className={styles.errorMessage}>{error}</span>
          </div>
        )}

        {/* Basic Options */}
        <div className={styles.formSection}>
          {/* Topic Input */}
          <div className={styles.formGroup}>
            <label htmlFor="topic" className={styles.label}>
              Topic <span className={styles.required}>*</span>
            </label>
            <input
              id="topic"
              type="text"
              className={`${styles.input} ${validationErrors.topic ? styles.inputError : ''}`}
              value={formData.topic}
              onChange={handleTopicChange}
              placeholder="e.g., Science, History, Technology"
              disabled={isLoading}
              aria-invalid={!!validationErrors.topic}
              aria-describedby={validationErrors.topic ? 'topic-error' : undefined}
              data-testid="topic-input"
            />
            {validationErrors.topic && (
              <span id="topic-error" className={styles.fieldError} role="alert">
                {validationErrors.topic}
              </span>
            )}
            <span className={styles.hint}>
              Enter a topic for the puzzle (e.g., "Space Exploration", "Ancient Rome")
            </span>
          </div>

          {/* Grid Size Selection */}
          <div className={styles.formGroup}>
            <label htmlFor="grid-size" className={styles.label}>
              Grid Size
            </label>
            <select
              id="grid-size"
              className={`${styles.select} ${validationErrors.grid_size ? styles.inputError : ''}`}
              value={formData.grid_size}
              onChange={handleGridSizeChange}
              disabled={isLoading}
              aria-invalid={!!validationErrors.grid_size}
              aria-describedby={validationErrors.grid_size ? 'grid-size-error' : undefined}
              data-testid="grid-size-select"
            >
              <option value={4}>4×4 (Tiny)</option>
              <option value={6}>6×6 (Small)</option>
              <option value={8}>8×8 (Standard)</option>
              <option value={10}>10×10 (Medium)</option>
              <option value={12}>12×12 (Large)</option>
              <option value={15}>15×15 (Extra Large)</option>
              <option value={20}>20×20 (Huge)</option>
            </select>
            {validationErrors.grid_size && (
              <span id="grid-size-error" className={styles.fieldError} role="alert">
                {validationErrors.grid_size}
              </span>
            )}
          </div>

          {/* Difficulty Selection */}
          <div className={styles.formGroup}>
            <label htmlFor="difficulty" className={styles.label}>
              Difficulty
            </label>
            <select
              id="difficulty"
              className={styles.select}
              value={formData.difficulty}
              onChange={handleDifficultyChange}
              disabled={isLoading}
              data-testid="difficulty-select"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <span className={styles.hint}>
              {formData.difficulty === 'easy' && 'Simple words and straightforward clues'}
              {formData.difficulty === 'medium' && 'Moderate vocabulary and clever clues'}
              {formData.difficulty === 'hard' && 'Advanced words and challenging clues'}
            </span>
          </div>
        </div>

        {/* Advanced Options Toggle */}
        <div className={styles.advancedToggle}>
          <button
            type="button"
            className={styles.toggleButton}
            onClick={handleToggleAdvanced}
            disabled={isLoading}
            aria-expanded={showAdvanced}
            data-testid="advanced-toggle"
          >
            <span className={styles.toggleIcon}>{showAdvanced ? '▼' : '▶'}</span>
            <span className={styles.toggleLabel}>Advanced Options</span>
          </button>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className={styles.formSection} data-testid="advanced-options">
            {/* Min Words */}
            <div className={styles.formGroup}>
              <label htmlFor="min-words" className={styles.label}>
                Minimum Words
              </label>
              <input
                id="min-words"
                type="number"
                className={`${styles.input} ${validationErrors.min_words ? styles.inputError : ''}`}
                value={formData.min_words}
                onChange={handleMinWordsChange}
                min={4}
                disabled={isLoading}
                aria-invalid={!!validationErrors.min_words}
                aria-describedby={validationErrors.min_words ? 'min-words-error' : undefined}
                data-testid="min-words-input"
              />
              {validationErrors.min_words && (
                <span id="min-words-error" className={styles.fieldError} role="alert">
                  {validationErrors.min_words}
                </span>
              )}
            </div>

            {/* Max Words */}
            <div className={styles.formGroup}>
              <label htmlFor="max-words" className={styles.label}>
                Maximum Words
              </label>
              <input
                id="max-words"
                type="number"
                className={`${styles.input} ${validationErrors.max_words ? styles.inputError : ''}`}
                value={formData.max_words}
                onChange={handleMaxWordsChange}
                min={4}
                disabled={isLoading}
                aria-invalid={!!validationErrors.max_words}
                aria-describedby={validationErrors.max_words ? 'max-words-error' : undefined}
                data-testid="max-words-input"
              />
              {validationErrors.max_words && (
                <span id="max-words-error" className={styles.fieldError} role="alert">
                  {validationErrors.max_words}
                </span>
              )}
            </div>

            {/* Max Iterations */}
            <div className={styles.formGroup}>
              <label htmlFor="max-iterations" className={styles.label}>
                Max Iterations
              </label>
              <input
                id="max-iterations"
                type="number"
                className={`${styles.input} ${validationErrors.max_iterations ? styles.inputError : ''}`}
                value={formData.max_iterations}
                onChange={handleMaxIterationsChange}
                min={1}
                max={100}
                disabled={isLoading}
                aria-invalid={!!validationErrors.max_iterations}
                aria-describedby={validationErrors.max_iterations ? 'max-iterations-error' : undefined}
                data-testid="max-iterations-input"
              />
              {validationErrors.max_iterations && (
                <span id="max-iterations-error" className={styles.fieldError} role="alert">
                  {validationErrors.max_iterations}
                </span>
              )}
              <span className={styles.hint}>
                Maximum number of attempts to generate the puzzle
              </span>
            </div>
          </div>
        )}

        {/* Form Actions */}
        <div className={styles.formActions}>
          <button
            type="button"
            className={styles.resetButton}
            onClick={handleReset}
            disabled={isLoading}
            data-testid="reset-button"
          >
            Reset
          </button>
          <button
            type="submit"
            className={styles.submitButton}
            disabled={isLoading || !formData.topic.trim()}
            data-testid="submit-button"
          >
            {isLoading ? (
              <>
                <span className={styles.spinner}></span>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <span>🎯</span>
                <span>Generate Puzzle</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PuzzleGeneratorForm;
