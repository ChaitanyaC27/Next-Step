import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./NonTechTest.css"; // ✅ Updated CSS

const backendUrl =
  process.env.REACT_APP_API_URL || "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

const personalityDescriptions = {
  INTJ: "The Problem-Solver – Analytical, strategic, and independent.",
  INTP: "The Theorist – Logical, curious, and innovative.",
  ENTJ: "The Leader – Decisive, goal-oriented, and confident.",
  ENTP: "The Visionary – Outgoing, idea-driven, and adaptable.",
  INFJ: "The Mentor – Insightful, thoughtful, and supportive.",
  INFP: "The Dreamer – Creative, idealistic, and deep-thinking.",
  ENFJ: "The Motivator – Charismatic, people-focused, and encouraging.",
  ENFP: "The Innovator – Energetic, spontaneous, and imaginative.",
  ISTJ: "The Organizer – Detail-oriented, responsible, and structured.",
  ISFJ: "The Supporter – Loyal, practical, and caring.",
  ESTJ: "The Director – Efficient, systematic, and strong-willed.",
  ESFJ: "The Helper – Warm, outgoing, and cooperative.",
  ISTP: "The Experimenter – Practical, hands-on, and resourceful.",
  ISFP: "The Artist – Flexible, gentle, and aesthetic-driven.",
  ESTP: "The Dynamo – Energetic, realistic, and risk-taking.",
  ESFP: "The Entertainer – Fun-loving, spontaneous, and social.",
};

const NonTechResultSummary = () => {
  const [personalityType, setPersonalityType] = useState("");
  const [description, setDescription] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  // ✅ Use localStorage as a fallback if location.state is missing
  const username = location.state?.username || localStorage.getItem("username");

  useEffect(() => {
    if (!username) {
      navigate("/dashboard"); // Redirect if no username
      return;
    }

    // Fetch personality type from backend
    fetch(`${backendUrl}/nontech_test/get_result?username=${username}`)
      .then((res) => res.json())
      .then((data) => {
        setPersonalityType(data.personality_type);
        setDescription(personalityDescriptions[data.personality_type] || "Unknown Type");
      })
      .catch(() => {
        setDescription("Error fetching result.");
      });
  }, [username, navigate]);

  return (
    <div className="result-container">``````
      <h2 className="slide-in">Your Coder Personality</h2>
      {personalityType ? (
        <>
          <h3 className="personality-type zoom-effect">{personalityType}</h3>
          <p className="fade-in">{description}</p>
        </>
      ) : (
        <div className="loading-animation"></div>
      )}
      <button className="btn-hover-neon" onClick={() => navigate("/dashboard")}>Back to Dashboard</button>
    </div>
  );
};

export default NonTechResultSummary;
