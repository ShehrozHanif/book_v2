/**
 * Frontend React entry point for the RAG Chatbot widget.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ChatBot } from "./components";
import LoginPage from "./pages/LoginPage";
import { AuthContextProvider } from "./contexts/AuthContext";
import "./index.css";

// Get root element
const root = document.getElementById("root");

if (!root) {
  throw new Error("Root element not found. Ensure public/index.html has a <div id='root'></div>");
}

// Create React root and render ChatBot
const reactRoot = ReactDOM.createRoot(root);

reactRoot.render(
  <React.StrictMode>
    <BrowserRouter basename="/book">
      <AuthContextProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={<ChatBot />} />
        </Routes>
      </AuthContextProvider>
    </BrowserRouter>
  </React.StrictMode>
);
