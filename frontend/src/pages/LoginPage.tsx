/**
 * Login and Registration Page
 *
 * Uses AuthContext for authentication (login/register).
 * Plain CSS styling - no Tailwind dependency.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './LoginPage.css';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);

  // Form state
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Validation errors
  const [validationErrors, setValidationErrors] = useState<{
    username?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  const validateForm = (): boolean => {
    const errors: typeof validationErrors = {};

    if (!isLogin) {
      if (!username.trim()) {
        errors.username = 'Username is required';
      } else if (username.length < 3) {
        errors.username = 'Username must be at least 3 characters';
      }
    }

    if (!email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Invalid email format';
    }

    if (!password) {
      errors.password = 'Password is required';
    } else if (!isLogin) {
      if (password.length < 8) {
        errors.password = 'Password must be at least 8 characters';
      } else if (!/[A-Z]/.test(password)) {
        errors.password = 'Must contain at least one uppercase letter';
      } else if (!/[a-z]/.test(password)) {
        errors.password = 'Must contain at least one lowercase letter';
      } else if (!/[0-9]/.test(password)) {
        errors.password = 'Must contain at least one digit';
      }
    }

    if (!isLogin) {
      if (!confirmPassword) {
        errors.confirmPassword = 'Please confirm your password';
      } else if (password !== confirmPassword) {
        errors.confirmPassword = 'Passwords do not match';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        await login(email.trim().toLowerCase(), password);
      } else {
        await register(username.trim(), email.trim().toLowerCase(), password);
      }

      setSuccess(isLogin ? 'Login successful! Redirecting...' : 'Registration successful! Redirecting...');

      setTimeout(() => {
        navigate('/');
      }, 800);

    } catch (err: any) {
      console.error('Auth error:', err);
      const message = err?.response?.data?.detail || err?.message ||
        (isLogin ? 'Login failed. Please check your credentials.' : 'Registration failed. Please try again.');
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setSuccess('');
    setValidationErrors({});
    setUsername('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  return (
    <div className="login-page">
      <div className="login-card">
        {/* Header */}
        <div className="login-header">
          <div className="login-icon">🤖</div>
          <h2>{isLogin ? 'Sign in to your account' : 'Create your account'}</h2>
          <p>
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <button className="toggle-link" onClick={toggleMode}>
              {isLogin ? 'Register here' : 'Sign in here'}
            </button>
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {/* Username (registration only) */}
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Choose a username"
                className={validationErrors.username ? 'input-error' : ''}
              />
              {validationErrors.username && (
                <span className="field-error">{validationErrors.username}</span>
              )}
            </div>
          )}

          {/* Email */}
          <div className="form-group">
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.email@example.com"
              className={validationErrors.email ? 'input-error' : ''}
            />
            {validationErrors.email && (
              <span className="field-error">{validationErrors.email}</span>
            )}
          </div>

          {/* Password */}
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete={isLogin ? 'current-password' : 'new-password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isLogin ? 'Enter your password' : 'Create a strong password'}
              className={validationErrors.password ? 'input-error' : ''}
            />
            {validationErrors.password && (
              <span className="field-error">{validationErrors.password}</span>
            )}
            {!isLogin && (
              <span className="field-hint">8+ characters with uppercase, lowercase, and digit</span>
            )}
          </div>

          {/* Confirm Password (registration only) */}
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm your password"
                className={validationErrors.confirmPassword ? 'input-error' : ''}
              />
              {validationErrors.confirmPassword && (
                <span className="field-error">{validationErrors.confirmPassword}</span>
              )}
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="alert alert-error">
              <span className="alert-icon">!</span>
              <span>{error}</span>
            </div>
          )}

          {/* Success message */}
          {success && (
            <div className="alert alert-success">
              <span className="alert-icon">&#10003;</span>
              <span>{success}</span>
            </div>
          )}

          {/* Submit button */}
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? (
              <span className="btn-loading">
                <span className="spinner"></span>
                Processing...
              </span>
            ) : (
              isLogin ? 'Sign in' : 'Create account'
            )}
          </button>
        </form>

        {/* Back to chatbot link */}
        <div className="back-link">
          <button onClick={() => navigate('/')}>
            &#8592; Back to Chatbot
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
