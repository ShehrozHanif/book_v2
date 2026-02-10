/**
 * Protected route component that requires authentication
 */

import React from "react";
import { useAuth } from "../hooks/useAuth";
import LoadingIndicator from "./LoadingIndicator";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <LoadingIndicator isVisible={true} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
          backgroundColor: "#f5f5f5",
        }}
      >
        <h2 style={{ color: "#333" }}>Access Denied</h2>
        <p style={{ color: "#666" }}>Please log in to access this page.</p>
        <a
          href="/"
          style={{
            marginTop: "20px",
            padding: "10px 20px",
            backgroundColor: "#2196f3",
            color: "white",
            textDecoration: "none",
            borderRadius: "4px",
            fontSize: "14px",
            fontWeight: "600",
          }}
        >
          Go to Login
        </a>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
