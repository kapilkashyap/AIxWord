/**
 * LoadingSpinner component - Reusable loading spinner with customizable size and message.
 * 
 * Features:
 * - Animated CSS spinner
 * - Customizable size (small, medium, large)
 * - Optional loading message
 * - Accessible with ARIA attributes
 * - Responsive design
 */

import React from 'react';

export interface LoadingSpinnerProps {
  /** Size of the spinner */
  size?: 'small' | 'medium' | 'large';
  /** Optional loading message to display */
  message?: string;
  /** Whether to center the spinner */
  centered?: boolean;
  /** Optional CSS class name */
  className?: string;
  /** Optional test ID */
  testId?: string;
}

/**
 * LoadingSpinner component displays an animated loading indicator.
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  message,
  centered = false,
  className = '',
  testId = 'loading-spinner',
}) => {
  // Size mappings
  const sizeMap = {
    small: '24px',
    medium: '40px',
    large: '64px',
  };

  const spinnerSize = sizeMap[size];

  // Styles
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: centered ? 'center' : 'flex-start',
    gap: '12px',
    padding: centered ? '40px 20px' : '0',
    minHeight: centered ? '200px' : 'auto',
  };

  const spinnerStyle: React.CSSProperties = {
    width: spinnerSize,
    height: spinnerSize,
    border: `${size === 'small' ? '2px' : size === 'medium' ? '3px' : '4px'} solid #e5e7eb`,
    borderTop: `${size === 'small' ? '2px' : size === 'medium' ? '3px' : '4px'} solid #667eea`,
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  };

  const messageStyle: React.CSSProperties = {
    fontSize: size === 'small' ? '14px' : size === 'medium' ? '16px' : '18px',
    color: '#6b7280',
    textAlign: 'center',
    maxWidth: '400px',
  };

  return (
    <div
      className={className}
      style={containerStyle}
      role="status"
      aria-live="polite"
      aria-busy="true"
      data-testid={testId}
    >
      <div style={spinnerStyle} aria-hidden="true" />
      {message && (
        <p style={messageStyle} data-testid={`${testId}-message`}>
          {message}
        </p>
      )}
      <span className="sr-only">Loading...</span>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border-width: 0;
          }
        `}
      </style>
    </div>
  );
};

export default LoadingSpinner;
