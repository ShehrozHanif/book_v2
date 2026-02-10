/**
 * PracticeQuestionsWidget - Interactive practice questions at end of chapters
 */

import React, { useState, useEffect } from 'react';
import { usePersonalization } from './PersonalizationProvider';
import { personalizationApi } from '../services/personalizationApi';
import { PracticeQuestion, PracticeResponse } from '../types/personalization';
import styles from './PracticeQuestionsWidget.module.css';

interface PracticeQuestionsWidgetProps {
  chapterId: number;
}

interface Answer {
  questionId: string;
  answer: string;
}

type WidgetState = 'loading' | 'questions' | 'submitted' | 'error';

export const PracticeQuestionsWidget: React.FC<PracticeQuestionsWidgetProps> = ({
  chapterId,
}) => {
  const { user, isAuthenticated, refetchProgress } = usePersonalization();
  const [state, setState] = useState<WidgetState>('loading');
  const [questions, setQuestions] = useState<PracticeQuestion[]>([]);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [result, setResult] = useState<PracticeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load questions when component mounts or chapter changes
  useEffect(() => {
    if (!isAuthenticated || !user) {
      setState('loading');
      return;
    }

    const loadQuestions = async () => {
      try {
        setState('loading');
        setError(null);
        const data = await personalizationApi.getPracticeQuestions(
          user.user_id,
          chapterId
        );
        setQuestions(data.questions);
        setAnswers(
          data.questions.map((q) => ({
            questionId: q.id,
            answer: '',
          }))
        );
        setState('questions');
      } catch (err) {
        const error = err as Error & { status?: number };
        if (error.status === 404) {
          setError('No practice questions available for this chapter yet.');
        } else {
          setError(
            error.message || 'Failed to load practice questions. Please try again.'
          );
        }
        setState('error');
      }
    };

    loadQuestions();
  }, [chapterId, isAuthenticated, user]);

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers((prev) =>
      prev.map((a) => (a.questionId === questionId ? { ...a, answer } : a))
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all questions answered
    const unanswered = answers.filter((a) => !a.answer);
    if (unanswered.length > 0) {
      setError('Please answer all questions before submitting.');
      return;
    }

    if (!user) {
      setError('User not authenticated');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const answersMap = answers.reduce(
        (acc, a) => ({
          ...acc,
          [a.questionId]: a.answer,
        }),
        {}
      );

      const response = await personalizationApi.submitPracticeAnswers(
        user.user_id,
        chapterId,
        answersMap
      );

      setResult(response);
      setState('submitted');

      // Refetch progress to update sidebar
      await refetchProgress();
    } catch (err) {
      const error = err as Error & { status?: number };
      setError(error.message || 'Failed to submit answers. Please try again.');
      setState('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setAnswers(
      questions.map((q) => ({
        questionId: q.id,
        answer: '',
      }))
    );
    setResult(null);
    setError(null);
    setState('questions');
  };

  if (!isAuthenticated) {
    return (
      <div className={styles.widget}>
        <div className={styles.loginPrompt}>
          <div className={styles.icon}>📝</div>
          <h3>Test Your Knowledge</h3>
          <p>
            Log in to access interactive practice questions and track your progress.
          </p>
          <a href={`/login?redirect=${window.location.pathname}`} className={styles.loginButton}>
            Sign In to Practice
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.widget}>
      <button
        className={styles.header}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <span className={styles.title}>📝 Test Your Knowledge</span>
        <span className={styles.toggle}>{isExpanded ? '−' : '+'}</span>
      </button>

      {isExpanded && (
        <div className={styles.content}>
          {state === 'loading' && (
            <div className={styles.loading}>
              <div className={styles.spinner} />
              Loading questions...
            </div>
          )}

          {state === 'error' && !result && (
            <div className={styles.error}>
              <p>{error}</p>
              {error?.includes('Failed') && (
                <button onClick={() => window.location.reload()}>
                  Try Again
                </button>
              )}
            </div>
          )}

          {state === 'questions' && questions.length > 0 && (
            <form onSubmit={handleSubmit}>
              <div className={styles.questionCount}>
                {questions.length} question{questions.length !== 1 ? 's' : ''}
              </div>

              {questions.map((question, qIndex) => (
                <div key={question.id} className={styles.question}>
                  <h4 className={styles.questionText}>
                    {qIndex + 1}. {question.question}
                  </h4>

                  <div className={styles.options}>
                    {question.options.map((option) => (
                      <label key={option.letter} className={styles.option}>
                        <input
                          type="radio"
                          name={`question-${question.id}`}
                          value={option.letter}
                          checked={
                            answers.find((a) => a.questionId === question.id)
                              ?.answer === option.letter
                          }
                          onChange={(e) =>
                            handleAnswerChange(question.id, e.target.value)
                          }
                          disabled={isSubmitting}
                        />
                        <span className={styles.optionLabel}>
                          {option.letter}. {option.text}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}

              {error && <div className={styles.error}>{error}</div>}

              <button
                type="submit"
                className={styles.submitButton}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Answers'}
              </button>
            </form>
          )}

          {state === 'submitted' && result && (
            <div className={styles.resultContainer}>
              <div
                className={`${styles.result} ${
                  result.passed ? styles.passed : styles.failed
                }`}
              >
                <div className={styles.resultIcon}>
                  {result.passed ? '✓' : '○'}
                </div>
                <h4 className={styles.resultTitle}>
                  {result.passed ? 'Great Work!' : 'Keep Learning!'}
                </h4>
                <p className={styles.resultMessage}>{result.message}</p>
                <div className={styles.scoreDisplay}>
                  <span className={styles.score}>{Math.round(result.score)}%</span>
                  <span className={styles.scoreLabel}>Score</span>
                </div>
              </div>

              <div className={styles.actions}>
                <button className={styles.resetButton} onClick={handleReset}>
                  Try Again
                </button>
              </div>

              <p className={styles.progressSaved}>
                ✓ Progress saved to your profile
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PracticeQuestionsWidget;
