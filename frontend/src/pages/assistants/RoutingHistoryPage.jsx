import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RoutingHistoryPage() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/assistants/routing-history/")
      .then((res) => setLogs(res.results || []))
      .catch((err) => console.error("Failed to load routing history", err));
  }, []);

  return (
    <div className="container my-5">
      <h1>Routing History</h1>
      {logs.length === 0 ? (
        <p>No routing logs.</p>
      ) : (
        <ul className="list-group">
          {logs.map((log) => (
            <li key={log.id} className="list-group-item">
              <div className="d-flex justify-content-between">
                <span>{log.context_summary.slice(0, 80)}</span>
                <span className="badge bg-secondary">
                  {log.confidence_score.toFixed(2)}
                </span>
              </div>
              {log.assistant && (
                <div className="small text-muted">Suggested: {log.assistant}</div>
              )}
              {log.reasoning && <div className="small">{log.reasoning}</div>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
