/**
 * Hooks module exports.
 * 
 * This module provides custom React hooks for the application:
 * - useAPI: API call state management
 * - usePuzzle: Puzzle state management
 * - useSolving: Solving-specific state and logic
 * - useAIAssistance: AI assistance features
 * - useToast: Toast notification management
 */

export { useAPI, useMultiAPI } from './useAPI';
export { usePuzzle } from './usePuzzle';
export { useSolving } from './useSolving';
export { useAIAssistance } from './useAIAssistance';
export { useToast } from './useToast';

// Re-export types
export type { ApiState } from '../types/api';
export type {
  SolvingStats,
  WordCompletionInfo,
} from './useSolving';
export type {
  HintModalState,
  ConfirmationDialogState,
  SolutionAnimationState,
} from './useAIAssistance';
export type {
  ToastOptions,
  ToastState,
  UseToastReturn,
} from './useToast';
