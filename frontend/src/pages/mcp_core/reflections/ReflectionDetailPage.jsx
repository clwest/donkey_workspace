import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import MoodBadge from "../../../components/mcp_core/MoodBadge";
import { moodColors } from "../../../components/mcp_core/MoodBadge";

export default function ReflectionDetailPage() {
  const { id } = useParams();
  const [reflection, setReflection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [thoughts, setThoughts] = useState([]);

  useEffect(() => {
    if (!id) {
      console.warn("ReflectionDetailPage: missing reflection id");
      return;
    }
    fetch(`/api/mcp/reflections/${id}/`)
      .then(res => res.json())
      .then(data => {
        setReflection(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch reflection:", err);
        setLoading(false);
      });

    fetch(`/api/assistants/reflections/${id}/thoughts/`)
      .then(res => res.json())
      .then(setThoughts)
      .catch(err => console.error("Failed to load thoughts", err));
  }, [id]);

  if (loading) return <div className="container mt-5">Loading reflection...</div>;
  if (!reflection) return <div className="container mt-5">Reflection not found.</div>;

  return (
    <div className="container mt-5">
      <h1 className="mb-4">🧠 {reflection.title || `Reflection #${reflection.id}`}</h1>
      <small className="text-muted mb-3 d-block">{reflection.created_at}</small>

      {reflection.mood && (
        <div className="mb-3">
          <strong>Mood:</strong>{" "}
          <MoodBadge mood={reflection.mood} />
        </div>
      )}

      {reflection.mood && (
        <div className="mb-3">
          <strong>Mood:</strong>{" "}
          <span
            className={`badge rounded-pill bg-${moodColors[reflection.mood.toLowerCase()] || "secondary"}`}
          >
            {reflection.mood.charAt(0).toUpperCase() + reflection.mood.slice(1).toLowerCase()}
          </span>
        </div>
      )}

      <h5 className="mt-4">Raw Summary:</h5>
      <pre className="p-3 bg-light rounded">{reflection.raw_summary || "No raw summary available."}</pre>

      <h5 className="mt-4">LLM Reflection:</h5>
      <p>{reflection.llm_summary || "No LLM reflection available."}</p>

      {thoughts.length > 0 && (
        <details className="mt-4">
          <summary>Related Thoughts ({thoughts.length})</summary>
          <ul className="mt-2">
            {thoughts.map((t) => (
              <li key={t.id}>{t.thought}</li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}