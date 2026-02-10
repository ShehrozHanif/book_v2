/**
 * ChatbotMessageRTL Component Tests
 *
 * Tests for RTL/LTR rendering of chatbot messages with proper direction handling,
 * code block preservation, and mobile responsiveness.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import {
  ChatbotMessageRTL,
  ChatbotMessageContent,
  CodeBlock,
  InlineCode,
} from './ChatbotMessageRTL';

describe('ChatbotMessageRTL Component', () => {
  describe('Direction Handling', () => {
    test('renders with dir="rtl" for Urdu language', () => {
      const { container } = render(
        <ChatbotMessageRTL language="urdu">
          سلام علیکم
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveAttribute('dir', 'rtl');
      expect(message).toHaveClass('dir-rtl');
    });

    test('renders with dir="ltr" for English language', () => {
      const { container } = render(
        <ChatbotMessageRTL language="english">
          Hello
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveAttribute('dir', 'ltr');
      expect(message).toHaveClass('dir-ltr');
    });

    test('sets correct lang attribute for Urdu', () => {
      const { container } = render(
        <ChatbotMessageRTL language="urdu">
          سلام علیکم
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveAttribute('lang', 'ur');
    });

    test('sets correct lang attribute for English', () => {
      const { container } = render(
        <ChatbotMessageRTL language="english">
          Hello
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveAttribute('lang', 'en');
    });
  });

  describe('Message Type Styling', () => {
    test('applies assistant-message class for bot messages', () => {
      const { container } = render(
        <ChatbotMessageRTL language="english" isUserMessage={false}>
          Bot response
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveClass('assistant-message');
    });

    test('applies user-message class for user messages', () => {
      const { container } = render(
        <ChatbotMessageRTL language="english" isUserMessage={true}>
          User message
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveClass('user-message');
    });
  });

  describe('Code Block Handling', () => {
    test('renders code block with dir="ltr" in Urdu context', () => {
      const { container } = render(
        <ChatbotMessageRTL language="urdu">
          <CodeBlock>
            {`def hello():
    print("Hello, World!")`}
          </CodeBlock>
        </ChatbotMessageRTL>
      );

      const codeBlock = container.querySelector('.code-block');
      expect(codeBlock).toHaveAttribute('dir', 'ltr');
    });

    test('renders inline code with dir="ltr"', () => {
      const { container } = render(
        <ChatbotMessageRTL language="urdu">
          <p>
            اس کوڈ میں <InlineCode>variable_name</InlineCode> استعمال کریں
          </p>
        </ChatbotMessageRTL>
      );

      const inlineCode = container.querySelector('.inline-code');
      expect(inlineCode).toHaveAttribute('dir', 'ltr');
    });

    test('code block preserves formatting', () => {
      const code = `const x = 10;
const y = 20;`;
      render(
        <CodeBlock>
          {code}
        </CodeBlock>
      );

      expect(screen.getByText(/const x = 10/)).toBeInTheDocument();
    });

    test('code block supports language specification', () => {
      const { container } = render(
        <CodeBlock language="python">
          {`print("hello")`}
        </CodeBlock>
      );

      const code = container.querySelector('code');
      expect(code).toHaveClass('language-python');
    });
  });

  describe('Content Wrapping', () => {
    test('ChatbotMessageContent applies direction classes', () => {
      const { container } = render(
        <ChatbotMessageContent language="urdu">
          Urdu text
        </ChatbotMessageContent>
      );

      const content = container.querySelector('.chatbot-message-content');
      expect(content).toHaveClass('dir-rtl');
    });

    test('ChatbotMessageContent maintains text for English', () => {
      const { container } = render(
        <ChatbotMessageContent language="english">
          English text
        </ChatbotMessageContent>
      );

      const content = container.querySelector('.chatbot-message-content');
      expect(content).toHaveClass('dir-ltr');
    });
  });

  describe('Accessibility', () => {
    test('includes aria-label for screen readers', () => {
      const { container } = render(
        <ChatbotMessageRTL language="english" messageId="msg-1">
          Hello
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveAttribute('aria-label');
    });

    test('includes role="article" for semantic meaning', () => {
      const { container } = render(
        <ChatbotMessageRTL language="english">
          Hello
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveAttribute('role', 'article');
    });

    test('includes message ID when provided', () => {
      const messageId = 'test-message-123';
      const { container } = render(
        <ChatbotMessageRTL language="english" messageId={messageId}>
          Hello
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveAttribute('id', messageId);
    });
  });

  describe('CSS Classes', () => {
    test('applies custom className', () => {
      const { container } = render(
        <ChatbotMessageRTL language="english" className="custom-class">
          Hello
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveClass('custom-class');
    });

    test('combines multiple classes correctly', () => {
      const { container } = render(
        <ChatbotMessageRTL
          language="urdu"
          isUserMessage={true}
          className="highlight"
        >
          Text
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      expect(message).toHaveClass('chatbot-message-rtl');
      expect(message).toHaveClass('dir-rtl');
      expect(message).toHaveClass('user-message');
      expect(message).toHaveClass('highlight');
    });
  });

  describe('Content Rendering', () => {
    test('renders string content', () => {
      render(
        <ChatbotMessageRTL language="english">
          Hello World
        </ChatbotMessageRTL>
      );

      expect(screen.getByText('Hello World')).toBeInTheDocument();
    });

    test('renders JSX content', () => {
      render(
        <ChatbotMessageRTL language="english">
          <div data-testid="custom-content">Custom JSX</div>
        </ChatbotMessageRTL>
      );

      expect(screen.getByTestId('custom-content')).toBeInTheDocument();
    });

    test('renders complex HTML content', () => {
      render(
        <ChatbotMessageRTL language="urdu">
          <div>
            <h3>عنوان</h3>
            <p>متن</p>
            <code>code</code>
          </div>
        </ChatbotMessageRTL>
      );

      expect(screen.getByText('عنوان')).toBeInTheDocument();
      expect(screen.getByText('متن')).toBeInTheDocument();
      expect(screen.getByText('code')).toBeInTheDocument();
    });
  });

  describe('Number and Symbol Handling', () => {
    test('preserves number order in Urdu context', () => {
      const { container } = render(
        <ChatbotMessageRTL language="urdu">
          <span className="number">123</span>
        </ChatbotMessageRTL>
      );

      const number = container.querySelector('.number');
      expect(number).toHaveTextContent('123');
    });

    test('handles mathematical symbols correctly', () => {
      render(
        <ChatbotMessageRTL language="urdu">
          <span className="math">∑ (1 + 2) = 3</span>
        </ChatbotMessageRTL>
      );

      expect(screen.getByText(/∑ \(1 \+ 2\) = 3/)).toBeInTheDocument();
    });
  });

  describe('Mobile Responsiveness', () => {
    test('renders correctly on mobile', () => {
      const { container } = render(
        <ChatbotMessageRTL language="urdu" isUserMessage={true}>
          Mobile message
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      // Component should have mobile-friendly classes
      expect(message).toBeInTheDocument();
    });

    test('message width adjusts for user messages', () => {
      const { container } = render(
        <ChatbotMessageRTL language="english" isUserMessage={true}>
          User message
        </ChatbotMessageRTL>
      );

      const message = container.querySelector('.chatbot-message-rtl');
      // User messages should have max-width constraint
      expect(message).toHaveClass('user-message');
    });
  });

  describe('Mixed Content Scenarios', () => {
    test('handles Urdu text with embedded English', () => {
      render(
        <ChatbotMessageRTL language="urdu">
          <p>یہ ایک English word والا Urdu text ہے</p>
        </ChatbotMessageRTL>
      );

      // Content should be present despite mixed scripts
      expect(screen.getByText(/English word/)).toBeInTheDocument();
    });

    test('handles text with code blocks and paragraphs', () => {
      render(
        <ChatbotMessageRTL language="urdu">
          <p>یہ کوڈ کی مثال ہے:</p>
          <CodeBlock language="python">{`print("Hello")`}</CodeBlock>
          <p>یہ کوڈ Python میں لکھا ہے</p>
        </ChatbotMessageRTL>
      );

      expect(screen.getByText(/کوڈ کی مثال/)).toBeInTheDocument();
      expect(screen.getByText(/print\("Hello"\)/)).toBeInTheDocument();
    });

    test('handles lists in RTL context', () => {
      const { container } = render(
        <ChatbotMessageRTL language="urdu">
          <ul>
            <li>پہلی چیز</li>
            <li>دوسری چیز</li>
            <li>تیسری چیز</li>
          </ul>
        </ChatbotMessageRTL>
      );

      const list = container.querySelector('ul');
      expect(list?.children.length).toBe(3);
    });
  });

  describe('Performance', () => {
    test('renders large content efficiently', () => {
      const largeContent = 'Lorem ipsum '.repeat(100);
      const { container } = render(
        <ChatbotMessageRTL language="english">
          {largeContent}
        </ChatbotMessageRTL>
      );

      expect(container.querySelector('.chatbot-message-rtl')).toBeInTheDocument();
    });
  });
});
