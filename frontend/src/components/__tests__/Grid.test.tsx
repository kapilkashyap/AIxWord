/**
 * Unit tests for Grid component.
 * 
 * Tests cover:
 * - Rendering the grid with cells
 * - Cell selection and navigation
 * - Keyboard navigation (arrow keys, tab, backspace)
 * - Direction toggling
 * - Active clue management
 * - Cell value updates
 * - Read-only mode
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Grid } from '../Grid';
import type { Cell, Clue, Direction } from '../../types/puzzle';

describe('Grid Component', () => {
  // Mock callbacks
  const mockOnCellSelect = vi.fn();
  const mockOnCellChange = vi.fn();
  const mockOnDirectionChange = vi.fn();
  const mockOnActiveClueChange = vi.fn();

  beforeEach(() => {
    mockOnCellSelect.mockClear();
    mockOnCellChange.mockClear();
    mockOnDirectionChange.mockClear();
    mockOnActiveClueChange.mockClear();
  });

  // Helper function to create a simple 3x3 grid
  const createSimpleGrid = (): Cell[] => {
    const cells: Cell[] = [];
    for (let row = 0; row < 3; row++) {
      for (let col = 0; col < 3; col++) {
        cells.push({
          row,
          col,
          value: null,
          is_blocked: false,
          number: null,
        });
      }
    }
    return cells;
  };

  // Helper function to create sample clues
  const createSampleClues = (): { across: Clue[]; down: Clue[] } => {
    return {
      across: [
        {
          number: 1,
          direction: 'across' as Direction,
          text: 'First across clue',
          answer: 'CAT',
          start_row: 0,
          start_col: 0,
          length: 3,
        },
      ],
      down: [
        {
          number: 1,
          direction: 'down' as Direction,
          text: 'First down clue',
          answer: 'CAN',
          start_row: 0,
          start_col: 0,
          length: 3,
        },
      ],
    };
  };

  describe('Rendering', () => {
    it('should render the grid container', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      const container = screen.getByTestId('grid-container');
      expect(container).toBeInTheDocument();
    });

    it('should render all cells', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      // Should render 9 cells (3x3)
      for (let row = 0; row < 3; row++) {
        for (let col = 0; col < 3; col++) {
          const cell = screen.getByTestId(`cell-${row}-${col}`);
          expect(cell).toBeInTheDocument();
        }
      }
    });

    it('should render direction indicator', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      const indicator = screen.getByTestId('direction-indicator');
      expect(indicator).toBeInTheDocument();
      expect(indicator).toHaveTextContent('→ Across');
    });

    it('should not render direction indicator in read-only mode', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
          readOnly={true}
        />
      );

      const indicator = screen.queryByTestId('direction-indicator');
      expect(indicator).not.toBeInTheDocument();
    });

    it('should apply custom cell size', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
          cellSize={60}
        />
      );

      const grid = screen.getByTestId('grid');
      expect(grid).toHaveStyle({ width: '180px', height: '180px' });
    });

    it('should apply custom className', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
          className="custom-class"
        />
      );

      const container = screen.getByTestId('grid-container');
      expect(container.className).toContain('custom-class');
    });
  });

  describe('Cell Selection', () => {
    it('should call onCellSelect when a cell is clicked', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      const cell = screen.getByTestId('cell-1-1');
      fireEvent.click(cell);

      expect(mockOnCellSelect).toHaveBeenCalledWith(1, 1);
    });

    it('should toggle direction when clicking the same cell', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 1, col: 1 }}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      const cell = screen.getByTestId('cell-1-1');
      fireEvent.click(cell);

      expect(mockOnDirectionChange).toHaveBeenCalledWith('down');
    });

    it('should highlight selected cell', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 1, col: 1 }}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      const cell = screen.getByTestId('cell-1-1');
      expect(cell).toHaveAttribute('data-selected', 'true');
    });
  });

  describe('Cell Input', () => {
    it('should update cell value when input is entered', async () => {
      const user = userEvent.setup();
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 0, col: 0 }}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      await user.type(input, 'A');

      expect(mockOnCellChange).toHaveBeenCalled();
      const updatedCells = mockOnCellChange.mock.calls[0][0];
      const updatedCell = updatedCells.find((c: Cell) => c.row === 0 && c.col === 0);
      expect(updatedCell?.value).toBe('A');
    });

    it('should move to next cell after input', async () => {
      const user = userEvent.setup();
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 0, col: 0 }}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      await user.type(input, 'A');

      // Should move to next cell in the across direction
      expect(mockOnCellSelect).toHaveBeenCalledWith(0, 1);
    });
  });

  describe('Keyboard Navigation', () => {
    it('should navigate with arrow keys', async () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 1, col: 1 }}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      // Arrow Right
      fireEvent.keyDown(window, { key: 'ArrowRight' });
      await waitFor(() => {
        expect(mockOnCellSelect).toHaveBeenCalledWith(1, 2);
      });

      mockOnCellSelect.mockClear();

      // Arrow Down
      fireEvent.keyDown(window, { key: 'ArrowDown' });
      await waitFor(() => {
        expect(mockOnCellSelect).toHaveBeenCalledWith(2, 1);
      });
    });

    it('should change direction based on arrow key', async () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 1, col: 1 }}
          currentDirection="down"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      // Arrow Right should change direction to across
      fireEvent.keyDown(window, { key: 'ArrowRight' });
      await waitFor(() => {
        expect(mockOnDirectionChange).toHaveBeenCalledWith('across');
      });
    });

    it('should toggle direction with space key', async () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 1, col: 1 }}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      fireEvent.keyDown(window, { key: ' ' });
      await waitFor(() => {
        expect(mockOnDirectionChange).toHaveBeenCalledWith('down');
      });
    });

    it('should clear cell with delete key', async () => {
      const cells = createSimpleGrid();
      cells[0].value = 'A'; // Set initial value
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 0, col: 0 }}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      fireEvent.keyDown(window, { key: 'Delete' });
      await waitFor(() => {
        expect(mockOnCellChange).toHaveBeenCalled();
        const updatedCells = mockOnCellChange.mock.calls[0][0];
        const updatedCell = updatedCells.find((c: Cell) => c.row === 0 && c.col === 0);
        expect(updatedCell?.value).toBeNull();
      });
    });

    it('should handle backspace to clear and move back', async () => {
      const cells = createSimpleGrid();
      cells[1].value = 'A'; // Set initial value at position 1
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 0, col: 1 }}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      fireEvent.keyDown(window, { key: 'Backspace' });
      await waitFor(() => {
        expect(mockOnCellChange).toHaveBeenCalled();
      });
    });
  });

  describe('Direction Management', () => {
    it('should display current direction', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      const { rerender } = render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      let indicator = screen.getByTestId('direction-indicator');
      expect(indicator).toHaveTextContent('→ Across');

      rerender(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="down"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      indicator = screen.getByTestId('direction-indicator');
      expect(indicator).toHaveTextContent('↓ Down');
    });
  });

  describe('Read-Only Mode', () => {
    it('should not allow cell selection in read-only mode', () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={null}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
          readOnly={true}
        />
      );

      const cell = screen.getByTestId('cell-1-1');
      fireEvent.click(cell);

      expect(mockOnCellSelect).not.toHaveBeenCalled();
    });

    it('should not respond to keyboard navigation in read-only mode', async () => {
      const cells = createSimpleGrid();
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 1, col: 1 }}
          currentDirection="across"
          activeClue={null}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
          readOnly={true}
        />
      );

      fireEvent.keyDown(window, { key: 'ArrowRight' });
      
      // Wait a bit to ensure no async calls are made
      await new Promise(resolve => setTimeout(resolve, 100));
      
      expect(mockOnCellSelect).not.toHaveBeenCalled();
    });
  });

  describe('Active Word Highlighting', () => {
    it('should highlight cells in active word', () => {
      const cells = createSimpleGrid();
      cells[0].number = 1;
      const clues = createSampleClues();

      render(
        <Grid
          cells={cells}
          gridSize={3}
          cluesAcross={clues.across}
          cluesDown={clues.down}
          selectedCell={{ row: 0, col: 0 }}
          currentDirection="across"
          activeClue={{ number: 1, direction: 'across' }}
          onCellSelect={mockOnCellSelect}
          onCellChange={mockOnCellChange}
          onDirectionChange={mockOnDirectionChange}
          onActiveClueChange={mockOnActiveClueChange}
        />
      );

      // Cells 0-0, 0-1, 0-2 should be highlighted as part of the active word
      const cell1 = screen.getByTestId('cell-0-0');
      const cell2 = screen.getByTestId('cell-0-1');
      const cell3 = screen.getByTestId('cell-0-2');

      expect(cell1).toHaveAttribute('data-active-word', 'true');
      expect(cell2).toHaveAttribute('data-active-word', 'true');
      expect(cell3).toHaveAttribute('data-active-word', 'true');
    });
  });
});
