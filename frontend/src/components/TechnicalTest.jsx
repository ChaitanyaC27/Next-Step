import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AceEditor from 'react-ace';
import { useNavigate } from 'react-router-dom';
import './AceEditorStyles.css';

// Import Ace Editor modes and themes
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/mode-java";
import "ace-builds/src-noconflict/mode-javascript";
import "ace-builds/src-noconflict/mode-c_cpp";
import "ace-builds/src-noconflict/theme-github";

const backendUrl =
  process.env.REACT_APP_API_URL ||
  "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

const languageOptions = [
  { value: "python", label: "Python", aceMode: "python" },
  { value: "java", label: "Java", aceMode: "java" },
  { value: "javascript", label: "JavaScript", aceMode: "javascript" },
  { value: "cpp", label: "C++", aceMode: "c_cpp" }
];

const TechnicalTest = ({ username }) => {
  const [question, setQuestion] = useState(null);
  const [questionId, setQuestionId] = useState(1);
  const [userCode, setUserCode] = useState('');
  const [message, setMessage] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState("python");

  const navigate = useNavigate();

  // Fallback: if username prop is missing, try localStorage or use default.
  const effectiveUsername = username || localStorage.getItem("username") || "default_user";

  useEffect(() => {
    // When starting the test (questionId is 1), reset progress via /technical_test/start endpoint.
    if (questionId === 1) {
      axios.post(`${backendUrl}/technical_test/start`, { username: effectiveUsername })
        .then(response => {
          setQuestion(response.data);
          setUserCode('');  // Reset code on new question
          setMessage('');
          setSelectedLanguage("python"); // Default to Python
        })
        .catch(error => {
          console.error("Error starting test", error);
        });
    } else {
      axios.get(`${backendUrl}/technical_test/question/${questionId}`)
        .then(response => {
          setQuestion(response.data);
          setUserCode('');  // Reset code on new question
          setMessage('');
        })
        .catch(error => {
          console.error("Error fetching question", error);
        });
    }
  }, [questionId, effectiveUsername]);

  const handleSubmit = () => {
    axios.post(`${backendUrl}/technical_test/submit_answer`, {
      username: effectiveUsername,
      question_id: questionId,
      user_code: userCode,
      language: selectedLanguage // Include language in submission
    })
    .then(response => {
      setMessage(response.data.message);
      if (questionId < 15) {
        setQuestionId(prev => prev + 1);
      } else {
        setMessage("Test Completed!");
      }
    })
    .catch(error => {
      if (error.response) {
        const detail = error.response.data.detail;
        setMessage(typeof detail === "string" ? detail : JSON.stringify(detail));
      } else {
        setMessage("Submission error");
      }
    });
  };

  const handleEndTest = () => {
    axios.post(`${backendUrl}/technical_test/end_test`, { username: effectiveUsername })
      .then(response => {
        // After ending the test, navigate to the technical result summary page
        navigate("/technical-result-summary");
      })
      .catch(error => {
        if (error.response) {
          const detail = error.response.data.detail;
          setMessage(typeof detail === "string" ? detail : JSON.stringify(detail));
        } else {
          setMessage("Error ending test");
        }
      });
  };

  if (!question) return <div>Loading question...</div>;

  return (
    <div className="technical-test-container">
      <h2>{question.title}</h2>
      <p>{question.problem_statement}</p>
      <p><strong>Example Input:</strong> {question.input_example}</p>
      <p><strong>Expected Output:</strong> {question.expected_output}</p>
      <p><strong>Constraints:</strong> {question.constraints}</p>
      <p><strong>Line Limit:</strong> {question.min_lines} - {question.max_lines} lines</p>

      {/* Language Selection Dropdown */}
      <label htmlFor="language">Choose a Language:</label>
      <select
        id="language"
        value={selectedLanguage}
        onChange={(e) => setSelectedLanguage(e.target.value)}
      >
        {languageOptions.map(lang => (
          <option key={lang.value} value={lang.value}>
            {lang.label}
          </option>
        ))}
      </select>

      {/* Code Editor */}
      <AceEditor
        mode={languageOptions.find(lang => lang.value === selectedLanguage)?.aceMode || "python"}
        theme="github"
        onChange={value => setUserCode(value)}
        value={userCode}
        name="codeEditor"
        editorProps={{ $blockScrolling: true }}
        width="100%"
        height="300px"
        setOptions={{
          useSoftTabs: true,
          tabSize: 4,
          fontSize: 14,
          highlightActiveLine: true,
          showPrintMargin: false
        }}
      />

      <button onClick={handleSubmit}>Submit Code</button>
      <button onClick={handleEndTest} style={{ marginLeft: "10px" }}>End Test</button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default TechnicalTest;
