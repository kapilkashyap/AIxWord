/**
 * Unit tests for CluePanel component.
 * 
 * Tests cover:
 * - Rendering with different props
 * - Search functionality
 * - Layout toggle (tabs vs split)
 * - Answer toggle
 * - Collapse/expand functionality
 * - Clue filtering
 * - User interactions
 * - Accessibility features
 * - Responsive behavior
 */

import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CluePanel } from '../CluePanel';
import type { Clue, Cell } from '../../types/puzzle';

describe('CluePanel Component', () => {
  // Mock callbacks
  const mockOnClueClick = vi.fn();

  // Mock scrollIntoView for jsdom
  beforeAll(() => {
    Element.prototype.scrollIntoView = vi.fn();
  });

  beforeEach(() => {
    mockOnClueClick.mockClear();
  });

  // Helper function to create mock clues
  const createMockClue = (overrides: Partial<Clue> = {}): Clue => ({
    number: 1,
    direction: 'across',
    text: 'Test clue',
    answer: 'TEST',
    start_row: 0,
    start_col: 0,
    length: 4,
    ...overrides,
  });

  // Helper function to create mock cells
  const createMockCells = (count: number = 64): Cell[] => {
    const cells: Cell[] = [];
    for (let i = 0; i < count; i++) {
      cells.push({
        row: Math.floor(i / 8),
        col: i % 8,
        value: null,
        is_blocked: false,
        number: null,
      });
    }
    return cells;
  };

  // Sample clues for testing
  const sampleCluesAcross: Clue[] = [
    createMockClue({ number: 1, text: 'Capital of France', answer: 'PARIS', length: 5 }),
    createMockClue({ number: 3, text: 'Opposite of hot', answer: 'COLD', length: 4 }),
    createMockClue({ number: 5, text: 'Large body of water', answer: 'OCEAN', length: 5 }),
  ];

  const sampleCluesDown: Clue[] = [
    createMockClue({
      number: 1,
      direction: 'down',
      text: 'Color of the sky',
      answer: 'BLUE',
      length: 4,
    }),
    createMockClue({
      number: 2,
      direction: 'down',
      text: 'Man\'s best friend',
      answer: 'DOG',
      length: 3,
    }),
  ];

  const sampleCells = createMockCells();

  describe('Rendering', () => {
    it('should render the clue panel', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      expect(screen.getByTestId('clue-panel')).toBeInTheDocument();
      expect(screen.getByText('Clues')).toBeInTheDocument();
    });

    it('should render with custom className', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          className="custom-class"
        />
      );

      const panel = screen.getByTestId('clue-panel');
      expect(panel.className).toContain('custom-class');
    });

    it('should render ClueList component', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      expect(screen.getByTestId('clue-list')).toBeInTheDocument();
    });

    it('should not render search bar by default', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      expect(screen.queryByTestId('search-input')).not.toBeInTheDocument();
    });

    it('should render search bar when showSearch is true', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showSearch={true}
        />
      );

      expect(screen.getByTestId('search-input')).toBeInTheDocument();
    });
  });

  describe('Layout Toggle', () => {
    it('should render layout toggle button by default', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      expect(screen.getByTestId('layout-toggle')).toBeInTheDocument();
    });

    it('should not render layout toggle when showLayoutToggle is false', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showLayoutToggle={false}
        />
      );

      expect(screen.queryByTestId('layout-toggle')).not.toBeInTheDocument();
    });

    it('should toggle layout when button is clicked', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          initialLayout="tabs"
        />
      );

      const toggleButton = screen.getByTestId('layout-toggle');
      
      // Initial state should be tabs
      expect(toggleButton).toHaveAttribute('title', 'Switch to split view');
      
      // Click to switch to split
      fireEvent.click(toggleButton);
      expect(toggleButton).toHaveAttribute('title', 'Switch to tabs view');
      
      // Click again to switch back to tabs
      fireEvent.click(toggleButton);
      expect(toggleButton).toHaveAttribute('title', 'Switch to split view');
    });

    it('should start with split layout when initialLayout is split', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          initialLayout="split"
        />
      );

      const toggleButton = screen.getByTestId('layout-toggle');
      expect(toggleButton).toHaveAttribute('title', 'Switch to tabs view');
    });
  });

  describe('Answer Toggle', () => {
    it('should not render answer toggle by default', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      expect(screen.queryByTestId('answer-toggle')).not.toBeInTheDocument();
    });

    it('should render answer toggle when showAnswerToggle is true', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showAnswerToggle={true}
        />
      );

      expect(screen.getByTestId('answer-toggle')).toBeInTheDocument();
    });

    it('should toggle answers when button is clicked', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showAnswerToggle={true}
        />
      );

      const toggleButton = screen.getByTestId('answer-toggle');
      
      // Initial state should be hidden
      expect(toggleButton).toHaveAttribute('title', 'Show answers');
      
      // Click to show answers
      fireEvent.click(toggleButton);
      expect(toggleButton).toHaveAttribute('title', 'Hide answers');
      
      // Click again to hide answers
      fireEvent.click(toggleButton);
      expect(toggleButton).toHaveAttribute('title', 'Show answers');
    });

    it('should use external showAnswers prop when provided', () => {
      const { rerender } = render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showAnswers={true}
          showAnswerToggle={true}
        />
      );

      const toggleButton = screen.getByTestId('answer-toggle');
      expect(toggleButton).toHaveAttribute('title', 'Hide answers');

      // External prop should override internal state
      rerender(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showAnswers={false}
          showAnswerToggle={true}
        />
      );

      expect(toggleButton).toHaveAttribute('title', 'Show answers');
    });
  });

  describe('Collapse Functionality', () => {
    it('should not render collapse toggle when collapsible is false', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          collapsible={false}
        />
      );

      expect(screen.queryByTestId('collapse-toggle')).not.toBeInTheDocument();
    });

    it('should render collapse toggle when collapsible is true', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          collapsible={true}
        />
      );

      expect(screen.getByTestId('collapse-toggle')).toBeInTheDocument();
    });

    it('should toggle collapse state when button is clicked', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          collapsible={true}
        />
      );

      const toggleButton = screen.getByTestId('collapse-toggle');
      const panel = screen.getByTestId('clue-panel');
      
      // Initial state should be expanded
      expect(toggleButton).toHaveAttribute('title', 'Collapse clues');
      expect(panel.className).not.toContain('collapsed');
      
      // Click to collapse
      fireEvent.click(toggleButton);
      expect(toggleButton).toHaveAttribute('title', 'Expand clues');
      expect(panel.className).toContain('collapsed');
      
      // Click again to expand
      fireEvent.click(toggleButton);
      expect(toggleButton).toHaveAttribute('title', 'Collapse clues');
      expect(panel.className).not.toContain('collapsed');
    });

    it('should start collapsed when initialCollapsed is true', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          collapsible={true}
          initialCollapsed={true}
        />
      );

      const panel = screen.getByTestId('clue-panel');
      expect(panel.className).toContain('collapsed');
      expect(screen.getByTestId('collapsed-message')).toBeInTheDocument();
    });

    it('should show collapsed message when collapsed', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          collapsible={true}
          initialCollapsed={true}
        />
      );

      expect(screen.getByTestId('collapsed-message')).toHaveTextContent('Click to expand clues');
    });

    it('should hide content when collapsed', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          collapsible={true}
          initialCollapsed={true}
        />
      );

      expect(screen.queryByTestId('clue-list')).not.toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    it('should filter clues based on search query', async () => {
      const user = userEvent.setup();
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showSearch={true}
        />
      );

      const searchInput = screen.getByTestId('search-input');
      
      // Type search query
      await user.type(searchInput, 'France');
      
      // Should show filtered count
      await waitFor(() => {
        expect(screen.getByText(/\(1 of 5\)/)).toBeInTheDocument();
      });
    });

    it('should show no results message when no clues match', async () => {
      const user = userEvent.setup();
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showSearch={true}
        />
      );

      const searchInput = screen.getByTestId('search-input');
      
      // Type search query that matches nothing
      await user.type(searchInput, 'xyz123');
      
      // Should show no results message
      await waitFor(() => {
        expect(screen.getByTestId('no-results')).toBeInTheDocument();
        expect(screen.getByText(/No clues found matching "xyz123"/)).toBeInTheDocument();
      });
    });

    it('should clear search when clear button is clicked', async () => {
      const user = userEvent.setup();
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showSearch={true}
        />
      );

      const searchInput = screen.getByTestId('search-input');
      
      // Type search query
      await user.type(searchInput, 'France');
      
      // Clear button should appear
      const clearButton = screen.getByTestId('clear-search');
      expect(clearButton).toBeInTheDocument();
      
      // Click clear button
      fireEvent.click(clearButton);
      
      // Search input should be empty
      expect(searchInput).toHaveValue('');
      
      // Clear button should disappear
      expect(screen.queryByTestId('clear-search')).not.toBeInTheDocument();
    });

    it('should not show clear button when search is empty', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showSearch={true}
        />
      );

      expect(screen.queryByTestId('clear-search')).not.toBeInTheDocument();
    });

    it('should search in clue text, number, and answer', async () => {
      const user = userEvent.setup();
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showSearch={true}
        />
      );

      const searchInput = screen.getByTestId('search-input');
      
      // Search by clue text
      await user.type(searchInput, 'France');
      await waitFor(() => {
        expect(screen.getByText(/\(1 of 5\)/)).toBeInTheDocument();
      });
      
      // Clear and search by answer
      await user.clear(searchInput);
      await user.type(searchInput, 'PARIS');
      await waitFor(() => {
        expect(screen.getByText(/\(1 of 5\)/)).toBeInTheDocument();
      });
      
      // Clear and search by number
      await user.clear(searchInput);
      await user.type(searchInput, '3');
      await waitFor(() => {
        expect(screen.getByText(/\(1 of 5\)/)).toBeInTheDocument();
      });
    });

    it('should be case-insensitive', async () => {
      const user = userEvent.setup();
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showSearch={true}
        />
      );

      const searchInput = screen.getByTestId('search-input');
      
      // Search with lowercase
      await user.type(searchInput, 'france');
      await waitFor(() => {
        expect(screen.getByText(/\(1 of 5\)/)).toBeInTheDocument();
      });
      
      // Clear and search with uppercase
      await user.clear(searchInput);
      await user.type(searchInput, 'FRANCE');
      await waitFor(() => {
        expect(screen.getByText(/\(1 of 5\)/)).toBeInTheDocument();
      });
    });
  });

  describe('Clue Click Handling', () => {
    it('should call onClueClick when a clue is clicked', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      // Find and click a clue
      const clue = screen.getByTestId('clue-1-across');
      fireEvent.click(clue);

      expect(mockOnClueClick).toHaveBeenCalledWith(
        expect.objectContaining({
          number: 1,
          direction: 'across',
        })
      );
    });
  });

  describe('Active Clue Highlighting', () => {
    it('should highlight the active clue', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={{ number: 1, direction: 'across' }}
          onClueClick={mockOnClueClick}
        />
      );

      const clue = screen.getByTestId('clue-1-across');
      expect(clue).toHaveAttribute('data-active', 'true');
    });

    it('should not highlight non-active clues', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={{ number: 1, direction: 'across' }}
          onClueClick={mockOnClueClick}
        />
      );

      const clue = screen.getByTestId('clue-3-across');
      expect(clue).toHaveAttribute('data-active', 'false');
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria-labels for buttons', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          collapsible={true}
          showAnswerToggle={true}
        />
      );

      const layoutToggle = screen.getByTestId('layout-toggle');
      expect(layoutToggle).toHaveAttribute('aria-label');

      const answerToggle = screen.getByTestId('answer-toggle');
      expect(answerToggle).toHaveAttribute('aria-label');

      const collapseToggle = screen.getByTestId('collapse-toggle');
      expect(collapseToggle).toHaveAttribute('aria-label');
    });

    it('should have proper aria-label for search input', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
          showSearch={true}
        />
      );

      const searchInput = screen.getByTestId('search-input');
      expect(searchInput).toHaveAttribute('aria-label', 'Search clues');
    });

    it('should be keyboard navigable', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      const layoutToggle = screen.getByTestId('layout-toggle');
      layoutToggle.focus();
      expect(layoutToggle).toHaveFocus();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty clue lists', () => {
      render(
        <CluePanel
          cluesAcross={[]}
          cluesDown={[]}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      expect(screen.getByTestId('clue-panel')).toBeInTheDocument();
      expect(screen.getByTestId('clue-list')).toBeInTheDocument();
    });

    it('should handle null activeClue', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={sampleCells}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      expect(screen.getByTestId('clue-panel')).toBeInTheDocument();
    });

    it('should handle empty cells array', () => {
      render(
        <CluePanel
          cluesAcross={sampleCluesAcross}
          cluesDown={sampleCluesDown}
          cells={[]}
          activeClue={null}
          onClueClick={mockOnClueClick}
        />
      );

      expect(screen.getByTestId('clue-panel')).toBeInTheDocument();
    });
  });
});
