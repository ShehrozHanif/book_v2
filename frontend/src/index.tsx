/**
 * Frontend React entry point for the RAG Chatbot widget.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import { ChatBot } from "./components";
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
    <AuthContextProvider>
      <ChatBot />
    </AuthContextProvider>
  </React.StrictMode>
);
