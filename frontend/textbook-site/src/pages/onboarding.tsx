/**
 * Onboarding Wizard - Guides new users through assessment and path selection
 *
 * 3-step flow:
 * 1. Welcome + Assessment Quiz
 * 2. Skill Result + Path Selection
 * 3. Ready to Learn
 */

import React, { useEffect, useState } from 'react';
import { usePersonalization } from '../components/PersonalizationProvider';
import { personalizationApi } from '../services/personalizationApi';
import styles from './onboarding.module.css';

type WizardStep = 'quiz' | 'results' | 'ready';

interface AssessmentQuestion {
  question_id: number;
  text: string;
  options: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

interface PathRecommendation {
  name: string;
  match_percentage: number;
  description: string | null;
  chapters: number[];
  estimated_hours: number | null;
}

interface AssessmentResult {
  assessment_id: string;
  skill_score: number;
  skill_tier: 'beginner' | 'intermediate' | 'advanced';
  recommended_paths: PathRecommendation[];
}

interface SelectedPathInfo {
  path_name: string;
  chapters: number[];
}

export default function OnboardingPage(): JSX.Element {
  const { user, isAuthenticated, isLoading: authLoading } = usePersonalization();

  const [step, setStep] = useState<WizardStep>('quiz');
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [selectedPathKey, setSelectedPathKey] = useState<string | null>(null);
  const [selectedPath, setSelectedPath] = useState<SelectedPathInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      window.location.href = `/login?redirect=${encodeURIComponent('/onboarding')}`;
    }
  }, [isAuthenticated, authLoading]);

  // Fetch assessment questions
  useEffect(() => {
    if (!user || !isAuthenticated) return;

    const fetchQuestions = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('[Onboarding] Fetching questions for user:', user.user_id);
        const data = await personalizationApi.getAssessmentQuestions(user.user_id);
        console.log('[Onboarding] Questions received:', data);
        setQuestions(data);
      } catch (err) {
        const e = err as Error & { status?: number };
        console.error('[Onboarding] Failed to fetch questions:', e);
        setError(`Failed to load assessment questions: ${e.message} (status: ${e.status || 'unknown'})`);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [user, isAuthenticated]);

  const handleAnswerChange = (questionId: number, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
  };

  const allAnswered = questions.length > 0 && questions.every((q) => answers[q.question_id]);

  const handleSubmitQuiz = async () => {
    if (!user || !allAnswered) return;

    try {
      setLoading(true);
      setError(null);

      const formattedAnswers = questions.map((q) => ({
        question_id: q.question_id,
        answer: answers[q.question_id],
      }));

      const data = await personalizationApi.submitAssessment(user.user_id, formattedAnswers);
      setResult(data);
      setStep('results');
    } catch (err) {
      const e = err as Error;
      setError(e.message || 'Failed to submit assessment.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPath = async (pathKey: string) => {
    if (!user) return;

    try {
      setLoading(true);
      setError(null);
      setSelectedPathKey(pathKey);

      const data = await personalizationApi.selectLearningPath(user.user_id, pathKey);
      setSelectedPath({
        path_name: data.path_name,
        chapters: data.chapters,
      });
      setStep('ready');
    } catch (err) {
      const e = err as Error;
      setError(e.message || 'Failed to select learning path.');
      setSelectedPathKey(null);
    } finally {
      setLoading(false);
    }
  };

  // Derive a URL-friendly key from the path name (e.g. "Developer Path" -> "developer")
  const pathNameToKey = (name: string): string => {
    return name.split(' ')[0].toLowerCase();
  };

  if (authLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <div className={styles.container}>
        <div className={styles.errorState}>
          <p>Please log in to access onboarding.</p>
        </div>
      </div>
    );
  }

  const stepIndex = step === 'quiz' ? 0 : step === 'results' ? 1 : 2;

  return (
    <div className={styles.container}>
      {/* Step Indicator */}
      <div className={styles.stepIndicator}>
        {['Assessment', 'Results', 'Ready'].map((label, i) => (
          <React.Fragment key={label}>
            {i > 0 && (
              <div className={`${styles.stepLine} ${i <= stepIndex ? styles.completed : ''}`} />
            )}
            <div className={styles.step}>
              <div
                className={`${styles.stepDot} ${i === stepIndex ? 'active' : ''} ${i < stepIndex ? 'completed' : ''}`}
                style={
                  i === stepIndex
                    ? { background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', boxShadow: '0 2px 8px rgba(102,126,234,0.4)' }
                    : i < stepIndex
                    ? { background: '#4caf50', color: 'white' }
                    : {}
                }
              >
                {i < stepIndex ? '\u2713' : i + 1}
              </div>
              <span className={`${styles.stepLabel} ${i === stepIndex ? styles.active : ''}`}>
                {label}
              </span>
            </div>
          </React.Fragment>
        ))}
      </div>

      {/* Error Display */}
      {error && (
        <div className={styles.errorState}>
          <h2>Something went wrong</h2>
          <p>{error}</p>
          <button className={styles.retryButton} onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {/* Step 1: Quiz */}
      {step === 'quiz' && !error && (
        <>
          <div className={styles.header}>
            <h1 className={styles.title}>Welcome to Your Learning Journey</h1>
            <p className={styles.subtitle}>
              Answer a few questions so we can recommend the best learning path for you.
            </p>
          </div>

          {loading && questions.length === 0 ? (
            <div className={styles.loadingState}>
              <div className={styles.spinner} />
              <p>Loading assessment questions...</p>
            </div>
          ) : (
            <div className={styles.quizContainer}>
              {questions.map((q, idx) => (
                <div key={q.question_id} className={styles.questionCard}>
                  <p className={styles.questionNumber}>
                    Question {idx + 1} of {questions.length}
                    <span className={`${styles.difficultyBadge} ${styles[q.difficulty]}`}>
                      {q.difficulty}
                    </span>
                  </p>
                  <p className={styles.questionText}>{q.text}</p>
                  <div className={styles.optionsList}>
                    {q.options.map((option, optIdx) => {
                      const optionLetter = String.fromCharCode(65 + optIdx);
                      const isSelected = answers[q.question_id] === optionLetter;
                      return (
                        <label
                          key={optIdx}
                          className={`${styles.optionLabel} ${isSelected ? styles.selected : ''}`}
                        >
                          <input
                            type="radio"
                            name={`question-${q.question_id}`}
                            value={optionLetter}
                            checked={isSelected}
                            onChange={() => handleAnswerChange(q.question_id, optionLetter)}
                            disabled={loading}
                          />
                          {option}
                        </label>
                      );
                    })}
                  </div>
                </div>
              ))}

              {questions.length > 0 && (
                <div className={styles.actions}>
                  <button
                    className={styles.primaryButton}
                    onClick={handleSubmitQuiz}
                    disabled={!allAnswered || loading}
                  >
                    {loading ? 'Submitting...' : `Submit Assessment (${Object.keys(answers).length}/${questions.length})`}
                  </button>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Step 2: Results + Path Selection */}
      {step === 'results' && result && !error && (
        <div className={styles.resultsContainer}>
          <div className={styles.header}>
            <h1 className={styles.title}>Your Assessment Results</h1>
            <p className={styles.subtitle}>
              Based on your answers, here's your skill profile and recommended paths.
            </p>
          </div>

          <div className={styles.scoreCard}>
            <p className={styles.scoreValue}>{result.skill_score}</p>
            <p className={styles.scoreLabel}>Skill Score (out of 100)</p>
            <span className={`${styles.tierBadge} ${styles[result.skill_tier]}`}>
              {result.skill_tier}
            </span>
          </div>

          <h2 className={styles.pathsTitle}>Choose Your Learning Path</h2>

          <div className={styles.pathsGrid}>
            {result.recommended_paths.map((path) => {
              const key = pathNameToKey(path.name);
              const isSelecting = selectedPathKey === key && loading;
              return (
                <div
                  key={path.name}
                  className={`${styles.pathCard} ${selectedPathKey === key ? styles.selectedPath : ''}`}
                  onClick={() => !loading && handleSelectPath(key)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && !loading && handleSelectPath(key)}
                >
                  <span className={styles.matchBadge}>{path.match_percentage}% match</span>
                  <h3 className={styles.pathName}>{path.name}</h3>
                  {path.description && (
                    <p className={styles.pathDescription}>{path.description}</p>
                  )}
                  <div className={styles.pathMeta}>
                    <span>{path.chapters.length} chapters</span>
                    {path.estimated_hours && <span>{path.estimated_hours}h estimated</span>}
                  </div>
                  {isSelecting && <p style={{ color: '#667eea', marginTop: 8, fontSize: 13 }}>Selecting...</p>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Step 3: Ready */}
      {step === 'ready' && selectedPath && !error && (
        <div className={styles.readyContainer}>
          <div className={styles.successCard}>
            <div className={styles.successIcon}>🎉</div>
            <h1 className={styles.successTitle}>You're All Set!</h1>
            <p className={styles.successSubtitle}>
              Your personalized learning path has been created. Start learning at your own pace.
            </p>

            <div className={styles.selectedPathInfo}>
              <h3>{selectedPath.path_name}</h3>
              <p>{selectedPath.chapters.length} chapters in your path</p>
            </div>

            <div className={styles.actions}>
              <a
                href={`/docs/module-01/chapter-0${selectedPath.chapters[0] || 1}`}
                className={styles.primaryButton}
                style={{ textDecoration: 'none', display: 'inline-block' }}
              >
                Start Learning
              </a>
            </div>

            <a href="/dashboard" className={styles.dashboardLink}>
              Go to Dashboard
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
