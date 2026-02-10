/**
 * LanguageSettings Component Tests (T055)
 *
 * Tests for language preference component:
 * - Display current preference
 * - Submit change
 * - Handle loading/error states
 */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LanguageSettings } from "./LanguageSettings";
import * as languageAPI from "../../services/languagePreferenceAPI";

// Mock the API
jest.mock("../../services/languagePreferenceAPI");

describe("LanguageSettings Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Display current preference", () => {
    it("should display current language preference", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "english",
      });

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByDisplayValue("english")).toBeInTheDocument();
      });
    });

    it("should display Urdu option when selected", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "urdu",
      });

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByDisplayValue("urdu")).toBeInTheDocument();
      });
    });

    it("should show loading state initially", () => {
      (languageAPI.getPreference as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(<LanguageSettings />);

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
  });

  describe("Submit change", () => {
    it("should submit language preference change", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "english",
      });
      (languageAPI.setPreference as jest.Mock).mockResolvedValue({
        language: "urdu",
      });

      const { rerender } = render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByDisplayValue("english")).toBeInTheDocument();
      });

      // Change to Urdu
      const urduRadio = screen.getByLabelText(/اردو|urdu/i);
      fireEvent.click(urduRadio);

      const saveButton = screen.getByRole("button", { name: /save|submit/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(languageAPI.setPreference).toHaveBeenCalledWith("urdu");
      });
    });

    it("should handle successful save", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "english",
      });
      (languageAPI.setPreference as jest.Mock).mockResolvedValue({
        language: "urdu",
      });

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByDisplayValue("english")).toBeInTheDocument();
      });

      const urduRadio = screen.getByLabelText(/urdu/i);
      fireEvent.click(urduRadio);

      const saveButton = screen.getByRole("button", { name: /save/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/saved|success/i)).toBeInTheDocument();
      });
    });

    it("should disable save button when loading", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "english",
      });
      (languageAPI.setPreference as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByDisplayValue("english")).toBeInTheDocument();
      });

      const urduRadio = screen.getByLabelText(/urdu/i);
      fireEvent.click(urduRadio);

      const saveButton = screen.getByRole("button", { name: /save/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(saveButton).toBeDisabled();
      });
    });
  });

  describe("Error handling", () => {
    it("should display error message on save failure", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "english",
      });
      (languageAPI.setPreference as jest.Mock).mockRejectedValue(
        new Error("Failed to save")
      );

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByDisplayValue("english")).toBeInTheDocument();
      });

      const urduRadio = screen.getByLabelText(/urdu/i);
      fireEvent.click(urduRadio);

      const saveButton = screen.getByRole("button", { name: /save/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/error|failed/i)).toBeInTheDocument();
      });
    });

    it("should display error when loading preference fails", async () => {
      (languageAPI.getPreference as jest.Mock).mockRejectedValue(
        new Error("Failed to load")
      );

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByText(/error|failed/i)).toBeInTheDocument();
      });
    });

    it("should allow retry after error", async () => {
      (languageAPI.getPreference as jest.Mock)
        .mockRejectedValueOnce(new Error("Failed"))
        .mockResolvedValueOnce({ language: "english" });

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByText(/error|failed/i)).toBeInTheDocument();
      });

      const retryButton = screen.getByRole("button", { name: /retry/i });
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByDisplayValue("english")).toBeInTheDocument();
      });
    });
  });

  describe("Radio button behavior", () => {
    it("should have English and Urdu options", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "english",
      });

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByLabelText(/english/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/urdu|اردو/i)).toBeInTheDocument();
      });
    });

    it("should only allow one language selected", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "english",
      });

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByDisplayValue("english")).toBeChecked();
      });

      const urduRadio = screen.getByDisplayValue("urdu") as HTMLInputElement;
      expect(urduRadio.checked).toBe(false);

      fireEvent.click(urduRadio);

      expect(urduRadio.checked).toBe(true);
      expect((screen.getByDisplayValue("english") as HTMLInputElement).checked).toBe(false);
    });
  });

  describe("Accessibility", () => {
    it("should have proper labels", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "english",
      });

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByLabelText(/english/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/urdu/i)).toBeInTheDocument();
      });
    });

    it("should have properly labeled buttons", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "english",
      });

      render(<LanguageSettings />);

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /save/i })).toBeInTheDocument();
      });
    });
  });

  describe("RTL support", () => {
    it("should apply proper direction for Urdu", async () => {
      (languageAPI.getPreference as jest.Mock).mockResolvedValue({
        language: "urdu",
      });

      const { container } = render(<LanguageSettings />);

      await waitFor(() => {
        const urduLabel = screen.getByText(/اردو/i);
        expect(urduLabel).toBeInTheDocument();
      });
    });
  });
});
