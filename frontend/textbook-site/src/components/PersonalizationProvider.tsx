/**
 * PersonalizationProvider - Context provider for authentication and personalization
 * Wraps the entire Docusaurus app to provide user state and API access
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { personalizationApi } from '../services/personalizationApi';
import {
  User,
  UserPreferences,
  AuthContextType,
  ProgressRecord,
} from '../types/personalization';

// Create the context
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface PersonalizationContextType extends AuthContextType {
  progress: ProgressRecord[] | null;
  refetchProgress: () => Promise<void>;
}

export const PersonalizationContext = createContext<PersonalizationContextType | undefined>(
  undefined
);

interface PersonalizationProviderProps {
  children: ReactNode;
}

/**
 * Extract user data from backend response.
 * Backend returns flat { user_id, username } fields (TokenResponse),
 * not a nested { user: User } object.
 */
function extractUser(response: any, email?: string): User {
  if (response.user && response.user.user_id) {
    return response.user;
  }
  return {
    user_id: response.user_id || "",
    username: response.username || "",
    email: email || "",
    skill_level: 1,
    skill_confidence: 0,
    preferences: {
      explanation_style: "theory_first",
      code_language: "python",
      learning_pace: "medium",
      content_focus: "balanced",
    },
    created_at: new Date().toISOString(),
  };
}

/**
 * PersonalizationProvider component that manages authentication state
 * and provides personalization context to the entire app
 */
export const PersonalizationProvider: React.FC<PersonalizationProviderProps> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [progress, setProgress] = useState<ProgressRecord[] | null>(null);

  // Initialize from localStorage on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const savedUser = localStorage.getItem('user');

        if (token && savedUser && savedUser !== "undefined") {
          try {
            const parsedUser = JSON.parse(savedUser);
            setUser(parsedUser);
            setIsAuthenticated(true);
            personalizationApi.setToken(token);

            // Fetch fresh user profile and progress
            try {
              const profile = await personalizationApi.getProfile(parsedUser.user_id);
              setUser(profile);
              localStorage.setItem('user', JSON.stringify(profile));

              // Fetch progress data
              const progressData = await personalizationApi.getProgress(parsedUser.user_id);
              if (progressData && Array.isArray(progressData.progress)) {
                setProgress(progressData.progress);
              }
            } catch (error) {
              console.error('Error fetching user profile:', error);
              // If profile fetch fails, keep using cached user data
            }
          } catch (parseError) {
            console.error('Error parsing stored user:', parseError);
            localStorage.removeItem('user');
            localStorage.removeItem('access_token');
          }
        } else if (token) {
          // Have token but no valid user data - still authenticated
          personalizationApi.setToken(token);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Error initializing authentication:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await personalizationApi.login({ email, password });
      const userData = extractUser(response, email);
      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);

      // Fetch initial progress data
      try {
        const progressData = await personalizationApi.getProgress(userData.user_id);
        if (progressData && Array.isArray(progressData.progress)) {
          setProgress(progressData.progress);
        }
      } catch (error) {
        console.error('Error fetching progress after login:', error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (
    username: string,
    email: string,
    password: string
  ): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await personalizationApi.register({
        username,
        email,
        password,
      });
      const userData = extractUser(response, email);
      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);

      // Fetch initial progress data
      try {
        const progressData = await personalizationApi.getProgress(userData.user_id);
        if (progressData && Array.isArray(progressData.progress)) {
          setProgress(progressData.progress);
        }
      } catch (error) {
        console.error('Error fetching progress after registration:', error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    personalizationApi.logout().catch((error) => {
      console.error('Error calling logout endpoint:', error);
    });

    setUser(null);
    setIsAuthenticated(false);
    setProgress(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  const updatePreferences = async (
    preferences: Partial<UserPreferences>
  ): Promise<void> => {
    if (!user) {
      throw new Error('User not authenticated');
    }

    try {
      const updated = await personalizationApi.updatePreferences(
        user.user_id,
        preferences
      );
      const updatedUser = { ...user, preferences: updated };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } catch (error) {
      console.error('Error updating preferences:', error);
      throw error;
    }
  };

  const refetchProgress = async (): Promise<void> => {
    if (!user) return;

    try {
      const progressData = await personalizationApi.getProgress(user.user_id);
      if (progressData && Array.isArray(progressData.progress)) {
        setProgress(progressData.progress);
      }
    } catch (error) {
      console.error('Error refetching progress:', error);
    }
  };

  const contextValue: PersonalizationContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    updatePreferences,
    progress,
    refetchProgress,
  };

  return (
    <PersonalizationContext.Provider value={contextValue}>
      {children}
    </PersonalizationContext.Provider>
  );
};

/**
 * Hook to use personalization context
 */
export const usePersonalization = (): PersonalizationContextType => {
  const context = useContext(PersonalizationContext);

  if (context === undefined) {
    throw new Error(
      'usePersonalization must be used within PersonalizationProvider'
    );
  }

  return context;
};

export default PersonalizationProvider;
