import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function AnchorConvergencePanel({ anchorSlug }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!anchorSlug) return;
    async function load() {
      try {
        const data = await apiFetch(
          `/memory/symbolic-anchors/${anchorSlug}/convergence/`
        );
        setLogs(data.results || data);
      } catch (err) {
        console.error("Failed to fetch convergence logs", err);
        setLogs([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [anchorSlug]);

  if (loading) return <div>Loading convergence...</div>;

  return (
    <div className="p-2 border rounded">
      <h5 className="mb-3">Glossary Convergence</h5>
      {logs.length === 0 ? (
        <div className="text-muted">No convergence logs.</div>
      ) : (
        <ul className="list-group list-unstyled">
          {logs.map((log) => (
            <li key={log.id} className="mb-2">
              <div>
                <strong>{log.assistant_name}</strong>{" "}
                <span className="badge bg-secondary ms-1">
                  {log.final_score.toFixed(2)}
                </span>
                {log.retried && (
                  <span className="badge bg-info text-dark ms-1">Retried</span>
                )}
                {log.guidance_used && (
                  <span className="badge bg-warning text-dark ms-1">
                    Guidance
                  </span>
                )}
              </div>
              {log.memory_summary && (
                <div className="text-muted small">{log.memory_summary}</div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
