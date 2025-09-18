import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

const backendUrl = process.env.REACT_APP_API_URL || "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState("");

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/login");
        return;
      }

      try {
        const response = await fetch(`${backendUrl}/auth/verify-token`, {
          method: "GET",
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) throw new Error("Invalid session. Please login again.");

        const userData = await response.json();
        setUsername(userData.username);
        setLoading(false);
      } catch (error) {
        console.error("Token verification failed:", error);
        localStorage.removeItem("token");
        navigate("/login");
      }
    };

    verifyToken();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div className="dashboard-container">
      {/* Top Navigation Bar */}
      <nav className="dashboard-navbar">
        <div className="dashboard-logo">NextStep</div>
        <div className="dashboard-user">
          <span>Welcome, {username}</span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="dashboard-content">
        <h2 className="dashboard-title">Dashboard</h2>
        <div className="dashboard-grid">
          <button onClick={() => navigate("/gap-test")} className="dashboard-card">
            Gap Analysis Test
          </button>
          <button onClick={() => navigate("/technical-test")} className="dashboard-card">
            Technical Test
          </button>
          <button onClick={() => navigate("/nontech-test")} className="dashboard-card">
            Non-Technical Test
          </button>
          <button onClick={() => navigate("/final-result")} className="dashboard-card">
            My Results
          </button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
