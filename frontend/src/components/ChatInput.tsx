import React, { useState, useRef, useEffect } from "react";
import { SelectedText } from "../hooks/useTextSelection";
import "./ChatInput.module.css";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  selectedText?: SelectedText | null;
  error?: string | null;
}

/**
 * Check if text looks like a prompt injection attempt
 * This is client-side validation only - server must also validate
 */
const looksLikeInjection = (text: string): boolean => {
  const suspiciousPatterns = [
    /ignore\s+(previous|all|earlier|above)/i,
    /forget\s+(about|everything|instructions)/i,
    /system\s+prompt/i,
    /jailbreak/i,
    /act\s+as\s+(a\s+)?different/i,
    /disregard\s+(previous|all)/i,
  ];

  return suspiciousPatterns.some(pattern => pattern.test(text));
};

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  selectedText,
  error,
}) => {
  const [inputValue, setInputValue] = useState("");
  const [validationWarning, setValidationWarning] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-populate input field when text is selected
  useEffect(() => {
    if (selectedText && selectedText.text) {
      // Set a suggested prompt with the selected text
      const suggestedPrompt = `Explain: "${selectedText.text.substring(0, 100)}"`;
      setInputValue(suggestedPrompt);
      inputRef.current?.focus();
    }
  }, [selectedText]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate input
    if (!inputValue.trim()) {
      setValidationWarning("Please enter a message");
      return;
    }

    // Check for obvious injection attempts (client-side only)
    if (looksLikeInjection(inputValue)) {
      console.warn("Possible injection attempt detected");
      // Still allow submission but log the warning
    }

    setValidationWarning(null);
    onSendMessage(inputValue);
    setInputValue("");
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  // Placeholder text
  const placeholderText = "Ask a question about the textbook...";

  // Check if input is valid
  const isValid = inputValue.trim().length > 0;

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <div className="input-wrapper">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            // Clear validation warning when user types
            if (validationWarning) {
              setValidationWarning(null);
            }
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholderText}
          disabled={isLoading}
          className={`chat-input ${validationWarning ? "invalid" : ""}`}
          maxLength={5000}
          autoFocus
          aria-label="Chat message input"
          aria-invalid={!!validationWarning}
          aria-describedby={validationWarning ? "input-error" : undefined}
        />
        <button
          type="submit"
          disabled={isLoading || !isValid}
          className="chat-submit-btn"
          aria-label="Send message"
          title={!isValid ? "Enter a message to send" : "Send message"}
        >
          {isLoading ? "..." : "Send"}
        </button>
      </div>
      {validationWarning && (
        <p id="input-error" className="input-validation-error" role="alert">
          {validationWarning}
        </p>
      )}
      {error && (
        <p className="input-error-message" role="alert">
          {error}
        </p>
      )}
    </form>
  );
};

export default ChatInput;
