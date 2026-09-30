/**
 * TypeScript type definitions for puzzle domain models.
 * These types match the backend API schemas for consistency.
 */

/**
 * Direction of a word in the crossword grid.
 */
export type Direction = 'across' | 'down';

/**
 * Difficulty level for puzzle generation.
 */
export type Difficulty = 'easy' | 'medium' | 'hard';

/**
 * Type of hint that can be requested.
 */
export type HintType = 'letter' | 'definition' | 'synonym';

/**
 * Represents a single cell in the crossword grid.
 */
export interface Cell {
  /** Row position (0-indexed) */
  row: number;
  /** Column position (0-indexed) */
  col: number;
  /** Letter value in the cell (uppercase), null if empty */
  value: string | null;
  /** Whether this cell is blocked (black square) */
  is_blocked: boolean;
  /** Clue number if this cell starts a word, null otherwise */
  number: number | null;
}

/**
 * Represents a clue for a word in the puzzle.
 */
export interface Clue {
  /** Clue number */
  number: number;
  /** Direction of the word */
  direction: Direction;
  /** Clue text */
  text: string;
  /** Answer word (may be null for unsolved puzzles) */
  answer: string | null;
  /** Starting row position */
  start_row: number;
  /** Starting column position */
  start_col: number;
  /** Length of the answer */
  length: number;
}

/**
 * Represents a complete crossword puzzle.
 */
export interface Puzzle {
  /** Unique puzzle identifier */
  puzzle_id: string;
  /** Topic of the puzzle */
  topic: string;
  /** Size of the grid (NxN) */
  grid_size: number;
  /** All cells in the grid */
  cells: Cell[];
  /** Across clues */
  clues_across: Clue[];
  /** Down clues */
  clues_down: Clue[];
  /** Number of words in the puzzle */
  word_count: number;
  /** Grid fill rate (0.0 to 1.0) */
  fill_rate: number;
  /** Difficulty level */
  difficulty: Difficulty;
  /** Creation timestamp */
  created_at: string;
  /** Additional metadata */
  metadata: Record<string, unknown>;
}

/**
 * Represents a word placement in the grid.
 */
export interface WordPlacement {
  /** Word text */
  word: string;
  /** Clue for the word */
  clue: string;
  /** Starting row */
  start_row: number;
  /** Starting column */
  start_col: number;
  /** Direction */
  direction: Direction;
  /** Clue number */
  number: number;
}

/**
 * Represents the current state of a cell during solving.
 */
export interface CellState extends Cell {
  /** Whether this cell is currently selected */
  is_selected: boolean;
  /** Whether this cell is part of the active word */
  is_active_word: boolean;
  /** Whether this cell is part of a completed word */
  is_completed: boolean;
  /** Whether this cell has an error */
  has_error: boolean;
}

/**
 * Represents the state of the puzzle grid during solving.
 */
export interface GridState {
  /** Current cell states */
  cells: CellState[];
  /** Currently selected cell position */
  selected_cell: { row: number; col: number } | null;
  /** Current word direction */
  current_direction: Direction;
  /** Currently active clue */
  active_clue: { number: number; direction: Direction } | null;
}

/**
 * Validation error for a cell.
 */
export interface ValidationError {
  /** Row position */
  row: number;
  /** Column position */
  col: number;
  /** Expected value */
  expected: string;
  /** Actual value provided */
  actual: string | null;
  /** Error message */
  message: string;
}
