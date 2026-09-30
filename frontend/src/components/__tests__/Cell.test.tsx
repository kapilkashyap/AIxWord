/**
 * Unit tests for Cell component.
 * 
 * Tests cover:
 * - Rendering different cell states (blocked, empty, filled)
 * - User interactions (click, input)
 * - Visual states (selected, active word, completed, error)
 * - Keyboard handling
 * - Focus management
 * - Read-only mode
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Cell } from '../Cell';
import type { CellState } from '../../types/puzzle';

describe('Cell Component', () => {
  // Mock callbacks
  const mockOnClick = vi.fn();
  const mockOnInput = vi.fn();

  beforeEach(() => {
    mockOnClick.mockClear();
    mockOnInput.mockClear();
  });

  // Helper function to create a cell state
  const createCellState = (overrides: Partial<CellState> = {}): CellState => ({
    row: 0,
    col: 0,
    value: null,
    is_blocked: false,
    number: null,
    is_selected: false,
    is_active_word: false,
    is_completed: false,
    has_error: false,
    ...overrides,
  });

  describe('Rendering', () => {
    it('should render an empty cell', () => {
      const cell = createCellState();
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const cellElement = screen.getByTestId('cell-0-0');
      expect(cellElement).toBeInTheDocument();
      
      const input = screen.getByTestId('cell-input-0-0');
      expect(input).toHaveValue('');
    });

    it('should render a cell with a value', () => {
      const cell = createCellState({ value: 'A' });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      expect(input).toHaveValue('A');
    });

    it('should render a cell with a number', () => {
      const cell = createCellState({ number: 1 });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const number = screen.getByTestId('cell-number-1');
      expect(number).toHaveTextContent('1');
    });

    it('should render a blocked cell', () => {
      const cell = createCellState({ is_blocked: true });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const cellElement = screen.getByTestId('cell-0-0');
      expect(cellElement).toHaveAttribute('data-blocked', 'true');
      
      // Blocked cells should not have an input
      const input = screen.queryByTestId('cell-input-0-0');
      expect(input).not.toBeInTheDocument();
    });

    it('should apply custom cell size', () => {
      const cell = createCellState();
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
          cellSize={60}
        />
      );

      const cellElement = screen.getByTestId('cell-0-0');
      expect(cellElement).toHaveStyle({ width: '60px', height: '60px' });
    });
  });

  describe('Visual States', () => {
    it('should show selected state', () => {
      const cell = createCellState({ is_selected: true });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const cellElement = screen.getByTestId('cell-0-0');
      expect(cellElement).toHaveAttribute('data-selected', 'true');
    });

    it('should show active word state', () => {
      const cell = createCellState({ is_active_word: true });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const cellElement = screen.getByTestId('cell-0-0');
      expect(cellElement).toHaveAttribute('data-active-word', 'true');
    });

    it('should show completed state', () => {
      const cell = createCellState({ is_completed: true, value: 'A' });
      const { container } = render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      // Check if completed class is applied
      const cellElement = container.querySelector('[data-testid="cell-0-0"]');
      expect(cellElement?.className).toContain('completed');
    });

    it('should show error state', () => {
      const cell = createCellState({ has_error: true, value: 'X' });
      const { container } = render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      // Check if error class is applied
      const cellElement = container.querySelector('[data-testid="cell-0-0"]');
      expect(cellElement?.className).toContain('error');
    });
  });

  describe('User Interactions', () => {
    it('should call onClick when cell is clicked', () => {
      const cell = createCellState({ row: 2, col: 3 });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const cellElement = screen.getByTestId('cell-2-3');
      fireEvent.click(cellElement);

      expect(mockOnClick).toHaveBeenCalledWith(2, 3);
    });

    it('should not call onClick for blocked cells', () => {
      const cell = createCellState({ is_blocked: true });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const cellElement = screen.getByTestId('cell-0-0');
      fireEvent.click(cellElement);

      expect(mockOnClick).not.toHaveBeenCalled();
    });

    it('should call onInput when a letter is entered', async () => {
      const user = userEvent.setup();
      const cell = createCellState({ row: 1, col: 2 });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-1-2');
      await user.type(input, 'A');

      expect(mockOnInput).toHaveBeenCalledWith(1, 2, 'A');
    });

    it('should convert lowercase letters to uppercase', async () => {
      const user = userEvent.setup();
      const cell = createCellState();
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      await user.type(input, 'a');

      expect(mockOnInput).toHaveBeenCalledWith(0, 0, 'A');
    });

    it('should only allow single letters A-Z', async () => {
      const user = userEvent.setup();
      const cell = createCellState();
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      
      // Try to enter a number
      await user.type(input, '1');
      expect(mockOnInput).not.toHaveBeenCalled();

      // Try to enter a special character
      await user.type(input, '@');
      expect(mockOnInput).not.toHaveBeenCalled();
    });

    it('should allow clearing the cell', async () => {
      const user = userEvent.setup();
      const cell = createCellState({ value: 'A' });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      await user.clear(input);

      expect(mockOnInput).toHaveBeenCalledWith(0, 0, '');
    });
  });

  describe('Keyboard Handling', () => {
    it('should prevent default for navigation keys', () => {
      const cell = createCellState();
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      
      const arrowEvent = new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true });
      const preventDefaultSpy = vi.spyOn(arrowEvent, 'preventDefault');
      
      input.dispatchEvent(arrowEvent);
      expect(preventDefaultSpy).toHaveBeenCalled();
    });
  });

  describe('Focus Management', () => {
    it('should focus the input when shouldFocus is true', () => {
      const cell = createCellState();
      const { rerender } = render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      expect(input).not.toHaveFocus();

      rerender(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={true}
        />
      );

      expect(input).toHaveFocus();
    });
  });

  describe('Read-Only Mode', () => {
    it('should not call onClick in read-only mode', () => {
      const cell = createCellState();
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
          readOnly={true}
        />
      );

      const cellElement = screen.getByTestId('cell-0-0');
      fireEvent.click(cellElement);

      expect(mockOnClick).not.toHaveBeenCalled();
    });

    it('should not call onInput in read-only mode', async () => {
      const user = userEvent.setup();
      const cell = createCellState();
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
          readOnly={true}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      await user.type(input, 'A');

      expect(mockOnInput).not.toHaveBeenCalled();
    });

    it('should disable the input in read-only mode', () => {
      const cell = createCellState();
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
          readOnly={true}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      expect(input).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria-label', () => {
      const cell = createCellState({ row: 2, col: 3, number: 5 });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-2-3');
      expect(input).toHaveAttribute('aria-label', 'Cell 2, 3, clue 5');
    });

    it('should have aria-label without clue number', () => {
      const cell = createCellState({ row: 1, col: 1 });
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-1-1');
      expect(input).toHaveAttribute('aria-label', 'Cell 1, 1');
    });

    it('should have tabIndex -1 to prevent tab navigation', () => {
      const cell = createCellState();
      render(
        <Cell
          cell={cell}
          onClick={mockOnClick}
          onInput={mockOnInput}
          shouldFocus={false}
        />
      );

      const input = screen.getByTestId('cell-input-0-0');
      expect(input).toHaveAttribute('tabIndex', '-1');
    });
  });
});
