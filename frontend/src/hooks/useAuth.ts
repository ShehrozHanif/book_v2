/**
 * Custom hook for authentication context
 */

import { useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import { AuthContextType } from "../types/personalization";

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth must be used within AuthContextProvider");
  }

  return context;
};
