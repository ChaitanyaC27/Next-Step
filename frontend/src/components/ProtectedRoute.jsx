import React, { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";

const backendUrl = process.env.REACT_APP_API_URL || "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

const ProtectedRoute = () => {
  const [isValid, setIsValid] = useState(null);
  const token = localStorage.getItem("token");

  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setIsValid(false);
        return;
      }

      try {
        const response = await fetch(`${backendUrl}/auth/verify-token`, {
          method: "GET",
          headers: { Authorization: `Bearer ${token}` },
        });

        setIsValid(response.ok);
      } catch (error) {
        console.error("Error verifying token:", error);
        setIsValid(false);
      }
    };

    verifyToken();
  }, [token]);

  if (isValid === null) return <p style={{ textAlign: "center", marginTop: "20px" }}>🔄 Verifying...</p>;

  return isValid ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;
