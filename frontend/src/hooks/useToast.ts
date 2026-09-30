/**
 * Custom hook for managing toast notifications.
 * 
 * This hook provides a simple API for showing toast notifications:
 * - Show success, error, warning, or info toasts
 * - Auto-dismiss after configurable duration
 * - Manual dismiss support
 * - Queue multiple toasts
 * - Position control
 * 
 * Features:
 * - Centralized toast state management
 * - Type-safe toast creation
 * - Automatic cleanup
 * - Support for action buttons
 * 
 * Usage:
 * ```tsx
 * const { showToast, showSuccess, showError, hideToast } = useToast();
 * 
 * // Show success toast
 * showSuccess('Puzzle saved successfully!');
 * 
 * // Show error toast
 * showError('Failed to generate puzzle');
 * 
 * // Show toast with action
 * showToast({
 *   message: 'Hint copied to clipboard',
 *   severity: 'info',
 *   action: {
 *     label: 'Undo',
 *     onClick: () => console.log('Undo clicked'),
 *   },
 * });
 * ```
 */

import { useState, useCallback } from 'react';
import type { ToastSeverity } from '../components/Toast';

/**
 * Toast configuration options.
 */
export interface ToastOptions {
  /** Toast message */
  message: string;
  /** Severity level */
  severity?: ToastSeverity;
  /** Duration in milliseconds (0 = no auto-dismiss) */
  duration?: number;
  /** Whether to show close button */
  dismissible?: boolean;
  /** Optional action button */
  action?: {
    label: string;
    onClick: () => void;
  };
  /** Position of the toast */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

/**
 * Toast state with unique ID.
 */
export interface ToastState extends ToastOptions {
  /** Unique toast ID */
  id: string;
}

/**
 * Hook return type.
 */
export interface UseToastReturn {
  /** Current active toasts */
  toasts: ToastState[];
  /** Show a toast with custom options */
  showToast: (options: ToastOptions) => string;
  /** Show a success toast */
  showSuccess: (message: string, duration?: number) => string;
  /** Show an error toast */
  showError: (message: string, duration?: number) => string;
  /** Show a warning toast */
  showWarning: (message: string, duration?: number) => string;
  /** Show an info toast */
  showInfo: (message: string, duration?: number) => string;
  /** Hide a specific toast by ID */
  hideToast: (id: string) => void;
  /** Hide all toasts */
  hideAllToasts: () => void;
}

/**
 * Generate a unique ID for toasts.
 */
let toastIdCounter = 0;
function generateToastId(): string {
  return `toast-${Date.now()}-${++toastIdCounter}`;
}

/**
 * Custom hook for managing toast notifications.
 * 
 * @param maxToasts - Maximum number of toasts to show simultaneously (default: 3)
 * @returns Object with toast state and control functions
 */
export function useToast(maxToasts: number = 3): UseToastReturn {
  const [toasts, setToasts] = useState<ToastState[]>([]);

  /**
   * Show a toast with custom options.
   */
  const showToast = useCallback((options: ToastOptions): string => {
    const id = generateToastId();
    const newToast: ToastState = {
      id,
      severity: 'info',
      duration: 5000,
      dismissible: true,
      position: 'top-right',
      ...options,
    };

    setToasts(prevToasts => {
      // If we've reached max toasts, remove the oldest one
      const updatedToasts = prevToasts.length >= maxToasts
        ? prevToasts.slice(1)
        : prevToasts;
      
      return [...updatedToasts, newToast];
    });

    return id;
  }, [maxToasts]);

  /**
   * Show a success toast.
   */
  const showSuccess = useCallback((message: string, duration: number = 3000): string => {
    return showToast({
      message,
      severity: 'success',
      duration,
    });
  }, [showToast]);

  /**
   * Show an error toast.
   */
  const showError = useCallback((message: string, duration: number = 5000): string => {
    return showToast({
      message,
      severity: 'error',
      duration,
    });
  }, [showToast]);

  /**
   * Show a warning toast.
   */
  const showWarning = useCallback((message: string, duration: number = 4000): string => {
    return showToast({
      message,
      severity: 'warning',
      duration,
    });
  }, [showToast]);

  /**
   * Show an info toast.
   */
  const showInfo = useCallback((message: string, duration: number = 3000): string => {
    return showToast({
      message,
      severity: 'info',
      duration,
    });
  }, [showToast]);

  /**
   * Hide a specific toast by ID.
   */
  const hideToast = useCallback((id: string) => {
    setToasts(prevToasts => prevToasts.filter(toast => toast.id !== id));
  }, []);

  /**
   * Hide all toasts.
   */
  const hideAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  return {
    toasts,
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hideToast,
    hideAllToasts,
  };
}

export default useToast;
