import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function GlossaryPanel() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/memory/glossary-retries/")
      .then((res) => setLogs(res.results || []))
      .catch((err) => console.error("Failed to load glossary retries", err));
  }, []);

  return (
    <div className="p-2 border rounded">
      <h5>Glossary Retry Logs</h5>
      {logs.length === 0 ? (
        <div className="text-muted">No retry logs</div>
      ) : (
        <ul className="small">
          {logs.map((log) => (
            <li key={log.id}>
              <strong>{log.anchor_label || log.anchor}</strong> – diff {log.score_diff}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

