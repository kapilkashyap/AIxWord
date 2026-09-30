/**
 * TypeScript type definitions for AI assistance features.
 * 
 * These types support the AI-powered solving assistance including:
 * - Hint modal state and display
 * - Confirmation dialogs for destructive actions
 * - Solution animations
 * - AI operation states and results
 */

import type { Cell, Direction, HintType } from './puzzle';

// ============================================================================
// AI Operation Types
// ============================================================================

/**
 * Type of AI assistance operation.
 */
export type AIOperationType = 'solve-word' | 'solve-puzzle' | 'hint';

/**
 * Status of an AI operation.
 */
export type AIOperationStatus = 'idle' | 'loading' | 'success' | 'error';

/**
 * Result of an AI solve operation.
 */
export interface AISolveResult {
  /** Whether the operation was successful */
  success: boolean;
  /** The answer or solution provided */
  answer: string | null;
  /** Confidence score (0.0 to 1.0) */
  confidence: number;
  /** AI's reasoning or explanation */
  reasoning: string | null;
  /** Cells that were updated */
  updatedCells: Cell[];
}

/**
 * Result of an AI hint operation.
 */
export interface AIHintResult {
  /** Whether the operation was successful */
  success: boolean;
  /** The hint text */
  hint: string;
  /** Type of hint provided */
  hintType: HintType;
  /** Revealed letter (if hint type is 'letter') */
  revealedLetter: string | null;
  /** Position of revealed letter (0-indexed) */
  position: number | null;
}

// ============================================================================
// Modal and Dialog State Types
// ============================================================================

/**
 * State for the hint modal display.
 */
export interface HintModalState {
  /** Whether the hint modal is visible */
  isVisible: boolean;
  /** The hint text to display */
  hint: string;
  /** Type of hint provided */
  hintType: HintType;
  /** Revealed letter (if hint type is 'letter') */
  revealedLetter: string | null;
  /** Position of revealed letter (if applicable) */
  position: number | null;
  /** Clue information for context */
  clueInfo: {
    /** Clue number */
    number: number;
    /** Direction (across/down) */
    direction: string;
    /** Clue text */
    text: string;
  };
}

/**
 * State for confirmation dialog.
 */
export interface ConfirmationDialogState {
  /** Whether the dialog is visible */
  isVisible: boolean;
  /** Title of the dialog */
  title: string;
  /** Message to display */
  message: string;
  /** Type of action (affects styling) */
  actionType: 'solve-word' | 'solve-puzzle';
  /** Callback when user confirms */
  onConfirm: () => void;
  /** Callback when user cancels */
  onCancel: () => void;
}

/**
 * State for solution animation.
 */
export interface SolutionAnimationState {
  /** Whether animation is active */
  isActive: boolean;
  /** Type of solution being animated */
  type: 'word' | 'puzzle';
  /** Cells being animated */
  cells: Array<{
    /** Row position */
    row: number;
    /** Column position */
    col: number;
    /** Letter value */
    value: string;
  }>;
  /** Current animation step (number of cells filled) */
  currentStep: number;
}

// ============================================================================
// AI Assistance Hook Types
// ============================================================================

/**
 * Parameters for the useAIAssistance hook.
 */
export interface UseAIAssistanceParams {
  /** Current puzzle ID */
  puzzleId: string | null;
  /** Currently active clue */
  activeClue: {
    /** Clue number */
    number: number;
    /** Direction */
    direction: Direction;
  } | null;
  /** Function to update cell values */
  setCellValue: (row: number, col: number, value: string | null) => void;
}

/**
 * Return type for the useAIAssistance hook.
 */
export interface UseAIAssistanceReturn {
  // Loading states
  /** Whether solve word operation is in progress */
  isSolvingWord: boolean;
  /** Whether solve puzzle operation is in progress */
  isSolvingPuzzle: boolean;
  /** Whether hint generation is in progress */
  isGettingHint: boolean;
  /** Whether any AI operation is in progress */
  isAnyOperationInProgress: boolean;

  // Error states
  /** Error message from solve word operation */
  solveWordError: string | null;
  /** Error message from solve puzzle operation */
  solvePuzzleError: string | null;
  /** Error message from hint operation */
  hintError: string | null;

  // Modal states
  /** Current hint modal state */
  hintModal: HintModalState | null;
  /** Current confirmation dialog state */
  confirmationDialog: ConfirmationDialogState | null;
  /** Current solution animation state */
  solutionAnimation: SolutionAnimationState | null;

  // Actions
  /** Show confirmation dialog for solve word */
  showSolveWordConfirmation: () => void;
  /** Show confirmation dialog for solve puzzle */
  showSolvePuzzleConfirmation: () => void;
  /** Get a hint for the current word */
  getHint: (hintType?: HintType, clueText?: string) => Promise<void>;
  /** Close the hint modal */
  closeHintModal: () => void;
  /** Close the confirmation dialog */
  closeConfirmationDialog: () => void;
  /** Clear all error messages */
  clearErrors: () => void;
}

// ============================================================================
// Component Prop Types
// ============================================================================

/**
 * Props for AIAssistancePanel component.
 */
export interface AIAssistancePanelProps {
  /** Whether a puzzle is loaded */
  hasPuzzle: boolean;
  /** Currently active clue */
  activeClue: {
    /** Clue number */
    number: number;
    /** Direction */
    direction: Direction;
  } | null;
  /** Whether solve word operation is in progress */
  isSolvingWord?: boolean;
  /** Whether solve puzzle operation is in progress */
  isSolvingPuzzle?: boolean;
  /** Whether hint generation is in progress */
  isGettingHint?: boolean;
  /** Callback when solve word is clicked */
  onSolveWord: () => void;
  /** Callback when solve puzzle is clicked */
  onSolvePuzzle: () => void;
  /** Callback when get hint is clicked */
  onGetHint: () => void;
  /** Optional CSS class name */
  className?: string;
}

/**
 * Props for HintModal component.
 */
export interface HintModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** The hint text to display */
  hint: string;
  /** Type of hint */
  hintType: HintType;
  /** Revealed letter (for letter hints) */
  revealedLetter?: string | null;
  /** Position of revealed letter (for letter hints) */
  position?: number | null;
  /** Clue number and direction for context */
  clueInfo?: {
    /** Clue number */
    number: number;
    /** Direction */
    direction: string;
    /** Clue text */
    text: string;
  };
  /** Callback when modal is closed */
  onClose: () => void;
  /** Optional test ID */
  testId?: string;
}

/**
 * Props for SolutionAnimation component.
 */
export interface SolutionAnimationProps {
  /** Cells to animate */
  cells: Cell[];
  /** Animation speed in milliseconds per letter */
  speed?: number;
  /** Whether animation is active */
  isAnimating: boolean;
  /** Callback when animation completes */
  onComplete: () => void;
  /** Callback to skip animation */
  onSkip?: () => void;
  /** Optional CSS class name */
  className?: string;
  /** Optional test ID */
  testId?: string;
}

/**
 * Props for ConfirmationDialog component.
 */
export interface ConfirmationDialogProps {
  /** Whether the dialog is open */
  isOpen: boolean;
  /** Dialog title */
  title: string;
  /** Dialog message/description */
  message: string;
  /** Confirm button label */
  confirmLabel?: string;
  /** Cancel button label */
  cancelLabel?: string;
  /** Confirm button variant */
  confirmVariant?: 'primary' | 'danger' | 'warning';
  /** Whether confirm action is in progress */
  isConfirming?: boolean;
  /** Callback when confirmed */
  onConfirm: () => void;
  /** Callback when cancelled */
  onCancel: () => void;
  /** Optional icon */
  icon?: string;
  /** Optional test ID */
  testId?: string;
}

// ============================================================================
// Animation Configuration Types
// ============================================================================

/**
 * Configuration for solution animation.
 */
export interface AnimationConfig {
  /** Speed in milliseconds per letter */
  speed: number;
  /** Batch size for puzzle solving (number of cells per step) */
  batchSize: number;
  /** Delay before ending animation (milliseconds) */
  endDelay: number;
  /** Whether to respect prefers-reduced-motion */
  respectReducedMotion: boolean;
}

/**
 * Default animation configuration.
 */
export const DEFAULT_ANIMATION_CONFIG: AnimationConfig = {
  speed: 150,
  batchSize: 3,
  endDelay: 500,
  respectReducedMotion: true,
};

// ============================================================================
// AI Assistance Context Types
// ============================================================================

/**
 * Context value for AI assistance features.
 * Used when providing AI assistance through React Context.
 */
export interface AIAssistanceContextValue {
  /** Current AI operation in progress */
  currentOperation: AIOperationType | null;
  /** Status of current operation */
  operationStatus: AIOperationStatus;
  /** Last error message */
  lastError: string | null;
  /** Solve current word with AI */
  solveWord: () => Promise<void>;
  /** Solve entire puzzle with AI */
  solvePuzzle: () => Promise<void>;
  /** Get hint for current word */
  getHint: (hintType?: HintType) => Promise<void>;
  /** Clear error state */
  clearError: () => void;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Options for AI solve operations.
 */
export interface AISolveOptions {
  /** Whether to use existing clues as hints */
  useHints?: boolean;
  /** Whether to use intersecting letters */
  useIntersections?: boolean;
  /** Whether to show confirmation dialog */
  showConfirmation?: boolean;
  /** Whether to animate the solution */
  animate?: boolean;
  /** Animation configuration */
  animationConfig?: Partial<AnimationConfig>;
}

/**
 * Options for AI hint operations.
 */
export interface AIHintOptions {
  /** Type of hint to request */
  hintType?: HintType;
  /** Whether to show the hint in a modal */
  showModal?: boolean;
  /** Custom clue text for context */
  clueText?: string;
}

/**
 * Callback function type for AI operation completion.
 */
export type AIOperationCallback = (
  result: AISolveResult | AIHintResult,
  error: Error | null
) => void;

/**
 * Callback function type for animation events.
 */
export type AnimationCallback = (step: number, total: number) => void;
