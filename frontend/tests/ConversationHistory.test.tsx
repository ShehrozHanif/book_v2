import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ConversationHistory, Message } from "../src/components/ConversationHistory";

describe("ConversationHistory Component", () => {
  const mockMessages: Message[] = [
    {
      id: "msg1",
      sender: "user",
      content: "What is ROS 2?",
      timestamp: new Date("2024-01-30T10:00:00").toISOString(),
    },
    {
      id: "msg2",
      sender: "bot",
      content: "ROS 2 is a middleware framework for robotics.",
      timestamp: new Date("2024-01-30T10:00:05").toISOString(),
    },
  ];

  it("renders conversation history with messages", () => {
    render(<ConversationHistory messages={mockMessages} currentConversationId="conv-123" />);

    expect(screen.getByText("Conversation History")).toBeInTheDocument();
    expect(screen.getByText(/What is ROS 2/)).toBeInTheDocument();
    expect(screen.getByText(/ROS 2 is a middleware/)).toBeInTheDocument();
  });

  it("shows conversation ID", () => {
    render(<ConversationHistory messages={mockMessages} currentConversationId="conv-12345678" />);

    expect(screen.getByText(/ID: conv-123/)).toBeInTheDocument();
  });

  it("shows empty state when no messages", () => {
    render(<ConversationHistory messages={[]} />);

    expect(screen.getByText("No messages yet")).toBeInTheDocument();
    expect(screen.getByText("Start a conversation to see history")).toBeInTheDocument();
  });

  it("highlights latest message", () => {
    render(<ConversationHistory messages={mockMessages} />);

    const latestBadge = screen.getByText("Latest");
    expect(latestBadge).toBeInTheDocument();
  });

  it("truncates long messages", () => {
    const longMessage: Message[] = [
      {
        id: "msg1",
        sender: "user",
        content: "This is a very long message that should be truncated because it exceeds the maximum length allowed for preview",
        timestamp: new Date().toISOString(),
      },
    ];

    render(<ConversationHistory messages={longMessage} />);

    expect(screen.getByText(/This is a very long message.../)).toBeInTheDocument();
  });

  it("shows only last 20 messages", () => {
    const manyMessages: Message[] = Array.from({ length: 30 }, (_, i) => ({
      id: `msg${i}`,
      sender: i % 2 === 0 ? "user" : "bot",
      content: `Message ${i}`,
      timestamp: new Date().toISOString(),
    }));

    const { container } = render(<ConversationHistory messages={manyMessages} />);

    const historyItems = container.querySelectorAll(".history-item");
    expect(historyItems.length).toBeLessThanOrEqual(20);
  });
});
