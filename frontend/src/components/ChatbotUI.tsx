import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useLanguagePreference } from '../hooks/useLanguagePreference';
import ChatbotLanguageToggle from './ChatbotLanguageToggle';
import ChatbotMessageRTL from './ChatbotMessageRTL';
import '../styles/chatbot-ui.css';


interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  language: 'english' | 'urdu';
  timestamp: Date;
}


const ChatbotUI: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { language, setLanguage, loading: prefLoading } = useLanguagePreference();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Scroll to bottom of messages
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Handle user message submission
   */
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      sender: 'user',
      content: inputValue,
      language,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      // Simulate chatbot response (in real app, call API)
      await new Promise(resolve => setTimeout(resolve, 1000));

      const botMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        sender: 'assistant',
        content:
          language === 'urdu'
            ? 'مجھے آپ کے سوال کا جواب دینے میں خوشی ہوگی۔'
            : 'I would be happy to answer your question.',
        language,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle language change
   */
  const handleLanguageChange = async (newLanguage: 'english' | 'urdu') => {
    try {
      await setLanguage(newLanguage);
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  };

  return (
    <div className={`chatbot-ui ${language === 'urdu' ? 'dir-rtl' : 'dir-ltr'}`}>
      {/* Header */}
      <div className="chatbot-header">
        <h1 className="chatbot-title">
          {language === 'urdu' ? 'روبوٹکس سہایک' : 'Robotics Assistant'}
        </h1>
        <ChatbotLanguageToggle
          currentLanguage={language}
          onLanguageChange={handleLanguageChange}
          isAuthenticated={isAuthenticated}
        />
      </div>

      {/* Messages Container */}
      <div className="chatbot-messages" role="log" aria-live="polite">
        {messages.length === 0 && (
          <div className="chatbot-empty-state">
            <p className="chatbot-welcome">
              {language === 'urdu'
                ? 'خوش آمدید! مجھ سے روبوٹکس کے بارے میں سوالات کریں۔'
                : 'Welcome! Ask me questions about robotics.'}
            </p>
            {!isAuthenticated && language === 'urdu' && (
              <div className="chatbot-login-notice">
                {language === 'urdu'
                  ? 'اردو میں رسائی کے لیے براہ کرم سائن ان کریں'
                  : 'Please sign in to use Urdu'}
              </div>
            )}
          </div>
        )}

        {messages.map(message => (
          <div
            key={message.id}
            className={`chatbot-message ${message.sender} ${
              message.language === 'urdu' ? 'rtl' : 'ltr'
            }`}
            dir={message.language === 'urdu' ? 'rtl' : 'ltr'}
          >
            {message.sender === 'assistant' ? (
              <ChatbotMessageRTL
                content={message.content}
                language={message.language}
                timestamp={message.timestamp}
              />
            ) : (
              <div className="user-message-content">
                <p>{message.content}</p>
                <span className="message-timestamp">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chatbot-message assistant loading">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form className="chatbot-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          className="chatbot-input"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          placeholder={
            language === 'urdu'
              ? 'اپنا سوال یہاں لکھیں...'
              : 'Type your question here...'
          }
          disabled={loading || prefLoading}
          dir={language === 'urdu' ? 'rtl' : 'ltr'}
          aria-label={
            language === 'urdu'
              ? 'سوال درج کریں'
              : 'Enter your question'
          }
        />
        <button
          type="submit"
          className="chatbot-send-button"
          disabled={loading || !inputValue.trim() || prefLoading}
          aria-label={language === 'urdu' ? 'بھیجیں' : 'Send'}
        >
          {loading ? (
            <span className="spinner">⟳</span>
          ) : (
            <span>{language === 'urdu' ? 'بھیجیں' : 'Send'}</span>
          )}
        </button>
      </form>
    </div>
  );
};

export default ChatbotUI;
