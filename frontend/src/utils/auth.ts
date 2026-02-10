/**
 * Authentication Utilities
 *
 * Provides helper functions for:
 * - Token management
 * - API authentication
 * - Token refresh
 */

import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_ID_KEY = 'user_id';
const USERNAME_KEY = 'username';

/**
 * Get access token from localStorage
 */
export const getAccessToken = (): string | null => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

/**
 * Get refresh token from localStorage
 */
export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Store authentication tokens
 */
export const storeTokens = (
  accessToken: string,
  refreshToken: string,
  userId: string,
  username: string
): void => {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  localStorage.setItem(USER_ID_KEY, userId);
  localStorage.setItem(USERNAME_KEY, username);
};

/**
 * Clear all authentication tokens
 */
export const clearTokens = (): void => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(USERNAME_KEY);
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};

/**
 * Get user info from localStorage
 */
export const getUserInfo = (): { userId: string | null; username: string | null } => {
  return {
    userId: localStorage.getItem(USER_ID_KEY),
    username: localStorage.getItem(USERNAME_KEY)
  };
};

/**
 * Refresh access token using refresh token
 */
export const refreshAccessToken = async (): Promise<boolean> => {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    return false;
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/users/refresh`, {
      refresh_token: refreshToken
    });

    const { access_token, refresh_token, user_id, username } = response.data;

    storeTokens(access_token, refresh_token, user_id, username);

    return true;
  } catch (error) {
    console.error('Token refresh failed:', error);
    clearTokens();
    return false;
  }
};

/**
 * Create axios instance with authentication
 */
export const createAuthAxios = () => {
  const instance = axios.create({
    baseURL: API_BASE_URL
  });

  // Request interceptor to add auth token
  instance.interceptors.request.use(
    (config) => {
      const token = getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor to handle token refresh
  instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as any;

      // If error is 401 and we haven't retried yet
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        const refreshed = await refreshAccessToken();

        if (refreshed) {
          // Retry the original request with new token
          const token = getAccessToken();
          if (token && originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return instance(originalRequest);
        } else {
          // Refresh failed, redirect to login
          clearTokens();
          window.location.href = '/login';
        }
      }

      return Promise.reject(error);
    }
  );

  return instance;
};

/**
 * Logout user
 */
export const logout = async (): Promise<void> => {
  try {
    const token = getAccessToken();
    if (token) {
      await axios.post(
        `${API_BASE_URL}/api/v1/users/logout`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
    }
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    clearTokens();
  }
};

/**
 * Get user profile
 */
export const getUserProfile = async () => {
  const authAxios = createAuthAxios();
  const response = await authAxios.get('/api/v1/users/me');
  return response.data;
};

/**
 * Update user profile
 */
export const updateUserProfile = async (updates: any) => {
  const authAxios = createAuthAxios();
  const response = await authAxios.put('/api/v1/users/me', updates);
  return response.data;
};

export default {
  getAccessToken,
  getRefreshToken,
  storeTokens,
  clearTokens,
  isAuthenticated,
  getUserInfo,
  refreshAccessToken,
  createAuthAxios,
  logout,
  getUserProfile,
  updateUserProfile
};
