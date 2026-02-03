import React from "react";
import "./LoadingIndicator.module.css";

interface LoadingIndicatorProps {
  isVisible: boolean;
  elapsedTime?: number; // in milliseconds
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  isVisible,
  elapsedTime = 0,
}) => {
  if (!isVisible) return null;

  const seconds = (elapsedTime / 1000).toFixed(1);
  const isSlowResponse = elapsedTime > 2000;

  return (
    <div
      className={`loading-indicator ${isSlowResponse ? "slow" : ""}`}
      role="status"
      aria-label="Loading indicator"
      aria-live="polite"
    >
      <div className="spinner"></div>
      <p className="loading-text">Searching textbook...</p>
      {isSlowResponse && (
        <p className="slow-message">
          This is taking longer than usual... Please be patient.
        </p>
      )}
      <span className="timer" aria-label={`Elapsed time: ${seconds} seconds`}>
        {seconds}s
      </span>
    </div>
  );
};

export default LoadingIndicator;
