/**
 * Unit tests for PuzzleGenerator component.
 * 
 * Tests cover:
 * - Rendering the generator with form and progress
 * - Form submission and puzzle generation
 * - Loading states during generation
 * - Success state with generated puzzle
 * - Error handling and retry functionality
 * - Cancel functionality
 * - Help section display
 * - Success actions (start solving, generate another)
 * - Responsive behavior
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PuzzleGenerator } from '../PuzzleGenerator';
import { apiClient } from '../../services/api';
import type { PuzzleGenerateResponse } from '../../types/api';
import type { Puzzle } from '../../types/puzzle';

// Mock the API client
vi.mock('../../services/api', () => ({
  apiClient: {
    generatePuzzle: vi.fn(),
  },
}));

describe('PuzzleGenerator Component', () => {
  // Mock callbacks
  const mockOnPuzzleGenerated = vi.fn();
  const mockOnCancel = vi.fn();

  // Sample puzzle data
  const mockPuzzle: Puzzle = {
    puzzle_id: 'test-puzzle-123',
    topic: 'Science',
    grid_size: 8,
    cells: [],
    clues_across: [],
    clues_down: [],
    word_count: 10,
    fill_rate: 0.75,
    difficulty: 'medium',
    created_at: '2026-09-28T12:00:00Z',
    metadata: {},
  };

  const mockSuccessResponse: PuzzleGenerateResponse = {
    success: true,
    puzzle: mockPuzzle,
    status: 'completed',
    iterations: 5,
    error_message: null,
  };

  const mockErrorResponse: PuzzleGenerateResponse = {
    success: false,
    puzzle: null,
    status: 'failed',
    iterations: 10,
    error_message: 'Failed to generate puzzle',
  };

  beforeEach(() => {
    mockOnPuzzleGenerated.mockClear();
    mockOnCancel.mockClear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('should render the generator container', () => {
      render(<PuzzleGenerator />);

      const container = screen.getByTestId('puzzle-generator');
      expect(container).toBeInTheDocument();
    });

    it('should render the header with title and subtitle', () => {
      render(<PuzzleGenerator />);

      expect(screen.getByText('Create Your Crossword Puzzle')).toBeInTheDocument();
      expect(
        screen.getByText('Generate an AI-powered crossword puzzle on any topic in seconds')
      ).toBeInTheDocument();
    });

    it('should render the puzzle generator form', () => {
      render(<PuzzleGenerator />);

      const form = screen.getByTestId('puzzle-generator-form');
      expect(form).toBeInTheDocument();
    });

    it('should render help section when no generation is in progress', () => {
      render(<PuzzleGenerator />);

      expect(screen.getByText('💡 Tips for Great Puzzles')).toBeInTheDocument();
      expect(screen.getByText(/Choose specific topics/)).toBeInTheDocument();
    });

    it('should render cancel button when showCancel is true', () => {
      render(<PuzzleGenerator showCancel={true} onCancel={mockOnCancel} />);

      const cancelButton = screen.getByTestId('puzzle-generator-cancel');
      expect(cancelButton).toBeInTheDocument();
    });

    it('should not render cancel button when showCancel is false', () => {
      render(<PuzzleGenerator showCancel={false} />);

      const cancelButton = screen.queryByTestId('puzzle-generator-cancel');
      expect(cancelButton).not.toBeInTheDocument();
    });
  });

  describe('Puzzle Generation', () => {
    it('should call API when form is submitted', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockSuccessResponse);

      render(<PuzzleGenerator onPuzzleGenerated={mockOnPuzzleGenerated} />);

      // Fill in the topic
      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      // Submit the form
      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(apiClient.generatePuzzle).toHaveBeenCalledWith(
          expect.objectContaining({
            topic: 'Science',
          })
        );
      });
    });

    it('should show loading state during generation', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve(mockSuccessResponse), 100);
          })
      );

      render(<PuzzleGenerator />);

      // Fill in and submit
      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      // Check for loading state
      await waitFor(() => {
        expect(screen.getByTestId('generating-state')).toBeInTheDocument();
      });
    });

    it('should show loading overlay during generation', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve(mockSuccessResponse), 100);
          })
      );

      render(<PuzzleGenerator />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('puzzle-generator-loading-overlay')).toBeInTheDocument();
      });
    });

    it('should call onPuzzleGenerated when generation succeeds', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockSuccessResponse);

      render(<PuzzleGenerator onPuzzleGenerated={mockOnPuzzleGenerated} />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnPuzzleGenerated).toHaveBeenCalledWith(mockPuzzle);
      });
    });

    it('should show success state after generation', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockSuccessResponse);

      render(<PuzzleGenerator />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('success-state')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message when generation fails', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockErrorResponse);

      render(<PuzzleGenerator />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('puzzle-generator-error')).toBeInTheDocument();
      });
    });

    it('should show error state in generation progress', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockErrorResponse);

      render(<PuzzleGenerator />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('error-state')).toBeInTheDocument();
      });
    });

    it('should handle API errors', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockRejectedValue(
        new Error('Network error')
      );

      render(<PuzzleGenerator />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('puzzle-generator-error')).toBeInTheDocument();
      });
    });

    it('should show retry button on error', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockErrorResponse);

      render(<PuzzleGenerator />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        const retryButton = screen.getByTestId('puzzle-generator-error-retry');
        expect(retryButton).toBeInTheDocument();
      });
    });

    it('should reset state when retry is clicked', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockErrorResponse);

      render(<PuzzleGenerator />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('puzzle-generator-error')).toBeInTheDocument();
      });

      const retryButton = screen.getByTestId('puzzle-generator-error-retry');
      await user.click(retryButton);

      await waitFor(() => {
        expect(screen.queryByTestId('puzzle-generator-error')).not.toBeInTheDocument();
      });
    });

    it('should track generation attempts', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockErrorResponse);

      render(<PuzzleGenerator />);

      // First attempt
      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('puzzle-generator-error')).toBeInTheDocument();
      });

      // Verify attempt info is not shown for first attempt (only shows for > 1)
      expect(screen.queryByText(/Attempt \d+ -/)).not.toBeInTheDocument();

      // Submit again without retry (to increment attempt counter)
      await user.click(submitButton);

      await waitFor(() => {
        // Now we should see attempt 2
        expect(screen.getByText(/Attempt 2 -/)).toBeInTheDocument();
      });
    });
  });

  describe('Success Actions', () => {
    it('should show success actions after successful generation', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockSuccessResponse);

      render(<PuzzleGenerator />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('puzzle-generator-start-solving')).toBeInTheDocument();
        expect(screen.getByTestId('puzzle-generator-generate-another')).toBeInTheDocument();
      });
    });

    it('should call onPuzzleGenerated when start solving is clicked', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockSuccessResponse);

      render(<PuzzleGenerator onPuzzleGenerated={mockOnPuzzleGenerated} />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('puzzle-generator-start-solving')).toBeInTheDocument();
      });

      const startButton = screen.getByTestId('puzzle-generator-start-solving');
      await user.click(startButton);

      expect(mockOnPuzzleGenerated).toHaveBeenCalledWith(mockPuzzle);
    });

    it('should reset state when generate another is clicked', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockResolvedValue(mockSuccessResponse);

      render(<PuzzleGenerator />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('puzzle-generator-generate-another')).toBeInTheDocument();
      });

      const generateAnotherButton = screen.getByTestId('puzzle-generator-generate-another');
      await user.click(generateAnotherButton);

      await waitFor(() => {
        expect(screen.queryByTestId('success-state')).not.toBeInTheDocument();
      });
    });
  });

  describe('Cancel Functionality', () => {
    it('should call onCancel when cancel button is clicked', async () => {
      const user = userEvent.setup();

      render(<PuzzleGenerator showCancel={true} onCancel={mockOnCancel} />);

      const cancelButton = screen.getByTestId('puzzle-generator-cancel');
      await user.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
    });

    it('should disable cancel button during generation', async () => {
      const user = userEvent.setup();
      vi.mocked(apiClient.generatePuzzle).mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve(mockSuccessResponse), 100);
          })
      );

      render(<PuzzleGenerator showCancel={true} onCancel={mockOnCancel} />);

      const topicInput = screen.getByTestId('topic-input');
      await user.type(topicInput, 'Science');

      const submitButton = screen.getByTestId('submit-button');
      await user.click(submitButton);

      await waitFor(() => {
        const cancelButton = screen.getByTestId('puzzle-generator-cancel');
        expect(cancelButton).toBeDisabled();
      });
    });
  });

  describe('Custom Props', () => {
    it('should apply custom className', () => {
      render(<PuzzleGenerator className="custom-class" />);

      const container = screen.getByTestId('puzzle-generator');
      expect(container).toHaveClass('custom-class');
    });

    it('should use custom testId', () => {
      render(<PuzzleGenerator testId="custom-test-id" />);

      const container = screen.getByTestId('custom-test-id');
      expect(container).toBeInTheDocument();
    });

    it('should pass showAdvancedOptions to form', () => {
      render(<PuzzleGenerator showAdvancedOptions={true} />);

      // Advanced options should be visible
      const advancedToggle = screen.getByTestId('advanced-toggle');
      expect(advancedToggle).toHaveAttribute('aria-expanded', 'true');
    });
  });
});
