import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CollapseChamber() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/agents/ritual-collapse/")
      .then(setLogs)
      .catch(() => setLogs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Collapses</h5>
      <ul className="list-group">
        {logs.map((log) => (
          <li key={log.id} className="list-group-item">
            <strong>{log.retired_entity}</strong> – {log.collapse_type}
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No collapses recorded.</li>
        )}
      </ul>
    </div>
  );
}
