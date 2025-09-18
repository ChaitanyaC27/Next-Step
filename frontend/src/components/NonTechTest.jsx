import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./NonTechTest.css";

const backendUrl = process.env.REACT_APP_API_URL || "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

const questions = [
  { id: 1, text: "1. I prefer working alone on coding problems rather than discussing them with others.", trait: "I" },
  { id: 2, text: "2. I feel more energized when brainstorming solutions with a group.", trait: "E" },
  { id: 3, text: "3. I would rather deeply focus on one task than switch between multiple discussions.", trait: "I" },
  { id: 4, text: "4. I like to talk through my thought process while coding.", trait: "E" },
  { id: 5, text: "5. I prefer reading documentation quietly over explaining it to someone else.", trait: "I" },

  { id: 6, text: "6. I rely on concrete examples and step-by-step guides when learning a new programming concept.", trait: "S" },
  { id: 7, text: "7. I prefer experimenting with different possibilities rather than following exact instructions.", trait: "N" },
  { id: 8, text: "8. I trust tried-and-tested coding solutions more than abstract ideas.", trait: "S" },
  { id: 9, text: "9. I often see patterns in code and anticipate problems before they occur.", trait: "N" },
  { id: 10, text: "10. I like to understand the big picture of a system before diving into the details.", trait: "N" },

  { id: 11, text: "11. I prioritize logic and efficiency when writing code, even if it makes it harder for others to read.", trait: "T" },
  { id: 12, text: "12. I consider how my coding decisions will impact my teammates and their workflow.", trait: "F" },
  { id: 13, text: "13. I would rather refactor code for better performance than keep it simple for readability.", trait: "T" },
  { id: 14, text: "14. I get frustrated when someone criticizes my code without considering my perspective.", trait: "F" },
  { id: 15, text: "15. I prefer objective coding standards over flexible guidelines that account for team dynamics.", trait: "T" },

  { id: 16, text: "16. I like to plan my coding tasks in advance and stick to a schedule.", trait: "J" },
  { id: 17, text: "17. I work best when I have the freedom to adjust my approach as I go.", trait: "P" },
  { id: 18, text: "18. I feel more comfortable when I have a clear deadline and structured workflow.", trait: "J" },
  { id: 19, text: "19. I often wait until the last moment to finalize my code, making changes as I get new ideas.", trait: "P" },
  { id: 20, text: "20. I prefer following a strict coding style guide rather than adapting based on the project’s needs.", trait: "J" },
];

const scaleLabels = {
  1: "Strongly Disagree",
  2: "Disagree",
  3: "Slightly Disagree",
  4: "Neutral",
  5: "Slightly Agree",
  6: "Agree",
  7: "Strongly Agree",
};

const NonTechTest = () => {
  const [responses, setResponses] = useState({});
  const navigate = useNavigate();
  const [username, setUsername] = useState("");

  useEffect(() => {
    const storedUsername = localStorage.getItem("username");
    if (!storedUsername) {
      alert("User not found. Please log in.");
      navigate("/login");
    } else {
      setUsername(storedUsername);
    }
  }, [navigate]);

  const handleResponseChange = (questionId, value) => {
    setResponses((prev) => ({ ...prev, [questionId]: value }));
  };

  const handleSubmit = async () => {
    if (Object.keys(responses).length !== questions.length) {
      alert("Please answer all questions before submitting.");
      return;
    }

    try {
      const formattedResponses = Object.keys(responses).reduce((acc, qId) => {
        acc[parseInt(qId)] = responses[qId];
        return acc;
      }, {});

      const res = await axios.post(`${backendUrl}/nontech_test/submit_non_tech_test`, {
        username,
        responses: formattedResponses,
      });

      if (res.data.personality_type) {
        navigate("/nontech-result", { state: { personality_type: res.data.personality_type } });
      }
    } catch (error) {
      alert("Submission failed. Try again later.");
    }
  };

  return (
    <div className="non-tech-test-container">
    <h2 class="coder-personality-heading">Coder Personality Test</h2>
      <p class="coder-personality-subtext">*Rate each statement from Strongly Disagree to Strongly Agree.*</p>

      <div className="questions-container">
        {questions.map((q) => (
          <div key={q.id} className="question">
            <p>{q.text}</p>
            <div className="likert-scale">
              {Object.entries(scaleLabels).map(([value, label]) => (
                <button
                  key={value}
                  className={`likert-btn ${responses[q.id] === parseInt(value) ? "selected" : ""}`}
                  onClick={() => handleResponseChange(q.id, parseInt(value))}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      <button className="submit-btn" onClick={handleSubmit}>Submit</button>
    </div>
  );
};

export default NonTechTest;
