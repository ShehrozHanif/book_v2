/**
 * Login page for Docusaurus textbook
 * Provides login and registration forms
 */

import React, { useState, useEffect } from 'react';
import { usePersonalization } from '../components/PersonalizationProvider';
import styles from './login.module.css';

type FormMode = 'login' | 'register';

export default function LoginPage(): JSX.Element {
  const { login, register, isLoading, isAuthenticated } = usePersonalization();

  // Get redirect URL from query parameters
  const getRedirectUrl = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get('redirect') || '/book/';
  };

  const [mode, setMode] = useState<FormMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      window.location.href = getRedirectUrl();
    }
  }, [isAuthenticated]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      // Use window.location instead of navigate
      setTimeout(() => {
        window.location.href = getRedirectUrl();
      }, 500);
    } catch (err) {
      const error = err as Error & { status?: number };
      setError(
        error.status === 401
          ? 'Invalid email or password'
          : error.message || 'Login failed. Please try again.'
      );
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(username, email, password);
      // Use window.location instead of navigate
      setTimeout(() => {
        window.location.href = getRedirectUrl();
      }, 500);
    } catch (err) {
      const error = err as Error & { status?: number };
      if (error.status === 409) {
        setError('Email already registered. Please log in instead.');
      } else {
        setError(error.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    if (mode === 'login') {
      handleLogin(e);
    } else {
      handleRegister(e);
    }
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingSpinner}>Loading...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>
          {mode === 'login' ? 'Login' : 'Create Account'}
        </h1>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit}>
          {mode === 'register' && (
            <div className={styles.formGroup}>
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Your username"
                required
                disabled={loading}
              />
            </div>
          )}

          <div className={styles.formGroup}>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              disabled={loading}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={loading}
              minLength={8}
            />
          </div>

          <button
            type="submit"
            className={styles.button}
            disabled={loading}
          >
            {loading
              ? 'Please wait...'
              : mode === 'login'
              ? 'Sign In'
              : 'Create Account'}
          </button>
        </form>

        <div className={styles.divider}>OR</div>

        <button
          className={styles.switchButton}
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login');
            setError('');
          }}
          disabled={loading}
        >
          {mode === 'login'
            ? "Don't have an account? Sign up"
            : 'Already have an account? Sign in'}
        </button>

        <p className={styles.info}>
          {mode === 'login'
            ? 'Log in to track your progress, complete practice questions, and access personalized learning features.'
            : 'Create an account to track your progress through the textbook and unlock interactive features.'}
        </p>
      </div>
    </div>
  );
}
