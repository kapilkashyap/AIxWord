/**
 * PuzzleContainerWithAI - Enhanced puzzle container with full AI assistance integration.
 * 
 * This component extends PuzzleContainer with complete AI assistance features:
 * - AI-powered word solving with confirmation
 * - AI-powered full puzzle solving with confirmation
 * - Hint generation with modal display
 * - Solution animations
 * - Manual solving controls
 * - Validation and progress tracking
 * 
 * It integrates all the AI assistance UI components and hooks to provide
 * a seamless experience combining manual solving with AI help.
 */

import React, { useState, useCallback } from 'react';
import { apiClient } from '../services/api';
import { useSolving } from '../hooks/useSolving';
import { useAIAssistance } from '../hooks/useAIAssistance';
import { useAPI } from '../hooks/useAPI';
import type {
  PuzzleGenerateRequest,
  PuzzleGenerateResponse,
  ValidateResponse,
} from '../types/api';
import type { HintType } from '../types/puzzle';
import { PuzzleGeneratorForm } from './PuzzleGeneratorForm';
import { GenerationProgress } from './GenerationProgress';
import { Grid } from './Grid';
import { CluePanel } from './CluePanel';
import { SolvingControls } from './SolvingControls';
import { AIAssistancePanel } from './AIAssistancePanel';
import { HintModal } from './HintModal';
import { ConfirmationDialog } from './ConfirmationDialog';
import { SolutionAnimation } from './SolutionAnimation';
import { ErrorMessage } from './ErrorMessage';
import styles from './PuzzleContainer.module.css';

export interface PuzzleContainerWithAIProps {
  /** Optional CSS class name */
  className?: string;
}

/**
 * Enhanced PuzzleContainer with full AI assistance integration.
 */
export const PuzzleContainerWithAI: React.FC<PuzzleContainerWithAIProps> = ({ className }) => {
  // Puzzle state management with solving stats
  // useSolving() includes all usePuzzle() state plus solving-specific features
  const solving = useSolving();
  const {
    puzzle,
    userCells,
    selectedCell,
    currentDirection,
    activeClue,
    completionPercentage,
    loadPuzzle,
    clearPuzzle,
    setCellValue,
    selectCell,
    selectClue,
    setActiveClue,
    toggleDirection,
    solvingStats,
    clearAllInput,
    clearWord,
  } = solving;

  // AI assistance hook
  const aiAssistance = useAIAssistance(
    puzzle?.puzzle_id || null,
    activeClue,
    setCellValue
  );

  // API state management
  const generateAPI = useAPI<PuzzleGenerateResponse>();
  const validateAPI = useAPI<ValidateResponse>();

  // Local state
  const [showGenerator, setShowGenerator] = useState(true);
  const [validationResult, setValidationResult] = useState<ValidateResponse | null>(null);

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
        aiAssistance.clearErrors();
      }
    },
    [generateAPI, loadPuzzle, aiAssistance]
  );

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
      // Auto-clear validation after 15 seconds
      setTimeout(() => setValidationResult(null), 15000);
    }
  }, [puzzle, userCells, validateAPI]);

  /**
   * Handle clear word
   */
  const handleClearWord = useCallback(() => {
    if (!activeClue) return;
    clearWord(activeClue.number, activeClue.direction);
  }, [activeClue, clearWord]);

  /**
   * Handle new puzzle
   */
  const handleNewPuzzle = useCallback(() => {
    clearPuzzle();
    setShowGenerator(true);
    setValidationResult(null);
    aiAssistance.clearErrors();
    generateAPI.reset();
  }, [clearPuzzle, aiAssistance, generateAPI]);

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

  /**
   * Handle hint request with type selection
   */
  const handleGetHint = useCallback(
    (hintType: HintType = 'definition') => {
      // Get the clue text for context
      let clueText = '';
      if (activeClue && puzzle) {
        const clues = activeClue.direction === 'across' ? puzzle.clues_across : puzzle.clues_down;
        const clue = clues.find(c => c.number === activeClue.number);
        clueText = clue?.text || '';
      }
      aiAssistance.getHint(hintType, clueText);
    },
    [aiAssistance, activeClue, puzzle]
  );

  /**
   * Handle hint modal close
   */
  const handleHintModalClose = useCallback(() => {
    aiAssistance.closeHintModal();
  }, [aiAssistance]);

  /**
   * Handle animation complete
   */
  const handleAnimationComplete = useCallback(() => {
    // Animation state is managed by the hook, no action needed
  }, []);

  return (
    <div className={`${styles.container} ${className || ''}`} data-testid="puzzle-container-with-ai">
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

            {/* Error Messages */}
            {aiAssistance.solveWordError && (
              <ErrorMessage
                message={aiAssistance.solveWordError}
                severity="error"
                onDismiss={aiAssistance.clearErrors}
                dismissible={true}
              />
            )}
            {aiAssistance.solvePuzzleError && (
              <ErrorMessage
                message={aiAssistance.solvePuzzleError}
                severity="error"
                onDismiss={aiAssistance.clearErrors}
                dismissible={true}
              />
            )}
            {aiAssistance.hintError && (
              <ErrorMessage
                message={aiAssistance.hintError}
                severity="error"
                onDismiss={aiAssistance.clearErrors}
                dismissible={true}
              />
            )}

            {/* Validation Result */}
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

            {/* Controls Section */}
            <div className={styles.controlsSection}>
              {/* Manual Solving Controls */}
              <SolvingControls
                hasPuzzle={!!puzzle}
                stats={solvingStats}
                activeClue={activeClue}
                isValidating={validateAPI.loading}
                onClearAll={clearAllInput}
                onClearWord={handleClearWord}
                onCheckSolution={handleValidate}
              />

              {/* AI Assistance Panel */}
              <AIAssistancePanel
                hasPuzzle={!!puzzle}
                activeClue={activeClue}
                isSolvingWord={aiAssistance.isSolvingWord}
                isSolvingPuzzle={aiAssistance.isSolvingPuzzle}
                isGettingHint={aiAssistance.isGettingHint}
                onSolveWord={aiAssistance.showSolveWordConfirmation}
                onSolvePuzzle={aiAssistance.showSolvePuzzleConfirmation}
                onGetHint={() => handleGetHint('definition')}
              />
            </div>
          </div>
        )}
      </div>

      {/* Modals and Overlays */}
      {aiAssistance.hintModal && (
        <HintModal
          isOpen={aiAssistance.hintModal.isVisible}
          hint={aiAssistance.hintModal.hint}
          hintType={aiAssistance.hintModal.hintType}
          revealedLetter={aiAssistance.hintModal.revealedLetter}
          position={aiAssistance.hintModal.position}
          clueInfo={aiAssistance.hintModal.clueInfo}
          onClose={handleHintModalClose}
        />
      )}

      {aiAssistance.confirmationDialog && (
        <ConfirmationDialog
          isOpen={aiAssistance.confirmationDialog.isVisible}
          title={aiAssistance.confirmationDialog.title}
          message={aiAssistance.confirmationDialog.message}
          confirmLabel="Yes, Solve"
          cancelLabel="Cancel"
          confirmVariant={aiAssistance.confirmationDialog.actionType === 'solve-puzzle' ? 'warning' : 'primary'}
          onConfirm={aiAssistance.confirmationDialog.onConfirm}
          onCancel={aiAssistance.confirmationDialog.onCancel}
        />
      )}

      {aiAssistance.solutionAnimation && (
        <SolutionAnimation
          cells={aiAssistance.solutionAnimation.cells.map(cell => ({
            row: cell.row,
            col: cell.col,
            value: cell.value,
            is_blocked: false,
            number: null,
          }))}
          isAnimating={aiAssistance.solutionAnimation.isActive}
          onComplete={handleAnimationComplete}
          speed={aiAssistance.solutionAnimation.type === 'word' ? 150 : 100}
        />
      )}
    </div>
  );
};

export default PuzzleContainerWithAI;
