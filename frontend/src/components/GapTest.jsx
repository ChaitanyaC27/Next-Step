import React, { useState, useEffect } from "react";
import GapQuestionCard from "./GapQuestionCard";
import { useNavigate } from "react-router-dom";
import "./GapTest.css";

const backendUrl =
  process.env.REACT_APP_API_URL || "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

const TOTAL_QUESTIONS = 60;

const GapTest = () => {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionCount, setQuestionCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    console.log("🔄 useEffect triggered, resetting test progress...");
    resetGapTest();
  }, []);

  const resetGapTest = async () => {
    const token = localStorage.getItem("token");
    try {
      const response = await fetch(`${backendUrl}/gap_test/reset_gap_test`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      console.log("🔄 Test progress reset:", data);
      // Reset local question count if needed
      setQuestionCount(0);
      loadNextQuestion();
    } catch (error) {
      console.error("❌ Error resetting test:", error);
    }
  };

  const loadNextQuestion = async () => {
    console.log(`📌 Loading next question... (Current count: ${questionCount})`);

    if (questionCount >= TOTAL_QUESTIONS) {
      console.log("✅ All questions answered. Navigating to results...");
      navigate("/gap-result-summary");
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      console.log("🔑 Token:", token ? "Token found" : "No token");

      const response = await fetch(`${backendUrl}/gap_test/next_gap_question`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("❌ Failed to fetch question");

      const questionData = await response.json();
      console.log("📩 Question Data Received:", questionData);

      if (!questionData || !questionData.id) {
        console.log("🚨 No more questions available! Navigating to results...");
        navigate("/gap-result-summary");
        return;
      }

      setCurrentQuestion(questionData);
      console.log("✅ Question set successfully:", questionData);
    } catch (error) {
      console.error("❌ Error fetching question:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = async (questionId, selectedAnswer) => {
    if (!questionId) {
      console.log("⚠️ Invalid questionId:", questionId);
      return;
    }

    console.log(`📝 Submitting answer for Question ID: ${questionId}, Answer: ${selectedAnswer}`);
    setLoading(true);
    try {
      const token = localStorage.getItem("token");

      const response = await fetch(`${backendUrl}/gap_test/evaluate_gap_question`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question_id: questionId, answer: selectedAnswer }),
      });

      if (!response.ok) throw new Error("❌ Error submitting answer");

      const data = await response.json();
      console.log("✅ Answer submitted successfully!", data);

      setQuestionCount((prevCount) => {
        const newCount = prevCount + 1;
        console.log(`🔢 Updated question count: ${newCount}`);
        if (newCount >= TOTAL_QUESTIONS) {
          console.log("🏁 Reached total questions, navigating to results...");
          navigate("/gap-result-summary");
        }
        return newCount;
      });

      loadNextQuestion();
    } catch (error) {
      console.error("❌ Error submitting answer:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="gap-test-container">
      <h1>Gap Analysis Test</h1>
      <p>Question {questionCount + 1} of {TOTAL_QUESTIONS}</p>
      {loading ? (
        <p>Loading...</p>
      ) : (
        currentQuestion && currentQuestion.id !== 0 && (
          <GapQuestionCard
            question={currentQuestion.question}
            options={currentQuestion.options}
            questionId={currentQuestion.id}
            onSubmit={handleAnswerSubmit}
          />
        )
      )}
    </div>
  );
};

export default GapTest;
