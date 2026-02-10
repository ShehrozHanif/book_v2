import { useEffect, useState, useCallback } from "react";

export interface SelectedText {
  text: string;
  context?: string;
  timestamp: number;
}

export const useTextSelection = (maxContextLength: number = 200) => {
  const [selectedText, setSelectedText] = useState<SelectedText | null>(null);

  const handleSelection = useCallback(() => {
    // First, check if the currently focused element is an input or textarea
    const activeElement = document.activeElement;
    if (
      activeElement &&
      (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA' || activeElement.classList.contains('chat-input'))
    ) {
      // Selection is from input/search box, don't capture it
      setSelectedText(null);
      return;
    }

    const selection = window.getSelection();
    if (!selection) {
      setSelectedText(null);
      return;
    }

    const text = selection.toString() || "";
    if (text.length > 0) {
      setSelectedText({
        text,
        context:
          text.length > maxContextLength
            ? text.substring(0, maxContextLength)
            : text,
        timestamp: Date.now(),
      });
    } else {
      // Clear selection if nothing is selected
      setSelectedText(null);
    }
  }, [maxContextLength]);

  useEffect(() => {
    document.addEventListener("mouseup", handleSelection);
    document.addEventListener("touchend", handleSelection);

    return () => {
      document.removeEventListener("mouseup", handleSelection);
      document.removeEventListener("touchend", handleSelection);
    };
  }, [handleSelection]);

  const clearSelection = useCallback(() => {
    setSelectedText(null);
  }, []);

  return {
    selectedText,
    clearSelection,
    hasSelection: selectedText !== null,
  };
};
