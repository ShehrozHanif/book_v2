/**
 * Chapter Quiz Page - Standalone quiz page for chapter practice
 * Opens in new tab, auth-protected, fetches questions and submits answers
 */

import React, { useEffect, useState } from 'react';
import { usePersonalization } from '../components/PersonalizationProvider';
import { personalizationApi } from '../services/personalizationApi';
import { PracticeQuestion } from '../types/personalization';
import styles from './chapter-quiz.module.css';

type QuizState = 'loading' | 'questions' | 'results' | 'error';

interface QuizResults {
  score: number;
  passed: boolean;
  message: string;
  correct_count?: number;
  total_count?: number;
}

export default function ChapterQuizPage(): JSX.Element {
  const { user, isAuthenticated, isLoading: authLoading } = usePersonalization();

  const [chapterId, setChapterId] = useState<number | null>(null);
  const [state, setState] = useState<QuizState>('loading');
  const [questions, setQuestions] = useState<PracticeQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<QuizResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Extract chapter ID from URL on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const params = new URLSearchParams(window.location.search);
    const chapterParam = params.get('chapter');

    if (!chapterParam) {
      setError('No chapter specified');
      setState('error');
      return;
    }

    const id = parseInt(chapterParam, 10);
    if (isNaN(id) || id < 1) {
      setError('Invalid chapter ID');
      setState('error');
      return;
    }

    setChapterId(id);
  }, []);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated && typeof window !== 'undefined') {
      window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`;
    }
  }, [isAuthenticated, authLoading]);

  // Fetch questions when authenticated and chapter ID is set
  useEffect(() => {
    if (!user || !isAuthenticated || !chapterId) return;

    const fetchQuestions = async () => {
      try {
        setState('loading');
        setError(null);
        const data = await personalizationApi.getPracticeQuestions(user.user_id, chapterId);

        if (!data.questions || data.questions.length === 0) {
          setError('No questions available for this chapter');
          setState('error');
          return;
        }

        setQuestions(data.questions);
        setState('questions');
      } catch (err) {
        const error = err as Error;
        setError(error.message || 'Failed to load questions. Please try again later.');
        setState('error');
      }
    };

    fetchQuestions();
  }, [user, isAuthenticated, chapterId]);

  const handleAnswerChange = (questionId: string, answerLetter: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answerLetter,
    }));
  };

  const handleSubmit = async () => {
    if (!user || !chapterId) return;

    // Check if all questions are answered
    const unansweredCount = questions.length - Object.keys(answers).length;
    if (unansweredCount > 0) {
      alert(`Please answer all questions (${unansweredCount} remaining)`);
      return;
    }

    try {
      setState('loading');
      const response = await personalizationApi.submitPracticeAnswers(
        user.user_id,
        chapterId,
        answers
      );

      setResults({
        score: response.score,
        passed: response.passed,
        message: response.message,
        correct_count: response.correct_count,
        total_count: response.total_count,
      });
      setState('results');
    } catch (err) {
      const error = err as Error;
      setError(error.message || 'Failed to submit answers. Please try again.');
      setState('error');
    }
  };

  const handleTryAgain = () => {
    setAnswers({});
    setResults(null);
    setState('questions');
  };

  const handleClose = () => {
    if (typeof window !== 'undefined') {
      window.close();
    }
  };

  // Loading state
  if (authLoading || state === 'loading') {
    return (
      <div className={styles.container}>
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>{authLoading ? 'Authenticating...' : 'Loading quiz...'}</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!isAuthenticated || !user) {
    return (
      <div className={styles.container}>
        <div className={styles.errorState}>
          <h2>Authentication Required</h2>
          <p>Please log in to access the quiz.</p>
        </div>
      </div>
    );
  }

  // Error state
  if (state === 'error') {
    return (
      <div className={styles.container}>
        <div className={styles.errorState}>
          <h2>⚠️ Error</h2>
          <p>{error || 'An unexpected error occurred.'}</p>
          <button className={styles.closeButton} onClick={handleClose}>
            Close
          </button>
        </div>
      </div>
    );
  }

  // Results state
  if (state === 'results' && results) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Chapter {chapterId} Quiz</h1>
          <p className={styles.subtitle}>Results</p>
        </div>

        <div className={styles.resultCard}>
          <div className={styles.scoreValue}>{results.score}%</div>
          <div className={`${styles.tierBadge} ${results.passed ? styles.passed : styles.failed}`}>
            {results.passed ? '✓ Passed' : '✗ Failed'}
          </div>
          <p className={styles.resultMessage}>{results.message}</p>
          {results.correct_count !== undefined && results.total_count !== undefined && (
            <p className={styles.resultStats}>
              {results.correct_count} out of {results.total_count} correct
            </p>
          )}
          <div className={styles.resultActions}>
            <button className={styles.primaryButton} onClick={handleTryAgain}>
              Try Again
            </button>
            <button className={styles.closeButton} onClick={handleClose}>
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Questions state
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Chapter {chapterId} Quiz</h1>
        <p className={styles.subtitle}>
          {questions.length} question{questions.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className={styles.questionsContainer}>
        {questions.map((question, index) => (
          <div key={question.id} className={styles.questionCard}>
            <div className={styles.questionNumber}>Question {index + 1}</div>
            <div className={styles.questionText}>{question.question}</div>
            <div className={styles.optionsList}>
              {question.options.map((option) => (
                <label
                  key={option.letter}
                  className={`${styles.optionLabel} ${
                    answers[question.id] === option.letter ? styles.selected : ''
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={option.letter}
                    checked={answers[question.id] === option.letter}
                    onChange={() => handleAnswerChange(question.id, option.letter)}
                    className={styles.optionRadio}
                  />
                  <span className={styles.optionContent}>
                    <span className={styles.optionLetter}>{option.letter}.</span>
                    <span className={styles.optionText}>{option.text}</span>
                  </span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className={styles.actions}>
        <button
          className={styles.primaryButton}
          onClick={handleSubmit}
          disabled={Object.keys(answers).length !== questions.length}
        >
          Submit Quiz ({Object.keys(answers).length}/{questions.length} answered)
        </button>
      </div>
    </div>
  );
}
