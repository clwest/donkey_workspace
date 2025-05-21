import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DissentMonitorPanel() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/agents/dissent-logs/")
      .then(setLogs)
      .catch(() => setLogs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Dissent Signals</h5>
      <ul className="list-group">
        {logs.map((log) => (
          <li key={log.id} className="list-group-item d-flex justify-content-between">
            <span>
              <strong>{log.agent?.name}</strong>: {log.dissent_reason || log.feedback_text}
            </span>
            {log.is_dissent && <span className="badge bg-danger">dissent</span>}
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No dissent detected.</li>
        )}
      </ul>
    </div>
  );
}
