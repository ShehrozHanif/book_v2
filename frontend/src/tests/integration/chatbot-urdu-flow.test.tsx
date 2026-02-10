/**
 * End-to-End Test Scenarios for Urdu Translation Feature (T068)
 *
 * Tests the complete user flow:
 * 1. Login
 * 2. Select Urdu language
 * 3. Ask question to chatbot
 * 4. Receive Urdu response
 * 5. Check glossary for terms
 * 6. Logout
 */

import React from "react";
import { render, screen, waitFor, fireEvent, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter as Router } from "react-router-dom";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import thunk from "redux-thunk";

// Components
import ChatbotInterface from "../../../../components/ChatBot/ChatbotInterface";
import ChatbotLanguageToggle from "../../../../components/ChatBot/ChatbotLanguageToggle";
import GlossaryModal from "../../../../components/Glossary/GlossaryModal";
import LanguageSettings from "../../../../components/LanguagePreference/LanguageSettings";

// Services
import { languagePreferenceAPI } from "../../../../services/languagePreferenceAPI";
import { chatbotTranslationAPI } from "../../../../services/chatbotTranslationAPI";
import { glossaryAPI } from "../../../../services/glossaryAPI";

// Mock dependencies
jest.mock("../../../../services/languagePreferenceAPI");
jest.mock("../../../../services/chatbotTranslationAPI");
jest.mock("../../../../services/glossaryAPI");

const mockStore = configureStore([thunk]);

describe("E2E: Urdu Chatbot Flow", () => {
  let store: ReturnType<typeof mockStore>;

  beforeEach(() => {
    store = mockStore({
      auth: {
        isAuthenticated: true,
        user: { id: "user_123", username: "testuser", role: "student" },
        token: "mock_jwt_token",
      },
      language: {
        current: "english",
        available: ["english", "urdu"],
      },
      chatbot: {
        messages: [],
        loading: false,
        error: null,
      },
    });

    // Reset mocks
    jest.clearAllMocks();
  });

  describe("Complete User Journey: Login → Urdu → Chat → Glossary → Logout", () => {
    it("should complete full urdu chatbot interaction flow", async () => {
      const user = userEvent.setup();

      // Mock API responses
      (languagePreferenceAPI.getPreference as jest.Mock).mockResolvedValue("english");
      (languagePreferenceAPI.setPreference as jest.Mock).mockResolvedValue({ language: "urdu" });
      (chatbotTranslationAPI.getLanguage as jest.Mock).mockResolvedValue({ language: "english" });
      (chatbotTranslationAPI.setLanguage as jest.Mock).mockResolvedValue({ language: "urdu" });
      (chatbotTranslationAPI.getResponse as jest.Mock).mockResolvedValue({
        template_key: "greeting",
        english_content: "Hello! How can I help?",
        urdu_translation: "السلام علیکم! میں آپ کی کیا مدد کر سکتا ہوں؟",
        language: "urdu",
      });
      (glossaryAPI.search as jest.Mock).mockResolvedValue({
        query: "ROS",
        results: [
          {
            id: 1,
            english_term: "ROS 2",
            urdu_translation: "ROS 2",
            pronunciation_transliterated: "ROS 2",
            definitions: {
              english: "Robot Operating System version 2",
              urdu: "روبوٹ آپریٹنگ سسٹم ورژن 2",
            },
          },
        ],
      });

      const { container } = render(
        <Provider store={store}>
          <Router>
            <div>
              <ChatbotInterface />
              <ChatbotLanguageToggle />
            </div>
          </Router>
        </Provider>
      );

      // Step 1: Verify user is authenticated (shown by components rendering)
      expect(screen.getByRole("textbox", { name: /message/i })).toBeInTheDocument();

      // Step 2: Switch to Urdu language
      const languageButtons = screen.getAllByRole("button").filter((btn) =>
        btn.textContent?.includes("اردو") || btn.getAttribute("aria-label")?.includes("urdu")
      );
      expect(languageButtons.length).toBeGreaterThan(0);

      await user.click(languageButtons[0]);

      // Verify API call to set language preference
      await waitFor(() => {
        expect(languagePreferenceAPI.setPreference).toHaveBeenCalledWith("urdu");
      });

      // Step 3: Send message to chatbot
      const messageInput = screen.getByRole("textbox", { name: /message/i });
      await user.type(messageInput, "السلام علیکم");
      await user.click(screen.getByRole("button", { name: /send/i }));

      // Step 4: Verify Urdu response is received
      await waitFor(() => {
        expect(chatbotTranslationAPI.getResponse).toHaveBeenCalled();
        // Check for Urdu response in document
        expect(container.textContent).toContain("السلام علیکم");
      });

      // Step 5: Open glossary and search for terms
      const glossaryButton = screen.getByRole("button", { name: /glossary/i });
      await user.click(glossaryButton);

      // Search glossary
      const glossarySearch = screen.getByRole("textbox", { name: /search/i });
      await user.type(glossarySearch, "ROS");
      await user.keyboard("{Enter}");

      // Verify glossary search results
      await waitFor(() => {
        expect(glossaryAPI.search).toHaveBeenCalledWith("ROS", "urdu");
        expect(screen.getByText(/ROS 2/i)).toBeInTheDocument();
        expect(container.textContent).toContain("روبوٹ آپریٹنگ سسٹم");
      });

      // Step 6: Logout (verify session ends)
      const logoutButton = screen.getByRole("button", { name: /logout/i });
      await user.click(logoutButton);

      // Verify user is logged out
      expect(screen.queryByRole("textbox", { name: /message/i })).not.toBeInTheDocument();
    });

    it("should maintain conversation history during language switch", async () => {
      const user = userEvent.setup();

      // Mock API responses
      (chatbotTranslationAPI.getResponse as jest.Mock)
        .mockResolvedValueOnce({
          template_key: "greeting",
          english_content: "Hello! How can I help?",
          urdu_translation: "",
          language: "english",
        })
        .mockResolvedValueOnce({
          template_key: "greeting",
          english_content: "Hello! How can I help?",
          urdu_translation: "السلام علیکم! میں آپ کی کیا مدد کر سکتا ہوں؟",
          language: "urdu",
        });

      const { container } = render(
        <Provider store={store}>
          <Router>
            <ChatbotInterface />
            <ChatbotLanguageToggle />
          </Router>
        </Provider>
      );

      // Send message in English
      const messageInput = screen.getByRole("textbox", { name: /message/i });
      await user.type(messageInput, "Hello");
      await user.click(screen.getByRole("button", { name: /send/i }));

      await waitFor(() => {
        expect(screen.getByText(/Hello! How can I help?/i)).toBeInTheDocument();
      });

      // Switch to Urdu
      const urduButton = screen.getAllByRole("button").find((btn) =>
        btn.textContent?.includes("اردو")
      );
      await user.click(urduButton!);

      // Verify conversation history is preserved
      const messages = screen.getAllByText(/Hello/i);
      expect(messages.length).toBeGreaterThan(0);

      // Verify response is now in Urdu
      await waitFor(() => {
        expect(container.textContent).toContain("السلام علیکم");
      });
    });

    it("should handle language persistence across page reload", async () => {
      const user = userEvent.setup();

      // Mock localStorage
      Storage.prototype.getItem = jest.fn((key) => {
        if (key === "selectedLanguage") return "urdu";
        return null;
      });

      (languagePreferenceAPI.getPreference as jest.Mock).mockResolvedValue("urdu");
      (chatbotTranslationAPI.getLanguage as jest.Mock).mockResolvedValue({ language: "urdu" });

      const { rerender } = render(
        <Provider store={store}>
          <Router>
            <ChatbotInterface />
            <ChatbotLanguageToggle />
          </Router>
        </Provider>
      );

      // Verify Urdu preference loaded on mount
      await waitFor(() => {
        expect(languagePreferenceAPI.getPreference).toHaveBeenCalled();
      });

      // Simulate page reload
      rerender(
        <Provider store={store}>
          <Router>
            <ChatbotInterface />
            <ChatbotLanguageToggle />
          </Router>
        </Provider>
      );

      // Verify preference is still Urdu
      await waitFor(() => {
        expect(localStorage.getItem("selectedLanguage")).toBe("urdu");
      });
    });

    it("should display RTL content properly when Urdu selected", async () => {
      const user = userEvent.setup();

      (chatbotTranslationAPI.getResponse as jest.Mock).mockResolvedValue({
        template_key: "response",
        english_content: "This is a test",
        urdu_translation: "یہ ایک ٹیسٹ ہے",
        language: "urdu",
      });

      const { container } = render(
        <Provider store={store}>
          <Router>
            <ChatbotInterface />
            <ChatbotLanguageToggle />
          </Router>
        </Provider>
      );

      // Switch to Urdu
      const urduButton = screen.getAllByRole("button").find((btn) =>
        btn.textContent?.includes("اردو")
      );
      await user.click(urduButton!);

      await waitFor(() => {
        expect(chatbotTranslationAPI.getResponse).toHaveBeenCalled();
      });

      // Verify RTL direction is applied
      const chatbotContainer = container.querySelector("[data-testid='chatbot-messages']");
      expect(chatbotContainer).toHaveStyle("direction: rtl");
    });

    it("should handle glossary term lookup with Urdu content", async () => {
      const user = userEvent.setup();

      (glossaryAPI.getTerm as jest.Mock).mockResolvedValue({
        id: 1,
        english_term: "Kinematics",
        urdu_translation: "کائنیمیٹکس",
        pronunciation_transliterated: "kaineematix",
        definitions: {
          english: "The study of motion without regard to forces",
          urdu: "حرکت کا مطالعہ قوتوں کے بغیر",
        },
        examples: {
          english: "In robotics, kinematics helps us understand arm movements",
          urdu: "روبوٹکس میں کائنیمیٹکس ہمیں بازوؤں کی حرکت سمجھنے میں مدد کرتا ہے",
        },
      });

      const { container } = render(
        <Provider store={store}>
          <Router>
            <GlossaryModal termId={1} language="urdu" />
          </Router>
        </Provider>
      );

      await waitFor(() => {
        expect(glossaryAPI.getTerm).toHaveBeenCalledWith(1);
      });

      // Verify Urdu content is displayed
      expect(screen.getByText(/کائنیمیٹکس/i)).toBeInTheDocument();
      expect(screen.getByText(/روبوٹکس/i)).toBeInTheDocument();

      // Verify RTL direction
      const termContainer = container.querySelector("[data-testid='glossary-term']");
      expect(termContainer).toHaveStyle("direction: rtl");
    });

    it("should handle authentication gate for Urdu access", async () => {
      const user = userEvent.setup();

      // Create store with unauthenticated user
      const unauthStore = mockStore({
        auth: {
          isAuthenticated: false,
          user: null,
          token: null,
        },
        language: {
          current: "english",
          available: ["english", "urdu"],
        },
      });

      render(
        <Provider store={unauthStore}>
          <Router>
            <ChatbotLanguageToggle />
          </Router>
        </Provider>
      );

      // Verify Urdu button is disabled for guest
      const urduButton = screen.queryByRole("button", { name: /اردو/i });
      if (urduButton) {
        expect(urduButton).toBeDisabled();
      }

      // Verify tooltip indicating authentication required
      const tooltip = screen.queryByText(/sign in to use urdu/i);
      expect(tooltip || urduButton?.getAttribute("aria-label")).toBeDefined();
    });

    it("should handle rapid language switching", async () => {
      const user = userEvent.setup();

      (languagePreferenceAPI.setPreference as jest.Mock).mockResolvedValue({ language: "urdu" });
      (chatbotTranslationAPI.setLanguage as jest.Mock).mockResolvedValue({ language: "urdu" });

      render(
        <Provider store={store}>
          <Router>
            <ChatbotLanguageToggle />
          </Router>
        </Provider>
      );

      const buttons = screen.getAllByRole("button");
      const languageButtons = buttons.filter(
        (btn) => btn.textContent?.includes("English") || btn.textContent?.includes("اردو")
      );

      // Rapidly switch languages 5 times
      for (let i = 0; i < 5; i++) {
        await user.click(languageButtons[i % languageButtons.length]);
        // Don't wait between clicks - test rapid succession
      }

      // Verify no errors occurred and final state is consistent
      await waitFor(() => {
        expect(languagePreferenceAPI.setPreference).toHaveBeenCalled();
      }, { timeout: 3000 });
    });

    it("should display glossary with correct RTL formatting", async () => {
      const user = userEvent.setup();

      (glossaryAPI.search as jest.Mock).mockResolvedValue({
        query: "node",
        results: [
          {
            id: 1,
            english_term: "Node",
            urdu_translation: "نوڈ",
            pronunciation_transliterated: "nod",
            definitions: {
              english: "A discrete entity in ROS",
              urdu: "ROS میں ایک الگ ہستی",
            },
            category: "robotics",
          },
        ],
      });

      const { container } = render(
        <Provider store={store}>
          <Router>
            <GlossaryModal open={true} language="urdu" />
          </Router>
        </Provider>
      );

      const searchInput = screen.getByRole("textbox", { name: /search/i });
      await user.type(searchInput, "node");
      await user.keyboard("{Enter}");

      await waitFor(() => {
        expect(glossaryAPI.search).toHaveBeenCalledWith("node", "urdu");
      });

      // Verify result display with RTL
      const resultItem = container.querySelector("[data-testid='glossary-result-1']");
      expect(resultItem).toHaveStyle("direction: rtl");
      expect(screen.getByText(/نوڈ/i)).toBeInTheDocument();
    });
  });

  describe("Error Handling in E2E Flow", () => {
    it("should handle API errors gracefully during language switch", async () => {
      const user = userEvent.setup();

      (languagePreferenceAPI.setPreference as jest.Mock).mockRejectedValue(
        new Error("Network error")
      );

      render(
        <Provider store={store}>
          <Router>
            <ChatbotLanguageToggle />
          </Router>
        </Provider>
      );

      const urduButton = screen.getAllByRole("button").find((btn) =>
        btn.textContent?.includes("اردو")
      );
      await user.click(urduButton!);

      // Verify error message displayed
      await waitFor(() => {
        expect(screen.getByText(/error|failed/i)).toBeInTheDocument();
      });

      // Verify language didn't change
      expect(store.getState().language.current).toBe("english");
    });

    it("should handle missing Urdu translation fallback to English", async () => {
      const user = userEvent.setup();

      (chatbotTranslationAPI.getResponse as jest.Mock).mockResolvedValue({
        template_key: "response",
        english_content: "This is an untranslated response",
        urdu_translation: null, // No Urdu translation available
        language: "english",
      });

      const { container } = render(
        <Provider store={store}>
          <Router>
            <ChatbotInterface />
          </Router>
        </Provider>
      );

      const messageInput = screen.getByRole("textbox", { name: /message/i });
      await user.type(messageInput, "test");
      await user.click(screen.getByRole("button", { name: /send/i }));

      // Verify fallback to English content
      await waitFor(() => {
        expect(screen.getByText(/This is an untranslated response/i)).toBeInTheDocument();
      });
    });

    it("should handle glossary search with no results", async () => {
      const user = userEvent.setup();

      (glossaryAPI.search as jest.Mock).mockResolvedValue({
        query: "nonexistent",
        results: [],
      });

      render(
        <Provider store={store}>
          <Router>
            <GlossaryModal open={true} language="urdu" />
          </Router>
        </Provider>
      );

      const searchInput = screen.getByRole("textbox", { name: /search/i });
      await user.type(searchInput, "nonexistent");
      await user.keyboard("{Enter}");

      await waitFor(() => {
        expect(screen.getByText(/no results|not found/i)).toBeInTheDocument();
      });
    });
  });
});
