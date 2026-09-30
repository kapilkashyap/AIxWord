/**
 * PuzzleContainer component - Main container orchestrating the puzzle flow.
 * 
 * This component manages the complete puzzle lifecycle:
 * - Puzzle generation
 * - Grid display and interaction
 * - Clue display
 * - Solving assistance (AI solve, hints)
 * - Validation
 * 
 * Features:
 * - Integrates all puzzle-related components
 * - Manages state for puzzle generation and solving
 * - Handles API calls for all puzzle operations
 * - Provides responsive layout
 * - Error handling and user feedback
 */

import React, { useState, useCallback } from 'react';
import { apiClient } from '../services/api';
import { usePuzzle } from '../hooks/usePuzzle';
import { useAPI, useMultiAPI } from '../hooks/useAPI';
import type {
  PuzzleGenerateRequest,
  PuzzleGenerateResponse,
  SolveResponse,
  HintResponse,
  ValidateResponse,
} from '../types/api';
import { PuzzleGeneratorForm } from './PuzzleGeneratorForm';
import { GenerationProgress } from './GenerationProgress';
import { Grid } from './Grid';
import { CluePanel } from './CluePanel';
import { PuzzleActions } from './PuzzleActions';
import styles from './PuzzleContainer.module.css';

export interface PuzzleContainerProps {
  /** Optional CSS class name */
  className?: string;
}

/**
 * PuzzleContainer component orchestrates the entire puzzle experience.
 */
export const PuzzleContainer: React.FC<PuzzleContainerProps> = ({ className }) => {
  // Puzzle state management
  const {
    puzzle,
    userCells,
    selectedCell,
    currentDirection,
    activeClue,
    isComplete,
    completionPercentage,
    loadPuzzle,
    clearPuzzle,
    setCellValue,
    resetGrid,
    selectCell,
    selectClue,
    setActiveClue,
    toggleDirection,
  } = usePuzzle();

  // API state management
  const generateAPI = useAPI<PuzzleGenerateResponse>();
  const solveAPI = useMultiAPI<SolveResponse>();
  const hintAPI = useAPI<HintResponse>();
  const validateAPI = useAPI<ValidateResponse>();

  // Local state
  const [showGenerator, setShowGenerator] = useState(true);
  const [validationResult, setValidationResult] = useState<ValidateResponse | null>(null);
  const [hintMessage, setHintMessage] = useState<string | null>(null);

  /**
   * Handle puzzle generation
   */
  const handleGeneratePuzzle = useCallback(
    async (request: PuzzleGenerateRequest) => {
      const response = await generateAPI.execute(() => apiClient.generatePuzzle(request));

      if (response?.success && response.puzzle) {
        loadPuzzle(response.puzzle);
        setShowGenerator(false);
        setValidationResult(null);
        setHintMessage(null);
      }
    },
    [generateAPI, loadPuzzle]
  );

  /**
   * Handle solve entire puzzle
   */
  const handleSolvePuzzle = useCallback(async () => {
    if (!puzzle) return;

    const response = await solveAPI.execute('puzzle', () =>
      apiClient.solvePuzzle(puzzle.puzzle_id, { use_hints: true })
    );

    if (response?.success && response.updated_cells) {
      // Update all cells with the solution
      response.updated_cells.forEach((cell) => {
        if (cell.value) {
          setCellValue(cell.row, cell.col, cell.value);
        }
      });
    }
  }, [puzzle, solveAPI, setCellValue]);

  /**
   * Handle solve current word
   */
  const handleSolveWord = useCallback(async () => {
    if (!puzzle || !activeClue) return;

    const response = await solveAPI.execute(`word-${activeClue.number}-${activeClue.direction}`, () =>
      apiClient.solveWord(puzzle.puzzle_id, {
        clue_number: activeClue.number,
        direction: activeClue.direction,
        use_intersections: true,
      })
    );

    if (response?.success && response.updated_cells) {
      // Update cells for this word
      response.updated_cells.forEach((cell) => {
        if (cell.value) {
          setCellValue(cell.row, cell.col, cell.value);
        }
      });
    }
  }, [puzzle, activeClue, solveAPI, setCellValue]);

  /**
   * Handle get hint
   */
  const handleGetHint = useCallback(async () => {
    if (!puzzle || !activeClue) return;

    const response = await hintAPI.execute(() =>
      apiClient.getHint(puzzle.puzzle_id, {
        clue_number: activeClue.number,
        direction: activeClue.direction,
        hint_type: 'definition',
      })
    );

    if (response?.success) {
      setHintMessage(response.hint);
      // Auto-clear hint after 10 seconds
      setTimeout(() => setHintMessage(null), 10000);
    }
  }, [puzzle, activeClue, hintAPI]);

  /**
   * Handle validate solution
   */
  const handleValidate = useCallback(async () => {
    if (!puzzle) return;

    const response = await validateAPI.execute(() =>
      apiClient.validateSolution(puzzle.puzzle_id, { cells: userCells })
    );

    if (response) {
      setValidationResult(response);
      // Auto-clear validation after 10 seconds
      setTimeout(() => setValidationResult(null), 10000);
    }
  }, [puzzle, userCells, validateAPI]);

  /**
   * Handle reset puzzle
   */
  const handleReset = useCallback(() => {
    resetGrid();
    setValidationResult(null);
    setHintMessage(null);
  }, [resetGrid]);

  /**
   * Handle new puzzle
   */
  const handleNewPuzzle = useCallback(() => {
    clearPuzzle();
    setShowGenerator(true);
    setValidationResult(null);
    setHintMessage(null);
    generateAPI.reset();
  }, [clearPuzzle, generateAPI]);

  /**
   * Handle cell change from Grid
   */
  const handleCellChange = useCallback(
    (cells: typeof userCells) => {
      // Update cells individually
      cells.forEach((cell, index) => {
        if (userCells[index]?.value !== cell.value) {
          setCellValue(cell.row, cell.col, cell.value);
        }
      });
    },
    [userCells, setCellValue]
  );

  /**
   * Handle direction change from Grid
   */
  const handleDirectionChange = useCallback(() => {
    toggleDirection();
  }, [toggleDirection]);

  return (
    <div className={`${styles.container} ${className || ''}`} data-testid="puzzle-container">
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>🧩 AIxWord</h1>
          <p className={styles.subtitle}>AI-Powered Interactive Crossword Puzzles</p>
        </div>
        {puzzle && (
          <button
            className={styles.newPuzzleButton}
            onClick={handleNewPuzzle}
            data-testid="new-puzzle-button"
          >
            <span>➕</span>
            <span>New Puzzle</span>
          </button>
        )}
      </div>

      {/* Main Content */}
      <div className={styles.content}>
        {/* Generator View */}
        {showGenerator && (
          <div className={styles.generatorView}>
            <PuzzleGeneratorForm
              onSubmit={handleGeneratePuzzle}
              isLoading={generateAPI.loading}
              error={generateAPI.error}
            />
            <GenerationProgress
              isGenerating={generateAPI.loading}
              response={generateAPI.data}
              error={generateAPI.error}
            />
          </div>
        )}

        {/* Puzzle View */}
        {!showGenerator && puzzle && (
          <div className={styles.puzzleView}>
            {/* Puzzle Info Bar */}
            <div className={styles.infoBar}>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Topic:</span>
                <span className={styles.infoValue}>{puzzle.topic}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Progress:</span>
                <span className={styles.infoValue}>{Math.round(completionPercentage)}%</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Words:</span>
                <span className={styles.infoValue}>{puzzle.word_count}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Difficulty:</span>
                <span className={styles.infoValue}>
                  {puzzle.difficulty.charAt(0).toUpperCase() + puzzle.difficulty.slice(1)}
                </span>
              </div>
            </div>

            {/* Notifications */}
            {hintMessage && (
              <div className={styles.notification} data-testid="hint-notification">
                <span className={styles.notificationIcon}>💡</span>
                <span className={styles.notificationText}>{hintMessage}</span>
                <button
                  className={styles.notificationClose}
                  onClick={() => setHintMessage(null)}
                  aria-label="Close hint"
                >
                  ✕
                </button>
              </div>
            )}

            {validationResult && (
              <div
                className={`${styles.notification} ${
                  validationResult.is_valid ? styles.notificationSuccess : styles.notificationError
                }`}
                data-testid="validation-notification"
              >
                <span className={styles.notificationIcon}>
                  {validationResult.is_valid ? '✅' : '❌'}
                </span>
                <span className={styles.notificationText}>
                  {validationResult.is_valid
                    ? 'Perfect! All answers are correct! 🎉'
                    : `${validationResult.correct_count} of ${validationResult.total_count} correct (${Math.round(validationResult.accuracy * 100)}%)`}
                </span>
                <button
                  className={styles.notificationClose}
                  onClick={() => setValidationResult(null)}
                  aria-label="Close validation"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Puzzle Grid and Clues */}
            <div className={styles.puzzleContent}>
              {/* Grid Section */}
              <div className={styles.gridSection}>
                <Grid
                  cells={userCells}
                  gridSize={puzzle.grid_size}
                  cluesAcross={puzzle.clues_across}
                  cluesDown={puzzle.clues_down}
                  selectedCell={selectedCell}
                  currentDirection={currentDirection}
                  activeClue={activeClue}
                  onCellSelect={selectCell}
                  onCellChange={handleCellChange}
                  onDirectionChange={handleDirectionChange}
                  onActiveClueChange={setActiveClue}
                />
              </div>

              {/* Clues Section */}
              <div className={styles.cluesSection}>
                <CluePanel
                  cluesAcross={puzzle.clues_across}
                  cluesDown={puzzle.clues_down}
                  cells={userCells}
                  activeClue={activeClue}
                  onClueClick={selectClue}
                  showAnswers={false}
                  initialLayout="tabs"
                  collapsible={true}
                  showSearch={true}
                  showLayoutToggle={true}
                />
              </div>
            </div>

            {/* Actions */}
            <div className={styles.actionsSection}>
              <PuzzleActions
                hasPuzzle={!!puzzle}
                isComplete={isComplete}
                activeClue={activeClue}
                isSolvingPuzzle={solveAPI.getState('puzzle').loading}
                isSolvingWord={
                  activeClue
                    ? solveAPI.getState(`word-${activeClue.number}-${activeClue.direction}`).loading
                    : false
                }
                isGettingHint={hintAPI.loading}
                isValidating={validateAPI.loading}
                onSolvePuzzle={handleSolvePuzzle}
                onSolveWord={handleSolveWord}
                onGetHint={handleGetHint}
                onValidate={handleValidate}
                onReset={handleReset}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PuzzleContainer;
