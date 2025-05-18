import React, { useEffect, useState } from "react";
import LoadingSpinner from "../LoadingSpinner";
import apiFetch from "../../utils/apiClient";

const PromptDiagnosticsPanel = ({ text }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!text) return;

    const runAnalysis = async () => {
      try {
        setLoading(true);
        const data = await apiFetch("/prompts/analyze/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
        setAnalysis(data);
      } catch (err) {
        console.error("❌ Failed to fetch diagnostics", err);
        setAnalysis(null); // Reset to null on error
      } finally {
        setLoading(false);
      }
    };

    runAnalysis();
  }, [text]);

  if (loading) return <LoadingSpinner />;
  if (!analysis) return <p className="text-muted">⚠️ Unable to analyze prompt.</p>;

  return (
          <div className="card mb-4 p-3">
            <h5 className="mb-3">📊 Prompt Diagnostics</h5>
            <ul className="list-group list-group-flush">
              <li className="list-group-item">🧠 Token Count: {analysis.tokens}</li>
              <li className="list-group-item">📚 Flesch Reading Ease: {analysis.flesch_reading_ease}</li>
              <li className="list-group-item">📖 FK Grade Level: {analysis.flesch_kincaid_grade}</li>
              <li className="list-group-item">✏️ Avg Sentence Length: {analysis.avg_sentence_length}</li>
              <li className="list-group-item">🔤 Avg Syllables per Word: {analysis.avg_syllables_per_word}</li>
              <li className="list-group-item">⏱ Estimated Read Time: {analysis.reading_time_seconds}s</li>
            </ul>
          </div>
  );
};

export default PromptDiagnosticsPanel;