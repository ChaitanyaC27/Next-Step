import React, { useState, useEffect } from "react";
import { generateFinalResult, getFinalResult } from "../api/finalResultApi";
import "./FinalResult.css"; // Import CSS file

const FinalResult = () => {
    const [finalResult, setFinalResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchFinalResult = async () => {
            setLoading(true);
            const result = await getFinalResult();
            if (result) {
                setFinalResult(result);
            } else {
                setError("No final result found. Please generate it first.");
            }
            setLoading(false);
        };

        fetchFinalResult();
    }, []);

    const handleFinalize = async () => {
        setLoading(true);
        const result = await generateFinalResult();
        if (result) {
            setFinalResult(result.final_result);
            setError("");
        } else {
            setError("Failed to generate the final result.");
        }
        setLoading(false);
    };

    return (
        <div className="final-result-container">
            <h2 className="final-result-title">FINAL TEST RESULTS</h2>

            {loading ? (
                <p className="loading-text">Loading...</p>
            ) : finalResult ? (
                <div className="final-result">
                    <p><strong>Average Elo:</strong> {finalResult.average_elo}</p>
                    <p><strong>Technical Test:</strong> {finalResult.technical_test}</p>
                    <p><strong>Personality Type:</strong> {finalResult.non_technical_test}</p>
                    <p className="career-guidance"><strong>Career Guidance:</strong></p>
                    <pre className="career-text">{finalResult.career_guidance}</pre>
                </div>
            ) : (
                <p className="error-text">{error}</p>
            )}

            <button className="finalize-button" onClick={handleFinalize} disabled={loading}>
                {loading ? "Generating..." : "Finalize Result"}
            </button>
        </div>
    );
};

export default FinalResult;
