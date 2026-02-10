import React, { useState } from 'react';
import { useGlossary } from '../../hooks/useGlossary';
import { GlossaryFeedback } from '../../services/glossaryAPI';

interface ChatbotGlossaryProps {
  isOpen: boolean;
  onClose: () => void;
  authToken?: string;
  selectedTerm?: string;
}

export const ChatbotGlossary: React.FC<ChatbotGlossaryProps> = ({
  isOpen,
  onClose,
  authToken,
  selectedTerm,
}) => {
  const { terms, loading, error, selectedTerm: glossaryTerm, searchTerms, getTerm, submitFeedback } = useGlossary();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLanguage, setSearchLanguage] = useState<'english' | 'urdu'>('english');
  const [feedbackType, setFeedbackType] = useState<'suggestion' | 'correction' | 'new_term'>('suggestion');
  const [feedbackContent, setFeedbackContent] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [feedbackError, setFeedbackError] = useState('');

  React.useEffect(() => {
    if (selectedTerm && isOpen) {
      getTerm(selectedTerm);
    }
  }, [selectedTerm, isOpen, getTerm]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    await searchTerms(searchQuery, searchLanguage);
  };

  const handleSelectTerm = async (termName: string) => {
    await getTerm(termName);
  };

  const handleSubmitFeedback = async () => {
    if (!authToken || !feedbackContent.trim()) return;

    try {
      const feedback: GlossaryFeedback = {
        feedback_type: feedbackType,
        content: feedbackContent,
        glossary_term_id: glossaryTerm?.id,
      };
      await submitFeedback(feedback, authToken);
      setFeedbackSubmitted(true);
      setFeedbackContent('');
      setTimeout(() => setFeedbackSubmitted(false), 3000);
    } catch (err) {
      setFeedbackError(err instanceof Error ? err.message : 'Error');
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000 }}>
      <div style={{ background: 'white', borderRadius: '8px', maxWidth: '600px', margin: '50px auto', maxHeight: '80vh', overflow: 'auto' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #ddd', display: 'flex', justifyContent: 'space-between' }}>
          <h2>Technical Glossary</h2>
          <button onClick={onClose}>×</button>
        </div>

        <div style={{ padding: '20px' }}>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <input
              type="text"
              placeholder="Search term..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              style={{ flex: 1, padding: '8px', border: '1px solid #ccc' }}
            />
            <select
              value={searchLanguage}
              onChange={(e) => setSearchLanguage(e.target.value as any)}
              style={{ padding: '8px', border: '1px solid #ccc' }}
            >
              <option value="english">English</option>
              <option value="urdu">Urdu</option>
            </select>
            <button
              onClick={handleSearch}
              disabled={loading}
              style={{ padding: '8px 16px', background: '#007bff', color: 'white', border: 'none' }}
            >
              Search
            </button>
          </div>

          {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}

          {terms.length > 0 && !glossaryTerm && (
            <div>
              <h3>Results ({terms.length})</h3>
              {terms.map((term) => (
                <button
                  key={term.id}
                  onClick={() => handleSelectTerm(term.english_term)}
                  style={{ display: 'block', width: '100%', padding: '10px', textAlign: 'left', marginBottom: '5px', border: '1px solid #ddd' }}
                >
                  <strong>{term.english_term}</strong> - {term.urdu_translation}
                </button>
              ))}
            </div>
          )}

          {glossaryTerm && (
            <div>
              <h3>{glossaryTerm.english_term}</h3>
              <p style={{ fontSize: '18px', color: '#666' }}>{glossaryTerm.urdu_translation}</p>
              <p><strong>Pronunciation:</strong> {glossaryTerm.pronunciation_transliterated}</p>
              <div style={{ marginTop: '15px' }}>
                <h4>English Definition</h4>
                <p>{glossaryTerm.definition_english}</p>
                <h4>Urdu Definition</h4>
                <p style={{ direction: 'rtl' }}>{glossaryTerm.definition_urdu}</p>
              </div>

              {authToken && (
                <div style={{ marginTop: '20px', borderTop: '1px solid #ddd', paddingTop: '15px' }}>
                  <h4>Feedback</h4>
                  <select
                    value={feedbackType}
                    onChange={(e) => setFeedbackType(e.target.value as any)}
                    style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
                  >
                    <option value="suggestion">Suggestion</option>
                    <option value="correction">Correction</option>
                    <option value="new_term">New Term</option>
                  </select>
                  <textarea
                    value={feedbackContent}
                    onChange={(e) => setFeedbackContent(e.target.value)}
                    placeholder="Your feedback..."
                    style={{ width: '100%', padding: '8px', minHeight: '80px', marginBottom: '10px' }}
                    maxLength={500}
                  />
                  {feedbackError && <div style={{ color: 'red' }}>{feedbackError}</div>}
                  {feedbackSubmitted && <div style={{ color: 'green' }}>Feedback submitted!</div>}
                  <button
                    onClick={handleSubmitFeedback}
                    disabled={loading}
                    style={{ padding: '8px 16px', background: '#28a745', color: 'white', border: 'none' }}
                  >
                    Submit
                  </button>
                </div>
              )}

              <button
                onClick={() => {
                  setSearchQuery('');
                  setFeedbackContent('');
                }}
                style={{ marginTop: '15px', padding: '8px 16px', background: '#6c757d', color: 'white', border: 'none' }}
              >
                Back
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatbotGlossary;
