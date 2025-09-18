import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

const backendUrl = process.env.REACT_APP_API_URL || "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      console.log("Attempting login...");

      const response = await fetch(`${backendUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Invalid credentials.");
      }

      const data = await response.json();
      console.log("Login successful, token received:", data.access_token);

      if (!data.access_token) {
        throw new Error("Login successful, but no token received.");
      }

      // ✅ Store the token & username in localStorage
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("username", username);
      console.log("Stored token & username:", localStorage.getItem("token"), localStorage.getItem("username"));

      // Verify token before navigation
      const verifyResponse = await fetch(`${backendUrl}/auth/verify-token`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${data.access_token}`,
          "Content-Type": "application/json",
        },
      });

      if (!verifyResponse.ok) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        throw new Error("Invalid session. Please login again.");
      }

      console.log("Token verified successfully! Navigating to dashboard...");
      navigate("/dashboard");
    } catch (err) {
      console.error("Login error:", err.message);
      setError(err.message);

      // ❌ Clear any invalid token or username
      localStorage.removeItem("token");
      localStorage.removeItem("username");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2 style={{ color: "#ff4d4d", textTransform: "uppercase", fontWeight: "600" }}>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="error-text">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Loading..." : "Login"}
        </button>
      </form>
      <p className="account-text">
        Don't have an account? <span onClick={() => navigate("/signup")} style={{ cursor: "pointer", color: "blue" }}>Sign up</span>
      </p>
    </div>
  );
}

export default Login;