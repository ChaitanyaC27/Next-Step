import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const backendUrl =
  process.env.REACT_APP_API_URL ||
  "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

const GapResultSummary = ({ username }) => {
  const navigate = useNavigate();
  
  // Use username from props or fallback to local storage.
  const effectiveUsername = username || localStorage.getItem("username");
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!effectiveUsername) {
      console.error("Error: Username is undefined");
      return;
    }

    console.log(`Fetching gap analysis result for username: ${effectiveUsername}`);

    fetch(`${backendUrl}/results/gap_analysis/${effectiveUsername}`)
      .then((res) => {
        if (!res.ok) {
          return res.text().then((text) => {
            throw new Error(`Server responded with ${res.status}: ${text}`);
          });
        }
        return res.json();
      })
      .then((data) => setResult(data))
      .catch((err) => console.error("Error fetching gap analysis result:", err));
  }, [effectiveUsername]);

  if (!effectiveUsername) {
    return <p>Error: No username provided.</p>;
  }

  return result ? (
    <div>
      <h2>Gap Analysis Results</h2>
      <h3>Average Elo: {result.average_elo}</h3>
      <h3>Topic Ratings:</h3>
      <ul>
        {result.topic_ratings && Object.entries(result.topic_ratings).map(([topic, rating]) => (
          <li key={topic}>
            <strong>{topic}:</strong> {rating}
          </li>
        ))}
      </ul>
      <button onClick={() => navigate("/dashboard")}>Back to Dashboard</button>
    </div>
  ) : (
    <p>Loading...</p>
  );
};

export default GapResultSummary;
