/**
 * ClueList component - Displays all clues for the crossword puzzle.
 * 
 * Features:
 * - Organized display of across and down clues
 * - Tabbed or side-by-side layout options
 * - Highlights active clue
 * - Shows completion status for each clue
 * - Scrollable list for large puzzles
 * - Click to select clue and jump to grid position
 * - Progress tracking for partially filled words
 * - Search/filter functionality (optional)
 */

import React, { useState, useRef, useEffect } from 'react';
import type { Clue, Cell, Direction } from '../types/puzzle';
import { ClueItem } from './ClueItem';
import styles from './ClueList.module.css';

export interface ClueListProps {
  /** Across clues */
  cluesAcross: Clue[];
  /** Down clues */
  cluesDown: Clue[];
  /** All cells in the grid (for progress tracking) */
  cells: Cell[];
  /** Currently active clue */
  activeClue: { number: number; direction: Direction } | null;
  /** Callback when a clue is clicked */
  onClueClick: (clue: Clue) => void;
  /** Whether to show answers (solution mode) */
  showAnswers?: boolean;
  /** Layout mode: 'tabs' or 'split' */
  layout?: 'tabs' | 'split';
  /** Optional CSS class name */
  className?: string;
}

/**
 * ClueList component renders all clues with interactive features.
 */
export const ClueList: React.FC<ClueListProps> = ({
  cluesAcross,
  cluesDown,
  cells,
  activeClue,
  onClueClick,
  showAnswers = false,
  layout = 'tabs',
  className,
}) => {
  const [activeTab, setActiveTab] = useState<Direction>('across');
  const acrossListRef = useRef<HTMLDivElement>(null);
  const downListRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to active clue when it changes
  useEffect(() => {
    if (!activeClue) return;

    const listRef = activeClue.direction === 'across' ? acrossListRef : downListRef;
    const clueElement = listRef.current?.querySelector(
      `[data-clue-number="${activeClue.number}"]`
    );

    if (clueElement) {
      clueElement.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [activeClue]);

  // Switch to the tab of the active clue
  useEffect(() => {
    if (activeClue && layout === 'tabs') {
      setActiveTab(activeClue.direction);
    }
  }, [activeClue, layout]);

  // Get current answer for a clue from cells
  const getCurrentAnswer = (clue: Clue): string => {
    const answer: string[] = [];
    for (let i = 0; i < clue.length; i++) {
      const row = clue.direction === 'across' ? clue.start_row : clue.start_row + i;
      const col = clue.direction === 'across' ? clue.start_col + i : clue.start_col;
      const cell = cells.find((c) => c.row === row && c.col === col);
      answer.push(cell?.value || '');
    }
    return answer.join('');
  };

  // Check if a clue is completed
  const isClueCompleted = (clue: Clue): boolean => {
    if (!clue.answer) return false;
    const currentAnswer = getCurrentAnswer(clue);
    return currentAnswer === clue.answer;
  };

  // Render a list of clues
  const renderClueSection = (clues: Clue[], direction: Direction, ref: React.RefObject<HTMLDivElement>) => {
    const completedCount = clues.filter(isClueCompleted).length;
    const totalCount = clues.length;

    return (
      <div className={styles.clueSection} ref={ref} data-testid={`clue-section-${direction}`}>
        {/* Section header */}
        <div className={styles.sectionHeader}>
          <h3 className={styles.sectionTitle}>
            {direction === 'across' ? '→ Across' : '↓ Down'}
          </h3>
          <div className={styles.sectionProgress}>
            {completedCount} / {totalCount}
          </div>
        </div>

        {/* Clue list */}
        <div className={styles.clueListContainer}>
          {clues.length === 0 ? (
            <div className={styles.emptyState}>
              No {direction} clues available
            </div>
          ) : (
            clues.map((clue) => {
              const isActive =
                activeClue !== null &&
                activeClue.number === clue.number &&
                activeClue.direction === direction;
              const isCompleted = isClueCompleted(clue);
              const currentAnswer = getCurrentAnswer(clue);

              return (
                <ClueItem
                  key={`${clue.number}-${direction}`}
                  clue={clue}
                  isActive={isActive}
                  isCompleted={isCompleted}
                  currentAnswer={currentAnswer}
                  onClick={onClueClick}
                  showAnswer={showAnswers}
                />
              );
            })
          )}
        </div>
      </div>
    );
  };

  // Render tabs layout
  const renderTabsLayout = () => {
    return (
      <div className={styles.tabsContainer}>
        {/* Tab buttons */}
        <div className={styles.tabButtons} role="tablist">
          <button
            className={`${styles.tabButton} ${activeTab === 'across' ? styles.active : ''}`}
            onClick={() => setActiveTab('across')}
            role="tab"
            aria-selected={activeTab === 'across'}
            aria-controls="across-panel"
            data-testid="tab-across"
          >
            → Across ({cluesAcross.length})
          </button>
          <button
            className={`${styles.tabButton} ${activeTab === 'down' ? styles.active : ''}`}
            onClick={() => setActiveTab('down')}
            role="tab"
            aria-selected={activeTab === 'down'}
            aria-controls="down-panel"
            data-testid="tab-down"
          >
            ↓ Down ({cluesDown.length})
          </button>
        </div>

        {/* Tab panels */}
        <div className={styles.tabPanels}>
          {activeTab === 'across' && (
            <div
              id="across-panel"
              role="tabpanel"
              aria-labelledby="tab-across"
              className={styles.tabPanel}
            >
              {renderClueSection(cluesAcross, 'across', acrossListRef)}
            </div>
          )}
          {activeTab === 'down' && (
            <div
              id="down-panel"
              role="tabpanel"
              aria-labelledby="tab-down"
              className={styles.tabPanel}
            >
              {renderClueSection(cluesDown, 'down', downListRef)}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render split layout
  const renderSplitLayout = () => {
    return (
      <div className={styles.splitContainer}>
        {renderClueSection(cluesAcross, 'across', acrossListRef)}
        {renderClueSection(cluesDown, 'down', downListRef)}
      </div>
    );
  };

  // Calculate overall progress
  const totalClues = cluesAcross.length + cluesDown.length;
  const completedClues =
    cluesAcross.filter(isClueCompleted).length +
    cluesDown.filter(isClueCompleted).length;
  const progressPercentage = totalClues > 0 ? (completedClues / totalClues) * 100 : 0;

  return (
    <div className={`${styles.clueList} ${className || ''}`} data-testid="clue-list">
      {/* Overall progress bar */}
      <div className={styles.overallProgress}>
        <div className={styles.progressHeader}>
          <span className={styles.progressLabel}>Progress</span>
          <span className={styles.progressValue}>
            {completedClues} / {totalClues} ({Math.round(progressPercentage)}%)
          </span>
        </div>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${progressPercentage}%` }}
            data-testid="progress-fill"
          />
        </div>
      </div>

      {/* Clue sections */}
      {layout === 'tabs' ? renderTabsLayout() : renderSplitLayout()}
    </div>
  );
};

export default ClueList;
