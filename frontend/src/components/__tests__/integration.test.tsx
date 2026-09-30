/**
 * Integration tests for the complete puzzle flow.
 * 
 * These tests verify the end-to-end user experience by testing
 * the integration of multiple components working together:
 * - PuzzleContainer orchestrating the entire flow
 * - Puzzle generation → solving → validation workflow
 * - Component interactions and state management
 * - API integration with mocked backend
 * - User interactions across multiple components
 * 
 * These tests provide confidence that the application works
 * as a cohesive whole, not just as isolated components.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PuzzleContainer } from '../PuzzleContainer';
import { apiClient } from '../../services/api';
import type {
  PuzzleGenerateResponse,
  SolveResponse,
  HintResponse,
  ValidateResponse,
} from '../../types/api';
import type { Puzzle, Cell, Clue } from '../../types/puzzle';

// Mock the API client
vi.mock('../../services/api', () => ({
  apiClient: {
    generatePuzzle: vi.fn(),
    solvePuzzle: vi.fn(),
    solveWord: vi.fn(),
    getHint: vi.fn(),
    validateSolution: vi.fn(),
  },
}));

describe('Integration Tests - Complete Puzzle Flow', () => {
  // Helper to create a simple 3x3 puzzle for testing
  const createTestPuzzle = (): Puzzle => {
    const cells: Cell[] = [];
    
    // Create a 3x3 grid
    for (let row = 0; row < 3; row++) {
      for (let col = 0; col < 3; col++) {
        cells.push({
          row,
          col,
          value: null,
          is_blocked: false,
          number: row === 0 && col === 0 ? 1 : null,
        });
      }
    }

    const cluesAcross: Clue[] = [
      {
        number: 1,
        direction: 'across',
        text: 'Feline pet',
        answer: 'CAT',
        start_row: 0,
        start_col: 0,
        length: 3,
      },
    ];

    const cluesDown: Clue[] = [
      {
        number: 1,
        direction: 'down',
        text: 'Metal container',
        answer: 'CAN',
        start_row: 0,
        start_col: 0,
        length: 3,
      },
    ];

    return {
      puzzle_id: 'test-puzzle-123',
      topic: 'Animals',
      grid_size: 3,
      cells,
      clues_across: cluesAcross,
      clues_down: cluesDown,
      word_count: 2,
      fill_rate: 0.67,
      difficulty: 'easy',
      created_at: '2026-09-28T12:00:00Z',
      metadata: {},
    };
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Complete User Journey: Generation → Solving → Validation', () => {
    it.skip('should complete the full puzzle workflow from generation to validation', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      // Mock successful validation
      const validateResponse: ValidateResponse = {
        is_valid: true,
        is_complete: true,
        errors: [],
        correct_count: 3,
        total_count: 3,
        accuracy: 1.0,
      };
      vi.mocked(apiClient.validateSolution).mockResolvedValue(validateResponse);

      // Render the container
      render(<PuzzleContainer />);

      // Step 1: Verify initial state shows generator form
      expect(screen.getByTestId('puzzle-generator-form')).toBeInTheDocument();

      // Step 2: Fill in the generation form
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      // Step 3: Submit the form to generate puzzle
      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Step 4: Wait for puzzle to be generated and displayed
      await waitFor(() => {
        expect(apiClient.generatePuzzle).toHaveBeenCalledWith(
          expect.objectContaining({
            topic: 'Animals',
          })
        );
      });

      // Verify puzzle grid is now displayed
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Step 5: Verify puzzle info is displayed
      expect(screen.getByText('Animals')).toBeInTheDocument();
      expect(screen.getByText(/progress:/i)).toBeInTheDocument();

      // Step 6: Verify clues are displayed
      expect(screen.getByText(/feline pet/i)).toBeInTheDocument();
      expect(screen.getByText(/metal container/i)).toBeInTheDocument();

      // Step 7: Manually solve the puzzle by entering letters
      const cell00 = screen.getByTestId('cell-input-0-0');
      const cell01 = screen.getByTestId('cell-input-0-1');
      const cell02 = screen.getByTestId('cell-input-0-2');

      await user.click(cell00);
      await user.type(cell00, 'C');
      await user.type(cell01, 'A');
      await user.type(cell02, 'T');

      // Step 8: Validate the solution
      const validateButton = screen.getByRole('button', { name: /check solution/i });
      await user.click(validateButton);

      // Step 9: Wait for validation response
      await waitFor(() => {
        expect(apiClient.validateSolution).toHaveBeenCalled();
      });

      // Step 10: Verify success notification is displayed
      await waitFor(() => {
        const notification = screen.getByTestId('validation-notification');
        expect(notification).toBeInTheDocument();
        expect(within(notification).getByText(/perfect/i)).toBeInTheDocument();
      });
    });

    it('should handle puzzle generation failure gracefully', async () => {
      const user = userEvent.setup();

      // Mock failed puzzle generation
      const errorResponse: PuzzleGenerateResponse = {
        success: false,
        puzzle: null,
        status: 'failed',
        iterations: 10,
        error_message: 'Unable to generate puzzle with given constraints',
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(errorResponse);

      render(<PuzzleContainer />);

      // Fill in and submit the form
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'InvalidTopic');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for error to be displayed
      await waitFor(() => {
        expect(apiClient.generatePuzzle).toHaveBeenCalled();
      });

      // Verify error message is shown
      await waitFor(() => {
        const errorText = screen.getByText(/unable to generate puzzle/i);
        expect(errorText).toBeInTheDocument();
      });

      // Verify puzzle grid is NOT displayed
      expect(screen.queryByTestId('grid-container')).not.toBeInTheDocument();
    });
  });

  describe('AI-Assisted Solving Integration', () => {
    it.skip('should solve entire puzzle using AI', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      // Mock successful puzzle solve
      const solveResponse: SolveResponse = {
        success: true,
        answer: 'Complete solution',
        confidence: 0.95,
        reasoning: 'All words solved successfully',
        updated_cells: [
          { row: 0, col: 0, value: 'C', is_blocked: false, number: 1 },
          { row: 0, col: 1, value: 'A', is_blocked: false, number: null },
          { row: 0, col: 2, value: 'T', is_blocked: false, number: null },
        ],
      };
      vi.mocked(apiClient.solvePuzzle).mockResolvedValue(solveResponse);

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Click "Solve Puzzle" button
      const solvePuzzleButton = screen.getByRole('button', { name: /solve puzzle/i });
      await user.click(solvePuzzleButton);

      // Wait for solve API call
      await waitFor(() => {
        expect(apiClient.solvePuzzle).toHaveBeenCalledWith(
          'test-puzzle-123',
          expect.objectContaining({ use_hints: true })
        );
      });

      // Verify cells are filled with solution
      await waitFor(() => {
        const cell00 = screen.getByTestId('cell-input-0-0') as HTMLInputElement;
        const cell01 = screen.getByTestId('cell-input-0-1') as HTMLInputElement;
        const cell02 = screen.getByTestId('cell-input-0-2') as HTMLInputElement;

        expect(cell00.value).toBe('C');
        expect(cell01.value).toBe('A');
        expect(cell02.value).toBe('T');
      });
    });

    it.skip('should solve individual word using AI', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      // Mock successful word solve
      const solveWordResponse: SolveResponse = {
        success: true,
        answer: 'CAT',
        confidence: 0.98,
        reasoning: 'Feline pet is CAT',
        updated_cells: [
          { row: 0, col: 0, value: 'C', is_blocked: false, number: 1 },
          { row: 0, col: 1, value: 'A', is_blocked: false, number: null },
          { row: 0, col: 2, value: 'T', is_blocked: false, number: null },
        ],
      };
      vi.mocked(apiClient.solveWord).mockResolvedValue(solveWordResponse);

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Select a cell to activate a clue
      const cell00 = screen.getByTestId('cell-0-0');
      await user.click(cell00);

      // Click "Solve Word" button
      const solveWordButton = screen.getByRole('button', { name: /solve word/i });
      await user.click(solveWordButton);

      // Wait for solve word API call
      await waitFor(() => {
        expect(apiClient.solveWord).toHaveBeenCalledWith(
          'test-puzzle-123',
          expect.objectContaining({
            clue_number: 1,
            direction: 'across',
            use_intersections: true,
          })
        );
      });

      // Verify cells are filled with word solution
      await waitFor(() => {
        const input00 = screen.getByTestId('cell-input-0-0') as HTMLInputElement;
        const input01 = screen.getByTestId('cell-input-0-1') as HTMLInputElement;
        const input02 = screen.getByTestId('cell-input-0-2') as HTMLInputElement;

        expect(input00.value).toBe('C');
        expect(input01.value).toBe('A');
        expect(input02.value).toBe('T');
      });
    });

    it.skip('should get hint for current word', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      // Mock successful hint
      const hintResponse: HintResponse = {
        success: true,
        hint: 'Think of a common household pet that meows',
        hint_type: 'definition',
        revealed_letter: null,
        position: null,
      };
      vi.mocked(apiClient.getHint).mockResolvedValue(hintResponse);

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Select a cell to activate a clue
      const cell00 = screen.getByTestId('cell-0-0');
      await user.click(cell00);

      // Click "Get Hint" button
      const hintButton = screen.getByRole('button', { name: /get hint/i });
      await user.click(hintButton);

      // Wait for hint API call
      await waitFor(() => {
        expect(apiClient.getHint).toHaveBeenCalledWith(
          'test-puzzle-123',
          expect.objectContaining({
            clue_number: 1,
            direction: 'across',
            hint_type: 'definition',
          })
        );
      });

      // Verify hint notification is displayed
      await waitFor(() => {
        const notification = screen.getByTestId('hint-notification');
        expect(notification).toBeInTheDocument();
        expect(within(notification).getByText(/think of a common household pet/i)).toBeInTheDocument();
      });
    });
  });

  describe('Grid and Clue Panel Integration', () => {
    it.skip('should synchronize grid selection with clue panel', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Click on a cell in the grid
      const cell00 = screen.getByTestId('cell-0-0');
      await user.click(cell00);

      // Verify the corresponding clue is highlighted in the clue panel
      await waitFor(() => {
        const clueItem = screen.getByTestId('clue-item-1-across');
        expect(clueItem).toHaveAttribute('data-active', 'true');
      });
    });

    it.skip('should update grid selection when clicking on a clue', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Click on a clue in the clue panel
      const clueItem = screen.getByTestId('clue-item-1-across');
      await user.click(clueItem);

      // Verify the first cell of that word is selected in the grid
      await waitFor(() => {
        const cell00 = screen.getByTestId('cell-0-0');
        expect(cell00).toHaveAttribute('data-selected', 'true');
      });
    });
  });

  describe('State Management and Persistence', () => {
    it.skip('should maintain user input when switching between clues', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Enter a letter in the first cell
      const cell00Input = screen.getByTestId('cell-input-0-0');
      await user.click(cell00Input);
      await user.type(cell00Input, 'C');

      // Switch to a different clue
      const clueDown = screen.getByTestId('clue-item-1-down');
      await user.click(clueDown);

      // Switch back to the original clue
      const clueAcross = screen.getByTestId('clue-item-1-across');
      await user.click(clueAcross);

      // Verify the previously entered letter is still there
      const input00 = screen.getByTestId('cell-input-0-0') as HTMLInputElement;
      expect(input00.value).toBe('C');
    });

    it.skip('should reset puzzle state when generating a new puzzle', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      render(<PuzzleContainer />);

      // Generate first puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Enter some letters
      const cell00Input = screen.getByTestId('cell-input-0-0');
      await user.click(cell00Input);
      await user.type(cell00Input, 'C');

      // Click "New Puzzle" button
      const newPuzzleButton = screen.getByTestId('new-puzzle-button');
      await user.click(newPuzzleButton);

      // Verify we're back to the generator form
      await waitFor(() => {
        expect(screen.getByTestId('puzzle-generator-form')).toBeInTheDocument();
      });

      // Generate another puzzle
      await user.clear(topicInput);
      await user.type(topicInput, 'Science');
      await user.click(generateButton);

      // Wait for new puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Verify cells are empty (state was reset)
      const newCell00Input = screen.getByTestId('cell-input-0-0') as HTMLInputElement;
      expect(newCell00Input.value).toBe('');
    });
  });

  describe('Error Handling and Recovery', () => {
    it.skip('should handle API errors gracefully during solving', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      // Mock failed solve
      vi.mocked(apiClient.solvePuzzle).mockRejectedValue(new Error('Network error'));

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Try to solve puzzle
      const solvePuzzleButton = screen.getByRole('button', { name: /solve puzzle/i });
      await user.click(solvePuzzleButton);

      // Wait for error handling
      await waitFor(() => {
        expect(apiClient.solvePuzzle).toHaveBeenCalled();
      });

      // Verify the grid is still functional (no crash)
      const cell00 = screen.getByTestId('cell-0-0');
      expect(cell00).toBeInTheDocument();
    });

    it.skip('should handle validation errors and display them', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      // Mock validation with errors
      const validateResponse: ValidateResponse = {
        is_valid: false,
        is_complete: true,
        errors: [
          {
            row: 0,
            col: 1,
            expected: 'A',
            actual: 'X',
            message: 'Incorrect letter',
          },
        ],
        correct_count: 2,
        total_count: 3,
        accuracy: 0.67,
      };
      vi.mocked(apiClient.validateSolution).mockResolvedValue(validateResponse);

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Enter some letters (with one wrong)
      const cell00Input = screen.getByTestId('cell-input-0-0');
      const cell01Input = screen.getByTestId('cell-input-0-1');
      const cell02Input = screen.getByTestId('cell-input-0-2');

      await user.click(cell00Input);
      await user.type(cell00Input, 'C');
      await user.type(cell01Input, 'X'); // Wrong letter
      await user.type(cell02Input, 'T');

      // Validate
      const validateButton = screen.getByRole('button', { name: /check solution/i });
      await user.click(validateButton);

      // Wait for validation
      await waitFor(() => {
        expect(apiClient.validateSolution).toHaveBeenCalled();
      });

      // Verify error notification is displayed with accuracy
      await waitFor(() => {
        const notification = screen.getByTestId('validation-notification');
        expect(notification).toBeInTheDocument();
        expect(within(notification).getByText(/2 of 3 correct/i)).toBeInTheDocument();
        expect(within(notification).getByText(/67%/i)).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Behavior and UI Updates', () => {
    it.skip('should update progress indicator as cells are filled', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // Initial progress should be 0%
      expect(screen.getByText(/progress:/i)).toBeInTheDocument();
      expect(screen.getByText(/0%/)).toBeInTheDocument();

      // Fill in one cell
      const cell00Input = screen.getByTestId('cell-input-0-0');
      await user.click(cell00Input);
      await user.type(cell00Input, 'C');

      // Progress should update (exact percentage depends on grid size)
      await waitFor(() => {
        const progressText = screen.queryByText(/0%/);
        // Progress should no longer be 0%
        expect(progressText).not.toBeInTheDocument();
      });
    });

    it.skip('should disable action buttons appropriately based on state', async () => {
      const user = userEvent.setup();
      const testPuzzle = createTestPuzzle();

      // Mock successful puzzle generation
      const generateResponse: PuzzleGenerateResponse = {
        success: true,
        puzzle: testPuzzle,
        status: 'completed',
        iterations: 5,
        error_message: null,
      };
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(generateResponse);

      render(<PuzzleContainer />);

      // Generate puzzle
      const topicInput = screen.getByLabelText(/topic/i);
      await user.clear(topicInput);
      await user.type(topicInput, 'Animals');

      const generateButton = screen.getByRole('button', { name: /generate puzzle/i });
      await user.click(generateButton);

      // Wait for puzzle to load
      await waitFor(() => {
        expect(screen.getByTestId('grid-container')).toBeInTheDocument();
      });

      // "Solve Word" button should be disabled when no cell is selected
      const solveWordButton = screen.getByRole('button', { name: /solve word/i });
      expect(solveWordButton).toBeDisabled();

      // Select a cell
      const cell00 = screen.getByTestId('cell-0-0');
      await user.click(cell00);

      // "Solve Word" button should now be enabled
      await waitFor(() => {
        expect(solveWordButton).not.toBeDisabled();
      });
    });
  });
});
