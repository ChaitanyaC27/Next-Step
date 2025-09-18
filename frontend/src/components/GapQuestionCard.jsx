import React, { useState, useEffect } from "react";
import "./GapTest.css";

const GapQuestionCard = ({ question, options, questionId, onSubmit }) => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [timeLeft, setTimeLeft] = useState(10); // 10-second timer

  useEffect(() => {
    if (timeLeft > 0 && !submitted) {
      const timer = setTimeout(() => setTimeLeft((prev) => prev - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && !submitted) {
      handleSubmit(); // Auto-submit when time runs out
    }
  }, [timeLeft, submitted]);

  const handleOptionSelect = (option) => {
    if (!submitted) {
      setSelectedOption(option);
    }
  };

  const handleSubmit = () => {
    if (!submitted) {
      setSubmitted(true);
      onSubmit(questionId, selectedOption || null); // Send answer to parent
    }
  };

  return (
    <div className="gap-question-card">
      <h2>{question}</h2>
      <p className="timer">Time Left: {timeLeft}s</p>
      <div className="options-container">
        {options.map((option, index) => (
          <button
            key={index}
            className={`option-btn ${selectedOption === option ? "selected" : ""}`}
            onClick={() => handleOptionSelect(option)}
            disabled={submitted}
            aria-pressed={selectedOption === option}
          >
            {option}
          </button>
        ))}
      </div>
      <button 
        className="submit-btn" 
        onClick={handleSubmit} 
        disabled={submitted || selectedOption === null}
      >
        {submitted ? "Submitted" : "Submit"}
      </button>
    </div>
  );
};

export default GapQuestionCard;
