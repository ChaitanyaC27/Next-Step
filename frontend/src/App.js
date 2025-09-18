import React from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import "./App.css";
import Signup from "./components/Signup";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import NonTechTest from "./components/NonTechTest";
import NonTechResultSummary from "./components/NonTechResultSummary";
import GapTest from "./components/GapTest";
import GapResultSummary from "./components/GapResultSummary";
import TechnicalTest from "./components/TechnicalTest";
import TechResultSummary from "./components/TechResultSummary"; // new import
import FinalResult from "./components/FinalResult";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="app-container">
      <h1 className="title">NextStep: Tailored Learning Solutions</h1>
      <button className="get-started-btn" onClick={() => navigate("/signup")}>
        Get Started
      </button>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/login" element={<Login />} />

      {/* Non-Technical Test */}
      <Route path="/nontech-test" element={<NonTechTest />} />
      <Route path="/nontech-result" element={<NonTechResultSummary />} />

      {/* Protected Routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />

        {/* Gap Analysis Test */}
        <Route path="/gap-test" element={<GapTest />} />
        <Route path="/gap-result-summary" element={<GapResultSummary />} />

        {/* Technical Test */}
        <Route path="/technical-test" element={<TechnicalTest />} />
        <Route path="/technical-result-summary" element={<TechResultSummary />} />
        <Route path="/final-result" element={<FinalResult />} />
      </Route>
    </Routes>
  );
}

export default App;
