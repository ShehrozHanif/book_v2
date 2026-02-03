import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ErrorMessage } from "../src/components/ErrorMessage";

describe("ErrorMessage Component", () => {
  it("renders error message with default type", () => {
    render(<ErrorMessage error="Something went wrong" />);

    expect(screen.getByText("Something went wrong. Please try again.")).toBeInTheDocument();
  });

  it("shows user-friendly message for user errors", () => {
    render(<ErrorMessage error="Invalid input" errorType="user" />);

    expect(screen.getByText("Please check your input and try again.")).toBeInTheDocument();
  });

  it("shows timeout message", () => {
    render(<ErrorMessage error="Timeout" errorType="timeout" />);

    expect(screen.getByText("Response is taking longer than expected. Please try again.")).toBeInTheDocument();
  });

  it("shows network error message", () => {
    render(<ErrorMessage error="Network failed" errorType="network" />);

    expect(screen.getByText("Network error. Please check your connection.")).toBeInTheDocument();
  });

  it("shows retry button for API errors", () => {
    const onRetry = jest.fn();
    render(<ErrorMessage error="API error" errorType="api" onRetry={onRetry} />);

    const retryButton = screen.getByText("Retry");
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("does not show retry button for user errors", () => {
    const onRetry = jest.fn();
    render(<ErrorMessage error="User error" errorType="user" onRetry={onRetry} />);

    expect(screen.queryByText("Retry")).not.toBeInTheDocument();
  });

  it("shows dismiss button when provided", () => {
    const onDismiss = jest.fn();
    render(<ErrorMessage error="Error" onDismiss={onDismiss} />);

    const dismissButton = screen.getByText("Dismiss");
    expect(dismissButton).toBeInTheDocument();

    fireEvent.click(dismissButton);
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("handles 429 error code", () => {
    render(<ErrorMessage error="Chat API error: 429 Too Many Requests" errorType="api" />);

    expect(screen.getByText("Too many requests. Please wait a moment before trying again.")).toBeInTheDocument();
  });

  it("handles 500 error code", () => {
    render(<ErrorMessage error="Chat API error: 500 Internal Server Error" errorType="api" />);

    expect(screen.getByText(/Server error. Our team has been notified/)).toBeInTheDocument();
  });
});
