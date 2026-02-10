import React from "react";
import "../styles/error-message.css";

export type ErrorType = "user" | "api" | "timeout" | "network";

interface ErrorMessageProps {
  error: string;
  errorType?: ErrorType;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  error,
  errorType = "api",
  onRetry,
  onDismiss,
}) => {
  const getUserFriendlyMessage = (type: ErrorType, originalError: string): string => {
    switch (type) {
      case "user":
        return "Please check your input and try again.";
      case "timeout":
        return "Response is taking longer than expected. Please try again.";
      case "network":
        return "Network error. Please check your connection.";
      case "api":
      default:
        // Only show generic message for API errors to avoid exposing internals
        if (originalError.includes("429")) {
          return "Too many requests. Please wait a moment before trying again.";
        }
        if (originalError.includes("400")) {
          return "Invalid request. Please check your input.";
        }
        if (originalError.includes("500") || originalError.includes("503")) {
          return "Server error. Our team has been notified. Please try again later.";
        }
        return "Something went wrong. Please try again.";
    }
  };

  const getErrorIcon = (type: ErrorType): string => {
    switch (type) {
      case "user":
        return "⚠️";
      case "timeout":
        return "⏱️";
      case "network":
        return "🌐";
      case "api":
      default:
        return "❌";
    }
  };

  const message = getUserFriendlyMessage(errorType, error);
  const icon = getErrorIcon(errorType);

  // Determine if retry should be shown
  const showRetry = onRetry && (errorType === "api" || errorType === "timeout" || errorType === "network");

  return (
    <div
      className={`error-message error-type-${errorType}`}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="error-content">
        <span className="error-icon" aria-hidden="true">
          {icon}
        </span>
        <p className="error-text">{message}</p>
      </div>

      <div className="error-actions">
        {showRetry && (
          <button
            className="error-btn retry-btn"
            onClick={onRetry}
            aria-label="Retry last action"
          >
            Retry
          </button>
        )}
        {onDismiss && (
          <button
            className="error-btn dismiss-btn"
            onClick={onDismiss}
            aria-label="Dismiss error message"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;
