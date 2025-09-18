import { useEffect, useState } from "react";

const backendUrl =
  process.env.REACT_APP_API_URL ||
  "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

const TechResultSummary = ({ username }) => {
  // Use username from props if available, otherwise from local storage.
  const effectiveUsername = username || localStorage.getItem("username");
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!effectiveUsername) {
      console.error("Error: Username is undefined");
      return;
    }

    console.log(`Fetching technical test result for username: ${effectiveUsername}`);

    fetch(`${backendUrl}/results/technical_test/${effectiveUsername}`)
      .then((res) => {
        if (!res.ok) {
          return res.text().then((text) => {
            throw new Error(`Server responded with ${res.status}: ${text}`);
          });
        }
        return res.json();
      })
      .then((data) => setResult(data))
      .catch((err) => console.error("Error fetching technical test result:", err));
  }, [effectiveUsername]);

  const getProgrammingLevel = (milestoneStr) => {
    const numericMilestone = milestoneStr ? parseInt(milestoneStr, 10) : 0;
    if (numericMilestone < 5) return "Programming Beginner";
    if (numericMilestone === 5) return "Programming Basic";
    if (numericMilestone === 10) return "Programming Adept";
    if (numericMilestone === 15) return "Programming Advanced";
    return "Unknown Level";
  };

  if (!effectiveUsername) {
    return <p>Error: No username provided.</p>;
  }

  return result ? (
    <div>
      <h2>Technical Test Results</h2>
      <p>
        <strong>Questions Solved:</strong> {result.solved} / 15
      </p>
      <p>
        <strong>Programming Level:</strong> {getProgrammingLevel(result.milestone || "0")}
      </p>
    </div>
  ) : (
    <p>Loading...</p>
  );
};

export default TechResultSummary;
