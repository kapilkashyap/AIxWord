/**
 * Toast component - Lightweight notification component for transient messages.
 * 
 * This component displays toast notifications with:
 * - Auto-dismiss after configurable duration
 * - Manual dismiss option
 * - Multiple severity levels (success, error, warning, info)
 * - Smooth slide-in/slide-out animations
 * - Accessible with ARIA live regions
 * - Stacking support for multiple toasts
 * 
 * Features:
 * - Used for non-blocking feedback (e.g., "Puzzle saved", "Hint copied")
 * - Positioned at top-right by default
 * - Does not interrupt user workflow
 * - Automatically removes after duration
 * 
 * Usage:
 * ```tsx
 * <Toast
 *   message="Puzzle saved successfully!"
 *   severity="success"
 *   duration={3000}
 *   onClose={() => setToast(null)}
 * />
 * ```
 */

import React, { useEffect, useRef, useState } from 'react';
import styles from './Toast.module.css';

export type ToastSeverity = 'success' | 'error' | 'warning' | 'info';

export interface ToastProps {
  /** Toast message to display */
  message: string;
  /** Severity level (affects icon and color) */
  severity?: ToastSeverity;
  /** Duration in milliseconds before auto-dismiss (0 = no auto-dismiss) */
  duration?: number;
  /** Whether to show close button */
  dismissible?: boolean;
  /** Callback when toast is closed */
  onClose: () => void;
  /** Optional action button */
  action?: {
    label: string;
    onClick: () => void;
  };
  /** Position of the toast */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  /** Optional test ID */
  testId?: string;
}

/**
 * Toast component displays transient notification messages.
 */
export const Toast: React.FC<ToastProps> = ({
  message,
  severity = 'info',
  duration = 5000,
  dismissible = true,
  onClose,
  action,
  position = 'top-right',
  testId = 'toast',
}) => {
  const [isExiting, setIsExiting] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const toastRef = useRef<HTMLDivElement>(null);

  // Auto-dismiss after duration
  useEffect(() => {
    if (duration > 0) {
      timerRef.current = setTimeout(() => {
        handleClose();
      }, duration);

      return () => {
        if (timerRef.current) {
          clearTimeout(timerRef.current);
        }
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [duration]);

  // Handle close with exit animation
  const handleClose = () => {
    setIsExiting(true);
    // Wait for exit animation to complete
    setTimeout(() => {
      onClose();
    }, 300); // Match animation duration
  };

  // Handle action click
  const handleActionClick = () => {
    if (action) {
      action.onClick();
      handleClose();
    }
  };

  // Get severity configuration
  const severityConfig = {
    success: {
      icon: '✓',
      ariaLabel: 'Success',
    },
    error: {
      icon: '✕',
      ariaLabel: 'Error',
    },
    warning: {
      icon: '⚠',
      ariaLabel: 'Warning',
    },
    info: {
      icon: 'ℹ',
      ariaLabel: 'Information',
    },
  };

  const config = severityConfig[severity];

  // Determine CSS classes
  const toastClasses = [
    styles.toast,
    styles[`toast${severity.charAt(0).toUpperCase() + severity.slice(1)}`],
    styles[`position${position.split('-').map(p => p.charAt(0).toUpperCase() + p.slice(1)).join('')}`],
    isExiting ? styles.toastExit : '',
  ].filter(Boolean).join(' ');

  return (
    <div
      ref={toastRef}
      className={toastClasses}
      role="alert"
      aria-live={severity === 'error' ? 'assertive' : 'polite'}
      aria-atomic="true"
      data-testid={testId}
    >
      {/* Icon */}
      <div
        className={styles.icon}
        aria-label={config.ariaLabel}
        data-testid={`${testId}-icon`}
      >
        {config.icon}
      </div>

      {/* Content */}
      <div className={styles.content}>
        <p className={styles.message} data-testid={`${testId}-message`}>
          {message}
        </p>
        
        {/* Action button */}
        {action && (
          <button
            className={styles.actionButton}
            onClick={handleActionClick}
            data-testid={`${testId}-action`}
          >
            {action.label}
          </button>
        )}
      </div>

      {/* Close button */}
      {dismissible && (
        <button
          className={styles.closeButton}
          onClick={handleClose}
          aria-label="Close notification"
          data-testid={`${testId}-close`}
        >
          ✕
        </button>
      )}

      {/* Progress bar for auto-dismiss */}
      {duration > 0 && (
        <div
          className={styles.progressBar}
          style={{
            animationDuration: `${duration}ms`,
          }}
          data-testid={`${testId}-progress`}
        />
      )}
    </div>
  );
};

export default Toast;
