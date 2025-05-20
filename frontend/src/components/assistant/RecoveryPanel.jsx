import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RecoveryPanel({ assistantSlug }) {
  const [log, setLog] = useState(null);
  const [thoughts, setThoughts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/assistants/${assistantSlug}/`);
        setLog(data.recent_drift);
        if (data.recent_drift) {
          const t = await apiFetch(
            `/assistants/${assistantSlug}/thoughts/?before=${data.recent_drift.timestamp}`
          );
          setThoughts(t.results || t);
        }
      } catch (err) {
        console.error("Failed to load recovery info", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [assistantSlug]);

  async function handleRecover() {
    try {
      const res = await apiFetch(`/assistants/${assistantSlug}/recover/`, {
        method: "POST",
      });
      alert(res.summary);
    } catch (err) {
      alert("Recovery failed");
    }
  }

  if (loading) return <div>Loading recovery info...</div>;

  return (
    <div className="card mb-3">
      <div className="card-header">Recovery</div>
      <div className="card-body">
        {log ? (
          <>
            <p>
              <strong>Last Drift:</strong> {log.summary}
            </p>
            {thoughts.length > 0 && (
              <ul>
                {thoughts.slice(0, 3).map((t) => (
                  <li key={t.id}>{t.thought}</li>
                ))}
              </ul>
            )}
          </>
        ) : (
          <p>No drift detected.</p>
        )}
        <button className="btn btn-warning" onClick={handleRecover}>
          Run Recovery
        </button>
      </div>
    </div>
  );
}
