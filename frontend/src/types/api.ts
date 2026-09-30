/**
 * TypeScript type definitions for API requests and responses.
 * These types match the backend FastAPI schemas.
 */

import type { Cell, Difficulty, Direction, HintType, Puzzle, ValidationError } from './puzzle';

// ============================================================================
// Request Types
// ============================================================================

/**
 * Request to generate a new puzzle.
 */
export interface PuzzleGenerateRequest {
  /** Topic for puzzle generation */
  topic: string;
  /** Grid size (NxN), default 8 */
  grid_size?: number;
  /** Minimum number of words, default 8 */
  min_words?: number;
  /** Maximum number of words, default 15 */
  max_words?: number;
  /** Difficulty level, default 'medium' */
  difficulty?: Difficulty;
  /** Maximum iterations allowed, default 50 */
  max_iterations?: number;
}

/**
 * Request to solve entire puzzle.
 */
export interface SolvePuzzleRequest {
  /** Whether to use existing clues as hints */
  use_hints?: boolean;
}

/**
 * Request to solve a specific word.
 */
export interface SolveWordRequest {
  /** Clue number to solve */
  clue_number: number;
  /** Direction of the word */
  direction: Direction;
  /** Whether to use intersecting letters */
  use_intersections?: boolean;
}

/**
 * Request to get a hint.
 */
export interface HintRequest {
  /** Clue number for hint */
  clue_number: number;
  /** Direction of the word */
  direction: Direction;
  /** Type of hint to provide */
  hint_type?: HintType;
}

/**
 * Request to validate user solution.
 */
export interface ValidateRequest {
  /** User's cell values */
  cells: Cell[];
}

// ============================================================================
// Response Types
// ============================================================================

/**
 * Response from puzzle generation.
 */
export interface PuzzleGenerateResponse {
  /** Whether generation was successful */
  success: boolean;
  /** Generated puzzle (if successful) */
  puzzle: Puzzle | null;
  /** Generation status */
  status: string;
  /** Number of iterations executed */
  iterations: number;
  /** Error message (if failed) */
  error_message: string | null;
}

/**
 * Response from solve operations.
 */
export interface SolveResponse {
  /** Whether solve was successful */
  success: boolean;
  /** The answer word or full solution */
  answer: string | null;
  /** Confidence score (0.0 to 1.0) */
  confidence: number;
  /** Explanation of the solution */
  reasoning: string | null;
  /** Cells that were updated */
  updated_cells: Cell[];
}

/**
 * Response from hint requests.
 */
export interface HintResponse {
  /** Whether hint generation was successful */
  success: boolean;
  /** The hint text */
  hint: string;
  /** Type of hint provided */
  hint_type: string;
  /** Revealed letter (if hint_type is 'letter') */
  revealed_letter: string | null;
  /** Position of revealed letter (if applicable) */
  position: number | null;
}

/**
 * Response from validation.
 */
export interface ValidateResponse {
  /** Whether the solution is valid */
  is_valid: boolean;
  /** Whether the puzzle is completely filled */
  is_complete: boolean;
  /** List of validation errors */
  errors: ValidationError[];
  /** Number of correct cells */
  correct_count: number;
  /** Total number of cells to fill */
  total_count: number;
  /** Accuracy percentage (0.0 to 1.0) */
  accuracy: number;
}

/**
 * Standard error response.
 */
export interface ErrorResponse {
  /** Error type or code */
  error: string;
  /** Human-readable error message */
  message: string;
  /** Additional error details */
  details?: Record<string, unknown>;
}

// ============================================================================
// API State Types
// ============================================================================

/**
 * State for API calls with loading and error handling.
 */
export interface ApiState<T> {
  /** Response data */
  data: T | null;
  /** Whether the request is in progress */
  loading: boolean;
  /** Error message if request failed */
  error: string | null;
}

/**
 * Configuration for API client.
 */
export interface ApiConfig {
  /** Base URL for API requests */
  baseUrl: string;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Additional headers */
  headers?: Record<string, string>;
}
