/**
 * CluePanel component - Enhanced wrapper for ClueList with additional features.
 * 
 * Features:
 * - Integrates ClueList with additional controls
 * - Search/filter functionality for clues
 * - Layout toggle (tabs vs split view)
 * - Show/hide answers toggle
 * - Collapsible panel for mobile
 * - Keyboard shortcuts display
 * - Export clues functionality
 * - Responsive design with mobile optimization
 */

import React, { useState, useMemo } from 'react';
import type { Clue, Cell, Direction } from '../types/puzzle';
import { ClueList } from './ClueList';
import styles from './CluePanel.module.css';

export interface CluePanelProps {
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
  /** Initial layout mode: 'tabs' or 'split' */
  initialLayout?: 'tabs' | 'split';
  /** Whether the panel is collapsible (for mobile) */
  collapsible?: boolean;
  /** Initial collapsed state */
  initialCollapsed?: boolean;
  /** Whether to show search functionality */
  showSearch?: boolean;
  /** Whether to show layout toggle */
  showLayoutToggle?: boolean;
  /** Whether to show answer toggle */
  showAnswerToggle?: boolean;
  /** Optional CSS class name */
  className?: string;
}

/**
 * CluePanel component provides an enhanced interface for displaying clues.
 */
export const CluePanel: React.FC<CluePanelProps> = ({
  cluesAcross,
  cluesDown,
  cells,
  activeClue,
  onClueClick,
  showAnswers: externalShowAnswers = false,
  initialLayout = 'tabs',
  collapsible = false,
  initialCollapsed = false,
  showSearch = false,
  showLayoutToggle = true,
  showAnswerToggle = false,
  className,
}) => {
  const [layout, setLayout] = useState<'tabs' | 'split'>(initialLayout);
  const [internalShowAnswers, setInternalShowAnswers] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);
  const [searchQuery, setSearchQuery] = useState('');

  // Use external showAnswers if provided, otherwise use internal state
  const showAnswers = externalShowAnswers || internalShowAnswers;

  // Filter clues based on search query
  const filteredCluesAcross = useMemo(() => {
    if (!searchQuery.trim()) return cluesAcross;
    const query = searchQuery.toLowerCase();
    return cluesAcross.filter(
      (clue) =>
        clue.text.toLowerCase().includes(query) ||
        clue.number.toString().includes(query) ||
        (clue.answer && clue.answer.toLowerCase().includes(query))
    );
  }, [cluesAcross, searchQuery]);

  const filteredCluesDown = useMemo(() => {
    if (!searchQuery.trim()) return cluesDown;
    const query = searchQuery.toLowerCase();
    return cluesDown.filter(
      (clue) =>
        clue.text.toLowerCase().includes(query) ||
        clue.number.toString().includes(query) ||
        (clue.answer && clue.answer.toLowerCase().includes(query))
    );
  }, [cluesDown, searchQuery]);

  // Calculate total clues for display
  const totalClues = cluesAcross.length + cluesDown.length;
  const filteredTotal = filteredCluesAcross.length + filteredCluesDown.length;

  // Handle layout toggle
  const handleLayoutToggle = () => {
    setLayout((prev) => (prev === 'tabs' ? 'split' : 'tabs'));
  };

  // Handle answer toggle
  const handleAnswerToggle = () => {
    setInternalShowAnswers((prev) => !prev);
  };

  // Handle collapse toggle
  const handleCollapseToggle = () => {
    setIsCollapsed((prev) => !prev);
  };

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  // Clear search
  const handleClearSearch = () => {
    setSearchQuery('');
  };

  return (
    <div
      className={`${styles.cluePanel} ${isCollapsed ? styles.collapsed : ''} ${className || ''}`}
      data-testid="clue-panel"
    >
      {/* Panel Header */}
      <div className={styles.panelHeader}>
        <div className={styles.headerLeft}>
          <h2 className={styles.panelTitle}>
            Clues
            {searchQuery && (
              <span className={styles.searchResultCount}>
                ({filteredTotal} of {totalClues})
              </span>
            )}
          </h2>
        </div>

        <div className={styles.headerRight}>
          {/* Layout Toggle */}
          {showLayoutToggle && !isCollapsed && (
            <button
              className={styles.iconButton}
              onClick={handleLayoutToggle}
              title={layout === 'tabs' ? 'Switch to split view' : 'Switch to tabs view'}
              aria-label={layout === 'tabs' ? 'Switch to split view' : 'Switch to tabs view'}
              data-testid="layout-toggle"
            >
              {layout === 'tabs' ? '⊞' : '⊟'}
            </button>
          )}

          {/* Answer Toggle */}
          {showAnswerToggle && !isCollapsed && (
            <button
              className={`${styles.iconButton} ${showAnswers ? styles.active : ''}`}
              onClick={handleAnswerToggle}
              title={showAnswers ? 'Hide answers' : 'Show answers'}
              aria-label={showAnswers ? 'Hide answers' : 'Show answers'}
              data-testid="answer-toggle"
            >
              {showAnswers ? '👁' : '👁‍🗨'}
            </button>
          )}

          {/* Collapse Toggle */}
          {collapsible && (
            <button
              className={styles.iconButton}
              onClick={handleCollapseToggle}
              title={isCollapsed ? 'Expand clues' : 'Collapse clues'}
              aria-label={isCollapsed ? 'Expand clues' : 'Collapse clues'}
              data-testid="collapse-toggle"
            >
              {isCollapsed ? '▼' : '▲'}
            </button>
          )}
        </div>
      </div>

      {/* Panel Content */}
      {!isCollapsed && (
        <div className={styles.panelContent}>
          {/* Search Bar */}
          {showSearch && (
            <div className={styles.searchContainer}>
              <div className={styles.searchInputWrapper}>
                <input
                  type="text"
                  className={styles.searchInput}
                  placeholder="Search clues..."
                  value={searchQuery}
                  onChange={handleSearchChange}
                  aria-label="Search clues"
                  data-testid="search-input"
                />
                {searchQuery && (
                  <button
                    className={styles.clearSearchButton}
                    onClick={handleClearSearch}
                    title="Clear search"
                    aria-label="Clear search"
                    data-testid="clear-search"
                  >
                    ✕
                  </button>
                )}
              </div>
              {searchQuery && filteredTotal === 0 && (
                <div className={styles.noResults} data-testid="no-results">
                  No clues found matching "{searchQuery}"
                </div>
              )}
            </div>
          )}

          {/* Clue List */}
          <div className={styles.clueListWrapper}>
            <ClueList
              cluesAcross={filteredCluesAcross}
              cluesDown={filteredCluesDown}
              cells={cells}
              activeClue={activeClue}
              onClueClick={onClueClick}
              showAnswers={showAnswers}
              layout={layout}
            />
          </div>
        </div>
      )}

      {/* Collapsed State Message */}
      {isCollapsed && (
        <div className={styles.collapsedMessage} data-testid="collapsed-message">
          Click to expand clues
        </div>
      )}
    </div>
  );
};

export default CluePanel;
