/**
 * Authentication context for user state management
 *
 * Handles both response formats from the backend:
 * - TokenResponse: { access_token, refresh_token, token_type, user_id, username }
 * - AuthResponse: { access_token, refresh_token, user: User }
 */

import React, { createContext, useState, useEffect, ReactNode } from "react";
import { User, UserPreferences, AuthContextType } from "../types/personalization";
import { personalizationApi } from "../services/personalizationApi";

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthContextProviderProps {
  children: ReactNode;
}

/**
 * Extract user data from backend response.
 * Backend returns flat { user_id, username } fields (TokenResponse),
 * not a nested { user: User } object.
 */
function extractUser(response: any, email?: string): User {
  // If response has a proper user object, use it
  if (response.user && response.user.user_id) {
    return response.user;
  }

  // Otherwise build user from flat TokenResponse fields
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

export const AuthContextProvider: React.FC<AuthContextProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Initialize from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const storedUser = localStorage.getItem("user");

    if (token) {
      personalizationApi.setToken(token);

      if (storedUser && storedUser !== "undefined") {
        try {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          console.error("Failed to restore user from storage:", error);
          localStorage.removeItem("user");
        }
      } else {
        // Have token but no user data - still authenticated
        setIsAuthenticated(true);
      }
    }

    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await personalizationApi.login({ email, password });
      const userData = extractUser(response, email);

      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem("user", JSON.stringify(userData));
      localStorage.setItem("refresh_token", response.refresh_token);
    } catch (error) {
      setIsAuthenticated(false);
      setUser(null);
      throw error;
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
      localStorage.setItem("user", JSON.stringify(userData));
      localStorage.setItem("refresh_token", response.refresh_token);
    } catch (error) {
      setIsAuthenticated(false);
      setUser(null);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    try {
      personalizationApi.logout();
    } catch (error) {
      console.error("Error during logout:", error);
    }

    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  };

  const updatePreferences = async (
    preferences: Partial<UserPreferences>
  ): Promise<void> => {
    if (!user) {
      throw new Error("User not authenticated");
    }

    try {
      const updated = await personalizationApi.updatePreferences(user.user_id, preferences);

      const updatedUser: User = {
        ...user,
        preferences: updated,
      };

      setUser(updatedUser);
      localStorage.setItem("user", JSON.stringify(updatedUser));
    } catch (error) {
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    updatePreferences,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
