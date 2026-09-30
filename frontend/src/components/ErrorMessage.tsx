/**
 * ErrorMessage component - Reusable error message display with customizable styling.
 * 
 * Features:
 * - Displays error messages with icon
 * - Customizable severity (error, warning, info)
 * - Optional dismiss button
 * - Optional retry action
 * - Accessible with ARIA attributes
 * - Responsive design
 */

import React from 'react';

export interface ErrorMessageProps {
  /** Error message to display */
  message: string;
  /** Severity level of the error */
  severity?: 'error' | 'warning' | 'info';
  /** Optional title for the error */
  title?: string;
  /** Whether to show a dismiss button */
  dismissible?: boolean;
  /** Callback when dismiss button is clicked */
  onDismiss?: () => void;
  /** Optional retry action */
  onRetry?: () => void;
  /** Retry button label */
  retryLabel?: string;
  /** Optional CSS class name */
  className?: string;
  /** Optional test ID */
  testId?: string;
}

/**
 * ErrorMessage component displays error messages with appropriate styling.
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  severity = 'error',
  title,
  dismissible = false,
  onDismiss,
  onRetry,
  retryLabel = 'Retry',
  className = '',
  testId = 'error-message',
}) => {
  // Icon and color mappings
  const severityConfig = {
    error: {
      icon: '❌',
      bgColor: '#fee',
      borderColor: '#fcc',
      textColor: '#c33',
      iconColor: '#c33',
    },
    warning: {
      icon: '⚠️',
      bgColor: '#fffbeb',
      borderColor: '#fde68a',
      textColor: '#92400e',
      iconColor: '#f59e0b',
    },
    info: {
      icon: 'ℹ️',
      bgColor: '#eff6ff',
      borderColor: '#bfdbfe',
      textColor: '#1e40af',
      iconColor: '#3b82f6',
    },
  };

  const config = severityConfig[severity];

  // Styles
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    padding: '16px',
    background: config.bgColor,
    border: `1px solid ${config.borderColor}`,
    borderRadius: '8px',
    color: config.textColor,
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
  };

  const iconStyle: React.CSSProperties = {
    fontSize: '20px',
    flexShrink: 0,
    color: config.iconColor,
  };

  const contentStyle: React.CSSProperties = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  };

  const titleStyle: React.CSSProperties = {
    margin: 0,
    fontSize: '16px',
    fontWeight: 600,
    lineHeight: 1.5,
  };

  const messageStyle: React.CSSProperties = {
    margin: 0,
    fontSize: '14px',
    lineHeight: 1.5,
  };

  const actionsStyle: React.CSSProperties = {
    display: 'flex',
    gap: '8px',
    marginTop: '8px',
  };

  const buttonBaseStyle: React.CSSProperties = {
    padding: '6px 12px',
    fontSize: '14px',
    fontWeight: 500,
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.2s',
  };

  const retryButtonStyle: React.CSSProperties = {
    ...buttonBaseStyle,
    background: config.textColor,
    color: 'white',
  };

  // Dismiss button style (currently unused, reserved for future use)
  // const dismissButtonStyle: React.CSSProperties = {
  //   ...buttonBaseStyle,
  //   background: 'transparent',
  //   color: config.textColor,
  //   border: `1px solid ${config.borderColor}`,
  // };

  const closeButtonStyle: React.CSSProperties = {
    marginLeft: 'auto',
    padding: '4px',
    background: 'transparent',
    border: 'none',
    color: config.textColor,
    fontSize: '18px',
    cursor: 'pointer',
    lineHeight: 1,
    opacity: 0.7,
    transition: 'opacity 0.2s',
  };

  return (
    <div
      className={className}
      style={containerStyle}
      role="alert"
      aria-live="assertive"
      data-testid={testId}
    >
      <div style={headerStyle}>
        <span style={iconStyle} aria-hidden="true">
          {config.icon}
        </span>
        <div style={contentStyle}>
          {title && (
            <h3 style={titleStyle} data-testid={`${testId}-title`}>
              {title}
            </h3>
          )}
          <p style={messageStyle} data-testid={`${testId}-text`}>
            {message}
          </p>
        </div>
        {dismissible && onDismiss && (
          <button
            style={closeButtonStyle}
            onClick={onDismiss}
            aria-label="Dismiss error"
            data-testid={`${testId}-dismiss`}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '1';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '0.7';
            }}
          >
            ✕
          </button>
        )}
      </div>
      {onRetry && (
        <div style={actionsStyle}>
          <button
            style={retryButtonStyle}
            onClick={onRetry}
            data-testid={`${testId}-retry`}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '0.9';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '1';
            }}
          >
            {retryLabel}
          </button>
        </div>
      )}
    </div>
  );
};

export default ErrorMessage;
