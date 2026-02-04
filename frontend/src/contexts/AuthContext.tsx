/**
 * Authentication context for user state management
 */

import React, { createContext, useState, useEffect, ReactNode } from "react";
import { User, UserPreferences, AuthContextType } from "../types/personalization";
import { personalizationApi } from "../services/personalizationApi";

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthContextProviderProps {
  children: ReactNode;
}

export const AuthContextProvider: React.FC<AuthContextProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Initialize from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const storedUser = localStorage.getItem("user");

    if (token && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        setIsAuthenticated(true);
        personalizationApi.setToken(token);
      } catch (error) {
        console.error("Failed to restore user from storage:", error);
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
      }
    }

    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await personalizationApi.login({ email, password });

      setUser(response.user);
      setIsAuthenticated(true);
      localStorage.setItem("user", JSON.stringify(response.user));
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

      setUser(response.user);
      setIsAuthenticated(true);
      localStorage.setItem("user", JSON.stringify(response.user));
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
