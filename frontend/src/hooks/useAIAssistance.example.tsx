/**
 * Example usage of the useAIAssistance hook.
 * 
 * This file demonstrates how to integrate AI assistance features
 * into a puzzle-solving component.
 */

import React from 'react';
import { useAIAssistance } from './useAIAssistance';
import { usePuzzle } from './usePuzzle';
import { AIAssistancePanel } from '../components/AIAssistancePanel';
import { HintModal } from '../components/HintModal';
import { ConfirmationDialog } from '../components/ConfirmationDialog';
import { SolutionAnimation } from '../components/SolutionAnimation';
import type { HintType } from '../types/puzzle';

/**
 * Example component showing AI assistance integration.
 */
export const AIAssistanceExample: React.FC = () => {
  // Get puzzle state
  const {
    puzzle,
    activeClue,
    setCellValue,
  } = usePuzzle();

  // Initialize AI assistance hook
  const aiAssistance = useAIAssistance(
    puzzle?.puzzle_id || null,
    activeClue,
    setCellValue
  );

  /**
   * Handle hint request with custom type.
   */
  const handleGetHint = (hintType: HintType = 'definition') => {
    aiAssistance.getHint(hintType);
  };

  /**
   * Handle hint modal close with optional letter reveal.
   */
  const handleHintModalClose = (revealLetter: boolean = false) => {
    if (revealLetter && aiAssistance.hintModal) {
      const { revealedLetter, position, clueNumber, direction } = aiAssistance.hintModal;
      
      if (revealedLetter && position !== null && puzzle) {
        // Find the clue and update the cell
        const clues = direction === 'across' ? puzzle.clues_across : puzzle.clues_down;
        const clue = clues.find(c => c.number === clueNumber);
        
        if (clue) {
          const row = direction === 'across' ? clue.start_row : clue.start_row + position;
          const col = direction === 'across' ? clue.start_col + position : clue.start_col;
          setCellValue(row, col, revealedLetter);
        }
      }
    }
    
    aiAssistance.closeHintModal();
  };

  return (
    <div>
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

      {/* Error Display */}
      {aiAssistance.solveWordError && (
        <div className="error">
          Error solving word: {aiAssistance.solveWordError}
          <button onClick={aiAssistance.clearErrors}>Dismiss</button>
        </div>
      )}

      {aiAssistance.solvePuzzleError && (
        <div className="error">
          Error solving puzzle: {aiAssistance.solvePuzzleError}
          <button onClick={aiAssistance.clearErrors}>Dismiss</button>
        </div>
      )}

      {aiAssistance.hintError && (
        <div className="error">
          Error getting hint: {aiAssistance.hintError}
          <button onClick={aiAssistance.clearErrors}>Dismiss</button>
        </div>
      )}

      {/* Hint Modal */}
      {aiAssistance.hintModal && (
        <HintModal
          isOpen={aiAssistance.hintModal.isVisible}
          hintText={aiAssistance.hintModal.hintText}
          hintType={aiAssistance.hintModal.hintType}
          revealedLetter={aiAssistance.hintModal.revealedLetter}
          position={aiAssistance.hintModal.position}
          clueNumber={aiAssistance.hintModal.clueNumber}
          direction={aiAssistance.hintModal.direction}
          onClose={handleHintModalClose}
          onRequestAnotherHint={handleGetHint}
        />
      )}

      {/* Confirmation Dialog */}
      {aiAssistance.confirmationDialog && (
        <ConfirmationDialog
          isOpen={aiAssistance.confirmationDialog.isVisible}
          title={aiAssistance.confirmationDialog.title}
          message={aiAssistance.confirmationDialog.message}
          confirmLabel="Yes, Solve"
          cancelLabel="Cancel"
          variant={
            aiAssistance.confirmationDialog.actionType === 'solve-puzzle'
              ? 'warning'
              : 'info'
          }
          onConfirm={aiAssistance.confirmationDialog.onConfirm}
          onCancel={aiAssistance.confirmationDialog.onCancel}
        />
      )}

      {/* Solution Animation */}
      {aiAssistance.solutionAnimation && (
        <SolutionAnimation
          isActive={aiAssistance.solutionAnimation.isActive}
          type={aiAssistance.solutionAnimation.type}
          progress={
            aiAssistance.solutionAnimation.cells.length > 0
              ? (aiAssistance.solutionAnimation.currentStep /
                  aiAssistance.solutionAnimation.cells.length) *
                100
              : 0
          }
          message={
            aiAssistance.solutionAnimation.type === 'word'
              ? 'AI is solving the word...'
              : 'AI is solving the puzzle...'
          }
        />
      )}
    </div>
  );
};

/**
 * Example: Simple integration with just solve word button.
 */
export const SimpleAIAssistanceExample: React.FC = () => {
  const { puzzle, activeClue, setCellValue } = usePuzzle();
  const aiAssistance = useAIAssistance(
    puzzle?.puzzle_id || null,
    activeClue,
    setCellValue
  );

  return (
    <div>
      <button
        onClick={aiAssistance.showSolveWordConfirmation}
        disabled={!activeClue || aiAssistance.isSolvingWord}
      >
        {aiAssistance.isSolvingWord ? 'Solving...' : 'Solve Word'}
      </button>

      {/* Minimal confirmation dialog */}
      {aiAssistance.confirmationDialog && (
        <ConfirmationDialog
          isOpen={aiAssistance.confirmationDialog.isVisible}
          title={aiAssistance.confirmationDialog.title}
          message={aiAssistance.confirmationDialog.message}
          onConfirm={aiAssistance.confirmationDialog.onConfirm}
          onCancel={aiAssistance.confirmationDialog.onCancel}
        />
      )}
    </div>
  );
};

/**
 * Example: Custom hint type selection.
 */
export const CustomHintExample: React.FC = () => {
  const { puzzle, activeClue, setCellValue } = usePuzzle();
  const aiAssistance = useAIAssistance(
    puzzle?.puzzle_id || null,
    activeClue,
    setCellValue
  );

  const [selectedHintType, setSelectedHintType] = React.useState<HintType>('definition');

  return (
    <div>
      {/* Hint Type Selector */}
      <div>
        <label>
          <input
            type="radio"
            value="letter"
            checked={selectedHintType === 'letter'}
            onChange={(e) => setSelectedHintType(e.target.value as HintType)}
          />
          Reveal Letter
        </label>
        <label>
          <input
            type="radio"
            value="definition"
            checked={selectedHintType === 'definition'}
            onChange={(e) => setSelectedHintType(e.target.value as HintType)}
          />
          Alternative Definition
        </label>
        <label>
          <input
            type="radio"
            value="synonym"
            checked={selectedHintType === 'synonym'}
            onChange={(e) => setSelectedHintType(e.target.value as HintType)}
          />
          Synonym
        </label>
      </div>

      {/* Get Hint Button */}
      <button
        onClick={() => aiAssistance.getHint(selectedHintType)}
        disabled={!activeClue || aiAssistance.isGettingHint}
      >
        {aiAssistance.isGettingHint ? 'Getting Hint...' : 'Get Hint'}
      </button>

      {/* Hint Modal */}
      {aiAssistance.hintModal && (
        <HintModal
          isOpen={aiAssistance.hintModal.isVisible}
          hintText={aiAssistance.hintModal.hintText}
          hintType={aiAssistance.hintModal.hintType}
          revealedLetter={aiAssistance.hintModal.revealedLetter}
          position={aiAssistance.hintModal.position}
          clueNumber={aiAssistance.hintModal.clueNumber}
          direction={aiAssistance.hintModal.direction}
          onClose={() => aiAssistance.closeHintModal()}
          onRequestAnotherHint={(type) => aiAssistance.getHint(type)}
        />
      )}
    </div>
  );
};

/**
 * Example: Programmatic AI assistance without UI.
 */
export const ProgrammaticAIExample: React.FC = () => {
  const { puzzle, activeClue, setCellValue } = usePuzzle();
  const aiAssistance = useAIAssistance(
    puzzle?.puzzle_id || null,
    activeClue,
    setCellValue
  );

  /**
   * Auto-solve when user is stuck (no input for 30 seconds).
   */
  React.useEffect(() => {
    if (!activeClue || aiAssistance.isAnyOperationInProgress) return;

    const timer = setTimeout(() => {
      // Offer hint after 30 seconds of inactivity
      aiAssistance.getHint('definition');
    }, 30000);

    return () => clearTimeout(timer);
  }, [activeClue, aiAssistance]);

  return (
    <div>
      <p>AI will offer hints if you're stuck for 30 seconds</p>
      
      {aiAssistance.hintModal && (
        <HintModal
          isOpen={aiAssistance.hintModal.isVisible}
          hintText={aiAssistance.hintModal.hintText}
          hintType={aiAssistance.hintModal.hintType}
          revealedLetter={aiAssistance.hintModal.revealedLetter}
          position={aiAssistance.hintModal.position}
          clueNumber={aiAssistance.hintModal.clueNumber}
          direction={aiAssistance.hintModal.direction}
          onClose={() => aiAssistance.closeHintModal()}
          onRequestAnotherHint={(type) => aiAssistance.getHint(type)}
        />
      )}
    </div>
  );
};

export default AIAssistanceExample;
